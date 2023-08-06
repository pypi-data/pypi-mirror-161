from time import sleep
import wx
from os import path,scandir
import wx

from .wolf_array import WolfArray,getkeyblock
from .PyTranslate import _
from .PyDraw import WolfMapViewer,imagetexture
from .PyParams import Wolf_Param
from .PyVertexvectors import Grid
from .RatingCurve import SPWMIGaugingStations,SPWDCENNGaugingStations
from .PyGuiHydrology import GuiHydrology
from .Results2DGPU import wolfres2DGPU
from .hydrology.Catchment import Catchment
from .hydrology.forcedexchanges import forced_exchanges
from .mesh2d.wolf2dprev import *

class GenMapManager(wx.Frame):
    allviews:WolfMapViewer

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def add_grid(self):
        mygrid=Grid(1000.)
        self.allviews.add_object('vector',newobj=mygrid,ToCheck=False,id='Grid')

    def add_WMS(self):
        xmin=0
        xmax=0
        ymin=0
        ymax=0
        orthos={'IMAGERIE':{'1971':'ORTHO_1971','1994-2000':'ORTHO_1994_2000',
                        '2006-2007':'ORTHO_2006_2007',
                        '2009-2010':'ORTHO_2009_2010',
                        '2012-2013':'ORTHO_2012_2013',
                        '2015':'ORTHO_2015','2016':'ORTHO_2016','2017':'ORTHO_2017',
                        '2018':'ORTHO_2018','2019':'ORTHO_2019','2020':'ORTHO_2020',
                        '2021':'ORTHO_2021'}}
        for idx,(k,item) in enumerate(orthos.items()):
            for kdx,(m,subitem) in enumerate(item.items()):
                self.allviews.add_object(which='wmsback',
                            newobj=imagetexture('PPNC',m,k,subitem,
                            self.allviews,xmin,xmax,ymin,ymax,-99999,1024),
                            ToCheck=False,id='PPNC '+m)
        self.allviews.add_object(which='wmsback',
                    newobj=imagetexture('PPNC','Orthos France','OI.OrthoimageCoverage.HR','',
                    self.allviews,xmin,xmax,ymin,ymax,-99999,1024,France=True,epsg='EPSG:27563'),
                    ToCheck=False,id='Orthos France')

        forelist={'EAU':{'Aqualim':'RES_LIMNI_DGARNE','Alea':'ALEA_INOND','Lidaxes':'LIDAXES'},
                    'LIMITES':{'Secteurs Statistiques':'LIMITES_QS_STATBEL'},
                    'INSPIRE':{'Limites administratives':'AU_wms'},
                    'PLAN_REGLEMENT':{'Plan Percellaire':'CADMAP_2021_PARCELLES'}}
        
        for idx,(k,item) in enumerate(forelist.items()):
            for kdx,(m,subitem) in enumerate(item.items()):
                self.allviews.add_object(which='wmsfore',
                            newobj=imagetexture('PPNC',m,k,subitem,
                            self.allviews,xmin,xmax,ymin,ymax,-99999,1024),
                            ToCheck=False,id=m)        

class MapManager(GenMapManager):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.allviews=WolfMapViewer(None,'All data')
        self.add_grid()
        self.add_WMS()

class GPU2DModel(GenMapManager):

    mydir:str
    files_results_array:dict
    mybed:WolfArray

    def __init__(self,dir:str='', *args, **kw):
        super(GPU2DModel, self).__init__(*args, **kw)
        
        self.allviews=WolfMapViewer(None,'All data')
        self.add_grid()
        self.add_WMS()

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)

        ext=['.top','.frott','.cls_pos','.cls_Z','.hbin','.zbin','.srcq']
        for myext in ext:
            if path.exists(self.mydir+'//simul'+myext):
                self.allviews.add_object(which='array',filename=self.mydir+'//simul'+myext,id=myext,ToCheck=False)
        
        self.mybed=WolfArray(self.mydir +'//simul.top')
        self.result = wolfres2DGPU(self.mydir,self.mybed,parent=self)
        self.allviews.add_object(which='array',newobj=self.result,id='res1',ToCheck=False)

        """self.files_results_array={}
        self.files_results_array['H']=[]
        idx=101
        while path.exists(self.mydir+'//out'+str(idx)+'r.bin'):
            self.files_results_array['H'].append(['out'+str(idx)+'r.bin','step '+str(idx)])
            idx+=1

        for curfile in self.files_results_array['H']:
            curext=curfile[0]
            curidx=curfile[1]
            self.allviews.add_object(which='array',filename=self.mydir+'//'+curext,id=curidx,ToCheck=False)
        """

        self.allviews.findminmax(True)        
        self.allviews.Autoscale(False)
    
