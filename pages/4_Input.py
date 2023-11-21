import streamlit as st
import streamlit.components.v1 as components
from Sumario import fetchDb

st.set_page_config(page_title='Gibraltar Registry', page_icon=':bar_chart:')

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

conn = st.session_state['conn']
rawdf, df, displayDf = fetchDb(conn)

valor = st.number_input('Valor',format='%.2f')
data = st.date_input('Data',format='DD/MM/YYYY')
gasto = st.text_input('Gasto')
categoria = st.selectbox('Categoria', set(df['Categoria']))
pagador = st.selectbox('Pagador', set(df['Pagador']))
cartao = st.selectbox('$', set(df['$']))

if st.button('Submit'):
    inputIndex = displayDf.index[-1]+1
    rawdf.loc[inputIndex] = [data,gasto,categoria,pagador,cartao,valor]
    rawdf = conn.update(
        worksheet = 'db',
        data=rawdf
    )
    st.cache_data.clear()
    st.session_state['counter']+=1
    st.success('%s submitted' % gasto)

components.html(
    f"""
        <div></div>
        <p>{st.session_state['counter']}</p>
        <script>
            var input = window.parent.document.querySelectorAll("input[type=number]");

            for (var i = 0; i < input.length; ++i) {{
                input[i].focus();
            }}
    </script>
    """,
    height=1
)