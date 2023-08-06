#Code INS des communes belges
from cProfile import label
from pickletools import optimize
from statistics import mean
from turtle import color
import numpy as np
from os import path,mkdir
from time import sleep
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize,curve_fit
from scipy.stats import gumbel_r,genextreme

from .ins import Localities
from .PyTranslate import _

Montana_a1 = 'a1' 
Montana_a2 = 'a2' 
Montana_a3 = 'a3' 
Montana_b1 = 'b1' 
Montana_b2 = 'b2' 
Montana_b3 = 'b3' 

RT2 = '2'
RT5 = '5'
RT10 = '10'
RT15 = '15'
RT20 ='20'
RT25 ='25'
RT30 = '30'
RT40 ='40'
RT50 ='50'
RT75 = '75'
RT100 ='100'
RT200  = '200'

RT = [RT2,RT5,RT10,RT15,RT20,RT25,RT30,RT40,RT50,RT75,RT100,RT200]
freqdep=np.array([1./float(x) for x in RT])
freqndep=1.-freqdep

dur10min = '10 min'
dur20min = '20 min'
dur30min = '30 min'
dur1h = '1 h'
dur2h = '2 h'
dur3h = '3 h'
dur6h = '6 h'
dur12h = '12 h'
dur1d = '1 d'
dur2d = '2 d'
dur3d = '3 d'
dur4d = '4 d'
dur5d = '5 d'
dur7d = '7 d'
dur10d = '10 d'
dur15d = '15 d'
dur20d = '20 d'
dur25d = '25 d'
dur30d = '30 d'

durationstext=[dur10min,dur20min,dur30min,dur1h,dur2h,dur3h,dur6h,dur12h,dur1d,
                dur2d,dur3d,dur4d,dur5d,dur7d,dur10d,dur15d,dur20d,dur25d,dur30d]
durations=np.array([10,20,30,60,120,180,360,720],np.float64)
durationsd=np.array([1,2,3,4,5,7,10,15,20,25,30],np.float64)*24.*60.
durations = np.concatenate([durations,durationsd])

class MontanaIRM():

    def __init__(self,coeff:pd.DataFrame,time_bounds=None) -> None:

        if time_bounds is None:
            self.time_bounds = [25,6000]
        else:
            self.time_bounds = time_bounds

        self.coeff=coeff

    def get_ab(self,dur,T):

        curcoeff = self.coeff.loc[float(T)]
        if dur<self.time_bounds[0]:
            a=curcoeff[Montana_a1]
            b=curcoeff[Montana_b1]
        elif dur<=self.time_bounds[1]:
            a=curcoeff[Montana_a2]
            b=curcoeff[Montana_b2]
        else:
            a=curcoeff[Montana_a3]
            b=curcoeff[Montana_b3]

        return a,b

    def get_meanrain(self,dur,T,ab=None):
        if ab is None:
            ab = self.get_ab(dur,T)
        return ab[0]*dur**(-ab[1])

    def get_instantrain(self,dur,T,ab=None):
        if ab is None:
            ab = self.get_ab(dur,T)
        meani=self.get_meanrain(dur,T,ab)
        return (1.-ab[1])*meani

    def get_Q(self,dur,T):
        rain = self.get_meanrain(dur,T)
        return rain*dur/60. #to obtains [mm.h^-1] as dur is in [min]

    def get_hyeto(self,durmax,T,r=0.5):
        x = np.arange(10,durmax,1,dtype=np.float64)
        # y = [self.get_instantrain(curx,T) for curx in x]

        startpeak=durmax*r-5
        endpeak=durmax*r+5

        if r==1.:
            xbeforepeak = np.zeros(1)
        else:
            xbeforepeak = np.arange(-float(durmax-10)*(1.-r),0,(1.-r))
        if r==0.:
            xafterpeak = endpeak
        else:
            xafterpeak  = np.arange(0,float(durmax-10)*r,r)

        xbeforepeak+= startpeak
        xafterpeak += endpeak

        x_hyeto = np.concatenate([xbeforepeak, [startpeak,endpeak], xafterpeak])
        y_hyeto = np.zeros(len(x_hyeto))
        for k in range(len(x_hyeto)):
            if x_hyeto[k] <= startpeak:
                y_hyeto[k] = self.get_instantrain((startpeak-x_hyeto[k])/(1.-r)+10,T)
            else:
                y_hyeto[k] = self.get_instantrain((x_hyeto[k]-endpeak)/r+10,T)

        if r==0.:
            y_hyeto[-1]=0.
        elif r==1.:
            y_hyeto[0]=0.

        return x_hyeto,y_hyeto
    
    def plot_hyeto(self,durmax,T,r=0.5):
        x,y = self.get_hyeto(durmax,T,r)
        
        fig,ax = plt.subplots(1,1,figsize=[15,10])
        ax.plot(x,y,label=_("Hyetogram"))
        
        ax.set_xlabel(_('Time [min]'))
        ax.set_ylabel(_('Intensity [mm/h]'))
        ax.legend().set_draggable(True)
        
        return fig,ax

    def plot_hyetos(self,durmax,r=0.5):
        fig,ax = plt.subplots(1,1,figsize=[15,10])

        for curT in RT:
            x,y = self.get_hyeto(durmax,curT,r)
            
            ax.plot(x,y,label=curT)
            
        ax.set_xlabel(_('Time [min]'))
        ax.set_ylabel(_('Intensity [mm/h]'))
        ax.legend().set_draggable(True)
        
        return fig,ax

