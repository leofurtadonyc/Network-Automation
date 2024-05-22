import os
import yaml
from pymongo import MongoClient
from config.load_settings import load_settings

def load_yaml(yaml_path: str) -> tuple:
    """Load device data from a YAML file."""
    try:
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
            return data['devices'], None, None
    except FileNotFoundError:
        print(f"YAML file {yaml_path} not found.")
        return {}, None, None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {yaml_path}: {e}")
        return {}, None, None

def load_mongodb(connection_string: str, database_name: str, customer_name: str) -> tuple:
    """Load device data from a MongoDB collection."""
    try:
        client = MongoClient(connection_string)
        db = client[database_name]
        customers_collection = db['customers']
        devices_collection = db['devices']
        
        customer_data = customers_collection.find_one({"name": customer_name})
        if not customer_data:
            print(f"Customer {customer_name} not found in MongoDB.")
            return {}, {}, {}

        access_device_name = customer_data['customer_details']['devices']['access']['name']
        pe_device_name = customer_data['customer_details']['devices']['pe']['name']
        
        access_device_info = devices_collection.find_one({"device_name": access_device_name})
        pe_device_info = devices_collection.find_one({"device_name": pe_device_name})

        return customer_data, access_device_info, pe_device_info
    except Exception as e:
        print(f"Error loading data from MongoDB: {e}")
        return {}, {}, {}

def load_devices(source: str, customer_name: str = None) -> tuple:
    """Load device data from the specified source (yaml or mongodb)."""
    if source == 'yaml':
        return load_yaml('devices/network_devices.yaml')
    elif source == 'mongodb':
        settings = load_settings()
        conn_string = settings['mongodb_connection']['uri']
        db_name = settings['mongodb_connection']['database_name']
        return load_mongodb(conn_string, db_name, customer_name)
    else:
        return {}, {}, f"Unsupported source: {source}"

def load_recipe(recipe_path: str) -> dict:
    """Load recipe data from a YAML or JSON file."""
    try:
        with open(recipe_path, 'r') as file:
            if recipe_path.endswith('.yaml') or recipe_path.endswith('.yml'):
                return yaml.safe_load(file)
            elif recipe_path.endswith('.json'):
                import json
                return json.load(file)
            else:
                raise ValueError("Unsupported file format. Use .yaml, .yml, or .json")
    except Exception as e:
        print(f"Error loading recipe file {recipe_path}: {e}")
        return {}
