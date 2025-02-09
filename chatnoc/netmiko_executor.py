# netmiko_executor.py
from netmiko import ConnectHandler

# Mapping from our device_type names to Netmiko device types
DEVICE_TYPE_MAPPING = {
    "cisco": "cisco_ios",
    "cisco_xe": "cisco_ios",
    "cisco_xr": "cisco_xr",
    "juniper_junos": "juniper_junos",
    "huawei_vrp": "huawei",
    "nokia_sr": "nokia_sros"
}

def execute_command(device, command, username="admin", password="admin"):
    """
    Connect to the device using Netmiko and execute the given command.
    """
    netmiko_device_type = DEVICE_TYPE_MAPPING.get(device.device_type)
    if not netmiko_device_type:
        return f"Unsupported device type: {device.device_type} for device {device.name}"
    
    device_params = {
        "device_type": netmiko_device_type,
        "host": device.mgmt_address,
        "username": username,
        "password": password,
    }
    
    try:
        connection = ConnectHandler(**device_params)
        output = connection.send_command(command)
        connection.disconnect()
        return output
    except Exception as e:
        return f"Failed to execute command on {device.name}: {e}"

if __name__ == "__main__":
    # For a quick test, you can define a dummy device here
    class DummyDevice:
        def __init__(self, name, device_type, mgmt_address):
            self.name = name
            self.device_type = device_type
            self.mgmt_address = mgmt_address

    dummy_device = DummyDevice("test_device", "cisco", "192.168.1.1")
    print(execute_command(dummy_device, "show ip interface brief"))
