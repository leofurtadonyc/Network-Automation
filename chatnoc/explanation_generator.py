# explanation_generator.py
def generate_explanation(operator_query, command, output):
    """
    Generate an explanation of the command output including:
      - The answer to the operator's question.
      - Where to find key information in the output.
      - Some educational context.
    
    This placeholder can later be replaced or enhanced by an LLM call.
    """
    explanation = (
        f"Operator Query: {operator_query}\n"
        f"Executed Command: {command}\n\n"
        "The output displays the status of the interfaces. Look at the 'Status' or 'State' column "
        "to determine if an interface is up or down. Additional details such as IP addresses and VLANs "
        "can provide further context. For more details, consult your device's documentation on the command output."
    )
    return explanation

if __name__ == "__main__":
    test_explanation = generate_explanation(
        "Show me the interface status",
        "show ip interface brief",
        "sample output..."
    )
    print(test_explanation)
