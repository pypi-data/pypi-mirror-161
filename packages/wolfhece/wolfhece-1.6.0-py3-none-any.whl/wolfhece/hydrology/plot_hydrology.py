import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange, MicrosecondLocator, num2date
from matplotlib import gridspec
import csv
import math
import datetime
import sys
from numpy.core.arrayprint import set_string_function

from numpy.core.defchararray import index

from ..PyTranslate import _

## This function plots a graph with
# @var nbElements The number of plots asked or the number of y elements to compare with
# @var writeDir The directory where the figure will be saved
# @var x The element on the x axis. The elements on the y axis will be compared with them.
# @var y The elements on the y axis will be compared with them. It is composed of nbElements number of columns.
# @var titles The title to write in the legend
# @var beginDate datetime object that indicates the time of the first element to plot.
# @var endDate datetime object that indicates the time of the last element to plot.
# @var dt time steps of the data to plot [sec]
# @var dataRange list of datetime objects representing the first time in the data and the last one
def compare_plot(nbElements, writeDir, x, y, x_title, y_titles, graph_title='', y_title='Flow in the legend', \
                beginDate=None, endDate=None, dt=None, dateRange=[], markersize=5, ax=None):
    # Verification of the coherence bewteen the arguments
    if(nbElements!=np.shape(y)[1] or nbElements!=len(y_titles)):
        print("ERROR: 'nbElements' does not coincide with the number of rows of 'y' and 'titles'")
        sys.exit()
    if(len(x)!=len(y)):
        print("ERROR: the length of 'x' and 'y' are different!")


    if beginDate!=None and endDate!=None and dt!=None and dateRange!=[]:
        if dateRange[0]>beginDate or dateRange[1]<endDate:
            print("ERROR: the first or last date to plot must be within the range of available data!")
            sys.exit()
        index1 = math.ceil((datetime.datetime.timestamp(beginDate)-datetime.datetime.timestamp(dateRange[0]))/dt)
        index2 = len(x)-math.ceil((datetime.datetime.timestamp(dateRange[1])-datetime.datetime.timestamp(endDate))/dt)
        x_plot = []
        y_plot = []
        x_plot = x[index1:index2]      
        y_plot = y[index1:index2,:]
    else : 
        x_plot = x     
        y_plot = y
      
    
    # Plot ot the graph and loop on all the elements to plot
    if(ax==None):
        plt.figure()

        plt.grid()
        plt.xlabel(x_title)
        plt.ylabel(y_title)
        
        for i in range(nbElements):
            plt.plot(x_plot,y_plot[:,i],'*',markersize=markersize,label=y_titles[i])
        plt.plot(x_plot,x_plot, label='Bissectrice', color='k')
        plt.title(graph_title)
        plt.legend()

        plt.savefig(writeDir)

    else:

        # ax = plt.subplot(gs)
        ax.set_xlabel(x_title)
        ax.set_ylabel(y_title)
        ax.grid()
        for i in range(nbElements):
            ax.plot(x_plot,y_plot[:,i],'*',markersize=markersize,label=y_titles[i])
        ax.plot(x_plot,x_plot, label='Bissectrice', color='k')
        ax.set_title(graph_title)




