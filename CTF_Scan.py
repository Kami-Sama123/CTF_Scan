import subprocess
import re
import pyperclip
import os
import pwd
from tqdm import tqdm

# ASCII Art and Introo
def intro():
    ascii_art = """
                                                                   ,-,
                                                             _.-=;~ /_
                                                          _-~   '     ;.
                                                      _.-~     '   .-~-~`-._
                                                _.--~~:.             --.____88
                              ____.........--~~~. .' .  .        _..-------~~
                     _..--~~~~               .' .'             ,'
                 _.-~                        .       .     ` ,'
               .'                                    :.    ./
             .:     ,/          `                   ::.   ,'
           .:'     ,(            ;.                ::. ,-'
          .'     ./'.`.     . . /:::._______.... _/:.o/
         /     ./'. . .)  . _.,'               `88;?88|
       ,'  . .,/'._,-~ /_.o8P'                  88P ?8b
    _,'' . .,/',-~    d888P'                    88'  88|
 _.'~  . .,:oP'        ?88b              _..--- 88.--'8b.--..__
:     ...' 88o __,------.88o ...__..._.=~- .    `~~   `~~      ~-._ Seal _.
`.;;;:='    ~~            ~~~                ~-    -       -   -
"""

    text = "CTF SCAN made by Kami"

    art_length = len(max(ascii_art.splitlines(), key=len))

    separator = "_" * art_length

    combined_output = f"{separator}\n{ascii_art}\n{separator}\n{text}"

    print(combined_output)

# Directory Creator
class DirectoryCreator:
    def __init__(self):
        self.new_directory_path = None

    def create_directory(self, location, directory_name):
        try:
            if location.lower() == 'here':
                location = os.getcwd() 
            elif not os.path.isabs(location):
                location = os.path.join(os.getcwd(), location)
                
            if not self.is_valid_directory_name(directory_name):
                raise ValueError("Invalid directory name. Please follow the naming conventions.")

            self.new_directory_path = os.path.join(location, directory_name)
            os.makedirs(self.new_directory_path, exist_ok=True)


            uid = pwd.getpwnam(os.getlogin()).pw_uid
            gid = pwd.getpwnam(os.getlogin()).pw_gid
            os.chown(self.new_directory_path, uid, gid)

            print(f"Directory '{directory_name}' created successfully at '{self.new_directory_path}'")

            os.chdir(self.new_directory_path)

            return True
        except PermissionError as pe:
            print(f"Error: {pe}")
            question = input(
                "\n\033[91mInsufficient privileges to change directory. Do you want to proceed with elevated privileges (sudo)? (y/n): \033[0m")
            if question.lower() == 'y':
                sudo_password = input("\033[93mEnter your sudo password: \033[0m")
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
        if not re.match("^[a-zA-Z0-9_-]*$", directory_name):
            return False

        reserved_keywords = {'dev', 'proc', 'sys', 'tmp', 'bin', 'sbin', 'etc'}
        if directory_name.lower() in reserved_keywords:
            return False

        if directory_name.startswith('.'):
            return False

        if directory_name in {'..', '.'}:
            return False
            
        return True


