# SPDX-License-Identifier: Apache-2.0
"""CDS data dictionary module."""

import json
from logging import getLogger, Logger

from .cds_element import CdsElement


class DataDictionary(CdsElement):
    """Data dictionary class."""

    logger: Logger = getLogger(__name__)

    def __init__(self, data_dictionary_json: dict) -> None:
        """Initialize data dictionary."""
        super().__init__()
        self.data_dictionary_json: dict = data_dictionary_json

    def __hash__(self) -> int:  # noqa: D401
        """Data dictionary object hash.

        Based on data dictionary name

        Returns:
            int: Data dictionary hash

        """
        return hash(self.name)

    def __eq__(self, dd: "DataDictionary") -> bool:
        """Compare two data dictionaries.

        Data dictionaries are equal if have the same name.

        Args:
            dd (DataDictionary): Object to compare with.

        Returns:
            bool: True if objects have the same name, False otherwise.

        """
        return self.name == dd.name

    def __repr__(self) -> str:
        """Representation of object.

        Returns:
            str: Object's string representation

        """
        return f'DataDictionary[name: "{self.name}"]'

    @property
    def name(self) -> str:  # noqa: D401
        """Data dictionary name.

        Returns:
            str: Data dictionary name

        """
        return self.data_dictionary_json["name"]

    @property
    def url(self) -> str:
        """URL to call.

        Returns:
            str: CDS dictionary API url

        """
        return f"{self._url}/resourcedictionary"

    def upload(self) -> None:
        """Upload data dictionary using CDS API.

        Raises:
            RuntimeError: CDS API returns error on upload.

        """
        self.logger.debug("Upload %s data dictionary", self.name)
        response: "requests.Response" = self.send_message(
            "POST",
            "Publish CDS data dictionary",
            f"{self.url}/save",
            data=json.dumps(self.data_dictionary_json),
        )
        if response is None:
            raise RuntimeError(f"Data dictionary {self.name} not uploaded")


class DataDictionarySet:
    """Data dictionary set.

    Stores data dictionary and upload to server.
    """

    logger: Logger = getLogger(__name__)

    def __init__(self) -> None:
        """Initialize data dictionary set."""
        self.dd_set = set()

    @property
    def length(self) -> int:
        """Get the length of data dicitonary set.

        Returns:
            int: Number of data dictionaries in set

        """
        return len(self.dd_set)

    def add(self, data_dictionary: DataDictionary) -> None:
        """Add data dictionary object to set.

        Based on name it won't add duplications.

        Args:
            data_dictionary (DataDictionary): object to add to set.

        """
        self.dd_set.add(data_dictionary)

    def upload(self) -> None:
        """Upload all data dictionaries using CDS API.

        Raises:
            RuntimeError: Raises if any data dictionary won't be uploaded to server.
                Data dictionaries uploaded before the one which raises excepion won't be
                deleted from server.

        """
        self.logger.debug("Upload data dictionary")
        for data_dictionary in self.dd_set:  # type DataDictionary
            data_dictionary.upload()

    def save_to_file(self, dd_file_path: str) -> None:
        """Save data dictionaries to file.

        Args:
            dd_file_path (str): Data dictinary file path.
        """
        with open(dd_file_path, "w") as dd_file:
            dd_file.write(json.dumps([dd.data_dictionary_json for dd in self.dd_set], indent=4))

    @classmethod
    def load_from_file(cls, dd_file_path: str) -> None:
        """Create data dictionary set from file.

        File has to have valid JSON with data dictionaries list.

        Args:
            dd_file_path (str): Data dictionaries file path.

        Raises:
            FileNotFoundError: File to load data dictionaries from doesn't exist

        Returns:
            [type]: Data dictionary set with data dictionaries from given file

        """
        dd_set: DataDictionarySet = DataDictionarySet()
        with open(dd_file_path, "r") as dd_file:  # type file
            dd_json: dict = json.loads(dd_file.read())
            for data_dictionary in dd_json:  # type DataDictionary
                dd_set.add(DataDictionary(data_dictionary))
        return dd_set
