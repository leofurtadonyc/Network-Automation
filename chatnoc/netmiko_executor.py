# netmiko_executor.py
import os
import yaml
from netmiko import ConnectHandler
from auth_manager import get_credentials

# Mapping from our device_type names to Netmiko device types
DEVICE_TYPE_MAPPING = {
    "cisco": "cisco_ios",
    "cisco_xe": "cisco_ios",
    "cisco_xr": "cisco_xr",
    "juniper_junos": "juniper_junos",
    "huawei_vrp": "huawei",
    "nokia_sr": "nokia_sros"
}

def get_config():
    """
    Load the configuration from config.yaml.
    """
    config_path = "config.yaml"
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}
    else:
        return {}

def execute_command(device, command):
    netmiko_device_type = DEVICE_TYPE_MAPPING.get(device.device_type)
    if not netmiko_device_type:
        return f"Unsupported device type: {device.device_type} for device {device.name}"
    
    # Retrieve credentials.
    try:
        username, password = get_credentials()
    except Exception as e:
        return f"Authentication error: {e}"

    # Load configuration to get SSH port.
    config = get_config()
    ssh_port = config.get("ssh_port", 22)
    
    device_params = {
        "device_type": netmiko_device_type,
        "host": device.mgmt_address,
        "username": username,
        "password": password,
        "port": ssh_port,
        # Remove 'look_for_keys' since it's causing the error.
    }
    
    if device.device_type == "cisco_xr":
        device_params["banner_timeout"] = 200
        device_params["auth_timeout"] = 200
    
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
