import subprocess
import re
import pyperclip
import os
import pwd
from tqdm import tqdm


class DirectoryCreator:
    def __init__(self):
        self.new_directory_path = None

    def create_directory(self, location, directory_name):
        try:
            if location.lower() == 'here':
                location = os.getcwd()  # Use the current working directory
            elif not os.path.isabs(location):
                location = os.path.join(os.getcwd(), location)  # Make it an absolute path

            # Check if the directory name is valid
            if not self.is_valid_directory_name(directory_name):
                raise ValueError("Invalid directory name. Please follow the naming conventions.")

            # Create the new directory
            self.new_directory_path = os.path.join(location, directory_name)
            os.makedirs(self.new_directory_path, exist_ok=True)

            # Change the ownership of the directory to the current user
            uid = pwd.getpwnam(os.getlogin()).pw_uid
            gid = pwd.getpwnam(os.getlogin()).pw_gid
            os.chown(self.new_directory_path, uid, gid)

            print(f"Directory '{directory_name}' created successfully at '{self.new_directory_path}'")

            # Change the current working directory to the newly created directory
            os.chdir(self.new_directory_path)

            return True
        except PermissionError as pe:
            print(f"Error: {pe}")
            question = input(
                "\nInsufficient privileges to change directory. Do you want to proceed with elevated privileges (sudo)? (y/n): ")
            if question.lower() == 'y':
                sudo_password = input("Enter your sudo password: ")
                sudo_command = f"echo {sudo_password} | sudo -S chown $USER:$USER {self.new_directory_path}"
                subprocess.run(sudo_command, shell=True)
                os.chdir(self.new_directory_path)
                print(
                    f"Directory '{directory_name}' created successfully at '{self.new_directory_path}' with elevated privileges.")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False

    @staticmethod
    def is_valid_directory_name(directory_name):
        # Avoid spaces and special characters
        if not re.match("^[a-zA-Z0-9_-]*$", directory_name):
            return False

        reserved_keywords = {'dev', 'proc', 'sys', 'tmp', 'bin', 'sbin', 'etc'}
        if directory_name.lower() in reserved_keywords:
            return False

        if directory_name.startswith('.'):
            return False

        if directory_name in {'..', '.'}:
            return False

        if directory_name.lower().startswith('/dev/'):
            return False

        return True


class PortScanner:
    @staticmethod
    def extract_open_ports(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                open_ports_match = re.findall(r'(\d+)/open/', content)
                if open_ports_match:
                    open_ports = [port for port in open_ports_match]
                    return open_ports
                else:
                    print("No open ports found.")
                    return []
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return []

    @staticmethod
    def run_second_scan(open_ports, target):
        if open_ports:
            try:
                ports_str = ','.join(open_ports)
                # Specify a user-writable file path for the output
                output_file = os.path.join(os.getcwd(), 'full.txt')
                print("\n##### RUNNING SERVICES SCAN #####\n")
                with open(os.devnull, 'w') as devnull:
                    subprocess.run(['sudo', 'nmap', '-p', ports_str, '-sCV', '-n', '-Pn', '-oN', 'full.txt', target], check=True,encoding='utf-8', stdout=devnull, stderr=subprocess.STDOUT)
                print("\n##### SCAN ENDED #####)\n")
                print("\nSecond scan completed. Results saved in info.txt\n")
                relevant_info = PortScanner.extract_service_info(output_file)
                PortScanner.save_to_file(relevant_info, "info.txt")
                choice = input("Do you want to see a preview of the extracted information? (yes/no): ").lower()
                if choice == "yes":
                    print("\n".join(relevant_info))
                print("Information saved to info.txt")
            except subprocess.CalledProcessError as e:
                print(f"\nError during the second scan: {e}")
        else:
            print("\nNo open ports to perform the second scan.")

    @staticmethod
    def extract_service_info(file_path):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                relevant_info = []
                for line in lines:
                    if "PORT" in line and "STATE" in line and "SERVICE" in line and "VERSION" in line:
                        relevant_info.append(line.strip())
                    elif "/tcp" in line:
                        relevant_info.append(line.strip())
                return relevant_info
        except FileNotFoundError:
            print(f"\nFile '{file_path}' not found.")

    @staticmethod
    def save_to_file(info, filename):
        with open(filename, "w") as file:
            for line in info:
                file.write(line + "\n")


def copy_to_clipboard(data):
    try:
        pyperclip.copy(data)
        print("Open ports copied to clipboard.")
    except pyperclip.PyperclipException as e:
        print(f"Error copying to clipboard: {e}")


def ping_check(target):
    try:
        # Perform the ping check
        response = subprocess.run(['ping', '-c', '1', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if response.returncode == 0:
            # Extract the TTL value from the ping response
            ttl_line = [line for line in response.stdout.split('\n') if 'ttl=' in line][0]
            ttl_value = int(re.search(r'ttl=(\d+)', ttl_line).group(1))

            # Determine the operating system based on the TTL value
            if ttl_value in range(64, 129):
                print(f"\nTarget IP ({target}) is up and responding to ping. The target machine is likely running a Linux-based operating system.")
            elif ttl_value in range(128, 256):
                print(f"\nTarget IP ({target}) is up and responding to ping. The target machine is likely running a Windows-based operating system.")
            else:
                print(f"\nTarget IP ({target}) is up and responding to ping, but the TTL value ({ttl_value}) does not match the expected range for Linux or Windows.")
            return True
        else:
            print(f"\nTarget IP ({target}) is down and not responding to ping.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking ping: {e}")
        return False


def main():
    try:
        # Prompt user for target IP address
        target = input("\nProvide the target IP address: ")

        if not ping_check(target):
            return

        question = input(
            "\nThis program creates files. If a file exists with the same name, it will overwrite it. "
            "To avoid future problems, the program will move or create a new directory.\n\n"
            "Do you want to proceed with the process of creating a directory? (y/n): ")

        if question.lower() == 'y':
            directory_creator = DirectoryCreator()
            while True:
                directory_name = input("\nWrite the name of the new directory: ")
                if directory_creator.is_valid_directory_name(directory_name):
                    directory_location = input(
                        "\nSpecify the location where you want to create the new directory. "
                        "If you want to store the directory in your current directory, just type 'here'.\n"
                        "Example: '/path/to/store/' or 'here': ")
                    directory_creator.create_directory(directory_location, directory_name)
                    break
                else:
                    print("\nThe name you wrote is not valid for a directory. Please be careful!!")

        # Run nmap scan and save results to FullPorts.gnmap
        print("\nPerfect, Now for the next scan we will perform a Stealth Scan so we are going to need sudo privileges\n")
        
        print("\n#### RUNNING FULLPORTS SCAN#####\n")
        
        with tqdm(total=100, desc="Scanning", unit="%", bar_format="{desc}: {percentage:.0f}%|{bar}|") as pbar:
            try:
                subprocess.run(['sudo', 'nmap', '-sS', '-p-', '--open', '--min-rate', '2000', '-n', '-Pn', '-oG', 'FullPorts.gnmap', target], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print(f"Error during the scan: {e}")
            pbar.update(100)
        print("\n#### SCAN END #####\n")
        open_ports = PortScanner.extract_open_ports('FullPorts.gnmap')

        # Copy open ports to clipboard
        if open_ports:
            ports_str = ', '.join(open_ports)
            copy_to_clipboard(ports_str)

            # Run the second scan using the open ports
            PortScanner.run_second_scan(open_ports, target)
    except KeyboardInterrupt:
        print("\ABORTING...")
    except Exception as e:
            print(f"Unexpected error: {e}")
            return

if __name__ == "__main__":
    main()
