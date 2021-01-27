import pandas as pd
import streamlit as st
import plotly_express as px

df = st.cache(pd.read_csv)('stonk.csv')


fig = px.treemap(df, path = ['sandp', 'GICS Sector', 'GICS Sub-Industry', 'Symbol'], values='CIK')

st.plotly_chart(fig)

st.write(df)
