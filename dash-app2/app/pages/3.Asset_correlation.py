import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container
from correlation_chart import correlation

#instantiate web page
dash.register_page(__name__, name= 'Asset correlation')

#style right-sidebar for controls
right_sidebar= {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "font-weight":"bold",
    "overflow": "auto" 
}

#layout design
layout= html.Div([
    dbc.Container([
        dbc.Col([
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
                dcc.Graph(id='output-chart2', figure={})
            ]),
        ], width=10),
        dbc.Col([
            dbc.Navbar(dbc.Nav([
                dcc.RadioItems(id='correlation-radioitem',
                      options=[{'label':'Price correlation', 'value':'Price-Correlation'},
                              {'label':'Returns correlation', 'value':'Returns-Correlation'}],
                          value='Returns-Correlation', inline=False, style={
                              'color':'gold'})
            ], navbar=True, vertical=True), color='#1d0251', dark=True, style=right_sidebar)
        ], width=2),
    ], fluid= True)
], style= {"margin-top":"89px"})

#callback
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

