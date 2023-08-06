import sys
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange, MicrosecondLocator
from matplotlib.font_manager import FontProperties
from scipy.interpolate import interp1d
import os
import ctypes as ct

from .Outlet import *
from .Dumping import *
from ..PyTranslate import _

class RetentionBasin():

    surfaceDrainedHydro:float # TO BUILD !!!!!!!!!!!!!!


    def __init__(self, _dateBegin, _dateEnd, _deltaT, _time=[], _id='J1', _name='Default name', _type='', _dictRB={}, _directDictRB={}, _tz=0, _outletNames=[], withRBDict=True):
        print('Creation of a RetentionBasin!')
        self.iD = _id
        self.name = _name
        self.type = _type
        self.time = _time
        self.dictRB = {}
        self.alreadyUsed = False
        self.isLeveled = False
        self.myLevel = 2
        self.dateBegin = _dateBegin
        self.dateEnd = _dateEnd
        self.deltaT = _deltaT
        self.tz = _tz
        if(_time==[]):
            tzDelta = datetime.timedelta(hours=self.tz)
            ti = datetime.datetime.timestamp(self.dateBegin-tzDelta)
            tf = datetime.datetime.timestamp(self.dateEnd-tzDelta)
            self.time = np.arange(ti,tf+self.deltaT,self.deltaT)


        self.x = 0.0
        self.y = 0.0
        self.surfaceDrainedHydro = 0.0

        # Dimensions
        self.hFloor = 0.0
        self.hBank = 0.0
        self.hStagn = 0.0
        self.volume = 0.0
        self.surface = 0.0
        self.hi = 0.0

        # inlets and outlets
        self.intletsObj = {}
        self.inlets = []
        self.inletsRaw = []

        self.directFluxObj = {}
        self.directFluxInRB = []
        self.directFluxInRB_Raw = []
        self.downstreamObj = {}
        self.outFlow = {}
        if(_outletNames != []):
            for i in range(len(_outletNames)):
                self.outFlow[_outletNames[i]]={}
                self.outFlow[_outletNames[i]]["Net"] = []
                self.outFlow[_outletNames[i]]["Raw"] = []
                self.downstreamObj[_outletNames[i]] = None
        # self.outFlowRaw = []

        self.rain = []
        
        self.filledVolume = []
        self.qLim = None        # object to compute "l'ecretage"

        self.outletObj = None   # object to compute the outlet 

        self.zData = []         # height from z-v file stored 
        self.vData = []         # volume from z-v file stored
        self.zvInterpol = None

        self.timeDelay = 0.0    # [s]????? -> A vérifier!!!
        self.timeDelayObj = None

        self.peakVal = 0.0                          # [m³/s] peak value for total outFlow
        self.peakTime = None                        # datetime of the peak for total outflow -> time delay is already applied


        if(_dictRB!={}):
            # Init of the object allowing to determine the outlet flux
            tmpCounter = 0
            for element in _dictRB:
                if(_dictRB[element]['from']['value'] == self.iD):
                    if(tmpCounter>0):
                        print("ERROR: the same RB associated to two different caracteristics. Please check the RetentionBasin.postPro file.")
                        sys.exit()
                    self.dictRB = _dictRB[element]
                    tmpCounter +=1
            if(tmpCounter == 0):
                print("Error: no RB associated! Please check the RetentionBasin.postPro file.")
                sys.exit()
        elif(_directDictRB!={}):
            self.dictRB = _directDictRB
        elif(withRBDict):
            print("ERROR: Not enough elements, it lacks a least a dictionary!")
            print("Do you still want to continue [Y-YES] [N-NO]?")
            myAnswer = input("Enter your answer:")
            isOk = False
            while(not isOk):
                if(myAnswer=="Y" or myAnswer=="y"):
                    isOk = True
                    self.dictRB['type'] = {}
                    self.dictRB['type']['value'] = ""
                elif(myAnswer=="N" or myAnswer=="n"):
                    sys.exit()
        else:
            self.dictRB['type'] = {}
            self.dictRB['type']['value'] = ""
            


        self.type = self.dictRB['type']['value']
        if('stagnant height' in self.dictRB):
            self.hStagn =  float(self.dictRB['stagnant height']['value'])
        if(self.type == 'HighwayRB'):
            self.surface = float(self.dictRB['surface']['value'])
            self.hBank = float(self.dictRB['height 2']['value'])
            self.volume = self.surface * self.hBank
        elif(self.type == 'RobiernuRB'):
            self.volume = float(self.dictRB['volume']['value'])
        elif(self.type == 'OrbaisRB'):
            self.volume = float(self.dictRB['volume']['value'])
            try:
                zvFile = self.dictRB['Z-V file']['value']
            except:
                zvFile = ""
            if(zvFile!=""):
                zvFile = zvFile.replace("\\", "/")
                self.read_zv(zvFile)
                
            # self.qLim = float(self.dictRB['ecretage']['value'])
        # elif(self.type == 'HelleRB'):
        #     self.volume = float(self.dictRB['volume']['value'])
        #     print("ERROR: Not implemented yet!")
        #     sys.exit()
        elif(self.type == 'ForcedDam'):
            self.volume = float(self.dictRB['volume']['value'])
            self.hi = float(self.dictRB['initial height']['value'])
            try:
                zvFile = self.dictRB['Z-V file']['value']
            except:
                zvFile = ""
            if(zvFile!=""):
                zvFile = zvFile.replace("\\", "/")
                self.read_zv(zvFile)
            if("time delay" in self.dictRB):
                self.timeDelay = float(self.dictRB["time delay"]["value"])
        elif(self.type == "HelleRB"):
            self.volume = float(self.dictRB['volume']['value'])
            try:
                zvFile = self.dictRB['Z-V file']['value']
            except:
                zvFile = ""
            if(zvFile!=""):
                zvFile = zvFile.replace("\\", "/")
                self.read_zv(zvFile)

        else:
            print("WARNING: This type RB was not recognised! Please check the RetentionBasin.postPro file.")


        if ("initial height" in self.dictRB):
            self.hi = float(self.dictRB['initial height']['value'])
        
        if("time delay" in self.dictRB):
            self.timeDelay = float(self.dictRB["time delay"]["value"])

         # Creation of Outlet object
        self.outletObj = Outlet(self.dictRB)
        self.qLim = Dumping(self.dictRB)
        
        
        
        # if('direct inside RB' in self.myCatchment[self.iD]):
        #     if(self.myCatchment[self.iD]['direct inside RB'] != ''):
        #         self.sum_directFluxInRB()
        # self.sumHydro = self.run()
        # print(self.sumHydro)<


    def increment_level(self):
        "This procedure increment the level in the Topo dictionary"
        self.myLevel += 1


    def add_inlet(self, toPoint, name="DEFAULT"):
        "This procedure link the inlets to the object"
        self.intletsObj[name] = toPoint

        if("time delay from module" in self.dictRB):
            nameModule = self.dictRB["time delay from module"]['value']
            if(toPoint.iD == nameModule):
                self.timeDelay = toPoint.timeDelay
                self.x = toPoint.x
                self.y = toPoint.y
        


    def add_downstreamObj(self, toPoint, name="DEFAULT", deltaTime=0.0, tolerance=0):
        """This procedure link the downstream element to the object
            tolerance indicates if the downstream objet should already exist (=0) to continue => to implement
        """
        if toPoint!=None:
            self.downstreamObj[name] = toPoint
            if(name in self.downstreamObj):
                self.downstreamObj[name] = toPoint
            else:
                print("ERROR: this outlet name is not recognised!")
                sys.exit()
        
        self.outFlow[name] = {}
        self.outFlow[name]["Net"] = []
        self.outFlow[name]["Raw"] = []
        self.outFlow[name]["delta time"] = deltaTime

        if("time delay from module" in self.dictRB):
            nameModule = self.dictRB["time delay from module"]['value']
            if(toPoint.iD == nameModule):
                self.timeDelay = toPoint.timeDelay
                self.x = toPoint.x
                self.y = toPoint.y


    def add_directFluxObj(self, toPoint, name="DEFAULT"):
        "This procedure link the direct inlet elements to the object"
        self.directFluxObj[name] = toPoint

        if("time delay from module" in self.dictRB):
            nameModule = self.dictRB["time delay from module"]['value']
            if(toPoint.iD == nameModule):
                self.timeDelay = toPoint.timeDelay
                self.x = toPoint.x
                self.y = toPoint.y


    def compute_hydro(self, givenDirectFluxIn=[], givenInlet=[]):
        """ This function computes the raw and real hydrographs.
            
            The volume filled and then the water height in the RB at time $t$ will be evaluated will depend of the flows
            at time $t-1$ exept if the 

            Internal variables modified : self.inlets, self.inletsRaw, 
                                        self.directFluxInRB, self.directFluxInRB_Raw,
                                        self.outFlowRaw, self.outFlow, self.filledVolume
        """
        self.sum_inlets(givenInlet)
        self.sum_directFluxInRB(givenDirectFluxIn)
        mainNameOut = list(self.outFlow.items())[0][0]
        # In the Raw hydrograph the first outlet is considered to be the main one. Therefore the exit where the flux would go if the structure were to present
        self.outFlow[mainNameOut]["Raw"] = self.inletsRaw + self.directFluxInRB_Raw
        for iOutFlow in range(1,len(list(self.outFlow.items()))):
            nameOut = list(self.outFlow.items())[iOutFlow][0]
            self.outFlow[nameOut]["Raw"] = np.zeros(len(self.inletsRaw))

        # sizeOfHydro = len(self.time)-1
        sizeOfHydro = len(self.time)    # Size of hydro is no longer t-1 smaller than time
        # Volume of the RB filled with water
        self.filledVolume = np.zeros(sizeOfHydro)
        for elOutFlow in self.outFlow:
            self.outFlow[elOutFlow]["Net"] =  np.zeros(sizeOfHydro)
        
        self.filledVolume[0] = self.h_to_volume(self.hi)
        outFlowReservoir = np.zeros(sizeOfHydro)
        for i in range(1,sizeOfHydro):
            # # To avoid a division by zero and physically correct.
            # if(self.surface == 0.0):
            #     h = 0.0
            # else:
            #     h = self.filledVolume[i-1]/self.surface
            # 1st evaluation of the outlet of the RB according to Vfilled at the previous time
            h = self.volume_to_h(self.filledVolume[i-1])
            # Qout = self.outletObj.compute(h,self.time[self.convert_index_global_to_local(i)])
            Qout = self.outletObj.compute(h,self.convert_time_global_to_local(self.time[i]))
            qLim = self.qLim.compute(h,self.convert_time_global_to_local(self.time[i]))
            diff = self.directFluxInRB[i-1]+max(self.inlets[i-1]-qLim,0.)-Qout
            outFlowReservoir[i-1]=Qout
            # If the volume increase => the outflow is kept (Maybe to improve!! The height can go to the upper threshold)
            if diff>0:
                self.filledVolume[i] = self.filledVolume[i-1] + diff*(self.time[i]-self.time[i-1])
            # If the volume is decreasing but is not enough to empty it at this time step
            elif self.filledVolume[i-1]>abs(diff*(self.time[i]-self.time[i-1])):
                self.filledVolume[i] = self.filledVolume[i-1] + diff*(self.time[i]-self.time[i-1])
                # if(self.surface == 0.0):
                #     h = 0.0
                # else:
                #     h = self.filledVolume[i]/self.surface
                h = self.volume_to_h(self.filledVolume[i])
                # All the values:
                    # -outlet, 
                    # -ecretage,
                    # -volume,
                # will be reevaluated. Because we can go to the lower threshold.
                # Qout = self.outletObj.compute(h,self.time[self.convert_index_global_to_local(i)])
                Qout = self.outletObj.compute(h,self.convert_time_global_to_local(self.time[i]))
                qLim = self.qLim.compute(h,self.convert_time_global_to_local(self.time[i]))
                diff = self.directFluxInRB[i-1]+max(self.inlets[i-1]-qLim,0.)-Qout
                outFlowReservoir[i-1] = Qout
                self.filledVolume[i] = self.filledVolume[i-1] + diff*(self.time[i]-self.time[i-1])


            else:
                self.filledVolume[i] =0
                outFlowReservoir[i-1] = self.filledVolume[i-1]/((self.time[i]-self.time[i-1]))+self.directFluxInRB[i-1]+max(self.inlets[i-1]-qLim,0.)

            if self.filledVolume[i]>self.volume:
                outFlowReservoir[i-1] += (self.filledVolume[i]-self.volume)/((self.time[i]-self.time[i-1]))
                self.filledVolume[i] = self.volume

            self.outFlow = self.compute_final(outFlowReservoir[i-1],min(self.inlets[i-1],qLim),i-1)
            # self.outFlow[i-1]+=min(self.inlets[i-1],qLim)

        return self.outFlow
            

    def sum_inlets(self, givenInlet=[]):
        """ This procedure sum all the inlets of the RB
            Caution: inlets variable is different from directFluxIn !!

            Internal variables modified: self.inlets, self.inletsRaw
        """
        if(self.intletsObj != {}):
            nameOutFlow = list(self.intletsObj.items())[0][0]
            self.inlets = self.intletsObj[nameOutFlow].outFlow[nameOutFlow]["Net"].copy()
            self.inletsRaw = self.intletsObj[nameOutFlow].outFlow[nameOutFlow]["Raw"].copy()
            for i in range(1,len(list(self.intletsObj.items()))):
                nameOutFlow = list(self.intletsObj.items())[i][0]
                self.inlets += self.intletsObj[nameOutFlow].outFlow[nameOutFlow]["Net"]
                self.inletsRaw += self.intletsObj[nameOutFlow].outFlow[nameOutFlow]["Raw"]
        elif(givenInlet != []):
            if(len(givenInlet)!=len(self.time)-1):
                print("ERROR: the dimension of the time array and the given inlet are not the same!")
                sys.exit()
            self.inlets = givenInlet
            self.inletsRaw = givenInlet
        else:
            # self.inlets = np.zeros(len(self.time)-1)        # the size of outflow will always be 1 element smaller than time (convention)
            # self.inletsRaw = np.zeros(len(self.time)-1)     # the size of outflow will always be 1 element smaller than time (convention)
            self.inlets = np.zeros(len(self.time))        # the size of outflow is no longer 1 element smaller than time (convention)
            self.inletsRaw = np.zeros(len(self.time))     # the size of outflow is no longer 1 element smaller than time (convention)


    def sum_directFluxInRB(self, givenDirectFluxIn=[]):
        """This procedure computes the flux going directly inside the RB

            Internal variables modified: self.directFluxInRB, self.directFluxInRB_Raw
        """
        if(self.directFluxObj != {}):
            nameOutFlow = list(self.directFluxObj.items())[0][0]
            self.directFluxInRB = self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Net"].copy()
            self.directFluxInRB_Raw = self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Raw"].copy()
            for i in range(1,len(list(self.directFluxObj.items()))):
                nameOutFlow = list(self.directFluxObj.items())[i][0]
                try:
                    self.directFluxInRB += self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Net"]
                except:
                        print("Hello!!!! TO CHANGE!!!!")
                        nbElT = len(self.directFluxInRB)
                        nbTMP = len(self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Net"])
                        if(nbElT==nbTMP+1):
                            tmpHydro = self.directFluxInRB.copy()
                            self.directFluxInRB = np.zeros(nbTMP)
                            self.directFluxInRB[:] = tmpHydro[:-1]
                            self.directFluxInRB += self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Net"]
                        elif(nbTMP==nbElT+1):
                            self.directFluxInRB[:] = self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Net"][:-1]
                        else:
                            print("Hello!!!! ERROR!!!!")

                # self.directFluxInRB_Raw += self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Raw"]
                try:
                    self.directFluxInRB_Raw += self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Raw"]
                except:
                        print("Hello!!!! TO CHANGE!!!!")
                        nbElT = len(self.directFluxInRB_Raw)
                        nbTMP = len(self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Raw"])
                        if(nbElT==nbTMP+1):
                            tmpHydro = self.directFluxInRB_Raw.copy()
                            self.directFluxInRB_Raw = np.zeros(nbTMP)
                            self.directFluxInRB_Raw[:] = tmpHydro[:-1]
                            self.directFluxInRB_Raw += self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Raw"]
                        elif(nbTMP==nbElT+1):
                            self.directFluxInRB_Raw[:] = self.directFluxObj[nameOutFlow].outFlow[nameOutFlow]["Raw"][:-1]
                        else:
                            print("Hello!!!! ERROR!!!!")

        elif(givenDirectFluxIn != []):
            if(len(givenDirectFluxIn)!=len(self.time)-1):
                print("ERROR: the dimension of the time array and the given inlet are not the same!")
                sys.exit()
            self.directFluxInRB = givenDirectFluxIn
            self.directFluxInRB_Raw = givenDirectFluxIn
        else:
            # self.directFluxInRB = np.zeros(len(self.time)-1)
            # self.directFluxInRB_Raw = np.zeros(len(self.time)-1)
            self.directFluxInRB = np.zeros(len(self.time))
            self.directFluxInRB_Raw = np.zeros(len(self.time))


    def plot(self, workingDir, plotRaw=True, axis="Hours",rangeData=[], deltaMajorTicks=24.0*3600.0, deltaMinorTicks=3600.0, tzPlot=0, unitReservoir="[m^3]"):
        ''' This procedure plots:
        - the inlets: in color chosen randomly by matplotlib
        - DirectIn : in color chosen randomly by matplotlib and in '-.' lines
        - the outlet: in black solid line 
        - the raw outlet: in black dashed line
        '''

        # x = self.time/3600.0
        if(axis=="Hours"):
            x = (self.time[:-1]-self.time[0])/3600.0
        else:
            tzDelta = datetime.timedelta(seconds=tzPlot*3600.0)
            timeDelayDelta = datetime.timedelta(seconds=self.timeDelay)
            beginDate = datetime.datetime.fromtimestamp(self.time[0], tz=datetime.timezone.utc)+tzDelta-timeDelayDelta
            endDate = datetime.datetime.fromtimestamp(self.time[-1], tz=datetime.timezone.utc)+tzDelta-timeDelayDelta
            dt = self.time[1]-self.time[0]
            time_delta = datetime.timedelta(seconds=dt)
            if(rangeData==[]):
                rangeData = [beginDate,endDate]
            x_date = drange(beginDate, endDate, time_delta)
        
        font11 = FontProperties()
        font11.set_family('serif')
        font11.set_name('Euclid')
        font11.set_size(11)

        font14 = FontProperties()
        font14.set_family('serif')
        font14.set_name('Euclid')
        font14.set_size(14)

        fig = plt.figure(figsize=(8.3, 11.7))
        ax1 = plt.subplot(2,1,1)

        # plt.subplot(2,1,1)
        # ax1.grid()
        
        if(axis=="Hours"):
            ax1.set_xlabel('Temps [h]', fontproperties=font11)
        else:
            ax1.set_xlabel('Date (GMT+'+str(tzPlot)+')', fontproperties=font11)
        ax1.set_ylabel('Débits [m³/s]', fontproperties=font11)
        fig.legend(loc="upper right")
        fig.suptitle(self.name + " Hydrogrammes écrêtés", fontproperties=font14)



        for iInlet in self.intletsObj:

            y = self.intletsObj[iInlet].outFlow[iInlet]["Net"]
            name = self.intletsObj[iInlet].name + " " + iInlet
            if(axis=="Hours"):
                ax1.plot(x, y, label = name)
            else:
                ax1.plot_date(x_date, y, '-', label = name)
        for iInlet in self.directFluxObj :
            y = self.directFluxObj[iInlet].outFlow[iInlet]["Net"]
            name = self.directFluxObj[iInlet].name + " " + iInlet
            if(name=="ss 18" or name=="ss 19"):
                name = "Qin BV"

            if(axis=="Hours"):    
                ax1.plot(x, y, '-.', label = name)
            else:
                ax1.plot_date(x_date, y, '-.', label = name)
        
        for iOutFlow in self.outFlow:
            y = self.outFlow[iOutFlow]["Net"]
            
            if(axis=="Hours"):
                ax1.plot(x, y, label = self.name+" "+iOutFlow, color='k')
            else:
                ax1.plot_date(x_date, y, '-', label = self.name+" "+iOutFlow, color='k')
        
        if(plotRaw):
            nameMainOut = list(self.outFlow.items())[0][0]
            y = self.outFlow[nameMainOut]["Raw"]

            if(axis=="Hours"):
                ax1.plot(x, y, '--', label = self.name+' Raw', color='k')
            else:
                ax1.plot(x_date, y, '--', label = self.name+' Raw', color='k')
        
        if(axis=="Hours"):
            ax1.set_xlim(x[0], x[len(x)-1])
            ax1.grid()

        else:
            ax1.set_xlim(rangeData[0], rangeData[1])


            for label in ax1.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment('right')
            ax1.tick_params(axis='y',labelcolor='k')


            if(deltaMajorTicks>0):
                majorTicks = HourLocator(interval=math.floor(deltaMajorTicks/3600))
                # majorTicks = drange(beginDate, endDate, deltaTimeMajorTicks)
                # ax1.set_xticks(majorTicks)
                ax1.xaxis.set_major_locator(majorTicks)
                ax1.grid(which='major', alpha=1.0)
                

                if(deltaMinorTicks>0):
                    # deltaTimeMinorTicks = datetime.timedelta(seconds=deltaMinorTicks)
                    # minorTicks = drange(beginDate, endDate, deltaTimeMinorTicks)
                    # ax1.set_xticks(minorTicks, minor=True)
                    # ax1.grid(which='minor', alpha=0.2)
                    ax1.minorticks_on()
                    minorTicks = MicrosecondLocator(interval=deltaMinorTicks*1E6)
                    ax1.xaxis.set_minor_locator(minorTicks)
                    # plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
                    ax1.grid(which='minor', alpha=0.2)
            else:
                ax1.grid()


        fig.legend(prop=font11)
        try:
            fig.savefig(workingDir+'PostProcess/QT_HydroEcrete_'+self.name+'.pdf')
        except:
            fig.savefig(workingDir+'/QT_HydroEcrete_'+self.name+'.pdf')

        ax2 = plt.subplot(2,1,2)


        ax2.set_xlabel('Temps [h]', fontproperties=font11)
        fig.legend(loc="upper right", prop=font11)
        fig.suptitle("Volume cumulé", fontproperties=font11)
        if unitReservoir == "[m^3]":
            ax2.set_ylabel('Volume [m³]', fontproperties=font11)
            y = self.filledVolume
        else:
            ax2.set_ylabel('Height [m]', fontproperties=font11)
            myH = np.zeros(len(self.filledVolume))
            for ii in range(len(self.filledVolume)):
                myH[ii] =  self.volume_to_h(self.filledVolume[ii])
            y = myH


        if(axis=="Hours"):
            ax2.plot(x, y, label = self.name)
            if unitReservoir == "[m^3]":
                y = self.volume*np.ones(len(x))
            else:
                y = self.hBank*np.ones(len(x))
        else:
            ax2.plot_date(x_date, y, '-', label = self.name)
            if unitReservoir == "[m^3]":
                y = self.volume*np.ones(len(x_date))
            else:
                y = self.hBank*np.ones(len(x_date))
        if(axis=="Hours"):
            if unitReservoir == "[m^3]":
                ax2.plot(x, y, '--', label = "Volume max")
            else:
                ax2.plot(x, y, '--', label = "Height max")
            ax2.set_xlim(x[0], x[len(x)-1])
            ax2.grid()
        else:
            if unitReservoir == "[m^3]":
                ax2.plot_date(x_date, y, '--', label = "Volume max")
            else:
                ax2.plot_date(x_date, y, '--', label = "Height max")
            ax2.set_xlim(rangeData[0], rangeData[1])

        
            for label in ax2.get_xticklabels():
                label.set_rotation(30)
                label.set_horizontalalignment('right')
            ax2.tick_params(axis='y',labelcolor='k')

            if(deltaMajorTicks>0):
                majorTicks = HourLocator(interval=math.floor(deltaMajorTicks/3600))
                ax2.xaxis.set_major_locator(majorTicks)
                ax2.grid(which='major', alpha=1.0)
                

                if(deltaMinorTicks>0):
                    ax2.minorticks_on()
                    minorTicks = MicrosecondLocator(interval=deltaMinorTicks*1E6)
                    ax2.xaxis.set_minor_locator(minorTicks)
                    ax2.grid(which='minor', alpha=0.2)
            else:
                ax2.grid()

        fig.legend(prop=font11)
        fig.savefig(workingDir+'PostProcess'+self.name+'.pdf')


    def add_rain(self, workingDir, tzDelta=datetime.timedelta(hours=0)):
        """ This function returns the a time array and a array containing the sum of all the rain in the inlets
            Value changed :  self.rain
        """
        if(self.directFluxObj == {}):
            nameInit = list(self.intletsObj.items())[0][0]
            rain = np.zeros(len(self.intletsObj[nameInit].rain))
        else:
            nameInit = list(self.directFluxObj.items())[0][0]
            rain = np.zeros(len(self.directFluxObj[nameInit].rain))
        for iInlet in self.intletsObj:
            rain += self.intletsObj[iInlet].rain
        for iInlet in self.directFluxObj:
            rain += self.directFluxObj[iInlet].rain
        self.rain = rain
        return self.time

    
    def volume_to_h(self, volume):

        if(volume==0.0):
            h=0
        elif(self.zData!=[]):
            if(volume>max(self.zvVtoHInterpol.x)):
                # h = max(self.zvVtoHInterpol.y)
                slope = (self.zvVtoHInterpol.y[-1]-self.zvVtoHInterpol.y[-2])/(self.zvVtoHInterpol.x[-1]-self.zvVtoHInterpol.x[-2])
                h = slope*(volume-self.zvVtoHInterpol.x[-1])+max(self.zvVtoHInterpol.y)
            else:
                h = self.zvVtoHInterpol(volume)
        else:
            if(self.surface == 0.0):
                h = 0.0
            else:
                h = volume/self.surface
        
        return h


    def h_to_volume(self, h):

        if(h==0):
            vol = 0
        elif(self.zData!=[]):
            if(h>max(self.zvHtoVInterpol.x)):
                # h_tmp=max(self.zvHtoVInterpol.x)
                # vol = self.zvHtoVInterpol(h_tmp)
                
                slope = (self.zvHtoVInterpol.y[-1]-self.zvHtoVInterpol.y[-2])/(self.zvHtoVInterpol.x[-1]-self.zvHtoVInterpol.x[-2])
                vol = slope*(h-self.zvHtoVInterpol.x[-1])+max(self.zvHtoVInterpol.y)
            else:
                vol = self.zvHtoVInterpol(h)
        else:
            vol = h*self.surface
        
        return vol
    

    def read_zv(self, fileName, typeOfInterpolation='linear'):

        if os.path.exists(fileName):
            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = list(data_reader)
            matrixData = np.array(list_data).astype("float")
            self.zData = matrixData[:,0]
            self.vData = matrixData[:,1]

            self.zvVtoHInterpol = interp1d(self.vData,self.zData,kind=typeOfInterpolation)  # kind is 'linear' by default in interp1d
            self.zvHtoVInterpol = interp1d(self.zData,self.vData,kind=typeOfInterpolation)

    
    def convert_index_global_to_local(self, i, lagTime=0.0):

        index = math.floor(self.timeDelay/(self.time[1]-self.time[0]))
        index = i - index

        if(index<0):
            index = 0

        return index


    
    def convert_data_global_to_local(self, dataGlob):

        dataLoc = np.zeros(len(dataGlob))

        myIndex = math.floor(self.timeDelay/(self.time[1]-self.time[0]))
        if(myIndex==0): 
            dataLoc = dataGlob[:]
        elif(myIndex<len(dataLoc)):
            dataLoc[:-myIndex] = dataGlob[myIndex:]
        else:
            print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
            sys.exit()

        return dataLoc




    def convert_index_global_to_other_global(self, i, timeDelayOut=0.0, timeDelta=0.0):

        index = math.floor((self.timeDelay-timeDelayOut-timeDelta)/(self.time[1]-self.time[0]))
        index = i - index

        # if(index<0):
        #     index = 0

        return index



    def convert_data_global_to_other_global(self, vector, timeDelayOut=0.0, timeDelta=0.0):

        myIndex = self.convert_data_global_to_other_global(0, timeDelayOut=timeDelayOut, timeDelta=timeDelta)

        result = np.zeros(len(vector))
        if(myIndex==0): 
            result = vector[:]
        elif(abs(myIndex)<len(vector)):
            if(myIndex>0):
                result[:-myIndex] = vector[myIndex:]
            else:
                result[myIndex:] = vector[:-myIndex]
        else:
            print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
            sys.exit()
        
        return result



    def convert_time_global_to_local(self, time):

        realTime = time - self.timeDelay

        return realTime




    def get_outFlow(self, whichOutFlow="", typeOutFlow="Net", unit="m3/s"):


        if(whichOutFlow==""):
            nameOutFlow = list(self.outFlow.items())[0][0]
            myOutFlow = self.outFlow[nameOutFlow][typeOutFlow].copy()
        else:
            myOutFlow = self.outFlow[whichOutFlow][typeOutFlow].copy()

        if unit=='mm/h':
            if self.surfaceDrainedHydro==0.0:
                print("ERROR: the surface drained = 0! Not possible to express the outFlow in mm/s!")
                sys.exit()
            myOutFlow *= 3.6/self.surfaceDrainedHydro

        
        return myOutFlow


    def get_outFlow_noDelay(self, whichOutFlow="", unit="m3/s"):
        '''
        This function returns the total outlet of the basin and considers t0=0 at the outlet of the 
        subbasin without considering timeDelay (the time of the real outlet of the whole potential catchment)
        '''

        if(whichOutFlow==""):
            nameOutFlow = list(self.outFlow.items())[0][0]
            outFlowOut = self.outFlow[nameOutFlow]["Net"]
        else:
            outFlowOut = self.outFlow[whichOutFlow]["Net"]

        tmpHydro = np.zeros(len(outFlowOut))
        index = math.floor(self.timeDelay/self.deltaT)
        if(index==0): 
            tmpHydro = outFlowOut
        elif(index<len(outFlowOut)):
            tmpHydro[:-index] = outFlowOut[index:]
        else:
            print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
            sys.exit()

        if unit=='mm/h':
            if self.surfaceDrainedHydro==0.0:
                print("ERROR: the surface drained = 0! Not possible to express the outFlow in mm/s!")
                sys.exit()
            tmpHydro *= 3.6/self.surfaceDrainedHydro


        return tmpHydro


    
    def get_outFlowRaw_noDelay(self, whichOutFlow="", unit="m3/s"):
        '''
        This function returns the total raw outlet of the basin and considers t0=0 at the outlet of the 
        subbasin without considering timeDelay (the time of the real outlet of the whole potential catchment)
        '''

        if(whichOutFlow==""):
            nameOutFlow = list(self.outFlow.items())[0][0]
            outFlowOut = self.outFlow[nameOutFlow]["Raw"]
        else:
            outFlowOut = self.outFlow[whichOutFlow]["Raw"]

        tmpHydro = np.zeros(len(outFlowOut))
        index = math.floor(self.timeDelay/self.deltaT)
        if(index==0): 
            tmpHydro = outFlowOut
        elif(index<len(outFlowOut)):
            tmpHydro[:-index] = outFlowOut[index:]
        else:
            print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
            sys.exit()

        if unit=='mm/h':
            if self.surfaceDrainedHydro==0.0:
                print("ERROR: the surface drained = 0! Not possible to express the outFlow in mm/s!")
                sys.exit()
            tmpHydro *= 3.6/self.surfaceDrainedHydro


        return tmpHydro

    
    def write_height_reservoir(self, workingDir):

        myH = np.zeros(len(self.filledVolume))
        for ii in range(len(self.filledVolume)):
            myH[ii] =  self.volume_to_h(self.filledVolume[ii])
    
        DataWrite = []
        for ii in range(len(self.filledVolume)):
            dateData = datetime.datetime.fromtimestamp(self.time[ii]-self.timeDelay,tz=datetime.timezone.utc)
            strDated = dateData.strftime("%d/%m/%Y %H:%M:%S")
            DataWrite.append([strDated, myH[ii]])
        
        fname=os.path.join(workingDir,self.name+'_H.csv')
        if os.path.exists(fname):
            f = open(fname, 'w')
            writer = csv.writer(f, delimiter="\t")
            for row in DataWrite:
                writer.writerow(row)



    
    def compute_final(self, Qres, Qstream, step):
        
        mainNameOut = list(self.outFlow.items())[0][0]
        if(self.type == "HelleRB"):
            # Natural exit
            self.outFlow[mainNameOut]["Net"][step] = Qres

            # Artificial exit
            nameArtificialExit = list(self.outFlow.items())[1][0]
            timeDelayNextRB = self.downstreamObj[nameArtificialExit].timeDelay
            timeDelta = self.outFlow[nameArtificialExit]["delta time"]
            newStep = self.convert_index_global_to_other_global(step,timeDelayOut=timeDelayNextRB,timeDelta=timeDelta)
            if(newStep>0 and newStep<len(self.outFlow[nameArtificialExit]["Net"])):
                self.outFlow[nameArtificialExit]["Net"][newStep] = Qstream 
        
        else:
            self.outFlow[mainNameOut]["Net"][step] = Qstream + Qres

        
        return self.outFlow

    
    def get_surface_proportions(self, show=True):       

        myNames = []
        mySurf = []
        for element in self.intletsObj:
            curObj = self.intletsObj[element]
            curName, curSurf = curObj.get_surface_proportions(show=False)
            myNames.append(curName)
            mySurf.append(curSurf)

        if show==True:
            print("To DO!!!")()


    
    def find_outFlow_peak(self, whichOutFlow=""):

        myOutFlow = self.get_outflow(typeOutFlow="Net", whichOutFlow=whichOutFlow)
        
        maxIndex = np.argmax(myOutFlow)
        maxValue = myOutFlow[maxIndex]
        maxTime = self.time[maxIndex]
        maxDatetime = datetime.datetime.fromtimestamp(maxTime, tz=datetime.timezone.utc)

        self.peakVal = maxValue
        self.peakTime = maxDatetime


    
    def get_outFlow_peak(self, noDelay=False, whichOutFlow=""):

        if(self.peakVal==0.0 or self.peakTime==None):
            self.find_outFlow_peak(whichOutFlow=whichOutFlow)
        
        maxValue = self.peakVal
        maxDatetime = self.peakTime

        if(noDelay):
            detlaTimeDelay = datetime.timedelta(seconds=self.timeDelay)
            maxDatetime -= detlaTimeDelay

        return maxValue, maxDatetime





    def compute_hydro2(self, givenDirectFluxIn=[], givenInlet=[], givenV:list=[]):
        """ This function computes the raw and real hydrographs.
            
            The volume filled and then the water height in the RB at time $t$ will be evaluated will depend of the flows
            at time $t-1$ exept if the 

            Internal variables modified : self.inlets, self.inletsRaw, 
                                        self.directFluxInRB, self.directFluxInRB_Raw,
                                        self.outFlowRaw, self.outFlow, self.filledVolume
        """
        self.sum_inlets(givenInlet)
        self.sum_directFluxInRB(givenDirectFluxIn)
        mainNameOut = list(self.outFlow.items())[0][0]
        # In the Raw hydrograph the first outlet is considered to be the main one. Therefore the exit where the flux would go if the structure were to present
        self.outFlow[mainNameOut]["Raw"] = self.inletsRaw + self.directFluxInRB_Raw
        for iOutFlow in range(1,len(list(self.outFlow.items()))):
            nameOut = list(self.outFlow.items())[iOutFlow][0]
            self.outFlow[nameOut]["Raw"] = np.zeros(len(self.inletsRaw))

        sizeOfHydro = len(self.time)-1
        # Volume of the RB filled with water
        self.filledVolume = np.zeros(sizeOfHydro)
        for elOutFlow in self.outFlow:
            self.outFlow[elOutFlow]["Net"] =  np.zeros(sizeOfHydro)
        
        self.filledVolume[0] = self.h_to_volume(self.hi)
        outFlowReservoir = np.zeros(sizeOfHydro)
        for i in range(1,sizeOfHydro):

            h = self.volume_to_h(self.filledVolume[i-1])
            qLim = self.qLim.compute(h,self.convert_time_global_to_local(self.time[i]))
            # Both of the following options are right, choose the correct one
            # diff = self.compute_Qout_from_V_mean(givenV, i, self.convert_index_global_to_local(i),30)
            diff = self.compute_Qout_from_V(givenV, i, self.convert_index_global_to_local(i))
            Qout = self.directFluxInRB[i]+max(self.inlets[i]-qLim,0.)-diff
            self.filledVolume[i] = givenV[self.convert_index_global_to_local(i)]

            outFlowReservoir[i-1] = Qout

            if self.filledVolume[i]>self.volume:
                outFlowReservoir[i-1] += (self.filledVolume[i]-self.volume)/((self.time[i]-self.time[i-1]))
                self.filledVolume[i] = self.volume

            self.outFlow = self.compute_final(outFlowReservoir[i-1],min(self.inlets[i-1],qLim),i-1)

        return self.outFlow



    def read_volume(self, fileName:str, tzDelta=datetime.timedelta(hours=0)):

        print("Reading the measurements volume file...")

        nbCl = 0
        with open(fileName, newline = '') as fileID:                                                                                          
            data_reader = csv.reader(fileID, delimiter=' ',skipinitialspace=True)
            list_data = []
            i=0
            for raw in data_reader:
                if i>3:
                    list_data.append(raw[0:nbCl])
                if i==2:
                    nbCl = int(raw[0])
                i += 1

        matrixData = np.array(list_data).astype("float")
        # Init of the outflow array
        timeInterval = self.dateEnd-self.dateBegin
        height = np.zeros(int(timeInterval.total_seconds()/self.deltaT))
        timeArray = np.zeros(int(timeInterval.total_seconds()/self.deltaT)+1)
        
        # From the measurements file, we will only read the desired data and save it in outflow
        prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), tzinfo=datetime.timezone.utc)
        prevDate -= tzDelta
        index = 0
        add1Hour = datetime.timedelta(hours=1)
        secondsInDay = 24*60*60

        # Verification
        if(datetime.datetime.timestamp(prevDate)>datetime.datetime.timestamp(self.dateBegin)):
            print("ERROR: the first hydro data element is posterior to dateBegin!")
            sys.exit()

        if(nbCl==5):
            # Caution : the index of the loop start at 24 because the timestamp function 
            # does not work until the 2/01/1970 at 03:00:00. => Je ne sais pas pourquoi ?!
            for i in range(25,len(matrixData)):
                # The hours are written in the file in [1,24] instead of [0,23]. Conversion below:
                if(int(matrixData[i][3])==24):
                    currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=23, tzinfo=datetime.timezone.utc) + add1Hour
                else:
                    currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), tzinfo=datetime.timezone.utc)
                currDate -= tzDelta
                if(int(matrixData[i-1][3])==24):
                    prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=23, tzinfo=datetime.timezone.utc) + add1Hour
                else:
                    prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), tzinfo=datetime.timezone.utc)
                prevDate -= tzDelta
                # Start at dateBegin and go to the element before dateEnd. Because the last date is needed for rain and evap in implicit simulations.
                if(datetime.datetime.timestamp(currDate)>=datetime.datetime.timestamp(self.dateBegin) and \
                datetime.datetime.timestamp(currDate)<datetime.datetime.timestamp(self.dateEnd)):
                    height[index] = matrixData[i][4]
                    diffDate = currDate - prevDate
                    diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                    timeArray[index] = datetime.datetime.timestamp(currDate)
                    index += 1
        elif(nbCl==7):
            for i in range(len(matrixData)):
                # The hours are written in the file in [1,24] instead of [0,23]. Conversion below:                    
                currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),tzinfo=datetime.timezone.utc)
                currDate -= tzDelta
                prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),tzinfo=datetime.timezone.utc)
                prevDate -= tzDelta
                # Start at dateBegin and go to the element before dateEnd. Because the last date is needed for rain and evap in implicit simulations.
                if(datetime.datetime.timestamp(currDate)>=datetime.datetime.timestamp(self.dateBegin) and \
                datetime.datetime.timestamp(currDate)<datetime.datetime.timestamp(self.dateEnd)):
                    if(matrixData[i][6]<0):
                        height[index] = 0.0
                    else:
                        height[index] = matrixData[i][6]
                    height[index] = matrixData[i][6]
                    diffDate = currDate - prevDate
                    diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                    timeArray[index] = datetime.datetime.timestamp(currDate)
                    index += 1
        # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
        diffDate = currDate - prevDate
        # Add the last element in the time matrix as its size is 1 element bigger than outlet
        timeArray[-1] = timeArray[-2] + diffTimeInSeconds
        if(self.deltaT!=diffDate.seconds):
            print("ERROR: The last timestep in hydro data does not coincide with the one expected!")
            sys.exit()
        # Save time array if it does not exist yet
        # Otherwise, check the consistency of the array with the time array of the object
        if(self.time==[]):
            self.time=timeArray
        elif(self.time.all()!=timeArray.all()):
            print("ERROR: the dates read are not consitent with the dates already recored in this subbasin!")
            sys.exit()

        volume = np.array([self.h_to_volume(i) for i in height])
    
        return timeArray, volume



    def compute_Qout_from_V(self, refVolume, indexSimul, indexData):

        # # To Complete !!!!
        if(indexData<3):
            vm1 = refVolume[indexData-1]
            vi = refVolume[indexData]
        else:            
            vm1 = (refVolume[indexData-3]+refVolume[indexData-2]+refVolume[indexData-1])/3
            vi = (refVolume[indexData-2]+refVolume[indexData-1]+refVolume[indexData])/3

        Qout = (vi-vm1) / (self.time[indexSimul]-self.time[indexSimul-1])
        # Qout = (refVolume[indexData] - refVolume[indexData-1]) / (self.time[indexSimul]-self.time[indexSimul-1])

        return Qout

    
    def compute_Qout_from_V_mean(self, refVolume, indexSimul, indexData, nbStep):

        # To Complete !!!!
        if(indexData<nbStep):
            vm1 = refVolume[indexData-1]
            vi = refVolume[indexData]
        else:            
            vm1 = (np.sum(refVolume[indexData-nbStep:indexData]))/nbStep
            vi = (np.sum(refVolume[indexData-nbStep+1:indexData+1]))/nbStep

        Qout = (vi-vm1) / (self.time[indexSimul]-self.time[indexSimul-1])
        # Qout = (refVolume[indexData] - refVolume[indexData-1]) / (self.time[indexSimul]-self.time[indexSimul-1])

        return Qout

    
    def construct_surfaceDrainedHydro(self):

        self.surfaceDrainedHydro = 0.0
        for element in self.directFluxObj:
            self.surfaceDrainedHydro += self.directFluxObj[element].surfaceDrainedHydro

        for element in self.intletsObj:
            self.surfaceDrainedHydro += self.intletsObj[element].surfaceDrainedHydro


    def unuse(self, mask=[]):

        self.alreadyUsed = False
        for element in self.intletsObj:
            self.intletsObj[element].unuse(mask=mask)
        
        for element in self.directFluxObj:
            self.directFluxObj[element].unuse(mask=mask)

    
    def activate(self, effSubs:list=[], effSubsSort:list=[], mask:list=[]):

        curSub = effSubs
        curSubSort = effSubsSort
        if self.alreadyUsed == False:
            self.alreadyUsed = True
            for element in self.intletsObj:
                curSub, curSubSort = self.intletsObj[element].activate(mask=mask, effSubs=curSub, effSubsSort=curSubSort)
            
            for element in self.directFluxObj:
                curSub, curSubSort = self.directFluxObj[element].activate(mask=mask, effSubs=curSub, effSubsSort=curSubSort)

        
        return curSub, curSubSort


    def reset_timeDelay(self, keepDelta=False, keepDeltaAll=False, upStreamTime=0.0):

        self.timeDelay = 0.0
        for element in self.intletsObj:
            self.intletsObj[element].reset_timeDelay(keepDelta=keepDelta, upStreamTime=upStreamTime)
        
        for element in self.directFluxObj:
            self.directFluxObj[element].reset_timeDelay(keepDelta=keepDelta, upStreamTime=upStreamTime)

        self.update_timeDelay()

    

    def find_timeDelayObj(self):

        timeDelay = 0.0 
        self.timeDelayObj = None

        if("time delay from module" in self.dictRB):
            nameModule = self.dictRB["time delay from module"]['value']
        else: 
            return timeDelay


        for element in self.intletsObj:
            upEl = self.intletsObj[element]
            if upEl.iD == nameModule:
                timeDelay = upEl.timeDelay
                self.timeDelayObj = upEl
                return timeDelay

        for element in self.directFluxObj:
            upEl = self.directFluxObj[element]
            if upEl.iD == nameModule:
                timeDelay = upEl.timeDelay
                self.timeDelayObj = upEl
                return timeDelay

        return timeDelay


    def update_timeDelay(self):

        self.timeDelay = self.timeDelayObj.timeDelay


    def add_timeDelay(self, deltaT=0.0, reset=False, resetAll=False):
        
        for element in self.intletsObj:
            self.intletsObj[element].add_timeDelay(deltaT, reset=resetAll, resetAll=resetAll)

        for element in self.directFluxObj:
            self.directFluxObj[element].add_timeDelay(deltaT, reset=resetAll, resetAll=resetAll)

        # Here we are sure all the upstream subbasins are updated -> timeDelay updated
        self.update_timeDelay()


    def get_inletsName(self):

        allInlets = []

        for element in self.intletsObj:
            allInlets.append(self.intletsObj[element].name)

        for element in self.directFluxObj:
            allInlets.append(self.directFluxObj[element].name)

        return allInlets