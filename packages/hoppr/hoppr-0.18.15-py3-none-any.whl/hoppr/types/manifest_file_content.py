"""
ManifestType dataclass and constructor
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, TypeAlias

from hoppr.exceptions import HopprLoadDataError
from hoppr.types.purl_type import PurlType
from hoppr.utils import dedup_list


@dataclass
class Include:
    """
    Include dataclass containing url or local file reference
    """

    url: Optional[str]
    local: Optional[str]

    def __init__(self, url: str = None, local: str = None) -> None:
        self.url = url
        self.local = local

    def __hash__(self):
        """
        Hash must be defined to allow Include objects to be included in a set
        """
        return hash(repr(self))


@dataclass
class Metadata:
    """
    Metadata Dataclass containing name, version, description
    """

    name: str
    version: str
    description: str

    def __init__(self, name: str, version: str, description: str) -> None:
        self.name = name
        self.version = version
        self.description = description


@dataclass
class SBOMRef:
    """
    SBOM dataclass containing url or local file reference
    """

    url: Optional[str]
    local: Optional[str]

    def __init__(self, url: str = None, local: str = None) -> None:
        self.url = url
        self.local = local

    def __hash__(self):
        """
        Hash must be defined to allow SBOM objects to be included in a set
        """
        return hash(repr(self))


@dataclass
class Repository:
    """
    Repository Dataclass taking url and description
    """

    url: str
    description: str

    def __init__(self, url: str, description: str) -> None:
        self.url = url
        self.description = description

    def __hash__(self):
        """
        Hash must be defined to allow Repository objects to be included in a set
        """
        return hash(repr(self))


Repositories: TypeAlias = Dict[PurlType, List[Repository]]


class ManifestFileContent:  # pylint: disable="too-few-public-methods"
    """
    Manifest data type class to construct ManifestType Object
    """

    schema_version: str
    kind: str
    metadata: Metadata
    sbom_refs: List[SBOMRef]
    includes: List[Include]
    repositories: Repositories

    def __init__(  # pylint: disable="too-many-arguments"
        self,
        schemaVersion: str,  # pylint: disable="invalid-name"
        kind: str,
        metadata: dict,  # pylint: disable="duplicate-code"
        sboms: List[dict],
        includes: List[dict],
        repositories: dict,
    ) -> None:
        self.schema_version = schemaVersion
        self.kind = kind
        self.metadata = Metadata(**metadata)
        self.sbom_refs = dedup_list([SBOMRef(**sbom_ref) for sbom_ref in sboms])
        self.includes = dedup_list([Include(**include) for include in includes])
        self.repositories = {}
        for purl_type_enum in PurlType:
            self.repositories[purl_type_enum] = []

        for purl_type in repositories:
            for repository in repositories[purl_type]:
                try:
                    self.repositories[PurlType(purl_type)].append(
                        Repository(url=repository["url"], description=purl_type)
                    )
                except ValueError as value_error:
                    raise HopprLoadDataError(
                        f"Purl type {purl_type} is not supported"
                    ) from value_error

        for purl_type_enum in PurlType:
            self.repositories[purl_type_enum] = dedup_list(
                self.repositories[purl_type_enum]
            )
