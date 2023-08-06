import numpy as np
from OpenGL.GL  import *
import math
from shapely.geometry import Point

from .PyParams import Wolf_Param
from .PyTranslate import _

def getRGBfromI(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return red, green, blue

def getIfromRGB(rgb):
    red = int(rgb[0])
    green = int(rgb[1])
    blue = int(rgb[2])
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

def circle(x:float,y:float,r:float,numseg:int=20):
    glBegin(GL_POLYGON)
    for ii in range(numseg+1):
        theta = 2.0 * 3.1415926 * float(ii) / float(numseg)
        x1 = r * math.cos(theta)
        y1 = r * math.sin(theta)
        glVertex2f(x+x1, y+y1)
    glEnd()

def cross(x:float,y:float,r:float):
    glBegin(GL_LINES)
    glVertex2f(x-r, y)
    glVertex2f(x+r, y)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(x, y-r)
    glVertex2f(x, y+r)
    glEnd()

def quad(x:float,y:float,r:float):
    glBegin(GL_QUADS)
    glVertex2f(x-r, y-r)
    glVertex2f(x+r, y-r)
    glVertex2f(x+r, y+r)
    glVertex2f(x-r, y+r)
    glEnd()

class wolfvertex:
    '''Vertex WOLF - 3 coordonnées + valeurs associées dans un dictionnaire'''    
    
    x:float
    y:float
    z:float
    values:dict=None

    def __init__(self,x,y,z=0.) -> None:
        self.x=x
        self.y=y
        self.z=z
        self.in_use=True
        pass

    def as_shapelypoint(self):
        return Point(self.getcoords())

    def copy(self):
        return wolfvertex(self.x,self.y,self.z)

    def getcoords(self):
        coords=np.array([self.x,self.y,self.z])
        return coords

    def dist3D(self,v):
        v=self.getcoords()-v.getcoords()
        return np.sqrt(np.inner(v,v))
    
    def dist2D(self,v):
        v=self.getcoords()[0:2]-v.getcoords()[0:2]
        return np.sqrt(np.inner(v,v))

    def addvalue(self,id,value):
        if self.values is None:
            self.values={}
        self.values[id]=value

    def getvalue(self,id):
        if not self.values is None:
            if id in self.values.keys():
                return self.values[id]
            else:
                return None

class cloudproperties:
    
    used:bool
    
    color:int
    width:int
    style:int
    alpha:int
    filled:bool
    legendvisible:bool
    transparent:bool
    flash:bool

    legendtext:str
    legendrelpos:int
    legendx:float
    legendy:float

    legendbold:bool
    legenditalic:bool
    legendunderlined:bool
    legendfontname=str
    legendfontsize:int
    legendcolor:int

    extrude:bool = False

    myprops:Wolf_Param = None

    def __init__(self,lines=[],parent=None) -> None:
        
        self.parent=parent
        
        if len(lines)>0:
            pass
            # line1=lines[0].split(',')
            # line2=lines[1].split(',')

            # self.color=int(line1[0])
            # self.width=int(line1[1])
            # self.style=int(line1[2])
            # self.filled=line1[4]=='#TRUE#'
            # self.legendvisible=line1[5]=='#TRUE#'
            # self.transparent=line1[6]=='#TRUE#'
            # self.alpha=int(line1[7])
            # self.flash=line1[8]=='#TRUE#'

            # self.legendtext=line2[0]
            # self.legendrelpos=int(line2[1])
            # self.legendx=float(line2[2])
            # self.legendy=float(line2[3])
            # self.legendbold=line2[4]=='#TRUE#'
            # self.legenditalic=line2[5]=='#TRUE#'
            # self.legendfontname=str(line2[6])
            # self.legendfontsize=int(line2[7])
            # self.legendcolor=int(line2[8])
            # self.legendunderlined=line2[9]=='#TRUE#'

            # self.used=lines[2]=='#TRUE#'
        else:
            self.color=0
            self.width=10
            self.style=0
            self.filled=False
            self.legendvisible=False
            self.transparent=False
            self.alpha=0
            self.flash=False

            self.legendtext=''
            self.legendrelpos=5
            self.legendx=0.
            self.legendy=0.
            self.legendbold=False
            self.legenditalic=False
            self.legendfontname='Arial'
            self.legendfontsize=10
            self.legendcolor=0
            self.legendunderlined=False

            self.used=True
        pass
    
    def fill_property(self):
        
        curdict=self.myprops.myparams_default
        if 'Draw' in curdict.keys():
            keysactive = curdict['Draw'].keys()
            if 'Color' in keysactive:
                self.color = getIfromRGB(curdict['Draw']['Color']['value'])
            if 'Width' in keysactive:
                self.width = float(curdict['Draw']['Width']['value'])
            if 'Style' in keysactive:
                self.style = int(curdict['Draw']['Style']['value'])
            if 'Filled' in keysactive:
                self.filled = bool(curdict['Draw']['Filled']['value'])
            if 'Transparent' in keysactive:
                self.transparent = bool(curdict['Draw']['Transparent']['value'])
            if 'Alpha' in keysactive:
                self.alpha = int(curdict['Draw']['Alpha']['value'])
            if 'Flash' in keysactive:
                self.flash = bool(curdict['Draw']['Flash']['value'])

        if 'Legend' in curdict.keys():
            keysactive = curdict['Legend'].keys()
            if 'Underlined' in keysactive:
                self.legendunderlined = bool(curdict['Legend']['Underlined']['value'])
            if 'Bold' in keysactive:
                self.legendbold = bool(curdict['Legend']['Bold']['value'])
            if 'Font name' in keysactive:
                self.legendfontname = str(curdict['Legend']['Font name']['value'])
            if 'Font size' in keysactive:
                self.legendfontsize = int(curdict['Legend']['Font size']['value'])
            if 'Color' in keysactive:
                self.legendcolor = getIfromRGB(curdict['Legend']['Color']['value'])
            if 'Italic' in keysactive:
                self.legenditalic = bool(curdict['Legend']['Italic']['value'])
            if 'relative Position' in keysactive:
                self.legendrelpos = int(curdict['Legend']['relative Position']['value'])
            if 'Text' in keysactive:
                self.legendtext = str(curdict['Legend']['Text']['value'])
            if 'Visible' in keysactive:
                self.legendvisible = bool(curdict['Legend']['Visible']['value'])
            if 'X' in keysactive:
                self.legendx = float(curdict['Legend']['X']['value'])
            if 'Y' in keysactive:
                self.legendy = float(curdict['Legend']['Y']['value'])
        
        curdict=self.myprops.myparams
        if 'Draw' in curdict.keys():
            keysactive = curdict['Draw'].keys()
            if 'Color' in keysactive:
                self.color = getIfromRGB(curdict['Draw']['Color']['value'].replace('(','').replace(')','').split(', '))
            if 'Width' in keysactive:
                self.width = float(curdict['Draw']['Width']['value'])
            if 'Style' in keysactive:
                self.style = int(curdict['Draw']['Style']['value'])
            if 'Filled' in keysactive:
                self.filled = bool(curdict['Draw']['Filled']['value'])
            if 'Transparent' in keysactive:
                self.transparent = bool(curdict['Draw']['Transparent']['value'])
            if 'Alpha' in keysactive:
                self.alpha = int(curdict['Draw']['Alpha']['value'])
            if 'Flash' in keysactive:
                self.flash = bool(curdict['Draw']['Flash']['value'])

        if 'Legend' in curdict.keys():
            keysactive = curdict['Legend'].keys()
            if 'Underlined' in keysactive:
                self.legendunderlined = bool(curdict['Legend']['Underlined']['value'])
            if 'Bold' in keysactive:
                self.legendbold = bool(curdict['Legend']['Bold']['value'])
            if 'Font name' in keysactive:
                self.legendfontname = str(curdict['Legend']['Font name']['value'])
            if 'Font size' in keysactive:
                self.legendfontsize = int(curdict['Legend']['Font size']['value'])
            if 'Color' in keysactive:
                self.legendcolor = getIfromRGB(curdict['Legend']['Color']['value'].replace('(','').replace(')','').split(', '))
            if 'Italic' in keysactive:
                self.legenditalic = bool(curdict['Legend']['Italic']['value'])
            if 'relative Position' in keysactive:
                self.legendrelpos = int(curdict['Legend']['relative Position']['value'])
            if 'Text' in keysactive:
                self.legendtext = str(curdict['Legend']['Text']['value'])
            if 'Visible' in keysactive:
                self.legendvisible = bool(curdict['Legend']['Visible']['value'])
            if 'X' in keysactive:
                self.legendx = float(curdict['Legend']['X']['value'])
            if 'Y' in keysactive:
                self.legendy = float(curdict['Legend']['Y']['value'])

        self.parent.forceupdategl=True
        
    def defaultprop(self):
        if self.myprops is None:
            self.myprops=Wolf_Param(title='Cloud Properties',to_read=False)
            self.myprops.callbackdestroy = self.destroyprop
            self.myprops.callback=self.fill_property
            self.myprops.saveme.Disable()
            self.myprops.loadme.Disable()
            self.myprops.reloadme.Disable()

        self.myprops.addparam('Draw','Color',getRGBfromI(0),'Color','Drawing color',whichdict='Default')
        self.myprops.addparam('Draw','Width',10,'Float','Drawing width',whichdict='Default')
        self.myprops.addparam('Draw','Style',0,'Integer','Drawing style',whichdict='Default')
        self.myprops.addparam('Draw','Filled',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Draw','Transparent',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Draw','Alpha',0,'Integer','Transparent intensity',whichdict='Default')
        self.myprops.addparam('Draw','Flash',False,'Logical','',whichdict='Default')

        self.myprops.addparam('Legend','Visible',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Legend','Text','','String','',whichdict='Default')
        self.myprops.addparam('Legend','relative Position',5,'Integer','',whichdict='Default')
        self.myprops.addparam('Legend','X',0,'Float','',whichdict='Default')
        self.myprops.addparam('Legend','Y',0,'Float','',whichdict='Default')
        self.myprops.addparam('Legend','Bold',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Legend','Italic',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Legend','Font name','Arial','String','',whichdict='Default')
        self.myprops.addparam('Legend','Font size',10,'Integer','',whichdict='Default')
        self.myprops.addparam('Legend','Color',getRGBfromI(0),'Color','',whichdict='Default')
        self.myprops.addparam('Legend','Underlined',False,'Logical','',whichdict='Default')

    def destroyprop(self):
        self.myprops=None

    def show(self):
        self.defaultprop()

        self.myprops.addparam('Draw','Color',getRGBfromI(self.color),'Color','Drawing color')
        self.myprops.addparam('Draw','Width',self.width,'Float','Drawing width')
        self.myprops.addparam('Draw','Style',self.style,'Integer','Drawing style')
        self.myprops.addparam('Draw','Filled',self.filled,'Logical','')
        self.myprops.addparam('Draw','Transparent',self.transparent,'Logical','')
        self.myprops.addparam('Draw','Alpha',self.alpha,'Integer','Transparent intensity')
        self.myprops.addparam('Draw','Flash',self.flash,'Logical','')

        self.myprops.addparam('Legend','Visible',self.legendvisible,'Logical','')
        self.myprops.addparam('Legend','Text',self.legendtext,'String','')
        self.myprops.addparam('Legend','relative Position',self.legendrelpos,'Integer','')
        self.myprops.addparam('Legend','X',self.legendx,'Float','')
        self.myprops.addparam('Legend','Y',self.legendy,'Float','')
        self.myprops.addparam('Legend','Bold',self.legendbold,'Logical','')
        self.myprops.addparam('Legend','Italic',self.legenditalic,'Logical','')
        self.myprops.addparam('Legend','Font name',self.legendfontname,'String','')
        self.myprops.addparam('Legend','Font size',self.legendfontsize,'Integer','')
        self.myprops.addparam('Legend','Color',getRGBfromI(self.legendcolor),'Color','')
        self.myprops.addparam('Legend','Underlined',self.legendunderlined,'Logical','')

        self.myprops.Populate()
        self.myprops.Show()

class cloud_vertices:
    idx:str
    filename:str
    myvertices:dict

    xbounds:tuple
    ybounds:tuple
    zbounds:tuple

    myprop:cloudproperties

    def __init__(self,fname:str='',fromxls:str='',header:bool=False,toload=True) -> None:
        self.myvertices={}
        self.filename=fname
        
        self.plotted=False
        self.loaded=False
        
        self.header=header
        
        self.gllist=0
        self.forceupdategl=False
        self.ongoing=False

        self.xbounds=(0.,0.)
        self.ybounds=(0.,0.)
        self.zbounds=(0.,0.)

        self.myprop=cloudproperties(parent=self)

        if fname!='':
            if toload:
                self.readfile(fname,header)
                
    def init_from_nparray(self,array):
        k=0
        for curv in array:
            mv =wolfvertex(curv[0],curv[1],curv[2])
            self.myvertices[k]={}
            self.myvertices[k]['vertex']=mv
            k+=1
                    
        self.xbounds=(np.min(array[:,0]),np.max(array[:,0]))
        self.ybounds=(np.min(array[:,1]),np.max(array[:,1]))
        self.loaded=True

    def check_plot(self):
        self.plotted = True
        if not self.loaded:
            self.readfile(self.filename,self.header)
            self.loaded=True

    def uncheck_plot(self,unload=True):
        self.plotted = False

    def readfile(self,fname='',header:bool=False):
        if fname!='':
            headers=None
            nbcols=0
            zpresent=False
            nbvals=0
            firstval=0

            xmin=1.e300
            xmax=-1.e300
            ymin=1.e300
            ymax=-1.e300
            zmin=1.e300
            zmax=-1.e300

            f=open(fname,'r')
            content=f.read().splitlines()
            f.close()

            if header:
                curhead=content[0]
                content.pop(0)
                sep=' '
                if curhead.index('\t')>0:
                    #séparateur tabulation
                    sep='\t'
                elif curhead.index(';')>0:
                    #séparateur tabulation
                    sep=';'
                headers=curhead.split(sep)
                nbcols=len(headers)
            else:
                curline=content[0]
                sep=' '
                if curline.index('\t')>0:
                    #séparateur tabulation
                    sep='\t'
                elif curline.index(';')>0:
                    #séparateur tabulation
                    sep=';'
                curval=curline.split(sep)
                nbcols=len(curval)

            if nbcols<2:
                print('Not enough values on one line -- Retry !!')
                return
            elif nbcols>3 :
                if headers is None:
                    print('No headers -- Retry !!')
                    return
                else:
                    if headers[2].lower()=='z':
                        zpresent=True
                        nbvals=nbcols-3
                        firstval=3
                    else:
                        #on interprète la 3ème colonne comme valeur et non comme Z
                        zpresent=False
                        nbvals=nbcols-2
                        firstval=2
            elif nbcols==3:
                if headers is None:
                    zpresent=True
                else:
                    if headers[2].lower()=='z':
                        zpresent=True
                    else:
                        #on interprète la 3ème colonne comme valeur et non comme Z
                        zpresent=False
                        nbvals=1
                        firstval=2
            k=0
            for curline in content:
                curval=curline.split(sep)

                x=float(curval[0])
                y=float(curval[1])
                z=0
                if zpresent:
                    z=float(curval[2])

                curvert=wolfvertex(x,y,z) 
                curdict=self.myvertices[k]={}
                curdict['vertex']=curvert

                xmin=min(x,xmin)
                xmax=max(x,xmax)
                ymin=min(y,ymin)
                ymax=max(y,ymax)
                zmin=min(z,zmin)
                zmax=max(z,zmax)
                
                if nbvals>0:
                    for i in range[firstval,firstval+nbvals]:
                        curdict[headers[i]]=curval[i]

                k+=1

            self.xbounds=(xmin,xmax)
            self.ybounds=(ymin,ymax)
            
            self.loaded=True

    def add_vertex(self,vertextoadd:wolfvertex=None,id=None,cloud:dict=None):
        if not vertextoadd is None:
            curid=id
            if curid is None:
                curid=len(self.myvertices)
            self.myvertices[curid]={}
            self.myvertices[curid]['vertex']=vertextoadd
            self.updatebounds(vertextoadd)

        if not cloud is None:
            for id,item in enumerate(cloud):
                self.myvertices[id]=item
            
            self.updatebounds(newcloud=cloud)
        pass

    def plot(self,update=False):
        
        if update or self.gllist==0 or self.forceupdategl and not self.ongoing:
            curvert:wolfvertex
            self.ongoing=True
            
            color=self.myprop.color
            width=self.myprop.width
            style=self.myprop.style  
            filled=self.myprop.filled
            
            if self.gllist!=0:
                glDeleteLists(self.gllist,1)
            
            self.gllist = glGenLists(1)
            glNewList(self.gllist,GL_COMPILE)

            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            if filled:
                glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)      

            if style==0:
                glPointSize(width)
                rgb=getRGBfromI(color)
                glBegin(GL_POINTS)
                for id,item in enumerate(self.myvertices):
                    curvert=self.myvertices[item]['vertex']
                    glColor3ub(int(rgb[0]),int(rgb[1]),int(rgb[2]))
                    glVertex2f(curvert.x, curvert.y)

                glEnd()
            elif style==1:
                glPointSize(1)
                rgb=getRGBfromI(color)
                for id,item in enumerate(self.myvertices):
                    curvert=self.myvertices[item]['vertex']
                    glColor3ub(int(rgb[0]),int(rgb[1]),int(rgb[2]))
                    circle(curvert.x,curvert.y,width/2.)
            elif style==2:
                glPointSize(1)
                rgb=getRGBfromI(color)
                for id,item in enumerate(self.myvertices):
                    curvert=self.myvertices[item]['vertex']
                    glColor3ub(int(rgb[0]),int(rgb[1]),int(rgb[2]))
                    cross(curvert.x,curvert.y,width/2)
            elif style==3:
                glPointSize(1)
                rgb=getRGBfromI(color)
                for id,item in enumerate(self.myvertices):
                    curvert=self.myvertices[item]['vertex']
                    glColor3ub(int(rgb[0]),int(rgb[1]),int(rgb[2]))
                    quad(curvert.x,curvert.y,width/2)
            
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)  
            
            glEndList()  
            self.forceupdategl=False 
            self.ongoing=False
        else:
            glCallList(self.gllist)
            pass 

    def updatebounds(self,newvert:wolfvertex=None,newcloud:dict=None):

        xmin=self.xbounds[0]
        xmax=self.xbounds[1]
        ymin=self.ybounds[0]
        ymax=self.ybounds[1]
        zmin=self.zbounds[0]
        zmax=self.zbounds[1]

        if not newvert is None:
            xmin=min(newvert.x,xmin)
            xmax=max(newvert.x,xmax)
            ymin=min(newvert.y,ymin)
            ymax=max(newvert.y,ymax)
            zmin=min(newvert.z,zmin)
            zmax=max(newvert.z,zmax)
                
            self.xbounds=(xmin,xmax)
            self.ybounds=(ymin,ymax)
            self.zbounds=(zmin,zmax)

        if not newcloud is None:
            for item in enumerate(newcloud):
                curvert=newcloud[item]['vertex']
                xmin=min(curvert.x,xmin)
                xmax=max(curvert.x,xmax)
                ymin=min(curvert.y,ymin)
                ymax=max(curvert.y,ymax)
                zmin=min(curvert.z,zmin)
                zmax=max(curvert.z,zmax)
                
            self.xbounds=(xmin,xmax)
            self.ybounds=(ymin,ymax)
            self.zbounds=(zmin,zmax)

    def find_minmax(self,force=False):
        if force:
            xmin=1.e300
            xmax=-1.e300
            ymin=1.e300
            ymax=-1.e300
            zmin=1.e300
            zmax=-1.e300

            for item in self.myvertices:
                curvert=self.myvertices[item]['vertex']

                x=curvert.x
                y=curvert.y
                z=curvert.z

                xmin=min(x,xmin)
                xmax=max(x,xmax)
                ymin=min(y,ymin)
                ymax=max(y,ymax)
                zmin=min(z,zmin)
                zmax=max(z,zmax)
                
            self.xbounds=(xmin,xmax)
            self.ybounds=(ymin,ymax)
            self.zbounds=(zmin,zmax)

            pass

