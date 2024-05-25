import os
import json
import argparse
import datetime
from pymongo import MongoClient
from bson import ObjectId
from influxdb_client import InfluxDBClient

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

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def export_mongodb_data(connection_string, database_name, output_file):
    client = MongoClient(connection_string)
    db = client[database_name]
    
    customers = list(db['customers'].find({}))
    devices = list(db['devices'].find({}))
    
    data = {
        'customers': customers,
        'devices': devices
    }
    
    if not os.path.exists('export_data'):
        os.makedirs('export_data')
    
    output_path = os.path.join('export_data', output_file)
    with open(output_path, 'w') as file:
        json.dump(data, file, cls=CustomJSONEncoder)
    
    print(f"MongoDB data exported to {output_path}")

def export_influxdb_data(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, output_file):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    query = f'''
    from(bucket: "{influxdb_bucket}")
    |> range(start: 0)
    '''
    
    result = client.query_api().query(query=query, org=influxdb_org)
    
    data = []
    for table in result:
        for record in table.records:
            data.append({
                'measurement': record.get_measurement(),
                'tags': record.values,
                'time': record.get_time().strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                'value': record.get_value()
            })
    
    if not os.path.exists('export_data'):
        os.makedirs('export_data')
    
    output_path = os.path.join('export_data', output_file)
    with open(output_path, 'w') as file:
        json.dump(data, file, cls=CustomJSONEncoder)
    
    print(f"InfluxDB data exported to {output_path}")

def main():
    settings = load_settings()
    
    connection_string = settings['mongodb_connection']['uri']
    database_name = settings['mongodb_connection']['database_name']
    influxdb_url = settings['influxdb']['url']
    influxdb_token = settings['influxdb']['token']
    influxdb_org = settings['influxdb']['org']
    influxdb_bucket = settings['influxdb']['bucket']
    
    parser = argparse.ArgumentParser(description="Export MongoDB and InfluxDB data to JSON files. It requires MongoDB and InfluxDB settings in the settings.yaml file.")
    parser.add_argument("--export-mongo", action='store_true', help="Export MongoDB data to JSON file.")
    parser.add_argument("--export-influx", action='store_true', help="Export InfluxDB data to JSON file.")
    parser.add_argument("--mongo-output", type=str, default="mongodb_export.json", help="Output file for MongoDB data.")
    parser.add_argument("--influx-output", type=str, default="influxdb_export.json", help="Output file for InfluxDB data.")
    
    args = parser.parse_args()
    
    if args.export_mongo:
        export_mongodb_data(connection_string, database_name, args.mongo_output)
    
    if args.export_influx:
        export_influxdb_data(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, args.influx_output)
    
    if not (args.export_mongo or args.export_influx):
        parser.print_help()

if __name__ == "__main__":
    main()
