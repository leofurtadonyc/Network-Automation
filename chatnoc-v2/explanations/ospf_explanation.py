# explanations/ospf_explanation.py

def explain_ospf_neighbors(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays OSPF neighbor adjacencies, showing which neighbors have reached FULL state. "
        "It is used to verify that OSPF routing adjacencies are healthy and that the exchange of routing information is complete."
    )
    course = (
        "Actions:\n"
        "  - Verify connectivity between OSPF neighbors if any expected neighbors are missing or not in FULL state.\n"
        "  - Check OSPF configurations and interface settings."
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
