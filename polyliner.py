from svg.path import parse_path
from svg.path.path import Line, Arc, QuadraticBezier, CubicBezier,Move,Close
#from PIL import Image,ImageDraw,ImageFont
#from plotter import Plotter
#from color import Color
from pickle import NONE
from scipy.spatial import distance

def pointtuple(p,quantization):
    return (int(p.real/quantization)*quantization, int(p.imag/quantization)*quantization)
    
def polyliner(path_strings, segments=10,weldradius=12,quantization=1):    
    beziersegments=segments            # set to 1 for degenerate polylines
    quadraticbeziersegments=segments   # set to 1 for degenerate polylines
    arcsegments=segments               # set to 1 for degenerate polylines

    # create list of unique points
    #todo rework this to quantization points
    points=set()
    for path_string in path_strings:
        path = parse_path(path_string)
        for e in path:
            if isinstance(e, Move):
                points.add(pointtuple(e.start,quantization))
            if isinstance(e, Line):
                points.add(pointtuple(e.start,quantization))
                points.add(pointtuple(e.end,quantization))
            if isinstance(e, Arc):
                for i in range(arcsegments+1):
                    j=float(i)/beziersegments
                    p=e.point(j)
                    points.add(pointtuple(p,quantization))
            if isinstance(e, QuadraticBezier):
                for i in range(quadraticbeziersegments+1):
                    j=float(i)/beziersegments
                    p=e.point(j)
                    points.add(pointtuple(p,quantization))
            if isinstance(e, CubicBezier):
                for i in range(beziersegments+1):
                    j=float(i)/beziersegments
                    p=e.point(j)
                    points.add(pointtuple(p,quantization))
    # convert point set into indexable list
    points=list(points)

    #sort points by x
    points.sort(key=lambda p:p[0])
        
    # create set of unique lines
    lines=set()
    def adduniqueline(i0,i1):
        if i0==i1:
            return
            line=(i0,i1)   # allows degenerate line segments
        elif i0<i1:
            line=(i0,i1)
        else:
            line=(i1,i0)
        lines.add(line)
            
    firsti=None
    starti=None 
    endi=None   
    for path_string in path_strings:
        path = parse_path(path_string)
        firsti=None
        for e in path:
            if isinstance(e, Move):
                starti=points.index(pointtuple(e.start,quantization))
                endi=starti
            if isinstance(e, Line):
                starti=points.index(pointtuple(e.start,quantization))
                endi=points.index(pointtuple(e.end,quantization))
                adduniqueline(starti,endi)
                #endi=points.index(pointtuple(e.end,quantization))
            if isinstance(e, Arc):
                pp=pointtuple(pointtuple(e.point(float(0)/arcsegments),quantization),quantization)
                ppi=points.index(pp)
                starti=ppi
                for i in range(1,arcsegments+1):
                    j=float(i)/arcsegments
                    p=pointtuple(e.point(j),quantization)
                    pi=points.index(p)
                    adduniqueline(ppi,pi)
                    ppi=pi
                endi=ppi
                #endi=points.index(pointtuple(e.end,quantization))
            if isinstance(e, QuadraticBezier):
                pp=pointtuple(e.point(float(0)/quadraticbeziersegments),quantization)
                ppi=points.index(pp)
                starti=ppi
                for i in range(1,quadraticbeziersegments+1):
                    j=float(i)/quadraticbeziersegments
                    p=pointtuple(e.point(j),quantization)
                    pi=points.index(p)
                    adduniqueline(ppi,pi)
                    ppi=pi
                endi=ppi
                #endi=points.index(pointtuple(e.end,quantization))
            if isinstance(e, CubicBezier):
                pp=pointtuple(e.point(float(0)/beziersegments),quantization)
                ppi=points.index(pp)
                starti=ppi
                for i in range(1,beziersegments+1):
                    j=float(i)/beziersegments
                    p=pointtuple(e.point(j),quantization)
                    pi=points.index(p)
                    adduniqueline(ppi,pi)
                    ppi=pi
                endi=ppi
                #endi=points.index(pointtuple(e.end,quantization))
            if firsti==None:
                firsti=starti
            if isinstance(e, Close):
                adduniqueline(endi,firsti)
                firsti=None
                
    # debug show the image as read    
    if False:
        from PIL import Image,ImageDraw
        from color import Color
        im= Image.new(mode="RGB", size=(11*250,int(8.5*250)),color=(255,255,255))
        imd=ImageDraw.Draw(im)    
        c=Color(0,0,0)
        delta=8  
        for line in lines:
            p0=points[line[0]]
            p1=points[line[1]]
            imd.line([p0,p1],fill=c.tuple())
            c.inc(delta)
        im.show()
                        
    # convert lines set into indexable list
    lines=list(lines)

    # now we have a collection of unique points and a collection of unique lines indexing the unique points
   
    #create array of len(points) empty lists to contain line indices
    pointlinereferences=[[] for x in range(len(points))]
    # populate point arrays with line indices
    for linei in range(len(lines)):
        line=lines[linei]
        # note degenerate line will create two segments on the same point, algorithm will still work
        pointlinereferences[line[0]].append(linei)
        pointlinereferences[line[1]].append(linei)

    '''
    New weld routine - "always weld closest vertices"
        calculate distance and index to nearest vertex for all vertices
        while there are two vertices with edges closer than weldr:
            Combine the closest two vertices
            Calculate shortest distance for the new vertex and for vertices in the neighborhood
    '''

    '''
    Weld routine that 
    loop source through vertices 
        Loop target from next vertex until next one is too far x or end
            if target has pointline references and distsquared <thresh
                move target line references to source vertex and change target to source in target's lines 
    '''
    # weld vertices 
    welds=0 
    welded=0
    if weldradius>0:
        wr2=weldradius**2
        # loop through all points but the last
        for si in range(len(points)-1):
            source=points[si]
            weldlist=[source]
            # loop through next point throught the last
            for ti in range(si+1,len(points)):
                target=points[ti]
                if (len(pointlinereferences[ti])>0) and (((source[0]-target[0])**2+(source[1]-target[1])**2)<=wr2):
                    # add target to list to be welded
                    weldlist.append(target)
                    # link all target line segments to source vertex
                    while len(pointlinereferences[ti])>0:
                        linei = pointlinereferences[ti].pop()
                        line=lines[linei]
                        # determine the other point from the line
                        oi=line[1] if line[0]==ti else line[0]
                        # create properly ordered new line
                        newline=(si if si<=oi else oi,si if si>oi else oi)
                        # add newline if it is unique, and get newline index in lines
                        if newline in lines:
                            newlinei=lines.index(newline)
                        else:        
                            newlinei=len(lines)
                            lines.append(newline)
                        # does the new line segment already exist for source?
                        if newlinei in pointlinereferences[si]:
                            # line from source to other point does already exist
                            # remove the line reference from the other point to the target 
                            pointlinereferences[oi].pop(pointlinereferences[oi].index(linei))
                        else:
                            # line from source to other point does not already exist 
                            # add the newlinei to source 
                            pointlinereferences[si].append(newlinei)
                            # replace the line reference in the other point line list with the new line index
                            pointlinereferences[oi][pointlinereferences[oi].index(linei)]=newlinei
            # replace source vertex with average welded vertices (equal weighting)
            if len(weldlist)>1:
                x=0
                y=0
                for p in weldlist:
                    x+=p[0]
                    y+=p[1]
                points[si]=(int(x/len(weldlist)),int(y/len(weldlist)))
                welds+=1
                welded+=len(weldlist)

    # create polylines from lines and points
    polylines=[]    
    currentposition=(0,0)    # current position
    while (True):
        # find point with connected lines closest to current position 
        nextindex=-1
        nextdistancesquared=99999999 #(250*12)^2=9000000
        for i in range(len(points)):
            if len(pointlinereferences[i])>0:
                distancesquared=(points[i][0]-currentposition[0])**2+(points[i][1]-currentposition[1])**2
                if distancesquared<nextdistancesquared:
                    nextdistancesquared=distancesquared
                    nextindex=i
        if nextindex<0:
            # no more vertices with lines, we're done
            break
        else:
            # start a new polyline
            polyline=[]
            while (True):
                # add current point to polyline
                polyline.append(points[nextindex])
                # are there lines at this point?
                if len(pointlinereferences[nextindex])>0:
                    '''
                    # select closest point to first point
                    nextlinei=-1
                    nextdistancesquared=99999999 #(250*12)^2=9000000
                    for linei in pointlinereferences[nextindex]:
                        line=lines[linei]
                        oi=line[1] if line[0]==nextindex else line[0]
                        distancesquared=(points[oi][0]-polyline[0][0])**2+(points[oi][1]-polyline[0][1])**2
                        if distancesquared<nextdistancesquared:
                            nextlinei=linei
                            nextdistancesquared=distancesquared
                    '''
                    #select point with the most lines
                    nextlinei=-1
                    maxlines=0
                    for linei in pointlinereferences[nextindex]:
                        line=lines[linei]
                        oi=line[1] if line[0]==nextindex else line[0]
                        nlines=len(pointlinereferences[oi])
                        if maxlines<nlines:
                            nextlinei=linei
                            maxlines=nlines
                    # follow next line (this can be optimized: closest to start point, straightest path, etc)
                    linei=pointlinereferences[nextindex].pop(pointlinereferences[nextindex].index(nextlinei))
                    line=lines[linei]
                    # determine next point from line indices
                    if line[0]==nextindex:
                        nextindex=line[1]   # this may be self for degenerate but will still work
                    else:
                        nextindex=line[0]
                    pointlinereferences[nextindex].pop(pointlinereferences[nextindex].index(linei))
                else:
                    # no more lines at this point
                    # save current position to find closest next point
                    currentposition=points[nextindex] 
                    # done making this polyline
                    break
            # add this polyline to the list of polylines
            polylines.append(polyline)
                
    #now polylines contains a list of polylines which are lists of ordered points
    return polylines
