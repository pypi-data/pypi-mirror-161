from tkinter.messagebox import NO
from numpy import asarray,ndarray,arange,zeros,linspace,concatenate,unique,amin,amax
import math
import matplotlib.pyplot as plt
from shapely.geometry import LineString,MultiLineString,Point,Polygon,CAP_STYLE,Point
from shapely.prepared import prep
from shapely.ops import nearest_points,substring
from OpenGL.GL  import *
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from os import path

from .PyTranslate import _
from .PyVertexvectors import vector,zone,Zones
from .PyVertex import wolfvertex,cloud_vertices
from .laz_viewer import scandir,xyzlaz_scandir,xyz_laz_grid

example_largesect='''-138 100
-114 90
-70 80
-45 70
-32 62
0 61.5
32 62
60 70
80 80
98 84
120 87'''

example_smallsect='''0 68
10 67
12 65
15 63
20 62
24 61.5
30 62
35 64
40 66
42 66.5
50 68'''

example_diffsect1='''0 10
10 5
12 5
15 6
16 6
17 5
20 3
25 3
30 5
42 7
50 10'''

def INTERSEC(x1,y1,x2,y2,el):
    '''Procédure de calcul de l'abscisse d'intersection d'une altitude donnée el 
    dans un segment défini par ses coordonnées (x1,y1) et (x2,y2)'''
    xx=1.0e10

    if x2-x1==0.:
        if y2>y1:
            if y1<=el<=y2:
                return x2
        elif y2<y1:
            if y2<=el<=y1:
                return x2
    elif 0.0<abs(y2-y1):
        a=(y2-y1)/(x2-x1)
        b=(x2*y1-x1*y2)/(x2-x1)
        xx=(el-b)/a
    return xx

