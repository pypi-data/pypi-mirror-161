import requests
import pandas as pd
import numpy as np
from calendar import monthrange

STATIONS_MI="""92150015	PETIGNY Barrage
92880015	CUL-DES-SARTS
91370015	BOUSSU-EN-FAGNE
10430015	WAVRE
10810015	BOUSVAL
60480015	RACHAMPS-NOVILLE
61280015	ORTHO
61680015	SAINT-HUBERT aéro
68580015	TAILLES
70030015	SART-TILMAN
70160015	OUFFET
70180015	MEAN
70480015	EREZEE
70870015	MARCHE
10570015	LOUVAIN LA NEUVE
15790015	PERWEZ
15840015	HELECINE
18980015	UCCLE
19540015	TUBIZE
19970015	SOIGNIES
23480015	LILLOIS
23880015	SENEFFE
24590015	DERGNEAU
28920015	ENGHIEN
29930015	CHIEVRES
32770015	KAIN
34760015	MOUSCRON
35340015	WASMUEL
35720015	TRIVIERES
36280015	ROISIN
36470015	ROUVEROY
36490015	BLAREGNIES
37170015	PERUWELZ
38850015	COMINES Barrage-Ecl
52840015	GEMMENICH
55780015	WAREMME
55960015	AWANS
56490015	BATTICE
57570015	LANAYE
64970015	TERNELL
65290015	MONT-RIGI
65380015	SPA aerodrome
65500015	JALHAY
66570015	LOUVEIGNE
67120015	COO INF.
67120115	COO INF.
67180015	COO SUP.
67180115	COO SUP.
68480015	VIELSALM
69580015	ROBERTVILLE
69670015	BUTGENBACH
69670115	BUTGENBACH
71680015	LANDENNE
72280015	MODAVE
72960015	VEDRIN
73350015	MORNIMONT Bar-Ecluse
73690015	CHATELET
73950015	MONCEAU Bar-Ecluse
74850015	SOLRE S/S Bar-Ecluse
75770015	MOMIGNIES
76290015	LIGNY
76780015	GERPINNES
78650015	PLATE TAILLE
78880015	SENZEILLES
79670015	SIVRY
80630015	ANSEREMME
81280015	SAINT-GERARD
81380015	CRUPET
81570015	CINEY
81890015	FLORENNES
83480015	DAVERDISSE
83880015	LIBIN
84680015	BEAURAING
85180015	ROCHEFORT
85380015	NASSOGNE
86770015	GEDINNE
86870015	CROIX-SCAILLE
94360015	VRESSE
94690015	BOUILLON
95740015	FRATIN
95880015	MEIX-LE-TIGE
95960015	ARLON
95960115	ARLON
96170015	SUGNY
96320015	BERTRIX
96520015	STRAIMONT
96980015	NAMOUSSART
97430015	TORGNY
97810015	ATHUS
97940015	AUBANGE
97970015	SELANGE
98160015	ORVAL
99150015	STEFFESHAUSEN
99220015	SANKT-VITH
99480015	BASTOGNE
"""

#Création de 2 dictionnaires de recherche sur base de la chaîne
pluviocode2name={}
pluvioname2code={}
for mypluvio in STATIONS_MI.splitlines():
    mycode,myname=mypluvio.split("\t")
    pluviocode2name[mycode]=myname
    pluvioname2code[myname]=mycode

STATS_HOURS_IRM=(1,2,3,6,12,24,2*24,3*24,4*24,5*24,7*24,10*24,15*24,20*24,25*24,30*24)

def get_rain_from_SPWMI(month=7,year=2021,code='',name=''):
    #récupération des données au pas horaire depuis le site SPW-MI VH
    #http://voies-hydrauliques.wallonie.be/opencms/opencms/fr/hydro/Archive/

    station=code
    if name!="":
        station=pluvioname2code[name]

    nbdays = monthrange(year, month)[1] 

    url="http://voies-hydrauliques.wallonie.be/opencms/opencms/fr/hydro/Archive/annuaires/stathorairetab.do?code="+station+"&mois="+str(month)+"&annee="+str(year)

    res=requests.get(url)
    html_tables = pd.read_html(res.content, match='.+')

    rain = html_tables[12].to_numpy()[0:24,1:nbdays+1].astype('float').reshape(24*nbdays,order='F')
    return rain

def compute_stats(rain,listhours):
    #Calcul des stats par convolution sur base d'un vecteur de nombre d'heures
    mystats=[]
    for locstat in listhours:
        a = np.ones(locstat)
        mystats.append(np.max(np.convolve(rain,a,'same')))

    return mystats

if __name__=="__main__":
    #exemple
    myrain=get_rain_from_SPWMI(name="JALHAY")
    mystats=compute_stats(myrain,STATS_HOURS_IRM)
    print(mystats)
