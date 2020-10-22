# SPDX-License-Identifier: Apache-2.0
"""CDS Blueprint module."""
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Generator, Iterator, List
from uuid import uuid4
from zipfile import ZipFile

import oyaml as yaml

from onapsdk.utils.jinja import jinja_env

from .cds_element import CdsElement
from .data_dictionary import DataDictionary, DataDictionarySet


@dataclass
class CbaMetadata:
    """Class to hold CBA metadata values."""

    tosca_meta_file_version: str
    csar_version: str
    created_by: str
    entry_definitions: str
    template_name: str
    template_version: str
    template_tags: str


@dataclass
class Mapping:
    """Blueprint's template mapping.

    Stores mapping data:
      - name,
      - type,
      - name of dictionary from which value should be get,
      - dictionary source of value.
    """

    name: str
    mapping_type: str
    dictionary_name: str
    dictionary_sources: List[str] = field(default_factory=list)

    def __hash__(self) -> int:  # noqa: D401
        """Mapping object hash.

        Based on mapping name.

        Returns:
            int: Mapping hash

        """
        return hash(self.name)

    def __eq__(self, mapping: "Mapping") -> bool:
        """Compare two mapping objects.

        Mappings are equal if have the same name.

        Args:
            mapping (Mapping): Mapping object to compare with.

        Returns:
            bool: True if objects have the same name, False otherwise.

        """
        return self.name == mapping.name

    def merge(self, mapping: "Mapping") -> None:
        """Merge mapping objects.

        Merge objects dictionary sources.

        Args:
            mapping (Mapping): Mapping object to merge.

        """
        self.dictionary_sources = list(
            set(self.dictionary_sources) | set(mapping.dictionary_sources)
        )

    def generate_data_dictionary(self) -> dict:
        """Generate data dictionary for mapping.

        Data dictionary with required data sources, type and name for mapping will be created from
            Jinja2 template.

        Returns:
            dict: Data dictionary

        """
        return json.loads(
            jinja_env().get_template("data_dictionary_base.json.j2").render(mapping=self)
        )


class MappingSet:
    """Set of mapping objects.

    Mapping objects will be stored in dictionary where mapping name is a key.
    No two mappings with the same name can be stored in this collection.
    """

    def __init__(self) -> None:
        """Initialize mappings collection.

        Create dictionary to store mappings.
        """
        self.mappings = {}

    def __len__(self) -> int:  # noqa: D401
        """Mapping set length.

        Returns:
            int: Number of stored mapping objects.

        """
        return len(self.mappings)

    def __iter__(self) -> Iterator[Mapping]:
        """Iterate through mapping stored in set.

        Returns:
            Iterator[Mapping]: Stored mappings iterator.

        """
        return iter(list(self.mappings.values()))

    def __getitem__(self, index: int) -> Mapping:
        """Get item stored on given index.

        Args:
            index (int): Index number.

        Returns:
            Mapping: Mapping stored on given index.

        """
        return list(self.mappings.values())[index]

    def add(self, mapping: Mapping) -> None:
        """Add mapping to set.

        If there is already mapping object with the same name in collection
            they will be merged.

        Args:
            mapping (Mapping): Mapping to add to collection.

        """
        if mapping.name not in self.mappings:
            self.mappings.update({mapping.name: mapping})
        else:
            self.mappings[mapping.name].merge(mapping)

    def extend(self, iterable: Iterator[Mapping]) -> None:
        """Extend set with an iterator of mappings.

        Args:
            iterable (Iterator[Mapping]): Mappings iterator.

        """
        for mapping in iterable:
            self.add(mapping)


