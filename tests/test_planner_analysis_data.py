import warnings
from typing import List

import pytest

from PyAres.Planning.planner_models import (
    PlanRequest,
    PlanningParameter,
    ParameterHistoryItem,
    AnalysisDataEntry,
)
from PyAres.Models import RequestMetadata, AresDataType
from PyAres.Planning.planning_service import AresPlannerServiceWrapper
from tests.mock_grpc_context import MockGrpcContext
from ares_datamodel.planning import plan_pb2
from ares_datamodel import ares_struct_pb2


def _make_dummy_parameter(name: str) -> PlanningParameter:
    return PlanningParameter(
        name=name,
        data_type=AresDataType.ARES_DATA_TYPE_DOUBLE if hasattr(AresDataType, "ARES_DATA_TYPE_DOUBLE") else AresDataType(0),
        minimum_value=0.0,
        maximum_value=1.0,
        param_history=[ParameterHistoryItem(0.1, 0.1)],
        is_planned=True,
        is_result=False,
        planner_name="test_planner",
        initial_value=0.0,
    )


def test_plan_request_analysis_data_native_and_no_proto_leakage():
    """
    Verify that PlanRequest stores analysis_data as native AnalysisDataEntry objects
    containing native Objective instances, and does not expose proto messages.
    """
    # Build dummy objectives (native Objective from analyzer_models)
    from PyAres.Analyzing.analyzer_models import Objective

    obj1 = Objective("obj1", 1.23, {"units": "unit1"})
    obj2 = Objective("obj2", 4.56, {"units": "unit2"})

    entry1 = AnalysisDataEntry(analysis_objectives=[obj1])
    entry2 = AnalysisDataEntry(analysis_objectives=[obj2])

    params: List[PlanningParameter] = [_make_dummy_parameter("p1")]

    req = PlanRequest(
        parameters=params,
        settings={"adapter": "settings"},
        analysis_results=[0.5, 0.6],
        metadata=RequestMetadata.from_default_values(),
        batch_size=2,
        previous_plan_status_codes=[],
        analysis_data=[entry1, entry2],
    )

    # Ensure we got the entries we expect
    assert len(req.analysis_data) == 2
    assert isinstance(req.analysis_data[0], AnalysisDataEntry)
    assert isinstance(req.analysis_data[1], AnalysisDataEntry)

    # Ensure objectives are native Objective instances
    first_objectives = req.analysis_data[0].analysis_objectives
    second_objectives = req.analysis_data[1].analysis_objectives

    assert len(first_objectives) == 1
    assert len(second_objectives) == 1

    assert isinstance(first_objectives[0], Objective)
    assert isinstance(second_objectives[0], Objective)

    all_objectives = req.analysis_objectives
    assert len(all_objectives) == 2
    assert isinstance(all_objectives[0][0], Objective)
    assert isinstance(all_objectives[1][0], Objective)

    # String representation should include analysis_data and not raise warnings
    with warnings.catch_warnings(record=True) as w:
        s = str(req)
        assert "analysis_data:" in s
        assert not any(issubclass(wi.category, DeprecationWarning) for wi in w)


def test_plan_request_analysis_results_deprecation_on_access_only():
    """
    Verify that accessing PlanRequest.analysis_results emits a DeprecationWarning,
    but the internal storage remains correct and printing does not emit the warning.
    """
    params: List[PlanningParameter] = [_make_dummy_parameter("p1")]
    req = PlanRequest(
        parameters=params,
        settings={},
        analysis_results=[1.0, 2.0],
        metadata=RequestMetadata.from_default_values(),
        batch_size=1,
        previous_plan_status_codes=[],
        analysis_data=[],
    )

    # Internal storage is as expected
    assert req._analysis_results == [1.0, 2.0]

    # Accessing the property should emit a DeprecationWarning
    with pytest.warns(DeprecationWarning):
        vals = req.analysis_results
    assert vals == [1.0, 2.0]

    # Calling __str__ should not emit DeprecationWarning
    with warnings.catch_warnings(record=True) as w:
        s = str(req)
        assert "analysis_results:" in s
        assert not any(issubclass(wi.category, DeprecationWarning) for wi in w)


def test_planner_service_wrapper_maps_proto_analysis_data_to_native(monkeypatch):
    """
    Integration-style test that verifies AresPlannerServiceWrapper.Plan converts
    proto AnalysisData messages into native AnalysisDataEntry with native Objective
    instances, and passes them into the PlanRequest.
    """
    from PyAres.Analyzing.analyzer_models import Objective

    captured_request = {"req": None}

    def custom_logic(req: PlanRequest):
        captured_request["req"] = req
        # Return an empty list of plans to keep response handling simple
        return []

    wrapper = AresPlannerServiceWrapper(
        service_name="test_service",
        version="1.0.0",
        description="Test planner service",
        timeout=30,
        custom_plan_logic=custom_logic,
    )

    planning_request = plan_pb2.PlanningRequest()
    planning_request.adapter_settings.CopyFrom(ares_struct_pb2.AresStruct())
    planning_request.analysis_results.extend([0.1, 0.2])
    planning_request.metadata.system_name = "test_service"
    planning_request.batch_size = 1
    proto_param = planning_request.planning_parameters.add()
    proto_param.parameter_name = "p1"
    proto_param.maximum_value = 1.0
    proto_param.minimum_value = 0.0
    proto_param.is_planned = True
    proto_param.is_result = False
    proto_param.planner_name = "test_planner"

    # Add default data type
    if hasattr(proto_param, "data_type"):
        proto_param.data_type = 0

    proto_param.initial_value.CopyFrom(ares_struct_pb2.AresValue(float_value=0.0))

    analysis_data_entry = planning_request.analysis_data.add()

    proto_obj = analysis_data_entry.analysis_objectives.add()
    proto_obj.objective_name = "proto_obj"
    proto_obj.objective_value.CopyFrom(ares_struct_pb2.AresValue(float_value=3.14))
    proto_obj.objective_metadata.CopyFrom(ares_struct_pb2.AresStruct())

    # Call Plan with a mock gRPC context
    context = MockGrpcContext()
    _ = wrapper.Plan(planning_request, context)

    # Verify the captured PlanRequest
    req = captured_request["req"]
    assert req is not None

    # Ensure analysis_data contains native AnalysisDataEntry objects
    assert len(req.analysis_data) == 1
    assert isinstance(req.analysis_data[0], AnalysisDataEntry)

    # Ensure objectives inside are native Objective instances
    objectives = req.analysis_data[0].analysis_objectives
    assert len(objectives) == 1
    assert isinstance(objectives[0], Objective)
    assert objectives[0].objective_name == "proto_obj"