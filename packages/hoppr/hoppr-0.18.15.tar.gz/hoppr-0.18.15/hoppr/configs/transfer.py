"""
Transfer business logic
"""

# Enable forward definitions
from __future__ import annotations

from hoppr import utils
from hoppr.types.transfer_file_content import TransferFileContent


class Transfer:
    """
    Transfer business logic class
    """

    def __init__(self) -> None:
        self.content = None

    @staticmethod
    def load_file(file) -> Transfer:
        """
        Creates a transfer object from a file
        """
        input_dict = utils.load_file(file)
        transfer = Transfer()
        transfer.populate(input_dict)

        return transfer

    def populate(self, input_dict):
        """
        Populates Transfer object with dictionary contents.
        """

        self.content = TransferFileContent(**input_dict)
