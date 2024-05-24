import argparse
import yaml
from pymongo import MongoClient
from prettytable import PrettyTable

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

def get_customer_details(connection_string, database_name, customer_name=None):
    client = MongoClient(connection_string)
    db = client[database_name]
    customers_collection = db['customers']

    if customer_name:
        customer_data = customers_collection.find_one({"name": {"$regex": customer_name, "$options": "i"}})
        if not customer_data:
            print(f"Customer matching '{customer_name}' not found in MongoDB.")
            return None
        return [customer_data]
    else:
        return list(customers_collection.find({}))

def get_device_details(connection_string, database_name, device_names=None):
    client = MongoClient(connection_string)
    db = client[database_name]
    devices_collection = db['devices']

    if device_names:
        device_data_list = []
        for device_name in device_names:
            device_data = devices_collection.find_one({"device_name": device_name})
            if not device_data:
                print(f"Device {device_name} not found in MongoDB.")
            else:
                device_data_list.append(device_data)
        return device_data_list
    else:
        return list(devices_collection.find({}))

def display_customer_details(customer_data_list):
    for customer_data in customer_data_list:
        table = PrettyTable()
        table.field_names = ["Field", "Details"]
        table.align = "l"  # Justify left

        for key, value in customer_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        for sub_sub_key, sub_sub_value in sub_value.items():
                            if isinstance(sub_sub_value, dict):
                                for sub_sub_sub_key, sub_sub_sub_value in sub_sub_value.items():
                                    table.add_row([f"{key}.{sub_key}.{sub_sub_key}.{sub_sub_sub_key}", sub_sub_sub_value])
                            else:
                                table.add_row([f"{key}.{sub_key}.{sub_sub_key}", sub_sub_value])
                    else:
                        table.add_row([f"{key}.{sub_key}", sub_value])
            else:
                table.add_row([key, value])

        print("Customer Details:")
        print(table)

def display_device_details(device_data_list):
    for device_data in device_data_list:
        table = PrettyTable()
        table.field_names = ["Field", "Details"]
        table.align = "l"  # Justify left

        for key, value in device_data.items():
            table.add_row([key, value])

        print("Device Details:")
        print(table)

def main():
    settings = load_settings()
    data_source = settings.get('data_source')

    parser = argparse.ArgumentParser(description="Query MongoDB for customer or device details.")
    parser.add_argument("--customer", type=str, help="Customer name to query (partial name allowed) or 'all' to list all customers.")
    parser.add_argument("--device", type=str, action='append', help="Device name to query (can specify multiple) or 'all' to list all devices.")
    args = parser.parse_args()

    if not args.customer and not args.device:
        parser.print_help()
        return

    if data_source != 'mongodb':
        print("The system isn't connected to a MongoDB database based on the current settings. This script might not return the desired output.")
        return

    connection_string = settings['mongodb_connection']['uri']
    database_name = settings['mongodb_connection']['database_name']

    if args.customer:
        if args.customer.lower() == 'all':
            customer_data_list = get_customer_details(connection_string, database_name)
        else:
            customer_data_list = get_customer_details(connection_string, database_name, args.customer)
        if customer_data_list:
            display_customer_details(customer_data_list)

    if args.device:
        if 'all' in [device.lower() for device in args.device]:
            device_data_list = get_device_details(connection_string, database_name)
        else:
            device_data_list = get_device_details(connection_string, database_name, args.device)
        if device_data_list:
            display_device_details(device_data_list)

if __name__ == "__main__":
    main()
