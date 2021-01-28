# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
dense_ret = pd.read_csv('dense_return2020.csv', index_col=0)
tickers = list(dense_ret.columns)

fig = px.line(dense_ret[['SPY']].cumsum())


app.layout = html.Div([

    dcc.Dropdown(
        id='chosen_ticker',
        value="SPY",
        options=[{'label':str(i), 'value':i} for i in tickers],
        multi=True
        ),

    html.Br(),

    dcc.Graph(
        id="stock_return",
        figure = fig)

    ])

@app.callback(
    Output(component_id='stock_return', component_property='figure'),
    Input(component_id='chosen_ticker', component_property='value'),
)


def update_graph(input_value):
    if not input_value:
        return None

    ret = dense_ret[input_value].cumsum()
    fig = px.line(ret)
    fig.update_layout(
        title_text="Stock Return in 2020"
    )
    fig.update_yaxes(title_text="Cumulative Return")
    fig.update_xaxes(
        title_text="Date",
        dtick="M1",
        rangeslider_visible=True)
    fig.add_vrect(x0="2020-03-13", x1="2020-03-14", col=1,
              annotation_text="National Emergency", annotation_position="top left",
              fillcolor="green", opacity=0.5, line_width=0)

    fig.add_vrect(x0="2020-11-09", x1="2020-11-10", col=1,
                  annotation_text="pfizer vaccine result", annotation_position="top left",
                  fillcolor="green", opacity=0.5, line_width=0)
    
    return fig


if __name__ == '__main__':
    app.run_server(host = '127.0.0.1', debug=True)