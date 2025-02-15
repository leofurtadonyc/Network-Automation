# explanations/bgp_vpnv4_vrf_explanation.py

def explain_bgp_vpnv4_vrf(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for BGP VPNv4 unicast VRF queries.
    """
    explanation = (
        "This command displays the BGP VPNv4 unicast routes for a specific VRF on the device.\n"
        "It is used to verify that VPN routes within a given VRF are correctly installed and advertised."
    )
    course = (
        "Actions:\n"
        "  - Ensure that the VRF contains all expected VPN routes.\n"
        "  - If routes are missing or incorrect, review the VRF configuration and BGP policies."
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
