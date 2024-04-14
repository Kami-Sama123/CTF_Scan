# CTF_Scan
Automate network analysis with this Python program that performs Nmap stealth scans, extracts open ports, and gathers detailed service information. Ideal for quick and efficient security assessments.

## Overview
This Python program automates the process of analyzing a network using Nmap, with a focus on a stealth scan. It streamlines the process of conducting a stealth scan, extracting open ports, and running a second scan on those ports to gather detailed service information.

## Features
1. **Directory Creation:**
   - Allows the user to create a new directory to store scan results.
   - Checks for valid directory names and ensures naming conventions are followed.
   - Handles permission issues by prompting the user to proceed with elevated privileges if necessary.

2. **Stealth Scan:**
   - Executes a stealth scan using Nmap with sudo privileges to discover open ports.
   - Saves the results in a file named `FullPorts.gnmap`.

3. **Open Port Extraction:**
   - Reads the `FullPorts.gnmap` file and extracts open ports using regular expressions.
   - Option to copy the list of open ports to the clipboard.

4. **Second Scan:**
   - Conducts a second scan on the open ports using Nmap to gather detailed service information.
   - Saves the results in a file named `info.txt`.

5. **Service Information Extraction:**
   - Reads the `info.txt` file and extracts detailed service information using regular expressions.
   - Displays the extracted information, including port, state, service, and version.

## How to Use
1. **Input Target IP Address:**
   - Enter the target IP address when prompted.

2. **Directory Creation:**
   - Decide whether to create a new directory to store scan results.
   - Provide a valid directory name and location.

3. **Stealth Scan:**
   - The program will perform a stealth scan using Nmap with sudo privileges.
   - Results will be saved in `FullPorts.gnmap`.

4. **Open Port Extraction:**
   - The program will extract open ports from `FullPorts.gnmap`.
   - Option to copy the open ports to the clipboard.

5. **Second Scan:**
   - If open ports are found, a second scan will be conducted using Nmap.
   - Results will be saved in `info.txt`.

6. **Service Information Extraction:**
   - The program will extract and display detailed service information from `info.txt`.

## Notes
- This program is specifically designed for automating Nmap stealth scans.
- It may overwrite existing files with the same name.
- Ensure you have the necessary permissions to create directories and run Nmap scans.
- Use the program responsibly and only on networks where you have permission.

## Requirements
- Python 3.x
- Nmap tool installed
- `pyperclip` library for clipboard operations (install using `pip install pyperclip`)

## Disclaimer
Use this program responsibly and in compliance with applicable laws. Unauthorized scanning of networks without permission is illegal and unethical. The authors are not responsible for any misuse or damage caused by the program.
