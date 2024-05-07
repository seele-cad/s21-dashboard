# import necessary packages
import pandas as pd  
import plotly.express as px  
import streamlit as st
import datetime
from engine import *


# Configurations of Streamlit page
st.set_page_config(
    page_title = "S21 Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

@st.cache_data
def load_data():
    df = format_rcom_data(get_rcom_objects(DOMAIN_NAME, token, CLIENT_ID_SEELE, '067D7718-6C48-4517-AB80-5E6128BAC7C2', None, searchKey=None, searchValue=None, changedFrom=None, changedUntil=None)[KEY], get_rcom_bins(DOMAIN_NAME, token))
    return df

df = load_data()
df = df[df['warenausgang_projekt']=='1796']
df.reset_index(drop=True, inplace=True)


# dashboard title
st.title("S21 - Dashboard")


# create general chart
df_bar = build_frame(df)
fig0 = px.bar(
    df_bar, 
    x='RLA_Nummer',
    y='Material_kg',
    color='Status',
    width=1700,
    height=600
    )
st.write(fig0)

col1, col2 = st.columns(2)

with col1:
    df_bar1796 = bar_1796(df)
    fig1 = px.pie(
    df_bar1796,
    values='lieferscheine',
    names='ziel',
    labels='ziel',
    title='Lieferscheine RLA Projekt 1796',
    width=400
    ).update_traces(textinfo='value')
    st.write(fig1)

with col2:
    df_plz = plz(df)
    fig2 = px.pie(
    df_plz,
    values='counts',
    names='plz',
    labels='plz',
    title='Lieferscheine Standort Projekt 1796'
    ).update_traces(textinfo='value')
    st.write(fig2)


# top-level filter
def set_filter():
    filter_ = st.selectbox("Wähle RLA", (["RLA 01", "RLA 02", "RLA 03", "RLA 04", "RLA 05", "RLA 06", "RLA 07", "RLA 08", "RLA 09", "RLA 10", "RLA 11", "RLA 12", "RLA 13", "RLA 14", "RLA 15", "RLA 16", "RLA 17", "RLA 18", "RLA 19", "RLA 20", "RLA 21", "RLA 22", "RLA 23"]))
    return filter_

filter_ = set_filter()
