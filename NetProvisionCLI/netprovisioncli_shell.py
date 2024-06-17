import cmd2
import subprocess
import os

class NetProvisionShell(cmd2.Cmd):
    prompt = 'NetProvisionCLI> '

    def __init__(self):
        super().__init__()
        self.netprovisioncli_scripts_path = os.path.abspath('./')  # Adjust the path as needed

    def run_script(self, script_name, args):
        script_path = os.path.join(self.netprovisioncli_scripts_path, script_name)
        if not os.path.exists(script_path):
            self.perror(f"Script {script_name} not found at path {script_path}")
            return
        try:
            result = subprocess.run(['python', script_path] + args.split(), check=True, capture_output=True, text=True)
            self.poutput(result.stdout)
        except subprocess.CalledProcessError as e:
            self.perror(f"Error executing {script_name}: {e.stderr}")

    def do_customer(self, arg):
        """Enter customer mode"""
        customer_shell = CustomerShell(self)
        customer_shell.cmdloop()

    def do_admin(self, arg):
        """Enter admin mode"""
        admin_shell = AdminShell(self)
        admin_shell.cmdloop()

    def do_exit(self, arg):
        """Exit the shell."""
        return True

class CustomerShell(cmd2.Cmd):
    prompt = 'NetProvisionCLI/customer> '

    def __init__(self, parent_shell):
        super().__init__()
        self.parent_shell = parent_shell
        self.netprovisioncli_scripts_path = parent_shell.netprovisioncli_scripts_path

    def run_script(self, script_name, args):
        script_path = os.path.join(self.netprovisioncli_scripts_path, script_name)
        if not os.path.exists(script_path):
            self.perror(f"Script {script_name} not found at path {script_path}")
            return
        try:
            result = subprocess.run(['python', script_path] + args.split(), check=True, capture_output=True, text=True)
            self.poutput(result.stdout)
        except subprocess.CalledProcessError as e:
            self.perror(f"Error executing {script_name}: {e.stderr}")

    def do_addcustomer(self, arg):
        """Add a new customer or modify an existing one to the service database. Usage: addcustomer --recipe RECIPEFILE --username USERNAME"""
        self.run_script('netprovisioncli_admin.py', arg)
        
    def do_generate(self, arg):
        """Generate configuration. Usage: generate --customer-name CUSTOMER_NAME"""
        self.run_script('netprovisioncli_generate.py', arg)

    def do_deploy(self, arg):
        """Deploy configuration. Usage: deploy --customer-name CUSTOMER_NAME --access-device ACCESS_DEVICE --pe-device PE_DEVICE --username USERNAME"""
        self.run_script('netprovisioncli_deploy.py', arg)

    def do_commitdb(self, arg):
        """Query deployed configs and audit logs from the database. Usage: commitdb -h"""
        self.run_script('netprovisioncli_commitdb.py', arg)

    def do_export(self, arg):
        """Export customer, device, and deployment data to an XLS (Excel) file. Usage: export --export"""
        self.run_script('netprovisioncli_export.py', arg)

    def do_query(self, arg):
        """Query the database for customer or device details. Usage: query -h"""
        self.run_script('netprovisioncli_query.py', arg)

    def do_exit(self, arg):
        """Exit to the main shell."""
        return True

    def do_help(self, arg):
        """Customized help command"""
        customer_commands = ['addcustomer', 'generate', 'deploy', 'commitdb', 'export', 'query']
        general_commands = [cmd for cmd in self.get_all_commands() if cmd not in customer_commands]

        self.poutput("\nCustomer Service Provisioning commands:")
        for cmd in sorted(customer_commands):
            doc = getattr(self, 'do_' + cmd).__doc__
            if doc:
                self.poutput(f"{cmd} - {doc.splitlines()[0]}")
            else:
                self.poutput(f"{cmd} - No description available.")

        self.poutput("\nGeneral operations:")
        for cmd in sorted(general_commands):
            doc = getattr(self, 'do_' + cmd).__doc__
            if doc:
                self.poutput(f"{cmd} - {doc.splitlines()[0]}")
            else:
                self.poutput(f"{cmd} - No description available.")

    def get_all_commands(self):
        """Get all command names"""
        return [name[3:] for name in dir(self) if name.startswith('do_')]

class AdminShell(cmd2.Cmd):
    prompt = 'NetProvisionCLI/admin> '

    def __init__(self, parent_shell):
        super().__init__()
        self.parent_shell = parent_shell
        self.netprovisioncli_scripts_path = parent_shell.netprovisioncli_scripts_path

    def run_script(self, script_name, args):
        script_path = os.path.join(self.netprovisioncli_scripts_path, script_name)
        if not os.path.exists(script_path):
            self.perror(f"Script {script_name} not found at path {script_path}")
            return
        try:
            result = subprocess.run(['python', script_path] + args.split(), check=True, capture_output=True, text=True)
            self.poutput(result.stdout)
        except subprocess.CalledProcessError as e:
            self.perror(f"Error executing {script_name}: {e.stderr}")

    def do_adduser(self, arg):
        """Add a new user. Usage: adduser --username USERNAME"""
        self.run_script('netprovisioncli_adduser.py', arg)

    def do_testuser(self, arg):
        """Test a new user. Usage: testuser"""
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        script_path = os.path.join(self.netprovisioncli_scripts_path, 'netprovisioncli_testuser.py')
        if not os.path.exists(script_path):
            self.perror(f"Script netprovisioncli_testuser.py not found at path {script_path}")
            return
        
        try:
            process = subprocess.Popen(['python', script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=f"{username}\n{password}\n")
            if stdout:
                self.poutput(stdout)
            if stderr:
                self.perror(stderr)
        except Exception as e:
            self.perror(f"Error executing netprovisioncli_testuser.py: {e}")

    def do_backup(self, arg):
        """Export MongoDB and InfluxDB data to JSON files. Usage: backup -h"""
        self.run_script('netprovisioncli_backup.py', arg)

    def do_restore(self, arg):
        """Restore MongoDB and InfluxDB data from JSON files. BE CAREFUL! Usage: restore -h"""
        self.run_script('netprovisioncli_restore.py', arg)

    def do_settings(self, arg):
        """View or modify the data sources for NetProvisionCLI. Usage: settings -h"""
        self.run_script('netprovisioncli_settings.py', arg)

    def do_exit(self, arg):
        """Exit to the main shell."""
        return True

    def do_help(self, arg):
        """Customized help command"""
        admin_commands = ['adduser', 'testuser', 'backup', 'restore', 'settings']
        general_commands = [cmd for cmd in self.get_all_commands() if cmd not in admin_commands]

        self.poutput("\nAdmin operations:")
        for cmd in sorted(admin_commands):
            doc = getattr(self, 'do_' + cmd).__doc__
            if doc:
                self.poutput(f"{cmd} - {doc.splitlines()[0]}")
            else:
                self.poutput(f"{cmd} - No description available.")

        self.poutput("\nGeneral operations:")
        for cmd in sorted(general_commands):
            doc = getattr(self, 'do_' + cmd).__doc__
            if doc:
                self.poutput(f"{cmd} - {doc.splitlines()[0]}")
            else:
                self.poutput(f"{cmd} - No description available.")

    def get_all_commands(self):
        """Get all command names"""
        return [name[3:] for name in dir(self) if name.startswith('do_')]

if __name__ == '__main__':
    app = NetProvisionShell()
    app.cmdloop()
