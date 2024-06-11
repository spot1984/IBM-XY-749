# IBM XY/749 (IBM XY/749, CalComp Model 81)

#2690x2060
class Plotter:
    maxx=2690
    maxy=2060

    # select pen
    def pen(self,pen):
        return ('f%d;'%(pen))
    # fast speed
    def fast(self):
        return ('f10,30;')
    # slow speed (only when pen is down)
    def slow(self):
        return ('f10,1;')
    # lift pen
    def penup(self):
        return ('h')
    # lower pen
    def pendown(self):
        return ('i')
    # move pen to absolute location
    def move(self,x,y):
        return ('%d/%dk'%(int(x),int((8.5*250-1)-y)))
    # move pen to relative location
    def moverelative(self,x,y):
        return ('%d/%dj'%(int(x),int((8.5*250-1)-y)))
    # draw an x axis
    def xaxis(self,length, intervals, markinglength):
        return ('x%d,%d,%d;'%(length,intervals,markinglength))
    # draw a y axis
    def yaxis(self,length, intervals, markinglength):
        return ('y%d,%d,%d;'%(length,intervals,markinglength))
    # draw a circular arc
    def circulararc(self,radius,a0,a1):
        return ('o0 %d,%d,%d;'%(radius,a0,a1))
    # set text size
    def textsize(self,size):
        return ('z%d;'%(size))
    # print text string
    def text(self,string):
        return ('b%s\r;'%(string))
    # place a marker (graphical icon)
    def mark(self,mark):
        return ('m%d;'%(mark))
    
        