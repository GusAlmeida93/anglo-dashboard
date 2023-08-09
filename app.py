import pandas as pd
import os
import streamlit as st
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import plotly.express as px


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

df = pd.read_parquet('data.parquet')

dfg_plantao = df[['ID','PLANTÃO']].groupby(['PLANTÃO'], as_index=False).count()

fig = px.pie(dfg_plantao, values='ID', names='PLANTÃO', title='Qtde atendimentos por plantão')

st.plotly_chart(fig)