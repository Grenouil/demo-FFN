import dash
from dash import Input, Output, State, html, dcc, dash_table
import pandas as pd


# Créez votre application Dash
app = dash.Dash(__name__)

# Exemple de DataFrame
df = pd.DataFrame({
    'Name': ['John', 'Jane', 'Bob', 'Alice'],
    'Age': [25, 30, 22, 28],
    'City': ['New York', 'Paris', 'London', 'Tokyo']
})

# Définissez votre mise en page
app.layout = html.Div([
    dcc.Dropdown(
        id='name-dropdown',
        options=[{'label': name, 'value': name} for name in df['Name'].unique()],
        # value=df['Name'].unique(),
        multi=True  # Permet la sélection de plusieurs noms
    ),
    dash_table.DataTable(
        id='table',
        columns=[{'name': str(column), 'id': str(column)} for column in df.columns],
        page_size=20,
        editable=True,
        row_selectable='multi',
        selected_rows=[],
        style_cell={'textAlign': 'center'},
        style_header={
            'backgroundColor': 'darkturquoise',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data={
            'width': '100px', 'minWidth': '100px', 'maxWidth': '100px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),
    html.Div(id='selected-rows')  # Affiche les indices des lignes sélectionnées
])

# Callback pour mettre à jour la table de données en fonction de la sélection du dropdown
@app.callback(
    Output('table', 'data'),
    [Input('name-dropdown', 'value')]
)
def update_table(selected_names):
    dff = df[df['Name'].isin(selected_names)]
    return dff.to_dict('records')

# Callback pour afficher les indices des lignes sélectionnées
@app.callback(
    Output('selected-rows', 'children'),
    [Input('table', 'selected_rows')],
    [State('table', 'data')]
)
def display_selected_rows(selected_rows, data):
    if selected_rows:
        return f"Lignes sélectionnées : {selected_rows}"
    return "Aucune ligne sélectionnée"

# Exécutez l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)
