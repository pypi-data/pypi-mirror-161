import wx

try:
    from ..PyTranslate import _
    from ..hydrology.Optimisation import Optimisation
except:
    from wolfhece.PyTranslate import _
    from wolfhece.hydrology.Optimisation import Optimisation

def main():
    app = wx.App()
    myOpti = Optimisation()
    myOpti.Show()
    app.MainLoop()
    print("That's all folks! ")

if __name__=='__main__':
    main()
    