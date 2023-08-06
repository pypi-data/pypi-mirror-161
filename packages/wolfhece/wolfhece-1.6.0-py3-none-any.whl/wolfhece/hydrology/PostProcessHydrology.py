import sys
import numpy as np
import matplotlib.pyplot as plt
from numpy.testing._private.utils import measure

from .Catchment import *
from .Comparison import *
from ..wolf_array import *
from ..PyParams import*
from ..PyTranslate import _

class PostProcessHydrology(wx.Frame):


    directoryPath:str
    filename:str
    writeDir:str

    myCatchments:dict
    dictToCompare:dict
    myComparison:Comparison

    def __init__(self, parent=None, title="", w=500, h=500, postProFile=''):
        super(PostProcessHydrology, self).__init__(parent, title=title, size=(w,h))

        self.directoryPath   = ""
        self.filename        = ""
        self.writeDir        = ""

        self.myCatchments = {}
        self.myComparison = {}
        self.dictToCompare = {}


        if postProFile=='':
            idir=wx.FileDialog(None,"Choose simulation file",wildcard='Fichiers de comparaison (*.compar)|*.compar|Fichiers post-processing (*.postPro)|*.postPro')
            if idir.ShowModal() == wx.ID_CANCEL:
                print("Post process cancelled!")
                sys.exit()
            self.filename = idir.GetPath()
            self.directoryPath = idir.GetDirectory() + "\\"
        else:
             self.filename = postProFile
             self.directoryPath = os.path.dirname(postProFile) + "\\"


        # if writeDir=='':
        #     idir=wx.DirDialog(None,"Choose writing file")
        #     if idir.ShowModal() == wx.ID_CANCEL:
        #         print("I'm here!")
        #         sys.exit()
        #     writeDir =idir.GetPath()+"\\"

        # Reading a compare file
        if(self.filename[-7:]==".compar"):
            # Reading of the input file 'Input.compar'
            paramsCompar = Wolf_Param(to_read=False)
            paramsCompar.ReadFile(self.filename)
            nbCatchment = int(paramsCompar.myparams['Main information']['nb catchment']['value'])

            beginElement = 'Catchment '
            for i in range(1,nbCatchment+1):
                element = beginElement + str(i)
                self.myCatchments[element]={}
                self.myCatchments[element]['Title'] = paramsCompar.myparams[element]['name']['value']
                # Just check and correct the name of the filePath the way 
                paramsCompar.myparams[element]['filePath']['value'] = paramsCompar.myparams[element]['filePath']['value'].replace("\\", "/")
                if not(paramsCompar.myparams[element]['filePath']['value'].endswith('/')):
                    paramsCompar.myparams[element]['filePath']['value'] = paramsCompar.myparams[element]['filePath']['value'] + '/'
                dirName = paramsCompar.myparams[element]['filePath']['value']
                # Read the name of the input file
                try:
                    self.fileName = paramsCompar.myparams[element]['fileName']['value']
                except:
                    self.fileName = "Input.postPro"

                paramsCatchment = Wolf_Param(to_read=False)
                paramsCatchment.ReadFile(dirName+self.fileName)
                nameCatchment = paramsCatchment.myparams['Main information']['Name']['value']

                paramsCatchment.myparams['Main information']['directoryPath']['value'] = paramsCatchment.myparams['Main information']['directoryPath']['value'].replace("\\", "/")
                if not(paramsCatchment.myparams['Main information']['directoryPath']['value'].endswith('/')):
                    paramsCatchment.myparams['Main information']['directoryPath']['value'] = paramsCatchment.myparams['Main information']['directoryPath']['value'] + '/'
                dirCatchment = paramsCatchment.myparams['Main information']['directoryPath']['value']

                try:
                    catchmentFileName = paramsCatchment.myparams['Main information']['Catchment file name']['value']
                except:
                    catchmentFileName = ""
                try:
                    rbFileName = paramsCatchment.myparams['Main information']['RB file name']['value']
                except:
                    rbFileName = ""
                try:
                    tz = int(paramsCatchment.myparams['Main information']['time zone']['value'])
                except:
                    tz = 0

                if(int(paramsCatchment.myparams['Plot information']['plot all subbasin']['value']) == 1):
                    plotAllHydro = True
                else:
                    plotAllHydro = False
                if nbCatchment > 1:
                    isCompared = True
                self.myCatchments[element]['Object'] = Catchment(nameCatchment, dirCatchment, plotAllHydro, isCompared, _catchmentFileName=catchmentFileName, _rbFileName=rbFileName, _tz=tz)
            if(nbCatchment>1):        
                dictToCompare = paramsCompar.myparams['Plots']
                self.myComparison = Comparison(self.directoryPath, self.myCatchments, dictToCompare)
                self.myComparison.compare_now()

        elif(self.filename[-8:]=='.postPro'):
            self.myCatchments['Catchment 1']={}
            self.myCatchments['Catchment 1']['Title']=''
            paramsCatchment = Wolf_Param(to_read=False)
            paramsCatchment.ReadFile(self.filename)
            nameCatchment = paramsCatchment.myparams['Main information']['Name']['value']
            if(int(paramsCatchment.myparams['Plot information']['plot all subbasin']['value']) == 1):
                plotAllHydro = True
            else:
                plotAllHydro = False
            isCompared = False
            try:
                tz = int(paramsCatchment.myparams['Main information']['time zone']['value'])
            except:
                tz = 0
            
            self.myCatchments['Catchment 1']['Object'] = Catchment(nameCatchment, self.directoryPath, plotAllHydro, _plotNothing=False, _tz=tz)

        else:
            print("ERROR: No valid input file found in this folder!")
            sys.exit()

        plt.show()

        print("That's all folks! ")




# When this module is run (not imported) then create the app, the
# frame, show it, and start the event loop.
if __name__ == '__main__':

    ex = wx.App()
    exLocale = wx.Locale()
    exLocale.Init(wx.LANGUAGE_ENGLISH)
    ex.MainLoop()

    myObj = PostProcessHydrology()
