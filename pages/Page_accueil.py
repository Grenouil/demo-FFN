import dash
from dash import dcc, html, callback, Input, Output, ctx
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

dash.register_page(__name__, path='/')

liste_mdp = ['lo', 'la']
check_user_icon = DashIconify(icon="fa6-solid:user-check", style={"marginRight": 15})

layout = dbc.Container(
    [
        html.Br(),

        dbc.Row([
            dbc.Col(
                html.H3(children='Pour accéder au contenu de ce site, veuillez entrer votre mot de passe.'),
                width = {"style" : 3}, style={"fontSize": 30, "textAlign": 'center'}
            )
        ]),
        
        html.Br(),
        html.Br(),
        html.Br(),
        
        dbc.Row([
            dbc.Col([
                dcc.Input(id="password", type="password", debounce=True, placeholder="Saisissez votre mot de passe ...", size='50')
            ],
            width={"size": 5, "offset": 3}
            )
        ]),
        
        html.Br(),
        
        dbc.Row([
            dbc.Col(
                dbc.Button([check_user_icon, 'Valider'], id='enter-password'),
                width={"size": 3, "offset": 5}
            )
        ]),
            
        dbc.Row([
            dbc.Col([
                html.Br(),
                
                html.Div(id='updated_access',
                     style={'textAlign': 'center', 'color': 'red'}
                )
            ])
        ])
    ])


@callback(
    Output('updated_access', 'children'),
    Input("enter-password", "n_clicks"),
    Input("password", "value"),
)

def update_access(n_clicks, input_value):
    if "enter-password" == ctx.triggered_id:
        if input_value in liste_mdp:
            return f"Mot de passe correct. Vous pouvez désormais accéder à l'ensemble de l'application. "
        else:
            return f'Mot de passe incorrect. Veuillez réessayer.'
    else:
        return f"Aucun mot de passe n'a encore été saisi."
   
