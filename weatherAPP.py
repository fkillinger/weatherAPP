from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="KC Webspace", page_icon=":sun:", layout="wide")

st.header('Weather - Information Glattbach Unterfranken')      # st.title() - st.header()  - st.subheader()

# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host/dbname'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://FKillinger:314159frigit!@mariadb-2.c74muwoki9iu.eu-north-1.rds.amazonaws.com:3306/esp_data'

conn = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

SQL_Query = pd.read_sql("""select location as loc
                                    FROM esp_data.SensorData 
                                    where id >= (select max(id) from esp_data.SensorData) -  12""", conn)

# Abfage welche locations es in DB gibt - Diese werden in der Select - Box angezeigt!
loc_set = set()                                                    # set --> Menge
loc_unit = set()
df = pd.DataFrame(SQL_Query, columns=['loc'])
df = df.reset_index()  # make sure indexes pair with number of rows

for index, row in df.iterrows():
    loc_unit = {row['loc']}
    loc_set = loc_set | loc_unit                                    # Vereinigungsmenge
# st.write(loc_set)

# ---- Header section -----
with st.container():
    #st.subheader("Meine neue Webseite")
    left_column, right_column = st.columns([2,4])

    with right_column:
        Counter = 240
        # Counter = st.selectbox('Auswahl Anzahl Messpunkte', (100, 500, 1000))
        # st.write('You selected: ', Counter)
        Counter = st.number_input('Insert dataset number', min_value = 100, step = 100)
        st.write('The current number is ', Counter)
        Counter = str(Counter)
        st.write('###')

    with left_column:
        locus = 'Test black'
        locus = st.selectbox('Auswahl Messstelle', (loc_set))
        st.write('You selected: ', locus)
        st.write('###')


SQL_Query = pd.read_sql("""select   reading_time as Time, 
                                    cast(value1 as DECIMAL(4,2)) as Temp, 
                                    cast(value2 as DECIMAL(4,0)) as Feuchte, 
                                    cast(value3 as DECIMAL(6,2)) as Druck, 
                                    cast(value5 as DECIMAL(4,0)) as Helligkeit
                                    FROM esp_data.SensorData 
                                    where location = '""" + locus + """'
                                    and id >= (select max(id) from esp_data.SensorData) - """ + Counter, conn)

SQL_Query_des = SQL_Query.sort_values(by="Time", ascending=False)       # Tabellenwerte sortiert nach DateTime descending

with st.container():
    #st.subheader("Meine neue Webseite")
    left_column, right_column = st.columns([2,4])

    with left_column:
        st.write("Temperaturverlauf Glattbach Weitzkaut 24 / letzte Tage")
        st.write(SQL_Query_des)

    with right_column:
        # DataFrames zur Anzeige
        df1 = pd.DataFrame(SQL_Query, columns=['Time', 'Temp'])
        df2 = pd.DataFrame(SQL_Query, columns=['Time', 'Druck'])

        # Besser mit Plotly
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig = fig.add_trace(go.Scatter(x=df1.Time, y=df1.Temp, mode="lines", name="Temp"), secondary_y=False)
        # fig.update_xaxes(griddash='dot')
        fig.update_yaxes(griddash='dot')
        # fig.update_xaxes(gridcolor='white')
        fig.update_yaxes(gridcolor='white')
        fig = fig.add_trace(go.Scatter(x=df2.Time, y=df2.Druck, mode="lines", name="Luftdruck"), secondary_y=True)

        # Add figure title
        fig.update_layout(title_text=" Wetterdaten Weitzkaut 24")
        # Set x-axis title
        fig.update_xaxes(title_text="Datum / Zeit")
        # fig.update_xaxes(griddash='dot')
        fig.update_yaxes(griddash='dot')
        # fig.update_xaxes(gridcolor='white')
        fig.update_yaxes(gridcolor='white')
        fig.update_layout(
            {
                "paper_bgcolor": "rgba(100, 111, 111, 1)",
                "plot_bgcolor": "rgba(55, 55, 55, 1)",
            }
        )

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>Temperaturin °C</b> ", secondary_y=False)
        fig.update_yaxes(title_text="<b>Luftdruckin hPascal</b> ", secondary_y=True)
        fig = fig.update_layout(showlegend=True)

        st.plotly_chart(fig)





