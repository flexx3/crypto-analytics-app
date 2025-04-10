#import libraries for the visualization
from plotly.subplots import make_subplots
from plotly import graph_objects as go
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode
#instantiate and enable cufflinks in offline mode
#init_notebook_mode(connected= True)
cf.go_offline()

#Librarie to prepare data
import os
import pandas as pd
import polars as pl
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from data import api_data, SqlRepository
from PsarClass import PSAR
load_dotenv()

class chart_selector:
    #general function to get data
    def wrangle(self, ticker, start_date, end_date):
        #setup conection to db
        engine= create_engine(f"duckdb:///{os.environ.get('DB_NAME')}")
        with engine.connect() as conn:
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
            #gets fresh data from api if specific range of data is not available from the database
            if (df.is_empty()) or df['Date'].max() != (datetime.strptime(end_date, '%Y-%m-%d').date()):
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
     #function to plot price using quantfig library
    def plot_price_only(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #observe simple moving averages
    def plot_sma_rsi(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_sma(periods= 10, name= '10period sma')
        qf.add_sma(name= '20period sma', color= 'red')
        qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #visualize exponentialmovingaverages
    def plot_ema_rsi(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_ema(periods=10, color= 'green', name= '10period ema')
        qf.add_ema(periods=20, color= 'red', name= '20period ema')
        qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #observe pricevolatility using bollinger
    def plot_bollinger(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_bollinger_bands()
        qf.add_ema(periods=50, color= 'green', name= '10period ema')
        #qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #observe trend changes with macd
    def plot_macd_adx(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_macd()
        qf.add_adx()
        #qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #detect trend changes with parabolicSAR
    def plot_Psar(self, ticker, start_date, end_date):
        #load data
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        #instantiate psar class
        psar= PSAR()
        #get columner data for psar, trend, extremepoint(ep), accelerationFactor(aF)
        data['PSAR']= data.apply(lambda x: psar.calcPSAR(x['High'], x['Low']), axis=1)
        data['Trend']= psar.trendList
        data['EP']= psar.epList
        data['AF']= psar.afList
        uptrend= data['PSAR'].loc[data['Trend']==1]
        downtrend= data['PSAR'].loc[data['Trend']==0]
        fig= go.Figure()
        fig.add_traces([go.Candlestick(
                x= data.index,
                open= data['Open'],
                high= data['High'],
                low= data['Low'],
                close= data['Close'],
                name= 'OHLC Price($)'),
        go.Scatter(x= uptrend.index, y= uptrend.values, name= 'Bullish(PSAR)', line=dict(dash='dot', color='green')),
        go.Scatter(x= downtrend.index, y= downtrend.values, name= 'Bearish(PSAR)', line=dict(dash='dot', color='red'))]) 
        #update layout 
        fig.update_layout(
            title= f'Parabolic Stop and Reverse(PSAR) for {ticker}',
            yaxis_title= 'Price($)',
            xaxis_title= 'Date',
            xaxis_rangeslider_visible= False,
            width= 750)
        
        return fig
    def stochastic_oscillator(self, ticker, start_date, end_date):
        #create function for stochastic oscillator
        def get_stochastics_data(data, window=14):
            max_high = data['High'].rolling(window=window).max()
            min_low = data['Low'].rolling(window=window).min()
            fast_k = 100 * ((data['Close'] - min_low) / (max_high - min_low))
            slow_k = fast_k.rolling(window=3).mean()
    
            return fast_k, slow_k
        #load data
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        data= data.to_pandas()
        data.set_index('Date', inplace=True)
        data['20dsma']= data['Close'].rolling(window=20).mean()
        data['%K'], data['%D']= get_stochastics_data(data)
        fig= make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, x_title='Date',row_heights=[800,600])
        fig.add_traces(
            [go.Candlestick(
                x= data.index,
                open= data['Open'],
                high= data['High'],
                low= data['Low'],
                close= data['Close'],
                name= 'OHLC Price($)'),
            go.Scatter(x= data.index, y= data['20dsma'], name= '20Day(SMA)', line=dict(color= 'green'))],
        rows= [1,1], cols= [1,1])
        fig.add_traces(
            [
                go.Scatter(x= data.index, y= data['%K'], name= 'FasterStochasticOscillator(%K)'),
                go.Scatter(x= data.index, y= data['%D'], name= 'SlowerStochasticOscillator(%D)')
            ], rows= [2,2], cols= [1,1]
        )
        fig.update_layout(
            title= f'Stochastic Oscillator and 20D SMA for {ticker}',
            yaxis_title= 'Price($)',
            yaxis2_title= 'Stochastic Oscillator',
            xaxis_rangeslider_visible=False,
            width= 750
        )
        return fig
        
    