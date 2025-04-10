#import necessary libraries
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from datetime import datetime
import pandas as pd
import polars as pl
import duckdb
from data import api_data, SqlRepository
import plotly.graph_objects as go
import plotly.express as px
load_dotenv()

class correlation:
    #load data
    def correlation_data(self, start_date, end_date):
        #setup connection to db
        engine= create_engine(f"duckdb:///{os.environ.get('DB_NAME')}")
        connection= engine.connect()
        with connection as conn:
            #query to output list of tables in db
            query= "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%/USD';"
            result= conn.execute(text(query))
            table_list= [row[0]for row in result.fetchall()]
            conn.commit()
            #instantiate 'sqlrepo' class from data.py library
            repo= SqlRepository(uri=f"duckdb:///{os.environ.get('DB_NAME')}")
            all_data= []
            for table in table_list:
                #load data from table
                data=repo.read_table(table)
                #search through dataframe to get data between 'start_date' and 'end_date'
                data= data.filter(pl.col('Date').is_between(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')))
                data= data.with_columns((pl.lit(table)).alias('Ticker'))
                all_data.append(data)
            df= pl.concat(all_data)
        return df
    
    #build the correlation plot based on raw closing price
    def price_correlation(self,start_date, end_date):
        #get data
        dt= self.correlation_data(start_date, end_date)
        #convert to pandas
        df= dt.to_pandas()
        #pivot data to specify OHLC data based on daily 'Close' price
        df= df.pivot_table(index='Date', columns='Ticker', values=['Close'])
        #reasign column names
        df.columns= [v[1] for v in df.columns.to_list()]
        text= df.corr().round(3).astype(str)
        fig= go.Figure(
            data= go.Heatmap(
                x= df.columns,
                y= df.columns,
                z=df.corr().round(3),
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
        #get data
        dt= self.correlation_data(start_date, end_date)
        #convert to pandas
        df= dt.to_pandas()
        #pivot data to specify OHLC data based on daily 'Close' price
        df= df.pivot_table(index='Date', columns='Ticker', values=['Close'])
        #reasign column names
        df.columns= [v[1] for v in df.columns.to_list()]
        returns= df.pct_change() * 100
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
