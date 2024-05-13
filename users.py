from enum import Enum
import json
import base64
import uuid


#................................

class UserStatus(Enum):
    ACTIVE = 1
    DEACTIVE = 0
    
    def __str__(self):
        return self.name


class User:
    def __init__(self):
        email,password,username = User.create_user()
        self._email=email
        self._password=str(base64.b64encode(password.encode("utf-8")))
        self.username=username
        self.status=str(UserStatus.ACTIVE)
        print(self.status)
        self.ID=str(uuid.uuid1())
        self._create_user_data()
    
    def _create_user_data(self):
        with open ('users/'+self.username+'.json','w') as file:
            data = vars(self)
            json.dump(data,file,indent=4)

    def create_user():
        email = input("Please enter a valid Email: ")
        password = input("Please enter a valid Password: ")
        username = input("Please Enter a valid uername: ")
        return email,password,username

    def __str__(self):
        return str(vars(self))

def register_user(email, username, password):
    try:
        if not is_valid_email(email):
            raise ValueError("Invalid email format")
        if not is_valid_username(username):
            raise ValueError("Invalid username format")
        if not is_unique_username(username):
            raise ValueError("Username already exists")
        if not is_strong_password(password):
            raise ValueError("Weak password")
        print("[bold green]Registration successful![/bold green]")
    except ValueError as e:
        print("[bold red]Error:[/bold red]", str(e))

def is_valid_email(email):
    pass

def is_valid_username(username):
    pass

def is_unique_username(username):
    pass

def is_strong_password(password):

    pass

kimia = User()
print(kimia)
# print(mahdi)