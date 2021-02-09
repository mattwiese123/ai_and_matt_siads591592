# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import re
import plotly.io as pio
import base64 
import datetime
import numpy as np
import json

pio.templates.default = "plotly_dark"

external_stylesheets = [dbc.themes.CYBORG]# ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="Covid SPY NYT Trends")

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# =========for stock cumulative return plot===========
dense_ret = pd.read_csv('./dense_return2020.csv', index_col=0)
tickers = list(dense_ret.columns)
fig = px.line(dense_ret[['SPY']].cumsum())

# =========for correlation treemap===========
merged2 = pd.read_csv('./stock_covid_search_pct_change_corr_final.csv', index_col=0)
fig2 = px.treemap(merged2, 
                  path=['GICS Sector','GICS Sub-Industry', 'ticker'], 
                  values='corr abs', color='corr w covid change', 
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=0,
                  height=800
                 )

# =========for covid timeline events ===========
timeline_df = pd.read_csv('./COVID_timeline.csv')
dates = list(timeline_df['date'].unique())

# =========covid news in NYT vs. Google searches vs. SPY cum. return====================
spy_ret = pd.DataFrame(dense_ret['SPY'])
spy_ret.index = pd.to_datetime(spy_ret.index)
covid_search = pd.read_csv('./covid_search_trend.csv', index_col=0)
covid_search.index = pd.to_datetime(covid_search.index)

wkly_return = spy_ret.cumsum().resample('W').sum()
wkly_search = covid_search.resample('W').sum()

spy_covid = pd.concat([wkly_return, wkly_search], axis=1)
spy_covid.columns = ['spy_return%', 'COVID_search']
spy_covid['spy_return%'] = spy_covid['spy_return%']*100
spy_covid = spy_covid.dropna()

news_count = pd.read_csv('./NYTnews_keyword_monthly.csv', index_col=0)
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
fig3.update_layout(width=1250, height=400, title='SPY Cumulative Return vs COVID Search Trends in 2020 (Weekly)')

# ========= Load company information data ===========

comps = pd.read_csv('./sp500_comp_description.csv', index_col=0)

# ======= News Timeline ===========
# https://gist.github.com/bendichter/d7dccacf55c7d95aec05c6e7bcf4e66e

