"""
Manifest business logic
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from typer import echo

from hoppr import net, utils
from hoppr.exceptions import HopprLoadDataError
from hoppr.types.cyclonedx_1_3 import (
    CyclonedxSoftwareBillOfMaterialSpecification as Bom_1_3,
)
from hoppr.types.cyclonedx_1_4 import (
    CyclonedxSoftwareBillOfMaterialsStandard as Bom_1_4,
)
from hoppr.types.manifest_file_content import ManifestFileContent, Repositories
from hoppr.types.purl_type import PurlType
from hoppr.utils import dedup_list

# Enable forward definitions


class Manifest:
    """
    Manifest business logic class
    """

    loaded_manifests: List[str] = []

    def __init__(self) -> None:
        self.manifest_file_content: ManifestFileContent
        self.sboms: List[Bom_1_4 | Bom_1_3] = []
        self.parent: Optional[Manifest] = None
        self.children: List["Manifest"] = []
        self.consolidated_repositories: Repositories

    @staticmethod
    def merge_repositories(
        first: Repositories,
        second: Repositories,
    ):
        """
        Add repos
        """
        combined: Repositories = {}
        for purl_type in PurlType:
            combined[purl_type] = dedup_list(first[purl_type] + second[purl_type])

        return combined

    @staticmethod
    def load_file(file: Path, parent: Optional[Manifest] = None) -> Manifest:
        """
        Creates a manifest object from a file
        """
        Manifest.loaded_manifests.append(str(file.resolve()))
        input_dict = utils.load_file(file)
        manifest = Manifest()
        manifest.populate(input_dict, parent)
        return manifest

    @staticmethod
    def load_url(url, parent: Optional[Manifest] = None) -> Manifest:
        """
        Creates a manifest object from a url
        """
        input_dict = net.load_url(url)
        manifest = Manifest()
        manifest.populate(input_dict, parent)
        return manifest

    @staticmethod
    def load_manifest(
        manifest_location,
        parent: Optional[Manifest] = None,
    ) -> Manifest:
        """
        Loads manifest
        """
        if manifest_location.url is not None:
            child_manifest = Manifest.load_url(manifest_location.url, parent)
        if manifest_location.local is not None:
            local_path = Path(manifest_location.local)
            child_manifest = Manifest.load_file(local_path, parent)

        return child_manifest

    @staticmethod
    def load_sbom(sbom_location) -> Bom_1_4 | Bom_1_3:
        """
        Loads SBOM from urls and files
        """

        if sbom_location.local is not None:
            sbom_file_object = utils.load_file(Path(sbom_location.local))
        elif sbom_location.url is not None:
            sbom_file_object = net.load_url(sbom_location.url)
        else:
            raise HopprLoadDataError(f"Unsupported SBOM Location {sbom_location}")

        spec_version = sbom_file_object.get("specVersion", "")

        if spec_version == "1.4":
            return Bom_1_4(**sbom_file_object)
        if spec_version == "1.3":
            return Bom_1_3(**sbom_file_object)
        raise HopprLoadDataError(
            f"{sbom_location} is an unknown spec version ({spec_version})"
        )

    def build_repository_search(self) -> None:
        """
        Builds the computed repository search sequence for a parent and child manifest
        """
        if self.parent is None:
            self.consolidated_repositories = self.manifest_file_content.repositories
        else:
            self.consolidated_repositories = self.merge_repositories(
                self.parent.consolidated_repositories,
                self.manifest_file_content.repositories,
            )

    def populate(
        self,
        input_dict,
        parent: Optional[Manifest] = None,
    ):
        """
        Populates Manifest object with dictionary contents.
        """

        self.manifest_file_content = ManifestFileContent(**input_dict)
        self.parent = parent

        if self.manifest_file_content is not None:
            for sbom_ref in self.manifest_file_content.sbom_refs:
                self.sboms.append(Manifest.load_sbom(sbom_ref))

            self.build_repository_search()

            for include in self.manifest_file_content.includes:
                if (
                    include.url or str(Path(str(include.local)).resolve())
                ) in Manifest.loaded_manifests:
                    echo(
                        f"WARNING: Manifest file '{include.url or include.local}' "
                        + "has already been loaded.  Subsequent load requests ignored."
                    )
                else:
                    child = self.load_manifest(include, self)
                    self.children.append(child)
