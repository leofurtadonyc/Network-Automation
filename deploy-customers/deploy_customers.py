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
import getpass
import socket

def get_current_user():
    return getpass.getuser()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = 'N/A'
    finally:
        s.close()
    return IP

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
    audit_dir = 'audit_logs'
    if not os.path.exists(audit_dir):
        os.makedirs(audit_dir)
    
    paramiko.util.log_to_file('audit_logs/paramiko.log')
    
    audit_file_name = f"{customer_name}_config_deploy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_audit.txt"
    audit_file_path = os.path.join(audit_dir, audit_file_name)

    with open(audit_file_path, 'w') as file:
        file.write(f"Operator: {audit_entries[0]['operator']} from IP {audit_entries[0]['operator_ip']}\n")
        file.write("--------------------------------------------------\n")
        for entry in audit_entries:
            file.write(f"Deployment start: {entry['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Deployment end: {entry['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Deployment duration: {(entry['end_time'] - entry['start_time']).seconds} seconds\n")
            file.write(f"Device: {entry['device_name']} ({entry['device_type']})\n")
            file.write(f"Generated config file: {entry['generated_config_path']}\n")
            file.write(f"Deployed config file: {entry['deployed_config_path']}\n")
            file.write(f"Deployment result: {'Success' if 'successfully' in entry['result'] else 'Failure'}\n")
            file.write("--------------------------------------------------\n")
    
    return audit_file_path

def save_deployed_config(customer_name, device_name, configuration):
    """Saves the deployed configuration to a file."""
    deployed_dir = 'deployed_configs'
    if not os.path.exists(deployed_dir):
        os.makedirs(deployed_dir)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{customer_name}_deployed_config_{device_name}_{timestamp}.txt"
    file_path = os.path.join(deployed_dir, filename)
    
    with open(file_path, 'w') as file:
        file.write(configuration)
    return file_path

def deploy_config(username, password, customer_name, access_device, pe_device):
    devices = load_devices()
    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    operator = get_current_user()
    operator_ip = get_ip_address()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    audit_entries = []

    for device_name, device_details in [(access_device, f"{customer_name}_access_config.txt"), (pe_device, f"{customer_name}_pe_config.txt")]:
        device = devices.get(device_name)
        if not device:
            continue

        ip_address = device['ip_address']
        device_type = device['device_type']
        generated_config_path = f"generated_configs/{device_details}"
        start_time = datetime.datetime.now()

        try:
            ssh_client.connect(ip_address, username=username, password=password, timeout=10)
            configuration = open(generated_config_path, 'r').read()

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

            deployed_config_path = save_deployed_config(customer_name, device_name, configuration)
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
                'generated_config_path': generated_config_path,
                'deployed_config_path': deployed_config_path,
                'result': result,
                'operator': operator,
                'operator_ip': operator_ip
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
