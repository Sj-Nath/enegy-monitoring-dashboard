import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import Dash, callback
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_daq as daq
import datetime

dash.register_page(__name__)

path  = os.getcwd()
file = 'vfd.csv'
df = pd.read_csv(os.path.join(path,'data','vfd.csv'))

df['Date_Time'] = pd.to_datetime(df['Date_Time'])
df = df.sort_values('Date_Time').reset_index(drop=True)
df['Node_Name'] = df['Node_Name'].str.strip()

for i in df['Node_Name'].unique():
    df.loc[df['Node_Name'].str.contains(i), 'Last_consumption'] = df.loc[
        df['Node_Name'].str.contains(i), 'Energy_Meter_KWH'].diff(-1)

df.drop(['Master_ID', 'Node_ID', 'Energy_Meter_MWH', 'Adjustable_OverCurrent_Level',
         'UnderCurrent_Level', 'Output_Current_level', 'Earth_Fault_Detection_Level',
         'Run_Time_Hrs', 'Energy_Saved_KWH'], inplace=True, axis=1)

I_u = go.Scatter(x=df['Date_Time'], y=df['Output_Current_U'], name='U phase o/p current')
I_v = go.Scatter(x=df['Date_Time'], y=df['Output_Current_V'], name='V phase o/p current')
I_w = go.Scatter(x=df['Date_Time'], y=df['Output_Current_W'], name='W phase o/p current')
I_a = go.Scatter(x=df['Date_Time'], y=df['Output_Current_Avg'], name='Average o/p current')
O_c = go.Layout({'title': 'Output currents'})
current = go.Figure(data=[I_u, I_v, I_w, I_a], layout=O_c)

HS_u = go.Scatter(x=df['Date_Time'], y=df['IGBT_HS_Temperature_U'], name='U phase IGBT Temp.')
HS_v = go.Scatter(x=df['Date_Time'], y=df['IGBT_HS_Temperature_V'], name='U phase IGBT Temp.')
HS_w = go.Scatter(x=df['Date_Time'], y=df['IGBT_HS_Temperature_W'], name='U phase IGBT Temp.')
HS_t = go.Layout({'title': 'IGBT Heat Sink Temperature'})
temperature = go.Figure(data=[HS_u, HS_v, HS_w], layout=HS_t)

V_i = go.Scatter(x=df['Date_Time'], y=df['Input_Voltage'], name='Input Voltage')
V_o = go.Scatter(x=df['Date_Time'], y=df['Output_Voltage'], name='Output Voltage')
V_d = go.Scatter(x=df['Date_Time'], y=df['DC_Bus_Voltage'], name='DC Voltage')
V_t = go.Layout({'title': 'Voltages at different points'})
voltage = go.Figure(data=[V_i, V_o, V_d], layout=V_t)

consumption = px.histogram(data_frame=df, x='Date_Time', y='Last_consumption', color='Node_Name', barmode='group')

layout = html.Div(children=[
    html.H1('Plant VFD Data',
            style={'textAlign': 'center', 'color': 'blue'}),
    html.Br(),
    html.H3('Current VFD parameters', style={'textAlign': 'center', 'color': 'blue'}),
    html.Br(),
    dcc.Dropdown(
        id='select_vfd',
        value='FDV Unit 3A',
        placeholder='Please select the VFDs',
        options=[{'label': i, 'value': i} for i in df.Node_Name.unique()],
        multi=False,
        style={'width': '500px',
               'verticalAlign': 'center',
               'border': '2px black solid'}),
    html.Br(),
    html.Div([
        daq.Gauge(
            id='Output_Current_U',
            color={"gradient": True, "ranges": {"green": [0, 150], "yellow": [151, 200], "red": [201, 500]}},
            value=200,
            label='Output Current U',
            max=500,
            min=0, style={'width': '16%',
                          'display': 'inline-block',
                          'border': '2px black solid'}),
        daq.Thermometer(
            id='IGBT_HS_Temp_U',
            value=200,
            label='IGBT HS Temp U',
            max=100,
            min=0,
            height=220,
            width=10,
            units="C", style={'width': '16%',
                              'height': '100%',
                              'display': 'inline-block'}),

        daq.Gauge(
            id='Output_Current_V',
            color={"gradient": True, "ranges": {"green": [0, 150], "yellow": [151, 200], "red": [201, 500]}},
            value=200,
            label='Output Current V',
            max=500,
            min=0, style={'width': '16%',
                          'display': 'inline-block',
                          'border': '2px black solid'}),
        daq.Thermometer(
            id='IGBT_HS_Temp_V',
            value=200,
            label='IGBT HS Temp V',
            max=100,
            min=0,
            height=220,
            width=10,
            units="C",
            style={'width': '16%',
                   'top': '0%',
                   'display': 'inline-block'}),

        daq.Gauge(
            id='Output_Current_W',
            value=200,
            color={"gradient": True, "ranges": {"green": [0, 150], "yellow": [151, 200], "red": [201, 500]}},
            label='Output Current W',
            max=500,
            min=0, style={'width': '16%',
                          'display': 'inline-block',
                          'border': '2px black solid'}),
        daq.Thermometer(
            id='IGBT_HS_Temp_W',
            value=200,
            label='IGBT HS Temp W',
            max=100,
            min=0,
            height=220,
            width=10,
            units="C",
            style={'width': '16%',
                   'height': '100%',
                   'display': 'inline-block'}),
    ]),
    html.Br(),
    html.H3('Historical parameter analysis graphs', style={'textAlign': 'center', 'color': 'blue'}),
    html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        start_date=df['Date_Time'].max().date(),
        end_date=df['Date_Time'].max().date(),
        min_date_allowed=df['Date_Time'].min().date(),
        max_date_allowed=df['Date_Time'].max().date(),
        display_format='DD MM YYYY',
        updatemode='bothdates',
        style={
            'border': '2px black solid'}),

    html.Br(),
    html.Div([
        dcc.Graph(id='current', figure=current,
                  style={'width': '48%',
                         'display': 'inline-block',
                         'border': '2px black solid'}),
        dcc.Graph(id='temperature', figure=temperature,
                  style={'width': '48%',
                         'display': 'inline-block',
                         'border': '2px black solid'}),
        html.Br(),
        dcc.Graph(id='voltage', figure=voltage,
                  style={'width': '48%',
                         'display': 'inline-block',
                         'border': '2px black solid'}),
        dcc.Graph(id='consumption', figure=consumption,
                  style={'width': '48%',
                         'display': 'inline-block',
                         'border': '2px black solid'})
    ])

])


