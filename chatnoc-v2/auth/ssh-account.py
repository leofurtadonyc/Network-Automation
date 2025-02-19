# auth/ssh-account.py
import argparse
import json
import bcrypt
import getpass
import os

def main():
    parser = argparse.ArgumentParser(
        description="Create SSH credentials for ChatNOC. Use --user for normal user credentials, or --jumpserver for jumpserver credentials."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--user", action="store_true", help="Create normal user credentials.")
    group.add_argument("--jumpserver", action="store_true", help="Create jumpserver credentials.")
    args = parser.parse_args()

    # Determine the target credentials file based on the flag.
    if args.user:
        target_file = os.path.join(os.path.dirname(__file__), "credentials.json")
        account_type = "normal user"
    elif args.jumpserver:
        target_file = os.path.join(os.path.dirname(__file__), "jumpserver_credentials.json")
        account_type = "jumpserver user"
    else:
        parser.error("One of --user or --jumpserver must be specified.")

    print(f"Creating {account_type} credentials...")
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
    
    try:
        with open(target_file, "w") as f:
            json.dump(credentials, f)
        print(f"Secure credentials stored in '{target_file}'.")
    except Exception as e:
        print(f"Error writing credentials: {e}")

if __name__ == "__main__":
    main()