class profile(vector):
    '''Surcharge d'un vecteur en vue de définir un profil de rivière
    
    Les coordonnées attendues sont en 3D (x,y,z)
    '''
    bankleft:wolfvertex
    bankright:wolfvertex
    bed:wolfvertex
    
    def __init__(self, name, data_sect='',parent=None) -> None:
        super().__init__(name=name)

        if data_sect!='':
            for curline in data_sect.splitlines():
                values=curline.split(' ')                
                curvert=wolfvertex(float(values[0]),0.,float(values[1]))
                self.add_vertex(curvert)
                
        self.bankleft=None
        self.bankright=None
        self.bed=None
        self.s = 0.0
        self.up = None
        self.down = None  
        self.laz=False
        self.parent=parent

        # self.zdatum = 0.
        # self.add_zdatum=False

        # self.sdatum = 0.
        # self.add_sdatum=False

        self.orient = None

    def set_orient(self):
        self.orient = asarray([self.myvertices[-1].x-self.myvertices[0].x,
                              self.myvertices[-1].y-self.myvertices[0].y])
        self.orient = self.orient /np.linalg.norm(self.orient)
    
    def get_xy_from_s(self,s):
        if self.orient is None:
            self.set_orient()

        return self.myvertices[0].x+self.orient[0]*s,self.myvertices[0].y+self.orient[1]*s

    def get_laz_around(self,length_buffer=10.):
        
        myls = self.asshapely_ls()
        mypoly = myls.buffer(length_buffer,cap_style=CAP_STYLE.square)
        mybounds = ((mypoly.bounds[0],mypoly.bounds[2]),(mypoly.bounds[1],mypoly.bounds[3]))
        
        myxyz = self.parent.gridlaz.scan(mybounds)
        
        prep_poly = prep(mypoly)
        mytests = [prep_poly.contains(Point(cur)) for cur in myxyz]
        
        self.usedlaz = np.asarray(myxyz[mytests])
        
        orig = [self.myvertices[0].x,self.myvertices[0].y]
        a=[self.myvertices[-1].x-self.myvertices[0].x,self.myvertices[-1].y-self.myvertices[0].y]
        a= a/np.linalg.norm(a)
        
        self.s_laz = np.asarray([np.dot(a,cur[:2]-orig) for cur in self.usedlaz])
        
        self.colors_laz=np.ones((self.usedlaz.shape[0],4),dtype=np.float32)

        self.colors_laz[self.usedlaz[:,3]==1]=[.5,.5,.5,1.]
        self.colors_laz[self.usedlaz[:,3]==2]=[.5,.25,.25,1.]
        self.colors_laz[self.usedlaz[:,3]==4]=[0.,0.5,0.,1.]
        self.colors_laz[self.usedlaz[:,3]==9]=[0.,0.5,1.,1.]
        self.colors_laz[self.usedlaz[:,3]==10]=[1,0.2,0.2,1.]

        s = np.asarray([float(np.cross(a,cur[:2]-orig))  for cur in self.usedlaz])
        self.colors_laz[:,3] = 1.-np.abs(s)/(length_buffer+1.)

        up=np.where(s[:]<0.)[0]
        down=np.where(s[:]>=0.)[0]
        self.uplaz = self.s_laz[up]
        self.downlaz = self.s_laz[down]
        
        self.uplaz_colors = self.colors_laz[up]
        self.downlaz_colors = self.colors_laz[down]
        
        self.upz = self.usedlaz[up]
        self.downz = self.usedlaz[down]
                
        self.laz=True
            
    def plot_laz(self,length_buffer=5.,fig:Figure=None,ax:Axes=None,show=False):
        
        if not self.laz:
            self.get_laz_around(length_buffer)
        
        if ax is None:
            fig = plt.figure()
            ax=fig.add_subplot(111)
                
        # ax.scatter(self.s_laz,self.usedlaz[:,2],c=self.colors_laz,marker='.')
        ax.scatter(self.uplaz,self.upz[:,2],c=self.uplaz_colors,marker='.')
        ax.scatter(self.downlaz,self.downz[:,2],c=self.downlaz_colors,marker='+')
                
        if show:
            fig.show()   
            
        return np.min(self.usedlaz[:,2]),np.max(self.usedlaz[:,2])
    
    def slide_vertex(self,s):
        if self.orient is None:
            self.set_orient()

        dx = self.orient[0] *s
        dy = self.orient[1] *s

        for curv in self.myvertices:
            curv.x +=dx
            curv.y +=dy
    
    def movebankbed(self,which,orientation):
        if which=='left':
            curvert = self.bankleft
        elif which =='right':
            curvert = self.bankright
        elif which=='bed':
            curvert = self.bed
            
        for k in range(self.nbvertices):
            if self.myvertices[k]==curvert:
                break

        if orientation=='left':
            if k>0:
                curvert=self.myvertices[k-1]
        elif orientation=='right':
            if k<self.nbvertices-1:
                curvert=self.myvertices[k+1]
    
        if which=='left':
            self.bankleft = curvert
        elif which=='right':
            self.bankright = curvert
        elif which=='bed':
            self.bed = curvert
            
    def movebankbedslider(self,which,pt:Point):
        if which=='left':
            curvert = self.bankleft
        elif which =='right':
            curvert = self.bankright
        elif which=='bed':
            curvert = self.bed
            
        curvert.x = pt.x
        curvert.y = pt.y
        curvert.z = pt.z
    
    def save(self,f):
        
        if self.parent.forcesuper:
            super().save(f)
        else:
            for curvert in self.myvertices:
                which=''
                if curvert is self.bed:
                    which = "BED"
                elif curvert is self.bankleft:
                    which = "LEFT"
                elif curvert is self.bankright:
                    which = "RIGHT"
                
                f.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(self.myname,curvert.x,curvert.y,which,curvert.z))
        
    def get_s_from_xy(self,xy:wolfvertex):
        x1 = self.myvertices[0].x
        y1 = self.myvertices[0].y
        length = math.sqrt((xy.x-x1)**2.+(xy.y-y1)**2.)
        
        return length
    
    def get_sz(self,cumul=True):
            
        z = asarray([self.myvertices[i].z for i in range(self.nbvertices)])
        
        if self.add_zdatum:
            z+=self.zdatum

        nb = len(z)
        s = zeros(nb)
        
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
            
        if self.add_sdatum:
            s+=self.sdatum

        return s,z

    def set_sz(self,sz,trace):
        orig = trace[0]
        end = trace[1]

        vec = np.asarray(end)-np.asarray(orig)
        vec = vec/np.linalg.norm(vec)

        xy = np.asarray([s*vec+np.asarray(orig) for s in sz[:,0]])

        for i in range(len(xy)):
            curvert = wolfvertex(xy[i,0],xy[i,1],sz[i,1])
            self.add_vertex(curvert)

    def get_sz_banksbed(self):
            
        x1 = self.myvertices[0].x
        y1 = self.myvertices[0].y

        if self.bankleft != None:
            x2 = self.bankleft.x
            y2 = self.bankleft.y            
            sleft = math.sqrt((x2-x1)**2.+(y2-y1)**2.)
            zleft=self.bankleft.z
        else:
            sleft=-99999.
            zleft=-99999.

        if self.bankright != None:
            x2 = self.bankright.x
            y2 = self.bankright.y            
            sright = math.sqrt((x2-x1)**2.+(y2-y1)**2.)
            zright=self.bankright.z
        else:
            sright=-99999.
            zright=-99999.

        if self.bed != None:
            x2 = self.bed.x
            y2 = self.bed.y            
            sbed = math.sqrt((x2-x1)**2.+(y2-y1)**2.)
            zbed=self.bed.z
        else:
            sbed=-99999.
            zbed=-99999.
            
        if self.add_sdatum:
            sleft+=self.sdatum
            sbed+=self.sdatum
            sright+=self.sdatum
        if self.add_zdatum:
            zleft+=self.zdatum
            zbed+=self.zdatum
            zright+=self.zdatum
            
        return sleft,sbed,sright,zleft,zbed,zright
        
    def get_min(self):
        return sorted(self.myvertices,key=lambda x:x.z)[0]
    
    def get_max(self):
        return sorted(self.myvertices,key=lambda x:x.z)[-1]
    
    def get_minz(self):
        return amin(list(x.z for x in self.myvertices))
    
    def get_maxz(self):
        return amax(list(x.z for x in self.myvertices))

    def plot_linked(self,fig,ax):
        
        colors=['red','blue','green']
        
        k=0
        for curarray,curlabel in zip(self.parent.linked_arrays,self.parent.linked_labels):
            if curarray.plotted:            
                myls = self.asshapely_ls()

                length = myls.length
                ds = min(curarray.dx,curarray.dy)
                nb = int(np.ceil(length/ds*2))
                
                alls = np.linspace(0,int(length),nb)
                
                pts = [myls.interpolate(curs) for curs in alls]
                
                allz = [curarray.get_value(curpt.x,curpt.y) for curpt in pts]
                
                if np.max(allz)>-99999:
                    ax.plot(alls,allz,
                            color=colors[np.mod(k,3)],
                            lw=2.0,
                            label=curlabel)
                k+=1
    
    def plot_cs(self,fwl=None,show=False,forceaspect=True,fig:Figure=None,ax:Axes=None,plotlaz=True):
        # plot
        x,y=self.get_sz()
        
        sl,sb,sr,yl,yb,yr = self.get_sz_banksbed()
        
        xmin=x[0]
        xmax=x[-1]
        ymin=self.get_minz()
        ymax=self.get_maxz()
        
        dy=ymax-ymin
        ymin-=dy/4.
        ymax+=dy/4.
        
        if ax is None:
            redraw=False
            fig = plt.figure()
            ax=fig.add_subplot(111)
        else:
            redraw=True
            ax.cla()
            
        ax.plot(x,y,color='black',
                lw=2.0,
                label='Profil ARNE')
        
        if plotlaz and self.parent.dirlaz !='':
            minlaz=ymin
            maxlaz=ymax
            minlaz,maxlaz=self.plot_laz(fig=fig,ax=ax)
            ymin = min(ymin,minlaz)
            ymax = max(ymax,maxlaz)

        self.plot_linked(fig,ax)
        
        if fwl != None:
            ax.fill_between(x,y,fwl,where=y<=fwl,facecolor='cyan',alpha=0.3,interpolate=True)
            
        if sl != -99999.:
            ax.plot(sl,yl,'or')
        if sb != -99999.:
            ax.plot(sb,yb,'ob')
        if sr != -99999.:
            ax.plot(sr,yr,'og')
        
        ax.set_title(self.myname)
        ax.set_xlabel('Distance [m]')
        ax.set_ylabel('Elevation [EL.m]')
        ax.legend()
        
        tol=(xmax-xmin)/10.
        ax.set_xlim(xmin-tol,xmax+tol)
        ax.set_ylim(ymin,ymax)
        
        if forceaspect:
            aspect=1.0*(ymax-ymin)/(xmax-xmin)*(ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0])
            ax.set_aspect(aspect)
                
        if show:
            fig.show()     
            
        if redraw:
            fig.canvas.draw()
            
    def relation_oneh(self,cury,x=None,y=None):

        if x is None and y is None:
            x,y=self.get_sz()

        s=a=w=0.0
        for i in range(0,len(x)-1):
            #recherche des intersections sur les segments
            x1=x[i]
            y1=y[i]
            x2=x[i+1]
            y2=y[i+1]
            
            #calcul des incréments de section et de périmètre
            dS=0.0
            dA=0.0
            dL=0.0
            if y1<=cury and y2<=cury:
                #le segment est totalement situé en dessous de la hauteur utile
                dS=math.sqrt((x2-x1)**2.+(y2-y1)**2.)
                dA=0.5*(2.0*cury-y1-y2)*(x2-x1)
                dL=(x2-x1)
            else:
                xx=INTERSEC(x1,y1,x2,y2,cury)
                if x1<=xx and xx<=x2:
                    #le segment intersecte la hauteur utile
                    if y2<=cury and cury<=y1:
                        dS=math.sqrt((x2-xx)**2.+(y2-cury)**2.)
                        dA=0.5*(x2-xx)*(cury-y2)
                        dL=(x2-xx)
                    if y1<=cury and cury<=y2:
                        dS=math.sqrt((xx-x1)**2.+(cury-y1)**2.)
                        dA=0.5*(xx-x1)*(cury-y1)
                        dL=(xx-x1)

            #ajout des incréments
            s+=dS
            a+=dA
            w+=dL
        
        if 0.0<s:
            r=a/s
        else:
            r=0.

        return a,s,w,r

    def relations(self):
        x,y=self.get_sz()
        
        ymin=min(y)
        ymax=max(y)
        
        yy = concatenate([linspace(ymin,ymax,100),y])
        yy=unique(yy)
        yy.sort()
                
        nb=len(yy)
        
        a=zeros(nb)      #area
        s=zeros(nb)      #wet perimeter
        w=zeros(nb)    #width
        r=zeros(nb)      #hydraulic radius
        h=zeros(nb)      #water depth
        
        for k in range(nb):
            a[k],s[k],w[k],r[k] = self.relation_oneh(yy[k],x,y)                
            h[k]=yy[k]-ymin

        self.wetarea = a
        self.wetperimeter = s
        self.hyrdaulicradius = r
        self.waterdepth=h
        self.localwidth=w

    def slopes(self):
        
        slopedown = (self.get_minz() - self.down.get_minz()) / abs(self.down.s - self.s+1.e-10)
        slopeup   = (self.up.get_minz() - self.get_minz()) / abs(self.s - self.up.s+1.e-10)
        slopecentered = (self.up.get_minz() - self.down.get_minz()) / abs(self.down.s - self.up.s+1.e-10)
        
        return slopeup,slopecentered,slopedown
    
    def ManningStrickler_Q(self,slope=1.e-3,nManning=0.,KStrickler=0.):
        '''Procédure générique pour obtenir une relation uniforme Q-H sur base 
            - nManning : un coefficient de frottement
            - slope : une pente
        '''
        
        if nManning==0. and KStrickler==0.:
            return
        elif nManning>0.: 
            coeff=1./nManning
        elif KStrickler>0.:
            coeff = KStrickler
            
        nn=len(self.waterdepth)
        sqrtslope=math.sqrt(slope)

        self.q=asarray([coeff * self.hyrdaulicradius[k]**(2./3.)*sqrtslope * self.wetarea[k] for k in range(nn)])

    def ManningStrickler_oneQ(self,slope=1.e-3,nManning=0.,KStrickler=0.,cury=0.):
        '''Procédure générique pour obtenir une relation uniforme Q-H sur base 
            - nManning : un coefficient de frottement
            - slope : une pente
        '''
        
        if nManning==0. and KStrickler==0.:
            return
        elif nManning>0.: 
            coeff=1./nManning
        elif KStrickler>0.:
            coeff = KStrickler
        
        a,s,w,r = self.relation_oneh(cury)

        sqrtslope=math.sqrt(slope)

        q=coeff * r**(2./3.) * sqrtslope * a

        return q

    def plot_relations_Q(self,fwl=None,show=False):
        # plot
        xmin=self.waterdepth[0]
        xmax=self.waterdepth[-1]
        
        fig,ax = plt.subplots(2,1)
        
        
        curax=ax[0]
        curax.set_title(self.myname)
        curax.plot(self.waterdepth,self.wetarea,color='black',lw=1.0,label='wet area')
        curax.plot(self.waterdepth,self.wetperimeter,color='blue',lw=.5,label='wet perimeter')
        curax.plot(self.waterdepth,self.localwidth,color='cyan',lw=.5,label='local width')
        curax.set_ylabel('S-P-W')
        curax.legend(loc='upper left')
        
        curax=curax.twinx()
        curax.plot(self.waterdepth,self.hyrdaulicradius,color='green',lw=.5,label='hydraulic radius')
        curax.set_ylabel('Radius')
        curax.legend(loc='lower right')
        curax.set_xlim(xmin,xmax)
        
        curax=ax[1]
        curax.plot(self.waterdepth,self.q,color='red',lw=1.0,label='uniform discharge')
        curax.set_ylabel('Discharge')
                
        curax.set_xlabel('Water depth [m]')        
        curax.set_xlim(xmin,xmax)
        
        if show:
            plt.show()        

