import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, dash_table, ctx
from dash_iconify import DashIconify
import plotly.express as px
import pandas as pd
import numpy as np
from functools import reduce
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
#from app import df

dash.register_page(__name__, name=[DashIconify(icon="map:diving", style={"marginRight": 8}),'Parcourir les parties non nagées'])

###################### Pré-traitement des données #########################
df_parties_NN = pd.read_csv("data/Base_parties_non_nagees.csv", dtype = {'id_analyse':int, 'nom_analyse':str, 'nom_prenom':str, 'nageur_sexe':str, 'competition_nom':str, 'mois_annee':str, 'distance_course':int, 'style_nage':str, 'round':str, 'temps_final':float,  'temps_reaction':float, 'temps_vol':float, 'temps_depart':float, 'DISTANCE_FIN_COULEE':str, 'LONGUEUR':str, 'TEMPS_FIN_COULEE': str, 'TEMPS_DE_PASSAGE': str})
df_parties_NN = df_parties_NN.rename(columns={'round': 'round_name'})

def comparer_noms(nom):
    return nom.split()[-1]

reset_NN_icon = DashIconify(icon="grommet-icons:power-reset", style={"marginRight": 5})
csv_NN_icon = DashIconify(icon="fa6-solid:file-csv", style={"marginRight": 5})
excel_NN_icon = DashIconify(icon="file-icons:microsoft-excel", style={"marginRight": 5})
question_icon = DashIconify(icon="pajamas:question", style={"marginRight": 5})
graph_NN_icon = DashIconify(icon="mdi:graph-line", style={"marginRight": 5})
selectall_NN_icon = DashIconify(icon="fluent:select-all-on-24-filled", style={"marginRight": 5})
deselectall_NN_icon = DashIconify(icon="charm:square-cross", style={"marginRight": 5})
magnifying_glass_NN_icon = DashIconify(icon="healthicons:magnifying-glass", style={"marginRight": 5})

def df_cleaned(df, distance): 
    dff = df.copy()
    dff = dff.loc[dff.distance_course == distance]
    series_dist_fin_coulee = dff['DISTANCE_FIN_COULEE'].str.split(';', expand=True)
    series_longueurs = dff['LONGUEUR'].str.split(';', expand=True)
    series_temps_fin_coulee = dff['TEMPS_FIN_COULEE'].str.split(';', expand=True)
    series_temps_passage = dff['TEMPS_DE_PASSAGE'].str.split(';', expand=True)

    col_dist = list(range(50, 50*(series_longueurs.shape[1]+1), 50))
    df_sep_dist_fin_coulee = pd.DataFrame({col_dist[i]: series_dist_fin_coulee[i] for i in range(len(col_dist))})
    df_sep_longueurs = pd.DataFrame({col_dist[i]: series_longueurs[i] for i in range(len(col_dist))})
    df_sep_temps_fin_coulee = pd.DataFrame({col_dist[i]: series_temps_fin_coulee[i] for i in range(len(col_dist))})
    df_sep_temps_passage = pd.DataFrame({col_dist[i]: series_temps_passage[i] for i in range(len(col_dist))})
    df_sep_temps_passage = df_sep_temps_passage.iloc[:, :-1]
    n = len(df_sep_temps_passage) 
    df_sep_temps_passage['0'] = [0] * n
    df_sep_temps_passage.insert(0, '0', df_sep_temps_passage.pop('0'))
    real_distance_coulee = {}
    real_temps_coulee = {}
        
    for nom_colonne in df_sep_dist_fin_coulee.columns:
        df_sep_dist_fin_coulee[nom_colonne] = df_sep_dist_fin_coulee[nom_colonne].astype(float)
        df_sep_longueurs[nom_colonne] = df_sep_longueurs[nom_colonne].astype(float)
        df_sep_temps_fin_coulee[nom_colonne] = df_sep_temps_fin_coulee[nom_colonne].astype(float)
            
        distance_coulee = df_sep_dist_fin_coulee[nom_colonne] - df_sep_longueurs[nom_colonne]
        real_distance_coulee[nom_colonne] = distance_coulee

    for nom_colonne in df_sep_temps_passage.columns:
        df_sep_temps_passage[nom_colonne] = df_sep_temps_passage[nom_colonne].astype(float)

    for i in range(0, df_sep_temps_passage.shape[1]):
        temps_coulee = df_sep_temps_fin_coulee.iloc[:,i] - df_sep_temps_passage.iloc[:,i]
        real_temps_coulee[i] = temps_coulee
            
    df_coulee = pd.DataFrame(real_distance_coulee)
    df_temps_coulee = pd.DataFrame(real_temps_coulee)
            
    nouveaux_noms_colonnes_distance = {}
    nouveaux_noms_colonnes_temps = {}
    for nom_colonne in df_coulee.columns:
        nouveaux_noms_colonnes_distance[nom_colonne] = f"Distance coulée {nom_colonne}"
    df_coulee = df_coulee.rename(columns=nouveaux_noms_colonnes_distance).round(1)
    for nom_colonne in df_temps_coulee.columns:
        valeur = 50 * (1 + int(nom_colonne))
        nouveaux_noms_colonnes_temps[nom_colonne] = f"Temps coulée {valeur}"
    df_temps_coulee = df_temps_coulee.rename(columns=nouveaux_noms_colonnes_temps).round(2)
            
    dff = pd.concat([dff, df_coulee, df_temps_coulee], axis=1)
            
    if distance == 50:
        columns_to_check = ["Distance coulée 50", "Temps coulée 50"]
        dff = dff.dropna(subset=columns_to_check, how="any")
    else:
        dff = dff.dropna(axis=1, how='any')
    dff = dff.drop(['DISTANCE_FIN_COULEE', 'LONGUEUR', 'TEMPS_FIN_COULEE','TEMPS_DE_PASSAGE'], axis=1)
    dff.temps_final = dff.temps_final.apply(lambda x: '{:02d}:{:05.2f}'.format(int(float(x) // 60), float(x) % 60))
    return(dff)


color_first_NN = '#fee3c8'
color_second_NN = '#fdc692'
color_third_NN = '#fda057'
color_fourth_NN = '#f67824'
color_fifth_NN = '#e05206'

thicker_hr_style_first_NN = {
    'border-top': '5px solid #b63c02',
}

thicker_hr_style_second_NN = {
    'border-top': '5px solid #fda057'
}

####################### Définition des cards ######################

card_carac_event_NN = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="pajamas:timer", style={"marginRight": 10}), "Sélection de l'épreuve"], className="text-nowrap"),
            html.Div("Choisissez l'épreuve que vous souhaitez parcourir. Si un menu déroulant est laissé vide, la base de données ne sera pas filtrée en fonction de la valeur de ce menu."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='distance-course-NN-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df_parties_NN.distance_course.unique())],
                    multi=False,
                    placeholder='Distance'),
                    # html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
                ], width=5),
                dbc.Col([
                    dcc.Dropdown(id='style-nage-NN-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df_parties_NN.style_nage.unique())],
                    multi=False,
                    placeholder='Style de nage'),
                    # html.Div(nage_drop := dcc.Dropdown([x for x in sorted(df.style_nage.unique())], placeholder="Nage", multi=True))
                ], width=7),
            ], justify='center'),
            
            html.Br(),
            
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='competition-nom-NN-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df_parties_NN.competition_nom.unique())],
                    multi=True,
                    placeholder='Compétition'),
                    # html.Div(epreuve_drop := dcc.Dropdown([x for x in sorted(df.round_name.unique())], placeholder="Epreuve", multi=True))
                ], width=8),
                
                
                dbc.Col([
                    dcc.Dropdown(id='round-name-NN-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df_parties_NN.round_name.unique())],
                    multi=True,
                    placeholder='Epreuve'),
                    # html.Div(epreuve_drop := dcc.Dropdown([x for x in sorted(df.round_name.unique())], placeholder="Epreuve", multi=True))
                ], width=4),
            ], justify='center')
        ], className="border-start border-dark border-5"
    ), style={"width": "50rem","background":color_first_NN},
    className="text-center m-4 ml-3"
)

