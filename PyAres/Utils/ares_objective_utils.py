from ..Models import Objective
from ares_datamodel.analyzing import analysis_pb2
from . import ares_value_utils, ares_struct_utils

def python_objective_to_proto(py_objective: Objective) -> analysis_pb2.Objective:
  proto_objective = analysis_pb2.Objective()
  proto_objective.objective_value.CopyFrom(ares_value_utils.create_ares_value(py_objective.objective_value))
  proto_objective.objective_name = py_objective.objective_name
  
  if py_objective.metadata:
    proto_objective.objective_metadata = ares_struct_utils.create_empty_struct()

    for key, value in py_objective.metadata:
      ares_struct_utils.add_value_to_struct(proto_objective.objective_metadata, key, value)

  return proto_objective

def proto_objective_to_python(proto_objective: analysis_pb2.Objective) -> Objective:
  python_objective = Objective(proto_objective.objective_name, ares_value_utils.ares_value_to_py(proto_objective.objective_value))

  if proto_objective.objective_metadata:
    python_objective.metadata = ares_struct_utils.ares_struct_to_dict(proto_objective.objective_metadata)

  return python_objective