class crosssections():

    myprofiles:dict
    mygenprofiles:dict

    def __init__(self,myfile,format=2022,dirlaz='F:\\LAZ\\GridXYZfine') -> None:
        
        self.filename=myfile
        self.myzones=None
        self.myzone=None
        
        if path.exists(dirlaz):
            self.dirlaz=dirlaz    
            self.gridlaz = xyz_laz_grid(self.dirlaz)
        else:
            self.dirlaz=''
            self.gridlaz =None
            
        self.format = None
        
        self.linked_arrays=[]
        self.linked_labels=[]
        
        f=open(myfile,'r')
        lines=f.read().splitlines()
        f.close()

        self.myprofiles={}
        self.mygenprofiles={}
        self.multils = None
        self.sorted = {}
        self.plotted = False

        if format==2000:
            self.format='2000'
            lines.pop(0)
            nameprev=''
            index=0
            for curline in lines:
                vals=curline.split('\t')
                name=vals[0]

                if name!=nameprev:
                    #création d'un nouveau dictionnaire
                    self.myprofiles[name]={}
                    curdict=self.myprofiles[name]
                    curdict['index']=index
                    index+=1
                    curdict['cs']=profile(name=name,parent=self)
                    cursect:profile
                    cursect=curdict['cs']

                x=float(vals[1])
                y=float(vals[2])
                type=vals[3]
                z=float(vals[4])

                curvertex=wolfvertex(x,y,z)
                cursect.add_vertex(curvertex)
                if type=='LEFT':
                    if cursect.bankleft is None:
                        cursect.bankleft=curvertex
                        curdict['left']=cursect.bankleft
                    else:
                        print(name)                
                elif type=='BED':
                    if cursect.bed is None:
                        cursect.bed=curvertex
                        curdict['bed']=cursect.bed
                    else:
                        print(name)                
                elif type=='RIGHT':
                    if cursect.bankright is None:
                        cursect.bankright=curvertex
                        curdict['right']=cursect.bankright
                    else:
                        print(name)                

                nameprev=name
        elif format==2022:
            self.format='2022'
            lines.pop(0)
            nameprev=''
            index=0
            for curline in lines:
                vals=curline.split('\t')
                
                if vals[0].find('.')>0:
                    name=vals[0].split('.')[0]
                    xpos=1
                    ypos=xpos+1
                    zpos=ypos+1
                    labelpos=zpos+1
                else:
                    name=vals[0]
                    xpos=2
                    ypos=xpos+1
                    zpos=ypos+1
                    labelpos=zpos+1

                if name!=nameprev:
                    #création d'un nouveau dictionnaire
                    self.myprofiles[name]={}
                    curdict=self.myprofiles[name]
                    curdict['index']=index
                    index+=1
                    curdict['cs']=profile(name=name,parent=self)
                    cursect:profile
                    cursect=curdict['cs']

                x=float(vals[xpos].replace(',','.'))
                y=float(vals[ypos].replace(',','.'))
                z=float(vals[zpos].replace(',','.'))

                curvertex=wolfvertex(x,y,z)
                cursect.add_vertex(curvertex)
                
                type=''
                type=vals[labelpos]
                
                if type=='HBG':
                    if cursect.bankleft is None:
                        cursect.bankleft=curvertex
                        curdict['left']=cursect.bankleft
                    else:
                        print(name)                
                elif type=='TWG':
                    if cursect.bed is None:
                        cursect.bed=curvertex
                        curdict['bed']=cursect.bed
                    else:
                        print(name)                
                elif type=='HBD':
                    if cursect.bankright is None:
                        cursect.bankright=curvertex
                        curdict['right']=cursect.bankright
                    else:
                        print(name)                

                nameprev=name
        elif format=='vecz':
            tmpzones=Zones(myfile)
            
            curzone:zone
            curvec:vector
            curzone=tmpzones.myzones[0]
            index=0
            for curvec in curzone.myvectors:

                self.myprofiles[curvec.myname]={}
                curdict=self.myprofiles[curvec.myname]
                
                curdict['index']=index
                curdict['left']=None
                curdict['bed']=None
                curdict['right']=None
                
                index+=1
                curdict['cs']=profile(name=curvec.myname,parent=self)
                cursect:profile
                cursect=curdict['cs']
                
                cursect.myvertices = curvec.myvertices
                cursect.nbvertices = curvec.nbvertices

        elif format=='sxy':
            self.format='sxy'
            nbpotsect = int(lines[0])
            index=1
            for i in range(nbpotsect):
                vals=lines[index].split(',')
                nbrel=int(vals[0])
                index+=1
                sz = np.asarray([np.float64(cursz) for k in range(index,index+nbrel) for cursz in lines[k].split(',') ]).reshape([nbrel,2],order='C')
                self.mygenprofiles[i+1]=sz
                index+=nbrel
            
            nbsect = int(lines[index])
            # o linked position in a 2D array (i, j) (integer,integer) (optional)
            # o datum (float) – added to the Z_min of the raw cross section (optional)
            # o boolean value indicating whether the relative datum must be added (logical)
            # o boolean value indicating whether it is a real or synthetic section (logical)
            # o ID of the cross section to which this line relates (integer)
            # o pair of coordinates of the left end point (float, float)
            # o pair of coordinates of the right end point (float, float)
            # o pair of coordinates of the minor bed (float, float) (optional)
            # o pair of coordinates of the left bank in local reference (float, float) (optional)
            # o pair of coordinates of the right bank in local reference (float, float) (optional)
            # o boolean value indicating whether an attachment point has been defined (optional)            
            # # 2,2,0,#FALSE#,#TRUE#,16,222075.5,110588.5,222331.5,110777.5,99999,99999,99999,99999,99999,99999,#FALSE#
            # 2,2,0,#FALSE#,#TRUE#,17,222131.6,110608.2,222364.4,110667.9,99999,99999,99999,99999,99999,99999,#FALSE#
            index+=1
            #création d'un nouveau dictionnaire
            for i in range(nbsect):
                name=str(i+1)
                vals=lines[index].split(',')
                index+=1
                
                posi = int(vals[0])
                posj = int(vals[1])
                zdatum = float(vals[2])
                add_zdatum=vals[3]=='#TRUE#'
                real_sect=vals[4]=='#TRUE#'
                id = int(vals[5])
                startx=float(vals[6])
                starty=float(vals[7])
                endx=float(vals[8])
                endy=float(vals[9])
                beds=float(vals[10])
                bedz=float(vals[11])
                lbs=float(vals[12])
                lbz=float(vals[13])
                rbs=float(vals[14])
                rbz=float(vals[15])
                attached=vals[16]=='#TRUE#'

                curdict=self.myprofiles[name]={}
                curdict['index']=id
                curdict['cs']=profile(name=name,parent=self)
                cursect:profile
                cursect=curdict['cs']

                cursect.zdatum = zdatum
                cursect.add_zdatum = add_zdatum
                
                cursect.set_sz(self.mygenprofiles[id],[[startx,starty],[endx,endy]])

                if lbs!=99999:
                    cursect.bankleft=wolfvertex(lbs,lbz)
                    curdict['left']=cursect.bankleft                
                if beds!=99999:
                    cursect.bed=wolfvertex(beds,bedz)
                    curdict['bed']=cursect.bed
                if rbs!=99999:
                    cursect.bankright=wolfvertex(rbs,rbz)
                    curdict['right']=cursect.bankright

        self.verif_bed()
        self.find_minmax(True)
        
        self.cloud = cloud_vertices()
        curprof:profile
        for idx,vect in self.myprofiles.items():
            curprof=vect['cs']
            if not curprof.bankleft is None:
                myvert = wolfvertex(curprof.bankleft.x,curprof.bankleft.y)
                self.cloud.add_vertex(myvert)
            if not curprof.bankright is None:
                myvert = wolfvertex(curprof.bankright.x,curprof.bankright.y)
                self.cloud.add_vertex(myvert)
            if not curprof.bed is None:
                myvert = wolfvertex(curprof.bed.x,curprof.bed.y)
                self.cloud.add_vertex(myvert)    
                
            # curprof.get_laz_around()   
        
        self.cloud.find_minmax(True)
        
        pass
       
        self.verif_bed()
        
        pass
    
    def set_zones(self,forceupdate=False):
        if forceupdate:
            self.myzone=None
            self.myzones=None

        if self.myzones is None:
            self.myzones=Zones(is2D=False)
            self.myzones.force3D=True
            self.myzone=zone(name='CS',parent=self.myzones)
            self.myzones.add_zone(self.myzone)
        
            for curprof in self.myprofiles.keys():
                curdict=self.myprofiles[curprof]
                curprof=curdict['cs']
                self.myzone.add_vector(curprof)
                curprof.parentzone=self.myzone
    
    def showstructure(self,parent,parentGUI=None):
        self.set_zones()
        self.myzones.showstructure(parent,parentGUI)

    def get_upstream(self):
        curprof:profile
        curprof=self.myprofiles[list(self.myprofiles.keys())[0]]['cs']

        while curprof.up is not curprof:
            curprof = curprof.up

        return self.myprofiles[curprof.myname]

    def get_downstream(self):
        curprof:profile
        curprof=self.myprofiles[list(self.myprofiles.keys())[0]]['cs']

        while curprof.down is not curprof:
            curprof = curprof.down

        return self.myprofiles[curprof.myname]

    def rename(self,fromidx,updown=True):

        idx=fromidx

        if updown:
            curdict=self.get_upstream()
            curvec:profile
            curvec=curdict['cs']
            while curvec.down is not curvec:
                self.myprofiles[idx]=curdict
                self.myprofiles.pop(curvec.myname)
                curvec.myname=str(idx)
                idx+=1

                curdict = self.myprofiles[curvec.down.myname]
                curvec=curvec.down

            self.myprofiles[idx]=curdict
            self.myprofiles.pop(curvec.myname)
            curvec.myname=str(idx)
        else:
            mykeys=list(self.myprofiles.keys())
            for curprof in mykeys:
                curdict=self.myprofiles[idx]=self.myprofiles[curprof]
                self.myprofiles.pop(curprof)
                curdict['cs'].myname=str(idx)
                idx+=1
                
        self.set_zones(True)
            
    def check_plot(self):
        self.plotted = True

    def uncheck_plot(self,unload=True):
        self.plotted = False

    def saveas(self,filename=None):
        self.forcesuper=False
        
        if filename is not None:
            self.filename = filename
            
        if self.filename is None:
            print(_('No Filename -- Retry !'))
            return
            
        if self.filename.endswith('.vecz'):
            self.forcesuper=True    
            self.saveas_wolfvec(self.filename)
        elif self.format=='2000' or self.format=='2022':        
            with open(self.filename,'w') as f:
                f.write("Profile\tx\ty\tBerge\tz\n")
                for idx,curvect in self.myprofiles.items():
                    curprof=curvect['cs']
                    curprof.save(f)
        elif self.format=='sxy':
            with open(self.filename,'w') as f:
                f.write(str(len(self.mygenprofiles)))
                for curid in self.mygenprofiles.keys():
                    cursect = self.mygenprofiles[curid]
                    f.write('{n},0'.format(n=len(cursect)))
                    for xy in cursect:
                        f.write('{x},{y}'.format(x=xy[0],y=xy[1]))
                f.write(str(len(self.myprofiles)))
                for curid in self.myprofiles.keys():
                    curdict = self.myprofiles[curid]
                    cursect:profile
                    cursect = curdict['cs']
                    locid=curdict['index']
                    
                    f.write('2,2,{zdatum},{add_datum},#TRUE#,{id},{x1},{y1},{x2},{y2},{beds},{bedz},{lbs},{lbz},{rbs},{rbz},#FALSE#'.format(
                                    zdatum=xy[0],
                                    add_datum=xy[1],
                                    id=locid,
                                    x1=cursect.myvertices[0].x,
                                    y1=cursect.myvertices[0].y,
                                    x2=cursect.myvertices[-1].x,
                                    y2=cursect.myvertices[-1].y,
                                    beds=cursect.get_s_from_xy(cursect.bed),
                                    bedz=cursect.bed.z,
                                    lbs=cursect.get_s_from_xy(cursect.bankleft),
                                    lbz=cursect.bankleft.z,
                                    rbs=cursect.get_s_from_xy(cursect.bankright),
                                    rbz=cursect.bankright.z))
    
    def verif_bed(self):        
        for idx,curvect in self.myprofiles.items():
            curprof=curvect['cs']
            if curprof.bed is None:
                curprof.bed = curprof.get_min()    

    def get_min(self,whichname='',whichprofile=None):
        curvect:profile
        if whichname!='':
            curvect=self.myprofiles[whichname]['cs']
            curvert=curvect.myvertices
        elif not whichprofile is None:
            curvect=whichprofile['cs']
            curvert=curvect.myvertices
        return sorted(curvert,key=lambda x:x.z)[0]       

    def asshapely_ls(self):
        mylines=[]
        curvect:profile
        for idx,curvect in self.myprofiles.items():
            mylines.append(curvect['cs'].asshapely_ls())
        return MultiLineString(mylines)

    def prepare_shapely(self):
        self.multils = self.asshapely_ls()
    
    def sort_along(self,vecsupport:LineString,name:str,downfirst=True):
        '''Sélectionne les sections qui intersectent un vecteur support 
        et les trie selon l'abscisse curviligne'''
        
        curdict = self.sorted[name]={}
        curdict['support'] = vecsupport
        mysorted = curdict['sorted']  = []
        length = vecsupport.length

        prep(vecsupport) #Prepare le vecteur support aux opérations récurrentes
        curvect:profile
        for idx,curv in self.myprofiles.items():
            #bouclage sur les sections
            curvect=curv['cs']
            #obtention de la section sous forme d'un objet Shapely
            myline = curvect.asshapely_ls()
            if vecsupport.intersects(myline):
                #le vecteur intersecte --> on calcule le point d'intersection
                myintersect = vecsupport.intersection(myline)
                #on projette l'intersection sur le support pour trouver l'abscisse curvi
                mydist = vecsupport.project(myintersect)
                #on ajoute le vecteur à la liste
                mysorted.append(curvect)
                if downfirst:
                    curvect.s = length - mydist        
                else:
                    curvect.s = mydist        
        
        #on trie le résultat en place        
        mysorted.sort(key=lambda x:x.s)
        
        mysorted[0].down = mysorted[1]
        mysorted[0].up = mysorted[0]
        mysorted[-1].up = mysorted[-2]
        mysorted[-1].down = mysorted[-1]
        for idx in arange(1,len(mysorted)-1):
            mysorted[idx].down = mysorted[idx+1] 
            mysorted[idx].up = mysorted[idx-1] 
        
        return len(mysorted)        
    
    def find_minmax(self,update=False):
        if update:
            for idx,vect in self.myprofiles.items():
                vect['cs'].find_minmax()

        self.minx=min(vect['cs'].minx for idx,vect in self.myprofiles.items())
        self.miny=min(vect['cs'].miny for idx,vect in self.myprofiles.items())
        self.maxx=max(vect['cs'].maxx for idx,vect in self.myprofiles.items())
        self.maxy=max(vect['cs'].maxy for idx,vect in self.myprofiles.items())

    def plot(self):
        self.set_zones()
        self.myzones.plot()
        # for idx,curvect in self.myprofiles.items():
        #     curvect['cs'].plot()
                        
    def saveas_wolfvec(self,filename:str):
        
        self.set_zones()
        self.myzones.saveas(filename=filename)
        
    def select_profile(self,x,y):
        
        mypt = Point(x,y)
        distmin=1.e300
        profmin=None
        
        curprof:profile
        for idx,vect in self.myprofiles.items():
            curprof=vect['cs']
            myshap=curprof.asshapely_ls()
            dist=myshap.distance(mypt)
            
            if dist<distmin:
                profmin=curprof
                distmin=dist
                
        return profmin
                
  


        
        
        