import argparse
import json
import os
import base64
import shutil
import logging
import platform
from rich.console import Console
from rich.theme import Theme

CUSTOM_THEME = Theme({
    "Title": "bold Magenta",
    "Info": "blue",
    "Notice": "bold green",
    "Error": "bold red"
})

console = Console(theme=CUSTOM_THEME)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def wait_for_key_press():
    console.print("\nPress any key to continue...", style="yellow")
    if platform.system().lower() == 'windows':
        import msvcrt
        return msvcrt.getch()
    else:
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class Manager:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def create_admin(self):
        if os.path.exists("manager_info.json"):
            console.print("Admin info already exists.", style='Error')
            exit()
        
        clear_screen()
        admin_info = {
            "username": self.username, 
            "password": base64.b64encode(self.password.encode("utf-8")).decode("utf-8")
        }
        
        with open("manager_info.json", "w") as admin_file:
            json.dump(admin_info, admin_file)
        console.print("Admin info created successfully.", style="Notice")
        logger.info("Manager has created successfully")
        wait_for_key_press()
    
    def login(self):
        data = {}
        try:
            with open("manager_info.json", 'r') as file:
                data = json.load(file)
        except FileExistsError:
            console.print("Manager is not defined.", style='Error')
            console.print("Create Manager first.", style='Error')
            exit()
        
        if data['username'] == self.username and base64.b64decode(data['password']).decode("utf-8") == self.password:
            clear_screen()
            console.print("Login successful.", style="Notice")
            logger.info("Manager has logged in successfully")
            wait_for_key_press()
            self.manager_menu()
        else:
            console.print("Invalid username or password.", style='Error')
            exit()
            
    def manager_menu(self):
        while True:
            clear_screen()
            console.print(f"|Welcome, Manager {self.username}!|\n", style='Title')
            console.print("What would you like to do?", style="Info")
            console.print("1. Deactivate a user")
            console.print("2. Activate a user")
            console.print("3. Delete database")
            console.print("4. Log out")

            choice = input("Enter your choice: ")
            if choice == '1':
                Manager.deactivate_user_menu()

            elif choice == '2':
                Manager.activate_user_menu()
            
            elif choice == '3':
                self.purge_data(is_run=True)
                wait_for_key_press()
            
            elif choice == '4':
                console.print("You have been successfully logged out.", style="Notice")
                logger.info("End of Manager program")
                exit()

            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()
        
    def load_users():
        if not os.path.exists("emails_and_usernames.json"):
            console.print("User info file not found.", style="Error")
            wait_for_key_press()
            return
        
        with open("emails_and_usernames.json", "r") as user_file:
            users_data = json.load(user_file)
        return list(users_data["usernames"].values())

    def deactivate_user(username):
        path = 'users/' + username + '/' + username + ".json"
        user_data = {}
        with open(path , 'r') as file :
            user_data = json.load(file)
        
        if user_data["active"] == False:
            console.print(f"User ({username}) has already been deactivated.", style='Error')
            wait_for_key_press()
            return
        
        user_data["active"] = False
        
        with open (path , 'w') as file:
            json.dump(user_data,file,indent=4)
        
        console.print(f"User ({username}) has been deactivated successfully.", style='Notice')
        logger.info(f"User ({username}) deactivated by Manager")
        wait_for_key_press()

    def deactivate_user_menu():
        clear_screen()
        console.print(f"|Deactivating Users|\n", style='Title')
        console.print("Available users:" , style='Info')
        all_usernames = Manager.load_users()
        for username in all_usernames:
            console.print("-", username)
        selected_usernames = list(map(lambda x:x.strip(),input("Enter usernames to deactive (format:'user1,user2') or press ENTER to go back: ").split(',')))
        
        if selected_usernames[0] == '':
            return
        
        for username in selected_usernames:
            Manager.deactivate_user(username)

    def activate_user(username):
        path = 'users/' + username + '/' + username + ".json"
        user_data = {}
        with open(path , 'r') as file :
            user_data = json.load(file)
        
        if user_data["active"] == True:
            console.print(f"User ({username}) is active." , style='Error')
            wait_for_key_press()
            return
        
        user_data["active"] = True
        
        with open (path , 'w') as file:
            json.dump(user_data,file,indent=4)
        
        console.print(f"User ({username}) has been activated successfully.", style='Notice')
        logger.info(f"User ({username}) activated by Manager")
        wait_for_key_press()
        
    def activate_user_menu():
        clear_screen()
        console.print(f"|Deactivating Users|\n", style='Title')
        console.print("Available users:" , style='Info')
        all_usernames = Manager.load_users()
        for username in all_usernames:
            console.print("-", username)
        selected_usernames = list(map(lambda x: x.strip(), input("Enter usernames to activate (format:'user1,user2') or press ENTER to go back: ").split(',')))
        
        if selected_usernames[0] == '':
            return
        
        for username in selected_usernames:
            Manager.activate_user(username)
            
    def purge_data(self, is_run=False):
        if not is_run:
            data = {}
            try:
                with open("manager_info.json", 'r') as file:
                    data = json.load(file)
            except FileExistsError:
                console.print("Manager is not defined.", style='Error')
                console.print("Create Manager first.", style='Error')
                exit()

            if data['username'] == self.username and base64.b64decode(data['password']).decode("utf-8") == self.password:
                pass
            else:
                console.print("Invalid username or password.", style='Error')
                exit()

        choice = input("Are you sure? (y/n)")
        if choice == 'y':
            project_path = 'projects/'
            with os.scandir(project_path) as entries:
                if not any(entries):
                    console.print("There is no project data.", style='Error')
                else:
                    shutil.rmtree(project_path)
                    console.print("All projects has been deleted.", style='Notice')
                    logger.info("All projects has been deleted")
                    os.makedirs(project_path)

            users_path = 'users/'
            with os.scandir(users_path) as entries:
                if not any(entries):
                    console.print("There is no user data.", style='Error')
                else:
                    shutil.rmtree(users_path)
                    os.remove("emails_and_usernames.json")
                    console.print("All users has been deleted.", style='Notice')
                    logger.info("All users has been deleted")
                    os.makedirs(users_path)
                    with open("emails_and_usernames.json", 'w') as file:
                        data = {'emails': [], 'usernames': {}}
                        json.dump(data, file, indent=4)


