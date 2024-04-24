# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import paramiko
import yaml
import bcrypt
import os
import argparse

def load_devices(file_path='devices/network_devices.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def verify_user(username, password, credentials_file='usercredentials.sec'):
    with open(credentials_file, 'r') as file:
        for line in file:
            stored_username, hashed_password = line.strip().split(':')
            if stored_username == username and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
    return False

def deploy_config(username, password, customer_name, access_device, pe_device):
    # Load device configurations and user validation
    devices = load_devices()
    if not verify_user(username, password):
        return "Authentication failed. Check username and password."

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for device_name, device_details in [(access_device, f"{customer_name}_access_config.txt"), (pe_device, f"{customer_name}_pe_config.txt")]:
        try:
            device_type = devices[device_name]['device_type']
            ip_address = devices[device_name]['ip_address']
            config_file_path = f"generated_configs/{device_details}"

            # Read configuration file
            with open(config_file_path, 'r') as file:
                configuration = file.read()

            # Connect to the device
            ssh_client.connect(ip_address, username=username, password=password)
            channel = ssh_client.invoke_shell()

            # Sending device specific commands
            if device_type == 'cisco_xe':
                commands = ['config terminal', configuration, 'end', 'write memory']
            elif device_type == 'cisco_xr':
                commands = ['config terminal', configuration, 'commit', 'exit']
            elif device_type == 'juniper_junos':
                commands = ['edit', configuration, 'commit and-quit']
            elif device_type == 'huawei_vrp':
                commands = ['system-view', configuration, 'return', 'save', 'Y']
            else:
                return f"Unsupported device type: {device_type}"

            for command in commands:
                channel.send(command + '\n')
                while not channel.recv_ready():  # Wait for the command to be processed
                    time.sleep(1)

            print(f"Configuration deployed successfully on {device_name}")
        except Exception as e:
            print(f"Failed to deploy configuration on {device_name}: {e}")
        finally:
            ssh_client.close()

    return "Deployment complete for all devices."

def main():
    parser = argparse.ArgumentParser(description="Network Configuration Deployment")
    parser.add_argument("customer_name", help="Customer name to identify config files")
    parser.add_argument("access_device", help="Hostname of the access device")
    parser.add_argument("pe_device", help="Hostname of the PE device")
    parser.add_argument("username", help="Username for SSH and credential verification")
    parser.add_argument("password", help="Password for SSH and credential verification")

    args = parser.parse_args()
    
    result = deploy_config(args.username, args.password, args.customer_name, args.access_device, args.pe_device)
    print(result)

if __name__ == "__main__":
    main()
