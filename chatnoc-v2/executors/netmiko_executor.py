# executors/netmiko_executor.py
#!/usr/bin/env python
import os
import json
import logging
from netmiko import ConnectHandler
from auth.auth_manager import get_credentials as load_credentials
from paramiko import ProxyCommand, SSHException
from config import Config  # Assumes your Config class loads config/config.yaml

# Mapping from our device_type names to Netmiko device types.
DEVICE_TYPE_MAPPING = {
    "cisco": "cisco_ios",
    "cisco_xe": "cisco_ios",
    "cisco_xr": "cisco_xr",
    "juniper_junos": "juniper_junos",
    "huawei_vrp": "huawei",
    "nokia_sr": "nokia_sros"
}

# Global variable to cache target device credentials.
CREDENTIALS = None

# Enable detailed logging.
logging.basicConfig(level=logging.DEBUG)

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
    
    # Build the connection parameters.
    device_params = {
        "device_type": netmiko_device_type,
        "host": device.mgmt_address,
        "username": username,
        "password": password,
        "port": ssh_port,
        "conn_timeout": 10  # Lower timeout so failures happen faster.
    }
    
    # Load global configuration.
    config = Config()  # Loads from config/config.yaml
    jump_cfg = config.config_data.get("jumpserver", {})
    if jump_cfg.get("enabled", False):
        # Load jumpserver credentials from the specified file in the auth folder.
        jump_creds_file = jump_cfg.get("credentials_file")
        if jump_creds_file:
            jump_creds_path = os.path.join(os.path.dirname(__file__), "..", "auth", jump_creds_file)
            if os.path.isfile(jump_creds_path):
                try:
                    with open(jump_creds_path, "r") as f:
                        jump_creds = json.load(f)
                    jump_username = jump_creds.get("username")
                except Exception as e:
                    return f"Error loading jumpserver credentials: {e}"
            else:
                return f"Jumpserver credentials file '{jump_creds_file}' not found."
        else:
            jump_username = jump_cfg.get("username")
        if not jump_username:
            return "Jumpserver username not provided in configuration or credentials file."
        jump_host = jump_cfg.get("host")
        jump_port = jump_cfg.get("port", 22)
        # Use extra options if provided (e.g., for specific vendors)
        extra_options_mapping = jump_cfg.get("extra_options", {})
        vendor_key = device.device_type.lower()
        if vendor_key in ["cisco", "cisco_xe"]:
            vendor_key = "cisco"
        elif vendor_key == "juniper_junos":
            vendor_key = "juniper"
        elif vendor_key == "nokia_sr":
            vendor_key = "nokia"
        jump_extra_options = extra_options_mapping.get(vendor_key, "").strip()
        # Always append options to disable host key checking.
        additional_opts = "-o StrictHostKeyChecking=no -o BatchMode=yes"
        if jump_extra_options:
            proxy_command = f"ssh -q {jump_extra_options} -W %h:%p {jump_username}@{jump_host} -p {jump_port} {additional_opts}"
        else:
            proxy_command = f"ssh -q -W %h:%p {jump_username}@{jump_host} -p {jump_port} {additional_opts}"
        logging.debug(f"Using ProxyCommand: {proxy_command}")
        try:
            sock = ProxyCommand(proxy_command)
            device_params["sock"] = sock
            # Optionally adjust jumpserver-related timeouts here:
            device_params["conn_timeout"] = jump_cfg.get("conn_timeout", 15)
        except Exception as e:
            return f"Error creating proxy connection through jumpserver: {e}"
    
    # For Cisco IOS XR, add extra timeouts and delay factor.
    if device.device_type.lower() == "cisco_xr":
        device_params["banner_timeout"] = 300
        device_params["auth_timeout"] = 300
        device_params["timeout"] = 300
        device_params["global_delay_factor"] = 2

    try:
        logging.debug(f"Connecting to {device.name} with parameters: {device_params}")
        connection = ConnectHandler(**device_params)
        output = connection.send_command(command)
        connection.disconnect()
        logging.debug(f"Command output from {device.name}: {output}")
        return output
    except SSHException as sshe:
        logging.error(f"SSHException for device {device.name}: {sshe}")
        return f"Failed to execute command on {device.name}: {sshe}"
    except Exception as e:
        logging.error(f"Exception for device {device.name}: {e}")
        return f"Failed to execute command on {device.name}: {e}"

def demo_execute_command(device, command):
    normalized = command.strip().lower().replace(" ", "_").replace("|", "").replace(":", "")
    demo_file = os.path.join("demo", device.name.lower(), f"{normalized}.txt")
    logging.debug(f"Looking for demo file: {demo_file}")
    if os.path.isfile(demo_file):
        with open(demo_file, "r") as f:
            content = f.read()
        if not content.strip():
            return "[Demo file is empty]"
        return content
    else:
        return f"[Demo output not available for command: {command}]"

if __name__ == "__main__":
    # For testing, define some dummy devices.
    class DummyDevice:
        def __init__(self, name, device_type, mgmt_address, ssh_port=22):
            self.name = name
            self.device_type = device_type
            self.mgmt_address = mgmt_address
            self.ssh_port = ssh_port

    dummy_device1 = DummyDevice("p1", "cisco_xe", "192.168.255.1", ssh_port=22)
    dummy_device2 = DummyDevice("p2", "cisco_xe", "192.168.255.2", ssh_port=2200)
    dummy_device3 = DummyDevice("pe2-iosxr", "cisco_xr", "192.168.255.12", ssh_port=22)
    
    print("Output from p1:")
    print(execute_command(dummy_device1, "show ip interface brief"))
    print("\nOutput from p2:")
    print(execute_command(dummy_device2, "show ip interface brief"))
    print("\nOutput from pe2-iosxr:")
    print(execute_command(dummy_device3, "show ip interface brief"))
