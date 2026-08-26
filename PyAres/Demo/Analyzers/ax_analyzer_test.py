from PyAres import *
import math
import random

def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """
    Evaluates the parameters chosen by your AX Planner and returns a simulated yield.
    """
    
    try:
        # 1. Extract the values ARES OS logged for this specific iteration.
        # Ensure the parameter names in your ARES Campaign match these strings exactly.
        temperature = request.inputs["Temperature"]
        concentration = request.inputs["Concentration"]
        
        # 2. Define the "Hidden Ground Truth"
        # This is the goal your AX Planner is trying to discover.
        ideal_temp = 165.0
        ideal_conc = 3.2
        max_yield = 100.0
        
        # 3. Calculate the distance penalty (the variances control the "width" of the peak)
        temp_variance = 400.0  
        conc_variance = 2.0    
        
        distance_penalty = (((temperature - ideal_temp) ** 2) / temp_variance) + \
                           (((concentration - ideal_conc) ** 2) / conc_variance)
                           
        # 4. Calculate theoretical yield and add noise
        simulated_yield = max_yield * math.exp(-distance_penalty)
        noise = random.gauss(0, 1.5) # mean=0, std_dev=1.5
        
        # Clamp the final yield between 0 and 100%
        final_yield = max(0.0, min(100.0, simulated_yield + noise))
        
        print(f"[Demo Analyzer] Received T={temperature:.1f}, C={concentration:.1f} | Calculated Yield: {final_yield:.2f}%")
    
        # Preferred new usage: return an objective-based AnalysisResponse
        return AnalysisResponse(
            objectives=[
                Objective(
                    objective_name="yield",
                    objective_value=final_yield,
                    objective_metadata={"units": "%"}
                )
            ]
        )

    except Exception as e:
        print(f"[Demo Analyzer] Error during analysis: {e}")
        # If extraction fails (e.g., missing parameter names), return a terrible score so the planner learns to avoid it
        return AnalysisResponse(
            objectives=[
                Objective(
                    objective_name="yield",
                    objective_value=None,
                    objective_metadata={"error": str(e)}
                )
            ],
            outcome=Outcome.FAILURE,
            error_string=str(e),
        )



if __name__ == "__main__":
    # Initialize the Analyzer Service
    demo_analyzer = AresAnalyzerService(custom_analysis_logic=analyze,
    name="Simulated Yield Demo",
    version="1.0.0",
    description="Calculates a simulated material yield based on a hidden ideal Temperature (165) and Concentration (3.2).",
    port=8200)

    demo_analyzer.add_analysis_parameter("Temperature", AresDataType.NUMBER)
    demo_analyzer.add_analysis_parameter("Concentration", AresDataType.NUMBER)

    demo_analyzer.add_objective_output("yield", AresDataType.NUMBER, "A numeric value that indicates the experiments yielded result")

    print("Starting PyAres Simulated Goal Analyzer...")
    demo_analyzer.start()