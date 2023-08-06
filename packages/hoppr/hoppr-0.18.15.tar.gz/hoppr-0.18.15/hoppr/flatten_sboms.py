"""
Flatten sboms
"""

# Enable forward definitions
from __future__ import annotations

import json
from typing import Optional

from packageurl import PackageURL  # type: ignore

from hoppr.configs.manifest import Manifest
from hoppr.types.cyclonedx_1_3 import (
    CyclonedxSoftwareBillOfMaterialSpecification as Bom_1_3,
)
from hoppr.types.cyclonedx_1_4 import Component as Component_1_4
from hoppr.types.cyclonedx_1_4 import (
    CyclonedxSoftwareBillOfMaterialsStandard as Bom_1_4,
)
from hoppr.types.cyclonedx_1_4 import ExternalReference, Property
from hoppr.types.manifest_file_content import Repositories
from hoppr.types.purl_type import PurlType


def to_current_component(source) -> Component_1_4:
    """
    Convert a CycloneDx component to the most current version (currently 1.4)
    """
    comp_json = source.json(by_alias=True)
    return Component_1_4.parse_raw(comp_json)


def merge_sbom(  # pylint: disable="too-many-branches"
    merged: Bom_1_4,
    to_insert: Bom_1_4 | Bom_1_3,
    to_insert_ref: Optional[str] = None,
    consolidated_repositories: Optional[Repositories] = None,
):
    """
    Add sboms
    """
    new_external_ref = None
    if to_insert_ref is not None:
        new_external_ref = ExternalReference(
            url=to_insert_ref,
            type="bom",
            comment=to_insert.serialNumber,
        )

    if to_insert.components is not None:
        if merged.components is None:
            merged.components = []

        for to_insert_comp_orig in to_insert.components:
            if to_insert_comp_orig is None or to_insert_comp_orig.purl is None:
                continue

            to_insert_comp = to_current_component(to_insert_comp_orig)

            merged_comp = None
            for comp in merged.components:
                if comp.purl is not None and comp.purl == to_insert_comp.purl:
                    merged_comp = comp

            if merged_comp is None:
                merged_comp = to_insert_comp
                merged.components.append(merged_comp)
            else:
                # TODO merge the two components # pylint: disable="fixme"
                external_ref_dict = {}
                for external_ref in (merged_comp.externalReferences or []) + (
                    to_insert_comp.externalReferences or []
                ):
                    external_ref_dict.update({external_ref.url: external_ref})

                merged_comp.externalReferences = list(external_ref_dict.values())

            if new_external_ref is not None:
                if merged_comp.externalReferences is None:
                    merged_comp.externalReferences = []
                merged_comp.externalReferences.append(new_external_ref)

            if consolidated_repositories is not None:
                purltype = PackageURL.from_string(to_insert_comp.purl).type
                search_sequence = {
                    "version": "v1",
                    "Repositories": [
                        repo.url
                        for repo in consolidated_repositories[PurlType(purltype)]
                    ],
                }
                if merged_comp.properties is None:
                    merged_comp.properties = []
                merged_comp.properties.append(
                    Property(
                        name="hoppr:repository:component_search_sequence",
                        value=json.dumps(search_sequence),
                    )
                )

    return merged


def flatten_sboms(manifest: Manifest) -> Bom_1_4:
    """
    Flatten (dedupe) sboms
    """
    flat_sbom = Bom_1_4(specVersion="1.4", version=1, bomFormat="CycloneDX")
    for index, to_insert_sbom in enumerate(manifest.sboms):

        sbom_ref = manifest.manifest_file_content.sbom_refs[index]
        if sbom_ref.local is not None:
            to_insert_sbom_ref = sbom_ref.local
        elif sbom_ref.url is not None:
            to_insert_sbom_ref = sbom_ref.url
        else:  # pragma: no cover
            to_insert_sbom_ref = None

        flat_sbom = merge_sbom(
            flat_sbom,
            to_insert_sbom,
            to_insert_sbom_ref,
            manifest.consolidated_repositories,
        )
    for child_manifest in manifest.children:
        merge_sbom(flat_sbom, flatten_sboms(child_manifest))

    return flat_sbom
