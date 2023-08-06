from os import path
from tkinter.messagebox import YES
import matplotlib.path as mpltPath
import numpy as np
from wx.dataview import *
from wx.core import BoxSizer, FlexGridSizer, TreeItemId
import wx
from OpenGL.GL  import *
from shapely.geometry import LineString, MultiLineString,Point,MultiPoint,Polygon
from shapely.ops import nearest_points

from .PyTranslate import _
from .CpGrid import CpGrid
from .PyVertex import wolfvertex,getIfromRGB,getRGBfromI
from .PyParams import Wolf_Param
from .laz_viewer import myviewer

class vectorproperties:
    
    used:bool
    
    color:int
    width:int
    style:int
    alpha:int
    closed=bool
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

    def __init__(self,lines=[]) -> None:
        
        if len(lines)>0:
            line1=lines[0].split(',')
            line2=lines[1].split(',')

            self.color=int(line1[0])
            self.width=int(line1[1])
            self.style=int(line1[2])
            self.closed=line1[3]=='#TRUE#'
            self.filled=line1[4]=='#TRUE#'
            self.legendvisible=line1[5]=='#TRUE#'
            self.transparent=line1[6]=='#TRUE#'
            self.alpha=int(line1[7])
            self.flash=line1[8]=='#TRUE#'

            self.legendtext=line2[0]
            self.legendrelpos=int(line2[1])
            self.legendx=float(line2[2])
            self.legendy=float(line2[3])
            self.legendbold=line2[4]=='#TRUE#'
            self.legenditalic=line2[5]=='#TRUE#'
            self.legendfontname=str(line2[6])
            self.legendfontsize=int(line2[7])
            self.legendcolor=int(line2[8])
            self.legendunderlined=line2[9]=='#TRUE#'

            self.used=lines[2]=='#TRUE#'
        else:
            self.color=0
            self.width=1
            self.style=1
            self.closed=False
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

    def save(self,f):
        line1 = str(self.color) + ',' + str(self.width)+','+ str(self.style)

        added = ',#TRUE#' if self.closed else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.filled else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.legendvisible else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.transparent else ',#FALSE#'
        line1+=added
        line1+=','+str(self.alpha)
        added = ',#TRUE#' if self.flash else ',#FALSE#'
        line1+=added
        
        f.write(line1+'\n')

        line1 = self.legendtext + ',' + str(self.legendrelpos)+','+ str(self.legendx)+','+ str(self.legendy)
        added = ',#TRUE#' if self.legendbold else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.legenditalic else ',#FALSE#'
        line1+=added
        line1+= ','+self.legendfontname + ',' + str(self.legendfontsize)+ ',' + str(self.legendcolor)
        added = ',#TRUE#' if self.legendunderlined else ',#FALSE#'
        line1+=added
                
        f.write(line1+'\n')
        
        added = '#TRUE#' if self.used else '#FALSE#'
        f.write(added+'\n')
            
    def fill_property(self):
        
        curdict=self.myprops.myparams
        if 'Draw' in curdict.keys():
            keysactive = curdict['Draw'].keys()
            if 'Color' in keysactive:
                self.color = getIfromRGB(curdict['Draw']['Color']['value'].replace('(','').replace(')','').split(', '))
            if 'Width' in keysactive:
                self.width = int(curdict['Draw']['Width']['value'])
            if 'Style' in keysactive:
                self.style = int(curdict['Draw']['Style']['value'])
            if 'Closed' in keysactive:
                self.closed = bool(curdict['Draw']['Closed']['value'])
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

    def defaultprop(self):
        if self.myprops is None:
            self.myprops=Wolf_Param(title='Vector Properties',to_read=False)
            self.myprops.callbackdestroy = self.destroyprop
            self.myprops.callback=self.fill_property
            self.myprops.saveme.Disable()
            self.myprops.loadme.Disable()
            self.myprops.reloadme.Disable()

        self.myprops.addparam('Draw','Color',(0,0,0),'Color','Drawing color',whichdict='Default')
        self.myprops.addparam('Draw','Width',1,'Integer','Drawing width',whichdict='Default')
        self.myprops.addparam('Draw','Style',1,'Integer','Drawing style',whichdict='Default')
        self.myprops.addparam('Draw','Closed',False,'Logical','',whichdict='Default')
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
        self.myprops.addparam('Legend','Color',(0,0,0),'Color','',whichdict='Default')
        self.myprops.addparam('Legend','Underlined',False,'Logical','',whichdict='Default')

    def destroyprop(self):
        self.myprops=None

    def show(self):
        self.defaultprop()

        self.myprops.addparam('Draw','Color',getRGBfromI(self.color),'Color','Drawing color')
        self.myprops.addparam('Draw','Width',self.width,'Integer','Drawing width')
        self.myprops.addparam('Draw','Style',self.style,'Integer','Drawing style')
        self.myprops.addparam('Draw','Closed',self.closed,'Logical','')
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

