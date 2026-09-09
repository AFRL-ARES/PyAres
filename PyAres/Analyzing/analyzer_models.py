from typing import Dict, Any, List, Optional
import warnings
from ..Models import Outcome, RequestMetadata, AresDataType, AresSchemaEntry
from ares_datamodel import ares_data_schema_pb2
from ..Utils import ares_data_type_utils

class AnalysisRequest:
    """ Represents an analysis request received from ARES. """

    def __init__(self, inputs: Dict[str, Any], settings: Dict[str, Any], metadata: RequestMetadata):
        self.inputs = inputs
        self.settings = settings
        self.request_metadata = metadata

    def __str__(self) -> str:
        """Returns a string representation of the AnalysisRequest with all information organized."""
        metadata_str = str(self.request_metadata).replace('\n', '\n\t')
        return (f"AnalysisRequest object with:\n"
                f"  inputs: {self.inputs}\n"
                f"  settings: {self.settings}\n"
                f"  metadata: {metadata_str}")
    
    def __repr__(self) -> str:
        return self.__str__()

class Objective:
    """ Represents a single analysis objective in the new AnalysisResponse model. """

    def __init__(self, objective_name: str, objective_value: Any, objective_metadata: Optional[Dict[str, Any]] = None):
        """
        Initializes a new Objective.

        Args:
            objective_name: A name the user wants associated with this objective.
            objective_value: The value associated with this objective, as calculated by the analyzer.
            objective_metadata: Optional metadata associated with this objective, represented as a dictionary.
        """
        self.objective_name = objective_name
        self.objective_value = objective_value
        self.objective_metadata = objective_metadata or {}

    def __str__(self) -> str:
        return (f"Objective object with:\n"
                f"  objective_name: {self.objective_name}\n"
                f"  objective_value: {self.objective_value}\n"
                f"  objective_metadata: {self.objective_metadata}")
    
    def __repr__(self) -> str:
        return self.__str__()


class ObjectiveSchema:
    """A schema representing the expected form of an objective."""

    def __init__(
        self,
        objective_name: str,
        proto_objective_schema: ares_data_schema_pb2.AresValueSchema,
    ):
        self.objective_name = objective_name
        # Convert basic scalar fields
        self.objective_type: AresDataType = ares_data_type_utils.proto_ares_type_to_python_ares_type(proto_objective_schema.type)
        self.objective_description: str = proto_objective_schema.description
        self.optional: bool = proto_objective_schema.optional

        # Convert nested struct schema, if present
        self.struct_schema: Optional[Dict[str, AresSchemaEntry]] = None
        if proto_objective_schema.struct_schema.fields:
            self.struct_schema = {}
            for field_name, field_schema in proto_objective_schema.struct_schema.fields.items():
                self.struct_schema[field_name] = self._proto_value_schema_to_ares_schema_entry(field_schema)

        # Convert list element schema, if present
        self.list_element_schema: Optional[AresSchemaEntry] = None
        # Treat type UNKNOWN (0) as "no list element schema configured"
        if proto_objective_schema.list_element_schema.type != 0:
            self.list_element_schema = self._proto_value_schema_to_ares_schema_entry(
                proto_objective_schema.list_element_schema
            )

    @staticmethod
    def _proto_value_schema_to_ares_schema_entry(
        proto: ares_data_schema_pb2.AresValueSchema,
    ) -> AresSchemaEntry:
        """Convert a proto AresValueSchema into a Python AresSchemaEntry."""
        py_type = ares_data_type_utils.proto_ares_type_to_python_ares_type(proto.type)

        # Extract choices if present
        choices: List[Any] = []
        if proto.string_choices.strings:
            choices = list(proto.string_choices.strings)
        elif proto.number_choices.numbers:
            choices = list(proto.number_choices.numbers)

        entry = AresSchemaEntry(
            type=py_type,
            optional=proto.optional,
            description=proto.description,
            choices=choices,
            struct_schema=None,
            list_element_schema=None,
            min_number_value=getattr(proto, "min_number_value", None),
            max_number_value=getattr(proto, "max_number_value", None),
        )

        # Nested struct schema
        if proto.struct_schema.fields:
            entry.struct_schema = {}
            for field_name, field_schema in proto.struct_schema.fields.items():
                entry.struct_schema[field_name] = ObjectiveSchema._proto_value_schema_to_ares_schema_entry(
                    field_schema
                )

        # Nested list element schema
        if proto.list_element_schema.type != 0:
            entry.list_element_schema = ObjectiveSchema._proto_value_schema_to_ares_schema_entry(
                proto.list_element_schema
            )

        return entry

    def __str__(self) -> str:
        struct_keys = list(self.struct_schema.keys()) if self.struct_schema else []
        list_elem_type = (
            self.list_element_schema.type.name
            if self.list_element_schema and hasattr(self.list_element_schema.type, "name")
            else None
        )

        return (
            f"ObjectiveSchema(\n"
            f"  objective_name={self.objective_name!r},\n"
            f"  objective_type={self.objective_type.name if hasattr(self.objective_type, 'name') else self.objective_type},\n"
            f"  objective_description={self.objective_description!r},\n"
            f"  optional={self.optional},\n"
            f"  struct_schema_keys={struct_keys},\n"
            f"  list_element_type={list_elem_type}\n"
            f")"
        )

    def __repr__(self) -> str:
        return self.__str__()


