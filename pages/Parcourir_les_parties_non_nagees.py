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
#from app import df

dash.register_page(__name__)

###################### Pré-traitement des données #########################
df_parties_NN = pd.read_csv("data/Base_parties_non_nagees.csv", dtype = {'id_analyse':int, 'nom_analyse':str, 'nom_prenom':str, 'nageur_sexe':str, 'competition_nom':str, 'mois_annee':str, 'distance_course':int, 'style_nage':str, 'round':str, 'temps_final':float,  'temps_reaction':float, 'temps_vol':float, 'temps_depart':float, 'DISTANCE_FIN_COULEE':str, 'LONGUEUR':str, 'TEMPS_FIN_COULEE': str, 'TEMPS_DE_PASSAGE': str})
df_parties_NN = df_parties_NN.rename(columns={'round': 'round_name'})

def comparer_noms(nom):
    return nom.split()[-1]

reset_NN_icon = DashIconify(icon="grommet-icons:power-reset", style={"marginRight": 5})
csv_section_icon = DashIconify(icon="fa6-solid:file-csv", style={"marginRight": 5})
excel_section_icon = DashIconify(icon="file-icons:microsoft-excel", style={"marginRight": 5})
# graph_section_icon = DashIconify(icon="mdi:graph-line", style={"marginRight": 5})

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
    df_coulee = df_coulee.rename(columns=nouveaux_noms_colonnes_distance).round(2)
    for nom_colonne in df_temps_coulee.columns:
        valeur = 50 * (1 + int(nom_colonne))
        nouveaux_noms_colonnes_temps[nom_colonne] = f"Temps coulée {valeur}"
    df_temps_coulee = df_temps_coulee.rename(columns=nouveaux_noms_colonnes_temps).round(2)
            
    dff = pd.concat([dff, df_coulee, df_temps_coulee], axis=1)
            
    if distance == 50:
        print(dff.columns)
        columns_to_check = ["Distance coulée 50", "Temps coulée 50"]
        dff = dff.dropna(subset=columns_to_check, how="any")
    else:
        dff = dff.dropna(axis=1, how='any')
    dff = dff.drop(['DISTANCE_FIN_COULEE', 'LONGUEUR', 'TEMPS_FIN_COULEE','TEMPS_DE_PASSAGE'], axis=1)
    return(dff)

color_first_NN = '#fedfc0'
color_second_NN = '#fd8c3b'

thicker_hr_style_first_NN = {
    'border-top': '5px solid #fdb97d',
}

thicker_hr_style_second_NN = {
    'border-top': '5px solid #fd8c3b',
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
                    multi=True,
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
                    options=[{'label': k, 'value': k} for k in pd.Series(sorted((df_parties_NN['nom_prenom']), key=comparer_noms)).unique()],
                    multi=True,
                    placeholder='Nom et prénom',
                    className="mb-3"),
                    # dcc.Dropdown(id='nom-prenom-dropdown')
                    # html.Div(nom_prenom_drop := dcc.Dropdown([x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()], placeholder="Nom et prénom du nageur", multi=True))
                ], width=8)
            ]),
        ], className="border-start border-dark border-5"
    ), style={"width": "40rem","background": "turquoise"},
    className="text-center m-4 ml-3"
)

####################### Layout ######################
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2(children='')
        ], width={"size": 1, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
        
        dbc.Col(
                html.H1(children='Parcourir les parties non nagées'),
                width={"size": 'auto', "offset": 0}, style={"fontSize": 30, "textAlign": 'center'}
            ),
        
        dbc.Col([
            html.H2(children='')
        ], width={"size": 1, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
    ]),
    
    dbc.Row([
        dbc.Col([card_carac_event_NN], width={'size': 9, 'offset': 1}),
    ]),
    
    # dbc.Row([
    #     dbc.Col([card_carac_swimmer_NN], width={'size': 9, 'offset': 2})
    # ]),
    
     dbc.Row([
        dbc.Col([
            dbc.Button(
            [reset_NN_icon, "Actualiser "], id="reset-NN-button", className="me-2", n_clicks=0, style={'background-color': color_second_NN}
            ),
        ],  width={"size": 'auto', "offset": 5})
    ]),
     
      html.Br(), 
    
    dbc.Row([
        dbc.Col(html.Div(id='warning-message-NN', style={'color': color_second_NN, 'fontWeight': 'bold', 'textAlign' : 'center'}), width={"offset": 0})
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
                    'backgroundColor': '#fd8c3b',
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
            dbc.Button([csv_section_icon, "Télécharger la base de données sous format .csv"], id="btn_csv_NN", style={'background-color': '#fd8c3b'}),
            dcc.Download(id="download-dataframe-NN-csv"),
        ], width={"size": 'auto'}),
        dbc.Col([
            dbc.Button([excel_section_icon, "Télécharger la base de données sous format .xlsx"], id="btn_excel_NN", style={'background-color': '#fd8c3b'}),
            dcc.Download(id="download-dataframe-NN-csv"),
        ],  width={"size": 'auto', "offset": 0})
    ]),
    
    
])


####################### Callbacks ######################

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
def update_style_NN(competition):
    dff = df_parties_NN.copy()
    if competition:
        dff = dff.loc[dff.competition_nom.isin(competition)]
    return [{'label': i, 'value': i} for i in sorted(dff.round_name.unique())]

@callback(
    Output('warning-message-NN',"children"),
    #Output('bdd-var-par-section', "children"),
    Output('bdd-NN', "data"),
    Output('df-stored-NN', "data"),
    Input('distance-course-NN-dropdown', "value"),
    Input('style-nage-NN-dropdown', "value"),
    Input('competition-nom-NN-dropdown', "value"),
    Input('round-name-NN-dropdown', "value"),
    # Input('sexe-section-dropdown', "value"),
    Input('reset-NN-button', "n_clicks"),
)

def display_bdd_NN(distance, style, competition, round,  btn_reset_clicks):
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
                dff = dff.loc[dff.style_nage.isin(style)]
            
            if competition:
                dff = dff.loc[dff.competition_nom.isin(competition)]
                
            if round:
                dff = dff.loc[dff.round_name.isin(round)]
            
            
            liste_col = ['id_analyse', 'competition_nom', 'distance_course', 'style_nage', 'round_name']
            dff = dff.drop(columns = liste_col, axis=1)

            dff = dff.rename(columns={'nom_analyse': 'ID complet (distance, nage, épreuve, compétition)',
                                    'nom_prenom' : 'Nom & prénom du nageur' })
            
            dff_store = dff.copy()
            dff_store['index'] = dff_store.index
            dff_store = dff_store.to_dict('records')
            #print(dff_store)
            
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