#!/usr/bin/env python
import json
import bcrypt
import getpass
import os

def main():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match!")
        return

    # Generate salt and hash the password.
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    credentials = {
        "username": username,
        "password_hash": password_hash
    }
    
    # Write the credentials file in the auth folder.
    credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
    try:
        with open(credentials_path, "w") as f:
            json.dump(credentials, f)
        print(f"Secure credentials stored in '{credentials_path}'.")
    except Exception as e:
        print(f"Error writing credentials: {e}")

if __name__ == "__main__":
    main()
