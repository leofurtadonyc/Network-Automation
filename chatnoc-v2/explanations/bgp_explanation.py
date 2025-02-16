# explanations/bgp_explanation.py

def explain_bgp_neighbors(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the BGP neighbor summary. It shows which BGP sessions are established and their status. "
        "It is useful for verifying that the device is receiving proper BGP routing updates."
    )
    course = (
        "Actions:\n"
        "  - Check that all expected BGP neighbors are present and in the 'Established' state.\n"
        "  - If any sessions are missing or not established, review BGP configuration and underlying connectivity."
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

# Optionally, if you want a specialized explanation for bgp routes, you can reuse this function or create a separate one.
