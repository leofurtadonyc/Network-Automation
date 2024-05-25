import os
import json
import argparse
import getpass
from pymongo import MongoClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def load_settings():
    """Load settings from the settings.yaml file."""
    import yaml
    try:
        with open('settings/settings.yaml', 'r') as file:
            settings = yaml.safe_load(file)
            return settings
    except FileNotFoundError:
        print("settings.yaml file not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing settings.yaml file: {e}")
        return {}

def import_mongodb_data(connection_string, database_name, input_file):
    client = MongoClient(connection_string)
    db = client[database_name]
    
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    db['customers'].delete_many({})
    db['devices'].delete_many({})
    
    db['customers'].insert_many(data['customers'])
    db['devices'].insert_many(data['devices'])
    
    print(f"MongoDB data imported from {input_file}")

def import_influxdb_data(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, input_file):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    for entry in data:
        point = Point(entry['measurement']).tag("customer_name", entry['tags'].get("customer_name", "")).tag("deployment_id", entry['tags'].get("deployment_id", "")).field("value", entry['value']).time(entry['time'])
        write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)
    
    print(f"InfluxDB data imported from {input_file}")

def main():
    print("\nWARNING: This operation will overwrite existing data in MongoDB and InfluxDB.")
    print("Some data may be lost in the process as it will be a full restore.\n")

    parser = argparse.ArgumentParser(description="Import MongoDB and InfluxDB data from JSON files.")
    parser.add_argument("--import-mongo", action='store_true', help="Import MongoDB data from JSON file.")
    parser.add_argument("--import-influx", action='store_true', help="Import InfluxDB data from JSON file.")
    parser.add_argument("--mongo-input", type=str, default="mongodb_import.json", help="Input file for MongoDB data.")
    parser.add_argument("--influx-input", type=str, default="influxdb_import.json", help="Input file for InfluxDB data.")
    parser.add_argument("--username", type=str, help="Username for authentication.")
    
    args = parser.parse_args()

    username = args.username
    if not username:
        username = input("Username: ")
    password = getpass.getpass("Password: ")

    confirm = input("Are you sure you want to proceed with the restore? Type YES to confirm: ")
    if confirm != "YES":
        print("Restore operation aborted.")
        return
    
    settings = load_settings()
    
    connection_string = settings['mongodb_connection']['uri']
    database_name = settings['mongodb_connection']['database_name']
    influxdb_url = settings['influxdb']['url']
    influxdb_token = settings['influxdb']['token']
    influxdb_org = settings['influxdb']['org']
    influxdb_bucket = settings['influxdb']['bucket']
    
    if args.import_mongo:
        import_mongodb_data(connection_string, database_name, args.mongo_input)
    
    if args.import_influx:
        import_influxdb_data(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, args.influx_input)
    
    if not (args.import_mongo or args.import_influx):
        parser.print_help()

if __name__ == "__main__":
    main()
