import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, callback, Input, Output, State, dash_table, ctx
from dash_iconify import DashIconify
from more_itertools import flatten
import plotly.express as px
import pandas as pd
import numpy as np
import base64
import io
import re
import time
from functools import reduce
#from app import df

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Prétraitement des données
t = time.time()
df = pd.read_csv("data/Freq_amp_base_entiere_date.csv", dtype = {'id_analyse':int, 'nom_analyse':str, 'nom_prenom':str, 'nageur_sexe':str, 'competition_nom':str, 'mois_annee':str, 'date':str, 'distance_course':str, 'round':str, 'style_nage':str, 'temps_final':float, 'id_cycle':float, 'temps':float, 'distance':float, 'frequence_instantanee':float, 'amplitude_instantanee':float})
liste_columns = df.columns
df = df[~df['distance_course'].astype(str).str.contains('x')].reset_index(drop=True)
df.distance_course = df.distance_course.astype(int)
df = df.dropna(subset=['nom_prenom']).reset_index(drop=True)

mini_df = df.loc[df.temps_final>0,['id_analyse', 'temps_final']].reset_index(drop=True)
df = df.drop(columns=['temps_final'],axis=1)
df = df.merge(mini_df, on = 'id_analyse')
df = df[liste_columns]
df = df.rename(columns={'round': 'round_name'})

def comparer_noms(nom):
    return nom.split()[-1]

print('chargement données page 1 : ', np.round(time.time()-t, 2))
t = time.time()


csv_icon = DashIconify(icon="fa6-solid:file-csv", style={"marginRight": 5})
excel_icon = DashIconify(icon="file-icons:microsoft-excel", style={"marginRight": 5})

# Layout
# app.layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             html.H2(children='')
#         ], width={"size": 2, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
        
#         dbc.Col(
#                 html.H1(children='Parcourir les données brutes'),
#                 width={"size": 'auto', "offset": 0}, style={"fontSize": 30, "textAlign": 'center'}
#             ),
        
#         dbc.Col([
#             html.H2(children='')
#         ], width={"size": 2, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
#     ]),
    
#     html.Br(),
    
    
#     dbc.Row([
#         dbc.Col([
#             html.Div(id_analyse_drop := dcc.Dropdown([x for x in sorted(df.id_analyse.unique())], placeholder="ID analyse", multi=True))
#         ], width=2),
#         dbc.Col([
#             html.Div(nom_analyse_drop := dcc.Dropdown([x for x in sorted(df.nom_analyse.unique())], placeholder="Nom analyse", multi=True))
#         ], width=6),
#         dbc.Col([
#             html.Div(nom_prenom_drop := dcc.Dropdown([x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()], placeholder="Nom et prénom du nageur", multi=True))
#         ], width=4)
#     ]),
    
#     dbc.Row([
#         dbc.Col([
#             html.Div(competition_nom_drop := dcc.Dropdown([x for x in sorted(df.competition_nom.unique())], placeholder="Nom de la compétition", multi=True))
#         ], width=5),
#         dbc.Col([
#             html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
#         ], width=2),
#         dbc.Col([
#             html.Div(epreuve_drop := dcc.Dropdown([x for x in sorted(df.round_name.unique())], placeholder="Epreuve", multi=True))
#         ], width=2),
#         dbc.Col([
#             html.Div(nage_drop := dcc.Dropdown([x for x in sorted(df.style_nage.unique())], placeholder="Nage", multi=True))
#         ], width=2),
#         dbc.Col([
#             html.Div(sex_drop := dcc.Dropdown([x for x in sorted(df.nageur_sexe.unique())], placeholder="Sexe", multi=True))
#         ], width=2),

#     ], justify="between", className='mt-3 mb-4'),
    
    
#     print('dropdowns : ', np.round(time.time()-t, 2)),
    
#     dbc.Row(
#         # dbc.Col(html.Div(dash_table.DataTable(id='bdd_table',columns=[{'name': str(column), 'id': str(column)} for column in df.columns.values]),
#         #                 )
#         # )
#         html.Div(id='bdd_table'),
#     ),
    
   
#     print('table : ', np.round(time.time()-t, 2)),
    
#     html.Br(),
    
#     dbc.Row([
#         dbc.Col([
#             dbc.Button([csv_icon, "Télécharger la base de données sous format .csv"], id="btn_csv"),
#             dcc.Download(id="download-dataframe-csv"),
#         ], width={"size": 'auto'}),
#         dbc.Col([
#             dbc.Button([excel_icon, "Télécharger la base de données sous format .xlsx"], id="btn_excel"),
#             dcc.Download(id="download-dataframe-xlsx"),
#         ],  width={"size": 'auto', "offset": 0})
        
        
        
#     ])

# ])

app.layout = dbc.Container([
    dbc.Row([
        dcc.Dropdown(id='id-course-dropdown',
            options=[{'label': k, 'value': k} for k in sorted(df.id_analyse.unique())],
            multi=True,
            placeholder='id analyse'),
        
        html.Div(id='tableau-donnees'),
    ]),
])

@callback(
    Output('tableau-donnees', 'children'),
    [Input('id-course-dropdown', 'value')]
)
def update_dropdown_options(id_analyse_v):
    t1 = time.time()
    dff = df.copy()

    print(len(dff))
    
    if id_analyse_v != None:
        dff = dff.loc[dff.id_analyse.isin(id_analyse_v)]

    print(len(dff))
    dff = dff.iloc[:10,:]
    return dash_table.DataTable(
        columns=[{'name': str(column), 'id': str(column)} for column in dff.columns],
        data=dff.to_dict('records'),
        editable=True
    )



if __name__ == '__main__':
    app.run_server(debug=True)