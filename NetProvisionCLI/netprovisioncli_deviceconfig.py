import argparse
import os
import paramiko
from paramiko import SSHException
import yaml
import bcrypt
import socket
from getpass import getpass
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from prettytable import PrettyTable
from difflib import unified_diff
import logging
import traceback

logging.getLogger("paramiko").setLevel(logging.WARNING)

# Helper function to read YAML settings
def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Helper function to fetch device configuration
def fetch_device_config(device_details, username, password):
    ip = device_details['ip_address']
    device_type = device_details['device_type']
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password, timeout=10)
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"Error: Unable to connect to {ip}. Please check the network connectivity and SSH settings. This could be transient, please retry.")
        return None
    except paramiko.ssh_exception.AuthenticationException:
        print(f"Error: Authentication failed for {username}@{ip}. Please check the username and password.")
        return None
    except paramiko.ssh_exception.SSHException as e:
        print(f"Error: {str(e)}. This could be transient, please retry.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}. This could be transient, please retry.")
        return None
    
    try:
        if device_type in ['cisco_ios', 'cisco_xe', 'cisco_xr']:
            command = "show running-config"
        elif device_type == 'juniper_junos':
            ssh.exec_command("set cli screen-length 0")
            command = "show configuration | display set | no-more"
        elif device_type == 'huawei_vrp':
            command = "display current-configuration"
        stdin, stdout, stderr = ssh.exec_command(command)
        config = stdout.read().decode()
    except Exception as e:
        print(f"Error: Failed to fetch configuration from {ip}. Please check the command and the device response.")
        logging.error(f"Error fetching configuration from {ip}: {traceback.format_exc()}")
        return None
    finally:
        ssh.close()
    return config

# Helper function to store configuration in YAML
def store_config_yaml(device_name, config):
    if config:
        directory = 'device_configs'
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        file_path = os.path.join(directory, f'{device_name}-config-{timestamp}.txt')
        with open(file_path, 'w') as file:
            file.write(config)
        print(f"Configuration for {device_name} saved to {file_path}")
        return file_path

# Helper function to store configuration in MongoDB
def store_config_mongodb(device_name, config, mongo_uri, db_name):
    if config:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db['deviceConfig']
        timestamp = datetime.now(timezone.utc)
        document = {
            "device_name": device_name,
            "config": config,
            "timestamp": timestamp
        }
        collection.insert_one(document)
        client.close()
        print(f"Configuration for {device_name} stored in MongoDB")
        return None

# Helper function to log audit in YAML
def log_audit_yaml(device_name, operation, user, duration, config_file_path):
    directory = 'audit_logs'
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    log_path = os.path.join(directory, f'BACKUP_{device_name}_{timestamp}.txt')
    with open(log_path, 'w') as file:
        file.write(f"Device: {device_name}\nOperation: {operation}\nUser: {user}\nDuration: {duration}s\nConfig File: {config_file_path}\n")
    print(f"Audit log for {device_name} written to {log_path}")

# Helper function to log audit in InfluxDB
def log_audit_influxdb(device_name, operation, user, duration, influx_settings):
    client = InfluxDBClient(url=influx_settings['url'], token=influx_settings['token'], org=influx_settings['org'])
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("deviceConfigBackup") \
        .tag("device", device_name) \
        .tag("operation", operation) \
        .tag("user", user) \
        .field("duration", duration) \
        .time(datetime.now(timezone.utc), WritePrecision.NS)
    write_api.write(bucket=influx_settings['bucket'], org=influx_settings['org'], record=point)
    client.close()
    print(f"Audit log for {device_name} written to InfluxDB")

# Helper function to display configuration from YAML
def display_config_yaml(device_name, date=None):
    directory = 'device_configs'
    if not os.path.exists(directory):
        print(f"No configuration files found for {device_name}.")
        return
    files = [f for f in os.listdir(directory) if f.startswith(f"{device_name}-config-")]
    if date:
        files = [f for f in files if date in f]
    if not files:
        print(f"No configuration files found for {device_name} on date {date}.")
        return
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(directory, x)))
    with open(os.path.join(directory, latest_file), 'r') as file:
        print(file.read())

