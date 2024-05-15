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

def load_data():
    if not os.path.exists("data.json"):
        return {"users": [], "projects": []}
    with open("data.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
