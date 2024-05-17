import json
import os
import uuid
import bcrypt
import re
from enum import Enum
from datetime import datetime, timedelta
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

#.........................
#        CLASSES          
#.........................


class Status(Enum):
    BACKLOG = 'BACKLOG'
    TODO = 'TODO'
    DOING = 'DOING'
    DONE = 'DONE'
    ARCHIVED = 'ARCHIVED'

class Priority(Enum):
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'

class User:
        
    def __init__(self, email, username, password, active = True , ID = None):
        self.email = email
        self.username = username
        self.password = password
        self.active = active
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]


    def validate_email_format(email):
        email_regex = r'^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$'
        return re.match(email_regex, email) is not None


    # def validate_username_format(username):
    #     username_regex = r'^[a-zA-Z0-9_]+$'
    #     if re.match(username_regex, username) and 3 <= len(username) <= 20:
    #         return True
    #     return False


    def get_all_usernames():
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        return data['usernames']
    

    def check_unique_username(username):
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        
        if username in data['usernames']:
            return False
        return True
    
    def check_unique_email(email):
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        
        if email in data['emails']:
            return False
        return True
    
    def add_email_username(email , username):
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        
        data['emails'].append(email)
        data['usernames'].append(username)
        
        with open ('emails and usernames.json' , 'w') as file:
            data = json.dump(data , file , indent=4)


    def save_user_data (self):
        user_folder = "users/" + self.username
        os.makedirs(user_folder, exist_ok=True)
        json_file_path = os.path.join(user_folder, f"{self.username}.json")
        with open(json_file_path, "w") as json_file:
            json.dump(vars(self), json_file, indent=4)

    def load_user_data (username):
        user_folder = "users/" + username
        json_file_path = os.path.join(user_folder, f"{username}.json")
        with open(json_file_path, "r") as json_file:
            return json.load(json_file)
        

    def add_my_project(username,project_id):
        path = "users/" + username + "/projects.json"
        data = {}
        if os.path.exists(path):
            with open(path, "r") as file:
                data = json.load(file)
            data['projects'].append(project_id)
        else:
            data = {'projects' : [project_id]}
        
        with open(path, "w") as file:
            json.dump(data , file , indent=4)


    def remove_project(username , project_id):
        path = "users/" + username + "/projects.json"
        data = {}
        with open(path, "r") as file:
            data = json.load(file)
            
        data['projects'].remove(project_id)
        with open(path, "w") as file:
            json.dump(data,file,indent=4)
    
    
    def load_user_projects(username):
        path = "users/" + username + "/projects.json"
        with open(path, "r") as file:
                return json.load(file)


    # def validate_password_strength(password):
    #     if len(password) < 8:
    #         return False
    #     if not re.search(r"[A-Z]", password):
    #         return False
    #     if not re.search(r"[a-z]", password):
    #         return False
    #     if not re.search(r"[0-9]", password):
    #         return False
    #     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #         return False
    #     return True
    

    def register():
        while(True):
            console.print("Registration", style="Title")
            console.print("Please provide the following details to create your account:", style="Info")
            email = input("Email: ")
            username = input("Username: ")
            password = input("Password: ")
            try:
                if not User.validate_email_format(email):
                    raise ValueError("Invalid email format! Please enter a valid email address in the format 'example@example.com'.")
                # if not User.validate_username_format(username):
                #     raise ValueError("Invalid username format! Usernames can only contain letters, digits, and underscores, and must be 3-20 characters long.")
                if not User.check_unique_username(username):
                    raise ValueError("Username already exists! Please choose a different username.")
                # if not User.validate_password_strength(password):
                #     raise ValueError("Weak password! Passwords must be at least 8 characters long and include uppercase and lowercase letters, digits, and special characters.")
                if not User.check_unique_email(email):
                    raise ValueError("Email already exists! Please enter a different email.")

                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                new_user = User(email, username, hashed_password)
                new_user.save_user_data()
                User.add_email_username(email , username)
                console.print("Account created successfully.", style="Notice")
                break

            except ValueError as e:
                console.print("Error: " + str(e), style="Error")


    def login():
        console.print("Login", style="Title")
        username = input("Username: ")
        password = input("Password: ")

        path = f"users/{username}/{username}.json"
        
        if os.path.exists(path):
            user_data =  User.load_user_data(username)
        
            if user_data["username"] == username and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
                if not user_data["active"]:
                    console.print("Your account is inactive.", style="Error")
                    return None
                console.print("Login successful.", style="Notice")
                return User(**user_data)

        console.print("Incorrect username or password.", style="Error")
        return None
    

