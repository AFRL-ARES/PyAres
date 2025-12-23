from typing import Dict, Any, List, Sequence
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


class PlanResponse:
    """ Represents a PlanResponse message to be send to ARES. """
    def __init__(self, parameter_names: list[str], parameter_values: list, planning_outcome: Outcome = Outcome.SUCCESS, error_string: str = ""):
        """
        Initializes a PlanResponse.

        Args:
            parameter_names: A list of names associated with planned parameters.
            parameter_values: A list of values associated with planned parameters. 
        """
        self.parameter_names = parameter_names
        self.parameter_values = parameter_values
        self.outcome = planning_outcome
        self.error_string = error_string