import pandas as pd
import requests
import time


def process_api(api, ticker):
    raw = requests.get(api)

    data = raw.json()
    keys = list(data.keys())
    data = data[keys[-1]]
    try:
        df = pd.DataFrame(data).T
        df['ticker'] = ticker
        return df
    except:
        print(raw.text)


if __name__ == '__main__':
	# load tickers that we want to download
    comps = pd.read_csv('../plotly/sp500.csv',index_col=0)
    symbols = comps['Symbol'].tolist()
	# specify date range for download
    dates = pd.date_range(start='2020-01-01', end='2020-12-31')
    start_date = str(dates.min())
    end_date = str(dates.max())

    cols = ['data_date', 'open', 'high', 'low', 'close', 'adj_close', 
    'volume', 'dividend amt', 'split coef', 'ticker']

	# alpha vantage does not return price data for these 2 tickers:
    bad_tickers = ['BF.B', 'PNR']

    # scraping
    data_all2=[]
    i=0
    # there are total 505 tickers
    while i<=500:
        data_all = []
        for ticker in symbols[i:i+5]:

            # with outputsize=full, it has 20 years of price data. default is 'compact', which only has 100days data
            if ticker in bad_tickers:
                continue
            # request free api key from alpha vantage website
            api = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={key}&outputsize=full"
            df = process_api(api=api, ticker=ticker)
            data_all.append(df)


        data_all = pd.concat(data_all)
        data_all = data_all.reset_index()
        data_all.columns = cols
        data_all['data_date'] = pd.to_datetime(data_all['data_date'])

        data_all = data_all.set_index('data_date')
        data_all = data_all.loc[start_date:end_date].reset_index()
        data_all2.append(data_all)
        i = i+5
    
        print(i)
        # to satisfy 5 queries per minute limitation for free account
        time.sleep(61)
    
    df3=pd.concat(data_all2)

    # add SPY data
    df = process_api(api=api, ticker='SPY')
    df = df.reset_index()
    df.columns = cols
    df['data_date'] = pd.to_datetime(df['data_date'])
    df = df.set_index('data_date')
    df = df.sort_index()['2020-01-01':]

    df_all = pd.concat([df3, df.reset_index()])
    df_all.to_csv('stock_prices_adj.csv')

