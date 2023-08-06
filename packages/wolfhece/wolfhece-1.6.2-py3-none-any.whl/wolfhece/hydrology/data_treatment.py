import sys                              # module to stop the program when an error is encountered
import numpy as np
import math
import datetime
from numpy.core.getlimits import _fr0
from numpy.core.numeric import False_

from ..PyTranslate import _
from numpy.ma.core import _DomainSafeDivide

## Function computing the cumulative volume of a given flow
# @var flow the flow to treat. Units: [m^3/s]
# @var dtData time step of the argument 'flow'. Units: [s]
# @var dtOut time step of the desired cumulative volume. It should be a multiple of 'dtData'. Units: [s]
# @var tData time array containing the timestamps of the data
# @var tRange optional array of datetime objects containing the range [tmin, tmax] in which the cumul sum will be carried out
# \undeline{Caution}: Take care to the units of dtData and dtOut according to the flow units. 
# E.g. Hyeto and Evap in [mm/h]                     => dtData in [h]
# \underline{But}: outflow and myHydro in [m^3/s]   => dtData in [sec] 
# Returns the cumulative volume. Units: [m^3]
# TO DO:    - ajouter interval de temps
#           - ajouter un argument 'unité'
def cumul_data(data, dtData, dtOut, tData=None, beginDate=None, tRange=None, noDataValue=None):
    # Check validity of the arguments
    if(dtOut%dtData!=0):
        print("ERROR: the time step of the desired output is not compatible with the data timestep!")
        sys.exit()
    else:
        factor = dtOut/dtData   # conversion factor from data timestep and cumul time step

    
    add_1_cell = 0
    if(tRange==None):
        # To detect the difference between a rain and an hydrograph data
        if(len(data)%int(factor)!=0):
            add_1_cell = 1

        cumul = np.zeros(int(len(data)/factor)+add_1_cell)
        iInit = 0
        iEnd = int(len(data)/factor)
    elif(tData!=None):
        # No distinction between rain and hydro needed here as the range is directly specified -> TO DISCUSS!!!
        tMin = datetime.datetime.timestamp(tRange[0])
        tMax = datetime.datetime.timestamp(tRange[1])
        if((tMax-tMin)%factor!=0):
            print("ERROR: the interval given does not coincide with the timestep of the desired output!")
            sys.exit()
        
        # We check whether the range is within data
        datesOk = False
        for i in range(len(data)):
            if(tMin==tData[i]):
                if((i+(tMax-tMin)/dtData)>len(data)-1):
                    print("ERROR: the upper bound of the desired range in out of data bounds!")
                    sys.exit()
                else:
                    datesOk = True
        if(datesOk==False):
            print("ERROR: lower bound of the range in out of the data bounds!")
            sys.exit()
    
    elif(beginDate!=None):
        tMin = tRange[0]
        tMax = tRange[1]
        iInit = index_from_date(beginDate, tMin, dtData, dtUnit="sec", roundType="ceil")
        iInit = math.ceil(iInit/factor)
        iEnd = index_from_date(beginDate, tMax, dtData, dtUnit="sec", roundType="floor")
        iEnd = math.floor(iEnd/factor)

        cumul = np.zeros(int((iEnd-iInit)))


    # Check whether there are holes in data.
    dataCorr = data.copy()
    if(noDataValue!=None):
        if(np.all(dataCorr>noDataValue)):
            holesInData = False
        else:
            holesInData = True
            isaved = -1
            for i in range(int((iInit)*factor), int(iEnd*factor)):
                if(dataCorr[i]<=noDataValue and isaved==-1):
                    isaved = i-1
                elif(isaved==-1):
                    continue
                elif(dataCorr[i]>noDataValue):
                    slope = (dataCorr[i]-dataCorr[isaved])/(i-isaved)
                    for j in range(isaved,i):
                        dataCorr[j] = dataCorr[isaved] + slope*(j-isaved)
                    isaved = -1
            if(isaved!=-1):
                lastIndex = math.floor(isaved/factor)-iInit
            else:
                lastIndex = len(cumul)

    else:
        holesInData = False
        lastIndex = len(cumul)

    

    cumul[0] = np.sum(dataCorr[iInit*int(factor):iInit*int(factor)+int(factor)])/factor*dtOut
    for i in range(iInit+1,iEnd):
        cumul[i-iInit] = cumul[i-iInit-1] + np.sum(dataCorr[i*int(factor): (i+1)*int(factor)])/factor*dtOut


    if(tRange==None):
        i = int(len(dataCorr)/factor)
        if(len(dataCorr)%int(factor)!=0):
            cumul[i] = cumul[int(len(dataCorr)/factor)-1] + dataCorr[i*int(factor)]/factor*dtOut

    if(holesInData):
        return cumul,lastIndex
    else:
        return cumul


