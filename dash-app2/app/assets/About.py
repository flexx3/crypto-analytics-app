import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container

#instantiate web page
dash.register_page(__name__ ,assets_folder = 'assets', path= '/', name= 'About')
waving_hand_logo= './assets/waving-hand.svg'

#app layout
layout= html.Div([
    dbc.Container([
        dbc.Row([
                html.H1(['Hello there', html.Img(src= waving_hand_logo, height= '50px')]),
                html.Hr(),
                html.H5(["Welcome to the crypto-analytics webapp that enables you to make informed trading decisions by:",html.Br(),
                ">Access to several charts for Fundamental analysis.",html.Br(),
                ">Viewing Asset correlations.",html.Br(),
                ">Make forecast of future price and volatility trends.",html.Br(),
                 "Daily OHLC data from twelvedatapi is loaded into a duckdb database for analysis.",html.Br(),
                 "We are only allowed to make a maximum of 6 api calls per minute and 80 api calls per month, because we are using the free tier.", html.Br(),
                  "The code is enhanced to fully optimize our api calls so the user doesnt get stranded. just follow the instructions below.", html.Br(),],
                style={'font-weight':'bold'}),
               html.H5([
               "1.Fundamental Analysis> Select a crypto ticker from the dropdown, input preferred date range, click submit", html.Br(),
               "Select from a list of charts on the charts dropdown for analysis.",html.Br(),
               "When a crypto ticker is selected, the database is searched for the table corresponding to it.",html.Br(),
               "which is then outputted based on the date range, If data from the given range or table corresponding to the ticker is not available,",html.Br(),
               "An api call is made to update the data or load fresh data for ticker into a new table for analysis.",html.Br(),
                html.Br(),
               "2.Asset Correlation> You are only required to input your preferred date range,",html.Br(),
               "Then select asset correlation based on daily close price or daily return",html.Br(),
               "To view asset correlations for a set of crypto assets, the database is searched for tables corresponding to each crypto ticker,",html.Br(),
               "correlated returns or close price data is then outputted based on the date range available in the database.",html.Br(),
               "Here fresh api calls are not made, hence to get updated correllated data,",html.Br(),
                "ensure to have loaded updated data for each of the crypto assets of your choice from the Fundamental Analysis page.",html.Br(),
                html.Br(),   
              "3.Make Predictions> Select ticker and Choose to make forecasts for its volatility(using Garch model) or close price(Arima model).",html.Br(),
              "Thank you so much for your time.",html.Br(),
              "Reach out to me on linkedin, star the project on github (Click the image on the Navbar).",html.Br(),
               "Wishing you an insightful analysis!!!!"
               ], style={'font-weight':'Bold'})
        ]),
    ], fluid= True)   
],style= {"margin-top":"90px", "margin-left":"60px"})