@callback(
    [Output('Output_Current_U', 'value'),
     Output('Output_Current_V', 'value'),
     Output('Output_Current_W', 'value'),
     Output('IGBT_HS_Temp_U', 'value'),
     Output('IGBT_HS_Temp_V', 'value'),
     Output('IGBT_HS_Temp_W', 'value')],
    Input('select_vfd', 'value')
)
def instant_value(node):
    df_copy = df.copy()
    df_copy = df_copy[df_copy['Node_Name'] == node].reset_index(drop=True)
    iu = int(df_copy['Output_Current_U'][0])
    iv = int(df_copy['Output_Current_V'][0])
    iw = int(df_copy['Output_Current_W'][0])
    hu = int(df_copy['IGBT_HS_Temperature_U'][0])
    hv = int(df_copy['IGBT_HS_Temperature_V'][0])
    hw = int(df_copy['IGBT_HS_Temperature_W'][0])
    return iu, iv, iw, hu, hv, hw


@callback(
    [Output('current', 'figure'),
     Output('temperature', 'figure'),
     Output('voltage', 'figure'),
     Output('consumption', 'figure')],
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('select_vfd', 'value'),
)
def vfd_callbacks(start_date, end_date, vfd):
    df_copy = df.copy()
    df_copy = df_copy[(df_copy['Date_Time'] >= start_date) &
                      (df_copy['Date_Time'] <= end_date) &
                      (df_copy['Node_Name'] == vfd)]

    I_u = go.Scatter(x=df_copy['Date_Time'], y=df_copy['Output_Current_U'], name='U phase o/p current')
    I_v = go.Scatter(x=df_copy['Date_Time'], y=df_copy['Output_Current_V'], name='V phase o/p current')
    I_w = go.Scatter(x=df_copy['Date_Time'], y=df_copy['Output_Current_W'], name='W phase o/p current')
    I_a = go.Scatter(x=df_copy['Date_Time'], y=df_copy['Output_Current_Avg'], name='Average o/p current')
    O_c = go.Layout({'title': 'Output currents'})
    current = go.Figure(data=[I_u, I_v, I_w, I_a], layout=O_c)

    HS_u = go.Scatter(x=df_copy['Date_Time'], y=df_copy['IGBT_HS_Temperature_U'], name='U phase IGBT Temp.')
    HS_v = go.Scatter(x=df_copy['Date_Time'], y=df_copy['IGBT_HS_Temperature_V'], name='U phase IGBT Temp.')
    HS_w = go.Scatter(x=df_copy['Date_Time'], y=df_copy['IGBT_HS_Temperature_W'], name='U phase IGBT Temp.')
    HS_t = go.Layout({'title': 'IGBT Heat Sink Temperature'})
    temperature = go.Figure(data=[HS_u, HS_v, HS_w], layout=HS_t)

    V_i = go.Scatter(x=df_copy['Date_Time'], y=df_copy['Input_Voltage'], name='Input Voltage')
    V_o = go.Scatter(x=df_copy['Date_Time'], y=df_copy['Output_Voltage'], name='Output Voltage')
    V_d = go.Scatter(x=df_copy['Date_Time'], y=df_copy['DC_Bus_Voltage'], name='DC Voltage')
    V_t = go.Layout({'title': 'Voltages at different points'})
    voltage = go.Figure(data=[V_i, V_o, V_d], layout=V_t)

    consumption = px.bar(data_frame=df_copy, x='Date_Time', y='Last_consumption', barmode='group')

    return current, temperature, voltage, consumption
