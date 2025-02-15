# explanations/bgp_vpnv4_all_explanation.py

def explain_bgp_vpnv4_all(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for BGP VPNv4 unicast all queries.
    """
    explanation = (
        "This command displays the BGP VPNv4 unicast routes across all VRFs on the device.\n"
        "It is used in service provider environments to verify connectivity for VPN customers."
    )
    course = (
        "Actions:\n"
        "  - Review the output to ensure that all expected VPN routes are present and properly advertised.\n"
        "  - Investigate any missing routes or unexpected information."
    )
    summary = (
        f"Input Query: {query}\n"
        f"Command Executed: {command} on device(s) {device_name}\n"
    )
    return (
        f"Device Output:\n{output}\n\n"
        "------------------------------\n\n"
        f"Command issued:\n{command}\n\n"
        f"Explanation:\n{explanation}\n\n"
        f"Course of action:\n{course}\n\n"
        f"Summary:\n{summary}"
    )
