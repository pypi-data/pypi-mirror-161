#import des modules
from os import path
import sys
import wx

#Import des modules WOLF
try:
    from ..PyTranslate import _
    from ..PyDraw import WolfMapViewer
    from ..wolf_array import WolfArray
except:
    from wolfhece.PyTranslate import _
    from wolfhece.PyDraw import WolfMapViewer
    from wolfhece.wolf_array import WolfArray

def main(strmydir='',ListArrays=None):
    '''Comparaison de 2 cartes WOLF
    args :
        - strmydir : répertoire contenant 2 matrices WOLF (1.bin et 2.bin) et leurs fichiers accompagant
    '''
    #Déclaration de l'App WX
    ex = wx.App()
    #Choix de la langue
    exLocale = wx.Locale()
    exLocale.Init(wx.LANGUAGE_ENGLISH)
    
    #Création de 3 fenêtres de visualisation basées sur la classe "WolfMapViewer"
    first = WolfMapViewer(None,'First',w=600,h=600)
    second = WolfMapViewer(None,'Second',w=600,h=600)
    third = WolfMapViewer(None,'Third',w=600,h=600)
    
    #Création d'une liste contenant les 3 instances d'objet "WolfMapViewer"
    list=[]
    list.append(first)
    list.append(second)
    list.append(third)
    
    #On indique que les objets sont liés en actiavt le Booléen et en pointant la liste précédente
    for curlist in list:
        curlist.linked=True
        curlist.linkedList=list
    
    if strmydir!='':
        #Création des matrices WolfArray sur base des fichiers    
        mnt = WolfArray(path.join(strmydir,'1.bin'))
        mns = WolfArray(path.join(strmydir,'2.bin'))
    elif ListArrays is not None:
        if len(ListArrays)==2:
            mnt = ListArrays[0]
            mns = ListArrays[1]
            
    #Création du différentiel -- Les opérateurs mathématiques sont surchargés
    diff = mns-mnt
    
    #Ajout des matrices dans les fenêtres de visualisation
    first.add_object('array',newobj=mnt,ToCheck=True,id='MNT')
    second.add_object('array',newobj=mns,ToCheck=True,id='MNS')
    third.add_object('array',newobj=diff,ToCheck=True,id='DIFF')
    
    #boucle infinie pour gérer les événements GUI
    ex.MainLoop()
    
if __name__=='__main__':
    '''gestion de l'éxécution du module en tant que code principal'''
    # total arguments
    n = len(sys.argv)
    if n==2:
        mydir = sys.argv[1]
        if path.exists(mydir):    
            main(mydir)
    else:
        if path.exists('d:\\compare'):
            main('d:\\compare')
    
    
    

