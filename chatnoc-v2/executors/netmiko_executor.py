#!/usr/bin/env python
import os
import yaml
from netmiko import ConnectHandler
from auth.auth_manager import get_credentials as load_credentials

# Mapping from our device_type names to Netmiko device types.
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
    global CREDENTIALS
    if CREDENTIALS is None:
        try:
            CREDENTIALS = load_credentials()  # Expected to return (username, password)
        except Exception as e:
            raise Exception(f"Error loading credentials: {e}")
    return CREDENTIALS

def execute_command(device, command):
    netmiko_device_type = DEVICE_TYPE_MAPPING.get(device.device_type)
    if not netmiko_device_type:
        return f"Unsupported device type: {device.device_type} for device {device.name}"
    
    try:
        username, password = get_cached_credentials()
    except Exception as e:
        return f"Authentication error: {e}"
    
    # Get per-device SSH port; default to 22.
    ssh_port = getattr(device, "ssh_port", 22)
    
    device_params = {
        "device_type": netmiko_device_type,
        "host": device.mgmt_address,
        "username": username,
        "password": password,
        "port": ssh_port
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

def demo_execute_command(device, command):
    """
    In demo mode, load the command output from a file in the "demo" folder.
    Filename: demo/<device.name.lower()>/<normalized_command>.txt
    """
    normalized = command.strip().lower().replace(" ", "_").replace("|", "").replace(":", "")
    demo_file = os.path.join("demo", device.name.lower(), f"{normalized}.txt")
    print(f"DEBUG: Looking for demo file: {demo_file}")
    if os.path.isfile(demo_file):
        with open(demo_file, "r") as f:
            content = f.read()
        if not content.strip():
            return "[Demo file is empty]"
        return content
    else:
        return f"[Demo output not available for command: {command}]"

if __name__ == "__main__":
    # For testing, define a dummy device.
    class DummyDevice:
        def __init__(self, name, device_type, mgmt_address, ssh_port=22):
            self.name = name
            self.device_type = device_type
            self.mgmt_address = mgmt_address
            self.ssh_port = ssh_port

    dummy_device1 = DummyDevice("p1", "cisco_xe", "192.168.255.1", ssh_port=22)
    dummy_device2 = DummyDevice("p2", "cisco_xe", "192.168.255.2", ssh_port=2200)
    print("Output from p1:")
    print(execute_command(dummy_device1, "show ip interface brief"))
    print("\nOutput from p2:")
    print(execute_command(dummy_device2, "show ip interface brief"))
