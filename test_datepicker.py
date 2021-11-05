# test_datepicker

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
from datetime import datetime as dt
import dash

lst_str_cols = ['BR_CD']
dict_dtypes = {x : 'str'  for x in lst_str_cols}
df = pd.read_excel('https://github.com/hoatranobita/test_datepicker/blob/main/MD6200(20150101_20201231)_2%20(1).xlsx?raw=true')
df['ISSUE_DATE_2'] = df['ISSUE_DATE']
df['ISSUE_DATE'] = pd.to_datetime(df['ISSUE_DATE'],infer_datetime_format=True,errors='coerce')
df.set_index('ISSUE_DATE',inplace=True)
    
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.LUX])
    
branches = df['BR_CD'].unique().tolist()
customers = df['CIF'].unique().tolist()
    
app.layout = html.Div([
        dbc.Row([
        dbc.Col([html.H5('Date Picker',className='text-center'),
        dcc.DatePickerRange(
            id='my-date-picker-range',  # ID to be used for callback
            calendar_orientation='horizontal',  # vertical or horizontal
            day_size=39,  # size of calendar image. Default is 39
            end_date_placeholder_text="Return",  # text that appears when no end date chosen
            with_portal=False,  # if True calendar will open in a full screen overlay portal
            first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
            reopen_calendar_on_clear=True,
            is_RTL=False,  # True or False for direction of calendar
            clearable=True,  # whether or not the user can clear the dropdown
            number_of_months_shown=1,  # number of months shown when calendar is open
            min_date_allowed=dt(2015, 1, 1),  # minimum date allowed on the DatePickerRange component
            max_date_allowed=dt.today(),  # maximum date allowed on the DatePickerRange component
            initial_visible_month=dt.today(),  # the month initially presented when the user opens the calendar
            #end_date_placeholder_text='DD-MM-YYYY',
            start_date=dt(2015, 1, 1).date(),
            end_date=dt.today().date(),
            display_format='DDMMYYYY',  # how selected dates are displayed in the DatePickerRange component.
            month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
            minimum_nights=0,  # minimum number of days between start and end date
            persistence=True,
            persisted_props=['start_date'],
            persistence_type='session',  # session, local, or memory. Default is 'local'
            updatemode='singledate'  # singledate or bothdates. Determines when callback is triggered
        )],width={'size':4,"offset":0,'order':1}),
        
        dbc.Col([html.H5('Branch Code',className='text-center'),
        dcc.Dropdown(
                id='filter_dropdown',placeholder="Please select branch code",
                options=[{'label':br, 'value':br} for br in branches],
                value = [],
                multi=True,
                disabled=False,
                clearable=True,
                searchable=True)],width={'size':2,"offset":0,'order':1}),

                    dbc.Col([html.H5('Branch Code',className='text-center'),
        dcc.Dropdown(
                id='filter_dropdown_2',placeholder="Please select customer code",
                options=[{'label':cu, 'value':cu} for cu in customers],
                value = [],
                multi=True,
                disabled=False,
                clearable=True,
                searchable=True)],width={'size':2,"offset":0,'order':1}),
        ]),
            
        dbc.Row([    
        dbc.Col([html.H5('Disbursement List',className='text-center'),
        dash_table.DataTable(
                id='table-container',data=[],
                columns=[{"name":i,"id":i,'type':'numeric'} for i in df.columns],
                style_table={'overflow':'scroll','height':500},
                style_cell={'textAlign':'center'})
                ],width={'size':12,"offset":0,'order':1})
            ])    
            ])

@app.callback(Output('table-container', 'data'),
             [Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('filter_dropdown', 'value'),
              Input('filter_dropdown_2', 'value'),])
def update_data(selected_start_date, selected_end_date, selected_branches,selected_customers):
    # filter the data frame based on the DatePickerRange selection
    data = df[(df.index >= selected_start_date) & (df.index <= selected_end_date)]
    # filter the data frame based on the Dropdown selection
    if selected_branches != []:
        data = data[data['BR_CD'].isin(selected_branches)]
    elif selected_customers != []:
        data = data[data['CIF'].isin(selected_customers)]
    return data.to_dict(orient='records')

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False,port=8051)