# Scanner
class Scanner:
    def extract_open_ports(self, file_path):
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

    def run_second_scan(self, open_ports, target):
        if open_ports:
            try:
                ports_str = ','.join(open_ports)
                output_file = "full.txt"
                print("\n##### RUNNING SERVICES SCAN #####\n")
                with open(output_file, 'w') as output_file_obj:
                    subprocess.run(['sudo', 'nmap', '-p', ports_str, '-sCV', '-n', '-Pn', '-oN', output_file, target], check=True, encoding='utf-8', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                print("\n##### SCAN ENDED #####)\n")
                print("\nSecond scan completed. Results saved in info.txt\n")
                relevant_info = self.extract_service_info(output_file)
                self.save_to_file(relevant_info, "info.txt", target)
                choice = input("\033[92mDo you want to see a preview of the extracted information? (yes/no): \033[0m").lower()
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
    def save_to_file(info, filename, target):
        with open(filename, "w") as file:
            file.write(f"This is the target machine IP: {target}\n")
            for line in info:
                file.write(line + "\n")

    def first_scan(self, target):
        print("\n#### RUNNING FULLPORTS SCAN#####\n")
        with tqdm(total=100, desc="Scanning", unit="%", bar_format="{desc}: {percentage:.0f}%|{bar}|") as pbar:
            try:
                subprocess.run(['sudo', 'nmap', '-sS', '-p-', '--open', '--min-rate', '2000', '-n', '-Pn', '-oG', 'FullPorts.gnmap', target], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print(f"Error during the scan: {e}")
            pbar.update(100)
        print("\n#### SCAN END #####\n")
        open_ports = self.extract_open_ports('FullPorts.gnmap')
        if open_ports:
            ports_str = ', '.join(open_ports)
            copy_to_clipboard(ports_str)
        return open_ports

    def second_scan(self, target):
        open_ports = self.first_scan(target)
        if open_ports:
            self.run_second_scan(open_ports, target)


def copy_to_clipboard(data):
    try:
        pyperclip.copy(data)
        print("\033[92mOpen ports copied to clipboard.\033[0m")
    except pyperclip.PyperclipException as e:
        print(f"Error copying to clipboard: {e}")


def ping_check(target):
    try:
        response = subprocess.run(['ping', '-c', '1', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if response.returncode == 0:
            ttl_line = [line for line in response.stdout.split('\n') if 'ttl=' in line][0]
            ttl_value = int(re.search(r'ttl=(\d+)', ttl_line).group(1))

            if ttl_value in range(64, 129):
                print(f"\n\033[92mTarget IP ({target}) is up and responding to ping. The target machine is likely running a Linux-based operating system.\033[0m")
            elif ttl_value in range(128, 256):
                print(f"\n\033[92mTarget IP ({target}) is up and responding to ping. The target machine is likely running a Windows-based operating system.\033[0m")
            else:
                print(f"\n\033[92mTarget IP ({target}) is up and responding to ping, but the TTL value ({ttl_value}) does not match the expected range for Linux or Windows.\033[0m")
            return True
        else:
            print(f"\n\033[92mTarget IP ({target}) is down and not responding to ping.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking ping: {e}")
        return False


def main():
    try:
        intro()

        target = input("\n\033[93mProvide the target IP address or hostname: \033[0m")
        if not re.match(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|([a-zA-Z0-9.-]+)$", target):
            print("Invalid target. Please enter a valid IP address")
            return

        if not ping_check(target):
            return

        question = input(
            "\n\033[91mThis program creates files. If a file exists with the same name, it will overwrite it. "
            "To avoid future problems, the program will move or create a new directory.\n\n"
            "Do you want to proceed with the process of creating a directory? (y/n): \033[0m")

        if question.lower() == 'y':
            directory_creator = DirectoryCreator()
            while True:
                directory_name = input("\n\033[91mWrite the name of the new directory: \033[0m")
                if directory_creator.is_valid_directory_name(directory_name):
                    directory_location = input(
                        "\n\033[91mSpecify the location where you want to create the new directory. "
                        "If you want to store the directory in your current directory, just type 'here'.\n"
                        "Example: '/path/to/store/' or 'here': \033[0m")
                    directory_creator.create_directory(directory_location, directory_name)
                    break
                else:
                    print("\nThe name you wrote is not valid for a directory. Please be careful!!")

        print("\n\033[91mPerfect, Now for the next scan we will perform a Stealth Scan so we are going to need sudo privileges\n\033[0m")

        scanner = Scanner()
        scanner.second_scan(target)
    except KeyboardInterrupt:
        print("\ABORTING...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return


if __name__ == "__main__":
    main()