## Function computing the cumulative volume of a given flow and for each season
# This function does not compute the volumes for incomplete seasons (i.e. at the beginning or at the end of the interval)
#  
def cumul_data_per_season(data, dtData, dtOut, tData):
    # Check the validity of the arguments
    if(dtOut%dtData!=0):
        print("ERROR: the time step of the desired output is not compatible with the data timestep!")
        sys.exit()
    else:
        factor = dtOut/dtData   # conversion factor from data timestep and cumul time step

    ## Definition of the ongoing year
    tmpDate = datetime.datetime.fromtimestamp(tData[0], tz=datetime.timezone.utc)
    myYear = tmpDate.year

    ## Definition of : 
    # - tOut array : time array of the output
    # - cumul list : list of cumul volume computed at each season
    tOut = [np.zeros(0), np.zeros(0), np.zeros(0), np.zeros(0)]
    cumul = [np.zeros(0), np.zeros(0), np.zeros(0), np.zeros(0)]




    ## Definition of the constants

    # @var mySeason Integer which is
    # =0, spring
    # =1, summer
    # =2, fall
    # =3, winter
    mySeason = 0

    # The dates for the beginning of each season
    dSeasons= []
    # Spring    -> [0]
    dSeasons.append(datetime.datetime(year=myYear, month=3, day=21, tzinfo=datetime.timezone.utc))
    # Summer    -> [1]  
    dSeasons.append(datetime.datetime(year=myYear, month=6, day=21, tzinfo=datetime.timezone.utc))
    # Fall      -> [2]
    dSeasons.append(datetime.datetime(year=myYear, month=9, day=21, tzinfo=datetime.timezone.utc))
    # Winter    -> [3]
    dSeasons.append(datetime.datetime(year=myYear, month=12, day=21, tzinfo=datetime.timezone.utc))

    # Timestamps for the beginning of each season
    tSeasons = np.zeros(len(dSeasons))
    for i in range(len(dSeasons)):
        tSeasons[i] = datetime.datetime.timestamp(dSeasons[i])


    ## Initialisation
     
    # Evaluation of the current season
    for i in range(len(tSeasons)):
        if(tData[0]<=tSeasons[i]):
            if(i<3):
                mySeason = i
                break
            else:
                mySeason = 0
                myYear += 1
                # Update of the seasons dates and times
                for j in range(dSeasons):
                    dSeasons[j] = dSeasons[j].replace(dSeasons[j].year+1)
                for j in range(len(tSeasons)):
                    tSeasons[j] = datetime.datetime.timestamp(dSeasons[j])
                break
    
    # Identification of the first element to treat
    firstIndex = int((tSeasons[mySeason]-tData[0])/dtData)
    if((tSeasons[mySeason]-tData[0])%dtData!=0):
        print("ERROR: this case was not considered in the code yet!")
        sys.exit()


    # Identification of the last element to treat
    lastSeason = 0
    lastTime = tData[-1]
    tmpDate = datetime.datetime.fromtimestamp(lastTime, tz=datetime.timezone.utc)
    lastYear = tmpDate.year

    tmpSeasons = []
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=3, day=21, tzinfo=datetime.timezone.utc)))
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=6, day=21, tzinfo=datetime.timezone.utc)))
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=9, day=21, tzinfo=datetime.timezone.utc)))
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=12, day=21, tzinfo=datetime.timezone.utc)))

    # The incomplete seasons are removed from the calculus
    for i in range(len(tmpSeasons)-1,0-1,-1):
        if(tData[-1]>=tmpSeasons[i]):
            if(i<0):
                lastSeason = tmpSeasons[i-1]
                break
            else:
                lastYear -= 1
                lastSeason = datetime.datetime.timestamp(datetime.datetime(year=lastYear-1, month=12, day=21, tzinfo=datetime.timezone.utc))
                break
        elif(i==0):
            lastYear -= 1
            lastSeason = datetime.datetime.timestamp(datetime.datetime(year=lastYear-1, month=12, day=21, tzinfo=datetime.timezone.utc))
            break                   


    ## Main loop 

    # ajouter l'init the tStart ou tEnd (ou les 2)
    while(tSeasons[mySeason]<=lastSeason):
        # Indentification of the interval of the seasons
        tStart = tSeasons[mySeason]
        if(mySeason<3):
            nextSeason = mySeason+1
            tEnd = tSeasons[nextSeason]
        else:
            # Update of the season's dates and times
            for j in range(len(dSeasons)):
                dSeasons[j] = dSeasons[j].replace(dSeasons[j].year+1)
            for j in range(len(tSeasons)):
                tSeasons[j] = datetime.datetime.timestamp(dSeasons[j])
            nextSeason = 0
            tEnd = tSeasons[nextSeason]

        # Identification of the number of time steps in this interval
        nbElementsIn = int((tEnd-tStart)/dtData)
        nbElementsOut = int((tEnd-tStart)/dtOut)
        tmpCumul = np.zeros(nbElementsOut)
        tmptOut = np.zeros(nbElementsOut)

        # Computation of the cumul volume for the current season
        if(len(cumul[mySeason])==0):
            tmpCumul[0] = np.sum(data[firstIndex:firstIndex+int(factor)])/factor*dtOut
        else:
            tmpCumul[0] = cumul[mySeason][-1] + (np.sum(data[firstIndex:firstIndex+int(factor)]))/factor*dtOut

        tmptOut[0] = tData[firstIndex]

        for i in range(1,nbElementsOut):
            tmpCumul[i] = tmpCumul[i-1] + np.sum(data[firstIndex+i*int(factor) : firstIndex+(i+1)*int(factor)])/factor*dtOut
            tmptOut[i] = tData[firstIndex+i*int(factor)]

        # Small test to check if all the elements were used in the data
        if((i+1)*int(factor) != nbElementsIn):
            print("ERROR: in the number of element In considered!!")
            sys.exit()
        firstIndex += (i+1)*int(factor)
        
        # Addition of the new cumul array to the previous one
        cumul[mySeason] = np.append(cumul[mySeason], tmpCumul)
        tOut[mySeason] = np.append(tOut[mySeason], tmptOut)

        mySeason = nextSeason


    return tOut, cumul




