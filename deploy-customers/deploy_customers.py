# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import paramiko
import yaml
import bcrypt
import os
import datetime
import argparse
import time
import paramiko.util

paramiko.util.log_to_file('paramiko.log')

def load_devices(file_path='devices/network_devices.yaml'):
    with open(file_path, 'r') as file:
        devices_dict = yaml.safe_load(file)
        return devices_dict['devices']

def verify_user(username, password, credentials_file='devices/usercredentials.sec'):
    with open(credentials_file, 'r') as file:
        for line in file:
            stored_username, hashed_password = line.strip().split(':')
            if stored_username == username and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
    return False

def write_audit_log(customer_name, audit_entries):
    """Writes all audit entries to a single log file for the session."""
    audit_dir = 'audit_logs'
    if not os.path.exists(audit_dir):
        os.makedirs(audit_dir)
    
    audit_file_name = f"{customer_name}_config_deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_audit.txt"
    audit_file_path = os.path.join(audit_dir, audit_file_name)

    with open(audit_file_path, 'w') as file:
        for entry in audit_entries:
            file.write(f"Deployment start: {entry['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Deployment end: {entry['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Deployment duration: {(entry['end_time'] - entry['start_time']).seconds} seconds\n")
            file.write(f"Device: {entry['device_name']} ({entry['device_type']})\n")
            file.write(f"Configuration file: {entry['config_file_path']}\n")
            file.write(f"Deployment result: {'Success' if 'successfully' in entry['result'] else 'Failure'}\n")
            file.write("--------------------------------------------------\n")
    
    return audit_file_path

def deploy_config(username, password, customer_name, access_device, pe_device):
    devices = load_devices()
    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    audit_entries = []

    for device_name, device_details in [(access_device, f"{customer_name}_access_config.txt"), (pe_device, f"{customer_name}_pe_config.txt")]:
        device = devices.get(device_name)
        if not device:
            continue

        ip_address = device['ip_address']
        device_type = device['device_type']
        config_file_path = f"generated_configs/{device_details}"
        start_time = datetime.datetime.now()

        try:
            ssh_client.connect(ip_address, username=username, password=password, timeout=10)
            configuration = open(config_file_path, 'r').read()

            commands = {
                'cisco_xe': ['config terminal', configuration, 'end', 'write memory', 'exit'],
                'cisco_xr': ['config terminal', configuration, 'commit', 'end', 'exit'],
                'juniper_junos': ['edit', configuration, 'commit and-quit'],
                'huawei_vrp': ['system-view', configuration, 'return', 'save', 'Y', 'quit']
            }.get(device_type, [])

            channel = ssh_client.invoke_shell()
            for command in commands:
                channel.send(command + '\n')
                time.sleep(1)

            result = f"Configuration deployed successfully on {device_name}"
        except Exception as e:
            result = f"Failed to deploy configuration on {device_name}: {e}"
        finally:
            end_time = datetime.datetime.now()
            audit_entries.append({
                'start_time': start_time,
                'end_time': end_time,
                'device_name': device_name,
                'device_type': device_type,
                'config_file_path': config_file_path,
                'result': result
            })
            ssh_client.close()

    audit_path = write_audit_log(customer_name, audit_entries)
    return f"Deployment completed. Detailed audit log saved at: {audit_path}"

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