import os
from scipy.interpolate import interpolate
from matplotlib import figure as mplfig
import matplotlib.pyplot as plt

from .PyTranslate import _
from .PyVertex import wolfvertex
from .wolf_array import *
from .PyCrosssections import crosssections
from .GraphNotebook import PlotNotebook

listdem=['dem1','dem2','dem10m','dem20m','cs']
#listdem=['dem2']

class node_watershed:
    '''Noeud du modèle hydrologique maillé'''
    i:int
    j:int
    index:int

    dem:dict    
    demdelta:float

    mycs:list = None

    time:float
    slope:float
    sloped8:float

    slopecorr:dict
    demcorr:dict

    river:bool
    reach:int
    sub:int
    forced:bool
    uparea:float

    strahler:int
    reachlevel:int
    
    cums:float
    incrs:float

    down=None
    up:list
    upriver:list

    flatindex:int = -1

    def incr_curvi(self):
        if self.down is None:
            self.cums=0.
        else:
            self.cums = self.down.cums+self.incrs
        
        #for curup in self.upriver:
        #    curup.incr_curvi()
        for curup in self.up:
            curup.incr_curvi()

    def mean_slope_up(self,threshold):
        curnode: node_watershed
        meanslope=0.
        nbmean=0
        for curnode in self.up:
            if curnode.slope>threshold:
                nbmean+=1.
                meanslope+=curnode.slope
        if nbmean>0:
            meanslope=meanslope/nbmean

        return meanslope

    def slope_down(self,threshold):
        slopedown=0.
        curnode=self
        while curnode.slope < threshold:
            if curnode.down is None:
                break
            curnode=curnode.down

        slopedown = curnode.slope
        return slopedown

    def slope_upriver(self,threshold):
        slopeup=0.

        if self.slope<threshold:
            if len(self.upriver)>0:
                slopeup=self.upriver[0].slope_upriver(threshold)
            else:
                slopeup=-1.
        else:
            slopeup = self.slope

        return slopeup