## This procedure plots the complete information about the hydrographs 
# @var nbElements The number of plots asked or the number of y elements to compare with
# @var y The elements on the y axis will be compared with them. It is composed of "nbElements" number of columns.
# @var x_title The title to write on the x axis
# @var y_title The title to write on the y axis
# @var time array composed of timetamps of the different times
# @var beginDate datetime object of the first date
# @var endDate datetime object of the last date
# @var dt time step in [sec]
# @var graph_title list of string containing the legend labels of each 'y'
# @var range array of datetime objects
# @var myColors list of string containing the colors desired. If the string is '' then we let the automatic choice.
# @var typeOfTraits list of string defining the type of trait desired in the plot. (e.g. '-','--', etc)
# @var upperPlot add a small additional plot just above the hydro (e.g. temperature, evapotranspiration)
# @var nbAddPlot number of additional graph to give (the hydro and hyeto not included)
# @var z array of additional data to plot. Its size is given by 'nbAddPlot'
# @var y_labelAddPlot the labels to write on the y-axis of each additional graph
# @var factor_RH factor between the hydro and the hyeto graph disposition
# @var allSurfaces list containing all the surfaces in [km²] to consider for outflow conversion in mm/h
# TO DO: REVOIR la facon de calculer "factor_RH"!!!!
# If y is an array : each element is by column [][here]
# elif y is a list : each element is located [here][]
# TO DO : Maybe change this rationale for y -> Too complicated
def plot_hydro(nbElements, y, rain=[], x_title="Dates", y_titles="Débits [m³/s]", time=None, beginDate=None, endDate=None, dt=None, \
                graph_title=None, y_labels=None, rangeData = [], myColors=None, typeOfTraits=None, \
                measures=[], beginDateMeasure=None, endDateMeasure=None, dtMeasure=None, surfaceMeasure=-1.0, addMeasfInTab=False, \
                upperPlot=False, nbAddPlot=1, z=[], y_labelAddPlot=[], factor_RH=1.5, y_rain_range=[], y_data_range=[], figSize = [10.4,6.25],\
                writeFile = '', deltaMajorTicks=-1, deltaMinorTicks=-1, \
                y_envelop=[], envelopID=0, textInGraph={}, addTable=False, allSurfaces=[], figure=None):

    summaryTab = [] # @var summaryTab will be composed of the following charcteristics for each element: [Qpeak(0), tpeak(1), Qcumul(2), Raincumul(3), Coeff ruissellement moyen(4)]. If no rain provided only the 3 first elements are considered

    # Check the input data
    if(nbElements==1):
        if(len(np.shape(y))!=1):
            # if(np.shape(y)[0]!=1):
            if(np.shape(y)[1]!=1):    
                print("ERROR: the number of element and the dimension of 'y' does not coincide")
                sys.exit()
    elif(type(y)==np.ndarray):
        if(nbElements!=np.shape(y)[1]):
            print("ERROR: the number of element and the dimension of 'y' does not coincide")
            sys.exit()
    elif(type(y)==list):
        if(nbElements!=np.shape(y)[0]):
            print("ERROR: the number of element and the dimension of 'y' does not coincide")
            sys.exit()

    if(time!=None):
        # Particular case if the user give the time in time stamps and the dates: it will check the validiy of the arguments
        if(beginDate!=None and endDate!=None and dt!=None):
            tmpBeginDate = beginDate
            tmpEndDate = endDate
            tmpDt = dt
        beginDate = datetime.datetime.fromtimestamp(time[0], tz=datetime.timezone.utc)
        endDate = datetime.datetime.fromtimestamp(time[-1], tz=datetime.timezone.utc)
        dt = time[1]-time[0]
        time_delta = datetime.timedelta(seconds=dt)
        # Check the regularity of the time steps
        for i in range(1,len(time)):
            if(time[i+1]-time[i] != dt):
                print("ERROR: this procedure cannot take into account irregular time steps")
                sys.exit()
                break
                
        if(beginDate!=None and endDate!=None and dt!=None):
            if(tmpBeginDate!=beginDate or tmpEndDate!=endDate or tmpDt!=dt):
                print("ERROR: the data does not coincide!")
                sys.exit()

    elif(beginDate!=None and endDate!=None and dt!=None):
        if(np.shape(dt)==()):
            time_delta = datetime.timedelta(seconds=dt)
        else:
            time_delta = []
            for i in range(nbElements):
                time_delta.append(datetime.timedelta(seconds=dt[i]))
        

    else:
        print("ERROR: This case is not considered or it lacks data!")
        print("Reminder: this procedure need at least the time array or the [beginDate,endDate,dt] information!")
        sys.exit()
    
    # if(y_labels!=None):
    #     if(len(y_labels)!=nbElements):
    #         print("ERROR: this relation is not verified 'ylabels=nbElements'!")
    #         sys.exit()

    if(rangeData==[]):
        if(np.shape(time_delta)==()):
            rangeData = [beginDate,endDate]
        else:
            rangeData = [beginDate[0],endDate[0]]
    else:
        print("TO DO: chek if the dates are valid.")
        

    if(myColors==None):
        myColors=[]
        for i in range(nbElements):
            myColors.append('')
    
    if(typeOfTraits==None):
        typeOfTraits = []
        for i in range(nbElements):
            typeOfTraits.append('-')


    if(measures!=[]):
        time_delta_measure = datetime.timedelta(seconds=dtMeasure)

    if(factor_RH!=1.5 and y_rain_range!=[]):
        print("WARNING: factor_RH and y_rain_range cannot be given at the same time! Only factor_RH will be taken into account.")
        y_rain_range=[]

    if(factor_RH!=1.5 and y_data_range!=[]):
        print("WARNING: factor_RH and y_data_range cannot be given at the same time! Only factor_RH will be taken into account.")
        y_data_range=[]

    # Command to be sure the title does not overlap the graph
    if(nbAddPlot==0):
        nbAddPlot=1
        

    # ==============
    # ==============

    if(np.shape(time_delta)==()):
        x_date = drange(beginDate, endDate+time_delta, time_delta)
    else:
        x_date = []
        for i in range(nbElements):
            x_date.append(drange(beginDate[i], endDate[i]+time_delta[i], time_delta[i]))

    
    if(measures!=[]):
        x_date_measure = drange(beginDateMeasure, endDateMeasure+time_delta_measure, time_delta_measure)
    
    if figure== None:
        fig = plt.figure(figsize=(figSize[0],figSize[1]))
    else:
        fig = figure
        fig.set_size_inches(figSize[0], figSize[1])

    fig.suptitle(graph_title)
    if(addTable):
        tableElement = 3
    else:
        tableElement = 0
    gs = gridspec.GridSpec(nbAddPlot*3+5+tableElement, 5)  # Subdivision of the main window in a grid of several subplots


    # ==============
    # --- Main plot --- :
    # a) Hydro:
    ax1 = fig.add_subplot(gs[:5,:])
    ax1.set_xlabel(x_title)
    ax1.set_ylabel(y_titles, color='k') #Color express in %RGB: (1,1,1)

    # ax1.set_ylabel('Coefficient de ruissellement [-]',color='k') #Color express in %RGB: (1,1,1)
    max_= 0
    if(y_labels!=None):
        title = y_labels



    # Plot hydro
    if(nbElements==1):
        if(len(np.shape(y))==1):
            y1 = y
            xdatePlot = x_date
            xdatePlotGen = x_date
            time_deltaGen = time_delta
            dt_Gen = dt
            dt_Plot = dt
        elif(type(y)==list):
            y1 = y[0]
            xdatePlot = x_date[0]
            xdatePlotGen = x_date[0]
            time_deltaGen = time_delta[0]
            dt_Gen = dt[0]
            dt_Plot = dt[0]
        else:
            y1 = y[:,0]
            # Could contain time data of the envelopp
            if(y_envelop!=[]):
                xdatePlot = x_date[envelopID]
                xdatePlotGen = x_date[0]
                time_deltaGen = time_delta[0]
                dt_Gen = dt[0]
                dt_Plot = dt[0]
            else:
                xdatePlot = x_date
                xdatePlotGen = x_date
                time_deltaGen = time_delta
                dt_Gen = dt
                dt_Plot = dt
        
        # complete summary table
        summaryTab.append([])
        # summaryTab[0].append("%.3f"%(y1.max()))
        summaryTab[0].append(str(int(round(y1.max()))))
        indexMax = np.argmax(y1)
        timeMax = num2date(xdatePlot[indexMax])
        # summaryTab[0].append(timeMax.strftime("%m/%d/%Y, %H:%M:%S"))
        summaryTab[0].append(timeMax.strftime("%m/%d/%Y, %H:%M"))
        if(allSurfaces!=[]):
            summaryTab[0].append(np.sum(y1)*dt_Plot)


        if(y1.max()>max_):
            max_ = y1.max()
        if(myColors[0]==''):
            ax1.plot_date(xdatePlot,y1,typeOfTraits[0],label=title[0])
        else:
            ax1.plot_date(xdatePlot,y1,typeOfTraits[0],label=title[0],color=myColors[0])    

        # ax1.plot_date(xdatePlot,y1, typeOfTraits[0],label=title[0])
        i = 0
    else:
        for i in range(nbElements):
            if(np.shape(x_date[0])==()):
                xdatePlot = x_date
                xdatePlotGen = x_date
                time_deltaGen = time_delta
                time_deltaPlot = time_delta
                dt_Gen = dt
                dt_Plot = dt
            else:
                xdatePlot = x_date[i]
                xdatePlotGen = x_date[0]
                if(np.shape(time_delta)==()):
                    time_deltaGen = time_delta
                    time_deltaPlot = time_delta
                    dt_Gen = dt
                    dt_Plot = dt
                else:
                    time_deltaGen = time_delta[0]
                    time_deltaPlot = time_delta[i]
                    dt_Gen = dt[0]
                    dt_Plot = dt[i]
            if(type(y)==list):
                y1 = y[i]
            elif(type(y)==np.ndarray):
                y1 = y[:,i]

            # complete summary table
            summaryTab.append([])
            # summaryTab[i].append("%.3f"%(y1.max()))
            summaryTab[i].append(str(int(round((y1.max())))))
            indexMax = np.argmax(y1)
            timeMax = num2date(xdatePlot[indexMax])
            # summaryTab[i].append(timeMax.strftime("%m/%d/%Y, %H:%M:%S"))
            summaryTab[i].append(timeMax.strftime("%m/%d/%Y, %H:%M"))
            if(allSurfaces!=[]):
                summaryTab[i].append(np.sum(y1)*dt_Plot)

            if(y1.max()>max_):
                max_ = y1.max()
            if(myColors[i]==''):
                if(len(xdatePlot)==len(y1)):
                    ax1.plot_date(xdatePlot,y1,typeOfTraits[i],label=title[i])
                elif(len(xdatePlot)-1==len(y1)):
                    print("ERROR: dimension of dates 1 elements greater than data! This could be a problem induced by drange() ... To investigate...")
                    toContinue = input("Do you still want to continue nonetheless? Y-[Yes] N-[No]: ")
                    if(toContinue=="Y"):
                        ax1.plot_date(xdatePlot[:-1],y1,typeOfTraits[i],label=title[i])
                    else:
                        sys.exit()
            else:
                if(len(xdatePlot)==len(y1)):
                    ax1.plot_date(xdatePlot,y1,typeOfTraits[i],label=title[i],color=myColors[i])
                elif(len(xdatePlot)-1==len(y1)):
                    print("ERROR: dimension of dates 1 elements greater than data! This could be a problem induced by drange() ... To investigate...")
                    toContinue = input("Do you still want to continue nonetheless? Y-[Yes] N-[No]: ")
                    if(toContinue):
                        ax1.plot_date(xdatePlot[:-1],y1,typeOfTraits[i],label=title[i],color=myColors[i])
                    else:
                        sys.exit()

    
    # Plot envelop
    if(y_envelop!=[]):
        if(nbElements==1):
            if(len(np.shape(y))==1):
                y1 = y
                xdatePlot = x_date
                xdatePlotGen = x_date
            elif(type(y)==list):
                y1 = y[0]
                xdatePlot = x_date[0]
            else:
                y1 = y[:,0]
                xdatePlot = x_date[envelopID]

            if(y_envelop[1].max()>max_):
                max_ = y_envelop[1].max()

            ax1.fill_between(xdatePlotGen, y_envelop[1], y_envelop[0], color='c', alpha=0.4)   

            # ax1.plot_date(xdatePlot,y1, typeOfTraits[0],label=title[0])
            i = 0
        else:
            for i in range(nbElements):
                if(np.shape(x_date[0])==()):
                    xdatePlot = x_date
                else:
                    xdatePlot = x_date[envelopID]

                if(y_envelop[1].max()>max_):
                    max_ = y_envelop[1].max()

                ax1.fill_between(xdatePlotGen, y_envelop[0], y_envelop[1], color='c', alpha=0.5)   




    # Plot measures
    if(measures!=[]):
        y1 = measures
        if(y1.max()>max_):
            max_ = y1.max()
        if(myColors[nbElements]==''):
            ax1.plot_date(x_date_measure,y1, typeOfTraits[-1],label=title[nbElements])
        else:
            ax1.plot_date(x_date_measure,y1, typeOfTraits[-1],label=title[nbElements],color=myColors[nbElements])

        if(addMeasfInTab):
            summaryTab.append([])
            i = len(summaryTab)-1
            summaryTab[i].append(str(int(round((y1.max())))))
            indexMax = np.argmax(y1)
            timeMax = num2date(x_date_measure[indexMax])
            # summaryTab[i].append(timeMax.strftime("%m/%d/%Y, %H:%M:%S"))
            summaryTab[i].append(timeMax.strftime("%m/%d/%Y, %H:%M"))
            if(allSurfaces!=[]):
                summaryTab[i].append(np.sum(y1)*dtMeasure)

    # Set the axis parameters
    if(y_data_range==[]):
        ax1.set_ylim(0, max_*factor_RH)
    else:
        ax1.set_ylim(y_data_range[0], y_data_range[1])
    ax1.set_xlim(rangeData[0],rangeData[1]-time_deltaGen)

    # for rotation of the dates on x axis
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


    if(textInGraph!={}):
        for element in textInGraph:
            mytxt = textInGraph[element]["Text"]
            coordx = textInGraph[element]["X"]
            coordy = textInGraph[element]["Y"]
            ax1.text(coordx, coordy, mytxt)

            

    # b) Hyeto
    if(rain!=[]):
        y2 = rain[:] # CAUTION only if the rain is 1 element greater than hydro
        ax2=ax1.twinx()
        ax2.set_ylabel('Précipitations [mm/h]',color='b')
        if(y_rain_range==[]):
            ax2.set_ylim(y2.max()*(1+(factor_RH-1)*3), 0)
        else:
            ax2.set_ylim(y_rain_range[1], y_rain_range[0])

        ax2.plot_date(xdatePlotGen,y2,'-',color='b')
        ax2.fill_between(xdatePlotGen, y2, 0, color='b')
        ax2.tick_params(axis='y',labelcolor='b')

        for i in range(nbElements):
            if(allSurfaces!=[]):
                summaryTab[i].append(np.sum(y2)*dt_Gen/3600.0)
                summaryTab[i][-2] = summaryTab[i][-2]*10**(-3)/allSurfaces[i]
                tmpRatio = summaryTab[i][-2]/summaryTab[i][-1]
                summaryTab[i].append(tmpRatio)
                # summaryTab[i].append("%.4f"%(np.sum(y2)*dt_Gen/3600.0))
                # summaryTab[i][-2] = summaryTab[i][-2]*10**(-3)/allSurfaces[i]
                # tmpRatio = summaryTab[i][-2]/summaryTab[i][-1]
                # summaryTab[i].append("%.4f"%(tmpRatio))
                summaryTab[i][-1] = "%.3f"%(summaryTab[i][-1])
                summaryTab[i][-2] = "%.3f"%(summaryTab[i][-2])
                summaryTab[i][-3] = "%.3f"%(summaryTab[i][-3])
        if(measures!=[] and allSurfaces!=[] and surfaceMeasure>0.0 and addMeasfInTab):
            summaryTab[-1].append(np.sum(y2)*dtMeasure/3600.0)
            summaryTab[-1][-2] = summaryTab[-1][-2]*10**(-3)/surfaceMeasure
            tmpRatio = summaryTab[-1][-2]/summaryTab[-1][-1]
            summaryTab[-1].append(tmpRatio)
            # summaryTab[i].append("%.4f"%(np.sum(y2)*dt_Gen/3600.0))
            # summaryTab[i][-2] = summaryTab[i][-2]*10**(-3)/allSurfaces[i]
            # tmpRatio = summaryTab[i][-2]/summaryTab[i][-1]
            # summaryTab[i].append("%.4f"%(tmpRatio))
            summaryTab[-1][-1] = "%.3f"%(summaryTab[-1][-1])
            summaryTab[-1][-2] = "%.3f"%(summaryTab[-1][-2])
            summaryTab[-1][-3] = "%.3f"%(summaryTab[-1][-3])
        elif(measures!=[] and allSurfaces!=[] and addMeasfInTab):
            summaryTab[-1].append("/")
            summaryTab[-1][-2] = "/"
            summaryTab[-1].append("/")


    fig.tight_layout()
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels)
    
    # ==============
    # --- Additional plots --- :
    if(upperPlot):
        ax3 = []
        for i in range(nbAddPlot):
            # if(np.shape(x_date)==()):
            #     xdatePlot = x_date
            # else:
            #     xdatePlot = x_date[i]

            ax3.append(fig.add_subplot(gs[4+(i+1)*3,:]))
            y1 = z[i][:-1]
            
            ax3[i].set_xlabel('Date')
            if(y_labelAddPlot==[]):
                ax3[i].set_ylabel('Evapotranpiration [mm/h]',color='orange')
            else:
                ax3[i].set_ylabel(y_labelAddPlot[i],color='orange')
            ax3[i].plot_date(xdatePlotGen,y1, '-', color='orange')
            ax3[i].set_xlim(rangeData[0]-time_deltaGen,rangeData[1])
            if(deltaMajorTicks>0):
                majorTicks = HourLocator(interval=math.floor(deltaMajorTicks/3600))
                ax3[i].xaxis.set_major_locator(majorTicks)
                ax3[i].grid(which='major', alpha=1.0)
                

                if(deltaMinorTicks>0):
                    ax3[i].minorticks_on()
                    minorTicks = MicrosecondLocator(interval=deltaMinorTicks*1E6)
                    ax3[i].xaxis.set_minor_locator(minorTicks)
                    ax3[i].grid(which='minor', alpha=0.2)
            else:
                ax3[i].grid()


    # =======================
    # ---- Plots tables ---- :

    if(addTable):
        ax4 = fig.add_subplot(gs[-3:,1:5])
        columnLabels = ["Q peak [m³/s]", "t peak"+x_title.replace("Dates","")]
        if(len(title)>1) and measures!=[]:
            if(addMeasfInTab):
                rowLabels = title[:]
            else:
                rowLabels = title[:-1]
        elif len(title)>0 and measures==[]:
            rowLabels = title[:]
        else:
            rowLabels = ["Hydrograph 1"]

        if(rain!=[]):
            if(allSurfaces!=[]):
                columnLabels.append("Q cumul [mm]")
                columnLabels.append("P cumul [mm]")
                columnLabels.append("Ratio [-]")

        ax4.axis('tight')
        ax4.axis('off')
        myTab = ax4.table(cellText=summaryTab,colLabels=columnLabels,rowLabels=rowLabels,loc="center",cellLoc='center')
        myTab.auto_set_font_size(False)
        myTab.set_fontsize(8)
    





    if(writeFile!=''):
        fig.savefig(writeFile, transparent=True)
    



