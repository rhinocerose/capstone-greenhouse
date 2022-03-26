from collections import deque
import flask
from flask import request
import dash
from dash import dcc
from dash import html, Input, Output
from pymongo import MongoClient

client = MongoClient(port=27017)
db = client.greenhouse_data

QUE_MAX = 10
buffer = deque(maxlen=QUE_MAX)

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div(
    html.Div([
        html.H4('Greenhouse Parameters'),
        html.Div(id='live-update-text'),
        # dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    data = buffer[-1]
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('CO2: {0:.2f}'.format(data['co2']), style=style),
        html.Span('Light: {0:.2f}'.format(data['light']), style=style),
        html.Span('Temperature: {0:0.2f}'.format(data['temperature']), style=style),
        html.Span('Humidity: {0:.2f}'.format(data['humidity']), style=style)
    ]

@server.route('/', methods=['POST'])
def req():
    print('Request triggered!')  # For debugging purposes, prints to console
    content = request.json
    store_data(content)
    return flask.redirect(flask.request.url)  # Should redirect to current page/ refresh page


def store_data(content):
    co2 = content.get("co2")
    light = content.get("light")
    temperature = content.get("temperature")
    humidity = content.get("humidity")
    if isinstance(co2, int):
        make_dict(co2, light, temperature, humidity)
    else:
        for idx, val in enumerate(co2):
            make_dict(val, light[idx], temperature[idx], humidity[idx])


def make_dict(co2, light, temperature, humidity):
    data = {
        'co2' : co2,
        'light': light,
        'temperature': temperature,
        'humidity' : humidity,
    }
    result=db.site_data.insert_one(data)
    buffer.append(data)
    print(buffer)
    print('Created of 500 as {0}'.format(result.inserted_id))


if __name__ == '__main__':
    app.run_server(debug=True)