class HydrologyModel(GenMapManager):

    mydir:str
    mydircharact:str
    mydirwhole:str
    files_hydrology_array:dict
    files_hydrology_vectors:dict
    mainparams:Wolf_Param
    basinparams:Wolf_Param
    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations
    mycatchment:Catchment
    myexchanges:forced_exchanges

    def __init__(self,dir:str='', *args, **kw):
        super(HydrologyModel, self).__init__(*args, **kw)

        self.SPWstations=SPWMIGaugingStations()
        self.DCENNstations=SPWDCENNGaugingStations()

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)
            
        self.mydircharact=path.join(self.mydir,'Characteristic_maps\\Drainage_basin')
        self.mydirwhole=path.join(self.mydir,'Whole_basin\\')
        
        self.mycatchment = Catchment('Mysim',self.mydir,False,True)
        self.myexchanges = forced_exchanges(self.mydir)

        self.allviews=GuiHydrology(title='Model : '+self.mydir)

        self.files_hydrology_array={'Characteristic_maps':[
            ('.b','Raw elevation [m]'),
            ('corr.b','Corrected elevation [m]'),
            #('diff.b','Corrections (corr-raw) [m]'),
            ('.nap','Mask [-]'),
            ('.sub','SubBasin index [-]'),
            ('.cnv','Accumulation [km²]'),
            ('.time','Total time [s]'),
            ('.coeff','RunOff coeff [-]'),
            ('.slope','Slope [-]'),
            ('.reachs','Reach index [-]'),
            ('.strahler','Strahler index [-]'),
            ('.reachlevel','Reach accumulation [-]'),
            ('.landuse1','Woodlands [m²]'),
            ('.landuse2','Pastures [m²]'),
            ('.landuse3','Cultivated [m²]'),
            ('.landuse4','Pavements [m²]'),
            ('.landuse5','Water [m²]'),
            ('.landuse6','River [m²]'),
            ('.landuse_limited_area','LandUse Verif'),
            ('.principal_landuse_cropped','Principal landuse [-]'),
            ('_encode.sub','Coded index SubB [-]')]}

        self.files_hydrology_vectors={'Characteristic_maps':[('.delimit.vec','Watershed')],
                                      'Whole_basin':[('Rain_basin_geom.vec','Rain geom'),
                                                     ('Evap_basin_geom.vec','Evapotranspiration geom')]}   

        for curfile in self.files_hydrology_array['Characteristic_maps']:
            curext=curfile[0]
            curidx=curfile[1]
            self.allviews.add_object(which='array',filename=self.mydircharact+curext,id=curidx,ToCheck=False)

        for curfile in self.files_hydrology_vectors['Characteristic_maps']:
            curext=curfile[0]
            curidx=curfile[1]
            self.allviews.add_object(which='vector',filename=self.mydircharact+curext,id=curidx,ToCheck=False)
        
        for curfile in self.files_hydrology_vectors['Whole_basin']:
            curext=curfile[0]
            curidx=curfile[1]
            if path.exists(self.mydirwhole+curext):
                self.allviews.add_object(which='vector',filename=self.mydirwhole+curext,id=curidx,ToCheck=False)
                
        self.allviews.add_object(which='vector',newobj=self.myexchanges.mysegs,id='Forced exchanges',ToCheck=False)
        self.allviews.add_object(which='cloud',newobj=self.mycatchment.subBasinCloud,id='Local outlets',ToCheck=False)
        self.allviews.add_object(which='cloud',newobj=self.myexchanges.mycloudup,id='Up nodes',ToCheck=False)
        self.allviews.add_object(which='cloud',newobj=self.myexchanges.myclouddown,id='Down nodes',ToCheck=False)
        
        self.allviews.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
        self.allviews.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

        self.add_grid()
        self.add_WMS()

        self.allviews.findminmax(True)        
        self.allviews.Autoscale(False)

        #Fichiers de paramètres
        self.mainparams=Wolf_Param(self.allviews,filename=self.mydir+'\\Main_model.param',title="Model parameters",DestroyAtClosing=False)
        self.basinparams=Wolf_Param(self.allviews,filename=self.mydircharact+'.param',title="Basin parameters",DestroyAtClosing=False)
        self.mainparams.Hide()
        self.basinparams.Hide() 

