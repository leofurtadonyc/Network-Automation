from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client.netprovision

# Creating collections
customers_collection = db.customers
devices_collection = db.devices

# Example data
customers_collection.insert_one({
    "name": "LEONARDOFURTADO",
    "customer_details": {
        "email": "leonardo@example.com",
        "devices": {
            "access": {
                "name": "a-cisco-01",
                "interface": "GigabitEthernet1",
            },
            "pe": {
                "name": "pe-juniper-01",
            }
        },
        "service_details": {
            "circuit_id": 20,
            "qos_input": 500,
            "qos_output": 500,
            "vlan_id": 20,
            "vlan_id_outer": 600,
            "pw_id": 20,
            "irb_ipaddr": "172.16.1.1/30",
            "irb_ipv6addr": "2001:db8:1234:1234::1/127",
            "ipv4_lan": "172.17.0.0/16",
            "ipv4_nexthop": "172.16.1.2",
            "ipv6_lan": "2001:db8:2222::/48",
            "ipv6_nexthop": "2001:db8:1234:1234::2",
        }
    }
})

devices_collection.insert_many([
    {
        "device_name": "a-cisco-01",
        "device_type": "cisco_xe",
        "device_role": "access",
        "ip_address": "192.168.255.11",
        "loopback": "10.255.255.1",
        "customer_provisioning": True,
        "forbidden_interfaces": ["^GigabitEthernet[2-4]$", "^Loopback[0-9999]$"],
    },
    {
        "device_name": "pe-juniper-01",
        "device_type": "juniper_junos",
        "device_role": "pe",
        "ip_address": "192.168.255.15",
        "loopback": "10.255.255.5",
        "customer_provisioning": True,
    }
])

print("Data insertion completed successfully.")