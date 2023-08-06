import numpy as np
import laspy
from laspy.compression import LazBackend
from PIL import Image
from os.path import exists,join
import matplotlib.pyplot as plt
from os import stat,remove,listdir,scandir
import pathlib
import math
from time import sleep

from .lazviewer import viewer
from .PyWMS import getWalonmap

'''
Importation et visualisation de données LAS et LAZ

@author Pierre Archambeau
'''

class xyz_laz():
    '''
    Classe de gestion des fichiers XYZ+Class issus d'un gros fichier laz
    '''
    
    def __init__(self,fn='',format='las',to_read=True) -> None:
        self.origx = -99999.
        self.origy = -99999.
        self.endx  = -99999.
        self.endy  = -99999.
        self.format = format
        
        if fn !='':
            self.filename = fn
            parts = fn.split('_')
            self.origx = float(parts[3])    
            self.origy = float(parts[4])  
            
            dx = 2500.
            dy = 3500.
            
            gridinfo=join(pathlib.Path(fn).parent,'gridinfo.txt')
            if exists(gridinfo):
                with open(gridinfo,'r') as f:
                    myinfos=f.read().splitlines()
                    myinfos[0]=np.float32(myinfos[0].split(','))
                    myinfos[1]=np.float32(myinfos[1].split(','))
                    myinfos[2]=np.float32(myinfos[2].split(','))
                    dx = (myinfos[0][1]-myinfos[0][0])/myinfos[2][0]
                    dy = (myinfos[1][1]-myinfos[1][0])/myinfos[2][1]
            
            self.endx = self.origx + dx
            self.endy = self.origy + dy  
            
            if to_read:
                 self.read_bin_xyz()

    def split(self,dir_out,nbparts):
        
        xparts = np.linspace(self.origx,self.endx,nbparts+1)
        yparts = np.linspace(self.origy,self.endy,nbparts+1)
        dx = (self.endx-self.origx)/nbparts
        dy = (self.endy-self.origy)/nbparts
        
        for curx in xparts[:-1]:
            for cury in yparts[:-1]:
                with open(join(dir_out,'LIDAR_2013_2014_'+str(int(curx))+'_'+str(int(cury))+'_xyz.bin'),'wb') as f:
                    
                    curbounds = [[curx,curx+dx],[cury,cury+dy]]
                    mypts = find_pointsXYZ(self.data,curbounds)
                    if len(mypts)>0:
                        f.write(np.int32(mypts.shape[0]))
                        f.write(np.float32(mypts[:,0]).tobytes())
                        f.write(np.float32(mypts[:,1]).tobytes())
                        f.write(np.float32(mypts[:,2]).tobytes())
                        f.write(np.int8(mypts[:,3]).tobytes())
    
    def get_bounds(self):
        return ((self.origx,self.endx),(self.origy,self.endy))
        
    def test_bounds(self,bounds):
        
        x1=bounds[0][0]
        x2=bounds[0][1]
        y1=bounds[1][0]
        y2=bounds[1][1]
        
        mybounds = self.get_bounds()

        test = not(x2 < mybounds[0][0] or x1 > mybounds[0][1] or y2 < mybounds[1][0] or y1 > mybounds[1][1])
    
        return test

    def read_bin_xyz(self):
        '''
        Lecture d'un fichier binaire de points XYZ+classification généré par la fonction sort_grid_np
        Le format est une succession de trame binaire de la forme :
        
        nbpoints (np.int32)
        X[nbpoints] (np.float32)
        Y[nbpoints] (np.float32)
        Z[nbpoints] (np.float32)
        Classif[nbpoints] (np.int8)
        
        Il est possible de récupérer une matrice numpy shape(nbtot,4) 
        ou un objet laspy via l'argument 'out' (par défaut à 'las')
        '''
        fn=self.filename
        
        fnsize=stat(fn).st_size
        nb=0
        count=0
        myret=[]
        with open(fn,'rb') as f:
            while count<fnsize:
                nbloc = np.frombuffer(f.read(4),np.int32)[0]
                nb+=nbloc
                x=np.frombuffer(f.read(nbloc*4),np.float32)
                y=np.frombuffer(f.read(nbloc*4),np.float32)
                z=np.frombuffer(f.read(nbloc*4),np.float32)
                classi=np.frombuffer(f.read(nbloc),np.int8)
                count+=4+nbloc*(3*4+1)
                
                if myret==[]:
                    dt=[('x',np.float32),('y',np.float32),('z',np.float32),('classification',np.int8)]
                    myret=np.array([x,y,z,classi]).transpose()
                else:
                    myret=np.concatenate((myret,np.array([x,y,z,classi]).transpose()))
        
        self.data = myret
        if self.format=='las':
            self.to_las()

    def to_las(self):
        if self.format=='las':
            return
        else:       
            # self.data=xyz_to_las(self.data) 
            self.format='las'        

