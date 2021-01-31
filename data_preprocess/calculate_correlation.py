import pandas as pd
import numpy as np


if __name__ == '__main__':
    prices = pd.read_csv('../data_collect/stock_prices_adj.csv', index_col=0)
    prices=prices.sort_values(by=['ticker', 'data_date'])
    prices['data_date'] = pd.to_datetime(prices['data_date'])

    dense_returns = prices.groupby(['data_date','ticker'])['adj_close'].last().unstack().pct_change()
    dense_returns = dense_returns.iloc[1:]
    # save dense return dataset
    dense_returns.to_csv('../plotly/dense_return2020.csv')


    # ==== calculate return correlation with covid search trends ====
    covid_search = pd.read_csv('covid_search_trend.csv', index_col=0)
    covid_search.index = pd.to_datetime(covid_search.index)

    # resample to weekly data for both covid search and returns (covid search data is only weekly)
    wkly_search = covid_search.resample('W').mean().reset_index()
    wkly_search.columns = ['data_date', 'searches']

    # we want to use percentage changes for correlation calculation with daily returns
    wkly_search['pct_change'] = wkly_search['searches'].pct_change()
    wkly_search2 = wkly_search.dropna().iloc[1:].drop('searches',1)

    return_search_df2 = dense_returns.resample('W').sum().reset_index().merge(wkly_search2)

    # calculate correlation 
    correlation_df2 = return_search_df2.set_index('data_date').corr()

    # load company information for sectors and sub-industry
    comps = pd.read_csv('../plotly/sp500.csv', index_col=0)

    # we only need all stock's correlation with covid search's pct_change
    search_return_corr = pd.DataFrame(correlation_df2['pct_change']).reset_index()

    merged2 = search_return_corr.merge(comps[['Symbol', 'GICS Sector', 'GICS Sub-Industry']], 
    	how='left', left_on='index', right_on='Symbol')
    merged2 = merged2.drop(['Symbol'],1)
    merged2 = merged2.dropna()

    # get absolute correlation for later treemap plot
    merged2['corr_abs'] = merged2['pct_change'].apply(abs)
    merged2.columns = ['ticker', 'corr w covid change', 'GICS Sector', 'GICS Sub-Industry', 'corr abs']
    merged2.to_csv('../plotly/stock_covid_search_pct_change_corr_final.csv')


    
    
    

