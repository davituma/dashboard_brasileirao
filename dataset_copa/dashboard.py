import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Copa do Mundo - Análise Estatística",
    page_icon="📊",
    layout="wide"
)

# --- CARREGANDO OS DADOS TRATADOS ---
try:
    df_cups = pd.read_csv('WorldCups_tratado.csv')
    df_matches = pd.read_csv('WorldCupMatches_tratado.csv')
except FileNotFoundError:
    st.error("Arquivos CSV tratados não encontrados!")
    st.stop()

# --- TÍTULO DO DASHBOARD ---
st.title("📊 Análise Estatística da Copa do Mundo de Futebol")
st.markdown("Dashboard criado para a disciplina de Estatística, aplicando conceitos de média, mediana, probabilidade e visualização de dados.")
st.markdown("---")


# --- SEÇÃO 1: MÉDIA, MEDIANA E DESVIO PADRÃO ---
st.header("Análise Descritiva: Gols Marcados por Copa")
st.markdown("Analisando a distribuição do total de gols em cada edição do torneio.")

# Cálculos
total_gols_por_copa = df_cups['GoalsScored']
media_gols = total_gols_por_copa.mean()
mediana_gols = total_gols_por_copa.median()
desvio_padrao_gols = total_gols_por_copa.std()

# Exibindo as métricas
col1, col2, col3 = st.columns(3)
col1.metric("Média de Gols por Copa", f"{media_gols:.2f}")
col2.metric("Mediana de Gols por Copa", f"{mediana_gols:.0f}")
col3.metric("Desvio Padrão", f"{desvio_padrao_gols:.2f}")

# Gráfico: Histograma com Plotly
fig_hist_gols = px.histogram(
    df_cups,
    x='GoalsScored',
    nbins=10,
    title='Distribuição do Total de Gols por Edição da Copa do Mundo',
    labels={'GoalsScored': 'Total de Gols Marcados'}
)
fig_hist_gols.update_layout(bargap=0.1)
st.plotly_chart(fig_hist_gols, use_container_width=True)

with st.expander("Ver análise do Boxplot"):
    fig_box_gols = px.box(df_cups, y='GoalsScored', title='Boxplot do Total de Gols por Copa', points='all')
    st.plotly_chart(fig_box_gols, use_container_width=True)
    st.write("O boxplot nos ajuda a visualizar a mediana (a linha no meio da caixa), os quartis (as bordas da caixa), e possíveis outliers (pontos individuais).")

st.markdown("---")


# --- SEÇÃO 2: DADOS QUANTITATIVOS E QUALITATIVOS ---
st.header("Análise de Dados Quantitativos e Qualitativos")

# Gráfico Qualitativo: Campeões por País
st.subheader("Maiores Campeões (Dados Qualitativos)")

# Preparamos os dados como antes
campeoes = df_cups['Winner'].value_counts().reset_index()
campeoes.columns = ['País', 'Títulos']

# --- ADIÇÃO DAS CORES PERSONALIZADAS ---
# 1. Criamos nosso dicionário de cores customizado
country_colors = {
    'Brazil': '#FFD700',      # Amarelo Ouro
    'Germany': '#000000',      # Preto
    'Italy': '#009246',       # Verde
    'Argentina': '#75AADB',    # Azul Celeste
    'France': '#0055A4',      # Azul
    'Uruguay': '#59A7E1',     # Azul Celeste
    'England': '#CE1124',      # Vermelho
    'Spain': '#AA151B'        # Vermelho
}

# 2. Modificamos o gráfico para usar o dicionário de cores
fig_bar_campeoes = px.bar(
    campeoes,
    x='País',
    y='Títulos',
    title='Número de Títulos da Copa do Mundo por País',
    text_auto=True,
    color='País',  # Diz ao Plotly para colorir com base na coluna 'País'
    color_discrete_map=country_colors # Diz ao Plotly para usar nosso dicionário
).update_xaxes(categoryorder='total descending')

# Remove a legenda de cores, pois é redundante
fig_bar_campeoes.update_layout(showlegend=False)

st.plotly_chart(fig_bar_campeoes, use_container_width=True)


# Gráfico Quantitativo: Evolução do Público
st.subheader("Evolução do Público Total (Dados Quantitativos)")
fig_line_publico = px.line(
    df_cups,
    x='Year',
    y='Attendance',
    hover_data=['Country'],
    title='Evolução do Público Total por Edição (Passe o mouse para ver o país-sede)',
    markers=True,
    labels={'Year': 'Ano', 'Attendance': 'Público Total', 'Country': 'País-Sede'}
)
st.plotly_chart(fig_line_publico, use_container_width=True)

st.markdown("---")


# --- SEÇÃO 3: PROBABILIDADE ---
st.header("Análise de Probabilidade")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Probabilidade de um País ser Campeão")
    prob_campeao = df_cups['Winner'].value_counts(normalize=True).reset_index()
    prob_campeao.columns = ['País', 'Probabilidade']
    prob_campeao['Probabilidade'] = (prob_campeao['Probabilidade'] * 100).round(2)
    st.dataframe(prob_campeao)
    st.write("Calculado com base na frequência histórica de vitórias.")

with col2:
    st.subheader("Probabilidade de Partidas com Muitos Gols")
    df_matches['Total Goals'] = df_matches['Home Team Goals'] + df_matches['Away Team Goals']
    
    prob_mais_de_2_gols = (df_matches['Total Goals'] > 2.5).mean()
    st.metric("P(Total de Gols > 2.5)", f"{prob_mais_de_2_gols:.2%}")
    
    prob_zero_a_zero = (df_matches['Total Goals'] == 0).mean()
    st.metric("P(Placar = 0x0)", f"{prob_zero_a_zero:.2%}")

st.markdown("---")

# --- SEÇÃO 4: PROBABILIDADE CONDICIONAL ---
st.header("Análise de Probabilidade Condicional")
st.markdown("Qual a probabilidade de um evento ocorrer, **dado que** outro evento já ocorreu?")

# Probabilidade de ser campeão jogando em casa
st.subheader("P(Ser Campeão | Jogando em Casa)")
pais_sede_foi_campeao = (df_cups['Country'] == df_cups['Winner'])
prob_sede_campeao = pais_sede_foi_campeao.mean()

st.metric("Probabilidade de um país-sede vencer a Copa", f"{prob_sede_campeao:.2%}")
st.write(f"Das {len(df_cups)} Copas do Mundo, em {pais_sede_foi_campeao.sum()} ocasiões o país-sede foi o campeão.")

with st.expander("Ver os países que venceram em casa"):
    st.dataframe(df_cups[pais_sede_foi_campeao][['Year', 'Country', 'Winner']])