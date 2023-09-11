# import dash
# import dash_bootstrap_components as dbc
# from dash import dcc, html, callback, Input, Output, State, dash_table, ctx
# import plotly.express as px
# import pandas as pd
# import numpy as np
# import base64
# import io

# dash.register_page(__name__)

# df = pd.read_csv("C:/Users/33647/Documents/INSA/Stages/Stage FFN 5A/Début stage/DASH analyses de courses/100m_NL_Dames_Frq_Amp_inst.csv",sep = ",",header=0, decimal = ",", encoding='latin-1')
# df = df.rename(columns={'round': 'round_name'})

# def comparer_noms(nom):
#     return nom.split()[-1]

# layout = dbc.Container([
#     dbc.Row(
#         dbc.Col(
#                 html.H3(children='Visualisation des données brutes'),
#                 width={"size": 6, "offset": 3}, style={"fontSize": 30, "textAlign": 'center'}
#             )
#     ),
    
#     html.Br(),
    
    
#     dbc.Row([
#         dbc.Col([
#             html.Div(id_analyse_drop := dcc.Dropdown([x for x in sorted(df.id_analyse.unique())], placeholder="ID analyse", multi=True))
#         ], width=3),
#         dbc.Col([
#             html.Div(nom_analyse_drop := dcc.Dropdown([x for x in sorted(df.nom_analyse.unique())], placeholder="Nom analyse", multi=True))
#         ], width=5),
#         dbc.Col([
#             html.Div(nom_prenom_drop := dcc.Dropdown([x for x in pd.Series(sorted((df['nom_prenom']), key=comparer_noms)).unique()], placeholder="Nom et prénom du nageur", multi=True))
#         ], width=3)
#     ]),
    
#     dbc.Row([
#         dbc.Col([
#             html.Div(competition_nom_drop := dcc.Dropdown([x for x in sorted(df.competition_nom.unique())], placeholder="Nom de la compétition", multi=True))
#         ], width=3),
#         dbc.Col([
#             html.Div(distance_course_drop := dcc.Dropdown([x for x in sorted(df.distance_course.unique())], placeholder="Distance", multi=True))
#         ], width=3),
#         dbc.Col([
#             html.Div(epreuve_drop := dcc.Dropdown([x for x in sorted(df.round_name.unique())], placeholder="Epreuve", multi=True))
#         ], width=3),
#         dbc.Col([
#             html.Div(nage_drop := dcc.Dropdown([x for x in sorted(df.style_nage.unique())], placeholder="Nage", multi=True))
#         ], width=3),

#     ], justify="between", className='mt-3 mb-4'),
    
#     bdd_table := dash_table.DataTable(
#         columns=[
#             {'name': 'ID analyse', 'id': 'id_analyse', 'type': 'numeric'},
#             {'name': 'Nom analyse', 'id': 'nom_analyse', 'type': 'text'},
#             {'name': 'Nom et prénom du nageur', 'id': 'nom_prenom', 'type': 'text'},
#             {'name': 'Nom de la compétition', 'id': 'competition_nom', 'type': 'text'},
#             {'name': 'Distance', 'id': 'distance_course', 'type': 'numeric'},
#             {'name': 'Epreuve', 'id': 'round_name', 'type': 'text'},
#             {'name': 'Nage', 'id': 'style_nage', 'type': 'text'},
#             {'name': 'Temps final', 'id': 'temps_final', 'type': 'numeric'},
#             {'name': 'ID cycle', 'id': 'id_cycle', 'type': 'numeric'},
#             {'name': 'Temps', 'id': 'temps', 'type': 'numeric'},
#             {'name': 'Distance', 'id': 'distance', 'type': 'numeric'},
#             {'name': 'Fréquence instantanée', 'id': 'frequence_instantanee', 'type': 'numeric'},
#             {'name': 'Amplitude instantanée', 'id': 'amplitude_instantanee', 'type': 'numeric'},
#         ],
#         data=df.to_dict('records'),
#         filter_action='native',
#         page_size=10,
        
#         style_cell={'textAlign': 'center'},

#         style_data={
#             'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
#             'overflow': 'hidden',
#             'textOverflow': 'ellipsis',
#         }
#     ),
    
#     html.Br(),
    
#     dbc.Row([
#         dbc.Col([
#             html.Button("Télécharger la base de données sous format .csv", id="btn_csv"),
#             dcc.Download(id="download-dataframe-csv"),
#         ], width={"size": 'auto'}),
#         dbc.Col([
#             html.Button("Télécharger la base de données sous format .xlsx", id="btn_excel"),
#             dcc.Download(id="download-dataframe-xlsx"),
#         ],  width={"size": 'auto', "offset": 0})
        
        
        
#     ])

# ])
        
# @callback(
#     Output(bdd_table, 'data'),
#     Input(id_analyse_drop, 'value'),
#     Input(nom_analyse_drop, 'value'),
#     Input(nom_prenom_drop, 'value'),
#     Input(competition_nom_drop, 'value'),
#     Input(distance_course_drop, 'value'),
#     Input(epreuve_drop, 'value'),
#     Input(nage_drop, 'value')
# )
# def update_dropdown_options(id_analyse_v, nom_analyse_v, nom_prenom_v, competition_nom_v, distance_course_v, epreuve_v, nage_v):
#     dff = df.copy()
    
