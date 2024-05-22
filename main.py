import json
import os
import uuid
import bcrypt
import re
import logging
import maskpass
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
        
    def update_username(self, new_username):
        old_username = self.username
        self.username = new_username
        
        os.rename(f"users/{old_username}",f"users/{new_username}")
        os.rename(f"users/{new_username}/{old_username}.json",f"users/{new_username}/{new_username}.json")
        self.save_user_data()
        
        data = {}
        with open('emails and usernames.json', 'r') as file:
            data = json.load(file)
        data['usernames'].remove(old_username)
        data['usernames'].append(new_username)
        with open('emails and usernames.json', 'w') as file:
            json.dump(data, file, indent=4)
        logger.info(f"User [{self.username}] changed username from {old_username} to {new_username}")

    def update_password(self, new_password):
        self.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.save_user_data()
        logger.info(f"User [{self.username}] changed password")

    def update_email(self, new_email):
        old_email = self.email
        self.email = new_email
        self.save_user_data()

        data = {}
        with open('emails and usernames.json', 'r') as file:
            data = json.load(file)
        data['emails'].remove(old_email)
        data['emails'].append(new_email)
        with open('emails and usernames.json', 'w') as file:
            json.dump(data, file, indent=4)
        logger.info(f"User [{self.username}] changed email from {old_email} to {new_email}")
        
    def edit_profile_menu(self):
        while(True):
            console.print("Edit Profile", style="Title")
            console.print("What would you like to edit?", style="Info")
            console.print("1. Username")
            console.print("2. Password")
            console.print("3. Email")
            console.print("4. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                new_username = input("Enter new username: ")
                if User.check_unique_username(new_username):
                    self.update_username(new_username)
                    console.print("Username updated successfully.", style="Notice")
                else:
                    console.print("Username already exists. Please choose a different one.", style="Error")
            elif choice == "2":
                new_password = input("Enter new password: ")
                self.update_password(new_password)
                console.print("Password updated successfully.", style="Notice")
            elif choice == "3":
                new_email = input("Enter new email: ")
                if User.check_unique_email(new_email):
                    self.update_email(new_email)
                    console.print("Email updated successfully.", style="Notice")
                else:
                    console.print("Email already exists. Please choose a different one.", style="Error")
            elif choice == "4":
                break
            else:
                console.print("Invalid choice.", style="Error")

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
        password = maskpass.advpass("Password: ", mask="*")  # Using maskpass to hide password input with '*'
        path = f"users/{username}/{username}.json"
        
        if os.path.exists(path):
            user_data = User.load_user_data(username)
            if user_data["username"] == username and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
                if not user_data["active"]:
                    console.print("Your account is inactive.", style="Error")
                    return None
                console.print("Login successful.", style="Notice")
                logger.info(f"User [{user_data['username']}] has logged in ")
                return User(**user_data)

        console.print("Incorrect username or password.", style="Error")
        return None
    
#........................................................................#
    
class Task:
        
    def __init__(self, title, description, priority = None, status = None, ID = None, start_time = None, end_time = None, assignees = [], comments = [], history = []):
        self.title = title
        self.description = description
        self.priority = priority if priority is not None else Priority.LOW.value
        self.status = status if status is not None else Status.BACKLOG.value
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]
        self.start_time = start_time if start_time is not None else str(datetime.now())
        self.end_time = end_time if end_time is not None else str(datetime.now() + timedelta(hours=24))
        self.assignees = assignees 
        self.comments = comments
        self.history = history
        

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
        for idx, status in enumerate(Status, start=1):
            console.print(f"{idx}. {status.value}")
        console.print("0. BACK")
        new_status_idx = int(input("Enter the number for the new status: "))
        if new_status_idx == 0:
            return  
        new_status_idx -= 1
        if 0 <= new_status_idx-1 < len(Status):
            new_status = list(Status)[new_status_idx].name
            self.status = new_status
            console.print("Task status changed successfully.", style="Notice")
            logger.debug(f"Task [id : {self.ID}] status has changed (current : {self.status})")
        else:
            console.print("Invalid status number.", style="Error")

    def change_priority(self):
        console.print("Available priorities:", style="Title")
        for idx, priority in enumerate(Priority, start=1):
            console.print(f"{idx}. {priority.value}")
        console.print("0. BACK")
        new_priority_idx = int(input("Enter the number for the new priority: "))
        if new_priority_idx == 0:
            return 
        new_priority_idx -= 1
        if 0 <= new_priority_idx < len(Priority):
            new_priority = list(Priority)[new_priority_idx].name
            self.priority = new_priority
            console.print("Task priority changed successfully.", style="Notice")
            logger.debug(f"Task [id : {self.ID}] priority has changed (current : {self.priority})")
        else:
            console.print("Invalid priority number.", style="Error")

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

    def view_comments(self):
        if not self.comments:
            console.print("No comments available.", style="bold red")
        else:
            table = Table(title="Comments")

            table.add_column("No.", justify="center", style="White")
            table.add_column("Username", justify="center", style="cyan", no_wrap=True)
            table.add_column("Role", justify="center", style="magenta")
            table.add_column("Comment", justify="center", style="green")
            table.add_column("Timestamp", justify="center", style="yellow")

            for idx, comment in enumerate(self.comments, start=1):
                table.add_row(
                    str(idx),
                    comment['user'],
                    comment['role'],
                    comment['comment'],
                    comment['timestamp']
                )

            console.print(table)

    def add_comment(self, username, is_owner: bool):
        comment = input("Enter comment: ")
        self.comments.append({"user": username, "comment": comment, "role": "owner" if is_owner else "assignee", "timestamp": str(datetime.now())[:19]})
        console.print("Comment added successfully.", style="Notice")
        logger.debug(f"A new comment added to task [id : {self.ID}]")

    def remove_comment(self):
        self.view_comments()
        if not self.comments:
            return

        try:
            comment_idx = int(input("Enter the number of the comment to remove: ")) - 1
            if 0 <= comment_idx < len(self.comments):
                removed_comment = self.comments.pop(comment_idx)
                console.print(f"Comment by {removed_comment['user']} removed successfully.", style="Notice")
                logger.debug(f"Comment removed from task [id : {self.ID}]")
            else:
                console.print("Invalid comment number.", style="Error")
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="Error")

    def edit_comment(self):
        self.view_comments()
        if not self.comments:
            return

        try:
            comment_idx = int(input("Enter the number of the comment to edit: ")) - 1
            if 0 <= comment_idx < len(self.comments):
                new_comment = input("Enter new comment: ")
                self.comments[comment_idx]['comment'] = new_comment
                self.comments[comment_idx]['timestamp'] = str(datetime.now())[:19]
                console.print("Comment edited successfully.", style="Notice")
                logger.debug(f"Comment edited on task [id : {self.ID}]")
            else:
                console.print("Invalid comment number.", style="Error")
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="Error")

    def add_to_history(self , username , action , message = None , members = None , new_amount = None) :
        if action == "add comment":
            new_history = {"user" : username , "action" : action , "message" : message["comment"]}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
            
        elif action == "change status":
            new_history = {"user" : username , "action" : action , "new status" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change priority":
            new_history = {"user" : username , "action" : action , "new priority" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change start time":
            new_history = {"user" : username , "action" : action , "new start time" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change end time":
            new_history = {"user" : username , "action" : action , "new end time" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "add assignee":
            new_history = {"user" : username , "action" : action , "new assignees" : members}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "remove assignee":
            new_history = {"user" : username , "action" : action , "removed assignees" : members}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change title":
            new_history = {"user" : username , "action" : action , "new title" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
            
        elif action == "change description":
            new_history = {"user" : username , "action" : action , "new description" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        logger.debug(f"Add new history to task [id : {self.ID}]")

    def view_history(self):
        if not self.history:
            console.print("No history available for this task.", style="Info")
            return

        table = Table(title="Task History")
        table.add_column("No.", style="white", justify="center")
        table.add_column("User", style="cyan", justify="center")
        table.add_column("Action", style="magenta", justify="center")
        table.add_column("Amount", style="green", justify="center")
        table.add_column("Timestamp", style="yellow", justify="center")  

        for index, entry in enumerate(self.history, start=1):
            user = entry.get("user", "")
            action = entry.get("action", "")
            amount = entry.get("new status", "") or entry.get("new priority", "") or entry.get("new start time", "") or entry.get("new end time", "") or str(entry.get("new assignees", "")) or str(entry.get("removed assignees", "")) or entry.get("new title", "") or entry.get("new description", "") or entry.get("message","")[:20]
            timestamp = entry.get("timestamp", "")
            table.add_row(str(index), user, action, amount, timestamp)

        console.print(table)

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

    def update_task(self,new_task:Task):
        self.tasks[new_task.ID] = vars(new_task)

    def view_members(self):
        if len(self.collaborators) == 1:  
            console.print("There are no project members to display.", style="Error")
            return
        console.print("Current project members:", style="Info")
        for member in self.collaborators:
            if member != self.owner:
                console.print("-", member)
        input_string = input("Enter 'back' to go back: ")
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
            
            #delete project id from user's project.json
            User.remove_project(member,self.ID)
            
            #erase user's name from any tasks
            for task in self.tasks.values():
                if member in task["assignees"]:
                    self.remove_assignee(member,Task(**task))
            
            self.save_project_data()
            console.print(f"{member} removed successfully.", style="Notice")
            logger.debug(f"A member [user : {member}] removed from project [id : {self.ID}] collaborators")
        else:
            console.print(f"{member} is not a member of the project.", style="Error")

    def add_member_menu(self, user: User):
        if self.owner != user.username:
            console.print("Only the project owner can add members.", style="Error")
            return
            
        console.print("Available users:", style='Info')
        all_usernames = User.get_all_usernames()
        all_usernames.remove(self.owner)
        
        if not all_usernames:
            console.print("There are no available users to add to the project.", style="Error")
            return

        for idx, username in enumerate(all_usernames, start=1):
            console.print(f"{idx}. {username}")
        console.print("0. Back")

        selected_indices =  list(map(lambda x:x.strip(),input("Enter the numbers of the users to add as members (e.g., '1,2') or '0' to go back: ").split(',')))
        
        if selected_indices[0] == "0":
            return
        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                return
            idx = int(idx_str) - 1
            if idx >= 0 and idx < len(all_usernames):
                selected_username = all_usernames[idx]
                self.add_member(selected_username)
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")

    def remove_member_menu(self, user: User):
        if self.owner != user.username:
            console.print("Only the project owner can remove members.", style="Error")
            return
            
        members_to_display = [member for member in self.collaborators if member != self.owner]
        if not members_to_display:
            console.print("There are no project members to remove.", style="Error")
            return

        console.print("Current project members:", style="Info")
        for idx, member in enumerate(members_to_display, start=1):
            console.print(f"{idx}. {member}")
        console.print("0. Back")

        selected_indices =  list(map(lambda x:x.strip(),input("Enter the numbers of the users to remove from the project (e.g., '1,2') or '0' to go back: ").strip(',')))
        
        if selected_indices[0] == "0":
            return

        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                return
            idx = int(idx_str) - 1
            if idx >= 0 and idx < len(members_to_display):
                selected_member = members_to_display[idx]
                self.remove_member(selected_member)
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")


    def view_assignees(self, task: Task):
        if not task.assignees:
            console.print("There are no assignees for this task.", style="Error")
            return
            
        console.print("Current task assignees:")
        for member in task.assignees:
            if member != self.owner:
                console.print("-", member)
        input_string = input("Enter 'back' to go back: ")
        if input_string == "back":
            return

    def assign_member(self, member, task: Task):
        if member in self.collaborators:
            if member not in task.assignees:
                task.assignees.append(member)
                console.print(f"Member ({member}) assigned to task successfully.", style="Notice")
                self.save_project_data()
                logger.debug(f"A new assignee [user : {member}] added to task.")
            else:
                console.print(f"Member ({member}) is already assigned to the task.", style="Error")
        else:
            console.print(f"User ({member}) is not a member of the project.", style="Error")

    def remove_assignee(self, username, task: Task):
        if username in task.assignees:
            task.assignees.remove(username)
            console.print(f"Member '{username}' removed from task successfully.", style="Notice")
            self.save_project_data()
            logger.debug(f"An assignee [user : {username}] removed from task.")
        else:
            console.print(f"Member '{username}' is not assigned to the task.", style="Error")
        
    def assign_member_menu(self, task: Task , user : User):
        if len(self.collaborators) == 1: 
            console.print("There are no project members to assign.", style="Error")
            return

        console.print("Project Members:")
        for idx, member in enumerate(self.collaborators[1:], start=1):
            if member != self.owner:
                console.print(f"{idx}. {member}")
        console.print("0. Back")
        
        
        selected_indices =  list(map(lambda x:x.strip(),input("Enter the numbers of the users to assign as members (e.g., '1,2') or '0' to go back: ").strip(',')))
        
        if selected_indices[0] == "0":
            return
        
        member_usernames = []
        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                return
            idx = int(idx_str)
            if idx >= 0 and idx < len(self.collaborators) and self.collaborators[idx] != self.owner:
                member_usernames.append(self.collaborators[idx])
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")
                return
            
            for member in member_usernames:
                self.assign_member(member,task)
            
            task.add_to_history(user.username, action="add assignee", members=member_usernames)

    def remove_assignee_menu(self, task: Task ,user : User):
        if not task.assignees:
            console.print("There are no assignees for this task to remove.", style="Error")
            return
        
        console.print("Current task assignees:", style="Info")
        for idx, member in enumerate(task.assignees, start=1):
            console.print(f"{idx}. {member}")
        console.print("0. Back")
        
        selected_indices =  list(map(lambda x:x.strip(),input("Enter the numbers of the users to remove from task (e.g., '1,2') or '0' to go back: ").strip(',')))
        if selected_indices[0] == "0":
            return
        
        member_usernames = []
        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                return
            idx = int(idx_str) -1
            if idx >= 0 and idx < len(task.assignees):
                member_usernames.append(task.assignees[idx])
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")
                return
            
            for member in member_usernames:
                self.remove_assignee(member,task)

            task.add_to_history(user.username, action="remove assignee", members=member_usernames)

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
                flag = True
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

    def change_task_fields(self, user : User , task : Task):
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
                task.add_to_history(user.username , action = "change status" , new_amount = task.status)
                self.update_task(task)
                self.save_project_data()
            elif choice == "2":
                task.change_priority()
                task.add_to_history(user.username , action = "change priority" , new_amount = task.priority)
                self.update_task(task)
                self.save_project_data()
            elif choice == "3":
                task.change_start_time()
                task.add_to_history(user.username , action = "change start time" , new_amount = task.start_time)
                self.update_task(task)
                self.save_project_data()
            elif choice == "4":
                task.change_end_time()
                task.add_to_history(user.username , action = "change end time" , new_amount = task.end_time)
                self.update_task(task)
                self.save_project_data()
            elif choice == "5":
                task.change_title()
                task.add_to_history(user.username , action = "change title" , new_amount = task.title)
                self.update_task(task)
                self.save_project_data()
            elif choice == "6":
                task.change_description()
                task.add_to_history(user.username , action = "change description" , new_amount = task.description)
                self.update_task(task)
                self.save_project_data()
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")

    def task_menu(self, user: User, task: Task):
        if user.username not in task.assignees and user.username != self.owner:
            console.print("You don't have access to modify this task", style='Error')
            return

        while True:
            console.print(f"Managing Task: {task.title}", style="Title")
            task.view_task()
            console.print("What would you like to do?", style="Info")
            console.print("1. Change Task Fields")
            console.print("2. View Comments")
            console.print("3. Add Comment")
            console.print("4. Edit Comment")
            console.print("5. Remove comment")
            console.print("6. View Assignees")
            console.print("7. Assign Member")
            console.print("8. Remove Assignees")
            console.print("9. View History")
            console.print("10. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.change_task_fields(user, task)
                self.update_task(task)
                self.save_project_data()

            elif choice == "2":
                task.view_comments()
        
            elif choice == "3":
                task.add_comment(user.username, user.username == self.owner)
                task.add_to_history(user.username, action="add comment", message=task.comments[-1])
                self.update_task(task)
                self.save_project_data()

            elif choice == "4":
                task.edit_comment()

            elif choice == "5":
                task.remove_comment()

            elif choice == "6":
                self.view_assignees(task)

            elif choice == "7":
                self.assign_member_menu(task,user)
                self.update_task(task)
                self.save_project_data()

            elif choice == "8":
                self.remove_assignee_menu(task,user)
                self.update_task(task)
                self.save_project_data()
            
            elif choice == "9":
                task.view_history()

            elif choice == "10":
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

    def view_user_projects(user: User):
        data = User.load_user_projects(user.username)
        user_projects = [Project.load_project_data(proj_id) for proj_id in data["projects"]]

        table = Table(title="Projects details", style="cyan")
        table.add_column("No.", style="cyan", justify="center")
        table.add_column("ID", style="magenta", justify="center")
        table.add_column("Name", style="green", justify="center")
        table.add_column("Owner", style="yellow", justify="center")

        project_map = {}
        for i, project in enumerate(user_projects, start=1):
            table.add_row(str(i), project["ID"], project["title"], project["owner"])
            project_map[str(i)] = project
        console.print(table)

        while True:
            project_number = input("Enter project number to manage (or 0 to go back): ")
            if project_number == "0":
                return
            if project_number in project_map:
                project = project_map[project_number]
                project_instance = Project(**project)
                logger.debug(f"User [{user.username}] is managing project [id: {project_instance.ID}]")
                project_instance.manage_project_menu(user)
                break
            else:
                console.print("Invalid number", style="Error")

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
            logger.info("EXIT (end of program)")
            break
        else:
            console.print("Invalid choice.", style="Error")

def user_menu(user: User):
    while True:
        console.print(f"Welcome, {user.username}!", style="Title")
        console.print("What would you like to do?", style="Info")
        console.print("1. Create Project")
        console.print("2. View Projects")
        console.print("3. Edit Profile")
        console.print("4. Logout")

        choice = input("Enter your choice: ")
        if choice == "1":
            Project.create_project(user)
        elif choice == "2":
            Project.view_user_projects(user)
        elif choice == "3":
            User.edit_profile_menu(user)
        elif choice == "4":
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