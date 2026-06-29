from ares_datamodel.analyzing import analysis_pb2
from ..Models import AnalysisResult
from . import ares_objective_utils, ares_outcome_utils

def proto_analysis_result_to_python(proto_analysis: analysis_pb2.AnalysisResponse) -> AnalysisResult:
  python_result = AnalysisResult([ares_objective_utils.proto_objective_to_python(proto_obj) for proto_obj in proto_analysis.objectives], 
                                 ares_outcome_utils.proto_ares_outcome_to_python_ares_outcome(proto_analysis.analysis_outcome))
  
  if proto_analysis.error_string is not "":
    python_result.error_string = proto_analysis.error_string

  return python_result