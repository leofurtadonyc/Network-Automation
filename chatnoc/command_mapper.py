# command_mapper.py

COMMAND_MAP = {
    "show_interface_status": {
        "cisco": "show ip interface brief",
        "cisco_xe": "show ip interface brief",
        "juniper_junos": "show interfaces terse",
        "cisco_xr": "show interfaces brief",
        "huawei_vrp": "display interface brief",
        "nokia_sr": "show router interface"
    },
    "show_routing_table": {
        "cisco": "show ip route",
        "cisco_xe": "show ip route",
        "juniper_junos": "show route",
        "cisco_xr": "show route",
        "huawei_vrp": "display ip routing-table",
        "nokia_sr": "show router route"
    },
    # Add additional command mappings as needed
}

def get_command(intent, device_type):
    mapping = COMMAND_MAP.get(intent)
    if mapping:
        return mapping.get(device_type)
    return None

if __name__ == "__main__":
    # Example test
    print(get_command("show_interface_status", "juniper_junos"))
