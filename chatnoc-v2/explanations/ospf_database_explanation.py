# explanations/ospf_database_explanation.py

def explain_ospf_database(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the OSPF database, which includes link-state advertisements (LSAs) that describe the network topology. "
        "It is useful for diagnosing OSPF convergence issues and verifying that LSAs are being properly distributed."
    )
    course = (
        "Actions:\n"
        "  - Review the LSAs to ensure that the OSPF topology matches expectations.\n"
        "  - Investigate any inconsistencies or missing LSAs."
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
