#!/usr/bin/env python
import argparse
import yaml
import sys
import re

# Updated imports to match the new structure:
from executors import execute_command
from inventory import DeviceInventory

# ---------------------------
# Helper Functions
# ---------------------------
def normalize_interface_name(name, device_type=None):
    """
    Normalize an interface name:
      - Convert to lowercase and remove spaces.
      - For Cisco IOS XR, replace "gigabitethernet" with "gi".
      - For other Cisco devices, replace "ethernet" with "et".
    """
    norm = name.lower().replace(" ", "")
    if device_type == "cisco_xr":
        norm = norm.replace("gigabitethernet", "gi")
    else:
        norm = norm.replace("ethernet", "et")
    return norm

def normalize_junos_interface(name):
    """
    For Junos devices, convert to lowercase, remove spaces, and strip a trailing ".0" if present.
    For example, "ge-0/0/0.0" becomes "ge-0/0/0".
    """
    norm = name.lower().replace(" ", "")
    if norm.endswith(".0"):
        norm = norm[:-2]
    return norm

# ---------------------------
# Health Check Functions
# ---------------------------
def check_backbone_interfaces(device, baseline_interfaces):
    """
    Run the vendor-specific interface status command on the device and compare each
    backbone interface’s admin/operational status with the baseline.
    """
    # Select command based on vendor.
    if device.device_type in ["cisco", "cisco_xe", "cisco_xr"]:
        command = "show ip interface brief"
    elif device.device_type == "juniper_junos":
        command = "show interfaces terse"
    elif device.device_type == "huawei_vrp":
        command = "display interface brief"
    elif device.device_type == "nokia_sr":
        command = "show router interface brief"
    else:
        command = "show ip interface brief"
    
    output = execute_command(device, command)
    issues = []
    confirmations = []
    
    for iface in baseline_interfaces:
        iface_name = iface.get("interface")
        expected_admin = iface.get("admin_state", "").lower()
        expected_oper = iface.get("operational_state", "").lower()
        
        # Normalize baseline name based on vendor.
        if device.device_type == "juniper_junos":
            norm_baseline = normalize_junos_interface(iface_name)
        else:
            norm_baseline = normalize_interface_name(iface_name, device.device_type)
        
        matched_line = None
        for line in output.splitlines():
            if device.device_type == "juniper_junos":
                parts = re.split(r'\s+', line.strip())
                if len(parts) < 3:
                    continue
                current_iface = normalize_junos_interface(parts[0])
            else:
                current_iface = normalize_interface_name(line, device.device_type)
            
            if norm_baseline in current_iface:
                matched_line = line
                break
        
        if not matched_line:
            issues.append(f"Interface {iface_name} not found in output.")
            continue
        
        # Parse the line based on vendor.
        if device.device_type in ["cisco", "cisco_xe"]:
            parts = re.split(r'\s+', matched_line.strip())
            if len(parts) < 6:
                issues.append(f"Interface {iface_name}: unexpected output format: {matched_line}")
                continue
            actual_admin = parts[4].lower()
            actual_oper = parts[5].lower()
        elif device.device_type == "cisco_xr":
            parts = re.split(r'\s+', matched_line.strip())
            # IOS XR output has 5 columns: Interface, IP-Address, Status, Protocol, Vrf-Name.
            if len(parts) < 5:
                issues.append(f"Interface {iface_name}: unexpected output format: {matched_line}")
                continue
            actual_admin = parts[2].lower()  # Status
            actual_oper = parts[3].lower()   # Protocol
        elif device.device_type == "juniper_junos":
            parts = re.split(r'\s+', matched_line.strip())
            if len(parts) < 3:
                issues.append(f"Interface {iface_name}: unexpected output format: {matched_line}")
                continue
            actual_admin = parts[1].lower()
            actual_oper = parts[2].lower()
        else:
            # For Huawei and Nokia, do a substring search.
            actual_admin = matched_line.lower()
            actual_oper = matched_line.lower()
        
        if actual_admin != expected_admin or actual_oper != expected_oper:
            issues.append(f"Interface {iface_name}: expected {expected_admin}/{expected_oper} but got {actual_admin}/{actual_oper}.")
        else:
            confirmations.append(f"Interface {iface_name} is healthy: {actual_admin}/{actual_oper}.")
    return issues, confirmations

