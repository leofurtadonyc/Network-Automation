import os
import pandas as pd
from pymongo import MongoClient
from influxdb_client import InfluxDBClient
import argparse
import json
import yaml
import sys

def load_settings():
    """Load settings from the settings.yaml file."""
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

def export_to_excel(customers, device_list, deployments, file_path):
    if not os.path.exists('reports'):
        os.makedirs('reports')

    writer = pd.ExcelWriter(file_path, engine='openpyxl')

    customer_data = []
    for customer in customers:
        customer_details = customer.get("customer_details", {})
        devices = customer_details.get("devices", {})
        service_details = customer_details.get("service_details", {})
        customer_data.append({
            "name": customer.get("name"),
            "email": customer_details.get("email"),
            "access_device_name": devices.get("access", {}).get("name"),
            "access_device_interface": devices.get("access", {}).get("interface"),
            "pe_device_name": devices.get("pe", {}).get("name"),
            "circuit_id": service_details.get("circuit_id"),
            "qos_input": service_details.get("qos_input"),
            "qos_output": service_details.get("qos_output"),
            "vlan_id": service_details.get("vlan_id"),
            "vlan_id_outer": service_details.get("vlan_id_outer"),
            "pw_id": service_details.get("pw_id"),
            "irb_ipaddr": service_details.get("irb_ipaddr"),
            "irb_ipv6addr": service_details.get("irb_ipv6addr"),
            "ipv4_lan": service_details.get("ipv4_lan"),
            "ipv4_nexthop": service_details.get("ipv4_nexthop"),
            "ipv6_lan": service_details.get("ipv6_lan"),
            "ipv6_nexthop": service_details.get("ipv6_nexthop")
        })

    df_customers = pd.DataFrame(customer_data)
    df_customers.to_excel(writer, sheet_name='Customers', index=False)

    device_data = []
    for device in device_list:
        if isinstance(device, dict):
            device_data.append({
                "device_name": device.get("device_name"),
                "device_type": device.get("device_type"),
                "device_role": device.get("device_role"),
                "ip_address": device.get("ip_address"),
                "loopback": device.get("loopback"),
                "customer_provisioning": device.get("customer_provisioning"),
                "forbidden_interfaces": ", ".join(device.get("forbidden_interfaces", [])) if isinstance(device.get("forbidden_interfaces"), list) else device.get("forbidden_interfaces")
            })
        else:
            print(f"Skipping non-dictionary device entry: {device}")

    df_devices = pd.DataFrame(device_data)
    df_devices.to_excel(writer, sheet_name='Devices', index=False)

    df_deployments = pd.DataFrame(deployments)
    df_deployments.to_excel(writer, sheet_name='Deployments', index=False)

    writer.close()

def get_customers(connection_string, database_name):
    client = MongoClient(connection_string)
    db = client[database_name]
    customers_collection = db['customers']
    return list(customers_collection.find({}))

def get_devices(connection_string, database_name):
    client = MongoClient(connection_string)
    db = client[database_name]
    devices_collection = db['devices']
    devices = list(devices_collection.find({}))
    print(f"Retrieved devices: {devices}")  # Debugging line
    return devices

def list_deployments(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)

    query = f'''
    from(bucket: "{influxdb_bucket}")
    |> range(start: -30d)
    |> filter(fn: (r) => r._measurement == "audit_logs")
    |> keep(columns: ["deployment_id", "_time", "customer_name", "operator"])
    |> sort(columns: ["_time"], desc: true)
    |> unique(column: "deployment_id")
    |> limit(n: 500)
    '''
    
    result = client.query_api().query(query=query, org=influxdb_org)
    
    deployments = []
    if result:
        for table in result:
            for record in table.records:
                deployments.append({
                    "deployment_id": record["deployment_id"],
                    "timestamp": record.get_time().strftime('%Y-%m-%d %H:%M:%S'),
                    "customer_name": record["customer_name"],
                    "operator": record.values.get("operator", "N/A")
                })
    return deployments

def main():
    settings = load_settings()
    connection_string = settings['mongodb_connection']['uri']
    database_name = settings['mongodb_connection']['database_name']
    influxdb_url = settings['influxdb']['url']
    influxdb_token = settings['influxdb']['token']
    influxdb_org = settings['influxdb']['org']
    influxdb_bucket = settings['influxdb']['bucket']

    parser = argparse.ArgumentParser(description="Export customer, device, and deployment data to an XLS file. It requires MongoDB and InfluxDB settings in the settings.yaml file.")
    parser.add_argument("--export", action='store_true', help="Export data to XLS file.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.export:
        customers = get_customers(connection_string, database_name)
        device_list = get_devices(connection_string, database_name)
        deployments = list_deployments(influxdb_url, influxdb_token, influxdb_org, influxdb_bucket)

        file_path = os.path.join('reports', 'netprovision_report.xlsx')
        export_to_excel(customers, device_list, deployments, file_path)
        print(f"Data exported successfully to {file_path}")

if __name__ == "__main__":
    main()
