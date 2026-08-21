from typing import Dict, Any, List, Sequence, Optional
from ..Models import Outcome, AresDataType, RequestMetadata, PlanStatusCode
from enum import Enum
from ..Analyzing.analyzer_models import Objective

class ParameterHistoryItem:
    """ Represents a single historical parameter item """
    def __init__(self, planned_value: Any, achieved_value: Any):
        """
        Initializes a ParameterHistoryItem

        Args:
          planned_value: A value that was planned
          achieved_value: Optionally a value that was actually achieved for what was planned
        """
        self.planned_value = planned_value
        self.achieved_value = achieved_value
    def __str__(self):
        return (f"ParameterHistoryItem object with:\n"
                f" planned_value: {self.planned_value}\n"
                f" achieved_value: {self.achieved_value}\n")
    
    def __repr__(self) -> str:
        return self.__str__()
    
class ObjectiveStatus(Enum):
    """ An enum representing the current status of the objective the planner is trying to achieve (if any) """
    OBJECTIVE_STATUS_UNSPECIFIED = 0
    OBJECTIVE_UNACHIEVED = 1
    OBJECTIVE_ACHIEVED = 2
    OBJECTIVE_FAILED = 3

class PlanningParameter:
    """
    Represents a single parameter within a planning request.

    Designed to provide a more user-friendly abstraction for the user to interact
    with planning parameters through.
    """
    def __init__(self, name: str, 
                 data_type: AresDataType,
                 minimum_value: float = None, 
                 maximum_value: float = None, 
                 param_history: list[ParameterHistoryItem] = [],
                 is_planned: bool = False, 
                 is_result: bool = False, 
                 planner_name: str = "", 
                 initial_value = None):
        """
        Initializes a PlanningParameter.

        Args:
            name: The name or key associated with the parameter.
            minimum_value: The minimum value the parameter is capable of being assigned.
            maximum_value: The maximum value the parameter is capable of being assigned.
            param_history: A list of historical planned and achieved values associated with the parameter.
            data_type: The data type associated with the parameter.
            is_planned: A bool representing whether this parameter is designed to be planned for.
            is_result: A bool representing whether this parameter is the intended result of the experiment.
            planner_name: The name of the planner ARES requested be used to plan for this parameter.
            initial_value: An optional initial value for the given parameter
        """
        self.name: str = name
        self.minimum_value: float = minimum_value
        self.maximum_value: float = maximum_value
        self.param_history: List[ParameterHistoryItem] = param_history
        self.data_type: AresDataType = data_type
        self.is_planned: bool = is_planned
        self.is_result: bool = is_result
        self.planner_name: str = planner_name
        self.initial_value = initial_value
    
    def __str__(self):
        return (f"ParameterHistoryItem object with:\n"
                f" name: {self.name}\n"
                f" minimum_value: {self.minimum_value}\n"
                f" maximum_value: {self.maximum_value}\n"
                f" param_history: {len(self.param_history)} records\n"
                f" data_type: {self.data_type}\n"
                f" is_planned: {self.is_planned}\n"
                f" is_result: {self.is_result}\n"
                f" planner_name: {self.planner_name}\n"
                f" initial_value: {self.initial_value}")
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def planned_values(self) -> list:
        return [item.planned_value for item in self.param_history]
    
    @property
    def achieved_values(self) -> list:
        return [item.achieved_value for item in self.param_history]
    
    @property
    def bounds(self) -> list:
        return [self.minimum_value, self.maximum_value]

class AnalysisDataEntry:
    """
    Represents the analysis data for a single experiment in a planning batch.

    Each entry currently exposes a list of analysis objectives as native Python objects.
    """
    def __init__(self, analysis_objectives: List[Objective]):
        """
        Initializes an AnalysisDataEntry.

        Args:
            analysis_objectives: A list of Objective instances produced by the analyzer.
        """
        self.analysis_objectives = analysis_objectives

    def __str__(self) -> str:
        if not self.analysis_objectives:
            return "AnalysisDataEntry(objectives: (none))"
        objectives_str = ", ".join(
            f"{obj.objective_name}={obj.objective_value}"
            for obj in self.analysis_objectives
        )
        return f"AnalysisDataEntry(objectives: [{objectives_str}])"

    def __repr__(self) -> str:
        return self.__str__()


