from enum import Enum

class AnalysisRequest:
    """
    Represents an analysis request received from ARES    
    """

    def __init__(self, inputs: dict, settings: dict):
        self.inputs = inputs
        self.settings = settings

class Analysis:
    """
    Represents the result of an analysis process.
    """

    def __init__(self, result: float, success: bool, error_string: str = ""):
        """
        Initializes an Analysis message

        Args:
            result: The value your analyzer returns as the result of the experiment being analyzed. Represented as a float.
            success: A boolean value that represents whether analysis was done successfully.
            error_string: An optional string argument for passing why analysis failed to ARES. Will default to an empty string if no value is provided.
        """
        self.result = result
        self.success = success
        self.error_string = error_string

class AnalyzerSetting:
    """
    Represents a setting associated with an analyzer.
    """

    def __init__(self, setting_name: str, optional: bool, setting_value):
        """
        Initializes an Analyzer Setting

        Args:
            setting_name: The name to be associated with your setting, in the form of a string.
            setting_value: The default value of your setting. This informs ARES what type is associated with your setting value.
                Currently ARES can support your setting values being booleans, strings, numbers, string arrays, number arrays, byte arrays or bool arrays.  
        """
        self.setting_name = setting_name
        self.optional = optional
        self.setting_value = setting_value 

class AnalyzerCapabilities:
    """
    Represents the capabilities of an analyzer, mainly used for creating settings.
    """

    def __init__(self, settings_schema: list[AnalyzerSetting], timeout_seconds: int = 60):
        """
        Initializes an Analyzer Capabilities message.

        Args:
            settings_schema: A list of your analyzers settings. See the :py:class:AnalyzerSetting for more information about what settings ARES can support.
            timeout_seconds: A timeout value, in seconds, that tells ARES how long to wait for your analyzer to respond. By default this is set to 60 seconds. 
        """

        self.settings_schema = settings_schema
        self.timeout_seconds = timeout_seconds

class ParameterValidationRequest:
    """
    A request to validate an analyzers expected parameters.
    """

    def __init__(self, input_schema: dict):
        self.input_schema = input_schema


class ParameterValidationResponse:
    """
    A response message to ARES indicating the success or failure of parameter validation.
    """

    def __init__(self, success: bool, message: list[str]):
        """
        Initializes a new Parameter Validation Response message.

        Args:
            success: A boolean value determining whether your analyzer successfully validated the parameters ARES provided.
            message: An optional list of strings for including specific error messages on why validation fails. 
        """

class ConnectionStatus(Enum):
    UNKNOWN: int = 1
    CONNECTED: int = 2
    DISCONNECTED: int = 3

class ConnectionStatusResponse:
    """
    A response message to report the analyzers connection status to ARES.
    """

    def __init__(self, status: ConnectionStatus, info: str = ""):
        """
        Initializes a new ConnectionStatusResponse message.
        
        Args:
            status: An enum value indicating whether the analyzers status is currently connected, disconnected, or unknown.
            info: An optional string value indicating a status message related to the analyzers current status.
        """

        self.status = status
        self.info = info

class AnalyzerState(Enum):
    UNSPECIFIED: int = 0
    ACTIVE: int = 1
    INACTIVE: int = 2
    ERROR: int = 3

class AnalyzerStateResponse:
    """
    A response message to indicate the analyzers current state.
    """

    def __init__(self, state: AnalyzerState, state_message: str):
        """
        Initializes a new AnalyzerStateResponse message.

        Args:
            state: An enum value indicated whether the analyzers state is currently active, inactive, error, or unknown.
            state_message: An optional string value indicating a status message related to the analyzers current state.
        """

        self.state = state
        self.state_message = state_message     

class InfoResponse:
    """
    A response message that provides basic information about your analyzer.
    """   

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


        