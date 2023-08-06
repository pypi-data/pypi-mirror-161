"""
Hoppr Network utility functions
"""

import requests
from requests.auth import HTTPBasicAuth

from hoppr.configs.credentials import Credentials
from hoppr.exceptions import HopprLoadDataError
from hoppr.types.cred_object import CredObject
from hoppr.utils import load_string


def load_url(url: str, creds: CredObject = None):
    """
    Load config content (either json or yml) from a url into a dict
    """
    if creds is None:
        creds = Credentials.find_credentials(url)

    response = None
    if creds is not None:
        authorization_headers = {
            "PRIVATE-TOKEN": creds.password,
            "Authorization": f"Bearer {creds.password}",
        }
        basic_auth = HTTPBasicAuth(username=creds.username, password=creds.password)
        response = requests.get(url, auth=basic_auth, headers=authorization_headers)
    else:
        response = requests.get(url)

    response.raise_for_status()
    valid_data = True
    try:
        if isinstance(response.content, bytes):
            data = load_string(response.content.decode("utf-8"))
            return data
        if isinstance(response.content, str):
            data = load_string(response.content)
            return data
        valid_data = False
    except HopprLoadDataError as parse_error:
        message = f"Unable to parse result from {url}."
        if response.url != url:
            message += (
                f" Request was redirected to {response.url}. "
                + "An auth issue might have occurred."
            )
        raise HopprLoadDataError(message) from parse_error

    if not valid_data:
        raise HopprLoadDataError("Response type is not bytes or str")

    return None  # pragma: no cover


def download_file(url, dest, creds=None):
    """
    Download content from a url into a file
    """
    if creds is None:
        creds = Credentials.find_credentials(url)

    basic_auth = None
    if creds is not None:
        basic_auth = HTTPBasicAuth(username=creds.username, password=creds.password)

    response = requests.get(
        url, auth=basic_auth, allow_redirects=True, stream=True, verify=True
    )

    if 200 <= response.status_code and response.status_code < 300:
        with open(dest, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)

    return response