def display_year(df,
                 year: int = None,
                 month_lines: bool = True,
                 fig=None,
                 row: int = None):
    
    def timeline_helper(i):
        x = df[df['date'] == pd.to_datetime(i)]['content'].str.strip().to_list()
        return 'Headlines: <br>'+'<br>'.join(x)
    
    if year is None:
        year = datetime.datetime.now().year
  
    # data[:len(df['date'])] = df['date']
    

    d1 = datetime.date(year, 1, 1)
    d2 = datetime.date(year, 12, 31)

    df['date'] = pd.to_datetime(df['date'])
    data = np.ones(365) * np.nan
    for i in range(len(data)):
        if pd.to_datetime(d1 + datetime.timedelta(i)) in [datetime.date(2020,3,13), datetime.date(2020,11,16)]:
            data[i] = 0.5
        elif (pd.to_datetime(d1 + datetime.timedelta(i)) in df['date'].unique()):
            # print(d1 + datetime.timedelta(i), df['date'].unique())
            data[i] = 1
        else:
            data[i] = 0
            
    
    delta = d2 - d1
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_days =   [31,    28,    31,     30,    31,     30,    31,    31,    30,    31,    30,    31]
    month_positions = (np.cumsum(month_days) - 15)/7

    dates_in_year = [d1 + datetime.timedelta(i) for i in range(delta.days+1)] #gives me a list with datetimes for each day a year
    weekdays_in_year = [i.weekday() for i in dates_in_year] #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
    
    weeknumber_of_dates = [int(i.strftime("%V")) if not (int(i.strftime("%V")) == 1 and i.month == 12) else 53
                           for i in dates_in_year] #gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory
    text = ['date: ' + str(i) + '<br>' + timeline_helper(i) if pd.to_datetime(i) in df['date'].unique()
            else 'date: ' + str(i) 
            for i in dates_in_year]
    #text = [str(i) for i in dates_in_year] #gives something like list of strings like ‘2018-01-25’ for each date. Used in data trace to make good hovertext.
    ttext = []
    #4cc417 green #347c17 dark green
    colorscale=[[0, '#eeeeee'], [0.5, '#34eb6b'], [1, '#513569']]
    
    # handle end of year
    

    data = [
        go.Heatmap(
            x=weeknumber_of_dates,
            y=weekdays_in_year,
            z=data,
            text=text,
            hoverinfo='text',
            xgap=3, # this
            ygap=3, # and this is used to make the grid-like apperance
            showscale=False,
            colorscale=colorscale
        )
    ]
    
        
    if month_lines:
        kwargs = dict(
            mode='lines',
            line=dict(
                color='#9e9e9e',
                width=1
            ),
            hoverinfo='skip'
            
        )
        for date, dow, wkn in zip(dates_in_year,
                                  weekdays_in_year,
                                  weeknumber_of_dates):
            if date.day == 1:
                data += [
                    go.Scatter(
                        x=[wkn-.5, wkn-.5],
                        y=[dow-.5, 6.5],
                        **kwargs
                    )
                ]
                if dow:
                    data += [
                    go.Scatter(
                        x=[wkn-.5, wkn+.5],
                        y=[dow-.5, dow - .5],
                        **kwargs
                    ),
                    go.Scatter(
                        x=[wkn+.5, wkn+.5],
                        y=[dow-.5, -.5],
                        **kwargs
                    )
                ]
                    
                    
    layout = go.Layout(
        title='NYT COVID Headline Activity Chart',
        height=250,
        width=1250,
        yaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            tickvals=[0, 1, 2, 3, 4, 5, 6],
            ticklabelposition='outside left',
            autorange="reversed"
        ),
        xaxis=dict(
            showline=False, showgrid=False, zeroline=False,
            tickmode='array',
            ticktext=month_names,
            tickvals=month_positions
        ),
        font={'size':10, 'color':'white'}, # #9e9e9e
        plot_bgcolor=('#fff'),
        margin = dict(t=40, pad=3),
        showlegend=False
    )

    if fig is None:
        fig = go.Figure(data=data, layout=layout)
    else:
        fig.add_traces(data, rows=[(row+1)]*len(data), cols=[1]*len(data))
        fig.update_layout(layout)
        fig.update_xaxes(layout['xaxis'])
        fig.update_yaxes(layout['yaxis'])

    fig['layout'].update(plot_bgcolor='rgb(17,17,17)')
    return fig


def display_years(z, years):
    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    for i, year in enumerate(years):
        data = z[i*365 : (i+1)*365]
        display_year(data, year=year, fig=fig, row=i)
        fig.update_layout(height=250*len(years))
    return fig

fig5 = display_years(timeline_df, (2020,))


# big_fig = make_subplots(rows=2, cols=1)
# big_fig.add_trace(fig3, row=1, col=1)
# big_fig.add_trace(fig5, row=2, col=1)

# ======== Fig Themes =============
fig.layout.template = 'plotly_dark'
fig2.layout.template = 'plotly_dark'
fig3.update_layout(template = 'plotly_dark')

# ==============================
# ========start layout==========
# 
app.layout = html.Div([
    html.H1(children="Covid Timeline Events 2020"),
    dcc.Tabs([
        dcc.Tab(label='Headline Timeline',
                children=[
                    dbc.Row([
                        dbc.Col([
                            # html.H3('COVID News Timeline'),
                            dcc.Graph(
                                id="news_tl",
                                figure = fig5
                            ),
                            dcc.Graph(
                            id="news_searches_spy",
                            figure = fig3
                        ),
                        ]), 
                        dbc.Col(
                            html.Div(id='hover_boi'),
                        )]
                    ),
                   html.Div([
                        # html.H3(children=" SPY Cumulative Return vs COVID Search Trends in 2020 (Weekly)"),
                        
                   ]),
                    html.Br(),
        ]),
        dcc.Tab(label="Ticker Chooser", children=[
            # ===============================================
            # ========ticker chooser           ==============
            # ===============================================
            html.H3(children="Choose multiple tickers for visualization"),
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
        ]),
        dcc.Tab(label="COVID Correlation Treemap", children=[
            # ===============================================
            # ========treemap ==============
            # ===============================================
            html.H3(children=" Stock Correlation with Covid Google Search Trends 2020"),
            dcc.Graph(
                id="stock_covid_corr",
                figure = fig2
                ),
        ]),
    ], 
    id="tabs",
    colors={'border':'#ffffff', 'primary':'#333333', 'background':'#000000'}
    )
],
    style={'marginLeft': 20, 'marginRight': 20, 'marginTop': 20, 'marginBottom': 10,})
)

