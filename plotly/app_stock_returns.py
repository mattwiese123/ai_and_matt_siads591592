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

# =========for stock cumulative return plot===========
dense_ret = pd.read_csv('dense_return2020.csv', index_col=0)
tickers = list(dense_ret.columns)
fig = px.line(dense_ret[['SPY']].cumsum())

# =========for correlation treemap===========
merged2 = pd.read_csv('stock_covid_search_pct_change_corr_final.csv', index_col=0)
fig2 = px.treemap(merged2, 
                  path=['GICS Sector','GICS Sub-Industry', 'ticker'], 
                  values='corr abs', color='corr w covid change', 
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=0)


# =========for covid timeline events ===========
timeline_df = pd.read_csv('COVID_timeline.csv')
dates = list(timeline_df['date'].unique())


# ========start layout==========
# 
app.layout = html.Div([
    dcc.Dropdown(
        id='chosen_date',
        value=dates[0],
        options=[{'label':str(i), 'value':i} for i in dates]
        ),
    html.Div(id="news"),
    html.Br(),

    dcc.Dropdown(
        id='chosen_ticker',
        value="SPY",
        options=[{'label':str(i), 'value':i} for i in tickers],
        multi=True
        ),

    html.Br(),

    dcc.Graph(
        id="stock_return",
        figure = fig),

    html.Br(),
    html.H4(children=" Stock Correlation with Covid Google Search Trends"),
    dcc.Graph(
        id="stock_covid_corr",
        figure = fig2
        ),

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