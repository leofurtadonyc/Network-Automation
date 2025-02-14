# netmiko_executor.py
from netmiko import ConnectHandler
from auth_manager import get_credentials as load_credentials

# Mapping from our device_type names to Netmiko device types
DEVICE_TYPE_MAPPING = {
    "cisco": "cisco_ios",
    "cisco_xe": "cisco_ios",
    "cisco_xr": "cisco_xr",
    "juniper_junos": "juniper_junos",
    "huawei_vrp": "huawei",
    "nokia_sr": "nokia_sros"
}

# Global variable to cache credentials.
CREDENTIALS = None

def get_cached_credentials():
    """
    Retrieve credentials from auth_manager and cache them for subsequent calls.
    """
    global CREDENTIALS
    if CREDENTIALS is None:
        try:
            CREDENTIALS = load_credentials()
        except Exception as e:
            raise Exception(f"Authentication error: {e}")
    return CREDENTIALS

def execute_command(device, command):
    netmiko_device_type = DEVICE_TYPE_MAPPING.get(device.device_type)
    if not netmiko_device_type:
        return f"Unsupported device type: {device.device_type} for device {device.name}"
    
    # Retrieve cached credentials.
    try:
        username, password = get_cached_credentials()
    except Exception as e:
        return str(e)

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
    # For testing, define a dummy device.
    class DummyDevice:
        def __init__(self, name, device_type, mgmt_address):
            self.name = name
            self.device_type = device_type
            self.mgmt_address = mgmt_address

    dummy_device = DummyDevice("test_device", "cisco", "192.168.1.1")
    print(execute_command(dummy_device, "show ip interface brief"))
