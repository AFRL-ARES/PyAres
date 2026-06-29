from ares_datamodel import request_metadata_pb2
from enum import Enum
from dataclasses import dataclass, field
from typing import Union, List, Optional, Dict, Any
import pint

class AresDataType(Enum):
    UNKNOWN = 0
    NULL = 1
    BOOLEAN = 2
    STRING = 3
    NUMBER = 4
    STRING_ARRAY = 5
    NUMBER_ARRAY = 6
    LIST = 7
    STRUCT = 8
    BYTE_ARRAY = 9
    ANY = 10
    UNIT = 11
    FUNCTION = 12
    QUANTITY = 13
    TIMESTAMP = 14
    FLOAT = 15
    INT = 16

class Outcome(Enum):
    UNSPECIFIED_OUTCOME = 0
    SUCCESS = 1
    FAILURE = 2
    WARNING = 3
    CANCELED = 4

class RequestMetadata():
    def __init__(self, proto_metadata: request_metadata_pb2.RequestMetadata):
        self.system_name = proto_metadata.system_name
        self.campaign_name = proto_metadata.campaign_name
        self.campaign_id = proto_metadata.campaign_id
        self.experiment_id = proto_metadata.experiment_id
        edt = proto_metadata.experiment_start_time.ToDatetime()
        cdt = proto_metadata.campaign_start_time.ToDatetime()
        self.experiment_start_time = edt.strftime("%Y-%m-%d %H:%M:%S")
        self.campaign_start_time = cdt.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) ->str:
        return (f"RequestMetadata object with fields:\n"
                f"System Name: {self.system_name}\n"
                f"Campaign Name: {self.campaign_name}\n"
                f"Campaign ID: {self.campaign_id}\n"
                f"Experiment ID: {self.experiment_id}\n"
                f"Experiment Start Time: {self.experiment_start_time}\n"
                f"Campaign Start Time: {self.campaign_start_time}\n")
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @classmethod
    def from_default_values(cls):
        """ Alternative constructor for creating fake metadata """
        default = request_metadata_pb2.RequestMetadata(system_name="TEST SYSTEM", campaign_name="TEST CAMPAIGN", campaign_id="TEST ID", experiment_id="TEST EXPERIMENT ID")
        return cls(default)

class Limits:
    def __init__(self, minimum: float, maximum: float):
        self.minimum = minimum
        self.maximum = maximum

@dataclass
class Quantity:
    scalar: float
    type: int # QuantityType enum value
    unit: str

@dataclass
class QuantitySchema:
    bounds_unit: pint.Unit = None
    min_scalar_value: Optional[float] = None
    max_scalar_value: Optional[float] = None

@dataclass
class AresSchemaEntry:
    type: AresDataType
    optional: bool = False
    description: str = ""
    unit: str = ""
    choices: Union[List[str], List[int], List[float]] = field(default_factory=list)
    quantity_schema: Optional[QuantitySchema] = None
    struct_schema: Optional[Dict[str, 'AresSchemaEntry']] = None
    list_element_schema: Optional['AresSchemaEntry'] = None
    min_number_value: Optional[float] = None
    max_number_value: Optional[float] = None

class Objective:
    """ A class that represents an objective during analysis. """

    def __init__(self, objective_name: str, objective_value: Any, metadata: Dict = {}):
        """
        Initializes a new objective object

        Args:
            objective_name: The name your analyzer is associating with your objective
            objective_value: The value your analyzer calculated for this objective
            description: An optional dictionary for storing various pieces of metadata
        """

        self.objective_name = objective_name
        self.objective_value = objective_value
        self.metadata = metadata

class AnalysisResult:
    """ A class that represents a round of analysis results """
    
    def __init__(self, objectives: List[Objective], analysis_outcome: Outcome, error_string: str = ""):
        """
        Initializes a new Analysis Result object

        Args:
            objectives: A list of objective objects representing the values produced by the analyzer for this round of analysis
            analysis_outcome: An outcome field that says whether the analysis failed, succeeded or otherwise
            error_string: An optional string value for specifying why analysis failed
        """

        self.objectives = objectives
        self.analysis_outcome = analysis_outcome
        self.error_string = error_string