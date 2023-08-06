import os
import sys
from matplotlib.axis import Axis
import numpy as np
import numpy.ma as ma
import math as m
from OpenGL.GL  import *
import math
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
import re
import wx
from scipy.interpolate import interp2d,griddata
import pygltflib
import struct

from .PyVertex import getIfromRGB, getRGBfromI
from .PyTranslate import _
from .GraphNotebook import PlotPanel
from .CpGrid import CpGrid

try:
    from . import wolfogl
except:
    print('Error importing wolfogl.pyd')
    print('   Python version : ' + sys.version)
    print('   If your Python version is not 3.7.x or 3.9.x, you need to compile an adapted library with compile_wcython.py in wolfhece library path')
    print('   See comments in compile_wcython.py or launch *python compile_wcython.py build_ext --inplace* in :')
    print('      ' + os.path.dirname(__file__))
    exit()

from .xyz_file import XYZFile
from .PyPalette import wolfpalette
from .PyVertexvectors import Zones, vector,wolfvertex, zone

WOLF_ARRAY_HILLSHAPE        = -1
WOLF_ARRAY_FULL_SINGLE      = 1
WOLF_ARRAY_FULL_DOUBLE      = 2
WOLF_ARRAY_SYM_DOUBLE       = 8
WOLF_ARRAY_FULL_LOGICAL     = 4
WOLF_ARRAY_CSR_DOUBLE       = 5
WOLF_ARRAY_FULL_INTEGER     = 6
WOLF_ARRAY_FULL_SINGLE_3D   = 7
WOLF_ARRAY_FULL_INTEGER8    = 8

WOLF_ARRAY_MB_SINGLE        = 3
WOLF_ARRAY_MB_INTEGER       = 9

WOLF_ARRAY_FULL_INTEGER16   = 11
WOLF_ARRAY_MNAP_INTEGER     = 20

WOLF_ARRAY_MB = [WOLF_ARRAY_MB_SINGLE,WOLF_ARRAY_MB_INTEGER,WOLF_ARRAY_MNAP_INTEGER]

def getkeyblock(i,addone=True):
    if addone:
        return 'block'+str(i+1)
    else:
        return 'block'+str(i)

class header_wolf():
    
    def __init__(self) -> None:
        self.origx = 0.0
        self.origy = 0.0
        self.origz = 0.0
        
        self.translx = 0.0
        self.transly = 0.0
        self.translz = 0.0

        self.dx = 0.0
        self.dy = 0.0
        self.dz = 0.0
        
        self.nbx = 0
        self.nby = 0
        self.nbz = 0

        self.nb_blocks = 0
        self.head_blocks={}

class NewArray(wx.Dialog):
    def __init__( self, parent):
        super(NewArray, self).__init__(parent,title=_('New array'), size=(300, 300),style = wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.OK)

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        glsizer=self.CreateSeparatedButtonSizer(wx.OK)

        gSizer1 = wx.GridSizer( 6, 2, 0, 0 )
        
        glsizer.Insert(0,gSizer1)

        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"dX", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )

        gSizer1.Add( self.m_staticText9, 0, wx.ALL, 5 )

        self.dx = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, style=wx.TE_CENTER )
        gSizer1.Add( self.dx, 0, wx.ALL, 5 )

        self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"dY", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )

        gSizer1.Add( self.m_staticText10, 0, wx.ALL, 5 )

        self.dy = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        gSizer1.Add( self.dy, 0, wx.ALL, 5 )

        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"NbX", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )

        gSizer1.Add( self.m_staticText11, 0, wx.ALL, 5 )

        self.nbx = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        gSizer1.Add( self.nbx, 0, wx.ALL, 5 )

        self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"NbY", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )

        gSizer1.Add( self.m_staticText12, 0, wx.ALL, 5 )

        self.nby = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        gSizer1.Add( self.nby, 0, wx.ALL, 5 )

        self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"OrigX", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )

        gSizer1.Add( self.m_staticText13, 0, wx.ALL, 5 )

        self.ox = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        gSizer1.Add( self.ox, 0, wx.ALL, 5 )

        self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"OrigY", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )

        gSizer1.Add( self.m_staticText14, 0, wx.ALL, 5 )

        self.oy = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        gSizer1.Add( self.oy, 0, wx.ALL, 5 )

        # self.OK = wx.Button( self, wx.ID_ANY, u"Validate", wx.DefaultPosition, wx.DefaultSize, 0 )
        # gSizer1.Add( self.OK, 0, wx.ALL, 5 )

        self.nbx.SetFocus()
        self.nbx.SelectAll()
        self.SetSizer( glsizer )
        self.Layout()

        self.Centre( wx.BOTH )

