# This script is designed to generate configurations for network devices, catering to a range of customer service provisioning requirements.
# https://github.com/leofurtadonyc/Network-Automation/wiki
import bcrypt
import os

def load_credentials(path):
    """Load user credentials from a file."""
    if not os.path.exists(path):
        print("Error: Credentials file does not exist.")
        return None
    with open(path, 'r') as file:
        credentials = {}
        for line in file:
            username, hashed_password = line.strip().split(':', 1)
            credentials[username] = hashed_password
        return credentials

def verify_user(credentials, username, password):
    """Verify a user's password against the hashed password in the credentials."""
    if username in credentials:
        password = password.encode('utf-8')
        hashed_password = credentials[username].encode('utf-8')
        if bcrypt.checkpw(password, hashed_password):
            return "Authentication successful."
        else:
            return "Invalid password."
    else:
        return "Username not found."

def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    credentials_path = "devices/usercredentials.sec"
    credentials = load_credentials(credentials_path)

    if credentials is not None:
        result = verify_user(credentials, username, password)
        print(result)

if __name__ == "__main__":
    main()
