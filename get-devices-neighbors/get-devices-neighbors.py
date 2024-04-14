# This is a simple script that captures structured data, such as LLDP neighbors, OSPF adjacencies, BGP sessions, and ARP tables from network devices in a lab topology in EVE-NG.
# Run this directly from the EVE-NG host. This allows you to connect directly using inband IP addresses, making it easier.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import os
import datetime
import time
from napalm import get_network_driver
from tabulate import tabulate
import networkx as nx
from asciinet import graph_to_ascii

def print_banner(title):
    banner_length = len(title) + 4
    print('*' * banner_length)
    print(f"* {title} *")
    print('*' * banner_length)
    print('')

def print_ospf_neighbors(device_name, output):
    print_banner(f"OSPF adjacencies to {device_name}")
    print(output)
    print('')

def print_bgp_neighbors(device_name, bgp_data):
    print_banner(f"BGP neighbors to {device_name}")
    for peer, details in bgp_data['global']['peers'].items():
        print(f"Neighbor: {peer} | Uptime: {details['uptime']} | Received prefixes: {details.get('received_prefixes', 'N/A')}")
    print('')

def print_lldp_neighbors(device_name, lldp_data):
    print_banner(f"LLDP neighbors to {device_name}")
    for interface, neighbors in lldp_data.items():
        for neighbor in neighbors:
            print(f"Interface: {interface}, Neighbor: {neighbor['hostname']}, Interface: {neighbor['port']}")
    print('')

def print_arp_table(device_name, arp_data):
    print_banner(f"ARP table to {device_name}")
    for entry in arp_data:
        print(f"Interface: {entry['interface']}, MAC address: {entry['mac']}, IP address: {entry['ip']}")
    print('')

def generate_ascii_graph(lldp_data):
    G = nx.Graph()

    for device, neighbors in lldp_data.items():
        for interface, neighbor_list in neighbors.items():
            for neighbor in neighbor_list:
                node_a = f"{device} ({interface})"
                node_b = f"{neighbor['hostname']} ({neighbor['port']})"
                G.add_edge(node_a, node_b)

    ascii_output = graph_to_ascii(G)
    return ascii_output

start_time = time.time()

operator_username = os.getlogin()

current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

devices = [
    {'name': 'ISP-2', 'host': '172.31.255.201', 'type': 'ios'},
    {'name': 'ISP-1', 'host': '172.31.255.202', 'type': 'ios'},
    {'name': 'Junos', 'host': '172.31.255.203', 'type': 'junos'},
    {'name': 'PE-ASR9K', 'host': '172.31.255.204', 'type': 'iosxr'},
]

print_banner("NETWORK ROUTING NEIGHBORS REPORT")

for device in devices:
    driver = get_network_driver(device['type'])
    active_device = driver(device['host'], 'operador', 'Juniper')
    active_device.open()

    # Get LLDP neighbors and print
    lldp_neighbors = active_device.get_lldp_neighbors()
    print_lldp_neighbors(device['name'], lldp_neighbors)

    # Get ARP table and print
    arp_table = active_device.get_arp_table()
    print_arp_table(device['name'], arp_table)

    # Get OSPF neighbors and print
    if device['type'] == 'ios':
        ospf_output = active_device.cli(["show ip ospf neighbor"])
        print_ospf_neighbors(device['name'], ospf_output['show ip ospf neighbor'])
    elif device['type'] in ['junos', 'iosxr']:
        ospf_output = active_device.cli(["show ospf neighbor"])
        print_ospf_neighbors(device['name'], ospf_output["show ospf neighbor"])

    # Get BGP neighbors and print
    bgp_neighbors = active_device.get_bgp_neighbors()
    print_bgp_neighbors(device['name'], bgp_neighbors)

    active_device.close()

# Calculate and print the script execution time
end_time = time.time()
execution_time = round(end_time - start_time, 2)

def display_table_with_textfsm(data, headers):
    """
    Displays the data in table format using TextFSM and tabulate.
    """
    table_data = []
    for entry in data:
        table_data.append([entry.get(header, 'N/A') for header in headers])
    print(tabulate(table_data, headers=headers))
    print("\n")

print("\nFormatted outputs from TextFSM:")
print_banner("ARP Tables")
for device in devices:
    driver = get_network_driver(device['type'])
    active_device = driver(device['host'], 'operador', 'Juniper')
    active_device.open()
    arp_table = active_device.get_arp_table()
    active_device.close()
    
    print_banner(f"ARP Table to {device['name']}")
    display_table_with_textfsm(arp_table, ["interface", "mac", "ip"])

lldp_all_data = {}
for device in devices:
    driver = get_network_driver(device['type'])
    active_device = driver(device['host'], 'operador', 'Juniper')
    active_device.open()
    lldp_neighbors = active_device.get_lldp_neighbors()
    lldp_all_data[device['name']] = lldp_neighbors
    active_device.close()

print_banner("Graphical View of LLDP Neighbors")
print(generate_ascii_graph(lldp_all_data))

print_banner("Execution Details")
print(f"Operator: {operator_username}")
print(f"Execution Date and Time: {current_datetime}")
print(f"Total Time of Execution: {execution_time} seconds")