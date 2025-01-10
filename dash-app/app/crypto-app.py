from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container
from charts import chart_selector
from correlation_chart import correlation
from decomposition import decompose
from get_model_api import get_predictions

#instantiate dash app
app = Dash(__name__,
           assets_folder = 'assets',
          external_stylesheets = [dbc.themes.BOOTSTRAP],
          title='Built by Flexxie', 
          meta_tags=[{'name': 'viewport',
                      'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.5, minimum-scale=0.5'}],)

#instantiate server
server = app.server

#navbar logo src
coin_logo_src = './assets/coin2-logo.png'
gmail_logo_src = './assets/gmail-logo.png'
linkedin_logo_src = './assets/linkedin-logo.png'
github_logo_src = './assets/github-mark.png'
hand_logo = './assets/hand-logo.png'

#inline style for the left-sidebar
sidebar_style = {
    "position": "fixed",
    "top": "76px",
    "left": 0,
    "bottom": 0,
    "width":"16%",
    "overflow": "auto"    
}

#instantiate the app layout
app.layout = html.Div([
    #1 design navbar
    dbc.Navbar(dbc.Container([
        dbc.Row([
           dbc.Col(html.Img(src = coin_logo_src, height = '75px')),
            dbc.Col((dbc.NavbarBrand('CryptoCurrency-Analytics', className = 'ms-2',
                                     style ={'color':'#BF9B30'}))),
            dbc.Col(style={'width':'200px'}),
           dbc.Col(html.H4('Say hi', style={'color':'#BF9B30'})),
          dbc.Col(html.Img(src = hand_logo, height = '50px')),
          dbc.Col(dbc.NavLink(html.Img(src= gmail_logo_src, height='50px'), href='https://felixobioma99@gmail.com')),
         dbc.Col(dbc.NavLink(html.Img(src= linkedin_logo_src,
                style={'height':'50px'}), href='https://www.linkedin.com/in/felix-obioma-nkwuzor-828a20215/')),
        dbc.Col(dbc.NavLink(html.Img(src= github_logo_src, style={'height':'50px'}), href='https://github.com/flex3'))
        ], align = 'center', className = 'g-0')
    ]), color = 'grey', dark = True, fixed='top'),
    
 #2 design left-sidebar
dbc.Navbar(
 dbc.Container([
    dbc.Nav([
        dbc.NavItem(
          html.Div([
              html.Label('Select Ticker', style={'color':'#BF9B30', 'font-weight':'bold', 'align':'center'}),
              dcc.Dropdown(id='ticker-dropdown', options=[
                 {'label':'BTC-USD', 'value':'BTC-USD'},
                 {'label':'ETH-USD', 'value':'ETH-USD'},
                 {'label':'XRP-USD', 'value':'XRP-USD'},
                {'label':'DOGE-USD', 'value':'DOGE-USD'},
                {'label':'BNB-USD', 'value':'BNB-USD'},
                {'label':'SOL-USD', 'value':'SOL-USD'},
                {'label':'SHIB-USD', 'value':'SHIB-USD'},
               {'label':'TRX-USD', 'value':'TRX-USD'},
               {'label':'LTC-USD', 'value':'LTC-USD'},
               {'label':'ADA-USD', 'value':'ADA-USD'},
              ], clearable=False, value='BTC-USD',
                           style={'border-radius':'50px', 'width':'185px', 'background-color':'grey'})
          ])  
        ),
      dbc.NavItem(
          html.Div([
              html.Label('Select Chart', style={'color':'#BF9B30','font-weight':'bold', 'align':'center'}),
              dcc.Dropdown(id='crypto-chart', options=[
                 {'label':'Candlestick-Chart', 'value':'Candlestick'},
                 {'label':'EMA-RSI', 'value':'EMA-RSI'},
                 {'label':'BollingerBands', 'value':'Bollingerbands'},
                 {'label':'SMA-RSI', 'value':'SMA-RSI'},
                 {'label':'Macd-Adx', 'value':'Macd-Adx'},
                 {'label':'Psar', 'value':'Psar'},
                 {'label':'Stochastic-Oscillator', 'value':'Stochastic-Oscillator'},
                  {'label':'Returns', 'value':'Returns'},
                  {'label':'Volatility_Decomposition', 'value':'Volatility_Decomposition'},
                  {'label':'Price_Decomposition', 'value':'Price_Decomposition'}
                  
              ], clearable=False, value='Psar',
                           style={'border-radius':'50px', 'width':'185px', 'margin-top':'0px'})
          ])  
        ),
    dbc.NavItem(
        html.Div([
            html.Label('Select Prediction Model', style={'color':'#BF9B30','font-weight':'bold', 'align':'center'}),
            dcc.Dropdown(id='model-selector', options=[
                {'label':'Price forecast with arima', 'value':'Arima_model'},
                {'label':'volatility forecast with garch', 'value':'Volatility_model'}
            ], clearable=False, value='Volatility_model', optionHeight=50,
                         style={'border-radius':'50px', 'width':'185px'})
        ]),
    ),
        
        
    ], vertical = True, navbar = True) 
     
 ], fluid = True),
    
style = sidebar_style, color ='dark', dark = True),
 #design main web page
    html.Div(
        dbc.Container([
         dbc.Row([
             dbc.Col(html.Div([html.Label('Input startDate'),dcc.Input(id = 'start-date', type='text',
            minLength=10, maxLength=10, value = '2023-01-01',
            placeholder = 'yyyy-mm-dd',style = {'border-radius':'50px', 'text-align':'center'})],
            style = {'text-align':'center'})),
             dbc.Col(html.Div([html.Label('Input endDate'),dcc.Input(id = 'end-date', type='text', minLength=10,maxLength=10,
              value='2023-12-31', placeholder = 'yyyy-mm-dd',style ={'border-radius':'50px', 'text-align':'center'})],
            style = {'text-align':'center'})),
             dbc.Col(dbc.Button('Submit',id='date-inputerbutton',
                n_clicks=0, style={'background-color':'black'}))
         ]),
             
         dbc.Row([
             dcc.Graph(id='output-chart', figure={})
         ]),
        dbc.Row([
        dcc.RadioItems(id='correlation-radioitem',
                      options=[{'label':'Crypto Asset Price correlation', 'value':'Price-Correlation'},
                              {'label':'Crypto Asset returns correlation', 'value':'Returns-Correlation'}],
                          value='Returns-Correlation', inline=True)
        ], style={'margin-top':'20px'}),
            
        dbc.Row([
             dcc.Graph(id='output-chart2', figure={})
         ]),
        
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Label('Projection Period', style={'text-align':'center'}),
                    dcc.Input(id='forecast-outputdays',
                      type='number',
                     inputMode='numeric', step=5, value=5, style={'border-radius':'50px', 'width':'100px'})
                ], style={'text-align':'center'})
            ),
            dbc.Col(dbc.Button('Submit',id='submit-button',n_clicks=0, style={'background-color':'black'}))
        ], style={'margin-top':'30px'}),
        dbc.Row([
            html.Div([html.Label('Forecast Data'),
              dash_table.DataTable(data=[], page_size=4, id='forecast-table')])
        ], style={'text-align':'center','color':'black' })
            
        ], fluid = True, style={'width':'68%', 'margin-top':'90px'})
        
    ),  
    
    
])

