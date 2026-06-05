import random

from PyAres import AresDeviceService, AresDataType, DeviceCommandDescriptor, DeviceSchemaEntry


class TestDevice:
    def fail(self):
        """Intentionally fails so command failure handling can be tested."""
        print("[Test Device] Running intentionally failing command...")
        raise RuntimeError("Intentional test command failure")

    def maybe_fail(self):
        """Fails half the time and otherwise returns 20."""
        print("[Test Device] Running command with a 50% failure chance...")
        if random.random() < 0.5:
            raise RuntimeError("Random test command failure")

        print("[Test Device] Command succeeded and returned 20.")
        return {"number": 20}

    def get_state(self):
        return {}

    def safe_mode(self):
        print("[Test Device] Safe mode triggered.")


if __name__ == "__main__":
    test_device = TestDevice()

    service = AresDeviceService(
        test_device.safe_mode,
        test_device.get_state,
        "Test Device",
        "A device with commands for testing ARES failure handling",
        "1.0.0",
        port=7102,
    )

    fail_command = DeviceCommandDescriptor(
        "Fail",
        "Intentionally throws an exception",
        {},
        {},
    )
    service.add_new_command(fail_command, test_device.fail)

    maybe_fail_output_schema = {
        "output": DeviceSchemaEntry(
            AresDataType.STRUCT,
            "Successful command output",
            struct_schema={
                "number": DeviceSchemaEntry(AresDataType.NUMBER, "Returned Number")
            },
        )
    }
    maybe_fail_command = DeviceCommandDescriptor(
        "Maybe Fail",
        "Has a 50% chance of failing; otherwise returns 20",
        {},
        maybe_fail_output_schema,
    )
    service.add_new_command(maybe_fail_command, test_device.maybe_fail)

    print("Test Device Service Running...")
    service.start()
