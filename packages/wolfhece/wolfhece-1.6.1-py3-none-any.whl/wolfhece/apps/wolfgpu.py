import os
import wx

try:
    from ..PyTranslate import _
    from ..PyGui import GPU2DModel
except:
    from wolfhece.PyTranslate import _
    from wolfhece.PyGui import GPU2DModel

def main(strmydir=''):
    ex = wx.App()
    exLocale = wx.Locale()
    exLocale.Init(wx.LANGUAGE_ENGLISH)
    mydro=GPU2DModel()
    ex.MainLoop()

if __name__=='__main__':
    main()