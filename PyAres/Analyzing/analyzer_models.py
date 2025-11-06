from typing import Dict, Any
from ..Models import Outcome, RequestMetadata

class AnalysisRequest:
    """ Represents an analysis request received from ARES. """

    def __init__(self, inputs: Dict[str, Any], settings: Dict[str, Any], metadata: RequestMetadata):
        self.inputs = inputs
        self.settings = settings
        self.request_metadata = metadata

class Analysis:
    """ Represents the result of an analysis process. """

    def __init__(self, result: float, outcome: Outcome = Outcome.SUCCESS, error_string: str = ""):
        """
        Initializes an Analysis message

        Args:
            result: The value your analyzer returns as the result of the experiment being analyzed. Represented as a float.
            success: A boolean value that represents whether analysis was done successfully.
            error_string: An optional string argument for passing why analysis failed to ARES. Will default to an empty string if no value is provided.
        """
        self.result = result
        self.outcome = outcome
        self.error_string = error_string
   

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


        