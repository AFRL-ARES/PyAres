import random

from PyAres import AresDeviceService, AresDataType, DeviceSchemaEntry, DeviceCommandDescriptor, DeviceCommandResponse, StatusCode


# --- PART 1: The Simulated Hardware ---
class VirtualRandomNumberDevice:
    def __init__(self):
        self.last_number = 0

    def generate_number(self):
        """Simulates reading a random value from hardware."""
        self.last_number = random.randint(1, 100)
        print(f"[Hardware] Generated random number: {self.last_number}")
        response = DeviceCommandResponse({"random_number": self.last_number}, status_code=StatusCode.COMMAND_SUCCESS)
        return response

    def get_state(self):
        """Required: Tells ARES the current status for logging."""
        return {"last_number": self.last_number}

    def safe_mode(self):
        """Required: A safety fallback."""
        print("[Hardware] SAFE MODE TRIGGERED: Random number device idle.")


# --- PART 2: The Ares Service Wrapper ---
if __name__ == "__main__":
    # 1. Initialize the hardware
    my_random_device = VirtualRandomNumberDevice()

    # 2. Define the Service Info
    service = AresDeviceService(
        my_random_device.safe_mode,
        my_random_device.get_state,
        "My Virtual Random Number Device",
        "A simulated device that generates random numbers",
        "1.0.0",
        port=7101
    )

    # 3. Define Command: Generate Number
    # This schema tells ARES to expect a struct back
    output_schema = {
        "output": DeviceSchemaEntry(
            AresDataType.STRUCT,
            "Generated random number output",
            struct_schema={
                "random_number": DeviceSchemaEntry(
                    AresDataType.NUMBER,
                    "Random Number",
                    "1-100",
                    min_number_value=1,
                    max_number_value=100,
                )
            },
        )
    }
    generate_cmd = DeviceCommandDescriptor(
        "Generate Number",
        "Generates a random number from 1 to 100",
        {},
        output_schema,
    )
    service.add_new_command(generate_cmd, my_random_device.generate_number)

    # 4. Start the Service
    # This will block and listen for ARES connections
    print("Virtual Random Number Device Service Running...")
    service.start()
