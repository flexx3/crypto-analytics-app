#import necessary libraries
import os
import pandas as pd
from dotenv import load_dotenv
import sqlite3
from data import api_data, SqlRepository
import plotly.graph_objects as go
import plotly.express as px
load_dotenv()

class correlation:
    #load data
    def _wrangle(self, ticker, start_date, end_date, table_name='Asset_Correlation', use_new_data=True):
        #setup connection to db
        connection= sqlite3.connect(database= os.environ.get('DB_NAME'), check_same_thread= False)
        #instantiate sql repository
        repo= SqlRepository(connection=connection)
        cursor= connection.cursor()
        if use_new_data == True:
            #instantiate api
            api= api_data()
            #extract fresh data from api
            records= api.get_data(ticker)
            #subset data to only Assets with daily Close price
            Close_price_data = records[records.columns.to_list()[0:9]]
            column_list = [val[1] for val in Close_price_data]
            Close_price_data.columns = column_list
            query = f'Drop Table If Exists "{table_name}" '
            cursor.execute(query)
            connection.commit()
            data = repo.insert_data(table_name= table_name, records= Close_price_data, if_exists= 'replace')
        df = repo.read_table(table_name)
        connection.close()
        df = df.loc[start_date:end_date]
        if df.shape[0]== 0:
                raise Exception(f"""oops! wrong date range, data only available between 
                                {df.index[0].strftime('%Y-%m-%d')} and {df.index[-1].strftime('%Y-%m-%d')}""")    
            
            
        return df
    
    #build the correlation plot based on raw closing price
    def price_correlation(self,start_date, end_date):
        Assets= ['BTC-USD','ETH-USD','XRP-USD','DOGE-USD','SHIB-USD','BNB-USD','SOL-USD','TRX-USD','LTC-USD','ADA-USD']
        data= self._wrangle(Assets, start_date= start_date, end_date= end_date)
        text= data.corr().round(3).astype(str)
        fig= go.Figure(
            data= go.Heatmap(
                x= data.columns,
                y= data.columns,
                z=data.corr().round(3),
                text=text,
                texttemplate="%{text}",
                colorscale='Viridis',
                showscale=False
            )
        )
        fig.update_layout(
            title= "Crypto Asset Correlation Based on Raw Daily Close Price",
            xaxis_rangeslider_visible= False
        )
        return fig
    
    #build correlation based on returns
    def returns_correlation(self, start_date, end_date):
        Assets= ['BTC-USD','ETH-USD','XRP-USD','DOGE-USD','SHIB-USD','BNB-USD','SOL-USD','TRX-USD','LTC-USD','ADA-USD']
        data= self._wrangle(Assets, start_date= start_date, end_date= end_date)
        returns= data.pct_change() * 100
        text= returns.corr().round(3).astype(str)
        fig= go.Figure(
            data= go.Heatmap(
                x= returns.columns,
                y= returns.columns,
                z= returns.corr().round(3),
                text= text,
                texttemplate= "%{text}",
                colorscale= "Viridis",
                showscale=False
            )
        )
        fig.update_layout(
            title= "Crypto Asset Correlation Based on Returns",
            xaxis_rangeslider_visible= False
        )
        return fig
