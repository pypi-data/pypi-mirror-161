
from os import path

#from ..color_constants import *
from ..PyVertexvectors import *
from ..PyVertex import cloud_vertices,wolfvertex
from ..PyTranslate import _    
    
class forced_exchanges:
    
    def __init__(self,workingdir='') -> None:
        
        self.type='COORDINATES'        
        self.mypairs=[]
        self.mycloudup=cloud_vertices()
        self.myclouddown=cloud_vertices()
        
        self.mysegs = Zones()
        self.myzone=zone(name='segments_fe')
        self.mysegs.add_zone(self.myzone)
    
        self.mycloudup.myprop.color=getIfromRGB((0,238,0))
        self.mycloudup.myprop.filled=True
        self.myclouddown.myprop.color=getIfromRGB((255,52,179))
        self.myclouddown.myprop.filled=True
        
        fname=path.join(workingdir,'Coupled_pairs.txt')
        if path.exists(fname):
            f=open(fname,'rt')
            content = f.read().splitlines()
            f.close()
            
            self.type = content[0]
            idx=1
            for curline in content[1:]:
                coords=curline.split('\t')
                coords = [float(x) for x in coords]
                self.mypairs.append(coords)
                
                vert1 = wolfvertex(coords[0],coords[1])
                vert2 = wolfvertex(coords[2],coords[3])
                
                myseg = vector(name='fe'+str(idx))
                myseg.myprop.width = 2
                myseg.myprop.color = getIfromRGB((0,0,128))
                myseg.add_vertex([vert1,vert2])
                self.myzone.add_vector(myseg)
                
                self.mycloudup.add_vertex(vert1)
                self.myclouddown.add_vertex(vert2)
                idx+=1
                
            self.myzone.find_minmax(True)
        
    def paint(self):
        self.mycloudup.plot()
        self.myclouddown.plot()
        self.mysegs.plot()