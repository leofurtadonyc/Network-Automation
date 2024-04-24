import paramiko
import yaml
import getpass
import hashlib

# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki


def load_device_credentials():
    with open('usercredentials.sec', 'r') as file:
        credentials = yaml.safe_load(file)
    return credentials

def authenticate_user(username, password):
    credentials = load_device_credentials()
    if username in credentials and credentials[username] == hashlib.sha256(password.encode()).hexdigest():
        return True
    return False

def load_network_devices():
    with open('devices/network_devices.yaml', 'r') as file:
        devices = yaml.safe_load(file)
    return devices

def deploy_config(customer_name, access_device, pe_device, username):
    # Load network devices
    devices = load_network_devices()

    # Check if access_device and pe_device exist in devices
    if access_device not in devices or pe_device not in devices:
        print("Invalid device name.")
        return

    # Check if username and password are valid
    password = getpass.getpass("Enter password: ")
    if not authenticate_user(username, password):
        print("Authentication failed.")
        return

    # Get access device details
    access_ip = devices[access_device]['ip_address']
    access_device_type = devices[access_device]['device_type']

    # Get pe device details
    pe_ip = devices[pe_device]['ip_address']
    pe_device_type = devices[pe_device]['device_type']

    # Generate config file paths
    access_config_file = f"generated_configs/{customer_name}_access_config.txt"
    pe_config_file = f"generated_configs/{customer_name}_pe_config.txt"

    # Connect to access device
    access_ssh = paramiko.SSHClient()
    access_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    access_ssh.connect(access_ip, username=username, password=password)

    # Deploy access config
    if access_device_type == 'cisco_xe':
        access_ssh.exec_command('config terminal')
        with open(access_config_file, 'r') as file:
            access_ssh.exec_command(file.read())
        access_ssh.exec_command('write terminal')
    elif access_device_type == 'cisco_xr':
        access_ssh.exec_command('config terminal')
        with open(access_config_file, 'r') as file:
            access_ssh.exec_command(file.read())
        access_ssh.exec_command('commit')
    elif access_device_type == 'juniper_junos':
        access_ssh.exec_command('edit')
        with open(access_config_file, 'r') as file:
            access_ssh.exec_command(file.read())
        access_ssh.exec_command('commit and-quit')
    elif access_device_type == 'huawei_vrp':
        access_ssh.exec_command('system-view')
        with open(access_config_file, 'r') as file:
            access_ssh.exec_command(file.read())
        access_ssh.exec_command('quit')
        access_ssh.exec_command('save')
        access_ssh.exec_command('Y')

    # Connect to pe device
    pe_ssh = paramiko.SSHClient()
    pe_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pe_ssh.connect(pe_ip, username=username, password=password)

    # Deploy pe config
    if pe_device_type == 'cisco_xe':
        pe_ssh.exec_command('config terminal')
        with open(pe_config_file, 'r') as file:
            pe_ssh.exec_command(file.read())
        pe_ssh.exec_command('write terminal')
    elif pe_device_type == 'cisco_xr':
        pe_ssh.exec_command('config terminal')
        with open(pe_config_file, 'r') as file:
            pe_ssh.exec_command(file.read())
        pe_ssh.exec_command('commit')
    elif pe_device_type == 'juniper_junos':
        pe_ssh.exec_command('edit')
        with open(pe_config_file, 'r') as file:
            pe_ssh.exec_command(file.read())
        pe_ssh.exec_command('commit and-quit')
    elif pe_device_type == 'huawei_vrp':
        pe_ssh.exec_command('system-view')
        with open(pe_config_file, 'r') as file:
            pe_ssh.exec_command(file.read())
        pe_ssh.exec_command('quit')
        pe_ssh.exec_command('save')
        pe_ssh.exec_command('Y')

    # Close SSH connections
    access_ssh.close()
    pe_ssh.close()

# Get user input
customer_name = input("Enter customer name: ")
access_device = input("Enter access device hostname: ")
pe_device = input("Enter PE device hostname: ")
username = input("Enter username: ")

# Deploy configurations
deploy_config(customer_name, access_device, pe_device, username)