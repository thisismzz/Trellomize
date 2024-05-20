import argparse
import json
import os
import base64
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
            self.manager_menu()
        else:
            console.print("Invalid username or password." , style='Error')
            exit()
            
    def manager_menu(self):
        while True:
            console.print(f"welcome Manager {self.username}" , style='Title')
            console.print("What would you like to do?", style="Info")
            console.print("1. Deactivate a user")
            console.print("2. Log out")

            choice = input("Enter your choice: ")
            if choice == '1':
                console.print("Available users:" , style='Info')
                all_usernames = Manager.load_users()
                for username in all_usernames:
                    console.print("-", username)
                selected_usernames = list(map(lambda x:x.strip(),input("Enter usernames to deactive (format:'user1,user2') or 'back' to go back: ").split(',')))
                
                if selected_usernames == 'back':
                    continue
                
                for username in selected_usernames:
                    Manager.deactive_user(username)
            
            elif choice == '2':
                console.print("You have been successfully logged out.", style="Notice")
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
            
        user_data["active"] = False
        
        with open (path , 'w') as file:
            json.dump(user_data,file,indent=4)
        
        console.print(f"User ({username}) has been deactivated successfully", style='Notice')

    def purge_data():
        pass
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="User and Admin Manager")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    create_admin_parser = subparsers.add_parser("create-admin", help="Create admin credentials")
    create_admin_parser.add_argument("--username", required=True, help="Admin username")
    create_admin_parser.add_argument("--password", required=True, help="Admin password")

    login_parser = subparsers.add_parser("login", help="Log in as admin")
    login_parser.add_argument("--username", required=True, help="Admin username")
    login_parser.add_argument("--password", required=True, help="Admin password")

    args = parser.parse_args()

    manager = Manager()
    if args.subcommand == "create-admin":
        manager.create_admin(args.username, args.password)
    elif args.subcommand == "login":
        manager.login(args.username, args.password)