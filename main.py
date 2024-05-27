import json
import os
import uuid
import bcrypt
import re
import logging
import pwinput
import platform
from enum import Enum
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# Custom theme for console output using the rich library
CUSTOM_THEME = Theme({
    "Title": "bold Magenta",
    "Info": "blue",
    "Notice": "bold green",
    "Error": "bold red"
})

console = Console(theme=CUSTOM_THEME)

# Setting up logger for logging errors and debug information
logger = logging.getLogger("__manager__")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def clear_screen():
    #Clears the terminal screen based on the operating system.
    os.system('cls' if os.name == 'nt' else 'clear')



def wait_for_key_press():
    #Waits for a key press from the user and handles different OS requirements.
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


class User:

    def __init__(self, email, username, password, active=True, ID = None):
        self.email = email
        self.username = username
        self.password = password
        self.active = active
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]

    @staticmethod
    def validate_email_format(email):
        #Validates the email format using a regex pattern.
        email_regex = r'^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$'
        return re.match(email_regex, email) is not None
    
    @staticmethod
    def validate_username_format(username):
        #Validates the username format and length.
        username_regex = r'^[a-zA-Z0-9_]+$'
        if re.match(username_regex, username) and 3 <= len(username) <= 20:
            return True
        return False

    @staticmethod
    def check_unique_email(email):
        #Checks if the email is unique by comparing it to stored emails.
        data = {}
        try:
            with open('emails_and_usernames.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error("Problem with [emails_and_usernames.json]")
            raise FileNotFoundError("File Error. Terminating Program")

        if email in data['emails']:
            return False
        return True

    @staticmethod
    def check_unique_username(username):
        #Checks if the username is unique by comparing it to stored usernames.
        data = {}
        try:
            with open('emails_and_usernames.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error("Problem with [emails_and_usernames.json]")
            raise FileNotFoundError("File Error. Terminating Program")

        if username in list(data['usernames'].values()):
            return False
        return True
    
    @staticmethod
    # Validate password strength based on criteria
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
    def get_all_usernames():
        # Retrieve all stored usernames
        data = {}
        try:
            with open('emails_and_usernames.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error("Problem with [emails_and_usernames.json]")
            raise FileNotFoundError("File Error. Terminating Program")
        return list(data['usernames'].values())
    
    def add_email_username(self):
        # Add email and username to stored data
        data = {}
        try:
            with open('emails_and_usernames.json', 'r') as file:
                data = json.load(file)

            data['emails'].append(self.email)
            data['usernames'][self.ID] = self.username

            with open('emails_and_usernames.json', 'w') as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            logger.error("Problem with [emails_and_usernames.json]")
            raise FileNotFoundError("File Error. Terminating Program")

    def save_user_data(self):
        # Create user folder if it doesn't exist
        user_folder = f"users/{self.username}"
        os.makedirs(user_folder, exist_ok=True)
        json_file_path = os.path.join(user_folder, f"{self.username}.json")
        try:
            # Save user data to a JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(vars(self), json_file, indent=4)
        except FileNotFoundError:
            logger.error(f"Problem with [{json_file_path}]")
            raise FileNotFoundError("File Error. Terminating Program")

    @staticmethod
    def load_user_data(username):
        # Load user data from a JSON file
        user_folder = f"users/{username}"
        json_file_path = os.path.join(user_folder, f"{username}.json")
        try:
            with open(json_file_path, "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"Problem with [{json_file_path}]")
            raise FileNotFoundError("File Error. Terminating Program")

    @staticmethod
    def add_my_project(username, project_id):
        # Add a project to the user's list of projects
        path = f"users/{username}/projects.json"
        data = {}
        if os.path.exists(path):
            with open(path, "r") as file:
                data = json.load(file)
            data['projects'].append(project_id)
        else:
            data = {'projects': [project_id]}
        try:
            # Save the updated projects list to a JSON file
            with open(path, "w") as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            logger.error(f"Problem with [{path}]")
            raise FileNotFoundError("File Error. Terminating Program")

    @staticmethod
    def remove_project(user_id, project_id):
        # Remove a project from the user's list of projects
        path = f"users/{get_username(user_id)}/projects.json"
        data = {}
        try:
            with open(path, "r") as file:
                data = json.load(file)

            data['projects'].remove(project_id)
            with open(path, "w") as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            logger.error(f"Problem with [{path}]")
            raise FileNotFoundError("File Error. Terminating Program")

    @staticmethod
    def load_user_projects(username):
        # Load the user's list of projects from a JSON file
        path = f"users/{username}/projects.json"
        try:
            with open(path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error(f"Problem with [{path}]")
            return None

    def change_username(self, new_username):
        old_username = self.username
        self.username = new_username
        os.rename(f"users/{old_username}", f"users/{new_username}")
        os.rename(f"users/{new_username}/{old_username}.json",
                  f"users/{new_username}/{new_username}.json")
        self.save_user_data()
        data = {}
        try:
            with open('emails_and_usernames.json', 'r') as file:
                data = json.load(file)
            data['usernames'][self.ID] = new_username
            with open('emails_and_usernames.json', 'w') as file:
                json.dump(data, file, indent=4)
            console.print("Username updated successfully.", style="Notice")
            logger.info(f"User [{self.username}] changed username from {old_username} to {new_username}")
        except FileNotFoundError:
            logger.error("Problem with [emails_and_usernames.json]")
            raise FileNotFoundError("File Error. Terminating Program")

    def change_password(self, new_password):
        if bcrypt.checkpw(new_password.encode('utf-8'), self.password.encode('utf-8')):
            console.print("Enter a new password not your old password!", style="Error")
            return
        self.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.save_user_data()
        console.print("Password updated successfully.", style="Notice")
        logger.info(f"User [{self.username}] changed password")

    def change_email(self, new_email):
        if new_email == self.email:
            console.print("Enter a new email not your old email!", style='Error')
            return

        data = {}
        try:
            old_email = self.email
            self.email = new_email
            self.save_user_data()
            with open('emails_and_usernames.json', 'r') as file:
                data = json.load(file)
            data['emails'].remove(old_email)
            data['emails'].append(new_email)
            with open('emails_and_usernames.json', 'w') as file:
                json.dump(data, file, indent=4)
            console.print("Email updated successfully.", style="Notice")
            logger.info(f"User [{self.username}] changed email from {old_email} to {new_email}")
        except FileNotFoundError:
            logger.error("Problem with [emails_and_usernames.json]")
            raise FileNotFoundError("File Error. Terminating Program")

    def edit_profile_menu(self):
        while True:
            clear_screen()
            console.print("|Editing Profile|\n", style="Title")
            console.print("What would you like to edit?", style="Info")
            console.print("1. Username")
            console.print("2. Password")
            console.print("3. Email")
            console.print("4. Back")
            choice = input("Choose an option: ")
            if choice == "1":
                clear_screen()
                console.print("|Editing Username|\n", style="Title")
                new_username = input("Enter new username (or press ENTER to go back): ")
                if new_username == "":
                    return
                if User.check_unique_username(new_username):
                    if User.validate_username_format(new_username):
                        self.change_username(new_username)
                        wait_for_key_press()
                    else:
                        console.print("Invalid username format! Usernames can only contain letters, digits, and underscores, and must be 3-20 characters long.", style='Error')
                        wait_for_key_press()
                else:
                    console.print("Username already exists. Please choose a different one.", style="Error")
                    wait_for_key_press()
            elif choice == "2":
                clear_screen()
                console.print("|Editing Password|\n", style="Title")
                new_password = input("Enter new password (or press ENTER to go back): ")
                if new_password == "":
                    return
                if User.validate_password_strength(new_password):
                    self.change_password(new_password)
                    wait_for_key_press()
                else:
                    console.print("Weak password! Passwords must be at least 8 characters long and include uppercase and lowercase letters, digits, and special characters.", style='Error')
                    wait_for_key_press()
            elif choice == "3":
                clear_screen()
                console.print("|Editing Email|\n", style="Title")
                new_email = input("Enter new email (or press ENTER to go back): ")
                if new_email == "":
                    return
                if User.check_unique_email(new_email):
                    if User.validate_email_format(new_email):
                        self.change_email(new_email)
                        wait_for_key_press()
                    else:
                        console.print("Invalid email format! Please enter a valid email address in the format 'example@example.com'." , style='Error')
                        wait_for_key_press()
                else:
                    console.print("Email already exists. Please choose a different one.", style="Error")
                    wait_for_key_press()
            elif choice == "4":
                break
            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()

    @staticmethod
    def register():
        clear_screen()
        console.print("|Registration|\n", style="Title")
        console.print("Please provide the following details to create your account:", style="Info")
        console.print("(or press ENTER to go back)", style='Info')
        email = input("Email: ")
        if email == "":
            return
        username = input("Username: ")
        password = input("Password: ")
        try:
            if not User.validate_email_format(email):
                raise ValueError("Invalid email format! Please enter a valid email address in the format 'example@example.com'.")
            if not User.check_unique_username(username):
                raise ValueError("Username already exists! Please choose a different username.")
            if not User.check_unique_email(email):
                raise ValueError("Email already exists! Please enter a different email.")
            if not User.validate_password_strength(password):
                raise ValueError("Weak password! Passwords must be at least 8 characters long and include uppercase and lowercase letters, digits, and special characters.")
            if not User.validate_username_format(username):
                raise ValueError("Invalid username format! Usernames can only contain letters, digits, and underscores, and must be 3-20 characters long.")
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(email, username, hashed_password)
            new_user.save_user_data()
            new_user.add_email_username()
            console.print("Account created successfully.", style="Notice")
            logger.info(f"A new user registered: {new_user.username}")
            wait_for_key_press()

        except ValueError as e:
            console.print(str(e), style="Error")
            wait_for_key_press()
        except FileNotFoundError as e:
            console.print(e, style="Error")
            exit()

    @staticmethod
    def login():
        clear_screen()
        console.print("|Login|\n", style="Title")
        console.print("Please provide your credentials to log in:", style="Info")
        console.print("(or press ENTER to go back)", style='Info')
        username = input("Username: ")
        if username == "":
            return
        password = pwinput.pwinput(prompt="Password: ", mask="*")
        path = f"users/{username}/{username}.json"

        if os.path.exists(path):
            user_data = User.load_user_data(username)
            if user_data["username"] == username and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
                if not user_data["active"]:
                    console.print("Your account is inactive.", style="Error")
                    wait_for_key_press()
                    return None
                console.print("Login successful.", style="Notice")
                logger.info(f"User [{user_data['username']}] has logged in")
                wait_for_key_press()
                return User(**user_data)

        console.print("Incorrect username or password.", style="Error")
        wait_for_key_press()


class Task:

    def __init__(self, title, description, priority=None, status=None, ID=None, start_time=None, end_time=None, assignees=None, comments=None, history=None):
        self.title = title
        self.description = description
        self.priority = priority if priority is not None else Priority.LOW.value
        self.status = status if status is not None else Status.BACKLOG.value
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]
        self.start_time = start_time if start_time is not None else str(datetime.now())[:19]
        self.end_time = end_time if end_time is not None else str(datetime.now() + timedelta(hours=24))[:19]
        self.assignees = assignees if assignees is not None else []
        self.comments = comments if comments is not None else []
        self.history = history if history is not None else []

    def view_task(self):
        # Create and display a table of task details
        table = Table(title=f"Task: {self.title}", style="cyan")
        table.add_column("ID", justify="center", width=15)
        table.add_column("Title", justify="center", width=15)
        table.add_column("Description", justify="center", width=15)
        table.add_column("Start Time", justify="center", width=25)
        table.add_column("End Time", justify="center", width=25)
        table.add_column("Priority", justify="center", width=15)
        table.add_column("Status", justify="center", width=15)

        table.add_row(self.ID, self.title, self.description, self.start_time[:19], self.end_time[:19], self.priority, self.status)
        console.print(table)

    def change_end_time(self):
        clear_screen()
        console.print("|Changing EndTime|\n", style="Title")
        new_end_time = input("Enter new end time (YYYY-MM-DD HH:MM:SS) (or press ENTER to go back): ")
        if new_end_time == "":
            return False
        try:
            # Ensure the new end time is not before the start time
            if datetime.strptime(new_end_time, "%Y-%m-%d %H:%M:%S") < datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S"):
                console.print("Cannot set a date before start time." , style='Error')
                wait_for_key_press()
                return False
            self.end_time = str(datetime.strptime(new_end_time, "%Y-%m-%d %H:%M:%S"))
            console.print("End time changed successfully.", style="Notice")
            logger.debug(f"Task [id: {self.ID}] end time has changed (current: {self.end_time})")
            wait_for_key_press()
            return True
        except ValueError:
            console.print("Invalid date/time format. Please use the format YYYY-MM-DD HH:MM:SS.", style="Error")
            wait_for_key_press()
            return False

    def change_start_time(self):
        clear_screen()
        console.print("|Changing StartTime|\n", style="Title")
        new_start_time = input("Enter new start time (YYYY-MM-DD HH:MM:SS) (or press ENTER to go back) : ")
        if new_start_time == "":
            return False
        try:
            # Ensure the new start time is not after the start time
            if datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S") > datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S"):
                console.print("Cannot set a date after end time." , style='Error')
                wait_for_key_press()
                return False
            self.start_time = str(datetime.strptime(new_start_time, "%Y-%m-%d %H:%M:%S"))
            console.print("Start time changed successfully.", style="Notice")
            logger.debug(f"Task [id: {self.ID}] start time has changed (current: {self.start_time})")
            wait_for_key_press()
            return True
        except ValueError:
            console.print("Invalid date/time format. Please use the format YYYY-MM-DD HH:MM:SS.", style="Error")
            wait_for_key_press()
            return False

    def change_status(self):
        clear_screen()
        console.print("|Changing Status|\n", style="Title")
        console.print("Available statuses:", style="Info")
        for idx, status in enumerate(Status, start=1):
            console.print(f"{idx}. {status.value}")
        new_status = input("Enter the number for the new status or press ENTER to go back: ")
        if new_status == "":
            return False
        try:
            new_status_idx = int(new_status) - 1
            if 0 <= new_status_idx < len(Status):
                new_status = list(Status)[new_status_idx].name
                self.status = new_status
                console.print("Task status changed successfully.", style="Notice")
                logger.debug(f"Task [id: {self.ID}] status has changed (current: {self.status})")
                wait_for_key_press()
                return True
            else:
                console.print("Invalid status number.", style="Error")
                wait_for_key_press()
                return False
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="Error")
            wait_for_key_press()
            return False

    def change_priority(self):
        clear_screen()
        console.print("|Changing Priority|\n", style="Title")
        console.print("Available priorities:", style="Info")
        for idx, priority in enumerate(Priority, start=1):
            console.print(f"{idx}. {priority.value}")
        new_priority = input("Enter the number for the new priority or press ENTER to go back: ")
        if new_priority == "":
            return False
        try:
            new_priority_idx = int(new_priority) - 1
            if 0 <= new_priority_idx < len(Priority):
                new_priority = list(Priority)[new_priority_idx].name
                self.priority = new_priority
                console.print("Task priority changed successfully.", style="Notice")
                logger.debug(f"Task [id: {self.ID}] priority has changed (current: {self.priority})")
                wait_for_key_press()
                return True
            else:
                console.print("Invalid priority number.", style="Error")
                wait_for_key_press()
                return False
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="Error")
            wait_for_key_press()
            return False

    def change_title(self):
        clear_screen()
        console.print("|Changing Title|\n", style="Title")
        new_title = input("Enter new title (or press ENTER to go back): ")
        if new_title == "":
            return False
        self.title = new_title
        console.print(f"Task title changed to {self.title}", style="Notice")
        logger.debug(f"Task [id: {self.ID}] title has changed (current: {self.title})")
        wait_for_key_press()
        return True

    def change_description(self):
        clear_screen()
        console.print("|Changing Description|\n", style="Title")
        new_description = input("Enter new description (or press ENTER to go back): ")
        if new_description == "":
            return False
        self.description = new_description
        console.print(f"Task description changed to {self.description}", style="Notice")
        logger.debug(f"Task [id: {self.ID}] description has changed (current: {self.description})")
        wait_for_key_press()
        return True

    def view_comments(self):
        # Display the comments associated with the task
        if not self.comments:
            console.print("No comments available for this task to display.", style="Error")
        else:
            clear_screen()
            console.print("|Task's Comments|\n", style="Title")

            table = Table(title="Comments")
            table.add_column("No.", justify="center", style="white", width=5)
            table.add_column("Username", justify="center", style="cyan", no_wrap=True, width=15)
            table.add_column("Role", justify="center", style="magenta", width=15)
            table.add_column("Comment", justify="center", style="green")
            table.add_column("Timestamp", justify="center", style="yellow", width=25)

            # Iterate over comments and add them to the table
            for idx, comment in enumerate(self.comments, start=1):
                table.add_row(str(idx), get_username(comment['user']), comment['role'], comment['comment'], comment['timestamp'])

            console.print(table)

    def add_comment(self, user_id, is_owner: bool):
        clear_screen()
        console.print("|Adding Comment To Task|\n", style="Title")
        new_comment = input("Enter new comment (or press ENTER to go back): " )
        if new_comment == "":
            return False
        # Add the new comment to the comments list
        self.comments.append({
            "user": user_id,
            "comment": new_comment,
            "role": "owner" if is_owner else "assignee",
            "timestamp": str(datetime.now())[:19]
        })
        console.print("Comment added successfully.", style="Notice")
        logger.debug(f"A new comment added to task [id: {self.ID}] by user [{get_username(user_id)}]")
        wait_for_key_press()
        return True

    def remove_comment(self, user: User):
        if not self.comments:
            console.print("No comments available for this task to remove.", style="Error")
            wait_for_key_press()
            return False

        try:
            clear_screen()
            console.print("|Removing Comment From Task|\n", style="Title")
            self.view_comments()
            comment_idx = input("Enter the number of the comment to remove or press ENTER to go back: ")
            if comment_idx == "":
                return False
            comment_idx = int(comment_idx) - 1
            if 0 <= comment_idx < len(self.comments):
                if self.comments[comment_idx]["user"] == user.ID:
                    removed_comment = self.comments.pop(comment_idx)
                    console.print(f"Comment by {get_username(removed_comment['user'])} removed successfully.", style="Notice")
                    logger.debug(f"Comment removed from task [id: {self.ID}] by user [{get_username(removed_comment['user'])}]")
                    wait_for_key_press()
                    return True
                else:
                    console.print("This comment does not belong to you.", style="Error")
                    wait_for_key_press()
                    return False
            else:
                console.print("Invalid comment number.", style="Error")
                wait_for_key_press()
                return False
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="Error")
            wait_for_key_press()
            return False

    def edit_comment(self, user: User):
        if not self.comments:
            console.print("No comments available for this task to edit.", style="Error")
            wait_for_key_press()
            return False

        try:
            clear_screen()
            console.print("|Editing Comment|\n", style="Title")
            self.view_comments()
            comment_idx = input("Enter the number of the comment to edit or press Enter to go back: ")
            if comment_idx == "":
                return False
            comment_idx = int(comment_idx) - 1
            if 0 <= comment_idx < len(self.comments):
                if self.comments[comment_idx]["user"] == user.ID:
                    new_comment = input("Enter new comment: ")
                    self.comments[comment_idx]['comment'] = new_comment
                    self.comments[comment_idx]['timestamp'] = str(datetime.now())[:19]
                    console.print("Comment edited successfully.", style="Notice")
                    logger.debug(f"Comment edited on task [id: {self.ID}] by user [{get_username(self.comments[comment_idx]['user'])}]")
                    wait_for_key_press()
                    return True
                else:
                    console.print("This comment does not belong to you.", style="Error")
                    wait_for_key_press()
                    return False
            else:
                console.print("Invalid comment number.", style="Error")
                wait_for_key_press()
                return False
        except ValueError:
            console.print("Invalid input. Please enter a number.", style="Error")
            wait_for_key_press()
            return False

    def add_to_history(self , ID , action , message = None , members = None , new_amount = None) :
        # Add a new entry to the task's history based on the action
        if action == "add comment":
            new_history = {"user" : ID , "action" : action , "message" : message["comment"]}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "remove comment":
            new_history = {"user" : ID , "action" : action , "description" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
            
        elif action == "edit comment":
            new_history = {"user" : ID , "action" : action , "description" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change status":
            new_history = {"user" : ID , "action" : action , "new status" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change priority":
            new_history = {"user" : ID , "action" : action , "new priority" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change start time":
            new_history = {"user" : ID , "action" : action , "new start time" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change end time":
            new_history = {"user" : ID , "action" : action , "new end time" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "add assignee":
            new_history = {"user" : ID , "action" : action , "new assignees" : members}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "remove assignee":
            new_history = {"user" : ID , "action" : action , "removed assignees" : members}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        elif action == "change title":
            new_history = {"user" : ID , "action" : action , "new title" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
            
        elif action == "change description":
            new_history = {"user" : ID , "action" : action , "new description" : new_amount}
            new_history["timestamp"] = str(datetime.now())[:19]
            self.history.append(new_history)
        
        logger.debug(f"Add new history to task [id : {self.ID}]")

    def view_history(self):
        if not self.history:
            console.print("No history available for this task.", style="Error")
            wait_for_key_press()
            return
        clear_screen()
        # Create a table to display the task's history
        console.print("|Task's History|\n", style="Title")
        table = Table(title="Task's History")
        table.add_column("No.", style="white", justify="center", width=5)
        table.add_column("User", style="cyan", justify="center", width=15)
        table.add_column("Action", style="magenta", justify="center", width=20)
        table.add_column("Amount", style="green", justify="center")
        table.add_column("Timestamp", style="yellow", justify="center", width=25)

        # Iterate over the task's history entries and add them to the table
        for index, entry in enumerate(self.history, start=1):
            user = get_username(entry.get("user", ""))
            action = entry.get("action", "")
            amount = entry.get("new status", "") or \
                     entry.get("new priority", "") or \
                     entry.get("new start time", "") or \
                     entry.get("new end time", "") or \
                     entry.get("new title", "") or \
                     entry.get("new description", "") or \
                     entry.get("message", "")[:20] or \
                     entry.get("description")
            if amount is None:
                amount = str([get_username(x) for x in entry.get("new assignees", "")])
            if amount == "[]":
                amount = str([get_username(x) for x in entry.get("removed assignees", "")])
            timestamp = entry.get("timestamp", "")
            table.add_row(str(index), user, action, amount, timestamp)

        console.print(table)
        wait_for_key_press()


class Project:

    def __init__(self, title, owner, tasks={}, collaborators=None, ID=None):
        self.title = title
        self.owner = owner
        self.tasks = tasks
        self.collaborators = collaborators if collaborators is not None else [owner]
        self.ID = ID if ID is not None else str(uuid.uuid1())[:8]

    def save_project_data(self):
        # Saves the project data to a JSON file in the "projects/" folder.
        project_folder = "projects/"
        os.makedirs(project_folder, exist_ok=True)
        json_file_path = os.path.join(project_folder, f"{self.ID}.json")
        try:
            with open(json_file_path, "w") as json_file:
                json.dump(vars(self), json_file, indent=4)
        except FileNotFoundError:
            raise FileNotFoundError("File Error. Teminating Program.")

    def load_project_data(ID):
        # Loads project data from a JSON file based on the given ID.
        project_folder = "projects/"
        json_file_path = os.path.join(project_folder, f"{ID}.json")
        try:
            with open(json_file_path, "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.error(f"Problem with [{json_file_path}]")
            raise FileNotFoundError("File Error. Terminating Program")

    def update_task(self, new_task: Task):
        self.tasks[new_task.ID] = vars(new_task)

    def view_members(self):
        # Displays the current project members in the console.
        if len(self.collaborators) == 1:
            console.print("There are no project members to display.", style="Error")
            wait_for_key_press()
            return
        clear_screen()
        console.print("|Project Members|\n", style="Title")
        console.print("Current project members:", style="Info")
        for member in self.collaborators:
            if member != self.owner:
                console.print("-", get_username(member))
        wait_for_key_press()

    def add_member(self, member):
        # Adds a new member to the project if they are not already a collaborator.
        if member not in self.collaborators:
            self.collaborators.append(member)
            console.print(f"Member '{get_username(member)}' added to project successfully.", style="Notice")
            User.add_my_project(get_username(member), self.ID)
            self.save_project_data()
            logger.debug(f"A new member [user : {get_username(member)}] added to project [id : {self.ID}] collaborators by owner")
        else:
            console.print(f"User {get_username(member)} has already been added", style='Error')

    def remove_member(self, user_ID):
        # Removes a member from the project if they are a current collaborator.
        if user_ID in self.collaborators:
            self.collaborators.remove(user_ID)

            # delete project id from user's project.json
            User.remove_project(user_ID, self.ID)

            # erase user's name from any tasks
            for task in self.tasks.values():
                if user_ID in task["assignees"]:
                    self.remove_assignee(user_ID, Task(**task))

            self.save_project_data()
            console.print(f"Member '{get_username(user_ID)}' removed from project successfully.", style="Notice")
            logger.debug(f"A member [user : {get_username(user_ID)}] removed from project [id : {self.ID}] collaborators")
        else:
            console.print(f"{get_username(user_ID)} is not a member of the project.", style="Error")

    def add_member_menu(self, user: User):
        # Displays a menu to add new members to the project, accessible only to the owner.
        if self.owner != user.ID:
            console.print("Only the project owner can add members.", style="Error")
            return

        all_usernames = User.get_all_usernames()
        if not all_usernames:
            console.print("There are no available users to add to the project.", style="Error")
            return

        # Display available users and add selected users to the project.
        clear_screen()
        console.print("|Adding Member To Project|\n", style="Title")
        console.print("Available users:", style='Info')
        all_usernames.remove(get_username(self.owner))

        for idx, username in enumerate(all_usernames, start=1):
            console.print(f"{idx}. {username}")

        selected_indices = list(map(lambda x: x.strip(), input("Enter the numbers of the users to add as members (e.g.:'1,2') or press ENTER to go back: ").split(',')))
        if selected_indices[0] == "":
            return

        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                continue
            idx = int(idx_str) - 1
            if idx >= 0 and idx < len(all_usernames):
                selected_username = all_usernames[idx]
                self.add_member(get_ID(selected_username))
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")

    def remove_member_menu(self, user: User):
        # Checks if the user trying to remove a member is the project owner.
        if self.owner != user.ID:
            console.print("Only the project owner can remove members.", style="Error")
            return

        # Creates a list of project members excluding the owner.
        members_to_display = [get_username(member) for member in self.collaborators if member != self.owner]
        if not members_to_display:
            console.print("There are no project members to remove.", style="Error")
            return

        clear_screen()
        console.print("|Removing Member From Project|\n", style="Title")
        console.print("Current project members:", style="Info")
        for idx, member in enumerate(members_to_display, start=1):
            console.print(f"{idx}. {member}")

        selected_indices = list(map(lambda x: x.strip(), input("Enter the numbers of the users to remove from the project (e.g.:'1,2') or press ENTER to go back: ").split(',')))
        if selected_indices[0] == "":
            return

        # Validates and processes the selected removals.
        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                continue
            idx = int(idx_str) - 1
            if idx >= 0 and idx < len(members_to_display):
                selected_member = members_to_display[idx]
                self.remove_member(get_ID(selected_member))
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")

    def view_assignees(self, task: Task):
        if not task.assignees:
            console.print("There are no assignees for this task.", style="Error")
            wait_for_key_press()
            return
        clear_screen()
        console.print("|Task Assignees|\n", style="Title")
        console.print("Current task assignees:", style="Info")
        for member in task.assignees:
            if member != self.owner:
                console.print("-", get_username(member))
        wait_for_key_press()

    def assign_member(self, member, task: Task):
        # Checks if the member is a project collaborator and assigns them to the task if not already assigned.
        if member in self.collaborators:
            if member not in task.assignees:
                task.assignees.append(member)
                console.print(f"Member ({get_username(member)}) assigned to task successfully.", style="Notice")
                self.save_project_data()
                logger.debug(f"A new assignee [user : {get_username(member)}] added to task.")
            else:
                console.print(f"Member ({get_username(member)}) is already assigned to the task.", style="Error")
        else:
            console.print(f"User ({get_username(member)}) is not a member of the project.", style="Error")

    def remove_assignee(self, userID, task: Task):
        # Checks if the assignee is in the task's assignees list and removes them if found.
        if userID in task.assignees:
            task.assignees.remove(userID)
            console.print(f"Member '{get_username(userID)}' removed from task successfully.", style="Notice")
            self.save_project_data()
            logger.debug(f"An assignee [user : {get_username(userID)}] removed from task.")
        else:
            console.print(f"Member '{get_username(userID)}' is not assigned to the task.", style="Error")
        
    def assign_member_menu(self, task: Task , user : User):
        if user.ID != self.owner:
            console.print("Only the project owner can assign members.", style="Error")
            return
        if len(self.collaborators) == 1: 
            console.print("There are no project members to assign.", style="Error")
            wait_for_key_press()
            return
        clear_screen()
        console.print("|Assigning Member To Task|\n", style="Title")
        console.print("Project Members:", style="Info")
        for idx, member in enumerate(self.collaborators[1:], start=1):
            if member != self.owner:
                console.print(f"{idx}. {get_username(member)}")

        selected_indices =  list(map(lambda x:x.strip(),input("Enter the numbers of the users to assign as members (e.g.:'1,2') or press ENTER to go back: ").split(',')))
        if selected_indices[0] == "":
            return
        
        member_ID = []
        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                continue
            idx = int(idx_str)
            if idx >= 1 and idx < len(self.collaborators):
                member_ID.append(self.collaborators[idx])
            else:
                console.print(f"Invalid user number: {idx}.", style="Error")
                return
            
        for member in member_ID:
            self.assign_member(member,task)
        
        task.add_to_history(user.ID, action="add assignee", members=member_ID)

    def remove_assignee_menu(self, task: Task ,user : User):
        if user.ID != self.owner:
            console.print("Only the project owner can remove assignees.", style="Error")
            return
        if not task.assignees:
            console.print("There are no assignees for this task to remove.", style="Error")
            return
        clear_screen()
        console.print("|Removing Assignees From Task|\n", style="Title")
        console.print("Current task assignees:", style="Info")
        for idx, member in enumerate(task.assignees, start=1):
            console.print(f"{idx}. {get_username(member)}")
        
        selected_indices =  list(map(lambda x:x.strip(),input("Enter the numbers of the users to remove from task (e.g.:'1,2') or press ENTER to go back: ").split(',')))
        if selected_indices[0] == "":
            return
        
        member_ID = []
        for idx_str in selected_indices:
            if not idx_str.isdigit():
                console.print("Invalid input. Please enter valid user numbers.", style="Error")
                continue
            idx = int(idx_str) -1
            if idx >= 0 and idx < len(task.assignees):
                member_ID.append(task.assignees[idx])
            else:
                console.print(f"Invalid user number: {idx + 1}.", style="Error")
                return
            
        for member in member_ID:
            self.remove_assignee(member,task)
        task.add_to_history(user.ID, action="remove assignee", members=member_ID)

    def create_manage_task(self, user:User):
        if self.owner != user.ID:
            console.print("Only the project owner can create tasks.", style="Error")
            wait_for_key_press()
            return
        
        clear_screen()
        console.print("|Creating New Task|\n", style="Title")
        console.print("Please provide the following details to create a new task:", style="Info")
        console.print("(or press ENTER to go back)" , style="Info")
        # Get task details from user input
        title = input("Task Title: ")
        if title == "":
            return
        description = input("Task Description: ")
        # Add the new task to the project's task list and save project data
        new_task = Task(title , description)
        self.tasks[new_task.ID]=vars(new_task)
        self.save_project_data()
        console.print("Task created successfully.", style="Notice")
        logger.info(f"A new task [name : {new_task.title} , id : [{new_task.ID}]] created by [{user.username}]")
        wait_for_key_press()
            
        
    def delete_task(self,task : Task , user : User):
        if user.ID == self.owner :
            # Confirm deletion with the user
            choice = input("Are you sure? (y/n)")
            if choice == 'y':
                # Delete the task from the project's task list
                del self.tasks[task.ID]
                console.print(f"Task [id = {task.ID}] has deleted successfully" , style='Notice')
                logger.debug(f"Task [id = {task.ID}] deleted by user [user = {user.username}]")
                wait_for_key_press()
                return True
        else:
            console.print("Only the project owner can delete project.", style="Error")
        wait_for_key_press()
        return False

    def view_project_tasks(self, user: User):
        if not self.tasks:
            console.print("There are no tasks for this project.", style="Error")
            wait_for_key_press()
        else:
            while True:
                clear_screen()
                console.print("|Tasks for Project: ", end="", style="Title")
                console.print(f"{self.title}", end="", style="cyan")
                console.print("|\n", style="Title")

                # Create a table to display tasks based on their status
                main_table = Table(title="Tasks based on their status")
                main_table.add_column("BACKLOG", style="cyan", justify="center", width=50)
                main_table.add_column("TODO", style="yellow", justify="center", width=50)
                main_table.add_column("DOING", style="magenta", justify="center", width=50)
                main_table.add_column("DONE", style="green", justify="center", width=50)
                main_table.add_column("ARCHIVED", style="blue", justify="center", width=50)

                # Create sub-tables for each status
                backlog_table = Table()
                todo_table = Table()
                doing_table = Table()
                done_table = Table()
                archived_table = Table()

                # Fill sub-tables with tasks based on their status
                backlog_table.add_column("ID", justify="center", width=50)
                backlog_table.add_column("Title", justify="center", width=50)
                todo_table.add_column("ID", justify="center", width=50)
                todo_table.add_column("Title", justify="center", width=50)
                doing_table.add_column("ID", justify="center", width=50)
                doing_table.add_column("Title", justify="center", width=50)
                done_table.add_column("ID", justify="center", width=50)
                done_table.add_column("Title", justify="center", width=50)
                archived_table.add_column("ID", justify="center", width=50)
                archived_table.add_column("Title", justify="center", width=50)

                for task in self.tasks.values():
                    instance_task = Task(**task)
                    if instance_task.status == "BACKLOG":
                        backlog_table.add_row(instance_task.ID, instance_task.title)
                    elif instance_task.status == "TODO":
                        todo_table.add_row(instance_task.ID, instance_task.title)
                    elif instance_task.status == "DOING":
                        doing_table.add_row(instance_task.ID, instance_task.title)
                    elif instance_task.status == "DONE":
                        done_table.add_row(instance_task.ID, instance_task.title)
                    else:
                        archived_table.add_row(instance_task.ID, instance_task.title)

                main_table.add_row(backlog_table if len(backlog_table.rows) != 0 else "No task Available",
                                todo_table if len(todo_table.rows) != 0 else "No task Available",
                                doing_table if len(doing_table.rows) != 0 else "No task Available",
                                done_table if len(done_table.rows) != 0 else "No task Available",
                                archived_table if len(archived_table.rows) != 0 else "No task Available")

                console.print(main_table)

                task_id = input("Enter task ID to manage (or press ENTER to go back): ")
                if task_id == "":
                    return
                flag = False
                for task in self.tasks.values():
                    if task["ID"] == task_id:
                        self.manage_task(user, Task(**task))
                        flag = True
                        break
                if not flag:
                    console.print("Invalid Task ID", style="Error")
                    wait_for_key_press()

    def create_project(user: User):
        """
        create project and add its ID to owner's projects.json file
        """
        
        clear_screen()
        console.print("|Creating new Project|\n", style="Title")
        title = input("Enter project title (or press ENTER to go back): ")
        if title == '':
            return
            
        # Create a new project with the entered title and user's ID and save project data to file
        project = Project(title, user.ID)
        project.save_project_data()
        logger.info(f"A new project [name: {project.title}, id: {project.ID}] created by [{user.username}]")
        User.add_my_project(user.username, project.ID)
        console.print("Project created successfully.", style="Notice")
        wait_for_key_press()

    def delete_project(self, user: User):
        """
        Delete the project by removing its ID from the projects.json
        file of all project members and then deleting its file
        
        """
        if self.owner != user.ID:
            console.print("Only the project owner can delete project.", style="Error")
            wait_for_key_press()
            return False
        
        # Confirm project deletion
        choice = input("Are you sure? (y/n)")
        if choice == 'y':
            file_path = f"projects/{self.ID}.json"
            try:
                # Remove project file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    for member in self.collaborators:
                        User.remove_project(member, self.ID)
                    console.print(f"Project '{self.title}' has been deleted successfully.", style="Notice")
                    logger.info(f"Project [id: {self.ID}] deleted by owner [user: {user.username}]")
                    wait_for_key_press()
                    return True
                else:
                    raise FileNotFoundError("No such Project")
            except FileNotFoundError as e:
                console.print(e, style="Error")
                wait_for_key_press()
                return False
        return False
            

    def manage_project_menu(self, user):
        # Menu for managing project tasks and members
        while True:
            clear_screen()
            console.print("|Managing Project: ", end="", style="Title")
            console.print(f"{self.title}", end="", style="cyan")
            console.print("|\n", style="Title")
            console.print("What would you like to do?", style="Info")
            console.print("1. Create Task")
            console.print("2. View Tasks")
            console.print("3. View Members")
            console.print("4. Add Member")
            console.print("5. Remove Member")
            console.print("6. Delete Project")
            console.print("7. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_manage_task(user)
            elif choice == "2":
                self.view_project_tasks(user)
            elif choice == "3":
                self.view_members()
            elif choice == "4":
                self.add_member_menu(user)
                wait_for_key_press()
            elif choice == "5":
                self.remove_member_menu(user)
                wait_for_key_press()
            elif choice == "6":
                if self.delete_project(user):
                    break
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()

    def change_task_fields(self, user: User, task: Task):
        # Allow the user to change various fields of a task
        while True:
            clear_screen()
            console.print("|Updating Task: ", end="", style="Title")
            console.print(f"{task.title}", end="", style="cyan")
            console.print("|\n", style="Title")
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
            # Handle field change choices
            if choice == "1":
                if task.change_status():
                    task.add_to_history(user.ID, action="change status", new_amount=task.status)
                    self.update_task(task)
                    self.save_project_data()
            elif choice == "2":
                if task.change_priority():
                    task.add_to_history(user.ID, action="change priority", new_amount=task.priority)
                    self.update_task(task)
                    self.save_project_data()
            elif choice == "3":
                if task.change_start_time():
                    task.add_to_history(user.ID, action="change start time", new_amount=task.start_time)
                    self.update_task(task)
                    self.save_project_data()
            elif choice == "4":
                if task.change_end_time():
                    task.add_to_history(user.ID, action="change end time", new_amount=task.end_time)
                    self.update_task(task)
                    self.save_project_data()
            elif choice == "5":
                if task.change_title():
                    task.add_to_history(user.ID, action="change title", new_amount=task.title)
                    self.update_task(task)
                    self.save_project_data()
            elif choice == "6":
                if task.change_description():
                    task.add_to_history(user.ID, action="change description", new_amount=task.description)
                    self.update_task(task)
                    self.save_project_data()
            elif choice == "7":
                break
            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()

    def manage_task(self, user: User, task: Task):
        # Manage tasks including changing fields, comments, assignees, history, and deletion
        if user.ID not in task.assignees and user.ID != self.owner:
            console.print("You don't have access to modify this task.", style='Error')
            wait_for_key_press()
            return

        while True:
            clear_screen()
            console.print("|Managing Task: ", end="", style="Title")
            console.print(f"{task.title}", end="", style="cyan")
            console.print("|\n", style="Title")
            task.view_task()
            console.print("What would you like to do?", style="Info")
            console.print("1. Change Task Fields")
            console.print("2. Manage Comments")
            console.print("3. Manage Assignees")
            console.print("4. View History")
            console.print("5. Delete Task")
            console.print("6. Back")

            choice = input("Enter your choice: ")
            # Handle task management choices
            if choice == "1":
                self.change_task_fields(user, task)
                self.update_task(task)
                self.save_project_data()

            elif choice == "2":
                self.manage_comments(task, user)

            elif choice == "3":
                self.manage_assignees(task, user)

            elif choice == "4":
                task.view_history()

            elif choice == "5":
                if self.delete_task(task, user):
                    self.save_project_data()
                    break
            elif choice == "6":
                break
            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()

    def manage_comments(self, task: Task, user: User):
        # Manage comments for a task including viewing, adding, editing, and removing comments
        while True:
            clear_screen()
            console.print("|Managing Comments|\n", style="Title")
            console.print("What would you like to do?", style="Info")
            console.print("1. View Comments")
            console.print("2. Add Comment")
            console.print("3. Edit Comment")
            console.print("4. Remove Comment")
            console.print("5. Back")

            choice = input("Enter your choice: ")
            # Handle comment management choices
            if choice == "1":
                task.view_comments()
                wait_for_key_press()
            
            elif choice == "2":
                if task.add_comment(user.ID, user.ID == self.owner):
                    task.add_to_history(user.ID, action="add comment", message=task.comments[-1])
                    self.update_task(task)
                    self.save_project_data()

            elif choice == "3":
                if task.edit_comment(user):
                    task.add_to_history(user.ID, action="edit comment", new_amount="VIEW EDITED MESSAGE IN VIEW COMMENTS")
                    self.update_task(task)
                    self.save_project_data()
                
            elif choice == "4":
                if task.remove_comment(user):
                    task.add_to_history(user.ID, action="remove comment", new_amount="MESSAGE REMOVED")
                    self.update_task(task)
                    self.save_project_data()
            
            elif choice == "5":
                break
            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()

    def manage_assignees(self, task: Task, user: User):
        # Manage assignees for a task including viewing, assigning, and removing assignees
        while True:
            clear_screen()
            console.print("|Managing Assignees|\n", style="Title")
            console.print("What would you like to do?", style="Info")
            console.print("1. View Assignees")
            console.print("2. Assign Member")
            console.print("3. Remove Assignees")
            console.print("4. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.view_assignees(task)

            elif choice == "2":
                self.assign_member_menu(task, user)
                self.update_task(task)
                self.save_project_data()
                wait_for_key_press()

            elif choice == "3":
                self.remove_assignee_menu(task, user)
                self.update_task(task)
                self.save_project_data()
                wait_for_key_press()

            elif choice == "4":
                break
            else:
                console.print("Invalid choice.", style="Error")
                wait_for_key_press()

    def view_user_projects(user: User):
        """
        load the user's projects.json file and 
        get the ID of projects that is related to user
        
        """
        
        data = User.load_user_projects(user.username)
        if data is not None and len(data['projects']) != 0:
            # Load user's projects if they exist
            user_projects = [Project.load_project_data(proj_id) for proj_id in data["projects"]]

        else:
            console.print("You don't have any projects to display.", style="Error")
            console.print("Create a project first.", style='Error')
            wait_for_key_press()
            return

        clear_screen()
        console.print(f"|{user.username}'s Projects|\n", style="Title")
        table = Table(title="Projects details")
        table.add_column("No.", style="cyan", justify="center", width=5)
        table.add_column("ID", style="magenta", justify="center", width=15)
        table.add_column("Title", style="green", justify="center", width=15)
        table.add_column("Owner", style="yellow", justify="center", width=15)

        project_map = {}
        for i, project in enumerate(user_projects, start=1):
            table.add_row(str(i), project["ID"], project["title"], get_username(project["owner"]))
            project_map[str(i)] = project
        console.print(table)

        while True:
            project_number = input("Enter project number to manage (or press ENTER to go back): ")
            if project_number == "":
                return
            if project_number in project_map:
                # Manage the selected project
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
        clear_screen()
        console.print("|Welcome to the Project Management System|\n", style="Title")
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
                # If login is successful, go to the user menu
                user_menu(user)
        elif choice == "3":
            console.print("Thank you for using the Project Management System. Have a great day!", style="Notice")
            logger.info("EXIT (end of program)")
            break
        else:
            console.print("Invalid choice.", style="Error")
            wait_for_key_press()
        

def user_menu(user: User):
    while True:
        clear_screen()
        console.print(f"|Welcome, {user.username}!|\n", style="Title")
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
            wait_for_key_press()
            break
        else:
            console.print("Invalid choice.", style="Error")
            wait_for_key_press()
            
def get_username(ID):
    # Function to retrieve username based on ID
    data = {}
    try:
        with open("emails_and_usernames.json", 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error("Problem with [emails_and_usernames.json]")
        raise FileNotFoundError("File Error. Terminating Program")
    return data["usernames"][ID]
    
def get_ID(username):
    # Function to retrieve ID based on username
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
    

#.........................#
#      START POINT        #
#.........................#

# Start the main menu loop when the script is executed
if __name__ == "__main__":
    main_menu()