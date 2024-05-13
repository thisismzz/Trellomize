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
    def __init__(self,email,password,username):
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

    

mahdi = User("mahdi@gmail.com","1234","mzz")
# print(mahdi)