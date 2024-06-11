from random import randint
import numpy as np

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

    def lab(self):
        #sR, sG and sB (Standard RGB) input range = 0 ÷ 255
        #X, Y and Z output refer to a D65/2° standard illuminant.
        var_R = ( self.r / 255.0 )
        var_G = ( self.g / 255.0 )
        var_B = ( self.b / 255.0 )
        
        if ( var_R > 0.04045 ): 
            var_R = np.power(( ( var_R + 0.055 ) / 1.055 ), 2.4)
        else:
            var_R = var_R / 12.92
        if ( var_G > 0.04045 ):
            var_G = np.power(( ( var_G + 0.055 ) / 1.055 ), 2.4)
        else:
            var_G = var_G / 12.92
        if ( var_B > 0.04045 ):
            var_B = np.power(( ( var_B + 0.055 ) / 1.055 ), 2.4)
        else:
            var_B = var_B / 12.92
        
        var_R = var_R * 100
        var_G = var_G * 100
        var_B = var_B * 100
        
        X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
        Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
        Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

        # Scale to reference        
        var_X = X / 95.047
        var_Y = Y / 100.0
        var_Z = Z / 108.883
        
        # Convert to Lab
        if ( var_X > 0.008856 ): 
            var_X = np.power(var_X,( 1.0/3.0 ))
        else:                    
            var_X = ( 7.787 * var_X ) + ( 16.0 / 116.0 )
        if ( var_Y > 0.008856 ): 
            var_Y = np.power(var_Y,( 1/3.0 ))
        else:                    
            var_Y = ( 7.787 * var_Y ) + ( 16.0 / 116.0 )
        if ( var_Z > 0.008856 ): 
            var_Z = np.power(var_Z,( 1.0/3.0 ))
        else:                    
            var_Z = ( 7.787 * var_Z ) + ( 16.0 / 116.0 )
        
        L = ( 116 * var_Y ) - 16
        a = 500 * ( var_X - var_Y )
        b = 200 * ( var_Y - var_Z )
        
        return (L,a,b)

    # compare this color to another, return a difference for comparisons
    def difference(self,other):
        algorithm=2
        if algorithm==0:
            # straight RGB comparison (squaring terms could improve performance) 
            return  abs(self.r-other.r)+ \
                    abs(self.g-other.g)+ \
                    abs(self.b-other.b)
        elif algorithm==1:
            # luminance weighted RGB comparison (squaring terms could improve performance)
            return  299*abs(self.r-other.r)+ \
                    587*abs(self.g-other.g)+ \
                    114*abs(self.b-other.b)
        else:
            # distance squared in Lab CIE space
            slab=self.lab()
            olab=other.lab()
            return np.power(slab[0]-olab[0],2)+np.power(slab[1]-olab[1],2)+np.power(slab[2]-olab[2],2)
        
    # return as a tuple
    def tuple(self):
        return(self.r,self.g,self.b)
    
    # return a random color
    def rnd(self):
        return(randint(0,256),randint(0,256),randint(0,256))
