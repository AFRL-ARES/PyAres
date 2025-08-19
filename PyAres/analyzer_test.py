from PyAres import AresAnalyzerService
from PyAres import AnalysisRequest
from PyAres import Analysis
from PyAres import AresDataType

def Analyze(request: AnalysisRequest) -> Analysis:
    print("Analysis Requested!")
    
    #PyARES should ensure all your required inputs are here, but use .get to follow best practice
    growth = request.inputs.get("Growth")
    temperature = request.inputs.get("Temperature")

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
    pythonDemoAnalyzer = AresAnalyzerService(Analyze, name, version, description)

    #Add Analysis Parameters
    pythonDemoAnalyzer.AddAnalysisParameter("Growth", AresDataType.NUMBER)
    pythonDemoAnalyzer.AddAnalysisParameter("Temperature", AresDataType.NUMBER)

    #Set Analyzer Timeout
    pythonDemoAnalyzer.SetTimeout(60)

    pythonDemoAnalyzer.start()