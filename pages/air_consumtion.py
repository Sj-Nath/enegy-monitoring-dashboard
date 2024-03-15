import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import Dash, callback
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import datetime
import os
dash.register_page(__name__)

path  = os.getcwd()
file = 'vfd.csv'
df = pd.read_csv(os.path.join(path,'data','Air_con.csv'))

df['Date_Time'] = pd.to_datetime(df['Date_Time'])
df.sort_values('Date_Time', ascending=False, inplace=True)


def shift_assign(x):
    if datetime.time(5, 45, 0) < x.time() < datetime.time(14, 20, 0):
        return 'A'
    elif datetime.time(14, 20, 0) < x.time() < datetime.time(22, 40, 0):
        return 'B'
    elif not (not (datetime.time(22, 40, 0) < x.time() < datetime.time(23, 59, 0)) and not (
            datetime.time(00, 00, 0) < x.time() < datetime.time(5, 45, 0))):
        return 'C'


df['Shift'] = df['Date_Time'].apply(shift_assign)

fig1 = px.line(data_frame=df, x='Date_Time', y='Flow_Rate', text='Flow_Rate')
fig1.update_traces(textposition='bottom right')
fig1.update_layout({'title': 'Flow Rate W.R.T Time'})
fig2 = px.pie(data_frame=df, names='Shift', values='Consumption')
fig2.update_layout({'title': 'Shift-wise % consumption'})
fig3 = px.bar(data_frame=df, x='Date_Time', y='Consumption')
fig3.update_layout({'title': 'Air Consumption W.R.T. Time'})
fig4 = go.Figure(data=[go.Table(header=dict(values=['Date_Time', 'Flow_Rate', 'Consumption']),
                                cells=dict(values=[df.head(10).Date_Time, df.head(10).Flow_Rate,
                                                   df.head(10).Consumption]))
                       ])

layout = html.Div(children=[
    html.H1('Plant Airflow Data',
            style={'textAlign': 'center', 'color': 'blue'}),
    html.Label('Please select date range here: ', style={'color': 'white'}),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        start_date=df['Date_Time'].max().date(),
        end_date=df['Date_Time'].max().date(),
        start_date_placeholder_text='Start date',
        end_date_placeholder_text='End date',
        min_date_allowed=df['Date_Time'].min().date(),
        max_date_allowed=df['Date_Time'].max().date(),
        display_format='DD MM YYYY',
        updatemode='bothdates',
        style={'background-color': 'blue',

               'border': '2px black solid'}),
    html.Div([
        dcc.Graph(id='1', figure=fig1,
                  style={'width': '65%',
                         'display': 'inline-block',
                         'border': '2px black solid'}),
        dcc.Graph(id='2', figure=fig2,
                  style={'width': '30%',
                         'display': 'inline-block',
                         'border': '2px black solid'}),
        dcc.Graph(id='3', figure=fig3,
                  style={'width': '50%',
                         'display': 'inline-block',
                         'border': '2px black solid'}),
        dcc.Graph(id='4', figure=fig4,
                  style={'width': '45%',
                         'display': 'inline-block',
                         'border': '2px black solid'})
    ])

])


@callback([Output('1', 'figure'),
           Output('2', 'figure'),
           Output('3', 'figure')],
          Input('my-date-picker-range', 'start_date'),
          Input('my-date-picker-range', 'end_date'))
def year_wise(start_date, end_date):
    df_copy = df.copy()
    df_copy = df_copy[(df_copy['Date_Time'] >= start_date) & (df_copy['Date_Time'] <= end_date)]

    fig1 = px.line(data_frame=df_copy, x='Date_Time', y='Flow_Rate', text='Flow_Rate',)
    fig1.update_traces(textposition='bottom right')
    fig1.update_layout({'title': 'Flow Rate W.R.T Time'})
    fig2 = px.pie(data_frame=df_copy, names='Shift', values='Consumption')
    fig2.update_layout({'title': 'Shift-wise % consumption'})
    fig3 = px.bar(data_frame=df_copy, x='Date_Time', y='Consumption', text='Consumption',)
    fig3.update_layout({'title': 'Air Consumption W.R.T. Time'})
    return fig1, fig2, fig3
