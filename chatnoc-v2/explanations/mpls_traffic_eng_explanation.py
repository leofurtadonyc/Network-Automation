# explanations/mpls_traffic_eng_explanation.py

def explain_mpls_traffic_eng(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays MPLS Traffic Engineering tunnels. It shows the status of TE tunnels, including details about labels and tunnel paths, "
        "which are used for optimized traffic routing."
    )
    course = (
        "Actions:\n"
        "  - Verify that the TE tunnels are up and configured as expected.\n"
        "  - Investigate any tunnels that are down or show anomalies."
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
