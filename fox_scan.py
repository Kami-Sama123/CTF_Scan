import subprocess
import re
import pyperclip
import os

def create_directory(location, directory_name):
    try:
        if location.lower() == 'here':
            location = os.getcwd()  # Use the current working directory
        elif not os.path.isabs(location):
            location = os.path.join(os.getcwd(), location)  # Make it an absolute path

        # Check if the directory name is valid
        if not is_valid_directory_name(directory_name):
            raise ValueError("Invalid directory name. Please follow the naming conventions.")

        # Create the new directory
        new_directory_path = os.path.join(location, directory_name)
        os.makedirs(new_directory_path, exist_ok=True)

        print(f"Directory '{directory_name}' created successfully at '{new_directory_path}'")

        # Change the current working directory to the newly created directory
        os.chdir(new_directory_path)

        return True
    except PermissionError as pe:
        print(f"Error: {pe}")
        question = input("\nInsufficient privileges to change directory. Do you want to proceed with elevated privileges (sudo)? (y/n): ")
        if question.lower() == 'y':
            sudo_password = input("Enter your sudo password: ")
            sudo_command = f"echo {sudo_password} | sudo -S chown $USER:$USER {new_directory_path}"
            subprocess.run(sudo_command, shell=True)
            os.chdir(new_directory_path)
            print(f"Directory '{directory_name}' created successfully at '{new_directory_path}' with elevated privileges.")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False


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

def extract_open_ports(file_path):
    try:
        with open(file_path, 'r') as file:
            # Read the content of the file
            content = file.read()

            # Use regex to extract open ports
            open_ports_match = re.search(r'(\d+)/open/tcp//[^/]*/', content)

            if open_ports_match:
                open_ports = re.findall(r'(\d+)/open/tcp//[^/]*/', content)
                
                if open_ports:
                    return open_ports
                else:
                    print("No open ports found.")
                    return []
            else:
                print("No open ports found.")
                return []
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []

def copy_to_clipboard(data):
    try:
        pyperclip.copy(data)
        print("Open ports copied to clipboard.")
    except pyperclip.PyperclipException as e:
        print(f"Error copying to clipboard: {e}")

def run_second_scan(open_ports, target):
    if open_ports:
        try:
            # Create a string of open ports separated by commas
            ports_str = ','.join(open_ports)

            # Run the second scan
            subprocess.run(['sudo', 'nmap', '-p', ports_str, '-sCV', '-n', '-Pn', '-oN', 'info.txt', target], check=True)

            print("Second scan completed. Results saved in info.txt")

            # Extract and print service information from info.txt
            extract_service_info('info.txt')
        except subprocess.CalledProcessError as e:
            print(f"\nError during the second scan: {e}")
    else:
        print("\nNo open ports to perform the second scan.")

def extract_service_info(file_path):
    try:
        with open(file_path, 'r') as file:
            # Read the content of the file
            content = file.read()

            # Use regex to extract service information
            service_info_match = re.search(r'PORT\s+STATE\s+SERVICE\s+VERSION\n(.+?)\n# Nmap done', content, re.DOTALL)

            if service_info_match:
                service_info_str = service_info_match.group(1)
                # Use regex to extract relevant details for each service
                service_details = re.findall(r'(\d+/tcp)\s+(\w+)\s+(\w+)\s+([^/]+)/', service_info_str)

                if service_details:
                    # Print the header
                    print("\nPorts         State/Service        Version")
                    # Print the extracted information for each service
                    for details in service_details:
                        print(f"{details[0]}    {details[1]}  {details[2]}          {details[3]}")
                else:
                    print("\nNo service information found.")
            else:
                print("\nNo service information found.")
    except FileNotFoundError:
        print(f"\nFile '{file_path}' not found.")

# Prompt user for target IP address
target = input("\nProvide the target IP address: ")

question = input("\nThis program creates files. If a file exists with the same name, it will overwrite it. "
                     "To avoid future problems, the program will move or create a new directory.\n\n"
                     "Do you want to proceed with the process of creating a directory? (y/n): ")

if question.lower() == 'y':
    while True:
        directory_name = input("\nWrite the name of the new directory: ")
        if is_valid_directory_name(directory_name):
            directory_location = input(
                "\nSpecify the location where you want to create the new directory. "
                "If you want to store the directory in your current directory, just type 'here'.\n"
                "Example: '/path/to/store/' or 'here': "
            )
            create_directory(directory_location, directory_name)
            break
        else:
            print("\nThe name you wrote is not valid for a directory. Please be careful!!")
    
# Run nmap scan and save results to FullPorts.gnmap
print("\nPerfect, Now for the next scan we will perform a Stealth Scan so we are going to need sudo privileges\n")
subprocess.run(['sudo', 'nmap', '-sS', '-p-', '--open', '--min-rate', '2000', '-n', '-Pn', '-oG', 'FullPorts.gnmap', target], check=True)

# Extract open ports from FullPorts.gnmap
open_ports = extract_open_ports('FullPorts.gnmap')

# Copy open ports to clipboard
if open_ports:
    ports_str = ', '.join(open_ports)
    copy_to_clipboard(ports_str)

    # Run the second scan using the open ports
    run_second_scan(open_ports, target)
