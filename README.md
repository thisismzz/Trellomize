# Trellomize (Terminal Based project management)

## overview
Trellomize is a powerful project management system executed in the terminal. Programmed with python language. Users can create accounts, define new projects, manage projects they’re part of, and organize their own projects. Key features include task fields and member assignments.

## Description
This program consists of four main parts:
### User class :
Handles functionalities like login, registration, and profile editing (password, email, and username).

Creates a new folder in “users/” for each registered user, along with a JSON file containing user data.

Adds user email and username to the “emails_and_usernames.json” file.

First when a new user register, a new folder in "users/" and in that folder a json file including user's data will be create. Then user's email and username will add to "emails_and_usernames.json" file.

### Project class :
Provides methods for adding and removing members, creating tasks, and managing tasks.

After creating a new project, a corresponding JSON file is generated in the “projects/” directory.

The project ID is added to a “projects.json” file located in the owner’s folder when a new member is added.


### Task class : 
Handles task attribute changes (e.g., status, priority, title).

Manages the style for printing task details.

Maintains a history of attribute modifications, including the modifier user, action, timestamp, and new value.

### manager.py : 
The most critical part of the project.
Creates a manager with capabilities to purge the entire database, deactivate or activate users.

Command-line usage: 

py manager.py create-admin --username [username] --password [password]

py manager.py login --username [username] --password [password]

py manager.py purge-data --username [username] --password [password]


# contact me
Please email me if you have any comments or suggestions. I look forward to hearing your thoughts.

Email: iammahdizz@gmail.com

Feel free to fork my code and explore it further!