card_carac_swimmer_NN = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="fa-solid:swimmer", style={"marginRight": 10}), "Sélection du nageur"], className="text-nowrap"),
            html.Div("Choisissez le sexe et / ou le patronyme que vous souhaitez parcourir. La sélection multiple est possible. Si un menu déroulant est laissé vide, la base de données ne sera pas filtrée en fonction de la valeur de ce menu."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='sexe-NN-dropdown',
                    options=[{'label': k, 'value': k} for k in df_parties_NN.nageur_sexe.unique()],
                    multi=True,
                    placeholder='Sexe'),
                    # html.Div(sex_drop := dcc.Dropdown([x for x in sorted(df.nageur_sexe.unique())], placeholder="Sexe", multi=True))
                ], width=4),
                dbc.Col([
                    dcc.Dropdown(id='nom-prenom-NN-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df_parties_NN['nom_prenom'].unique())],
                    multi=True,
                    placeholder='Nom et prénom',
                    className="mb-3"),
                    # dcc.Dropdown(id='nom-prenom-dropdown')
                    # html.Div(nom_prenom_drop := dcc.Dropdown([x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()], placeholder="Nom et prénom du nageur", multi=True))
                ], width=8)
            ]),
        ], className="border-start border-dark border-5"
    ), style={"width": "40rem","background": color_second_NN},
    className="text-center m-4 ml-3"
)

card_carac_coulee_NN = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="pajamas:question", style={"marginRight": 10}), "Sélection de la coulée"], className="text-nowrap"),
            html.Div("Choisissez la coulée que vous souhaitez analyser."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='numero-coulee-dropdown',
                    options=[{'label': k, 'value': k} for k in range(0,sum(col.startswith('Temps coulée') for col in df_parties_NN.columns))],
                    multi=False,
                    placeholder='Coulée'),
                    # html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
                ], width=5),
            ], justify='center'),
            
            html.Br(),
            
        ], className="border-start border-dark border-5"
    ), style={"width": "25rem","background": color_third_NN},
    className="text-center m-4 ml-3"
)


card_carac_variable_NN = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="healthicons:magnifying-glass", style={"marginRight": 10}), "Sélection de la variable"], className="text-nowrap"),
            html.Div("Choisissez la variable que vous souhaitez analyser pour la coulée précédemment sélectionnée."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='variable-coulee-dropdown',
                    options=[{'label': k, 'value': k} for k in ['Distance', 'Temps']],
                    multi=False,
                    placeholder='Variable'),
                    # html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
                ], width=5),
            ], justify='center'),
            
            html.Br(),
            
        ], className="border-start border-dark border-5"
    ), style={"width": "30rem","background": color_fourth_NN},
    className="text-center m-4 ml-3"
)


card_carac_graphic_NN = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="el:graph-alt", style={"marginRight": 10}), "Sélection du graphique"], className="text-nowrap"),
            html.Div("Choisissez le graphique que vous souhaitez afficher pour la coulée précédemment sélectionnée. Si vous sélectionnez '1 dimension', veuillez préalablament choisir la variable d'étude."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='graphique-coulee-dropdown',
                    options=[{'label': k, 'value': k} for k in ['1 dimension (distance OU temps en fonction du nageur)', '2 dimensions (distance ET temps en fonction du nageur)']],
                    multi=False,
                    placeholder='Graphique'),
                    # html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
                ], width=12),
            ], justify='center'),
            
            html.Br(),
            
        ], className="border-start border-dark border-5"
    ), style={"width": "35rem","background": color_fifth_NN},
    className="text-center m-4 ml-3"
)


card_warning_NN = dbc.Card(
    dbc.CardBody(
        [
            html.H5([DashIconify(icon="ph:warning-fill", style={"marginRight": 10}), "Remarque"], className="text-nowrap"),
            html.Div(["Lorsque vous sélectionnez un nageur dans le menu déroulant ci-dessus, appuyez sur le bouton ",
                      html.Span('"Mettre à jour le graphique"', style={'font-weight': 'bold'}),
                      " pour tenir compte de votre sélection. Une fois l'examen du nageur terminé, cliquez sur la petite croix à côté de son nom et appuyez à nouveau sur ",
                      html.Span('"Mettre à jour le graphique"', style={'font-weight': 'bold'}),
                      " pour afficher tous les points avec la même opacité."])
        ]
    ),
    style={"width": "40rem","background":"LightCoral"},
    className="text-center m-4"
)

