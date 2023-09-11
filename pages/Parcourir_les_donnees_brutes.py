import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, dash_table, ctx
from dash_iconify import DashIconify
import plotly.express as px
import pandas as pd
import numpy as np
from functools import reduce
#from app import df

dash.register_page(__name__)

###################### Pré-traitement des données #########################
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
df = df.drop('mois_annee',axis=1)
df['temps_final'] = df['temps_final'].apply(lambda x: '{:02d}:{:05.2f}'.format(int(float(x) // 60), float(x) % 60))

def comparer_noms(nom):
    return nom.split()[-1]

# print('chargement données page 1 : ', np.round(time.time()-t, 2))
# t = time.time()

# liste_id = [x for x in sorted(df.id_analyse.unique())]
# liste_noms_analye = [x for x in sorted(df.nom_analyse.unique())]
# liste_noms_prenoms = [x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()]
# liste_competitions_noms = [x for x in sorted(df.competition_nom.unique())]
# liste_distances_courses = [x for x in sorted(df.distance_course.unique())]
# liste_round_name = [x for x in sorted(df.round_name.unique())]
# liste_style_nage = [x for x in sorted(df.style_nage.unique())]
# liste_sexes = [x for x in sorted(df.nageur_sexe.unique())]

# print('listes dropdowns : ', np.round(time.time()-t, 2))

csv_icon = DashIconify(icon="fa6-solid:file-csv", style={"marginRight": 5})
excel_icon = DashIconify(icon="file-icons:microsoft-excel", style={"marginRight": 5})


###################### Définition des cards #########################
# card_carac_analyse = dbc.Card(
#     dbc.CardBody(
#         [
#             html.H4([DashIconify(icon="bxs:spreadsheet", style={"marginRight": 10}), "Sélection de l'analyse"], className="text-nowrap"),
#             html.Div("Choisissez l'identifiant et / ou le nom de l'analyse."),
#             html.Br(),
#             dbc.Row(
#                 [
#                     dbc.Col(
#                         dcc.Dropdown(
#                             id='id-course-dropdown',
#                             options=[{'label': k, 'value': k} for k in sorted(df.id_analyse.unique())],
#                             multi=True,
#                             placeholder='ID analyse',
#                             className="text-center"
#                         ),
#                         width=5
#                     )
#                 ],
#                 justify="center"
#             ),
#             html.Br(),
#             dbc.Row(
#                 [
#                     dbc.Col(
#                         dcc.Dropdown(
#                             id='nom-analyse-dropdown',
#                             options=[{'label': k, 'value': k} for k in sorted(df.nom_analyse.unique())],
#                             multi=True,
#                             placeholder='Nom analyse',
#                             className="text-center"
#                         ),
#                         width=12
#                     )
#                 ],
#                 justify="center"
#             ),
#         ],
#         className="border-start border-dark border-5"
#     ),
#     style={"width": "32rem", "background": "Wheat"},
#     className="text-center m-4"
# )


card_carac_swimmer = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="fa-solid:swimmer", style={"marginRight": 10}), "Sélection du nageur"], className="text-nowrap"),
            html.Div("Choisissez le sexe et / ou le patronyme."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='sexe-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df.nageur_sexe.unique())],
                    multi=True,
                    placeholder='Sexe'),
                    # html.Div(sex_drop := dcc.Dropdown([x for x in sorted(df.nageur_sexe.unique())], placeholder="Sexe", multi=True))
                ], width=4),
                dbc.Col([
                    dcc.Dropdown(id='nom-prenom-dropdown',
                    options=[{'label': k, 'value': k} for k in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()],
                    multi=True,
                    placeholder='Nom et prénom',
                    className="mb-3"),
                    # dcc.Dropdown(id='nom-prenom-dropdown')
                    # html.Div(nom_prenom_drop := dcc.Dropdown([x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()], placeholder="Nom et prénom du nageur", multi=True))
                ], width=8)
            ]),
            html.Br()
        ], className="border-start border-dark border-5"
    ), style={"width": "23rem","background":"#FECEE3"},
    className="text-center m-4 ml-3"
)

