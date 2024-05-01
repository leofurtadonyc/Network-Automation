# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import os
import paramiko
import yaml
import json
import bcrypt
import datetime
import argparse
import time
import difflib
import getpass
import socket

def get_current_user():
    """Retrieve the current user's username for audit logging."""
    return getpass.getuser()

def get_ip_address():
    """Retrieve the IP address of the current machine for audit logging."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # It doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = 'N/A'
    finally:
        s.close()
    return IP

def load_devices(file_path='devices/network_devices.yaml'):
    """Load network devices from a YAML file."""
    try:
        with open(file_path, 'r') as file:
            devices_dict = yaml.safe_load(file)
            return devices_dict['devices']
    except FileNotFoundError:
        print("Devices file not found.")
        return yaml.safe_load(file).get('devices', {})

def verify_user(username, password, credentials_file='devices/usercredentials.sec'):
    """Verify user credentials against a stored file."""
    try:
        with open(credentials_file, 'r') as file:
            for line in file:
                stored_username, hashed_password = line.strip().split(':')
                if stored_username == username and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return True
    except FileNotFoundError:
        print("Credentials file not found.")
    return False

def write_audit_log(customer_name, audit_entries):
    """Write detailed audit log including configuration differences."""
    audit_dir = 'audit_logs'
    if not os.path.exists(audit_dir):
        os.makedirs(audit_dir)
    
    audit_file_name = f"{customer_name}_config_deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_audit.txt"
    audit_file_path = os.path.join(audit_dir, audit_file_name)

    with open(audit_file_path, 'w') as file:
        """Write audit log entries to file."""
        file.write(f"Operator: {audit_entries[0]['operator']} from IP {audit_entries[0]['operator_ip']}\n")
        file.write("--------------------------------------------------\n")
        for entry in audit_entries:
            file.write(f"Deployment start: {entry['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Deployment end: {entry['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Deployment duration: {(entry['end_time'] - entry['start_time']).seconds} seconds\n")
            file.write(f"Device: {entry['device_name']} ({entry['device_type']})\n")
            file.write(f"Generated config file: {entry['generated_config_path']}\n")
            file.write(f"Deployed config file: {entry['deployed_config_path']}\n")
            file.write(f"Deployment result: {entry['result']}\n")
            file.write(f"Activation status: {entry['activation_status']}\n")
            file.write("Configuration differences:\n")
            file.write(entry['diff_results'] + "\n")
            file.write("--------------------------------------------------\n")
    
    return audit_file_path

def find_latest_config(customer_name, device_type, deployed_dir='deployed_configs'):
    """Find the most recent configuration file for a customer per device type. Create the directory if it does not exist."""
    if not os.path.exists(deployed_dir):
        os.makedirs(deployed_dir, exist_ok=True)
    
    latest_file = None
    latest_time = None

    for file in os.listdir(deployed_dir):
        if file.startswith(f"{customer_name}_{device_type}") and file.endswith('.txt'):
            file_path = os.path.join(deployed_dir, file)
            file_time = os.path.getmtime(file_path)
            if not latest_time or file_time > latest_time:
                latest_time = file_time
                latest_file = file_path

    return latest_file

def compare_configurations(new_config, old_config_path):
    """Generate a diff between the new configuration and the most recent configuration."""
    if not old_config_path or not os.path.exists(old_config_path):
        return "No previous configuration to compare."
    with open(old_config_path, 'r') as file:
        old_config = file.readlines()
    new_config = new_config.splitlines()
    diff = difflib.unified_diff(old_config, new_config, fromfile='old_config', tofile='new_config', lineterm='')
    return '\n'.join(diff) if diff else "No changes detected."

def save_deployed_config(customer_name, device_name, configuration):
    """Saves the deployed configuration to a file."""
    deployed_dir = 'deployed_configs'
    if not os.path.exists(deployed_dir):
        os.makedirs(deployed_dir)
    filename = f"{customer_name}_{device_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.join(deployed_dir, filename)
    with open(file_path, 'w') as file:
        file.write(configuration)
    return file_path

def check_for_error_logs(customer_name, directory='generated_configs'):
    """Check for existing error logs for the customer and abort deployment if found."""
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    if os.path.exists(error_path):
        with open(error_path, 'r') as file:
            error_data = json.load(file)
        return error_data
    return None

def cleanup_generated_configs(customer_name, directory='generated_configs'):
    """Remove generated configuration files for a specific customer post-deployment."""
    for filename in os.listdir(directory):
        if filename.startswith(customer_name) and filename.endswith(".txt"):
            os.remove(os.path.join(directory, filename))
            print(f"Removed {filename} from {directory} after successful deployment.")

def deploy_config(username, password, customer_name, access_device, pe_device):
    """Deploy configurations to access and PE devices for a customer, ensuring both device configurations are correct."""
    error_data = check_for_error_logs(customer_name)
    if error_data:
        return f"Deployment aborted due to config generation errors: {error_data['error_message']} (Error Code: {error_data['error_code']})"

    devices = load_devices()
    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    operator = get_current_user()
    operator_ip = get_ip_address()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    audit_entries = []

    access_config_path = f"generated_configs/{customer_name}_{access_device}_access_config.txt"
    pe_config_path = f"generated_configs/{customer_name}_{pe_device}_pe_config.txt"

    # Check that configuration files for both devices exist
    if not os.path.exists(access_config_path) or not os.path.exists(pe_config_path):
        missing_files = []
        if not os.path.exists(access_config_path):
            missing_files.append(f"access device {access_device}")
        if not os.path.exists(pe_config_path):
            missing_files.append(f"PE device {pe_device}")
        return f"Configuration file(s) for {', '.join(missing_files)} not found. Wrong device? Check the device names and generated files."

    try:
        configurations = {
            access_device: (access_config_path, 'access'),
            pe_device: (pe_config_path, 'pe')
        }
        all_successful = True
        for device_name, (config_path, config_suffix) in configurations.items():
            device = devices.get(device_name)
            if not device:
                return f"Device {device_name} not found in device configuration."

            device_type = device['device_type']
            ip_address = device['ip_address']
            configuration = open(config_path, 'r').read()
            start_time = datetime.datetime.now()
            deployed_config_path = save_deployed_config(customer_name, device_name, configuration)
            diff_results = compare_configurations(configuration, find_latest_config(customer_name, device_name))
            activation_status = "Re-activation" if diff_results != "No previous configuration to compare." else "First-time activation"

            ssh_client.connect(ip_address, username=username, password=password, timeout=10)
            channel = ssh_client.invoke_shell()
            deployment_commands = {
                'cisco_xe': ['config terminal', configuration, 'end', 'write memory', 'exit'],
                'cisco_xr': ['config terminal', configuration, 'commit', 'end', 'exit'],
                'juniper_junos': ['edit', configuration, 'commit and-quit'],
                'huawei_vrp': ['system-view', configuration, 'return', 'save', 'Y', 'quit']
            }.get(device_type, [])

            for command in deployment_commands:
                channel.send(command + '\n')
                time.sleep(1)

            ssh_client.close()
            end_time = datetime.datetime.now()
            result = "Success"
            audit_entries.append({
                'start_time': start_time,
                'end_time': end_time,
                'device_name': device_name,
                'device_type': device_type,
                'generated_config_path': config_path,
                'deployed_config_path': deployed_config_path,
                'result': result,
                'diff_results': diff_results,
                'activation_status': activation_status,
                'operator': operator,
                'operator_ip': operator_ip
            })
    except Exception as e:
        all_successful = False
        print(f"Deployment failed with an exception: {str(e)}")

    if all_successful:
        audit_path = write_audit_log(customer_name, audit_entries)
        cleanup_generated_configs(customer_name)
        return f"Deployment completed successfully. Detailed audit log saved at: {audit_path}"
    else:
        return "One or more deployments failed. Check the logs for more details."

def main():
    parser = argparse.ArgumentParser(description="Network Configuration Deployment")
    parser.add_argument("--customer-name", required=True, help="Customer name to identify config files")
    parser.add_argument("--username", required=True, help="Username for SSH and credential verification")
    parser.add_argument("--password", required=True, help="Password for SSH and credential verification", type=str)
    parser.add_argument("--access-device", required=True, help="Hostname of the access device")
    parser.add_argument("--pe-device", required=True, help="Hostname of the PE device")

    args = parser.parse_args()

    result = deploy_config(args.username, args.password, args.customer_name, args.access_device, args.pe_device)
    print(result)

if __name__ == "__main__":
    main()
