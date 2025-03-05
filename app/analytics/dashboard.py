from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import json
from app.models import Fire
from app import db
from sqlalchemy import extract, func
from datetime import datetime

def create_dashboard(server):
    dash_app = Dash(__name__, server=server, url_base_pathname='/analytics/')
    
    # Загрузка GeoJSON карты Казахстана
    with open('app/static/data/kazakhstan.geojson', 'r', encoding='utf-8') as f:
        kz_regions = json.load(f)
    
    # Получаем доступные годы
    available_years = db.session.query(
        extract('year', Fire.date_reported).distinct()
    ).order_by(extract('year', Fire.date_reported)).all()
    
    dash_app.layout = html.Div([
        html.Div([
            # Фильтры
            html.Div([
                dcc.Dropdown(
                    id='year-filter',
                    options=[{'label': str(year[0]), 'value': year[0]} 
                            for year in available_years],
                    value=datetime.now().year,
                    placeholder='Выберите год',
                    className='dropdown'
                ),
                dcc.Dropdown(
                    id='region-filter',
                    options=[{'label': region[0], 'value': region[0]} 
                            for region in REGIONS],
                    placeholder='Выберите регион',
                    className='dropdown'
                )
            ], className='filters-container'),
            
            # Статистика
            html.Div([
                html.Div([
                    html.H3('Всего пожаров'),
                    html.H2(id='total-fires', className='stat-value')
                ], className='stat-box'),
                html.Div([
                    html.H3('Общая площадь (га)'),
                    html.H2(id='total-area', className='stat-value')
                ], className='stat-box'),
                html.Div([
                    html.H3('Общий ущерб (тг)'),
                    html.H2(id='total-damage', className='stat-value')
                ], className='stat-box')
            ], className='stats-container'),
            
            # Карта и графики
            html.Div([
                dcc.Graph(
                    id='region-map',
                    className='map-container',
                    config={'displayModeBar': True}
                ),
                html.Div([
                    dcc.Graph(id='monthly-trend'),
                    dcc.Graph(id='damage-by-region')
                ], className='charts-grid')
            ], className='visualizations-container')
        ], className='dashboard-container')
    ])
    
    @dash_app.callback(
        [Output('region-map', 'figure'),
         Output('monthly-trend', 'figure'),
         Output('damage-by-region', 'figure'),
         Output('total-fires', 'children'),
         Output('total-area', 'children'),
         Output('total-damage', 'children')],
        [Input('year-filter', 'value'),
         Input('region-filter', 'value')]
    )
    def update_dashboard(year, region):
        # Базовый запрос
        query = db.session.query(
            Fire.region,
            Fire.date_reported,
            Fire.area_total,
            Fire.damage,
            func.count(Fire.id).label('fire_count')
        ).group_by(Fire.region, Fire.date_reported, Fire.area_total, Fire.damage)
        
        # Применяем фильтры
        if year:
            query = query.filter(extract('year', Fire.date_reported) == year)
        if region:
            query = query.filter(Fire.region == region)
            
        results = query.all()
        
        # Подготовка данных
        df = pd.DataFrame([{
            'region': r.region,
            'date': r.date_reported,
            'area': r.area_total,
            'damage': r.damage,
            'count': r.fire_count
        } for r in results])
        
        # Карта регионов
        map_data = df.groupby('region').agg({
            'area': 'sum',
            'damage': 'sum',
            'count': 'sum'
        }).reset_index()
        
        map_fig = px.choropleth_mapbox(
            map_data,
            geojson=kz_regions,
            locations='region',
            featureidkey='properties.name',
            color='area',
            hover_data=['count', 'damage'],
            color_continuous_scale='Viridis',
            mapbox_style='carto-positron',
            zoom=3,
            center={'lat': 48.0196, 'lon': 66.9237},
            labels={
                'area': 'Площадь (га)',
                'count': 'Количество пожаров',
                'damage': 'Ущерб (тг)'
            }
        )
        
        # График по месяцам
        df['month'] = df['date'].dt.strftime('%Y-%m')
        monthly_data = df.groupby('month').agg({
            'count': 'sum',
            'area': 'sum'
        }).reset_index()
        
        monthly_fig = go.Figure(data=[
            go.Bar(name='Количество', y=monthly_data['count'], x=monthly_data['month']),
            go.Scatter(name='Площадь', y=monthly_data['area'], x=monthly_data['month'],
                      yaxis='y2', mode='lines+markers')
        ])
        
        monthly_fig.update_layout(
            title='Динамика пожаров по месяцам',
            yaxis=dict(title='Количество пожаров'),
            yaxis2=dict(title='Площадь (га)', overlaying='y', side='right')
        )
        
        # График ущерба
        damage_fig = px.bar(
            map_data,
            x='region',
            y='damage',
            title='Материальный ущерб по регионам',
            labels={'damage': 'Ущерб (тг)', 'region': 'Регион'}
        )
        
        # Общие показатели
        total_fires = f"{int(map_data['count'].sum()):,}".replace(',', ' ')
        total_area = f"{map_data['area'].sum():,.2f}".replace(',', ' ')
        total_damage = f"{map_data['damage'].sum():,.0f}₸".replace(',', ' ')
        
        return map_fig, monthly_fig, damage_fig, total_fires, total_area, total_damage
    
    return dash_app