#!/usr/bin/env python
import json
import getpass
import bcrypt
import os
from config import Config

def get_credentials():
    config = Config()
    auth_config = config.config_data.get("authentication", {})
    auth_type = auth_config.get("type", "plain-text")
    
    if auth_type == "plain-text":
        username = auth_config.get("username")
        password = auth_config.get("password")
        if not username or not password:
            raise Exception("Plain-text credentials not fully provided in config.")
        return username, password

    elif auth_type == "secure":
        cred_file = auth_config.get("credentials_file")
        if not cred_file:
            raise Exception("Secure authentication selected but no credentials_file is defined.")
        # If cred_file is not an absolute path, assume it is relative to the auth folder.
        if not os.path.isabs(cred_file):
            cred_file = os.path.join(os.path.dirname(__file__), cred_file)
        try:
            with open(cred_file, "r") as f:
                creds = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Credentials file '{cred_file}' not found.")
        stored_username = creds.get("username")
        stored_hash = creds.get("password_hash")
        if not stored_username or not stored_hash:
            raise Exception("Credentials file is missing username or password_hash.")
        # Prompt the user for a password.
        input_password = getpass.getpass("Enter password for secure authentication: ")
        # Verify using bcrypt.
        if bcrypt.checkpw(input_password.encode("utf-8"), stored_hash.encode("utf-8")):
            return stored_username, input_password
        else:
            raise Exception("Invalid credentials provided.")
    else:
        raise Exception(f"Unsupported authentication type: {auth_type}")

if __name__ == "__main__":
    try:
        username, password = get_credentials()
        print(f"Authenticated as {username}.")
    except Exception as e:
        print("Authentication error:", e)
