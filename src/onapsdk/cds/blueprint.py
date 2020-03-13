# SPDX-License-Identifier: Apache-2.0
"""CDS Blueprint module."""
from typing import Generator

from .cds_element import CdsElement
from .data_dictionary import DataDictionary


class Blueprint(CdsElement):
    """CDS blueprint representation."""

    def __init__(self, cba_file_bytes: bytes) -> None:
        """Blueprint initialization.

        Save blueprint zip file bytes.
        You can create that object using opened file or bytes:
            blueprint = Blueprint(open("path/to/CBA.zip", "rb"))
        or
            with open("path/to/CBA.zip", "rb") as cba:
                blueprint = Blueprint(cba.read())
        It is even better to use second example due to CBA file will be correctly closed for sure.

        Args:
            cba_file_bytes (bytes): CBA ZIP file bytes
        """
        super().__init__()
        self.cba_file_bytes: bytes = cba_file_bytes

    @property
    def url(self) -> str:
        """URL address to use for CDS API call.

        Returns:
            str: URL to CDS blueprintprocessor.

        """
        return self._url

    @classmethod
    def load_from_file(cls, cba_file_path: str) -> "Blueprint":
        """Load blueprint from file.

        Raises:
            FileNotFoundError: File to load blueprint from doesn't exist

        Returns:
            Blueprint: Blueprint object

        """
        with open(cba_file_path, "rb") as cba_file:
            return Blueprint(cba_file.read())

    def enrich(self) -> "Blueprint":
        """Call CDS API to get enriched blueprint file.

        Returns:
            Blueprint: Enriched blueprint object

        """
        response: "requests.Response" = self.send_message(
            "POST",
            "Enrich CDS blueprint",
            f"{self.url}/blueprint-model/enrich",
            files={"file": self.cba_file_bytes},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth,
        )
        if response is None:
            raise AttributeError("Can't enrich blueprint, look on logs to get more information")
        return Blueprint(response.content)

    def publish(self) -> None:
        """Publish blueprint."""
        self.send_message(
            "POST",
            "Publish CDS blueprint",
            f"{self.url}/blueprint-model/publish",
            files={"file": self.cba_file_bytes},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth,
        )

    def deploy(self) -> None:
        """Deploy bluepirint using CDS API."""
        self.send_message(
            "POST",
            "Deploy CDS blueprint",
            f"{self.url}/execution-service/upload",
            files={"file": self.cba_file_bytes},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth,
        )

    def save(self, dest_file_path: str) -> None:
        """Save blueprint to file.

        Args:
            dest_file_path (str): Path of file where blueprint is going to be saved
        """
        with open(dest_file_path, "wb") as cba_file:
            cba_file.write(self.cba_file_bytes)

    def get_data_dictionaries(self) -> Generator[DataDictionary, None, None]:
        """Get the generator of data dictionaries required by blueprint.

        If mapping reqires other source than input it should be updated before upload to CDS.

        Returns:
            Generator[DataDictionary, None, None]: DataDictionary objects.

        """
        raise NotImplementedError
