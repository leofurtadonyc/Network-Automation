import paramiko
import time
import os
import datetime
import difflib
import json
from collections import defaultdict
from typing import Optional, Dict, Any, List
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from utils.file_utils import write_to_file, log_error, delete_error_log
from utils.validation import valid_ip_irb, valid_ip_nexthop, valid_ip_lan, interface_allowed
from audit.audit_log import create_audit_log_entry, write_audit_log
from audit.cleanup import check_for_error_logs
from security.auth import verify_user
from utils.network_utils import get_current_user, get_ip_address
from config.load_config import load_yaml, load_settings, load_devices, load_mongodb
from utils.template_utils import render_template
from config.save_config import save_deployed_config

settings = load_settings()
data_source = settings.get('data_source')
influxdb_url = settings['influxdb']['url']
influxdb_token = settings['influxdb']['token']
influxdb_org = settings['influxdb']['org']
influxdb_bucket = settings['influxdb']['bucket']

def find_latest_config(customer_name: str, device_name: str, influx_client=None) -> Optional[str]:
    """Find the most recent configuration file for a customer per device type."""
    if data_source == 'yaml':
        latest_file = None
        latest_time = None
        for file_name in os.listdir('deployed_configs'):
            if file_name.startswith(f"{customer_name}_{device_name}") and file_name.endswith('.txt'):
                file_time = parse_time_from_filename(file_name)
                if file_time and (not latest_time or file_time > latest_time):
                    latest_time = file_time
                    latest_file = os.path.join('deployed_configs', file_name)
        return latest_file
    elif data_source == 'mongodb':
        query = f'from(bucket:"{influxdb_bucket}") |> range(start: -30d) |> filter(fn:(r) => r._measurement == "deployed_configs" and r.customer_name == "{customer_name}" and r.device_name == "{device_name}") |> sort(columns: ["_time"], desc: true) |> limit(n: 1)'
        result = influx_client.query_api().query(query=query, org=influxdb_org)
        if result and len(result) > 0:
            return result[0].records[0].get_value()
        return None

def find_previous_deployment_id(customer_name: str, influx_client, current_deployment_id: str) -> Optional[str]:
    """Find the most recent deployment ID for a customer prior to the current deployment."""
    query = f'''
    from(bucket: "{influxdb_bucket}")
    |> range(start: -30d)
    |> filter(fn: (r) => r._measurement == "audit_logs" and r.customer_name == "{customer_name}")
    |> sort(columns: ["_time"], desc: true)
    '''
    result = influx_client.query_api().query(query=query, org=influxdb_org)
    
    deployment_ids = []
    
    for table in result:
        for record in table.records:
            deployment_id = record.values["deployment_id"]
            deployment_ids.append(deployment_id)

    if current_deployment_id not in deployment_ids:
        deployment_ids.append(current_deployment_id)
        print(f"Added current deployment ID: {current_deployment_id}")  # Debug statement

    deployment_ids.sort()

    current_index = deployment_ids.index(current_deployment_id)
    if current_index > 0:
        previous_deployment_id = deployment_ids[current_index - 1]
        print(f"This customer's most recent (previous) Deployment ID: {previous_deployment_id}")  # Debug statement
        return previous_deployment_id
    else:
        print("No previous deployment ID found.")  # Debug statement
        return None

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
    if not old_config_path or (data_source == 'yaml' and not os.path.exists(old_config_path)):
        return "No previous configuration to compare."

    if data_source == 'yaml':
        with open(old_config_path, 'r') as file:
            old_config = file.read().strip().replace('\r\n', '\n').split('\n')
    elif data_source == 'mongodb':
        old_config = old_config_path.strip().replace('\r\n', '\n').split('\n')

    new_config_lines = new_config.strip().replace('\r\n', '\n').split('\n')
    diff = list(difflib.unified_diff(old_config, new_config_lines, fromfile='old_config', tofile='new_config', lineterm=''))

    return '\n'.join(diff) if diff else "No changes detected."

