import os
import json
import time

def write_to_file(directory, filename, data):
    """Write data to a file and ensure the directory exists."""
    base_path = os.path.abspath(directory)
    filepath = os.path.join(base_path, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as file:
        file.write(data)
    print(f"Configuration written to {filepath}")

def log_error(directory, customer_name, message, error_code):
    """Log an error message with an error code to a structured JSON file for future reference. The deploy script should not move forward if an error is logged."""
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    error_info = {
        "error_message": message,
        "error_code": error_code,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(error_path, 'w') as file:
        json.dump(error_info, file, indent=4)
    print(f"Error logged to {error_path}")

def delete_error_log(directory, customer_name):
    """Delete a previous error log file for the customer if it exists. This is to unblock the deployment if the error condition is resolved."""
    error_file = f"{customer_name}_error.json"
    error_path = os.path.join(directory, error_file)
    if os.path.exists(error_path):
        os.remove(error_path)
        print(f"Deleted any old error log to unblock deployment: {error_path}")
