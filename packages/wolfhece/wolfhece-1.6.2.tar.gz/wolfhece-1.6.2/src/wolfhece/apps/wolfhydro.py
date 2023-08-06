import os       
import wx
try:
    from ..PyTranslate import _
    from ..PyGui import HydrologyModel
except:
    from wolfhece.PyTranslate import _
    from wolfhece.PyGui import HydrologyModel

def main(strmydir=''):
    ex = wx.App()
    exLocale = wx.Locale()
    exLocale.Init(wx.LANGUAGE_ENGLISH)
    mydro=HydrologyModel()
    ex.MainLoop()

if __name__=='__main__':
    main()