# Helper function to display configuration from MongoDB
def display_config_mongodb(device_name, mongo_uri, db_name, date=None):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db['deviceConfig']
    query = {"device_name": device_name}
    if date:
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
        query["timestamp"] = {"$gte": start_date, "$lt": end_date}
    document = collection.find_one(query, sort=[("timestamp", -1)])
    client.close()
    if document:
        print(document["config"])
    else:
        print(f"No configuration found for {device_name} in MongoDB on date {date}.")

# Helper function to display audit history from YAML
def display_audit_history_yaml(last=None, date=None, device=None):
    directory = 'audit_logs'
    if not os.path.exists(directory):
        print("No audit logs found.")
        return
    files = [f for f in os.listdir(directory) if f.startswith("BACKUP_")]
    if date:
        files = [f for f in files if date in f]
    if device:
        files = [f for f in files if f'BACKUP_{device}_' in f]
    if last:
        files = sorted(files, key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)[:last]
    if not files:
        print("No audit logs found.")
        return
    table = PrettyTable(["Device", "Operation", "Date and Time", "Operator", "Config File"])
    table._max_width = {"Device": 20, "Operation": 20, "Date and Time": 20, "Operator": 20, "Config File": None}
    for file in files:
        with open(os.path.join(directory, file), 'r') as f:
            lines = f.readlines()
            device = lines[0].split(":")[1].strip() if len(lines) > 0 else "N/A"
            operation = lines[1].split(":")[1].strip() if len(lines) > 1 else "N/A"
            date_time = file.split("_")[2] + "_" + file.split("_")[3].split(".")[0]
            operator = lines[2].split(":")[1].strip() if len(lines) > 2 else "N/A"
            config_filename = lines[4].split(":")[1].strip() if len(lines) > 4 else "N/A"
            table.add_row([device, operation, date_time, operator, config_filename])
    table.max_width = 80
    print(table)

# Helper function to display audit history from InfluxDB
def display_audit_history_influxdb(influx_settings, last=None, date=None, device=None):
    client = InfluxDBClient(url=influx_settings['url'], token=influx_settings['token'], org=influx_settings['org'])
    query_api = client.query_api()
    query = f'from(bucket:"{influx_settings["bucket"]}") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "deviceConfigBackup")'
    if date:
        start_date = datetime.strptime(date, "%Y-%m-%d").isoformat() + "Z"
        end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).isoformat() + "Z"
        query = f'from(bucket:"{influx_settings["bucket"]}") |> range(start: {start_date}, stop: {end_date}) |> filter(fn: (r) => r._measurement == "deviceConfigBackup")'
    if device:
        query += f' |> filter(fn: (r) => r.device == "{device}")'
    tables = query_api.query(query)
    records = [record for table in tables for record in table.records]
    if last:
        records = records[-last:]
    if not records:
        print("No audit logs found.")
        return
    table = PrettyTable(["Device", "Operation", "Date and Time", "Operator"])
    for record in records:
        timestamp = datetime.fromtimestamp(record.get_time().timestamp()).strftime('%Y-%m-%d_%H:%M:%S')
        table.add_row([record.values["device"], record.values["operation"], timestamp, record.values["user"]])
    table.max_width = 80
    print(table)

# Helper function to log purge audit in InfluxDB
def log_purge_influxdb(user, influx_settings):
    client = InfluxDBClient(url=influx_settings['url'], token=influx_settings['token'], org=influx_settings['org'])
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("deviceConfigPurge") \
        .tag("operation", "purge") \
        .tag("user", user) \
        .time(datetime.now(timezone.utc), WritePrecision.NS)
    write_api.write(bucket=influx_settings['bucket'], org=influx_settings['org'], record=point)
    client.close()
    print(f"Purge operation by {user} logged to InfluxDB")

