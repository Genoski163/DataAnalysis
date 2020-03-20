#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import getopt
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

if __name__ == "__main__":
    #Задаём входные параметры
    unixOptions = "s:e:"
    gnuOptions = ["start_dt=", "end_dt="]
    
    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:] #excluding script name
    
    try:
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as err:
        print (str(err))
        sys.exit(2)

    start_dt = ''
    end_dt = ''
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-s", "--start_dt"):
            start_dt = currentValue
        elif currentArgument in ("-e", "--end_dt"):
            end_dt = currentValue

    
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
    engine = create_engine(connection_string)
    
    #Теперь выберем из таблицы только те строки,
    #которые были выпущены между start_dt и end_dt
    query = ''' SELECT *
               FROM (SELECT *, TO_TIMESTAMP(ts / 1000) AT TIME ZONE 'Etc/UTC' as dt
                     FROM log_raw) as tt
               WHERE dt::TIMESTAMP BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
        '''.format(start_dt, end_dt)
    
    data_raw = pd.io.sql.read_sql(query, con = engine, index_col = 'event_id')

    columns_str = ['item_topic', 'source_topic', 'age_segment', 'event']
    for column in columns_str: data_raw[column] = data_raw[column].astype(str)


    data_raw['dt'] = pd.to_datetime(data_raw['dt']).dt.round('min')


    # группируем по визитам
    dash_visits = data_raw.groupby(['item_topic', 'source_topic', 'age_segment', 'dt']).agg({'event' : 'count'})
    dash_visits = dash_visits.rename(columns = {'event' : 'visits'})
    
    # группируем по уникальным пользователям
    dash_engagement = data_raw.groupby(['dt', 'item_topic', 'event', 'age_segment']).agg({'user_id' : 'nunique'})
    dash_engagement = dash_engagement.rename(columns = {'user_id' : 'unique_users'})

    dash_visits = dash_visits.fillna(0).reset_index()
    dash_visits['visits'] = pd.to_numeric(dash_visits['visits'] , errors='coerce')
    dash_engagement = dash_engagement.fillna(0).reset_index()
    dash_engagement['unique_users'] = pd.to_numeric(dash_engagement['unique_users'] , errors='coerce')


    tables = {'dash_visits': dash_visits, 
              'dash_engagement': dash_engagement}

    for table_name, table_data in tables.items():   

        query = '''
                  DELETE FROM {} WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
                '''.format(table_name, start_dt, end_dt)
        engine.execute(query)

        table_data.to_sql(name = table_name, con = engine, if_exists = 'append', index = False)

    print('All done.')
