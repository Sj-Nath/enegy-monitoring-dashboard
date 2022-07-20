import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import Dash, callback
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import datetime

dash.register_page(__name__)


def get_em():
    data = pd.read_excel('..\\data\\EM.xlsx')
    data.sort_values(['DATE_TIME'], ascending=True)
    data['Year'] = data['DATE_TIME'].dt.year
    data['Month'] = data['DATE_TIME'].dt.month

    for i in data['Node_Name'].unique():
        data.loc[data['Node_Name'].str.contains(i), 'Last_consumption'] = data.loc[
            data['Node_Name'].str.contains(i), 'Cumm_Power'].diff(-1)
    return data


df = get_em()

gauge = ['Active_Power', 'Average_Apparent_Power', 'Average_Reactive_Power',
         'LL_Average_Voltage', 'LN_Average_Voltage', 'Average_Current',
         'R_Ph_THD_Current', 'Y_Ph_THD_Current', 'B_Ph_THD_Current',
         'L_L_Average_THD_Voltage', 'L_N_Average_THD_Voltage']
card = ['Frequency', 'Average_Power_Factor']


def unit(x):
    if 'Power' in x:
        return 'KW'
    elif 'Voltage' in x:
        return 'Volts'
    elif 'Current' in x:
        return 'Amps'
    else:
        return None


em_P1 = px.histogram(
    data_frame=df.groupby(['Node_Name', 'Year', 'Month'], as_index=False).sum().sort_values('Last_consumption',
                                                                                            ascending=False),
    y='Last_consumption',
    x='Node_Name',
    labels={
        'Node_Name': '<b>Area<b>',
        'Last_consumption': '<b>Power Consumed in KW<b>'})
em_P1.update_layout(
    title='<b>Area-wise Energy consumption<b>',
    title_x=0.5)

em_P2 = px.histogram(
    data_frame=df,
    y='Last_consumption',
    x='DATE_TIME',
    color='Node_Name',
    barmode='group',
    labels={
        'Node_Name': '<b>Area<b>',
        'Last_consumption': '<b>Power Consumed in KW<b>'})
em_P2.update_layout(
    title='<b>Hourly Energy consumption<b>',
    title_x=0.5)
voltage_thd_list = [i for i in df.columns if 'THD_Voltage' in i]
current_thd_list = [i for i in df.columns if 'THD_Current' in i]

pd.options.plotting.backend = "plotly"
em_P3 = df.plot(kind='scatter', x=df['DATE_TIME'], y=voltage_thd_list)
em_P3.layout.template = 'plotly_dark'
em_P4 = df.plot(kind='scatter', x=df['DATE_TIME'], y=current_thd_list)
em_P4.layout.template = 'plotly_dark'

layout = html.Div(children=[
    html.H1('Wooshin Line Energy Monitoring',
            style={'textAlign': 'center', 'color': 'blue'}),
    html.Br(),
    html.H3("Current Energy parameters' parameters", style={'textAlign': 'center', 'color': 'blue'}),
    html.Br(),
    dcc.Dropdown(
        id='select_em',
        value='WSHN LGT DB',
        placeholder='Please select the Energy Meter',
        options=[{'label': i, 'value': i} for i in df.Node_Name.unique()],
        multi=False,
        style={'width': '500px',
               'verticalAlign': 'center',
               'border': '2px black solid'}),
    dcc.Interval(
        id='interval-component',
        interval=1 * 5000,
        n_intervals=0),
    html.Div([dbc.Card(
        dbc.CardBody(
            html.H3(f"{i.replace('_', ' ')} = {df[i][0]}", className="card-title", id="card_num1"))
    ) for i in card]),
    html.Div([
        daq.Gauge(
            id=i,
            value=df[i].mean(),
            label=i.replace('_', ' '),
            units=unit(i),
            showCurrentValue=True,
            max=round(df[i].max()),
            min=round(df[i].min(), 0), style={'width': '16%',
                                              'display': 'inline-block',
                                              "margin-left": "5px",
                                              "margin-top": "5px",
                                              'border': '2px black solid'}) for i in gauge
    ]),
    html.Br(),
    html.H3("Analysis of wooshin EMs' parameters", style={'textAlign': 'center', 'color': 'blue'}),
    html.Br(),
    dcc.DatePickerRange(
        id='em-date-picker-range',
        start_date=df['DATE_TIME'].max().date(),
        end_date=df['DATE_TIME'].max().date(),
        min_date_allowed=df['DATE_TIME'].min().date(),
        max_date_allowed=df['DATE_TIME'].max().date(),
        display_format='DD MM YYYY',
        updatemode='bothdates',
        style={
            'border': '2px black solid'}),
    html.Br(),
    html.H4("Energy consumption Analysis", style={'textAlign': 'center', 'color': 'blue'}),
    dcc.Graph(id='em_wise', figure=em_P1, style={'width': '48%',
                                                 'display': 'inline-block',
                                                 'border': '2px black solid',
                                                 }),
    dcc.Graph(id='node_wise', figure=em_P2, style={'width': '48%',
                                                   'display': 'inline-block',
                                                   'border': '2px black solid',
                                                   "margin-left": "2px"
                                                   }),
    html.Br(),
    html.H4("THD Analysis", style={'textAlign': 'center', 'color': 'blue'}),
    dcc.Dropdown(
        id='select_em_thd',
        value='WSHN LGT DB',
        placeholder='Please select the Energy Meter',
        options=[{'label': i, 'value': i} for i in df.Node_Name.unique()],
        multi=False,
        style={'width': '500px',
               'verticalAlign': 'center',
               'border': '2px black solid'}),

    dcc.Graph(id='voltage_thd', figure=em_P3, style={'width': '48%',
                                                     'display': 'inline-block',
                                                     'border': '2px black solid'}),
    dcc.Graph(id='current_thd', figure=em_P4, style={'width': '48%',
                                                     'display': 'inline-block',
                                                     'border': '2px black solid',
                                                     "margin-left": "2px"})

])


