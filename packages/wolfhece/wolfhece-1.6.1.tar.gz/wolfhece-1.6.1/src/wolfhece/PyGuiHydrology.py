import wx

from .PyTranslate import _
from .PyDraw import WolfMapViewer
from .RatingCurve import *

class selectpoint(wx.Frame):
    
    def __init__(self, parent=None, title="Default Title", w=500,h=200, SPWstations:SPWMIGaugingStations = None, DCENNstations:SPWDCENNGaugingStations = None):
        wx.Frame.__init__(self, parent, title=title, size=(w,h),style=wx.DEFAULT_FRAME_STYLE)
        
        
        self.SPWMI = SPWstations
        self.SPWDCENN = DCENNstations
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerv = wx.BoxSizer(wx.VERTICAL)
        
        self.buttonOK = wx.Button(self,label="OK")
        self.buttonOK.Bind(wx.EVT_BUTTON,self.Apply)
        
        lblList = [_('Coordinates'), _('Code station'), _('River/Name')] 
        self.rbox = wx.RadioBox(self, label = 'Which', choices = lblList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS) 
        self.rbox.Bind(wx.EVT_RADIOBOX,self.onRadioBox)         
        
        self.tcoordx = wx.StaticText(self, label="X: ")    
        self.coordx = wx.TextCtrl(self, value=_("X coordinate"), size=(140,-1))
        self.tcoordy = wx.StaticText(self, label="Y: ")        
        self.coordy = wx.TextCtrl(self, value=_("Y coordinate"), size=(140,-1))        
        self.coords=[self.tcoordx,self.coordx,self.tcoordy,self.coordy]
        
        mycodes = [str(x) for x in SPWstations.mystations.keys()] + [str(x) for x in DCENNstations.mystations.keys()]

        myrivers =[*list(SPWstations.myrivers.keys()),*list(DCENNstations.myrivers.keys())]

        self.tcodestation = wx.StaticText(self, label=_("Code station: "))           
        self.codestation = wx.ComboBox(self, size=(95, -1), choices=mycodes, style=wx.CB_DROPDOWN) 
        self.codes=[self.tcodestation,self.codestation]

        self.triverstation = wx.StaticText(self, label=_("River: "))           
        self.riverstation = wx.ComboBox(self, size=(95, -1), choices=myrivers, style=wx.CB_DROPDOWN)     
        self.tnamestation = wx.StaticText(self, label=_("Station name: "))           
        self.namestation = wx.ComboBox(self, size=(95, -1), choices=[], style=wx.CB_DROPDOWN)     
        self.riverstation.Bind(wx.EVT_COMBOBOX,self.onComboRiver)    

        self.riversname=[self.triverstation,self.riverstation,self.tnamestation,self.namestation]
                
        self.sizerv.Add(self.rbox,0,wx.EXPAND)
        
        for curitem in self.coords:
            self.sizerv.Add(curitem,1,wx.EXPAND)
        for curitem in self.codes:
            self.sizerv.Add(curitem,1,wx.EXPAND)
            curitem.Hide()
        for curitem in self.riversname:
            self.sizerv.Add(curitem,1,wx.EXPAND)
            curitem.Hide()
        
        self.sizer.Add(self.sizerv,1,wx.EXPAND)
        self.sizer.Add(self.buttonOK,0,wx.EXPAND)
        
        #ajout du sizer à la page
        self.SetSizer(self.sizer)
        #self.SetSize(w,h)
        self.SetAutoLayout(1)

        #affichage de la page
        self.Show(True)
        
    def Apply(self):
        pass
    
    def onComboRiver(self,evt):
        str = self.riverstation.GetStringSelection()
        
        namestation=[]
        if str in self.SPWMI.myrivers.keys():
            namestation+=list(self.SPWMI.myrivers[str].keys())
        if str in self.SPWDCENN.myrivers.keys():
            namestation+=list(self.SPWDCENN.myrivers[str].keys())
        
        self.namestation.SetItems(namestation)
        
        pass
    
    def onRadioBox(self,evt):
        str = self.rbox.GetStringSelection()
        if str ==  _('Coordinates'):
            for curitem in self.coords:
                curitem.Show()
            for curitem in self.codes:
                curitem.Hide()
            for curitem in self.riversname:
                curitem.Hide()
        elif str ==   _('Code station'):
            for curitem in self.coords:
                curitem.Hide()
            for curitem in self.codes:
                curitem.Show()
            for curitem in self.riversname:
                curitem.Hide()
        elif str ==   _('River/Name'):
            for curitem in self.coords:
                curitem.Hide()
            for curitem in self.codes:
                curitem.Hide()
            for curitem in self.riversname:
                curitem.Show()

        self.sizerv.Layout()