class xyz_laz_grid():
    
    def __init__(self,mydir) -> None:
        self.mydir = mydir

        gridinfo=join(mydir,'gridinfo.txt')
        if exists(gridinfo):
            with open(gridinfo,'r') as f:
                myinfos=f.read().splitlines()
                
                self.origx,self.endx=np.float32(myinfos[0].split(','))
                self.origy,self.endy=np.float32(myinfos[1].split(','))
                self.nbx,self.nby=np.int32(myinfos[2].split(','))
                self.genfile = myinfos[3]
                
                self.dx = (self.endx-self.origx)/float(self.nbx)
                self.dy = (self.endy-self.origy)/float(self.nby)
    
    def scan(self,bounds):

        x1=bounds[0][0]
        x2=bounds[0][1]
        y1=bounds[1][0]
        y2=bounds[1][1]
        
        file1= self.genfile.split('x1')[0]
        file2= self.genfile.split('y1')[-1]
        
        data=[]
                
        for x in range(int(self.origx),int(self.endx),int(self.dx)):
            for y in range(int(self.origy),int(self.endy),int(self.dy)):
                locbounds=np.float64(((x,x+self.dx),(y,y+self.dy)))
                test = not(x2 < locbounds[0][0] or x1 > locbounds[0][1] or y2 < locbounds[1][0] or y1 > locbounds[1][1])
                if test:
                    fxyz=file1+str(int(x))+'_'+str(int(y))+file2
                    locxyz=xyz_laz(join(self.mydir,fxyz))
                    data.append(locxyz.data)
        
        if len(data)>0:
            retdata=find_pointsXYZ(np.concatenate(data),bounds)

        return retdata          
    
    def split_xyz(self,dirout):
        
        for entry in scandir(self.mydir):
            if entry.is_file():
                if entry.name.endswith('.bin'):
                    myxy=xyz_laz(entry.path)
                    myxy.split(dirout,10)
                    print(entry.name)

    def sort_grid_np(self,fn_in,fn_out,bounds,gridsize,chunksize=5000000):
        
        xbounds=bounds[0]
        ybounds=bounds[1]
        
        xloc = np.linspace(xbounds[0],xbounds[1],gridsize[0]+1)
        yloc = np.linspace(ybounds[0],ybounds[1],gridsize[1]+1)
        
        fn=join(pathlib.Path(fn_out).parent,'gridinfo.txt')
        if exists(fn):
            remove(fn)
        with open(fn,'w') as f:
            f.write(str(int(xbounds[0]))+','+str(int(xbounds[1]))+'\n')
            f.write(str(int(ybounds[0]))+','+str(int(ybounds[1]))+'\n')
            f.write(str(int(gridsize[0]))+','+str(int(gridsize[1])))
            f.write(fn_out+'_'+'x1'+'_'+'y1'+'_xyz.bin')

        k=0
        with laspy.open(fn_in,laz_backend=LazBackend.Laszip) as f:
            nb = (f.header.point_count // chunksize) +1
            print('Points from Header:', f.header.point_count)
        
            #création des objets d'écriture
            writers=[]
            for i in range(gridsize[0]):
                writers.append([])
                for j in range(gridsize[1]):
                    fn=fn_out+'_'+str(int(xloc[i]))+'_'+str(int(yloc[j]))+'_xyz.bin'
                    if exists(fn):
                        remove(fn)
                    writers[i].append(open(fn, "wb"))

            for las in f.chunk_iterator(chunksize):       
                print(k,' / ',nb)
                for i in range(gridsize[0]):
                    for j in range(gridsize[1]):
                        mypts=find_points(las,(xloc[i],xloc[i+1]),(yloc[j],yloc[j+1]))
                        if len(mypts)>0:
                            print(len(mypts))
                            
                            print(int(xloc[i]),int(yloc[j]))
                            writers[i][j].write(np.int32(len(mypts)))
                            
                            writers[i][j].write(np.float32(mypts.x).tobytes())
                            writers[i][j].write(np.float32(mypts.y).tobytes())
                            writers[i][j].write(np.float32(mypts.z).tobytes())
                            writers[i][j].write(np.int8(mypts.classification).tobytes())

                k+=1
                print('--')
                
        self.origx = xbounds[0]
        self.origy = ybounds[0]
        self.endx = xbounds[1]
        self.endy = ybounds[1]
        self.dx = (self.endx-self.origx)/float(self.nbx)
        self.dy = (self.endy-self.origy)/float(self.nby)
        self.genfile=fn_out+'_'+'x1'+'_'+'y1'+'_xyz.bin'

def xyzlaz_scandir(mydir,bounds):
    
    first=[]
    for curfile in listdir(mydir):
        if curfile.endswith('.bin'):
            mydata = xyz_laz(join(mydir,curfile),format='numpy',to_read=False)
            if mydata.test_bounds(bounds):
                print(curfile)
                mydata.read_bin_xyz()
                first.append(mydata.data)

    for entry in scandir(mydir):
        if entry.is_dir():
            locf=xyzlaz_scandir(entry,bounds)
            if len(locf)>0:
                first.append(locf)
    
    retfirst=[]

    if len(first)>0:
        retfirst=find_pointsXYZ(np.concatenate(first),bounds)

    return retfirst

def find_pointsXYZ(xyz,bounds):
    
    xb=bounds[0]
    yb=bounds[1]
    # Get arrays which indicate invalid X, Y, or Z values.
    X_valid = (xb[0] <= xyz[:,0]) & (xb[1] >= xyz[:,0])
    Y_valid = (yb[0] <= xyz[:,1]) & (yb[1] >= xyz[:,1])
    good_indices = np.where(X_valid & Y_valid)[0]          
    return xyz[good_indices]

def find_points(las,xb,yb):
    # Get arrays which indicate invalid X, Y, or Z values.
    X_valid = (xb[0] <= las.x) & (xb[1] >= las.x)
    Y_valid = (yb[0] <= las.y) & (yb[1] >= las.y)
    good_indices = np.where(X_valid & Y_valid)[0]          
    return las[good_indices]

def clip_data_xyz(dir_in,fn_out,bounds):
    
    myxyz = xyzlaz_scandir(dir_in,bounds)
    np.savez_compressed(fn_out,myxyz)
    
def clip_data_laz(fn_in,fn_out,bounds,chunksize=5000000):
    pts=[]
    k=0
    xbounds=bounds[0]
    ybounds=bounds[1]
    with laspy.open(fn_in,laz_backend=LazBackend.Laszip) as f:
        nb = (f.header.point_count // chunksize) +1
        print('Points from Header:', f.header.point_count)
        with laspy.open(fn_out, mode="w", header=f.header) as writer:
            for las in f.chunk_iterator(chunksize):       
                print(k,' / ',nb)
                mypts=find_points(las,xbounds,ybounds)
                if len(mypts)>0:
                    pts.append(mypts)
                    print(len(mypts))
                    writer.write_points(mypts)
                k+=1
                print('--')
    pts=[]
                
def read_laz(fn:str):
    if fn.endswith('.npz'):
        return np.load(fn)['arr_0']
    elif fn.endswith('.laz') or fn.endswith('.las'):
        with laspy.open(fn,laz_backend=LazBackend.Laszip) as f:
            return f.read()        

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def get_Orthos_Walonmap(bounds,fn,cat='IMAGERIE/ORTHO_2012_2013',size=3000):
    '''
    Récupération des orthos depuis Walonmap
    fn = filename sans extension --> .png sera ajouté automatiquement
    
    catégories possibles :
     - 'IMAGERIE/ORTHO_2012_2013'
     - 'IMAGERIE/ORTHO_2015'
     - 'IMAGERIE/ORTHO_2021'
     - 'IMAGERIE/ORTHO_2006_2007'
    '''
    
    resmin=.3
    xbounds=bounds[0]
    ybounds=bounds[1]
    dx = xbounds[1]-xbounds[0]
    dy = ybounds[1]-ybounds[0]
    
    sizex=size
    sizey=size
    if dx>dy:
        sizey=math.ceil(float(size)*float(dy/dx))
    elif dx<dy:
        sizex=math.ceil(float(size)*float(dx/dy))
        
    resx = dx/float(size)
    resy = dy/float(size)
    
    if resx<=resmin and resy <=resmin:    
        try:
            im = Image.open(getWalonmap(cat,xbounds[0],ybounds[0],xbounds[1],ybounds[1],sizex,sizey,tofile=False))
        except:
            im = Image.open(getWalonmap(cat,xbounds[0],ybounds[0],xbounds[1],ybounds[1],sizex/2,sizey/2,tofile=False))
    elif resx>resmin and resy <=resmin:    
        nbx = math.ceil(resx/resmin)
        liste=[]
        x1=xbounds[0]
        dx = dx/float(nbx)
        for i in range(nbx):
            liste.append(Image.open(getWalonmap(cat,x1,ybounds[0],x1+dx,ybounds[1],sizex,sizey,tofile=False)))
            sleep(.5)
            x1+=dx
        im = liste[0]
        for i in range(1,nbx):
            im = get_concat_h(im,liste[i])
    elif resx<=resmin and resy >resmin:    
        nby= math.ceil(resy/resmin)
        liste=[]
        y1=ybounds[0]
        dy = dy/float(nby)
        for j in range(nby):
            liste.append(Image.open(getWalonmap(cat,xbounds[0],y1,xbounds[1],y1+dx,sizex,sizey,tofile=False)))
            sleep(.5)
            y1+=dy
        im = liste[0]
        for j in range(1,nby):
            im = get_concat_v(liste[j],im)
    elif resx>resmin and resy >resmin:    
        nbx = math.ceil(resx/resmin)
        nby = math.ceil(resy/resmin)

        liste=[]

        x1=xbounds[0]
        y1=ybounds[0]

        dx = dx/float(nbx)
        dy = dy/float(nby)

        print('Awaiting image from Walonmap - be patient !')
        for i in range(nbx):
            liste.append([])
            y1=ybounds[0]
            for j in range(nby):
                liste[i].append(Image.open(getWalonmap(cat,x1,y1,x1+dx,y1+dy,sizex,sizey,tofile=False)))
                y1+=dy
                print(str(i)+'/'+str(nbx-1)+' -- '+str(j)+'/'+str(nby-1))
                sleep(.5)
            x1+=dx
            print('--')

        for i in range(nbx):
            im = liste[i][0]
            for j in range(1,nby):
                im = get_concat_v(liste[i][j],im)
            liste[i][0]=im
        
        im = liste[0][0] 
        for i in range(1,nbx):          
            im = get_concat_h(im,liste[i][0])                    

    Image.Image.save(im,fn +'.png')
    with open(fn+'.png_bounds.txt','w') as f:
        f.write(str(xbounds[0])+','+str(xbounds[1])+'\n')
        f.write(str(ybounds[0])+','+str(ybounds[1]))

def get_colors(las,which_colors,imsize=2000,fname=''):
    
    if type(las) is laspy.LasData:
        nb = las.header.point_count
    else:
        nb = len(las)
    
    colors=np.ones((nb,4),dtype=np.float32)
    
    if which_colors==0:
        '''
        - Hors-sol (building, toits et autres) - Code 1;
        - Sol (y compris talus et digues) - Code 2;
        - Végétation haute (y compris la végétation linéaire) - Code 4;
        - Eau - Code 9;
        - Pont – Code 10.
        '''
        if type(las) is laspy.LasData:
            myclass = las.classification
        else:
            myclass = np.int8(las[:,3])
            
        colors[myclass==1]=[.5,.5,.5,1.]
        colors[myclass==2]=[.5,.25,.25,1.]
        colors[myclass==4]=[0.,0.5,0.,1.]
        colors[myclass==9]=[0.,0.5,1.,1.]
        colors[myclass==10]=[1,0.2,0.2,1.]
    elif which_colors==1 and fname != '':
        im=Image.open(fname)
        width = im.width
        height = im.height
        
        if exists(fname+'_bounds.txt'):
            with open((fname+'_bounds.txt'),'r') as f:
                mylines=f.read().splitlines()
                xb = np.float64(mylines[0].split(','))
                yb = np.float64(mylines[1].split(','))

        myPPNC = np.asarray(im)
        
        if type(las) is laspy.LasData:
            x = las.x
            y = las.y
        else:
            x = las[:,0]
            y = las[:,1]

        i = np.int16((x-xb[0])/(xb[1]-xb[0])*(width-1))
        j = np.int16((yb[1]-y)/(yb[1]-yb[0])*(height-1))
        
        # print(np.max(i),np.max(j))
        colors=myPPNC[j,i]/255.     
        
    else:
        if which_colors==2013:
            mycat='IMAGERIE/ORTHO_2012_2013'
        elif which_colors==2015:
            mycat='IMAGERIE/ORTHO_2015'
        elif which_colors==2021:
            mycat='IMAGERIE/ORTHO_2021'
        elif which_colors==2006:
            mycat='IMAGERIE/ORTHO_2006_2007'

        if type(las) is laspy.LasData:
            x = las.x
            y = las.y
        else:
            x = las[:,0]
            y = las[:,1]
        
        mins = np.int32(np.amin(np.vstack((x,y)).transpose(),axis=0))
        maxs = np.int32(np.amax(np.vstack((x,y)).transpose(),axis=0))
        width = min(int((maxs[0]-mins[0])/.3),imsize)
        height = min(int((maxs[1]-mins[1])/.3),imsize)
        
        im = Image.open(getWalonmap(mycat,mins[0],mins[1],maxs[0],maxs[1],width,height,tofile=False))
        myPPNC = np.asarray(im)
        
        i = np.int16((x-mins[0])/(maxs[0]-mins[0])*(imsize-1))
        j = np.int16((maxs[1]-y)/(maxs[1]-mins[1])*(imsize-1))
        colors=myPPNC[j,i]/255.
        
    return colors
        
def myviewer(las,which_colors,fname=''):

    if type(las) is list:
        xyz=[]
        for mypts in las:
            xyz.append(np.vstack((mypts.x,mypts.y,mypts.z)).transpose())
        xyz=np.concatenate(xyz)
    elif type(las) is laspy.LasData:
        xyz = np.vstack((las.x,las.y,las.z)).transpose()
    else:
        xyz=las[:,:3]

    colors = get_colors(las,which_colors,fname=fname)
            
    v=viewer(xyz,colors)
    v.set(point_size=.05)
    return v
