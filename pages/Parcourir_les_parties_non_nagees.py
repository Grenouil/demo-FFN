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
])