#!/usr/bin/python3
'''
    ibm_xy_749.py
    by D. Scott Williamson 
    June 27, 2023
    
    Usage:
        python IBMxy749.py input.svg

        python IBMxy749.py input.svg >/dev/ttyS0
        python IBMxy749.py input.svg >outputfile.txt
        python cp outputfile.txt /dev/ttyS0

        python IBMxy749.py input.svg >com10:
        python IBMxy749.py input.svg >outputfile.txt
        python copy outputfile.txt com10:
        
    Converts SVG paths into plotter commands printed in the output.
    Output can be viewed, piped to a file, or piped to the serial device.
    SCVG paths expected to be in machine units (inches scaled by 250)  
    Compatible with IBM X/Y 748/750, CalComp Model 81 plotters, and TEWIP281

    This script requires svg.path, install it like this: pip3 install svg.path
    Source: https://github.com/regebro/svg.path/blob/master/src/svg/path/path.py
    SVG reference: https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
        
    From: https://books.google.com/books?id=0deFa0SWTOkC&pg=PP177&lpg=PP177&dq=IBM+%22XY/749%22+%22XY/750%22&source=bl&ots=yje3iC2c50&sig=ACfU3U26r2vUBudlii68u7Go8my1YB593Q&hl=en&sa=X&ved=2ahUKEwjA1OfM5LH_AhU7kYkEHfUJBu84ChDoAXoECAQQAw#v=onepage&q=IBM%20%22XY%2F749%22%20%22XY%2F750%22&f=false
    IBM X/Y 749 specifications 
        step size .004 inches (250 steps per inch)
        Maximum speed 17.1 in/s
        1k buffer
        8 pens
                
    Commands reverse engineered from https://en.industryarena.com/forum/calcomp-m81-pen-plotter-ibm-xy750--114895.html
    and http://web.mit.edu/~xavid/bin/eagle.def
    
        ;            between commands
        f%p          select pen p (1-7, 0 returns pen
        f10,%d;      pen down feedrate, <30 slow, >=30 fast
        i            lower pen
        h            raise pen
        z%s;         sets text size
        btext(enter) draws text ends with enter ("\r")
        m%d;         mark type x 
                         0 square
                         1 triangle
                         2 X
                         3 +
                         4 Y
        %x/%yk       moves absolute position
        %x/%yj       moves relative position
        o0 %r,%s,%e  circle radius r, from s to e angle
        x%X,%S,%H;   plots X axis, marking S intervals, H height
        y%X,%S,%W;   plots Y axis, marking S intervals, W width
        s            sends returns free buffer space
        !            shows absolute machine coordinates
        ?            starts digitize, press select prints coords
        
        v            draws big box, there may be a page size commend
        w 

[TEWIP281]

Type     = PenPlotter
Long     = "tewidata P 281 plotter"
Init     = "H\n"
Reset    = "HF0\n"
Width    = 16
Height   = 11
ResX     = 254
ResY     = 254
PenSelect  = "F%u\n"
PenUp      = "H"
PenDown    = "I"
Move       = "%d/%dK\n"
Draw       = "%d/%dK\n"
PenCircleRxn = "O%d,180,540\n" ; Rxn = Radius X (long, negative)

[CALCOMP_M84]

Type            = PenPlotter
Long            = "Calcomp M84 Plotter"
Init            = ""
Reset           = "F\nH\nR0\n"
Width           = 16
Height          = 11
ResX            = 254
ResY            = 254
PenSelect       = "F%u\n"
Move            = "C %d,%d HK\n"
Draw            = "C %d,%d IK\n"
PenCircleCxCyRxCxCyRx  = "C %d,%d HK \n O0 %d,0,360\n"
PenVelocity     = "F10,%d\n"

    Recommended Inkscape settings
        Preferences
            Interface
             [x] Origin at upper left with y-axis pointing down (requires restart)
        Document properties 
            inches
            width 11
            height 8.5
            scale 250
        All content needs to fit within the page
        

    ToDo:
        Colors
            x Pass pen colors in on command line: pen colors (optional, default 000000) -p0=#000000
            Parse path styles and extract stroke:#rrggbb or fill="#DDB893"
            Lab Cie or Hue matching of color to pen color
            Command line to select fill color or line color (default)
            Collect polylines for each pen and process accordingly
            Polyliner should only deal with geometry (to be run on each color)
            Separate polyliner line generation from screen drawing and plotting
            Separate polyines by color and assign pens
            Final render should include all colors
            Output all moves for each pen in order (light to dark recommended)

        Models
            Include OpenSCAD pen holder in github
            Penholder in customizer
            Upload pen holders to thingiverse
            Output should parse geometries and output with pen changes
     
'''
import sys
from xml.dom import minidom
from simple import simple
from polyliner import polyliner
#from numpy.distutils.fcompiler import none