class Workflow(CdsElement):
    """Blueprint's workflow.

    Stores workflow steps, inputs, outputs.
    Executes workflow using CDS HTTP API.
    """

    @dataclass
    class WorkflowStep:
        """Workflow step class.

        Stores step name, description, target and optional activities.
        """

        name: str
        description: str
        target: str
        activities: List[Dict[str, str]] = field(default_factory=list)

    @dataclass
    class WorkflowInput:
        """Workflow input class.

        Stores input name, information if it's required, type, and optional description.
        """

        name: str
        required: bool
        type: str
        description: str = ""

    @dataclass
    class WorkflowOutput:
        """Workflow output class.

        Stores output name, type na value.
        """

        name: str
        type: str
        value: Dict[str, Any]

    def __init__(self,
                 cba_workflow_name: str,
                 cba_workflow_data: dict,
                 blueprint: "Blueprint") -> None:
        """Workflow initialization.

        Args:
            cba_workflow_name (str): Workflow name.
            cba_workflow_data (dict): Workflow data.
            blueprint (Blueprint): Blueprint object which contains workflow.

        """
        super().__init__()
        self.name: str = cba_workflow_name
        self.workflow_data: dict = cba_workflow_data
        self.blueprint: "Blueprint" = blueprint
        self._steps: List[self.WorkflowStep] = None
        self._inputs: List[self.WorkflowInput] = None
        self._outputs: List[self.WorkflowOutput] = None

    def __repr__(self) -> str:
        """Representation of object.

        Returns:
            str: Object's string representation

        """
        return (f"Workflow(name='{self.name}', "
                f"blueprint_name='{self.blueprint.metadata.template_name})'")

    @property
    def steps(self) -> List["Workflow.WorkflowStep"]:
        """Workflow's steps property.

        Returns:
            List[Workflow.WorkflowStep]: List of workflow's steps.

        """
        if self._steps is None:
            self._steps = []
            for step_name, step_data in self.workflow_data.get("steps", {}).items():
                self._steps.append(
                    self.WorkflowStep(
                        name=step_name,
                        description=step_data.get("description"),
                        target=step_data.get("target"),
                        activities=step_data.get("activities", []),
                    )
                )
        return self._steps

    @property
    def inputs(self) -> List["Workflow.WorkflowInput"]:
        """Workflow's inputs property.

        Returns:
            List[Workflow.WorkflowInput]: List of workflows's inputs.

        """
        if self._inputs is None:
            self._inputs = []
            for input_name, input_data in self.workflow_data.get("inputs", {}).items():
                self._inputs.append(
                    self.WorkflowInput(
                        name=input_name,
                        required=input_data.get("required"),
                        type=input_data.get("type"),
                        description=input_data.get("description"),
                    )
                )
        return self._inputs

    @property
    def outputs(self) -> List["Workflow.WorkflowOutput"]:
        """Workflow's outputs property.

        Returns:
            List[Workflow.WorkflowOutput]: List of workflows's outputs.

        """
        if self._outputs is None:
            self._outputs = []
            for output_name, output_data in self.workflow_data.get("outputs", {}).items():
                self._outputs.append(
                    self.WorkflowOutput(
                        name=output_name,
                        type=output_data.get("type"),
                        value=output_data.get("value"),
                    )
                )
        return self._outputs

    @property
    def url(self) -> str:
        """Workflow execution url.

        Returns:
            str: Url to call warkflow execution.

        """
        return f"{self._url}/api/v1/execution-service/process"

    def execute(self, inputs: dict) -> dict:
        """Execute workflow.

        Call CDS HTTP API to execute workflow.

        Args:
            inputs (dict): Inputs dictionary.

        Raises:
            AttributeError: Execution returns error.

        Returns:
            dict: Response's payload.

        """
        # There should be some flague to check if CDS UI API is used or blueprintprocessor.
        # For CDS UI API there is no endporint to execute workflow, so it has to be turned off.
        execution_service_input: dict = {
            "commonHeader": {
                "originatorId": "onapsdk",
                "requestId": str(uuid4()),
                "subRequestId": str(uuid4()),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            },
            "actionIdentifiers": {
                "blueprintName": self.blueprint.metadata.template_name,
                "blueprintVersion": self.blueprint.metadata.template_version,
                "actionName": self.name,
                "mode": "SYNC",  # Has to be SYNC for REST call
            },
            "payload": {f"{self.name}-request": inputs},
        }
        response: "requests.Response" = self.send_message_json(
            "POST",
            f"Execute {self.blueprint.metadata.template_name} blueprint {self.name} workflow",
            self.url,
            auth=self.auth,
            data=json.dumps(execution_service_input),
            exception=ValueError
        )
        return response["payload"]


