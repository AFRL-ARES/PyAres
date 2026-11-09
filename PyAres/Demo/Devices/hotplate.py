"""A multi-burner virtual hotplate device.

This demo intentionally models a little more of a real device than simply
storing the requested value: each burner has an independent setpoint and its
sensor value approaches that setpoint over time with a small amount of noise.
"""

from random import Random
from threading import RLock
from time import monotonic
from PyAres import *
from PyAres.Device.device_models import StateItem


class VirtualHotplate:
    """Simulated four-burner hotplate with independent temperature control."""

    AMBIENT_TEMP = 25.0
    MIN_TEMP = AMBIENT_TEMP
    MAX_TEMP = 300.0
    HEATING_RATE = 18.0  # degrees C per second when far from the setpoint
    COOLING_RATE = 8.0
    SENSOR_NOISE = 0.35

    def __init__(self, burner_count: int = 4):
        if burner_count < 1:
            raise ValueError("A hotplate must have at least one burner")

        self._lock = RLock()
        self._random = Random()
        self._last_update = monotonic()
        self._burners = {
            burner: {"target_temp": self.AMBIENT_TEMP, "current_temp": self.AMBIENT_TEMP}
            for burner in range(1, burner_count + 1)
        }

    @property
    def burner_count(self) -> int:
        return len(self._burners)

    def _update_temperatures(self) -> None:
        """Advance the thermal simulation and refresh each sensor reading."""
        now = monotonic()
        elapsed = max(0.0, now - self._last_update)
        self._last_update = now

        for burner in self._burners.values():
            target = burner["target_temp"]
            current = burner["current_temp"]
            rate = self.HEATING_RATE if target > current else self.COOLING_RATE
            maximum_change = rate * elapsed
            difference = target - current
            change = max(-maximum_change, min(maximum_change, difference))
            burner["current_temp"] = current + change

    def _validate_burner(self, burner: int) -> bool:
        return burner in self._burners

    def set_temperature(self, burner: int, temp: float):
        """Set one burner's target temperature; its sensor changes gradually."""
        with self._lock:
            if not self._validate_burner(burner):
                return DeviceCommandResponse(
                    None,
                    error_string=f"Burner must be between 1 and {self.burner_count}.",
                    status_code=StatusCode.INVALID_COMMAND,
                )
            if not self.MIN_TEMP <= temp <= self.MAX_TEMP:
                return DeviceCommandResponse(
                    None,
                    error_string=f"Temperature must be between {self.MIN_TEMP} and {self.MAX_TEMP} °C.",
                    status_code=StatusCode.OUT_OF_RANGE,
                )

            self._update_temperatures()
            self._burners[burner]["target_temp"] = float(temp)
            print(f"[Hardware] Burner {burner} target set to {temp:.1f}°C.")
            return DeviceCommandResponse(None, status_code=StatusCode.COMMAND_SUCCESS)

    def get_temperature(self):
        """Read all burners, including independent targets and current readings."""
        with self._lock:
            self._update_temperatures()
            readings = {}
            for burner_number, values in self._burners.items():
                # Noise is applied to the reading, not the simulated thermal state,
                # so successive reads vary without randomly walking away.
                readings[f"burner_{burner_number}"] = {
                    "target_temp": values["target_temp"],
                    "current_temp": max(
                        self.AMBIENT_TEMP,
                        values["current_temp"] + self._random.uniform(-self.SENSOR_NOISE, self.SENSOR_NOISE),
                    ),
                }
            print("[Hardware] Retrieving temperatures for all burners...")
            return DeviceCommandResponse(readings, status_code=StatusCode.COMMAND_SUCCESS)

    def get_state(self) -> list[StateItem]:
        """Return ordered, UI-visible state items for ARES logging and display."""
        with self._lock:
            self._update_temperatures()
            state_items = []
            for burner_number, values in self._burners.items():
                item_index = (burner_number - 1) * 2
                state_items.extend(
                    [
                        StateItem(
                            name=f"Burner {burner_number} Target Temperature",
                            value=values["target_temp"],
                            index=item_index,
                            display_on_UI=True,
                        ),
                        StateItem(
                            name=f"Burner {burner_number} Current Temperature",
                            value=values["current_temp"],
                            index=item_index + 1,
                            display_on_UI=True,
                        ),
                    ]
                )
            return state_items

    def safe_mode(self):
        """Turn every heater off and let the burners return to room temperature."""
        with self._lock:
            self._update_temperatures()
            for burner in self._burners.values():
                burner["target_temp"] = self.AMBIENT_TEMP
            print("[Hardware] SAFE MODE TRIGGERED: All heaters off.")


def _temperature_schema() -> DeviceSchemaEntry:
    return DeviceSchemaEntry(AresDataType.NUMBER, "Temperature", "Celsius")


if __name__ == "__main__":
    my_hotplate = VirtualHotplate(burner_count=4)

    service = AresDeviceService(
        my_hotplate.safe_mode,
        my_hotplate.get_state,
        "Virtual Four-Burner Hotplate",
        "A simulated hotplate with independent thermal sensors and setpoints",
        "2.0.0",
    )

    burner_ui = WidgetDescriptor(WidgetType.DROPDOWN)
    temperature_ui = WidgetDescriptor(WidgetType.NUMERIC_SLIDER, slider_step_size=0.5)
    set_input_schema = {
        "burner": DeviceSchemaEntry(
            AresDataType.INT,
            "Burner number",
            constraints=list(range(1, my_hotplate.burner_count + 1)),
            user_interface_description=burner_ui,
        ),
        "temp": DeviceSchemaEntry(
            AresDataType.NUMBER,
            "Target temperature",
            "Celsius",
            min_number_value=my_hotplate.MIN_TEMP,
            max_number_value=my_hotplate.MAX_TEMP,
            user_interface_description=temperature_ui,
        ),
    }
    set_cmd = DeviceCommandDescriptor(
        "Set Burner Temperature",
        "Set the target temperature for one burner.",
        set_input_schema,
        {},
        render_in_ui=True,
    )
    service.add_new_command(set_cmd, my_hotplate.set_temperature)

    burner_output_schema = {
        f"burner_{burner}": DeviceSchemaEntry(
            AresDataType.STRUCT,
            f"Burner {burner} temperatures",
            struct_schema={
                "target_temp": _temperature_schema(),
                "current_temp": _temperature_schema(),
            },
        )
        for burner in range(1, my_hotplate.burner_count + 1)
    }
    get_cmd = DeviceCommandDescriptor(
        "Get Burner Temperatures",
        "Read target and simulated current temperatures for every burner.",
        {},
        burner_output_schema,
        render_in_ui=True,
    )
    service.add_new_command(get_cmd, my_hotplate.get_temperature)

    print("Virtual Four-Burner Hotplate Service Running...")
    service.start()
