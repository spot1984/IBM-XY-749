# IBM XY/749 (IBM XY/749, CalComp Model 81)

# todo
#   Move newline stuff out of class and just return strings.

#2690x2060
class Plotter:
    maxx=2690
    maxy=2060
    commandsperline=10
    count=0
    def newline(self):
        self.count+=1
        if self.count>self.commandsperline:
            self.count=0
            return "\n"
        return ""
    def pen(self,pen):
        return ('f%d;%s'%(pen,self.newline()))#.encode('utf-8')
    def fast(self):
        return ('f10,30;%s'%(self.newline()))#.encode('utf-8')
    def slow(self):
        return ('f10,1;%s'%(self.newline()))#.encode('utf-8')
    def penup(self):
        return ('h%s'%(self.newline()))#.encode('utf-8')
    def pendown(self):
        return ('i%s'%(self.newline()))#.encode('utf-8')
    def move(self,x,y):
        return ('%d/%dk%s'%(int(x),int((8.5*250-1)-y),self.newline()))#.encode('utf-8')
    def moverelative(self,x,y):
        return ('%d/%dj%s'%(int(x),int((8.5*250-1)-y),self.newline()))#.encode('utf-8')
    def xaxis(self,length, intervals, markinglength):
        return ('x%d,%d,%d;%s'%(length,intervals,markinglength,self.newline()))#.encode('utf-8')
    def yaxis(self,length, intervals, markinglength):
        return ('y%d,%d,%d;%s'%(length,intervals,markinglength,self.newline()))#.encode('utf-8')
    def circulararc(self,radius,a0,a1):
        return ('o0 %d,%d,%d;%s'%(radius,a0,a1,self.newline()))#.encode('utf-8')
    def textsize(self,size):
        return ('z%d;%s'%(size,self.newline()))#.encode('utf-8')
    def text(self,string):
        return ('b%s\r;%s'%(string,self.newline()))#.encode('utf-8')
    def mark(self,mark):
        return ('m%d;%s'%(mark,self.newline()))#.encode('utf-8')
    
        