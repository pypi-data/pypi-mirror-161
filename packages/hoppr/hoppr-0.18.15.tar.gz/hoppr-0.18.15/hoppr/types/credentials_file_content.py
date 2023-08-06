"""
ManifestType dataclass and constructor
"""

from dataclasses import dataclass
from typing import Optional, Set


@dataclass
class CredentialRequiredService:
    """
    CredentialRequiredService
    """

    url: str
    user: Optional[str]
    user_env: Optional[str]
    pass_env: str

    def __init__(
        self, url: str = "", user: str = None, user_env: str = None, pass_env: str = ""
    ) -> None:
        self.url = url
        self.user = user
        self.user_env = user_env
        self.pass_env = pass_env

    def __hash__(self):
        """
        Hash must be defined to allow Repository objects to be included in a set
        """
        return hash(repr(self))


@dataclass
class CredentialMetadata:  # pylint: disable="duplicate-code"
    """
    CredentialMetadata Dataclass containing name, version, description
    """

    name: str
    version: str
    description: str

    def __init__(self, name: str, version: str, description: str) -> None:
        self.name = name
        self.version = version
        self.description = description


class CredentialFileContent:  # pylint: disable="too-few-public-methods"
    """
    Manifest data type class to construct ManifestType Object
    """

    schema_version: str
    kind: str
    metadata: CredentialMetadata
    credential_required_services: Set[CredentialRequiredService]

    def __init__(
        self,
        schemaVersion: str,  # pylint: disable="invalid-name"
        kind: str,
        metadata: dict,
        credential_required_services: Set[dict],
    ) -> None:
        self.schema_version = schemaVersion
        self.kind = kind
        self.metadata = CredentialMetadata(**metadata)
        self.credential_required_services = {
            CredentialRequiredService(**service)
            for service in credential_required_services
        }