fig3.layout.template = 'plotly_dark'

# ===============================================
# ========timeline events dropdown ==============
# ===============================================
'''
@app.callback(
    Output(component_id='news', component_property='children'),
    Input(component_id='chosen_date', component_property='value'),
)

def update_output_div(input_value):

    # return input_value
    month = str(input_value)[5:8]
    if month[0] == '0':
        img_month = month[1]
    else:
        img_month = month[:2]
    image_filename = 'NYT_News_2020_M'+img_month+'.jpg'
    #encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    
    news = timeline_df[timeline_df['date']==input_value]['content'].tolist()
    news_items = [html.Div(html.H6(x)) for x in news]
    news_items.insert(0, html.H5('COVID Related Headlines for ' + str(input_value)))
    # news_items.append(html.Div(html.Img(src=app.get_asset_url(image_filename))))
    # news_items.append(html.H5(img_month))
    
    return dbc.Row([dbc.Col(news_items), 
                    dbc.Col(html.Div(html.Img(src=app.get_asset_url(image_filename), height=400, width=400)))])
dcc.Tab(label="SPY vs COVID Trends", children=[
            # ===============================================
            # ========timeline events dropdown ==============
            # ===============================================
            
            dcc.Dropdown(
                id='chosen_date',
                value=dates[0],
                options=[{'label':str(i), 'value':i} for i in dates]
                ),
            html.Div(id="news", style={'display':'inline-block',}),
            html.Br(),
        
            # ===============================================
            # ========covid search trends viz  ==============
            # ===============================================
            html.H3(children=" SPY Cumulative Return vs COVID Search Trends in 2020 (Weekly)"),
            dcc.Graph(
                id="news_searches_spys",
                figure = fig3
                ),
            html.Br(),
        ]),
'''
# ===============================================
# ========ticker viz  ===========================
# ===============================================
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
        texts.append(html.H6(t))
        #text = t+': '+re.sub(r'\[\d+\]', '', text)
        texts.append(html.P(re.sub(r'\[\d+\]', '', text)))

    return texts # [html.P(x) for x in texts]

@app.callback(
    Output(component_id='hover_boi', component_property='children'),
    [Input(component_id='news_tl', component_property='hoverData')]
)
def dis_play_hover_data(hover_data):
    try:
        x = json.loads(json.dumps(hover_data, indent=2))['points'][0]['text']
        image_month = str(int(x[11:13])) 
        image_filename = 'NYT_News_2020_M'+image_month+'.jpg'
        return [html.Br(),
                html.H4('NYT Abstracts Word Cloud ' + str(datetime.date(2020,int(image_month),1).strftime('%b, %Y')),
                 style={'textAlign': 'center'}),
                 html.Div([
                     html.Img(src=app.get_asset_url(image_filename), height=500, width=500),
                     ], style={'textAlign': 'center'})
                 ]
    except:
        image_month = '1'
        image_filename = 'NYT_News_2020_M'+image_month+'.jpg'
        return [html.Br(),
                html.H4('NYT Abstracts Word Cloud Jan, 2020',
                    style={'textAlign': 'center'}),
                 html.Div([
                     html.Img(src=app.get_asset_url(image_filename), height=500, width=500),
                     ], style={'textAlign': 'center'})
                 ]

if __name__ == '__main__':
    app.run_server(host = '192.168.1.104', port=7506, debug=True)