class riversystem:
    '''Classe du réseau de rivières d'un modèle hydrologique WOLF'''
    nbreaches:int
    myreaches:dict
    
    myupmin:dict
    
    parent=None
    myupstreams:dict 
    
    maxlevels:int
    maxstrahler:int

    tslopemin:float =None
    tslopemax:float =None

    myplotter:PlotNotebook = None
    savedir:str=''

    def __init__(self,rivers:list,parent,thslopemin,
                thslopemax, *args, **kwargs):
        curnode:node_watershed

        self.parent=parent
        self.nbreaches = max([x.reach for x in rivers])
        self.myreaches={}
        self.myreaches['reaches']={}
        self.myupstreams={}
        self.myupstreams['list']=[]

        for curreach in range(1,self.nbreaches+1):
            curup:node_watershed
            listreach,curup=parent.find_rivers(whichreach=curreach)

            if len(curup.upriver)==0:
                self.myupstreams['list'].append(curup)

            self.myreaches['reaches'][curreach]={}
            curdict=self.myreaches['reaches'][curreach]
            curdict['upstream']=curup
            curdict['baselist']=listreach
            
        self.create_index()
        
        self.tslopemin=thslopemin
        self.tslopemax=thslopemax
        self.slope_correctionmin()
        self.slope_correctionmax()

        return super().__init__(*args, **kwargs)

    def get_x(self,whichreach=None,whichup=None):
        if not whichreach is None:
            nodeslist=self.myreaches['reaches'][whichreach]['baselist']
            x=list(curnode.cums for curnode in nodeslist)
        elif not whichup is None:
            curnode:node_watershed
            x=[]
            curnode=self.myupstreams['list'][whichup]
            while not curnode is None:
                x.append(curnode.cums)
                curnode=curnode.down
        else:
            x=[]

        return x

    def get_dem(self,whichdem,whichreach=None,whichup=None):
        if not whichreach is None:
            nodeslist=self.myreaches['reaches'][whichreach]['baselist']
            dem=list(curnode.dem[whichdem] for curnode in nodeslist)
        elif not whichup is None:
            curnode:node_watershed
            dem=[]
            curnode=self.myupstreams['list'][whichup]
            while not curnode is None:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_dem_corr(self,whichdem,whichreach=None,whichup=None):
        if not whichreach is None:
            nodeslist=self.myreaches['reaches'][whichreach]['baselist']
            dem=list(curnode.demcorr[whichdem] for curnode in nodeslist)
        elif not whichup is None:
            curnode:node_watershed
            dem=[]
            curnode=self.myupstreams['list'][whichup]
            while not curnode is None:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_slope(self,whichslope=None,whichreach=None,whichup=None):
        if whichslope is None:
            if not whichreach is None:
                nodeslist=self.myreaches['reaches'][whichreach]['baselist']
                slope=list(curnode.slope for curnode in nodeslist)
            elif not whichup is None:
                curnode:node_watershed
                slope=[]
                curnode=self.myupstreams['list'][whichup]
                while not curnode is None:
                    slope.append(curnode.slope)
                    curnode=curnode.down
        else:        
            if not whichreach is None:
                nodeslist=self.myreaches['reaches'][whichreach]['baselist']
                slope=list(curnode.slopecorr[whichslope]['value'] for curnode in nodeslist)
            elif not whichup is None:
                curnode:node_watershed
                slope=[]
                curnode=self.myupstreams['list'][whichup]
                while not curnode is None:
                    slope.append(curnode.slopecorr[whichslope]['value'])
                    curnode=curnode.down
        
        return slope

    def create_index(self):
        #incrément d'index depuis l'amont jusque l'exutoire final
        for curup in self.myupstreams['list']:
            curnode:node_watershed
            curnode=curup
            while not curnode is None:
                curnode.reachlevel +=1
                curnode=curnode.down

        #recherche de l'index max --> à l'exutoire
        self.maxlevels = self.parent.myoutlet.reachlevel
        self.maxstrahler=0
        self.myreaches['indexed']={}
        for i in range(1,self.maxlevels+1):
            self.myreaches['indexed'][i]=[]

        #création de listes pour chaque niveau
        for curreach in self.myreaches['reaches']:
            curdict=self.myreaches['reaches'][curreach]
            listreach=curdict['baselist']                       
            curlevel=listreach[0].reachlevel
            self.myreaches['indexed'][curlevel].append(curreach)

        #création de listes pour chaque amont
        #  on parcourt toutes les mailles depuis chaque amont et on ajoute les index de biefs qui sont différents
        for idx,curup in enumerate(self.myupstreams['list']):
            curdict=self.myupstreams[idx]={}
            curdict['up']=curup
            curdict['fromuptodown']=[]
            curdict['fromuptodown'].append(curup.reach)
            curnode=curup.down
            while not curnode is None:
                if curnode.reach!=curdict['fromuptodown'][-1]:
                    curdict['fromuptodown'].append(curnode.reach)
                curnode=curnode.down

        #création de l'indice de strahler
        self.myreaches['strahler']={}
        #on commence par ajouter les biefs de 1er niveau qui sont à coup sûr d'indice 1
        self.myreaches['strahler'][1]=self.myreaches['indexed'][1]
        for curreach in self.myreaches['strahler'][1]:
            self.set_strahler_in_nodes(curreach,1)

        #on parcourt les différents niveaux
        for i in range(2,self.maxlevels+1):
            listlevel=self.myreaches['indexed'][i]
            for curreach in listlevel:
                curup:node_watershed
                curup=self.myreaches['reaches'][curreach]['upstream']
                upidx=list(x.strahler for x in curup.upriver)
                sameidx=upidx[0]==upidx[-1]
                maxidx=max(upidx)

                curidx=maxidx
                if sameidx:
                    curidx+=1
                    if not curidx in self.myreaches['strahler'].keys():
                         #création de la liste du niveau supérieur
                         self.myreaches['strahler'][curidx]=[]
                         self.maxstrahler=curidx
                    
                self.myreaches['strahler'][curidx].append(curreach)
                self.set_strahler_in_nodes(curreach,curidx)


        myarray=WolfArray(mold=self.parent.subs)
        myarray.reset()
        curnode:node_watershed
        for curreach in self.myreaches['reaches']:
            curdict=self.myreaches['reaches'][curreach]
            listreach=curdict['baselist']
            for curnode in listreach:
                i=curnode.i
                j=curnode.j
                myarray.array[i,j]=curnode.strahler
        myarray.filename = self.parent.mydir+'\\Characteristic_maps\\Drainage_basin.strahler'
        myarray.write_all()
        myarray.reset()
        for curreach in self.myreaches['reaches']:
            curdict=self.myreaches['reaches'][curreach]
            listreach=curdict['baselist']
            for curnode in listreach:
                i=curnode.i
                j=curnode.j
                myarray.array[i,j]=curnode.reachlevel
        myarray.filename = self.parent.mydir+'\\Characteristic_maps\\Drainage_basin.reachlevel'
        myarray.write_all()
                 
    def set_strahler_in_nodes(self,whichreach,strahler):
        listnodes = self.myreaches['reaches'][whichreach]['baselist']
        curnode:node_watershed
        for curnode in listnodes:
            curnode.strahler = strahler

    def plot_dem(self,which=-1):
        mymarkers=['x','+','1','2','3','4']
        if which==-1:
            if not self.myplotter is None:
                fig=self.myplotter.add('All Reaches')
            else:
                fig=plt.figure()

            ax=fig.add_subplot(111)

            for curreach in self.myreaches['reaches']:
                x=np.array(self.get_x(whichreach=curreach))
                for idx,curdem in enumerate(listdem):
                    y=np.array(self.get_dem(curdem,whichreach=curreach))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)

                    ax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
            ax.legend()            
            fig.canvas.draw()

        elif which==-99:
            size=int(np.ceil(np.sqrt(self.nbreaches)))
            
            if not self.myplotter is None:
                fig=self.myplotter.add('reaches')
            else:
                fig=plt.figure()

            for index,curreach in enumerate(self.myreaches['reaches']):
                #curax=ax[int(np.floor(index/size)),int(np.mod(index,size))]
                curax=fig.add_subplot(size,size,index+1)

                curdict=self.myreaches['reaches'][curreach]
                x=np.array(self.get_x(whichreach=curreach))

                for idx,curdem in enumerate(listdem):
                    y=np.array(self.get_dem(curdem,whichreach=curreach))

                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)

                    curax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
            curax.legend()
            fig.canvas.draw()

        elif which==-98:
            size=int(np.ceil(np.sqrt(len(self.myupstreams['list']))))
            
            if not self.myplotter is None:
                fig=self.myplotter.add('reaches')
            else:
                fig=plt.figure()

            for idxup,curup in enumerate(self.myupstreams['list']):
                curax=fig.add_subplot(size,size,idxup+1)

                x=np.array(self.get_x(whichup=idxup))

                for idx,curdem in enumerate(listdem):
                    y=np.array(self.get_dem(curdem,whichup=idxup))
                    
                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)
                    curax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
                
            curax.legend()
            fig.canvas.draw()

        elif which>-1:
            if which<len(self.myupstreams['list']):
                if not self.myplotter is None:
                    fig=self.myplotter.add('Upstream n°'+str(which))
                else:
                    fig=plt.figure()

                ax=fig.add_subplot(111)
               
                x=np.array(self.get_x(whichup=which))
                for idx,curdem in enumerate(listdem):
                    y=np.array(self.get_dem(curdem,whichup=which))
                    
                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)
                    ax.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
                
            ax.legend()
            fig.canvas.draw()


    def plot_dem_and_corr(self,which=-1,whichdem='dem2'):
        
        if which<len(self.myupstreams['list']):
            if not self.myplotter is None:
                fig=self.myplotter.add('Upstream n°'+str(which))
            else:
                fig=plt.figure()
                fig.suptitle('Upstream n°'+str(which))   
            
            ax=fig.add_subplot(111)            
            
            x=np.array(self.get_x(whichup=which))
            y=np.array(self.get_dem(whichdem,whichup=which))
            
            xcorr=self.myupmin[which][whichdem][0]
            ycorr=self.myupmin[which][whichdem][1]
            
            xmask=np.ma.masked_where(y==99999.,x)
            ymask=np.ma.masked_where(y==99999.,y)

            ax.scatter(xmask,ymask,marker='x',label=whichdem)
            ax.scatter(xcorr,ycorr,marker='+',label='selected points')
            
            ax.legend()
            fig.canvas.draw()

            if not self.savedir=='':
                plt.savefig(self.savedir+'\\Up'+str(which)+'_'+whichdem+'.png')

    def plot_slope(self,which=-1):
        mymarkers=['x','+','1','2','3','4']
        if which==-1:
            if not self.myplotter is None:
                fig=self.myplotter.add('reaches')
            else:
                fig=plt.figure()
            
            ax=fig.add_subplot(111)

            for curreach in self.myreaches['reaches']:
                x=self.get_x(whichreach=curreach)
                for idx,curdem in enumerate(listdem):
                    y=self.get_slope(curdem,whichreach=curreach)
                    ax.scatter(x,y,marker=mymarkers[idx],label=curdem)
            fig.canvas.draw()
    
        elif which==-99:
            size=int(np.ceil(np.sqrt(self.nbreaches)))
            if not self.myplotter is None:
                fig=self.myplotter.add('reaches')
            else:
                fig=plt.figure()

            for index,curreach in enumerate(self.myreaches['reaches']):
                curax=fig.add_subplot(size,size,index+1)

                x=self.get_x(whichreach=curreach)

                for idx,curdem in enumerate(listdem):
                    y=self.get_slope(curdem,whichreach=curreach)
                    curax.scatter(x,y,marker=mymarkers[idx],label=curdem)
            curax.legend()
            fig.canvas.draw()

        elif which==-98:
            size=int(np.ceil(np.sqrt(len(self.myupstreams['list']))))

            if not self.myplotter is None:
                fig=self.myplotter.add('reaches')
            else:
                fig=plt.figure()

            for idxup,curup in enumerate(self.myupstreams['list']):
                curax=fig.add_subplot(size,size,idxup+1)
                x=self.get_x(whichup=idxup)

                for idx,curdem in enumerate(listdem):
                    y=self.get_slope(curdem,whichup=idxup)
                    curax.scatter(x,y,marker=mymarkers[idx],label=curdem)
            curax.legend()
            fig.canvas.draw()
    
    def write_slopes(self):
        #Uniquement les pentes rivières
        for curlist in listdem:
            slopes= WolfArray(self.parent.mydir+'\\Characteristic_maps\\Drainage_basin.slope')
            slopes.reset()
            for curreach in self.myreaches['reaches']:
                curdict=self.myreaches['reaches'][curreach]
                listreach=curdict['baselist']

                curnode:node_watershed
                for curnode in listreach:
                    i=curnode.i
                    j=curnode.j
                    slopes.array[i,j]=curnode.slopecorr[curlist]['value']

            slopes.filename = self.parent.mydir+'\\Characteristic_maps\\Drainage_basin.slope_corr_riv_'+curlist
            slopes.write_all()

    def slope_correctionmin(self):
        if not self.tslopemin is None:
            print(_('select min - river'))
            self.selectmin()
            print(_('slope correction min - river'))
            self.compute_slopescorr(self.myupmin)

    def slope_correctionmax(self):
        if not self.tslopemax is None:
            print(_('select max - river'))
            self.selectmax()
            print(_('slope correction max - river'))
            self.compute_slopescorr(self.myupmax)

    def selectmin(self):
        #Sélection des valeurs minimales afin de conserver une topo décroissante vers l'aval --> une pente positive
        self.myupmin={}
        
        #on initialise le dictionnaire de topo min pour chaque amont
        for idx,curup in enumerate(self.myupstreams['list']):
            self.myupmin[idx]={}

        curnode:node_watershed
        for curdem in listdem:
            print(_(curdem))
            for idx,curup in enumerate(self.myupstreams['list']):
                #on part de l'amont
                curnode=curup
                x=[]
                y=[]
                
                x.append(curnode.cums)
                
                if curdem=='cs':
                    basey=min(curnode.dem[curdem],curnode.dem['dem2'])
                else:
                    basey=curnode.dem[curdem]

                y.append(basey)
                curnode=curnode.down

                locs= self.parent.myresolution
                while not curnode is None:
                    if curdem=='cs':
                        yloc=min(curnode.dem[curdem],curnode.dem['dem2'])
                    else:
                        yloc=curnode.dem[curdem]
                    
                    #on ajoute la maille si la pente est suffisante, sinon cekla créera un trou dans le parcours
                    if (basey-yloc)/locs>self.tslopemin:
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs= self.parent.myresolution
                    else:
                        locs+= self.parent.myresolution

                    #if curnode.i==232 and curnode.j==226:
                    #    a=1

                    curnode=curnode.down

                #on stocke les vecteurs de coordonnées curvi et d'altitudes pour les zones respectant les critères
                self.myupmin[idx][curdem]=[x,y]

    def selectmax(self):
        #Sélection des valeurs maximales afin de conserver une topo décroissante vers l'aval --> une pente positive
        # on travaille sur base de la topo corrigée min
        self.myupmax={}
        
        #on initialise le dictionnaire de topo max pour chaque amont
        for idx,curup in enumerate(self.myupstreams['list']):
            self.myupmax[idx]={}

        ds=self.parent.myresolution
        curnode:node_watershed
        for curdem in listdem:
            print(_(curdem))
            for idx,curup in enumerate(self.myupstreams['list']):
                curnode=curup
                x=[]
                y=[]
                                
                basey=curnode.demcorr[curdem]['value']

                x.append(curnode.cums)
                y.append(basey)
                curnode=curnode.down

                locs= ds
                while not curnode is None:
                    yloc=curnode.demcorr[curdem]['value']

                    if (basey-yloc)/locs>self.tslopemax:
                        while len(x)>1 and (basey-yloc)/locs>self.tslopemax:
                            x.pop()
                            y.pop()
                            basey=y[-1]
                            locs+=ds
                        
                    if yloc<y[-1]:    
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs=ds

                    curnode=curnode.down

                self.myupmax[idx][curdem]=[x,y]

    def compute_slopescorr(self,whichdict:dict):
        curnode:node_watershed
        for curdem in listdem:
            print(_(curdem))
            for idx,curup in enumerate(self.myupstreams['list']):
                curdict=whichdict[idx][curdem]
                xmin=curdict[0]
                if len(xmin)>1:
                    ymin=curdict[1]
                    x=self.get_x(whichup=idx)

                    #on cale une fonction d'interpolation sur la sélection dans lequalle on a oublié les pentes faibles --> à trou
                    f=interpolate.interp1d(xmin,ymin, fill_value='extrapolate')
                    #on interpole sur tous les x --> on remplit les trous
                    y=f(x)
                    #calcul des pentes sur base des noeuds aval
                    slopes=self.compute_slope_down(x,y)

                    #on remplit le dictionnaire de résultat
                    curnode=curup
                    i=0
                    while not curnode is None:
                        #if curnode.i==232 and curnode.j==226:
                        #    a=1
                        curnode.demcorr[curdem]['parts'].append(y[i])
                        curnode.slopecorr[curdem]['parts'].append(slopes[i])
                        i+=1
                        curnode=curnode.down

        #calcul de la moyenne sur base des valeurs partielles
        for curdem in listdem:
            for curreach in self.myreaches['reaches']:
                nodeslist=self.myreaches['reaches'][curreach]['baselist']
                for curnode in nodeslist:
                    #if curnode.i==232 and curnode.j==226:
                    #    a=1
                    if len(nodeslist)<2:
                        if not self.tslopemin is None:
                            curnode.slopecorr[curdem]['value']=max(self.tslopemin,curnode.slope)
                        else:
                            curnode.slopecorr[curdem]['value']=self.tslopemin=1.e-4

                        if not self.tslopemax is None:
                            curnode.slopecorr[curdem]['value']=min(self.tslopemax,curnode.slope)
                    else:
                        curnode.demcorr[curdem]['value']=np.mean(curnode.demcorr[curdem]['parts'])
                        curnode.slopecorr[curdem]['value']=np.mean(curnode.slopecorr[curdem]['parts'])

                    #on vide les parts
                    curnode.demcorr[curdem]['parts']=[]
                    curnode.slopecorr[curdem]['parts']=[]

    def compute_slope_down(self,x,y):
        slope=[]
        for i in range(len(x)-1):
            slope.append((y[i+1]-y[i])/(x[i+1]-x[i]))
        slope.append(slope[-1])
        return slope

    def plot_all_in_notebook(self):
        
        self.myplotter = PlotNotebook()

        for i in range(self.nbreaches):
            self.plot_dem_and_corr(i,whichdem='cs')
        self.plot_dem()
        self.plot_slope(-98)
        self.plot_dem(-98)

