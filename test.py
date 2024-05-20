from enum import Enum
def _id_generator():
    seed = 12032341
    
    while(True):
        yield str(seed)
        seed +=1
    
    
g = _id_generator()


class a:
    def __init__(self , a : str):
        self.a = a
    
    
obj1 = a(2)
print(type(obj1.a))

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