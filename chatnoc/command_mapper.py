# command_mapper.py

COMMAND_MAP = {
    "show_interfaces_down": {
        "cisco": "show ip interface brief | include down",
        "cisco_xe": "show ip interface brief | include down",
        "juniper_junos": "show interfaces terse | match down",
        "cisco_xr": "show interfaces brief | include down",
        "huawei_vrp": "display interface | include down",
        "nokia_sr": "show router interface brief | include down"
    },
    "get_mgmt_ip": {
        "cisco": "show ip interface brief | include Management",
        "cisco_xe": "show ip interface brief | include Management",
        "juniper_junos": "show interfaces terse | match mgmt",
        "cisco_xr": "show interfaces brief | include Management",
        "huawei_vrp": "display interface | include Management",
        "nokia_sr": "show router interface brief | include Management"
    },
    "show_ospf_routes_count": {
        "cisco": "show ip ospf route",
        "cisco_xe": "show ip ospf route",
        "juniper_junos": "show route protocol ospf",
        "cisco_xr": "show ospf route",
        "huawei_vrp": "display ospf routing-table",
        "nokia_sr": "show router ospf route"
    },
    "check_route": {
        "cisco": "show ip route {destination_ip}",
        "cisco_xe": "show ip route {destination_ip}",
        "juniper_junos": "show route {destination_ip}",
        "cisco_xr": "show route {destination_ip}",
        "huawei_vrp": "display ip routing-table | include {destination_ip}",
        "nokia_sr": "show router route {destination_ip}"
    },
    "show_uptime": {
        "cisco": "show version | include uptime",
        "cisco_xe": "show version | include uptime",
        "juniper_junos": "show system uptime",
        "cisco_xr": "show version | include uptime",
        "huawei_vrp": "display version | include uptime",
        "nokia_sr": "show system uptime"
    },
    "show_ospf_neighbors_full": {
        "cisco": "show ip ospf neighbor | include FULL",
        "cisco_xe": "show ip ospf neighbor | include FULL",
        "juniper_junos": "show ospf neighbor | match FULL",
        "cisco_xr": "show ip ospf neighbor | include FULL",
        "huawei_vrp": "display ospf peer | include FULL",
        "nokia_sr": "show router ospf neighbor | include FULL"
    },
    "ping": {
        "cisco": "ping {destination_ip} source {source_ip}",
        "cisco_xe": "ping {destination_ip} source {source_ip}",
        "juniper_junos": "ping {destination_ip} source {source_ip}",
        "cisco_xr": "ping {destination_ip} source {source_ip}",
        "huawei_vrp": "ping {destination_ip} source {source_ip}",
        "nokia_sr": "ping source {source_ip} {destination_ip}"
    },
    "traceroute": {
        "cisco": "traceroute {destination_ip} source {source_ip}",
        "cisco_xe": "traceroute {destination_ip} source {source_ip}",
        "juniper_junos": "traceroute {destination_ip} source {source_ip}",
        "cisco_xr": "traceroute {destination_ip} source {source_ip}",
        "huawei_vrp": "traceroute {destination_ip} source {source_ip}",
        "nokia_sr": "traceroute source {source_ip} {destination_ip}"
    }
}

def get_command(action, device_type, **kwargs):
    mapping = COMMAND_MAP.get(action)
    if mapping:
        cmd_template = mapping.get(device_type)
        if cmd_template:
            try:
                return cmd_template.format(**kwargs)
            except KeyError:
                # A required parameter is missing.
                return None
    return None

if __name__ == "__main__":
    # Example tests:
    print(get_command("ping", "cisco", destination_ip="100.65.255.14", source_ip="100.65.255.1"))
    print(get_command("traceroute", "nokia_sr", destination_ip="100.65.255.14", source_ip="100.65.255.1"))
