# explanations/general_explanation.py

def explain_general(query, command, output, device_name="", baseline=None):
    explanation = (
        "This command retrieves network information based on your query. "
        "It provides raw output which you should review for any inconsistencies or unexpected results."
    )
    course = (
        "Actions:\n"
        "  - Review the output carefully.\n"
        "  - Verify the device's configuration and connectivity if the output does not match expectations."
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
