"""
Enumeration of supported purl types
"""

from enum import Enum


class PurlType(Enum):
    """
    Enumeration of supported purl types
    """

    DOCKER = "docker"
    GIT = "git"
    GITHUB = "github"
    GITLAB = "gitlab"
    GOLANG = "golang"
    HELM = "helm"
    RPM = "rpm"
    PYPI = "pypi"
    MAVEN = "maven"
    GENERIC = "generic"
    APT = "apt"
