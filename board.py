import users
from enum import Enum
import uuid




class Project:
    def __init__(self,name,title,leader : users.User):
        self.name=name
        self.title=title
        self.leader=leader
        
        
    def add_member(self, user):
        self.members.append(user)

    def remove_member(self, user):
        self.members.remove(user)
        

class TaskStatus(Enum):
    BACKLOG = 0
    TODO = 1
    DOING = 2
    DONE = 3
    ARCHIVED = 4
    
    def __str__(self):
        return self.name

class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    
    def __str__(self):
        return self.name

class Task:
    def __init__(self,title,description,assignees:users.User,due,status=str(TaskStatus.BACKLOG),priority=str(TaskPriority.LOW)):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.assignees = assignees
        self.priority = priority
        self.status = status
        self.created_at = datetime.now()
        self.due = due
        self.comments = []
    def create_task():
        title = input("Please enter a title: ")
        description = input("Please write a description: ")
        show the list of member of project
        assignees = input()
        print("Choose the priority of you task:")
        priority = input("Please a description: ")
        status = input("Please write a description: ")
        return title,description,assignees,priority,status 