# explanations/version_explanation.py

def explain_version(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command displays the device's version information, including hardware, software, and uptime details. "
        "It is essential for verifying the device's current software release and ensuring that it meets the required standards."
    )
    course = (
        "Actions:\n"
        "  - Check the version output to ensure the device is running the expected software.\n"
        "  - Investigate any discrepancies or anomalies that may require a software upgrade or configuration changes."
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