#     if id_analyse_v:
#         dff = dff[dff.id_analyse.isin(id_analyse_v)]
#     if nom_analyse_v:
#         dff = dff[dff.nom_analyse.isin(nom_analyse_v)]
#     if nom_prenom_v:
#         dff = dff[dff.nom_prenom.isin(nom_prenom_v)]
#     if competition_nom_v:
#         dff = dff[dff.competition_nom.isin(competition_nom_v)]
#     if distance_course_v:
#         dff = dff[dff.distance_course.isin(distance_course_v)]
#     if epreuve_v:
#         dff = dff[dff.round_name.isin(epreuve_v)]
#     if nage_v:
#         dff = dff[dff.nage.isin(nage_v)]

#     return (dff.to_dict('records'))


# @callback(
#     Output("download-dataframe-csv", "data"),
#     Input("btn_csv","n_clicks"),
#     Input(id_analyse_drop, 'value'),
#     Input(nom_analyse_drop, 'value'),
#     Input(nom_prenom_drop, 'value'),
#     Input(competition_nom_drop, 'value'),
#     Input(distance_course_drop, 'value'),
#     Input(epreuve_drop, 'value'),
#     Input(nage_drop, 'value'),
#     prevent_initial_call=True,
# )
# def func(n_clicks, id_analyse_v, nom_analyse_v, nom_prenom_v, competition_nom_v, distance_course_v, epreuve_v, nage_v):
#     dff = df.copy()
    
#     if id_analyse_v:
#         dff = dff[dff.id_analyse.isin(id_analyse_v)]
#     if nom_analyse_v:
#         dff = dff[dff.nom_analyse.isin(nom_analyse_v)]
#     if nom_prenom_v:
#         dff = dff[dff.nom_prenom.isin(nom_prenom_v)]
#     if competition_nom_v:
#         dff = dff[dff.competition_nom.isin(competition_nom_v)]
#     if distance_course_v:
#         dff = dff[dff.distance_course.isin(distance_course_v)]
#     if epreuve_v:
#         dff = dff[dff.round_name.isin(epreuve_v)]
#     if nage_v:
#         dff = dff[dff.nage.isin(nage_v)]
        
#     if "btn_csv" == ctx.triggered_id:
#         return dcc.send_data_frame(dff.to_csv, "FFN_app_bdd.csv")
    
    

# @callback(
#     Output("download-dataframe-xlsx", "data"),
#     Input("btn_excel","n_clicks"),
#     Input(id_analyse_drop, 'value'),
#     Input(nom_analyse_drop, 'value'),
#     Input(nom_prenom_drop, 'value'),
#     Input(competition_nom_drop, 'value'),
#     Input(distance_course_drop, 'value'),
#     Input(epreuve_drop, 'value'),
#     Input(nage_drop, 'value'),
#     prevent_initial_call=True,
# )
# def func(n_clicks, id_analyse_v, nom_analyse_v, nom_prenom_v, competition_nom_v, distance_course_v, epreuve_v, nage_v):
#     dff = df.copy()
    
#     if id_analyse_v:
#         dff = dff[dff.id_analyse.isin(id_analyse_v)]
#     if nom_analyse_v:
#         dff = dff[dff.nom_analyse.isin(nom_analyse_v)]
#     if nom_prenom_v:
#         dff = dff[dff.nom_prenom.isin(nom_prenom_v)]
#     if competition_nom_v:
#         dff = dff[dff.competition_nom.isin(competition_nom_v)]
#     if distance_course_v:
#         dff = dff[dff.distance_course.isin(distance_course_v)]
#     if epreuve_v:
#         dff = dff[dff.round_name.isin(epreuve_v)]
#     if nage_v:
#         dff = dff[dff.nage.isin(nage_v)]
            
#     if "btn_excel" == ctx.triggered_id:
#         return dcc.send_data_frame(dff.to_excel, "FFN_app_bdd.xlsx", sheet_name="Feuille_1")
    


################################ UTILE ##################################
#df_data_parties_nagees = df.copy()
# df = pd.read_csv("C:/Users/33647/Documents/INSA/Stages/Stage FFN 5A/Début stage/DASH analyses de courses/Freq_amp_base_entiere.csv",sep = ",",header=0, decimal = ",", encoding='latin-1')
# df = df.rename(columns={'round': 'round_name'})
# df = df.dropna(subset=['nom_prenom'])
# sub_dataframes = {}
# for name in set(df['id_analyse']):
#     sub_dataframes[name] = df[df['id_analyse'] == name]
# for name, sub_df in sub_dataframes.items():
#     first_row = sub_df.iloc[0]  # Accéder à la première ligne du DataFrame
#     sub_df.loc[:, 'temps_final'] = np.repeat(first_row['temps_final'], len(sub_df))

