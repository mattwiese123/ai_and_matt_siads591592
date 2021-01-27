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
timeline_df = pd.read_csv('COVID_timeline.csv')

dates = list(timeline_df['date'].unique())

app.layout = html.Div([

    dcc.Dropdown(
        id='chosen_date',
        value=dates[0],
        options=[{'label':str(i), 'value':i} for i in dates]
        ),

    html.Br(),

    html.Div(id="news")

    ])

@app.callback(
    Output(component_id='news', component_property='children'),
    Input(component_id='chosen_date', component_property='value'),
)


def update_output_div(input_value):

    # return input_value
    news = timeline_df[timeline_df['date']==input_value]['content'].tolist()
    news = '; '.join(news)
    
    return news


if __name__ == '__main__':
    app.run_server(host = '127.0.0.1', debug=True)