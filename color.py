from random import randint

class Color:
    r=0
    g=0
    b=0
    def __init__(self,r,g,b):
        self.r=r    
        self.g=g
        self.b=b
    
    def inc(self,d):
        self.r+=d
        if self.r>255:
            self.r=0
            self.g=self.g+d
        if self.g>255:
            self.g=0
            self.b=self.b+d
        if self.b>255:
            self.b=0    
    
    def tuple(self):
        return(self.r,self.g,self.b)
    
    def rnd(self):
        return(randint(0,256),randint(0,256),randint(0,256))
