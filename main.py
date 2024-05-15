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
    def __init__(self, email, username, password, active=True):
        self.email = email
        self.username = username
        self.password = password
        self.active = active
        self.ID=str(uuid.uuid1())

    @staticmethod
    def get_all_usernames():
        data = load_data()
        usernames = [user["username"] for user in data["users"]]
        return usernames

    @staticmethod
    def validate_email_format(email):
        email_regex = r'^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def validate_username_format(username):
        username_regex = r'^[a-zA-Z0-9_]+$'
        if re.match(username_regex, username) and 3 <= len(username) <= 20:
            return True
        return False

    @staticmethod
    def check_unique_username(username, data):
        for user in data["users"]:
            if user["username"] == username:
                return False
        return True

    @staticmethod
    def validate_password_strength(password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True
    
    @staticmethod
    def register():
        data = load_data()
        
        while(True):
            console.print("Registration", style="Title")
            console.print("Please provide the following details to create your account:", style="Info")
            email = input("Email: ")
            username = input("Username: ")
            password = input("Password: ")
            try:
                if not User.validate_email_format(email):
                    raise ValueError("Invalid email format! Please enter a valid email address in the format 'example@example.com'.")
                if not User.validate_username_format(username):
                    raise ValueError("Invalid username format! Usernames can only contain letters, digits, and underscores, and must be 3-20 characters long.")
                if not User.check_unique_username(username, data):
                    raise ValueError("Username already exists! Please choose a different username.")
                if not User.validate_password_strength(password):
                    raise ValueError("Weak password! Passwords must be at least 8 characters long and include uppercase and lowercase letters, digits, and special characters.")

                for user in data["users"]:
                    if user["email"] == email or user["username"] == username:
                        console.print("Email or username already exists.", style="Error")
                        return

                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                new_user = User(email, username, hashed_password)
                data["users"].append(new_user.__dict__)
                save_data(data)
                console.print("Account created successfully.", style="Notice")
                break

            except ValueError as e:
                console.print("Error: " + str(e), style="Error")

    @staticmethod
    def login():
        data = load_data()
        console.print("Login", style="Title")
        username = input("Username: ")
        password = input("Password: ")

        for user_data in data["users"]:
            if user_data["username"] == username and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
                if not user_data["active"]:
                    console.print("Your account is inactive.", style="Error")
                    return None
                console.print("Login successful.", style="Notice")
                return User(**user_data)

        console.print("Incorrect username or password.", style="Error")
        return None

class Task:
    def __init__(self, title, description, project, priority=Priority.LOW.value, status=Status.BACKLOG.value):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = datetime.now()  
        self.end_time = datetime.now() + timedelta(hours=24)  
        self.priority = priority
        self.status = status
        self.assignees = []
        self.comments = []
        self.project = project  

    def formatted_start_time(self):
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def formatted_end_time(self):
        return self.end_time.strftime("%Y-%m-%d %H:%M:%S")
    
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

    def remove_assignee(self, username):
        if username in self.assignees:
            self.assignees.remove(username)
            save_data(load_data())
            console.print(f"Member '{username}' removed from task '{self.title}' successfully.", style="Notice")
        else:
            console.print(f"Member '{username}' is not assigned to task '{self.title}'.", style="Error")

class Project:
    def __init__(self, title, owner):
        self.id = str(uuid.uuid4())
        self.title = title
        self.owner = owner
        self.tasks = []
        self.members = [owner]

    def add_member(self, username):
        if username not in self.members:
            self.members.append(username)
        save_data(load_data())

    def remove_member(self, username):
        if username in self.members:
            self.members.remove(username)
            save_data(load_data())

    def delete_project(self):
        data = load_data()
        data["projects"] = [proj for proj in data["projects"] if proj["id"] != self.id]
        save_data(data)
        console.print(f"Project '{self.name}' has been deleted successfully.", style="Notice")

    def create_task(self, title, description):
        new_task = Task(title, description, self, priority=Priority.LOW.value, status=Status.BACKLOG.value)
        self.tasks.append(new_task)  
        save_data(load_data())
        return new_task

    def manage_tasks(self, user):
        while True:
            console.print(f"Managing Tasks for Project: {self.name}", style="Title")
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
                self.add_member_menu()
            elif choice == "4":
                self.remove_member_menu()
            elif choice == "5":
                self.delete_project()
                break
            elif choice == "6":
                break
            else:
                console.print("Invalid choice.", style="Error")

    def add_member_menu(self):
        console.print("Available users:")
        for username in User.get_all_usernames():
            console.print("-", username)
        member_username = input("Enter username to add as member: ")
        if member_username in User.get_all_usernames():
            self.add_member(member_username)
            console.print("Member added successfully.", style="Notice")
        else:
            console.print("Invalid username.", style="Error")

    def remove_member_menu(self):
        console.print("Current project members:")
        for member in self.members:
            console.print("-", member)
        member_username = input("Enter username to remove from project: ")
        if member_username in self.members:
            self.remove_member(member_username)
            console.print("Member removed successfully.", style="Notice")
        else:
            console.print("User is not a member of the project.", style="Error")

    def create_task_menu(self, user):
        if self.owner != user.username:
            console.print("Only the project owner can create tasks.", style="Error")
            return
        
        title = input("Task Title: ")
        description = input("Task Description: ")

        self.create_task(title, description)  
        console.print("Task created successfully.", style="Notice")

    def view_project_tasks(self, user):
        table = Table(title=f"Tasks for Project: {self.name}")
        table.add_column("ID", justify="center")
        table.add_column("Title", justify="center")
        table.add_column("Description", justify="center")
        table.add_column("Start Time", justify="center")
        table.add_column("End Time", justify="center")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")

        for task in self.tasks:
            priority = Priority(task.priority).name  
            status = Status(task.status).name       
            table.add_row(task.id, task.title, task.description, task.formatted_start_time(), task.formatted_end_time(), priority, status)  

        console.print(table)
        task_id = input("Enter task ID to manage (or 'back' to go back): ")
        if task_id == "back":
            return
        for task in self.tasks:
            if task.id == task_id:
                self.task_menu(user, task)  
                break

    def task_menu(self, user, task):
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

    def create_project(self, user):
        name = input("Project Name: ")
        project = Project(name, user.username)
        data = load_data()
        data["projects"].append(project.__dict__)
        save_data(data)
        console.print("Project created successfully.", style="Notice")

    @staticmethod
    def view_user_projects(user):
        data = load_data()
        user_projects = [proj for proj in data["projects"] if user.username in proj["members"]]

        table = Table(title="Projects")
        table.add_column("ID", justify="center")
        table.add_column("Name", justify="center")
        table.add_column("Owner", justify="center")

        for project in user_projects:
            table.add_row(project["id"], project["name"], project["owner"])

        console.print(table)
        project_id = input("Enter project ID to manage (or 'back' to go back): ")
        if project_id == "back":
            return
        for project in user_projects:
            if project["id"] == project_id:
                project_instance = Project(name=project["name"], owner=project["owner"])  
                project_instance.manage_tasks(user)
                break

#.........................
#       FUNCTIONS         
#.........................

def load_data():
    if not os.path.exists("data.json"):
        return {"users": [], "projects": []}
    with open("data.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

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

def user_menu(user):
    while True:
        console.print(f"Welcome, {user.username}", style="Title")
        console.print("1. Create Project")
        console.print("2. View Projects")
        console.print("3. Logout")

        choice = input("Enter your choice: ")
        if choice == "1":
            Project().create_project(user)
        elif choice == "2":
            Project.view_user_projects(user)
        elif choice == "3":
            console.print("You have been successfully logged out.", style="Notice")
            break
        else:
            console.print("Invalid choice.", style="Error")

def unique_id_generator():
    seed = 111100
    while True:
        yield seed
        seed += 1

#.........................
#      START POINT        
#.........................

if __name__ == "__main__":
    main_menu()