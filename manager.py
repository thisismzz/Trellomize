import argparse
import json
import os
import base64
import shutil
import logging
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

custom_theme = Theme({
    "Title":  "bold Magenta",
    "Info": "blue",
    "Notice": "bold green",
    "Error": "bold red"
})

console = Console(theme=custom_theme)

logger = logging.getLogger("__manager__")
logger.setLevel(logging.DEBUG)
handler  = logging.FileHandler('logs.log' , mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Manager:
    def __init__(self , username , password):
        self.username = username
        self.password = password
    
    def create_admin(self):
        if os.path.exists("manager_info.json"):
            console.print("Error: Admin info already exists." , style='Error')
            exit()
        
        admin_info = {
            "username": self.username, 
            "password": base64.b64encode(self.password.encode("utf-8")).decode("utf-8")
        }
        
        with open("manager_info.json", "w") as admin_file:
            json.dump(admin_info, admin_file)
        print("Admin info created successfully.")
        logger.info("Manager has created successfully")
    
    def login(self):
        data = {}
        try:
            with open("manager_info.json" , 'r') as file:
                data = json.load(file)
        except FileExistsError : 
            console.print("Manager is not defined" , style='Error')
            console.print("Create Manager first", style='Error')
            exit()
            
        if data['username'] == self.username and base64.b64decode(data['password']).decode("utf-8") == self.password:
            console.print("Login successful.", style="Notice")
            logger.info("Manager has logged in successfully")
            self.manager_menu()
        else:
            console.print("Invalid username or password." , style='Error')
            exit()
            
    def manager_menu(self):
        while True:
            console.print(f"welcome Manager {self.username}" , style='Title')
            console.print("What would you like to do?", style="Info")
            console.print("1. Deactivate a user")
            console.print("2. Activated a user")
            console.print("3. Delete database")
            console.print("4. Log out")

            choice = input("Enter your choice: ")
            if choice == '1':
                console.print("Available users:" , style='Info')
                all_usernames = Manager.load_users()
                for username in all_usernames:
                    console.print("-", username)
                selected_usernames = list(map(lambda x:x.strip(),input("Enter usernames to deactive (format:'user1,user2') or 'back' to go back: ").split(',')))
                
                if selected_usernames[0] == 'back':
                    self.manager_menu()
                
                for username in selected_usernames:
                    Manager.deactive_user(username)
                
            elif choice == '2':
                console.print("Available users:" , style='Info')
                all_usernames = Manager.load_users()
                for username in all_usernames:
                    console.print("-", username)
                selected_usernames = list(map(lambda x:x.strip(),input("Enter usernames to activate (format:'user1,user2') or 'back' to go back: ").split(',')))
                
                if selected_usernames[0] == 'back':
                    self.manager_menu()
                
                for username in selected_usernames:
                    Manager.activate_user(username)
            
            elif choice == '3':
                self.purge_data(is_run=True)
            
            elif choice == '4':
                console.print("You have been successfully logged out.", style="Notice")
                logger.info("End of Manager program")
                exit()

            else:
                console.print("Invalid choice.", style="Error")
        
    def load_users():
        if not os.path.exists("emails and usernames.json"):
            print("Error: User info file not found.")
            return
        
        with open("emails and usernames.json", "r") as user_file:
            users_data = json.load(user_file)
        return users_data["usernames"]

    def deactive_user(username):
        path = 'users/' + username + '/' + username + ".json"
        user_data = {}
        with open(path , 'r') as file :
            user_data = json.load(file)
        
        if user_data["active"] == False:
            console.print(f"User ({username}) has already been deactivated" , style='Error')
            return
        
        user_data["active"] = False
        
        with open (path , 'w') as file:
            json.dump(user_data,file,indent=4)
        
        console.print(f"User ({username}) has been deactivated successfully", style='Notice')
        logger.info(f"User ({username}) deactivated by Manager")

    def activate_user(username):
        path = 'users/' + username + '/' + username + ".json"
        user_data = {}
        with open(path , 'r') as file :
            user_data = json.load(file)
        
        if user_data["active"] == True:
            console.print(f"User ({username}) is active" , style='Error')
            return
        
        user_data["active"] = True
        
        with open (path , 'w') as file:
            json.dump(user_data,file,indent=4)
        
        console.print(f"User ({username}) has been activated successfully", style='Notice')
        logger.info(f"User ({username}) activated by Manager")
        
        
    def purge_data(self,is_run = False):
        if not is_run:
            data = {}
            try:
                with open("manager_info.json" , 'r') as file:
                    data = json.load(file)
            except FileExistsError : 
                console.print("Manager is not defined" , style='Error')
                console.print("Create Manager first", style='Error')
                exit()

            if data['username'] == self.username and base64.b64decode(data['password']).decode("utf-8") == self.password:
                pass
            else:
                console.print("Invalid username or password." , style='Error')
                exit()
            
        project_path = 'projects/'
        with os.scandir(project_path) as entries:
            if not any(entries):
                console.print("There is no project data" , style='Error')
            else:
                shutil.rmtree(project_path)
                console.print("All projects has been deleted" , style='Notice')
                logger.info("All projects has been deleted")
                os.makedirs(project_path)
        
        users_path = 'users/'
        with os.scandir(users_path) as entries:
            if not any(entries):
                console.print("There is no user data" , style='Error')
            else:
                shutil.rmtree(users_path)
                os.remove("emails and usernames.json")
                console.print("All users has been deleted" , style='Notice')
                logger.info("All users has been deleted")
                os.makedirs(users_path)
                with open ("emails and usernames.json" , 'w') as file:
                    data = {'emails' : [] , 'usernames' : []}
                    json.dump(data,file,indent=4)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User and Admin Manager")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    create_admin_parser = subparsers.add_parser("create-admin", help="Create admin credentials")
    create_admin_parser.add_argument("--username", required=True, help="Admin username")
    create_admin_parser.add_argument("--password", required=True, help="Admin password")

    login_parser = subparsers.add_parser("login", help="Log in as admin")
    login_parser.add_argument("--username", required=True, help="Admin username")
    login_parser.add_argument("--password", required=True, help="Admin password")

    purge_parser = subparsers.add_parser("purge-data" , help="Purge database")
    purge_parser.add_argument("--username", required=True, help="Admin username")
    purge_parser.add_argument("--password", required=True, help="Admin password")
    
    args = parser.parse_args()

    manager = Manager(args.username,args.password)
    if args.subcommand == "create-admin":
        manager.create_admin()
        
    elif args.subcommand == "login":
        manager.login()
    
    elif args.subcommand == "purge-data":
        manager.purge_data()
        