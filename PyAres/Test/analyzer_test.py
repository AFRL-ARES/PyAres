from PyAres import AresAnalyzerService
from PyAres import AnalysisRequest
from PyAres import Analysis
from PyAres import AresDataType
from PyAres import Outcome

def analyze(request: AnalysisRequest) -> Analysis:
    #Custom Analysis Logic
    #growth = request.inputs.get("Growth")
    temperature = request.inputs.get("Temperature")

    #print(f"Growth: {growth}")
    print(f"Temperature: {temperature}")

    analysis = Analysis(result=temperature, outcome=Outcome.WARNING, error_string="This is a test analyzer warning!")
    return analysis


if __name__ == "__main__":
    #Basic details about your analyzer
    name = "Python Test Analyzer"
    version = "0.0.1"
    description = "This is a test analyzer to demonstrate working with PyAres to create analyzers!"
    pythonDemoAnalyzer = AresAnalyzerService(analyze, name, version, description)

    #Add Analysis Parameters
    #pythonDemoAnalyzer.add_analysis_parameter("Growth", AresDataType.NUMBER)
    pythonDemoAnalyzer.add_analysis_parameter("Temperature", AresDataType.NUMBER)

    pythonDemoAnalyzer.start()