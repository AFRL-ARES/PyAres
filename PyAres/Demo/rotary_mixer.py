from PyAres import AresDeviceService, AresDataType, DeviceSchemaEntry, DeviceCommandDescriptor

# 1. Define your hardware logic
def set_speed(rpm: float):
    print(f"Setting motor speed to {rpm}")
    # Hardware communication goes here...
    return {} # Return empty dict if no data needs to be sent back

def get_status():
    # Return a dictionary matching your state schema
    return { "rpm": 1200 } 

def safe_mode():
    print("Stopping motor immediately!")

# 2. Initialize Service
service = AresDeviceService(
    safe_mode, 
    get_status, 
    "Rotary Mixer", 
    "High-speed mixer control", 
    "1.0.0",
    port=7101
)

# 3. Define the 'Set Speed' Command
# Input: One number (Speed)
input_schema = { 
    "rpm": DeviceSchemaEntry(AresDataType.NUMBER, "Speed in RPM", "RPM") 
}
cmd_descriptor = DeviceCommandDescriptor("Set Speed", "Sets mixer speed", input_schema, {})

# 4. Register the command
service.add_new_command(cmd_descriptor, set_speed)

# 5. Start
service.start()