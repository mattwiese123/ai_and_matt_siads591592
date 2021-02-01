# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import re

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

# =========covid news in NYT vs. Google searches vs. SPY cum. return====================
spy_ret = pd.DataFrame(dense_ret['SPY'])
spy_ret.index = pd.to_datetime(spy_ret.index)
covid_search = pd.read_csv('covid_search_trend.csv', index_col=0)
covid_search.index = pd.to_datetime(covid_search.index)

wkly_return = spy_ret.cumsum().resample('W').sum()
wkly_search = covid_search.resample('W').sum()

spy_covid = pd.concat([wkly_return, wkly_search], axis=1)
spy_covid.columns = ['spy_return%', 'COVID_search']
spy_covid['spy_return%'] = spy_covid['spy_return%']*100
spy_covid = spy_covid.dropna()

news_count = pd.read_csv('NYTnews_keyword_monthly.csv', index_col=0)
news_count['date'] = '2020-'+news_count['month'].astype(str)+'-15'
news_count['date'] = pd.to_datetime(news_count['date'])


spy_covid_correlation_all = spy_covid.corr()['COVID_search'][0]*100
spy_covid_correlation_after_march = spy_covid['2020-03':].corr()['COVID_search'][0]*100

fig3 = make_subplots(specs=[[{"secondary_y": True}]])

fig3.add_trace(
    go.Line(x=spy_covid.index, 
            y=spy_covid['spy_return%'], 
            name="spy return%",
            mode="markers+lines",
            marker_symbol="star"),
    secondary_y=False,
)

fig3.add_trace(
    go.Line(x=spy_covid.index, 
            y=spy_covid['COVID_search'], 
            name="covid search",
            mode="markers+lines",
            marker_symbol="star"),
    secondary_y=True,
)


fig3.add_trace(
    go.Bar(x=news_count.date, y=news_count['mention_per_news'], 
           name="COVID in news", opacity=0.3),
    secondary_y=True
)

fig3.update_yaxes(title_text="SPY Cumulative Return%", secondary_y=False, showgrid=False)
fig3.update_yaxes(title_text="Covid Search Trends", secondary_y=True, showgrid=False)

fig3.update_xaxes(dtick="M1", showgrid=True, rangeslider_visible=True)

fig3.add_vrect(x0="2020-03-13", x1="2020-03-14", col=1,
              annotation_text="National Emergency", annotation_position="top left",
              fillcolor="green", opacity=0.5, line_width=0)

fig3.add_vrect(x0="2020-11-09", x1="2020-11-10", col=1,
              annotation_text="pfizer vaccine result", annotation_position="top left",
              fillcolor="green", opacity=0.5, line_width=0)

# ========= Load company information data ===========

comps = pd.read_csv('sp500_comp_description.csv', index_col=0)


# ==============================
# ========start layout==========
# 
app.layout = html.Div([
    
    # ===============================================
    # ========timeline events dropdown ==============
    # ===============================================
    html.H4(children="Y Covid Timeline Events 2020"),
    dcc.Dropdown(
        id='chosen_date',
        value=dates[0],
        options=[{'label':str(i), 'value':i} for i in dates]
        ),
    html.Div(id="news"),
    html.Br(),

    
    # ===============================================
    # ========covid search trends viz  ==============
    # ===============================================
    html.H4(children=" SPY Cumulative Return vs COVID Search Trends in 2020 (Weekly)"),
    dcc.Graph(
        id="news_searches_spy",
        figure = fig3
        ),
    html.Br(),

    
    # ===============================================
    # ========ticker chooser           ==============
    # ===============================================
    html.H4(children=" Choose multiple tickers for visualization"),
    dcc.Dropdown(
        id='chosen_ticker',
        value="SPY",
        options=[{'label':str(i), 'value':i} for i in tickers],
        multi=True
        ),
    
    html.Br(),

    
    # ===============================================
    # ========ticker viz               ==============
    # ===============================================
    dcc.Graph(
        id="stock_return",
        figure = fig),

    html.Br(),

    html.H4(children=" Company Description for Selected Tickers (from Wikipedia)"),
    html.Div(id="company_description"),

    html.Br(),
    
    # ===============================================
    # ========treemap ==============
    # ===============================================
    html.H4(children=" Stock Correlation with Covid Google Search Trends 2020"),
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


@app.callback(
    Output(component_id='company_description', component_property='children'),
    Input(component_id='chosen_ticker', component_property='value'),
)
def update_company_info(input_value):
    
    input_value = list(input_value)
    input_value = [x for x in input_value if x!='SPY']
    if not input_value:
        return None

    comp_des = comps[comps['Symbol'].isin(input_value)]
    texts = []
    for i in range(len(comp_des)):
        text = comp_des['comp_description2'].iloc[i]
        t = comp_des['Symbol'].iloc[i]
        text = t+': '+re.sub(r'\[\d+\]', '', text)
        texts.append(text)

    return '---------------------->'.join(texts)



if __name__ == '__main__':
    app.run_server(host = '192.168.1.104', port=7506,debug=True)