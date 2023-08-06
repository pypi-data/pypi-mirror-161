import wx

try:
    from ..PyTranslate import _
    from ..PyParams import Wolf_Param
except:
    from wolfhece.PyTranslate import _
    from wolfhece.PyParams import Wolf_Param

def main():
    ex = wx.App()
    frame = Wolf_Param(None,"Params")
    ex.MainLoop()

if __name__=="__main__":
    main()