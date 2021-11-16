import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots
import datetime as dt
import logging
import sys


logging.basicConfig(filename='covid-dashboard.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

CREATOR='Mohsin Asif'
COUNTRY='Russia' #country of interest # Name of country must match the name provided in dataset
SRC_DAILY_DEATH='https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv'
SRC_DAILY_CASES='https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv'
logging.info(f'Started processing data for {COUNTRY}')
date_today= dt.date.today()
logging.info(f'Date today: {date_today}')

def processing_data(src,country):
        """
        This function takes the source link and country name
        to return the x and y axis
        """
        try:
            df=pd.read_csv(src)
        except pd.Error as e:
            logging.error(e)
            logging.error('Unable to read the source link. Please check logs for details')
            logging.info('Terminating the process')
            sys.exit(1)
        df.drop(['Province/State','Lat', 'Long'],inplace=True, axis=1) #dropping Province, Latitute and longiture values as they are not required
        df=df.groupby(['Country/Region']).sum() # sum rows for countries having multiple rows in the dataset
        df.reset_index(inplace=True) # Flatten the header as previous step created a multi-index header
        df=df.melt('Country/Region') # Plotly likes to have long dataset for visualization so unpivoting the dataset and
        df=df[df['Country/Region']==country] #filtering based on the country of interest
        df.reset_index(inplace=True, drop=True)
        df['daily_rate']=pd.Series(dtype=str)
        for x in range (1, len(df)):
            df['daily_rate'][x]=df['value'].iloc[x]-df['value'].iloc[x-1]
        y_axis=df['daily_rate']
        x_axis=df['variable']
        coordinates=[]
        coordinates.append(x_axis)
        coordinates.append(y_axis)
        return coordinates


logging.info('Making plots')
def make_plots(src_daily_cases, src_daily_deaths,country):
    """
    This function takes src links and country name to product graphs
    """
    trace0=go.Scatter(x=processing_data(src_daily_cases,country)[0], y=processing_data(src_daily_cases,country)[1], mode='markers', name='Number of Death')
    trace2=go.Scatter(x=processing_data(src_daily_deaths,country)[0], y=processing_data(src_daily_deaths,country)[1], mode='markers', name='Number of New Cases')
    fig = make_subplots(rows=2, cols=1, subplot_titles=(f'Number of Daily Deaths in {country}', f'Number of Daily New Cases in {country}'))
    fig.add_trace(trace0,row=1, col=1)
    fig.add_trace(trace2,row=2, col=1)

    fig.update_layout(height=900, width=1500, title_text=f'COVID-19 Deaths in {country} as of {str(date_today)}: Dashboard by Mohsin Asif')
    data1=[trace0]
    data2=[trace2]

    pyo.plot(fig)

if __name__=='__main__':
        make_plots(SRC_DAILY_CASES,SRC_DAILY_DEATH,COUNTRY)
        logging.info('Process finished successfully')