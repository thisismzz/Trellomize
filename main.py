import json
import os
import uuid
import bcrypt
import re
import logging
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler  = logging.FileHandler('logs.log' , mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#........................#
#        CLASSES         #
#........................#

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

#........................................................................#

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

    def check_unique_email(email):
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        
        if email in data['emails']:
            return False
        return True

    def check_unique_username(username):
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        
        if username in data['usernames']:
            return False
        return True
    
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
    
    def get_all_usernames():
        data = {}
        with open ('emails and usernames.json' , 'r') as file:
            data = json.load(file)
        return data['usernames']
    
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
                logger.info(f"A new user registered : {new_user.username}")
                break

            except ValueError as e:
                console.print("Error: " + str(e), style="Error")

    def login():
        console.print("Login", style="Title")
        console.print("Please provide your credentials to log in:", style="Info")
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
                logger.info(f"User [{user_data["username"]}] has logged in ")
                return User(**user_data)

        console.print("Incorrect username or password.", style="Error")
        return None
    
#........................................................................#
    
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

    def view_task(self):
        table = Table(title=f"Task: {self.title}", style="cyan")
        table.add_column("ID", justify="center")
        table.add_column("Title", justify="center")
        table.add_column("Description", justify="center")
        table.add_column("Start Time", justify="center")
        table.add_column("End Time", justify="center")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")

        table.add_row(self.ID, self.title, self.description, self.start_time[:19], self.end_time[:19], self.priority, self.status)  

        console.print(table)

    def change_end_time(self):
        new_end_time = input("Enter new end time (YYYY-MM-DD HH:MM:SS): ")
        try:
            self.end_time = str(datetime.strptime(new_end_time, "%Y-%m-%d %H:%M:%S"))
            console.print("End time changed successfully.", style="Notice")
            logger.debug(f"Task [id : {self.ID}] end time has changed (current : {self.end_time})")
        except ValueError:
            console.print("Invalid date/time format. Please use the format YYYY-MM-DD HH:MM:SS.", style="Error")

    def change_start_time(self):
        new_start_time = input("Enter new start time (YYYY-MM-DD HH:MM:SS): ")
        try:
            self.start_time = str(datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S"))
            console.print("Start time changed successfully.", style="Notice")
            logger.debug(f"Task [id : {self.ID}] start time has changed (current : {self.start_time})")
        except ValueError:
            console.print("Invalid date/time format. Please use the format YYYY-MM-DD HH:MM:SS.", style="Error")

    def change_status(self):
        console.print("Available statuses:", style="Title")
        for status in Status:
            console.print(f"- {status.value}")
        new_status = input("Enter new status: ")
        if new_status in Status.__members__:
            self.status = new_status
            console.print("Task status changed successfully.", style="Notice")
            logger.debug(f"Task [id : {self.ID}] status has changed (current : {self.status})")
        else:
            console.print("Invalid status.", style="Error")

    def change_priority(self):
        console.print("Available priorities:", style="Title")
        for priority in Priority:
            console.print(f"- {priority.value}")
        new_priority = input("Enter new priority: ")
        if new_priority in Priority.__members__:
            self.priority = new_priority
            console.print("Task priority changed successfully.", style="Notice")
            logger.debug(f"Task [id : {self.ID}] priority has changed (current : {self.priority})")
        else:
            console.print("Invalid priority.", style="Error")

    def change_title(self):
        new_title = input("Enter new title: ")
        self.title = new_title
        console.print(f"Task title changed to {self.title}", style="Notice")
        logger.debug(f"Task [id : {self.ID}] title has changed (current : {self.title})")

    def change_description(self):
        new_description = input("Enter new description: ")
        self.description = new_description
        console.print(f"Task description changed to {self.description}", style="Notice")
        logger.debug(f"Task [id : {self.ID}] description has changed (current : {self.description})")

    def add_comment(self, username ,is_owner:bool):
        comment = input("Enter comment: ")
        self.comments.append({"user": username, "comment": comment, "role": "owner" if is_owner else "assigness","timestamp": str(datetime.now())[:19]})
        console.print("Comment added successfully.", style="Notice")
        logger.debug(f"A new comment added to task [id : {self.ID}]")

    def view_comments(self):
        if not self.comments:
            console.print("No comments available.", style="bold red")
        else:
            table = Table(title="Comments")

            table.add_column("Username", justify="center", style="cyan", no_wrap=True)
            table.add_column("Role", justify="center" , style="magenta")
            table.add_column("Comment", justify="center" , style="green")
            table.add_column("Timestamp", justify="center" , style="yellow")

            for comment in self.comments:
                table.add_row(
                    comment['user'],
                    comment['role'],
                    comment['comment'],
                    comment['timestamp']
                )

            console.print(table)
    
    def assign_member(self, project_members, member):
        if member in project_members:
            if member not in self.assigness:
                self.assigness.append(member)
                console.print("Member assigned to task successfully.", style="Notice")
                logger.debug(f"A new assigness [user : {member}] added to task [id : {self.ID}]")
            else:
                console.print("Member is already assigned to the task.", style="Error")
        else:
            console.print("User is not a member of the project.", style="Error")

    def remove_assignees(self, username):
        if username in self.assigness:
            self.assigness.remove(username)
            console.print(f"Member '{username}' removed from task '{self.title}' successfully.", style="Notice")
            logger.debug(f"An assigness [user : {username}] removed from task [id : {self.ID}]")
        else:
            console.print(f"Member '{username}' is not assigned to task '{self.title}'.", style="Error")

#........................................................................#

class Project:

    def __init__(self, title, owner , tasks = {} , collaborators = None, ID = None):
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
        
    def create_project(user:User):
        console.print("Create new Project" , style="Title")
        title = input("Enter Project title: ")
        project = Project(title, user.username)
        project.save_project_data()
        User.add_my_project(user.username,project.ID)
        console.print("Project created successfully.", style="Notice")

    def view_members(self):
        console.print("Current project members:", style="Info")
        for member in self.collaborators:
            if member != self.owner:
                console.print("-", member)
        input_string= input("Enter 'back' to go back: ")
        if input_string == "back":
            return

    def add_member(self, member):
        if member not in self.collaborators:
            self.collaborators.append(member)
            console.print(f"{member} added successfully.", style="Notice")
            User.add_my_project(member,self.ID)
            self.save_project_data()
            logger.debug(f"A new member [user : {member}] added to project [id : {self.ID}] collaborators by owner")
        else:
            console.print(f"User {member} has already been added" , style='Error')

    def remove_member(self, member):
        if member in self.collaborators:
            self.collaborators.remove(member)
            User.remove_project(member,self.ID)
            self.save_project_data()
            console.print(f"{member} removed successfully.", style="Notice")
            logger.debug(f"A member [user : {member}] removed from project [id : {self.ID}] collaborators")
        else:
            console.print(f"{member} is not a member of the project.", style="Error")

    def add_member_menu(self,user:User):
        if self.owner != user.username:
            console.print("Only the project owner can add member.", style="Error")
            return
        
        console.print("Available users:" , style='Info')
        all_usernames = User.get_all_usernames()
        all_usernames.remove(self.owner)
        for username in all_usernames:
            console.print("-", username)

        member_username = list(map(lambda x:x.strip(),input("Enter usernames to add as member (format:'user1,user2') or 'back' to go back: ").split(',')))
        if member_username == "back":
            return
        for username in member_username:
            if username in all_usernames:
                self.add_member(username)
            else:
                console.print(f"Invalid username {username}.", style="Error")

    def remove_member_menu(self,user:User):
        if self.owner != user.username:
            console.print("Only the project owner can remove member.", style="Error")
            return
    
        console.print("Current project members:", style="Info")
        for member in self.collaborators:
            if member != self.owner:
                console.print("-", member)
        member_usernames = list(map(lambda x:x.strip(),input("Enter usernames to remove from project (format:'user1,user2') or 'back' to go back: ").split(',')))
        if member_usernames == "back":
            return
        for member in member_usernames:
                self.remove_member(member)
    
    def update_task(self,new_task:Task):
        self.tasks[new_task.ID] = vars(new_task)

    def view_assignees(self,task:Task):
        console.print("Current task assigness:")
        for member in task.assigness:
            if member != self.owner:
                console.print("-", member)
        input_string= input("Enter 'back' to go back: ")
        if input_string == "back":
            return

    def create_task_menu(self, user:User):
        if self.owner != user.username:
            console.print("Only the project owner can create tasks.", style="Error")
            return
        
        console.print("Please provide the following details to create a new task:", style="Info")
        title = input("Task Title: ")
        description = input("Task Description: ")
        
        new_task = Task(title , description)
        self.tasks[new_task.ID]=vars(new_task)
        self.save_project_data()
        console.print("Task created successfully.", style="Notice")
        logger.info(f"A new task [name : {new_task.title} , id : [{new_task.ID}]] created by [{user.username}]")

    def view_project_tasks(self, user:User):
        table = Table(title=f"Tasks for Project: {self.title}", style="cyan")
        table.add_column("ID", justify="center")
        table.add_column("Title", justify="center")
        table.add_column("Description", justify="center")
        table.add_column("Start Time", justify="center")
        table.add_column("End Time", justify="center")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")
        
        for task in self.tasks.values():
            instance_task = Task(**task)
            table.add_row(instance_task.ID, instance_task.title, instance_task.description, instance_task.start_time[:19], instance_task.end_time[:19], instance_task.priority, instance_task.status)  
        console.print(table)

        task_id = input("Enter task ID to manage (or 'back' to go back): ")
        if task_id == "back":
            return
        flag = False
        for task in self.tasks.values():
            if task["ID"] == task_id:
                self.task_menu(user, Task(**task))
                break
        if not flag:
            console.print("Invalid ID" , style="Error")

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
                logger.info(f"Project [id : {self.ID}] deleted by owner [user : {user.username}]")
                return True
            else:
                raise FileNotFoundError("No such Project")
        except FileNotFoundError as e:
            console.print(e , style="Error")
            return False

    def manage_project_menu(self, user):
        while True:
            console.print(f"Managing Project:", end=" " ,style="Title")
            console.print(f"{self.title}" , style="Info")
            console.print("What would you like to do?", style="Info")
            console.print("1. Create Task")
            console.print("2. View Tasks")
            console.print("3. View Project Members")
            console.print("4. Add Member")
            console.print("5. Remove Member")
            console.print("6. Delete Project")
            console.print("7. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_task_menu(user)
            elif choice == "2":
                self.view_project_tasks(user)
            elif choice == "3":
                self.view_members()
            elif choice == "4":
                self.add_member_menu(user)
            elif choice == "5":
                self.remove_member_menu(user)
            elif choice == "6":
                if self.delete_project(user):
                    break
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")

    def change_task_fields(self, task: Task):
        while True:
            console.print(f"Updating Task: {task.title}", style="Title")
            task.view_task()
            console.print("Which task field do you want to change?", style="Info")
            console.print("1. Status")
            console.print("2. Priority")
            console.print("3. Start Time")
            console.print("4. End Time")
            console.print("5. Title")
            console.print("6. Description")
            console.print("7. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                task.change_status()
                self.update_task(task)
                self.save_project_data()
            elif choice == "2":
                task.change_priority()
                self.update_task(task)
                self.save_project_data()
            elif choice == "3":
                task.change_start_time()
                self.update_task(task)
                self.save_project_data()
            elif choice == "4":
                task.change_end_time()
                self.update_task(task)
                self.save_project_data()
            elif choice == "5":
                task.change_title()
                self.update_task(task)
                self.save_project_data()
            elif choice == "6":
                task.change_description()
                self.update_task(task)
                self.save_project_data()
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")

    def task_menu(self, user: User, task: Task):
        if user.username not in task.assigness and user.username != self.owner:
            console.print("You don't have access to modify this task", style='Error')
            return

        while True:
            console.print(f"Managing Task: {task.title}", style="Title")
            task.view_task()
            console.print("What would you like to do?", style="Info")
            console.print("1. Change Task Fields")
            console.print("2. View Comments")
            console.print("3. Add Comment")
            console.print("4. View Assignees")
            console.print("5. Assign Member")
            console.print("6. Remove Assignees")
            console.print("7. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.change_task_fields(task)
                self.update_task(task)
                self.save_project_data()
            elif choice == "2":
                task.view_comments()
            elif choice == "3":
                task.add_comment(user.username, user.username == self.owner)
                self.update_task(task)
                self.save_project_data()
            elif choice == "4":
                self.view_assignees(task)
            elif choice == "5":
                all_usernames = User.get_all_usernames()
                console.print("Project Members:")
                for member in self.collaborators:
                    if member != self.owner:
                        console.print("-", member)
                member_usernames = list(map(lambda x: x.strip(), input("Enter usernames to add as member (format:'user1,user2') or 'back' to go back: ").split(',')))
                if member_usernames == "back":
                    return
                for username in member_usernames:
                    if username in all_usernames:
                        task.assign_member(self.collaborators, username)
                    else:
                        console.print(f"Invalid username {username}.", style="Error")
                self.update_task(task)
                self.save_project_data()
            elif choice == "6":
                console.print("Current task assigness:", style="Info")
                for member in task.assigness:
                    if member != self.owner:
                        console.print("-", member)
                member_usernames = list(map(lambda x: x.strip(), input("Enter usernames to remove from task (format:'user1,user2') or 'back' to go back: ").split(',')))
                if member_usernames == "back":
                    return
                for member in member_usernames:
                    task.remove_assignees(member)
                self.update_task(task)
                self.save_project_data()
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")

    def create_project(user:User):
        console.print("Create new Project" , style="Title")
        title = input("Enter Project title: ")
        project = Project(title, user.username)
        project.save_project_data()
        logger.info(f"A new project [name : {project.title} , id : {project.ID}] created by [{user.username}]")
        User.add_my_project(user.username,project.ID)
        console.print("Project created successfully.", style="Notice")

    def view_user_projects(user:User):
        data = User.load_user_projects(user.username)
        user_projects = [Project.load_project_data(proj_id) for proj_id in data["projects"]]

        table = Table(title="Projects details", style="cyan")
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
                logger.debug(f"User [{user.username}] is managing project [id : {project_instance.ID}]") 
                project_instance.manage_project_menu(user)
                flag = True
                break
        if not flag:
            console.print("Invalid ID" , style="Error")

#.........................#
#       FUNCTIONS         #
#.........................#

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
            logger.info("EXIT")
            break
        else:
            console.print("Invalid choice.", style="Error")

def user_menu(user:User):
    while True:
        console.print(f"Welcome, {user.username}!", style="Title")
        console.print("What would you like to do?", style="Info")
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
            logger.info(f"User [{user.username}] logged out")
            break
        else:
            console.print("Invalid choice.", style="Error")

#.........................#
#      START POINT        #
#.........................#

if __name__ == "__main__":
    main_menu()