class vector:

    myname:str
    nbvertices:int
    myvertices:list
    myprop:vectorproperties
    minx:float
    miny:float
    maxx:float
    maxy:float

    mytree:TreeListCtrl
    myitem:TreeItemId

    def __init__(self,lines:list=[],is2D=True,name='',parentzone=None) -> None:
            
        self.is2D = is2D
        self.closed=False
        self.parentzone=parentzone
        self.minx=-99999.
        self.miny=-99999.
        self.maxx=-99999.
        self.maxy=-99999.
        
        self.length2D=None
        self.length3D=None
        self._lengthparts2D=None
        self._lengthparts3D=None
                
        if type(lines)==list:
            if len(lines)>0:
                self.myname=lines[0]
                self.nbvertices=int(lines[1])
                self.myvertices=[]

                if is2D:
                    for i in range(self.nbvertices):
                        try:
                            curx,cury=lines[2+i].split()
                        except:
                            curx,cury=lines[2+i].split(',')
                        curvert = wolfvertex(float(curx),float(cury))
                        self.myvertices.append(curvert)
                else:
                    for i in range(self.nbvertices):
                        try:
                            curx,cury,curz=lines[2+i].split()
                        except:
                            curx,cury,curz=lines[2+i].split(',')
                        curvert = wolfvertex(float(curx),float(cury),float(curz))
                        self.myvertices.append(curvert)

                self.myprop=vectorproperties(lines[self.nbvertices+2:])

        if name!='':
            self.myname=name
            self.nbvertices=0
            self.myvertices=[]
            self.myprop=vectorproperties()
        
        self.linestring = None
        
        #•Utile surtout pour les sections en travers
        self.zdatum = 0.
        self.add_zdatum=False
        self.sdatum = 0.
        self.add_sdatum=False

    def save(self,f):
        f.write(self.myname+'\n')
        f.write(str(self.nbvertices)+'\n')

        force3D=False
        if self.parentzone is not None:
            force3D = self.parentzone.parent.force3D

        if self.is2D and not force3D:
            for curvert in self.myvertices:
                f.write(f'{curvert.x},{curvert.y}'+'\n')
        else:
            for curvert in self.myvertices:
                f.write(f'{curvert.x},{curvert.y},{curvert.z}'+'\n')
                
        self.myprop.save(f)

    def reverse(self):
        self.myvertices.reverse()
    
    def isinside(self,x,y):
        if self.nbvertices==0:
            return False
        
        poly = self.asshapely_pol()
        inside2 = poly.contains(Point([x,y]))        
        return inside2
    
    def asshapely_pol(self):
        coords=self.asnparray()
        return Polygon(coords)

    def asshapely_ls(self):
        coords=self.asnparray3d()
        return LineString(coords)

    def asshapely_mp(self):
        multi=self.asnparray3d()
        return MultiPoint(multi)

    def asnparray(self):
        return np.asarray(list([vert.x,vert.y] for vert in self.myvertices))

    def asnparray3d(self):
        xyz= np.asarray(list([vert.x,vert.y,vert.z] for vert in self.myvertices))
        
        if self.add_zdatum:
            xyz[:,2]+=self.zdatum
        return xyz

    def prepare_shapely(self):
        self.linestring = self.asshapely_ls()
        
    def intersection(self,vec2 = None,eval_dist=False,norm=False):
        ls1 = self.asshapely_ls() if self.linestring is None else self.linestring
        ls2 = vec2.asshapely_ls() if vec2.linestring is None else vec2.linestring
        
        myinter = ls1.intersection(ls2)
        
        if eval_dist:
            mydists = ls1.project(myinter,normalized=norm)
            return ls1.intersection(ls2),mydists
        else:
            return ls1.intersection(ls2)

    def reset(self):
        self.nbvertices=0
        self.myvertices=[]
        self.linestring=None
    
    def add_vertex(self,addedvert):
        if type(addedvert) is list:
            for curvert in addedvert:
                self.add_vertex(curvert)
        else:
            self.myvertices.append(addedvert)
            self.nbvertices+=1

    def count(self):
        self.nbvertices=len(self.myvertices)

    def close_force(self):
        cond = self.myvertices[-1] is not self.myvertices[0] and (self.myvertices[-1].x!=self.myvertices[0].x and self.myvertices[-1].y!=self.myvertices[0].y)
        if not self.is2D :
            cond = cond and self.myvertices[-1].z!=self.myvertices[0].z
        if cond:
            self.add_vertex(self.myvertices[0])
            self.closed=True                

    def nblines(self):
        return self.nbvertices+5

    def verify_s_ascending(self):
        
        s,z=self.get_sz(cumul=False)
        
        correction=False
        where=[]
        
        for i in range(self.nbvertices-1):
            if s[i]>s[i+1]:
                
                correction=True
                where.append(i+1)
                
                x=self.myvertices[i].x
                y=self.myvertices[i].y
                
                self.myvertices[i].x=self.myvertices[i+1].x
                self.myvertices[i].y=self.myvertices[i+1].y

                self.myvertices[i+1].x=x
                self.myvertices[i+1].y=y
                
        return correction,where

    def find_nearest_vert(self,x,y):
        
        xy=Point(x,y)
        mynp = self.asnparray()
        mp = MultiPoint(mynp)
        near = np.asarray(nearest_points(mp,xy)[0])
        return self.myvertices[np.argwhere(mynp==near[0])[0,0]]

    def insert_nearest_vert(self,x,y):
        
        xy=Point(x,y)
        mynp = self.asnparray()
        mp = MultiPoint(mynp)
        ls = LineString(mynp)
        
        nearmp = nearest_points(mp,xy) #point le plus proche sur base du nuage
        nearls = nearest_points(ls,xy) #point le plus proche sur base de la ligne
        
        smp = ls.project(nearmp[0]) #distance le long de la ligne du sommet le plus proche
        sls = ls.project(nearls[0]) #distance le long de la ligne du point le plus proche au sens géométrique (perpendiculaire au segment) 
        
        indexmp= np.argwhere(mynp==nearmp[0])[0,0] #index du vertex
        
        if indexmp==0 and self.closed:
            #le vecteur est fermé
            #il faut donc chercher à savoir si le point est après le premier point ou avant le dernier (qui possèdent les mêmes coords)
            if sls<=ls.length and sls >=ls.project(Point([self.myvertices[-2].x,self.myvertices[-2].y])):
                smp=ls.length
                indexmp=self.nbvertices-1
            else:
                indexmp=1
        else:
            if sls >= smp:
                #le point projeté sur la droite est au-delà du vertex le plus proche
                #on ajoute donc le point après
                indexmp+=1

        myvert=wolfvertex(x,y)
        self.myvertices.insert(indexmp,myvert)
        self.nbvertices+=1

        return self.myvertices[indexmp]
    
    def find_minmax(self):
        if len(self.myvertices)>0:
            self.minx=min(vert.x for vert in self.myvertices)
            self.miny=min(vert.y for vert in self.myvertices)
            self.maxx=max(vert.x for vert in self.myvertices)
            self.maxy=max(vert.y for vert in self.myvertices)

    def plot(self):

        if self.myprop.used:
            
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)        
            glLineWidth(float(self.myprop.width))
            #glPointSize(float(self.myprop.width))

            glBegin(GL_LINE_STRIP)
            #!J'aimerais bien changer la largeur du trait mais je n'y parviens pas...
            #!call glGet(GL_ALIASED_LINE_WIDTH_RANGE, max_width)
            rgb=getRGBfromI(self.myprop.color)
            
            if self.myprop.color==65536:
                a=1
            
            glColor3ub(int(rgb[0]),int(rgb[1]),int(rgb[2]))
            for curvertex in self.myvertices:
                glVertex2d(curvertex.x, curvertex.y)

            if self.myprop.closed and (self.myvertices[0].x != self.myvertices[-1].x or self.myvertices[0].y != self.myvertices[-1].y):
                curvertex = self.myvertices[0]
                glVertex2d(curvertex.x, curvertex.y)

            glEnd()

    def add2tree(self,tree:TreeListCtrl,root):
        self.mytree=tree
        self.myitem=tree.AppendItem(root, self.myname,data=self)
        if self.myprop.used:
            tree.CheckItem(self.myitem)

    def unuse(self):
        self.myprop.used=False
        self.mytree.UncheckItem(self.myitem)

    def use(self):
        self.myprop.used=True
        self.mytree.CheckItem(self.myitem)

    def fillgrid(self,gridto:CpGrid):
        curv:wolfvertex

        gridto.SetColLabelValue(0,'X')
        gridto.SetColLabelValue(1,'Y')
        gridto.SetColLabelValue(2,'Z')
        gridto.SetColLabelValue(3,'value')
        
        nb=gridto.GetNumberRows()
        if len(self.myvertices)-nb>0:
            gridto.AppendRows(len(self.myvertices)-nb)
        k=0
        for curv in self.myvertices:
           gridto.SetCellValue(k,0,str(curv.x))
           gridto.SetCellValue(k,1,str(curv.y))
           gridto.SetCellValue(k,2,str(curv.z))
           k+=1

    def updatefromgrid(self,gridfrom:CpGrid):
        curv:wolfvertex
       
        nbl=gridfrom.GetNumberRows()       
        k=0
        while k<nbl:
            x=gridfrom.GetCellValue(k,0)
            y=gridfrom.GetCellValue(k,1)
            z=gridfrom.GetCellValue(k,2)
            if z=='':
                z=0.
            if x!='':
                if k<self.nbvertices:
                    self.myvertices[k].x=float(x)
                    self.myvertices[k].y=float(y)
                    self.myvertices[k].z=float(z)
                else:
                    newvert=wolfvertex(float(x),float(y),float(z))
                    self.add_vertex(newvert)
                k+=1
            else:
                break

        while k<self.nbvertices:
            self.myvertices.pop(k)
            self.nbvertices-=1

    def get_s3d(self):
        s3d=np.zeros[self.nbvertices]
        for k in range(1,self.nbvertices+1):
            s3d[k]=s3d[k-1]+self.myvertices[k-1].dist3D(self.myvertices[k])

    def get_sz(self,cumul=True):
            
        z = np.asarray([self.myvertices[i].z for i in range(self.nbvertices)])
        
        nb = len(z)
        s = np.zeros(nb)
                
        if cumul:
            x1 = self.myvertices[0].x
            y1 = self.myvertices[0].y
            for i in range(nb-1):
                x2 = self.myvertices[i+1].x
                y2 = self.myvertices[i+1].y
                
                length = np.sqrt((x2-x1)**2.+(y2-y1)**2.)
                s[i+1] = s[i]+length
                
                x1=x2
                y1=y2
        else:
            for i in range(nb):
                s[i] = self.myvertices[0].dist2D(self.myvertices[i])
                            
        return s,z

    def update_lengths(self):      
        self._lengthparts2D=np.zeros(self.nbvertices-1)
        self._lengthparts3D=np.zeros(self.nbvertices-1)
        
        for k in range(self.nbvertices-1):
            self._lengthparts2D[k] = self.myvertices[k].dist2D(self.myvertices[k+1])
            self._lengthparts3D[k] = self.myvertices[k].dist3D(self.myvertices[k+1])
            
        if self.closed and self.myvertices[0]!=self.myvertices[-1]:
            self._lengthparts2D[-1] = self.myvertices[-2].dist2D(self.myvertices[-1])
            self._lengthparts3D[-1] = self.myvertices[-2].dist3D(self.myvertices[-1])

        self.length2D = np.sum(self._lengthparts2D)
        self.length3D = np.sum(self._lengthparts3D)
        
    def get_segment(self,s,is3D,adim=True,frombegin=True):
        if is3D:
            length = self.length3D
            lengthparts = self._lengthparts3D
        else:
            length = self.length2D
            lengthparts = self._lengthparts2D
        
        if length is None:
            self.update_lengths()
            if is3D:
                length = self.length3D
                lengthparts = self._lengthparts3D
            else:
                length = self.length2D
                lengthparts = self._lengthparts2D
            
        cums = np.cumsum(lengthparts)

        if adim:
            cums = cums.copy()/length
            lengthparts = lengthparts.copy()/length
            if s>1.:
                s=1.
            if s<0.:
                s=0.
        else:        
            if s>length:
                s=length
            if s<0.:
                s=0.
        
        if frombegin:
            k=0
            while s>cums[k]:
                k+=1
        else:
            k=self.nbvertices-2
            if k>0:
                while s<cums[k] and k>0:
                    k-=1                
                if k==0 and s<cums[0]:
                    pass
                else:
                    k+=1
                
        return k,cums[k],lengthparts
    
    def interpolate(self,s,is3D=True,adim=True,frombegin=True):
        
        k,cums,lengthparts=self.get_segment(s,is3D,adim,frombegin)
        if k==-1:
            return
                
        pond = (cums-s)/lengthparts[k]
        
        return wolfvertex(self.myvertices[k].x*pond+self.myvertices[k+1].x*(1.-pond),
                          self.myvertices[k].y*pond+self.myvertices[k+1].y*(1.-pond),
                          self.myvertices[k].z*pond+self.myvertices[k+1].z*(1.-pond))
        
    def substring(self,s1,s2,is3D=True,adim=True):

        k1,cums1,lengthparts1=self.get_segment(s1,is3D,adim,True)
        k2,cums2,lengthparts2=self.get_segment(s2,is3D,adim,False)
                
        pond1 = (cums1-s1)/lengthparts1[k1]
        pond2 = (cums2-s2)/lengthparts2[k2]
        
        v1= wolfvertex(self.myvertices[k1].x*pond1+self.myvertices[k1+1].x*(1.-pond1),
                       self.myvertices[k1].y*pond1+self.myvertices[k1+1].y*(1.-pond1),
                       self.myvertices[k1].z*pond1+self.myvertices[k1+1].z*(1.-pond1))
        
        v2= wolfvertex(self.myvertices[k2].x*pond2+self.myvertices[k2+1].x*(1.-pond2),
                       self.myvertices[k2].y*pond2+self.myvertices[k2+1].y*(1.-pond2),
                       self.myvertices[k2].z*pond2+self.myvertices[k2+1].z*(1.-pond2))
        
        newvec = vector(name='substr')
        newvec.add_vertex(v1)
        for k in range(k1+1,k2+1):
            newvec.add_vertex(self.myvertices[k])
        newvec.add_vertex(v2)
        
        return newvec