class runoffsystem:
    '''Classe de l'ensemble des mailles de ruissellement d'un modèle 
    hydrologique WOLF'''   
    myupmin:dict
    mynodes:list
    
    parent=None
    myupstreams:dict 
    
    maxlevels:int
    maxstrahler:int

    tslopemin:float =None
    tslopemax:float =None

    def __init__(self,runoff:list,parent,thslopemin,
                thslopemax,*args, **kwargs):
        curnode:node_watershed

        self.parent=parent
        self.mynodes=runoff
        self.myupstreams={}
        #sélection des mailles qui ont une surface unitaire comme surface drainée
        areaup = pow(parent.myresolution,2)/1.e6
        self.myupstreams['list']=list(filter(lambda x: (x.uparea-areaup)<1.e-6 ,runoff))            

        self.tslopemin=thslopemin
        self.tslopemax=thslopemax

        self.slope_correctionmin()
        self.slope_correctionmax()
        
        return super().__init__(*args, **kwargs)

    def get_x(self,whichup=None):
        if not whichup is None:
            curnode:node_watershed
            x=[]
            curnode=self.myupstreams['list'][whichup]
            while not curnode.river:
                x.append(curnode.cums)
                curnode=curnode.down
            if len(x)==1:
                x.append(curnode.cums)
        else:
            x=[]

        return x

    def get_dem(self,whichdem,whichup=None):
        if not whichup is None:
            curnode:node_watershed
            dem=[]
            curnode=self.myupstreams['list'][whichup]
            while not curnode.river:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_dem_corr(self,whichdem,whichup=None):
        if not whichup is None:
            curnode:node_watershed
            dem=[]
            curnode=self.myupstreams['list'][whichup]
            while not curnode.river:
                dem.append(curnode.dem[whichdem])
                curnode=curnode.down
        return dem

    def get_slope(self,whichslope=None,whichup=None):
        if whichslope is None:
            if not whichup is None:
                curnode:node_watershed
                slope=[]
                curnode=self.myupstreams['list'][whichup]
                while not curnode.river:
                    slope.append(curnode.slope)
                    curnode=curnode.down
        else:        
            if not whichup is None:
                curnode:node_watershed
                slope=[]
                curnode=self.myupstreams['list'][whichup]
                while not curnode.river:
                    slope.append(curnode.slopecorr[whichslope]['value'])
                    curnode=curnode.down
        
        return slope

    def plot_dem(self,which=-1):
        mymarkers=['x','+','1','2','3','4']
        if which>-1:
            if which<len(self.myupstreams['list']):
                fig=plt.figure()
                fig.suptitle('Upstream n°'+str(which))               
                
                x=np.array(self.get_x(whichup=which))
                for idx,curdem in enumerate(listdem):
                    y=np.array(self.get_dem(curdem,whichup=which))
                    
                    xmask=np.ma.masked_where(y==99999.,x)
                    ymask=np.ma.masked_where(y==99999.,y)
                    plt.scatter(xmask,ymask,marker=mymarkers[idx],label=curdem)
                
            plt.legend()
        plt.show()

    def plot_dem_and_corr(self,which=-1,whichdem='dem2'):
        if which<len(self.myupstreams['list']):
            fig=plt.figure()
            fig.suptitle('Upstream n°'+str(which))               
            
            x=np.array(self.get_x(whichup=which))
            y=np.array(self.get_dem(whichdem,whichup=which))
            
            xcorr=self.myupmin[which][whichdem][0]
            ycorr=self.myupmin[which][whichdem][1]
            
            xmask=np.ma.masked_where(y==99999.,x)
            ymask=np.ma.masked_where(y==99999.,y)

            plt.scatter(xmask,ymask,marker='x',label=whichdem)
            plt.scatter(xcorr,ycorr,marker='+',label='selected points')
            
            plt.legend()
            plt.savefig(r'D:\OneDrive\OneDrive - Universite de Liege\Crues\2021-07 Vesdre\Simulations\Hydrologie\Up'+str(which)+'_'+whichdem+'.png')
            #plt.show()
    
    def write_slopes(self):
        #Uniquement les pentes runoff
        for curlist in listdem:
            slopes= WolfArray(self.parent.mydir+'\\Characteristic_maps\\Drainage_basin.slope')
            slopes.reset()
            curnode:node_watershed
            for curnode in self.mynodes:
                i=curnode.i
                j=curnode.j
                slopes.array[i,j]=curnode.slopecorr[curlist]['value']

            slopes.filename = self.parent.mydir+'\\Characteristic_maps\\Drainage_basin.slope_corr_run_'+curlist
            slopes.write_all()

    def slope_correctionmin(self):
        if not self.tslopemin is None:
            print(_('select min - runoff'))
            self.selectmin()
            print(_('slope correction min - runoff'))
            self.compute_slopescorr(self.myupmin)

    def slope_correctionmax(self):
        if not self.tslopemax is None:
            print(_('select max - runoff'))
            self.selectmax()
            print(_('slope correction max - runoff'))
            self.compute_slopescorr(self.myupmax)

    def selectmin(self):
        #Sélection des valeurs minimales afin de conserver une topo décroissante vers l'aval --> une pente positive
        self.myupmin={}
        
        #on initialise le dictionnaire de topo min pour chaque amont
        for idx,curup in enumerate(self.myupstreams['list']):
            self.myupmin[idx]={}

        ds=self.parent.myresolution
        curnode:node_watershed
        for curdem in listdem:
            print(_(curdem))
            for idx,curup in enumerate(self.myupstreams['list']):
                curnode=curup
                x=[]
                y=[]
                               
                if curdem=='cs':
                    basey=min(curnode.dem[curdem],curnode.dem['dem2'])
                else:
                    basey=curnode.dem[curdem]

                x.append(curnode.cums)
                y.append(basey)
                curnode=curnode.down

                locs=ds
                while not curnode is None:
                    if curdem=='cs':
                        yloc=min(curnode.dem[curdem],curnode.dem['dem2'])
                    else:
                        yloc=curnode.dem[curdem]
                    
                    if (basey-yloc)/locs>self.tslopemin:
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs=ds
                        if curnode.river:
                            break
                    else:
                        locs+=ds
                    curnode=curnode.down

                self.myupmin[idx][curdem]=[x,y]

    def selectmax(self):
        #Sélection des valeurs minimales afin de conserver une topo décroissante vers l'aval --> une pente positive
        self.myupmax={}
        
        #on initialise le dictionnaire de topo min pour chaque amont
        for idx,curup in enumerate(self.myupstreams['list']):
            self.myupmax[idx]={}

        ds=self.parent.myresolution
        curnode:node_watershed
        for curdem in listdem:
            print(_(curdem))
            for idx,curup in enumerate(self.myupstreams['list']):
                curnode=curup
                x=[]
                y=[]
                                
                '''
                if curdem=='cs':
                    basey=min(curnode.demcorr[curdem]['value'],curnode.demcorr['dem2']['value'])
                else:
                    basey=curnode.demcorr[curdem]['value']
                '''
                basey=curnode.demcorr[curdem]['value']

                x.append(curnode.cums)
                y.append(basey)
                curnode=curnode.down

                locs= ds
                while not curnode is None:
                    '''
                    if curdem=='cs':
                        yloc=min(curnode.demcorr[curdem]['value'],curnode.demcorr['dem2']['value'])
                    else:
                        yloc=curnode.demcorr[curdem]['value']
                    '''
                    yloc=curnode.demcorr[curdem]['value']

                    if (basey-yloc)/locs>self.tslopemax:
                        while len(x)>1 and (basey-yloc)/locs>self.tslopemax:
                            x.pop()
                            y.pop()
                            basey=y[-1]
                            locs+=ds

                    if yloc<y[-1]:    
                        x.append(curnode.cums)
                        y.append(yloc)
                        basey=yloc
                        locs=ds
                        if curnode.river:
                            break
                    
                    curnode=curnode.down
                    #if curnode.i==187 and curnode.j==207:
                    #    a=1
                        
                self.myupmax[idx][curdem]=[x,y]

    def compute_slopescorr(self,whichdict:dict):
        curnode:node_watershed
        for curdem in listdem:
            print(_(curdem))
            for idx,curup in enumerate(self.myupstreams['list']):
                curdict=whichdict[idx][curdem]
                xmin=curdict[0]
                if len(xmin)>1:                
                    ymin=curdict[1]
                    x=self.get_x(whichup=idx)

                    f=interpolate.interp1d(xmin,ymin, fill_value='extrapolate')
                    y=f(x)
                    slopes=self.compute_slope_down(x,y)

                    curnode=curup
                    i=0
                    while not curnode.river:
                        #if curnode.i==187 and curnode.j==207:
                        #    a=1
                        curnode.demcorr[curdem]['parts'].append(y[i])
                        curnode.slopecorr[curdem]['parts'].append(slopes[i])
                        i+=1
                        curnode=curnode.down
        #calcul de la moyenne sur base des valeurs partielles
        for curdem in listdem:
            for curnode in self.mynodes:
                #if curnode.i==187 and curnode.j==207:
                #    a=1
                if len(curnode.slopecorr[curdem]['parts'])<2:
                    #Ce cas particulier peut arriver si des mailles BV sont remplies par une zone plate qui s'étend en rivière
                    # Comme on ne recherche de mailles plus basses que dans la partie BV, il n'est pas possible de corriger les pentes
                    if not self.tslopemin is None:
                        curnode.slopecorr[curdem]['value']=max(self.tslopemin,curnode.slope)
                    else:
                        curnode.slopecorr[curdem]['value']=1.e-4

                    if not self.tslopemax is None:
                        curnode.slopecorr[curdem]['value']=min(self.tslopemax,curnode.slope)
                else:
                    curnode.demcorr[curdem]['value']=np.mean(curnode.demcorr[curdem]['parts'])
                    curnode.slopecorr[curdem]['value']=np.mean(curnode.slopecorr[curdem]['parts'])
            
                curnode.demcorr[curdem]['parts']=[]
                curnode.slopecorr[curdem]['parts']=[]

    def compute_slope_down(self,x,y):
        slope=[]
        for i in range(len(x)-1):
            slope.append((y[i+1]-y[i])/(x[i+1]-x[i]))
        slope.append(slope[-1])
        return slope

