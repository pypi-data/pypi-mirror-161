import numpy as np
from OpenGL.GL  import *
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
import re

from ..wolf_array import WOLF_ARRAY_FULL_INTEGER, WOLF_ARRAY_FULL_SINGLE, WolfArray, WolfArrayMB,WolfArrayMNAP,header_wolf
from ..PyVertexvectors import *
from ..PyTranslate import _

## prev_bc_fv_*
PREV_BC_FV_IMPERVIOUS              = 4     ##< IMPERMÉABLE
PREV_BC_FV_WATERDEPTH             = 1     ##< HAUTEUR IMPOSÉE
PREV_BC_FV_WATERDEPTH_MOD         = 7     ##< HAUTEUR IMPOSÉE MODIFIÉE
PREV_BC_FV_FREESURFACE             = 1     ##< SURFACE LIBRE IMPOSÉE
PREV_BC_FV_DISCHARGE_X             = 2     ##< DÉBITS IMPOSÉS
PREV_BC_FV_DISCHARGE_Y             = 3     ##< DÉBITS IMPOSÉS
PREV_BC_FV_FROUDE                  = 8     ##< FROUDE IMPOSÉ
PREV_BC_FV_DISCHARGE_X_SED         = 5     ##< BORD LIBRE
PREV_BC_FV_DISCHARGE_Y_SED         = 6     ##< CL DE BARRAGE MOBILE (LOIS EN PUISSANCE)

PREV_INFILTRATION_NULL                  = 0     ##< PAS D'INFILTRATION
PREV_INFILTRATION_SIMPLE                = 1     ##< INFILTRATION SIMPLE (RÉPARTITION UNIFORME DU DÉBIT INJECTÉ PAR FICHIER .INF)
PREV_INFILTRATION_MOD_MOMENTUM          = 2     ##< INFILTRATION AVEC MODIFICATION DE LA QT DE MVT (RÉPARTITION NON UNIFORME DU DÉBIT INJECTÉ PAR FICHIER .INF)
PREV_INFILTRATION_MOD_MOMENTUM_IMPOSED  = 4     ##< INFILTRATION AVEC MODIFICATION IMPOSÉE DE LA QT DE MVT (RÉPARTITION NON UNIFORME DU DÉBIT INJECTÉ PAR FICHIER .INF)
PREV_INFILTRATION_VAR_SIMPLE            = -1    ##< INFILTRATION VARIABLE (RÉPARTITION UNIFORME DU DÉBIT INJECTÉ CALCULÉ SUR BASE DE L'ÉTAT HYDRODYNAMIQUE INSTANTANÉ)
PREV_INFILTRATION_VAR_MOD_MOMENTUM      = -2    ##< INFILTRATION VARIABLE AVEC MOD QT MVT (RÉPARTITION NON UNIFORME DU DÉBIT INJECTÉ CALCULÉ SUR BASE DE L'ÉTAT HYDRODYNAMIQUE INSTANTANÉ)
PREV_INFILTRATION_VAR_LINKED_ZONES      = -3    ##< INFILTRATION/EXFILTRATION "INTERNE" VARIABLE (RÉPARTITION UNIFORME DU DÉBIT SUR BASE DE DEUX ZONES D'INFILTRATION)

