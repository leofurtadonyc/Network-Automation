# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import paramiko
import yaml
import bcrypt
# import os
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

def deploy_config(username, password, customer_name, access_device, pe_device):
    devices = load_devices()
    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results = []

    def attempt_connect(ip_address):
        retries = 3
        for attempt in range(1, retries + 1):
            try:
                ssh_client.connect(ip_address, username=username, password=password, timeout=10)
                return ssh_client
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                if attempt < retries:
                    print(f"Retrying connection to {ip_address}... Attempt {attempt}")
                    time.sleep(5)
                else:
                    raise e

    for device_name, device_details in [(access_device, f"{customer_name}_access_config.txt"), (pe_device, f"{customer_name}_pe_config.txt")]:
        if device_name not in devices:
            results.append(f"Error: Device {device_name} not found in configuration.")
            continue

        device = devices[device_name]
        try:
            ip_address = device['ip_address']
            device_type = device['device_type']
            config_file_path = f"generated_configs/{device_details}"

            with open(config_file_path, 'r') as file:
                configuration = file.read()

            ssh_client = attempt_connect(ip_address)
            channel = ssh_client.invoke_shell()
            time.sleep(2)

            if device_type == 'cisco_xe':
                commands = ['config terminal', configuration, 'end', 'write memory', 'exit']
            elif device_type == 'cisco_xr':
                commands = ['config terminal', configuration, 'commit', 'end', 'exit']
            elif device_type == 'juniper_junos':
                commands = ['edit', configuration, 'commit and-quit']
            elif device_type == 'huawei_vrp':
                commands = ['system-view', configuration, 'return', 'save', 'Y', 'quit']
            else:
                print(f"Unsupported device type: {device_type}")
                continue

            output = ""
            for command in commands:
                channel.send(command + '\n')
                time.sleep(1)
                while not channel.recv_ready():
                    time.sleep(1)
                output += channel.recv(9999).decode('utf-8')

            results.append(f"Configuration deployed successfully on {device_name} with output: {output}")
        except Exception as e:
            results.append(f"Failed to deploy configuration on {device_name}: {e}")
        finally:
            ssh_client.close()

    return "\n".join(results)

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
