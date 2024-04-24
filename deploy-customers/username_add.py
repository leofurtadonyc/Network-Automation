# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import bcrypt
import os
import argparse

def hash_password(password):
    """Hash a password for storing."""
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt)

def load_credentials(path):
    """Load user credentials from the network_devices/usercredentials.sec file."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as file:
        credentials = {}
        for line in file:
            username, hashed_password = line.strip().split(':', 1)
            credentials[username] = hashed_password
        return credentials

def save_credentials(path, credentials):
    """Save user credentials to the network_devices/usercredentials.sec file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        for username, hashed_password in credentials.items():
            file.write(f"{username}:{hashed_password}\n")

def add_or_update_user(credentials, username, password):
    """Add or update a user's password in the credentials dictionary."""
    credentials[username] = hash_password(password).decode('utf-8')
    return credentials

def main():
    parser = argparse.ArgumentParser(description="User Credentials Manager")
    parser.add_argument("--username", help="Username for the credential")
    parser.add_argument("--password", help="Password for the credential")
    args = parser.parse_args()

    if args.username is not None and args.username == "":
        print("Error: Username is a mandatory input.")
        return
    if args.username and (args.password is None or args.password == ""):
        print("Error: Password is mandatory when username is provided.")
        return

    if args.username is None:
        username = input("Enter your username: ").strip()
        if not username:
            print("Error: Username is a mandatory input.")
            return
    else:
        username = args.username

    if args.password is None:
        while True:
            password = input("Enter your password: ").strip()
            if not password:
                print("Error: Password is a mandatory input.")
                return
            password_confirmation = input("Confirm your password: ").strip()
            if password == password_confirmation:
                break
            else:
                print("Error: Passwords do not match.")
    else:
        password = args.password

    credentials_path = "devices/usercredentials.sec"
    credentials = load_credentials(credentials_path)

    credentials = add_or_update_user(credentials, username, password)

    save_credentials(credentials_path, credentials)
    print("User credentials updated.")

if __name__ == "__main__":
    main()
