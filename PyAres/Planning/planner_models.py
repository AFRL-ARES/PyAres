from typing import Dict, Any, List, Sequence, Optional
from ..Models import Outcome, AresDataType, RequestMetadata

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
                f" acheived_value: {self.achieved_value}\n")
    
    def __repr__(self) -> str:
        return self.__str__()

class PlanningParameter:
    """
    Represents a single parameter within a planning request.

    Designed to provide a more user-friendly abstraction for the user to interact
    with planning parameters through.
    """
    def __init__(self, name: str, minimum_value: float, 
                 maximum_value: float, param_history: list[ParameterHistoryItem], data_type: AresDataType, 
                 is_planned: bool, is_result: bool, planner_name: str, initial_value = None):
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
    

class ParamHistoryInfo:
    """
    Represents the history of a given parameter.

    Designed to provide a more user-friendly abstraction for interacting with a param history object.
    """
    def __init__(self, planned_value: Any, achieved_value: Any):
        """
        Initializes a ParamHistoryInfo.

        Args:
            planned_value (Any): The value given directly from the planner.
            achieved_value (Any): An optional value that represents the real world achieved value, which may differ from the planners target value.
        """
        self.planned_value = planned_value
        self.achieved_value = achieved_value


class PlanRequest:
    """
    Represents a PlanRequest message received from ARES.
    
    Designed to provide a more user-friendly abstraction for interacting with a plan request message.
    """
    def __init__(self, parameters: list[PlanningParameter], settings: Dict[str, Any], analysis_results: Sequence[float], metadata: RequestMetadata = RequestMetadata.from_default_values()):
        """
        Initializes a PlanRequest.

        Args:
            parameters: A list of PlanningParameter objects.
        """
        self.parameters = parameters
        self.settings = settings
        self.analysis_results = analysis_results
        self.request_metadata = metadata

    def __str__(self) -> str:
        param_str = "\n ".join(self.parameter_names)
        settings_str = "\n ".join([f"{k}: {v}" for k, v in self.settings.items()])
        analysis_str = "\n ".join([f"{i}: {val}" for i, val in enumerate(self.analysis_results)])
        
        return (f"PlanRequest object with:\n"
                f"parameters:\n"
                f" {param_str}\n"
                f"settings:\n"
                f" {settings_str}\n"
                f"analysis_results:\n"
                f" {analysis_str}\n"
                f"request_metadata:\n"
                f"{str(self.request_metadata).replace('\n','\n ')}")
    
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
    def planned_parameter_table(self) ->list:
        return [p.planned_values for p in self.parameters]
    @property
    def acheived_parameter_table(self) ->list:
        return [p.achieved_values for p in self.parameters]

    
class PlanResponse:
    """ Represents a PlanResponse message to be send to ARES. """
    def __init__(self, 
                 parameter_names: Optional[list[str]] = None,
                 parameter_values: Optional[list] = None,
                 parameter_data: Optional[dict[str,Any]] = None,
                 planning_outcome: Outcome = Outcome.SUCCESS, 
                 error_string: str = ""):
        """
        Initializes a PlanResponse. Using either lists of names and values or a python dictonary of name:value pairs

        Args:
            parameter_names: A list of names associated with planned parameters.
            parameter_values: A list of values associated with planned parameters. 
            parameter_data: A python dictionary of key:value pairs of planned parameters and planned values
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
        
        self.outcome = planning_outcome
        self.error_string = error_string
    
    def __str__(self):
        return (f"PlanResponse object with:\n"
                f" outcome: {self.outcome}\n"
                f" parameter_names: {self.parameter_names}\n"
                f" parameter_values: {self.parameter_values}\n"
                f" error_string: {self.error_string}\n")
    
    def __repr__(self) -> str:
        return self.__str__()