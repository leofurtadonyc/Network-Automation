# db/mongo_utils.py
from pymongo import MongoClient

def get_mongo_client():
    """Establish and return a MongoDB client connection."""
    return MongoClient('mongodb://localhost:27017/')

def load_customer_and_device_info(customer_name, access_device, pe_device):
    """Load customer and device information from MongoDB."""
    client = get_mongo_client()
    db = client.netprovision
    
    customer_info = db.customers.find_one({'name': customer_name})
    access_device_info = db.devices.find_one({'name': access_device})
    pe_device_info = db.devices.find_one({'name': pe_device})
    
    return customer_info, access_device_info, pe_device_info
