from collections import deque
from datetime import datetime, timedelta
import flask
from flask import request, Flask
import plotly.graph_objs as go
from dash import Dash
import numpy as np
from dash import dcc, html, Input, Output
from pymongo import MongoClient

client = MongoClient(port=27017)
db = client.greenhouse_data

QUE_MAX = 100
buffer = deque(maxlen=QUE_MAX)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
    html.H1(children='Greenhouse Dash'),
    html.Div(id='live-update-text'),

    html.Div([
        html.Div([
            # html.Div(children=''' CO2 Concentration '''),
            dcc.Graph( id='co2-graph'),
        ], className='six columns'),
        html.Div([
            # html.Div(children=''' Solar Radiation '''),
            dcc.Graph( id='light-graph'),
        ], className='six columns'),
    ], className='row'),
    html.Div([
        html.Div([
            # html.Div(children=''' Temperature '''),
            dcc.Graph( id='temperature-graph'),
        ], className='six columns'),
        html.Div([
            # html.Div(children=''' Humidity '''),
            dcc.Graph( id='humidity-graph'),
        ], className='six columns'),
    ], className='row'),

    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    )
]
)


@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    data = buffer[-1]
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.H5('Last Updated:'),
        html.Span('Timestamp: {0}'.format(data['timestamp'].strftime("%m/%d/%Y, %H:%M:%S")), style=style),
        html.Span('CO2: {0:.2f}'.format(data['co2']), style=style),
        html.Span('Light: {0:.2f}'.format(data['light']), style=style),
        html.Span('Temperature: {0:0.2f}'.format(data['temperature']), style=style),
        html.Span('Humidity: {0:.2f}'.format(data['humidity']), style=style)
    ]


@app.callback(Output('co2-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_co2_graph_live(n):
    data = assemble_data()
    fig = make_graph(data, 'co2')
    return fig

@app.callback(Output('light-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_light_graph_live(n):
    data = assemble_data()
    fig = make_graph(data, 'light')
    return fig

@app.callback(Output('temperature-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_temperature_graph_live(n):
    data = assemble_data()
    fig = make_graph(data, 'temperature')
    return fig

@app.callback(Output('humidity-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_humidity_graph_live(n):
    data = assemble_data()
    fig = make_graph(data, 'humidity')
    return fig

def make_graph(data, data_type):
    param = data[data_type]
    time = data['timestamp']
    std_dev = np.std(data[data_type])

    if data_type == 'co2':
        line_name = 'CO2'
        yaxis = 'CO2 Concentration (ppm)'
        fig_title = 'CO2 Concentration Over Time'
    if data_type == 'light':
        line_name = 'Solar Radiation'
        yaxis = 'Solar Radiation (PAR)'
        fig_title = 'Solar Radation Over Time'
    if data_type == 'temperature':
        line_name = 'Temperature'
        yaxis = 'Temperature (Celsius)'
        fig_title = 'Temperature Over Time'
    if data_type == 'humidity':
        line_name = 'Humidity'
        yaxis = 'Humidity (%)'
        fig_title = 'Humidity Over Time'

    fig = go.Figure([
        go.Scatter(
            name=line_name,
            x=time,
            y=param,
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
            showlegend=False
        ),
        go.Scatter(
            name='Upper Bound',
            x=time,
            y = [x+std_dev for x in param],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=time,
            y = [x-std_dev for x in param],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    fig.update_layout(
        yaxis_title=yaxis,
        title=fig_title,
        hovermode="x"
    )

    return fig

@server.route('/', methods=['POST'])
def req():
    print('Request triggered!')  # For debugging purposes, prints to console
    content = request.json
    store_data(content)
    return flask.redirect(flask.request.url)  # Should redirect to current page/ refresh page


def store_data(content):
    time = content.get("timestamp")
    if isinstance(time, int):
        time = datetime.fromtimestamp(time)
    elif isinstance(time, list):
        if isinstance(time[0], int):
            time = [datetime.fromtimestamp(x) for x in time]

    co2 = content.get("co2")
    light = content.get("light")
    temperature = content.get("temperature")
    humidity = content.get("humidity")
    if isinstance(co2, int):
        make_dict(time, co2, light, temperature, humidity)
    else:
        for idx, val in enumerate(co2):
            make_dict(time[idx], val, light[idx], temperature[idx], humidity[idx])


def make_dict(timestamp, co2, light, temperature, humidity):
    data = {
        'timestamp' : timestamp,
        'co2' : co2,
        'light': light,
        'temperature': temperature,
        'humidity' : humidity,
    }
    result=db.site_data.insert_one(data)
    buffer.append(data)
    print(buffer)

def assemble_data():
    data = {
        'timestamp' : [],
        'co2' : [],
        'light': [],
        'temperature': [],
        'humidity' : [],
    }
    for idx in range(QUE_MAX):
        read_data = buffer[idx]
        data['timestamp'].append(read_data['timestamp'])
        data['co2'].append(read_data['co2'])
        data['light'].append(read_data['light'])
        data['temperature'].append(read_data['temperature'])
        data['humidity'].append(read_data['humidity'])
    return data

def fill_data():
    time = datetime.now()
    data = {
        'timestamp' : [],
        'co2' : np.random.uniform(400, 700, QUE_MAX).tolist(),
        'light': np.random.uniform(400, 70000, QUE_MAX).tolist(),
        'temperature': np.random.uniform(5, 40, QUE_MAX).tolist(),
        'humidity' : np.random.uniform(0, 100, QUE_MAX).tolist(),
    }
    for idx in range(QUE_MAX):
        result = time - timedelta(seconds=5*(QUE_MAX - idx))
        data['timestamp'].append(result)
    store_data(data)



if __name__ == '__main__':
    fill_data()
    app.run_server(debug=True, host='0.0.0.0')