class prev_parameters_blocks:
    ''' #> Paramètres de calcul propres aux blocs
    @author Pierre Archambeau
     '''

    def __init__(self,lines=None) -> None:
        self.infiltration=False	    ##< infiltration de débit ou non
        self.infiltration_sed=False	    ##< infiltration de débit solide ou non
        self.reclineaire=False	    #	    #< reconstruction linéaire ou non
        self.reclinfront=False	    #	    #< reconstruction linéaire ou non sur les bords frontière
        self.optmaillage=False	    #	    #< optimisation du maillage de calcul
        self.incli_axes=False	    #	    #< inclinaison d'axes
        self.turbulence=False	    #	    #< calcul de termes turbulents ou pas
        self.vam5=False	    #			    #< calcul des équations de moment ou pas
        self.profil_equil=False	    #	    #< calcul d'un profil d'équilibre sédimentaire ou pas
        self.transport_solide=False	    #	#< equations additionnelles de transport solide ou pas
        self.frot_jacobien=False	    #     #< evaluation semi-implicite par inversion d'une matrice 3*3 du frottement
        self.carte_de_risque=False	    #   #< ecriture d'une carte de risque ou pas
        self.carte_de_risque_max=False	    # #< ecriture d'une carte de risque étendue ou pas
        self.carte_de_risque_qv=False	    # #< ecriture d'une carte de risque vmax et qmax si vitesse
        self.ponts=False	    #			    #< présence ou non de ponts
        self.irv=False	    #			    #< présence ou non d'in coef d'inégale répartition de vitesse distribué
        self.first_resu_bloc=False	    #   #< premier résu du bloc écrit ou pas (csr)
        self.surf_mod=False	    #		    #< modification des surfaces de frottement ou pas
        self.contour_mob=False	    #		#< contour mobile dans le bloc ou pas
        self.contour=False	    #		    #< contour fixe dans le bloc ou pas
        self.contour_fixe=False	    #	    #< contour fixe dans le bloc ou pas pour gestion données topo
        self.topo_inst=False	    #		    #< topo variable dans le temps
        self.report_cl_bloc=False	    #    #< report de conditions limites dans un bloc
        self.effacement_bloc=False	    #   #< effacement de mailles (bâtiments) dans le bloc ou pas
        self.nforcing=0		    ##< forcing ou pas
        self.nturb=0			#    #< nbre d'inconnues pour le calcul de la turbulence
        self.ncurv=0			#    #< nbre d'inconnues pour le calcul des coor curvilignes
        self.npor=0			    ##< nbre d'inconnues pour le calcul de la porosité
        self.nsed=0			    ##< calcul de bilan sédim dans le bloc (1) ou pas (0)
        self.nsusp=0			#    #< calcul de bilan supension dans le bloc (1) ou pas (0)
        self.ntyprec=0		    ##< =0 si rec constante, 1 si rec linéaire
        self.ntyprecfront=0	    ##< =0 si rec cst, 1 si rec lin non limitée, 2 si rec lin limitée des bords frontière
        self.ntyprecbord=0	    ##< type de reconstruction des bords libres (0 = cst, 1 = lin limitée (non implémenté), 2 = lin non limitée)
        self.nvoislimit=0	    ##< nbre de voisins pour la limitation
        self.nrechzh=0		    ##< =0 si limitation de h, 1 si limitation de h+z
        self.ntraitefront=0	    ##< type de traitement des frontières (1 = rien, 0 = moyenne et décentrement unique)
        self.ntypflux=0		    ##< type de spliting (1 = spliting maison, le reste n'est pas encore implémenté)
        self.nbvar=0			#    #< nbre d'inconnues du calcul
        self.nbequ=0			#    #< nbre d'equations à résoudre
        self.nconflit=0		    ##< gestion des conflits (0), ou juste en centré (1) ou pas (2)
        self.ncouvdecouv=0	    ##< gestion des éléments couvrants-découvrants ou non
        self.ntypetopo=0		#    #< type d'agglomération de la topo (1=moy, 2=max, 3=min)
        self.ninfil=0		    ##< infiltration avec modif eq qté mvt (=2), infiltration simple (=1) ou non (=0)
        self.ntypfil=0		    ##< infiltration modifiée (=2) ou non (=1)
        self.nincli_axes=0	    ##< type d'inclinaison d'axe (0 si pas d'inclinaison)
        self.iegal=0			#    #< =1 si égalisation d'altitude
        self.istat=0			#    #< arrêt stationnaire
        self.nvartop=0		    ##< topo variable ou non
        self.ntype_turb=0	    ##< type de modèle de turbulence (1 = prandtl, ...)
        self.ntype_sedim=0	    ##< type de modèle sédimentaire (1 = charriage, 2 = charriage + suspension)
        self.ntype_charriage=0	##< différentes loi de transport par charriage
        self.npos_flux_loi_sedim=0 ##< loi de capacité de transport par charriage
        self.dim_bil_fvs=0		##< dimension de la matrice bilan_fvs
        self.dim_bil_turb=0		##< dimension de la matrice bilan_turb
        self.dim_bil_vam5=0		##< dimension de la matrice bilan_vam5
        self.dim_bil_sedim=0	#	#< dimension de la matrice bilan_sedim
        self.dim_bil_suspension=0##< dimension de la matrice bilan_suspension
        self.nbflux=0		    ##< nombre de routines de flux à appeler pour le bloc
        self.nasseche=0		    ##< traitement des assèchements ou pas
        self.limite_erosion=0   # #< gestion des zones non érodables ou pas
        self.ntypfrot=0		    
        '''#< relatif au vdebug(3): type de calcul du frottement
                                    #< 	=-2 bathurst
                                    #< 	=-1 chézy
                                    #< 	=0	manning "classique"
                                    #< 	=1	manning + bords frottants "brufau - garcia navarro"
                                    #< 	=2	manning + surfaces frottantes réelles
                                    #< 	=3	manning + surfaces frottantes réelles + bords frottants "brufau - garcia navarro"
                                    #< 	=4	manning + bords frottant "hach"
                                    #< 	=5	manning + surf frottantes réelles + bords frottant "hach"
                                    #< 	=6	manning + surfaces frottantes réelles correctes en 2d
                                    #< 	=7	manning + surf frottantes réelles correctes en 2d + bords frottant "hach"'''
        self.nirv=0			    ##< inégale répartition de vitesse
        self.nqbgravite=0	    ##<  1: active les débits solides dus à la gravité
        
        self.froudemax=0. #		    #< froude max pour limitation des résultats
        self.frotimpl=0. #	    #< frottement implicite (1) ou pas (0)
        self.frotimpl2=0. #		    #< coeff du pondération du frotement implicite
        self.hfilref=0. #			    #< hauteur de référence pour infiltration modifiée
        self.alti=0. #			    #< altitude de surface libre à laquelle égaliser
        self.epsstat=0. #			    #< epsilon à vérifier pour l'arrêt stationnaire
        self.vresi=0. #			    #< résidu basé sur la variation moyenne des vitesses dans le domaine de calcul
        self.vresi2=0. #			    #< résidu basé sur la variation max de hauteur d'eau dans le domaine de calcul
        self.vresi3=0. #			    #< résidu basé sur la variation moy de hauteur d'eau dans le domaine de calcul
        self.epsstabfond=0. #		    #< epsilon à vérifier pour la stabilisation du fond
        self.vresifond=0. #		    #< résidu basé sur la variation de la topo de fond
        self.epssedim=0.		    ##< epsilon sur h pour recalculer le fond
        self.imult=0. #			    #< indicateur des équations résolues (1 = éq en h et q, 0 = éq en h et u)
        self.imult2=0. #			    #< indicateur des équations résolues (1 = éq sp, 0 = autres)
        self.un_moins_poros=0. #      #< )
        self.facteur_cst1=0. #
        self.facteur_cst2=0. #
        self.expos1=0. #
        self.expos2=0. #
        self.s_moins_un=0. #          #< )
        self.vthetacr=0. #            #< ) paramètres sédimentaires
        self.d_moyen=0. #             #< )
        self.d_90=0. #                #< )
        self.gammacr=0. #             #< )
        self.gammanat=0. #            #< )
        self.param_pente_reduite=0. # #< )
        self.tps_consolidation =0. #  #< )	paramètres fluide frictionnel
        self.r_u0=0. #                #< )
        self.vit_infil_x=0. #         #< )
        self.vit_infil_y=0. #         #< )
        self.cmu=0. #         	    #< )
        self.cnu=0. #                 #< )paramètres du modèle k-e pour la turbulenceread(nl,*) 
        self.c1e=0. #                 #< )
        self.c2e=0. #                 #< )
        self.c3e=0. #                 #< )
        self.cd1=0. #                 #< )
        self.cd2=0. #                 #< )
        self.clk=0. #                 #< )
        self.cle=0. #                 #< )
        self.sigmak=0. #		        #< )
        self.sigmae=0. #		        #< )
        self.cdk=0. #	        	    #< paramètre du modèle k pour la turbulence
        self.vminediv=0. #	        #< valeur min de k pour la division
        self.vminkdiv=0. #	        #< valeur min de e pour la division
        self.vnu_eau=0. #
        self.inv_vnu_eau=0. #         #< 1 / viscosité cinématique de l'eau
        self.vmaxvnut=0. #	        #< viscosité turbulente max

        ##> paramètres de debug - pointeur dans la version précédente
        self.vdebug=[] #		    #< vecteur des 60 paramètres debug par bloc (stockage en real*8)
        
        if type(lines) is list:
            ##reconstruction et limitation
            self.ntyprec            =int(lines[0])		#=0 si rec constante, 1 si rec linéaire
            self.ntyprecfront       =int(lines[1])      #=0 si rec cst, 1 si rec lin non limitée, 2 si rec lin limitée des bords frontière
            self.ntyprecbord        =int(lines[2])      #type de reconstruction des bords libres (0 = cst, 1 = lin limitée (non implémenté), 2 = lin non limitée)
            self.nvoislimit         =int(lines[3])	    #nbre de voisins pour la limitation
            self.nrechzh            =int(lines[4])		#=0 si limitation de h, 1 si limitation de h+z
            self.ntraitefront       =int(lines[5])      #type de traitement des frontières (1 = rien, 0 = moyenne et décentrement unique)
            self.ntypflux           =int(lines[6])	    #type de spliting :
            #paramètres de calcul
            self.nbvar              =int(lines[7])		#nbre d'inconnues du calcul
            self.nbequ              =int(lines[8])		#nbre d'equations à résoudre
            self.froudemax          =float(lines[9])	#froude max pour limitation des résultats
            self.nirv               =int(lines[10])		#inégale répartition de vitesse
            #options
            self.nconflit           =int(lines[11])	    #gestion des conflits (0), ou juste en centré (1) ou pas (2)
            self.ncouvdecouv        =int(lines[12])	    #gestion des éléments couvrants-découvrants ou non
            self.ntypetopo          =int(lines[13])	    #type d'agglomération de la topo (max, min ou moy)
            #options
            self.frotimpl           =float(lines[14])	#frottement : 0 = expl, 1 = impl simple,
                                                        #			 [-1,0[ = impl complet pondéré par ||
            self.ninfil             =int(lines[15])		#infiltration avec mod qté mvt (=2), classique (=1) ou non (=0)
            self.hfilref            =float(lines[16])	#hauteur de référence pour infiltration modifiée
            self.nincli_axes        =int(lines[17])      #type d'inclinaison d'axe : 0 si pas d'inclinaison
            self.iegal              =int(lines[18])		#=1 si égalisation d'altitude
            self.alti               =float(lines[19])	#altitude de surface libre à laquelle égaliser
            self.istat              =int(lines[20])		#arrêt stationnaire (=1 si critère sur v, =2 si sur h)
            self.epsstat            =float(lines[21])	#epsilon à vérifier pour l'arrêt stationnaire
            self.nvartop            =int(lines[22])		#topo variable ou non
                
