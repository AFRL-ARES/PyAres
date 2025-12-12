from PyAres import AresDeviceService, AresDataType, DeviceSchemaEntry, DeviceCommandDescriptor

# --- PART 1: The Simulated Hardware ---
class VirtualHotplate:
    def __init__(self):
        self.target_temp = 25.0 # Start at room temp
    
    def set_temperature(self, temp: float):
        """Simulates setting the heater."""
        print(f"[Hardware] Heating to {temp}°C...")
        self.target_temp = temp
        return {} # Return empty dict if no data needs to be sent back

    def get_temperature(self):
        """Simulates reading the sensor."""
        # In a real device, you'd read a serial port here.
        print("[Hardware] Retrieving the current temperature...")
        return { "current_temp": self.target_temp }

    def get_state(self):
        """Required: Tells ARES the current status for logging."""
        return { "current_temp": self.target_temp }

    def safe_mode(self):
        """Required: A safety fallback (e.g., turn off heat)."""
        print("[Hardware] SAFE MODE TRIGGERED: Heater off.")
        self.target_temp = 0.0

# --- PART 2: The Ares Service Wrapper ---
if __name__ == "__main__":
    # 1. Initialize the hardware
    my_hotplate = VirtualHotplate()

    # 2. Define the Service Info
    service = AresDeviceService(
        my_hotplate.safe_mode,
        my_hotplate.get_state,
        "My Virtual Hotplate",    # Device Name
        "A simulated lab hotplate", # Description
        "1.0.0"                   # Version
    )

    # 3. Define Command: Set Temperature
    # This schema tells ARES to draw a Number Input box in the UI
    input_schema = { 
        "temp": DeviceSchemaEntry(AresDataType.NUMBER, "Target Temperature", "Celsius") 
    }
    set_cmd = DeviceCommandDescriptor(
        "Set Temp", 
        "Sets the hotplate target temperature", 
        input_schema, 
        {} # No output expected
    )
    service.add_new_command(set_cmd, my_hotplate.set_temperature)

    # 4. Define Command: Get Temperature
    # This schema tells ARES to expect a number back
    output_schema = {
        "current_temp": DeviceSchemaEntry(AresDataType.NUMBER, "Current Temperature", "Celsius")
    }
    get_cmd = DeviceCommandDescriptor(
        "Get Temp", 
        "Reads the current temperature", 
        {}, # No input needed
        output_schema
    )
    service.add_new_command(get_cmd, my_hotplate.get_temperature)

    # 5. Start the Service
    # This will block and listen for ARES connections
    print("Virtual Hotplate Service Running...")
    service.start()