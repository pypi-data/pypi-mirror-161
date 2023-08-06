"""
Run Hoppr processing, using multiple processors
"""
from __future__ import annotations

import logging
from multiprocessing import cpu_count
import os
import platform
import shutil
import socket
import tempfile
import urllib
from concurrent.futures import Future, ProcessPoolExecutor
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from packageurl import PackageURL  # type: ignore
from typer import echo

from hoppr.base_plugins.hoppr import HopprPlugin
from hoppr.configs.manifest import Manifest
from hoppr.configs.transfer import Transfer
from hoppr.context import Context
from hoppr.exceptions import HopprPluginError
from hoppr.flatten_sboms import flatten_sboms
from hoppr.net import download_file
from hoppr.result import Result
from hoppr.types.cyclonedx_1_4 import Component
from hoppr.types.transfer_file_content import Plugin as PluginRef
from hoppr.utils import plugin_instance

if "nux" in platform.system():
    import pwd


def _run_plugin(
    plugin: HopprPlugin, method_name: str, component: Optional[Component]
) -> Result:
    """
    Runs a single method for a single component (if supplied) on a single plugin
    """
    if method_name == HopprPlugin.pre_stage_process.__name__:
        result = plugin.pre_stage_process()
    elif method_name == HopprPlugin.process_component.__name__:
        result = plugin.process_component(component)
    elif method_name == HopprPlugin.post_stage_process.__name__:
        result = plugin.post_stage_process()
    else:
        result = Result.fail(f"Invalid method: {method_name}")

    return result


class StageProcessor:  # pylint: disable=too-few-public-methods
    """
    Class to handle all processing within a single Hoppr stage
    """

    def __init__(
        self, stage_id: str, context: Context, plugin_ref_list: List[PluginRef]
    ):
        self.stage_id = stage_id
        self.context = context
        self.plugin_ref_list = plugin_ref_list
        self.plugins: List[HopprPlugin] = []
        self.results: Dict = {}

    def run(self) -> Result:
        """
        Run all processes for this stage
        """

        HopprProcessor.get_logger().info(  # pylint: disable=logging-fstring-interpolation
            f"---------- Beginning Stage {self.stage_id} ----------"
        )
        try:
            self.plugins = self._load_plugins()
        except (ModuleNotFoundError, HopprPluginError) as err:
            return Result.fail(str(err))

        result = Result.success()

        # Run each sub-stage (pre_stage_process, process_component, post_stage_process)
        # for all plugins (and, for process_component, for all components).
        # Each sub-stage must complete before the next can begin

        result.merge(self._run_all(HopprPlugin.pre_stage_process.__name__))
        result.merge(self._run_all(HopprPlugin.process_component.__name__))
        result.merge(self._run_all(HopprPlugin.post_stage_process.__name__))

        return result

    def _run_all(self, method_name: str):
        """
        Run the named method for all plugins.  If appropriate to the method, run it for
        all components for all plug-ins.
        """

        component_based_methods = [HopprPlugin.process_component.__name__]
        futures = []

        # Map to allow access to the arguments that went into a future call
        future_argument_map: Dict[Future, Tuple[HopprPlugin, Optional[Component]]] = {}

        with ProcessPoolExecutor(max_workers=self.context.max_processes) as executor:
            for plugin in self.plugins:
                if method_name in component_based_methods:

                    # Create one concurrent future object to run this method for each component

                    for component in self.context.consolidated_sbom.components or []:
                        future_proc = executor.submit(
                            _run_plugin, plugin, method_name, component
                        )
                        future_argument_map[future_proc] = (plugin, component)
                        futures.append(future_proc)
                else:

                    # Create a concurrent future object to run this method

                    future_proc = executor.submit(
                        _run_plugin, plugin, method_name, None
                    )
                    future_argument_map[future_proc] = (plugin, None)
                    futures.append(future_proc)

            # Save all the results, count failures and retries
            # Note: future.results() blocks until the process is complete

            failures = 0
            retries = 0
            for future_proc in futures:
                future_result = future_proc.result()
                if not future_result.is_skip():
                    plugin, comp = future_argument_map[future_proc]
                    self._save_result(method_name, plugin, future_result, comp)

                    if future_result.is_fail():
                        failures += 1
                    if future_result.is_retry():
                        retries += 1

        if failures + retries == 0:
            return Result.success()
        if failures == 0 and retries > 0:
            return Result.fail(f"{retries} '{method_name}' processes returned 'retry'")
        if failures > 0 and retries == 0:
            return Result.fail(f"{failures} '{method_name}' processes failed")
        return Result.fail(
            f"{failures} '{method_name}' processes failed, and {retries} returned 'retry'"
        )

    def _save_result(
        self,
        method_name: str,
        plugin: HopprPlugin,
        result: Result,
        comp: Optional[Component],
    ):
        """
        Store the results for later use
        """
        comp_string = None
        if comp is not None:
            comp_purl = PackageURL.from_string(comp.purl)
            if comp_purl is not None:
                comp_string = comp_purl.to_string()

        # If needed, create a new list for this method
        # Might need to expand this definition in the future to separate by plug-in

        if not method_name in self.results:
            self.results[method_name] = []

        self.results[method_name].append(
            (plugin.__class__.__name__, comp_string, result)
        )

    def _load_plugins(self) -> List[HopprPlugin]:
        """
        Create a list consisting of a single instance of each plug-in class used in this stage
        """
        plugin_list = []
        for plugin_ref in self.plugin_ref_list:
            plugin_inst = plugin_instance(
                plugin_ref.name, self.context, plugin_ref.config
            )
            plugin_list.append(plugin_inst)

        return plugin_list


