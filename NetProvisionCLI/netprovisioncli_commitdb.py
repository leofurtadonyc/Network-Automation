import argparse
from influxdb_client import InfluxDBClient
import json

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

def query_audit_log(deployment_id, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    query = f'''
    from(bucket: "{influxdb_bucket}")
    |> range(start: -30d)
    |> filter(fn: (r) => r._measurement == "audit_logs" and r._field == "entry" and r.deployment_id == "{deployment_id}")
    '''
    result = client.query_api().query(query=query, org=influxdb_org)
    
    if result:
        for table in result:
            for record in table.records:
                entry = json.loads(record.get_value())
                print(json.dumps(entry, indent=4))
    else:
        print(f"No audit log entry found for deployment ID: {deployment_id}")

def main():
    settings = load_settings()
    influxdb_url = settings['influxdb']['url']
    influxdb_token = settings['influxdb']['token']
    influxdb_org = settings['influxdb']['org']
    influxdb_bucket = settings['influxdb']['bucket']

    parser = argparse.ArgumentParser(description="Query InfluxDB for a specific audit log entry based on deployment ID.")
    parser.add_argument("--deployment-id", type=str, required=True, help="Deployment ID to query the audit log entry.")
    args = parser.parse_args()

    query_audit_log(args.deployment_id, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)

if __name__ == "__main__":
    main()