class zone:

    myname:str
    nbvectors:int
    myvectors:list
    minx:float
    miny:float
    maxx:float
    maxy:float
    selected_vectors:list
    mytree:TreeListCtrl
    myitem:TreeItemId
    active_vector:vector

    def __init__(self,lines=[],name='',parent=None,is2D=True) -> None:
        
        self.idgllist = -99999
        self.active_vector=None
        self.parent=parent

        if len(lines)>0:
            self.myname=lines[0]
            self.nbvectors=int(lines[1])
            self.myvectors=[]
            curstart=2
            for i in range(self.nbvectors):
                curvec=vector(lines[curstart:],parentzone=self,is2D=is2D)
                curstart+=curvec.nblines()
                self.myvectors.append(curvec)

        if name!='':
            self.myname=name
            self.nbvectors=0
            self.myvectors=[]
        
        self.selected_vectors=[]
        self.multils = None

        pass

    def save(self,f):
        f.write(self.myname+'\n')
        f.write(str(self.nbvectors)+'\n')
        for curvect in self.myvectors:
            curvect.save(f)

    def add_vector(self,addedvect):
        self.myvectors.append(addedvect)
        self.nbvectors+=1

    def count(self):
        self.nbvectors=len(self.myvectors)

    def nblines(self):
        nb=2
        for curvec in self.myvectors:
            nb+=curvec.nblines()
        
        return nb

    def find_minmax(self,update=False):
        if update:
            for vect in self.myvectors:
                vect.find_minmax()

        if self.nbvectors==0:
            self.minx=-99999.
            self.miny=-99999.
            self.maxx=-99999.
            self.maxy=-99999.
        else:
            minsx=np.asarray([vect.minx for vect in self.myvectors])
            minsy=np.asarray([vect.miny for vect in self.myvectors])
            maxsx=np.asarray([vect.maxx for vect in self.myvectors])
            maxsy=np.asarray([vect.maxy for vect in self.myvectors])
            
            if len(minsx)>1:
                self.minx=np.min(minsx[np.where(minsx!=-99999.)])
                self.maxx=np.max(maxsx[np.where(maxsx!=-99999.)])
                self.miny=np.min(minsy[np.where(minsy!=-99999.)])
                self.maxy=np.max(maxsy[np.where(maxsy!=-99999.)])
            else:
                self.minx=minsx[0]
                self.maxx=maxsx[0]
                self.miny=minsy[0]
                self.maxy=maxsy[0]
            
    def plot(self,prep=False):
        
        if prep:
            if self.idgllist==-99999:
                self.idgllist = glGenLists(1)
            
            glNewList(self.idgllist,GL_COMPILE)
            for curvect in self.myvectors:
                curvect.plot()        
            glEndList()
        else:
            if self.idgllist!=-99999:
                glCallList(self.idgllist)
            else:
                for curvect in self.myvectors:
                    curvect.plot()

    def select_vectors_from_point(self,x:float,y:float,inside=True):
        curvect:vector
        self.selected_vectors.clear()
        
        if inside:
            for curvect in self.myvectors:
                if curvect.isinside(x,y):
                    self.selected_vectors.append(curvect)
        else:
            distmin=99999.
            for curvect in self.myvectors:
                nvert:wolfvertex
                nvert= curvect.find_nearest_vert(x,y)
                dist=np.sqrt((nvert.x-x)**2.+(nvert.y-y)**2.)
                if dist<distmin:
                    distmin=dist
                    vectmin=curvect
            
            self.selected_vectors.append(vectmin)
                    
    def add2tree(self,tree:TreeListCtrl,root):
        self.mytree=tree
        self.myitem=tree.AppendItem(root, self.myname,data=self)
        tree.CheckItem(self.myitem)
        for curvect in self.myvectors:
            curvect.add2tree(tree,self.myitem)

    def unuse(self):
        for curvect in self.myvectors:
            curvect.unuse()
        self.mytree.UncheckItem(self.myitem)

    def use(self):
        for curvect in self.myvectors:
            curvect.use()
        self.mytree.CheckItem(self.myitem)

    def asshapely_ls(self):
        mylines=[]
        curvect:vector
        for curvect in self.myvectors:
            mylines.append(curvect.asshapely_ls())
        return MultiLineString(mylines)

    def prepare_shapely(self):
        self.multils = self.asshapely_ls()

    def get_selected_vectors(self,all=False):
        if all:
            mylist=[]
            if len(self.selected_vectors)>0:
                mylist.append(self.selected_vectors)
            return mylist
        else:
            if len(self.selected_vectors)>0:
                return self.selected_vectors[0]
                
        return None