class Ops_Array(wx.Frame):
    
    def __init__( self, wxparent, parentarray, parentGUI ):
        super(Ops_Array, self).__init__(wxparent,title=_('Operations'), size=(370, 450),style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)

        self.active_vector=None
        self.active_zone=None
        self.myzones = Zones(parent=self)
        self.myzonetmp=zone(name='tmp')
        self.vectmp=vector(name='tmp')
        self.fnsave=''
        
        self.myzonetmp.add_vector(self.vectmp)
        self.myzones.add_zone(self.myzonetmp)

        self.parentarray=parentarray
        self.parentGUI = parentGUI

        self.Bind(wx.EVT_CLOSE,self.onclose)

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.array_ops = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize )
        self.selection = wx.Panel( self.array_ops, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.array_ops.AddPage( self.selection, _("Selection"), True )

        self.operation = wx.Panel(self.array_ops, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.array_ops.AddPage( self.operation, _("Operations"), False )        
        
        self.Interpolation = wx.Panel( self.array_ops, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.array_ops.AddPage( self.Interpolation, _("Interpolation"), False )

        #PALETTE de couleurs
        self.Palette = PlotPanel(self.array_ops,wx.ID_ANY,toolbar=False)
        self.palgrid = CpGrid(self.Palette,wx.ID_ANY,style=wx.WANTS_CHARS|wx.TE_CENTER)
        self.palapply = wx.Button( self.Palette, wx.ID_ANY, _("Apply"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.palgrid.CreateGrid(16,4)
        self.palauto = wx.CheckBox( self.Palette, wx.ID_ANY, _("Automatic"), wx.DefaultPosition, wx.DefaultSize, style=wx.CHK_CHECKED )
        self.palalpha = wx.CheckBox( self.Palette, wx.ID_ANY, _("Opacity"), wx.DefaultPosition, wx.DefaultSize, style=wx.CHK_CHECKED )
        self.palshader = wx.CheckBox( self.Palette, wx.ID_ANY, _("Hillshade"), wx.DefaultPosition, wx.DefaultSize, style=wx.CHK_CHECKED )
        self.palalphaslider = wx.Slider(self.Palette, wx.ID_ANY, 100, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='palslider' )

        self.palalphahillshade = wx.Slider(self.Palette, wx.ID_ANY, 100, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='palalphaslider' )
        self.palazimuthhillshade = wx.Slider(self.Palette, wx.ID_ANY, 315, 0, 360, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='palazimuthslider' )
        self.palaltitudehillshade = wx.Slider(self.Palette, wx.ID_ANY, 0, 0, 90, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL,name='palaltitudeslider' )
        
        self.palsave= wx.Button( self.Palette, wx.ID_ANY, _("Save to file"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.palload= wx.Button( self.Palette, wx.ID_ANY, _("Load from file"), wx.DefaultPosition, wx.DefaultSize, 0 )
        
        if self.parentarray.mypal.automatic:
            self.palauto.SetValue(1)
        else:
            self.palauto.SetValue(0)

        self.palalpha.SetValue(1)

        self.palchoosecolor =wx.Button( self.Palette, wx.ID_ANY, _("Choose color for current value"), wx.DefaultPosition, wx.DefaultSize )        
        
        self.Palette.sizerfig.Add(self.palgrid,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palauto,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palalpha,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palalphaslider,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palshader,1, wx.EXPAND)

        self.Palette.sizer.Add(self.palalphahillshade,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palazimuthhillshade,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palaltitudehillshade,1, wx.EXPAND)
        
        self.Palette.sizer.Add(self.palchoosecolor,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palapply,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palload,1, wx.EXPAND)
        self.Palette.sizer.Add(self.palsave,1, wx.EXPAND)
        
        self.array_ops.AddPage( self.Palette, _("Palette"), False )

        #HISTOGRAMMES 
        self.histo = PlotPanel(self.array_ops,wx.ID_ANY,toolbar=True)
        self.histoupdate = wx.Button( self.histo, wx.ID_ANY, _("All data..."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.histoupdatezoom = wx.Button( self.histo, wx.ID_ANY, _("On zoom..."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.histoupdateerase = wx.Button( self.histo, wx.ID_ANY, _("Erase"), wx.DefaultPosition, wx.DefaultSize, 0 )

        self.histo.sizer.Add(self.histoupdate,0, wx.EXPAND)
        self.histo.sizer.Add(self.histoupdatezoom,0, wx.EXPAND)
        self.histo.sizer.Add(self.histoupdateerase,0, wx.EXPAND)

        self.array_ops.AddPage( self.histo, _("Histogram"), False )

        #LINKS
        self.links = wx.Panel( self.array_ops, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.array_ops.AddPage( self.links, _("Links"), False )
        
        #Interpolation
        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

        self.interp2D = wx.Button( self.Interpolation, wx.ID_ANY, _("Interp2D"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.interp2D, 0, wx.ALL, 5 )
        self.interp2D.Bind(wx.EVT_BUTTON,self.interpolation2D)

        self.m_button7 = wx.Button( self.Interpolation, wx.ID_ANY, _("MyButton"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_button7, 0, wx.ALL, 5 )

        self.m_button8 = wx.Button( self.Interpolation, wx.ID_ANY, _("MyButton"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_button8, 0, wx.ALL, 5 )

        self.m_button9 = wx.Button( self.Interpolation, wx.ID_ANY, _("MyButton"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.m_button9, 0, wx.ALL, 5 )

        self.Interpolation.SetSizer( gSizer1 )
        self.Interpolation.Layout()
        gSizer1.Fit( self.Interpolation )
  
        #Selection

        bSizer15 = wx.BoxSizer( wx.VERTICAL )

        bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer16 = wx.BoxSizer( wx.VERTICAL )

        selectmethodChoices = [ _("by clicks"), _("by vectors"), _("by temporary vector") ]
        self.selectmethod = wx.RadioBox( self.selection, wx.ID_ANY, _("How to select nodes?"), wx.DefaultPosition, wx.DefaultSize, selectmethodChoices, 1, wx.RA_SPECIFY_COLS )
        self.selectmethod.SetSelection( 2 )
        self.selectmethod.SetToolTip( _("Selection mode") )

        bSizer16.Add( self.selectmethod, 0, wx.ALL, 5 )

        self.LaunchSelection = wx.Button( self.selection, wx.ID_ANY, 
                                         _("Action !"), wx.DefaultPosition, 
                                         wx.DefaultSize, 0 )
        bSizer16.Add( self.LaunchSelection, 0, wx.EXPAND )
        self.AllSelection = wx.Button( self.selection, wx.ID_ANY, 
                                         _("Select all nodes"), wx.DefaultPosition, 
                                         wx.DefaultSize, 0 )
        bSizer16.Add( self.AllSelection, 0, wx.EXPAND )
        self.MoveSelection = wx.Button( self.selection, wx.ID_ANY, 
                                         _("Move current selection to..."), wx.DefaultPosition, 
                                         wx.DefaultSize, 0 )
        bSizer16.Add( self.MoveSelection, 0, wx.EXPAND)
        self.ResetSelection = wx.Button( self.selection, wx.ID_ANY, 
                                         _("Reset"), wx.DefaultPosition, 
                                         wx.DefaultSize, 0 )
        bSizer16.Add( self.ResetSelection, 0, wx.EXPAND )
        self.ResetAllSelection = wx.Button( self.selection, wx.ID_ANY, 
                                         _("Reset All"), wx.DefaultPosition, 
                                         wx.DefaultSize, 0 )
        bSizer16.Add( self.ResetAllSelection, 0, wx.EXPAND )


        bSizer21.Add( bSizer16, 1, wx.EXPAND, 5 )

        bSizer17 = wx.BoxSizer( wx.VERTICAL )

        self.m_button2 = wx.Button( self.selection, wx.ID_ANY, _("Manage vectors"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer17.Add( self.m_button2, 0, wx.EXPAND )

        self.active_vector_id = wx.StaticText( self.selection, wx.ID_ANY, _("Active vector"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.active_vector_id.Wrap( -1 )

        bSizer17.Add( self.active_vector_id, 0, wx.EXPAND )

        self.CurActiveparent = wx.StaticText( self.selection, wx.ID_ANY, _("Active parent"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.CurActiveparent.Wrap( -1 )

        bSizer17.Add( self.CurActiveparent, 0, wx.EXPAND )

        self.loadvec = wx.Button( self.selection, wx.ID_ANY, _("Read from file..."), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer17.Add( self.loadvec, 0, wx.EXPAND )

        self.saveas = wx.Button( self.selection, wx.ID_ANY, _("Save as..."), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer17.Add( self.saveas, 0, wx.EXPAND )

        self.save = wx.Button( self.selection, wx.ID_ANY, _("Save"), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer17.Add( self.save, 0, wx.EXPAND )


        bSizer21.Add( bSizer17, 1, wx.EXPAND, 5 )


        bSizer15.Add( bSizer21, 1, wx.EXPAND, 5 )

        bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

        self.nbselect = wx.StaticText( self.selection, wx.ID_ANY, _("nb"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.nbselect.Wrap( -1 )

        bSizer22.Add( self.nbselect, 0, wx.ALL, 10 )

        self.minx = wx.StaticText( self.selection, wx.ID_ANY, _("xmin"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.minx.Wrap( -1 )

        self.minx.SetToolTip( _("X Mininum") )

        bSizer22.Add( self.minx, 0, wx.ALL, 10 )

        self.maxx = wx.StaticText( self.selection, wx.ID_ANY, _("xmax"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.maxx.Wrap( -1 )

        self.maxx.SetToolTip( _("X Maximum") )

        bSizer22.Add( self.maxx, 0, wx.ALL, 10 )

        self.miny = wx.StaticText( self.selection, wx.ID_ANY, _("ymin"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.miny.Wrap( -1 )

        self.miny.SetToolTip( _("Y Minimum") )

        bSizer22.Add( self.miny, 0, wx.ALL, 10 )

        self.maxy = wx.StaticText( self.selection, wx.ID_ANY, _("ymax"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.maxy.Wrap( -1 )

        self.maxy.SetToolTip( _("Y Maximum") )

        bSizer22.Add( self.maxy, 0, wx.ALL, 10 )


        bSizer15.Add( bSizer22, 0, wx.EXPAND, 5 )


        self.selection.SetSizer( bSizer15 )
        self.selection.Layout()
        bSizer15.Fit( self.selection )
        
        #Operations
        sizeropgen = wx.BoxSizer( wx.VERTICAL )
        sepopcond = wx.BoxSizer( wx.HORIZONTAL )
        sizerop = wx.BoxSizer( wx.VERTICAL )
        sizercond = wx.BoxSizer( wx.VERTICAL )
        # bSizer26 = wx.BoxSizer( wx.VERTICAL )


        # bSizer14.Add( bSizer26, 1, wx.EXPAND, 5 )
        sepopcond.Add( sizercond, 1, wx.EXPAND )
        sepopcond.Add( sizerop, 1, wx.EXPAND )
        sizeropgen.Add( sepopcond, 1, wx.EXPAND )

        operationChoices = [ u"+", u"-", u"*", u"/", _("replace") ]
        self.choiceop = wx.RadioBox( self.operation, wx.ID_ANY, 
                                     _("Operation"), wx.DefaultPosition, 
                                     wx.DefaultSize, operationChoices, 1, wx.RA_SPECIFY_COLS )
        self.choiceop.SetSelection( 4 )
        sizerop.Add( self.choiceop, 1, wx.EXPAND )

        self.opvalue = wx.TextCtrl( self.operation, wx.ID_ANY, u"1", 
                                   wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        sizerop.Add( self.opvalue, 0, wx.EXPAND )

        conditionChoices = [ u"<", u"<=", u"=", u">=", u">",u"isNaN" ]
        self.condition = wx.RadioBox( self.operation, wx.ID_ANY, _("Condition"), wx.DefaultPosition, wx.DefaultSize, conditionChoices, 1, wx.RA_SPECIFY_COLS )
        self.condition.SetSelection( 2 )
        sizercond.Add( self.condition, 1, wx.EXPAND )

        self.condvalue = wx.TextCtrl( self.operation, wx.ID_ANY, u"0", 
                                     wx.DefaultPosition, wx.DefaultSize,style=wx.TE_CENTER )
        sizercond.Add( self.condvalue, 0, wx.EXPAND )

        self.ApplyOp = wx.Button( self.operation, wx.ID_ANY, _("Apply math operator"), wx.DefaultPosition, wx.DefaultSize, 0 )
        sizeropgen.Add( self.ApplyOp, 1, wx.EXPAND )

        self.SelectOp = wx.Button( self.operation, wx.ID_ANY, _("Apply selection condition"), wx.DefaultPosition, wx.DefaultSize, 0 )
        sizeropgen.Add( self.SelectOp, 1, wx.EXPAND )

        self.operation.SetSizer( sizeropgen )
        self.operation.Layout()
        sizeropgen.Fit( self.operation )

        gensizer = wx.BoxSizer( wx.VERTICAL )
        gensizer.Add( self.array_ops, 1, wx.EXPAND |wx.ALL )

        self.SetSizer( gensizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.LaunchSelection.Bind( wx.EVT_BUTTON, self.OnLaunchSelect )
        self.AllSelection.Bind( wx.EVT_BUTTON, self.OnAllSelect )
        self.MoveSelection.Bind( wx.EVT_BUTTON, self.OnMoveSelect )
        self.ResetSelection.Bind( wx.EVT_BUTTON, self.OnResetSelect )
        self.ResetAllSelection.Bind( wx.EVT_BUTTON, self.OnResetAllSelect )
        self.m_button2.Bind( wx.EVT_BUTTON, self.OnManageVectors )
        self.loadvec.Bind( wx.EVT_BUTTON, self.OnLoadvec )
        self.saveas.Bind( wx.EVT_BUTTON, self.OnSaveasvec )
        self.save.Bind( wx.EVT_BUTTON, self.OnSavevec )
        self.ApplyOp.Bind( wx.EVT_BUTTON, self.OnApplyOpMath )        
        self.SelectOp.Bind( wx.EVT_BUTTON, self.OnApplyOpSelect )     
        self.palapply.Bind(wx.EVT_BUTTON,self.Onupdatepal)  
        self.palsave.Bind(wx.EVT_BUTTON,self.Onsavepal)  
        self.palload.Bind(wx.EVT_BUTTON,self.Onloadpal)  
        self.palchoosecolor.Bind(wx.EVT_BUTTON,self.OnClickColorPal) 
        self.histoupdate.Bind(wx.EVT_BUTTON,self.OnClickHistoUpdate) 
        self.histoupdatezoom.Bind(wx.EVT_BUTTON,self.OnClickHistoUpdate) 
        self.histoupdateerase.Bind(wx.EVT_BUTTON,self.OnClickHistoUpdate) 
        
    def interpolation2D(self,event):
        self.parentarray.interpolation2D()
    
    def OnAllSelect(self,event):
        self.parentarray.mngselection.myselection = 'all'
    
    def OnMoveSelect(self,event):
        dlg = wx.TextEntryDialog(self,'Choose id','id?')
        ret=dlg.ShowModal()
        idtxt = dlg.GetValue()
        self.parentarray.mngselection.selections[idtxt]={}
        curdict=self.parentarray.mngselection.selections[idtxt]
        
        curdict['select']=self.parentarray.mngselection.myselection
        curdict['idgllist']=0
        self.parentarray.mngselection.myselection=[]
        self.parentarray.mngselection.update_nb_nodes_sections()
        
        dlg=wx.ColourDialog(self)
        ret=dlg.ShowModal()
        color=dlg.GetColourData()
        curdict['color']=color
    
    def OnResetSelect(self,event):
        self.parentarray.mngselection.myselection=[]
        self.nbselect.SetLabelText('0')

    def OnResetAllSelect(self,event):
        self.OnResetSelect(0)
        self.parentarray.mngselection.selections={}
    
    def OnApplyOpSelect(self,event):
        curcond = self.condition.GetSelection()
               
        curcondvalue = float(self.condvalue.GetValue())
        
        self.parentarray.mngselection.condition_select(curcond,curcondvalue)
    
    def OnApplyOpMath(self,event):
        
        curop = self.choiceop.GetSelection()
        curcond = self.condition.GetSelection()
        
        curopvalue = float(self.opvalue.GetValue())
        curcondvalue = float(self.condvalue.GetValue())
        
        self.parentarray.mngselection.treat_select(curop,curcond,curopvalue,curcondvalue)
        pass
    
    def OnManageVectors(self,event):
        if self.parentGUI.linked:
            if self.parentGUI.link_shareopsvect:
                if self.myzones.parentGUI in self.parentGUI.linkedList:
                    self.myzones.showstructure(self.myzones.parent,self.myzones.parentGUI)
                    return
                        
        self.myzones.showstructure(self,self.parentGUI)
    
    def OnLoadvec(self,event):
        dlg = wx.FileDialog(None,'Select file',wildcard='Vec file (*.vec)|*.vec|All (*.*)|*.*',style=wx.FD_OPEN)
        
        ret=dlg.ShowModal()
        if ret==wx.ID_CANCEL:
            return
        
        self.fnsave = dlg.GetPath()
        self.myzones=Zones(self.fnsave,parent=self)
        
        if self.parentGUI is not None:
            if self.parentGUI.linked:
                if not self.parentGUI.linkedList is None:
                    for curFrame in self.parentGUI.linkedList:
                        if curFrame.link_shareopsvect:
                            curFrame.active_array.myops.myzones = self.myzones
                            curFrame.active_array.myops.fnsave=self.fnsave
                 
    def OnSaveasvec(self,event):
        
        dlg = wx.FileDialog(None,'Select file',wildcard='Vec file (*.vec)|*.vec|All (*.*)|*.*',style=wx.FD_SAVE)
        
        ret=dlg.ShowModal()
        if ret==wx.ID_CANCEL:
            return
        
        self.fnsave = dlg.GetPath()
        
        self.myzones.saveas(self.fnsave)

        if self.parentGUI is not None:
            if self.parentGUI.linked:
                if not self.parentGUI.linkedList is None:
                    for curFrame in self.parentGUI.linkedList:
                        if curFrame.link_shareopsvect:
                            curFrame.active_array.myops.fnsave=self.fnsave

    def OnSavevec(self,event):
           
        if self.fnsave =='':
            return
        
        self.myzones.saveas(self.fnsave)
    
    def select_nod_by_node(self):
        if self.parentGUI is not None:
            self.parentGUI.action='select node by node'
            self.parentGUI.active_array=self.parentarray

    def select_vector_inside_manager(self):
        if self.active_vector is None:
            wx.MessageBox('Please select an active vector !')
            return

        if len(self.active_vector.myvertices)>2:
            self.parentarray.mngselection.select_insidepoly(self.active_vector)
            
        elif self.parentGUI is not None:
            if len(self.active_vector.myvertices)<3:
                wx.MessageBox('Please add points to vector by clicks !')

            self.parentGUI.action='select by vector'                
            self.parentGUI.active_array=self.parentarray

            firstvert=wolfvertex(0.,0.)
            self.vectmp.add_vertex(firstvert)

    def select_vector_tmp(self):
        if self.parentGUI is not None:
            self.parentGUI.action='select by tmp vector'
            self.vectmp.reset()
            self.Active_vector(self.vectmp)
            self.parentGUI.active_array=self.parentarray
            
            firstvert=wolfvertex(0.,0.)
            self.vectmp.add_vertex(firstvert)
            
    def OnLaunchSelect(self,event):
        id= self.selectmethod.GetSelection()
        
        if id==0:
            self.select_nod_by_node()
        elif id==1:
            self.select_vector_inside_manager()
        elif id==2:
            self.select_vector_tmp()
    
    def onclose(self,event):
        self.Hide()    
        
    def Active_vector(self,vect:vector,copyall=True):
        if vect is None:
            return
        self.active_vector = vect
        self.active_vector_id.SetLabelText(vect.myname)

        if vect.parentzone is not None:
            self.active_zone = vect.parentzone
        
        if self.parentGUI is not None and copyall:
            self.parentGUI.Active_vector(vect)

    def Active_zone(self,zone):
        self.active_zone = zone
        if self.parentGUI is not None:
            self.parentGUI.Active_zone(zone)

    def update_palette(self):
        self.Palette.add_ax()
        fig,ax = self.Palette.get_fig_ax()
        self.parentarray.mypal.plot(fig,ax)
        fig.canvas.draw()
        self.parentarray.mypal.fillgrid(self.palgrid)
    
    def Onsavepal(self,event):
        myarray:WolfArray
        myarray=self.parentarray
        myarray.mypal.savefile()
    
    def Onloadpal(self,event):
        myarray:WolfArray
        myarray=self.parentarray
        myarray.mypal.readfile()
    
    def Onupdatepal(self,event):
        curarray:WolfArray
        curarray = self.parentarray
                    
        auto = self.palauto.IsChecked()

        oldalpha = curarray.alpha
        if self.palalpha.IsChecked():
            curarray.alpha=1.
        else:
            curarray.alpha = float(self.palalphaslider.GetValue())/100.

        ret= curarray.mypal.updatefromgrid(self.palgrid)
        if curarray.mypal.automatic!= auto  or curarray.alpha!= oldalpha or ret:
            curarray.mypal.automatic=auto
            curarray.updatepalette(0)
            curarray.delete_lists()
            
        shadehill = self.palshader.IsChecked()
        if not curarray.shading and shadehill:
            curarray.shading = True
        
        azim = float(self.palazimuthhillshade.GetValue())
        alti = float(self.palaltitudehillshade.GetValue())
        
        if curarray.azimuthhill != azim:
            curarray.azimuthhill=azim
            curarray.shading=True
            
        if curarray.altitudehill != alti:
            curarray.altitudehill=alti
            curarray.shading=True
            
        alpha = float(self.palalphahillshade.GetValue())/100.
        if curarray.shaded.alpha != alpha:
            curarray.shaded.alpha = alpha
            curarray.shading=True
                
    def OnClickHistoUpdate(self,event:wx.Event):
        
        itemlabel=event.GetEventObject().GetLabel()
        fig,ax=self.histo.get_fig_ax()
        
        if itemlabel == self.histoupdateerase.LabelText:
            ax.clear()
            fig.canvas.draw()
            return
            
        myarray:WolfArray
        myarray=self.parentarray
        
        onzoom=[]
        if itemlabel == self.histoupdatezoom.LabelText:
            if self.parentGUI is not None:
                onzoom=[self.parentGUI.xmin,self.parentGUI.xmax,self.parentGUI.ymin,self.parentGUI.ymax]
                
        partarray = myarray.get_working_array(onzoom).flatten(order='F') #.sort(axis=-1)
      
        ax:Axis
        ax.hist(partarray,200,density=True)
        
        fig.canvas.draw()
        
    def OnClickColorPal(self,event):
        
        gridto = self.palgrid
        k=gridto.GetGridCursorRow()
        r=int(gridto.GetCellValue(k,1))
        g=int(gridto.GetCellValue(k,2))
        b=int(gridto.GetCellValue(k,3))

        curcol = wx.ColourData()
        curcol.SetChooseFull(True)
        curcol.SetColour(wx.Colour(r, g, b))

        dlg = wx.ColourDialog(None,curcol)
        ret = dlg.ShowModal()
        
        if ret == wx.ID_CANCEL:
            return

        curcol=dlg.GetColourData()
        rgb=curcol.GetColour()

        k=gridto.GetGridCursorRow()
        gridto.SetCellValue(k,1,str(rgb.red))
        gridto.SetCellValue(k,2,str(rgb.green))
        gridto.SetCellValue(k,3,str(rgb.blue))
    
class SelectionData():
    myselection:list
    selections:dict

    def __init__(self,parent) -> None:
        self.parent:WolfArray
        self.parent = parent

        self.dx = parent.dx
        self.dy = parent.dy

        self.myselection=[]
        self.selections={}
        self.update_plot_selection=True
        self.numlist_select=0
    
    def plot_selection(self):
        
        if self.myselection!='all':
            if len(self.myselection)>0 :
                self.numlist_select= self._plot_selection(self.myselection,(1.,0.,0.),self.numlist_select)

        if len(self.selections)>0:
            for cur in self.selections.values():
                if cur['select']!='all':
                    col=cur['color'].GetColour()
                    cur['idgllist']=self._plot_selection(cur['select'],
                                     (float(col[0])/255.,float(col[1])/255.,float(col[2])/255.),
                                     cur['idgllist'])

    def _plot_selection(self,curlist,color,loclist=0):
        
        if self.update_plot_selection:
            if loclist!=0:
                glDeleteLists(loclist,1)
            
            loclist = glGenLists(1)
            glNewList(loclist,GL_COMPILE)
 
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBegin(GL_QUADS)
            for cursel in curlist:
                x1=cursel[0]-self.dx/2.
                x2=cursel[0]+self.dx/2.
                y1=cursel[1]-self.dy/2.
                y2=cursel[1]+self.dy/2.
                glColor3f(color[0],color[1],color[2])
                glVertex2f(x1,y1)
                glVertex2f(x2,y1)
                glVertex2f(x2,y2)
                glVertex2f(x1,y2)
            glEnd()
            
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            for cursel in curlist:
                glBegin(GL_LINE_STRIP)
                x1=cursel[0]-self.dx/2.
                x2=cursel[0]+self.dx/2.
                y1=cursel[1]-self.dy/2.
                y2=cursel[1]+self.dy/2.
                glColor3f(0.,1.,0.)
                glVertex2f(x1,y1)
                glVertex2f(x2,y1)
                glVertex2f(x2,y2)
                glVertex2f(x1,y2)
                glVertex2f(x1,y1)
                glEnd()
            
            glEndList()
            self.update_plot_selection=False
        else:
            glCallList(loclist)

        return loclist

    def add_node_to_selection(self,x,y,verif=True):
        i,j = self.parent.get_ij_from_xy(x,y)
        x1,y1=self.parent.get_xy_from_ij(i,j)
        
        if verif:
            try:
                ret=self.myselection.index((x1,y1))
            except:
                ret=-1
            if  ret>=0 :
                self.myselection.pop(ret)
            else:
                self.myselection.append((x1,y1))
        else:
            self.myselection.append((x1,y1)) 

    def add_node_to_selectionij(self,i,j,verif=True):
        x1,y1=self.parent.get_xy_from_ij(i,j)        
        
        if verif:
            try:
                ret=self.myselection.index((x1,y1))
            except:
                ret=-1
            if  ret>=0 :
                self.myselection.pop(ret)
            else:
                self.myselection.append((x1,y1))
        else:
            self.myselection.append((x1,y1))  

    def select_insidepoly(self,myvect:vector):
        
        nbini = len(self.myselection)
        
        myvect.find_minmax()
        mypoints=self.parent.get_xy_infootprint_vect(myvect)
        polygon=np.asarray(list([vert.x,vert.y] for vert in myvect.myvertices))
        path = mpltPath.Path(polygon)
        inside = path.contains_points(mypoints)
        
        for x,y in mypoints[np.where(inside)]:
            self.add_node_to_selection(x,y,verif=nbini!=0)

        self.update_nb_nodes_sections()
        
    def update_nb_nodes_sections(self):
        self.update_plot_selection=True      
        self.parent.myops.nbselect.SetLabelText(str(len(self.myselection)))

    def condition_select(self,cond,condval):
        array=self.parent.array        
        if len(self.myselection)==0:
            if cond==0:
                #<
                ij=np.argwhere(array<condval)
            elif cond==1:
                #<=
                ij=np.argwhere(array<=condval)
            elif cond==2:
                #==
                ij=np.argwhere(array==condval)
            elif cond==3:
                #>=
                ij=np.argwhere(array>=condval)
            elif cond==4:
                #>
                ij=np.argwhere(array>condval)
            elif cond==5:
                #NaN
                ij=np.argwhere(np.isnan(array))
                
            for i,j in ij:
                self.add_node_to_selectionij(i,j,False)
        else:
            sel = np.asarray(self.myselection)
            ijall = np.asarray(self.parent.get_ij_from_xy(sel[:,0],sel[:,1])).transpose()

            if cond==0:
                #<
                ij = np.argwhere(array[ijall[:,0],ijall[:,1]]<condval)
            elif cond==1:
                #<=
                ij = np.argwhere(array[ijall[:,0],ijall[:,1]]<=condval)
            elif cond==2:
                #==
                ij = np.argwhere(array[ijall[:,0],ijall[:,1]]==condval)
            elif cond==3:
                #>=
                ij = np.argwhere(array[ijall[:,0],ijall[:,1]]>=condval)
            elif cond==4:
                #>
                ij = np.argwhere(array[ijall[:,0],ijall[:,1]]>condval)
            elif cond==5:
                #NaN
                ij=np.argwhere(np.isnan(array[ijall[:,0],ijall[:,1]]))
            
            ij=ij.flatten()
            for i,j in ijall[ij]:
                self.add_node_to_selectionij(i,j)
            
        self.update_nb_nodes_sections()
             
    def treat_select(self,op,cond,opval,condval):
        # operationChoices = [ u"+", u"-", u"*", u"/", u"replace'" ]
        # conditionChoices = [ u"<", u"<=", u"=", u">=", u">",u"isNaN" ]
        def test(val,cond,condval):
            if cond==0:
                return val<condval
            elif cond==1:
                return val<=condval
            elif cond==2:
                return val==condval
            elif cond==3:
                return val>=condval
            elif cond==4:
                return val>condval
            elif cond==5:
                return np.isnan(val)

        array=self.parent.array
        if self.myselection=='all':   
            if op==0:        
                if cond==0:
                    #<
                    array[np.where(array<condval)[0]]+=opval
                elif cond==1:
                    #<=
                    array[np.where(array<=condval)[0]]+=opval
                elif cond==2:
                    #==
                    array[np.where(array==condval)[0]]+=opval
                elif cond==3:
                    #>=
                    array[np.where(array>=condval)[0]]+=opval
                elif cond==4:
                    #>
                    array[np.where(array>condval)[0]]+=opval
                elif cond==5:
                    #NaN
                    array[np.where(np.isnan(array))[0]]+=opval
            elif op==1:        
                if cond==0:
                    #<
                    array[np.where(array<condval)[0]]-=opval
                elif cond==1:
                    #<=
                    array[np.where(array<=condval)[0]]-=opval
                elif cond==2:
                    #==
                    array[np.where(array==condval)[0]]-=opval
                elif cond==3:
                    #>=
                    array[np.where(array>=condval)[0]]-=opval
                elif cond==4:
                    #>
                    array[np.where(array>condval)[0]]-=opval
                elif cond==5:
                    #NaN
                    array[np.where(np.isnan(array))[0]]-=opval
            elif op==2:        
                if cond==0:
                    #<
                    array[np.where(array<condval)[0]]*=opval
                elif cond==1:
                    #<=
                    array[np.where(array<=condval)[0]]*=opval
                elif cond==2:
                    #==
                    array[np.where(array==condval)[0]]*=opval
                elif cond==3:
                    #>=
                    array[np.where(array>=condval)[0]]*=opval
                elif cond==4:
                    #>
                    array[np.where(array>condval)[0]]*=opval
                elif cond==5:
                    #NaN
                    array[np.where(np.isnan(array))[0]]*=opval
            elif op==3 and opval!=0.:        
                if cond==0:
                    #<
                    array[np.where(array<condval)[0]]/=opval
                elif cond==1:
                    #<=
                    array[np.where(array<=condval)[0]]/=opval
                elif cond==2:
                    #==
                    array[np.where(array==condval)[0]]/=opval
                elif cond==3:
                    #>=
                    array[np.where(array>=condval)[0]]/=opval
                elif cond==4:
                    #>
                    array[np.where(array>condval)[0]]/=opval
                elif cond==5:
                    #NaN
                    array[np.where(np.isnan(array))[0]]/=opval
            elif op==4:        
                if cond==0:
                    #<
                    array[np.where(array<condval)[0]]=opval
                elif cond==1:
                    #<=
                    array[np.where(array<=condval)[0]]=opval
                elif cond==2:
                    #==
                    array[np.where(array==condval)[0]]=opval
                elif cond==3:
                    #>=
                    array[np.where(array>=condval)[0]]=opval
                elif cond==4:
                    #>
                    array[np.where(array>condval)[0]]=opval
                elif cond==5:
                    #NaN
                    array[np.where(np.isnan(array))[0]]=opval
        else:
            ij = [self.parent.get_ij_from_xy(cur[0],cur[1]) for cur in self.myselection]        

            if op==0:        
                for i,j in ij:
                    if test(array.data[i,j],cond,condval):
                        array.data[i,j]+=opval
            elif op==1:        
                for i,j in ij:
                    if test(array.data[i,j],cond,condval):
                        array.data[i,j]-=opval
            elif op==2:        
                for i,j in ij:
                    if test(array.data[i,j],cond,condval):
                        array.data[i,j]*=opval
            elif op==3 and opval!=0.:        
                for i,j in ij:
                    if test(array.data[i,j],cond,condval):
                        array.data[i,j]/=opval
            elif op==4:        
                for i,j in ij:
                    if test(array.data[i,j],cond,condval):
                        array.data[i,j]=opval
        
        self.parent.updatepalette()
        self.parent.delete_lists()

    def get_values_sel(self):
        sel = np.asarray(self.myselection)
        if len(sel)==1:
            ijall = np.asarray(self.parent.get_ij_from_xy(sel[0,0],sel[0,1])).transpose()
            z = self.parent.array[ijall[0],ijall[1]]
        else:
            ijall = np.asarray(self.parent.get_ij_from_xy(sel[:,0],sel[:,1])).transpose()
            z = self.parent.array[ijall[:,0],ijall[:,1]].flatten()
        return z

# Objet Wolf Array en simple précision
class WolfArray(header_wolf):
    """ Classe pour l'importation de WOLF arrays"""
    array : ma.masked_array
    mygrid:dict
    idx:str

    myops:Ops_Array

    def __init__(self,fname = None,mold = None,masknull=True,crop=None,whichtype=WOLF_ARRAY_FULL_SINGLE,preload=True,create=False,parentgui=None):
        super().__init__()
        
        self.parentGUI=parentgui
        
        self.filename = ""
        self.nbdims = 2
        self.isblock=False
        self.blockindex=0
        self.wolftype = whichtype
        
        self.preload = preload
        self.loaded = False
        self.masknull=masknull
        
        self.rgb=None
        self.mypal = None
        self.alpha = 1.
        self.shading=False
        if self.wolftype!= WOLF_ARRAY_HILLSHAPE:
            self.shaded=WolfArray(whichtype=WOLF_ARRAY_HILLSHAPE)
            self.shaded.mypal.defaultgray()
            self.shaded.mypal.automatic=False
            self.azimuthhill=315.
            self.altitudehill=0.
    
        self.nullvalue = 0.
        self.nbnotnull = 99999
        self.nbnotnullzoom = 99999
        self.nbtoplot = 0

        self.gridsize=100
        self.gridmaxscales = -1
        
        self.plotted=False
        self.plotting=False

        self.mypal=wolfpalette(None,"Palette of colors")
        self.mypal.default16()
        self.mypal.automatic = True
        self.mygrid={}
        
        self.cropini=crop

        """ Constructeur d'un WOLF array """
        if fname is not None:
            self.filename = fname
            self.read_all()
            if masknull and self.preload:
                self.mask_data(0.)
        
        elif mold is not None:
            self.nbdims = mold.nbdims
            self.nbx = mold.nbx
            self.nby = mold.nby
            self.nbz = mold.nbz
            self.dx = mold.dx
            self.dy = mold.dy
            self.dz = mold.dz
            self.origx = mold.origx
            self.origy = mold.origy
            self.origz = mold.origz
            self.translx = mold.translx
            self.transly = mold.transly
            self.translz = mold.translz
            self.array = ma.copy(mold.array)
            #return

        elif create:
            new = NewArray(None)
            ret=new.ShowModal()
            if ret == wx.ID_CANCEL:
                return
            else:
                self.init_from_new(new)            

        self.myops=Ops_Array(None,self,self.parentGUI)
        self.myops.Hide()        

        self.mngselection = SelectionData(self)

    def interpolate_on_cloud(self,xy,z,method='linear'):
        '''
        See : https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
            
            method == nearest, linear or cubic
            
        '''

        x=np.arange(self.dx/2.,float(self.nbx)*self.dx+self.dx/2,self.dx)
        y=np.arange(self.dy/2.,float(self.nby)*self.dy+self.dy/2,self.dy)
        grid_x,grid_y = np.meshgrid(x,y,sparse=True,indexing='xy')
        
        newvalues = griddata(xy,z,(grid_x,grid_y), method=method,fill_value=-99999.).transpose()
        self.array.data[np.where(newvalues != -99999.)]=newvalues[np.where(newvalues != -99999.)]
        
        self.updatepalette()
        self.delete_lists()
    
    def import_from_gltf(self,fn='',fnpos=''):
        
        if fn=='' or fnpos=='':
            print(_('Retry !! -- Bad files'))
            return        

        gltf = pygltflib.GLTF2().load(fn)

        with open(fnpos,'r') as f:
            mylines=f.read().splitlines()

            ox=float(mylines[0])
            oy=float(mylines[1])

            nbx=int(mylines[2])
            nby=int(mylines[3])

            i1=int(mylines[4])
            j1=int(mylines[5])
            i2=int(mylines[6])
            j2=int(mylines[7])

            xmin=float(mylines[8])
            xmax=float(mylines[9])
            ymin=float(mylines[10])
            ymax=float(mylines[11])        

        # get the first mesh in the current scene 
        mesh = gltf.meshes[gltf.scenes[gltf.scene].nodes[0]]

        # get the vertices for each primitive in the mesh 
        for primitive in mesh.primitives:

            # get the binary data for this mesh primitive from the buffer
            accessor = gltf.accessors[primitive.attributes.POSITION]
            
            bufferView = gltf.bufferViews[accessor.bufferView]
            buffer = gltf.buffers[bufferView.buffer]
            data = gltf.get_data_from_buffer_uri(buffer.uri)

            # pull each vertex from the binary buffer and convert it into a tuple of python floats
            # vertices = []
            points=np.zeros([accessor.count,2],order='F',dtype=np.float64)
            values=np.zeros(accessor.count,order='F',dtype=np.float64)
            for i in range(accessor.count):
                index = bufferView.byteOffset + accessor.byteOffset + i*12  # the location in the buffer of this vertex
                d = data[index:index+12]  # the vertex data
                v = struct.unpack("<fff", d)   # convert from base64 to three floats
                
                points[i,:]=[v[0],-v[2]]
                values[i]=v[1]
                # vertices.append(v)

            # accessor = gltf.accessors[primitive.indices]

            # bufferView = gltf.bufferViews[accessor.bufferView]
            # buffer = gltf.buffers[bufferView.buffer]
            # data = gltf.get_data_from_buffer_uri(buffer.uri)

            # triangles = []
            # if accessor.componentType==pygltflib.UNSIGNED_SHORT:
            #     size=6
            #     format='<HHH'
            # elif accessor.componentType==pygltflib.UNSIGNED_INT:
            #     size=12
            #     format='<LLL'

            # for i in range(int(accessor.count/3)):
            #     index = bufferView.byteOffset + accessor.byteOffset + i*size  # the location in the buffer of this vertex
            #     d = data[index:index+size]  # the vertex data
            #     v = struct.unpack(format, d)   # convert from base64 to three floats
            #     triangles.append(v)
            
        x=np.arange(self.dx/2.,float(nbx)*self.dx+self.dx/2,self.dx)
        y=np.arange(self.dy/2.,float(nby)*self.dy+self.dy/2,self.dy)
        grid_x,grid_y = np.meshgrid(x,y,sparse=True,indexing='xy')
        
        newvalues = griddata(points,values,(grid_x,grid_y), method='linear')
        self.array.data[i1:i2,j1:j2]=newvalues.transpose()
        
        self.updatepalette()
        self.delete_lists()
    
    def export_to_gltf(self,bounds=None,fn=''):

        if bounds is None:
            ox=self.origx+self.translx
            oy=self.origy+self.transly
            nbx=self.nbx
            nby=self.nby
            
        else:
            ox=max(self.origx,bounds[0][0])
            oy=max(self.origy,bounds[1][0])

            i1,j1 = self.get_ij_from_xy(ox,oy)
            i2,j2 = self.get_ij_from_xy(bounds[0][1],bounds[1][1])
            
            i1=max(i1,0)
            j1=max(j1,0)
            i2=min(i2+1,self.nbx)
            j2=min(j2+1,self.nby)

            nbx=i2-i1
            nby=j2-j1
            
        x=np.arange(self.dx/2.,float(nbx)*self.dx+self.dx/2,self.dx)
        y=np.arange(self.dy/2.,float(nby)*self.dy+self.dy/2,self.dy)
        
        zmin=np.min(self.array[i1:i2,j1:j2])

        points = np.asarray([[xx,self.get_value(xx+ox,yy+oy,nullvalue=zmin),-yy]  for xx in x for yy in y],dtype=np.float32)

        decal=0
        triangles=[]
        triangles.append([ [i+decal,i+decal+1,i+decal+nby] for i in range(nby-1)])
        triangles.append([ [i+decal+nby,i+decal+1,i+decal+nby+1] for i in range(nby-1)])

        for k in range(1,nbx-1):
            decal=k*nby
            triangles.append([ [i+decal,i+decal+1,i+decal+nby] for i in range(nby-1)])
            triangles.append([ [i+decal+nby,i+decal+1,i+decal+nby+1] for i in range(nby-1)])
        triangles=np.asarray(triangles,dtype=np.uint32).reshape([(2*nby-2)*(nbx-1),3])

        triangles_binary_blob = triangles.flatten().tobytes()
        points_binary_blob = points.tobytes()
        
        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[0])],
            nodes=[pygltflib.Node(mesh=0)],
            meshes=[
                pygltflib.Mesh(
                    primitives=[
                        pygltflib.Primitive(
                            attributes=pygltflib.Attributes(POSITION=1), indices=0
                        )
                    ]
                )
            ],
            accessors=[
                pygltflib.Accessor(
                    bufferView=0,
                    componentType=pygltflib.UNSIGNED_INT,
                    count=triangles.size,
                    type=pygltflib.SCALAR,
                    max=[int(triangles.max())],
                    min=[int(triangles.min())],
                ),
                pygltflib.Accessor(
                    bufferView=1,
                    componentType=pygltflib.FLOAT,
                    count=len(points),
                    type=pygltflib.VEC3,
                    max=points.max(axis=0).tolist(),
                    min=points.min(axis=0).tolist(),
                ),
            ],
            bufferViews=[
                pygltflib.BufferView(
                    buffer=0,
                    byteLength=len(triangles_binary_blob),
                    target=pygltflib.ELEMENT_ARRAY_BUFFER,
                ),
                pygltflib.BufferView(
                    buffer=0,
                    byteOffset=len(triangles_binary_blob),
                    byteLength=len(points_binary_blob),
                    target=pygltflib.ARRAY_BUFFER,
                ),
            ],
            buffers=[
                pygltflib.Buffer(
                    byteLength=len(triangles_binary_blob) + len(points_binary_blob)
                )
            ],
        )
        gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)
        
        if fn=='':
            fn=self.filename.rpartition('.')[0]+'gltf'
        
        gltf.save(fn)    
        with open(fn+'.pos','w') as f:
            f.write(str(ox)+'\n')
            f.write(str(oy)+'\n')
            f.write(str(nbx)+'\n')
            f.write(str(nby)+'\n')
            f.write(str(i1)+'\n')
            f.write(str(j1)+'\n')
            f.write(str(i2)+'\n')
            f.write(str(j2)+'\n')
            f.write(str(bounds[0][0])+'\n')
            f.write(str(bounds[0][1])+'\n')
            f.write(str(bounds[1][0])+'\n')
            f.write(str(bounds[1][1]))
        
    def hillshade(self,azimuth,angle_altitude):
        azimuth = 360.0 - azimuth 
        
        x, y = np.gradient(self.array)
        slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
        aspect = np.arctan2(-x, y)
        azimuthrad = azimuth*np.pi/180.
        altituderad = angle_altitude*np.pi/180.
    
        shaded = np.sin(altituderad)*np.sin(slope) + np.cos(altituderad)*np.cos(slope)*np.cos((azimuthrad - np.pi/2.) - aspect)
        shaded+=1.
        shaded*=.5
        
        self.shaded.set_header(self.get_header())
        self.shaded.array = shaded
        self.shading=False
        self.shaded.delete_lists()

    def set_values_sel(self,xy,z):
        
        sel = np.asarray(xy)
        
        if len(sel)==1:
            ijall = np.asarray(self.get_ij_from_xy(sel[0,0],sel[0,1])).transpose()
            i=ijall[0]
            j=ijall[1]
            self.array[i,j]=z
        else:
            ijall = np.asarray(self.get_ij_from_xy(sel[:,0],sel[:,1])).transpose()
        
            for k in range(len(ijall)):
                i=ijall[k,0]
                j=ijall[k,1]
                self.array[i,j]=z[k]
        self.updatepalette()
        self.delete_lists()

    def init_from_new(self,dlg:NewArray):
        self.dx = float(dlg.dx.Value)
        self.dy = float(dlg.dy.Value)
        self.nbx = int(dlg.nbx.Value)
        self.nby = int(dlg.nby.Value)
        self.origx = float(dlg.ox.Value)
        self.origy = float(dlg.oy.Value)
        
        self.array = ma.MaskedArray(np.ones((self.nbx,self.nby),order='F',dtype=np.float32))
        
        pass
    
    def interpolation2D(self):
        
        if '1' in self.mngselection.selections.keys():
            curlist=self.mngselection.selections['1']['select']
            cursel=self.mngselection.myselection
            if len(curlist)>0:
                ij=[self.get_ij_from_xy(cur[0],cur[1]) for cur in curlist]
                z=[self.array.data[curij[0],curij[1]] for curij in ij]
                
                if cursel=='all':
                    xall = np.linspace(self.origx+self.dx/2.,self.origx+(float(self.nbx)-.5)*self.dx,self.nbx)
                    yall = np.linspace(self.origy+self.dy/2.,self.origy+(float(self.nby)-.5)*self.dy,self.nby)
                    cursel=[(x,y) for x in xall for y in yall]

                z=griddata(curlist,z,cursel,fill_value=np.NaN)
                
                for cur,curz in zip(cursel,z):
                    if not np.isnan(curz):
                        i,j=self.get_ij_from_xy(cur[0],cur[1])
                        self.array.data[i,j]=curz

                self.updatepalette(0)
                self.delete_lists()        

    def copy_mask(self,source,forcenullvalue:False):
        
        if forcenullvalue:
            self.array[np.where(source.array.mask)]=self.nullvalue

        self.array.mask = source.array.mask
        self.nbnotnull = source.nbnotnull        
        
        self.updatepalette(0)
        self.delete_lists()

    def check_plot(self):
        self.plotted = True
        
        if not self.loaded and self.filename!='':
            self.read_data()
            if self.masknull:
                self.mask_data(0.)
                    
        self.loaded=True

        if self.rgb is None:
            self.updatepalette(0)
    
    def uncheck_plot(self,unload=True):
        self.plotted = False
        
        if unload and self.filename!='':
            dlg=wx.MessageDialog(None,_('Do you want to unload data? \n If YES, the data will be reloaded from file once checekd \n If not saved, modifications will be lost !!'),style=wx.YES_NO)
            ret=dlg.ShowModal()
            if ret==wx.ID_YES:
                self.delete_lists()
                self.array=np.zeros([1])
                self.rgb=None
                self.loaded=False
                return

        dlg=wx.MessageDialog(None,_('Do you want to reset OpenGL lists?'),style=wx.YES_NO)
        ret=dlg.ShowModal()
        if ret==wx.ID_YES:
            self.delete_lists()
            self.rgb=None
    
    def get_header(self,abs=True) -> header_wolf():
        curhead=header_wolf()

        curhead.origx = self.origx
        curhead.origy = self.origy
        curhead.origz = self.origz

        curhead.dx = self.dx
        curhead.dy = self.dy
        curhead.dz = self.dz

        curhead.nbx = self.nbx
        curhead.nby = self.nby
        curhead.nbz = self.nbz

        curhead.translx = self.translx
        curhead.transly = self.transly
        curhead.translz = self.translz
        
        curhead.nb_blocks = self.nb_blocks

        if abs:
            curhead.origx+=curhead.translx
            curhead.origy+=curhead.transly
            curhead.origz+=curhead.translz
            
            curhead.translx=0.
            curhead.transly=0.
            curhead.translz=0.
        return curhead
                
    def set_header(self,header:header_wolf):
        self.origx = header.origx
        self.origy = header.origy
        self.origz = header.origz
        
        self.translx = header.translx
        self.transly = header.transly
        self.translz = header.translz

        self.dx = header.dx
        self.dy = header.dy
        self.dz = header.dz
        
        self.nbx = header.nbx
        self.nby = header.nby
        self.nbz = header.nbz

        self.nb_blocks = header.nb_blocks
        self.head_blocks=header.head_blocks.copy()

    def __add__(self, other):
        """Surcharge de l'opérateur d'addition"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        if type(other)==float:
            if other !=0.:
                newArray.array=np.ma.masked_array(self.array + other,self.array.mask)
        else:
            newArray.array = np.ma.masked_array(self.array + other.array,self.array.mask)
        return newArray
    
    def __mul__(self, other):
        """Surcharge de l'opérateur d'addition"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        if type(other)==float:
            if other !=0.:
                newArray.array=np.ma.masked_array(self.array * other,self.array.mask)
        else:
            newArray.array = np.ma.masked_array(self.array * other.array,self.array.mask)
        return newArray    

    def __sub__(self, other):
        """Surcharge de l'opérateur de soustraction"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        if type(other)==float:
            if other !=0.:
                newArray.array=np.ma.masked_array(self.array - other,self.array.mask)
        else:
            newArray.array = np.ma.masked_array(self.array - other.array,self.array.mask)
        return newArray

    def __pow__(self, other):
        """Surcharge de l'opérateur puissance"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        newArray.array = np.ma.masked_array(self.array**other,self.array.mask)
        return newArray

    def __truediv__(self, other):
        """Surcharge de l'opérateur puissance"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        if type(other)==float:
            if other !=0.:
                newArray.array=np.ma.masked_array(self.array/other,self.array.mask)
        else:
            newArray.array=np.ma.masked_array(np.where(other==0.,0.,self.array/other.array),self.array.mask)
        
        return newArray

    def get_xy_infootprint_vect(self,myvect:vector) -> np.ndarray:
        i1,j1=self.get_ij_from_xy(myvect.minx,myvect.miny)
        i2,j2=self.get_ij_from_xy(myvect.maxx,myvect.maxy)
        mypts=np.zeros(((i2-i1+1)*(j2-j1+1),2))
        k=0
        for j in range(j1,j2+1): 
            for i in range(i1,i2+1):
                x,y=self.get_xy_from_ij(i,j)
                mypts[k]=[x,y]
                k+=1
        return mypts
    
    def reset(self):
        if self.nbdims==2:
            self.array[:,:] = 0.0
        elif self.nbdims==3:
            self.array[:,:,:] = 0.0

    def allocate_ressources(self):
        if self.nbdims==2:
            self.array = ma.ones([self.nbx,self.nby]) 
        elif self.nbdims==3:
            self.array = ma.ones([self.nbx,self.nby,self.nbz]) 

    def read_all(self):
        """ Lecture d'un Wolf aray depuis le nom de fichier """
        self.read_txt_header()
        if self.preload:
            self.read_data()
            self.loaded=True
        return

    def write_all(self):
        """ Ecriture de tous les fichiers d'un Wolf array """
        self.write_txt_header()
        self.write_array()
        
    def rebin(self, factor, operation='mean'):
        """ Adaptation de la résolution"""
        operation = operation.lower()
        if not operation in ['sum', 'mean']:
            raise ValueError("Operation not supported.")
        
        self.nbx = int(self.nbx/factor)
        self.nby = int(self.nby/factor)
        self.dx = self.dx*float(factor)
        self.dy = self.dy*float(factor)
        new_shape=(self.nbx,self.nby)
        
        compression_pairs = [(d, c//d) for d,c in zip(new_shape,
                                                    self.array.shape)]
        flattened = [l for p in compression_pairs for l in p]
        self.array = self.array.reshape(flattened)
        for i in range(len(new_shape)):
            op = getattr(self.array, operation)
            self.array = np.float32(op(-1*(i+1)))

    def read_txt_header(self):
        """ Lecture du header .txt """
        if self.filename.endswith('.flt'):
            #Fichier .flt
            f = open(self.filename[:-4] + '.hdr', 'r')
            lines = f.read().splitlines()
            f.close()            
            
            tmp = lines[0].split(' ')
            self.nbx = int(tmp[-1])
            tmp = lines[1].split(' ')
            self.nby = int(tmp[-1])
            tmp = lines[2].split(' ')
            self.origx = float(tmp[-1])
            tmp = lines[3].split(' ')
            self.origy = float(tmp[-1])
            tmp = lines[4].split(' ')
            self.dx = self.dy = float(tmp[-1])
            pass
        else:
            with open(self.filename + '.txt', 'r') as f:
                lines = f.read().splitlines()

            tmp = lines[0].split(':')
            self.nbx = int(tmp[1])
            tmp = lines[1].split(':')
            self.nby = int(tmp[1])
            tmp = lines[2].split(':')
            self.origx = float(tmp[1])
            tmp = lines[3].split(':')
            self.origy = float(tmp[1])
            tmp = lines[4].split(':')
            self.dx = float(tmp[1])
            tmp = lines[5].split(':')
            self.dy = float(tmp[1])
            tmp = lines[6].split(':')
            self.wolftype = int(tmp[1])
            tmp = lines[7].split(':')
            self.translx = float(tmp[1])
            tmp = lines[8].split(':')
            self.transly = float(tmp[1])

            decal=9
            if self.wolftype==WOLF_ARRAY_FULL_SINGLE_3D:
                self.nbdims=3
                tmp = lines[9].split(':')
                self.nbz = int(tmp[1])
                tmp = lines[10].split(':')
                self.origz = float(tmp[1])
                tmp = lines[11].split(':')
                self.dz = float(tmp[1])
                tmp = lines[12].split(':')
                self.translz = float(tmp[1])
                decal=13
                
            if self.wolftype in WOLF_ARRAY_MB:
                tmp = lines[decal].split(':')
                self.nb_blocks = int(tmp[1])
                
                decal+=1
                for i in range(self.nb_blocks):
                    curhead = header_wolf()
                    tmp = lines[decal].split(':')
                    curhead.nbx = int(tmp[1])
                    tmp = lines[decal+1].split(':')
                    curhead.nby = int(tmp[1])
                    tmp = lines[decal+2].split(':')
                    curhead.origx = float(tmp[1])
                    tmp = lines[decal+3].split(':')
                    curhead.origy = float(tmp[1])
                    tmp = lines[decal+4].split(':')
                    curhead.dx = float(tmp[1])
                    tmp = lines[decal+5].split(':')
                    curhead.dy = float(tmp[1])
                    decal+=6
                    
                    curhead.translx = self.translx + self.origx
                    curhead.transly = self.transly + self.origy
                    
                    self.head_blocks[getkeyblock(i)]=curhead

    def write_txt_header(self):
        """ Ecriture de l'en-tête de Wolf array """
        f = open(self.filename + '.txt', 'w')
        f.write('NbX :\t{0}\n'.format(str(self.nbx)))
        f.write('NbY :\t{0}\n'.format(str(self.nby)))
        f.write('OrigX :\t{0}\n'.format(str(self.origx)))
        f.write('OrigY :\t{0}\n'.format(str(self.origy)))
        f.write('DX :\t{0}\n'.format(str(self.dx)))
        f.write('DY :\t{0}\n'.format(str(self.dy)))
        f.write('TypeEnregistrement :\t{0}\n'.format(str(self.wolftype)))
        f.write('TranslX :\t{0}\n'.format(str(self.translx)))
        f.write('TranslY :\t{0}\n'.format(str(self.transly)))
        if self.wolftype==WOLF_ARRAY_FULL_SINGLE_3D:
            f.write('NbZ :\t{0}\n'.format(str(self.nbz)))
            f.write('OrigZ :\t{0}\n'.format(str(self.origz)))
            f.write('DZ :\t{0}\n'.format(str(self.dz)))
            f.write('TranslZ :\t{0}\n'.format(str(self.translz)))

        if self.wolftype in WOLF_ARRAY_MB:
            f.write('Nb Blocs :\t{0}\n'.format(str(self.nb_blocks)))            
            for i in range(self.nb_blocks):
                curhead = self.head_blocks[getkeyblock(i)]
                f.write('NbX :\t{0}\n'.format(str(curhead.nbx)))
                f.write('NbY :\t{0}\n'.format(str(curhead.nby)))
                f.write('OrigX :\t{0}\n'.format(str(curhead.origx)))
                f.write('OrigY :\t{0}\n'.format(str(curhead.origy)))
                f.write('DX :\t{0}\n'.format(str(curhead.dx)))
                f.write('DY :\t{0}\n'.format(str(curhead.dy)))
                            
        f.close()

    def read_data(self):
        if self.cropini is None:            
            with open(self.filename, 'rb') as f:
                self._read_binary_data(f)
        else:                    
            with open(self.filename, 'rb') as f:
                if self.wolftype==1 or self.wolftype==7:
                    
                    imin,jmin = self.get_ij_from_xy(self.cropini[0][0],self.cropini[1][0]) 
                    imax,jmax = self.get_ij_from_xy(self.cropini[0][1],self.cropini[1][1])
                    
                    imin=int(imin)
                    jmin=int(jmin)
                    imax=int(imax)
                    jmax=int(jmax)
                    
                    oldnbx = self.nbx
                    oldnby = self.nby
                                    
                    self.nbx = imax-imin
                    self.nby = jmax-jmin
                    self.origx,self.origy = self.get_xy_from_ij(imin,jmin)
                    self.origx -=self.dx/2.
                    self.origy -=self.dy/2.
                    
                    locarray = np.zeros([self.nbx,self.nby])
                    
                    #on boucle sur les 'j'
                    nbi = imax-imin
                    if self.filename.endswith('.flt'):
                        f.seek(((oldnby-jmax)*oldnbx+imin)*4)
                    else:
                        f.seek((imin+jmin*oldnbx)*4)                    

                    for j in range(jmin,jmax):
                        locarray[0:imax-imin,j-jmin] = np.frombuffer(f.read(4*nbi),dtype=np.float32)                        
                        f.seek((oldnbx-nbi)*4,1)
                    
                    self.array = ma.masked_array(locarray, dtype=np.float32)

            if self.filename.endswith('.flt'):
                #fichier .flt --> miroir "horizontal"
                self.array = np.fliplr(self.array)

    def _read_binary_data(self,f,seek=0):
        
        if seek>0:
            f.seek(0)
        
        if self.wolftype==WOLF_ARRAY_FULL_SINGLE or self.wolftype==WOLF_ARRAY_FULL_SINGLE_3D:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*4), dtype=np.float32)
            self.array = ma.masked_array(locarray.copy(), dtype=np.float32)
        elif self.wolftype ==WOLF_ARRAY_FULL_DOUBLE:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*8), dtype=np.float64)
            self.array = ma.masked_array(locarray.copy(), dtype=np.float64)
        elif self.wolftype==WOLF_ARRAY_FULL_INTEGER:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*4), dtype=np.int32)
            self.array = ma.masked_array(locarray.copy(), dtype=np.int32)
        elif self.wolftype==WOLF_ARRAY_FULL_INTEGER16:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*2), dtype=np.int16)
            self.array = ma.masked_array(locarray.copy(), dtype=np.int16)

        if self.nbdims==2:
            self.array = self.array.reshape(self.nbx, self.nby, order='F')
        elif self.nbdims==3:
            self.array = self.array.reshape(self.nbx, self.nby, self.nbz, order='F')
                                    
    def write_array(self):
        """ Ecriture du tableau en binaire """
        self.array.data.transpose().tofile(self.filename, "")

    def write_xyz(self, fname):
        """ Ecriture d un fichier xyz avec toutes les données du Wolf Array """
        my_file = XYZFile(fname)
        my_file.fill_from_wolf_array(self)
        my_file.write_to_file()

    def get_xyz(self,which='all'):
        x1,y1 = self.get_xy_from_ij(0,0)
        x2,y2 = self.get_xy_from_ij(self.nbx,self.nby,aswolf=True)
        xloc=np.linspace(x1,x2,self.nbx)
        yloc=np.linspace(y1,y2,self.nby)
        xy=np.meshgrid(xloc,yloc,indexing='xy')
        
        xyz = np.column_stack([xy[0].flatten(),xy[1].flatten(),self.array.flatten()])
        
        filter = np.invert(ma.getmaskarray(self.array).flatten())
                
        return xyz[filter]

    def set_general_frame_from_xyz(self, fname, dx, dy):
        """ Lecture d'un fichier xyz et initialisation des données de base """
        my_file = XYZFile(fname)
        my_file.read_from_file()
        (xlim, ylim) = my_file.get_extent()

        self.dx = dx
        self.dy = dy
        self.origx = m.floor(xlim[0]) - 5.0*self.dx
        self.origy = m.floor(ylim[0]) - 5.0 * self.dy
        self.nbx = int((m.floor(xlim[1]) - m.ceil(xlim[0]))/self.dx) + 10
        self.nby = int((m.floor(ylim[1]) - m.ceil(ylim[0]))/self.dy) + 10

        self.array = np.zeros((self.nbx, self.nby))

    def mask_reset(self):
        if self.nbdims==2:
            self.array.mask = np.zeros((self.nbx,self.nby))
            self.nbnotnull = self.nbx * self.nby
        elif self.nbdims==3:
            self.array.mask = np.zeros((self.nbx,self.nby,self.nbz))
            self.nbnotnull = self.nbx * self.nby * self.nbz 

    def mask_data(self, value):
        self.array.mask = self.array.data == value
        #self.array = np.ma.masked_where(self.array == value, self.array)
        self.nbnotnull = self.array.count()

    def mask_allexceptdata(self, value):
        self.array.mask = self.array.data != value
        self.nbnotnull = self.array.count()

    def mask_invert(self):
        self.array.mask = not(self.array.mask)
        self.nbnotnull = self.array.count()

    def meshgrid(self,mode='gc'):
        x_start = self.translx + self.origx
        y_start = self.transly + self.origy
        if mode == 'gc':
            x_discr = np.linspace(x_start + self.dx / 2, x_start + self.nbx * self.dx - self.dx / 2, self.nbx)
            y_discr = np.linspace(y_start + self.dy / 2, y_start + self.nby * self.dy - self.dy / 2, self.nby)
        elif mode == 'borders':
            x_discr = np.linspace(x_start, x_start + self.nbx * self.dx , self.nbx+1)
            y_discr = np.linspace(y_start , y_start + self.nby * self.dy , self.nby+1)

        y, x = np.meshgrid(y_discr, x_discr)
        return x, y

    def crop(self,i_start,j_start,nbx,nby,k_start=1,nbz=1):
        newWolfArray = WolfArray()
        newWolfArray.nbx = nbx
        newWolfArray.nby = nby
        newWolfArray.dx = self.dx
        newWolfArray.dy = self.dy
        newWolfArray.origx = self.origx + i_start*self.dx
        newWolfArray.origy = self.origy + j_start * self.dy
        newWolfArray.translx = self.translx
        newWolfArray.transly = self.transly

        if self.nbdims ==3:
            newWolfArray.nbz = nbz
            newWolfArray.dz = self.dz
            newWolfArray.origz = self.origz + k_start*self.dz
            newWolfArray.translz = self.translz
            
            newWolfArray.array = self.array[i_start:i_start+nbx, j_start:j_start+nby, k_start:k_start+nbz]
        elif self.nbdims==2:
            newWolfArray.array = self.array[i_start:i_start+nbx, j_start:j_start+nby]
        
        return newWolfArray

    def extremum(self,which='min'):
        if which=='min':
            my_extr = np.amin(self.array)
        else:
            my_extr = np.amax(self.array)

        return my_extr
    
    def get_bounds(self,abs=True):
        if abs:
            return ([self.origx+self.translx, self.origx+self.translx + float(self.nbx)*self.dx],
                    [self.origy+self.transly, self.origy+self.transly + float(self.nby)*self.dy])
        else:
            return ([self.origx, self.origx + float(self.nbx)*self.dx],
                    [self.origy, self.origy + float(self.nby)*self.dy])

    def get_ij_from_xy(self,x,y,z=0.,scale=1.,aswolf=False,abs=True):

        locx = np.float64(x) - self.origx
        locy = np.float64(y) - self.origy
        locz = np.float64(z) - self.origz
        if abs:
            locx = locx -self.translx
            locy = locy -self.transly
            locz = locz -self.translz
            
        i = np.int32(locx / (self.dx*scale))
        j = np.int32(locy / (self.dy*scale))

        if aswolf:
            i+=1
            j+=1

        if self.nbdims==3:
            k = np.int32(locz / (self.dz*scale))
            if aswolf:
                k+=1
            return i, j, k # ATTENTION, Indices en numérotation Python --> WOLF ajouter +1
        elif self.nbdims==2:
            return i, j # ATTENTION, Indices en numérotation Python --> WOLF ajouter +1

    def get_xy_from_ij(self,i,j,k=0,scale=1.,aswolf=False,abs=True):
        
        i=np.int32(i)
        j=np.int32(j)

        if aswolf:
            i += -1
            j += -1

        if abs:
            x= (np.float64(i) + .5) * (self.dx*scale) + self.origx + self.translx
            y= (np.float64(j) + .5) * (self.dy*scale) + self.origy + self.transly
        else:
            x= (np.float64(i) + .5) * (self.dx*scale) + self.origx
            y= (np.float64(j) + .5) * (self.dy*scale) + self.origy

        if self.nbdims==3:
            k=np.int32(k)
            if aswolf:
                k += -1

            if abs:
                z= (np.float64(k) - .5) * (self.dz*scale) + self.origz + self.translz
            else:
                z= (np.float64(k) - .5) * (self.dz*scale) + self.origz
                
            return x,y,z
        
        elif self.nbdims==2:
            return x,y
        
    def get_value(self,x,y,z=0.,nullvalue=-99999):

        if self.nbdims==2:        
            i, j = self.get_ij_from_xy(x,y)
            if i>=0 and i<self.nbx and j>=0 and j<self.nby:
                if self.array.mask[i,j]:
                    value=nullvalue
                else:
                    value = self.array[i,j]                
            else:
                value = nullvalue
        elif self.nbdims==3:
            i, j, k = self.get_ij_from_xy(x,y,z)
            if i>=0 and i<self.nbx and j>=0 and j<self.nby and k>=0 and k<self.nbz:
                
                if self.array.mask[i,j,k]:
                    value=nullvalue
                else:
                    value = self.array[i,j,k]
            else:
                value = nullvalue

        return value

    def get_xlim(self,window_x,window_y):
        a_x = window_x / (self.nbx*self.dx)
        a_y = window_y / (self.nby*self.dy)
        if a_x < a_y :
            #C'est la mise à l'échelle selon x qui compte
            return (self.origx + self.translx, self.origx + self.translx + self.nbx * self.dx)
        else:
            #C'est la mise à l'échelle selon y qui compte
            l = (self.nby * self.dy) / window_y * window_x
            return (self.origx + self.translx + self.nbx * self.dx * 0.5 - l * 0.5,
                    self.origx + self.translx + self.nbx * self.dx * 0.5 + l * 0.5)

    def get_ylim(self,window_x,window_y):
        a_x = window_x / (self.nbx * self.dx)
        a_y = window_y / (self.nby * self.dy)
        if a_x < a_y:
            # C'est la mise à l'échelle selon x qui compte
            l = (self.nbx * self.dx) / window_x * window_y
            return (self.origy + self.transly + self.nby * self.dy * 0.5 - l * 0.5,
                    self.origy + self.transly + self.nby * self.dy * 0.5 + l * 0.5)
        else:
            # C'est la mise à l'échelle selon y qui compte
            return (self.origy + self.transly, self.origy + self.transly + self.nby * self.dy)

    def get_working_array(self,onzoom=[]):
        if onzoom!=[]:
            istart,jstart = self.get_ij_from_xy(onzoom[0],onzoom[2])
            iend,jend = self.get_ij_from_xy(onzoom[1],onzoom[3])
            
            istart= 0 if istart < 0 else istart
            jstart= 0 if jstart < 0 else jstart
            iend= self.nbx if iend > self.nbx else iend
            jend= self.nby if jend > self.nby else jend
            
            partarray=self.array[istart:iend,jstart:jend]
            self.nbnotnullzoom = partarray.count()
            return partarray[partarray.mask==False]
        else:
            return self.array[self.array.mask==False]
    
    def updatepalette(self,which=0,onzoom=[]):
        
        if self.mypal.automatic:        
            if onzoom!=[]:
                self.mypal.isopop(self.get_working_array(onzoom),self.nbnotnullzoom)
            else:
                self.mypal.isopop(self.get_working_array(),self.nbnotnull)
            
        self.rgb = self.mypal.get_rgba(self.array)
        self.myops.update_palette()

    def plot(self, sx=None, sy=None,xmin=None,ymin=None,xmax=None,ymax=None):
                
        if not self.plotted:
            return

        self.plotting=True

        if self.plotted and sx is None:
            sx=self.sx
            sy=self.sy
            xmin=self.xmin
            xmax=self.xmax
            ymin=self.ymin
            ymax=self.ymax
        else:
            self.sx=sx
            self.sy=sy
            self.xmin=xmin
            self.xmax=xmax
            self.ymin=ymin
            self.ymax=ymax

        nbpix=min(sx*self.dx,sy*self.dy)
        if nbpix>=1.:
            #si une maille est tracée sur au moins 2 pixels
            curscale=1
        elif math.ceil(1./nbpix)<=3:
            curscale = math.ceil(math.ceil(1./nbpix))
        else:
            curscale = math.ceil(math.ceil(1./nbpix)/3)*3

        curscale=max(curscale,1)
        cursize = curscale #2.**curscale
        curnbx = max(math.ceil(float(self.nbx)/(self.gridsize*cursize)),1)
        curnby = max(math.ceil(float(self.nby)/(self.gridsize*cursize)),1)

        if not cursize in self.mygrid.keys():
            self.mygrid[cursize]={}
            curlist=self.mygrid[cursize]
            curlist['nbx']=curnbx
            curlist['nby']=curnby
            print('réservation listes ')
            numlist = glGenLists(curnbx*curnby)
            curlist['firstlist']=numlist
            print(numlist)
            curlist['mylists']= np.linspace(numlist,numlist+curnbx*curnby-1,num=curnbx*curnby,dtype=np.integer).reshape((curnbx,curnby),order='F')
            curlist['done']=np.zeros((curnbx,curnby),dtype=np.integer,order='F')

        if(curnbx==1 and curnby==1):
            if(self.gridmaxscales==-1):
                self.gridmaxscales=curscale
            elif curscale>self.gridmaxscales:
                curscale=self.gridmaxscales
                cursize = curscale
                curnbx = max(math.ceil(float(self.nbx)/(self.gridsize*cursize)),1)
                curnby = max(math.ceil(float(self.nby)/(self.gridsize*cursize)),1)
            
        istart,jstart = self.get_ij_from_xy(xmin,ymin,scale=cursize*float(self.gridsize))
        iend,jend     = self.get_ij_from_xy(xmax,ymax,scale=cursize*float(self.gridsize))

        istart=max(0,istart)
        jstart=max(0,jstart)
        iend=min(curnbx-1,iend)
        jend=min(curnby-1,jend)

        if self.wolftype != WOLF_ARRAY_HILLSHAPE and self.shading:
            self.hillshade(self.azimuthhill,self.altitudehill)   
            self.shaded.updatepalette(0) 
            if self.parentGUI is not None:
                if not self.idx+'_hillshade' in self.parentGUI.added['arrays'].keys():
                    self.parentGUI.add_object('array',newobj=self.shaded,ToCheck=True,id=self.idx+'_hillshade')
        
        try:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

            for j in range(jstart,jend+1):
                for i in range(istart,iend+1):
                    self.fillonecellgrid(cursize,i,j)
                    try:
                        mylistdone = self.mygrid[cursize]['done'][i,j]
                        if mylistdone==1 :
                            mylist = self.mygrid[cursize]['mylists'][i,j]
                            if mylist>0:
                                glCallList(self.mygrid[cursize]['mylists'][i,j])                        
                    except:
                        pass

            glDisable(GL_BLEND)
        except:
            pass                        
        self.plotting=False
        self.mngselection.plot_selection()
        self.myops.myzones.plot()

    def delete_lists(self):
        for idx,cursize in enumerate(self.mygrid):
            curlist=self.mygrid[cursize]
            nbx=curlist['nbx']
            nby=curlist['nby']
            first=curlist['firstlist']
            glDeleteLists(first,nbx*nby)
            print(first,nbx*nby)

        self.mygrid={}
        self.gridmaxscales = -1

    def plot_matplotlib(self):

        self.mask_data(0.)
        self.updatepalette(0)

        fig = plt.figure()

        ax = fig.add_subplot(111)
        plt.imshow(self.array.transpose(),origin='lower',cmap=self.mypal,extent=(self.origx,self.origx+self.dx*self.nbx,self.origy,self.origy+self.dy*self.nby))
        ax.set_aspect('equal')

        plt.show()
                            
    def fillonecellgrid(self,curscale,loci,locj,force=False):

        cursize = curscale #2**curscale

        if not cursize in self.mygrid.keys():
            return

        curlist=self.mygrid[cursize]
        exists=curlist['done'][loci,locj]

        if exists==0 or force:
            #print('Computing OpenGL List for '+str(loci)+';' +str(locj) + ' on scale factor '+str(curscale))
            
            ox=self.origx+self.translx
            oy=self.origy+self.transly
            dx=self.dx
            dy=self.dy

            numlist = int(curlist['mylists'][loci,locj])
            #print(numlist)

            try:
                glNewList(numlist,GL_COMPILE)
                glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)      

                step=self.gridsize*cursize
                jstart = max(locj*step,0)
                jend = min(jstart+step,self.nby)
                istart = max(loci*step,0)
                iend = min(istart+step,self.nbx)
                
                try:
                    if self.wolftype!=WOLF_ARRAY_FULL_SINGLE:
                        if self.nbnotnull!=self.nbx*self.nby:
                            if self.nbnotnull>0:  
                                wolfogl.addme(self.array.astype(dtype=np.float32),self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue,self.alpha)
                        elif self.nbnotnull>0:
                            wolfogl.addmeall(self.array.astype(dtype=np.float32),self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue,self.alpha)
                    else:
                        if self.nbnotnull!=self.nbx*self.nby:
                            if self.nbnotnull>0:  
                                wolfogl.addme(self.array,self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue,self.alpha)
                        else:
                            wolfogl.addmeall(self.array,self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue,self.alpha)
                except:
                    pass
                glEndList()
            except:
                pass
            curlist['done'][loci,locj]=1
            
class WolfArrayMB(WolfArray):
    
    myblocks:dict
    
    def __init__(self, fname=None, mold=None, masknull=True, crop=None, whichtype=WOLF_ARRAY_MB_SINGLE, preload=True, create=False, parentgui=None):
        self.myblocks={}
        super().__init__(fname, mold, masknull, crop, whichtype, preload, create, parentgui)
        self.wolftype = WOLF_ARRAY_MB_SINGLE

    def check_plot(self):
        self.plotted = True
        self.mimic_plotdata()
        
        if not self.loaded and self.filename!='':
            self.read_data()
            if self.masknull:
                self.mask_data(0.)
            if self.rgb is None:
                self.rgb=np.ones((self.nbx,self.nby,4),order='F',dtype=np.integer)
            self.updatepalette(0)
            self.loaded=True
    
    def uncheck_plot(self,unload=True):
        self.plotted = False
        self.mimic_plotdata()
        
        if unload:
            for curblock in self.myblocks.values():
                curblock.uncheck_plot(unload)
            self.rgb = None
            self.myblocks={}
            self.loaded=False
        
    def mask_data(self, value):
        self.nbnotnull=0
        for i in range(self.nb_blocks):
            curblock=self.myblocks[getkeyblock(i)]
            curarray=curblock.array
            curarray.mask = curarray.data == value
            
            nbnotnull=curarray.count()
            curblock.nbnotnull = nbnotnull
            self.nbnotnull += nbnotnull
    
    def read_data(self):
                
        with open(self.filename, 'rb') as f:
            
            for i in range(self.nb_blocks):
                curblock = WolfArray(whichtype=WOLF_ARRAY_FULL_SINGLE)
                curblock.isblock=True
                curblock.blockindex = i
                curblock.set_header(self.head_blocks[getkeyblock(i)])
                curblock._read_binary_data(f)
                self.myblocks[getkeyblock(i)]=curblock                    

    def write_array(self):
        """ Ecriture du tableau en binaire """
        with open(self.filename,'wb') as f:
            for i in range(self.nb_blocks):
                curarray = self.myblocks[getkeyblock(i)]
                f.write(curarray.array.data.transpose().tobytes())

    def get_ij_from_xy(self, x, y, z=0, scale=1, aswolf=False,abs=True,which_block=1):
        return self.myblocks[getkeyblock(which_block,False)].get_ij_from_xy(x, y, z, scale, aswolf,abs)
    
    def get_values_as_wolf(self,i,j,which_block=1):

        keyblock=getkeyblock(which_block,False)
        curblock=self.myblocks[keyblock]
        
        nbx = curblock.nbx
        nby = curblock.nby

        if(i>0 and i<=nbx and j>0 and j<=nby):
            h = curblock.array[i-1,j-1]
        
        return h

    def get_value(self,x,y,abs=True):

        h = np.NaN
        for curblock in self.myblocks.values():
            curblock:WolfArray
            nbx = curblock.nbx
            nby = curblock.nby
            
            i,j=curblock.get_ij_from_xy(x,y,abs=abs)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                h = curblock.array[i,j]
                if not curblock.array.mask[i,j]:
                    break

        return h

    def get_xy_from_ij(self,i,j,which_block,aswolf=False,abs=True):
        x,y = self.myblocks[getkeyblock(which_block,False)].get_xy_from_ij(i,j,aswolf=aswolf,abs=abs)
        return x,y

    def get_blockij_from_xy(self,x,y,abs=True):

        exists=False
        k=1
        for curblock in self.myblocks.values():
            curblock:WolfArray
            nbx = curblock.nbx
            nby = curblock.nby
            
            i,j=curblock.get_ij_from_xy(x,y,abs=abs)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                if not curblock.array.mask[i,j]:
                    exists=True
                    break
            k+=1
        
        if exists:
            return i,j,k
        else:
            return -1,-1,-1

    def link_palette(self):
        for curblock in self.myblocks.values():
            curblock.mypal = self.mypal
    
    def updatepalette(self,which=0,onzoom=[]):
        
        if onzoom!=[]:
            allarrays=[]
            for curblock in self.myblocks.values():
                istart,jstart = curblock.get_ij_from_xy(onzoom[0],onzoom[2])
                iend,jend = curblock.get_ij_from_xy(onzoom[1],onzoom[3])
                
                istart= 0 if istart < 0 else istart
                jstart= 0 if jstart < 0 else jstart
                iend= curblock.nbx if iend > curblock.nbx else iend
                jend= curblock.nby if jend > curblock.nby else jend
                
                partarray=curblock.array[istart:iend,jstart:jend]
                partarray=partarray[partarray.mask==False]
                if len(partarray)>0:
                    allarrays.append(partarray.flatten())
            
            allarrays=np.concatenate(allarrays)            
            self.mypal.isopop(allarrays,allarrays.count())            
        else:
            allarrays = np.concatenate([curblock.array[curblock.array.mask==False].flatten() for curblock in self.myblocks.values()])
            self.mypal.isopop(allarrays,self.nbnotnull)
        
        self.link_palette()
        for curblock in self.myblocks.values():
            curblock.rgb = self.mypal.get_rgba(curblock.array)

    def delete_lists(self):
        for curblock in self.myblocks.values():
            curblock.delete_lists()

    def mimic_plotdata(self): 
        for curblock in self.myblocks.values():
            curblock:WolfArray
            curblock.plotted = self.plotted
            curblock.plotting = self.plotting
            
    def plot(self, sx=None, sy=None,xmin=None,ymin=None,xmax=None,ymax=None):
        
        self.plotting=True
        self.mimic_plotdata()
        
        for curblock in self.myblocks.values():
            curblock.plot(sx, sy,xmin,ymin,xmax,ymax)
        
        self.plotting=False
        self.mimic_plotdata()
            
    def fillonecellgrid(self,curscale,loci,locj,force=False):
        for curblock in self.myblocks.values():
                curblock.fillonecellgrid(curscale,loci,locj,force)
                
class WolfArrayMNAP(WolfArrayMB):
    
    contour:Zones
    
    def __init__(self, fname=None, mold=None, masknull=True, crop=None):
        super().__init__(fname, mold, masknull, crop)
        
        self.contour=Zones()
        
    def read_data(self):
        with open(self.filename+'.mnap') as f:
            lines=f.read().splitlines()
            
            self.nb_blocks=abs(int(lines[0]))
            self.contour= Zones()
            
            decal=1
            for i in range(self.nb_blocks):
                curkey = getkeyblock(i)
                curarray = WolfArray()
                self.myblocks[curkey]=curarray
                
                curarray.wolftype=WOLF_ARRAY_FULL_INTEGER8
                curarray.isblock=True
                curarray.blockindex = i
                
                tmp=re.sub('\\s+', ' ', lines[decal].strip()).split(' ')
                curarray.dx = float(tmp[0])
                curarray.dy = float(tmp[1])

                tmp=re.sub('\\s+', ' ', lines[decal+1].strip()).split(' ')
                curarray.origx = float(tmp[0])-self.origx

                tmp=re.sub('\\s+', ' ', lines[decal+2].strip()).split(' ')
                curarray.origy = float(tmp[0])-self.origy
                
                tmp=re.sub('\\s+', ' ', lines[decal+3].strip()).split(' ')
                curarray.nbx = int(tmp[0])
                curarray.nby = int(tmp[1])
                
                decal+=4
                myarray=[]
                
                for j in range(curarray.nby):
                    newline = [np.int32(curval) for curval in re.sub('\\s+', ' ',lines[decal].strip()).split()]
                    while len(newline) != curarray.nbx:
                        decal+=1
                        newline = np.concatenate([newline,[np.int32(curval) for curval in re.sub('\\s+', ' ',lines[decal].strip()).split()]])
                    myarray.append(newline)
                    decal+=1
                                
                curarray.array = np.flipud(np.ma.asarray(myarray,order='C'))                                                

                curzone=zone(name=curkey)
                contourblock = vector(name='contour')
                
                curzone.add_vector(contourblock)
                self.contour.add_zone(curzone)

                nbvert = int(lines[decal])
                for j in range(nbvert):
                    decal+=1
                    xy = re.sub('\\s+', ' ', lines[decal].strip()).split(' ')
                    myvert = wolfvertex(float(xy[0]),float(xy[1]))
                    contourblock.add_vertex(myvert)
                decal+=1
                curarray.translx = self.translx+self.origx
                curarray.transly = self.transly+self.origy
    
    def read_txt_header(self):
        
        with open(self.filename+'.trl') as f:
            lines=f.read().splitlines()
            self.translx = float(lines[1])
            self.transly = float(lines[2])

        with open(self.filename+'.par') as f:
            lines=f.read().splitlines()
            self.dx = float(lines[7])
            self.dy = float(lines[8])
            self.nbx = int(lines[9])
            self.nby = int(lines[10])
            self.origx = float(lines[11])
            self.origy = float(lines[12])
            
        self.wolftype = WOLF_ARRAY_MNAP_INTEGER
        