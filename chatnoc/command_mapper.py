# command_mapper.py

def get_command(action, device_type, **kwargs):
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
            "cisco": "show ip vrf interfaces",
            "cisco_xe": "show ip vrf interfaces",
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
            "huawei_vrp": "display ospf routing",
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
            "cisco_xr": "show ospf neighbor | include FULL",
            "huawei_vrp": "display ospf peer | include FULL",
            "nokia_sr": "show router ospf neighbor | include FULL"
        }
    }
    
    mapping = COMMAND_MAP.get(action)
    if mapping:
        command_template = mapping.get(device_type)
        if command_template and '{destination_ip}' in command_template:
            destination_ip = kwargs.get('destination_ip', '')
            command = command_template.format(destination_ip=destination_ip)
            return command
        return command_template
    return None

if __name__ == "__main__":
    # Example test:
    cmd = get_command("check_route", "cisco", destination_ip="100.65.255.14")
    print(cmd)
