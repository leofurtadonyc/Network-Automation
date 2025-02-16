# explanations/bgp_vpnv4_all_explanation.py

def explain_bgp_vpnv4_all(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the BGP VPNv4 unicast routes across all VRFs on the device. "
        "It is used in service provider environments to verify that all VPN routes are properly advertised."
    )
    course = (
        "Actions:\n"
        "  - Verify that the VPN routes match the expected routing policies.\n"
        "  - Investigate any missing or unexpected routes."
    )
    summary = (
        f"Input Query: {query}\n"
        f"Command Executed: {command} on device(s) {device_name}\n"
    )
    return (
        f"Device Output:\n{output}\n\n------------------------------\n\n"
        f"Command issued:\n{command}\n\n"
        f"Explanation:\n{explanation}\n\n"
        f"Course of action:\n{course}\n\n"
        f"Summary:\n{summary}"
    )
