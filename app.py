import pandas as pd
import os
import streamlit as st
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import plotly.express as px
import datetime


def get_data(user : str, password : str, site_url : str, relative_url_to_file : str) -> bytes:
    
    ctx_auth = AuthenticationContext(site_url)
    try:
        
        ctx_auth.acquire_token_for_user(user, password)
        ctx = ClientContext(site_url, ctx_auth)
        response = File.open_binary(ctx, relative_url_to_file)
        
        return response.content
    
    except Exception as e:
        raise e


user = os.environ['user']
password = os.environ['password']
site_url = os.environ['site_url']
relative_url_to_file = os.environ['relative_url_to_file']

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start_date = st.date_input('Start date', today)
end_date = st.date_input('End date', tomorrow)

df = pd.read_parquet('data.parquet')
df_filter = df[(df['DATA'] >= start_date) & (df['DATA'] <= end_date)]

dfg_plantao = df_filter[['ID','PLANTÃO']].groupby(['PLANTÃO'], as_index=False).count()

fig_plantao = px.pie(dfg_plantao, values='ID', names='PLANTÃO', title='Qtde atendimentos por plantão')

st.plotly_chart(fig_plantao)

dfg_unidade = df_filter[['ID','UNIDADE DO ALUNO']].groupby(['UNIDADE DO ALUNO'], as_index=False).count()

fig_unidade = px.bar(dfg_unidade, x='UNIDADE DO ALUNO', y='ID')

st.plotly_chart(fig_unidade)

