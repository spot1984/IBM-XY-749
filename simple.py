from svg.path import parse_path
from svg.path.path import Line, Arc, QuadraticBezier, CubicBezier,Move,Close
from PIL import Image,ImageDraw
from plotter import Plotter
from color import Color

def simple(path_strings,segments=10):
    beziersegments=segments            # set to 1 for degenerate polylines
    quadraticbeziersegments=segments   # set to 1 for degenerate polylines
    arcsegments=segments               # set to 1 for degenerate polylines

    plotter=Plotter()
    #print(plotter.pen(1), end ="")
    
    im= Image.new(mode="RGB", size=(11*250,int(8.5*250)),color=(255,255,255))
    imd=ImageDraw.Draw(im)
    
    c=Color(0,0,0)
    delta=2
    for path_string in path_strings:
        #print ("***** New path *****")
        path = parse_path(path_string)
        first=None
        for e in path:
            if isinstance(e, Move):
                start=e.start
                x0 = e.start.real
                y0 = e.start.imag
                #print("Move (%.2f, %.2f)" % (x0, y0))
                print(plotter.penup(), end ="")
                print(plotter.move(x0,y0), end ="")
                print(plotter.pendown(), end ="")
            if isinstance(e, Line):
                start=e.start
                end=e.end
                x0 = e.start.real
                y0 = e.start.imag
                x1 = e.end.real
                y1 = e.end.imag
                #print("Line (%.2f, %.2f) - (%.2f, %.2f)" % (x0, y0, x1, y1))
                # assumes plotter was at start
                print(plotter.move(x1,y1), end ="")
                #imd.line([(x0,y0),(x1,y1)],c.tuple())
                c.inc(delta)   
                '''
            if isinstance(e, Arc):
                start=e.point(0.0)
                end=e.point(1.0)
                x0 = start.real
                y0 = start.imag
                x1 = end.real
                y1 = end.imag
                #print("Arc (%.2f, %.2f) - (%.2f, %.2f)" % (x0, y0, x1, y1))
                # assumes plotter was at start
                pl=e.start
                for i in range(1,arcsegments+1):
                    j=float(i)/arcsegments
                    p=e.point(j)
                    print(plotter.move(p.real,p.imag), end ="")
                    #imd.line([(pl.real,pl.imag),(p.real,p.imag)],fill=c.tuple())
                    c.inc(delta)   
                    pl=p
            if isinstance(e, QuadraticBezier):
                start=e.point(0.0)
                end=e.point(1.0)
                x0 = start.real
                y0 = start.imag
                x1 = end.real
                y1 = end.imag
                #print("QuadraticBezier (%.2f, %.2f) - (%.2f, %.2f)" % (x0, y0, x1, y1))
                # assumes plotter was at start
                pl=e.start
                for i in range(1,quadraticbeziersegments+1):
                    j=float(i)/quadraticbeziersegments
                    p=e.point(j)
                    print(plotter.move(p.real,p.imag), end ="")
                    #imd.line([(pl.real,pl.imag),(p.real,p.imag)],fill=c.tuple())
                    c.inc(delta)   
                    pl=p
                    '''
            if isinstance(e, CubicBezier):
                start=e.point(0.0)
                end=e.point(1.0)
                x0 = start.real
                y0 = start.imag
                x1 = end.real
                y1 = end.imag
                #print("CubicBezier (%.2f, %.2f) - (%.2f, %.2f)" % (x0, y0, x1, y1))
                # assumes plotter was at start
                pl=e.start
                for i in range(1,beziersegments+1):
                    j=float(i)/beziersegments
                    p=e.point(j)
                    print(plotter.move(p.real,p.imag), end ="")    
                    #imd.line([(pl.real,pl.imag),(p.real,p.imag)],fill=c.tuple())
                    c.inc(delta)   
                    pl=p
            if first==None:
                first=start
            if isinstance(e, Close):
                x0=first.real
                y0=first.imag
                #print("Close (%.2f, %.2f)" % (x0, y0))
                print(plotter.move(x0,y0), end ="")    
                imd.line([(first.real,first.imag),(end.real,end.imag)],fill=c.tuple())
                c.inc(delta)
                first=None
        print(plotter.penup(), end ="")
    print(plotter.move(0,0))
    
    im.show()
    
    # release plotter
    plotter=None
