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
        predictions_data.columns= ['Date', 'Close Price Forecast']
        #set date column to index
        predictions_data.set_index('Date')
        return predictions_data

    #get volatility  model-api forecasts
    def get_volatility_model_api(self, ticker, horizon):
        #fit model using '/fit' path
        def fit_model(ticker):
            url= "https://volatility-model-api.onrender.com/fit"
            #2. json data to send to path
            json= {'ticker':ticker}
            #3. response for the post request
            response= requests.post(url=url, json=json)
            response.json()
        
        fit_model(ticker=ticker)
        #get forecasts    
        url= "https://volatility-model-api.onrender.com/predict"
        #2. json data to send to path
        json= {
            'ticker':ticker,
            'horizon':horizon
        }
        #3. response for the post request
        response= requests.post(url=url, json=json)
        data = response.json()
        data= pd.DataFrame.from_dict(data)
        data= data[['forecasts']]
        data= data.rename(columns={'forecasts':'Projected Volatility'})
        data.index.name= 'Date'
        return data.reset_index()
