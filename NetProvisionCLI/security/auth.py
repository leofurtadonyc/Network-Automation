import bcrypt

def verify_user(username: str, password: str, credentials_file: str = 'devices/usercredentials.sec') -> bool:
    try:
        with open(credentials_file, 'r') as file:
            for line in file:
                stored_username, hashed_password = line.strip().split(':')
                if stored_username == username and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return True
        return False
    except FileNotFoundError:
        print("Credentials file not found.")
        return False
