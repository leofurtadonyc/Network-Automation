import argparse
import yaml
import json
import getpass
from pymongo import MongoClient
from prettytable import PrettyTable
import bcrypt
import glob
import ipaddress

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

def authenticate_user(username, password=None):
    """Authenticate user using stored credentials."""
    if password is None:
        password = getpass.getpass(prompt='Password: ')

    try:
        with open('devices/usercredentials.sec', 'r') as file:
            credentials = file.readlines()
            for line in credentials:
                stored_username, hashed_password = line.strip().split(':')
                if stored_username == username:
                    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                        print("Authentication successful.")
                        return True
                    else:
                        print("Authentication failed.")
                        return False
            print("Username not found.")
            return False
    except FileNotFoundError:
        print("usercredentials.sec file not found.")
        return False

def validate_and_transform_customer_data(customer_data):
    """Validate and transform customer data to match the required structure."""
    transformed_data = {
        "name": customer_data["name"],
        "service_type": customer_data.get("service_type", ""),
        "customer_details": {
            "devices": {
                "access": {
                    "name": customer_data["devices"]["access"]["name"],
                    "interface": customer_data["devices"]["access"]["interface"]
                },
                "pe": {
                    "name": customer_data["devices"]["pe"]["name"]
                }
            },
            "service_details": {
                "circuit_id": customer_data["configuration"]["circuit_id"],
                "qos_input": customer_data["configuration"]["qos"]["input"],
                "qos_output": customer_data["configuration"]["qos"]["output"],
                "vlan_id": customer_data["configuration"]["vlan"]["id"],
                "vlan_id_outer": customer_data["configuration"]["vlan"].get("outer_id", None),
                "pw_id": customer_data["configuration"]["pseudowire_id"],
                "irb_ipaddr": customer_data["configuration"]["irb"]["ipv4_address"],
                "irb_ipv6addr": customer_data["configuration"]["irb"]["ipv6_address"],
                "ipv4_lan": customer_data["configuration"]["lan"]["ipv4"]["network"],
                "ipv4_nexthop": customer_data["configuration"]["lan"]["ipv4"]["next_hop"],
                "ipv6_lan": customer_data["configuration"]["lan"]["ipv6"]["network"],
                "ipv6_nexthop": customer_data["configuration"]["lan"]["ipv6"]["next_hop"]
            }
        }
    }
    return transformed_data

