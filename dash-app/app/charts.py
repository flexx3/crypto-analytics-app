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
from dotenv import load_dotenv
import sqlite3
from data import api_data, SqlRepository
from PsarClass import PSAR
load_dotenv()

class chart_selector:
    #general function to get data
    def wrangle(self, ticker, start_date, end_date, use_new_data=True):
        #setup connection to database
        connection = sqlite3.connect(database= os.environ.get('DB_NAME'), check_same_thread= False)
        #instantiate sql repo
        repo = SqlRepository(connection= connection)
        cursor = connection.cursor()
        if use_new_data is True:
            #instantiate api_data
            api = api_data()
            records = api.get_data(ticker)
            #format the columns
            if records.columns.to_list() != ['Close', 'High', 'Low', 'Open', 'Volume']:
                column_list= records.columns.to_list()
                columns= [val[0] for val in column_list]
                records.columns= columns
            query = f"Drop Table If Exists '{ticker}' "
            cursor.execute(query)
            connection.commit()
            data = repo.insert_data(table_name= ticker, records= records, if_exists= 'replace')
        df = repo.read_table(ticker)
        connection.close()
        df = df.loc[start_date:end_date]
        if df.shape[0]== 0:
                raise Exception(f"""oops! wrong date range, data only available between 
                                {df.index[0].strftime('%Y-%m-%d')} and {df.index[-1].strftime('%Y-%m-%d')}""")
        return df
    #function to plot price using quantfig library
    def plot_price_only(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_volume()
        qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #observe simple moving averages
    def plot_sma_rsi(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_volume()
        qf.add_sma(periods= 10, name= '10period sma')
        qf.add_sma(name= '20period sma', color= 'red')
        qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #visualize exponentialmovingaverages
    def plot_ema_rsi(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_volume()
        qf.add_ema(periods=10, color= 'green', name= '10period ema')
        qf.add_ema(periods=20, color= 'red', name= '20period ema')
        qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #observe pricevolatility using bollinger
    def plot_bollinger(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_volume()
        qf.add_bollinger_bands()
        qf.add_ema(periods=50, color= 'green', name= '10period ema')
        #qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #observe trend changes with macd
    def plot_macd_adx(self, ticker, start_date, end_date):
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        qf= cf.quant_figure.QuantFig(data, title= f"{ticker}'s stock price", legend= 'top', name= f'{ticker}')
        qf.add_volume()
        qf.add_macd()
        qf.add_adx()
        #qf.add_rsi(periods= 7, rsi_upper= 80, rsi_lower= 20)
        return qf.iplot(asFigure=True)
    #detect trend changes with parabolicSAR
    def plot_Psar(self, ticker, start_date, end_date):
        #load data
        data= self.wrangle(ticker=ticker, start_date=start_date, end_date=end_date)
        #instantiate psar class
        psar= PSAR()
        #get columner data for psar, trend, extremepoint(ep), accelerationFactor(aF)
        data['PSAR']= data.apply(lambda x: psar.calcPSAR(x['High'], x['Low']), axis=1)
        data['Trend']= psar.trendList
        data['EP']= psar.epList
        data['AF']= psar.afList
        uptrend= data['PSAR'].loc[data['Trend']==1]
        downtrend= data['PSAR'].loc[data['Trend']==0]
        fig= make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, x_title='Date',row_heights=[800,600])
        fig.add_traces(
            [
             go.Candlestick(
                x= data.index,
                open= data['Open'],
                high= data['High'],
                low= data['Low'],
                close= data['Close'],
                name= 'OHLC Price($)'
            ),
            go.Scatter(x= uptrend.index, y= uptrend.values, name= 'Bullish(PSAR)', line=dict(dash='dot', color='green')),
            go.Scatter(x= downtrend.index, y= downtrend.values, name= 'Bearish(PSAR)', line=dict(dash='dot', color='red'))],
        rows= [1,1,1], cols= [1,1,1])
         #add trace for volume
        fig.add_trace(go.Bar(x= data.index, y= data['Volume'], name= 'Trading Volume', marker=dict(color='blue')), row=2, col=1) 
        #update layout 
        fig.update_layout(
            title= f'Parabolic Stop and Reverse(PSAR) for {ticker}',
            yaxis_title= 'Price($)',
            yaxis2_title= 'Volume',
            xaxis_rangeslider_visible=False,
            width= 1000
        )
       
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
                name= 'OHLC Price($)'
            ),
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
            width= 1000
        )
        return fig
        
    