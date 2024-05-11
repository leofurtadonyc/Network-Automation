import argparse
import time
from config.load_config import load_yaml
from utils.file_utils import write_to_file, log_error, delete_error_log
from utils.validation import valid_ip_irb, valid_ip_nexthop, valid_ip_lan, interface_allowed
from utils.template_utils import render_template
from input.input_handler import collect_inputs, load_recipe

def validate_arguments(args):
    """Validate that all necessary arguments are provided."""
    missing_args = []

    if args.deactivate:
        if not args.customer_name:
            missing_args.append('--customer-name')
        if not args.access_device:
            missing_args.append('--access-device')
        if not args.pe_device:
            missing_args.append('--pe-device')
    else:
        required_args = ['customer_name', 'access_device', 'access_interface', 'circuit_id', 
                         'qos_input', 'qos_output', 'vlan_id', 'vlan_id_outer', 'pw_id', 
                         'irb_ipaddr', 'irb_ipv6addr', 'ipv4_lan', 'ipv4_nexthop', 
                         'ipv6_lan', 'ipv6_nexthop', 'pe_device', 'service_type']
        for arg in required_args:
            if getattr(args, arg) is None:
                missing_args.append(f'--{arg.replace("_", "-")}')

    if missing_args:
        raise ValueError(f"Missing required arguments: {', '.join(missing_args)}")