def check_for_conflicts(customers_collection, customer_data):
    """Check for conflicts in VLAN ID, Pseudowire ID, Circuit ID, IRB IP addresses, and customer LAN routes."""
    service_details = customer_data['customer_details']['service_details']
    devices = customer_data['customer_details']['devices']

    # Check VLAN ID
    vlan_id_conflict = customers_collection.find_one({
        'customer_details.service_details.vlan_id': service_details['vlan_id'],
        'customer_details.devices.access.name': devices['access']['name'],
        'customer_details.devices.access.interface': devices['access']['interface'],
        'name': {'$ne': customer_data['name']}
    })
    if vlan_id_conflict:
        return f"Conflict: VLAN ID {service_details['vlan_id']} on {devices['access']['name']} {devices['access']['interface']} is already in use by customer {vlan_id_conflict['name']}."

    # Check Pseudowire ID
    pw_id_conflict = customers_collection.find_one({
        '$or': [
            {'customer_details.devices.access.name': devices['access']['name']},
            {'customer_details.devices.pe.name': devices['pe']['name']}
        ],
        'customer_details.service_details.pw_id': service_details['pw_id'],
        'name': {'$ne': customer_data['name']}
    })
    if pw_id_conflict:
        return f"Conflict: Pseudowire ID {service_details['pw_id']} is already in use by customer {pw_id_conflict['name']} on access device {pw_id_conflict['customer_details']['devices']['access']['name']} or PE device {pw_id_conflict['customer_details']['devices']['pe']['name']}."

    # Check Circuit ID
    circuit_id_conflict = customers_collection.find_one({
        'customer_details.service_details.circuit_id': service_details['circuit_id'],
        'customer_details.devices.access.name': devices['access']['name'],
        'customer_details.devices.access.interface': devices['access']['interface'],
        'name': {'$ne': customer_data['name']}
    })
    if circuit_id_conflict:
        return f"Conflict: Circuit ID {service_details['circuit_id']} on {devices['access']['name']} {devices['access']['interface']} is already in use by customer {circuit_id_conflict['name']}."

    # Check IRB IPv4 address
    irb_ipv4_conflicts = customers_collection.find({
        'customer_details.service_details.irb_ipaddr': {'$exists': True},
        'name': {'$ne': customer_data['name']}
    })
    for conflict in irb_ipv4_conflicts:
        existing_network = ipaddress.ip_network(conflict['customer_details']['service_details']['irb_ipaddr'], strict=False)
        new_network = ipaddress.ip_network(service_details['irb_ipaddr'], strict=False)
        if new_network.overlaps(existing_network):
            if new_network == existing_network:
                return f"Conflict: IRB IPv4 address {service_details['irb_ipaddr']} is already in use by customer {conflict['name']}."
            else:
                return f"Conflict: IRB IPv4 prefix {service_details['irb_ipaddr']} overlaps with {conflict['customer_details']['service_details']['irb_ipaddr']} owned by customer {conflict['name']}."

    # Check IRB IPv6 address
    irb_ipv6_conflicts = customers_collection.find({
        'customer_details.service_details.irb_ipv6addr': {'$exists': True},
        'name': {'$ne': customer_data['name']}
    })
    for conflict in irb_ipv6_conflicts:
        existing_network = ipaddress.ip_network(conflict['customer_details']['service_details']['irb_ipv6addr'], strict=False)
        new_network = ipaddress.ip_network(service_details['irb_ipv6addr'], strict=False)
        if new_network.overlaps(existing_network):
            if new_network == existing_network:
                return f"Conflict: IRB IPv6 address {service_details['irb_ipv6addr']} is already in use by customer {conflict['name']}."
            else:
                return f"Conflict: IRB IPv6 prefix {service_details['irb_ipv6addr']} overlaps with {conflict['customer_details']['service_details']['irb_ipv6addr']} owned by customer {conflict['name']}."

    # Check IPv4 LAN route
    ipv4_lan_conflicts = customers_collection.find({
        'customer_details.service_details.ipv4_lan': {'$exists': True},
        'name': {'$ne': customer_data['name']}
    })
    for conflict in ipv4_lan_conflicts:
        existing_network = ipaddress.ip_network(conflict['customer_details']['service_details']['ipv4_lan'], strict=False)
        new_network = ipaddress.ip_network(service_details['ipv4_lan'], strict=False)
        if new_network.overlaps(existing_network):
            if new_network == existing_network:
                return f"Conflict: IPv4 LAN route {service_details['ipv4_lan']} is already in use by customer {conflict['name']}."
            else:
                return f"Conflict: IPv4 LAN prefix {service_details['ipv4_lan']} overlaps with {conflict['customer_details']['service_details']['ipv4_lan']} owned by customer {conflict['name']}."

    # Check IPv6 LAN route
    ipv6_lan_conflicts = customers_collection.find({
        'customer_details.service_details.ipv6_lan': {'$exists': True},
        'name': {'$ne': customer_data['name']}
    })
    for conflict in ipv6_lan_conflicts:
        existing_network = ipaddress.ip_network(conflict['customer_details']['service_details']['ipv6_lan'], strict=False)
        new_network = ipaddress.ip_network(service_details['ipv6_lan'], strict=False)
        if new_network.overlaps(existing_network):
            if new_network == existing_network:
                return f"Conflict: IPv6 LAN route {service_details['ipv6_lan']} is already in use by customer {conflict['name']}."
            else:
                return f"Conflict: IPv6 LAN prefix {service_details['ipv6_lan']} overlaps with {conflict['customer_details']['service_details']['ipv6_lan']} owned by customer {conflict['name']}."

    return None