# df = pd.concat(sub_dataframes.values(), ignore_index=True)
# df = df.drop(df[df['competition_nom'].isin(['Francilly', '43 TROFEU ALEJANDRO LOPEZ', 'Golden FFN Tour Marseille', 'MEETING NATIONAL TOULOUSE'])].index)
# df = df.drop(df[df['distance_course'].isin(['4x100 4N Mixte', '4x100 NL Mixte', '4x100', '4x200', '4x200 NL Mixte', '4x50 4N Mixte', '4x50 NL Mixte'])].index)

# Fonction pour extraire les années d'une chaîne de caractères
# def extract_years(text):
#     pattern = r'\b\d{4}\b'  # Motif regex pour trouver une année de 4 chiffres
#     years = re.findall(pattern, text)
#     return years
# # Appliquer la fonction extract_years à la colonne "competition_nom"
# df['annees'] = df['competition_nom'].apply(extract_years)
# # Extraire les années de la colonne df['annees']
# annees = list(flatten(df['annees']))
# df['annees'] = np.array([int(element) for element in annees])
# df['id_analyse'] = np.array([int(dist) for dist in df['id_analyse']])
# df['id_cycle'] = np.array([float(cycle) for cycle in df['id_cycle']])
# df['distance_course'] = np.array([int(dist) for dist in df['distance_course']])
# df['temps'] = np.array([float(temps) for temps in df['temps']])
# df['temps_final'] = np.array([float(temps_final) for temps_final in df['temps_final']])
# df['distance'] = np.array([float(distance) for distance in df['distance']])
# df['frequence_instantanee'] = np.array([float(freq) for freq in df['frequence_instantanee']])
# df['amplitude_instantanee'] = np.array([float(ampl) for ampl in df['amplitude_instantanee']])


 # Créer la table avec les nouvelles données
    # bdd_table = dash_table.DataTable(
    #     id='bdd_table',
    #     columns=[{'name': str(column), 'id': str(column)} for column in dff.columns],
    #     data=dff.to_dict('records'),
    #     filter_action='native',
    #     page_size=10,
    #     style_cell={'textAlign': 'center'},
    #     style_header={
    #         'backgroundColor': 'black',
    #         'color': 'white',
    #         'fontWeight': 'bold'
    #     },
    #     style_data={
    #         'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
    #         'overflow': 'hidden',
    #         'textOverflow': 'ellipsis',
    #     }
    # )

    # return bdd_table.to_dict('records')



   
    #     fig_clust = go.Figure()
        #df_test = clustering[['Clusters','Temps']]
        # dict_fig = {}
        # for clust in clustering.Clusters.unique():
        #     df_clust = clustering.loc[clustering.Clusters == clust].copy().reset_index(drop=True)
        #     fig_clust = go.Figure()
        #     for i in range(len(df_clust)):
        #         df_race = pd.DataFrame()
        #         liste_points_GP = df_clust.iloc[i,:100]
        #         df_race = pd.concat([df_race,pd.Series(X_echantillon),pd.Series(liste_points_GP)], axis=1)
        #         df_race.columns=['X_echantillon','Points_GP']
        #         fig_clust.add_trace(go.Scatter(x=df_race['X_echantillon'], y=df_race['Points_GP'], mode='lines', name=df_clust.loc[i,'Course']))
        #     dict_fig[f'fig{clust}'] = fig_clust
        
    
    #return tuple([dict_fig[f'fig{k}'] for k in range(1,len(dict_fig.keys())+1)])
    
    # else:
    #     return None
    #,hue='Clusters',dodge=False,palette="turbo",fliersize=3)
        # sns.boxplot(data=df_points_gp,x='Clusters',y='Temps',hue='Clusters',dodge=False,palette="turbo",fliersize=3)
        
        # return clustering  
        
        
        
########### Tri BDD par section ##############

# dff['TEMPS_SECTION_list'] = dff['TEMPS_SECTION'].str.split(';')
        # # Obtenez la liste de toutes les listes de floats
        # temps_section_lists = dff['TEMPS_SECTION_list'].tolist()
        
        # dff_2 = dff.loc[:,['id_analyse','TEMPS_SECTION_list']].copy()
        # # Trouvez la longueur maximale parmi les listes
        # max_length = max(len(lst) for lst in temps_section_lists)
        # # Créez un tableau numpy vide pour stocker les listes alignées
        # aligned_temps_section_lists = np.full((len(temps_section_lists), max_length), np.nan)

        # # Parcourez chaque liste de temps et copiez-la dans le tableau numpy aligné
        # for i, temps_list in enumerate(temps_section_lists):
        #     aligned_temps_section_lists[i, :len(temps_list)] = temps_list

        # # Créez un nouveau DataFrame à partir du tableau numpy aligné
        # dff_temps_sections = pd.DataFrame(aligned_temps_section_lists, columns=col)
        # dff_temps_sections['id_analyse'] = dff_2['id_analyse']
        
        # # Concaténez le nouveau DataFrame avec le DataFrame d'origine
        # dff = dff.merge(dff_temps_sections, how = "outer", on = "ref")