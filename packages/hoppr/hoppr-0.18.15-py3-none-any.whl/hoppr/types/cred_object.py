"""
Define an object for a single set of credentials
"""

from dataclasses import dataclass


@dataclass
class CredObject:
    """
    Define credential details for a single set of credentials
    """

    username: str
    password: str
