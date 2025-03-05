def create_dashboard(server):
    dash_app = Dash(__name__, server=server, url_base_pathname='/analytics/')
    
    dash_app.layout = html.Div([
        dcc.Dropdown(
            id='year-filter',
            options=[{'label': str(year), 'value': year} 
                    for year in range(2023, 2025)],
            value=2024
        ),
        
        html.Div([
            dcc.Graph(id='fire-map'),
            dcc.Graph(id='monthly-trend'),
            dcc.Graph(id='damage-by-region')
        ])
    ])