import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Copa do Mundo",
    page_icon="⚽",
    layout="wide"
)

# --- CARREGANDO OS DADOS TRATADOS ---
try:
    df_cups = pd.read_csv('WorldCups_tratado.csv')
    df_matches = pd.read_csv('WorldCupMatches_tratado.csv')
    df_players = pd.read_csv('WorldCupPlayers_tratado.csv')
except FileNotFoundError:
    st.error("Arquivos CSV tratados não encontrados! Certifique-se de que os arquivos .csv estão na mesma pasta que o seu script `dashboard.py`.")
    st.stop()

# --- PREPARAÇÃO DE DADOS AUTOMATIZADA ---
country_name_mapping = {
    'Soviet Union': 'Russia', 'Czechoslovakia': 'Czech Republic',
    'Germany FR': 'Germany', 'German DR': 'Germany', 'Zaire': 'DR Congo'
}
# Aplicar mapeamento aos dataframes relevantes
df_matches['Home Team Name'] = df_matches['Home Team Name'].replace(country_name_mapping)
df_matches['Away Team Name'] = df_matches['Away Team Name'].replace(country_name_mapping)
df_cups['Winner'] = df_cups['Winner'].replace(country_name_mapping)
df_cups['Runners-Up'] = df_cups['Runners-Up'].replace(country_name_mapping)

all_countries = sorted(pd.concat([df_matches['Home Team Name'], df_matches['Away Team Name']]).unique())

map_name_initials = pd.concat([
    df_matches[['Home Team Name', 'Home Team Initials']].rename(columns={'Home Team Name': 'Country', 'Home Team Initials': 'Initials'}),
    df_matches[['Away Team Name', 'Away Team Initials']].rename(columns={'Away Team Name': 'Country', 'Away Team Initials': 'Initials'})
]).drop_duplicates().set_index('Country')['Initials']


# --- LAYOUT DO DASHBOARD ---

st.title("🏆 Dashboard Histórico da Copa do Mundo de Futebol")
st.markdown("---")

# --- MAPA MUNDI ---
st.header("🗺️ Mapa de Títulos Mundiais")
# (O código do mapa continua o mesmo)
titulos_por_pais = df_cups['Winner'].value_counts().reset_index()
titulos_por_pais.columns = ['Country', 'Titles']
iso_codes = px.data.gapminder()[['country', 'iso_alpha']].drop_duplicates()
correcoes_nomes_mapa = {"England": "United Kingdom", "USA": "United States"}
titulos_por_pais['Country'] = titulos_por_pais['Country'].replace(correcoes_nomes_mapa)
df_mapa = pd.merge(left=titulos_por_pais, right=iso_codes, left_on='Country', right_on='country', how='left')
fig = px.choropleth(df_mapa, locations="iso_alpha", color="Titles", hover_name="Country",
                    color_continuous_scale=px.colors.sequential.YlOrRd, projection="natural earth")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- SEÇÃO DE ANÁLISE DETALHADA ---
st.header("🔍 Análise Detalhada por País")
selected_country = st.selectbox("Selecione um país para ver suas estatísticas", all_countries)

# --- LÓGICA PARA EXIBIR ESTATÍSTICAS DINAMICAMENTE ---
if selected_country:
    # Filtrar os dados para as partidas do país selecionado
    matches_country = df_matches[
        (df_matches['Home Team Name'] == selected_country) | (df_matches['Away Team Name'] == selected_country)
    ]

    # --- ANÁLISE GERAL ---
    st.subheader("Estatísticas Gerais")
    total_jogos = len(matches_country)
    
    # Calcular vitórias, empates e derrotas
    vitorias = 0
    for index, row in matches_country.iterrows():
        if row['Home Team Name'] == selected_country:
            if row['Home Team Goals'] > row['Away Team Goals']: vitorias += 1
        elif row['Away Team Name'] == selected_country:
            if row['Away Team Goals'] > row['Home Team Goals']: vitorias += 1
            
    total_titulos = len(df_cups[df_cups['Winner'] == selected_country])
    total_vices = len(df_cups[df_cups['Runners-Up'] == selected_country])

    # Exibir as métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏆 Títulos", total_titulos)
    col2.metric("🥈 Vices", total_vices)
    col3.metric("🏟️ Partidas Jogadas", total_jogos)
    col4.metric("✅ Vitórias", vitorias)
    
    st.markdown("---")

    # --- ANÁLISE DE ARTILHARIA ---
    st.subheader("Maiores Artilheiros do País em Copas")
    country_initials = map_name_initials.get(selected_country)
    if country_initials:
        artilheiros = df_players[
            (df_players['Team Initials'] == country_initials) & (df_players['GoalsScored'] > 0)
        ]
        if not artilheiros.empty:
            ranking_artilheiros = artilheiros.groupby('Player Name')['GoalsScored'].sum().sort_values(ascending=False).reset_index()
            st.dataframe(ranking_artilheiros.head(10))
        else:
            st.info(f"Não há registros de gols para {selected_country} neste dataset.")
    else:
        st.warning(f"Não foi possível encontrar as iniciais para '{selected_country}' e calcular a artilharia.")