# Helper function to display purge history from InfluxDB
def display_purge_history_influxdb(influx_settings):
    client = InfluxDBClient(url=influx_settings['url'], token=influx_settings['token'], org=influx_settings['org'])
    query_api = client.query_api()
    query = f'from(bucket:"{influx_settings["bucket"]}") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "deviceConfigPurge")'
    tables = query_api.query(query)
    records = [record for table in tables for record in table.records]
    if not records:
        print("No purge logs found.")
        return
    table = PrettyTable(["Operator", "Date and Time", "Operation"])
    for record in records:
        timestamp = datetime.fromtimestamp(record.get_time().timestamp()).strftime('%Y-%m-%d_%H:%M:%S')
        table.add_row([record.values["user"], timestamp, record.values["operation"]])
    table.max_width = 80
    print(table)

# Helper function for diff-check
def diff_check(device1, timestamp1, device2, timestamp2, settings):
    data_source = settings['data_source']
    timestamp1_dt = datetime.strptime(timestamp1, '%Y-%m-%d_%H:%M:%S')
    timestamp2_dt = datetime.strptime(timestamp2, '%Y-%m-%d_%H:%M:%S')
    if data_source == 'yaml':
        file1 = f"device_configs/{device1}-config-{timestamp1}.txt"
        file2 = f"device_configs/{device2}-config-{timestamp2}.txt"
        if not os.path.exists(file1) or not os.path.exists(file2):
            print(f"Error: One or both of the specified configuration files do not exist.")
            return
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            diff = list(unified_diff(f1.readlines(), f2.readlines(), fromfile=file1, tofile=file2))
            if diff:
                print("".join(diff))
            else:
                print("No differences found.")
    elif data_source == 'mongodb':
        client = MongoClient(settings['mongodb_connection']['uri'])
        db = client[settings['mongodb_connection']['database_name']]
        collection = db['deviceConfig']
        
        doc1 = collection.find_one({"device_name": device1, "timestamp": {"$gte": timestamp1_dt, "$lt": timestamp1_dt + timedelta(seconds=1)}})
        doc2 = collection.find_one({"device_name": device2, "timestamp": {"$gte": timestamp2_dt, "$lt": timestamp2_dt + timedelta(seconds=1)}})

        if not doc1 or not doc2:
            print(f"Error: One or both of the specified configuration records do not exist in MongoDB.")
            return
        
        config1 = doc1['config'].splitlines(keepends=True)
        config2 = doc2['config'].splitlines(keepends=True)
        
        diff = list(unified_diff(config1, config2, fromfile=f"{device1}-{timestamp1}", tofile=f"{device2}-{timestamp2}"))
        if diff:
            print("".join(diff))
        else:
            print("No differences found.")
        client.close()

# Main function for backup operation
def backup_device(device_name, username, password, settings):
    data_source = settings['data_source']
    success_count = 0
    failure_count = 0
    failures = []
    if data_source == 'yaml':
        devices = read_yaml('devices/network_devices.yaml')['devices']
    else:
        client = MongoClient(settings['mongodb_connection']['uri'])
        db = client[settings['mongodb_connection']['database_name']]
        devices = {device['device_name']: device for device in db['devices'].find()}
        client.close()

    if device_name == 'all':
        device_list = devices.keys()
    else:
        device_list = [device_name]

    for device in device_list:
        if device not in devices:
            print(f"Device {device} not found in the inventory.")
            failures.append((device, "Device not found in the inventory"))
            failure_count += 1
            continue
        device_details = devices[device]
        start_time = datetime.now()
        config = fetch_device_config(device_details, username, password)
        if config is None:
            failures.append((device, "Failed to fetch configuration"))
            failure_count += 1
            continue
        duration = (datetime.now() - start_time).total_seconds()
        if data_source == 'yaml':
            config_file_path = store_config_yaml(device, config)
            log_audit_yaml(device, 'backup', os.getlogin(), duration, config_file_path)
        else:
            store_config_mongodb(device, config, settings['mongodb_connection']['uri'], settings['mongodb_connection']['database_name'])
            log_audit_influxdb(device, 'backup', os.getlogin(), duration, settings['influxdb'])
        success_count += 1

    print(f"Summary: {success_count} configurations successfully retrieved and written.")
    if failures:
        print(f"{failure_count} configurations weren't fetched due to connection failures:")
        for device, reason in failures:
            print(f"Device: {device}, Reason: {reason}")

