import argparse
from influxdb_client import InfluxDBClient
import json
import difflib
from datetime import datetime
from utils.network_utils import get_current_user

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
    
    entries = []
    if result:
        for table in result:
            for record in table.records:
                entry = json.loads(record.get_value())
                entries.append(entry)
    else:
        print(f"No audit log entry found for deployment ID: {deployment_id}")
    return entries

def list_deployments(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, customer=None, timeframe=None, last=None):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    
    query = f'''
    from(bucket: "{influxdb_bucket}")
    |> range(start: -30d)
    |> filter(fn: (r) => r._measurement == "audit_logs")
    '''
    
    if customer:
        query += f'''|> filter(fn: (r) => r.customer_name == "{customer}")\n'''
    
    if timeframe:
        start_time = f"{timeframe}T00:00:00Z"
        end_time = f"{timeframe}T23:59:59Z"
        query += f'''|> filter(fn: (r) => r._time >= {start_time} and r._time <= {end_time})\n'''

    query += '''
    |> keep(columns: ["deployment_id", "_time", "customer_name", "operator"])
    |> sort(columns: ["_time"], desc: true)
    |> unique(column: "deployment_id")
    '''
    
    query += '''|> limit(n: 500)\n'''  # Apply a default limit of 500 to avoid overwhelming the query results

    # print(f"Query: {query}")  # Debugging: Print the query

    result = client.query_api().query(query=query, org=influxdb_org)
    
    deployments = []
    if result:
        for table in result:
            for record in table.records:
                # print(f"Record: {record.values}")  # Debugging: Print the record values
                deployments.append({
                    "deployment_id": record["deployment_id"],
                    "timestamp": record.get_time().strftime('%Y-%m-%d %H:%M:%S'),
                    "customer_name": record["customer_name"],
                    "operator": record.values.get("operator", "N/A")  # Handle missing operator field
                })
    else:
        print("No deployments found.")

    # Apply the limit if the --last argument is provided
    if last:
        deployments = deployments[:last]

    return deployments

def diff_check(deployment_id1, deployment_id2, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket):
    entries1 = query_audit_log(deployment_id1, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)
    entries2 = query_audit_log(deployment_id2, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)
    
    if not entries1 or not entries2:
        print("One or both deployment IDs not found.")
        return
    
    for entry1, entry2 in zip(entries1, entries2):
        config1 = entry1['deployed_config_path'].splitlines()
        config2 = entry2['deployed_config_path'].splitlines()
        
        diff = difflib.unified_diff(config1, config2, fromfile=deployment_id1, tofile=deployment_id2)
        print('\n'.join(diff))

def main():
    settings = load_settings()
    influxdb_url = settings['influxdb']['url']
    influxdb_token = settings['influxdb']['token']
    influxdb_org = settings['influxdb']['org']
    influxdb_bucket = settings['influxdb']['bucket']

    parser = argparse.ArgumentParser(description="Query InfluxDB for audit log entries.")
    parser.add_argument("--customer", type=str, help="Filter deployments by customer name.")
    parser.add_argument("--deployment-id", type=str, help="Deployment ID to query the audit log entry.")
    parser.add_argument("--deployment-list", action='store_true', help="List the last 500 deployments.")
    parser.add_argument("--diff-check", nargs=2, metavar=('DEPLOYMENT_ID1', 'DEPLOYMENT_ID2'), help="Display the differences between two deployment IDs.")
    parser.add_argument("--timeframe", type=str, help="Filter deployments by date (YYYY-MM-DD).")
    parser.add_argument("--last", type=int, help="List the last N deployments.")

    args = parser.parse_args()

    if args.deployment_id:
        entries = query_audit_log(args.deployment_id, influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)
        if entries:
            for entry in entries:
                print(json.dumps(entry, indent=4))
    elif args.deployment_list or args.customer or args.timeframe or args.last:
        deployments = list_deployments(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket, args.customer, args.timeframe, args.last)
        print(f"{'Deployment ID':<20} {'Timestamp':<30} {'Customer Name':<20} {'Operator':<20}")
        print("="*90)
        for deployment in deployments:
            print(f"{deployment['deployment_id']:<20} {deployment['timestamp']:<30} {deployment['customer_name']:<20} {deployment['operator']:<20}")
    elif args.diff_check:
        diff_check(args.diff_check[0], args.diff_check[1], influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