class GuiHydrology(WolfMapViewer):

    def __init__(self, parent=None, title='MyForm',w=500,h=500):
        super(GuiHydrology, self).__init__(parent, title = title,w=w,h=h)
        
        self.parent=parent

        self.filemenu.Insert(0,1100,_('New from scratch'),_('Create a new simulation from scratch...'))
        
        self.toolsmenu = wx.Menu()
        self.toolsmenu.Append(1200,_('Forced exchanges'),_('Manage the forced exchanges...'))
        self.toolsmenu.Append(1201,_('Crop MNT/MNS'),_('Cropping data...'))
        self.toolsmenu.Append(1202,_('Crop land use (COSW)'),_('Cropping data...'))
        self.toolsmenu.Append(1205,_('Analyze slope'),_('Slope analyzer...'))
        self.toolsmenu.Append(1203,_('IRM - QDF'),_('Manage data...'))
        self.toolsmenu.Append(1204,_('SPW - Hydrometry'),_('Manage data...'))
        self.menubar.Append(self.toolsmenu,_('&Tools'))
        
        self.modelmenu = wx.Menu()
        paramgen = self.modelmenu.Append(1500,_('New'),_('Wizard !'))
        paramgen = self.modelmenu.Append(1501,_('Interior points'),_('Interior points'))
        paramgen = self.modelmenu.Append(1502,_('Topology'),_('Topology manager'))
        paramgen = self.modelmenu.Append(1503,_('Main model'),_('General parameters'))
        paramgen = self.modelmenu.Append(1504,_('Basin'),_('Basin parameters'))
        paramgen = self.modelmenu.Append(1505,_('Subbasins'),_('Sub-Basin parameters'))
        self.menubar.Append(self.modelmenu,_('&Model'))

        # self.computemenu = wx.Menu()
        # paramgen = self.computemenu.Append(1300,_('Calibration/Optimisation'),_('Parameters calibration of the model'))
        # paramgen = self.computemenu.Append(1301,_('Run'),_('Run simulation !'))
        # self.menubar.Append(self.computemenu,_('&Computation'))

        # self.resultsmenu = wx.Menu()
        # paramgen = self.resultsmenu.Append(1400,_('Assemble'),_('Run postprocessing !'))
        # paramgen = self.resultsmenu.Append(1401,_('Plot'),_('Plot'))
        # self.menubar.Append(self.resultsmenu,_('&Results'))
    
    def OnMenubar(self,event):

        super().OnMenubar(event)

        id = event.GetId()
        item = self.menubar.FindItemById(id)

        if id==wx.ID_EXECUTE :
            print(_('Do anything !!'))
        elif id==1503 :
            self.parent.mainparams.Show()
        elif id==1504 :
            self.parent.basinparams.Show()
        # elif id==1300:
        #     self.myoptimisation = Optimisation()  
        #     self.myoptimisation.Show()
        elif id==1500:
            myselect = selectpoint(title=_('Outlet'),SPWstations=self.parent.SPWstations,DCENNstations=self.parent.DCENNstations)
            myselect.Show()