class Qdf_IRM():
    '''Gestion des relations QDF calculées par l'IRM
    
    Exemple d'utilisation :
    
    #Pour importer les fichiers depuis le site web de l'IRM meteo.be
    import wolfhece.irm_qdf as qdf
    qdf = Qdf_IRM(force_import=True)
    
    Il est possible de spécifier le répertoire de stockage des fichiers Excel
    Par défaut, il s'agit d'un sous-répertoire 'irm' du répertoire courant qui sera créé s'il n'exsiste pas
    
    Une fois importé, il est possible de charger une commune sur base de l'INS ou de son nom
    
    myqdf = qdf.Qdf_IRM(name='Jalhay')
    
    Les données sont ensuite disponibles dans les propriétés, qui sont des "dataframes" pandas (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) :
         - qdf           : les relation Quantité/durée/fréquence
         - standarddev   : l'écart-type de l'erreur
         - confintlow    : la valeur inférieure de l'intervalle de confiance (-2*stddev)
         - confintup     : la valeur supérieure de l'intervalle de confiance (+2*stddev)
         - montanacoeff  : les coeffciients de Montana 
         
    Il est par exemple possible d'accéder aux coefficients de Montana via l'une de ces lignes ou une combinaison :
    
    display(myqdf.montanacoeff)
    rt = myqdf.montanacoeff.index
    display(myqdf.montanacoeff.loc[rt[0]])
    display(myqdf.montanacoeff.iloc[0])
    display(myqdf.get_Montanacoeff(qdf.RT2))
    
    '''
    
    def __init__(self,store_path='irm',code:int=0,name='',force_import=False) -> None:
        
        self.myloc = Localities()
        self.store = store_path
        
        if force_import:
            self.importfromwebsite(store_path)
            
        if code !=0:
            self.ins_read_excel(code=str(code))
        elif name!='':
            self.ins_read_excel(name=name)
            
        self.fit_all()
        
        pass
    
    def importfromwebsite(self,store_path='irm',verbose=False,waitingtime=.01):
        ''' Import des fichiers Excel pour toutes les communes depuis le site de l'IRM '''
        import requests

        if not path.exists(store_path):
            mkdir(store_path)

        for key,myins in enumerate(self.myloc.inscode2name):
            #chaîne URL du fichier Excel
            url="https://www.meteo.be//resources//climatology//climateCity//xls//IDF_table_INS"+str(myins)+".xlsx"
            #Obtention du fichiers depuis le site web de l'IRM
            response=requests.get(url)
            
            if str(response.content).find("Page not found")==-1 :
                file=open(path.join(store_path,str(myins)+".xlsx"), 'wb')
                file.write(response.content)
                file.close()
                if verbose:
                    print(myins)
                    
            sleep(waitingtime)

    def ins_read_excel(self,code='',name=''):
        '''Lecture des caractéristiques d'une commune depuis le fichier Excel associé au code INS'''
        import warnings

        if code !='':
            loccode=code
            name = self.myloc.get_namefromINS(int(loccode))            
        elif name!='':
            if not name.lower() in self.myloc.insname2code.keys():
                return _('Bad name ! - Retry')      
            loccode=str(self.myloc.insname2code[name.lower()])
        
        self.code = loccode
        self.name = name
        
        pathname = path.join(self.store,loccode+".xlsx")

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            if path.exists(pathname):
                self.qdf=pd.read_excel(pathname,"Return level",index_col=0,skiprows=range(7),nrows=19,usecols="A:M")
                self.standarddev=pd.read_excel(pathname,"Standard deviation",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl')
                self.confintlow=pd.read_excel(pathname,"Conf. interval, lower bound",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl')
                self.confintup=pd.read_excel(pathname,"Conf. interval, upper bound",index_col=0,skiprows=range(7),nrows=19,usecols="A:M",engine='openpyxl')
                self.montanacoeff=pd.read_excel(pathname,"Montana coefficients",index_col=0,skiprows=range(11),nrows=12,usecols="A:G",engine='openpyxl')        
                self.montana = MontanaIRM(self.montanacoeff)
            else:
                return 'File not present'
    
    def plot_idf(self,T=None,which='All',color=[27./255.,136./255.,245./255.]):
        '''
        Plot IDF relations on a new figure 
        T       : the return period (based on RT constants)
        which   : information to plot 
            - 'Montana' 
            - 'QDFTable' 
            - 'All' 
        '''
        fig,ax = plt.subplots(1,1,figsize=(15,10))
        ax.set_xscale('log')
        ax.set_yscale('log')
        
        if T is None:
            for k in range(len(RT)):
                pond = .3+.7*float(k/len(RT))
                mycolor = color+[pond]
                if which=='All' or which=='QDFTable':
                    ax.scatter(durations,self.qdf[RT[k]]/durations*60.,label=RT[k] + _(' QDF Table'),color=mycolor)
            
                if which=='All' or which=='Montana':
                    iMontana = [self.montana.get_meanrain(curdur,RT[k]) for curdur in durations]
                    ax.plot(durations,iMontana,label=RT[k] + ' Montana',color=mycolor)
        else:
            if which=='All' or which=='QDFTable':
                ax.scatter(durations,self.qdf[T],label=T+ _(' QDF Table'),color=color)
            
            if which=='All' or which=='Montana':
                iMontana = [self.montana.get_instantrain(curdur,T) for curdur in durations]
                ax.plot(durations,iMontana,label=T + ' Montana',color=color)

        ax.legend().set_draggable(True)
        ax.set_xlabel(_('Duration [min]'))
        ax.set_ylabel(_('Intensity [mm/h]'))
        ax.set_xticks(durations)
        ax.set_xticklabels(durationstext,rotation=45)
        ax.set_title(self.name + ' - code : ' + str(self.code))

        return fig,ax

    def plot_qdf(self,T=None,which='All',color=[27./255.,136./255.,245./255.]):
        '''
        Plot QDF relations on a new figure
        T       : the return period (based on RT constants)
        which   : information to plot 
            - 'Montana' 
            - 'QDFTable' 
            - 'All' 
        '''
        fig,ax = plt.subplots(1,1,figsize=(15,10))
        ax.set_xscale('log')
        
        if T is None:
            for k in range(len(RT)):
                pond = .3+.7*float(k/len(RT))
                mycolor = color+[pond]
                if which=='All' or which=='QDFTable':
                    ax.scatter(durations,self.qdf[RT[k]],label=RT[k] + _(' QDF Table'),color=mycolor)
            
                if which=='All' or which=='Montana':
                    QMontana = [self.montana.get_Q(curdur,RT[k]) for curdur in durations]
                    ax.plot(durations,QMontana,label=RT[k] + ' Montana',color=mycolor)
        else:
            if which=='All' or which=='QDFTable':
                ax.scatter(durations,self.qdf[T],label=T+ _(' QDF Table'),color=color)
            
            if which=='All' or which=='Montana':
                QMontana = [self.montana.get_Q(curdur,T) for curdur in durations]
                ax.plot(durations,QMontana,label=T + ' Montana',color=color)

        ax.legend().set_draggable(True)
        ax.set_xlabel(_('Duration [min]'))
        ax.set_ylabel(_('Quantity [mm]'))
        ax.set_xticks(durations)
        ax.set_xticklabels(durationstext,rotation=45)
        ax.set_title(self.name + ' - code : ' + str(self.code))

        return fig,ax
        
    def plot_cdf(self,dur=None):

        fig,ax = plt.subplots(1,1,figsize=(10,10))
        if dur is None:
            for k in range(len(durations)):
                pond = .3+.7*float(k/len(durations))
                mycolor = (27./255.,136./255.,245./255.,pond)
                ax.scatter(self.qdf.loc[durationstext[k]],freqndep,marker='o',label=durationstext[k],color=mycolor)
        else:
            ax.scatter(self.qdf.loc[dur],freqndep,marker='o',label=dur,color=(0,0,1))

        ax.legend().set_draggable(True)
        ax.set_ylabel(_('Cumulative distribution function (cdf)'))
        ax.set_xlabel(_('Quantity [mm]'))
        ax.set_title(self.name + ' - code : ' + str(self.code))
        
        return fig,ax 
            
    def fit_all(self):
        
        self.popt_all={}
        self.pcov_all={}
        
        for curdur in durationstext:
            fig,ax,popt,pcov = self.fit_cdf(curdur)
            self.popt_all[curdur]=popt
            self.pcov_all[curdur]=pcov
    
    def fit_cdf(self,dur=None,plot=False):
        
        x=np.asarray(self.qdf.loc[dur],dtype=np.float64)

        def locextreme(x,a,b,c):
            return genextreme.cdf(x,a,loc=b,scale=c)

        def locextreme2(a):
            LL = -np.sum(genextreme.logpdf(x,a[0],loc=a[1],scale=a[2]))
            return LL

        popt = genextreme.fit(x)
        popt,pcov=curve_fit(locextreme,x,freqndep,p0=popt)
        
        #ptest = minimize(locextreme2,popt,bounds=[[-10.,0.],[0.,100.],[0.,100.]])
        
        perr = np.sqrt(np.diag(pcov))
    
        fig=ax=None
        if plot:
            fig,ax=self.plot_cdf(dur)
            ax.plot(x,genextreme.cdf(x,popt[0],loc=popt[1],scale=popt[2]),label='fit')
            # ax.plot(x,genextreme.cdf(x,ptest.x[0],loc=ptest.x[1],scale=ptest.x[2]),label='fit_MLE')
            ax.legend().set_draggable(True)
        
        self.stat = genextreme
                
        return fig,ax,popt,pcov
    
    def get_Tfromrain(self,Q,dur=dur1h):
        return 1./self.stat.sf(Q,self.popt_all[dur][0],loc=self.popt_all[dur][1],scale=self.popt_all[dur][2])
    
    def get_rainfromT(self,T,dur=dur1h):
        return self.stat.isf(1./T,self.popt_all[dur][0],loc=self.popt_all[dur][1],scale=self.popt_all[dur][2])

    def get_MontanacoeffforT(self,return_period):
        
        if return_period in RT:
            return self.montanacoeff.loc[float(return_period)]
        else:
            return _('Bad RT - Retry !')
        
    def plot_hyeto(self,durmax,T,r=.5):
        
        fig,ax = self.montana.plot_hyeto(durmax,T,r)
        ax.set_title(self.name + ' - code : ' + str(self.code))

    def plot_hyetos(self,durmax,r=.5):
        
        fig,ax = self.montana.plot_hyetos(durmax,r)
        ax.set_title(self.name + ' - code : ' + str(self.code))
