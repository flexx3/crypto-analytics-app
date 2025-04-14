import pandas as pd
import requests
from model1 import Arima

class get_predictions:

    #get price forecasts
    def get_price_model_api(self, ticker, horizon):
        #instantiate model
        model= Arima(ticker)
        #fit model to data
        model.fit_arima()
        #make predictions
        predictions= model.make_forecast(horizon)
        #convert predictions data into a dataframe
        df= pd.DataFrame.from_dict(predictions, orient='index')
        #reset index
        predictions_data= df.reset_index()
        #name columns
        predictions_data.columns= ['Date', f'{ticker} Close Price Forecast']
        #set date column to index
        predictions_data.set_index('Date')
        return predictions_data

    #get volatility  model-api forecasts
    def get_volatility_model_api(self, ticker, horizon):
       #instantiate model
        model= Garch_model(ticker)
        #fit model to data
        model.fit()
        #get predictions
        predictions= model.forecast_volatility(horizon)
         #convert predictions data into a dataframe
        df= pd.DataFrame.from_dict(predictions.to_dict(), orient='index')
        predictions_data= df.reset_index()
        #name columns
        predictions_data.columns= ['Date', f'{ticker} Volatility Forecast']
        #set date column to index
        return predictions_data 
