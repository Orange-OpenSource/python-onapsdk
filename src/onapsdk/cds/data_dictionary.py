# SPDX-License-Identifier: Apache-2.0
"""CDS data dictionary module."""

import json
from logging import getLogger, Logger

from onapsdk.exceptions import FileError, ValidationError

from .cds_element import CdsElement


class DataDictionary(CdsElement):
    """Data dictionary class."""

    logger: Logger = getLogger(__name__)

    def __init__(self, data_dictionary_json: dict, fix_schema: bool = True) -> None:
        """Initialize data dictionary.

        Args:
            data_dictionary_json (dict): data dictionary json
            fix_schema (bool, optional): determines if data dictionary should be fixed if
                the invalid schema is detected. Fixing can raise ValidationError if
                dictionary is invalid. Defaults to True.

        """
        super().__init__()
        self.data_dictionary_json: dict = data_dictionary_json
        if not self.has_valid_schema() and fix_schema:
            self.fix_schema()

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
        return f"{self._url}/api/v1/dictionary"

    def upload(self) -> None:
        """Upload data dictionary using CDS API."""
        self.logger.debug("Upload %s data dictionary", self.name)
        self.send_message(
            "POST",
            "Publish CDS data dictionary",
            f"{self.url}",
            auth=self.auth,
            data=json.dumps(self.data_dictionary_json)
        )

    def has_valid_schema(self) -> bool:
        """Check data dictionary json schema.

        Check data dictionary JSON and return bool if schema is valid or not.
            Valid schema means that data dictionary has given keys:
             - "name"
             - "tags"
             - "data_type"
             - "description"
             - "entry_schema"
             - "updatedBy"
             - "definition"
            "definition" key value should contains the "raw" data dictionary.

        Returns:
            bool: True if data dictionary has valid schema, False otherwise

        """
        return all(key_to_check in self.data_dictionary_json for
                   key_to_check in ["name", "tags", "data_type", "description", "entry_schema",
                                    "updatedBy", "definition"])

    def fix_schema(self) -> None:
        """Fix data dictionary schema.

        "Raw" data dictionary can be passed during initialization, but
            this kind of data dictionary can't be uploaded to blueprintprocessor.
            That method tries to fix it. It can be done only if "raw" data dictionary
            has a given schema:
                {
                    "name": "string",
                    "tags": "string",
                    "updated-by": "string",
                    "property": {
                        "description": "string",
                        "type": "string"
                    }
                }

        Raises:
            ValidationError: Data dictionary doesn't have all required keys

        """
        try:
            self.data_dictionary_json = {
                "name": self.data_dictionary_json["name"],
                "tags": self.data_dictionary_json["tags"],
                "data_type": self.data_dictionary_json["property"]["type"],
                "description": self.data_dictionary_json["property"]["description"],
                "entry_schema": self.data_dictionary_json["property"]["type"],
                "updatedBy": self.data_dictionary_json["updated-by"],
                "definition": self.data_dictionary_json
            }
        except KeyError:
            raise ValidationError("Raw data dictionary JSON has invalid schema")


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
            data_dictionary.upload()  # raise a relevant exception

    def save_to_file(self, dd_file_path: str) -> None:
        """Save data dictionaries to file.

        Args:
            dd_file_path (str): Data dictinary file path.
        """
        with open(dd_file_path, "w") as dd_file:
            dd_file.write(json.dumps([dd.data_dictionary_json for dd in self.dd_set], indent=4))

    @classmethod
    def load_from_file(cls, dd_file_path: str, fix_schema: bool = True) -> "DataDictionarySet":
        """Create data dictionary set from file.

        File has to have valid JSON with data dictionaries list.

        Args:
            dd_file_path (str): Data dictionaries file path.
            fix_schema (bool): Determines if schema should be fixed or not.

        Raises:
            FileError: File to load data dictionaries from doesn't exist.

        Returns:
            DataDictionarySet: Data dictionary set with data dictionaries from given file.

        """
        dd_set: DataDictionarySet = DataDictionarySet()

        try:
            with open(dd_file_path, "r") as dd_file:  # type file
                dd_json: dict = json.loads(dd_file.read())
                for data_dictionary in dd_json:  # type DataDictionary
                    dd_set.add(DataDictionary(data_dictionary, fix_schema=fix_schema))
            return dd_set
        except FileNotFoundError as exc:
            msg = "File with a set of data dictionaries does not exist."
            raise FileError(msg) from exc
