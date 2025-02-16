# explanations/l2vpn_atom_vc_explanation.py

def explain_l2vpn_atom_vc(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays L2VPN Atom VC information, showing the status of virtual circuits used in L2VPN services. "
        "It is used to verify that L2VPN connections are properly established."
    )
    course = (
        "Actions:\n"
        "  - Verify that all expected virtual circuits are operational.\n"
        "  - If any circuits are down, review L2VPN configurations and connectivity."
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
