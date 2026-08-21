from PyAres import *

def analyze_sample(request: AnalysisRequest) -> AnalysisResponse:
    # 1. Extract inputs
    # 'Growth_Metric' would come from a sensor or previous step
    raw_value = request.inputs.get("Growth_Metric")

    if raw_value is None:
        return AnalysisResponse(objectives=[], outcome=Outcome.FAILURE, error_string="No raw value provided, cannot analyze")
    
    # 2. Perform Logic
    print(f"Analyzing sample with value: {raw_value}")
    
    calculated_score = raw_value * 1.5

    objective_score = Objective("Calculated Score", calculated_score) 
    
    # 3. Return Result
    return AnalysisResponse(objectives=[objective_score], outcome=Outcome.SUCCESS)

if __name__ == "__main__":
    service = AresAnalyzerService(
        analyze_sample, 
        "Growth Analyzer", 
        "0.1.0", 
        "Calculates growth viability"
    )

    # Define what data we need from ARES
    service.add_analysis_parameter("Growth_Metric", AresDataType.NUMBER)
    
    service.add_setting("Random Setting", AresDataType.NUMBER, 
                        default_value=250, 
                        limits=Limits(1, 500),
                        description="This is a random setting, it is purely for demonstration purposes")

    service.start()