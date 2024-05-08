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
from collections import defaultdict
from typing import Optional, Dict, Any, List

def get_current_user() -> str:
    """Retrieve the current user's username for audit logging."""
    return getpass.getuser()

def get_ip_address() -> str:
    """Retrieve the IP address of the current machine for audit logging."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        return s.getsockname()[0]
    except Exception:
        return 'N/A'
    finally:
        s.close()

def load_devices(file_path: str = 'devices/network_devices.yaml') -> Dict[str, Any]:
    """Load network devices from a YAML file."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file).get('devices', {})
    except FileNotFoundError:
        print("Devices file not found.")
        return {}

def verify_user(username: str, password: str, credentials_file: str = 'devices/usercredentials.sec') -> bool:
    """Verify user credentials against a stored file."""
    try:
        with open(credentials_file, 'r') as file:
            for line in file:
                stored_username, hashed_password = line.strip().split(':')
                if stored_username == username and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return True
        return False
    except FileNotFoundError:
        print("Credentials file not found.")
        return False

def create_audit_entry(operator, operator_ip, **kwargs):
    entry = {
        'operator': operator,
        'operator_ip': operator_ip
    }
    entry.update(kwargs)
    return entry

def write_audit_log(customer_name: str, audit_entries: List[Dict[str, Any]]) -> str:
    """Write detailed audit log including configuration differences."""
    audit_dir = 'audit_logs'
    os.makedirs(audit_dir, exist_ok=True)
    audit_file_name = f"{customer_name}_config_deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_audit.txt"
    audit_file_path = os.path.join(audit_dir, audit_file_name)

    with open(audit_file_path, 'w') as file:
        file.write(f"Operator: {audit_entries[0].get('operator', 'Unknown Operator')} from IP {audit_entries[0].get('operator_ip', 'Unknown IP')}\n")
        file.write(f"Completed at: {audit_entries[0].get('timestamp')}\n")
        file.write("--------------------------------------------------\n")
        for entry in audit_entries:
            file.write(f"Duration of execution: {entry.get('elapsed_time')}\n")
            file.write(f"Device: {entry.get('device_name', 'Unknown Device')} ({entry.get('device_type', 'unknown')})\n")
            file.write(f"Generated config file: {entry.get('configuration_path', 'No Path Available')}\n")
            file.write(f"Deployed config file: {entry.get('deployed_config_path', 'No Path Available')}\n")
            file.write(f"Deployment result: {'Success' if 'diff_results' in entry else 'Failure'}\n")

            diff = entry.get('diff_results', 'No changes detected.')
            if "No previous configuration to compare." in diff:
                activation_status = "First-time customer activation (no previous configuration found)."
            elif "No changes detected." in diff:
                activation_status = "Re-activation"
            else:
                activation_status = "Re-activation with service changes"

            file.write(f"Activation status: {activation_status}\n")
            file.write("Configuration differences:\n")
            file.write(f"{diff}\n")
            file.write("--------------------------------------------------\n")

    return audit_file_path

def find_latest_config(customer_name: str, device_name: str, deployed_dir: str = 'deployed_configs') -> Optional[str]:
    """Find the most recent configuration file for a customer per device type."""
    latest_file = None
    latest_time = None

    for file_name in os.listdir(deployed_dir):
        if file_name.startswith(f"{customer_name}_{device_name}") and file_name.endswith('.txt'):
            file_time = parse_time_from_filename(file_name)
            if file_time and (not latest_time or file_time > latest_time):
                latest_time = file_time
                latest_file = os.path.join(deployed_dir, file_name)
    return latest_file

def parse_time_from_filename(filename: str) -> Optional[datetime.datetime]:
    """Extract and parse the datetime from the filename."""
    try:
        parts = filename.split('_')
        date_part = parts[-2]
        time_part = parts[-1].split('.')[0]
        return datetime.datetime.strptime(f"{date_part}_{time_part}", '%Y%m%d_%H%M%S')
    except ValueError:
        return None

def compare_configurations(new_config: str, old_config_path: str) -> str:
    """Generate a diff between the new configuration and the most recent configuration."""
    if not old_config_path or not os.path.exists(old_config_path):
        return "No previous configuration to compare."

    with open(old_config_path, 'r') as file:
        old_config = file.read().strip().replace('\r\n', '\n').split('\n')

    new_config_lines = new_config.strip().replace('\r\n', '\n').split('\n')
    diff = list(difflib.unified_diff(old_config, new_config_lines, fromfile='old_config', tofile='new_config', lineterm=''))

    return '\n'.join(diff) if diff else "No changes detected."

def save_deployed_config(customer_name: str, device_name: str, configuration: str) -> str:
    """Saves the deployed configuration to a file."""
    deployed_dir = 'deployed_configs'
    os.makedirs(deployed_dir, exist_ok=True)
    filename = f"{customer_name}_{device_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.join(deployed_dir, filename)
    with open(file_path, 'w') as file:
        file.write(configuration)
    return file_path

def check_for_error_logs(customer_name: str, directory: str = 'generated_configs') -> Optional[Dict[str, Any]]:
    """Check for existing error logs for the customer and abort deployment if found."""
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    if os.path.exists(error_path):
        with open(error_path, 'r') as file:
            return json.load(file)
    return None