class Wolf2DModel(GenMapManager):

    mydir:str
    filenamegen:str
    files_others:dict
    files_fine_array:dict
    files_MB_array:dict
    files_vectors:dict
    mainparams:Wolf_Param

    SPWstations:SPWMIGaugingStations
    DCENNstations:SPWDCENNGaugingStations

    def __init__(self,dir:str='', *args, **kw):
        super(Wolf2DModel, self).__init__(*args, **kw)

        self.SPWstations=SPWMIGaugingStations()
        self.DCENNstations=SPWDCENNGaugingStations()

        if dir=='':
            idir=wx.DirDialog(None,"Choose Directory")
            if idir.ShowModal() == wx.ID_CANCEL:
                return
            self.mydir =idir.GetPath()
        else:
            self.mydir=path.normpath(dir)
            
        #recherche du nom générique --> sans extension
        for curfile in scandir(self.mydir):
            if curfile.is_file:
                ext=path.splitext(curfile)
                if len(ext[1])==0:
                    self.filenamegen = path.join(self.mydir,curfile.name)
                    break
                    
        self.allviews=WolfMapViewer(None,title='2D model : '+self.mydir)
        
        self.files_others={'Generic file':[
            ('','First parametric file - historical'),
            ('.par','Parametric file - multiblocks')],
                           'Charachteristics':[
            ('.fil','Infiltration hydrographs [m³/s]'),
            ('.mnap','Resulting mesh [-]'),
            ('.trl','Translation to real world [m]')
            ]}
        
        self.files_vectors={'Block file':[
            ('.bloc','Blocks geometry')],
                            'Borders':[
            ('.sux','X borders'),
            ('.suy','Y borders')],
                            'Contour':[
            ('.xy','General perimeter')                     
        ]}

        self.files_MB_array={'Initial Conditions':[
            ('.topini','Bed elevation [m]'),
            ('.hbinb','Water depth [m]'),
            ('.qxbinb','Discharge X [m²/s]'),
            ('.qybinb','Discharge Y [m²/s]')
        ]}

        self.files_fine_array={'Characteristics':[
            ('.napbin','Mask [-]'),
            ('.top','Bed Elevation [m]'),
            ('.frot','Roughness coefficient [law dependent]'),
            ('.inf','Infiltration zone [-]')
        ]}

        self.myparam=prev_parameters_simul(self)
        self.myparam.read_file()

        self.mynap = self.read_fine_nap()
        
        self.mysuxy = prev_suxsuy(self)
        self.mysuxy.read_file()
        
        self.myinfil=prev_infiltration(self)
        self.myinfil.read_file()
        self.myinfil.read_array()

        self.myblocfile=bloc_file(self)
        self.myblocfile.read_file()
        
        self.mymnap= WolfArrayMNAP(self.filenamegen)        
        
        # self.cont_sauv:Zones
        # self.filaire:Zones
        self.myinfil.myarray.parentGUI=self
        self.mymnap.parentGUI=self
        
        self.myinfil.myarray.myops.parentGUI=self
        self.mymnap.myops.parentGUI=self

        self.allviews.add_object(which='array',newobj=self.myinfil.myarray,id='infiltration',ToCheck=False)
        self.allviews.add_object(which='array',newobj=self.mymnap,id='mnap',ToCheck=False)
        
        self.allviews.add_object(which='vector',newobj=self.mysuxy.myborders,id='Borders',ToCheck=True)
        self.allviews.add_object(which='vector',newobj=self.myblocfile.my_vec_blocks,id='Blocks',ToCheck=False)
        
        self.allviews.add_object(which='other',newobj=self.SPWstations,ToCheck=False,id='SPW-MI stations')
        self.allviews.add_object(which='other',newobj=self.DCENNstations,ToCheck=False,id='SPW-DCENN stations')

        self.add_grid()
        self.add_WMS()

        self.allviews.findminmax(True)        
        self.allviews.Autoscale(False)

        self.mysuxy.myborders.prep_listogl()
        self.myblocfile.my_vec_blocks.prep_listogl()

        #Fichiers de paramètres
        # self.mainparams=Wolf_Param(self.allviews,filename=self.mydir+'\\Main_model.param',title="Model parameters",DestroyAtClosing=False)
        # self.mainparams.Hide()
    
    def get_header_MB(self,abs=False):
        '''#> Renvoit un header avec les infos multi-blocs'''
        myheader = self.mymnap.get_header(abs=abs)
        for curblock in self.mymnap.myblocks.values():
            myheader.head_blocks[getkeyblock(curblock.blockindex)] = curblock.get_header(abs=abs)
        return  myheader
        
    def get_header(self,abs=True):
        '''#> Renvoit un header de matrice "fine" non MB'''
        
        curhead = header_wolf()
        
        curhead.nbx = self.myparam.nxfin
        curhead.nby = self.myparam.nyfin
        
        curhead.dx = self.myparam.dxfin
        curhead.dy = self.myparam.dyfin
        
        curhead.origx = self.myparam.xminfin
        curhead.origy = self.myparam.yminfin
        
        curhead.translx = self.myparam.translx
        curhead.transly = self.myparam.transly
        
        return curhead
        # return self.mymnap.get_header(abs=abs)
                
    def read_fine_array(self,which=''):
        '''Lecture d'une matrice fine'''
        
        myarray =WolfArray()
        myarray.set_header(self.get_header())
        myarray.filename = self.filenamegen+which
        myarray.read_data()
        
        return myarray
    
    def read_MB_array(self,which=''):
        '''Lecture d'une matrice MB'''
        
        myarray =WolfArrayMB()
        myarray.set_header(self.get_header_MB())
        myarray.filename = self.filenamegen+which
        myarray.read_data()
        
        return myarray

    def read_fine_nap(self) -> np.ndarray:
        '''Lecture de la matrice nap sur le maillage fin'''
        nbx=self.myparam.nxfin
        nby=self.myparam.nyfin        
        
        with open(self.filenamegen +'.napbin', 'rb') as f:
            mynap = np.frombuffer(f.read(nbx*nby*2), dtype=np.int16).copy()
            mynap=np.abs(mynap)
        
        return mynap.reshape([nbx,nby], order='F')