class Zones(wx.Frame):

    idx:str
    tx:float
    ty:float
    minx:float
    miny:float
    maxx:float
    maxy:float

    nbzones:int

    myzones:list
    treelist:TreeListCtrl
    xls:CpGrid

    def __init__(self,myfile='',ox:float=0.,oy:float=0.,tx:float=0.,ty:float=0.,parent=None,is2D=True):
        self.loaded=True
        self.active_vector = None
        self.active_zone = None
        self.last_active = None
        self.force3D=False
        self.is2D=is2D
        
        if myfile!='':
            
            if myfile.endswith('.vecz'):
                self.is2D=False
            
            f = open(myfile, 'r')
            lines = f.read().splitlines()
            f.close()

            try:
                tx,ty=lines[0].split()
            except:
                tx,ty=lines[0].split(',')
            self.tx=float(tx)
            self.ty=float(ty)
            self.nbzones=int(lines[1])
            self.myzones=[]

            curstart=2
            for i in range(self.nbzones):
                curzone=zone(lines[curstart:],parent=self,is2D=self.is2D)
                self.myzones.append(curzone)
                curstart+=curzone.nblines()

            self.find_minmax(True)
        else:
            self.minx=ox
            self.miny=oy
            self.tx=tx
            self.ty=ty
            self.myzones=[]
            self.nbzones=0
            
        self.filename=myfile

        try:
            super(Zones, self).__init__(parent, size=(300, 400))
            self.Bind(wx.EVT_CLOSE,self.OnClose)
        except:
            pass
        
        self.parent = parent
        self.parentGUI = parent
        self.init_struct=True

    def find_nearest_vector(self,x,y):
        
        xy=Point(x,y)

        distmin=99999.
        minvec=None
        curzone:zone
        for curzone in self.myzones:
            curvect:vector
            for curvect in curzone.myvectors:
                mynp = curvect.asnparray()
                mp = MultiPoint(mynp)
                near = nearest_points(mp,xy)[0]
                dist = xy.distance(near)
                if dist < distmin:
                    minvec=curvect
                    distmin=dist
        
        return minvec


    def prep_listogl(self):
        for curzone in self.myzones:
            curzone.plot(True)
        
    def check_plot(self):
        self.plotted = True

    def uncheck_plot(self,unload=True):
        self.plotted = False
    
    def saveas(self,filename=''):
        if filename!='':
            self.filename=filename
            
        if self.filename.endswith('.vecz'):
            self.force3D=True
        
        with open(self.filename, 'w') as f:
            f.write(f'{self.tx} {self.ty}'+'\n')
            f.write(str(self.nbzones)+'\n')
            for curzone in self.myzones:
                curzone.save(f)

    def OnClose(self,e):
        self.Hide()
        pass

    def add_zone(self,addedzone):
        self.myzones.append(addedzone)
        self.nbzones+=1

    def find_minmax(self,update=False):
        
        if update:
            for zone in self.myzones:
                zone.find_minmax(update)

        if len(self.myzones)>0:
            
            minsx=np.asarray([zone.minx for zone in self.myzones])
            minsy=np.asarray([zone.miny for zone in self.myzones])
            maxsx=np.asarray([zone.maxx for zone in self.myzones])
            maxsy=np.asarray([zone.maxy for zone in self.myzones])
            
            if len(minsx)>1:
                self.minx=np.min(minsx[np.where(minsx!=-99999.)])
                self.maxx=np.max(maxsx[np.where(maxsx!=-99999.)])
                self.miny=np.min(minsy[np.where(minsy!=-99999.)])
                self.maxy=np.max(maxsy[np.where(maxsy!=-99999.)])
            else:
                self.minx=minsx[0]
                self.maxx=maxsx[0]
                self.miny=minsy[0]
                self.maxy=maxsy[0]
        else:
            self.minx=0.
            self.miny=0.
            self.maxx=1.
            self.maxy=1.
            
    def plot(self):
        for curzone in self.myzones:
            curzone.plot()

    def select_vectors_from_point(self,x:float,y:float,inside=True):
        curzone:zone
        for curzone in self.myzones:
            curzone.select_vectors_from_point(x,y,inside)

    def showstructure(self,parent,parentGUI=None):

        self.parent = parent
        self.parentGUI = parent
        if parentGUI is not None:
            self.parentGUI = parentGUI

        if self.init_struct:
            box = BoxSizer(orient=wx.HORIZONTAL)
            
            boxleft = BoxSizer(orient=wx.VERTICAL)
            boxright = BoxSizer(orient=wx.VERTICAL)

            boxadd = BoxSizer(orient=wx.VERTICAL)
            boxdelete = BoxSizer(orient=wx.VERTICAL)
            
            self.xls=CpGrid(self,-1,wx.WANTS_CHARS)
            self.xls.CreateGrid(10,4)

            self.addrows = wx.Button(self,label=_('Add rows'))
            self.addrows.Bind(wx.EVT_BUTTON,self.Onaddrows)

            self.updatevertices = wx.Button(self,label=_('Update coordinates'))
            self.updatevertices.Bind(wx.EVT_BUTTON,self.Onupdatevertices)

            self.capturevertices = wx.Button(self,label=_('Add'))
            self.capturevertices.Bind(wx.EVT_BUTTON,self.Oncapture)

            self.modifyvertices = wx.Button(self,label=_('Modify'))
            self.modifyvertices.Bind(wx.EVT_BUTTON,self.Onmodify)

            self.sascending = wx.Button(self,label=_('Verify s ascending order'))
            self.sascending.Bind(wx.EVT_BUTTON,self.Onsascending)

            self.insertvertices = wx.Button(self,label=_('Insert'))
            self.insertvertices.Bind(wx.EVT_BUTTON,self.Oninsert)

            self.zoomonactive = wx.Button(self,label=_('Zoom on'))
            self.zoomonactive.Bind(wx.EVT_BUTTON,self.Onzoom)
            
            self.saveimages = wx.Button(self,label=_('Save images from active zone'))
            self.saveimages.Bind(wx.EVT_BUTTON,self.Onsaveimages)

            boxright.Add(self.xls,1,wx.EXPAND)
            boxright.Add(self.addrows,0,wx.EXPAND)
            boxright.Add(self.updatevertices,0,wx.EXPAND)
            boxright.Add(self.capturevertices,0,wx.EXPAND)
            boxright.Add(self.modifyvertices,0,wx.EXPAND)
            boxright.Add(self.insertvertices,0,wx.EXPAND)
            boxright.Add(self.zoomonactive,0,wx.EXPAND)
            boxright.Add(self.sascending,0,wx.EXPAND)

            self.treelist = TreeListCtrl(self,style=TL_CHECKBOX|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_EDIT_LABELS)
            self.treelist.AppendColumn('Zones')
            self.treelist.Bind(EVT_TREELIST_ITEM_CHECKED, self.OnCheckItem)
            self.treelist.Bind(EVT_TREELIST_ITEM_ACTIVATED, self.OnActivateItem)
            self.treelist.Bind(EVT_TREELIST_ITEM_CONTEXT_MENU,self.OnRDown)

            self.treelist.Bind(wx.EVT_CHAR,self.OnEditLabel)

            self.addzone = wx.Button(self,label=_('Add zone'))
            self.addvector = wx.Button(self,label=_('Add vector'))
            self.deletezone = wx.Button(self,label=_('Delete zone'))
            self.findactivevector = wx.Button(self,label=_('Find in whole zones'))
            self.findactivevectorcurz = wx.Button(self,label=_('Find in active zone'))
            self.deletevector = wx.Button(self,label=_('Delete vector'))
            # self.interpolate = wx.Button(self,label=_('Interpolate vector'))

            self.addzone.Bind(wx.EVT_BUTTON,self.OnClickadd_zone)
            self.addvector.Bind(wx.EVT_BUTTON,self.OnClickadd_vector)
            self.deletezone.Bind(wx.EVT_BUTTON,self.OnClickdelete_zone)
            self.deletevector.Bind(wx.EVT_BUTTON,self.OnClickdelete_vector)
            # self.interpolate.Bind(wx.EVT_BUTTON,self.OnClickInterpolate)
            self.findactivevector.Bind(wx.EVT_BUTTON,self.OnClickfindactivate_vector)
            self.findactivevectorcurz.Bind(wx.EVT_BUTTON,self.OnClickfindactivate_vector2)

            boxadd.Add(self.addzone,1,wx.EXPAND)
            boxadd.Add(self.addvector,1,wx.EXPAND)
            boxadd.Add(self.findactivevector,1,wx.EXPAND)
            boxadd.Add(self.findactivevectorcurz,1,wx.EXPAND)
            boxdelete.Add(self.deletezone,1,wx.EXPAND)
            boxdelete.Add(self.deletevector,1,wx.EXPAND)
            # boxdelete.Add(self.interpolate,1,wx.EXPAND)
            boxdelete.Add(self.saveimages,1,wx.EXPAND)

            boxleft.Add(self.treelist,1,wx.EXPAND)
            boxleft.Add(boxadd,0,wx.EXPAND)
            boxleft.Add(boxdelete,0,wx.EXPAND)

            box.Add(boxleft,1,wx.EXPAND)
            box.Add(boxright,1,wx.EXPAND)

            self.fill_structure()

            self.treelist.SetSize(200,500)

            self.SetSizer(box)
            
            self.init_struct=False
            
        self.Show()
    
    def fill_structure(self):
        self.treelist.DeleteAllItems()

        root = self.treelist.GetRootItem()
        mynode=self.treelist.AppendItem(root, 'All zones',data=self)
        self.treelist.CheckItem(mynode)
        
        curzone:zone
        for curzone in self.myzones:
            curzone.add2tree(self.treelist,mynode)
            
        self.treelist.Expand(mynode)
        
    def expand_tree(self,objzone=None):
        root = self.treelist.GetRootItem()
        
        curchild = self.treelist.GetFirstChild(root)
        curzone=self.treelist.GetItemData(curchild)
        
        while curchild is not None:
            if curzone is objzone:
                self.treelist.Expand(curchild)
                break
            else:
                curchild=self.treelist.GetNextItem(curchild)        
                curzone=self.treelist.GetItemData(curchild)

    def Oncapture(self,event):
        if self.verify_activevec():
            return
                
        self.parentGUI.action='capture vertices'
        firstvert=wolfvertex(0.,0.)
        self.active_vector.add_vertex(firstvert)
        self.parentGUI.mimicme()

    def Onsascending(self,e):
        correct,wherec= self.active_vector.verify_s_ascending()
        self.xls_active_vector()
        
        if self.parentGUI is not None:
            if correct:
                msg=_('Modification on indices :\n')
                for curi in wherec:
                    msg+= str(curi)+'<-->'+str(curi+1)+'\n'
                dlg=wx.MessageDialog(None,msg)
                dlg.ShowModal()
    
    def Onmodify(self,event):
        self.parentGUI.action='modify vertices'
        self.parentGUI.mimicme()

    def Onzoom(self,event):
        self.parentGUI.zoomon_activevector()

    def Onsaveimages(self,event):
        self.save_images_fromvec()        
                    
    def save_images_fromvec(self,dir=''):
        if dir=='':
            dlg = wx.DirDialog(None,"Choose directory to store images",style=wx.FD_SAVE)
            ret=dlg.ShowModal()
            
            if ret==wx.ID_CANCEL:
                return
            
            dir = dlg.GetPath()
        
        for curzone in self.myzones:        
            for curvec in curzone.myvectors:
                curvec:vector
                if curvec.nbvertices>1:                
                    oldwidth=curvec.myprop.width
                    curvec.myprop.width=4
                    myname = curvec.myname

                    self.Activate_vector(curvec)
                    
                    if self.parentGUI.linked:
                        for curview in self.parentGUI.linkedList:
                            title = curview.GetTitle()
                            curview.zoomon_activevector()           
                            fn = path.join(dir,title + '_' + myname+'.png')
                            curview.save_canvasogl(fn)
                    else:
                        self.parentGUI.zoomon_activevector()           
                        fn = path.join(dir,myname+'.png')
                        self.parentGUI.save_canvasogl(fn)
                        
                        fn = path.join(dir,'palette_v_' + myname+'.png')
                        self.parentGUI.active_array.mypal.export_image(fn,'v')
                        fn = path.join(dir,'palette_h_' + myname+'.png')
                        self.parentGUI.active_array.mypal.export_image(fn,'h')
                        
                    curvec.myprop.width = oldwidth
            
    def Oninsert(self,event):
        self.parentGUI.action='insert vertices'
        self.parentGUI.mimicme()

    def Onupdatevertices(self,event):
        if self.verify_activevec():
            return
        
        self.active_vector.updatefromgrid(self.xls)
        self.find_minmax(True)

    def Onaddrows(self,event):
        nbrows=None
        dlg=wx.TextEntryDialog(None,_('How many rows?'),value='1')
        while nbrows is None:
            rc = dlg.ShowModal()
            if rc == wx.ID_OK:
                nbrows = int(dlg.GetValue())
                self.xls.AppendRows(nbrows)
            else:
                return        

    def OnClickadd_zone(self,event):
        curname=None
        dlg=wx.TextEntryDialog(None,_('Choose a name for the new zone'),value='New_Zone')
        while curname is None:
            rc = dlg.ShowModal()
            if rc == wx.ID_OK:
                curname = str(dlg.GetValue())
                newzone = zone(name=curname,parent=self)
                self.add_zone(newzone)
                self.fill_structure()
                self.active_zone = newzone
            else:
                return
    
    def OnClickadd_vector(self,event):
        curname=None
        dlg=wx.TextEntryDialog(None,_('Choose a name for the new vector'),value='New_Vector')
        while curname is None:
            rc = dlg.ShowModal()
            if rc == wx.ID_OK:
                curname = str(dlg.GetValue())
                newvec = vector(name=curname,parentzone=self.active_zone)
                self.active_zone.add_vector(newvec)
                self.fill_structure()
                self.active_vector = newvec
                
                if not self.parent is None:
                    self.parent.Active_vector(self.active_vector)                
            else:
                return

    def OnClickdelete_zone(self,event):
        curname=self.active_zone.myname
        r = wx.MessageDialog(
            None,
            _('The zone {n} will be deleted. Continue?').format(n=curname),
            style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        ).ShowModal()

        if r != wx.ID_YES:
            return

        self.myzones.pop(int(self.myzones.index(self.active_zone)))
        self.nbzones-=1
        self.fill_structure()
        self.find_minmax(True)

    def OnClickfindactivate_vector(self,event):
        if self.parentGUI is not None:
            
            dlg=wx.MessageDialog(None,"Search only closed polyline?",style=wx.YES_NO)
            ret=dlg.ShowModal()
            if ret==wx.YES:
                self.parentGUI.action = 'select active vector inside'
            else:
                self.parentGUI.action = 'select active vector all'
            self.parentGUI.active_zones=self

    def OnClickfindactivate_vector2(self,event):
        if self.parentGUI is not None:
            dlg=wx.MessageDialog(None,"Search only closed polyline?",style=wx.YES_NO)
            ret=dlg.ShowModal()
            if ret==wx.YES:
                self.parentGUI.action = 'select active vector2 inside'
            else:
                self.parentGUI.action = 'select active vector2 all'

            self.parentGUI.active_zone=self.active_zone
            self.parentGUI.active_zones=self
            
    def get_selected_vectors(self,all=False):
        curzone:zone
        if all:
            mylist=[]
            for curzone in self.myzones:
                ret = curzone.get_selected_vectors(all)
                if ret is not None:                    
                    mylist.append(ret)
            return mylist
        else:
            for curzone in self.myzones:
                ret = curzone.get_selected_vectors()
                if ret is not None:                    
                    return ret
                
            return None

    def verify_activevec(self):
        msg=''
        if self.active_vector is None:
            msg+=_('Active vector is None\n')            
            msg+=_('\n')
            msg+=_('Retry !\n')
            wx.MessageBox(msg)
            return True
         
        return False

    def OnClickdelete_vector(self,event):
        if self.verify_activevec():
            return
        
        curname=self.active_vector.myname
        r = wx.MessageDialog(
            None,
            _('The vector {n} will be deleted. Continue?').format(n=curname),
            style=wx.YES_NO | wx.ICON_QUESTION
        ).ShowModal()

        if r != wx.ID_YES:
            return

        actzone =self.active_zone
        actzone.myvectors.pop(int(actzone.myvectors.index(self.active_vector)))
        actzone.nbvectors-=1
        self.fill_structure()
        self.find_minmax(True)
        
    def unuse(self):
        for curzone in self.myzones:
            curzone.unuse()

    def use(self):
        for curzone in self.myzones:
            curzone.use()

    def OnCheckItem(self,event):

        myitem=event.GetItem()
        check = self.treelist.GetCheckedState(myitem)
        myitemdata=self.treelist.GetItemData(myitem)
        if check:
            myitemdata.use()
        else:
            myitemdata.unuse()

    def OnRDown(self,event):
        if self.verify_activevec():
            return
                
        self.active_vector.myprop.show()

    def OnActivateItem(self,event:TreeListEvent):
        myitem=event.GetItem()
        myitemdata=self.treelist.GetItemData(myitem)
        
        if isinstance(myitemdata,vector):
            self.Activate_vector(myitemdata)         
        elif isinstance(myitemdata,zone):
            self.Activate_zone(myitemdata)
            
        self.last_active = myitemdata
        
    def Activate_vector(self,object:vector):
        self.active_vector = object
        self.xls_active_vector()
        
        if object.parentzone is not None:
            self.active_zone = object.parentzone
            object.parentzone.active_vector = object

        if not self.parent is None:
            self.parent.Active_vector(self.active_vector)

    def Activate_zone(self,object:zone):
        self.active_zone = object
        if object.active_vector is not None:
            self.active_vector = object.active_vector
        elif object.nbvectors>0:
            self.active_vector = object.myvectors[0]
    
    def xls_active_vector(self):
        self.xls.ClearGrid()
        self.active_vector.fillgrid(self.xls)        

    def OnEditLabel(self,event):
        key=event.GetKeyCode()

        if key==wx.WXK_F2:
            if self.last_active is not None:        
                curname=None
                dlg=wx.TextEntryDialog(None,_('Choose a new name'),value=self.last_active.myname)
                while curname is None:
                    rc = dlg.ShowModal()
                    if rc == wx.ID_OK:
                        curname = str(dlg.GetValue())
                        self.last_active.myname = curname
                        self.fill_structure()
                    else:
                        return

    def add_interpolators(self,myinterpolators):
        myinterpolators:Interpolators
        curinterp:Interpolator

        id=0
        for curinterp in myinterpolators.myinterp:
            id+=1
            myzone = zone(name='Interpolator'+str(id),parent=self,is2D=False)
            self.add_zone(myzone)
            curinterp.add_triangles_to_zone(myzone)

        self.fill_structure()