## Function decomposing data per each season and returns an array per season.
# This function does not decompose data for incomplete seasons (i.e. at the beginning or at the end of the interval)
#  
def decompose_data_per_season(data, dtData, dtOut, tData):

    ## Definition of the ongoing year
    tmpDate = datetime.datetime.fromtimestamp(tData[0], tz=datetime.timezone.utc)
    myYear = tmpDate.year

    ## Definition of : 
    # - tOut array : time array of the output
    # - newData list : list of data decomposed into each season
    tOut = [np.zeros(0), np.zeros(0), np.zeros(0), np.zeros(0)]
    newData = [np.zeros(0), np.zeros(0), np.zeros(0), np.zeros(0)]




    ## Definition of the constants

    # @var mySeason Integer which is
    # =0, spring
    # =1, summer
    # =2, fall
    # =3, winter
    mySeason = 0

    # The dates for the beginning of each season
    dSeasons= []
    # Spring    -> [0]
    dSeasons.append(datetime.datetime(year=myYear, month=3, day=21, tzinfo=datetime.timezone.utc))
    # Summer    -> [1]  
    dSeasons.append(datetime.datetime(year=myYear, month=6, day=21, tzinfo=datetime.timezone.utc))
    # Fall      -> [2]
    dSeasons.append(datetime.datetime(year=myYear, month=9, day=21, tzinfo=datetime.timezone.utc))
    # Winter    -> [3]
    dSeasons.append(datetime.datetime(year=myYear, month=12, day=21, tzinfo=datetime.timezone.utc))

    # Timestamps for the beginning of each season
    tSeasons = np.zeros(len(dSeasons))
    for i in range(len(dSeasons)):
        tSeasons[i] = datetime.datetime.timestamp(dSeasons[i])


    ## Initialisation
     
    # Evaluation of the current season
    for i in range(len(tSeasons)):
        if(tData[0]<=tSeasons[i]):
            if(i<3):
                mySeason = i
                break
            else:
                mySeason = 0
                myYear += 1
                # Update of the seasons dates and times
                for j in range(dSeasons):
                    dSeasons[j] = dSeasons[j].replace(dSeasons[j].year+1)
                for j in range(len(tSeasons)):
                    tSeasons[j] = datetime.datetime.timestamp(dSeasons[j])
                break
    
    # Identification of the first element to treat
    firstIndex = int((tSeasons[mySeason]-tData[0])/dtData)
    if((tSeasons[mySeason]-tData[0])%dtData!=0):
        print("ERROR: this case was not considered in the code yet!")
        sys.exit()


    # Identification of the last element to treat
    lastSeason = 0
    lastTime = tData[-1]
    tmpDate = datetime.datetime.fromtimestamp(lastTime, tz=datetime.timezone.utc)
    lastYear = tmpDate.year

    tmpSeasons = []
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=3, day=21, tzinfo=datetime.timezone.utc)))
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=6, day=21, tzinfo=datetime.timezone.utc)))
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=9, day=21, tzinfo=datetime.timezone.utc)))
    tmpSeasons.append(datetime.datetime.timestamp(datetime.datetime(year=lastYear, month=12, day=21, tzinfo=datetime.timezone.utc)))

    # The incomplete seasons are removed from the calculus
    for i in range(len(tmpSeasons)-1,0-1,-1):
        if(tData[-1]>=tmpSeasons[i]):
            if(i<0):
                lastSeason = tmpSeasons[i-1]
                break
            else:
                lastYear -= 1
                lastSeason = datetime.datetime.timestamp(datetime.datetime(year=lastYear-1, month=12, day=21, tzinfo=datetime.timezone.utc))
                break
        elif(i==0):
            lastYear -= 1
            lastSeason = datetime.datetime.timestamp(datetime.datetime(year=lastYear-1, month=12, day=21, tzinfo=datetime.timezone.utc))
            break                   


    ## Main loop 

    # ajouter l'init the tStart ou tEnd (ou les 2)
    while(tSeasons[mySeason]<=lastSeason):
        # Indentification of the interval of the seasons
        tStart = tSeasons[mySeason]
        if(mySeason<3):
            nextSeason = mySeason+1
            tEnd = tSeasons[nextSeason]
        else:
            # Update of the season's dates and times
            for j in range(len(dSeasons)):
                dSeasons[j] = dSeasons[j].replace(dSeasons[j].year+1)
            for j in range(len(tSeasons)):
                tSeasons[j] = datetime.datetime.timestamp(dSeasons[j])
            nextSeason = 0
            tEnd = tSeasons[nextSeason]

        # Identification of the number of time steps in this interval
        nbElements = int((tEnd-tStart)/dtData)
        tmpdata = np.zeros(nbElements)
        tmptOut = np.zeros(nbElements)

        # Computation of the cumul volume for the current season
        if(len(newData[mySeason])==0):
            tmpdata[0] = data[firstIndex]
        else:
            tmpdata[0] = data[firstIndex]

        tmptOut[0] = tData[firstIndex]

        for i in range(1,nbElements):
            tmpdata[i] = tmpdata[i-1] + data[firstIndex+i]
            tmptOut[i] = tData[firstIndex+i]

        # Small test to check if all the elements were used in the data
        if((i+1) != nbElements):
            print("ERROR: in the number of element In considered!!")
            sys.exit()
        firstIndex += (i+1)
        
        # Addition of the new cumul array to the previous one
        newData[mySeason] = np.append(newData[mySeason], tmpdata)
        tOut[mySeason] = np.append(tOut[mySeason], tmptOut)

        mySeason = nextSeason


    return tOut, newData





