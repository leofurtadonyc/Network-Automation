import argparse
import yaml
import logging
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import getpass

# File path for the debug log file
log_file = 'netmiko.log'

# Check if the debug log file already exists and delete it if it does
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lists to store report data
successful_devices = []
failed_devices = []

# Function to read YAML file
def read_yaml(file):
    with open(file, 'r') as stream:
        return yaml.safe_load(stream)

# Function to retrieve config based on device type
def retrieve_config(device_details, username, password):
    try:
        connection = ConnectHandler(
            device_type=device_details['device_type'],
            host=device_details['ip_address'],
            username=username,
            password=password,
            secret=device_details.get('secret', '')
        )
        connection.auto_width = False
        
        # Set the expected prompt for different device types
        if device_details['device_type'] in ['cisco_ios', 'cisco_xe']:
            expect_string = None  # Use Netmiko's default prompt detection
        elif device_details['device_type'] == 'cisco_xr':
            # expect_string = 'RP/0/RSP'
            expect_string = None
        elif device_details['device_type'] == 'juniper_junos':
            # expect_string = '>'
            expect_string = None
        elif device_details['device_type'] == 'huawei_vrp':
            expect_string = None  # Specify if there's a specific ending character for Huawei VRP devices; using Netmiko's default prompt detection for now
        else:
            logging.error(f"Unsupported device type {device_details['device_type']}")
            return

        # Execute the appropriate command based on the device type
        if device_details['device_type'] in ['cisco_ios', 'cisco_xe', 'cisco_xr']:
            command = "show running-config"
        elif device_details['device_type'] == 'juniper_junos':
            connection.send_command("set cli screen-length 0")  # Disable paging
            command = "show configuration | display set | no-more"
        elif device_details['device_type'] == 'huawei_vrp':
            command = "display current-configuration"
        
        # running_config = connection.send_command_expect(command, expect_string=expect_string, delay_factor=5, max_loops=1000)
        print("Accessing and collecting running configurations from device list, please wait...")
        running_config = connection.send_command(command, expect_string=expect_string, delay_factor=20, max_loops=3000)

        # Save running-config of each device to a separate file
        hostname = device_details.get('hostname', None)
        if hostname:
            date_today = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
            filename = f"{hostname}-{date_today}.cfg"
            output_directory = f"./configs/{hostname}/"
            os.makedirs(output_directory, exist_ok=True)
            with open(os.path.join(output_directory, filename), 'w') as f:
                f.write(running_config)
            logging.info(f"Retrieved configuration from device {hostname}")
            successful_devices.append(hostname)
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        logging.error(f"Failed to connect to device {device_details['hostname']}: {e}")
        failed_devices.append((device_details['hostname'], str(e)))
    finally:
        if 'connection' in locals():
            connection.disconnect()

# Main function
def main(file_name, max_workers, ip_address=None):
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    data = read_yaml(file_name)
    device_details_list = data['devices']

    if ip_address:
        device_details_list = [d for d in device_details_list if d['ip_address'] == ip_address]

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(retrieve_config, device, username, password) for device in device_details_list]
        for future in as_completed(futures):
            future.result()
    
    end_time = time.time()

    # Printing Report
    print("\n--- Execution Report ---")
    print(f"\nExecution time: {end_time - start_time} seconds")
    print("\nSuccessful Devices:")
    for device in successful_devices:
        print(f"- {device}")
    print("\nFailed Devices:")
    for device, reason in failed_devices:
        print(f"- {device}, Reason: {reason}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve configurations from network devices.")
    parser.add_argument('file', help="YAML file with device details.")
    parser.add_argument('--max_workers', type=int, default=5, help="Maximum number of concurrent workers.")
    parser.add_argument('--ip_address', help="Process a specific device by IP address.")
    args = parser.parse_args()
    main(args.file, args.max_workers, args.ip_address)