def main():
    parser = argparse.ArgumentParser(description="Generate service provisioning configurations for network devices.")
    parser.add_argument("--customer-name", type=str, help="Customer name for the service.")
    parser.add_argument("--access-device", type=str, help="Hostname of the access device.")
    parser.add_argument("--access-interface", type=str, help="Interface name on the access device.")
    parser.add_argument("--circuit-id", type=int, help="Circuit ID for the service.")
    parser.add_argument("--qos-input", type=int, help="Input QoS policer in bits.")
    parser.add_argument("--qos-output", type=int, help="Output QoS policer in bits.")
    parser.add_argument("--vlan-id", type=int, help="VLAN ID (1-4095).")
    parser.add_argument("--vlan-id-outer", type=int, help="Outer VLAN ID (1-4095).")
    parser.add_argument("--pw-id", type=int, help="Pseudowire ID.")
    parser.add_argument("--irb-ipaddr", type=valid_ip_irb, help="IP address for the BVI or IRB PE interface.")
    parser.add_argument("--irb-ipv6addr", type=valid_ip_irb, help="IPv6 address for the BVI or IRB PE interface.")
    parser.add_argument("--ipv4-lan", type=valid_ip_lan, help="Customer IPv4 LAN network. Format prefix/mask.")
    parser.add_argument("--ipv4-nexthop", type=valid_ip_nexthop, help="IPv4 next-hop address to customer's LAN")
    parser.add_argument("--ipv6-lan", type=valid_ip_lan, help="Customer IPv6 LAN network. Format prefix/mask.")
    parser.add_argument("--ipv6-nexthop", type=valid_ip_nexthop, help="IPv6 next-hop address to customer's LAN")
    parser.add_argument("--pe-device", type=str, help="Hostname of the Provider Edge device.")
    parser.add_argument("--service-type", choices=['p2p', 'p2mp'], help="Service type: point-to-point or point-to-multipoint.")
    parser.add_argument("--interactive", action='store_true', help="Run the script in interactive mode to gather input from the operator.")
    parser.add_argument("--recipe", type=str, help="Path to a YAML or JSON file containing the recipe for customer service activation.")
    parser.add_argument("--deactivate", action='store_true', help="Deactivate the specified customer name.")

    args = parser.parse_args()

    if args.recipe:
        recipe_data = load_recipe(args.recipe)
        args.customer_name = recipe_data['customer']['name']
        args.access_device = recipe_data['customer']['devices']['access']['name']
        args.access_interface = recipe_data['customer']['devices']['access']['interface']
        args.circuit_id = recipe_data['customer']['configuration']['circuit_id']
        args.qos_input = recipe_data['customer']['configuration']['qos']['input']
        args.qos_output = recipe_data['customer']['configuration']['qos']['output']
        args.vlan_id = recipe_data['customer']['configuration']['vlan']['id']
        args.vlan_id_outer = recipe_data['customer']['configuration']['vlan']['outer_id']
        args.pw_id = recipe_data['customer']['configuration']['pseudowire_id']
        args.irb_ipaddr = recipe_data['customer']['configuration']['irb']['ipv4_address']
        args.irb_ipv6addr = recipe_data['customer']['configuration']['irb']['ipv6_address']
        args.ipv4_lan = recipe_data['customer']['configuration']['lan']['ipv4']['network']
        args.ipv4_nexthop = recipe_data['customer']['configuration']['lan']['ipv4']['next_hop']
        args.ipv6_lan = recipe_data['customer']['configuration']['lan']['ipv6']['network']
        args.ipv6_nexthop = recipe_data['customer']['configuration']['lan']['ipv6']['next_hop']
        args.pe_device = recipe_data['customer']['devices']['pe']['name']
        args.service_type = recipe_data['customer']['service_type']

    elif args.interactive:
        args.customer_name, args.access_device, args.access_interface, args.circuit_id, args.qos_input, args.qos_output, args.vlan_id, args.vlan_id_outer, args.pw_id, args.irb_ipaddr, args.irb_ipv6addr, args.ipv4_lan, args.ipv4_nexthop, args.ipv6_lan, args.ipv6_nexthop, args.pe_device, args.service_type = collect_inputs()

    try:
        validate_arguments(args)
    except ValueError as e:
        print(str(e))
        return

    start_time = time.time()

    devices_config = load_yaml('devices/network_devices.yaml')
    access_device_info = devices_config.get(args.access_device)
    pe_device_info = devices_config.get(args.pe_device)

    if not access_device_info or not pe_device_info:
        print("Error: Device information is missing or incorrect in the YAML file.")
        log_error('generated_configs', args.customer_name, 
                  "Device information is missing or incorrect in the YAML file. Please check the device names.",
                  400)
        return
    
    if not interface_allowed(access_device_info, args.access_interface):
        print(f"Error: The specified interface {args.access_interface} on the Access device {args.access_device} is not allowed for customer configurations.")
        log_error('generated_configs', args.customer_name, 
                  f"The specified interface {args.access_interface} on the Access device {args.access_device} is not allowed for customer configurations.",
                  400)
        return

    if access_device_info.get('device_role') != 'access' and pe_device_info.get('device_role') != 'pe':
        print(f"Error: Incorrect device roles specified. The device '{args.access_device}' is assigned the role '{access_device_info.get('device_role')}', but expected 'access'.")
        print(f"Similarly, the device '{args.pe_device}' is assigned the role '{pe_device_info.get('device_role')}', but expected 'pe'.")
        log_error('generated_configs', args.customer_name, 
                  f"Incorrect device roles specified. The device '{args.access_device}' is assigned the role '{access_device_info.get('device_role')}', but expected 'access'. The device '{args.pe_device}' is assigned the role '{pe_device_info.get('device_role')}', but expected 'pe'.",
                  400)
        return

    if access_device_info.get('device_role') != 'access':
        print(f"Error: The specified Access device {args.access_device} has a role of {access_device_info.get('device_role')}, not 'access'.")
        log_error('generated_configs', args.customer_name, 
                  f"The specified Access device {args.access_device} has a role of {access_device_info.get('device_role')}, not 'access'.",
                  400)
        return

    if pe_device_info.get('device_role') != 'pe':
        print(f"Error: The specified PE device {args.pe_device} has a role of {pe_device_info.get('device_role')}, not 'pe'.")
        log_error('generated_configs', args.customer_name,
                    f"The specified PE device {args.pe_device} has a role of {pe_device_info.get('device_role')}, not 'pe'.",
                    400)
        return
    
    if not access_device_info.get('customer_provisioning', False) and not pe_device_info.get('customer_provisioning', False):
        print(f"Error: Customer provisioning is disabled for both specified devices, Access device {args.access_device} and PE device {args.pe_device}.")
        log_error('generated_configs', args.customer_name,
                  f"Customer provisioning is disabled for both specified devices, Access device {args.access_device} and PE device {args.pe_device}. Cannot proceed with configuration.",
                  400)
        return

    if not access_device_info.get('customer_provisioning', False):
        print(f"Error: Customer provisioning is disabled for this specified Access device {args.access_device}.")
        log_error('generated_configs', args.customer_name,
                  "Customer provisioning is disabled for the specified Access device. Cannot proceed with configuration.",
                  400)
        return

    if not pe_device_info.get('customer_provisioning', False):
        print(f"Error: Customer provisioning is disabled for this specified PE device {args.pe_device}.")
        log_error('generated_configs', args.customer_name,
                    "Customer provisioning is disabled for the specified PE device. Cannot proceed with configuration.",
                    400)
        return
    
    if args.deactivate:
        if access_device_info['device_type'] == 'cisco_xe':
            access_template_name = "cisco_xe_to_generic_deactivate.j2"
        elif access_device_info['device_type'] == 'cisco_xr':
            access_template_name = "cisco_xr_to_generic_deactivate.j2"
        elif access_device_info['device_type'] == 'juniper_junos':
            access_template_name = "juniper_junos_to_generic_deactivate.j2"
        elif access_device_info['device_type'] == 'huawei_vrp':
            access_template_name = "huawei_vrp_to_generic_deactivate.j2"
        elif access_device_info['device_type'] == 'huawei_vrp_xpl':
            access_template_name = "huawei_vrp_xpl_to_generic_deactivate.j2"
        else:
            print(f"Unsupported Access device type: {access_device_info['device_type']}")
            return

        if pe_device_info['device_type'] == 'cisco_xr':
            pe_template_name = "cisco_xr_to_generic_deactivate.j2"
        elif pe_device_info['device_type'] == 'juniper_junos':
            pe_template_name = "juniper_junos_to_generic_deactivate.j2"
        elif pe_device_info['device_type'] == 'huawei_vrp':
            pe_template_name = "huawei_vrp_to_generic_deactivate.j2"
        elif pe_device_info['device_type'] == 'huawei_vrp_xpl':
            pe_template_name = "huawei_vrp_xpl_to_generic_deactivate.j2"
        else:
            print(f"Unsupported PE device type: {pe_device_info['device_type']}")
            return
    else:
        if access_device_info['device_type'] == 'cisco_xe' and args.service_type == 'p2p':
            access_template_name = "p2p_cisco_xe_to_generic.j2"
            access_template_name_remove = "p2p_cisco_xe_to_generic_remove.j2"
        elif access_device_info['device_type'] == 'cisco_xe' and args.service_type == 'p2mp':
            access_template_name = "p2mp_cisco_xe_to_generic.j2"
            access_template_name_remove = "p2mp_cisco_xe_to_generic_remove.j2"
        elif access_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2p':
            access_template_name = "p2p_huawei_vrp_to_generic.j2"
            access_template_name_remove = "p2p_huawei_vrp_to_generic_remove.j2"
        elif access_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2mp':
            access_template_name = "p2mp_huawei_vrp_to_generic.j2"
            access_template_name_remove = "p2mp_huawei_vrp_to_generic_remove.j2"
        elif access_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2p':
            access_template_name = "p2p_huawei_vrp_xpl_to_generic.j2"
            access_template_name_remove = "p2p_huawei_vrp_xpl_to_generic_remove.j2"
        elif access_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2mp':
            access_template_name = "p2mp_huawei_vrp_xpl_to_generic.j2"
            access_template_name_remove = "p2mp_huawei_vrp_xpl_to_generic_remove.j2"
        else:
            print(f"Unsupported Access device type: {access_device_info['device_type']}")
            return

        if pe_device_info['device_type'] == 'cisco_xr' and args.service_type == 'p2p':
            pe_template_name = "p2p_cisco_xr_to_generic.j2"
            pe_template_name_remove = "p2p_cisco_xr_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'cisco_xr' and args.service_type == 'p2mp':
            pe_template_name = "p2mp_cisco_xr_to_generic.j2"
            pe_template_name_remove = "p2mp_cisco_xr_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'juniper_junos' and args.service_type == 'p2p':
            pe_template_name = "p2p_juniper_junos_to_generic.j2"
            pe_template_name_remove = "p2p_juniper_junos_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'juniper_junos' and args.service_type == 'p2mp':
            pe_template_name = "p2mp_juniper_junos_to_generic.j2"
            pe_template_name_remove = "p2mp_juniper_junos_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2p':
            pe_template_name = "p2p_huawei_vrp_to_generic.j2"
            pe_template_name_remove = "p2p_huawei_vrp_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'huawei_vrp' and args.service_type == 'p2mp':
            pe_template_name = "p2mp_huawei_vrp_to_generic.j2"
            pe_template_name_remove = "p2mp_huawei_vrp_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2p':
            pe_template_name = "p2p_huawei_vrp_xpl_to_generic.j2"
            pe_template_name_remove = "p2p_huawei_vrp_xpl_to_generic_remove.j2"
        elif pe_device_info['device_type'] == 'huawei_vrp_xpl' and args.service_type == 'p2mp':
            pe_template_name = "p2mp_huawei_vrp_xpl_to_generic.j2"
            pe_template_name_remove = "p2mp_huawei_vrp_xpl_to_generic_remove.j2"
        else:
            print(f"Unsupported PE device type: {pe_device_info['device_type']}")
            return

    if args.deactivate:
        print(f"Using template: {access_template_name} to deactivate configuration for this customer from the Access device")
        print(f"Using template: {pe_template_name} to deactivate configuration for this customer from the PE device")
    else:
        print(f"Using template: {access_template_name_remove} to remove any previous configuration for this customer from the Access device")
        print(f"Using template: {pe_template_name_remove} to remove any previous configuration for this customer from the PE device")
        print(f"Using template: {access_template_name} for Access device new configuration")
        print(f"Using template: {pe_template_name} for PE device new configuration")

    context = {
        'customer_name': args.customer_name,
        'interface_name': args.access_interface,
        'service_instance_id': args.circuit_id,
        'qos_input': args.qos_input,
        'qos_output': args.qos_output,
        'vlan_id': args.vlan_id,
        'vlan_id_outer': args.vlan_id_outer,
        'pw_id': args.pw_id,
        'irb_ipaddr': args.irb_ipaddr,
        'irb_ipv6addr': args.irb_ipv6addr,
        'ipv4_lan': args.ipv4_lan,
        'ipv4_nexthop': args.ipv4_nexthop,
        'ipv6_lan': args.ipv6_lan,
        'ipv6_nexthop': args.ipv6_nexthop,
        'access_address': access_device_info['ip_address'],
        'pe_address': pe_device_info['ip_address'],
        'access_loopback': access_device_info['loopback'],
        'pe_loopback': pe_device_info['loopback'],
        'device_type': pe_device_info['device_type']
    }

    try:
        if args.deactivate:
            access_rendered_config = render_template(access_template_name, context) + '\n'
            pe_rendered_config = render_template(pe_template_name, context) + '\n'
            access_output_file = f"{args.customer_name}_{args.access_device}_access_config_deactivate.txt"
            pe_output_file = f"{args.customer_name}_{args.pe_device}_pe_config_deactivate.txt"
            write_to_file('generated_configs', access_output_file, access_rendered_config)
            write_to_file('generated_configs', pe_output_file, pe_rendered_config)
        else:
            access_rendered_config_remove = render_template(access_template_name_remove, context) + '\n'
            pe_rendered_config_remove = render_template(pe_template_name_remove, context) + '\n'
            access_rendered_config = render_template(access_template_name, context) + '\n'
            pe_rendered_config = render_template(pe_template_name, context) + '\n'

            access_remove_output_file = f"{args.customer_name}_{args.access_device}_access_config_remove.txt"
            pe_remove_output_file = f"{args.customer_name}_{args.pe_device}_pe_config_remove.txt"
            access_output_file = f"{args.customer_name}_{args.access_device}_access_config.txt"
            pe_output_file = f"{args.customer_name}_{args.pe_device}_pe_config.txt"

            write_to_file('generated_configs', access_remove_output_file, access_rendered_config_remove)
            write_to_file('generated_configs', pe_remove_output_file, pe_rendered_config_remove)
            write_to_file('generated_configs', access_output_file, access_rendered_config)
            write_to_file('generated_configs', pe_output_file, pe_rendered_config)

        delete_error_log('generated_configs', args.customer_name)
        print("Configuration generation completed successfully.")

    except Exception as e:
        log_error('generated_configs', args.customer_name,
                  f"Failed to generate configurations due to: {str(e)}",
                  500)
        return

    elapsed_time = time.time() - start_time
    print(f"Configuration generation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
