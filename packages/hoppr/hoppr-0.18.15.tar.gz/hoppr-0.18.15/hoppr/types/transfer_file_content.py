"""
TransferType dataclass and constructor
"""

from dataclasses import dataclass
from multiprocessing import cpu_count
from typing import Optional


@dataclass
class Plugin:
    """
    Plugin Dataclass containing name and optional config
    """

    name: str
    config: Optional[dict]

    def __init__(self, name: str, config: Optional[dict] = None) -> None:
        self.name = name
        self.config = config


@dataclass
class Stage:
    """
    Stage Dataclass containing an array of plugins
    """

    name: str
    plugins: list[Plugin]

    def __init__(self, name: str, plugins: list[dict]) -> None:
        self.name = name
        self.plugins = []
        for plugin in plugins:
            self.plugins.append(Plugin(**plugin))


class TransferFileContent:  # pylint: disable="too-few-public-methods"
    """
    Transfer data type class to construct TransferType Object
    """

    schema_version: str
    kind: str
    stages: list[Stage]
    max_processes: int

    def __init__(
        self,
        schemaVersion: str,  # pylint: disable="invalid-name"
        kind: str,
        stages: dict,
        max_processes: Optional[int] = None,
    ) -> None:
        self.schema_version = schemaVersion
        self.kind = kind
        self.stages = []
        for name, stage in stages.items():
            self.stages.append(Stage(name, stage))

        self.max_processes = cpu_count()
        if max_processes is not None:
            self.max_processes = max_processes