def check_ospf_adjacencies(device, baseline_interfaces):
    """
    Run the vendor-specific OSPF neighbor command and verify that each baseline
    backbone interface has an OSPF neighbor entry with state FULL.
    """
    if device.device_type in ["cisco", "cisco_xe", "cisco_xr"]:
        command = "show ip ospf neighbor"
    elif device.device_type == "juniper_junos":
        command = "show ospf neighbor"
    elif device.device_type == "huawei_vrp":
        command = "display ospf peer"
    elif device.device_type == "nokia_sr":
        command = "show router ospf neighbor"
    else:
        command = "show ip ospf neighbor"
    
    output = execute_command(device, command)
    issues = []
    confirmations = []
    
    lines = output.splitlines()
    neighbor_entries = []
    for line in lines:
        if ("Neighbor" in line and "Interface" in line) or not line.strip():
            continue
        neighbor_entries.append(line)
    
    for iface in baseline_interfaces:
        iface_name = iface.get("interface")
        expected_state = iface.get("ospf_adjacency", "full").lower()
        if device.device_type == "juniper_junos":
            norm_iface = normalize_junos_interface(iface_name)
        else:
            norm_iface = normalize_interface_name(iface_name, device.device_type)
        
        found = False
        for entry in neighbor_entries:
            parts = re.split(r'\s+', entry.strip())
            if device.device_type == "juniper_junos":
                if len(parts) < 3:
                    continue
                neighbor_interface = normalize_junos_interface(parts[1])
                neighbor_state = parts[2].lower()
            else:
                if len(parts) < 6:
                    continue
                neighbor_interface = normalize_interface_name(parts[-1], device.device_type)
                neighbor_state = parts[2].lower()
            if neighbor_interface == norm_iface:
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
    Run the vendor-specific LDP neighbor command and verify that each baseline
    backbone interface has an associated LDP session. Also, check for label bindings
    for the 100.65.255.0/24 prefix.
    """
    if device.device_type in ["cisco", "cisco_xe", "cisco_xr"]:
        command = "show mpls ldp neighbor"
        binding_command = "show mpls ldp binding | include 100.65.255."
    elif device.device_type == "juniper_junos":
        command = "show ldp neighbor"
        binding_command = "show ldp database | match 100.65.255."
    elif device.device_type == "huawei_vrp":
        command = "display mpls ldp neighbor"
        binding_command = "display mpls ldp binding | include 100.65.255."
    elif device.device_type == "nokia_sr":
        command = "show router mpls ldp neighbor"
        binding_command = "show router mpls ldp binding | include 100.65.255."
    else:
        command = "show mpls ldp neighbor"
        binding_command = "show mpls ldp binding | include 100.65.255."
    
    output = execute_command(device, command)
    issues = []
    confirmations = []
    
    for iface in baseline_interfaces:
        iface_name = iface.get("interface")
        if device.device_type == "juniper_junos":
            norm_iface = normalize_junos_interface(iface_name)
        else:
            norm_iface = normalize_interface_name(iface_name, device.device_type)
        if norm_iface in normalize_interface_name(output, device.device_type):
            confirmations.append(f"LDP session for interface {iface_name} appears established.")
        else:
            issues.append(f"LDP session for interface {iface_name} not found.")
    
    binding_output = execute_command(device, binding_command)
    if "100.65.255." not in binding_output:
        issues.append("No label bindings found for 100.65.255.0/24.")
    else:
        confirmations.append("Label bindings for 100.65.255.0/24 are present.")
    return issues, confirmations

def check_bgp_sessions(device, baseline_bgp):
    """
    Run the vendor-specific BGP summary command and verify that each expected BGP peer is present.
    """
    if device.device_type in ["cisco", "cisco_xe", "cisco_xr"]:
        command = "show ip bgp summary"
    elif device.device_type == "juniper_junos":
        command = "show bgp summary"
    elif device.device_type == "huawei_vrp":
        command = "display bgp peer"
    elif device.device_type == "nokia_sr":
        command = "show router bgp summary"
    else:
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
    Run all health-check functions for a device and aggregate the results.
    """
    results = {}
    # Backbone Interfaces
    issues, confirmations = check_backbone_interfaces(device, baseline_for_device.get("backbone_interfaces", []))
    results["backbone_interfaces"] = {"issues": issues, "confirmations": confirmations}
    
    # OSPF Adjacencies
    issues, confirmations = check_ospf_adjacencies(device, baseline_for_device.get("backbone_interfaces", []))
    results["ospf_adjacencies"] = {"issues": issues, "confirmations": confirmations}
    
    # LDP Sessions
    issues, confirmations = check_ldp_sessions(device, baseline_for_device.get("backbone_interfaces", []))
    results["ldp_sessions"] = {"issues": issues, "confirmations": confirmations}
    
    # BGP Sessions (if defined)
    if "bgp_peers" in baseline_for_device:
        issues, confirmations = check_bgp_sessions(device, baseline_for_device.get("bgp_peers", []))
        results["bgp_sessions"] = {"issues": issues, "confirmations": confirmations}
    else:
        results["bgp_sessions"] = {"issues": [], "confirmations": ["No BGP baseline defined; skipping BGP check."]}
    
    return results

def print_health_check_results(device_name, results):
    """
    Print the health check results for a device in a structured, detailed format.
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

def main():
    parser = argparse.ArgumentParser(description="Network Health Check Tool")
    parser.add_argument("target", help="Device name to health-check, or 'all' for all devices.")
    parser.add_argument("--baseline", default="baseline/healthcheck_baseline.yaml", help="Path to baseline YAML file.")
    args = parser.parse_args()
    
    try:
        with open(args.baseline, "r") as f:
            baseline_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading baseline file: {e}")
        sys.exit(1)
    
    inventory = DeviceInventory()
    
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
