# adduser.py - A script to add a user to the chatnoc system.
import json
import bcrypt
import getpass

def main():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match!")
        return
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    credentials = {
        "username": username,
        "password_hash": password_hash
    }
    with open("credentials.json", "w") as f:
        json.dump(credentials, f)
    print("Secure credentials stored in 'credentials.json'.")

if __name__ == "__main__":
    main()
