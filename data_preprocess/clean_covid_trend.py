import pickle
import pandas as pd


if __name__ == "__main__":
	covid_trend = pickle.load(open('../data_collect/covid_trends.pkl', 'rb'))
    covid_trend_df = pd.DataFrame(covid_trend['trends_interest_over_time']['data'])

    covid_trend_df['has_values'] = covid_trend_df['values'].apply(lambda x: x[0]['has_value'])
    covid_trend_df = covid_trend_df[covid_trend_df['has_values']==True]
    
    covid_trend_df['values2'] = covid_trend_df['values'].apply(lambda x: x[0]['value'])
    covid_trend_df['date'] = covid_trend_df['date_utc'].apply(lambda x: x.split('T')[0])
    covid_trend_df['date'] = pd.to_datetime(covid_trend_df['date'])
    
    covid_search = covid_trend_df[['date', 'values2']].set_index('date')
    covid_search.columns = ['covid_search_trend']
    covid_search.to_csv('../plotly/covid_search_trend.csv')