@callback(
    [Output(i, 'value') for i in gauge],
    Input('select_em', 'value'),
    Input('interval-component', 'n_intervals')
)
def gauge_update(em, n):
    df_copy = df.copy()
    df_copy = df_copy[df_copy['Node_Name'].str.contains(em)].reset_index(drop=True)
    val = []
    for i in gauge:
        val.append(float(df_copy[i][0]))
    return val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8], val[9], val[10]


@callback(
    [Output('em_wise', 'figure'),
     Output('node_wise', 'figure'),
     Input('em-date-picker-range', 'start_date'),
     Input('em-date-picker-range', 'end_date')]
)
def em_callbacks(start_date, end_date):
    df_copy = df.copy()
    df_copy = df_copy[(df_copy['DATE_TIME'] >= start_date) &
                      (df_copy['DATE_TIME'] <= end_date)]
    em_P1 = px.histogram(
        data_frame=df_copy.groupby('Node_Name', as_index=False).sum().sort_values('Last_consumption', ascending=False),
        y='Last_consumption',
        x='Node_Name',
        labels={
            'Node_Name': '<b>Area<b>',
            'Last_consumption': '<b>Power Consumed in KW<b>'})
    em_P1.update_layout(
        title='<b>Area-wise Energy consumption<b>',
        title_x=0.5, template='plotly_dark')

    em_P2 = px.histogram(
        data_frame=df_copy,
        y='Last_consumption',
        x='DATE_TIME',
        color='Node_Name',
        barmode='relative',
        labels={
            'Node_Name': '<b>Area<b>',
            'Last_consumption': '<b>Power Consumed in KW<b>'}, template='plotly_dark')

    em_P2.update_layout(
        title='<b>Hourly Energy consumption<b>',
        title_x=0.5,
        bargap=0.3)

    return em_P1, em_P2


@callback(
    [Output('voltage_thd', 'figure'),
     Output('current_thd', 'figure')],
    Input('em-date-picker-range', 'start_date'),
    Input('em-date-picker-range', 'end_date'),
    Input('select_em_thd', 'value')
)
def thd_callbacks(start_date, end_date, thd):
    df_copy = df.copy()
    df_copy = df_copy[(df_copy['DATE_TIME'] >= start_date) &
                      (df_copy['DATE_TIME'] <= end_date) &
                      (df_copy['Node_Name'] == thd)]
    voltage_thd_list = [i for i in df_copy.columns if 'THD_Voltage' in i]
    current_thd_list = [i for i in df_copy.columns if 'THD_Current' in i]

    pd.options.plotting.backend = "plotly"
    em_P3 = df_copy.plot(kind='scatter', x=df_copy['DATE_TIME'], y=voltage_thd_list)
    em_P3.layout.template = 'plotly_dark'
    em_P4 = df_copy.plot(kind='scatter', x=df_copy['DATE_TIME'], y=current_thd_list)
    em_P4.layout.template = 'plotly_dark'
    return em_P3, em_P4