card_carac_compet = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="ph:calendar-fill", style={"marginRight": 10}), "Sélection de la compétition"], className="text-nowrap"),
            html.Div("Choisissez la date et / ou le nom de la compétition."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='date-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df.date.unique())],
                    multi=True,
                    placeholder='Date'),
                    # html.Div(sex_drop := dcc.Dropdown([x for x in sorted(df.nageur_sexe.unique())], placeholder="Sexe", multi=True))
                ], width=4),
                dbc.Col([
                    dcc.Dropdown(id='nom-competition-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df.competition_nom.unique())],
                    multi=True,
                    placeholder='Nom de la compétition',
                    className="mb-5"),
                    # dcc.Dropdown(id='nom-competition-dropdown'),
                    # html.Div(competition_nom_drop := dcc.Dropdown([x for x in sorted(df.competition_nom.unique())], placeholder="Nom de la compétition", multi=True))
                ], width=8),
            ])
        ], className="border-start border-dark border-5"
    ), style={"width": "32rem","background":"#FE9FC9"},
    className="text-center m-4 ml-3"
)

card_carac_event = dbc.Card(
    dbc.CardBody(
        [
            html.H4([DashIconify(icon="pajamas:timer", style={"marginRight": 10}), "Sélection de l'épreuve"], className="text-nowrap"),
            html.Div("Choisissez la distance, l'épreuve et / ou le style de nage."),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(id='distance-course-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df.distance_course.unique())],
                    multi=True,
                    placeholder='Distance'),
                    # html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
                ], width=5),
                dbc.Col([
                    dcc.Dropdown(id='style-nage-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df.style_nage.unique())],
                    multi=True,
                    placeholder='Style de nage'),
                    # html.Div(nage_drop := dcc.Dropdown([x for x in sorted(df.style_nage.unique())], placeholder="Nage", multi=True))
                ], width=7),
            ], justify='center'),
            
            html.Br(),
            
            dbc.Row([
                 dbc.Col([
                    dcc.Dropdown(id='round-name-dropdown',
                    options=[{'label': k, 'value': k} for k in sorted(df.round_name.unique())],
                    multi=True,
                    placeholder='Epreuve'),
                    # html.Div(epreuve_drop := dcc.Dropdown([x for x in sorted(df.round_name.unique())], placeholder="Epreuve", multi=True))
                ], width=8),
            ], justify='center')
        ], className="border-start border-dark border-5"
    ), style={"width": "32rem","background":"#FE70AF"},
    className="text-center m-4 ml-3"
)