####################### Layout ######################
layout = dbc.Container([
    dbc.Row([
        # dbc.Col([
        #     html.H2(children='')
        # ], width={"size": 1, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
        
        dbc.Col(
                html.H1([DashIconify(icon='map:diving', style={"marginRight": 30}),'Parcourir les parties non nagées']),
                width={"size": 'auto', "offset": 1}, style={"fontSize": 30, "textAlign": 'center'}
            ),
        
        # dbc.Col([
        #     html.H2(children='')
        # ], width={"size": 1, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
    ]),
    
    dbc.Row([
        dbc.Col([card_carac_event_NN], width={'size': 9, 'offset': 1}),
    ]),
    
    dbc.Row([
        dbc.Col([card_carac_swimmer_NN], width={'size': 9, 'offset': 2})
    ]),
    
     dbc.Row([
        dbc.Col([
            dbc.Button(
            [reset_NN_icon, "Actualiser "], id="reset-NN-button", className="me-2", n_clicks=0, style={'background-color': 'black'}
            ),
        ],  width={"size": 'auto', "offset": 5})
    ]),
     
      html.Br(), 
    
    dbc.Row([
        dbc.Col(html.Div(id='warning-message-NN', style={'color': color_third_NN, 'fontWeight': 'bold', 'textAlign' : 'center'}), width={"offset": 0})
    ]),
    
    dcc.Store(id = 'df-stored-NN'),
    
    html.Br(),
    
    dbc.Row([
        html.Div(dash_table.DataTable(
                columns=[],
                #data=[],
                id='bdd-NN',
                page_size=20,
                editable=True,
                row_selectable='multi',
                selected_rows=[],
                style_cell={'textAlign': 'center'},
                style_header={
                    'backgroundColor': color_second_NN,
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data={
                    'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                )),
        
        # html.Div(id='selected-rows', style={'textAlign': "center"})
        ]
    ),
    
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dbc.Button(
            [selectall_NN_icon, "Tout sélectionner "], id="selectall-NN-button", className="me-2", n_clicks=0, style={'background-color': 'black'}
            ),
        ],  width={"size": '2', "offset": 0}),
        dbc.Col([
            dbc.Button(
            [deselectall_NN_icon, "Tout désélectionner"], id="deselectall-NN-button", className="me-2", n_clicks=0, style={'background-color': 'black'}
            ),
        ],  width={"size": '2', "offset": 0}),
        dbc.Col([
            dbc.Button([csv_NN_icon, "Télécharger sous format .csv"], id="btn_csv_NN", style={'background-color': color_second_NN}),
            dcc.Download(id="download-dataframe-NN-csv"),
        ], width={"size": '3', "offset": 1}),
        dbc.Col([
            dbc.Button([excel_NN_icon, "Télécharger sous format .xlsx"], id="btn_excel_NN", style={'background-color': color_second_NN}),
            dcc.Download(id="download-dataframe-NN-csv"),
        ],  width={"size": '3', "offset": 0}),
    ]),
    
    html.Br(),
    
    html.Hr(style=thicker_hr_style_first_NN),
    
    dbc.Row(
        [dbc.Col(card_carac_coulee_NN), dbc.Col(card_carac_variable_NN)]
    ),
    
    dbc.Row(
        [dbc.Col(card_carac_graphic_NN, width={"offset": 2})]
    ),
    
    dbc.Row([
        dbc.Col([
            dbc.Button(
            [graph_NN_icon, "Mettre à jour le graphique"], id="reset-graph-NN-button", className="me-2", n_clicks=0, style={'background-color': 'black'}
            ),
        ],  width={"size": 'auto', "offset": 4})
    ]),
    
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='graph-NN')
        ])
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='displayed-swimmer-dropdown',
                             multi=True, 
                             placeholder='Rechercher un nageur ...'),
        width={"size": 4, "offset": 7})
    ]),
    
    dbc.Row([
        dbc.Col(card_warning_NN, width={"size": 10, "offset": 2})
    ])
    
    
])


####################### Callbacks ######################
@callback(
    Output('nom-prenom-NN-dropdown', "options"),
    Input('competition-nom-NN-dropdown',"value"),
    Input('distance-course-NN-dropdown',"value"),
    Input('style-nage-NN-dropdown', "value"),
    Input('sexe-NN-dropdown', "value"),
    Input('round-name-NN-dropdown', "value")
)
def update_nom_prenom(nom_compet,distance,style,sexe,round):
    dff = df_parties_NN.copy()
    if nom_compet:
        dff = dff.loc[dff.competition_nom.isin(nom_compet)]
    if distance:
        dff = dff.loc[dff.distance_course.isin([distance])]
    if style:
        dff = dff.loc[dff.style_nage.isin([style])]
    if sexe:
        dff = dff.loc[dff.nageur_sexe.isin(sexe)]
    if round:
        dff = dff.loc[dff.round_name.isin(round)]
    return [{'label': i, 'value': i} for i in sorted(dff.nom_prenom.unique())]



@callback(
    Output('style-nage-NN-dropdown', "options"),
    Input('distance-course-NN-dropdown', "value")
)
def update_style_NN(distance):
    dff = df_parties_NN.copy()
    if distance:
        dff = dff.loc[dff.distance_course == distance]
    return [{'label': i, 'value': i} for i in sorted(dff.style_nage.unique())]


@callback(
    Output('round-name-NN-dropdown', "options"),
    Input('competition-nom-NN-dropdown', "value")
)
def update_round_NN(competition):
    dff = df_parties_NN.copy()
    if competition:
        dff = dff.loc[dff.competition_nom.isin(competition)]
    return [{'label': i, 'value': i} for i in sorted(dff.round_name.unique())]



@callback(
    Output('warning-message-NN',"children"),
    Output('bdd-NN', "data"),
    Output('df-stored-NN', "data"),
    Input('distance-course-NN-dropdown', "value"),
    Input('style-nage-NN-dropdown', "value"),
    Input('competition-nom-NN-dropdown', "value"),
    Input('round-name-NN-dropdown', "value"),
    Input('sexe-NN-dropdown', "value"),
    Input('nom-prenom-NN-dropdown', "value"),
    Input('reset-NN-button', "n_clicks"),
)

