import pandas as pd
import requests

class get_predictions:

    #get price forecasts
    def get_price_model_api(self, ticker, horizon):
        #fit model using '/fit' path
        def fit_model(ticker):
            url= "https://price-model-api.onrender.com/fit"
            #2. json data to send to path
            json= {'ticker':f'{ticker}'}
            #3. response for the post request
            response= requests.post(url=url, json=json)
            response.json()
        fit_model(ticker)
        #get forecasts    
        url= "https://price-model-api.onrender.com/forecast"
        #2. json data to send to path
        json= {
            "ticker":f"{ticker}",
            "horizon":horizon
        }
        #3. response for the post request
        response= requests.post(url=url, json=json)
        data = response.json()
        data= pd.DataFrame.from_dict(data)
        data= data[['forecast']]
        data= data.rename(columns={'forecast':'Projected Close Price'})
        data.index.name= 'Date'
        return data.reset_index()

    #get volatility  model-api forecasts
    def get_volatility_model_api(self, ticker, horizon):
        #fit model using '/fit' path
        def fit_model(ticker):
            url= "https://volatility-model-api.onrender.com/fit"
            #2. json data to send to path
            json= {'ticker':f'{ticker}'}
            #3. response for the post request
            response= requests.post(url=url, json=json)
            response.json()
        fit_model(ticker)
        #get forecasts    
        url= "https://volatility-model-api.onrender.com/predict"
        #2. json data to send to path
        json= {
            "ticker":f"{ticker}",
            "horizon":horizon
        }
        #3. response for the post request
        response= requests.post(url=url, json=json)
        data = response.json()
        data= pd.DataFrame.from_dict(data)
        data= data[['forecasts']]
        data= data.rename(columns={'forecasts':'Projected Volatility'})
        data.index.name= 'Date'
        return data.reset_index()