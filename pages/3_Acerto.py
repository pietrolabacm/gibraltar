import streamlit as st
import datetime as dt
import streamlit.components.v1 as components
from Sumario import fetchDb

st.set_page_config(page_title='Gibraltar Registry', page_icon=':bar_chart:')

conn = st.session_state['conn']
rawdf, df, displayDf = fetchDb(conn)

monthsDict = {'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,
              'julho':7,'agosto':8, 'setembro':9, 'outubro':10, 'novembro':11,
              'dezembro':12}

with st.sidebar:
    st.image('./abacus.png')
    selectMonth = st.selectbox('Mês', list(monthsDict.keys()),
                               index=dt.datetime.now().month-1)
    displayDf = displayDf.loc[(displayDf['Data'].dt.month==monthsDict[selectMonth])]

total = displayDf['Valor'].sum()
juliana = displayDf.query('Pagador=="Juliana"')['Valor'].sum()
pietro = displayDf.query('Pagador=="Pietro"')['Valor'].sum()

#c1,center,c2 = st.columns([0.25,0.5,0.25])
#with center:

col1,col2 = st.columns(2)
with col1:
    st.metric('Total','R$ %.2f'% total)
    st.image('./obedient.jpg',width= 200)
    
with col2:
    st.write('#')
    st.metric('Juliana','R$ %.2f'% juliana, delta='%.2f'%(-(total/2-juliana)))
    st.write('#')
    st.metric('Pietro','R$ %.2f'% pietro, delta='%.2f'%(-(total/2-pietro)),)

col1,col2, col3 = st.columns(3)
with col1:
    data = st.date_input('Data')
with col2:
    if juliana>pietro:
        pagador = 'Pietro'
    else:
        pagador = 'Juliana'
    st.selectbox('Pagador',[pagador],disabled=True)
with col3:
    if pagador == 'Julina':
        acertVal = -(total/2-juliana)
    else:
        acertVal = -(total/2-pietro)
    val = st.number_input('Valor',value=acertVal,disabled=True)
if st.button('Acertar'):
    st.write('%s %s %.2f X'%(data,pagador,acertVal))