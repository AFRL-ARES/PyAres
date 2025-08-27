from PyAres import AresAnalyzerService
from PyAres import AnalysisRequest
from PyAres import Analysis
from PyAres import AresDataType

def analyze(request: AnalysisRequest) -> Analysis:
    print("Analysis Requested!")
    
    #PyARES should ensure all your required inputs are here, but use .get to follow best practice
    growth = request.inputs.get("Growth")
    temperature = request.inputs.get("Temperature")

    #PyARES will also provide your settings in much the same way
    string_setting = request.settings.get("String Setting")
    number_setting = request.settings.get("Number Setting")
    boolean_setting = request.settings.get("Boolean Setting")

    print(f"Growth: {growth}")
    print(f"Temperature: {temperature}")

    #Typically do something more intelligent here... but I'm just writing some code
    analysis = Analysis(result=6.0, success=True)
    return analysis


if __name__ == "__main__":
    #Basic details about your analyzer
    name = "Python Test Analyzer"
    version = "0.0.1"
    description = "This is a test analyzer to demonstrate working with PyAres to create analyzers!"
    pythonDemoAnalyzer = AresAnalyzerService(analyze, name, version, description)

    #Add Analysis Parameters
    pythonDemoAnalyzer.add_analysis_parameter("Growth", AresDataType.NUMBER)
    pythonDemoAnalyzer.add_analysis_parameter("Temperature", AresDataType.NUMBER)

    #Add Settings
    pythonDemoAnalyzer.add_setting("String Setting", AresDataType.STRING)
    pythonDemoAnalyzer.add_setting("Number Setting", AresDataType.NUMBER)
    pythonDemoAnalyzer.add_setting("Boolean Setting", AresDataType.BOOLEAN)
    pythonDemoAnalyzer.add_setting("String Array Setting", AresDataType.STRING_ARRAY)
    pythonDemoAnalyzer.add_setting("Number Array Setting", AresDataType.NUMBER_ARRAY)
    pythonDemoAnalyzer.add_setting("Constrained Strings", AresDataType.STRING_ARRAY, True, ["One", "Two", "Three"])
    pythonDemoAnalyzer.add_setting("Constrained Numbers", AresDataType.NUMBER_ARRAY, True, [1, 2, 3])

    #Set Analyzer Timeout
    pythonDemoAnalyzer.set_timeout(60)

    pythonDemoAnalyzer.start()