class prev_boundary_condition():
    '''
	Type des CL générales, faibles et fortes
	@author Pierre Archambeau
    '''
    def __init__(self,x:int,y:int,ntype:int,val:float) -> None:
        self.x=x		    # indice de colonne dans le plus petit maillage
        self.y=y		    # indice de ligne   dans le plus petit maillage
        self.ntype=ntype    # type de cl (h=1,qx=2,qy=3,rien=4,qbx=5,qby=6,hmod=7,fr=8)
        self.val=val		# valeur à imposer

class prev_boundary_conditions():
    '''type pour le stockage des cl générales, faibles et fortes
	@author pierre archambeau
    '''
    
    def __init__(self,parent) -> None:
        self.parent = parent
        self.mybc = []
        
    def read_file(self,lines:list):
        '''#> lecture du fichier de paramètres'''
        for curline in lines:
            tmp=curline.split(',')
            self.mybc.append(prev_boundary_condition(int(tmp[0]),
                                                     int(tmp[1]),
                                                     int(tmp[2]),
                                                     float(tmp[3])))
        
class prev_parameters_simul:
    '''paramètres de simulation
    @author pierre archambeau
    '''
    def __init__(self,parent) -> None:
        
        self.parent = parent

        ##> infos générales
        self.npas=0 #		    #< nbre de pas de simulation à réaliser
        self.dur=0.			    ##< durée souhaitée d'un pas de temps
        self.freq=0.		    ##< fréquence de sortie des résultats
        self.ntypefreq=0	    ##< type de fréquence de sortie des résultats (en temps ou en pas)
        self.ntypewrite=0	##< format d'écriture des résultats (1 = texte, 2 = binaire, 3=csr)
        self.ntyperead=0	    ##< format de lecture des données (1 = texte, 2 = binaire, 3 = binaire par blocs)
        self.nun_seul_resu=0 ##< ecriture d'un seul résu ou pas

        ##> maillage fin
        self.dxfin=0.		##< dx du maillage le + fin = maillage sur lequel sont données
        self.dyfin=0.		##< dy    les caract de topo, frot,...
        self.nxfin=0		##< nbre de noeuds selon x du maillage le + fin
        self.nyfin=0		##< nbre de noeuds selon y du maillage le + fin
        self.xminfin=0.		##< coordonnées absolues inf droites de la matrice des données
        self.yminfin=0.		##<(maillage le plus fin : dxfin et dyfin)

        ##> conditions limites
        self.impfgen=0		##< nbre de cl fortes
        self.impfbxgen=0	##< nbre de cl faibles sur les bords x
        self.impfbygen=0	##< nbre de cl faibles sur les bords y

        self.clf=prev_boundary_conditions(self)
        self.clfbx=prev_boundary_conditions(self)
        self.clfby=prev_boundary_conditions(self)

        ##> stabilité et schéma
        self.ponderation=0	##< indicateur du type de schéma r-k
        # #> lecture du fichier de paramètresvncsouhaite=0.	#< nbre de courant souhaité
        self.mult_dt=0.		##< facteur mult du pas de temps pour vérif a posteriori
        self.noptpas=0		##< =1 si optimisation du pas de temps
        self.nmacc=0		##< mac cormack ou non

        ##> limiteurs
        self.ntyplimit=0	##< 0 si pas de limiteur, 1 si barth jesperson, 2 si venkatakrishnan, 3 si superbee, 4 si van leer, 5 si van albada, 6 si minmod
        self.vkvenka=0.		##< k de venkatakrishnan et des limiteurs modifiés

        # #> constantes de calcul
        self.vminhdiv=0.	##< hauteur min de division
        self.vminh=0.		##< hauteur d'eau min sur 1 maille
        self.vminh2=0.		##< hauteur d'eau min sur 1 maille pour la calculer
        self.nepsrel=0		##< epsilon relatif pour la dtm de q nul sur les bords

        # #>paramètres de calcul
        self.nderdec=0		##< =2 si dérivées centrées, 1 sinon
        self.npentecentree=0##< pente centrée ou non
        self.vlatitude=0.	##< latitude pour le calcul de la force de coriolis

        # #> options
        self.mailonly=0	    ##< 1 si uniquement maillage
        self.nremaillage=0	##< =1 si remaillage
        self.ntronc=0		##< troncature des variables
        self.nsmooth=0		##< =1 si smoothing arithmétique, =2 si smoothing géométrique
        self.nclinst=0		##< cl instationnaires ou pas

        # #> blocs
        self.nblocs=0		##< nombre de blocs
        self.my_param_blocks:list ##< paramètres de blocs

        # #> paramètres de debug
        self.vdebug:list

    def read_file(self):
        '''#> lecture du fichier de paramètres'''
        with open(self.parent.filenamegen+'.trl') as f:
            lines=f.read().splitlines()
            self.translx = float(lines[1])
            self.transly = float(lines[2])
        
        with open(self.parent.filenamegen+'.par') as f:
            lines=f.read().splitlines()

        #Lecture des PARAMETRES GLOBAUX
        #Durée de la simulation et résultats
        self.npas           = np.int64(float(lines[0]))		    #nbre de pas de simulation à réaliser
        self.dur            =float(lines[1])		#durée souhaitée d'un pas de temps
        self.freq           =float(lines[2])		#fréquence de sortie des résultats
        self.ntypefreq      =int(lines[3])	        #type de fréquence de sortie des résultats (en temps ou en pas)
        self.ntypewrite     =int(lines[4])	        #format d'écriture des résultats (1 = texte, 2 = binaire, 3=csr)
        self.ntyperead      =int(lines[5])	        #format de lecture des données (1 = texte, 2 = binaire, 3 = binaire par blocs)
        self.nun_seul_resu  =int(lines[6])          #ecriture d'un seul résu ou pas
        #maillage fin
        self.dxfin          =float(lines[7])		#dx du maillage le + fin = maillage sur lequel sont données
        self.dyfin          =float(lines[8])		#dy    les caract de topo, frot,...
        self.nxfin          =int(lines[9])			#nbre de noeuds selon x du maillage le + fin
        self.nyfin          =int(lines[10])			#					  y
        self.xminfin        =float(lines[11])		#coordonnées absolues inf droites de la matrice des données
        self.yminfin        =float(lines[12])		#(maillage le plus fin : dxfin et dyfin)
        #conditions limites
        self.impfgen        =int(lines[13])			#nbre de cl fortes
        self.impfbxgen      =int(lines[14])		    #nbre de cl faibles sur les bords x
        self.impfbygen      =int(lines[15])		    #nbre de cl faibles sur les bords y
        #stabilité et schéma
        self.ponderation    =float(lines[16])	    #indicateur du type de schéma r-k
        self.vncsouhaite    =float(lines[17])	    #nbre de courant souhaité
        self.mult_dt        =float(lines[18])		#facteur mult du pas de temps pour vérif a posteriori
        self.noptpas        =int(lines[19])			#=1 si optimisation du pas de temps
        self.nmacc          =int(lines[20])			#mac cormack ou non
        #limiteurs
        self.ntyplimit      =int(lines[21])		    #0 si pas de limiteur, 1 si barth jesperson, 2 si venkatakrishnan
                                                    #3 si superbee, 4 si van leer, 5 si van albada, 6 si minmod
        self.vkvenka        =float(lines[22])		#k de venkatakrishnan et des limiteurs modifiés
        #constantes de calcul
        self.vminhdiv       =float(lines[23])	    #hauteur min de division
        self.vminh          =float(lines[24])		#hauteur d'eau min sur 1 maille
        self.vminh2         =float(lines[25])		#hauteur d'eau min sur 1 maille pour la calculer
        self.nepsrel        =int(lines[26])			#epsilon relatif pour la dtm de q nul sur les bords
        #paramètres de calcul
        self.nderdec        =int(lines[27])			#=2 si dérivées centrées, 1 sinon
        self.npentecentree  =int(lines[28])	        #pente centrée ou non
        self.vlatitude      =float(lines[29])	    #latitude pour le calcul de la force de coriolis
        #options
        self.mailonly       =int(lines[30])		    #1 si uniquement maillage
        self.nremaillage    =int(lines[31])		    #=1 si remaillage
        self.ntronc         =int(lines[32])			#troncature des variables
        self.nsmooth        =int(lines[33])			#=1 si smoothing arithmétique, =2 si smoothing géométrique
        self.nclinst        =int(lines[34])			#cl instationnaires ou pas
        #nbre de blocs
        self.nblocs         =int(lines[35])			#nombre de blocs

        # allocation des espaces mémoire pour le stockage des param de blocs
        self.my_param_blocks=[]

        # lecture des parametres propres aux blocs
        decal= 36
        for nbblocs in range(self.nblocs):
            curparambl=prev_parameters_blocks(lines[decal:])
            self.my_param_blocks.append(curparambl)
            decal+=23

        # allocation des matrices contenant les cl générales
        self.clf.read_file(lines[decal:decal+self.impfgen])
        decal+=self.impfgen
        self.clfbx.read_file(lines[decal:decal+self.impfbxgen])
        decal+=self.impfbxgen
        self.clfby.read_file(lines[decal:decal+self.impfbygen])
        decal+=self.impfbygen

        # #lecture des paramètres debug globaux
        self.vdebug=[]
        for i in range(60):
             self.vdebug.append(float(lines[decal+i]))

        decal+=60
        # lecture des paramètres debug par blocs
        for nbblocs in range(self.nblocs):
            for i in range(60):
                self.my_param_blocks[nbblocs].vdebug.append(float(lines[decal+i]))
            decal+=60

