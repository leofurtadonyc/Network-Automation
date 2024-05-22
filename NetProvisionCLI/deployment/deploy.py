import paramiko
import time
import os
import datetime
import difflib
from collections import defaultdict
from typing import Optional, Dict, Any, List
from utils.file_utils import write_to_file, log_error, delete_error_log
from utils.validation import valid_ip_irb, valid_ip_nexthop, valid_ip_lan, interface_allowed
from audit.audit_log import create_audit_log_entry, write_audit_log
from audit.cleanup import cleanup_generated_configs, check_for_error_logs
from security.auth import verify_user
from utils.network_utils import get_current_user, get_ip_address
from config.load_config import load_yaml
from utils.template_utils import render_template
from config.save_config import save_deployed_config

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

def deploy_configurations(username: str, password: str, customer_name: str, device_names: dict):
    """Deploy configurations to specified devices for a customer."""
    error_log = check_for_error_logs(customer_name)
    if error_log:
        return f"Deployment aborted due to config generation errors: {error_log['error_message']} (Error Code: {error_log['error_code']})"

    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    devices = load_yaml('devices/network_devices.yaml')
    operator = get_current_user()
    operator_ip = get_ip_address()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    audit_entries = []

    start_time = time.time()

    print(f"Deployment started by {operator} from IP {operator_ip} at {datetime.datetime.now()}")

    config_suffixes = ['config_remove', 'config', 'config_deactivate']
    all_configs = defaultdict(list)

    # Collect and verify all necessary config files before deployment
    for device_name, config_action in device_names.items():
        for suffix in config_suffixes:
            config_type = f"{config_action}_{suffix}.txt"
            config_file_name = f"{customer_name}_{device_name}_{config_type}"
            config_file_path = f"generated_configs/{config_file_name}"

            if os.path.exists(config_file_path):
                if device_name not in devices:
                    print(f"Device {device_name} not found in device configuration.")
                    return f"Deployment aborted. Device not found: {device_name}"

                all_configs[device_name].append((config_file_path, devices[device_name]['ip_address'], devices[device_name]['device_type'], suffix))
                print(f"Added configuration for {device_name}: {config_file_path}")

    if not all_configs:
        return "Deployment aborted. No configuration files found."

    # Proceed with deployment if all files are verified
    try:
        for device_name, configs in all_configs.items():
            previous_config_path = find_latest_config(customer_name, device_name)  # Find the latest config before any changes
            for config_file_path, ip_address, device_type, suffix in configs:
                print(f"Deploying configuration for {device_name} from {config_file_path}")
                ssh_client.connect(ip_address, username=username, password=password, timeout=10)
                channel = ssh_client.invoke_shell()

                with open(config_file_path, 'r') as file:
                    configuration = file.read()

                commands = prepare_device_commands(device_type, configuration)
                for command in commands:
                    channel.send(command + '\n')
                    time.sleep(2)  # Ensure the command gets executed

                ssh_client.close()

                is_deactivate = suffix == 'config_deactivate'
                is_new_config = suffix == 'config'

                if is_new_config or is_deactivate:  # Only log active and deactivate configurations
                    diff_results = ""
                    if is_new_config:  # Only compare diffs for new configurations
                        diff_results = compare_configurations(configuration, previous_config_path)

                    deployed_config_path = save_deployed_config(customer_name, device_name, configuration)
                    audit_entries.append(create_audit_log_entry(
                        operator=operator,
                        operator_ip=operator_ip,
                        device_name=device_name,
                        device_type=device_type,
                        configuration_type=config_type.split('_')[0],
                        configuration_path=config_file_path,
                        deployed_config_path=deployed_config_path,
                        diff_results=diff_results,
                        is_deactivate=is_deactivate,
                        timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        elapsed_time=f"Deployment completed in {time.time() - start_time:.2f} seconds"
                    ))

        cleanup_generated_configs(customer_name, audit_entries, operator, operator_ip)
        filtered_entries = [entry for entry in audit_entries if 'configuration_path' in entry and 'deployed_config_path' in entry]
        if not filtered_entries:
            print("No valid audit entries found.")
            return "Deployment aborted. No valid audit entries found."
        audit_path = write_audit_log(customer_name, filtered_entries)
        return f"Deployment completed successfully. Detailed audit log saved at: {audit_path}"
    except Exception as e:
        ssh_client.close()
        return f"Deployment failed with an exception: {str(e)}"

def prepare_device_commands(device_type: str, configuration: str) -> list:
    """Prepare device-specific deployment commands."""
    commands = {
        'cisco_xe': ['config terminal', configuration, 'end', 'write memory', 'exit'],
        'cisco_xr': ['config terminal', configuration, 'commit', 'end', 'exit'],
        'juniper_junos': ['edit', configuration, 'commit', 'commit and-quit'],
        'huawei_vrp': ['system-view', configuration, 'return', 'save', 'Y', 'quit']
    }.get(device_type, [])
    return [cmd for cmd in commands if cmd.strip()]
