import altair as alt
import streamlit as st
import pandas as pd
import datetime as dt
from PIL import Image
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title='Gibraltar Registry', page_icon=':bar_chart:')

def drawSideBar(df, displayDf):
    with st.sidebar:
        selectDate = st.date_input('Data',
                                    (dt.date(2023,1,1),dt.date(2023,12,31)),
                                    dt.date(2023,1,1),
                                    dt.date(2023,12,31),
                                    format='DD/MM/YYYY')
        categoriaSelect = st.multiselect('Categoria', set(df['Categoria'].values))
        gastoSelect = st.multiselect('Gasto',set(df['Gasto'].values))
        pagadorSelect = st.multiselect('Pagador',set(df['Pagador'].values))


        if len(selectDate)==1:
            displayDf = displayDf.loc[(displayDf['Data'].dt.date>=selectDate[0])]
        if len(selectDate)>1:
            displayDf = displayDf.loc[(displayDf['Data'].dt.date>=selectDate[0]) &
                                (displayDf['Data'].dt.date<=selectDate[1])]
            
        stmtCategoria = ['Categoria=="%s"'%i for i in categoriaSelect]
        queryCategoria = ' | '.join(stmtCategoria)
        if queryCategoria:
            displayDf.query(queryCategoria, inplace=True)

        stmtGasto = ['Gasto=="%s"'%i for i in gastoSelect]
        queryGasto = ' | '.join(stmtGasto)
        if queryGasto:
            displayDf.query(queryGasto, inplace=True)

        stmtPagador = ['Pagador=="%s"'%i for i in pagadorSelect]
        queryPagador = ' | '.join(stmtPagador)
        if queryPagador:
            displayDf.query(queryPagador, inplace=True)

        st.session_state['df'] = df
        st.session_state['displayDf'] = displayDf

        return df, displayDf
    
def fetchDb(conn):
    rawdf = conn.read(
    worksheet='db',
    usecols=[0,1,2,3,4,5]
    #ttl='10m',
    )
    st.session_state['rawdf'] = rawdf

    #db clean
    dfColumns = ['Data','Gasto','Categoria','Pagador','$','Valor']
    df = rawdf[dfColumns]
    df = df.dropna()
    df['Data'] = pd.to_datetime(df['Data'],dayfirst=True)
    df.sort_values(['Data'],inplace=True)

    displayDf = df

    return rawdf, df, displayDf

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
st.session_state['conn'] = conn

rawdf, df, displayDf = fetchDb(conn)

st.session_state['rawdf'] = rawdf
st.session_state['df'] = df
st.session_state['displayDf'] = displayDf

df, displayDf = drawSideBar(df, displayDf)

barChart = alt.Chart(displayDf).mark_bar().encode(
    x='Categoria',
    y='Valor',
    tooltip=['Gasto','Valor']
)
st.altair_chart(barChart,use_container_width=True)

displayDf['Data'] = displayDf['Data'].dt.strftime('%d/%m/%Y')
dfFormat = {'Valor':'R$ {:.2f}'}
for key, value in dfFormat.items():
    displayDf[key] = displayDf[key].apply(value.format)

# Print results.
st.dataframe(displayDf, use_container_width=True, hide_index=True)