class prev_infiltration():
    '''Infiltration
    Gère à la fois le fichier '.fil' (quantités au cours du temps) et '.inf' (matrice)
    @author Pierre Archambeau
    '''
    def __init__(self,parent) -> None:
        self.parent=parent

        self.nb_zones = 0       ##< nombre de zones mentionnées dans .fil
        self.nb_steps = 0       ##< nombre de pas de temps dans .fin

        self.my_Q:np.ndarray    #         #< débits injectés par zone
        self.myarray=WolfArray()   ##< matrice d'infiltration (en entiers)

    def read_file(self):
        '''lecture du fichier'''
        #!Identification du débit total infiltré de la simulation
        with open(self.parent.filenamegen+'.fil','r') as f:
            lines=f.read().splitlines()
        
        self.nb_zones = int(lines[0])
        self.nb_steps = len(lines)-1

        if self.nb_steps>0:
            locarray = [[float(val) for val in lines[i].strip().split(',')[:self.nb_zones+1]] for i in range(1,len(lines))]
            self.my_Q = np.asarray(locarray)        
        
    def read_array(self):
        '''lecture de la matrice d'infiltration'''
        
        self.myarray.set_header(self.parent.get_header())
        self.myarray.filename = self.parent.filenamegen+'.inf'
        self.myarray.wolftype = WOLF_ARRAY_FULL_INTEGER
        self.myarray.read_data()
        
        self.myarray.array.mask = np.logical_not(self.parent.mynap)
        self.myarray.array.data[self.myarray.array.mask]=-1
        
        self.myarray.nbnotnull = self.myarray.array.count()
        self.myarray.nullvalue = -1.
        
        self.myarray.mypal.colormin = np.array([.8,.8,.8])
        self.myarray.mypal.set_bounds()
        
        self.myarray.updatepalette(0)
        self.myarray.loaded=True
        
        pass
        
    def plot_plt(self,show=True):
        
        fig, ax = plt.subplots(1,1)
        shape = self.my_Q.shape
        for i in range(shape[1]):
            ax.plot(self.my_Q[:,0],self.my_Q[:,i+1],label='Infil '+str(i+1))
        
        ax.legend()

        if show:
            plt.show()
      
