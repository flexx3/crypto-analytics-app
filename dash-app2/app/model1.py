#libraries for the machine learning models
import pmdarima as pm
#Libraries to prepare data
import os
import numpy as np
import pandas as pd
import polars as pl
import duckdb
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from datetime import datetime
from dotenv import load_dotenv
from data import api_data, SqlRepository
load_dotenv()
#library to determine number of differencing to use
from decomposition import decompose
#libraries to save and load model
import joblib
from glob import glob
from pathlib import Path

class Arima:
    def __init__(self, ticker):
        self.ticker = ticker
        #instantiate name for the filepath for price model sub directory
        self.model_directory = os.environ.get('Model_directory')
        self.model1_subdirectory = os.environ.get('model1_subdirectory')
        
    #general function to get data
    def wrangle(self):
        #get current date str
        today= datetime.now().strftime('%Y-%m-%d')
        #setup conection to db
        engine= create_engine(f"duckdb:///{os.environ.get('DB_NAME')}")
        with engine.connect() as conn:
            #check if table exists
            result= conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.ticker}'"))
            table_name= result.fetchone()
        #if table name exists    
        if table_name is not None:
            #instantiate 'sqlrepo' class from data.py library
            repo= SqlRepository(uri=f"duckdb:///{os.environ.get('DB_NAME')}")
            #load data from table
            df= repo.read_table(self.ticker)
            #check if data corresponds to the most recent date
            if (df.is_empty()) or (df['Date'].max() != datetime.strptime(today, '%Y-%m-%d').date()):
                api= api_data(self.ticker)
                data= api.get_data()
                repo.insert_data(table_name=self.ticker, records=data)
                #load data from table
                df= repo.read_table(self.ticker)
            else:
                df= df
        #if table does not exists in database
        else:
            #instantiate 'api_data' class from data.py library
            api= api_data(self.ticker)
            data= api.get_data()
            #instantiate 'sqlrepo' class from data.py library
            repo= SqlRepository(uri=f"duckdb:///{os.environ.get('DB_NAME')}")
            #setup connection to execute and commit changes to the db based on the below query
            with engine.connect() as conn:
                conn.execute(text(f'Drop Table If Exists "{self.ticker}"'))
                conn.commit()
            #insert data into database
            repo.insert_data(table_name=self.ticker, records=data)
            #load data from table
            df=repo.read_table(self.ticker)
        return df
    
    #function to get d
    def _get_d(self, series):
        sig_value= 0.05
        data= series
        model= decompose()
        difference_test= model.adf(data)
        if difference_test[1] < sig_value:
            return 0
        count= 1
        while difference_test[1] > sig_value:
            data= data.diff().dropna()
            difference_test= model.adf(data)
            count = +1
        return count
    #create model and fit data
    def fit_arima(self):
        data= self.wrangle()
        #convert to pandas
        data= data.to_pandas()
        #set 'Date' as index
        data.set_index('Date', inplace=True)
        #get d
        data.sort_values(by='Date', inplace=True)
        d= self._get_d(data['Close'])
        self.model= pm.auto_arima(data['Close'],
                    start_p=1, start_q=1,max_p=5, max_q=5,  
                       # frequency of series set to annual
                      d=d, # 'd' determined manually using the adf test
                      seasonal=False,  
                      start_P=1, start_Q=1, D=0,
                      trace=True,
                      error_action='ignore',  
                      suppress_warnings=True,
                      stepwise=True,
                     approximaton=False,
                     n_jobs= -1)
        
        
       #make forecast with the model
    def make_forecast(self, horizon):
        forecasts = self.model.predict(n_periods=horizon, alpha=0.05)
        forecasts_dict = forecasts.to_dict()
        return forecasts_dict
    #save model
    def dump(self):
       #create file path to save and store the price model
        filepath = os.path.join(self.model_directory, self.model1_subdirectory,(f'{self.ticker}.pkl'))
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        #save model
        joblib.dump(self.model, filepath)
        return filepath
        
    #load model
    def load(self):
        #prepare a pattern for glob search
        pattern = os.path.join(self.model_directory, self.model1_subdirectory, (f'*{self.ticker}.pkl'))
        try:
            model_path = sorted(glob(pattern))[-1]
        except IndexError:
            raise Exception(f"Oops No model trained for {self.ticker} chai..")
        self.model = joblib.load(model_path)
        return self.model
        
        
                
     
