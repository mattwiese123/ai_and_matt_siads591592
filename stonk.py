import pandas as pd
import streamlit as st
import plotly_express as px

df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
df.rename(columns={'Date first added': 'date_added'}, inplace=True)
df['date_added'].replace(to_replace=r'(\ \(.+\))', value='' ,regex=True, inplace=True)
df['date_added'] = pd.to_datetime(df['date_added'], infer_datetime_format=True)
df['sandp'] = 'S&P 500'
df.to_csv('stonk.csv')