class Blueprint(CdsElement):
    """CDS blueprint representation."""

    TEMPLATES_RE = r"Templates\/.*json$"
    TOSCA_META = "TOSCA-Metadata/TOSCA.meta"

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
        self._cba_metadata: CbaMetadata = None
        self._cba_mappings: MappingSet = None
        self._cba_workflows: List[Workflow] = None

    @property
    def url(self) -> str:
        """URL address to use for CDS API call.

        Returns:
            str: URL to CDS blueprintprocessor.

        """
        return f"{self._url}/api/v1/blueprint-model"

    @property
    def metadata(self) -> CbaMetadata:
        """Blueprint metadata.

        Data from TOSCA.meta file.

        Returns:
            CbaMetadata: Blueprint metadata object.

        """
        if not self._cba_metadata:
            with ZipFile(BytesIO(self.cba_file_bytes)) as cba_zip_file:
                self._cba_metadata = self.get_cba_metadata(cba_zip_file.read(self.TOSCA_META))
        return self._cba_metadata

    @property
    def mappings(self) -> MappingSet:
        """Blueprint mappings collection.

        Returns:
            MappingSet: Mappings collection.

        """
        if not self._cba_mappings:
            with ZipFile(BytesIO(self.cba_file_bytes)) as cba_zip_file:
                self._cba_mappings = self.get_mappings(cba_zip_file)
        return self._cba_mappings

    @property
    def workflows(self) -> List["Workflow"]:
        """Blueprint's workflows property.

        Returns:
            List[Workflow]: Blueprint's workflow list.

        """
        if not self._cba_workflows:
            with ZipFile(BytesIO(self.cba_file_bytes)) as cba_zip_file:
                self._cba_workflows = list(
                    self.get_workflows(cba_zip_file.read(self.metadata.entry_definitions))
                )
        return self._cba_workflows

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
            f"{self.url}/enrich",
            files={"file": self.cba_file_bytes},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth,
            exception=ValueError
        )
        return Blueprint(response.content)

    def publish(self) -> None:
        """Publish blueprint."""
        self.send_message(
            "POST",
            "Publish CDS blueprint",
            f"{self.url}/publish",
            files={"file": self.cba_file_bytes},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth,
            exception=ValueError
        )

    def deploy(self) -> None:
        """Deploy blueprint."""
        self.send_message(
            "POST",
            "Deploy CDS blueprint",
            f"{self.url}",
            files={"file": self.cba_file_bytes},
            headers={},  # Leave headers empty to fill it correctly by `requests` library
            auth=self.auth,
            exception=ValueError
        )

    def save(self, dest_file_path: str) -> None:
        """Save blueprint to file.

        Args:
            dest_file_path (str): Path of file where blueprint is going to be saved

        """
        with open(dest_file_path, "wb") as cba_file:
            cba_file.write(self.cba_file_bytes)

    def get_data_dictionaries(self) -> DataDictionarySet:
        """Get the generated data dictionaries required by blueprint.

        If mapping reqires other source than input it should be updated before upload to CDS.

        Returns:
            Generator[DataDictionary, None, None]: DataDictionary objects.

        """
        dd_set: DataDictionarySet = DataDictionarySet()
        for mapping in self.mappings:
            dd_set.add(DataDictionary(mapping.generate_data_dictionary()))
        return dd_set

    @staticmethod
    def get_cba_metadata(cba_tosca_meta_bytes: bytes) -> CbaMetadata:
        """Parse CBA TOSCA.meta file and get values from it.

        Args:
            cba_tosca_meta_bytes (bytes): TOSCA.meta file bytes.

        Raises:
            ValueError: File has invalid format.

        Returns:
            CbaMetadata: Dataclass with CBA metadata

        """
        meta_dict: dict = yaml.safe_load(cba_tosca_meta_bytes)
        if not isinstance(meta_dict, dict):
            raise ValueError("Invalid TOSCA Meta file")
        return CbaMetadata(
            tosca_meta_file_version=meta_dict.get("TOSCA-Meta-File-Version"),
            csar_version=meta_dict.get("CSAR-Version"),
            created_by=meta_dict.get("Created-By"),
            entry_definitions=meta_dict.get("Entry-Definitions"),
            template_name=meta_dict.get("Template-Name"),
            template_version=meta_dict.get("Template-Version"),
            template_tags=meta_dict.get("Template-Tags"),
        )

    @staticmethod
    def get_mappings_from_mapping_file(cba_mapping_file_bytes: bytes
                                       ) -> Generator[Mapping, None, None]:
        """Read mapping file and create Mappping object for it.

        Args:
            cba_mapping_file_bytes (bytes): CBA mapping file bytes.

        Yields:
            Generator[Mapping, None, None]: Mapping object.

        """
        mapping_file_json = json.loads(cba_mapping_file_bytes)
        for mapping in mapping_file_json:
            yield Mapping(
                name=mapping["name"],
                mapping_type=mapping["property"]["type"],
                dictionary_name=mapping["dictionary-name"],
                dictionary_sources=[mapping["dictionary-source"]],
            )

    def get_mappings(self, cba_zip_file: ZipFile) -> MappingSet:
        """Read mappings from CBA file.

        Search mappings in CBA file and create Mapping object for each of them.

        Args:
            cba_zip_file (ZipFile): CBA file to get mappings from.

        Returns:
            MappingSet: Mappings set object.

        """
        mapping_set = MappingSet()
        for info in cba_zip_file.infolist():
            if re.match(self.TEMPLATES_RE, info.filename):
                mapping_set.extend(
                    self.get_mappings_from_mapping_file(cba_zip_file.read(info.filename))
                )
        return mapping_set

    def get_workflows(self,
                      cba_entry_definitions_file_bytes: bytes) -> Generator[Workflow, None, None]:
        """Get worfklows from entry_definitions file.

        Parse entry_definitions file and create Workflow objects for workflows stored in.

        Args:
            cba_entry_definitions_file_bytes (bytes): entry_definition file.

        Yields:
            Generator[Workflow, None, None]: Workflow object.

        """
        entry_definitions_json: dict = json.loads(cba_entry_definitions_file_bytes)
        workflows: dict = entry_definitions_json.get("topology_template", {}).get("workflows", {})
        for workflow_name, workflow_data in workflows.items():
            yield Workflow(workflow_name, workflow_data, self)