## cst = [m^3/s]
# dt = [sec]
# Attention si c'est: - une pluie -> ok
#                     - un débit  -> enlever une taille
def cumul_fromCst(cst, dateBegin, dateEnd, dt, isFlow=False):
    timeLength = dateEnd-dateBegin
    if(dt==3600):
        if(timeLength.total_seconds()%3600==0):
            mySize = int(timeLength.total_seconds()/3600)
        else:
            print("ERROR: the number of hours not an integer!")
            sys.exit()
    elif(timeLength.total_seconds()%3600==0):
        mySize = int(timeLength.total_seconds()/dt)
    
    if(isFlow==False):
        mySize +=1
    # else:
        # mySize +=1
    cumul = np.zeros(mySize)
    cumul[0] = cst
    for i in range(1,mySize):
        cumul[i] = cumul[i-1] + cst*dt

    return cumul



def evaluate_Nash(simul, tSimul, measures, tMeasures, dateBegin, dateEnd, mask=[]):
    '''
    Function evaluating the Nash-Suttcliff coeff 
    Caution: So far, if a measure is 0, it is not considered the N-S evaluation.
    '''
    # Nash–Sutcliffe model efficiency coefficient
    print("TO CORRECT -> Check 'Hello !'  !!!!!")

    # Definition of the time step
    # Test of the constant time step - for simulation
    dtS = tSimul[1]-tSimul[0]
    for i in range(2,len(measures)):
        tmp_dt = tSimul[i]-tSimul[i-1]
        # Hello ! A corriger!!!!!!!!!
        # if(tmp_dt!=dtS):
            # print("WARNING: the time step is not regular and constant in the simulation data !")
            # print("Two timestamps can be equal when there is time changeover.")
            # sys.exit()
    # Test of the constant time step - for measures
    dtM = tMeasures[1]-tMeasures[0]
    for i in range(2,len(measures)):
        tmp_dt = tSimul[i]-tSimul[i-1]
        # if(tmp_dt!=dtM):
        #     print("WARNING: the time step is not regular and constant in the measures!")
        #     print("Two timestamps can be equal when there is time changeover.")
            # sys.exit()

    
    # Definition of the factor between both time steps
    if(dtM%dtS!=0):
        print("ERROR: the time step of the desired output is not compatible with the data timestep!")
        sys.exit()
    else:
        factor = dtM/dtS   # conversion factor from data timestep and cumul time step


    # Definition of the first elements
    ti = datetime.datetime.timestamp(dateBegin)
    tend = datetime.datetime.timestamp(dateEnd)
    # - simulation:
    first_el_simul = -9999
    last_el_simul = -9999
    for i in range(len(tSimul)):
        if(tSimul[i]==ti):
            first_el_simul = i
        if(tSimul[i]==tend):
            last_el_simul = i
            break
    if(first_el_simul==-9999 or last_el_simul==-9999):
        print("ERROR: the simulation data are out of range!")
        sys.exit()
    nb_el_simul = last_el_simul - first_el_simul
    # - measures:
    first_el_measures = -9999
    last_el_measures = -9999
    for i in range(len(tSimul)):
        if(tMeasures[i]==ti):
            first_el_measures = i
        if(tMeasures[i]==tend):
            last_el_measures = i
            break
    if(first_el_measures==-9999 or last_el_measures==-9999):
        print("ERROR: the simulation data are out of range!")
        sys.exit
    nb_el_measures = last_el_measures - first_el_measures

    # Verification of the proportionality between simulations and measures
    if(nb_el_simul%nb_el_measures!=0):
        print("ERROR: proportionality between simulations and measures!")
        sys.exit()


    sumNum = 0.0
    sumDen = 0.0
    meanMeasures = 0.0
    if mask==[]:
        # meanMeasures = np.mean(measures[first_el_measures:last_el_measures+1])
        counter = 0
        mask = [False for i in range(nb_el_measures)]
        for i in range(nb_el_measures):
            if(measures[i]!=0.0):
                meanMeasures += measures[i]
                mask[i]= True
                counter += 1
        meanMeasures = meanMeasures/counter

        for i in range(nb_el_measures):
            if(mask[i]==True):
                sumNum += (simul[first_el_simul+i*int(factor)]-measures[first_el_measures+i])**2.0
                sumDen += (measures[first_el_measures+i]-meanMeasures)**2.0
    else:
        counter = 0
        for i in range(nb_el_measures):
            if(mask[first_el_simul+i*int(factor) and measures[first_el_measures+i]!=0]):
                meanMeasures += measures[first_el_measures+i]
                counter += 1
        meanMeasures = meanMeasures/counter

        for i in range(nb_el_measures):
            if(mask[first_el_simul+i*int(factor)]):
                sumNum += (simul[first_el_simul+i*int(factor)]-measures[first_el_measures+i])**2.0
                sumDen += (measures[first_el_measures+i]-meanMeasures)**2.0



    NSE = 1.0 - (sumNum/sumDen)

    # sumNum = 0.0
    # sumDen = 0.0
    # meanMeasures = np.mean(measures)
    # for i in range(len(measures)):
    #     sumNum += (outflow[(first_el)*4+4*i]-measures[i])**2.0
    #     sumDen += (measures[i]-meanMeasures)**2.0


    # NSE = 1.0 - (sumNum/sumDen)

    return NSE