def display_bdd_NN(distance, style, competition, round,  sexe, nageur, btn_reset_clicks):
    warning = "ATTENTION : soit vous n'avez pas sélectionné d'épreuve pour le moment, soit vous n'avez pas actualisé après avoir changé le paramètre d'étude. N'oubliez pas d'actualiser pour tenir compte des changements opérés."
    dff = pd.DataFrame()
    dff_store = pd.DataFrame().to_dict('records')
    if "reset-NN-button" in ctx.triggered[0]['prop_id']:
        if distance:
            warning = ''
            dff = df_parties_NN.copy()
            dff = df_cleaned(dff, int(distance))
            dff = dff.loc[dff.distance_course == distance]
            if style:
                dff = dff.loc[dff.style_nage == style]
            
            if competition:
                dff = dff.loc[dff.competition_nom.isin(competition)]
                
            if round:
                dff = dff.loc[dff.round_name.isin(round)]
                
            if sexe:
                dff = dff.loc[dff.nageur_sexe.isin(sexe)]
            
            if nageur:
                dff = dff.loc[dff.nom_prenom.isin(nageur)]
            
            
            liste_col = ['id_analyse', 'competition_nom', 'distance_course', 'style_nage', 'round_name']
            dff = dff.drop(columns = liste_col, axis=1)

            dff = dff.rename(columns={'nom_analyse': 'ID complet (distance, nage, épreuve, compétition)',
                                    'nom_prenom' : 'Nom & prénom du nageur', 'nageur_sexe': 'Sexe',
                                    'mois_annee': 'Date', 'temps_final': 'Temps final', 'temps_reaction': 'Temps réaction',
                                    'temps_vol': 'Temps vol', 'temps_depart': "Temps départ"})
            
            liste_round = ['Temps réaction', 'Temps vol', 'Temps départ']
            for col in liste_round:
                dff[col] = dff[col].round(2)
            
            dff_store = dff.copy()
            dff_store['index'] = dff_store.index
            dff_store = dff_store.to_dict('records')
            
            return (warning, dff_store, dff_store)
        else:
            warning = 'ATTENTION : Veuillez au moins sélectionner une distance.'
            dff_store = df_parties_NN.to_dict('records')
            
    return(warning, dff_store, dff_store)


@callback(
    Output('bdd-NN', 'columns'),
    [Input('df-stored-NN', 'data')],
)

def update_columns(data):
    if data is not None:
        # Récupérez les colonnes du DataFrame
        df_columns = pd.DataFrame(data).columns
        # Créez une liste de colonnes au format attendu par dash_table.DataTable
        columns = [{'name': str(column), 'id': str(column)} for column in df_columns]
        return columns
    # Si aucune donnée n'est disponible, utilisez une liste vide pour les colonnes
    return []


@callback(
    Output("download-dataframe-NN-csv", "data"),
    Input("btn_csv_NN","n_clicks"),
    Input("btn_excel_NN","n_clicks"),
    Input('df-stored-NN', "data"),
    prevent_initial_call = True
)

def download_df_section_csv(btn_csv_clicks, btn_excel_clicks, df_stored):
    dff = df_stored.copy()
    dff = pd.DataFrame(dff)
    if "btn_csv_NN" == ctx.triggered_id:
        return dcc.send_data_frame(dff.to_csv, "FFN_app_bdd_parties_NN.csv")
    
    if "btn_excel_NN" == ctx.triggered_id:
        return dcc.send_data_frame(dff.to_excel, "FFN_app_bdd_parties_NN.xlsx", sheet_name="Feuille_1")
    

@callback(
    Output('numero-coulee-dropdown', "options"),
    Input('distance-course-NN-dropdown', "value")
)
def update_style_section(distance):
    dff = df_parties_NN.copy()
    if distance:
        dff = df_cleaned(df_parties_NN, distance)
        dff = dff.loc[dff.distance_course.isin([distance])]
    return  [k for k in np.arange(50,50*(1+sum(col.startswith('Temps coulée') for col in dff.columns)), 50)]


@callback(
    Output('selected-rows-NN', 'children'),
    [Input('bdd-NN', 'selected_rows'),
     Input('reset-graph-NN-button', "n_clicks"),
     Input('selectall-NN-button', "n_clicks")],
     Input('deselectall-NN-button', "n_clicks"),
    [State('bdd-NN', 'data')],
)
def display_selected_rows(selected_rows, btn_reset, btn_selectall, btn_deselectall, data):
    if "reset-graph-NN-button" in ctx.triggered[0]['prop_id']:
        if selected_rows:
            indices = [row['index'] for i, row in enumerate(data) if i in selected_rows]
            return f"Lignes sélectionnées : {indices}"
        
        if "selectall-NN-button" in ctx.triggered[0]['prop_id']:
            all_rows = list(range(len(data)))
        if "deselectall-NN-button" in ctx.triggered[0]['prop_id']:
            all_rows = []
        return all_rows
    else :
        return {}

@callback(
    Output('bdd-NN', "selected_rows"),
    Input('selectall-NN-button', "n_clicks"),
    Input('deselectall-NN-button', "n_clicks"),
    Input('reset-NN-button', "n_clicks"),
    State('bdd-NN', 'data')
)
def select_all_rows(n_clicks_select, n_clicks_deselect, n_clicks_reset, data):
    all_rows = []
    if "reset-NN-button" in ctx.triggered[0]['prop_id']:
        all_rows = []
    if n_clicks_select is not None and n_clicks_select > 0 and n_clicks_select > n_clicks_deselect:
        # Sélectionnez toutes les lignes en utilisant les indices de ligne
        all_rows = list(range(len(data)))
            
    if n_clicks_deselect is not None and n_clicks_deselect > 0 and n_clicks_deselect >= n_clicks_select:
        all_rows = []
    return all_rows
    
# @callback(
#     Output('displayed-swimmer-dropdown', "options"),
#     Input('bdd-NN', "data"),
#     Input('bdd-NN', "selected_rows"),
#     Input('reset-graph-NN-button', "n_clicks"),
#     #State('reset-graph-NN-button', "n_clicks")
# )

# def update_dropdown_options(data_stored, selected_rows, btn_reset_clicks):
#     # ctx = dash.callback_context
#     # reset_clicks = ctx.inputs['reset-graph-NN-button.n_clicks']
    
#     if "reset-graph-NN-button" in ctx.triggered[0]['prop_id']:
#         if selected_rows is not None and len(selected_rows) > 0:
#             data_stored = pd.DataFrame(data_stored)
#             dff = data_stored.copy()
#             displayed_swimmer = []
#             nageurs_selectionnes = len(selected_rows)
#             for i in range(0, nageurs_selectionnes):
#                 selected_index = selected_rows[i]
#                 displayed_swimmer.append(dff.loc[selected_index,'Nom & prénom du nageur'])
#                 displayed_swimmer = list(set(displayed_swimmer))
#             return displayed_swimmer
#         else:
#             return{}
#     else:
#         return{}


# @callback(
#     Output('selected-rows-NN', 'children'),
#     Input('reset-graph-NN-button', "n_clicks"),
#     Input('deselectall-NN-button', "n_clicks"),
#     State('bdd-NN', 'selected_rows'),
#     State('bdd-NN', 'data'),
# )
# def select_deselect_all_rows(select_all_clicks, deselect_all_clicks, data):
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         return dash.no_update, ""
    
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     if button_id == "selectall-NN-button":
#         # Sélectionnez toutes les lignes en utilisant les indices de ligne
#         all_rows = list(range(len(data)))
#         return all_rows, "Toutes les lignes sélectionnées"
#     elif button_id == "deselectall-NN-button":
#         # Désélectionnez toutes les lignes en renvoyant une liste vide
#         return [], "Toutes les lignes désélectionnées"
    
