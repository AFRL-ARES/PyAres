from ..Models import PlanStatusCode
from ares_datamodel.planning import plan_pb2
from typing import cast

def python_plan_status_to_proto_plan_status(py_value: PlanStatusCode) -> plan_pb2.PlanStatusCode:
  val = cast(plan_pb2.PlanStatusCode, py_value)
  return val

def proto_plan_status_to_python_plan_status(proto_value: plan_pb2.PlanStatusCode) -> PlanStatusCode:
  return PlanStatusCode(proto_value)