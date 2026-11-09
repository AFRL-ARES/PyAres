"""A simulated environmental chamber with temperature and humidity control.

The chamber is intentionally small but models two useful device behaviors for
examples: readings move gradually toward their setpoints, and invalid requests
return a structured :class:`DeviceCommandResponse` instead of raising an
exception.
"""

from threading import RLock
from time import monotonic

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


class VirtualEnvironmentalChamber:
    """Simulate a benchtop chamber with independent temperature and humidity."""

    AMBIENT_TEMPERATURE = 22.0
    AMBIENT_HUMIDITY = 45.0
    MIN_TEMPERATURE = 4.0
    MAX_TEMPERATURE = 80.0
    MIN_HUMIDITY = 10.0
    MAX_HUMIDITY = 90.0
    TEMPERATURE_RATE = 3.0  # degrees C per second
    HUMIDITY_RATE = 8.0  # percentage points per second

    def __init__(self) -> None:
        self._lock = RLock()
        self._last_update = monotonic()
        self._target_temperature = self.AMBIENT_TEMPERATURE
        self._target_humidity = self.AMBIENT_HUMIDITY
        self._temperature = self.AMBIENT_TEMPERATURE
        self._humidity = self.AMBIENT_HUMIDITY
        self._door_open = False

    def _update_readings(self) -> None:
        now = monotonic()
        elapsed = max(0.0, now - self._last_update)
        self._last_update = now

        temperature_change = self.TEMPERATURE_RATE * elapsed
        humidity_change = self.HUMIDITY_RATE * elapsed
        self._temperature += max(
            -temperature_change,
            min(temperature_change, self._target_temperature - self._temperature),
        )
        self._humidity += max(
            -humidity_change,
            min(humidity_change, self._target_humidity - self._humidity),
        )

    @staticmethod
    def _out_of_range(value: float, minimum: float, maximum: float) -> bool:
        return not minimum <= value <= maximum

    def set_conditions(self, temperature: float, humidity: float):
        """Set chamber targets after validating both requested conditions."""
        with self._lock:
            if self._out_of_range(temperature, self.MIN_TEMPERATURE, self.MAX_TEMPERATURE):
                return DeviceCommandResponse(
                    None,
                    error_string=(
                        f"Temperature must be between {self.MIN_TEMPERATURE} and "
                        f"{self.MAX_TEMPERATURE} °C."
                    ),
                    status_code=StatusCode.OUT_OF_RANGE,
                )
            if self._out_of_range(humidity, self.MIN_HUMIDITY, self.MAX_HUMIDITY):
                return DeviceCommandResponse(
                    None,
                    error_string=(
                        f"Humidity must be between {self.MIN_HUMIDITY} and "
                        f"{self.MAX_HUMIDITY}%."
                    ),
                    status_code=StatusCode.OUT_OF_RANGE,
                )
            if self._door_open:
                return DeviceCommandResponse(
                    None,
                    error_string="Close the chamber door before changing conditions.",
                    status_code=StatusCode.INVALID_COMMAND,
                )

            self._update_readings()
            self._target_temperature = float(temperature)
            self._target_humidity = float(humidity)
            return DeviceCommandResponse(None, status_code=StatusCode.COMMAND_SUCCESS)

    def set_door(self, open: bool):
        """Open or close the simulated chamber door."""
        with self._lock:
            self._update_readings()
            self._door_open = bool(open)
            if self._door_open:
                # An open door makes the chamber move back toward ambient.
                self._target_temperature = self.AMBIENT_TEMPERATURE
                self._target_humidity = self.AMBIENT_HUMIDITY
            return DeviceCommandResponse(None, status_code=StatusCode.COMMAND_SUCCESS)

    def read_conditions(self):
        """Read current conditions and the active targets."""
        with self._lock:
            self._update_readings()
            return DeviceCommandResponse(
                {
                    "temperature": self._temperature,
                    "humidity": self._humidity,
                    "target_temperature": self._target_temperature,
                    "target_humidity": self._target_humidity,
                    "door_open": self._door_open,
                },
                status_code=StatusCode.COMMAND_SUCCESS,
            )

    def get_state(self) -> list[StateItem]:
        with self._lock:
            self._update_readings()
            return [
                StateItem("Temperature", self._temperature, 0, True),
                StateItem("Humidity", self._humidity, 1, True),
                StateItem("Door Open", self._door_open, 2, True),
            ]

    def safe_mode(self) -> None:
        """Return the chamber to safe ambient conditions."""
        with self._lock:
            self._update_readings()
            self._target_temperature = self.AMBIENT_TEMPERATURE
            self._target_humidity = self.AMBIENT_HUMIDITY
            self._door_open = False
            print("[Hardware] SAFE MODE: Chamber targets reset to ambient conditions.")


def _build_service() -> AresDeviceService:
    chamber = VirtualEnvironmentalChamber()
    service = AresDeviceService(
        chamber.safe_mode,
        chamber.get_state,
        "Virtual Environmental Chamber",
        "A simulated chamber for temperature and humidity experiments",
        "1.0.0",
        port=7104,
    )

    numeric_input = WidgetDescriptor(WidgetType.NUMERIC_INPUT)
    set_conditions = DeviceCommandDescriptor(
        "Set Conditions",
        "Set the chamber temperature and relative humidity targets.",
        {
            "temperature": DeviceSchemaEntry(
                AresDataType.NUMBER,
                "Target temperature",
                "°C",
                min_number_value=chamber.MIN_TEMPERATURE,
                max_number_value=chamber.MAX_TEMPERATURE,
                user_interface_description=numeric_input,
            ),
            "humidity": DeviceSchemaEntry(
                AresDataType.NUMBER,
                "Target relative humidity",
                "%",
                min_number_value=chamber.MIN_HUMIDITY,
                max_number_value=chamber.MAX_HUMIDITY,
                user_interface_description=numeric_input,
            ),
        },
        {},
        render_in_ui=True,
    )
    service.add_new_command(set_conditions, chamber.set_conditions)

    door_command = DeviceCommandDescriptor(
        "Set Door",
        "Open or close the chamber door.",
        {
            "open": DeviceSchemaEntry(
                AresDataType.BOOLEAN,
                "Whether the door is open",
                user_interface_description=WidgetDescriptor(WidgetType.BOOLEAN_TOGGLE),
            )
        },
        {},
        render_in_ui=True,
    )
    service.add_new_command(door_command, chamber.set_door)

    condition_schema = {
        "temperature": DeviceSchemaEntry(AresDataType.NUMBER, "Current temperature", "°C"),
        "humidity": DeviceSchemaEntry(AresDataType.NUMBER, "Current relative humidity", "%"),
        "target_temperature": DeviceSchemaEntry(AresDataType.NUMBER, "Temperature target", "°C"),
        "target_humidity": DeviceSchemaEntry(AresDataType.NUMBER, "Humidity target", "%"),
        "door_open": DeviceSchemaEntry(AresDataType.BOOLEAN, "Whether the door is open"),
    }
    service.add_new_command(
        DeviceCommandDescriptor(
            "Read Conditions",
            "Read current chamber conditions and targets.",
            {},
            condition_schema,
            render_in_ui=True,
        ),
        chamber.read_conditions,
    )
    return service


if __name__ == "__main__":
    print("Virtual Environmental Chamber Service Running...")
    _build_service().start()