class prev_suxsuy():
    
    def __init__(self,parent) -> None:
        
        self.parent=parent
        self.filenamesux = self.parent.filenamegen + '.sux'
        self.filenamesuy = self.parent.filenamegen + '.suy'
        
        self.myborders = Zones()
        self.mysux = zone(name='sux')
        self.mysuy = zone(name='sux')
        
        self.myborders.add_zone(self.mysux)
        self.myborders.add_zone(self.mysuy)
        
    def read_file(self):
        
        with open(self.filenamesux,'r') as f:
            linesX=f.read().splitlines()
        with open(self.filenamesuy,'r') as f:
            linesY=f.read().splitlines()
            
        linesX=[np.float64(curline.split(',')) for curline in linesX]
        linesY=[np.float64(curline.split(',')) for curline in linesY]
        
        myparams:prev_parameters_simul
        myparams=self.parent.myparam
        
        dx = myparams.dxfin
        dy = myparams.dyfin
        ox = myparams.xminfin
        oy = myparams.yminfin
        tx = myparams.translx
        ty = myparams.transly
        
        k=1
        for curline in linesX:
            x1 = (curline[0]-1.)*dx + tx + ox
            y1 = (curline[1]-1.)*dy + ty + oy 
            x2 = x1        
            y2 = y1+dy        
            
            vert1 = wolfvertex(x1,y1)
            vert2 = wolfvertex(x2,y2)
            
            curborder = vector(name='b'+str(k))
            
            self.mysux.add_vector(curborder)
            curborder.add_vertex([vert1,vert2])
            
            k+=1
        
        k=1
        for curline in linesY:
            x1 = (curline[0]-1.)*dx + tx + ox
            y1 = (curline[1]-1.)*dy + ty + oy
            x2 = x1+dx        
            y2 = y1        
            
            vert1 = wolfvertex(x1,y1)
            vert2 = wolfvertex(x2,y2)
            
            curborder = vector(name='b'+str(k))
            
            self.mysuy.add_vector(curborder)
            curborder.add_vertex([vert1,vert2])
            
            k+=1
            
        self.myborders.find_minmax(True)

