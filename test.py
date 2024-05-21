from enum import Enum
import os
import shutil
def _id_generator():
    seed = 12032341
    
    while(True):
        yield str(seed)
        seed +=1
    
    
g = _id_generator()


class a:
    def salam(self):
        print("salam")
    
    
# obj1 = a(2)
# print(type(obj1.a))
# obj = a()
# obj.salam()
# exit("salamdsdasd")
os.remove("projects")


# s1 = list(map(lambda x:x.strip(),input("enter ").split(',')))
# print(s1)

class Priority(Enum):
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    
    def __str__():
        print("salam")
        
# print(Priority)