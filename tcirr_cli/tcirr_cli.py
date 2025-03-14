import os
import json
import requests

# Configurations
API_BASE_URL = 'https://rr.example.net/v1/submit/'  # Replace with your actual TC IRR API URL
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
# Folder where JSON files are stored
RECORDS_FOLDER = 'irr_records'

def load_record(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_record(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def submit_change(data):
    """
    Submits a change to the TC IRR API.
    This function sends a POST request with the JSON data.
    """
    response = requests.post(API_BASE_URL, headers=HEADERS, data=json.dumps(data))
    try:
        return response.json()
    except ValueError:
        return {'error': 'Invalid JSON response', 'status_code': response.status_code, 'response': response.text}

def get_existing_object(object_type, identifier):
    """
    Retrieves the existing object from TC IRR for comparison.
    This is a placeholder function.
    Replace with the appropriate API GET call and parsing logic.
    """
    # Example: GET request to retrieve an object.
    # For instance, if your API has an endpoint like /<object_type>/<identifier>
    url = f"{API_BASE_URL.rstrip('/')}/{object_type}/{identifier}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()  # assuming JSON response with object details
    else:
        return None

def process_add(record):
    # For new entries, simply submit the new object
    submission = {
        "objects": [{"object_text": record['data']['object_text']}],
        "passwords": record['data'].get("passwords", [])
    }
    result = submit_change(submission)
    return result

def process_modify(record):
    # Retrieve existing object from TC IRR (using a unique identifier from the record)
    identifier = record['data'].get('identifier')
    if not identifier:
        return {"error": "No identifier provided for modification."}
    
    existing_object = get_existing_object(record['object_type'], identifier)
    if not existing_object:
        return {"error": "Existing object not found for comparison."}
    
    # Compare existing object with new data (this could be a detailed diff; here we simply re-submit the new object)
    # In a real scenario, you might compute differences and only send updated fields.
    submission = {
        "objects": [{"object_text": record['data']['object_text']}],
        "passwords": record['data'].get("passwords", [])
    }
    result = submit_change(submission)
    return result

def process_delete(record):
    # For deletion, we assume the API accepts a delete flag or delete_reason field.
    submission = {
        "objects": [{"object_text": record['data']['object_text']}],
        "passwords": record['data'].get("passwords", []),
        "delete_reason": record.get("delete_reason", "No longer needed")
    }
    result = submit_change(submission)
    return result

def process_record(file_path):
    record = load_record(file_path)
    action = record.get('action')
    object_type = record.get('object_type')
    print(f"Processing {file_path} - Action: {action}, Object Type: {object_type}")
    
    if action == 'add':
        result = process_add(record)
        if result.get("error") is None:
            record['status'] = "published"
    elif action == 'modify':
        result = process_modify(record)
        if result.get("error") is None:
            record['status'] = "published"
    elif action == 'delete':
        result = process_delete(record)
        if result.get("error") is None:
            record['status'] = "deleted"
    else:
        result = {"error": f"Unknown action: {action}"}
    
    # Update the record file with the new status and possibly any API response details.
    record['last_api_response'] = result
    save_record(file_path, record)
    print(f"Updated record file: {file_path} with status: {record['status']}")
    print("API response:", result)

def process_all_records():
    for filename in os.listdir(RECORDS_FOLDER):
        if filename.endswith('.json'):
            file_path = os.path.join(RECORDS_FOLDER, filename)
            try:
                process_record(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    process_all_records()