#     # Si aucun des boutons n'a été cliqué, conservez la sélection actuelle
#     return dash.no_update, ""



@callback(
    Output('graph-NN', "figure"),
    Output('displayed-swimmer-dropdown', "options"),
    Input('bdd-NN', "data"),
    Input('bdd-NN', "selected_rows"),
    Input('reset-graph-NN-button', "n_clicks"),
    Input('numero-coulee-dropdown', "value"),
    Input('variable-coulee-dropdown', "value"),
    Input('graphique-coulee-dropdown', "value"),
    Input('displayed-swimmer-dropdown', "value"),
    # State('reset-graph-NN-button', "n_clicks")
)

def display_graph(data_stored, selected_rows, btn_reset_clicks, coulee, variable, graphique, selected_swimmers):
    data_stored = pd.DataFrame(data_stored)
    dff = data_stored.copy()
    figure = go.Figure()
    displayed_swimmer = []
    
    # Obtenir le nombre de clics sur le bouton de réinitialisation
    # ctx = dash.callback_context
    # reset_clicks = ctx.inputs['reset-graph-NN-button.n_clicks']

    if "reset-graph-NN-button" in ctx.triggered[0]['prop_id']:
        if selected_rows is not None and len(selected_rows) > 0:
            data_stored = pd.DataFrame(data_stored)
            dff = data_stored.copy()
            displayed_swimmer = []
            nageurs_selectionnes = len(selected_rows)
            for i in range(0, nageurs_selectionnes):
                selected_index = selected_rows[i]
                displayed_swimmer.append(dff.loc[selected_index,'Nom & prénom du nageur'])
                displayed_swimmer = list(set(displayed_swimmer))
        
        if coulee:
            ######################################## GRAPHIQUE 1D #########################################
            if graphique == '1 dimension (distance OU temps en fonction du nageur)':
                ################################ Sélection automatique ###################################
                if selected_rows is not None and data_stored.shape[0] > 50 and len(selected_rows) == data_stored.shape[0]:
                    selected_columns = [col for col in data_stored.columns if str(coulee) in col or col in ['ID complet (distance, nage, épreuve, compétition)', 'Nom & prénom du nageur', 'Temps final']]
                    data_stored = data_stored[selected_columns]
                    
                    max_nageurs = len(selected_rows)
                    dist_coulee = []
                    temps_coulee = []

                    if variable == 'Distance':
                        # Créer une liste vide pour stocker les templates hover
                        hover_templates = []
                        for i in range(max_nageurs):
                            selected_index = selected_rows[i]
                            row_variable = data_stored.iloc[selected_index,:]
                            row_variable = pd.DataFrame(row_variable)
                            row_variable = row_variable.transpose()
                            row_variable = row_variable.reset_index()
                            row_variable = row_variable.drop('index', axis=1)
                            colonne_distance = [col for col in row_variable.columns if str('Distance') in col]
                            dist_coulee.append(row_variable[colonne_distance[0]])
                            distance_value = float(row_variable[colonne_distance[0]])
                            temps_final_value = str(row_variable['Temps final'].iloc[0])
                            hover_templates.append(f"<b>Distance</b>: {distance_value:.2f}m <br><b>Temps final</b>: {temps_final_value}")

                            if selected_swimmers is not None and selected_swimmers != []:
                                if row_variable['Nom & prénom du nageur'].iloc[0] in selected_swimmers:
                                    opacity = 1  # Opacité plus faible pour les nageurs sélectionnés
                                else:
                                    opacity = 0.1
                            else:
                                opacity = 0.8  # Opacité plus élevée pour les autres nageurs lorsque le dropdown est vide
                                
                            figure.add_trace(go.Scatter(
                                x=row_variable[colonne_distance[0]],
                                y=[row_variable['Nom & prénom du nageur'].iloc[0]],  # Utilisez le nom du nageur comme étiquette sur l'axe des ordonnées
                                mode='markers',
                                name=row_variable['Nom & prénom du nageur'].iloc[0] + ', ' + row_variable['ID complet (distance, nage, épreuve, compétition)'].iloc[0],
                                hovertemplate=hover_templates[i],
                                marker=dict(opacity=opacity)
                            ))
                        
                        median_coulee = np.median(dist_coulee)
                        nb_nageurs = len(data_stored['Nom & prénom du nageur'].unique())
                        
                        # Ajustez la hauteur du graphique en fonction du nombre de nageurs
                        hauteur_graphique = max_nageurs * 4
                        
                        figure.update_layout(
                            yaxis_title='Nageur',
                            xaxis_title='Distance (en mètres)',
                            title='Distance parcourue sur la coulée étudiée en fonction des nageurs sélectionnés',
                            legend={'itemsizing': 'constant', 'title_font': {'size': 12}, 'font': {'size': 8}},  # Ajustez ici la taille de la police
                            legend_itemclick="toggleothers",
                            autosize=True,
                            height=hauteur_graphique,  # Hauteur en pixels du graphique
                            margin=dict(l=100, r=20, b=40, t=60)  # Ajustez les marges au besoin
                        )

                        # Ajoutez la ligne de repère pour la médiane
                        figure.add_shape(
                            go.layout.Shape(
                                type="line",
                                x0=median_coulee,
                                x1=median_coulee,
                                y0=-10,  # Position de départ de la ligne sur l'axe des ordonnées
                                y1=nb_nageurs,  # Position finale de la ligne sur l'axe des ordonnées
                                line=dict(color="red", width=2),  # Couleur et épaisseur de la ligne
                            )
                        )

                        # Ajout d'une annotation textuelle pour afficher la valeur de la médiane sur l'axe des abscisses
                        figure.add_annotation(
                            x=median_coulee,  # Position de l'annotation sur l'axe des abscisses
                            y= -10,  # Position de l'annotation au-dessus de l'axe
                            text=f"Médiane : {median_coulee:.2f} m",  # Texte à afficher
                            font=dict(
                                size=12,  # Taille de la police
                                color="black"  # Couleur du texte
                            )
                        )
                        
                        figure.update_yaxes(
                            title='Nageur',
                            tickfont=dict(
                                size=8  # Ajustez ici la taille de la police
                            )
                        )
                    
                    if variable == 'Temps':
                        hover_templates = []
                        for i in range(max_nageurs):
                            selected_index = selected_rows[i]
                            row_variable = data_stored.iloc[selected_index,:]
                            row_variable = pd.DataFrame(row_variable)
                            row_variable = row_variable.transpose()
                            row_variable = row_variable.reset_index()
                            row_variable = row_variable.drop('index', axis=1)
                            
                            colonne_temps = [col for col in row_variable.columns if str('Temps') in col and col not in ['Temps final', 'Temps réaction', 'Temps vol', 'Temps départ']]
                            temps_coulee.append(row_variable[colonne_temps[0]])
                            temps_value = float(row_variable[colonne_temps[0]])
                            temps_final_value = str(row_variable['Temps final'].iloc[0])
                            hover_templates.append(f"<b>Temps</b>: {temps_value:.2f}s <br><b>Temps final</b>: {temps_final_value}")
                            
                            if selected_swimmers == []:
                                selected_swimmers = displayed_swimmer
                            
                            if selected_swimmers is not None and selected_swimmers != []:
                                if row_variable['Nom & prénom du nageur'].iloc[0] in selected_swimmers:
                                    opacity = 1  # Opacité plus faible pour les nageurs sélectionnés
                                else:
                                    opacity = 0.1
                            else:
                                opacity = 0.8  # Opacité plus élevée pour les autres nageurs lorsque le dropdown est vide
                            
                            
                            figure.add_trace(go.Scatter(
                                x=row_variable[colonne_temps[0]],
                                y=[row_variable['Nom & prénom du nageur'].iloc[0]],  # Utilisez le nom du nageur comme étiquette sur l'axe des ordonnées
                                mode='markers',
                                name=row_variable['Nom & prénom du nageur'].iloc[0] + ', ' + row_variable['ID complet (distance, nage, épreuve, compétition)'].iloc[0],
                                hovertemplate=hover_templates[i],
                                marker=dict(opacity=opacity)
                            ))
                        
                        median_coulee = np.median(temps_coulee)
                        nb_nageurs = len(data_stored['Nom & prénom du nageur'].unique())
                        
                        # Ajustez la hauteur du graphique en fonction du nombre de nageurs
                        hauteur_graphique = max_nageurs * 4
                        
                        figure.update_layout(
                            yaxis_title='Nageur',
                            xaxis_title='Temps (en secondes)',
                            title='Temps passé sur la coulée étudiée en fonction des nageurs sélectionnés',
                            legend={'itemsizing': 'constant', 'title_font': {'size': 12}, 'font': {'size': 8}},  # Ajustez ici la taille de la police
                            legend_itemclick="toggleothers",
                            autosize=True,
                            height=hauteur_graphique,  # Hauteur en pixels du graphique
                            margin=dict(l=100, r=20, b=40, t=60)  # Ajustez les marges au besoin
                        )

                        # Ajoutez la ligne de repère pour la médiane
                        figure.add_shape(
                            go.layout.Shape(
                                type="line",
                                x0=median_coulee,
                                x1=median_coulee,
                                y0=-10,  # Position de départ de la ligne sur l'axe des ordonnées
                                y1=nb_nageurs,  # Position finale de la ligne sur l'axe des ordonnées
                                line=dict(color="red", width=2),  # Couleur et épaisseur de la ligne
                            )
                        )

                        # Ajout d'une annotation textuelle pour afficher la valeur de la médiane sur l'axe des abscisses
                        figure.add_annotation(
                            x=median_coulee,  # Position de l'annotation sur l'axe des abscisses
                            y= -10,  # Position de l'annotation au-dessus de l'axe
                            text=f"Médiane : {median_coulee:.2f} s",  # Texte à afficher
                            font=dict(
                                size=12,  # Taille de la police
                                color="black"  # Couleur du texte
                            )
                        )
                        
                        figure.update_yaxes(
                            title='Nageur',
                            tickfont=dict(
                                size=8  # Ajustez ici la taille de la police
                            )
                        )
                    
                ############## Sélection "manuelle" / avec moins de nageurs que n'en contient la BDD complète #############    
                if len(selected_rows) > 0  and len(selected_rows) < 50 :
                    selected_columns = [col for col in data_stored.columns if str(coulee) in col or col in ['ID complet (distance, nage, épreuve, compétition)', 'Nom & prénom du nageur', 'Temps final']]
                    data_stored = data_stored[selected_columns]
                    
                    dist_coulee = []
                    temps_coulee = []
                    
                    if variable == 'Distance':
                        hover_templates = []
                        for i in range(len(selected_rows)):
                            selected_index = selected_rows[i]
                            row_variable = data_stored.iloc[selected_index,:]
                            row_variable = pd.DataFrame(row_variable)
                            row_variable = row_variable.transpose()
                            row_variable = row_variable.reset_index()
                            row_variable = row_variable.drop('index', axis=1)
                            colonne_distance = []
                            
                            for col in row_variable.columns:
                                if str('Distance') in col :
                                    colonne_distance.append(col)
                            
                            dist_coulee.append(row_variable[colonne_distance[0]])
                            distance_value = float(row_variable[colonne_distance[0]])
                            temps_final_value = str(row_variable['Temps final'].iloc[0])
                            hover_templates.append(f"<b>Distance</b>: {distance_value:.2f}m <br><b>Temps final</b>: {temps_final_value}")
                            
                            if selected_swimmers:
                                if row_variable['Nom & prénom du nageur'].iloc[0] in selected_swimmers:
                                    opacity = 1  # Opacité plus faible pour les nageurs sélectionnés
                                else:
                                    opacity = 0.1
                            else:
                                opacity = 0.8  # Opacité plus élevée pour les autres nageurs lorsque le dropdown est vide
                                
                            figure.add_trace(go.Scatter(
                                x = row_variable[colonne_distance[0]],
                                y = row_variable['Nom & prénom du nageur'],
                                mode='markers',
                                name=data_stored.loc[selected_rows[i], 'Nom & prénom du nageur'] + ', ' + data_stored.loc[selected_rows[i], 'ID complet (distance, nage, épreuve, compétition)'],
                                hovertemplate=hover_templates[i],
                                marker=dict(opacity=opacity)
                            ))
                            
                        median_coulee = np.median(dist_coulee)
                        
                        # Ajoutez la ligne de repère pour la médiane
                        figure.add_shape(
                            go.layout.Shape(
                                type="line",
                                x0=median_coulee,
                                x1=median_coulee,
                                y0=-2,  # Position de départ de la ligne sur l'axe des ordonnées
                                y1=len(selected_rows),  # Position finale de la ligne sur l'axe des ordonnées
                                line=dict(color="red", width=2),  # Couleur et épaisseur de la ligne
                            )
                        )

                        # Ajout d'une annotation textuelle pour afficher la valeur de la médiane sur l'axe des abscisses
                        figure.add_annotation(
                            x=median_coulee,  # Position de l'annotation sur l'axe des abscisses
                            y= -2,  # Position de l'annotation au-dessus de l'axe
                            text=f"Médiane : {median_coulee:.2f} m",  # Texte à afficher
                            font=dict(
                                size=12,  # Taille de la police
                                color="black"  # Couleur du texte
                            )
                        )

                        if len(selected_rows) >= 6 :
                            hauteur_graphique = len(selected_rows) * 50  # Ajustez ici la hauteur en pixels par nageur
                        if len(selected_rows) < 6 :
                            hauteur_graphique = len(selected_rows) * 150
                            
                        figure.update_layout(
                            yaxis_title='Nageur',
                            xaxis_title='Distance (en mètres)',
                            title='Distance parcourue sur la coulée étudiée en fonction des nageurs sélectionnés',
                            #hovermode="x",
                            height=hauteur_graphique,
                            legend={'itemsizing': 'constant'},
                            legend_itemclick="toggleothers"
                        )
                        
                        
                    if variable == 'Temps':
                        hover_templates = []
                        for i in range(len(selected_rows)):
                            selected_index = selected_rows[i]
                            row_variable = data_stored.iloc[selected_index,:]
                            row_variable = pd.DataFrame(row_variable)
                            row_variable = row_variable.transpose()
                            row_variable = row_variable.reset_index()
                            row_variable = row_variable.drop('index', axis=1)
                            colonne_temps = []
                            
                            for col in row_variable.columns:
                                if str('Temps') in col and col not in ['Temps final', 'Temps réaction', 'Temps vol', 'Temps départ'] :
                                    colonne_temps.append(col)
                            
                            temps_coulee.append(row_variable[colonne_temps[0]])
                            temps_value = float(row_variable[colonne_temps[0]])
                            temps_final_value = str(row_variable['Temps final'].iloc[0])
                            hover_templates.append(f"<b>Temps</b>: {temps_value:.2f}s <br><b>Temps final</b>: {temps_final_value}")
                            
                            if selected_swimmers:
                                if row_variable['Nom & prénom du nageur'].iloc[0] in selected_swimmers:
                                    opacity = 1  # Opacité plus faible pour les nageurs sélectionnés
                                else:
                                    opacity = 0.1
                            else:
                                opacity = 0.8  # Opacité plus élevée pour les autres nageurs lorsque le dropdown est vide
                            
                            figure.add_trace(go.Scatter(
                                x = row_variable[colonne_temps[0]],
                                y = row_variable['Nom & prénom du nageur'],
                                mode='markers',
                                name=data_stored.loc[selected_rows[i], 'Nom & prénom du nageur'] + ', ' + data_stored.loc[selected_rows[i], 'ID complet (distance, nage, épreuve, compétition)'],
                                hovertemplate=hover_templates[i],
                                marker=dict(opacity=opacity)
                            ))
                            
                        median_coulee = np.median(temps_coulee)
                        
                        # Ajoutez la ligne de repère pour la médiane
                        figure.add_shape(
                            go.layout.Shape(
                                type="line",
                                x0=median_coulee,
                                x1=median_coulee,
                                y0=-2,  # Position de départ de la ligne sur l'axe des ordonnées
                                y1=len(selected_rows),  # Position finale de la ligne sur l'axe des ordonnées
                                line=dict(color="red", width=2),  # Couleur et épaisseur de la ligne
                            )
                        )

                        # Ajout d'une annotation textuelle pour afficher la valeur de la médiane sur l'axe des abscisses
                        figure.add_annotation(
                            x=median_coulee,  # Position de l'annotation sur l'axe des abscisses
                            y= -2,  # Position de l'annotation au-dessus de l'axe
                            text=f"Médiane : {median_coulee:.2f} s",  # Texte à afficher
                            font=dict(
                                size=12,  # Taille de la police
                                color="black"  # Couleur du texte
                            )
                        )

                        if len(selected_rows) >= 6 :
                            hauteur_graphique = len(selected_rows) * 50  # Ajustez ici la hauteur en pixels par nageur
                        if len(selected_rows) < 6 :
                            hauteur_graphique = len(selected_rows) * 150
                            
                        figure.update_layout(
                            yaxis_title='Nageur',
                            xaxis_title='Temps (en secondes)',
                            title='Temps passé sur la coulée étudiée en fonction des nageurs sélectionnés',
                            #hovermode="x",
                            height=hauteur_graphique,
                            legend={'itemsizing': 'constant'},
                            legend_itemclick="toggleothers"
                        )
                
                else:
                    return figure, displayed_swimmer        
            ######################################## GRAPHIQUE 2D #########################################            
            if graphique == '2 dimensions (distance ET temps en fonction du nageur)':
                    # Créez deux listes vides pour stocker les données de distance et de temps
                distances = []
                temps = []
                if selected_rows is not None and len(selected_rows) > 0:
                    selected_columns = [col for col in data_stored.columns if str(coulee) in col or col in ['ID complet (distance, nage, épreuve, compétition)', 'Nom & prénom du nageur', 'Sexe', 'Temps final']]
                    data_stored = data_stored[selected_columns]

                    for i in range(len(selected_rows)):
                        selected_index = selected_rows[i]
                        row_variable = data_stored.iloc[selected_index, :]
                        row_variable = pd.DataFrame(row_variable)
                        row_variable = row_variable.transpose()
                        row_variable = row_variable.reset_index()
                        row_variable = row_variable.drop(['index'], axis=1)
                        colonne = []
                        for col in row_variable.columns:
                            if str('Distance') in col or str('Temps') in col and str('Temps final') not in col:
                                colonne.append(col)
                                
                        if selected_swimmers:
                                if row_variable['Nom & prénom du nageur'].iloc[0] in selected_swimmers:
                                    opacity = 1  # Opacité plus élevée pour les nageurs sélectionnés
                                else:
                                    opacity = 0.1
                        else:
                            opacity = 0.8  # Opacité plus élevée pour les autres nageurs lorsque le dropdown est vide

                        if row_variable[colonne[0]].iloc[0] < 7 or row_variable[colonne[0]].iloc[0] > 15:
                            continue

                        else:
                            figure.add_trace(go.Scatter(
                                x=row_variable[colonne[0]],
                                y=row_variable[colonne[1]],
                                mode='markers',
                                name=data_stored.loc[selected_rows[i], 'Nom & prénom du nageur'] + ', ' + data_stored.loc[selected_rows[i], 'ID complet (distance, nage, épreuve, compétition)'],
                                hovertemplate='Distance: %{x} <br>Temps: %{y} <br>Temps final: %{customdata}',
                                customdata=[row_variable['Temps final'].iloc[0]],  # Convertissez le temps_final en liste,
                                marker=dict(opacity=opacity)
                            ))

                            # Ajoutez les coordonnées à vos listes
                            distances.append(row_variable[colonne[0]].iloc[0])
                            temps.append(row_variable[colonne[1]].iloc[0])

                    # Régression linéaire
                    reg = LinearRegression().fit(np.array(distances).reshape(-1, 1), temps)
                    coefficient_directeur = reg.coef_[0]
                    ordonnee_origine = reg.intercept_

                    # Créez un ensemble de points pour la ligne de régression
                    x_regr = np.linspace(min(distances), max(distances), 100)
                    y_regr = coefficient_directeur * x_regr + ordonnee_origine
                    vitesse = x_regr / y_regr

                    # Créer une liste vide pour stocker les templates hover
                    hover_templates = []

                    # Boucle à travers les points et ajoutez le modèle hover approprié
                    for i in range(len(x_regr)):
                        hover_templates.append(f'<b>Distance</b>: {x_regr[i]:.2f}m <br><b>Temps</b>: {y_regr[i]:.2f}s <br><b>Valeur de la vitesse</b>: {vitesse[i]:.2f}m/s')

                    # Ajoutez la ligne de régression au graphique
                    figure.add_trace(go.Scatter(
                        x=x_regr,
                        y=y_regr,
                        mode='lines',
                        name='Vitesse moyenne',
                        hovertemplate=hover_templates,  # Utilisez la liste de modèles hover
                        line=dict(color='black', width=2),
                    ))
                    
                    figure.update_layout(
                                yaxis_title='Temps (en secondes)',
                                xaxis_title='Distance (en mètres)',
                                title='Graphique 2D du temps en fonction de la distance pour la coulée sélectionnée',
                                #hovermode="x",
                                legend={'itemsizing': 'constant', 'font': {'size': 9}},
                                height=400,
                                width = 1000,
                                legend_itemclick="toggleothers"
                    )

                else:
                    return figure, displayed_swimmer
                
    return(figure, displayed_swimmer)


