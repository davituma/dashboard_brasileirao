import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Copa do Mundo",
    page_icon="⚽",
    layout="wide"
)

# --- TÍTULO DO DASHBOARD ---
st.title("🏆 Dashboard Histórico da Copa do Mundo de Futebol")

# --- CARREGANDO OS DADOS TRATADOS ---
try:
    df_cups = pd.read_csv('WorldCups_tratado.csv')
    df_matches = pd.read_csv('WorldCupMatches_tratado.csv')
    df_players = pd.read_csv('WorldCupPlayers_tratado.csv')
except FileNotFoundError:
    st.error("Arquivos CSV tratados não encontrados! Verifique se os arquivos .csv estão na mesma pasta que o seu script `dashboard.py`.")
    st.stop()

st.markdown("---") # Adiciona uma linha divisória

# --- ANÁLISE 1: MAPA INTERATIVO DE TÍTULOS MUNDIAIS ---
st.header("🗺️ Mapa de Títulos Mundiais")

# 1. Preparar os dados para o mapa
titulos_por_pais = df_cups['Winner'].value_counts().reset_index()
titulos_por_pais.columns = ['Country', 'Titles']

# 2. Obter os códigos ISO dos países para o Plotly
iso_codes = px.data.gapminder()[['country', 'iso_alpha']].drop_duplicates()

# 3. Corrigir nomes de países para compatibilidade
correcoes_nomes = {"England": "United Kingdom", "USA": "United States"}
titulos_por_pais['Country'] = titulos_por_pais['Country'].replace(correcoes_nomes)

# 4. Juntar os dados de títulos com os códigos ISO
df_mapa = pd.merge(
    left=titulos_por_pais,
    right=iso_codes,
    left_on='Country',
    right_on='country',
    how='left'
)

# 5. Desenhar o mapa com Plotly Express
fig = px.choropleth(
    df_mapa,
    locations="iso_alpha",
    color="Titles",
    hover_name="Country",
    color_continuous_scale=px.colors.sequential.YlOrRd,
    title="Países Campeões da Copa do Mundo"
)

# Melhorar o layout do mapa
fig.update_geos(
    showcountries=True,
    showcoastlines=True,
    showland=True, landcolor="lightgray",
    showocean=True, oceancolor="lightblue"
)
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

# 6. Exibir o mapa no dashboard
st.plotly_chart(fig, use_container_width=True)


st.markdown("---")