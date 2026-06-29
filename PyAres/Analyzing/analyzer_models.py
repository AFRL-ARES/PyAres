from typing import Dict, Any, List, overload
from ..Models import Outcome, RequestMetadata, Objective

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

class AnalysisResponse:
    @overload
    def __init__(self, result: float, outcome: Outcome = Outcome.SUCCESS, error_string: str = ""):
        """
        Initializes an Analysis Result message using the deprecated format.
        ...
        """
        ... 

    @overload
    def __init__(self, objectives: List[Objective], outcome: Outcome = Outcome.SUCCESS, error_string: str = ""):
        """
        Initializes an Analysis Result message using the new standard format.
        ...
        """
        ... 
    
    def __init__(self, *args, **kwargs):
        self.outcome = args[1] if len(args) > 1 else kwargs.get("outcome", Outcome.SUCCESS)
        self.error_string = args[2] if len(args) > 2 else kwargs.get("error_string", "")
        self.result = 0.0
        self.objectives = []

        if len(args) > 0:
            primary_arg = args[0]
            
            if isinstance(primary_arg, (float, int)):
                self.result = float(primary_arg)
            
            elif isinstance(primary_arg, list):
                self.objectives = primary_arg
                
            elif primary_arg is None:
                self.result = None
                   
            else:
                raise TypeError(f"First argument must be a float or a list of Objectives, got {type(primary_arg)}")

        else:
            if "result" in kwargs:
                self.result = float(kwargs["result"])
            elif "objectives" in kwargs:
                self.objectives = kwargs["objectives"]
            else:
                raise TypeError("You must provide either 'result' or 'objectives'.")

    def __str__(self) -> str:
        return (f"Analysis object with:\n"
                f"  result: {self.result}\n"
                f"  objectives: {self.objectives}\n"
                f"  outcome: {self.outcome}\n"
                f"  error_string: {self.error_string}")
    
    def __repr__(self) -> str:
        return self.__str__()   

class InfoResponse:
    """ A response message that provides basic information about your analyzer. """   

    def __init__(self, name: str, version: str, description: str = ""):
        """
        Initializes a new InfoResponse message.

        Args:
            name: The name of your analyzer, to be displayed in ARES.
            version: The specific version of your analyzer. This information is saved in experiment results that use your analyzer.
            description: An optional (but recommended) string that gives a basic description of your analyzer. 
        """

        self.name = name
        self.version = version
        self.description = description

