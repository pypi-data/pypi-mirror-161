from matplotlib.pyplot import axes, show
import numpy as np
import wx
import wx.lib.agw.aui as aui
from shapely.geometry import LineString
from matplotlib import figure as mplfig
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas, NavigationToolbar2WxAgg as NavigationToolbar

from wolfhece.PyVertexvectors import Zones, vector, zone

from .PyCrosssections import profile
from .PyTranslate import _
from .PyVertex import getIfromRGB,getRGBfromI

class PlotPanel(wx.Panel):
    '''
    Un seul Panneau du notebook
    
    Plusieurs sizers : 
        - sizerfig (horizontal) avec la figure en premier élément --> l'ajout se place à droite
        - sizer    (vertical) avec comme éléments sizerfig et la barre d'outils Matplotlib --> l'ajout se place en dessous
    '''

    figure:mplfig.Figure

    def __init__(self, parent, id=-1, dpi=None,toolbar=True, **kwargs):
        super().__init__(parent, id=id, **kwargs)
        self.figure = mplfig.Figure(dpi=dpi, figsize=(2,2))    #Création d'une figure Matplotlib

        self.canvas = FigureCanvas(self, -1, self.figure)       #Création d'un Canvas wx pour contenir le dessin de la figure Matplotlib

        self.sizerfig = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        self.sizer = wx.BoxSizer(wx.VERTICAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre

        self.sizerfig.Add(self.canvas, 1, wx.EXPAND)                    #ajout du canvas
        self.sizer.Add(self.sizerfig, 1, wx.EXPAND)                    #ajout du canvas

        if toolbar:
            self.toolbar = NavigationToolbar(self.canvas)           #Ajout d'une barre d'outils pour la figure courante
            self.toolbar.Realize()
            self.sizer.Add(self.toolbar, 0, wx.LEFT| wx.EXPAND)         #ajout de la barre
            
        self.SetSizer(self.sizer)                                    #application du sizer

        self.myax=None
    
    def add_ax(self,ax3d=False):
        if ax3d:
            if self.myax is None:
                self.myax = self.figure.add_subplot(projection='3d')
        else:
            if self.myax is None:
                self.myax = self.figure.add_subplot()
        return self.myax

    def get_fig_ax(self,ax3d=False):
        self.myax = self.add_ax(ax3d)
        return self.figure,self.myax

class PlotCS(PlotPanel):
    '''
    Panels de traçage des sections en travers
    @author Pierre Archambeau
    '''
    
    def __init__(self, parent, id=-1, dpi=None, mycs=None, **kwargs):
        
        super().__init__(parent, id, dpi, **kwargs)
        
        self.mycs:profile
        self.mycs = mycs
        self.ls = None
        self.length = 100.

        self.second_fig = None
        self.second_ax = None
        
        self.sizernextprev = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        self.sizerposbank = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        # self.sizerposbankbut = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        
        self.sizer.Add(self.sizernextprev,0,wx.EXPAND)
        self.sizer.Add(self.sizerposbank,0,wx.EXPAND)
        # self.sizer.Add(self.sizerposbankbut,0,wx.EXPAND)

        self.ButPrev = wx.Button(self,label=_("Previous"))
        self.ButNext = wx.Button(self,label=_("Next"))

        curs=5000
        self.slidergenhor = wx.Slider(self, wx.ID_ANY, curs, 0, 10000, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='sliderhor' )
        self.slidergenver = wx.Slider(self, wx.ID_ANY, curs, 0, 10000, wx.DefaultPosition, wx.DefaultSize, wx.SL_VERTICAL,name='sliderver' )
        self.sizer.Add(self.slidergenhor,0,wx.EXPAND)
        self.sizerfig.Add(self.slidergenver,0,wx.EXPAND)
        
        self.sizernextprev.Add(self.ButPrev,1,wx.LEFT| wx.EXPAND)
        self.sizernextprev.Add(self.ButNext,1,wx.LEFT| wx.EXPAND)
        
        self.sizerslider1 = wx.BoxSizer(wx.VERTICAL)
        curs = 0.
        self.sliderleft = wx.Slider(self, wx.ID_ANY, curs, 0, 10000, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='sliderleft' )
        self.txtleft = wx.TextCtrl( self, wx.ID_ANY, str(curs), wx.DefaultPosition, wx.DefaultSize, style=wx.TE_CENTER|wx.TE_PROCESS_ENTER,name='textleft' )
        self.sizerslider1.Add( self.sliderleft, 1, wx.EXPAND)
        self.sizerslider1.Add( self.txtleft, 0, wx.EXPAND)
        self.sizerposbank.Add(self.sizerslider1,1,wx.EXPAND)

        self.sizerslider2 = wx.BoxSizer(wx.VERTICAL)
        curs = 0.
        self.sliderbed = wx.Slider(self, wx.ID_ANY, curs, 0, 10000, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='sliderbed' )
        self.txtbed = wx.TextCtrl( self, wx.ID_ANY, str(curs), wx.DefaultPosition, wx.DefaultSize, style=wx.TE_CENTER|wx.TE_PROCESS_ENTER,name='textbed' )
        self.sizerslider2.Add( self.sliderbed, 1, wx.EXPAND)
        self.sizerslider2.Add( self.txtbed, 0, wx.EXPAND)
        self.sizerposbank.Add(self.sizerslider2, 1, wx.EXPAND)
        
        self.sizerslider3 = wx.BoxSizer(wx.VERTICAL)
        curs = 0.
        self.sliderright = wx.Slider(self, wx.ID_ANY, curs, 0, 10000, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='sliderright' )
        self.txtright = wx.TextCtrl( self, wx.ID_ANY, str(curs), wx.DefaultPosition, wx.DefaultSize, style=wx.TE_CENTER|wx.TE_PROCESS_ENTER,name='textright' )
        self.sizerslider3.Add( self.sliderright, 1, wx.EXPAND)
        self.sizerslider3.Add( self.txtright, 0, wx.EXPAND)
        self.sizerposbank.Add(self.sizerslider3, 1, wx.EXPAND)
        
        self.txtbed.Bind(wx.EVT_TEXT_ENTER,self.movebanksslider)
        self.txtleft.Bind(wx.EVT_TEXT_ENTER,self.movebanksslider)
        self.txtright.Bind(wx.EVT_TEXT_ENTER,self.movebanksslider)

        self.sliderleft.Bind(wx.EVT_SLIDER,self.movebanksslider)
        self.sliderbed.Bind(wx.EVT_SLIDER,self.movebanksslider)
        self.sliderright.Bind(wx.EVT_SLIDER,self.movebanksslider)

        self.slidergenhor.Bind(wx.EVT_SLIDER,self.movegenslider)
        self.slidergenver.Bind(wx.EVT_SLIDER,self.movegenslider)
        
        self.ButPrev.Bind(wx.EVT_BUTTON,self.plot_up)
        self.ButNext.Bind(wx.EVT_BUTTON,self.plot_down)

    def set_cs(self,mycs:profile):
        
        self.mycs=mycs
        self.ls = self.mycs.asshapely_ls()
        self.length = self.ls.length

        if self.mycs.bankleft is not None:
            curs = self.ls.project(self.mycs.bankleft.as_shapelypoint())
            self.sliderleft.SetValue(curs)
            self.txtleft.SetLabelText(str(curs))

        if self.mycs.bed is not None:
            curs = self.ls.project(self.mycs.bed.as_shapelypoint())
            self.sliderbed.SetValue(curs)
            self.txtbed.SetLabelText(str(curs))
        
        if self.mycs.bankright is not None:
            curs = self.ls.project(self.mycs.bankright.as_shapelypoint())
        self.sliderright.SetValue(curs)
        self.txtright.SetLabelText(str(curs))

    def movegenslider(self,event):
        if self.mycs is None:
            return
        
        id = event.GetEventObject().GetName()
        cs:profile = self.mycs

        if id=='sliderhor':
            cs.sdatum = float(self.slidergenhor.Value-5000)/10000.*self.length
            cs.add_sdatum=True
        elif id=='sliderver':
            cs.zdatum = -float(self.slidergenver.Value-5000)/1000.
            cs.add_zdatum=True
            
        self.plot_cs()
        self.ls=self.mycs.asshapely_ls()
        
    def movebanksslider(self,event:wx.Event):
        if self.mycs is None:
            return
        
        id = event.GetEventObject().GetName()
        cs:profile = self.mycs

        if id=='sliderleft':
            curs=float(self.sliderleft.Value)/10000.*self.length
            self.txtleft.SetValue("{0:.2f}".format(curs))
            cs.movebankbedslider('left',self.ls.interpolate(curs))
        elif id=='sliderright':
            curs=float(self.sliderright.Value)/10000.*self.length
            self.txtright.SetValue("{0:.2f}".format(curs))
            cs.movebankbedslider('right',self.ls.interpolate(curs))
        elif id=='sliderbed':
            curs=float(self.sliderbed.Value)/10000.*self.length
            self.txtbed.SetValue("{0:.2f}".format(curs))
            cs.movebankbedslider('bed',self.ls.interpolate(curs))
        elif id=='textleft':
            curs=float(self.txtleft.Value)
            if curs<0.:
                self.txtleft.SetValue('0.')
                curs=0.
            elif curs>self.length:
                self.txtleft.SetValue(str(self.length))
                curs=self.length
            curslider = int(curs/self.length*10000.)
            self.sliderleft.SetValue(curslider)
            cs.movebankbedslider('left',self.ls.interpolate(curs))
        elif id=='textright':
            curs=float(self.txtright.Value)
            if curs<0.:
                self.txtright.SetValue('0.')
                curs=0.
            elif curs>self.length:
                curs=self.length
                self.txtright.SetValue(str(self.length))
            curslider = int(curs/self.length*10000.)
            self.sliderright.SetValue(curslider)
            cs.movebankbedslider('right',self.ls.interpolate(curs))
        elif id=='textbed':
            curs=float(self.txtbed.Value)
            if curs<0.:
                self.txtbed.SetValue('0.')
                curs=0.
            elif curs>self.length:
                self.txtbed.SetValue(str(self.length))
                curs=self.length
            curslider = int(curs/self.length*10000.)
            self.sliderbed.SetValue(curslider)
            cs.movebankbedslider('bed',self.ls.interpolate(curs))
        
        self.plot_cs()

    # def movebanks(self,event:wx.Event):
    #     if self.mycs is None:
    #         return
        
    #     '''Mouvement des berges'''
    #     id = event.GetEventObject().GetName()
        
    #     cs:profile = self.mycs
        
    #     if id=="BLLeft":
    #         cs.movebankbed('left','left')
    #     elif id=="BLRight":
    #         cs.movebankbed('left','right')
    #     elif id=="BRLeft":
    #         cs.movebankbed('right','left')
    #     elif id=="BRRight":  
    #         cs.movebankbed('right','right')
    #     elif id=="BedLeft":
    #         cs.movebankbed('bed','left')
    #     elif id=="BedRight":  
    #         cs.movebankbed('bed','right')
            
    #     self.plot_cs()
    
    def plot_cs(self):
        cs:profile = self.mycs
        cs.plot_cs(fig=self.figure,ax=self.myax)
        if self.second_fig is not None:
            cs.plot_cs(fig=self.second_fig,ax=self.second_ax,forceaspect=False)
                            
    def plot_up(self,event):
        
        self.mycs:profile
        
        self.mycs.myprop.width=1
        self.mycs.myprop.color=0

        if self.mycs.up is not None:
            self.set_cs(self.mycs.up)
        
        self.plot_cs()
                
        self.mycs.myprop.width=2
        self.mycs.myprop.color=getIfromRGB([255,0,0])
    
    def plot_down(self,event):
        
        self.mycs.myprop.width=1
        self.mycs.myprop.color=0

        if self.mycs.down is not None:
            self.set_cs(self.mycs.down)
        
        self.plot_cs()
                
        self.mycs.myprop.width=2
        self.mycs.myprop.color=getIfromRGB([255,0,0])

class ManagerInterp(PlotPanel):
    
    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        
        super().__init__(parent, id, dpi, **kwargs)
        
        self.active_zones = None
        self.active_zone = None
        self.active_vec = None
        self.active_cs = None

        self.parentGUI = None

        self.fig_3D = None
        self.ax_3D = None
        
        self.sizernextprev = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        self.sizerposbank = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        
        self.sizer.Add(self.sizernextprev,0,wx.EXPAND)
        self.sizer.Add(self.sizerposbank,0,wx.EXPAND)

        self.ButPrev = wx.Button(self,label=_("Previous"))
        self.ButNext = wx.Button(self,label=_("Next"))

        self.tftHBG = wx.Button(self,label=_("Transfer to HBG"))
        self.tftHBD = wx.Button(self,label=_("Transfer to HBD"))
        self.tftTHA = wx.Button(self,label=_("Transfer to THA"))
        self.tftGarbage = wx.Button(self,label=_("Transfer to Garbage"))
        self.correctz = wx.Button(self,label=_("Apply correction on Z elevation"))

        self.sizernextprev.Add(self.ButPrev,1,wx.LEFT| wx.EXPAND)
        self.sizernextprev.Add(self.ButNext,1,wx.LEFT| wx.EXPAND)

        self.sizerposbank.Add(self.correctz,1,wx.EXPAND)
        self.sizerposbank.Add(self.tftHBG,1,wx.EXPAND)
        self.sizerposbank.Add(self.tftTHA,1,wx.EXPAND)
        self.sizerposbank.Add(self.tftHBD,1,wx.EXPAND)
        self.sizerposbank.Add(self.tftGarbage,1,wx.EXPAND)

        self.ButPrev.Bind(wx.EVT_BUTTON,self.plot_up)
        self.ButNext.Bind(wx.EVT_BUTTON,self.plot_down)

        self.tftHBD.Bind(wx.EVT_BUTTON,self.hbd)
        self.tftHBG.Bind(wx.EVT_BUTTON,self.hbg)
        self.tftTHA.Bind(wx.EVT_BUTTON,self.tha)
        self.tftGarbage.Bind(wx.EVT_BUTTON,self.garbage)
        self.correctz.Bind(wx.EVT_BUTTON,self.corrz)

    def pointing(self,gui,aczones,aczone,accs):
        self.parentGUI=gui
        self.active_zones=aczones
        self.active_zone=aczone
        self.active_cs=accs

        self.curidx = 0
        self.active_vec = self.active_zone.myvectors[self.curidx]
        
        self.create_struct()

        for curcs in self.active_cs.myprofiles.values():
            curprof:profile
            curprof = curcs['cs']
            curprof.prepare_shapely()
            
        self.plot_curvec()
    
    def create_struct(self):
        zonename=['THA','HBG','HBD','Garbage']

        self.tft={}
        act_zones= [cur.myname for cur in self.active_zones.myzones]
        
        for curname in zonename:
            if not curname in act_zones:
                added_zone = zone(name=curname,parent=self.active_zones)
                self.active_zones.add_zone(added_zone)
                self.tft[curname]=added_zone
            else:
                self.tft[curname]=self.active_zones.myzones[act_zones.index(curname)]
                
        self.active_zones.fill_structure()
    
    def tft_vec(self,zonename):
        curzone:zone
        curzone=self.tft[zonename]
        curzone.add_vector(self.active_vec)
        self.active_vec.parentzone = curzone
        
        curzone=self.active_zone
        curzone.myvectors.pop(self.curidx)
        curzone.nbvectors-=1
        
        self.active_zones.fill_structure()
        
        self.uncolor_acvec()
        
        if curzone.nbvectors>0:
            self.active_vec=curzone.myvectors[min(curzone.nbvectors-1,self.curidx)]
            self.plot_curvec()
        pass

    def color_acvec(self):
        curvec:vector
        curvec=self.active_vec
        
        curvec.myprop.color = getIfromRGB([255,0,0])
        curvec.myprop.width = 3
        self.parentGUI.zoomon_activevector()

    def uncolor_acvec(self):
        curvec:vector
        curvec=self.active_vec
        
        curvec.myprop.color = self.oldcol
        curvec.myprop.width = self.oldwidth

    def plot_curvec(self):

        curvec:vector
        curvec=self.active_vec
        
        self.oldcol = curvec.myprop.color
        self.oldwidth = curvec.myprop.width
        
        self.color_acvec()

        s,z = curvec.get_sz()

        self.myax.clear()
        self.ax_3D.clear()
        
        self.myax.set_title(curvec.myname)
        self.myax.plot(s,z)
        
        xyz=curvec.asnparray3d()
        self.ax_3D.plot(xyz[:,0],xyz[:,1],xyz[:,2])

        curvec.prepare_shapely()

        self.sprof=[]
        self.zprof=[]
        self.name=[]

        for curcs in self.active_cs.myprofiles.values():
            curprof:profile
            curprof = curcs['cs']

            if curvec.linestring.intersects(curprof.linestring):
                inter = curvec.linestring.intersection(curprof.linestring)
                self.sprof.append(curvec.linestring.project(inter))
                self.zprof.append(curprof.interpolate(curprof.linestring.project(inter),is3D=False,adim=False).z)
                self.name.append(curprof.myname)
                                
                xyz=curprof.asnparray3d()
                self.ax_3D.plot(xyz[:,0],xyz[:,1],xyz[:,2])

        self.myax.scatter(self.sprof,self.zprof)

        for curx,cury,curname in zip(self.sprof,self.zprof,self.name):        
            self.myax.text(curx,cury+.5,curname)

        self.myax.set_ylim([np.min([np.min(z),np.min(self.zprof)])-5.,np.max([np.max(z),np.max(self.zprof)])+5.])
        self.myax.set_xlim([0.,np.max(s)])
        
        self.figure.canvas.draw()
        self.fig_3D.canvas.draw()

    def tha(self,event):
        self.tft_vec('THA')

    def hbg(self,event):
        self.tft_vec('HBG')

    def hbd(self,event):
        self.tft_vec('HBD')

    def garbage(self,event):
        self.tft_vec('Garbage')

    def corrz(self,event):

        ls = LineString(np.asarray([[s,z] for s,z in sorted(zip(self.sprof,self.zprof))]))

        curvec:vector
        curvec=self.active_vec
        s,z = self.active_vec.get_sz()
        
        decal = np.min(self.sprof)

        for i in range(curvec.nbvertices):
            newz = ls.interpolate(s[i]-decal).y
            curvec.myvertices[i].z=newz

        self.plot_curvec()

        pass

    def plot_up(self,event):
        self.curidx-=1
        self.curidx=max(0,self.curidx)

        self.uncolor_acvec()

        if self.active_zone.nbvectors==0:
            return
        
        self.active_vec = self.active_zone.myvectors[self.curidx]
        self.plot_curvec()

        pass

    def plot_down(self,event):
        self.curidx+=1
        self.curidx=min(self.curidx,self.active_zone.nbvectors-1)

        self.uncolor_acvec()

        if self.active_zone.nbvectors==0:
            return

        self.active_vec = self.active_zone.myvectors[self.curidx]
        self.plot_curvec()
        pass

class PlotNotebook(wx.Panel):
    '''
    Fenêtre contenant potentiellement plusieurs graphiques Matplotlib
    '''
    
    def __init__(self, parent = None, id=-1,show=True,framesize=(1024,768)):
        '''Initialisation
         Si un parent est fourni, on l'attache, sinon on crée une fenêtre indépendante
        '''
        if parent is None:
            self.frame = wx.Frame(None, -1, 'Plotter',size=framesize)
            super().__init__(self.frame, id=id)
        else:
            self.frame=parent
            super().__init__(parent, id=id)

        self.ntb = aui.AuiNotebook(self)    #ajout du notebook 
        sizer = wx.BoxSizer()               #sizer pour servir de contenant au notebook
        sizer.Add(self.ntb, 1, wx.EXPAND)   #ajout du notebook au sizer et demande d'étendre l'objet en cas de redimensionnement
        self.SetSizer(sizer)                #applique le sizer
        if show:
            self.frame.Show()
            
        self.Bind(wx.EVT_CLOSE , self.OnClose)

    def OnClose(self):
        self.Hide()

    def add(self, name="plot",which=""):
        '''
        Ajout d'un onglet au notebook
        L'onglet contient une Figure Matplotlib
        On retourne la figure du nouvel onglet
        '''
        
        if which=="":
            page = PlotPanel(self.ntb)               #crée un objet Plot
            self.ntb.AddPage(page, name)        #ajout de l'objet Plot au notebook
        elif which=="CS":
            page = PlotCS(self.ntb)               #crée un objet Plot
            page2 = PlotPanel(self.ntb)               #crée un objet Plot
            self.ntb.AddPage(page, name)        #ajout de l'objet Plot au notebook
            self.ntb.AddPage(page2, name+' expand')        #ajout de l'objet Plot au notebook
            
            ax=page.add_ax()
            ax2=page2.add_ax()
            
            page.second_fig = page2.figure
            page.second_ax = ax2
        
        elif which=="ManagerInterp":
            page = ManagerInterp(self.ntb)               #crée un objet Plot
            page2 = PlotPanel(self.ntb)               #crée un objet Plot
            self.ntb.AddPage(page, name)        #ajout de l'objet Plot au notebook
            self.ntb.AddPage(page2, name+' 3D')        #ajout de l'objet Plot au notebook
            
            ax=page.add_ax()
            ax2=page2.add_ax(True)
            
            page.fig_3D = page2.figure
            page.ax_3D = ax2
            
        return page                  

    def getfigure(self,index = -1, caption="") -> mplfig.Figure:
        if index!=-1:
            return self.ntb.GetPage(index).figure
        elif caption!="":
            for curpage in range(self.ntb.GetPageCount()):
                if caption==self.ntb.GetPageText(curpage):
                    return self.ntb.GetPage(curpage).figure
            return
        else:
            return

def demo():
    app = wx.App()
    # frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook()
    axes1 = plotter.add('figure 1').figure.add_subplot()
    axes1.plot([1, 2, 3], [2, 1, 4])
    # axes2 = plotter.add('figure 2').add_subplot()
    # axes2.plot([1, 2, 3, 4, 5], [2, 1, 4, 2, 3])

    fig=plotter.getfigure(0)
    fig.get_axes()[0].plot([5, 6, 10], [2, 1, 10])
    app.MainLoop()

if __name__ == "__main__":
    demo()