class Task:
        
    def __init__(self, title, description, priority = None, status = None, ID = None, start_time = None, end_time= None, assigness = [], comments = []):
        self.title = title
        self.description = description
        self.priority = priority if priority is not None else Priority.LOW.value
        self.status = status if status is not None else Status.BACKLOG.value
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]
        self.start_time = start_time if start_time is not None else str(datetime.now())
        self.end_time = end_time if end_time is not None else str(datetime.now() + timedelta(hours=24))
        self.assigness = assigness 
        self.comments = comments


    def update_end_time(self):
        new_end_time = input("Enter new end time (YYYY-MM-DD HH:MM:SS): ")
        try:
            self.end_time = datetime.strptime(new_end_time, "%Y-%m-%d %H:%M:%S")
            save_data(load_data())
            console.print("End time updated successfully.", style="Notice")
        except ValueError:
            console.print("Invalid date/time format. Please use the format YYYY-MM-DD HH:MM:SS.", style="Error")

    def update_start_time(self):
        new_start_time = input("Enter new start time (YYYY-MM-DD HH:MM:SS): ")
        try:
            self.start_time = datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S")
            save_data(load_data())
            console.print("Start time updated successfully.", style="Notice")
        except ValueError:
            console.print("Invalid date/time format. Please use the format YYYY-MM-DD HH:MM:SS.", style="Error")

    def update_status(self):
        console.print("Available statuses:", style="Title")
        for status in Status:
            console.print(f"- {status.value}")
        new_status = input("Enter new status: ")
        if new_status in Status.__members__:
            self.status = new_status
            save_data(load_data())
            console.print("Task status updated successfully.", style="Notice")
        else:
            console.print("Invalid status.", style="Error")

    def update_priority(self):
        console.print("Available priorities:", style="Title")
        for priority in Priority:
            console.print(f"- {priority.value}")
        new_priority = input("Enter new priority: ")
        if new_priority in Priority.__members__:
            self.priority = new_priority
            save_data(load_data())
            console.print("Task priority updated successfully.", style="Notice")
        else:
            console.print("Invalid priority.", style="Error")

    def add_comment(self, user):
        comment = input("Enter comment: ")
        self.comments.append({"user": user.username, "comment": comment, "timestamp": datetime.now().isoformat()})
        save_data(load_data())
        console.print("Comment added successfully.", style="Notice")
    
    def show_project_members(self):
        console.print("Project Members:")
        for member in self.project.members:
            console.print("-", member)

    def assign_member(self, project, member):
        if member in project.members:
            if member not in self.assignees:
                self.assignees.append(member)
                save_data(load_data())
                console.print("Member assigned to task successfully.", style="Notice")
            else:
                console.print("Member is already assigned to the task.", style="Error")
        else:
            console.print("User is not a member of the project.", style="Error")

    def remove_assignees(self, username):
        if username in self.assignees:
            self.assignees.remove(username)
            save_data(load_data())
            console.print(f"Member '{username}' removed from task '{self.title}' successfully.", style="Notice")
        else:
            console.print(f"Member '{username}' is not assigned to task '{self.title}'.", style="Error")

