# from PIL import Image,ExifTags
import os.path as path
from os import curdir, listdir
from exif import Image
from osgeo import ogr
from osgeo import osr  
import wx

from .PyTranslate import _

'''
Ajout des coordonnées GPS d'une photo en Lambert72 si n'existe pas

!!! A COMPLETER !!!

'''
class Picture(wx.Frame):
    
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
    

# Spatial Reference System
inputEPSG = 4326 #WGS84
outputEPSG = 31370 #Lambert72

# create coordinate transformation
inSpatialRef = osr.SpatialReference()
inSpatialRef.ImportFromEPSG(inputEPSG)

outSpatialRef = osr.SpatialReference()
outSpatialRef.ImportFromEPSG(outputEPSG)

coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

dir = path.normpath(r'D:\OneDrive\OneDrive - Universite de Liege\Crues\2021-07 Vesdre\CSC - Convention - ARNE\3 noeuds critiques\tronçon 34')

for curfile in listdir(dir):
    filename,fileextent = path.splitext(curfile)
    if fileextent.lower()=='.jpg':
        img = Image(path.join(dir,curfile))     

        if img.get('Lambert72X'):
            x = img.get('Lambert72X')
            y = img.get('Lambert72Y')

        elif img.get('gps_latitude'):
            lat=img.gps_latitude
            lon=img.gps_longitude
            alt=img.gps_altitude

            # create a geometry from coordinates
            point = ogr.Geometry(ogr.wkbPoint)
            if len(lat)==3:
                lat = lat[0]+lat[1]/60+lat[2]/(60*60)
                lon = lon[0]+lon[1]/60+lon[2]/(60*60)
            point.AddPoint(lat, lon)
            # transform point
            point.Transform(coordTransform)
            # print point in EPSG 31370
            print(point.GetX(), point.GetY())
            img.set('Lambert72X',point.GetX())             
            img.set('Lambert72Y',point.GetY()) 
            
            with open(path.join(dir,'modified_image.jpg'), 'wb') as new_image_file:
                new_image_file.write(img.get_file())