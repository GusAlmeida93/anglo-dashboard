import pandas as pd
import os
import streamlit as st
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import plotly.express as px
import datetime
import re


def get_data(user : str, password : str, site_url : str, relative_url_to_file : str) -> bytes:
    
    ctx_auth = AuthenticationContext(site_url)
    try:
        
        ctx_auth.acquire_token_for_user(user, password)
        ctx = ClientContext(site_url, ctx_auth)
        response = File.open_binary(ctx, relative_url_to_file)
        
        return response.content
    
    except Exception as e:
        raise e
    

def dataframe_cursos(df : pd.DataFrame) -> pd.DataFrame:
    

    cursos_columns = [column for column in df.columns if re.search('CURSOS', column) ]
    cursos_columns.append('ID')
    df_temp = df[cursos_columns]
    df_cursos = pd.melt(df_temp, id_vars=['ID'], var_name='UNIDADE', value_name='CURSO')
    df_cursos['UNIDADE'] = df_cursos['UNIDADE'].apply(lambda x : re.findall(r'^.*? (.*)', x)[0])
    df_cursos = df_cursos.dropna(subset=['CURSO']).reset_index(drop=True)
    
    return df_cursos

def dataframe_plantonistas(df : pd.DataFrame) -> pd.DataFrame:
        
    
    plantonistas_columns = [column for column in df.columns if re.search('PLANTONISTA', column) ]
    plantonistas_columns.append('ID')
    df_temp = df[plantonistas_columns]
    df_plantonistas = pd.melt(df_temp, id_vars=['ID'], var_name='PLANTÃO', value_name='PLANTONISTA')
    df_plantonistas['PLANTÃO'] = df_plantonistas['PLANTÃO'].apply(lambda x : re.findall(r'\((.*?)\)', x)[0])
    df_plantonistas = df_plantonistas.dropna(subset=['PLANTONISTA']).reset_index(drop=True)
        
    return df_plantonistas



#user = os.environ['user']
#password = os.environ['password']
#site_url = os.environ['site_url']
#relative_url_to_file = os.environ['relative_url_to_file']

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

df = pd.read_parquet('data.parquet')
df['DATA'] = pd.to_datetime(df['DATA']).dt.date
columns = [column.replace('\n','') for column in df.columns]
df.columns = columns

df_plantonistas = dataframe_plantonistas(df)

with st.sidebar:
    start_date = st.date_input('Data Inicial', today)
    end_date = st.date_input('Data Final', tomorrow)
    disciplinas = st.multiselect('DISCIPLINA', sorted(df['DISCIPLINA'].unique()))
    plantonistas = st.multiselect('PLANTONISTAS', sorted(df_plantonistas['PLANTONISTA'].unique()))


df_filter = df[(df['DATA'] >= start_date) & (df['DATA'] <= end_date)]

df_filter = df_filter.merge(df_plantonistas[['ID', 'PLANTONISTA']], on='ID', how='left')

df_filter = df_filter[df_filter['PLANTONISTA'].isin(plantonistas)]

dfg_plantao = df_filter[['ID','PLANTÃO']].groupby(['PLANTÃO'], as_index=False).count()

fig_plantao = px.pie(dfg_plantao, values='ID', names='PLANTÃO', title='Qtde atendimentos por plantão')

st.plotly_chart(fig_plantao)

dfg_unidade = df_filter[['ID','UNIDADE DO ALUNO']].groupby(['UNIDADE DO ALUNO'], as_index=False).count()

fig_unidade = px.bar(dfg_unidade, x='UNIDADE DO ALUNO', y='ID')

st.plotly_chart(fig_unidade)