class Grid(Zones):

    def __init__(self, size:float=1000.,ox:float=0.,oy:float=0.,ex:float=1000.,ey:float=1000., parent=None):
        super().__init__(ox=ox, oy=oy, parent=parent)

        mygrid=zone(name='mygrid',parent=self)
        self.add_zone(mygrid)
        mygridx=vector(name='mygridx')
        mygridy=vector(name='mygridy')
        contour=vector(name='contour')
        mygrid.add_vector(mygridx)
        mygrid.add_vector(mygridy)
        mygrid.add_vector(contour)
        self.creategrid(size,ox,oy,ex,ey)

    def creategrid(self,size:float=100.,ox:float=0.,oy:float=0.,ex:float=1000.,ey:float=1000.):

        mygridx=self.myzones[0].myvectors[0]
        mygridy=self.myzones[0].myvectors[1]
        contour=self.myzones[0].myvectors[2]
        mygridx.reset()
        mygridy.reset()
        contour.reset()

        locox=int(ox/size)*size
        locoy=int(oy/size)*size
        locex=(np.ceil(ex/size))*size
        locey=(np.ceil(ey/size))*size

        nbx=int(np.ceil((locex-locox)/size))
        nby=int(np.ceil((locey-locoy)/size))

        dx=locex-locox
        dy=locey-locoy

        #grillage vertical        
        xloc=locox
        yloc=locoy
        for i in range(nbx):
            newvert=wolfvertex(xloc,yloc)
            mygridx.add_vertex(newvert)
            
            yloc+=dy
            newvert=wolfvertex(xloc,yloc)
            mygridx.add_vertex(newvert)
            
            xloc+=size
            dy=-dy

        #grillage horizontal        
        xloc=locox
        yloc=locoy
        for i in range(nby):
            newvert=wolfvertex(xloc,yloc)
            mygridy.add_vertex(newvert)
            
            xloc+=dx
            newvert=wolfvertex(xloc,yloc)
            mygridy.add_vertex(newvert)
            
            yloc+=size
            dx=-dx

        newvert=wolfvertex(locox,locoy)
        contour.add_vertex(newvert)
        newvert=wolfvertex(locex,locoy)
        contour.add_vertex(newvert)
        newvert=wolfvertex(locex,locey)
        contour.add_vertex(newvert)
        newvert=wolfvertex(locox,locey)
        contour.add_vertex(newvert)

        self.find_minmax(True)
                
