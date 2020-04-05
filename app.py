#!/usr/bin/env python
# python3.5
# -*- coding: utf8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import pandas as pd
import dash_html_components as html
import numpy as np

app = dash.Dash()


def load_file() -> pd.DataFrame:
    return pd.read_csv('data.csv')


df = load_file()

app.layout = html.Div(
    id='root',
    children=[
        html.H1('shiny'),
        dcc.Tabs(
            [dcc.Tab(label='hour statistics',
                     children=[
                         html.Div("日期"),
                         dcc.Dropdown(
                             id='date',
                             options=[{'label': d, 'value': d} for d in df['日期'].unique()],
                             value='20170901',
                         ),
                         html.Div("小时数"),
                         dcc.Dropdown(id='hour'),
                         dcc.Graph(id='my-graph')
                     ]),
             dcc.Tab(label='location statistics',
                     children=[
                         html.Div('select date'),
                         dcc.Dropdown(
                             id='loc-date',
                             options=[{'label': d, 'value': d} for d in df['日期'].unique()],
                             value='20170901',
                         ),
                         dcc.Dropdown(
                             id='loc-coord',
                             options=[{'label': d, 'value': d} for d in df['网格编号'].unique()],
                             value='13',
                         ),
                         dcc.Graph(id='loc-graph')
                     ])
             ]
        )
    ]
)


@app.callback(output=Output('hour', 'options'), inputs=[Input('date', 'value')])
def update_hour(selected_date):
    global df
    values = df.query('日期 == %s' % selected_date)['小时数'].unique()
    return [{'label': h, 'value': h} for h in values]


@app.callback(output=Output('my-graph', 'figure'), inputs=[
    Input('date', 'value'),
    Input('hour', 'value')
])
def update_graph(date, hour):
    global df
    data = df.query('日期 == "%s" & 小时数 == "%s"' % (date, hour))

    return {
        'data': [
            {
                'x': data['网格编号'],
                'y': data['出发人数'],
                'type': 'bar',
                'name': 'Departure number'
            },
            {
                'x': data['网格编号'],
                'y': data['到达人数'],
                'type': 'bar',
                'name': 'Master arrivals'
            }
        ],
        'layout': {
            'xaxis': {'title': '网格编号'},
            'yaxis': {'title': '人数'}
        }
    }


@app.callback(output=Output('loc-graph', 'figure'), inputs=[
    Input('loc-date', 'value'),
    Input('loc-coord', 'value')
])
def update_location_graph(date, loc):
    global df
    groups = df.query('日期 == %s & 网格编号 == %s' % (date, loc)).groupby('小时数')
    departure = groups['出发人数'].agg(np.sum)
    arrivals = groups['到达人数'].agg(np.sum)
    return {
        'data': [
            {
                'x': departure.index,
                'y': departure.values,
                'name': 'Departure number'
            },
            {
                'x': arrivals.index,
                'y': arrivals.values,
                'name': 'Master arrivals'
            }
        ],
        'layout': {
            'xaxis': {'title': '网格编号'},
            'yaxis': {'title': '人数'}
        }
    }


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=12345)
