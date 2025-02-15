# explanations/ospf_database_explanation.py

def explain_ospf_database(query, command, output, device_name="", baseline=None):
    """
    Generate an explanation for OSPF database queries.
    """
    explanation = (
        "This command displays the OSPF database, which contains detailed information about the OSPF link-state advertisements (LSAs) and network topology.\n"
        "It is useful for troubleshooting OSPF network convergence and verifying LSA propagation."
    )
    course = (
        "Actions:\n"
        "  - Review the LSAs to ensure that the OSPF topology is as expected.\n"
        "  - Check for any inconsistencies or missing LSAs that may indicate problems with OSPF neighbor relationships."
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