####################### Layout ######################
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2(children='')
        ], width={"size": 2, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
        
        dbc.Col(
                html.H1(children='Parcourir les données brutes'),
                width={"size": 'auto', "offset": 0}, style={"fontSize": 30, "textAlign": 'center'}
            ),
        
        dbc.Col([
            html.H2(children='')
        ], width={"size": 2, "offset": 0}, style={"fontSize": 30, "backgroundColor": "black"}),
    ]),
    
    dbc.Row(
        [dbc.Col(card_carac_swimmer),dbc.Col(card_carac_compet)]
    ),
    
    dbc.Row(
        [dbc.Col(card_carac_event, width={"offset": 2}),
    ]),
    
    # dbc.Row([
    #     dbc.Col([
    #         dcc.Dropdown(id='id-course-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.id_analyse.unique())],
    #         multi=True,
    #         placeholder='ID analyse'),
    #     ], width=2),
    #     dbc.Col([
    #         dcc.Dropdown(id='nom-analyse-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.nom_analyse.unique())],
    #         multi=True,
    #         placeholder='Nom analyse'),
    #         # html.Div(nom_analyse_drop := dcc.Dropdown([x for x in sorted(df.nom_analyse.unique())], placeholder="Nom analyse", multi=True))
    #     ], width=6),
    #     dbc.Col([
    #         dcc.Dropdown(id='nom-prenom-dropdown',
    #         options=[{'label': k, 'value': k} for k in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()],
    #         multi=True,
    #         placeholder='Nom et prénom'),
    #         # html.Div(nom_prenom_drop := dcc.Dropdown([x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()], placeholder="Nom et prénom du nageur", multi=True))
    #     ], width=4)
    # ]),
    
    # dbc.Row([
    #     dbc.Col([
    #         dcc.Dropdown(id='nom-competition-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.competition_nom.unique())],
    #         multi=True,
    #         placeholder='Nom de la compétition'),
    #         # html.Div(competition_nom_drop := dcc.Dropdown([x for x in sorted(df.competition_nom.unique())], placeholder="Nom de la compétition", multi=True))
    #     ], width=5),
    #     dbc.Col([
    #         dcc.Dropdown(id='distance-course-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.distance_course.unique())],
    #         multi=True,
    #         placeholder='Distance'),
    #         # html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
    #     ], width=2),
    #     dbc.Col([
    #         dcc.Dropdown(id='round-name-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.round_name.unique())],
    #         multi=True,
    #         placeholder='Epreuve'),
    #         # html.Div(epreuve_drop := dcc.Dropdown([x for x in sorted(df.round_name.unique())], placeholder="Epreuve", multi=True))
    #     ], width=4),

    # ], justify="between", className='mt-3 mb-4'),
    
    # dbc.Row([
    #     dbc.Col([
    #         dcc.Dropdown(id='style-nage-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.style_nage.unique())],
    #         multi=True,
    #         placeholder='Style de nage'),
    #         # html.Div(nage_drop := dcc.Dropdown([x for x in sorted(df.style_nage.unique())], placeholder="Nage", multi=True))
    #     ], width=4),
    #     dbc.Col([
    #         dcc.Dropdown(id='sexe-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.nageur_sexe.unique())],
    #         multi=True,
    #         placeholder='Sexe'),
    #         # html.Div(sex_drop := dcc.Dropdown([x for x in sorted(df.nageur_sexe.unique())], placeholder="Sexe", multi=True))
    #     ], width=2),
    #     dbc.Col([
    #         dcc.Dropdown(id='date-dropdown',
    #         options=[{'label': k, 'value': k} for k in sorted(df.date.unique())],
    #         multi=True,
    #         placeholder='Date'),
    #         # html.Div(sex_drop := dcc.Dropdown([x for x in sorted(df.nageur_sexe.unique())], placeholder="Sexe", multi=True))
    #     ], width=3),

    # ], justify="between", className='mt-3 mb-4'),
    
    html.Br(),
    
    dbc.Row(
        html.Div(id='bdd_table'),
    ),
    
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dbc.Button([csv_icon, "Télécharger la base de données sous format .csv"], id="btn_csv", style={'background-color':'#FE70AF'}),
            dcc.Download(id="download-dataframe-csv"),
        ], width={"size": 'auto'}),
        dbc.Col([
            dbc.Button([excel_icon, "Télécharger la base de données sous format .xlsx"], id="btn_excel", style={'background-color':'#FE70AF'}),
            dcc.Download(id="download-dataframe-xlsx"),
        ],  width={"size": 'auto', "offset": 0})
    ])

])


####################### Callbacks ######################     
@callback(
    Output('bdd_table', 'children'),
    [#Input('id-course-dropdown', 'value'),
     #Input('nom-analyse-dropdown', 'value'),
     Input('nom-prenom-dropdown', 'value'),
     Input('nom-competition-dropdown', 'value'),
     Input('distance-course-dropdown', 'value'),
     Input('round-name-dropdown', 'value'),
     Input('style-nage-dropdown', 'value'),
     Input('sexe-dropdown', 'value'),
     Input('date-dropdown', 'value')]
)
def update_dropdown_options(nom_prenom_v, competition_nom_v, distance_course_v, epreuve_v, nage_v, sexe_v, date_v):
    #t1 = time.time()
    dff = df.copy()

    # if id_analyse_v:
    #     dff = dff.loc[dff.id_analyse.isin(id_analyse_v)]
    
    # if nom_analyse_v:
    #     dff = dff.loc[dff.nom_analyse.isin(nom_analyse_v)]
        
    if nom_prenom_v:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom_v)]
        
    if competition_nom_v:
        dff = dff.loc[dff.competition_nom.isin(competition_nom_v)]
        
    if distance_course_v:
        dff = dff.loc[dff.distance_course.isin(distance_course_v)]
        
    if epreuve_v:
        dff = dff.loc[dff.round_name.isin(epreuve_v)]
        
    if nage_v:
        dff = dff.loc[dff.style_nage.isin(nage_v)]
        
    if sexe_v:
        dff = dff.loc[dff.nageur_sexe.isin(sexe_v)]
        
    if date_v:
        dff = dff.loc[dff.date.isin(date_v)]
    
    return dash_table.DataTable(
        columns=[{'name': str(column), 'id': str(column)} for column in dff.columns],
        data=dff.iloc[:10000,:].to_dict('records'),
        page_size=10,
        editable=True,
        style_cell={'textAlign': 'center'},
        style_header={
            'backgroundColor': '#FE70AF',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data={
            'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    )


@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv","n_clicks"),
    Input("btn_excel","n_clicks"),
    #Input('id-course-dropdown', 'value'),
    #Input('nom-analyse-dropdown', 'value'),
    Input('nom-prenom-dropdown', 'value'),
    Input('nom-competition-dropdown', 'value'),
    Input('distance-course-dropdown', 'value'),
    Input('round-name-dropdown', 'value'),
    Input('style-nage-dropdown', 'value'),
    Input('sexe-dropdown', 'value'),
    prevent_initial_call=True,
)
def func(btn_csv_clicks, btn_excel_clicks, nom_prenom_v, competition_nom_v, distance_course_v, epreuve_v, nage_v, sexe_v):
    dff = df.copy()
    
    # if id_analyse_v:
    #     dff = dff.loc[dff.id_analyse.isin(id_analyse_v)]
    
    # if nom_analyse_v:
    #     dff = dff.loc[dff.nom_analyse.isin(nom_analyse_v)]
        
    if nom_prenom_v:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom_v)]
        
    if competition_nom_v:
        dff = dff.loc[dff.competition_nom.isin(competition_nom_v)]
        
    if distance_course_v:
        dff = dff.loc[dff.distance_course.isin(distance_course_v)]
        
    if epreuve_v:
        dff = dff.loc[dff.round_name.isin(epreuve_v)]
        
    if nage_v:
        dff = dff.loc[dff.style_nage.isin(nage_v)]
        
    if sexe_v:
        dff = dff.loc[dff.nageur_sexe.isin(sexe_v)]
        
    if "btn_csv" == ctx.triggered_id:
        return dcc.send_data_frame(dff.to_csv, "FFN_app_bdd.csv")
    
    if "btn_excel" == ctx.triggered_id:
        return dcc.send_data_frame(dff.to_excel, "FFN_app_bdd.xlsx", sheet_name="Feuille_1")
    


