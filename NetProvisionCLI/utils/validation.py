import ipaddress
import argparse
import re

def valid_ip_irb(network):
    """Validate an IP network prefix and return the first usable IP address with the prefix."""
    try:
        network_obj = ipaddress.ip_network(network, strict=False)
        first_usable_ip = next(network_obj.hosts())
        return f"{first_usable_ip}/{network_obj.prefixlen}"
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid IP network: {network}. Error: {e}")

def valid_ip_nexthop(address):
    """Validate an IP address."""
    try:
        ip_obj = ipaddress.ip_address(address)
        return str(ip_obj)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {address}")
    
def valid_ip_lan(network):
    """Validate an IP network prefix."""
    try:
        network_obj = ipaddress.ip_network(network, strict=False)
        return str(network_obj)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP network: {network}")

def interface_allowed(device_info, interface_name):
    """Check if the specified interface is allowed based on forbidden ranges in the device configuration."""
    forbidden_patterns = device_info.get('forbidden_interfaces', [])
    for pattern in forbidden_patterns:
        if re.match(pattern, interface_name):
            return False
    return True