def cleanup_generated_configs(customer_name: str, audit_entries: List[Dict[str, Any]], operator: str, operator_ip: str, directory: str = 'generated_configs') -> None:
    """Remove generated configuration files for a specific customer post-deployment and log this action."""
    for filename in os.listdir(directory):
        if filename.startswith(customer_name) and (filename.endswith(".txt") or filename.endswith(".json")):
            os.remove(os.path.join(directory, filename))
            audit_entries.append(create_audit_entry(operator, operator_ip, action='Removed', file=filename))

def deploy_configurations(username: str, password: str, customer_name: str, device_names: Dict[str, str], deactivate: bool):
    """Deploy configurations to specified devices for a customer, based on activation or deactivation request."""
    error_log = check_for_error_logs(customer_name)
    if error_log:
        return f"Deployment aborted due to config generation errors: {error_log['error_message']} (Error Code: {error_log['error_code']})"

    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    devices = load_devices()
    operator = get_current_user()
    operator_ip = get_ip_address()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    audit_entries = []

    start_time = time.time()

    print(f"Deployment started by {operator} from IP {operator_ip} at {datetime.datetime.now()}")

    config_suffixes = ['config_remove', 'config']  # Process removals first, then apply new configurations
    config_file_paths = {}
    all_configs = defaultdict(list)

    # Collect and verify all necessary config files before deployment
    for device_name, config_action in device_names.items():
        for suffix in config_suffixes:
            config_type = f"{config_action}_{suffix}.txt"
            config_file_name = f"{customer_name}_{device_name}_{config_type}"
            config_file_path = f"generated_configs/{config_file_name}"

            if not os.path.exists(config_file_path):
                print(f"Configuration file for {device_name} ({config_type}) not found. Please verify and try again.")
                return f"Deployment aborted. Missing configuration file: {config_file_name}"

            if device_name not in devices:
                print(f"Device {device_name} not found in device configuration.")
                return f"Deployment aborted. Device not found: {device_name}"

            all_configs[device_name].append((config_file_path, devices[device_name]['ip_address'], devices[device_name]['device_type'], suffix == 'config'))

    # Proceed with deployment if all files are verified
    try:
        for device_name, configs in all_configs.items():
            previous_config_path = find_latest_config(customer_name, device_name)  # Find the latest config before any changes
            for config_file_path, ip_address, device_type, is_new_config in configs:
                ssh_client.connect(ip_address, username=username, password=password, timeout=10)
                channel = ssh_client.invoke_shell()

                configuration = open(config_file_path, 'r').read()
                commands = prepare_device_commands(device_type, configuration)
                for command in commands:
                    channel.send(command + '\n')
                    time.sleep(1)

                ssh_client.close()

                if is_new_config:  # Only compare diffs for new configurations
                    diff_results = compare_configurations(configuration, previous_config_path)
                    deployed_config_path = save_deployed_config(customer_name, device_name, configuration)
                    audit_entries.append({
                        'device_name': device_name,
                        'device_type': device_type,
                        'configuration_type': config_type.split('_')[0],
                        'configuration_path': config_file_path,
                        'deployed_config_path': deployed_config_path,
                        'diff_results': diff_results,
                        'operator': operator,
                        'operator_ip': operator_ip,
                        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'elapsed_time': f"Deployment completed in {time.time() - start_time:.2f} seconds"
                    })

        cleanup_generated_configs(customer_name, audit_entries, operator, operator_ip)
        filtered_entries = [entry for entry in audit_entries if 'configuration_path' in entry and 'deployed_config_path' in entry]
        audit_path = write_audit_log(customer_name, filtered_entries)
        return f"Deployment completed successfully. Detailed audit log saved at: {audit_path}"
    except Exception as e:
        ssh_client.close()
        return f"Deployment failed with an exception: {str(e)}"

def prepare_device_commands(device_type: str, configuration: str) -> List[str]:
    """Prepare device-specific deployment commands."""
    return {
        'cisco_xe': ['config terminal', configuration, 'end', 'write memory', 'exit'],
        'cisco_xr': ['config terminal', configuration, 'commit', 'end', 'exit'],
        'juniper_junos': ['edit', configuration, 'commit', 'commit and-quit'],
        'huawei_vrp': ['system-view', configuration, 'return', 'save', 'Y', 'quit']
    }.get(device_type, [])

def main():
    parser = argparse.ArgumentParser(description="Network Configuration Deployment")
    parser.add_argument("--customer-name", required=True, help="Customer name to identify config files")
    parser.add_argument("--username", required=True, help="Username for SSH and credential verification")
    parser.add_argument("--password", required=True, help="Password for SSH and credential verification", type=str)
    parser.add_argument("--access-device", required=True, help="Hostname of the access device")
    parser.add_argument("--pe-device", required=True, help="Hostname of the PE device")
    parser.add_argument("--deactivate", action='store_true', help="Deploy only the removal configurations")

    args = parser.parse_args()
    device_configurations = {
        args.access_device: 'access' if not args.deactivate else 'remove',
        args.pe_device: 'pe' if not args.deactivate else 'remove'
    }

    result = deploy_configurations(args.username, args.password, args.customer_name, device_configurations, args.deactivate)
    print(result)

if __name__ == "__main__":
    main()
