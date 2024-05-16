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
    

for _ in range(10):
    obj = a()
    print(obj)