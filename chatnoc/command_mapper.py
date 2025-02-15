# command_mapper.py

COMMAND_MAP = {
    "show_interfaces_down": {
        "cisco": [
            "show ip interface brief | include down",
            "show interfaces description | include down"
        ],
        "cisco_xe": [
            "show ip interface brief | include down",
            "show interfaces description | include down"
        ],
        "juniper_junos": "show interfaces terse | match down",
        "cisco_xr": "show interfaces brief | include down",
        "huawei_vrp": "display interface brief | include down",
        "nokia_sr": 'show router interface | match "Down/Down"'
    },
    "get_mgmt_ip": {
        "cisco": "show ip vrf | include MGMT",
        "cisco_xe": "show ip vrf | include MGMT",
        "juniper_junos": "show interfaces terse | match fxp",
        "cisco_xr": "show ipv4 int mgmtEth 0/RP0/CPU0/0",
        "huawei_vrp": "display ip vpn-instance",
        "nokia_sr": "show router interface if-oob"
    },
    "show_ospf_routes_count": {
        "cisco": "show ip route ospf",
        "cisco_xe": "show ip route ospf",
        "juniper_junos": "show route protocol ospf",
        "cisco_xr": "show route ospf",
        "huawei_vrp": "display ip routing-table protocol ospf",
        "nokia_sr": "show router route-table protocol ospf"
    },
    "check_route": {
        "cisco": "show ip route {destination_ip}",
        "cisco_xe": "show ip route {destination_ip}",
        "juniper_junos": "show route {destination_ip}",
        "cisco_xr": "show route {destination_ip}",
        "huawei_vrp": "display ip routing-table {destination_ip}",
        "nokia_sr": "show router route-table {destination_ip}"
    },
    "show_uptime": {
        "cisco": "show version | include uptime",
        "cisco_xe": "show version | include uptime",
        "juniper_junos": "show system uptime",
        "cisco_xr": "show version | include uptime",
        "huawei_vrp": "display version | include uptime",
        "nokia_sr": 'show system information | match "System Up Time"'
    },
    "show_ospf_neighbors_full": {
        "cisco": "show ip ospf neighbor | include FULL",
        "cisco_xe": "show ip ospf neighbor | include FULL",
        "juniper_junos": "show ospf neighbor | match FULL",
        "cisco_xr": "show ospf neighbor | include FULL",
        "huawei_vrp": "display ospf peer | include FULL",
        "nokia_sr": "show router ospf neighbor | match Full"
    },
    "ping": {
        "cisco": "ping {destination_ip} source {source_ip}",
        "cisco_xe": "ping {destination_ip} source {source_ip}",
        "juniper_junos": "ping {destination_ip} source {source_ip}",
        "cisco_xr": "ping {destination_ip} source {source_ip}",
        "huawei_vrp": "ping -a {source_ip} {destination_ip}",
        "nokia_sr": "ping source {source_ip} {destination_ip}"
    },
    "traceroute": {
        "cisco": "traceroute {destination_ip} source {source_ip}",
        "cisco_xe": "traceroute {destination_ip} source {source_ip}",
        "juniper_junos": "traceroute {destination_ip} source {source_ip}",
        "cisco_xr": "traceroute {destination_ip} source {source_ip}",
        "huawei_vrp": "tracert -a {source_ip} {destination_ip}",
        "nokia_sr": "traceroute source {source_ip} {destination_ip}"
    },
    "bgp_neighbors": {
        "cisco": "show ip bgp summary",
        "cisco_xe": "show ip bgp summary",
        "juniper_junos": "show bgp summary",
        "cisco_xr": "show bgp summary",
        "huawei_vrp": "display bgp peer",
        "nokia_sr": "show router bgp summary"
    },
    "ldp_label_binding": {
        "cisco": "show mpls ldp binding | include {destination_ip}",
        "cisco_xe": "show mpls ldp bindings {destination_ip} {mask}",
        "juniper_junos": "show ldp database | match {destination_ip}",
        "cisco_xr": "show mpls ldp binding | include {destination_ip}",
        "huawei_vrp": "display mpls ldp lsp | include {destination_ip}",
        "nokia_sr": "show router ldp bindings | match {destination_ip}"
    },
    "ldp_neighbors": {
        "cisco": "show mpls ldp neighbor",
        "cisco_xe": "show mpls ldp neighbor",
        "juniper_junos": "show ldp neighbor",
        "cisco_xr": "show mpls ldp neighbor",
        "huawei_vrp": "display mpls ldp peer",
        "nokia_sr": "show router ldp session"
    },
    "mpls_interfaces": {
        "cisco": "show mpls interfaces",
        "cisco_xe": "show mpls interfaces",
        "juniper_junos": "show mpls interface",
        "cisco_xr": "show mpls interfaces",
        "huawei_vrp": "display mpls interface",
        "nokia_sr": "show router mpls interface"
    },
    "mpls_forwarding": {
        "cisco": "show mpls forwarding-table",
        "cisco_xe": "show mpls forwarding-table",
        "juniper_junos": "show route table mpls.0",
        "cisco_xr": "show mpls forwarding",
        "huawei_vrp": "display mpls ldp lsp",
        "nokia_sr": "show router ldp bindings active"
    },
    "ospf_database": {
        "cisco": "show ip ospf database",
        "cisco_xe": "show ip ospf database",
        "juniper_junos": "show ospf database",
        "cisco_xr": "show ospf database",
        "huawei_vrp": "display ospf lsdb",
        "nokia_sr": "show router ospf database"
    },
    "ip_explicit_paths": {
        "cisco": "show ip explicit-paths",
        "cisco_xe": "show ip explicit-paths",
        "juniper_junos": "show mpls path",
        "cisco_xr": "show explicit-paths",
        "huawei_vrp": "display explicit-path",
        "nokia_sr": "show router mpls path"
    },
    "l2vpn_atom_vc": {
        "cisco": "show l2vpn atom vc",
        "cisco_xe": "show l2vpn atom vc",
        "juniper_junos": "show vpls connections summary",
        "cisco_xr": "show l2vpn bridge-domain brief",
        "huawei_vrp": "display mpls l2vc",
        "nokia_sr": "show service service-name-using | match Epipe"
    },
    "mpls_traffic_eng": {
        "cisco": "show mpls traffic-eng tunnels",
        "cisco_xe": "show mpls traffic-eng tunnels",
        "juniper_junos": "show mpls lsp",
        "cisco_xr": "show mpls traffic-eng tunnels",
        "huawei_vrp": "display mpls te tunnel",
        "nokia_sr": "show router mpls lsp"
    },
    "version_full": {
        "cisco": "show version",
        "cisco_xe": "show version",
        "juniper_junos": "show version",
        "cisco_xr": "show version",
        "huawei_vrp": "display version",
        "nokia_sr": "show version"
    },
    "bgp_vpnv4_all": {
        "cisco": "show bgp vpnv4 unicast all",
        "cisco_xe": "show bgp vpnv4 unicast all",
        "juniper_junos": "show route table bgp.l3vpn.0",
        "cisco_xr": "show bgp vpnv4 unicast all",
        "huawei_vrp": "display bgp vpnv4 all routing-table",
        "nokia_sr": "show router bgp routes vpn-ipv4"
    },
    "bgp_vpnv4_vrf": {
        "cisco": "show bgp vpnv4 unicast vrf",
        "cisco_xe": "show bgp vpnv4 unicast vrf",
        "juniper_junos": "show route table",
        "cisco_xr": "show bgp vpnv4 unicast vrf",
        "huawei_vrp": "display bgp vpnv4 vpn-instance",
        "nokia_sr": "show router bgp routes vpn-ipv4"
    },
}

def get_command(action, device_type, **kwargs):
    mapping = COMMAND_MAP.get(action)
    if mapping:
        cmd_template = mapping.get(device_type)
        if cmd_template:
            if isinstance(cmd_template, list):
                cmds = []
                for template in cmd_template:
                    try:
                        cmds.append(template.format(**kwargs))
                    except KeyError:
                        return None
                return cmds
            else:
                try:
                    return cmd_template.format(**kwargs)
                except KeyError:
                    return None
    return None

if __name__ == "__main__":
    print("Ping (Cisco):", get_command("ping", "cisco", destination_ip="100.65.255.14", source_ip="100.65.255.1"))
    print("Traceroute (Nokia):", get_command("traceroute", "nokia_sr", destination_ip="100.65.255.14", source_ip="100.65.255.1"))
    print("Show Interfaces Down (Cisco):", get_command("show_interfaces_down", "cisco"))
    print("LDP Label Binding (Cisco XE):", get_command("ldp_label_binding", "cisco_xe", destination_ip="100.65.255.14", mask="32"))
    print("MPLS Interfaces (Cisco):", get_command("mpls_interfaces", "cisco"))
    print("MPLS Traffic Eng (Cisco):", get_command("mpls_traffic_eng", "cisco"))
