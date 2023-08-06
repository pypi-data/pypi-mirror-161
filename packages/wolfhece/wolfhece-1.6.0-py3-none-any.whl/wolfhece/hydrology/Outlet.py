from os import times,path
import sys
from textwrap import dedent
import numpy as np
from scipy.interpolate import interp1d
import csv
import datetime                         # module which contains objects treating dates

from ..PyTranslate import _

class Outlet:
    
    def __init__(self, _retentionBasinDict):
        print("Run Outlet")
        self.myType = ''
        self.myRbDict = _retentionBasinDict
        self.nbFlows = 0
        self.flows = []
        self.times = []
        
        self.myType = self.myRbDict['type']['value']
        self.myRef = None
        
        try:
            fileRef = self.myRbDict["Reference fileName"]['value']
        except:
            fileRef = ""
        try:
            tz = float(self.myRbDict["Time zone"]["value"])
        except:
            tz = 0.0

        if(fileRef!=""):
            self.myRef = self.read_ref(fileRef, tz=tz)


        if("nb flows" in self.myRbDict): 
            self.nbFlows = int(self.myRbDict["nb flows"]["value"])

            for i in range(1,self.nbFlows+1):
                self.flows.append(float(self.myRbDict['flow '+str(i)]['value']))
                if(i==1):
                    self.times.append(-1.0)
                else:
                    tmpDate = datetime.datetime.strptime(self.myRbDict['time '+str(i)]['value'], "%d-%m-%Y %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
                    tmpTime = datetime.datetime.timestamp(tmpDate)
                    self.times.append(tmpTime)


    def compute(self, h, t=-1.0):
        if(self.myType == 'HighwayRB'):
            q = self.compute_HighwayRB(h)
        elif(self.myType == 'RobiernuRB'):
            q = self.compute_RobiernuRB(h)
        elif(self.myType == 'OrbaisRB' or self.myType == "HelleRB"):
            if(self.nbFlows>0):
                q = self.compute_multistep(h,t)
            else:
                q = self.compute_OrbaisRB(h)
        # elif(self.myType == "HelleRB"):
        #     q = self.compute_HelleRB(h)
        elif(self.myType == "ForcedDam"):
            q = self.compute_forcedDam(t)
        return q


    def compute_HighwayRB(self, h):
        "This function compute the "
        q = 0.0
        h0 = float(self.myRbDict['stagnant height']['value'])
        h1 = float(self.myRbDict['height 1']['value'])
        h2 = float(self.myRbDict['height 2']['value'])
        q1 = float(self.myRbDict['flow 1']['value'])
        q2 = float(self.myRbDict['flow 2']['value'])

        if(h<=h1):
            q = q1
        else:
            q = q2
        return q        

    def compute_RobiernuRB(self, h):
        q = float(self.myRbDict['flow 1']['value'])
        return q

    def compute_OrbaisRB(self, h):
        q = float(self.myRbDict['flow 1']['value'])
        return q


    # def compute_HelleRB(self,h):
    #     qRmoved = float(self.myRbDict['flow 1']['value'])
    #     q = 0.0
    #     return q

    def compute_forcedDam(self, time):
        if(time<min(self.myRef.x) or time>max(self.myRef.x)):
            q=0
        else:
            q = self.myRef(time)

        return q


    def compute_multistep(self, h, time):
        
        q = self.flows[-1]

        for i in range(self.nbFlows-1):
            if(time<self.times[i+1]):
                q = self.flows[i]
                break
        
        return q
        




    def read_ref(self, fileName, typeOfInterpolation='linear', tz=0):
        '''
        tz represents the time zone "GMT+"tz
        '''
        if not path.exists(fileName):
            return
        
        if(type(fileName)!=str):
            print("ERROR: Expecting only 1 file name for measurements!")
            sys.exit()
        with open(fileName, newline = '') as fileID:                                                                                          
            data_reader = csv.reader(fileID, delimiter=' ',skipinitialspace=True)
            list_data = []
            i=0
            for raw in data_reader:
                if i>3:
                    list_data.append(raw)
                if i==2:
                    nbCl = int(raw[0])
                i += 1 
        matrixData = np.array(list_data).astype("float")
        # Init of the outflow array
        timeInterval = len(matrixData)
        outFlow = np.zeros(timeInterval)
        timeArray = np.zeros(timeInterval)
        
        # From the measurements file, we will only read the desired data and save it in outflow
        prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), tzinfo=datetime.timezone.utc)
        index = 0
        add1Hour = datetime.timedelta(hours=1)
        secondsInDay = 24*60*60 

        if(nbCl==5):
            # Caution : the index of the loop start at 24 because the timestamp function 
            # does not work until the 2/01/1970 at 03:00:00. => Je ne sais pas pourquoi ?!
            for i in range(25,len(matrixData)):
                # The hours are written in the file in [1,24] instead of [0,23]. Conversion below:
                if(int(matrixData[i][3])==24):
                    currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=23, tzinfo=datetime.timezone.utc) + add1Hour
                else:
                    currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), tzinfo=datetime.timezone.utc)
                if(int(matrixData[i-1][3])==24):
                    prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=23, tzinfo=datetime.timezone.utc) + add1Hour
                else:
                    prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), tzinfo=datetime.timezone.utc)
                # Start at dateBegin and go to the element before dateEnd. Because the last date is needed for rain and evap in implicit simulations.
                if(datetime.datetime.timestamp(currDate)>=datetime.datetime.timestamp(self.dateBegin) and \
                datetime.datetime.timestamp(currDate)<datetime.datetime.timestamp(self.dateEnd)):
                    outFlow[index] = matrixData[i][4]
                    diffDate = currDate - prevDate
                    diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                    timeArray[index] = datetime.datetime.timestamp(currDate)
                    # timeArray[index] = timeArray[index-1] + diffTimeInSeconds
                    index += 1
        elif(nbCl==7):
            for i in range(len(matrixData)):
                # The hours are written in the file in [1,24] instead of [0,23]. Conversion below:                    
                currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),tzinfo=datetime.timezone.utc)
                prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),tzinfo=datetime.timezone.utc)
                # Start at dateBegin and go to the element before dateEnd. Because the last date is needed for rain and evap in implicit simulations.
                if(matrixData[i][6]<0):
                    outFlow[index] = 0.0
                else:
                    outFlow[index] = matrixData[i][6]
                outFlow[index] = matrixData[i][6]
                diffDate = currDate - prevDate
                diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                timeArray[index] = datetime.datetime.timestamp(currDate)
                # timeArray[index] = timeArray[index-1] + diffTimeInSeconds
                index += 1
        # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
        diffDate = currDate - prevDate
        # Add the last element in the time matrix as its size is 1 element bigger than outlet
        timeArray[-1] = timeArray[-2] + diffTimeInSeconds
        
        timeArray -= tz*3600

        interpol = interp1d(timeArray,outFlow,kind=typeOfInterpolation)

        return interpol
