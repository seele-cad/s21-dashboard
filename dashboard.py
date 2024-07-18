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

sb1=st.selectbox('Einheit', ['Kilogramm','Anzahl_Lieferscheine'])

if sb1=='Anzahl_Lieferscheine':
    ls=waa(df)
    st.write(
        px.bar(
        ls, 
        x='Projekt',
        y='Anzahl_Lieferscheine',
        color='Status',
        text='Anzahl_Lieferscheine',
        width=850,
        height=600
        )
    )
else:
    kg=kg(df)
    st.write(
        px.bar(
        kg, 
        x='Projekt',
        y='Material_kg',
        color='Status',
        text='Material_kg',
        width=850,
        height=600,
        title='Projekt nach Gewicht in kg'
        )
    )


col1, col2, col3 = st.columns(3)

with col1:
    df_bar1796 = bar_1796(df)
    fig1 = px.pie(
    df_bar1796,
    values='lieferscheine',
    names='ziel',
    labels='ziel',
    title='Lieferscheine RLA',
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
    title='Lieferscheine nach Empfänger-Adresse',
    width=400
    ).update_traces(textinfo='value')
    st.write(fig2)

with col3:
    df_gate = gate(df)
    st.write(
        px.pie(
        df_gate,
        values='Count',
        names='Type',
        labels='Type',
        title='Lieferschein Erfassung',
        width=400
        ).update_traces(textinfo='value')
    )
    

status = st.selectbox('Wähle Status', ['shipped','warehouse', 'onsite', 'installed'])

if status == 'installed':
    df_hist = installed(df)
    st.write(
        px.bar(
            df_hist,
            x='week_installed',
            y='anzahl_lieferscheine',
            text='anzahl_lieferscheine',
            title='Anzahl Installationen nach Lieferscheinen & Woche',
            width=1700,
            height=600,
            color='anzahl_lieferscheine'
            )
    )

elif status == 'onsite':
    df_onsite = onsite(df)
    st.write(
        px.bar(
            df_onsite,
            x='week_onsite',
            y='anzahl_lieferscheine',
            text='anzahl_lieferscheine',
            title='Anzahl onsite-Buchungen nach Lieferscheinen & Woche',
            width=1700,
            height=600,
            color='anzahl_lieferscheine'
            )
    )
elif status == 'warehouse':
    df_ware = warehouse(df)
    st.write(
        px.bar(
            df_ware,
            x='week_warehouse',
            y='anzahl_lieferscheine',
            text='anzahl_lieferscheine',
            title='Anzahl warehouse-Buchungen nach Lieferscheinen & Woche',
            width=1700,
            height=600,
            color='anzahl_lieferscheine'
        )
    )
else:
    df_shipped = shipped(df)
    st.write(
        px.bar(
            df_shipped,
            x='week_shipped',
            y='anzahl_lieferscheine',
            text='anzahl_lieferscheine',
            title='Anzahl shipped-Buchungen nach Lieferscheinen & Woche',
            width=1700,
            height=600,
            color='anzahl_lieferscheine'
        )
    )


# create general chart
sb2=st.selectbox('Darstellung', ['nach Gewicht','nach Anzahl_Lieferscheine']) 

if sb2=='nach Gewicht':
    df_bar = gewicht(df)
    st.write(
        px.bar(
            df_bar, 
            x='RLA_Nummer',
            y='Material_kg',
            color='Status',
            text='Material_kg',
            title='Lieferscheine der Regellichtaugen nach Status und Gewicht',
            width=1700,
            height=600
            )
        )

else:
    df_bar2 = lieferschein(df)
    st.write(
        px.bar(
            df_bar2, 
            x='rla_nummer',
            y='anzahl_lieferscheine',
            color='status',
            text='anzahl_lieferscheine',
            title='Lieferscheine der Regellichtaugen nach Status und Anuahl der Lieferscheine',
            width=1700,
            height=600
            )
        )
