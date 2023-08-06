"""
Credentials Global Store
"""

# Enable forward definitions
from __future__ import annotations

from os import environ
from typing import Optional

from hoppr import utils
from hoppr.exceptions import HopprCredentialsError
from hoppr.types.cred_object import CredObject
from hoppr.types.credentials_file_content import (
    CredentialFileContent,
    CredentialRequiredService,
)


class Credentials:
    """
    Credentials Global Store
    """

    __content = None

    @staticmethod
    def get_content():
        """
        Access the credentials file content
        """
        return Credentials.__content

    @staticmethod
    def load_file(file):
        """
        Creates a credentials object from a file
        """
        input_dict = utils.load_file(file)
        Credentials.__content = CredentialFileContent(**input_dict)

    @staticmethod
    def find_credentials(url=None) -> Optional[CredObject]:
        """
        Method to find credentials that match the provided URL.
        The longest matching in the authentication object should be used.
        """

        # Find the longest "url" in the auth list that is within the "url"
        matching_service = CredentialRequiredService(url="")

        if Credentials.__content:
            for service in Credentials.__content.credential_required_services:
                if service.url in url:
                    if len(service.url) > len(matching_service.url):
                        matching_service = service

        # If no match was found, return found == False
        if matching_service.url != "":
            pass_env = matching_service.pass_env
            if pass_env not in environ:
                raise HopprCredentialsError(
                    Credentials.__content,
                    url,
                    f"'{pass_env}' not found in environment variables.",
                )

            return CredObject(
                username=str(matching_service.user), password=environ[str(pass_env)]
            )

        return None