## This procedure can plot multiple hydrograph in the same window
def plot_multi_hydro(nbElements, writeDir, beginDate, endDate, dt, y, x_title, y_titles, \
                    graph_title=None, x_range = [], y_range = None, figSize = [10.4,5.25],\
                    writeFile=''):
    plt.figure(figsize=(figSize[0],figSize[1]))
    plt.grid()
    if(graph_title!=None):
        plt.title(graph_title)

    if(x_range==[]):
        x_range = [beginDate,endDate]
    else:
        print("TO DO: chek if the dates are valid.")


    for i in range(nbElements-1):
        if(dt[i]==3600):
            time_delta = datetime.timedelta(hours=1)
        elif(dt[i]==900):
            time_delta = datetime.timedelta(minutes=15)
        else:
            print("ERROR: Problem in the dates")
            sys.exit()
        x_date = drange(beginDate, endDate, time_delta)
        
        x1 = x_date
        y1 = y[i]
        plt.plot_date(x1, y1, '--', label=y_titles[i])
        
    if(dt[nbElements-1]==3600):
        time_delta = datetime.timedelta(hours=1)
    elif(dt[nbElements-1]==900):
        time_delta = datetime.timedelta(minutes=15)
    else:
        print("ERROR: Problem in the dates")
        sys.exit()

    x_date = drange(beginDate, endDate, time_delta)
        
    x1 = x_date
    y1 = y[nbElements-1]
    plt.plot_date(x_date, y1, '-', label=y_titles[nbElements-1], color='k')
    plt.xlim(x_range[0]-time_delta,x_range[1])
    if(x_range!=None):
        plt.ylim(y_range)
    # Rotation of the axis graduation
    plt.xticks(rotation=30)
    plt.legend()

    if(writeFile!=''):
        plt.savefig(writeFile)