def evaluate_logNash(simul, tSimul, measures, tMeasures, dateBegin, dateEnd):
    # Nash–Sutcliffe model efficiency coefficient
    print("TO CORRECT -> Check 'Hello !'  !!!!!")

    # Definition of the time step
    # Test of the constant time step - for simulation
    dtS = tSimul[1]-tSimul[0]
    for i in range(2,len(measures)):
        tmp_dt = tSimul[i]-tSimul[i-1]
        # Hello ! A corriger!!!!!!!!!
        # if(tmp_dt!=dtS):
            # print("WARNING: the time step is not regular and constant in the simulation data !")
            # print("Two timestamps can be equal when there is time changeover.")
            # sys.exit()
    # Test of the constant time step - for measures
    dtM = tMeasures[1]-tMeasures[0]
    for i in range(2,len(measures)):
        tmp_dt = tSimul[i]-tSimul[i-1]
        # if(tmp_dt!=dtM):
        #     print("WARNING: the time step is not regular and constant in the measures!")
        #     print("Two timestamps can be equal when there is time changeover.")
            # sys.exit()

    
    # Definition of the factor between both time steps
    if(dtM%dtS!=0):
        print("ERROR: the time step of the desired output is not compatible with the data timestep!")
        sys.exit()
    else:
        factor = dtM/dtS   # conversion factor from data timestep and cumul time step


    # Definition of the first elements
    ti = datetime.datetime.timestamp(dateBegin)
    tend = datetime.datetime.timestamp(dateEnd)
    # - simulation:
    first_el_simul = -9999
    last_el_simul = -9999
    for i in range(len(tSimul)):
        if(tSimul[i]==ti):
            first_el_simul = i
        if(tSimul[i]==tend):
            last_el_simul = i
            break
    if(first_el_simul==-9999 or last_el_simul==-9999):
        print("ERROR: the simulation data are out of range!")
        sys.exit()
    nb_el_simul = last_el_simul - first_el_simul
    # - measures:
    first_el_measures = -9999
    last_el_measures = -9999
    for i in range(len(tSimul)):
        if(tMeasures[i]==ti):
            first_el_measures = i
        if(tMeasures[i]==tend):
            last_el_measures = i
            break
    if(first_el_measures==-9999 or last_el_measures==-9999):
        print("ERROR: the simulation data are out of range!")
        sys.exit
    nb_el_measures = last_el_measures - first_el_measures

    # Verification of the proportionality between simulations and measures
    if(nb_el_simul%nb_el_measures!=0):
        print("ERROR: proportionality between simulations and measures!")
        sys.exit()


    sumNum = 0.0
    sumDen = 0.0
    meanMeasures = np.mean(measures[first_el_measures:last_el_measures+1])
    for i in range(nb_el_measures):
        sumNum += (np.log(simul[first_el_simul+i*int(factor)])-np.log(measures[first_el_measures+i]))**2.0
        sumDen += (np.log(measures[first_el_measures+i])-np.log(meanMeasures))**2.0


    logNSE = 1.0 - (sumNum/sumDen)

    return logNSE



