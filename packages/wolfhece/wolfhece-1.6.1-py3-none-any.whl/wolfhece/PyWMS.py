from owslib.wms import WebMapService
from PIL import Image
from io import BytesIO
import pyproj

from .PyTranslate import _

def getWalonmap(cat:str,xl,yl,xr,yr,w,h,tofile=True) -> BytesIO:
    try:
        wms=WebMapService('https://geoservices.wallonie.be/arcgis/services/'
                        + cat+'/MapServer/WMSServer',version='1.3.0')
    except:
        wms=WebMapService('http://ccff02.minfin.fgov.be/geoservices/arcgis/services/'
                        + cat+'/MapServer/WMSServer',version='1.3.0')

    if tofile:
        img=wms.getmap(layers=['0'],styles=['default'],srs='EPSG:31370',bbox=(xl,yl,xr,yr),size=(w,h),format='image/png',transparent=True)
        out = open('aqualim.png', 'wb')
        out.write(img.read())
        out.close()
        return BytesIO(b'1')
    else:
        mycontents=list(wms.contents)
        curcont=['0']
        curstyles=['default']
        
        if cat.find('ALEA')>0:
            ech=(xr-xl)/w
            if ech>6.5:
                curcont=['6'] #au-dessus du 1:25000
            else:
                curcont=['5'] #en-dessous du 1:25000 et au-dessus de 1:5000
        elif cat.find('CADMAP')>0:
            curcont=['0,1']
            curstyles=['default,default']
        elif cat.find('wms')>0:
            curcont=['1,2,3,4,5']
            curstyles=['default,default,default,default,default']
        elif cat.find('LIDAXES')>0:
            curcont=['4,5,6,7,8,9,11,13']
            curstyles=['default,default,default,default,default,default,default,default']
        img=wms.getmap(layers=curcont,styles=curstyles,srs='EPSG:31370',bbox=(xl,yl,xr,yr),size=(w,h),format='image/png',transparent=True)
        return BytesIO(img.read())

def getIGNFrance(cat:str,epsg:str,xl,yl,xr,yr,w,h,tofile=True) -> BytesIO:

    if epsg!='EPSG:4326':
        transf=pyproj.Transformer.from_crs(epsg,'EPSG:4326')
        y1,x1=transf.transform(xl,yl)
        y2,x2=transf.transform(xr,yr)    
    else:
        x1=xl
        x2=xr
        y1=yl
        y2=yr

    wms=WebMapService('https://wxs.ign.fr/inspire/inspire/r/wms',version='1.3.0')

    img=wms.getmap(layers=[cat],styles=[''],srs='EPSG:4326',bbox=(x1,y1,x2,y2),size=(w,h),format='image/png',transparent=True)
    
    if tofile:
        out = open('ignFrance.png', 'wb')
        out.write(img.read())
        out.close()
        return BytesIO(b'1')
    else:
        return BytesIO(img.read())

if __name__=='__main__':
    me=pyproj.CRS.from_epsg(27573)
    t=pyproj.Transformer.from_crs(27573,4326)
    getIGNFrance('OI.OrthoimageCoverage.HR','EPSG:27563',878000,332300,879000,333300,1000,1000)