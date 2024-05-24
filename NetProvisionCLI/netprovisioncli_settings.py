import yaml
import os
import argparse
import sys
import getpass
from security.auth import verify_user

def load_settings():
    settings_path = 'settings/settings.yaml'
    if not os.path.exists(settings_path):
        print("Settings not found. Initializing default settings.")
        return initialize_settings()
    with open(settings_path, 'r') as file:
        return yaml.safe_load(file)

def save_settings(settings):
    with open('settings/settings.yaml', 'w') as file:
        yaml.safe_dump(settings, file, default_flow_style=False)

def initialize_settings():
    settings = {
        'data_source': 'yaml',
        'mongodb_connection': {
            'uri': 'mongodb://localhost:27017/',
            'database_name': 'netprovision'
        }
    }
    save_settings(settings)
    print("Default settings have been initialized.")
    return settings

def set_data_source(source):
    settings = load_settings()
    if source not in ['yaml', 'mongodb']:
        print("Invalid data source. Use 'yaml' or 'mongodb'.")
        return
    settings['data_source'] = source
    save_settings(settings)
    print(f"Data source set to {source}.")

def show_settings():
    settings = load_settings()
    print("Current Settings:")
    print(yaml.safe_dump(settings, default_flow_style=False))

def authenticate_user(username, password):
    if not verify_user(username, password):
        print("Authentication failed.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Manage settings for NetProvisionCLI.')
    parser.add_argument('--set-source', type=str, help='Set the data source (yaml, mongodb)')
    parser.add_argument('--show', action='store_true', help='Show current settings')
    parser.add_argument('--init', action='store_true', help='Initialize or reset settings to default')
    parser.add_argument('--username', type=str, help='Username for authentication')
    parser.add_argument('--password', type=str, help='Password for authentication')

    args = parser.parse_args()

    # Check if no arguments were provided
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nNo options provided. Use one of the flags to manage settings.")
        return

    if args.show:
        show_settings()
    else:
        if not args.username:
            print("Error: --username is required for authentication when changing settings.")
            sys.exit(1)
        if not args.password:
            args.password = getpass.getpass(prompt='Password: ')
        authenticate_user(args.username, args.password)

        if args.set_source:
            set_data_source(args.set_source)
        elif args.init:
            initialize_settings()

if __name__ == '__main__':
    main()
