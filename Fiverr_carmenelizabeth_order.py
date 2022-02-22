#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from io import BytesIO
from wordcloud import WordCloud
import base64
import dash.dependencies as dd
import mysql.connector

db = mysql.connector.connect(
    host="localhost",              
    user="root",            
    password="",        
    database="indeed_data_dump"     
)   

cur = db.cursor()
cur.execute("SELECT * FROM jobs")
data = pd.DataFrame(cur.fetchall())
db.close()
data.rename(columns = {1:'Url',2:'Job Link',3:'Title',4:'Company',5:'Rating',6:'Location',
                       7:'Posted',8:'Job Description',9:'Min Salary',10:'Max Salary'}, inplace = True)
data.to_dict()
data = data[data['Max Salary'].notnull()]

jobs_2 = data[['Title','Company','Rating','Location','Max Salary']]
jobs_2['Max Salary'] = jobs_2['Max Salary'].str.replace(',','')
jobs_2['Type'] = jobs_2['Max Salary'].str[-5:]
jobs_2['Type'] = jobs_2['Type'].str.replace(' ','')
jobs_2['Max Salary'] = jobs_2['Max Salary'].str.extract('(\d+)')
jobs_2 = jobs_2.dropna(subset=['Max Salary'])
jobs_2['Max Salary'] = jobs_2['Max Salary'].astype(int)

jobs_2['Max Salary'] = np.where((jobs_2['Type'] == "year"),(jobs_2['Max Salary']/12).round(decimals=0),jobs_2['Max Salary'])
jobs_2['Max Salary'] = np.where((jobs_2['Type'] == "week"),(jobs_2['Max Salary']*4).round(decimals=0),jobs_2['Max Salary'])

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.LUX])
app.layout = html.Div([
        dbc.Row([
        html.Img(src='/assets/clipart1617907.png',style={'height':'12%',
                                                 'width':'12%',
                                                 'position' : 'relative',
                                                 'padding-top' : 10,
                                                 'padding-left' : 10})
        ],style={'textAlign': 'left','padding-left' : 25,'padding-bottom' : 25}),
    
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([html.H5('Average salary on each location',className='text-center'), #marks=mark_values
                    dcc.Graph(id='sal_location',figure={},style={'height':500,'width':'auto'}),
                ])
            ])
        ],width={'size':12,"offset":0,'order':1},style={'padding-left' : 25,'padding-right' : 25}),
    ]),
    html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([html.H5('Top 10 Job',className='text-center'), #marks=mark_values
                    dcc.Graph(id='sal_top10',figure={},style={'height':600,'width':'auto'}),
                ])
            ])
        ],width={'size':6,"offset":0,'order':1},style={'padding-left' : 25}),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([html.H5('Average salary on star',className='text-center'), #marks=mark_values
                    dcc.Graph(id='sal_star',figure={},style={'height':600,'width':'auto'}),
                ])
            ])
        ],width={'size':6,"offset":0,'order':1},style={'padding-right' : 25}),            
    ]),
    html.Hr(),    
        dbc.Row([
            dbc.Col([html.H5('Drop Down',className='text-center'),
               dcc.Dropdown(id='location_cd_2',placeholder="Please select location",
                            options=[{'label':x,'value':x} for x in data.sort_values('Location')['Location'].unique()],
                            value='Select',
                            multi=False,
                            disabled=False,
                            clearable=True,
                            searchable=True),
                    ],width={'size':6,"offset":0,'order':1},style={'padding-left' : 25}),
    ]),    
    html.Hr(),
        dbc.Row([    
            dbc.Col([
                 dbc.Card([
                    dbc.CardBody([html.H5('Job on each location',className='text-center'), #marks=mark_values
                    dcc.Graph(id='job_location_2',figure={},style={'height':600,'width':'auto'}),
                ])
            ])
        ],width={'size':12,"offset":0,'order':1},style={'padding-left' : 25,'padding-right' : 25}),
        
    ]),
        dbc.Row([    
            dbc.Col([
                 dbc.Card([
                    dbc.CardBody([html.H5('Word Cloud',className='text-center'),
                    html.Img(id="image_wc"),
                ])
            ])
        ],width={'size':12,"offset":0,'order':1},style={'padding-left' : 25,'padding-right' : 25},className='text-center'),
        
    ]),
    dcc.Interval(id='update', n_intervals = 0, interval=1000*5)
])
    
@app.callback(
    Output('sal_location', 'figure'),
    [Input('update', 'n_intervals')])

