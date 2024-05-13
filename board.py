import users
from enum import Enum



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
    def __init__(self,title,defenition,due,status=str(TaskStatus.BACKLOG),priority=str(TaskPriority.LOW)):
        pass