def help():
    print("IBMxy749.py converts svg paths into plotter commands")
    print("")
    print("Usage to send directly to the plotter:")
    print("    Linux:")
    print("        python ibm_xy_749.py [-h] [-pn=#RRGGBB] input.svg >/dev/ttyS0")
    print("    Windows:")
    print("        python ibm_xy_749.py [-h] [-pn=#RRGGBB] input.svg >com10:")
    print("")
    print("Usage to send to a file:")
    print("    Linux/Windows:")
    print("        python ibm_xy_749.py input.svg >output.txt")
    print("To send the file to the plotter:")
    print("    Linux:")
    print("        cp output.txt /dev/ttyS0")
    print("    Windows:")
    print("        copy output.txt com10:")
    print("")
    print("These examples assume plotter is connected to /dev/sttyS0 in Linux")
    print("or com10: in Windows, replace with actual device in your system.")


# default is one black pen
pens={0:(0,0,0)}

# parse parameters
progname=None

# svg file specification
svgfilespec=None

# use fill color (line color default)
usefillcolor=False

for arg in sys.argv:
    argl=arg.lower()
    # -h 
    if argl[0:1]=='-h':
        help()
        exit(0)
    # -f enable fill color usage
    if argl[0:1]=='-f':
        usefillcolor=True
    # -p0=#RRGGBB
    if argl[0:2]=='-p' and arg[3:5]=='=#':
        if len(arg)!=11:
            print('ERROR: Pen format incorrect ("-pn=#RRGGBB"):',arg)
            exit(1)
        pen=int(argl[2:3])
        red=int(arg[5:7],16)
        green=int(arg[7:9],16)
        blue=int(arg[9:11],16)
        pens[pen]=(red,green,blue)
        if pen>7: 
            print("ERROR: Pen out of range (0-7):",pen)
            exit(1)
    else:
        if progname==None:
            progname=arg
        elif svgfilespec==None:
            svgfilespec=arg
        else:
            # too many arguments
            print("ERROR: Unknown parameter:",arg)
            help()
            exit(1)
    
if svgfilespec==None:
    help()
    print("ERROR: No input file.",arg)
    exit(1)        

#svgfilespec="svg\\Plotter face.svg"
#svgfilespec="svg\\Plotter Brain 1536087723.svg"
#svgfilespec="svg\\Plotter 3d-stanford-bunny-wireframe-polyprismatic.svg"
#svgfilespec="svg\\Plotter R2D2.svg"

# read the SVG file
doc = minidom.parse(svgfilespec)

'''
# beginning to parse color information from svg
for path in doc.getElementsByTagName('path'):
    id=path.getAttribute('id')
    d=path.getAttribute('d')
    style=path.getAttribute('style')
    styled=dict(item.split(":") for item in style.split(";"))
    print(id,style,styled['fill'],styled['stroke'])
exit(0)
'''  

path_strings = [path.getAttribute('d') for path
                in doc.getElementsByTagName('path')]
doc.unlink()



if 0:
    simple(path_strings)
else:
    polylines = polyliner(path_strings,segments=7,quantization=1,weldradius=0)

from PIL import Image,ImageDraw,ImageFont
from plotter import Plotter
from color import Color


# stub in variables to be handled later
quantization=1
welded=0
welds=0
weldradius=0

# Build histogram of polyline lengths
histogram={}
for polyline in polylines:
    l=len(polyline)
    histogram[l]=histogram.get(l,0)+1

# Draw image statistics and reference information  
im= Image.new(mode="RGB", size=(11*250,int(8.5*250)),color=(255,255,255))
imd=ImageDraw.Draw(im)

# specified font size
#font = ImageFont.truetype(r'C:\Users\System-Pc\Desktop\arial.ttf', 20)
font=ImageFont.load_default(); 

polylineaverage=0
polylinecount=0
polylinelongest=0;
for length,count in histogram.items():
    imd.line([(length,0),(length,count)],fill=(0,64,0))
    if length>polylinelongest:
        polylinelongest=length
    polylinecount+=length
    polylineaverage+=length*count
polylineaverage/=polylinecount

# drawing text size
imd.text(  (5, 500), 
            text='welds:%d\nwelded:%d\npolylines:%d\nlongest polyline:%d\npolyline average:%.2f'%
                (welds,welded,polylinecount,polylinelongest, polylineaverage), 
            font = font,
            fill ="black",  
            align ="left")

# 1 inch square
imd.rectangle((100,700,100+250,700+250), fill = None, outline =(128,128,128))
# quantization square
imd.rectangle((100,700,100+quantization-1,700+quantization-1), fill = None, outline ='orange')
# weld radius circle
imd.ellipse((100,700,100+weldradius*2,700+weldradius*2), fill = None, outline ='blue')

# draw the polylines to the plotter and to the image 
# open plotter       
plotter=Plotter()
#plotter.pen(1)
c=Color(0,0,0)
delta=8    
print(plotter.slow(), end ="")
for polyline in polylines:
    print(plotter.move(polyline[0][0],polyline[0][1]), end ="")
    print(plotter.pendown(), end ="")
    color=c.rnd()
    for i in range(1,len(polyline)):
        print(plotter.move(polyline[i][0],polyline[i][1]), end ="")
        imd.line([(polyline[i-1][0],polyline[i-1][1]),(polyline[i][0],polyline[i][1])],fill=color,width=3)
    print(plotter.penup(), end ="")
    c.inc(delta)
print(plotter.penup(), end ="")
print(plotter.move(plotter.maxx,plotter.maxy))

# hack: have to print 1024 characters to flush the buffer
for i in range(16):
    print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
print()
    
im.show()


# release plotter
plotter=None