def cleanup_generated_configs(customer_name: str):
    """Clean up generated configuration files for the customer."""
    directory = 'generated_configs'
    for file_name in os.listdir(directory):
        if file_name.startswith(customer_name):
            file_path = os.path.join(directory, file_name)
            try:
                os.remove(file_path)
                print(f"Deleted generated config file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

def deploy_configurations(username: str, password: str, customer_name: str, device_names: dict) -> Optional[str]:
    """Deploy configurations to specified devices for a customer."""
    error_log = check_for_error_logs(customer_name)
    if error_log:
        return f"Deployment aborted due to config generation errors: {error_log['error_message']} (Error Code: {error_log['error_code']})"

    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    if data_source == 'yaml':
        devices, _, _ = load_yaml('devices/network_devices.yaml')
    else:
        customer_data, access_device_info, pe_device_info = load_devices('mongodb', customer_name)
        devices = {
            access_device_info['device_name']: access_device_info,
            pe_device_info['device_name']: pe_device_info
        }
        print("Loaded devices from MongoDB:", devices)  # Debug statement to print the loaded devices

    operator = get_current_user()
    operator_ip = get_ip_address()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    audit_entries = []

    deployment_id = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    influx_client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org) if data_source == 'mongodb' else None

    previous_deployment_id = None
    if influx_client:
        previous_deployment_id = find_previous_deployment_id(customer_name, influx_client, deployment_id)
    print(f"Deployment started by {operator} from IP {operator_ip} at {datetime.datetime.now()}")

    config_suffixes = ['config_remove', 'config', 'config_deactivate']
    all_configs = defaultdict(list)

    for device_name, config_action in device_names.items():
        if device_name not in devices:
            print(f"Device {device_name} not found in device configuration.")
            print("Available devices:", list(devices.keys()))  # Debug statement to list available devices
            return f"Deployment aborted. Device not found: {device_name}"

        for suffix in config_suffixes:
            config_type = f"{config_action}_{suffix}.txt"
            config_file_name = f"{customer_name}_{device_name}_{config_type}"
            config_file_path = f"generated_configs/{config_file_name}"

            if os.path.exists(config_file_path):
                device_info = devices[device_name]
                all_configs[device_name].append((config_file_path, device_info['ip_address'], device_info['device_type'], suffix))
                print(f"Added configuration for {device_name}: {config_file_path}")

    if not all_configs:
        return "Deployment aborted. No configuration files found."

    start_time = time.time()
    try:
        for device_name, configs in all_configs.items():
            previous_config_path = find_latest_config(customer_name, device_name, influx_client)  # Find the latest config before any changes
            for config_file_path, ip_address, device_type, suffix in configs:
                print(f"Deploying configuration for {device_name} from {config_file_path}")
                try:
                    ssh_client.connect(ip_address, username=username, password=password, timeout=10)
                    channel = ssh_client.invoke_shell()

                    with open(config_file_path, 'r') as file:
                        configuration = file.read()

                    commands = prepare_device_commands(device_type, configuration)
                    for command in commands:
                        channel.send(command + '\n')
                        time.sleep(2)

                    ssh_client.close()

                except paramiko.ssh_exception.SSHException as e:
                    return f"Deployment failed for {device_name} with error: {str(e)}. Please retry the operation."

                is_deactivate = suffix == 'config_deactivate'
                is_new_config = suffix == 'config'

                if is_new_config or is_deactivate:
                    diff_results = ""
                    if is_new_config:
                        diff_results = compare_configurations(configuration, previous_config_path)

                    if data_source == 'yaml':
                        deployed_config_path = save_deployed_config(customer_name, device_name, configuration)
                    elif data_source == 'mongodb':
                        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
                        point = Point("deployed_configs").tag("customer_name", customer_name).tag("device_name", device_name).field("config_content", configuration).tag("operator", operator).time(datetime.datetime.utcnow(), write_precision='s')
                        write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)
                        print(f"Written deployed config for {device_name} to InfluxDB.")  # Debug statement
                        deployed_config_path = configuration

                    audit_entry = create_audit_log_entry(
                        operator=operator,
                        operator_ip=operator_ip,
                        device_name=device_name,
                        device_type=device_type,
                        configuration_type=config_type.split('_')[0],
                        configuration_path=config_file_path,
                        deployed_config_path=deployed_config_path,
                        diff_results=diff_results,
                        is_deactivate=is_deactivate,
                        timestamp=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                        elapsed_time=f"Deployment completed in {time.time() - start_time:.2f} seconds"
                    )
                    audit_entries.append(audit_entry)

        if data_source == 'yaml':
            audit_path = write_audit_log(customer_name, audit_entries)
            print(f"Deployment completed successfully. Detailed audit log saved at: {audit_path}")
            cleanup_generated_configs(customer_name)
        elif data_source == 'mongodb':
            write_api = influx_client.write_api(write_options=SYNCHRONOUS)
            for entry in audit_entries:
                point = Point("audit_logs").tag("customer_name", customer_name).tag("deployment_id", deployment_id).field("entry", json.dumps(entry)).tag("operator", operator).time(datetime.datetime.utcnow(), write_precision='s')
                write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)

            print(f"=== Cleanup of temporary generated configs ===")
            cleanup_generated_configs(customer_name)
            print(f"=== End of cleanup ===")
            print(f"Deployment issued by user {operator} for customer {customer_name} completed successfully in {time.time() - start_time:.2f} seconds.")
            print(f"Detailed audit log saved in InfluxDB under deployment ID {deployment_id}.")
            print(f"To check the audit log entries for this deployment, use: python netprovisioncli_commitdb.py --deployment-id {deployment_id}")
            print(f"To check the audit log from within NetProvisionCLI Shell: NetProvisionCLI/customer> commitdb --deployment-id {deployment_id}")
            if previous_deployment_id:
                print(f"To compare the new deployment with the previous configurations, use: python netprovisioncli_commitdb.py --diff-check {deployment_id} {previous_deployment_id}")
                print(f"To diff-check this deployment in NetProvisionCLI Shell: NetProvisionCLI/customer> commitdb --diff-check {deployment_id} {previous_deployment_id}")
            else:
                print("No previous deployment ID found to compare.")  # Debug statement

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

def load_devices(source: str, customer_name: str = None) -> tuple:
    """Load device data from the specified source (yaml or mongodb)."""
    if source == 'yaml':
        return load_yaml('devices/network_devices.yaml')
    elif source == 'mongodb':
        settings = load_settings()
        conn_string = settings['mongodb_connection']['uri']
        db_name = settings['mongodb_connection']['database_name']
        return load_mongodb(conn_string, db_name, customer_name)
    else:
        return {}, {}, f"Unsupported source: {source}"
