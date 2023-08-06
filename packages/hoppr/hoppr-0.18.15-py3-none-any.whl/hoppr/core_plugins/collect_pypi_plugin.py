"""
Collector plugin for pypi images
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


class CollectPypiPlugin(CollectorPlugin):
    """
    Collector plugin for pypi images
    """

    supported_purl_types = ["pip", "pypi"]
    required_commands = ["pip"]

    def get_version(self) -> str:  # pylint: disable=duplicate-code
        return __version__

    def __init__(self, context: Context, config: Optional[Dict] = None) -> None:
        super().__init__(context=context, config=config)
        if self.config is not None:
            if "pip_command" in self.config:
                self.required_commands = [self.config["pip_command"]]

    @hoppr_rerunner
    def collect(self, comp: Any, repo_url: str, creds: CredObject = None):
        """
        Copy a component to the local collection directory structure
        """
        purl = PackageURL.from_string(comp.purl)
        if not repo_url.endswith("simple") or repo_url.endswith("simple/"):
            source_url = os.path.join(repo_url, "simple")
        password_list = []
        if creds is not None:
            source_url = source_url.replace(
                "://", f"://{creds.username}:{creds.password}@", 1
            )
            password_list = [creds.password]

        target_dir = self.directory_for(
            purl.type, repo_url, subdir=f"{purl.name}_{purl.version}"
        )

        self.get_logger().info(
            f"Copying pypi artifact {purl.name}:{purl.version} from {repo_url} to {target_dir}"
        )

        command = [
            self.required_commands[0],
            "download",
            "--no-deps",
            f"{purl.name}=={purl.version}",
            "--index-url",
            source_url,
            "-d",
            target_dir,
            "--no-cache",
            "--timeout",
            "60",
            "--only-binary=:all:",
        ]

        got_binary = True

        result = self.run_command(command, password_list)
        if result.returncode != 0:
            self.get_logger().error(
                f"Failed to download {purl.name} version {purl.version} binary"
            )
            got_binary = False

        command[-1] = "--no-binary=:all:"

        result = self.run_command(command, password_list)
        if result.returncode != 0:
            self.get_logger().error(
                f"Failed to download {purl.name} version {purl.version} source"
            )
            if not got_binary:
                msg = (
                    f"Failed to download {purl.name} version {purl.version} "
                    + "as either whl or source."
                )
                return Result.retry(msg)

        return Result.success()
