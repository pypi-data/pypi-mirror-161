import numpy.ma as ma
import numpy as np

from .PyPalette import wolfpalette
from .PyTranslate import _
from .libs import wolfpy
from .wolf_array import WolfArray
from .mesh2d import wolf2dprev

CHOICES_VIEW_2D = [_('Water depth [m]'), 
                  _('Water level [m]'), 
                  _('Bottom level [m]'), 
                  _('Discharge X [m2s-1]'), 
                  _('Discharge Y [m2s-1]'), 
                  _('Discharge norm [m2s-1]'), 
                  _('Velocity X [ms-1]'), 
                  _('Velocity Y [ms-1]'), 
                  _('Velocity norm [ms-1]'), 
                  _('Head [m]'), 
                  _('Froude [-]')] 

class OneWolfResult:
    waterdepth : WolfArray 
    qx : WolfArray
    qy : WolfArray

    def __init__(self,fname = None,mold = None):
                
        self.waterdepth = WolfArray()
        self.top = WolfArray()
        self.qx = WolfArray()
        self.qy = WolfArray()

        self.current = self.waterdepth
        
    def set_current(self,which):        

        if which=='waterdepth':
            self.current=self.waterdepth
        elif which=='topography':
            self.current=self.top
        elif which=='qx':
            self.current=self.qx
        elif which=='qy':
            self.current=self.qy
        elif which=='qnorm':
            self.current=(self.qx**2.+self.qy**2.)**.5
        elif which=='unorm':
            self.current=(self.qx**2.+self.qy**2.)**.5/self.waterdepth
        elif which=='ux':
            self.current=self.qx/self.waterdepth
        elif which=='uy':
            self.current=self.qy/self.waterdepth
        elif which=='waterlevel':
            self.current=self.waterdepth+self.top
        elif which=='froude':
            self.current=(self.qx**2.+self.qy**2.)**.5/self.waterdepth/(self.waterdepth*9.81)**.5
        elif which=='head':
            self.current=(self.qx**2.+self.qy**2.)**.5/self.waterdepth/(2.*9.81)+self.waterdepth+self.top