#create callbacks to output chart
@callback(
    Output(component_id='output-chart', component_property='figure'),
    Input(component_id='ticker-dropdown', component_property='value'),
    Input(component_id='crypto-chart', component_property='value'),
    State(component_id='start-date', component_property='value'),
    State(component_id='end-date', component_property='value'),
    Input(component_id='date-inputerbutton', component_property='n_clicks')
)
def display_chart(ticker,chart,start_date, end_date,n_clicks):
    charts = chart_selector()
    new_chart = decompose()
    display_chart = None
    #if n_clicks is None:
    #    charts = None
    #else:
    #    charts = charts_inst
    if chart == 'Candlestick':
        display_chart= charts.plot_price_only(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'EMA-RSI':
        display_chart= charts.plot_ema_rsi(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'SMA-RSI':
        display_chart= charts.plot_sma_rsi(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Bollingerbands':
        display_chart= charts.plot_bollinger(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Macd-Adx':
        display_chart= charts.plot_macd_adx(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Psar':
        display_chart= charts.plot_Psar(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Stochastic-Oscillator':
        display_chart= charts.stochastic_oscillator(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Returns':
        display_chart = new_chart.plot_return(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Volatility_Decomposition':
        display_chart = new_chart.decompose_volatility(ticker=ticker, start_date=start_date, end_date=end_date)
    elif chart == 'Price_Decomposition':
        display_chart = new_chart.decompose_price(ticker=ticker, start_date=start_date, end_date=end_date)
    
    return display_chart

@callback(
    Output(component_id='output-chart2', component_property='figure'),
    Input(component_id='correlation-radioitem', component_property='value'),
    State(component_id='start-date', component_property='value'),
    State(component_id='end-date', component_property='value'),
    Input(component_id='date-inputerbutton', component_property='n_clicks')
)
def show_heatmap(chart,start_date, end_date,n_clicks):
    charts2 = correlation()
    show_chart = None
    if chart == 'Price-Correlation':
        show_chart= charts2.price_correlation(start_date=start_date, end_date=end_date)
    elif chart == 'Returns-Correlation':
        show_chart= charts2.returns_correlation(start_date=start_date, end_date=end_date)
        
    return show_chart

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
    
#run app
if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080, use_reloader=False)    