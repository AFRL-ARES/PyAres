from typing import Dict, Any

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
                 maximum_value: float, param_history: list[ParameterHistoryItem], data_type: str, 
                 is_planned: bool, is_result: bool, planner_name: str):
        """
        Initializes a PlanningParameter.

        Args:
            name: The name or key associated with the parameter.
            value: The value of the parameter.
            minimum_value: The minimum value the parameter is capable of being assigned.
            maximum_value: The maximum value the parameter is capable of being assigned.
            param_history: A list of historical planned and achieved values associated with the parameter.
            data_type: The data type associated with the parameter.
            is_planned: A bool representing whether this parameter is designed to be planned for.
            is_result: A bool representing whether this parameter is the intended result of the experiment.
            planner_name: The name of the planner ARES requested be used to plan for this parameter.
        """
        self.name = name
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value
        self.param_history = param_history
        self.data_type = data_type
        self.is_planned = is_planned
        self.is_result = is_result
        self.planner_name = planner_name

class PlanRequest:
    """
    Represents a PlanRequest message received from ARES.

    Designed to provide a more user-friendly abstraction for interacting with a plan request message.
    """
    def __init__(self, parameters: list[PlanningParameter], settings: Dict[str, Any], analysis_results: list[float], session_id: str):
        """
        Initializes a PlanRequest.

        Args:
            parameters: A list of PlanningParameter objects.
        """
        self.parameters = parameters
        self.settings = settings
        self.analysis_results = analysis_results
        self.session_id = session_id


class PlanResponse:
    """ Represents a PlanResponse message to be send to ARES. """
    def __init__(self, parameter_names: list[str], parameter_values: list):
        """
        Initializes a PlanResponse.

        Args:
            parameter_names: A list of names associated with planned parameters.
            parameter_values: A list of values associated with planned parameters. 
        """
        self.parameter_names = parameter_names
        self.parameter_values = parameter_values