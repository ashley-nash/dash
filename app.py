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

df_data = pd.read_csv('data.csv')
df_geo = pd.read_csv('GeoLabel.csv', dtype=str)
css_border = {
    'border': '1px solid black'
}

app.layout = html.Div(
    id='root',
    children=[
        html.H1('shiny'),
        dcc.Tabs([
            dcc.Tab(label='hour statistics',
                    children=[
                        html.Div("select date"),
                        dcc.Dropdown(
                            id='date',
                            options=[{'label': d, 'value': d} for d in df_data['日期'].unique()],
                            value='20170901',
                        ),
                        html.Div("select hour"),
                        dcc.Dropdown(id='hour', value='0'),
                        dcc.Graph(id='my-graph')
                    ]),
            dcc.Tab(label='location statistics',
                    children=[
                        html.Div('select date'),
                        dcc.Dropdown(
                            id='loc-date',
                            options=[{'label': d, 'value': d} for d in df_data['日期'].unique()],
                            value='20170901',
                        ),
                        html.Div('select location label'),
                        dcc.Dropdown(
                            id='loc-coord',
                            options=[{'label': d, 'value': d} for d in df_data['网格编号'].unique()],
                            value='13',
                        ),
                        dcc.Graph(id='loc-graph')
                    ]),
            dcc.Tab(label='geo label', children=[
                html.Table(children=[
                    html.Tr([html.Td('label'), html.Td('lng'), html.Td('lat')]),
                    *[
                        html.Tr(
                            [html.Td(row['label'], style=css_border),
                             html.Td(row['lng'], style=css_border),
                             html.Td(row['Lat'], style=css_border)]
                        )
                        for _, row in df_geo.iterrows()
                    ]
                ])
            ]),
        ]
        )
    ]
)


@app.callback(output=Output('hour', 'options'), inputs=[Input('date', 'value')])
def update_hour(selected_date):
    global df_data
    values = df_data.query('日期 == %s' % selected_date)['小时数'].unique()
    return [{'label': h, 'value': h} for h in values]


@app.callback(output=Output('my-graph', 'figure'), inputs=[
    Input('date', 'value'),
    Input('hour', 'value')
])
def update_graph(date, hour):
    global df_data
    data = df_data.query('日期 == "%s" & 小时数 == "%s"' % (date, hour))

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
            'xaxis': {'title': 'The location label'},
            'yaxis': {'title': 'number of people'}
        }
    }


@app.callback(output=Output('loc-graph', 'figure'), inputs=[
    Input('loc-date', 'value'),
    Input('loc-coord', 'value')
])
def update_location_graph(date, loc):
    global df_data
    groups = df_data.query('日期 == %s & 网格编号 == %s' % (date, loc)).groupby('小时数')
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
            'xaxis': {'title': 'hours'},
            'yaxis': {'title': 'number of people'}
        }
    }


if __name__ == '__main__':
    app.run_server(host="0.0.0.0")
