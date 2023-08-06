from pyextremes import EVA
from pyextremes.plotting import plot_extremes
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ReadDataDCENN
from ReadDataDCENN import dcenn_data

if __name__ == '__main__':

    #Verviers DCENN - 2004-2021
    #series = dcenn_data('D://OneDrive//OneDrive - Universite de Liege//Crues//2021-07 Vesdre//Données SPW//SPW-DCENN//Station Verviers').series['data']
    series=pd.read_csv('D://OneDrive//OneDrive - Universite de Liege//Crues//2021-07 Vesdre//Données SPW//SPW-DCENN//Station Verviers//seriecomplete.csv',
                       sep=' ',
                       parse_dates=True,index_col=0,
                       dtype={'Débit (m3/s)': str}).squeeze()


    '''
    series = pd.read_csv(
        #"D://OneDrive//OneDrive - Universite de Liege//Crues//2021-07 Vesdre//Données SPW//SPW-MI//Chaudfontaine//H92-20.csv",
        "D://OneDrive//OneDrive - Universite de Liege//Crues//2021-07 Vesdre//Données SPW//SPW-MI//Chaudfontaine//Chaudfontaine92-20.csv",
        #"d://1974-2021.csv",
        #"F://2021 - Les Salins//data.txt",
        sep='\t',
        index_col=0,
        parse_dates=True,
        squeeze=True,
    )
    '''

    series = (
        series
        .sort_index(ascending=True)
        .astype(float)
        .dropna()
        .loc[:pd.to_datetime("2021-07-31")]
    )
    
    #series = series - (series.index.array - pd.to_datetime("1992")) / pd.to_timedelta("365.2425D") * 2.87e-3

    def GEV(series):

        model = EVA(series)
        model.get_extremes(method="BM", block_size="365.2425D")
        model.extremes.values[-1]=460-190
        fig,ax=model.plot_extremes()
        
        model.fit_model(distribution="genextreme")

        summary = model.get_summary(
        return_period=[1, 2, 5, 10, 25, 50, 75, 100, 250, 500,1000,2000,10000],
        alpha=0.95,
        n_samples=10000)
        print(summary)

        T=np.linspace(5,201,100)
        fig,ax=model.plot_diagnostic(T,alpha=0.95,plotting_position="Hazen")
        model.plot_return_values(T,
            return_period_size="365.2425D",
            alpha=0.95,
            plotting_position="Hazen")
        
    def Gumbel(series):

        model = EVA(series)
        model.get_extremes(method="BM", block_size="365.2425D")
        fig,ax=model.plot_extremes()
        params={}
        params['fc']=0
        model.fit_model(distribution="genextreme",distribution_kwargs=params)

        summary = model.get_summary(
        return_period=[1, 2, 5, 10, 25, 50, 75, 100, 250, 500,1000,2000,10000],
        alpha=0.95,
        n_samples=10000)
        print(summary)

        T=np.linspace(5,201,100)
        fig,ax=model.plot_diagnostic(T,alpha=0.95,plotting_position="Hazen")
        model.plot_return_values(T,
            return_period_size="365.2425D",
            alpha=0.95,
            plotting_position="Hazen")

    def GPD(series):

        model = EVA(series)
        model.get_extremes(method="POT",threshold=30,r="480H")
        model.extremes.values[-1]=460-190
        print(model.extremes.values[-1])
        fig,ax=model.plot_extremes()
        # params={}
        # params['fc']=0
        model.fit_model(distribution="genpareto")
        print(model.distribution.mle_parameters)
    
        summary = model.get_summary(
        return_period=[1, 2, 5, 10, 25, 50, 75, 100, 120, 150, 175, 200, 250, 500,1000,2000,10000],
        alpha=0.95,
        n_samples=1000
        )
        
        print(summary)

        T=np.linspace(5,201,100)
        fig,ax=model.plot_diagnostic(T,alpha=0.95,plotting_position="Hazen")
        model.plot_return_values(T,
            return_period_size="365.2425D",
            alpha=0.95,
            plotting_position="Hazen")
        

    #GEV(series)
    #plt.show()
    # Gumbel(series)
    # plt.show()
    GPD(series)
    plt.show()
    pass