class PlanRequest:
    """
    Represents a PlanRequest message received from ARES.
    
    Designed to provide a more user-friendly abstraction for interacting with a plan request message.
    """
    def __init__(self, 
                parameters: list[PlanningParameter], 
                settings: Dict[str, Any], 
                analysis_results: Sequence[float],
                metadata: RequestMetadata = RequestMetadata.from_default_values(),
                batch_size: int = 1,
                previous_plan_status_codes: List[PlanStatusCode] = None,
                analysis_data: Optional[List[AnalysisDataEntry]] = None):
        """
        Initializes a PlanRequest.

        Args:
            parameters: A list of PlanningParameter objects.
            settings: A dictionary of adapter settings associated with this request.
            analysis_results: A deprecated sequence of numeric analysis results. This will be removed in a future major release.
            metadata: Additional request metadata from ARES.
            batch_size: The number of plans requested from this planner.
            previous_plan_status_codes: A list of status codes associated with previously planned experiments.
            analysis_data: A list of AnalysisDataEntry objects, one per experiment, containing analyzer-produced objectives.
        """
        self.parameters = parameters
        self.settings = settings
        self._analysis_results = list(analysis_results)
        self.batch_size = batch_size
        self.request_metadata = metadata

        if previous_plan_status_codes is None:
            self.previous_plan_status_codes = []
        else:    
            self.previous_plan_status_codes = previous_plan_status_codes

        self.analysis_data: List[AnalysisDataEntry] = analysis_data or []

    def __str__(self) -> str:
        param_str = "\n ".join(self.parameter_names)
        settings_str = "\n ".join([f"{k}: {v}" for k, v in self.settings.items()])
        analysis_results_str = "\n ".join([f"{i}: {val}" for i, val in enumerate(self._analysis_results)])
        analysis_data_str = "\n ".join([f"{i}: {val}" for i, val in enumerate(self.analysis_data)])
        
        metadata_str = str(self.request_metadata).replace('\n', '\n ')
        return (f"PlanRequest object with:\n"
                f"parameters:\n"
                f"{param_str}\n"
                f"settings:\n"
                f"{settings_str}\n"
                f"analysis_results:\n"
                f"{analysis_results_str}\n"
                f"analysis_data:\n"
                f"{analysis_data_str}\n"
                f"request_metadata:\n"
                f"{metadata_str}"
                f"batch_size:\n"
                f"{self.batch_size}")
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __getattr__(self, name):
        """
        Allow easier retreival of parameters from the plan request
        """
        if name in self.parameter_names:
            return self.parameters[self.parameter_names.index(name)]
        else:
            print("Attribute not found: ", name)
            return None
        
    # Easier access to the data the planners will use
    @property
    def parameter_names(self) -> list[str]:
        return [p.name for p in self.parameters]

    @property
    def planned_parameter_table(self) -> list:
        return [p.planned_values for p in self.parameters]

    @property
    def acheived_parameter_table(self) -> list:
        return [p.achieved_values for p in self.parameters]

    @property
    def analysis_results(self) -> list[float]:
        """
        Deprecated numeric analysis results.

        Accessing this property will emit a DeprecationWarning. Use `analysis_data`
        (and its contained objectives) instead.
        """
        import warnings
        warnings.warn(
            "PlanRequest.analysis_results is deprecated and will be removed in a future major release. "
            "Use PlanRequest.analysis_data instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._analysis_results

    @analysis_results.setter
    def analysis_results(self, value: Sequence[float]):
        self._analysis_results = list(value)

    @property
    def analysis_objectives(self) -> List[List[Objective]]:
        """
        Convenience property that returns a list of objective lists, one per experiment.
        """
        return [entry.analysis_objectives for entry in self.analysis_data]

    
class PlanResponse:
    """ Represents a PlanResponse message to be sent to ARES. """
    def __init__(self, 
                 parameter_names: Optional[list[str]] = None,
                 parameter_values: Optional[list] = None,
                 parameter_data: Optional[dict[str,Any]] = None,
                 outcome: Outcome = Outcome.SUCCESS, 
                 error_string: str = "",
                 objective_status: ObjectiveStatus = ObjectiveStatus.OBJECTIVE_STATUS_UNSPECIFIED):
        """
        Initializes a PlanResponse. Using either lists of names and values or a python dictonary of name:value pairs

        Args:
            parameter_names: A list of names associated with planned parameters.
            parameter_values: A list of values associated with planned parameters. 
            parameter_data: A python dictionary of key:value pairs of planned parameters and planned values
            outcome: An enum of type Outcome that determines whether the planning process succeeded or not, defaults to SUCCESS
            error_string: An optional string for specifying planning failure reasons to be relayed to ARES
            objective_status: An optional value that specifies the status of the objective your planner is trying to achieve (if any)
        """
        if parameter_data is not None:
            self.parameter_names = list(parameter_data.keys())
            self.parameter_values = list(parameter_data.values())
        
        elif parameter_names is not None and parameter_values is not None:
            if len(parameter_names) != len(parameter_values):
                raise ValueError("Parameter names list and values lists must have the same length")
            self.parameter_names = parameter_names
            self.parameter_values = parameter_values

        else:
             raise ValueError("No values to assign!")
        
        self.outcome = outcome
        self.error_string = error_string
        self.objective_status = objective_status
    
    def __str__(self):
        return (f"PlanResponse object with:\n"
                f" outcome: {self.outcome}\n"
                f" parameter_names: {self.parameter_names}\n"
                f" parameter_values: {self.parameter_values}\n"
                f" error_string: {self.error_string}\n"
                f" objective_status: {self.objective_status}\n")
    
    def __repr__(self) -> str:
        return self.__str__()

class PlannedParameter:
    def __init__(self, parameter_name: str, parameter_value: Any):
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value

    def __str__(self):
        # A clean, readable key-value output
        return f"{self.parameter_name}: {self.parameter_value}"

    def __repr__(self):
        # The !r formatting flag automatically wraps strings in quotes and calls __repr__ on the values
        return f"PlannedParameters(parameter_name={self.parameter_name!r}, parameter_value={self.parameter_value!r})"

class Plan:
    def __init__(self, 
                 planned_parameters: List[PlannedParameter], 
                 outcome: Outcome, 
                 error_string: str = "", 
                 objective_status: ObjectiveStatus = ObjectiveStatus.OBJECTIVE_STATUS_UNSPECIFIED):
        self.planned_parameters = planned_parameters
        self.outcome = outcome
        self.error_string = error_string
        self.objective_status = objective_status

    def __str__(self):
        base_str = f"Plan (Outcome: {self.outcome}) \n (Objective Status: {self.objective_status})"
        
        # Format the list of parameters into a readable string
        if self.planned_parameters:
            params_str = ", ".join(str(p) for p in self.planned_parameters)
            base_str += f" | Parameters: [{params_str}]"
            
        if self.error_string:
            base_str += f" - Error: '{self.error_string}'"
            
        return base_str

    def __repr__(self):
        return f"Plan(planned_parameters={self.planned_parameters!r}, outcome={self.outcome!r}, error_string={self.error_string!r})"
