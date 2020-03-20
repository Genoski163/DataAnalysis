#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

from datetime import datetime

import pandas as pd

# задаём данные для отрисовки
from sqlalchemy import create_engine

db_config = {'user': 'my_user',
                 'pwd': 'my_user_password',
                 'host': 'localhost',
                 'port': 5432,
                 'db': 'zen'}   

connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                             db_config['pwd'],
                                                             db_config['host'],
                                                             db_config['port'],
                                                             db_config['db'])                 

    #запрашиваем сырые данные
engine = create_engine(connection_string)    

query = '''
        select * from dash_visits
        '''

dash_visits = pd.io.sql.read_sql(query, con = engine)
dash_visits['dt'] = pd.to_datetime(dash_visits['dt'])

query1 = '''
         select * from dash_engagement
         '''
dash_engagement = pd.io.sql.read_sql(query1, con = engine)
dash_engagement['dt'] = pd.to_datetime(dash_engagement['dt'])

note = '''
         Этот дашборд показывает историю событий по темам карточек, разбивку событий по темам источников и глубину взаимодействия пользователей с карточками.
         Используйте выбор интервала даты и времени истории событий по темам карточек и интервал возрастных категорий для управления дашбордом.
         Используйте выбор тем карточек для анализа графика разбивки событий по темам источников.
      '''


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[  

    # формируем html
    html.H1(children = 'Анализ взаимодействия пользователей с карточками'),

    html.Label(note),

    html.Br(),    

    html.Div([    

        html.Div([         
            # выбор платформы
            html.Label('Платформы:'),
            dcc.Dropdown(
                options = [{'label': x, 'value': x} for x in dash_visits['item_topic'].unique()],
                value = dash_visits['item_topic'].unique().tolist(),
                multi = True,
                id = 'item_topic_dropdown'
            ),                
        ], className = 'six columns'),

        html.Div([    
            # Возрастная группа
            html.Label('Возрастная группа:'),
            dcc.Dropdown(
                options = [{'label': x, 'value': x} for x in dash_visits['age_segment'].unique()],
                value = dash_visits['age_segment'].unique().tolist(),
                multi = True,
                id = 'age_dropdown'
            ),                   
        ], className = 'six columns'),  

        html.Div([
            # выбор временного периода
            html.Label('Выбор временного периода:'),
            dcc.DatePickerRange(
                start_date = dash_visits['dt'].dt.date.min(),
                end_date = '2019-09-25',
                display_format = 'YYYY-MM-DD',
                id = 'dt_selector',       
            ),
        ], className = 'six columns'),
            ], className = 'row'),

    html.Br(),  

    html.Div([
        html.Div([

            # График событий во времени
            html.Label('График событий во времени:'),    
       
            dcc.Graph(
                style = {'height': '50vw'}, 
                id = 'history_absolute_visits'
            ),  
        ], className = 'six columns'),            

        html.Div([
            # Круговая диаграмма событий
             html.Label('Круговая диаграмма событий:'),
             dcc.Graph(
                style = {'height': '25vw'},
                id = 'pie_visits'
            ),     
        ], className = 'six columns'),

        html.Div([

            # Столбчатая диаграмма глубины взаимодействия
            html.Label('Столбчатая диаграмма глубины взаимодействия:'),    
        
            dcc.Graph(
                style = {'height': '25vw'},
                id = 'engagement_graph'
            ),  
        ], className = 'six columns'),            
    ], className = 'row'),

   
])

# описываем логику дашборда
@app.callback(
    [Output('history_absolute_visits', 'figure'),
     Output('pie_visits', 'figure'),
     Output('engagement_graph', 'figure'),
    ],
    [Input('item_topic_dropdown', 'value'),
     Input('age_dropdown', 'value'),
     Input('dt_selector', 'start_date'),
     Input('dt_selector', 'end_date'),
    ])
def update_figures(selected_item_topics, selected_ages, start_date, end_date):

      #применяем фильтрацию
      filtered = dash_visits.query('item_topic.isin(@selected_item_topics)')
      filtered = filtered.query('age_segment.isin(@selected_ages)')
      filtered = filtered.query('dt >= @start_date and dt <= @end_date')

      filtered_eng = dash_engagement.query('item_topic.isin(@selected_item_topics)')
      filtered_eng = filtered_eng.query('age_segment.isin(@selected_ages)')
      filtered_eng = filtered_eng.query('dt >= @start_date and dt <= @end_date')

      by_item_topic = (filtered.groupby(['item_topic', 'dt'])
                                .agg({'visits': 'sum'})
                                .reset_index()
                          )

      by_source_topic = (filtered.groupby(['source_topic'])
                                   .agg({'visits': 'sum'})
                                   .reset_index()
                          )

      by_unique_users = (filtered_eng.groupby(['event'])
                                   .agg({'unique_users': 'mean'})
                                   .reset_index()
                          )
      by_unique_users['unique_users'] = by_unique_users['unique_users'].astype(int)
      total = by_unique_users.query('event == "show"')['unique_users'].sum()
      by_unique_users['persent'] = ((by_unique_users['unique_users'] / total) * 100).round(1)
      by_unique_users = by_unique_users.sort_values(by = 'persent', ascending = False)


      data_by_item_topic = []
      for item_topic in by_item_topic['item_topic'].unique():
        data_by_item_topic += [go.Scatter(x = by_item_topic.query('item_topic == @item_topic')['dt'],
                                   y = by_item_topic.query('item_topic == @item_topic')['visits'],
                                   mode = 'lines',
                                   stackgroup = 'one',
                                   name = item_topic)]

      data_by_source_topic = [go.Pie(labels = by_source_topic['source_topic'],
                                    values = by_source_topic['visits'],
                                    name = 'source_topics')]

      data_by_unique_users = [go.Bar(x = by_unique_users['event'],
                                    y = by_unique_users['persent'],
                                    text=by_unique_users['persent'],
                                    textposition='auto',
                                     name = 'by_source_topic')]


      #формируем результат для отображения
      return (
                {
                    'data': data_by_item_topic,
                    'layout': go.Layout(xaxis = {'title': 'Дата'},
                                        yaxis = {'title': 'Визиты'})
                 },           
                {
                    'data': data_by_source_topic,
                    'layout': go.Layout()
                 },
                {
                    'data': data_by_unique_users,
                    'layout': go.Layout(xaxis = {'title': 'Событие'},
                                        yaxis = {'title': 'Cредний % от показов'})
                 },             

      )  

if __name__ == '__main__':
    app.run_server(debug = True, host='0.0.0.0')