def add_or_update_customer(connection_string, database_name, recipe_file):
    if recipe_file.endswith('.yaml') or recipe_file.endswith('.yml'):
        with open(recipe_file, 'r') as file:
            customer_data = yaml.safe_load(file)['customer']
    elif recipe_file.endswith('.json'):
        with open(recipe_file, 'r') as file:
            customer_data = json.load(file)['customer']
    else:
        raise ValueError("Unsupported file format. Use .yaml, .yml, or .json")

    customer_data = validate_and_transform_customer_data(customer_data)

    client = MongoClient(connection_string)
    db = client[database_name]
    customers_collection = db['customers']

    conflict_message = check_for_conflicts(customers_collection, customer_data)
    if conflict_message:
        print(conflict_message)
        return

    result = customers_collection.update_one(
        {'name': customer_data['name']},
        {'$set': customer_data},
        upsert=True
    )

    if result.upserted_id:
        print(f"Customer {customer_data['name']} added.")
    else:
        print(f"Customer {customer_data['name']} updated.")

def remove_customer(connection_string, database_name, customer_name):
    client = MongoClient(connection_string)
    db = client[database_name]
    customers_collection = db['customers']

    result = customers_collection.delete_one({'name': customer_name})
    if result.deleted_count > 0:
        print(f"Customer {customer_name} removed.")
    else:
        print(f"Customer {customer_name} not found.")

def add_or_update_device(connection_string, database_name, device_file):
    if device_file.endswith('.yaml') or device_file.endswith('.yml'):
        with open(device_file, 'r') as file:
            device_data = yaml.safe_load(file)['devices']
    elif device_file.endswith('.json'):
        with open(device_file, 'r') as file:
            device_data = json.load(file)['devices']
    else:
        raise ValueError("Unsupported file format. Use .yaml, .yml, or .json")

    client = MongoClient(connection_string)
    db = client[database_name]
    devices_collection = db['devices']

    for device_name, device_details in device_data.items():
        result = devices_collection.update_one(
            {'device_name': device_name},
            {'$set': device_details},
            upsert=True
        )
        if result.upserted_id:
            print(f"Device {device_name} added.")
        else:
            print(f"Device {device_name} updated.")

def remove_device(connection_string, database_name, device_name):
    client = MongoClient(connection_string)
    db = client[database_name]
    devices_collection = db['devices']

    result = devices_collection.delete_one({'device_name': device_name})
    if result.deleted_count > 0:
        print(f"Device {device_name} removed.")
    else:
        print(f"Device {device_name} not found.")

def main():
    settings = load_settings()
    data_source = settings.get('data_source')

    if data_source != 'mongodb':
        print("The system isn't connected to a MongoDB database based on the current settings. This script might not return the desired output.")
        return

    connection_string = settings['mongodb_connection']['uri']
    database_name = settings['mongodb_connection']['database_name']

    parser = argparse.ArgumentParser(description="Manage MongoDB entries for customers and devices.")
    parser.add_argument("--username", type=str, required=True, help="Username for authentication.")
    parser.add_argument("--password", type=str, help="Password for authentication.")
    parser.add_argument("--recipe", type=str, nargs='*', help="Paths to YAML or JSON files containing the customer recipes (can use globs).")
    parser.add_argument("--device", type=str, action='append', help="Path to a YAML or JSON file containing the device details (can specify multiple).")
    parser.add_argument("--remove", action='store_true', help="Flag to remove a customer or device.")
    parser.add_argument("--customer", type=str, help="Customer name to query, add, or remove.")
    args = parser.parse_args()

    if args.password:
        authenticated = authenticate_user(args.username, args.password)
    else:
        authenticated = authenticate_user(args.username)

    if not authenticated:
        return

    if args.recipe:
        for recipe_pattern in args.recipe:
            recipe_files = glob.glob(recipe_pattern)
            for recipe_file in recipe_files:
                add_or_update_customer(connection_string, database_name, recipe_file)

    if args.customer and args.remove:
        remove_customer(connection_string, database_name, args.customer)

    if args.device:
        for device_file in args.device:
            add_or_update_device(connection_string, database_name, device_file)

    if args.device and args.remove:
        for device_name in args.device:
            remove_device(connection_string, database_name, device_name)

if __name__ == "__main__":
    main()
