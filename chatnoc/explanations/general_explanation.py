# explanations/general_explanation.py

def explain_general(query, command, output, device_name="", baseline=None):
    """
    Generate a general explanation for queries that do not fall into a specialized category.
    The baseline parameter is accepted for consistency with other explanation functions.
    """
    explanation = (
        "This command retrieves network information based on the query.\n"
        "Review the output for any inconsistencies or unexpected information."
    )
    course = (
        "Actions:\n"
        "  - If the output is not as expected, verify the device's configuration and relevant settings."
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

if __name__ == "__main__":
    # Test the function
    print(explain_general("test query", "test command", "test output", device_name="test_device", baseline={"dummy": "value"}))
