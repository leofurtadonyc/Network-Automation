import argparse
from deployment.deploy import deploy_configurations

def main():
    parser = argparse.ArgumentParser(description="Network Configuration Deployment")
    parser.add_argument("--customer-name", required=True, help="Customer name to identify config files")
    parser.add_argument("--username", required=True, help="Username for SSH and credential verification")
    parser.add_argument("--password", required=True, help="Password for SSH and credential verification", type=str)
    parser.add_argument("--access-device", required=True, help="Hostname of the access device")
    parser.add_argument("--pe-device", required=True, help="Hostname of the PE device")
    parser.add_argument("--deactivate", action='store_true', help="Deploy only the removal configurations")

    args = parser.parse_args()
    device_configurations = {
        args.access_device: 'access' if not args.deactivate else 'remove',
        args.pe_device: 'pe' if not args.deactivate else 'remove'
    }

    result = deploy_configurations(args.username, args.password, args.customer_name, device_configurations)
    print(result)

if __name__ == "__main__":
    main()