@callback(
    Output('nom-competition-dropdown', "options"),
    Input('nom-prenom-dropdown',"value"),
)
def update_nom_compet(nom_prenom):
    dff = df.copy()
    if nom_prenom:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom)]
    return [{'label': i, 'value': i} for i in sorted(dff.competition_nom.unique())]

@callback(
    Output('nom-prenom-dropdown', "options"),
    Input('nom-competition-dropdown',"value"),
    Input('date-dropdown',"value"),
    Input('sexe-dropdown', "value")
)
def update_nom_prenom(nom_compet,date,sexe):
    dff = df.copy()
    if nom_compet:
        dff = dff.loc[dff.competition_nom.isin(nom_compet)]
    if date:
        dff = dff.loc[dff.date.isin(date)]
    if sexe:
        dff = dff.loc[dff.nageur_sexe.isin(sexe)]
    return [{'label': i, 'value': i} for i in pd.Series(sorted((dff['nom_prenom']), key=comparer_noms)).unique()]


@callback(
    Output('date-dropdown', "options"),
    Input('nom-prenom-dropdown',"value"),
)
def update_date(nom_prenom):
    dff = df.copy()
    if nom_prenom:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom)]
    return [{'label': i, 'value': i} for i in sorted(dff.date.unique())]


@callback(
    Output('distance-course-dropdown', "options"),
    Input('nom-prenom-dropdown',"value"),
    Input('style-nage-dropdown', "value")
)
def update_distance(nom_prenom,style):
    dff = df.copy()
    if nom_prenom:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom)]
    if style:
        dff = dff.loc[dff.style_nage.isin(style)]   
    return [{'label': i, 'value': i} for i in sorted(dff.distance_course.unique())]


@callback(
    Output('style-nage-dropdown', "options"),
    Input('nom-prenom-dropdown',"value"),
    Input('distance-course-dropdown', "value")
)
def update_style(nom_prenom, distance):
    dff = df.copy()
    if nom_prenom:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom)]
    if distance:
        dff = dff.loc[dff.distance_course.isin(distance)]
    return [{'label': i, 'value': i} for i in sorted(dff.style_nage.unique())]

@callback(
    Output('round-name-dropdown', "options"),
    Input('nom-prenom-dropdown',"value"),
    Input('distance-course-dropdown',"value"),
)
def update_round(nom_prenom,distance):
    dff = df.copy()
    if nom_prenom:
        dff = dff.loc[dff.nom_prenom.isin(nom_prenom)]
    if distance:
        dff = dff.loc[dff.distance_course.isin(distance)]
    return [{'label': i, 'value': i} for i in sorted(dff.round_name.unique())]
