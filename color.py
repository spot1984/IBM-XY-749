from random import randint

# create a color from a string
def colorFromString(s):
    i=0
    if s[0:1]=='#':
        i=1
    r=int(s[i:i+2],16)
    g=int(s[i+2:i+4],16)
    b=int(s[i+4:i+6],16)
    return Color(r,g,b)

class Color:
    r=0
    g=0
    b=0
    # initialize from values
    def __init__(self,r,g,b):
        self.r=r    
        self.g=g
        self.b=b
      
    # increment color
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

    # compare this color to another
    def difference(self,other):
        # constants for relative importance from luminance calculation
        # integers used 
        #return  abs(self.r-other.r)+ \
        #        abs(self.g-other.g)+ \
        #        abs(self.b-other.b)
        return  299*abs(self.r-other.r)+ \
                587*abs(self.g-other.g)+ \
                114*abs(self.b-other.b)
        
    # return as a tuple
    def tuple(self):
        return(self.r,self.g,self.b)
    
    # return a random color
    def rnd(self):
        return(randint(0,256),randint(0,256),randint(0,256))
