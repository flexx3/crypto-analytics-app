import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container

#instantiate dash app
app = Dash(__name__, 
           use_pages = True,
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

#left-Navigationbar
Navigation_bar= dbc.Navbar([
    dbc.Nav([
        dbc.NavLink([
        html.Div(page["name"], className="ms-2"),
        ], href=page["path"],
           active="exact",
        )
        for page in dash.page_registry.values()
    ],
     vertical=True,
    pills=True,                      
    ),
], color='dark', dark=True, style=sidebar_style)

#instantiate the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Navbar([
          dbc.Col([
              html.Img(src = coin_logo_src, height = '75px')
          ]),
          dbc.Col([dbc.NavbarBrand(
             'CryptoCurrency-Analytics', className = 'ms-2',
              style ={'color':'#BF9B30'}
          )]),
         dbc.Col(style={'width':'200px'}),
        dbc.Col(html.H4('Say hi', style={'color':'#BF9B30'})),
        dbc.Col(html.Img(src = hand_logo, height = '50px')),
        dbc.Col(dbc.NavLink(html.Img(src= gmail_logo_src, height='50px'), href='https://felixobioma99@gmail.com')),
        dbc.Col(dbc.NavLink(html.Img(src= linkedin_logo_src,
                style={'height':'50px'}), href='https://www.linkedin.com/in/felix-obioma-nkwuzor-828a20215/')),
        dbc.Col(dbc.NavLink(html.Img(src= github_logo_src, style={'height':'50px'}), href='https://github.com/flex3'))
        ], color='grey', dark=True, fixed='top'),
    ], align = 'center', className = 'g-0'),
    dbc.Row([
        dbc.Col([Navigation_bar], width=3),
        dbc.Col([dash.page_container
                ], width=9)
    ]),
], fluid= True)

#run app
if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080, use_reloader=False)