import unittest

from PyAres.Models import AresDataType, AresSchemaEntry
from PyAres.Visualizers import (
    AresVisualizerService,
    AresVisualizerServiceWrapper,
    VisualizationOption,
)
from ares_datamodel.visualizing.remote import (
    ares_remote_visualizer_service_pb2 as visualizer_service,
)
from PyAres.Utils import ares_value_utils


class TestAresVisualizerService(unittest.TestCase):
    def setUp(self):
        self.requests = []

        def render(request):
            self.requests.append(request)
            return {"points": len(request.visualization_data)}

        self.wrapper = AresVisualizerServiceWrapper("Visualizer", "1.0", "", 30)
        self.wrapper.add_visualization(
            VisualizationOption(
                visualization_name="line",
                visualization_input_schema={
                    "value": AresSchemaEntry(AresDataType.NUMBER),
                },
                chart_type="line",
            ),
            render,
        )

    def _request(self):
        request = visualizer_service.GetUpdatedVisualRequest(
            visualization_name="line"
        )
        point = request.visualization_data.add(index=4)
        point.values.fields["value"].CopyFrom(
            ares_value_utils.create_ares_value(12.5)
        )
        return request

    def test_visualization_options_include_schema(self):
        response = self.wrapper.GetVisualizationOptions(None, None)

        self.assertEqual(response.visualization_options[0].chart_type, "line")
        self.assertEqual(
            response.visualization_options[0]
            .visualization_input_schema.fields["value"]
            .type,
            AresDataType.NUMBER.value,
        )

    def test_request_converts_data_and_serializes_mapping(self):
        response = self.wrapper.RequestUpdatedVisualization(self._request(), None)

        self.assertEqual(response.chart_json_data, '{"points": 1}')
        self.assertEqual(self.requests[0].visualization_data[0].index, 4)
        self.assertEqual(self.requests[0].visualization_data[0].values, {"value": 12.5})

    def test_streaming_callback_can_return_multiple_charts(self):
        self.wrapper.add_visualization(
            VisualizationOption("stream"),
            lambda request: ["first", "second"],
        )
        request = visualizer_service.GetUpdatedVisualRequest(
            visualization_name="stream"
        )

        responses = list(self.wrapper.StreamPlotlyVisualization(request, None))

        self.assertEqual([response.chart_json_data for response in responses], ["first", "second"])

    def test_service_registers_generated_servicer(self):
        service = AresVisualizerService(None, "Visualizer", "1.0", port=0)
        try:
            self.assertIsNotNone(service._service_wrapper)
        finally:
            service.stop()


if __name__ == "__main__":
    unittest.main()
