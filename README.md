Hello there!
This project aimed at assisting crypto enthusiast to analyse the market was fully written in python.
It consists of a data.py module for collecting data from twelve data api using requests, pandas and polars and storing in a duckdb database using sqlalchemy.
data is also retrieved from the database with polars and sqlalchemy for analysis.
The charts.py module, decomposition.py module and correlation.py module gives the user the ability to make sound trading decisions
with the plethora of analytical charts available all written using cufflinks and plotly with data from importing the data.py module.
It is important that user have basic understanding of technical charts like bollinger,stochastic oscillator, adx, rsi, price decomposition, psar etc.
Then there's the get_model_api.py module to give user the choice of either making forecasts of future price using arima or volatilty using garch all written in their seperate scripts.
The whole thing is then combined in an interactive web app(link in the About corner),  wrapped into a docker container, deployed on render.
