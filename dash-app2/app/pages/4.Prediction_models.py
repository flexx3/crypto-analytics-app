import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container
from decomposition import decompose
from get_model_api import get_predictions

#instantiate web page
dash.register_page(__name__, name= 'Make Predictions')

#style right-sidebar for controls
right_sidebar= {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "font-weight":"bold",
    "overflow": "auto" 
}

layout= html.Div([
    dbc.Container([
        dbc.Col([
            dbc.Row([
                dbc.Col(
                   html.Div([
                       html.Label('Projection Period'),
                       dcc.Input(id='forecast-outputdays',type='number',inputMode='numeric',
                                 step=5, value=5, style={'border-radius':'50px', 'width':'100px'})
                   ], style={'text-align':'center', 'font-weight':'bold'}) 
                ),
                dbc.Col(dbc.Button('Submit',id='submit-button',n_clicks=0, style={'background-color':'black'}))
            ]),
            dbc.Row([
               html.Div([html.Label('Forecast Data'),dash_table.DataTable(data=[], page_size=4, id='forecast-table')],
                        style={'font-weight':'bold', 'margin-top':'25px', 'text-align':'center'}) 
            ])
        ], width=8),
        dbc.Col([
            dbc.Navbar(
                dbc.Nav([
                    dbc.NavItem(
                        html.Div([
                            html.Label('Select Ticker', style={'color':'#BF9B30'}),
                            dcc.Dropdown(id='ticker-dropdown', options=[
                                {'label':'BTC-USD', 'value':'BTC/USD'},
                                {'label':'ETH-USD', 'value':'ETH/USD'},
                                {'label':'XRP-USD', 'value':'XRP/USD'},
                                {'label':'DOGE-USD', 'value':'DOGE/USD'},
                                {'label':'BNB-USD', 'value':'BNB/USD'},
                                {'label':'SOL-USD', 'value':'SOL/USD'},
                                {'label':'SHIB-USD', 'value':'SHIB/USD'},
                               {'label':'TRX-USD', 'value':'TRX/USD'},
                               {'label':'LTC-USD', 'value':'LTC/USD'},
                               {'label':'ADA-USD', 'value':'ADA/USD'},
                              ], clearable=False, value='BTC/USD',
                            style={'border-radius':'50px', 'width':'185px', 'background-color':'grey'})
                        ], style={'text-align':'center', 'font-weight':'bold'})),
                     dbc.NavItem(html.Div([
                         html.Label('Select Model', style={'color':'#BF9B30'}),
                         dcc.Dropdown(id='model-selector', options=[
                             {'label':'Arima', 'value':'Arima_model'},
                             {'label':'Garch', 'value':'Volatility_model'}
                         ], clearable=False, value='Volatility_model', optionHeight=50, style={'border-radius':'50px', 'width':'185px'})
                     ], style={'text-align':'center', 'font-weight':'bold'})),
                ], vertical=True, navbar=True),
            color='dark', dark=True, style=right_sidebar)
        ], width=4)
    ], fluid=True)  
], style= {"margin-top":"90px"})


#make forecasts
@callback(
    Output(component_id='forecast-table', component_property='data'),
    Input(component_id='ticker-dropdown', component_property='value'),
    Input(component_id='model-selector', component_property='value'),
    State(component_id='forecast-outputdays', component_property='value'),
    Input(component_id='submit-button', component_property='n_clicks')
)
def make_forecasts(ticker,model_selector, horizon, n_clicks):
    predictions= get_predictions()
    #forecast_data = None
    if model_selector == 'Volatility_model':
        forecast_data= predictions.get_volatility_model_api(ticker=ticker, horizon=horizon)
    elif model_selector == 'Arima_model':
        forecast_data= predictions.get_price_model_api(ticker=ticker, horizon=horizon)
    
    return forecast_data.to_dict('records')
