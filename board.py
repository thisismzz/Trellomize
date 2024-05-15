import users
from enum import Enum
import uuid
from datetime import datetime



class Project:
    def __init__(self,name,title,leader : users.User,collabrators):
        self.name=name
        self.title=title
        self.leader=leader
        self.collabrators = collabrators
        
    def add_member(self, user):
        self.members.append(user)

    def remove_member(self, user):
        self.members.remove(user)
        

class TaskStatus(Enum):
    BACKLOG = 1
    TODO = 2
    DOING = 3
    DONE = 4
    ARCHIVED = 5
    
    def __str__(self):
        return self.name

    def print_task_status():
        print("Choose the status of you task:")
        for status in TaskStatus:
            print(f"{status.value} : {status.name}")

class TaskPriority(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    
    def __str__(self):
        return self.name

    def print_task_priority():
        print("Choose the priority of you task:")
        for priority in TaskPriority:
            print(f"{priority.value} : {priority.name}")


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
        
    def add_comment(self,comment):
        self.comments.append(comment)

    def create_task():
        title = input("Please enter a title: ")
        description = input("Please write a description: ")
        assignees = input()   # show the list of member of project
        TaskPriority.print_task_priority()
        priority = input("Please enter the priority name : ")
        TaskStatus.print_task_status()
        status = input("Please enter the status name : ")
        due = datetime.strptime(input("Enter the due time (HH:MM AM/PM): ") , "%I:%M %p")

        return Task(title,description,assignees,due,TaskStatus[status],TaskPriority[priority])