def get_username(ID):
    data = {}
    try:
        with open("emails_and_usernames.json", 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error("Problem with [emails_and_usernames.json]")
        raise FileNotFoundError("File Error. Terminating Program.")
    return data["usernames"][ID]


def get_ID(username):
    data = {}
    try:
        with open("emails_and_usernames.json", 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error("Problem with [emails_and_usernames.json]")
        raise FileNotFoundError("File Error. Terminating Program")

    for ID in data['usernames']:
        if data['usernames'][ID] == username:
            return ID


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User and Admin Manager")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    create_admin_parser = subparsers.add_parser("create-admin", help="Create admin credentials")
    create_admin_parser.add_argument("--username", required=True, help="Admin username")
    create_admin_parser.add_argument("--password", required=True, help="Admin password")

    login_parser = subparsers.add_parser("login", help="Log in as admin")
    login_parser.add_argument("--username", required=True, help="Admin username")
    login_parser.add_argument("--password", required=True, help="Admin password")

    purge_parser = subparsers.add_parser("purge-data", help="Purge database")
    purge_parser.add_argument("--username", required=True, help="Admin username")
    purge_parser.add_argument("--password", required=True, help="Admin password")

    args = parser.parse_args()

    manager = Manager(args.username, args.password)
    if args.subcommand == "create-admin":
        manager.create_admin()
    elif args.subcommand == "login":
        manager.login()
    elif args.subcommand == "purge-data":
        manager.purge_data()