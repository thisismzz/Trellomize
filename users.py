from enum import Enum
import json

#................................

class userStatus:
    ACTIVE = 1
    DEACTIVE = 0


class user:
    def __init__(self,email,password,username):
        self._email=email
        self._password=password
        self.username=username
        self.status=userStatus.ACTIVE
        self._create_user_data()
    
    def _create_user_data(self):
        with open ('users/'+self.username+'.json','w') as file:
            data = vars(self)
            json.dump(data,file,indent=4)


mahdi = user("mahdi@gmail.com","1234","mzz")
# print(mahdi)