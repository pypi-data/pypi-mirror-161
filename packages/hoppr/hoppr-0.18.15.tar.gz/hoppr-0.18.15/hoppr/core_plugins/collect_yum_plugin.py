"""
Collector plugin for docker images
"""
import urllib
from typing import Any, Dict, Optional

from packageurl import PackageURL  # type: ignore

from hoppr import __version__
from hoppr.base_plugins.collector import CollectorPlugin
from hoppr.base_plugins.hoppr import hoppr_rerunner
from hoppr.context import Context
from hoppr.result import Result


class CollectYumPlugin(CollectorPlugin):
    """
    Collector plugin for yum images
    """

    supported_purl_types = ["rpm"]
    required_commands = ["yumdownloader"]

    def get_version(self) -> str:
        return __version__

    def __init__(self, context: Context, config: Optional[Dict] = None) -> None:
        super().__init__(context=context, config=config)
        if self.config is not None:
            if "yumdownloader_command" in self.config:
                self.required_commands = [self.config["yumdownloader_command"]]

    @hoppr_rerunner
    def collect(self, comp: Any, repo_url: str, creds=None):
        """
        Copy a component to the local collection directory structure
        """

        purl = PackageURL.from_string(comp.purl)

        file_name = urllib.parse.unquote(purl.name)
        target_dir = self.directory_for(purl.type, repo_url, subdir=f"{purl.namespace}")

        self.get_logger().info(f"Copying yum package from {purl} to {target_dir}")

        command = [
            self.required_commands[0],
            "-q",
            "--disableexcludes=all",
            "--downloadonly",
            "--urls",
            file_name,
        ]

        result = self.run_command(command)
        if result.returncode != 0:
            msg = f"Yum failed to copy package to {target_dir}, return_code={result.returncode}"
            self.get_logger().error(msg)

            return Result.retry(msg)

        # Taking the first URL if multiple are returned
        found_url = result.stdout.decode("utf-8").strip().split("\n")[0]

        if not found_url.startswith(repo_url):
            msg = (
                "Yum download url does not match requested url.\n"
                + f"   Yum download url:      {found_url}\n"
                + f"   Expected url starting: {repo_url}"
            )
            self.get_logger().error(msg)
            return Result.fail(msg)

        command = [
            self.required_commands[0],
            "-q",
            "--disableexcludes=all",
            "--downloadonly",
            f"--destdir={target_dir}",
            file_name,
        ]

        result = self.run_command(command, [])
        if result.returncode != 0:
            msg = f"Failed to download Yum artifact {purl.name} version {purl.version} "
            return Result.retry(msg)

        return Result.success()
