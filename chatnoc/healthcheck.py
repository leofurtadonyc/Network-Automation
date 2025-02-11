#!/usr/bin/env python
import argparse
import yaml
import sys
import re

# Import your project modules.
from netmiko_executor import execute_command
from devices_inventory import DeviceInventory

# ---------------------------
# Helper Functions
# ---------------------------
def normalize_interface_name(name):
    """
    Normalize an interface name by:
      - Converting to lowercase.
      - Removing spaces.
      - Replacing "ethernet" with "et".
    This converts "Ethernet 0/0" into "et0/0", which should match abbreviations like "Et0/0" or "Ethernet0/0".
    """
    norm = name.lower().replace(" ", "")
    norm = norm.replace("ethernet", "et")
    return norm

# ---------------------------
# Health Check Functions
# ---------------------------
def check_backbone_interfaces(device, baseline_interfaces):
    """
    Run "show ip interface brief" on the device and compare each backbone interface’s admin/operational status
    with the baseline. Uses normalization for interface name matching.
    """
    command = "show ip interface brief"
    output = execute_command(device, command)
    issues = []
    confirmations = []
    
    for iface in baseline_interfaces:
        iface_name = iface.get("interface")
        expected_admin = iface.get("admin_state").lower()
        expected_oper = iface.get("operational_state").lower()
        norm_baseline = normalize_interface_name(iface_name)
        
        matched_line = None
        for line in output.splitlines():
            # Normalize the entire line and check if the baseline interface appears.
            if norm_baseline in normalize_interface_name(line):
                matched_line = line
                break
        if not matched_line:
            issues.append(f"Interface {iface_name} not found in output.")
            continue
        
        # Parse the line. (Adjust indices according to your device’s actual format.)
        parts = re.split(r'\s+', matched_line.strip())
        if len(parts) < 6:
            issues.append(f"Interface {iface_name}: unexpected output format: {matched_line}")
            continue
        actual_admin = parts[4].lower()
        actual_oper = parts[5].lower()
        if actual_admin != expected_admin or actual_oper != expected_oper:
            issues.append(f"Interface {iface_name}: expected {expected_admin}/{expected_oper} but got {actual_admin}/{actual_oper}.")
        else:
            confirmations.append(f"Interface {iface_name} is healthy: {actual_admin}/{actual_oper}.")
    return issues, confirmations

def check_ospf_adjacencies(device, baseline_interfaces):
    """
    Run "show ip ospf neighbor" on the device and verify that for each backbone interface
    defined in the baseline there is an OSPF neighbor entry whose interface (normalized) matches
    the baseline interface and whose state is FULL.
    """
    command = "show ip ospf neighbor"
    output = execute_command(device, command)
    issues = []
    confirmations = []
    
    # Split output into lines and ignore header lines.
    lines = output.splitlines()
    neighbor_entries = []
    for line in lines:
        # Skip header lines (we assume they contain "Neighbor" and "Interface")
        if "Neighbor" in line and "Interface" in line:
            continue
        if line.strip() == "":
            continue
        neighbor_entries.append(line)
    
    for iface in baseline_interfaces:
        iface_name = iface.get("interface")
        expected_state = iface.get("ospf_adjacency", "full").lower()  # expecting "full"
        norm_iface = normalize_interface_name(iface_name)
        
        found = False
        for entry in neighbor_entries:
            # The typical OSPF neighbor output columns are:
            # Neighbor ID, Pri, State, Dead Time, Address, Interface
            parts = re.split(r'\s+', entry.strip())
            if len(parts) < 6:
                continue  # skip if the format is not as expected
            neighbor_interface = parts[-1]
            normalized_neighbor_interface = normalize_interface_name(neighbor_interface)
            neighbor_state = parts[2].lower()  # this may be "full/" or "full"
            if normalized_neighbor_interface == norm_iface:
                found = True
                if neighbor_state.startswith("full"):
                    confirmations.append(f"OSPF adjacency on {iface_name} is FULL.")
                else:
                    issues.append(f"OSPF adjacency on {iface_name} is not FULL (state: {neighbor_state}).")
                break
        if not found:
            issues.append(f"No OSPF neighbor entry found for interface {iface_name}.")
    
    return issues, confirmations


