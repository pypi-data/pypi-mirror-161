"""
Plugin to create tar file bundle
"""
import os
import re
import tarfile
import time

from hoppr import __version__
from hoppr.base_plugins.hoppr import HopprPlugin, hoppr_process
from hoppr.result import Result


class TarBundlePlugin(HopprPlugin):
    """
    Plugin to create tar file bundle

    This plug-in supports the following config values:
       - compression: Specifies the compression to be applied to the output tar file.  Defaults
                      to "gz".  Recognized values are "none", "gzip", "gz", "bzip2", "bz",
                      "lmza", "xz"

        - tarfile_name: Name of the tar file to be created.  Defaults to "./bundle.tar.<comp>",
                        where <comp> is the short form of the compression used.  For "none"
                        compression, default is "./bundle.tar"
    """

    def get_version(self) -> str:
        return __version__

    @hoppr_process
    def post_stage_process(self):
        """
        Tar-up the context.collect_root_dir directory
        """

        compression = "gz"
        if self.config is not None:
            compression = self.config.get("compression", "gz").lower()

        if compression == "none":
            compression = ""
            default_filename = "./bundle.tar"
        elif compression in ["gzip", "gz"]:
            compression = "gz"
            default_filename = "./bundle.tar.gz"
        elif compression in ["bzip2", "bz"]:
            compression = "bz2"
            default_filename = "./bundle.tar.bz"
        elif compression in ["lzma", "xz"]:
            compression = "xz"
            default_filename = "./bundle.tar.xz"
        else:
            return Result.fail(f"Unrecognized compression in config: {compression}")

        root_dir = self.context.collect_root_dir

        tarfile_name = default_filename
        if self.config is not None:
            tarfile_name = self.config.get("tarfile_name", default_filename)
            tarfile_name = os.path.expanduser(tarfile_name)

        if os.path.exists(tarfile_name):
            timestr = time.strftime("%Y%m%d-%H%M%S")
            matches = re.search(r"^(.*?)(\.tar(\..*)?)?$", tarfile_name)

            if matches:
                tarfile_name = f"{matches.group(1)}-{timestr}{matches.group(2) if matches.group(2) is not None else ''}"

        self.get_logger().info(f"Bundling collected artifacts into {tarfile_name}")

        try:
            with tarfile.open(tarfile_name, f"x:{compression}") as tar:
                tar.add(root_dir, ".")
        except tarfile.ReadError as err:
            return Result.fail(f"Unable to create tarfile {tarfile_name}, {err}")
        except FileNotFoundError:
            return Result.fail(f"File {tarfile_name}: Directory not found.")
        except PermissionError:
            return Result.fail(f"File {tarfile_name}: Permission denied.")

        return Result.success()
