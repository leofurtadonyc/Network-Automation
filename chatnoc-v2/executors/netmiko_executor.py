# executors/netmiko_executor.py
import os
import json
from netmiko import ConnectHandler
from auth.auth_manager import get_credentials as load_credentials
from paramiko import ProxyCommand
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

# Global variable to cache device credentials.
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
    
    # Set up basic connection parameters.
    device_params = {
        "device_type": netmiko_device_type,
        "host": device.mgmt_address,
        "username": username,
        "password": password,
        "port": ssh_port,
        "conn_timeout": 10,  # Default connection timeout if no jumpserver is used.
    }
    
    # For Cisco IOS XR, add extra timeouts and delay factor.
    if device.device_type == "cisco_xr":
        device_params["banner_timeout"] = 300
        device_params["auth_timeout"] = 300
        device_params["timeout"] = 300
        device_params["global_delay_factor"] = 2

    # Check if jumpserver is enabled in the global config.
    config = Config()  # Loads configuration from config/config.yaml
    jump_cfg = config.config_data.get("jumpserver", {})
    if jump_cfg.get("enabled", False):
        # Load jumpserver credentials from the file specified in the config.
        jump_creds_file = jump_cfg.get("credentials_file")
        if not jump_creds_file:
            return "Jumpserver is enabled but no credentials_file is defined in config."
        # Assume the jumpserver credentials file is in the auth folder.
        jump_creds_path = os.path.join(os.path.dirname(__file__), "..", "auth", jump_creds_file)
        try:
            with open(jump_creds_path, "r") as f:
                jump_creds = json.load(f)
            jump_username = jump_creds.get("username")
            if not jump_username:
                return "Jumpserver credentials missing username."
        except Exception as e:
            return f"Error loading jumpserver credentials: {e}"
        jump_host = jump_cfg.get("host")
        jump_port = jump_cfg.get("port", 22)
        # Use jumpserver-specific timeouts (defaulting to 60 seconds).
        device_params["conn_timeout"] = jump_cfg.get("conn_timeout", 60)
        device_params["banner_timeout"] = jump_cfg.get("banner_timeout", 60)
        # Build the ProxyCommand string.
        proxy_command = f"ssh -q -W %h:%p {jump_username}@{jump_host} -p {jump_port}"
        try:
            sock = ProxyCommand(proxy_command)
            device_params["sock"] = sock
        except Exception as e:
            return f"Error creating proxy connection through jumpserver: {e}"
    
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
    # For testing, define dummy devices.
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