# Helper function to purge configurations from MongoDB
def purge_configs(date, username, password, settings):
    client = MongoClient(settings['mongodb_connection']['uri'])
    db = client[settings['mongodb_connection']['database_name']]
    collection = db['deviceConfig']
    start_date = datetime.strptime(date, "%Y-%m-%d")
    result = collection.delete_many({"timestamp": {"$gte": start_date}})
    client.close()
    print(f"Purged {result.deleted_count} configurations from MongoDB.")
    log_purge_influxdb(username, settings['influxdb'])
    purge_audit_logs_influxdb(start_date, settings['influxdb'])

# Helper function to purge audit logs from InfluxDB
def purge_audit_logs_influxdb(start_date, influx_settings):
    client = InfluxDBClient(url=influx_settings['url'], token=influx_settings['token'], org=influx_settings['org'])
    delete_api = client.delete_api()
    end_date = datetime.now(timezone.utc)
    delete_api.delete(start=start_date, stop=end_date, bucket=influx_settings['bucket'], org=influx_settings['org'], predicate='_measurement="deviceConfigBackup"')
    client.close()
    print("Corresponding audit entries from InfluxDB purged.")

def main():
    parser = argparse.ArgumentParser(description='NetProvision CLI for device configurations')
    parser.add_argument('--backup', type=str, help='Backup the running configuration of a specific device hostname or "all" for all devices')
    parser.add_argument('--display', type=str, help='Display the latest or most recent stored configuration for a specific device hostname')
    parser.add_argument('--audit-history', action='store_true', help='Display audit logs for backup operations')
    parser.add_argument('--device', type=str, help='Specify a device for audit-history or diff-check')
    parser.add_argument('--last', type=int, help='Display the last N backup operations')
    parser.add_argument('--date', type=str, help='Display backup operations for a specific date (YYYY-MM-DD)')
    parser.add_argument('--diff-check', nargs=4, type=str, help='Display differences between two versions. Usage: --diff-check <device1> <timestamp1> <device2> <timestamp2>')
    parser.add_argument('--username', type=str, help='Username for backup operations and purgedb')
    parser.add_argument('--password', type=str, help='Password for backup operations and purgedb')
    parser.add_argument('--purgedb', type=str, help='Purge configurations from MongoDB from a specific date (YYYY-MM-DD) or view purge history. Usage: --purgedb <YYYY-MM-DD> or --purgedb history')

    args = parser.parse_args()

    settings = read_yaml('settings/settings.yaml')

    if args.backup:
        username = args.username
        if not username:
            print("Username is required for backup operations.")
            return
        password = args.password if args.password else getpass("Password: ")
        backup_device(args.backup, username, password, settings)
    elif args.display:
        if settings['data_source'] == 'yaml':
            display_config_yaml(args.display, args.date)
        else:
            display_config_mongodb(args.display, settings['mongodb_connection']['uri'], settings['mongodb_connection']['database_name'], args.date)
    elif args.audit_history:
        if settings['data_source'] == 'yaml':
            display_audit_history_yaml(args.last, args.date, args.device)
        else:
            display_audit_history_influxdb(settings['influxdb'], args.last, args.date, args.device)
    elif args.diff_check:
        diff_check(*args.diff_check, settings)
    elif args.purgedb:
        if settings['data_source'] == 'yaml':
            print("Purge operation is not supported for YAML data source.")
            return
        if args.purgedb.lower() == 'history':
            display_purge_history_influxdb(settings['influxdb'])
        else:
            username = args.username
            if not username:
                print("Username is required for purge operations.")
                return
            password = args.password if args.password else getpass("Password: ")
            confirmation = input(f"WARNING: This operation will delete all configurations from {args.purgedb} onwards from the MongoDB database and corresponding entries from InfluxDB. Type 'YES' to confirm: ")
            if confirmation == 'YES':
                purge_configs(args.purgedb, username, password, settings)
            else:
                print("Purge operation cancelled.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()