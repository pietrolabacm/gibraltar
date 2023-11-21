import altair as alt
import streamlit as st
import pandas as pd
import datetime as dt
from streamlit_echarts import st_echarts
from PIL import Image
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from Sumario import fetchDb

st.set_page_config(page_title='Gibraltar Registry', page_icon=':bar_chart:',
                   layout='wide')

monthsDict = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
        'julho':7,'agosto':8, 'setembro':9, 'outubro':10, 'novembro':11,
        'dezembro':12}

def drawSideBar(df, displayDf):
    with st.sidebar:
        st.image('./abacus.png')
        selectMonth = st.selectbox('Mês', list(monthsDict.keys()),
                                   index=dt.datetime.now().month-1)
        displayDf = displayDf.loc[(displayDf['Data'].dt.month==monthsDict[selectMonth])]
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
    
conn = st.session_state['conn']
rawdf, df, displayDf = fetchDb(conn)

monthsDict = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
              'julho':7,'agosto':8, 'setembro':9, 'outubro':10, 'novembro':11,
              'dezembro':12}

df, displayDf = drawSideBar(df, displayDf)

col1,col2,col3 = st.columns(3)
col1.metric('Total','R$ %.2f'%displayDf['Valor'].sum())
col2.metric('Mercado','R$ %.2f'%displayDf.query('Categoria=="Mercado"')['Valor'].sum())
col3.metric('Treatos','R$ %.2f'%displayDf.query('Categoria=="Treatos"')['Valor'].sum())

#pxChart = px.bar(displayDf,x='Categoria',y='Valor')
#st.write(pxChart)

barChartMonth = alt.Chart(displayDf).mark_bar().encode(
    x='Categoria',
    y='Valor',
    #tooltip=['Gasto','Valor'],
    color='Categoria'
)
st.altair_chart(barChartMonth,use_container_width=True)

colList = list(st.columns(len(set(displayDf['Categoria']))))
for i, col in zip(set(displayDf['Categoria']),colList):
    with col:
        barChart = alt.Chart(displayDf.query('Categoria=="%s"'%
                                             i)).mark_bar().encode(
            x=alt.X('Gasto',axis=None),
            y=alt.Y('Valor',scale=alt.Scale(domain=[0,displayDf['Valor'].max()])),
            tooltip=['Gasto','Valor'],
            color='Gasto'
        ).properties(title=i)
        st.altair_chart(barChart,use_container_width=True)

##legendSel = alt.selection_point(fields=['Categoria'], bind='legend')
#chartSel = alt.selection_multi()
#horChart = alt.Chart(displayDf,height=300).mark_bar(height=40).encode(
#    x='Valor',
#    y='Categoria',
#    color=alt.condition(chartSel, 'Gasto', alt.value('lightgray'))
#).add_params(chartSel)
#st.altair_chart(horChart,use_container_width=True)

displayDf['Data'] = displayDf['Data'].dt.strftime('%d/%m/%Y')
dfFormat = {'Valor':'R$ {:.2f}'}
for key, value in dfFormat.items():
    displayDf[key] = displayDf[key].apply(value.format)

# Print results.
st.dataframe(displayDf, use_container_width=True, hide_index=True)