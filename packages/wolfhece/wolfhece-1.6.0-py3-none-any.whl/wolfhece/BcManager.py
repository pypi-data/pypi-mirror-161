import wx
import numpy as np
from scipy.spatial import cKDTree
from OpenGL.GL  import *

from .PyTranslate import _

class BcManager(wx.Frame):
    """Boundary conditions Manager for WOLF"""

    filename_borders=''
    bordersX ={}
    bordersY ={}
    dx=1.
    dy=1.
    orig=[0.,0.]

    BCType2D={'water depth':1,
              'water level':2,
              'Froude':4,
              'Impervious':99,
              'Normal discharge':31,
              'Tangent discharge':32,
              'Free (no condition)':5,
              'Mobile dam with power law':127,
              'Concentration':7,
              'Close conduit (q normal)':61,
              'Close conduit (q tangent)':62,
              'Close conduit (h for velocity)':63}

    ColorsNb={1:(0.,0.,1.),2:(1.,.5,0.),3:(0.,1.,0.),4:(1.,0.,1.),5:(0.,1.,1.)}

    def __init__(self,parent,dx,dy,ox,oy,title,w=500,h=500, *args, **kwargs):
    
        super(BcManager, self).__init__(parent, title = title,size = (w,h))
        self.dx=dx
        self.dy=dy
        self.orig=[ox,oy]

        self.init_2D()

        self.bordersX['bc']={}
        self.bordersY['bc']={}

        self.Show(True)

        return super().__init__(*args, **kwargs)

    def init_2D(self):

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #Premiers boutons
        self.sizerbut1 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.butLoad = wx.Button(self,wx.ID_FILE,"Load from file...")
        self.butLoad.Bind(wx.EVT_BUTTON,self.OnLoad)
        self.butSave = wx.Button(self,wx.ID_SAVEAS,"Write to file...")
        
        #self.butSave.Bind(wx.EVT_BUTTON,self.OnSave)

        self.sizerbut1.Add(self.butLoad,1,wx.EXPAND)
        self.sizerbut1.Add(self.butSave,1,wx.EXPAND)

        self.sizerbut2 = wx.BoxSizer(wx.HORIZONTAL)
        self.butSet = wx.Button(self,wx.ID_APPLY,"Set BC")
        self.butSet.Bind(wx.EVT_BUTTON,self.OnApplyBC)
        self.butGet = wx.Button(self,wx.ID_FIND,"Get BC")
        self.butGet.Bind(wx.EVT_BUTTON,self.OnGetBC)
        self.butReset = wx.Button(self,wx.ID_FIND,"Reset BC")
        self.butReset.Bind(wx.EVT_BUTTON,self.OnResetBC)
        self.sizerbut2.Add(self.butSet,1,wx.EXPAND)
        self.sizerbut2.Add(self.butGet,1,wx.EXPAND)
        self.sizerbut2.Add(self.butReset,1,wx.EXPAND)

        #type de CL en "collapsable"
        self.sizerAllBC = wx.BoxSizer(wx.VERTICAL)
        self.sizerAllBCt = wx.BoxSizer(wx.VERTICAL)
        self.sizerBC = {}
        self.checkBC = {}
        self.labelBC = {}
        self.valueBC = {}
        self.findBC = {}

        self.collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Type of BC:")
        win = self.collpane.GetPane()
        self.sizerAllBC.Add(self.collpane,1,wx.EXPAND|wx.GROW| wx.ALL)

        for onebc in self.BCType2D.keys():
            self.sizerBC[onebc] = wx.BoxSizer(wx.HORIZONTAL)

            self.checkBC[onebc] = wx.CheckBox(win)
            self.labelBC[onebc] = wx.StaticText(win,label=onebc,size=(200,20))
            self.valueBC[onebc] = wx.TextCtrl(win,size=(100,20),style=wx.TE_CENTRE)
            self.findBC[onebc] = wx.Button(win,name=onebc,label="Find all",size=(60,20))
            self.findBC[onebc].Bind(wx.EVT_BUTTON,self.OnFind)
            
            self.sizerBC[onebc].Add(self.checkBC[onebc],0,wx.GROW)
            self.sizerBC[onebc].Add(self.labelBC[onebc],0,wx.FIXED_MINSIZE|wx.GROW)
            self.sizerBC[onebc].Add(self.valueBC[onebc],1,wx.FIXED_MINSIZE|wx.GROW|wx.EXPAND)
            self.sizerBC[onebc].Add(self.findBC[onebc],0,wx.GROW)
            self.sizerAllBCt.Add(self.sizerBC[onebc],1,wx.EXPAND)
        
        win.SetSizer(self.sizerAllBCt)

        #Zone de selection
        self.sizerselectAll = wx.BoxSizer(wx.VERTICAL)
        self.sizerselect = wx.BoxSizer(wx.VERTICAL)

        self.collpaneSelect = wx.CollapsiblePane(self, wx.ID_ANY, "Selected Borders:")
        win = self.collpaneSelect.GetPane()
        self.sizerselectAll.Add(self.collpaneSelect,1,wx.EXPAND|wx.GROW| wx.ALL)


        self.sizerselButtons = wx.BoxSizer(wx.HORIZONTAL)
        self.butClear = wx.Button(win,wx.ID_CLEAR,"Unselect all")
        self.butClear.Bind(wx.EVT_BUTTON,self.OnClearselection)
        self.butFind = wx.Button(win,wx.ID_CLEAR,"Find borders")
        self.butFind.Bind(wx.EVT_BUTTON,self.OnFindBorders)
        
        self.sizerselButtons.Add(self.butClear,1,wx.EXPAND|wx.GROW)
        self.sizerselButtons.Add(self.butFind,1,wx.EXPAND|wx.GROW)

        self.sizercmdx = wx.BoxSizer(wx.HORIZONTAL)
        self.sizercmdy = wx.BoxSizer(wx.HORIZONTAL)
        
        self.labelcmdx = wx.StaticText(win,label='X:')
        self.cmdx = wx.TextCtrl(win,size=(490,20),style=wx.TE_PROCESS_TAB)
        self.sizercmdx.Add(self.labelcmdx,0,wx.GROW)
        self.sizercmdx.Add(self.cmdx,1,wx.FIXED_MINSIZE|wx.GROW)
        
        self.labelcmdy = wx.StaticText(win,label='Y:')
        self.cmdy = wx.TextCtrl(win,size=(490,20),style=wx.TE_PROCESS_TAB)
        self.sizercmdy.Add(self.labelcmdy,0,wx.GROW)
        self.sizercmdy.Add(self.cmdy,1,wx.FIXED_MINSIZE|wx.GROW)

        self.sizerselcommand = wx.BoxSizer(wx.VERTICAL)
        self.labelcmd = wx.StaticText(win,label='Selection')
        self.labelexample = wx.StaticText(win,label='example : 5,6,10-20  tab  10,20,40-60')
        
        self.sizerselcommand.Add(self.labelcmd,0,wx.GROW)
        self.sizerselcommand.Add(self.labelexample,0,wx.GROW)
        
        self.sizerselcommand.Add(self.sizercmdx,1,wx.EXPAND)
        self.sizerselcommand.Add(self.sizercmdy,1,wx.EXPAND)

        self.sizerTextBoxes = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sizerTextBoxX = wx.BoxSizer(wx.VERTICAL)
        self.sizerTextBoxY = wx.BoxSizer(wx.VERTICAL)

        self.labelBCx = wx.StaticText(win,label='Borders along X axis |')
        self.BCx = wx.TextCtrl(win,size=(250,250),style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB)
        self.sizerTextBoxX.Add(self.labelBCx,0,wx.GROW)
        self.sizerTextBoxX.Add(self.BCx,1,wx.GROW|wx.EXPAND)

        self.labelBCy = wx.StaticText(win,label='Borders along Y axis _')
        self.BCy = wx.TextCtrl(win,size=(250,250),style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB)
        self.sizerTextBoxY.Add(self.labelBCy,0,wx.GROW)
        self.sizerTextBoxY.Add(self.BCy,1,wx.GROW|wx.EXPAND)
        
        self.sizerTextBoxes.Add(self.sizerTextBoxX,1,wx.EXPAND)
        self.sizerTextBoxes.Add(self.sizerTextBoxY,1,wx.EXPAND)

        self.sizerselect.Add(self.sizerselcommand,0,wx.EXPAND)
        self.sizerselect.Add(self.sizerselButtons,0,wx.EXPAND)
        self.sizerselect.Add(self.sizerTextBoxes,0,wx.EXPAND)

        win.SetSizer(self.sizerselect)

        self.sizerfile = wx.BoxSizer(wx.HORIZONTAL)
        self.File = wx.TextCtrl(self,size=(500,250),style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB)
        self.FileCmd=wx.Button(self,label='Apply\n<<<')
        self.FileCmd.Bind(wx.EVT_BUTTON,self.OnFileCmd)
        self.sizerfile.Add(self.File,0,wx.EXPAND)
        self.sizerfile.Add(self.FileCmd,1)

        self.sizer.Add(self.sizerbut1,0,wx.EXPAND)
        self.sizer.Add(self.sizerbut2,0,wx.EXPAND)
        self.sizer.Add(self.sizerAllBC,0,wx.EXPAND)
        self.sizer.Add(self.sizerselectAll,0,wx.EXPAND)
        self.sizer.Add(self.sizerfile,1,wx.EXPAND)


        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.SetAutoLayout(1)

    def OnLoad(self,e):
        #ouverture d'une boîte de dialogue
        file=wx.FileDialog(self,"Choose file", wildcard="Boundary conditions (*.cl)|*.cl|all (*.*)|*.*")
        if file.ShowModal() == wx.ID_CANCEL: 
            return
        else:
            #récuparétaion du nom de fichier avec chemin d'accès
            filename =file.GetPath()

        #lecture du contenu 
        with open(filename, 'r') as myfile:
            txt = myfile.read()
            myfile.close()

        self.File.Value=txt.replace(',','\t')

    def Onsave(self,e):
        #ouverture d'une boîte de dialogue
        file=wx.FileDialog(self,"Choose file", wildcard="Boundary conditions (*.cl)|*.cl|all (*.*)|*.*")
        if file.ShowModal() == wx.ID_CANCEL: 
            return
        else:
            #récuparétaion du nom de fichier avec chemin d'accès
            filename =file.GetPath()

        #lecture du contenu 
        with open(filename, 'w') as myfile:
            myfile.write(self.File.Value)
            myfile.close()
        
    def OnFind(self,event):
        textx=''
        texty=''
        tbc=event.EventObject.Name

        curlist=self.bordersX['bc']
        for k,ij in enumerate(curlist):
            try:
                i,j=ij.split('-')
                val=str(curlist[ij][tbc])
                if(val!='99999.0'):
                    textx+=i+'\t'+j+'\n'
            except:
                pass

        curlist=self.bordersY['bc']
        for k,ij in enumerate(curlist):
            try:
                i,j=ij.split('-')
                val=str(curlist[ij][tbc])
                if(val!='99999.0'):
                    texty+=i+'\t'+j+'\n'
            except:
                pass

        self.BCx.Clear()
        self.BCy.Clear()
        self.BCx.Value=textx
        self.BCy.Value=texty
        self.GetBC()

    def OnApplyBC(self,e):

        for xy in range(2):
            if xy==0:
                sel=self.BCx.Value.splitlines()
                curbord=self.bordersX
            else:
                sel=self.BCy.Value.splitlines()
                curbord=self.bordersY

            for cursel in sel:
                i,j=cursel.split('\t')
                txt=str(i)+'-'+str(j)
                try:
                    mybc= curbord['bc'][txt]
                except:
                    mybc=curbord['bc'][txt]={}

                for k,tbc in enumerate(self.checkBC.keys()):
                    if self.checkBC[tbc].Value:
                        if self.valueBC[tbc].Value!='':
                            mybc[tbc]=float(self.valueBC[tbc].Value)
                                
        self.resetBC()        
        self.PopulateFile()

    def resetBC(self):
        for cl in self.BCType2D.keys():
            self.checkBC[cl].Value=False
            self.valueBC[cl].Value=''

    def OnResetBC(self,e):
        self.resetBC()

    def GetBC(self):
        values={}
        for tbc in self.BCType2D.keys():
            values[tbc]={}
            values[tbc]['val']={}
            values[tbc]['same']=True
            values[tbc]['nb']=0

        for xy in range(2):
            if xy==0:
                sel=self.BCx.Value.splitlines()
                curbord=self.bordersX
            else:
                sel=self.BCy.Value.splitlines()
                curbord=self.bordersY

            for cursel in sel:
                i,j=cursel.split('\t')
                txt=str(i)+'-'+str(j)
                
                try:
                    mybc= curbord['bc'][txt]

                    for ibc,tbc in enumerate(mybc):
                        curval=float(mybc[tbc])

                        if values[tbc]['nb']>0:
                            if not curval in values[tbc]['val'].values():
                                values[tbc]['nb']+=1
                                values[tbc]['val'][values[tbc]['nb']]=curval
                                values[tbc]['same']=False
                        else:
                            values[tbc]['nb']+=1
                            values[tbc]['val'][values[tbc]['nb']]=curval
                except:
                    pass

        for tbc in self.BCType2D.keys():
            if values[tbc]['nb']>0:
                self.checkBC[tbc].Value=True
                txt=''
                if values[tbc]['same']:
                    for curval in values[tbc]['val']:
                        txt += str(curval)
                else:
                    for curval in values[tbc]['val']:
                        txt += str(curval) +' or '
                    txt+='...'
                self.valueBC[tbc].Value=txt
            else:
                self.checkBC[tbc].Value=False

    def OnGetBC(self,e):

        self.GetBC()        

    def OnClearselection(self,e):
        self.bordersX['selected'][:]=False
        self.bordersY['selected'][:]=False
        self.Populate()

    def OnFindBorders(self,event):

        if self.cmdx.Value!='':
            tx = self.cmdx.Value.split('\t')
            if len(tx)==2:
                indi={}
                indj={}
                partxi = tx[0].split(',')
                for i,curpart in enumerate(partxi):
                    indi[i]={}
                    bounds=curpart.split('-')
                    indi[i]['chain']=curpart
                    indi[i]['istart']=int(bounds[0])-1
                    try:
                        indi[i]['iend']=int(bounds[1])-1
                    except:
                        indi[i]['iend']=int(bounds[0])-1
                partxj = tx[1].split(',')
                for i,curpart in enumerate(partxj):
                    indj[i]={}
                    bounds=curpart.split('-')
                    indj[i]['chain']=curpart
                    indj[i]['jstart']=int(bounds[0])-1
                    try:
                        indj[i]['jend']=int(bounds[1])-1
                    except:
                        indj[i]['jend']=int(bounds[0])-1

                for whichi in indi.keys():
                    for i in range(indi[whichi]['istart'],indi[whichi]['iend']+1):
                        for whichj in indj.keys():
                            for j in range(indj[whichj]['jstart'],indj[whichj]['jend']+1):
                                text=str(i)+'-'+str(j)
                                try:
                                    index=self.bordersX['indicesstr'].index(text)  
                                    self.bordersX['selected'][index] = ~ self.bordersX['selected'][index]
                                except:
                                    pass

            else:
                wx.MessageBox('Bad command for X borders -- Nothing to do !')

        if self.cmdy.Value!='':
            ty = self.cmdy.Value.split('\t')
            if len(ty)==2:
                indi={}
                indj={}
                partyi = ty[0].split(',')
                for i,curpart in enumerate(partyi):
                    indi[i]={}
                    bounds=curpart.split('-')
                    indi[i]['chain']=curpart
                    indi[i]['istart']=int(bounds[0])-1
                    try:
                        indi[i]['iend']=int(bounds[1])-1
                    except:
                        indi[i]['iend']=int(bounds[0])-1
                partyj = ty[1].split(',')
                for i,curpart in enumerate(partyj):
                    indj[i]={}
                    bounds=curpart.split('-')
                    indj[i]['chain']=curpart
                    indj[i]['jstart']=int(bounds[0])-1
                    try:
                        indj[i]['jend']=int(bounds[1])-1
                    except:
                        indj[i]['jend']=int(bounds[0])-1

                for whichi in indi.keys():
                    for i in range(indi[whichi]['istart'],indi[whichi]['iend']+1):
                        for whichj in indj.keys():
                            for j in range(indj[whichj]['jstart'],indj[whichj]['jend']+1):
                                text=str(i)+'-'+str(j)
                                try:
                                    index=self.bordersY['indicesstr'].index(text)  
                                    self.bordersY['selected'][index] = ~ self.bordersY['selected'][index]
                                except:
                                    pass
            else:
                wx.MessageBox('Bad command for Y borders -- Nothing to do !')

        self.Populate()
        
    def Populate(self):

        text=''
        for k,selected in enumerate(self.bordersX['selected']):
            if selected:
                text+= str(self.bordersX['indices'][0][k]+1) + '\t'+ str(self.bordersX['indices'][1][k]+1)+'\n'

        self.BCx.Clear()
        self.BCx.AppendText(text)

        text=''
        for k,selected in enumerate(self.bordersY['selected']):
            if selected:
                text+= str(self.bordersY['indices'][0][k]+1) + '\t'+ str(self.bordersY['indices'][1][k]+1)+'\n'

        self.BCy.Clear()
        self.BCy.AppendText(text)

    def PopulateFile(self):

        text=''
        nb=0

        for orient in range(1,3):
            if orient==1:
                curlist=self.bordersX['bc']
            else:
                curlist=self.bordersY['bc']

            for k,ij in enumerate(curlist):
                for m,tbc in enumerate(curlist[ij]):
                    i,j=ij.split('-')
                    numbc=self.BCType2D[tbc]
                    val=str(curlist[ij][tbc])
                    if(val!='99999.0'):
                        text+=i+'\t'+j+'\t'+str(orient)+'\t'+str(numbc)+'\t'+val+'\n'
                    nb+=1


        self.File.Clear()
        self.File.Value=str(nb)+'\n'+text
    
    def OnFileCmd(self,e):

        text = self.File.Value
        text=text.splitlines()

        nb=int(float(text[0]))

        try:
            for i in range(1,nb+1):
                i,j,orient,type,value=text[i].split('\t')

        except:
             wx.MessageBox('Bad text values -- Correct and Retry !!')
             return

        self.File.Clear()
        self.bordersX['bc']={}
        self.bordersY['bc']={}
        for i in range(1,nb+1):
            i,j,orient,type,value=text[i].split('\t')
            i=int(float(i))
            j=int(float(j))
            type=int(float(type))
            orient=int(float(orient))
            value=float(value)
            if orient==1:               
                texttxt=str(i-1)+'-'+str(j-1)
                try:
                    index=self.bordersX['indicesstr'].index(texttxt)  
                    try:
                        curbc =self.bordersX['bc'][str(i)+'-'+str(j)]
                    except:
                        curbc=self.bordersX['bc'][str(i)+'-'+str(j)]={}
                
                    try:     
                        curbc[self.findTypeBC(type)]=value
                    except:
                        try:
                            curbc[type]=value
                        except:
                            pass
                except:
                    print('Bad border indices on X ('+str(i)+'-'+str(j)+(')'))
            elif orient==2:
                texttxt=str(i-1)+'-'+str(j-1)
                try:
                    index=self.bordersY['indicesstr'].index(texttxt)  
                    try:
                        curbc =self.bordersY['bc'][str(i)+'-'+str(j)]
                    except:
                        curbc=self.bordersY['bc'][str(i)+'-'+str(j)]={}
                
                    try:     
                        curbc[self.findTypeBC(type)]=value
                    except:
                        try:
                            curbc[type]=value
                        except:
                            pass
                except:
                    print('Bad border indices on Y ('+str(i)+'-'+str(j)+(')'))
        self.PopulateFile()

    def FindBorders(self,array : np.ma.array):

        shape = array.shape

        nbx=0
        for j in range(1,shape[1]-1):
            for i in range(1,shape[0]):
                if (array.mask[i,j] and not array.mask[i-1,j]) or (not array.mask[i,j] and array.mask[i-1,j]):
                    nbx+=1
        nby=0
        for i in range(1,shape[0]-1):
            for j in range(1,shape[1]):
                if (array.mask[i,j] and not array.mask[i,j-1]) or (not array.mask[i,j] and array.mask[i,j-1]):
                    nby+=1

        self.bordersX['nb']=nbx
        self.bordersY['nb']=nby

        indicesX = np.zeros((2,nbx),dtype=np.integer,order='F') 
        indicesY = np.zeros((2,nby),dtype=np.integer,order='F') 
        indicesXstr=[]
        indicesYstr=[]

        nbx=0
        for j in range(1,shape[1]-1):
            for i in range(1,shape[0]):
                if (array.mask[i,j] and not array.mask[i-1,j]) or (not array.mask[i,j] and array.mask[i-1,j]):
                    indicesX[0,nbx]=i
                    indicesX[1,nbx]=j
                    indicesXstr.append(str(i)+'-'+str(j))
                    nbx+=1
        nby=0
        for i in range(1,shape[0]-1):
            for j in range(1,shape[1]):
                if (array.mask[i,j] and not array.mask[i,j-1]) or (not array.mask[i,j] and array.mask[i,j-1]):
                    indicesY[0,nby]=i
                    indicesY[1,nby]=j
                    indicesYstr.append(str(i)+'-'+str(j))
                    nby+=1

        self.bordersX['indices']=indicesX
        self.bordersX['indicesstr']=indicesXstr
        self.bordersY['indices']=indicesY
        self.bordersY['indicesstr']=indicesYstr
        self.ComputeCoordinates()
        self.do_kdtree()


    def ReadFileBorders(self,*args):
        if len(args)>0:
            #s'il y a un argument on le prend tel quel
            self.filename = str(args[0])
        else:
            #ouverture d'une boîte de dialogue
            file=wx.FileDialog(self,"Choose file", wildcard="sux (*.sux)|*.sux|all (*.*)|*.*")
            if file.ShowModal() == wx.ID_CANCEL: 
                return
            else:
                #récuparétaion du nom de fichier avec chemin d'accès
                self.filename =file.GetPath()

        #lecture du contenu SUX
        with open(self.filename, 'r') as myfile:
            #split des lignes --> récupération des infos sans '\n' en fin de ligne
            #  différent de .readlines() qui lui ne supprime pas les '\n'
            myparamsline = myfile.read().splitlines()
            myfile.close()

        indicesX = np.zeros((2,myparamsline.count()),dtype=np.integer,order='F') 
        k=0
        for myborder in myparamsline:
            indicesX[:,k] = myborder.split()
            k+=1

        self.bordersX['nb']=indicesX.size()/2
        self.bordersX['indices']=indicesX
        
        #lecture du contenu SUX
        with open(self.filename.replace('sux','suy'), 'r') as myfile:
            #split des lignes --> récupération des infos sans '\n' en fin de ligne
            #  différent de .readlines() qui lui ne supprime pas les '\n'
            myparamsline = myfile.read().splitlines()
            myfile.close()

        indicesY = np.zeros((2,myparamsline.count()),dtype=np.integer,order='F') 
        k=0
        for myborder in myparamsline:
            indicesY[:,k] = myborder.split()
            k+=1
        
        self.bordersY['nb']=indicesY.size()/2
        self.bordersY['indices']=indicesY

    def ComputeCoordinates(self):

        nbx=self.bordersX['nb']
        coordscgX = np.zeros((2,nbx),dtype=float,order='F')
        coordsX = np.zeros((2,2,nbx),dtype=float,order='F')
        selectedX = np.zeros(nbx,dtype=np.bool,order='F')
        for k in range(nbx):
            x1=self.orig[0]+self.bordersX['indices'][0,k]*self.dx
            y1=self.orig[1]+self.bordersX['indices'][1,k]*self.dy
            y2=y1+self.dy

            coordsX[0,0,k]=x1
            coordsX[1,0,k]=y1
            coordsX[0,1,k]=x1
            coordsX[1,1,k]=y2

            coordscgX[0,k]=x1
            coordscgX[1,k]=(y1+y2)/2.

        self.bordersX['coords']=coordsX
        self.bordersX['coordscg']=coordscgX
        self.bordersX['selected']=selectedX

        nby=self.bordersY['nb']
        coordscgY = np.zeros((2,nby),dtype=float,order='F')
        coordsY = np.zeros((2,2,nby),dtype=float,order='F')
        selectedY = np.zeros(nbx,dtype=np.bool,order='F')
        for k in range(nby):
            x1=self.orig[0]+self.bordersY['indices'][0,k]*self.dx
            x2=x1+self.dx
            y1=self.orig[1]+self.bordersY['indices'][1,k]*self.dy

            coordsY[0,0,k]=x1
            coordsY[1,0,k]=y1
            coordsY[0,1,k]=x2
            coordsY[1,1,k]=y1

            coordscgY[0,k]=(x1+x2)/2.
            coordscgY[1,k]=y1

        self.bordersY['coords']=coordsY
        self.bordersY['coordscg']=coordscgY
        self.bordersY['selected']=selectedY

    def count_nbbc(self,bc,axis):

        nb=0

        if axis.lower()=='x':
            locbc=self.bordersX['bc'][bc]
            for valbc in locbc:
                curval=float(locbc[valbc])
                if curval!=99999:
                    nb+=1
        elif axis.lower()=='y':
            locbc=self.bordersY['bc'][bc]
            for valbc in locbc:
                curval=float(locbc[valbc])
                if curval!=99999:
                    nb+=1

        return nb

    def plot(self):

        nbx = self.bordersX['nb']
        nby = self.bordersX['nb']

        coordx = self.bordersX['coords']
        coordy = self.bordersY['coords']

        for curbc in self.bordersX['bc']:
            i,j=curbc.split('-')
            txt=str(int(i)-1)+'-'+str(int(j)-1)
            index=self.bordersX['indicesstr'].index(txt)  
            
            x1,y1=coordx[:,0,index]
            x2,y2=coordx[:,1,index]
            
            glLineWidth(5.)

            nb = self.count_nbbc(curbc,'x')
            try:
                r,g,b = self.ColorsNb[nb]
            except:
                r=1.
                g=0.
                b=0.

            glColor3f(r,g,b)            
            glBegin(GL_LINES)
            glVertex2d(x1,y1)
            glVertex2d(x2,y2)
            glEnd()

        for curbc in self.bordersY['bc']:
            i,j=curbc.split('-')
            txt=str(int(i)-1)+'-'+str(int(j)-1)
            index=self.bordersY['indicesstr'].index(txt)  
            
            x1,y1=coordy[:,0,index]
            x2,y2=coordy[:,1,index]
            
            glLineWidth(5.)

            nb = self.count_nbbc(curbc,'y')
            try:
                r,g,b = self.ColorsNb[nb]
            except:
                r=1.
                g=0.
                b=0.

            glColor3f(r,g,b)            
            glBegin(GL_LINES)
            glVertex2d(x1,y1)
            glVertex2d(x2,y2)
            glEnd()
        
        for k in range(nbx):
            
            x1,y1=coordx[:,0,k]
            x2,y2=coordx[:,1,k]
            
            if self.bordersX['selected'][k]:
                glLineWidth(4.)
                glColor3f(1.,0.,0.)
            else:
                glLineWidth(2.)
                glColor3f(0.,0.,0.)
            
            glBegin(GL_LINES)
            glVertex2d(x1,y1)
            glVertex2d(x2,y2)
            glEnd()

        for k in range(nby):
            
            x1,y1=coordy[:,0,k]
            x2,y2=coordy[:,1,k]
            
            if self.bordersY['selected'][k]:
                glLineWidth(4.)
                glColor3f(1.,0.,0.)
            else:
                glLineWidth(2.)
                glColor3f(0.,0.,0.)

            glBegin(GL_LINES)
            glVertex2d(x1,y1)
            glVertex2d(x2,y2)
            glEnd()
    
    def do_kdtree(self):
        self.mytreeX = cKDTree(self.bordersX['coordscg'].transpose())
        self.mytreeY = cKDTree(self.bordersY['coordscg'].transpose())
        
    def query_kdtree(self,point):
       
        distX, indexesX = self.mytreeX.query(point)
        distY, indexesY = self.mytreeY.query(point)

        if distX<distY:
            self.bordersX['selected'][indexesX] = ~self.bordersX['selected'][indexesX]
        else:
            self.bordersY['selected'][indexesY] = ~self.bordersY['selected'][indexesY]
        
        return indexesX,indexesY
        
    def ray_tracing_numpy(self,poly,XorY = 'X'):

        if XorY=='X':
            x=self.bordersX['coordscg'][0,:]
            y=self.bordersX['coordscg'][1,:]
        else:
            x=self.bordersY['coordscg'][0,:]
            y=self.bordersY['coordscg'][1,:]

        n = len(poly)
        inside = np.zeros(len(x),np.bool_)
        p2x = 0.0
        p2y = 0.0
        xints = 0.0
        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            idx = np.nonzero((y > min(p1y,p2y)) & (y <= max(p1y,p2y)) & (x <= max(p1x,p2x)))[0]
            if p1y != p2y:
                xints = (y[idx]-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                if p1x == p2x:
                    inside[idx] = ~inside[idx]
                else:
                    idxx = idx[x[idx] <= xints]
                    inside[idxx] = ~inside[idxx]    

            p1x,p1y = p2x,p2y

        if XorY=='X':
            self.bordersX['selected']=np.logical_xor(self.bordersX['selected'],inside)
        else:
            self.bordersY['selected']=np.logical_xor(self.bordersY['selected'],inside)

        return inside    
        
    def findTypeBC(self,i):
        for k in self.BCType2D.keys():
            if self.BCType2D[k]==i:
                return k
                break