class watershed:
    '''Classe bassin versant'''
    
    mydir: str
    myresolution: float

    myoutlet=None

    subs: WolfArray

    mynodes:list
    mynodesindex:np.array
    myrivers:list
    myrunoff:list
    up=None

    mycoupled:list

    mysubs: dict
    nbsubs: int
    mystats: dict

    mycouplednodesxy:list
    mycouplednodesij:list
    myriversystem:riversystem
    myrunoffsystem:runoffsystem
    mycs:crosssections = None    

    def __init__(self,dir,thzmin=None,thslopemin=None,
                thzmax=None,thslopemax=None,
                mycs=None,
                computestats=False,plotstats=False,
                 *args, **kwargs):

        print(_('Read files...'))
        self.mydir=os.path.normpath(dir)

        self.subs= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.sub')
        self.nbsubs = ma.max(self.subs.array)
        self.myresolution = self.subs.dx

        f = open(self.mydir+'\\Coupled_pairs.txt', 'r')
        lines = f.read().splitlines()
        f.close()

        self.mycouplednodesxy=[]
        self.mycouplednodesij=[]

        if lines[0]=='COORDINATES':
            for xy in enumerate(lines[1:]):
                xup,yup,xdown,ydown=xy[1].split('\t')
                self.mycouplednodesxy.append([float(xup),float(yup),float(xdown),float(ydown)])
                self.mycouplednodesij.append([self.subs.get_ij_from_xy(float(xup),float(yup)),self.subs.get_ij_from_xy(float(xdown),float(ydown))])

        self.mynodesindex = np.zeros([self.subs.nbx,self.subs.nby],dtype=int)

        print(_('Initialization of nodes...'))
        self.init_nodes()
        
        if not mycs is None:
            print(_('Cross sections...'))
            self.set_crossSections(mycs)
            self.attrib_cs_to_nodes()

        print(_('Slopes corrections...'))
        self.myriversystem = riversystem(self.myrivers,self,thslopemin=thslopemin,thslopemax=thslopemax)
        self.myrunoffsystem = runoffsystem(self.myrunoff,self,thslopemin=thslopemin,thslopemax=thslopemax)

        if computestats or plotstats:
            print(_('Statistics...'))
            self.compute_stats(plotstats)

        print(_('Done!'))

        #Ecriture des résultats de correction des pentes
        self.write_dem()
        self.write_slopes()
        self.myriversystem.plot_all_in_notebook()

    def write_slopes(self):
        
        for curlist in listdem:
            curpath=self.mydir+'\\Characteristic_maps\\corrslopes\\'+curlist
            os.makedirs(curpath,exist_ok=True)
            slopes= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.slope')
        
            curnode:node_watershed
            for curnode in self.mynodes:
                i=curnode.i
                j=curnode.j
                slopes.array[i,j]=curnode.slopecorr[curlist]['value']

            slopes.filename = curpath +'\\Drainage_basin.slope_corr'
            slopes.write_all()

    def write_dem(self):
        
        for curlist in listdem:
            curpath=self.mydir+'\\Characteristic_maps\\corrdem\\'+curlist
            os.makedirs(curpath,exist_ok=True)
            dem= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basincorr.b')
        
            curnode:node_watershed
            for curnode in self.mynodes:
                i=curnode.i
                j=curnode.j
                dem.array[i,j]=curnode.demcorr[curlist]['value']

            dem.filename = curpath +'\\Drainage_basincorr.b'
            dem.write_all()

    def set_crossSections(self,cs):
        self.mycs=cs

    def attrib_cs_to_nodes(self):
        if not self.mycs is None:
            for curlist in self.mycs:
                for namecs in curlist.myprofiles:
                    curvert:wolfvertex
                    curcs=curlist.myprofiles[namecs]
                    
                    try:
                        curvert=curcs['bed']
                    except:
                        curvert=curlist.get_min(whichprofile=curcs)

                    i,j=self.subs.get_ij_from_xy(curvert.x,curvert.y)
                    curnode:node_watershed
                    curnode =self.mynodes[self.mynodesindex[i,j]]

                    if curnode.river:
                        if curnode.mycs is None:
                            curnode.mycs=[]
                        curnode.mycs.append(curcs)                
                        curnode.dem['cs']=min(curnode.dem['cs'],curvert.z)            

    def init_nodes(self):
        self.mynodes=[node_watershed() for i in range(self.subs.nbnotnull)]

        dem1= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.b')
        dem2= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basincorr.b')
        demdelta= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basindiff.b')
        slopes= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.slope',masknull=False)
        reaches= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.reachs')
        cnv= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.cnv')
        times= WolfArray(self.mydir+'\\Characteristic_maps\\Drainage_basin.time')

        dem2.array.mask = self.subs.array.mask

        nb=0
        for index,x in np.ndenumerate(self.subs.array):
            if(x>0):
                i=int(index[0])
                j=int(index[1])
                self.mynodesindex[i,j]=nb
                nb+=1

        curnode:node_watershed
        nb=0
        for index,x in np.ndenumerate(self.subs.array):
            if(x>0):
                i=int(index[0])
                j=int(index[1])
                curnode =self.mynodes[self.mynodesindex[i,j]]

                curnode.i = i
                curnode.j = j
                curnode.index=nb
                curnode.dem={}
                curnode.dem['dem1']=dem1.array[i,j]
                curnode.dem['dem2']=dem2.array[i,j]
                curnode.dem['cs']=99999.
                curnode.demdelta=demdelta.array[i,j]
                curnode.slope=slopes.array[i,j]

                curnode.slopecorr={}
                for curlist in listdem:
                    curnode.slopecorr[curlist]={}
                    curnode.slopecorr[curlist]['parts']=[]
                    curnode.slopecorr[curlist]['value']=curnode.slope

                curnode.demcorr={}
                for curlist in listdem:
                    curnode.demcorr[curlist]={}
                    curnode.demcorr[curlist]['parts']=[]
                    curnode.demcorr[curlist]['value']=curnode.dem['dem2']

                curnode.sub=int(x)
                curnode.time=times.array[i,j]
                curnode.uparea=cnv.array[i,j]
                curnode.river=not reaches.array.mask[i,j]
                if curnode.river:
                    curnode.reach=int(reaches.array[i,j])
                curnode.forced=False
                curnode.up=[]
                curnode.upriver=[]
                curnode.strahler=0
                curnode.reachlevel=0
                nb+=1
                
        #Liaison échanges forcés
        incr=slopes.dx
        for curexch in self.mycouplednodesij:
            i=int(curexch[0][0])
            j=int(curexch[0][1])
            curnode=self.mynodes[self.mynodesindex[i,j]]
            curnode.forced=True
            idown = int(curexch[1][0])
            jdown = int(curexch[1][1])
            curdown = self.mynodes[self.mynodesindex[idown,jdown]]
            curnode.down = curdown
            curdown.up.append(curnode)
            if curnode.river:
                curdown.upriver.append(curnode)
            curnode.incrs = incr * np.sqrt(pow(curdown.i-i,2)+pow(curdown.j-j,2))

        #Liaison hors échanges forcés
        for curnode in self.mynodes:
            if not curnode.forced:
                i=curnode.i
                j=curnode.j

                curtop=curnode.dem['dem2']
                diff=[dem2.array[i-1,j] - curtop,dem2.array[i+1,j] - curtop,dem2.array[i,j-1] - curtop,dem2.array[i,j+1] - curtop]
                mindiff = ma.min(diff)
                if mindiff<0:
                    index = diff.index(mindiff)
                    if index==0:
                        curdown = self.mynodes[self.mynodesindex[i-1,j]]
                    elif index==1:
                        curdown = self.mynodes[self.mynodesindex[i+1,j]]
                    elif index==2:
                        curdown = self.mynodes[self.mynodesindex[i,j-1]]
                    else:
                        curdown = self.mynodes[self.mynodesindex[i,j+1]]

                    curnode.down = curdown
                    curdown.up.append(curnode)
                    if curnode.river:
                        curdown.upriver.append(curnode)
                    curnode.incrs=incr
                else:
                    self.myoutlet = curnode

        #Rechreche de la pente dans les voisins en croix dans la topo non remaniée
        for curnode in self.mynodes:
            if not curnode.forced:
                i=curnode.i
                j=curnode.j

                curtop = curnode.dem['dem1']
                diff=[dem1.array[i-1,j] - curtop,dem1.array[i+1,j] - curtop,dem1.array[i,j-1] - curtop,dem1.array[i,j+1] - curtop,
                      dem1.array[i-1,j-1] - curtop,dem1.array[i+1,j+1] - curtop,dem1.array[i+1,j-1] - curtop,dem1.array[i-1,j+1] - curtop]
                mindiff = ma.min(diff)

                fact=1.
                if mindiff<0:
                    index = diff.index(mindiff)
                    if index>3:
                        fact=np.sqrt(2)

                curnode.sloped8 = -mindiff/(self.myresolution*fact)

        self.myrivers=list(filter(lambda x: x.river,self.mynodes))
        self.myrivers.sort(key=lambda x: x.dem['dem2'])
        self.myoutlet.incr_curvi()
        
        self.find_dem_subpixels()

        self.myrunoff=self.find_runoffnodes()

    def find_rivers(self,whichsub=0,whichreach=0):
        """
        Recherche des mailles rivières 
        @param whichsub : numéro du sous-bassin à traiter
        @param whicreach : numéro du tronçon à identifier
        """
        if whichsub>0 and whichsub<=self.nbsubs:
            if whichreach>0:
                myrivers=list(filter(lambda x: x.river and x.sub==whichsub and x.reach==whichreach,self.myrivers))
            else:
                myrivers=list(filter(lambda x: x.river and x.sub==whichsub,self.myrivers))
        else:
            if whichreach>0:
                myrivers=list(filter(lambda x: x.river and x.reach==whichreach,self.myrivers))
            else:
                myrivers=list(filter(lambda x: x.river,self.myrivers))

        myrivers.sort(key=lambda x: x.dem['dem2'])
        
        up=None
        if len(myrivers)>0:
            up=myrivers[-1]

        return myrivers,up

    def find_sub(self,whichsub=0):
        """
        Recherche des mailles du sou-bassin versant
        @param whichsub : numéro du sous-bassin à traiter
        """
        if whichsub>0 and whichsub<=self.nbsubs:
            mysub=list(filter(lambda x: x.sub==whichsub,self.mynodes))
        else:
            mysub=self.mynodes.copy

        mysub.sort(key=lambda x: x.dem['dem2'])
        
        return mysub

    def find_runoffnodes(self,whichsub=0):
        """
        Recherche des mailles du bassin versant seul (sans les rivières)    
        @param whichsub : numéro du sous-bassin à traiter
        """
        if whichsub>0 and whichsub<=self.nbsubs:
            myrunoff=list(filter(lambda x: not x.river and x.sub==whichsub,self.mynodes))
        else:
            myrunoff=list(filter(lambda x: not x.river,self.mynodes))

        myrunoff.sort(key=lambda x: x.dem['dem2'])
        
        return myrunoff

    def index_flatzone(self,listofsortednodes,threshold):
        curnode:node_watershed
        curflat:node_watershed

        curindex=0
        for curnode in listofsortednodes[-1:1:-1]:
            addone=False
            while curnode.slope<threshold and curnode.flatindex==-1:
                addone=True
                curnode.flatindex=curindex
                if curnode.down is None:
                    break
                curnode=curnode.down
            if addone:
                curindex+=1

        return curindex

    def find_flatnodes(self,listofsortednodes):
        """
        Recherche des mailles dans des zones de faibles pentes    
        @param listofsortednodes : liste triée de mailles
        """
        myflatnodes=list(filter(lambda x: x.flatindex>-1,listofsortednodes))
        
        return myflatnodes

    def find_flatzones(self,listofsortednodes,maxindex):
        """
        Recherche des mailles dans des zones de faibles pentes    
        @param listofsortednodes : liste triée de mailles
        """
        myflatzones=[[]] * maxindex
        for i in range(maxindex):
            myflatzones[i]=list(filter(lambda x: x.flatindex==i,listofsortednodes))
        
        return myflatzones

    def find_dem_subpixels(self):
        """
        Recherche des altitudes dans un mnt plus dense    
        """        
        dem10m=WolfArray(self.mydir+'\\mnt10m.bin')
        dem20m=WolfArray(self.mydir+'\\mnt20m.bin')

        demsubs={'dem10m':dem10m,'dem20m':dem20m}

        curnode:node_watershed
        for curdem in demsubs:
            locdem=demsubs[curdem]
            dx=locdem.dx
            dy=locdem.dy

            for curnode in self.mynodes:
                curi=curnode.i
                curj=curnode.j

                curx,cury=self.subs.get_xy_from_ij(curi,curj)
                
                decalx=(self.myresolution-dx)/2.
                decaly=(self.myresolution-dy)/2.
                x1=curx-decalx
                y1=cury-decaly
                x2=curx+decalx
                y2=cury+decaly

                i1,j1=locdem.get_ij_from_xy(x1,y1)
                i2,j2=locdem.get_ij_from_xy(x2,y2)

                curnode.dem[curdem]=np.min(locdem.array[i1:i2+1,j1:j2+1])

    def compute_stats(self,plot=False):
        
        self.mystats={}
        
        slopes=np.array(list(x.slope for x in self.mynodes))
        slopesrunoff=np.array(list(x.slope for x in list(filter(lambda x: not x.river,self.mynodes))))
        slopesriver=np.array(list(x.slope for x in list(filter(lambda x: x.river,self.mynodes))))

        curdict=self.mystats
        curdict['slopemin'] = np.min(slopes)
        curdict['slopemax'] = np.max(slopes)
        curdict['slopemedian'] = np.median(slopes)
        curdict['slopemean'] = np.mean(slopes)
        curdict['hist'] = slopes
        curdict['hist_watershed'] = slopesrunoff
        curdict['hist_reaches'] = slopesriver
        curdict['count_neg'] = np.count_nonzero(slopes < 0.)
        
        print(_('Min : '),curdict['slopemin'])
        print(_('Max : '),curdict['slopemax'])
        print(_('Median : '),curdict['slopemedian'])
        print(_('Mean : '),curdict['slopemean'])
        print(_('Non Zero : '),curdict['count_neg'])


        for curlist in listdem:
            curdict=self.mystats[curlist]={}
            
            slopes=np.array(list(x.slopecorr[curlist]['value'] for x in self.mynodes))
            slopesrunoff=np.array(list(x.slopecorr[curlist]['value'] for x in list(filter(lambda x: not x.river,self.mynodes))))
            slopesriver=np.array(list(x.slopecorr[curlist]['value'] for x in list(filter(lambda x: x.river,self.mynodes))))

            curdict['slopemin'] = np.min(slopes)
            curdict['slopemax'] = np.max(slopes)
            curdict['slopemedian'] = np.median(slopes)
            curdict['slopemean'] = np.mean(slopes)
            curdict['hist'] = slopes
            curdict['hist_watershed'] = slopesrunoff
            curdict['hist_reaches'] = slopesriver
            curdict['count_neg'] = np.count_nonzero(slopes < 0.)

            print(_(curlist))
            print(_('Min : '),curdict['slopemin'])
            print(_('Max : '),curdict['slopemax'])
            print(_('Median : '),curdict['slopemedian'])
            print(_('Mean : '),curdict['slopemean'])
            print(_('Non Zero : '),curdict['count_neg'])

        if plot:
            self.plot_stats()

    def plot_stats(self):

        self.myplotterstats = PlotNotebook()

        bin1=np.array([1.e-8,1.e-7,1.e-6,5.e-6])
        bin2=np.linspace(1.e-5,1e-3,num=20)
        bin3=np.linspace(2.e-3,1e-1,num=20)
        bin4=np.linspace(.11,1,num=100)
        bins=np.concatenate((bin1,bin2,bin3,bin4)) 
        
        fig=self.myplotterstats.add(_('Slope distribution - log'))
        ax:plt.axis

        ax = fig.add_subplot(311)
        ax.hist(self.mystats['hist'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xscale('log')
        ax.set_xlabel(_('All meshes'))

        for curlist in listdem:
            curdict=self.mystats[curlist]
            ax.hist(curdict['hist'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_subplot(312)
        ax.hist(self.mystats['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xscale('log')
        ax.set_xlabel(_('Watershed'))

        for curlist in listdem:
            curdict=self.mystats[curlist]
            ax.hist(curdict['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_subplot(313)
        ax.hist(self.mystats['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xscale('log')
        ax.set_xlabel(_('River'))

        for curlist in listdem:
            curdict=self.mystats[curlist]
            ax.hist(curdict['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)
        
        ax.legend()
        fig.canvas.draw()

        fig=self.myplotterstats.add(_('Slope distribution'))
        ax:plt.axis

        ax = fig.add_subplot(311)
        ax.hist(self.mystats['hist'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xlabel(_('All meshes'))

        for curlist in listdem:
            curdict=self.mystats[curlist]
            ax.hist(curdict['hist'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_subplot(312)
        ax.hist(self.mystats['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xlabel(_('Watershed'))

        for curlist in listdem:
            curdict=self.mystats[curlist]
            ax.hist(curdict['hist_watershed'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)

        ax = fig.add_subplot(313)
        ax.hist(self.mystats['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label='base')
        ax.set_xlabel(_('River'))

        for curlist in listdem:
            curdict=self.mystats[curlist]
            ax.hist(curdict['hist_reaches'],bins,cumulative=True,density=True,histtype=u'step',label=curlist)
        
        ax.legend()
        fig.canvas.draw()

        
    def analyze_flatzones(self):
        
        self.myplotterflat = PlotNotebook()

        ### Flat zones
        eps=1e-7
        #indexation des zones "indépendantes" de plats - ruissellement
        maxindex=self.index_flatzone(self.myrunoff,eps)
        #identification des mailles dans les zones
        myflatnodes=self.find_flatnodes(self.myrunoff)
        #création de listes avec les noeuds dans chaque zone
        myflats=self.find_flatzones(myflatnodes,maxindex)
        
        #calcul de la longueur de la zone de plat --> sommation du nombre de mailles
        lenflats=np.zeros((maxindex),dtype=np.int32)
        for i in range(maxindex):
            lenflats[i]=len(myflats[i])

        #indexation des zones "indépendantes" de plats - rivières
        maxindexrivers=self.index_flatzone(self.myrivers,eps)
        #création de listes avec les noeuds dans chaque zone - rivières
        myflatsrivers=self.find_flatzones(self.myrivers,maxindexrivers)

        #calcul de la longueur de la zone de plat --> sommation du nombre de mailles
        lenflatsrivers=np.zeros((maxindexrivers),dtype=np.int32)
        for i in range(maxindexrivers):
            lenflatsrivers[i]=len(myflatsrivers[i])

        fig:mplfig.Figure
        fig=self.myplotterflat.add("Nb nodes in flat area")
        ax=fig.add_subplot(211)
        mybins=np.arange(0.5,np.max(lenflats),1.)
        myticks=np.arange(1,np.ceil(np.max(lenflats)),1)
        ax.hist(lenflats,bins=mybins)
        ax.set_xlabel(_('Nb nodes in flat area - runoff'))
        ax.set_xticks(myticks)
        ax.set_xbound(.5,np.max(lenflats))
        ax.set_ylabel('Nb flat areas')
        ax.set_yscale('log')

        ax=fig.add_subplot(212)
        mybinsrivers=np.arange(0.5,np.max(lenflatsrivers),1.)
        myticksrivers=np.arange(1,np.ceil(np.max(lenflatsrivers)),1)
        ax.hist(lenflatsrivers,bins=mybinsrivers)
        ax.set_xlabel(_('Nb nodes in flat area - rivers'))
        ax.set_xticks(myticksrivers)
        ax.set_xbound(.5,np.max(lenflatsrivers))
        ax.set_ylabel('Nb flat areas')
        ax.set_yscale('log')

        fig=self.myplotterflat.add("Nb nodes in flat area")
        ax=fig.add_subplot(211)
        ax.hist(lenflats,bins=mybins,cumulative=True,density=True)
        ax.set_xlabel(_('Nb nodes in flat area - runoff'))
        ax.set_xticks(myticks)
        ax.set_xbound(.5,np.max(lenflats))
        ax.set_ylabel('Cumulative flat areas')
        #ax.set_yscale('log')

        ax=fig.add_subplot(212)
        ax.hist(lenflatsrivers,bins=mybinsrivers,cumulative=True,density=True)
        ax.set_xlabel(_('Nb nodes in flat area - rivers'))
        ax.set_xticks(myticksrivers)
        ax.set_xbound(.5,np.max(lenflatsrivers))
        ax.set_ylabel('Cumulative flat areas')
        #ax.set_yscale('log')
        fig.canvas.draw()

        #Tri des pentes dans différentes listes
        
        #toutes les mailles
        sdown=[]
        sup=[]
        for curflat in myflats:
            for curnode in curflat:
                #recherche de la pente aval plus grande que le seuil
                sdown.append(curnode.slope_down(eps))
                #recherche de la pente amont moyenne - uniquement pour les mailles qui ont une pente supérieure au seuil
                sup.append(curnode.mean_slope_up(eps))

        sflat=[]
        sdownraw=[]
        for curflat in myflats:
            for curnode in curflat:
                #pente de la maille aval
                sdownraw.append(curnode.down.slope) 
                #pente courante
                sflat.append(curnode.slope) 

        #mailles rivières
        sdownriv=[]
        supriv=[]
        suponlyriv=[]
        for curflat in myflatsrivers:
            for curnode in curflat:
                #recherche de la pente aval plus grande que le seuil
                sdownriv.append(curnode.slope_down(eps))
                #recherche de la pente amont moyenne - uniquement pour les mailles qui ont une pente supérieure au seuil
                supriv.append(curnode.mean_slope_up(eps))
                #recherche de la pente amont > seuil 
                suponlyriv.append(curnode.slope_upriver(eps))

        sdownd8=[]
        suponlyriv1=[]
        for curflat in myflatsrivers:
            for curnode in curflat:
                #pente aval selon voisines D8
                sdownd8.append(curnode.sloped8) 
                #recherche de la pente amont > seuil 
                suponlyriv1.append(curnode.slope_upriver(eps))

        sflatriver=[]
        sdownrawriver=[]
        sd8rawriver=[]
        for curflat in myflatsrivers:
            if len(curflat)==1:
                for curnode in curflat:
                    if not curnode.down is None:
                        sd8rawriver.append(curnode.sloped8)
                        sdownrawriver.append(curnode.down.slope)
                        sflatriver.append(curnode.slope)

        
        #tracage des graphiques
        fig=self.myplotterflat.add("Scatter plots")
        ax=fig.add_subplot(211)
        ax.scatter(sdownrawriver,sflatriver,marker='o',label='slope down vs flat slope')
        ax.scatter(sdownriv,suponlyriv,marker='+',label='slope down vs slope d8')
        ax=fig.add_subplot(212)
        ax.scatter(sdownraw,sflat,marker='0',label='slope down vs flat slope')
        ax.scatter(sdown,sup,marker='+',label='slope down vs slope up')
        fig.canvas.draw()

        fig=self.myplotterflat.add("Scatter plots 2")
        curax=fig.add_subplot(221)
        curax.scatter(sdown,sup,marker='+')
        curax.set_xlabel(_('Slope down [-]'))
        curax.set_ylabel(_('Mean slope up [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.55)
        curax.set_ybound(0,.55)
        curax.set_title('Runoff')

        curax=fig.add_subplot(222)
        curax.scatter(sdownriv,supriv,marker='+')
        curax.set_xlabel(_('Slope down [-]'))
        curax.set_ylabel(_('Mean slope up [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.55)
        curax.set_ybound(0,.55)
        curax.set_title('River')

        curax=fig.add_subplot(223)
        curax.scatter(sdownriv,suponlyriv,marker='+')
        curax.set_xlabel(_('Slope down [-]'))
        curax.set_ylabel(_('Slope up only river [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.55)
        curax.set_ybound(0,.55)
        curax.set_title('River')

        curax=fig.add_subplot(224)
        curax.scatter(sdownd8,suponlyriv1,marker='+')
        curax.set_xlabel(_('Slope D8 [-]'))
        curax.set_ylabel(_('Slope up only river [-]'))
        curax.set_aspect('equal','box')
        curax.set_xbound(0,.3)
        curax.set_ybound(0,.3)
        curax.set_title('River')
        fig.canvas.draw()