def compare_withRangeResults(beginDate, endDate, dty1, dty2, y1, y2_mean, y2_min, y2_max, title='', x_axis = '', y_axis = '', labely1='', labely2='', x_range=[], y_range=[], opacity=0.3):
    ''' This graph is comparing data when with data depending on a range 
    '''
    if(len(y2_mean)!=len(y2_max) or len(y2_mean)!=len(y2_min)):
        print("ERROR: The data lengths between data are not the same.")
        sys.exit()
    
    timeDelta1 = datetime.timedelta(seconds=dty1)
    timeDelta2 = datetime.timedelta(seconds=dty2)
    x_date1 = drange(beginDate, endDate+timeDelta1, timeDelta1)
    x_date2 = drange(beginDate, endDate+timeDelta2, timeDelta2)
    if(len(x_date1)!=len(y1) or len(x_date2)!=len(y2_mean)):
        print("ERROR: the date length is not the same size as the data")
        sys.exit()
    

    if(x_range==[]):
        x_range = [beginDate, endDate]
    # if(y_range==[]):
    #     ymin = sys.float_info.max
    #     ymax = sys.float_info.min
    #     tmp = np.min(y1)
    #     tmp


    fig, ax1 = plt.subplots()
    ax1.grid()
    
    x1 = x_date1
    x2 = x_date2
    
    ax1.plot_date(x1, y1, '--', label=labely1, color='g')
    ax1.plot_date(x2,y2_mean, '-', label=labely2, color='k')
    ax1.fill_between(x2, y2_max, y2_mean, facecolor='red', alpha=opacity)
    ax1.fill_between(x2, y2_min, y2_mean, facecolor='blue', alpha=opacity)

    plt.xlim(x_range[0],x_range[1])
    if(y_range!=[]):
        plt.ylim(y_range[0],y_range[1])

    if(title!=''):
        plt.title(title)


    plt.xticks(rotation=30)
    plt.legend()

