from PyAres import AresAnalyzerService, AnalysisRequest, Analysis, AresDataType, Outcome

def analyze_sample(request: AnalysisRequest) -> Analysis:
    # 1. Extract inputs
    # 'Growth_Metric' would come from a sensor or previous step
    raw_value = request.inputs.get("Growth_Metric")

    if raw_value is None:
        return Analysis(result=0.0, outcome=Outcome.FAILURE)
    
    # 2. Perform Logic
    print(f"Analyzing sample with value: {raw_value}")
    
    calculated_score = raw_value * 1.5 # Placeholder logic
    is_success = calculated_score > 10.0 # Define success criteria
    
    # 3. Return Result
    return Analysis(result=calculated_score, outcome=Outcome.SUCCESS)

if __name__ == "__main__":
    service = AresAnalyzerService(
        analyze_sample, 
        "Growth Analyzer", 
        "0.1.0", 
        "Calculates growth viability"
    )

    # Define what data we need from ARES
    service.add_analysis_parameter("Growth_Metric", AresDataType.NUMBER)

    service.start()