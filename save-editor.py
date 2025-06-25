import datetime
import json
import os
import time

import colorama
from colorama import Back, Fore, Style

colorama.init()

save_file_path = os.path.expandvars(r"%APPDATA%\Godot\app_userdata\Psycho Patrol R\newgame.save") # Default save file path

def load_save_file():
    global save_file_path
    try:
        with open(save_file_path, "r") as file:
            lines = file.readlines()
            # Process the save file as a collection of separate JSON objects
            save_data = {}
            for line in lines:
                if line.strip():  # Skip empty lines
                    try:
                        obj = json.loads(line)
                        # Use the "id" field as key if it exists
                        if "id" in obj:
                            save_data[obj["id"]] = obj
                        # Otherwise add to the save_data dictionary using another unique identifier
                        elif "type" in obj:
                            # Use type as part of the key for objects without ID
                            key = f"{obj['type']}_{len([k for k in save_data if k.startswith(obj['type'])])}"
                            save_data[key] = obj
                    except json.JSONDecodeError:
                        print(Fore.YELLOW + f"Warning: Could not parse line: {line}" + Style.RESET_ALL)
                        continue
            return save_data
    except FileNotFoundError:
        print(Fore.RED + f"File {save_file_path} was not found." + Style.RESET_ALL)
        new_path = input("Please enter the path to the save file: ")
        try:
            with open(new_path, "r") as file:
                lines = file.readlines()
                save_file_path = new_path  # Update the save file path
                
                # Process the save file as a collection of separate JSON objects
                save_data = {}
                for line in lines:
                    if line.strip():  # Skip empty lines
                        try:
                            obj = json.loads(line)
                            # Use the "id" field as key if it exists
                            if "id" in obj:
                                save_data[obj["id"]] = obj
                            # Otherwise add to the save_data dictionary using another unique identifier
                            elif "type" in obj:
                                # Use type as part of the key for objects without ID
                                key = f"{obj['type']}_{len([k for k in save_data if k.startswith(obj['type'])])}"
                                save_data[key] = obj
                        except json.JSONDecodeError:
                            print(Fore.YELLOW + f"Warning: Could not parse line: {line}" + Style.RESET_ALL)
                            continue
                return save_data
        except FileNotFoundError:
            print(Fore.RED + f"File {new_path} was not found." + Style.RESET_ALL)
            return None


def save_save_file(data):
    with open(save_file_path, "w") as file:
        for key, value in data.items():
            file.write(json.dumps(value, separators=(",", ":")) + "\n")

def count_unlocked_weapons(save_data):
    # Count weapons that have "unlocked": true
    weapon_count = 0
    for key, value in save_data.items():
        if isinstance(value, dict) and value.get('type') == 'weapon' and value.get('unlocked') == True:
            weapon_count += 1
    return weapon_count

def get_global_data(save_data):
    # Find the global data object which contains money and other global settings
    for key, value in save_data.items():
        if isinstance(value, dict) and value.get('type') == 'global':
            return value
    # If no global data found, create a default one
    return {"type": "global", "money": 0}

def print_status(save_data):
    global_data = get_global_data(save_data)
    levels_unlocked = global_data.get("levels_unlocked", 0)  # Use .get() with default in case key doesn't exist
    weapons_unlocked = count_unlocked_weapons(save_data)
    money = global_data.get("money", 0)

    print("Psycho Patrol R Save Editor created by Aholicknight")
    print("Current Levels Unlocked:", Fore.RED + str(levels_unlocked) + Style.RESET_ALL)
    print("Number of Weapons Unlocked:", Fore.RED + str(weapons_unlocked) + Style.RESET_ALL)
    print("Current Money:", Fore.GREEN + str(money) + Style.RESET_ALL)

def clear_console():
    command = 'cls' if os.name == 'nt' else 'clear'
    os.system(command)

def main():
    save_data = load_save_file()
    if save_data is None:
        return
    
    global_data = get_global_data(save_data)

    print_status(save_data)
    
    while True:
        print("\nOptions:")
        print("1) Edit levels unlocked")
        print("2) Unlock all weapons")
        print("3) Edit Money")
        print("4) Load/Backup Current Save File")
        print("5) " + Fore.GREEN + "Unlock" + Style.RESET_ALL + " all implants")
        print("6) " + Fore.RED + "Lock" + Style.RESET_ALL + " all implants")
        print("10) Exit")

        choice = input("Enter your choice: ")

        if choice == "1": # unlock all levels
            new_levels_unlocked = int(input("Enter new levels unlocked (1-19): "))
            if 1 <= new_levels_unlocked <= 19:
                global_data["levels_unlocked"] = new_levels_unlocked
                save_save_file(save_data)
                print("Levels unlocked updated.")
                clear_console()
                print_status(save_data)
            else:
                print("Invalid input.")

        elif choice == "2": # unlock all weapons
            weapon_count = 0
            weapons_unlocked = 0
            for key, value in save_data.items():
                if isinstance(value, dict) and value.get('type') == 'weapon':
                    weapon_count += 1
                    if value.get('unlocked') == True:
                        weapons_unlocked += 1
                    else:
                        value['unlocked'] = True
            
            if weapons_unlocked == weapon_count:
                print(f"{Fore.RED}All weapons are already unlocked.{Style.RESET_ALL}")
            elif weapon_count == 0:
                print(f"{Fore.YELLOW}No weapons found in save file.{Style.RESET_ALL}")
            else:
                save_save_file(save_data)
                print(f"{Fore.GREEN}Unlocked {weapon_count - weapons_unlocked} additional weapons!{Style.RESET_ALL}")
                clear_console()
                print_status(save_data)
        
        elif choice == "3": # edit money
            global_data = get_global_data(save_data)
            current_money = global_data.get("money", 0)
            print(f"Current Money: {Fore.GREEN}{current_money}{Style.RESET_ALL}")
            new_money = input("Enter new money amount: ")
            try:
                new_money = int(new_money)
                global_data["money"] = new_money
                save_save_file(save_data)
                print(f"Money updated to: {Fore.GREEN}{new_money}{Style.RESET_ALL}")
                clear_console()
                print_status(save_data)
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
        
        elif choice == "4": # create and load save file backup
            backup_file_path = save_file_path.replace('.save', '.bak')

            if os.path.exists(backup_file_path):
                creation_time = os.path.getctime(backup_file_path)
                creation_date = datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %I:%M:%S %p")
                print(Fore.YELLOW + f"Backup file created on {creation_date}" + Style.RESET_ALL)

            print("\nSave File Operations:")
            print(Fore.GREEN + "1) Backup current save file" + Style.RESET_ALL)
            print(Fore.RED + "2) Load from backup" + Style.RESET_ALL)
            print("3) Go back to the main menu")

            operation_choice = input("Enter your choice: ")

            if operation_choice == "1":
                if os.path.exists(backup_file_path): # delete existing backup file if it exists
                    os.remove(backup_file_path)
                with open(save_file_path, 'r') as original: data = original.read()
                with open(backup_file_path, 'w') as backup: backup.write(data)
                print("Backup created.")
            elif operation_choice == "2":
                with open(backup_file_path, 'r') as backup: data = backup.read()
                with open(save_file_path, 'w') as original: original.write(data)
                print("Backup loaded. Going back to main menu...")
                time.sleep(2) # wait 2 seconds before going back to main menu to print stats
                clear_console()
                print_status(save_data)
            else:
                clear_console()
                print_status(save_data)
        
        elif choice == "10": # exit
            print("Exiting...")
            break


if __name__ == "__main__":
    main()