"""A simulated precision liquid pump for ARES device demos.

The pump exposes a small stateful API: a priming command, a volume-delivery
command, and a status readback.  Delivery is modeled as an instantaneous demo
operation while retaining totals so planners and analyzers can observe useful
state over multiple commands.
"""

from threading import RLock

from PyAres import (
    AresDataType,
    AresDeviceService,
    DeviceCommandDescriptor,
    DeviceCommandResponse,
    DeviceSchemaEntry,
    StatusCode,
    WidgetDescriptor,
    WidgetType,
)
from PyAres.Device.device_models import StateItem


class VirtualLiquidPump:
    """Simulated pump with bounded flow and cumulative delivered volume."""

    MIN_FLOW_RATE = 0.1
    MAX_FLOW_RATE = 25.0
    MAX_SINGLE_VOLUME = 100.0

    def __init__(self) -> None:
        self._lock = RLock()
        self._primed = False
        self._running = False
        self._flow_rate = 5.0
        self._delivered_volume = 0.0
        self._last_fluid = "water"

    def prime(self, fluid: str):
        """Prime the pump with a named fluid before dispensing."""
        fluid = fluid.strip()
        if not fluid:
            return DeviceCommandResponse(
                None,
                error_string="Fluid name cannot be empty.",
                status_code=StatusCode.INVALID_COMMAND,
            )

        with self._lock:
            self._primed = True
            self._last_fluid = fluid
            print(f"[Hardware] Pump primed with {fluid}.")
            return DeviceCommandResponse(None, status_code=StatusCode.COMMAND_SUCCESS)

    def dispense(self, volume: float, flow_rate: float):
        """Dispense a volume in milliliters at the requested rate."""
        with self._lock:
            if not self._primed:
                return DeviceCommandResponse(
                    None,
                    error_string="Prime the pump before dispensing.",
                    status_code=StatusCode.INVALID_COMMAND,
                )
            if not 0 < volume <= self.MAX_SINGLE_VOLUME:
                return DeviceCommandResponse(
                    None,
                    error_string=f"Volume must be greater than 0 and at most {self.MAX_SINGLE_VOLUME} mL.",
                    status_code=StatusCode.OUT_OF_RANGE,
                )
            if not self.MIN_FLOW_RATE <= flow_rate <= self.MAX_FLOW_RATE:
                return DeviceCommandResponse(
                    None,
                    error_string=(
                        f"Flow rate must be between {self.MIN_FLOW_RATE} and "
                        f"{self.MAX_FLOW_RATE} mL/s."
                    ),
                    status_code=StatusCode.OUT_OF_RANGE,
                )

            self._running = True
            self._flow_rate = float(flow_rate)
            self._delivered_volume += float(volume)
            self._running = False
            print(f"[Hardware] Dispensed {volume:.2f} mL at {flow_rate:.2f} mL/s.")
            return DeviceCommandResponse(
                {"dispensed_volume": float(volume), "total_volume": self._delivered_volume},
                status_code=StatusCode.COMMAND_SUCCESS,
            )

    def stop(self):
        """Stop an active dispense operation."""
        with self._lock:
            was_running = self._running
            self._running = False
            return DeviceCommandResponse(
                {"was_running": was_running},
                status_code=StatusCode.COMMAND_SUCCESS,
            )

    def get_status(self):
        with self._lock:
            return DeviceCommandResponse(
                {
                    "primed": self._primed,
                    "running": self._running,
                    "fluid": self._last_fluid,
                    "flow_rate": self._flow_rate,
                    "total_volume": self._delivered_volume,
                },
                status_code=StatusCode.COMMAND_SUCCESS,
            )

    def get_state(self) -> list[StateItem]:
        with self._lock:
            return [
                StateItem("Pump Primed", self._primed, 0, True),
                StateItem("Pump Running", self._running, 1, True),
                StateItem("Fluid", self._last_fluid, 2, True),
                StateItem("Total Delivered Volume", self._delivered_volume, 3, True),
            ]

    def safe_mode(self) -> None:
        with self._lock:
            self._running = False
            self._primed = False
            print("[Hardware] SAFE MODE: Pump stopped and unprimed.")


def _build_service() -> AresDeviceService:
    pump = VirtualLiquidPump()
    service = AresDeviceService(
        pump.safe_mode,
        pump.get_state,
        "Virtual Precision Liquid Pump",
        "A simulated pump for repeatable liquid dispensing demonstrations",
        "1.0.0",
        port=7105,
    )

    fluid_command = DeviceCommandDescriptor(
        "Prime Pump",
        "Prime the pump with the named fluid.",
        {
            "fluid": DeviceSchemaEntry(
                AresDataType.STRING,
                "Fluid name",
                user_interface_description=WidgetDescriptor(WidgetType.STRING_INPUT),
            )
        },
        {},
        render_in_ui=True,
    )
    service.add_new_command(fluid_command, pump.prime)

    dispense_output = {
        "dispensed_volume": DeviceSchemaEntry(AresDataType.NUMBER, "Volume dispensed", "mL"),
        "total_volume": DeviceSchemaEntry(AresDataType.NUMBER, "Cumulative volume", "mL"),
    }
    dispense_command = DeviceCommandDescriptor(
        "Dispense",
        "Dispense a controlled volume of the primed fluid.",
        {
            "volume": DeviceSchemaEntry(
                AresDataType.NUMBER,
                "Volume to dispense",
                "mL",
                min_number_value=0.1,
                max_number_value=pump.MAX_SINGLE_VOLUME,
                user_interface_description=WidgetDescriptor(WidgetType.NUMERIC_INPUT),
            ),
            "flow_rate": DeviceSchemaEntry(
                AresDataType.NUMBER,
                "Dispense flow rate",
                "mL/s",
                min_number_value=pump.MIN_FLOW_RATE,
                max_number_value=pump.MAX_FLOW_RATE,
                user_interface_description=WidgetDescriptor(WidgetType.NUMERIC_SLIDER, slider_step_size=0.1),
            ),
        },
        dispense_output,
        render_in_ui=True,
    )
    service.add_new_command(dispense_command, pump.dispense)

    service.add_new_command(
        DeviceCommandDescriptor(
            "Stop Pump",
            "Stop any active dispensing operation.",
            {},
            {"was_running": DeviceSchemaEntry(AresDataType.BOOLEAN, "Whether the pump was running")},
            render_in_ui=True,
        ),
        pump.stop,
    )
    service.add_new_command(
        DeviceCommandDescriptor(
            "Get Pump Status",
            "Read pump priming, flow, and cumulative volume status.",
            {},
            {
                "primed": DeviceSchemaEntry(AresDataType.BOOLEAN, "Whether the pump is primed"),
                "running": DeviceSchemaEntry(AresDataType.BOOLEAN, "Whether the pump is running"),
                "fluid": DeviceSchemaEntry(AresDataType.STRING, "Primed fluid name"),
                "flow_rate": DeviceSchemaEntry(AresDataType.NUMBER, "Current flow rate", "mL/s"),
                "total_volume": DeviceSchemaEntry(AresDataType.NUMBER, "Cumulative volume", "mL"),
            },
            render_in_ui=True,
        ),
        pump.get_status,
    )
    return service


if __name__ == "__main__":
    print("Virtual Precision Liquid Pump Service Running...")
    _build_service().start()
