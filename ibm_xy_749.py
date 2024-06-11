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
        

    LePen colors
        Pink        ff7299
        Purple      995db4
        Cyan        1e9fbb
        Light Green 43b766
        Yellow      bcdc72
        Orange      fba551
        Red         be302e
        Green       00544d
        Blue        190ebf
        Black       3a362c
        
                                        pink             purple      cyan       orange       red         green       blue        light green
        "svg\\plotter cap-fill.svg" -f  -p0=#ff7299 -p1=#995db4 -p2=#1e9fbb -p3=#fba551 -p4=#be302e -p5=#00544d -p6=#190ebf -p7=#43b766
        
                                        pink             purple      cyan       orange       red         green       blue        black
        "svg\\plotter cap-fill.svg" -f  -p0=#ff7299 -p1=#995db4 -p2=#1e9fbb -p3=#fba551 -p4=#be302e -p5=#00544d -p6=#190ebf -p7=#3a362c
        
        "svg\\plotter cap-fill.svg" -f  -p0=#000000 -p1=#202020 -p2=#0000c0 -p3=#c00000 -p4=#00c000 -p5=#800080 -p6=#008080 -p7=#808000
    ToDo:
        Colors
            [] Lab Cie matching of color to pen color

            [x] Remove newline stuff from plotter
            [x] Separate drawing from plotter output
            [x] Parse path styles and extract stroke:#rrggbb or fill="#DDB893" or fill attribute in path
            [x] Pass pen colors in on command line: pen colors (optional, default 000000) -p0=#000000
            [x] what order are pens output?  command line order?  (need test svg)
            [x] Command line to select fill color or line color (default)
            [x] Collect polylines for each pen and process accordingly
            [x] Polyliner should only deal with geometry (to be run on each color)
            [x] Separate polyliner line generation from screen drawing and plotting
            [x] Separate polyines by color and assign pens
            [x] Final render should include all pen colors
            [x] Output all moves for each pen in order (light to dark recommended)

        Models
            Include OpenSCAD pen holder in github
            Penholder in customizer
            Upload pen holders to thingiverse
            Output should parse geometries and output with pen changes
     
'''
import sys
from xml.dom import minidom
from polyliner import polyliner
from PIL import Image,ImageDraw,ImageFont
from plotter import Plotter
from color import Color, colorFromString

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
pens={0:(Color(0,0,0),[],[])}

# parse parameters
progname=None

# svg file specification
svgfilespec=None

# use fill color (line color default)
usefillcolor=False

for arg in sys.argv:
    argl=arg.lower()
    # -h 
    if argl[0:2]=='-h':
        help()
        exit(0)
    # -f enable fill color usage
    elif argl[0:2]=='-f':
        usefillcolor=True
    # -p0=#RRGGBB
    elif argl[0:2]=='-p' and arg[3:5]=='=#':
        if len(arg)!=11:
            print('ERROR: Pen format incorrect ("-pn=#RRGGBB"):',arg)
            exit(1)
        pen=int(argl[2:3])
        red=int(arg[5:7],16)
        green=int(arg[7:9],16)
        blue=int(arg[9:11],16)
        pens[pen]=(Color(red,green,blue),[],[])
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
#svgfilespec="svg\\Plotter 3d-stanford-bunny-wireframe-polyprismatic color stroke.svg"
#svgfilespec="svg\\Plotter R2D2.svg"
#svgfilespec="svg\\plotter cap-fill.svg"

# read the SVG file
doc = minidom.parse(svgfilespec)

# parse color information from svg
for path in doc.getElementsByTagName('path'):
    #id=path.getAttribute('id')
    # path data
    d=path.getAttribute('d')
    style=path.getAttribute('style')
    styled=dict(item.split(":") for item in style.split(";"))
    
    # get fill color if it exists
    fillcolorstr=path.getAttribute('fill')
    if len(fillcolorstr)==0:
        # failed to get the fill color from the shape, try the style
        fillcolorstr=styled.get('fill')
    # parse the fill color string
    if fillcolorstr==None or len(fillcolorstr)!=7:
        # if no fill color can be found, set to black
        fillcolorstr='#000000'
    fillcolor=colorFromString(fillcolorstr)
    
    # get stroke color if it exists
    # path style needed for color
    stylecolorstr=styled['stroke']
    # if no stroke color specified fall back to fill color 
    if stylecolorstr=='none':
        stylecolorstr='#000000'
    strokecolor=colorFromString(stylecolorstr)
    
    # select color needed, only fallback to black
    if usefillcolor:
        pathcolor=fillcolor
    else:
        pathcolor=strokecolor
       
    # Select the best matching pen
    colormaxdiff=9999*255*3
    penmatch=0
    for pen in pens.keys():
        pencol=pens[pen][0]
        colordiff=pathcolor.difference(pencol)
        if colordiff<colormaxdiff:
            colormaxdiff=colordiff
            penmatch=pen 
    
    # add the path data to the list for the pen.
    pens[penmatch][1].append(d)

# release svg document
doc.unlink()


###############################################################################
# stub in variables to be handled later
quantization=1
weldradius=0

# Fuse lines into polylines
for pen in pens.keys():
    pens[pen][2].extend(polyliner(pens[pen][1],segments=7,quantization=quantization,weldradius=weldradius))


###############################################################################
# Output

# stub in variables to be handled later
welded=0
welds=0

# Build histogram of polyline lengths
histogram={}
for pen in pens.keys():
    polylines=pens[pen][2]
    for polyline in polylines:
        l=len(polyline)
        histogram[l]=histogram.get(l,0)+1

###############################################################################
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

if polylinecount>0:
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

for pen in pens.keys():
    polylines=pens[pen][2]
    pencolor=pens[pen][0]
    for polyline in polylines:
        color=pencolor.tuple()
        for i in range(1,len(polyline)):
            imd.line([(polyline[i-1][0],polyline[i-1][1]),(polyline[i][0],polyline[i][1])],fill=color,width=3)
im.show()

###############################################################################
# Plotter output

# helper class to output a fixed number of commands per line
class NewLine():
    commandsperline=10
    count=0
    def newline(self):
        self.count+=1
        if self.count>self.commandsperline:
            self.count=0
            return "\n"
        return ""

nl=NewLine()

# open plotter       
plotter=Plotter()
# loop through pens
for pen in pens.keys():
    # select pen
    print(plotter.penup(), end=nl.newline())
    print(plotter.pen(pen), end=nl.newline())
    # loop through polylines
    polylines=pens[pen][2]
    print(plotter.slow(), end=nl.newline())
    for polyline in polylines:
        print(plotter.move(polyline[0][0],polyline[0][1]), end=nl.newline())
        print(plotter.pendown(), end=nl.newline())
        for i in range(1,len(polyline)):
            print(plotter.move(polyline[i][0],polyline[i][1]), end=nl.newline())
        print(plotter.penup(), end=nl.newline())
# when done lift pen and move out of the way    
print(plotter.penup(), end=nl.newline())
print(plotter.move(plotter.maxx,plotter.maxy))

# hack: have to print 1024 characters to flush the buffer
for i in range(16):
    print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
print()

# release plotter
plotter=None