class Interpolator():
    '''
    Objet d'interpolation sur sections en travers
    
        - self.interpolants est une liste de listes
        - chaque élément de self.interpolants est également une liste de listes
        - chaque liste de self.interpolants[k] contient les wolfvertex de la section discrétisée
    
    '''
    
    def __init__(self,vec1:vector,vec2:vector,supports:list,ds=1.) -> None:
        
        self.interpolants=[]
        
        sect1={}
        sect2={}
        
        #Linestrings shapely des sections 1 et 2
        #ATTENTION, SHAPELY est une librairie géométrique 2D --> des outils spécifiques ont été programmés pour faire l'interpolation 3D
        s1=sect1['ls']=vec1.asshapely_ls()
        s2=sect2['ls']=vec2.asshapely_ls()
        
        nb = 0
        supls={}
        for curvec in supports:
            #linestring du support courant
            #distances des intersections des sections sur le support           
            myls:LineString
            myls=curvec.asshapely_ls()
            
            #intersections du vecteur support avec les sections
            i1=myls.intersects(s1)
            i2=myls.intersects(s2)

            if i1 and i2:
                supls[nb]={}
                supls[nb]['ls']=myls
                supls[nb]['vec']=curvec    
                nb+=1

        for k in range(nb):
            #linestring du support courant
            #distances des intersections des sections sur le support           
            myls:LineString
            myls=supls[k]['ls']
            
            #intersections du vecteur support avec les sections
            i1=myls.intersection(s1)
            i2=myls.intersection(s2)

            #Les distances, sur le support, sont calculées en projetant l'intersection du vecteur support et des sections
            supls[k][1]=myls.project(i1)
            supls[k][2]=myls.project(i2)
            
            #on ne conserve que la fraction utile entre intersections
            supls[k]['vec']=supls[k]['vec'].substring(supls[k][1],supls[k][2],False,False)

            #Les distances, sur les sections, sont calculées en projetant l'intersection du vecteur support et des sections
            sect1[k]=s1.project(i1)
            sect2[k]=s2.project(i2)

        for k in range(nb-1):
            interpolant=[]
            self.interpolants.append(interpolant)

            cursupl:vector
            cursupr:vector
            curvec1:vector
            curvec2:vector

            curvec1=sect1['sub'+str(k)]=vec1.substring(sect1[k],sect1[k+1],is3D=False,adim=False)
            curvec2=sect2['sub'+str(k)]=vec2.substring(sect2[k],sect2[k+1],is3D=False,adim=False)
            
            cursupl = supls[k]['vec']
            cursupr = supls[k+1]['vec']

            cursupl.update_lengths()
            cursupr.update_lengths()
            curvec1.update_lengths()
            curvec2.update_lengths()
                
            #Trouve la liste des distances
            nbi = np.ceil(max(curvec1.length3D,curvec2.length3D)/ds)
            locds = 1./float(nbi)
            dist = np.concatenate([np.arange(0.,1.,locds),np.cumsum(curvec1._lengthparts3D)/curvec1.length3D,np.cumsum(curvec2._lengthparts3D)/curvec2.length3D])
            dist = np.unique(np.sort(dist))
            
            nbi = int(np.ceil(max(cursupl.length3D,cursupr.length3D)/ds))
            locds = 1./float(nbi)
                    
            sloc=0.
            pt1l = curvec1.interpolate(0.,True,True)
            pt2l = curvec2.interpolate(0.,True,True)
            pt1r = curvec1.interpolate(1.,True,True)
            pt2r = curvec2.interpolate(1.,True,True)
            
            for curalong in range(nbi+1):
                print(str(curalong))
                                
                l1 = cursupl.interpolate(sloc,True,True)
                l2 = cursupr.interpolate(sloc,True,True)
                
                curvec=vector(name='loc')
                curvec.add_vertex([l1,l2])
                val = []

                if l1.z!=0.:
                    if pt1l.z==0.:
                        alpha1l=0.
                    else:
                        alpha1l = l1.z/pt1l.z
                    if pt2l.z==0.:
                        alpha2l=0.
                    else:
                        alpha2l = l1.z/pt2l.z
                else:
                    alpha1l = 0.
                    alpha2l = 0.
                if l2.z!=0.:
                    if pt1r.z==0.:
                        alpha1r = 0.
                    else:
                        alpha1r = l2.z/pt1r.z
                    
                    if pt2r.z==0.:
                        alpha2r = 0.
                    else:
                        alpha2r = l2.z/pt2r.z
                else:
                    alpha1r=0.
                    alpha2r=0.

                for curdist in dist:
                    
                    pt = curvec.interpolate(curdist,True,True)
                    
                    cur1 = curvec1.interpolate(curdist,True,True)
                    cur2 = curvec2.interpolate(curdist,True,True)

                    alpha1 = alpha1l*(1.-curdist)+alpha1r*curdist
                    alpha2 = alpha2l*(1.-curdist)+alpha2r*curdist

                    pt.z = cur1.z*alpha1*(1.-sloc) + cur2.z*alpha2*sloc
                    
                    val.append(pt)

                interpolant.append(val)
                
                sloc+=locds
                sloc=min(sloc,1.)
                
        pass

    def get_xyz_for_viewer(self,nbsub=10):
        
        pts=self.interpolants
        
        nb=0
        for curpt in pts:
            for curl in curpt:
                nb+=(len(curpt)-1)*(len(curl)-1)*3+(len(curl)-1)+(len(curpt))

        pond=np.arange(0.,1.,1./float(nbsub))
        xyz=np.ones([(nb-1)*nbsub,4],order='F')
        start=0
        for curpt in pts:           
            for k in range(len(curpt)-1):
                curl=curpt[k]
                nextl=curpt[k+1]
                for i in range(len(curl)-1):
                    v1=curl[i].getcoords()
                    v2=curl[i+1].getcoords()
                    v3=nextl[i].getcoords()
                    
                    xyz[start:start+nbsub,:3]=[v1+(v2-v1)*curpond for curpond in pond] 
                    start+=nbsub
                    xyz[start:start+nbsub,:3]= [v2+(v3-v2)*curpond for curpond in pond] 
                    start+=nbsub
                    xyz[start:start+nbsub,:3]= [v3+(v1-v3)*curpond for curpond in pond]
                    start+=nbsub
            
            curl=curpt[-1]
            for i in range(len(curl)-1):
                v1=curl[i].getcoords()
                v2=curl[i+1].getcoords()               
                xyz[start:start+nbsub,:3]=[v1+(v2-v1)*curpond for curpond in pond] 
                start+=nbsub
            for k in range(len(curpt)-1):
                curl=curpt[k]
                nextl=curpt[k+1]
                v1=curl[-1].getcoords()
                v3=nextl[-1].getcoords()                
                xyz[start:start+nbsub,:3]=[v1+(v3-v1)*curpond for curpond in pond] 
                start+=nbsub   
                
        return xyz

    def add_triangles_to_zone(self,myzone:zone):
        
        nb=0
        npt=1
        for curpt in self.interpolants:
            for k in range(len(curpt)-1):
                curl=curpt[k]
                nextl=curpt[k+1]
                for i in range(len(curl)-1):
                    curvec = vector(name='tr'+'_'+str(npt)+'_'+str(k)+'_'+str(i),parentzone=myzone)                
                    curvec.add_vertex([curl[i],curl[i+1],nextl[i]])
                    curvec.close_force()
                    myzone.add_vector(curvec)
                    
                    curvec = vector(name='tr'+'_'+str(npt)+'_'+str(k+1)+'_'+str(i),parentzone=myzone)                
                    curvec.add_vertex([nextl[i],curl[i+1],nextl[i+1]])
                    curvec.close_force()
                    myzone.add_vector(curvec)
                
            npt+=1
            nb+=(len(curpt)-1)*(len(curl)-1)*3+(len(curl)-1)+(len(curpt))
            
    def get_xy_z_for_griddata(self):
        
        xy = np.asarray([[curvertex.x,curvertex.y] for curpt in self.interpolants for curl in curpt for curvertex in curl])
        z = np.asarray([curvertex.z for curpt in self.interpolants for curl in curpt for curvertex in curl])
        
        return xy,z
                                               
