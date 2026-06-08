from PyAres import *

class RotaryMixer:
    def __init__(self, speed):
        self.speed = speed


mixer = RotaryMixer(1200)

# 1. Define your hardware logic
def set_speed(rpm: float):
    print(f"Setting motor speed to {rpm}")
    mixer.speed = rpm
    return DeviceCommandResponse(None, status_code=StatusCode.COMMAND_SUCCESS) # Return empty dict if no data needs to be sent back

def get_speed():
    print("Hey I got speed")
    return DeviceCommandResponse(mixer.speed, status_code=StatusCode.COMMAND_SUCCESS)

def get_status():
    # Return a dictionary matching your state schema
    return { "rpm": mixer.speed } 

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
input_schema = { "rpm": DeviceSchemaEntry(AresDataType.NUMBER, "Speed in RPM", "RPM") }
cmd_descriptor = DeviceCommandDescriptor("Set Speed", "Sets mixer speed", input_schema, {})

output_schema = { "rpm": DeviceSchemaEntry(AresDataType.NUMBER, "Speed in RPM", "RPM") }
get_speed_descriptor = DeviceCommandDescriptor("Get Speed", "Gets mixer speed", {}, output_schema)

# 4. Register the command
service.add_new_command(cmd_descriptor, set_speed)
service.add_new_command(get_speed_descriptor, get_speed)

# 5. Start
service.start()