class Wolfresults_2D(object):
    
    myblocks:dict

    def __init__(self,fname = None,mold = None):
        self.filename=""
        self.filenamegen=self.filename
        
        self.myparams =None
        
        self.nb_blocks = 0
        self.loaded=False
        self.current_result = -1
        self.mypal = wolfpalette(None,'Colors')
        self.mypal.default16()
        self.mypal.automatic = True

        self.nbnotnull=99999
        self.parentgui=None
        self.idx=None

        self.plotted=False
        self.plotting=False
        self.currentview=_('Water depth [m]')

        if fname is not None:
            #self.filename = fname.ljust(255)
            self.filename = fname
            self.filenamegen=self.filename
            
            with open(self.filename + '.trl') as f:
                trl=f.read().splitlines()
                self.translx=float(trl[1])
                self.transly=float(trl[2])

            wolfpy.r2d_init(self.filename.ljust(255).encode('ansi'))
            self.nb_blocks = wolfpy.r2d_nbblocks()
            self.myblocks={}
            for i in range(self.nb_blocks):
                curblock = OneWolfResult()
                self.myblocks['block'+str(i+1)] = curblock
                nbx,nby,dx,dy,ox,oy,tx,ty = wolfpy.r2d_hblock(i+1)
                
                self.myblocks['block'+str(i+1)].waterdepth.dx = dx
                self.myblocks['block'+str(i+1)].waterdepth.dy = dy
                self.myblocks['block'+str(i+1)].waterdepth.nbx = nbx
                self.myblocks['block'+str(i+1)].waterdepth.nby = nby
                self.myblocks['block'+str(i+1)].waterdepth.origx = ox
                self.myblocks['block'+str(i+1)].waterdepth.origy = oy
                self.myblocks['block'+str(i+1)].waterdepth.translx = self.translx
                self.myblocks['block'+str(i+1)].waterdepth.transly = self.transly

                self.myblocks['block'+str(i+1)].top.dx = dx
                self.myblocks['block'+str(i+1)].top.dy = dy
                self.myblocks['block'+str(i+1)].top.nbx = nbx
                self.myblocks['block'+str(i+1)].top.nby = nby
                self.myblocks['block'+str(i+1)].top.origx = ox
                self.myblocks['block'+str(i+1)].top.origy = oy
                self.myblocks['block'+str(i+1)].top.translx = self.translx
                self.myblocks['block'+str(i+1)].top.transly = self.transly
                
                self.myblocks['block'+str(i+1)].qx.dx = dx
                self.myblocks['block'+str(i+1)].qx.dy = dy
                self.myblocks['block'+str(i+1)].qx.nbx = nbx
                self.myblocks['block'+str(i+1)].qx.nby = nby
                self.myblocks['block'+str(i+1)].qx.origx = ox
                self.myblocks['block'+str(i+1)].qx.origy = oy
                self.myblocks['block'+str(i+1)].qx.translx = self.translx
                self.myblocks['block'+str(i+1)].qx.transly = self.transly

                self.myblocks['block'+str(i+1)].qy.dx = dx
                self.myblocks['block'+str(i+1)].qy.dy = dy
                self.myblocks['block'+str(i+1)].qy.nbx = nbx
                self.myblocks['block'+str(i+1)].qy.nby = nby
                self.myblocks['block'+str(i+1)].qy.origx = ox
                self.myblocks['block'+str(i+1)].qy.origy = oy
                self.myblocks['block'+str(i+1)].qy.translx = self.translx
                self.myblocks['block'+str(i+1)].qy.transly = self.transly

            self.allocate_ressources()
            self.read_topography()

        self.nbx = 1
        self.nby = 1

        ox=99999.
        oy=99999.
        ex=-99999.
        ey=-99999.
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curhead=curblock.waterdepth.get_header(False)
            ox=min(ox,curhead.origx)
            oy=min(oy,curhead.origy)
            ex=max(ex,curhead.origx+float(curhead.nbx)*curhead.dx)
            ey=max(ey,curhead.origy+float(curhead.nby)*curhead.dy)
        self.dx = ex-ox
        self.dy = ey-oy
        self.origx = ox
        self.origy = oy

    def read_param_simul(self):
        self.myparams = wolf2dprev.prev_parameters_simul(self)
        self.myparams.read_file(self.filename)
    
    def set_currentview(self,which):
                
        if which in CHOICES_VIEW_2D:

            self.plotting=True
            self.mimic_plotdata()
            
            self.delete_lists() #on efface les listes OpenGL car on va remplacer l'objet, or il peut être nue combinaison de cartes de base

            if which == _('Water depth [m]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('waterdepth')
            elif which==_('Water level [m]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('waterlevel')
            elif which==_('Bottom level [m]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('topography')
            elif which==_('Discharge X [m2s-1]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('qx')
            elif which==_('Discharge Y [m2s-1]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('qy')
            elif which==_('Discharge norm [m2s-1]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('qnorm')
            elif which==_('Velocity X [ms-1]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('ux')                
            elif which==_('Velocity Y [ms-1]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('uy')
            elif which==_('Velocity norm [ms-1]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('unorm')                
            elif which==_('Head [m]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('head')                
            elif which==_('Froude [-]'):
                for curblock in self.myblocks.values():
                    curblock:OneWolfResult
                    curblock.set_current('froude')
                    
            self.updatepalette()
            
            self.plotting=False
            self.mimic_plotdata()            

    def allocate_ressources(self):
        for i in range(self.nb_blocks):
            self.myblocks['block'+str(i+1)].waterdepth.allocate_ressources()
            self.myblocks['block'+str(i+1)].top.allocate_ressources()
            self.myblocks['block'+str(i+1)].qx.allocate_ressources()
            self.myblocks['block'+str(i+1)].qy.allocate_ressources()

    def read_topography(self):

        with open(self.filename.strip() + '.topini','rb') as f:
            for i in range(self.nb_blocks):
                nbx=self.myblocks['block'+str(i+1)].top.nbx
                nby=self.myblocks['block'+str(i+1)].top.nby
                nbbytes=nbx*nby*4
                self.myblocks['block'+str(i+1)].top.array = ma.masked_equal(np.frombuffer(f.read(nbbytes),dtype=np.float32),0.)
                self.myblocks['block'+str(i+1)].top.array = self.myblocks['block'+str(i+1)].top.array.reshape(nbx,nby,order='F')

    def get_nbresults(self):
        wolfpy.r2d_init(self.filename.ljust(255).encode('ansi'))
        return  wolfpy.r2d_getnbresults()
    
    def read_oneblockresult_withoutmask(self,which=-1,whichblock=-1):
        if whichblock!=-1:
            nbx = self.myblocks['block'+str(whichblock)].waterdepth.nbx
            nby = self.myblocks['block'+str(whichblock)].waterdepth.nby
            self.myblocks['block'+str(whichblock)].waterdepth.array, self.myblocks['block'+str(whichblock)].qx.array, self.myblocks['block'+str(whichblock)].qy.array = wolfpy.r2d_getresults(which,nbx,nby,whichblock)

    def read_oneblockresult(self,which=-1,whichblock=-1):
        if whichblock!=-1:
            self.read_oneblockresult_withoutmask(which,whichblock)
            self.myblocks['block'+str(whichblock)].waterdepth.array=ma.masked_equal(self.myblocks['block'+str(whichblock)].waterdepth.array,0.)
            self.myblocks['block'+str(whichblock)].qx.array=ma.masked_where(self.myblocks['block'+str(whichblock)].waterdepth.array==0.,self.myblocks['block'+str(whichblock)].qx.array)
            self.myblocks['block'+str(whichblock)].qy.array=ma.masked_where(self.myblocks['block'+str(whichblock)].waterdepth.array==0.,self.myblocks['block'+str(whichblock)].qy.array)

    def read_oneresult(self,which=-1):
        wolfpy.r2d_init(self.filename.ljust(255).encode('ansi'))
        for i in range(self.nb_blocks):
            self.read_oneblockresult(which,i+1)
            
        self.current_result = which
        self.loaded=True

    def get_values_as_wolf(self,i,j,which_block=1):
        h=-1
        qx=-1
        qy=-1
        vx=-1
        vy=-1
        vabs=-1
        fr=-1
        
        nbx = self.myblocks['block'+str(which_block)].waterdepth.nbx
        nby = self.myblocks['block'+str(which_block)].waterdepth.nby

        if(i>0 and i<=nbx and j>0 and j<=nby):
            h = self.myblocks['block'+str(which_block)].waterdepth.array[i-1,j-1]
            top = self.myblocks['block'+str(which_block)].top.array[i-1,j-1]
            qx = self.myblocks['block'+str(which_block)].qx.array[i-1,j-1]
            qy = self.myblocks['block'+str(which_block)].qy.array[i-1,j-1]
            if(h>0.):
                vx = qx/h
                vy = qy/h
                vabs=(vx**2.+vy**2.)**.5
                fr = vabs/(9.81*h)**.5
        
        return h,qx,qy,vx,vy,vabs,fr,h+top,top

    def get_values_from_xy(self,x,y,abs=False):
        h=-1
        qx=-1
        qy=-1
        vx=-1
        vy=-1
        vabs=-1
        fr=-1
        
        exists=False
        for which_block in range(1,self.nb_blocks+1):
            nbx = self.myblocks['block'+str(which_block)].waterdepth.nbx
            nby = self.myblocks['block'+str(which_block)].waterdepth.nby
            i,j=self.get_ij_from_xy(x,y,which_block=which_block,abs=abs)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                h = self.myblocks['block'+str(which_block)].waterdepth.array[i-1,j-1]
                top = self.myblocks['block'+str(which_block)].top.array[i-1,j-1]
                qx = self.myblocks['block'+str(which_block)].qx.array[i-1,j-1]
                qy = self.myblocks['block'+str(which_block)].qy.array[i-1,j-1]
                
                exists = top>0.
                
                if(h>0.):
                    vx = qx/h
                    vy = qy/h
                    vabs=(vx**2.+vy**2.)**.5
                    fr = vabs/(9.81*h)**.5
                    exists=True
                if exists:
                    break

        if exists:
            return (h,qx,qy,vx,vy,vabs,fr,h+top,top),(i,j,which_block)
        else:
            return (-1,-1,-1,-1,-1,-1,-1),('-','-','-')

    def get_value(self,x,y,abs=False):
        h=-1
        exists=False
        for which_block in range(1,self.nb_blocks+1):
            nbx = self.myblocks['block'+str(which_block)].waterdepth.nbx
            nby = self.myblocks['block'+str(which_block)].waterdepth.nby
            i,j=self.get_ij_from_xy(x,y,which_block=which_block,abs=False)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                h = self.myblocks['block'+str(which_block)].waterdepth.array[i-1,j-1]
                val = self.myblocks['block'+str(which_block)].current.array[i-1,j-1]

                if h is not np.nan:
                    exists=np.abs(h)>0.
                    if exists:
                        break

        if exists:
            return val
        else:
            return -1

    def get_xy_from_ij(self,i,j,which_block,abs=False):
        x,y = self.myblocks['block'+str(which_block)].waterdepth.get_xy_from_ij(i,j)
        if abs:
            return x+self.translx,y+self.transly
        else:
            return x,y

    def get_ij_from_xy(self,x,y,which_block,abs=False):
        locx=x
        locy=y
        if abs:
            locx=x-self.translx
            locy=y-self.transly
        
        i,j = self.myblocks['block'+str(which_block)].waterdepth.get_ij_from_xy(locx,locy)
        return i+1,j+1 # En indices WOLF

    def get_blockij_from_xy(self,x,y,abs=False):
        locx=x
        locy=y
        if abs:
            locx=x-self.translx
            locy=y-self.transly

        ret=self.get_values_from_xy(x,y,abs)
        
        return ret[1]

    # def extract_allsteps(x,y):
    #     myvalues=np.zeros()

    def check_plot(self):
        self.plotted = True
        self.mimic_plotdata()
        
        if not self.loaded and self.filename!='':
            self.read_oneresult(self.current_result)
            self.updatepalette()
    
    def uncheck_plot(self,unload=False):
        self.plotted = False
        self.mimic_plotdata()
        
        # if unload:
        #     for curblock in self.myblocks.values():
        #         curblock:OneWolfResult
        #         curblock.current.uncheck_plot(unload)
        #     self.rgb = None
        #     self.myblocks={}
        #     self.loaded=False
    
    def link_palette(self):
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.current.mypal = self.mypal
    
    def updatepalette(self,which=0,onzoom=[]):
        
        if onzoom!=[]:
            allarrays=[]
            for curblock in self.myblocks.values():
                curblock:OneWolfResult
                istart,jstart = curblock.current.get_ij_from_xy(onzoom[0],onzoom[2])
                iend,jend = curblock.current.get_ij_from_xy(onzoom[1],onzoom[3])
                
                istart= 0 if istart < 0 else istart
                jstart= 0 if jstart < 0 else jstart
                iend= curblock.current.nbx if iend > curblock.current.nbx else iend
                jend= curblock.current.nby if jend > curblock.current.nby else jend
                
                partarray=curblock.current.array[istart:iend,jstart:jend]
                partarray=partarray[partarray.mask==False]
                if len(partarray)>0:
                    allarrays.append(partarray.flatten())
            
            allarrays=np.concatenate(allarrays)            
            self.mypal.isopop(allarrays,allarrays.count())            
        else:
            allarrays = np.concatenate([curblock.current.array[curblock.current.array.mask==False].flatten() for curblock in self.myblocks.values()])
            self.mypal.isopop(allarrays,self.nbnotnull)
        
        self.link_palette()
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.current.rgb = self.mypal.get_rgba(curblock.current.array)

    def delete_lists(self):
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.current.delete_lists()

    def mimic_plotdata(self): 
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.current.plotted = self.plotted
            curblock.current.plotting = self.plotting
            
    def plot(self, sx=None, sy=None,xmin=None,ymin=None,xmax=None,ymax=None):
        
        self.plotting=True
        self.mimic_plotdata()
        
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.current.plot(sx, sy,xmin,ymin,xmax,ymax)
        
        if self.myparams is not None:
            self.myparams.clfbx.myzones.plot()
            self.myparams.clfby.myzones.plot()
        
        self.plotting=False
        self.mimic_plotdata()
            
    def fillonecellgrid(self,curscale,loci,locj,force=False):
        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.current.fillonecellgrid(curscale,loci,locj,force)    
            
    def set_current(self,which):

        for curblock in self.myblocks.values():
            curblock:OneWolfResult
            curblock.set_current(which)    
            
    def next_result(self):
        
        nb = self.get_nbresults()
        
        if self.current_result==-1:
            self.read_oneresult(-1)
        else:
            self.current_result+=1
            self.current_result = min(nb,self.current_result)
            self.read_oneresult(self.current_result)
            
            self.updatepalette()
            self.delete_lists()
