from tkinter import VERTICAL
from typing import List
from matplotlib.pyplot import title
from numpy.lib.function_base import append
import matplotlib.path as mpltPath
import numpy as np
import wx
from wx.dataview import TreeListCtrl
from wx.core import HORIZONTAL, BoxSizer, RadioButton,RadioBox,Button,ComboBox
from wx.lib.agw import xlsgrid
import wx.grid
import wx.dataview
from OpenGL.GL  import *
from os import path

from .PyTranslate import _
from .wolf_array import WolfArray
from .CpGrid import CpGrid
from .PyPalette import wolfpalette

RES_WATERLEVEL=-1
RES_WATERDEPTH=0
RES_QX=1
RES_QY=2
RES_FROUDE=3
RES_QABS=4
RES_VX=5
RES_VY=6
RES_VABS=7

ALL_RES_TYPE={'Water level':RES_WATERLEVEL,
               'Water depth':RES_WATERDEPTH, 
               'Discharge X':RES_QX,
               'Discharge Y':RES_QY,
               'Discharge norm':RES_QABS,
               'Froude':RES_FROUDE,
               'Speed X':RES_VX,
               'Speed Y':RES_VY,
               'Speed norm':RES_VABS}

class wolfres2DGPU(WolfArray,wx.Frame):

    bedelevation:WolfArray
    waterdepth:WolfArray
    qx:WolfArray
    qy=WolfArray

    currentstep:int
    whichres:int

    mydir:str
    mysteps:list

    def __init__(self,dir,bedelev,parent=None, fname=None, masknull=True):

        super().__init__(mold=bedelev)
        super(wx.Frame,self).__init__(parent, size=(300, 400))

        self.mydir = dir
        self.bedelevation= WolfArray(mold=bedelev)
        self.currentstep=0
        self.mysteps=[]
        self.showstructure(parent)
        self.whichres=RES_WATERLEVEL
        self.change_step(self.mysteps[0])
        self.combosteps.ChangeValue(self.mysteps[0])

    def change_step(self,which):
        self.currentstep=which
        
        if path.exists(self.mydir+'//out'+str(which)+'r.bin'):
            self.waterdepth = WolfArray(self.mydir+'//out'+str(which)+'r.bin')
            self.qx = WolfArray(self.mydir+'//out'+str(which)+'g.bin')
            self.qy = WolfArray(self.mydir+'//out'+str(which)+'b.bin')

            self.bedelevation.array.mask = self.waterdepth.array.mask
            self.qx.array.mask = self.waterdepth.array.mask
            self.qy.array.mask = self.waterdepth.array.mask

            self.change_res(self.whichres)

    def find_steps(self):
        k=101
        while path.exists(self.mydir+'//out'+str(k)+'r.bin'):
            self.mysteps.append(str(k))
            k+=1

    def change_res(self,which):
        
        self.nbnotnull = self.waterdepth.nbnotnull
        
        if(which==RES_WATERLEVEL):
            self.array = self.waterdepth.array+self.bedelevation.array
            self.mypal=wolfpalette(None,"Palette of colors")
            self.mypal.default16()
            self.delete_lists()
        elif(which==RES_WATERDEPTH):
            self.array = self.waterdepth.array
            self.mypal = self.waterdepth.mypal
            self.delete_lists()
        elif(which==RES_QX):
            self.array = self.qx.array
            self.mypal = self.qx.mypal
            self.nbnotnull = self.qx.nbnotnull
            self.delete_lists()
        elif(which==RES_QY):
            self.array = self.qy.array
            self.mypal = self.qy.mypal
            self.nbnotnull = self.qy.nbnotnull
            self.delete_lists()
        elif(which==RES_FROUDE):
            self.array = (self.qx.array**2.+self.qy.array**2.)**.5/(9.81 * self.waterdepth.array**3)**.5
            self.mypal=wolfpalette(None,"Palette of colors")
            self.mypal.default16()
            self.delete_lists()
        elif(which==RES_QABS):
            self.array = (self.qx.array**2.+self.qy.array**2.)**.5
            self.mypal=wolfpalette(None,"Palette of colors")
            self.mypal.default16()
            self.delete_lists()
        elif(which==RES_VX):
            self.array = self.qx.array/self.waterdepth.array
            self.mypal=wolfpalette(None,"Palette of colors")
            self.mypal.default16()
            self.delete_lists()
        elif(which==RES_VY):
            self.array = self.qy.array/self.waterdepth.array
            self.mypal=wolfpalette(None,"Palette of colors")
            self.mypal.default16()
            self.delete_lists()
        elif(which==RES_VABS):
            self.array = (self.qx.array**2.+self.qy.array**2.)**.5/self.waterdepth.array
            self.mypal=wolfpalette(None,"Palette of colors")
            self.mypal.default16()
            self.delete_lists()

        self.updatepalette(0)
        #self.plot()
        #glFlush()

    def onRadioBox(self,e):
        text=self.boxtype.GetStringSelection()
        self.whichres=ALL_RES_TYPE[text]
        self.change_res(self.whichres)

    def oncombo(self,e):
        if self.combosteps.Value in self.mysteps:
            self.change_step(int(self.combosteps.Value))

    def onnext(self,e):
        curpos=self.mysteps.index(self.combosteps.Value)
        if curpos==len(self.mysteps)-1:
            itemnext=self.mysteps[0]
        else:
            itemnext = self.mysteps[curpos+1]
        self.combosteps.ChangeValue(itemnext)
        self.change_step(itemnext)

    def onprevious(self,e):
        curpos=self.mysteps.index(self.combosteps.Value)
        if curpos==0:
            itemprev=self.mysteps[-1]
        else:
            itemprev = self.mysteps[curpos-1]
        self.combosteps.ChangeValue(itemprev)
        self.change_step(itemprev)

    def showstructure(self,parent):

        box = BoxSizer(orient=wx.HORIZONTAL)
        box2 = BoxSizer(orient=wx.VERTICAL)

        lbllist=list(ALL_RES_TYPE.keys())
        self.boxtype = RadioBox(self,label='Which type?',choices=lbllist,majorDimension = 0, style = wx.RA_VERTICAL)

        self.boxtype.Bind(wx.EVT_RADIOBOX,self.onRadioBox)

        self.find_steps()
        self.combosteps=ComboBox(self,choices=self.mysteps)
        self.combosteps.Bind(wx.EVT_COMBOBOX,self.oncombo)

        self.next = Button(self,label="Next")
        self.previous = Button(self,label="Previous")
        self.next.Bind(wx.EVT_BUTTON,self.onnext)
        self.previous.Bind(wx.EVT_BUTTON,self.onprevious)

        box2.Add(self.combosteps,0,wx.EXPAND)
        box2.Add(self.next,1,wx.EXPAND)
        box2.Add(self.previous,1,wx.EXPAND)

        box.Add(self.boxtype,0,wx.EXPAND)
        box.Add(box2,1,wx.EXPAND)

        self.SetSizer(box)
        self.Show()

