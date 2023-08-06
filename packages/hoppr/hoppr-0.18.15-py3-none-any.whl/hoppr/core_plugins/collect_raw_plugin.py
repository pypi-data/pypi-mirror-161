"""
Collector plugin for raw files
"""
import os
import shutil
import urllib
from pathlib import Path
from typing import Any

from packageurl import PackageURL  # type: ignore

from hoppr import __version__
from hoppr.base_plugins.collector import CollectorPlugin
from hoppr.base_plugins.hoppr import hoppr_rerunner
from hoppr.net import download_file
from hoppr.result import Result
from hoppr.types.cred_object import CredObject


class CollectRawPlugin(CollectorPlugin):
    """
    Collector plugin for raw files
    """

    supported_purl_types = ["binary", "generic", "raw"]

    def get_version(self) -> str:
        return __version__

    @hoppr_rerunner
    def collect(self, comp: Any, repo_url: str, creds: CredObject = None):
        """
        Copy a component to the local collection directory structure
        """
        source_url = os.path.join(repo_url)

        purl = PackageURL.from_string(comp.purl)
        subdir = None
        if purl.namespace is not None:
            source_url += urllib.parse.unquote(purl.namespace) + "/"
            subdir = urllib.parse.unquote(purl.namespace)

        target_dir = self.directory_for(purl.type, repo_url, subdir=subdir)

        file_name = urllib.parse.unquote(purl.name)

        if source_url.startswith("file://"):
            source_file = os.path.expanduser(source_url[7:] + file_name)
            if not Path(source_file).is_file():
                return Result.fail(f"Unable to locate file {source_file}")

            self.get_logger().info(
                f"Copying file from {source_file} to directory {target_dir}"
            )
            shutil.copy(source_file, target_dir)
            return Result.success()

        self.get_logger().info(
            f"Downloading from {source_url + file_name} to file {target_dir + file_name}"
        )
        download_creds = None
        if creds is not None:
            download_creds = (creds.username, creds.password)

        response = download_file(
            source_url + file_name, target_dir + file_name, download_creds
        )

        return Result.from_http_response(response)