class HopprProcessor:  # pylint: disable=too-few-public-methods
    """
    Run the Hoppr process
    """

    @staticmethod
    def _create_logger() -> logging.Logger:
        """
        Creates a logger to stderr
        """

        logger_name: str = f"HopprProcessor--{os.getpid()}"

        new_logger = logging.getLogger(logger_name)
        new_logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        new_logger.addHandler(handler)
        return new_logger

    logger = _create_logger()

    def __init__(self, transfer: Transfer, manifest: Manifest) -> None:
        self.transfer = transfer
        self.manifest = manifest
        self.context: Context
        self.stages: Dict = {}
        self.metadata_files: List[Path] = []

    @classmethod
    def get_logger(cls):
        """
        Returns the logger for this class
        """
        return cls.logger

    def _collect_file(self, file_name, target_dir) -> None:
        self.get_logger().info(  # pylint: disable=logging-fstring-interpolation
            f"Collecting metadata file {file_name}"
        )
        abs_path = os.path.abspath(file_name)

        target = os.path.join(target_dir, urllib.parse.quote_plus(abs_path))
        shutil.copyfile(file_name, target)

    def _collect_url(self, url, target_dir) -> None:
        self.get_logger().info(  # pylint: disable=logging-fstring-interpolation
            f"Collecting metadata from url {url}"
        )
        target = os.path.join(target_dir, urllib.parse.quote_plus(url))
        download_file(url, target, None)

    def _collect_manifest_metadata(self, manifest: Manifest, target_dir) -> None:
        for (child_ref, child) in zip_longest(
            manifest.manifest_file_content.includes, manifest.children
        ):
            if child_ref.local is not None:
                self._collect_file(child_ref.local, target_dir)
            else:
                self._collect_url(child_ref.url, target_dir)

            self._collect_manifest_metadata(child, target_dir)

        for bom_ref in manifest.manifest_file_content.sbom_refs:
            if bom_ref.local is not None:
                self._collect_file(bom_ref.local, target_dir)
            else:
                self._collect_url(bom_ref.url, target_dir)

    def _collect_metadata(self):
        target_dir = f"{self.context.collect_root_dir}/generic/_metadata_/"
        os.makedirs(target_dir, exist_ok=True)

        if "nux" in platform.system():
            user = pwd.getpwuid(os.getuid())[0]
        else:
            user = os.getlogin()

        with open(target_dir + "_run_data_", "w", encoding="utf-8") as rundata:
            rundata.write(f"Collection Start: {str(datetime.now())}\n")
            rundata.write(f"User:             {user}\n")
            rundata.write(f"Host FQDN:        {socket.getfqdn()}\n")

        for file_name in self.metadata_files:
            self._collect_file(file_name, target_dir)

        self._collect_manifest_metadata(self.context.manifest, target_dir)

    def _collect_bom(self) -> None:
        target_dir = f"{self.context.collect_root_dir}/generic/_metadata_/"
        os.makedirs(target_dir, exist_ok=True)

        with open(
            os.path.join(target_dir, "_consolidated_bom.json"), "w", encoding="utf-8"
        ) as bom_data:
            bom_data.write(self.context.consolidated_sbom.json(by_alias=True, indent=2))

    def _summarize_results(self) -> int:
        """
        Summarize the results of a HopprProcess run
        """

        echo("\n========== Results Summary ==========")
        total_success_count = 0
        total_failure_count = 0
        for stage_id, stage in self.stages.items():
            echo(f"\nStage: {stage_id}")
            failure_list = "\n      Failure Summary:\n"
            for method_name, result_list in stage.results.items():
                echo(f"   {method_name}")
                result_count = len(result_list)
                failure_count = 0
                for plugin_name, comp_str, result in result_list:

                    # All retries should be handled internally by the plugins,
                    # So if a RETRY result is returned, that's a failure

                    if result.is_fail() or result.is_retry():
                        failure_count += 1
                        failure_list += f"         {plugin_name}: "
                        if comp_str is not None:
                            failure_list += f"Component: {comp_str}: "
                        failure_list += result.message + "\n"

                total_failure_count += failure_count
                total_success_count += result_count - failure_count
                echo(
                    f"      {result_count - failure_count} jobs succeeded, {failure_count} failed"
                )
                if failure_count > 0:
                    echo(failure_list)

        echo(
            f"\nGRAND TOTAL: {total_success_count} jobs succeeded, {total_failure_count} failed\n"
        )
        return total_failure_count

    def run(self) -> Result:
        """
        Run the Hoppr process executing each stage in turn
        """
        result = Result.success()

        with tempfile.TemporaryDirectory() as collection_root:

            self.context = Context(
                manifest=self.manifest,
                collect_root_dir=collection_root,
                consolidated_sbom=flatten_sboms(self.manifest),
                max_processes=cpu_count(),
            )
            if self.transfer.content:
                self.context.max_processes = self.transfer.content.max_processes

            self.get_logger().info(  # pylint: disable=logging-fstring-interpolation
                f"Beggining Hoppr Process execution, max_processes={self.context.max_processes}"
            )
            self._collect_metadata()

            if self.transfer.content is not None:
                for stage_ref in self.transfer.content.stages:
                    stage = StageProcessor(
                        stage_ref.name, self.context, stage_ref.plugins
                    )
                    self.stages[stage_ref.name] = stage
                    result = stage.run()
                    if result.is_fail() or result.is_retry():
                        self.logger.error(  # pylint: disable=logging-fstring-interpolation
                            f"Stage {stage_ref.name} failed, processing terminated: {result.message}"
                        )
                        break

                    self._collect_bom()

        failed_jobs = self._summarize_results()
        if failed_jobs > 0:
            result.merge(Result.fail(f"{failed_jobs} failed during this execution"))

        return result