class Project:

    def __init__(self, title, owner , tasks = [] , collaborators = None, ID = None):
        self.title = title
        self.owner = owner
        self.tasks = tasks
        self.collaborators = collaborators if collaborators is not None else [owner]
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]

    def save_project_data(self):
        project_folder = "projects/"
        os.makedirs(project_folder, exist_ok=True)
        json_file_path = os.path.join(project_folder, f"{self.ID}.json")
        with open(json_file_path, "w") as json_file:
            json.dump(vars(self), json_file, indent=4)


    def load_project_data(ID):
        project_folder = "projects/"
        json_file_path = os.path.join(project_folder, f"{ID}.json")
        with open(json_file_path, "r") as json_file:
            return json.load(json_file)


    def add_member(self, member):
        if member not in self.collaborators:
            self.collaborators.append(member)
            console.print(f"{member} added successfully.", style="Notice")
            User.add_my_project(member,self.ID)
            self.save_project_data()
        else:
            console.print(f"User {member} has already been added" , style='Error')


    def remove_member(self, member):
        if member in self.collaborators:
            self.collaborators.remove(member)
            User.remove_project(member,self.ID)
            self.save_project_data()
            console.print(f"{member} removed successfully.", style="Notice")
        else:
            console.print(f"{member} is not a member of the project.", style="Error")

    def delete_project(self,user:User):
        if self.owner != user.username:
            console.print("Only the project owner can delete project.", style="Error")
            return False
        
        file_path = f"projects/{self.ID}.json"
    
        try:
            if os.path.exists(file_path) :
                os.remove(file_path)
                for member in self.collaborators:
                    User.remove_project(member,self.ID)
                console.print(f"Project '{self.title}' has been deleted successfully." , style="Notice")
                return True
            else:
                raise FileNotFoundError("No such Project")
        except FileNotFoundError as e:
            console.print(e , style="Error")
            return False


    def manage_project(self, user):
        while True:
            console.print(f"Managing Tasks for Project:", end=" " ,style="Title")
            console.print(f"{self.title}" , style="Info")
            console.print("1. Create Task")
            console.print("2. View Tasks")
            console.print("3. Add Member")
            console.print("4. Remove Member")
            console.print("5. Delete Project")
            console.print("6. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_task_menu(user)
            elif choice == "2":
                self.view_project_tasks(user)
            elif choice == "3":
                self.add_member_menu(user)
            elif choice == "4":
                self.remove_member_menu(user)
            elif choice == "5":
                if self.delete_project(user):
                    break
            elif choice == "6":
                break
            else:
                console.print("Invalid choice.", style="Error")


    def add_member_menu(self,user:User):
        if self.owner != user.username:
            console.print("Only the project owner can add member.", style="Error")
            return
        
        console.print("Available users:" , style='Info')
        all_usernames = User.get_all_usernames()
        all_usernames.remove(self.owner)
        for username in all_usernames:
            console.print("-", username)

        member_username = list(map(lambda x:x.strip(),input("Enter usernames to add as member :(format : 'user1,user2') ").split(',')))
        for username in member_username:
            if username in all_usernames:
                self.add_member(username)
            else:
                console.print(f"Invalid username {username}.", style="Error")


    def remove_member_menu(self,user:User):
        if self.owner != user.username:
            console.print("Only the project owner can remove member.", style="Error")
            return

        console.print("Current project members:")
        for member in self.collaborators:
            if member != self.owner:
                console.print("-", member)
        
        member_usernames = list(map(lambda x:x.strip(),input("Enter usernames to remove from project :(format : 'user1 , user2') ").split(',')))
        for member in member_usernames:
                self.remove_member(member)


    def create_task_menu(self, user:User):
        if self.owner != user.username:
            console.print("Only the project owner can create tasks.", style="Error")
            return
        
        title = input("Task Title: ")
        description = input("Task Description: ")
        
        new_task = Task(title , description)
        self.tasks.append(vars(new_task))
        self.save_project_data()
        console.print("Task created successfully.", style="Notice")



    def view_project_tasks(self, user):
        table = Table(title=f"Tasks for Project: {self.title}")
        table.add_column("ID", justify="center")
        table.add_column("Title", justify="center")
        table.add_column("Description", justify="center")
        table.add_column("Start Time", justify="center")
        table.add_column("End Time", justify="center")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")
        

        for task in self.tasks:
            instance_task = Task(**task)
            table.add_row(instance_task.ID, instance_task.title, instance_task.description, instance_task.start_time, instance_task.end_time, instance_task.priority, instance_task.status)  

        console.print(table)

        task_id = input("Enter task ID to manage (or 'back' to go back): ")
        if task_id == "back":
            return
        for task in self.tasks:
            if task.id == task_id:
                self.task_menu(user, task)
                break


    def task_menu(self, user, task:Task):
        if user not in task.assigness:
            console.print("You don't have access to modify this task" , style='Error')
            return

        while True:
            console.print(f"Managing Task: {task.title}", style="Title")
            console.print("1. Change Status")
            console.print("2. Change Priority")
            console.print("3. Update Start Time")
            console.print("4. Update End Time")
            console.print("5. Add Comment")
            console.print("6. Assign Member")
            console.print("7. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                task.update_status()
            elif choice == "2":
                task.update_priority()
            elif choice == "3":
                task.update_start_time()
            elif choice == "4":
                task.update_end_time()
            elif choice == "5":
                task.add_comment(user)
            elif choice == "6":
                task.show_project_members()  
                member = input("Enter member username: ")
                task.assign_member(self, member)  
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")


    def create_project(user:User):
        console.print("Create new Project" , style="Title")
        title = input("Enter Project title: ")
        project = Project(title, user.username)
        project.save_project_data()
        User.add_my_project(user.username,project.ID)
        console.print("Project created successfully.", style="Notice")


    def view_user_projects(user:User):
        data = User.load_user_projects(user.username)
        
        user_projects = [Project.load_project_data(proj_id) for proj_id in data["projects"]]

        table = Table(title="Projects")
        table.add_column("ID", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Owner", justify="center")

        for project in user_projects:
            table.add_row(project["ID"], project["title"], project["owner"])

        console.print(table)
        project_id = input("Enter project ID to manage (or 'back' to go back): ")
        
        if project_id == "back":
            return

        flag = False
        for project in user_projects:
            if project["ID"] == project_id:
                project_instance = Project(**project)  
                project_instance.manage_project(user)
                flag = True
                break

        if not flag:
            console.print("Invalid ID" , style="Error")

#.........................
#       FUNCTIONS         
#.........................


def main_menu():
    while True:
        console.print("Welcome to the Project Management System", style="Title")
        console.print("Already have an account? Login now. New user? Register to get started.", style="Info")
        console.print("1. Register")
        console.print("2. Login")
        console.print("3. Exit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            User.register()
        elif choice == "2":
            user = User.login()
            if user:
                user_menu(user)
        elif choice == "3":
            console.print("Thank you for using the Project Management System. Have a great day!", style="Notice")
            break
        else:
            console.print("Invalid choice.", style="Error")


def user_menu(user:User):
    console.print(f"Welcome, {user.username}", style="Title")
    while True:
        console.print("1. Create Project")
        console.print("2. View Projects")
        console.print("3. Logout")

        choice = input("Enter your choice: ")
        if choice == "1":
            Project.create_project(user)
        elif choice == "2":
            Project.view_user_projects(user)
        elif choice == "3":
            console.print("You have been successfully logged out.", style="Notice")
            break
        else:
            console.print("Invalid choice.", style="Error")


#.........................
#      START POINT        
#.........................

if __name__ == "__main__":
    main_menu()