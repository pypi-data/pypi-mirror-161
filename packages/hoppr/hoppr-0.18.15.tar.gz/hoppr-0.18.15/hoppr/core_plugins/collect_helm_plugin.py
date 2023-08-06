"""
Collector plugin for helm charts
"""
import os
from typing import Any, Dict, Optional

from packageurl import PackageURL  # type: ignore

from hoppr import __version__
from hoppr.base_plugins.collector import CollectorPlugin
from hoppr.base_plugins.hoppr import hoppr_rerunner
from hoppr.context import Context
from hoppr.result import Result
from hoppr.types.cred_object import CredObject


class CollectHelmPlugin(CollectorPlugin):
    """
    Class to copy helm charts
    """

    supported_purl_types = ["helm"]
    required_commands = ["helm"]

    def get_version(self) -> str:  # pylint: disable=duplicate-code
        return __version__

    def __init__(self, context: Context, config: Optional[Dict] = None) -> None:
        super().__init__(context=context, config=config)
        if self.config is not None:
            if "helm_command" in self.config:
                self.required_commands = [self.config["helm_command"]]

    @hoppr_rerunner
    def collect(
        self, comp: Any, repo_url: str, creds: CredObject = None
    ):  # pylint: disable=duplicate-code
        """
        Collect helm chart
        """

        purl = PackageURL.from_string(comp.purl)

        self.get_logger().info(f"Copying helm chart from {repo_url}")

        source_url = os.path.join(repo_url, purl.name)
        target_dir = self.directory_for(
            purl.type, repo_url, subdir=f"{purl.name}_{purl.version}"
        )

        command = [
            "helm",
            "fetch",
            "--repo",
            source_url,
            "-d",
            target_dir,
            purl.name,
            "--version",
            purl.version,
        ]

        password_list = []
        if creds is not None:
            command = command + [
                "--username",
                creds.username,
                "--password",
                creds.password,
            ]
            password_list = [creds.password]

        result = self.run_command(command, password_list)
        if result.returncode != 0:
            # pylint: disable=duplicate-code
            msg = f"Failed to download {purl.name} version {purl.version} helm chart"
            self.get_logger().error(msg)
            return Result.retry(msg)

        self.get_logger().info(
            "Complete helm chart artifact copy for {purl.to_string()}"
        )

        return Result.success()
