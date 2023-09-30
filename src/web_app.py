import pandas as pd
import streamlit as st

st.header('House prices in Moscow')

df = pd.read_csv("data/avito_ads.csv", index_col='id', sep=";")

st.write(df)
st.map(data=df, latitude='geo_lat', longitude='geo_lon')