class bloc_file():
    '''objet général permettant la lecture et la manipulation d'un fichier .BLOC'''

    def __init__(self,parent) -> None:
        
        self.parent=parent
        self.filename = self.parent.filenamegen + '.bloc'
        
        self.nb_blocs=0         #     #< nombre de blocs
        self.max_size_cont= 0   #  #< taille maximale des contours
        self.interior=False     #        #< gestion des contours intérieurs --> ne tient pas compte des allers-retours vers les contours internes lors des calculs d'intersection

        self.dx_grid=0.         ##< pas spatial selon X du grid magnétique
        self.dy_grid=0.         ##< pas spatial selon Y du grid magnétique

        self.dx_max=0.          ##< plus grande taille de bloc selon X
        self.dy_max=0.          ##< plus grande taille de bloc selon Y

        self.my_blocks=[]
        self.my_vec_blocks=Zones()        #    #< vecteur des objets blocs
    
    def read_file(self):

        ox = self.parent.myparam.xminfin
        oy = self.parent.myparam.yminfin
        tx = self.parent.myparam.translx
        ty = self.parent.myparam.transly        

        general=zone(name='General')
        self.my_vec_blocks.add_zone(general)                
        external_border=vector(is2D=True,name='external border')    ##< vecteur du contour externe
        general.add_vector(external_border)
        
        myextents = zone(name='Blocks extents')
        self.my_vec_blocks.add_zone(myextents)

        # #ouverture du fichier
        with open(self.filename,'r') as f:
            lines = f.read().splitlines()

        # #lecture du nombre de blocs et de la taille maximale du contour
        tmpline=lines[0].split(',')
        self.nb_blocs  = int(tmpline[0])
        self.max_size_cont = int(tmpline[1])

        # #lecture du nombre de points du contour extérieur
        nb= int(lines[1])

        # #si nb est négatif, il existe une troisième colonne qui dit si le segment est utile ou pas (maillage de zones intérieures)
        if nb<0:
            self.interior=True
        
        nb=np.abs(nb)

        #lecture des données du contour extérieur
        decal=2
        if(self.interior) :
            for i in range(decal,nb+decal):
                tmpline = lines[i].split(',')
                x= float(tmpline[0])+tx
                y= float(tmpline[1])+ty
                in_use= float(tmpline[2])
                curvert = wolfvertex(x,y)
                curvert.in_use= in_use==0.
                
                external_border.add_vertex(curvert)
        else:
            for i in range(decal,nb+decal):
                tmpline = lines[i].split(',')
                x= float(tmpline[0])+tx
                y= float(tmpline[1])+ty
                curvert = wolfvertex(x,y)
                
                external_border.add_vertex(curvert)
        
        external_border.close_force()

        #lecture des données par bloc
        decal = nb+2
        for i in range(self.nb_blocs):
            curextent=bloc_extent(self,lines[decal:])
            myextents.add_vector(curextent.external_border)
            self.my_blocks.append(curextent)
            decal+=curextent.nb+3

        #lecture des tailles de maille pour tous les blocs
        for i in range(self.nb_blocs):
            tmp=lines[decal].split(',')
            self.my_blocks[i].dx = float(tmp[0])
            self.my_blocks[i].dy = float(tmp[1])
            decal+=1
            
        self.my_vec_blocks.find_minmax(True)
        
