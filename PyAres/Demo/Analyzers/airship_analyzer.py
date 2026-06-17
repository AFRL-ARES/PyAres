from PyAres import AresAnalyzerService, AnalysisRequest, Analysis, AresDataType, Outcome

def analysis_logic(request: AnalysisRequest):
  result = int(request.inputs["ShotOutcome"])
  print(f"Analyzing, result is: {result}")
  response = Analysis(result=result, outcome=Outcome.SUCCESS)
  return response

if __name__ == "__main__":
  print("Welcome to the Airship Analyzer")

  analyzer = AresAnalyzerService(
    custom_analysis_logic=analysis_logic, 
    description="An analyzer for use with the Airship Device", 
    name="Airship Analyzer",
    version="1.0.0")
  
  analyzer.add_analysis_parameter("ShotOutcome", AresDataType.NUMBER)

  analyzer.start()
