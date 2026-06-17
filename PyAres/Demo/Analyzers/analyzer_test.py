from PyAres import AresAnalyzerService, AnalysisRequest, AnalysisResponse, AresDataType, Outcome, Limits

def analyze(request: AnalysisRequest) -> AnalysisResponse:
    #Custom Analysis Logic
    temp_one = request.inputs.get("Temperature One")
    print("Processing Analysis Request")

    if not isinstance(temp_one, float):
        print("Temperature One was not a float")
        print(temp_one)
        temp_one = 0.0

    else:
        print(f"Temperature One: {temp_one}")
    
    analysis = AnalysisResponse(result=temp_one)
    return analysis


if __name__ == "__main__":
    #Basic details about your analyzer
    name = "Python Test Analyzer"
    version = "0.0.1"
    description = "This is a test analyzer to demonstrate working with PyAres to create analyzers!"
    pythonDemoAnalyzer = AresAnalyzerService(analyze, name, version, description)

    #Add Analysis Parameters
    pythonDemoAnalyzer.add_analysis_parameter("Temperature", AresDataType.NUMBER)
    pythonDemoAnalyzer.add_setting(setting_name="", setting_type=AresDataType.NULL, optional=True, constraints=[], limits=Limits(0, 10000))
    pythonDemoAnalyzer.start()