# @callback(
#     Output('graph-NN-2D', "figure"),
#     Input('graphique-coulee-dropdown', "value"),
#     Input('bdd-NN', "data"),
#     Input('bdd-NN', "selected_rows"),
#     Input('reset-graph-NN-button', "n_clicks"),
#     Input('numero-coulee-dropdown', "value"),
# )

# def display_graph_2D(graph, data_stored, selected_rows, btn_reset_clicks, coulee):
#     data_stored = pd.DataFrame(data_stored)
#     dff = data_stored.copy()
#     figure = go.Figure()
    
#     # Créez deux listes vides pour stocker les données de distance et de temps
#     distances = []
#     temps = []

#     if "reset-graph-NN-button" in ctx.triggered[0]['prop_id']:
#         if coulee:
#             ################################ Sélection automatique ###################################
#             if selected_rows is not None and len(selected_rows) > 0:
#                 selected_columns = [col for col in data_stored.columns if str(coulee) in col or col in ['ID complet (distance, nage, épreuve, compétition)', 'Nom & prénom du nageur', 'temps_final']]
#                 data_stored = data_stored[selected_columns]

#                 for i in range(len(selected_rows)):
#                     selected_index = selected_rows[i]
#                     row_variable = dff.iloc[selected_index, :]
#                     row_variable = pd.DataFrame(row_variable)
#                     row_variable = row_variable.transpose()
#                     row_variable = row_variable.reset_index()
#                     row_variable = row_variable.drop('index', axis=1)
#                     colonne = []
#                     for col in row_variable.columns:
#                         if str('Distance') in col or str('Temps') in col:
#                             colonne.append(col)