class AnalysisResponse:
    """ Represents the result of an analysis process using objectives. 

    Preferred usage:
        - Construct with a list of Objective instances:
            AnalysisResponse(
                objectives=[
                    Objective("primary_metric", 0.87, {"units": "accuracy"})
                ],
                outcome=Outcome.SUCCESS,
                error_string=""
            )

    Deprecated usage:
        - Construct with a single scalar result (will be removed in a future major version):
            AnalysisResponse(result=0.87)
    """

    def __init__(
        self,
        objectives: Optional[List[Objective]] = None,
        outcome: Outcome = Outcome.SUCCESS,
        error_string: str = "",
        result: Optional[float] = None,
    ):
        """
        Initializes an AnalysisResponse message.

        Args:
            objectives: A list of Objective instances representing the objectives returned by analysis.
            outcome: An Outcome value that represents whether analysis was done successfully.
            error_string: An optional string argument for passing why analysis failed to ARES.
            result: DEPRECATED. A single numeric result that will be wrapped into a default Objective. 
                    This parameter is deprecated and will be removed in a future major version.
        """
        self._deprecated_result_usage = False

        if objectives is not None and result is not None:
            raise ValueError("AnalysisResponse cannot be constructed with both 'objectives' and deprecated 'result'. "
                             "Use 'objectives' only.")

        if objectives is None and result is not None:
            # Deprecated path: single scalar result
            warnings.warn(
                "AnalysisResponse(result=...) is deprecated; use "
                "AnalysisResponse(objectives=[Objective(...)]) instead. "
                "Support will be removed in a future major version.",
                DeprecationWarning
            )
            self._deprecated_result_usage = True

            # Use a default objective name for backward compatibility
            default_objective = Objective(
                objective_name="result",
                objective_value=result,
                objective_metadata=None,
            )
            self.objectives: List[Objective] = [default_objective]
        elif objectives is not None:
            self.objectives = objectives
        else:
            # No objectives and no result provided: treat as empty objectives
            self.objectives = []

        self.outcome = outcome
        self.error_string = error_string

    @property
    def deprecated_result_usage(self) -> bool:
        """Indicates whether this AnalysisResponse was created via the deprecated 'result' parameter."""
        return self._deprecated_result_usage

    def __str__(self) -> str:
        if not self.objectives:
            objectives_str = "\t- (none)"

        else:
            objectives_str = "\n".join(
                [f"\t- {obj.objective_name}: value={obj.objective_value}, metadata={obj.objective_metadata}"
                 for obj in self.objectives])
            
        return (f"AnalysisResponse object with:\n"
                f"  objectives:\n{objectives_str}\n"
                f"  outcome: {self.outcome}\n"
                f"  error_string: {self.error_string}")
    
    def __repr__(self) -> str:
        return self.__str__()   

class InfoResponse:
    """ A response message that provides basic information about your analyzer. """   

    def __init__(self, name: str, version: str, description: str = ""):
        """Initializes a new InfoResponse message.

        Args:
            name: The name of your analyzer, to be displayed in ARES.
            version: The specific version of your analyzer. This information is saved in experiment results that use your analyzer.
            description: An optional (but recommended) string that gives a basic description of your analyzer. 
        """

        self.name = name
        self.version = version
        self.description = description