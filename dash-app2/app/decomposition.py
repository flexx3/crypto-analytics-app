#Librarie to prepare data
import os
import numpy as np
import pandas as pd
import polars as pl
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from data import api_data, SqlRepository
from dotenv import load_dotenv
load_dotenv()
#library for decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
#library for running adf and kpss tests for stationarity
from statsmodels.tsa.stattools import adfuller, kpss
#import libraries for the visualization
from plotly.subplots import make_subplots
from plotly import graph_objects as go

class decompose:
    #general function to get data
    def wrangle(self, ticker, start_date, end_date):
        #setup conection to db
        engine= create_engine(f"duckdb:///{os.environ.get('DB_NAME')}")
        connection= engine.connect()
        with connection as conn:
            #check if table exists
            result= conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ticker}'"))
            table_name= result.fetchone()
        if table_name is not None:
            #instantiate 'sqlrepo' class from data.py library
            repo= SqlRepository(uri=f"duckdb:///{os.environ.get('DB_NAME')}")
            #load data from table
            df= repo.read_table(ticker)
            #search through dataframe to get data between 'start_date' and 'end_date'
            df= df.filter(pl.col('Date').is_between(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')))
            if (df.is_empty()) or (df['Date'].max() != datetime.strptime(end_date, '%Y-%m-%d').date()):
                api= api_data(ticker)
                data= api.get_data()
                repo.insert_data(table_name=ticker, records=data)
                #load data from table
                df= repo.read_table(ticker)
                #search through dataframe to get data between 'start_date' and 'end_date'
                df= df.filter(pl.col('Date').is_between(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')))
            else:
                df= df
        else:
            #instantiate 'api_data' class from data.py library
            api= api_data(ticker)
            data= api.get_data()
            #instantiate 'sqlrepo' class from data.py library
            repo= SqlRepository(uri=f"duckdb:///{os.environ.get('DB_NAME')}")
            #setup connection to execute and commit changes to the db based on the below query
            with engine.connect() as conn:
                conn.execute(text(f'Drop Table If Exists "{ticker}"'))
                conn.commit()
            #insert data into database
            repo.insert_data(table_name=ticker, records=data)
            #load data from table
            df=repo.read_table(ticker)
            #search through dataframe to get data between 'start_date' and 'end_date'
            df= df.filter(pl.col('Date').is_between(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')))
        return df
    
    #function for stochastic oscillator
    def get_stochastics_data(self, data, window=14):
            max_high = data['High'].rolling(window=window).max()
            min_low = data['Low'].rolling(window=window).min()
            fast_k = 100 * ((data['Close'] - min_low) / (max_high - min_low))
            slow_k = fast_k.rolling(window=3).mean()

            return fast_k, slow_k
    #function to determine model type for time series decomposition
    def model_threshold(self, data, window):
        #calculate standard deviation
        model_type= None
        rolling_std= data.rolling(window=window).std()
        #calculate rolling mean
        rolling_mean= data.rolling(window=window).mean()
        #calculate coefficient of variation(cv)
        cv= rolling_std / rolling_mean
        #calculate variance of the cv
        variance= cv.var()
        #set threshold value
        threshold= 0.02
        #identify model based on threshold and variance
        if variance < threshold:
            model_type= 'additive'
            return model_type
        else:
            model_type= 'multiplicative'
            return model_type
        
    #function to plot returns
    def plot_return(self, ticker, start_date, end_date):
        data = self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        data['Returns']= data['Close'].pct_change() *100
        data['26D EMA Returns'] = data['Returns'].ewm(span=26, adjust=False).mean()
        data['20D SMA Returns'] = data['Returns'].rolling(20).mean()
        data['%K'], data['%D']= self.get_stochastics_data(data)
        #prepare plots
        fig= make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, x_title='Date',row_heights=[800,800])
        fig.add_traces(
            [
                go.Scatter(x=data.index, y=data['Returns'], name='Returns'),
                go.Scatter(x=data.index, y=data['26D EMA Returns'], name='26D EMA Returns', line=dict(dash='dot')),
                go.Scatter(x=data.index, y=data['20D SMA Returns'], name='20D SMA Returns', line=dict(dash='dashdot', color='black')),
                go.Scatter(x= data.index, y= data['%K'], name= 'FasterStochasticOscillator(%K)'),
                go.Scatter(x= data.index, y= data['%D'], name= 'SlowerStochasticOscillator(%D)')
            ],
            rows=[1,1,1,2,2], cols=[1,1,1,1,1]
        )
        fig.update_layout(
            title= f' 26D and 20D EMA returns for {ticker}',
            yaxis_title= 'Returns',
            yaxis2_title= 'Stochastic Oscillator',
            xaxis_rangeslider_visible=False,
            width= 750
        )
        return fig
    #decompose time series volatility
    def decompose_returns(self, ticker, start_date, end_date):
        #get the data
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        data['Returns']= data['Close'].pct_change() *100
        data['Volatility']= data['Returns'].std()
        #drop missing values
        data.dropna(inplace=True)
        #determine model type
        model_type= self.model_threshold(data['Volatility'], window=5)
        #decompose data
        decomposition= seasonal_decompose(data['Returns'], model= model_type)
        #extract the decomposed components
        observed= decomposition.observed
        trend= decomposition.trend
        seasonal= decomposition.seasonal
        residual= decomposition.resid
        fig=  make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, x_title='Date',row_heights=[800,800,800,800])
        fig.add_traces(
            [
                go.Scatter(x=observed.index, y=observed, mode='lines', name='Observed'),
                go.Scatter(x=trend.index, y=trend, mode='lines', name='Trend', line=dict(dash='dot', color='blue')),
                go.Scatter(x=seasonal.index, y=seasonal, mode='lines', name='Seasonal', line=dict(dash='dash', color='green')),
                go.Scatter(x=residual.index, y=residual, mode='lines', name='Residual', line=dict(dash='dashdot', color='red'))
            ],
            rows= [1,2,3,4], cols= [1,1,1,1]
        )
        fig.update_layout(
            title= f'Daily Return Time Series Decomposition For {ticker} Weekly Trading Cycle',
            yaxis_title= 'Observed',
            yaxis2_title= 'Trend',
            yaxis3_title= 'Seasonality',
            yaxis4_title= 'Residuals',
            xaxis_rangeslider_visible=False,
            width= 750
        )
        return fig
    #decompose time series closing price
    def decompose_price(self, ticker, start_date, end_date):
        #get the data
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        data['Returns']= data['Close'].pct_change() *100
        data['Volatility']= data['Returns'].std()
        data['Close']= data['Close'].rolling(21).mean()
        #drop nan
        data.dropna(inplace= True)
        #determine model type
        model_type= self.model_threshold(data['Volatility'], window=21)
        #decompose data
        decomposition= seasonal_decompose(data['Close'], model= model_type)
        #extract the decomposed components
        observed= decomposition.observed
        trend= decomposition.trend
        seasonal= decomposition.seasonal
        residual= decomposition.resid
        fig=  make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, x_title='Date',row_heights=[800,800,800,800])
        fig.add_traces(
            [
                go.Scatter(x=observed.index, y=observed, mode='lines', name='Observed'),
                go.Scatter(x=trend.index, y=trend, mode='lines', name='Trend', line=dict(dash='dot', color='blue')),
                go.Scatter(x=seasonal.index, y=seasonal, mode='lines', name='Seasonal', line=dict(dash='dash', color='green')),
                go.Scatter(x=residual.index, y=residual, mode='lines', name='Residual', line=dict(dash='dashdot', color='red'))
            ],
            rows= [1,2,3,4], cols= [1,1,1,1]
        )
        fig.update_layout(
            title= f'Time Series Decomposition For Closing Price of {ticker} For Monthly Trading Cycle',
            yaxis_title= 'Observed',
            yaxis2_title= 'Trend',
            yaxis3_title= 'Seasonality',
            yaxis4_title= 'Residuals',
            xaxis_rangeslider_visible=False,
            width= 750
        )
        return fig
    
    #perform augmented dickey-fuller test for non-stationarity
    def adf(self, series):
        '''
        Null Hypotesis: Data is not stationary
        Alternate Hypothesis: Data is stationary
        
        '''
        indices= ['Test Statistic', 'p-value', 'No of Lags', 'No of Observations']
        adf_test= adfuller(series, autolag= 'AIC')
        result= pd.Series(adf_test[0:4], index= indices)
        for key, value in adf_test[4].items():
            result[f'Critical_value {key}']= value
        return result
    #perform kpss test for stationarity
    def kpss_test(self,series, h0_type= 'c'):
        '''
        Null Hypotesis: Data is stationary
        Alternate Hypothesis: Data is not stationary
        
        '''
        indices= ['Test Statistic', 'p-value', 'No of Lags']
        kpss_test= kpss(series, regression= h0_type)
        result= pd.Series(kpss_test[0:3], index= indices)
        for key, values in kpss_test[3].items():
            result[f'Critical_value {key}']= value
        return result
    
    