#                     if row_variable[colonne[0]].iloc[0] < 7 or row_variable[colonne[0]].iloc[0] > 15:
#                         continue

#                     else:
#                         figure.add_trace(go.Scatter(
#                             x=row_variable[colonne[0]],
#                             y=row_variable[colonne[1]],
#                             mode='markers',
#                             name=data_stored.loc[selected_rows[i], 'Nom & prénom du nageur'] + ', ' + data_stored.loc[selected_rows[i], 'ID complet (distance, nage, épreuve, compétition)'],
#                             hovertemplate='Distance: %{x} <br>Temps: %{y} <br>Temps final: %{customdata}',
#                             customdata=[row_variable['temps_final'].iloc[0]]  # Convertissez le temps_final en liste
#                         ))

#                         # Ajoutez les coordonnées à vos listes
#                         distances.append(row_variable[colonne[0]].iloc[0])
#                         temps.append(row_variable[colonne[1]].iloc[0])

#                 # Régression linéaire
#                 reg = LinearRegression().fit(np.array(distances).reshape(-1, 1), temps)
#                 coefficient_directeur = reg.coef_[0]
#                 ordonnee_origine = reg.intercept_

#                 # Créez un ensemble de points pour la ligne de régression
#                 x_regr = np.linspace(min(distances), max(distances), 100)
#                 y_regr = coefficient_directeur * x_regr + ordonnee_origine
#                 vitesse = x_regr / y_regr

#                # Créer une liste vide pour stocker les templates hover
#                 hover_templates = []

#                 # Boucle à travers les points et ajoutez le modèle hover approprié
#                 for i in range(len(x_regr)):
#                     hover_templates.append(f'<b>Distance</b>: {x_regr[i]:.2f} <br><b>Temps</b>: {y_regr[i]:.2f} <br><b>Valeur de la vitesse</b>: {vitesse[i]:.2f}')

#                 # Ajoutez la ligne de régression au graphique
#                 figure.add_trace(go.Scatter(
#                     x=x_regr,
#                     y=y_regr,
#                     mode='lines',
#                     name='Vitesse moyenne',
#                     hovertemplate=hover_templates,  # Utilisez la liste de modèles hover
#                     line=dict(color='black', width=2)
#                 ))
                
#                 figure.update_layout(
#                             yaxis_title='Temps (en secondes)',
#                             xaxis_title='Distance (en mètres)',
#                             title='Graphique 2D du temps en fonction de la distance pour la coulée sélectionnée',
#                             #hovermode="x",
#                             legend={'itemsizing': 'constant', 'font': {'size': 9}},
#                             height=400,
#                             width = 1000,
#                             legend_itemclick="toggleothers"
#                 )
    
#     return figure