def update_graph(jobs_location):    
    global jobs
    jobs = jobs_2.copy()  
    jobs_location = pd.pivot_table(jobs,values=['Max Salary',],index=['Location'],aggfunc=np.mean)
    jobs_location = jobs_location.reset_index()

    # Fig 1
    fig_1 = go.Figure(data=[
    go.Bar(x=jobs_location['Location'],
           y=jobs_location['Max Salary'].round(decimals=2),
           width=0.45,
           text = jobs_location['Max Salary'].round(decimals=2),
           textposition='inside',
           marker_color='indianred')])
    
    fig_1.update_layout(barmode='stack')
    fig_1.update_traces(texttemplate='%{text:,}')
    fig_1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig_1.update_yaxes(showline=False,showgrid=False,dtick=5000,exponentformat="none",separatethousands=True)
    return fig_1   
   
@app.callback(
    Output('sal_top10', 'figure'),
    [Input('update', 'n_intervals')])   

def update_graph_2(top_10):     
    global job_cloud
    jobs['Rating'].fillna(0,inplace=True)
    jobs_title = pd.pivot_table(jobs,values=['Max Salary',],index=['Title'],aggfunc=np.mean)
    jobs_title = jobs_title.reset_index() 
    top_10 = jobs_title.sort_values(['Max Salary'], ascending=[False]).head(10)
    top_10 = top_10.sort_values(['Max Salary'], ascending=[True])
    job_cloud = jobs.groupby(["Title"])["Title"].count().reset_index(name="count")
    # Fig 3
    fig_3 = px.bar(top_10, x="Max Salary", y="Title", orientation='h')
    fig_3.update_traces(marker_color='#E8788C')
    fig_3.update_layout(plot_bgcolor='white',xaxis_title='',yaxis_title='')
    fig_3.update_yaxes(showline=False,showgrid=False,exponentformat="none",separatethousands=True)
    fig_3.update_xaxes(showline=False,showgrid=False,exponentformat="none",separatethousands=True)
    return fig_3

@app.callback(
    Output('sal_star', 'figure'),
    [Input('update', 'n_intervals')]) 

def update_graph_3(jobs_rating):
    jobs_rating = pd.pivot_table(jobs,values=['Max Salary',],index=['Rating'],aggfunc=np.mean)
    jobs_rating = jobs_rating.reset_index()  
    fig_2 = go.Figure(data=[
    go.Bar(x=jobs_rating['Rating'],
           y=jobs_rating['Max Salary'].round(decimals=2),
           width=0.45,
           text = jobs_rating['Max Salary'].round(decimals=2),
           textposition='inside',
           marker_color='lightsalmon')])
        
    fig_2.update_layout(barmode='stack')
    fig_2.update_traces(texttemplate='%{text:,}')
    fig_2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig_2.update_yaxes(showline=False,showgrid=False,dtick=5000,exponentformat="none",separatethousands=True)
    fig_2.update_xaxes(type='category')
    return fig_2

@app.callback(Output('job_location_2', 'figure'),
             [Input('location_cd_2', 'value'),
              Input('update', 'n_intervals')])

def build_graph(location_code,dff_2):
    if not location_code or 'Select' in location_code:
        dff_2 = pd.pivot_table(jobs,values=['Max Salary',],index=['Location','Title'],aggfunc=np.mean).reset_index()
        dff_2 = dff_2[(dff_2['Location']=='Kuala Lumpur')]
        
    else:
        dff_2 = pd.pivot_table(jobs,values=['Max Salary',],index=['Location','Title'],aggfunc=np.mean).reset_index()
        dff_2 = dff_2[(dff_2['Location'] == location_code)]          
    
    fig_4 = go.Figure(data=[
    go.Bar(x=dff_2['Title'],
           y=dff_2['Max Salary'].round(decimals=2),
           width=0.45,
           text = dff_2['Max Salary'].round(decimals=2),
           textposition='inside',
           marker_color='lightsalmon')])
    
    fig_4.update_layout(barmode='stack')
    fig_4.update_traces(texttemplate='%{text:,}')
    fig_4.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    fig_4.update_yaxes(showline=False,showgrid=False,dtick=20000,exponentformat="none",separatethousands=True)
    fig_4.update_xaxes(type='category')
    return fig_4   
    
def plot_wordcloud(data):
    d = {a: x for a, x in data.values}
    wc = WordCloud(background_color='white', width=1080, height=360)
    wc.fit_words(d)
    return wc.to_image()

@app.callback(dd.Output('image_wc', 'src'), [dd.Input('image_wc', 'id')])
def make_image(b):
    img = BytesIO()
    plot_wordcloud(data=job_cloud).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
   
if __name__ == "__main__":
    app.run_server(debug=False,port=1215)