class bloc_extent():
    
    def __init__(self,parent:bloc_file,lines=[]) -> None:

        self.parent=parent # #< objetparent

        dx = parent.parent.myparam.dxfin
        dy = parent.parent.myparam.dyfin
        ox = parent.parent.myparam.xminfin
        oy = parent.parent.myparam.yminfin
        tx = parent.parent.myparam.translx
        ty = parent.parent.myparam.transly
        
        self.xmin=0.               ##< position minimale selon X du contour une fois qu'il a été "accroché" sur le gri magnétique
        self.xmax=0.               ##< position maximale selon X du contour une fois qu'il a été "accroché" sur le gri magnétique
        self.ymin=0.               ##< position minimale selon Y du contour une fois qu'il a été "accroché" sur le gri magnétique
        self.ymax=0.               ##< position maximale selon Y du contour une fois qu'il a été "accroché" sur le gri magnétique
        self.dx=0.                 ##< taille de discrétisation selon X
        self.dy=0.                 ##< taille de discrétisation selon Y

        self.external_border=vector(name='External_border')     #   #< contour externe du bloc (en coordonnées réelles, c-à-d non translatée vis-à-vis du bloc général)
        
        ##lecture du nombre de points du contour extérieur
        self.nb=int(lines[0])

        ##lecture des données
        for i in range(self.nb):
            tmp = lines[i+1].split(',')
            
            x=float(tmp[0])+ox+tx
            y=float(tmp[1])+oy+ty
            
            curvert=wolfvertex(x,y)
            self.external_border.add_vertex(curvert)

        self.external_border.close_force() ##on force la fermeture du contour extérieur des blocs

        ##emprise du bloc en accord avec le grid magnétique
        tmp = lines[self.nb+1].split(',')
        self.xmin=float(tmp[0])
        self.xmax=float(tmp[1])
        tmp = lines[self.nb+2].split(',')
        self.ymin=float(tmp[0])
        self.ymax=float(tmp[1])

class xy_file(Zones):
    
    def __init__(self, myfile='', ox: float = 0, oy: float = 0, tx: float = 0, ty: float = 0, wxparent=None, simparent=None):
        
        super().__init__(myfile, ox, oy, tx, ty, wxparent)
        
        self.parent = simparent
        
        self.myzone = zone(name='contour')
        self.myvect = vector(name='xy')
        
        self.add_zone(self.myzone)
        self.myzone.add_vector(self.myvect)        
        
        with open(self.parent.filenamegen+'.xy','r') as f:
            lines = f.read().splitlines()
            
        nb = int(lines[0])
        
        splitchar=' '
        if lines[1].find(',')>0:
            splitchar=','
        
        for i in range(nb):
            tmp=re.sub('\\s+', ' ', lines[i+1].strip()).split(splitchar)
            x = float(tmp[0])
            y = float(tmp[1])
            
            curvert = wolfvertex(x,y)
            self.myvect.add_vertex(curvert)
            
        self.find_minmax(True)