class Interpolators():
    
    def __init__(self,banks:Zones,cs,ds=1.) -> None:
        
        self.mybanks = [curv for curzone in banks.myzones for curv in curzone.myvectors]
        cs.set_zones()
        self.mycs = cs.myzones
        
        self.myinterp=[]
        
        zonecs:zone
        zonecs = self.mycs.myzones[0]
        
        if zonecs.myvectors[0].up is not None:
            
            cs1=cs.get_upstream()['cs']
            
            while cs1.down is not cs1:
                cs2=cs1.down
                myinterp=Interpolator(cs1,cs2,self.mybanks,ds)
                self.myinterp.append(myinterp)
                cs1=cs2
        else:
            for i in range(zonecs.nbvectors-1):
                cs1=zonecs.myvectors[i]
                cs2=zonecs.myvectors[i+1]
                myinterp=Interpolator(cs1,cs2,self.mybanks,ds)
                self.myinterp.append(myinterp)
        
        self.mycs.add_interpolators(self)

    def viewer_interpolator(self):

        xyz=[]
        for curinterp in self.myinterp:
            xyz.append(curinterp.get_xyz_for_viewer())

        xyz=np.concatenate(xyz)

        myviewer(xyz,0)
        
    def interp_on_array(self,myarray,method):
        
        xy=[]
        z=[]
        for curint in self.myinterp: 
            tmpxy,tmpz = curint.get_xy_z_for_griddata()
            xy.append(tmpxy)
            z.append(tmpz)
            
        xy = np.concatenate(xy)
        z = np.concatenate(z)
        
        myarray.interpolate_on_cloud(xy,z,method)
                                    
                
                
                
                
        