def check_ldp_sessions(device, baseline_interfaces):
    """
    Run "show mpls ldp neighbor" and verify for each baseline backbone interface that its
    normalized interface name appears in the LDP discovery sources section, indicating an established session.
    Also check for label bindings for 100.65.255.0/24.
    """
    command = "show mpls ldp neighbor"
    output = execute_command(device, command)
    issues = []
    confirmations = []
    # Process the LDP neighbor output as text.
    for iface in baseline_interfaces:
        iface_name = iface.get("interface")
        norm_iface = normalize_interface_name(iface_name)
        # Search for the normalized interface name in the output.
        if norm_iface in normalize_interface_name(output):
            confirmations.append(f"LDP session for interface {iface_name} appears established.")
        else:
            issues.append(f"LDP session for interface {iface_name} not found.")
    
    # Check for label bindings in the 100.65.255.0/24 range.
    command_binding = "show mpls ldp binding | include 100.65.255."
    binding_output = execute_command(device, command_binding)
    if "100.65.255." not in binding_output:
        issues.append("No label bindings found for 100.65.255.0/24.")
    else:
        confirmations.append("Label bindings for 100.65.255.0/24 are present.")
    return issues, confirmations

def check_bgp_sessions(device, baseline_bgp):
    """
    Run "show ip bgp summary" and verify that each expected BGP peer from the baseline appears.
    Instead of looking for the literal word "established," we simply check for the peer's IP.
    """
    command = "show ip bgp summary"
    output = execute_command(device, command)
    issues = []
    confirmations = []
    for peer in baseline_bgp:
        if peer.lower() in output.lower():
            confirmations.append(f"BGP session with {peer} is present.")
        else:
            issues.append(f"BGP session with {peer} is not present.")
    return issues, confirmations

def run_health_check_for_device(device, baseline_for_device):
    """
    Run all health-check functions for a device and collect the results.
    """
    results = {}
    # Check backbone interfaces.
    issues, confirmations = check_backbone_interfaces(device, baseline_for_device.get("backbone_interfaces", []))
    results["backbone_interfaces"] = {"issues": issues, "confirmations": confirmations}
    
    # Check OSPF adjacencies using interface descriptions.
    issues, confirmations = check_ospf_adjacencies(device, baseline_for_device.get("backbone_interfaces", []))
    results["ospf_adjacencies"] = {"issues": issues, "confirmations": confirmations}
    
    # Check LDP sessions.
    issues, confirmations = check_ldp_sessions(device, baseline_for_device.get("backbone_interfaces", []))
    results["ldp_sessions"] = {"issues": issues, "confirmations": confirmations}
    
    # Check BGP sessions if defined.
    if "bgp_peers" in baseline_for_device:
        issues, confirmations = check_bgp_sessions(device, baseline_for_device.get("bgp_peers", []))
        results["bgp_sessions"] = {"issues": issues, "confirmations": confirmations}
    else:
        results["bgp_sessions"] = {"issues": [], "confirmations": ["No BGP baseline defined; skipping BGP check."]}
    
    return results

def print_health_check_results(device_name, results):
    """
    Print the health check results for a device.
    """
    print(f"\nHealth Check Results for {device_name}:")
    for section, data in results.items():
        print(f"\n== {section.upper()} ==")
        if data["confirmations"]:
            print("Confirmations:")
            for confirmation in data["confirmations"]:
                print(f"  - {confirmation}")
        if data["issues"]:
            print("Issues:")
            for issue in data["issues"]:
                print(f"  - {issue}")
        if not data["issues"] and not data["confirmations"]:
            print("No data available.")

# ---------------------------
# Main Script Entry Point
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Network Health Check Tool")
    parser.add_argument("target", help="Device name to health-check, or 'all' for all devices.")
    parser.add_argument("--baseline", default="healthcheck_baseline.yaml", help="Path to baseline YAML file.")
    args = parser.parse_args()
    
    # Load the baseline YAML file.
    try:
        with open(args.baseline, "r") as f:
            baseline_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading baseline file: {e}")
        sys.exit(1)
    
    # Get the device inventory.
    inventory = DeviceInventory()
    
    # Determine which devices to check.
    devices_to_check = []
    if args.target.lower() == "all":
        for dev in baseline_data:
            device_obj = inventory.get_device_by_name(dev)
            if device_obj:
                devices_to_check.append(device_obj)
            else:
                print(f"Warning: Device '{dev}' defined in baseline not found in inventory.")
    else:
        device_obj = inventory.get_device_by_name(args.target)
        if not device_obj:
            print(f"Device '{args.target}' not found in inventory.")
            sys.exit(1)
        devices_to_check.append(device_obj)
    
    # Run health check for each device.
    for device in devices_to_check:
        baseline_for_device = baseline_data.get(device.name)
        if not baseline_for_device:
            print(f"No baseline defined for device '{device.name}'. Skipping health check for this device.")
            continue
        print(f"\nPerforming health check on device {device.name} ({device.mgmt_address})...")
        results = run_health_check_for_device(device, baseline_for_device)
        print_health_check_results(device.name, results)

if __name__ == "__main__":
    main()
