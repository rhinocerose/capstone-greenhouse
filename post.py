import flask
import csv
from flask import request
import dash
from dash import dcc
import dash_daq as daq
from dash import html, Input, Output

text_style = {
    'color': 'blue',
}

file = 'data.csv'

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
co2val = 0
lightval = 2

app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=1*1000),

    html.Div(id='dummy', children='Test', style={'display': 'none'}),

    daq.Gauge(
        id='my-gauge-1',
        label="Default",
        value=lightval
    ),

    # dcc.Graph(
    #     id='example-graph',
    #     figure=fig
    # )

])

@server.route('/', methods=['POST'])
def req():
    print('Request triggered!')  # For debugging purposes, prints to console
    if text_style['color'] == 'blue':  # Toggle textcolor between red and blue
        text_style['color'] = 'red'
    else:
        text_style['color'] = 'blue'
    co2val = str(request.form.get('foo'))
    lightval = str(request.form.get('bin'))
    row = [co2val, lightval]
    with open(file, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    return flask.redirect(flask.request.url)  # Should redirect to current page/ refresh page

@app.callback(Output('dummy', 'style'),
              [Input('interval-component', 'n_intervals')])
def timer(n_intervals):
    return text_style

@app.callback(Output('my-gauge-1', 'value'), Input('interval-component', 'lightval'))
def update_output(value):
    return int(value)

if __name__ == '__main__':
    app.run_server(debug=True)
