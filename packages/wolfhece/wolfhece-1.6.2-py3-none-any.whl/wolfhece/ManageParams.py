import wx

from .PyTranslate import _
from .PyParams import Wolf_Param

def main():
    ex = wx.App()
    frame = Wolf_Param(None,"Params",to_read=False)
    ex.MainLoop()

if __name__=="__main__":
    main()