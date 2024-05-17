def _id_generator():
    seed = 12032341
    
    while(True):
        yield str(seed)
        seed +=1
    
    
g = _id_generator()


class a:
    def __init__(self):
        self.a=next(g)
    
    def __str__(self):
        return self.a
    


s1 = list(map(lambda x:x.strip(),input("enter ").split(',')))
print(s1)