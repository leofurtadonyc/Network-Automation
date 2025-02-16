# explanations/bgp_vpnv4_vrf_explanation.py

def explain_bgp_vpnv4_vrf(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the BGP VPNv4 unicast routes for a specific VRF on the device. "
        "It helps verify that VPN routes within the specified VRF are correctly installed and being advertised."
    )
    course = (
        "Actions:\n"
        "  - Ensure that the VRF contains all the expected VPN routes.\n"
        "  - If routes are missing, review the VRF configuration and BGP policies."
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
