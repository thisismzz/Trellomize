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

        except ValueError as e:
            console.print("Error: " + str(e), style="Error")

def load_data():
    if not os.path.exists("data.json"):
        return {"users": [], "projects": []}
    with open("data.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
