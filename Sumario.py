import altair as alt
import streamlit as st
import pandas as pd
import datetime as dt
from streamlit_echarts import st_echarts
from PIL import Image
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title='Gibraltar Registry', page_icon=':bar_chart:',
                   layout='wide')

monthsDict = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
        'julho':7,'agosto':8, 'setembro':9, 'outubro':10, 'novembro':11,
        'dezembro':12}

invMonthDict = {v: k for k, v in monthsDict.items()}

def drawSideBar(df, displayDf):
    with st.sidebar:
        st.image('./abacus.png')
        selectYear = st.selectbox('Ano', [2023])
        displayDf = displayDf.loc[(displayDf['Data'].dt.year==selectYear)]
        #mont only for now
        #selectDate = st.date_input('Data',
        #                            (dt.date(2023,1,1),dt.date(2023,12,31)),
        #                            dt.date(2023,1,1),
        #                            dt.date(2023,12,31),
        #                            format='DD/MM/YYYY')
        categoriaSelect = st.multiselect('Categoria', set(df['Categoria'].values))
        gastoSelect = st.multiselect('Gasto',set(df['Gasto'].values))
        pagadorSelect = st.multiselect('Pagador',set(df['Pagador'].values))

        
        #Month only for now
        #if len(selectDate)==1:
        #    displayDf = displayDf.loc[(displayDf['Data'].dt.date>=selectDate[0])]
        #if len(selectDate)>1:
        #    displayDf = displayDf.loc[(displayDf['Data'].dt.date>=selectDate[0]) &
        #                        (displayDf['Data'].dt.date<=selectDate[1])]
            
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

col1,col2,col3 = st.columns(3)
col1.metric('Total','R$ %.2f'%displayDf['Valor'].sum())
col2.metric('Mercado','R$ %.2f'%displayDf.query('Categoria=="Mercado"')['Valor'].sum())
col3.metric('Treatos','R$ %.2f'%displayDf.query('Categoria=="Treatos"')['Valor'].sum())

#legendSel = alt.selection_point(fields=['Categoria'], bind='legend')

displayDfHor = displayDf
#displayDfHor['Mes'] = [i.month for i in displayDf['Data']]
#displayDfHor = displayDf.resample(rule='M', on='Data')['Valor'].sum().reset_index()
displayDfHor['Mes'] = displayDfHor['Data'].dt.to_period('M').astype('datetime64[M]')
displayDfHor = displayDfHor.groupby(['Mes','Categoria']).sum().reset_index()
#displayDfHor = displayDfHor.sort_values('Mes',ascending=False)
#displayDfHor = displayDfHor.replace(invMonthDict)

chartSel = alt.selection_multi()
horChart = alt.Chart(displayDfHor,height=300).mark_bar(size=40).encode(
    x='Valor',
    y='Mes',
    color=alt.condition(chartSel, 'Categoria', alt.value('lightgray'))
).add_params(chartSel)
st.altair_chart(horChart,use_container_width=True)

displayDf['Data'] = displayDf['Data'].dt.strftime('%d/%m/%Y')
dfFormat = {'Valor':'R$ {:.2f}'}
for key, value in dfFormat.items():
    displayDf[key] = displayDf[key].apply(value.format)

# Print results.
st.dataframe(displayDf, use_container_width=True, hide_index=True)