## Function to convert rain data from rain .dat file into another data matrix with a new timestep
# @var data Matrix containing all data in a rain file. Units: [day]-[month]-[year]-[hour]-[min]-[sec]-[mm/h]
def convert_inother_timestep(data, dtIn, dtOut):
    '''
    data
    Check script Test_convert_dt_data for more information
    Function to correct!!! Only valid for rain data in [mm/h] with dtIn=1h -> dtOut=1day
    '''

    if(dtIn%dtOut==0):
        # dtIn is a multiple of dtOut
        print("This case was not considered yet. Please complete it!")
        sys.exit()

        return dataOut

    elif(dtOut%dtIn==0):
        # dtOut is a multiple of dtIn
        factor = int(dtOut/dtIn)
        dataOut = np.zeros((len(data)*factor,7))
        
        for i in range(len(data)):
            for j in range(factor):
                dataOut[i*factor+j][:] = data[i][:]
                dataOut[i*factor+j][3] = j

        return dataOut
    else:
        print("This case was not considered yet. Please complete it!")
        sys.exit()



## Function to convert data with a smaller timestep into data with a greater timestep
# @var data vector of data to convert
# @var dtIn time step of the data
# @var dtOut time step of the data to return
# @var method string containing the method to use to aggregate the data
def aggregate(data, dtIn, dtOut, method="mean"):

    if(dtOut%dtIn!=0):
        print("ERROR: the data time step is not a multiple of the desired timestep")
        sys.exit()
    

    factor = int(dtOut/dtIn)
    nbIn  = len(data)
    nbOut = int(nbIn/factor)
    dataOut = np.zeros(len(data)/factor)
    
    if(method=="mean"):
        for i in range(nbOut):
            for j in range(factor):
                dataOut[i] += data[i*factor+j]/factor

        return dataOut

    
    elif(method=="sum"):
        print("ERROR: Not implemented yet!")
        return dataOut



def index_from_date(beginDate, currentDate, dt, dtUnit="sec", roundType="nearest"):

    deltaDate = currentDate - beginDate
    deltaSec = deltaDate.seconds
    deltaDay = deltaDate.days
    if(dtUnit=="sec" or dtUnit=="SEC"):
        delta = deltaSec + deltaDay*3600.0*24.0
    elif(dtUnit=="hour" or dtUnit=="HOUR"):
        delta = deltaSec/60 + deltaDay*24
    elif(dtUnit=="days" or dtUnit=="DAYS"):
        delta = deltaSec/(60.0*3600.0) + deltaDay

    if(roundType=="nearest"):
        myIndex = int(round(delta/dt))
    elif(roundType=="floor"):
        myIndex = math.floor(delta/dt)
    elif(roundType=="ceil"):
        myIndex = math.ceil(delta/dt)

    return myIndex
    



def Horton_function(u, uMax, infilParams):

    f0 = infilParams[0]
    fc = infilParams[1]
    k = infilParams[2]

    infil = fc + (f0-fc)*np.exp(-k*u/uMax)

    return infil