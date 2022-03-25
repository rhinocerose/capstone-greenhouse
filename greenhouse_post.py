import flask
import csv
from flask import request
import dash
from dash import dcc
# import dash_daq as daq
from dash import html, Input, Output
from pymongo import MongoClient

client = MongoClient(port=27017)
db = client.greenhouse_data

file = 'data.csv'

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=1*1000),

    html.Div(id='dummy', children='Test', style={'display': 'none'}),

    # dcc.Graph(
    #     id='example-graph',
    #     figure=fig
    # )

])

@server.route('/', methods=['POST'])
def req():
    print('Request triggered!')  # For debugging purposes, prints to console
    content = request.json
    makeDataEntry(content)
    # co2val = content.get("foo")
    # lightval = content.get("bar")
    # with open(file, 'a', encoding='UTF8', newline='') as f:
    #     writer = csv.writer(f)
    #     if isinstance(co2val, int):
    #         print("CO2: " + str(co2val) + " Light: " + str(lightval) )
    #         row = [co2val, lightval]
    #         writer.writerow(row)
    #     else:
    #         for idx, val in enumerate(co2val):
    #             print("CO2: " + str(val) + " Light: " + str(lightval[idx]) )
    #             row = [val, lightval[idx]]
    #             writer.writerow(row)
    return flask.redirect(flask.request.url)  # Should redirect to current page/ refresh page

# def writeToDB(values):
#     for item in values:

def makeDataEntry(content):
    co2 = content.get("co2")
    light = content.get("light")
    temperature = content.get("temperature")
    humidity = content.get("humidity")
    if isinstance(co2, int):
        data = {
            'co2' : co2,
            'light': light,
            'temperature': temperature,
            'humidity' : humidity,
        }
        result=db.reviews.insert_one(data)
        print('Created of 500 as {0}'.format(result.inserted_id))
    else:
        for idx, val in enumerate(co2):
            data = {
                'co2' : val,
                'light': light[idx],
                'temperature': temperature[idx],
                'humidity' : humidity[idx],
            }
            result=db.reviews.insert_one(data)
            print('Created {0} of 500 as {1}'.format(idx, result.inserted_id))



@app.callback(Output('my-gauge-1', 'value'), Input('interval-component', 'lightval'))
def update_output(value):
    return int(value)

if __name__ == '__main__':
    app.run_server(debug=True)
