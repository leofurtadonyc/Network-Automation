# explanations/l2vpn_atom_vc_explanation.py

def explain_l2vpn_atom_vc(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for L2VPN atom VC queries.
    """
    explanation = (
        "This command displays L2VPN Atom VC information, showing the status of virtual circuits used in L2VPN services.\n"
        "It is useful for verifying that L2VPN services are correctly established between devices."
    )
    course = (
        "Actions:\n"
        "  - Check that all virtual circuits are operational and match expected configurations.\n"
        "  - Investigate any discrepancies that could affect service delivery."
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
