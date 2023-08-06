"""
Collector plugin for docker images
"""
import os
import re
import urllib
from typing import Any, Dict, Optional

from packageurl import PackageURL  # type: ignore

from hoppr import __version__
from hoppr.base_plugins.collector import CollectorPlugin
from hoppr.base_plugins.hoppr import hoppr_rerunner
from hoppr.context import Context
from hoppr.result import Result
from hoppr.types.cred_object import CredObject


class CollectDockerPlugin(CollectorPlugin):
    """
    Collector plugin for docker images
    """

    supported_purl_types = ["docker"]
    required_commands = ["skopeo"]

    def get_version(self) -> str:  # pylint: disable=duplicate-code
        return __version__

    def __init__(self, context: Context, config: Optional[Dict] = None) -> None:
        super().__init__(context=context, config=config)
        if self.config is not None:
            if "skopeo_command" in self.config:
                self.required_commands = [self.config["skopeo_command"]]

    @hoppr_rerunner
    def collect(self, comp: Any, repo_url: str, creds: CredObject = None):
        """
        Copy a component to the local collection directory structure
        """
        purl = PackageURL.from_string(comp.purl)
        purl_id = purl.name + ":" + purl.version
        source_url = os.path.join(repo_url, purl.namespace, purl_id)
        source_url = re.sub(r"^https?://", "", source_url)
        if not source_url.startswith("docker://"):
            source_url = "docker://" + source_url

        file_name = urllib.parse.unquote(purl.name) + "_" + purl.version
        target_dir = self.directory_for(purl.type, repo_url, subdir=purl.namespace)
        destination = "docker-archive:" + os.path.join(target_dir, file_name)

        self.get_logger().info(
            f"Copying docker image from {source_url} to {destination}"
        )

        command = [self.required_commands[0], "copy"]

        password_list = []
        if creds is not None:
            password_list = [creds.password]
            command.extend(["--src-creds", f"{creds.username}:{creds.password}"])

        if re.match("^http://", repo_url):
            command.append("--src-tls-verify=false")

        command.extend([source_url, destination])

        proc = self.run_command(command, password_list)

        if proc.returncode != 0:
            msg = (
                f"Skopeo failed to copy docker image to {destination}, "
                + f"return_code={proc.returncode}"
            )
            self.get_logger().error(msg)
            return Result.retry(msg)

        return Result.success()
