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

# --- CUSTOMIZAÇÃO DO TEMA PARA FUNDO BRANCO ---
st.markdown(
    """
    <style>
    .main {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- CARREGANDO OS DADOS TRATADOS ---
try:
    df_cups = pd.read_csv('WorldCups_tratado.csv')
    df_matches = pd.read_csv('WorldCupMatches_tratado.csv')
    # Adicionando o carregamento do dataset de jogadores
    df_players = pd.read_csv('WorldCupPlayers_tratado.csv')
except FileNotFoundError:
    st.error("Arquivos CSV tratados não encontrados! Verifique se todos os arquivos .csv estão na pasta correta.")
    st.stop()

# --- PREPARAÇÃO E LIMPEZA ADICIONAL ---
# Unificar Alemanha Ocidental (FRG) para Alemanha (GER) no df_players
df_players.replace('FRG', 'GER', inplace=True)
# Criar colunas de análise no início para uso em múltiplas seções
df_matches['Total Goals'] = df_matches['Home Team Goals'] + df_matches['Away Team Goals']
df_players['Shirt Number'] = pd.to_numeric(df_players['Shirt Number'], errors='coerce')
df_players['YellowCards'] = df_players['Event'].str.count('Y')
df_players['RedCards'] = df_players['Event'].str.count('R')


# --- TÍTULO DO DASHBOARD ---
st.title("📊 Análise Estatística da Copa do Mundo de Futebol")
st.markdown("Dashboard criado para a disciplina de Estatística, aplicando conceitos de média, mediana, probabilidade e visualização de dados.")
st.markdown("---")


# --- SEÇÃO 1: MÉDIA, MEDIANA E DESVIO PADRÃO ---
st.header("Análise Descritiva: Gols Marcados por Copa")
st.markdown("Analisando a distribuição e a evolução do total de gols em cada edição do torneio.")

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

# Gráfico: Gráfico de Barras da Evolução de Gols (SUBSTITUIÇÃO DO HISTOGRAMA)
st.subheader("Evolução do Total de Gols Marcados por Edição")
fig_bar_gols_ano = px.bar(
    df_cups,
    x='Year',
    y='GoalsScored',
    title='Total de Gols Marcados em Cada Copa do Mundo',
    labels={'GoalsScored': 'Total de Gols Marcados', 'Year': 'Ano da Copa'},
    text_auto=True
)
fig_bar_gols_ano.update_traces(textposition='outside')
st.plotly_chart(fig_bar_gols_ano, use_container_width=True)
st.markdown("Este gráfico mostra a variação no total de gols marcados em cada Copa do Mundo, permitindo observar tendências ao longo do tempo, como os picos em edições específicas.")


# --- GRÁFICO COMBINADO: BOXPLOT + BEESWARM ---
with st.expander("Ver análise detalhada de Gols por Partida (Boxplot + Beeswarm)"):
    st.markdown("Este gráfico combina um Boxplot com um Beeswarm (Strip) plot. O Boxplot resume a distribuição de gols, enquanto cada ponto individual representa uma única partida, permitindo uma visualização completa da densidade e dos outliers.")
    
    # Preparar dados para o gráfico
    fases_principais = ['Group 1', 'Group 2', 'Group 3', 'Group 4', 'First round', 
                        'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    df_plot_combined = df_matches[df_matches['Stage'].isin(fases_principais)].copy()
    
    # Padronizar nomes das fases para português
    df_plot_combined['Stage'] = df_plot_combined['Stage'].replace({
        'Group 1': 'Fase de Grupos', 'Group 2': 'Fase de Grupos', 
        'Group 3': 'Fase de Grupos', 'Group 4': 'Fase de Grupos',
        'First round': 'Fase de Grupos',
        'Round of 16': 'Oitavas de Final',
        'Quarter-finals': 'Quartas de Final',
        'Semi-finals': 'Semifinais'
        # 'Final' já está correto
    })

    # Definir a ordem cronológica das fases para o eixo X
    ordem_fases = ['Fase de Grupos', 'Oitavas de Final', 'Quartas de Final', 'Semifinais', 'Final']

    fig_combined = px.box(
        df_plot_combined,
        x='Stage',
        y='Total Goals',
        color='Stage',
        points='all', # Adiciona os pontos (beeswarm) sobre o boxplot
        title='Distribuição de Gols por Fase do Torneio',
        labels={'Total Goals': 'Total de Gols na Partida', 'Stage': 'Fase do Torneio'},
        hover_data=['Home Team Name', 'Home Team Goals', 'Away Team Goals', 'Away Team Name', 'Year'],
        category_orders={'Stage': ordem_fases} # Aplica a ordem correta no eixo X
    )
    
    # Adicionar linha da média geral para referência
    media_geral_gols = df_matches['Total Goals'].mean()
    fig_combined.add_hline(y=media_geral_gols, line_dash="dot", 
                            annotation_text=f"Média Geral: {media_geral_gols:.2f}", 
                            annotation_position="bottom right")

    fig_combined.update_layout(showlegend=False)
    st.plotly_chart(fig_combined, use_container_width=True)


st.markdown("---")


# --- SEÇÃO 2: DADOS QUANTITATIVOS E QUALITATIVOS ---
st.header("Análise de Dados Quantitativos e Qualitativos")

# Gráfico Qualitativo: Campeões por País
st.subheader("Maiores Campeões (Dados Qualitativos)")

# Preparamos os dados como antes
campeoes = df_cups['Winner'].value_counts().reset_index()
campeoes.columns = ['País', 'Títulos']

# Dicionário de cores customizado
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

# Modificamos o gráfico para usar o dicionário de cores
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
    prob_mais_de_2_gols = (df_matches['Total Goals'] > 2.5).mean()
    st.metric("P(Total de Gols > 2.5)", f"{prob_mais_de_2_gols:.2%}")
    
    prob_zero_a_zero = (df_matches['Total Goals'] == 0).mean()
    st.metric("P(Placar = 0x0)", f"{prob_zero_a_zero:.2%}")

# Análise de Probabilidade por Posição
st.subheader("Probabilidade de Eventos por Posição (baseado na numeração da camisa)")

# Definir números de camisa para cada posição
atacantes_numeros = [7, 8, 9, 10, 11]
defensores_numeros = [2, 3, 4, 5, 6]

# Filtrar jogadores com número de camisa válido
jogadores_validos = df_players.dropna(subset=['Shirt Number'])

# Separar em dataframes de atacantes e defensores
df_atacantes = jogadores_validos[jogadores_validos['Shirt Number'].isin(atacantes_numeros)]
df_defensores = jogadores_validos[jogadores_validos['Shirt Number'].isin(defensores_numeros)]

# Calcular Probabilidades de Gol
total_gols_com_numeracao = jogadores_validos['GoalsScored'].sum()
gols_atacantes = df_atacantes['GoalsScored'].sum()
gols_defensores = df_defensores['GoalsScored'].sum()
prob_gol_atacante = (gols_atacantes / total_gols_com_numeracao) if total_gols_com_numeracao > 0 else 0
prob_gol_defensor = (gols_defensores / total_gols_com_numeracao) if total_gols_com_numeracao > 0 else 0

# Calcular Probabilidades de Cartão Amarelo
# A probabilidade aqui é o total de cartões dividido pelo total de "oportunidades" (jogadores em campo)
total_cartoes_atacantes = df_atacantes['YellowCards'].sum()
total_cartoes_defensores = df_defensores['YellowCards'].sum()
prob_cartao_atacante = (total_cartoes_atacantes / len(df_atacantes)) if len(df_atacantes) > 0 else 0
prob_cartao_defensor = (total_cartoes_defensores / len(df_defensores)) if len(df_defensores) > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("P(Gol | Camisa de Atacante)", f"{prob_gol_atacante:.2%}")
    st.metric("P(Cartão Amarelo | Camisa de Atacante)", f"{prob_cartao_atacante:.2%}")
with col2:
    st.metric("P(Gol | Camisa de Defensor)", f"{prob_gol_defensor:.2%}")
    st.metric("P(Cartão Amarelo | Camisa de Defensor)", f"{prob_cartao_defensor:.2%}")


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
st.markdown("---")


# --- NOVA SEÇÃO: HEATMAP DE CORRELAÇÃO ---
st.header("🔥 Heatmap de Correlação entre Variáveis do Torneio")
st.markdown("Este mapa de calor mostra a correlação de Pearson entre as principais variáveis numéricas das Copas. Valores próximos de 1 (vermelho escuro) indicam uma forte correlação positiva, enquanto valores próximos de -1 indicam uma forte correlação negativa. Valores próximos de 0 (cores claras) sugerem uma correlação fraca.")

# Selecionar e renomear as colunas para o heatmap
df_heatmap = df_cups[['GoalsScored', 'QualifiedTeams', 'MatchesPlayed', 'Attendance']].copy()
df_heatmap.rename(columns={
    'GoalsScored': 'Gols Marcados',
    'QualifiedTeams': 'Seleções Qualificadas',
    'MatchesPlayed': 'Partidas Jogadas',
    'Attendance': 'Público Total'
}, inplace=True)

# Calcular a matriz de correlação
corr = df_heatmap.corr()

# Criar o heatmap com Plotly
fig_heatmap = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    color_continuous_scale='RdBu_r', # Esquema de cores: Vermelho (positivo), Azul (negativo)
    title="Correlação entre Variáveis Numéricas das Copas"
)
st.plotly_chart(fig_heatmap, use_container_width=True)
st.markdown("---")


# --- SEÇÃO DE ESTATÍSTICAS DOS JOGADORES ---
st.header("🏆 Estatísticas dos Jogadores")

# Métricas gerais dos jogadores
total_jogadores = df_players['Player Name'].nunique()
total_gols_jogadores = df_players['GoalsScored'].sum()

col1, col2 = st.columns(2)
col1.metric("Total de Jogadores Únicos", f"{total_jogadores:,}".replace(",", "."))
col2.metric("Total de Gols Registrados (por jogadores)", f"{total_gols_jogadores:,}".replace(",", "."))

# Rankings
col1, col2 = st.columns(2)
with col1:
    st.subheader("Maiores Artilheiros de Todas as Copas")
    # Agrupamos por nome, somamos os gols e pegamos a primeira nacionalidade encontrada
    top_scorers = df_players.groupby('Player Name').agg(
        Nacionalidade=('Team Initials', 'first'),
        Gols=('GoalsScored', 'sum')
    ).sort_values(by='Gols', ascending=False).reset_index().head(10)
    
    # Reordenamos as colunas para melhor visualização
    top_scorers = top_scorers[['Player Name', 'Nacionalidade', 'Gols']]
    top_scorers.rename(columns={'Player Name': 'Jogador'}, inplace=True)
    st.dataframe(top_scorers)

with col2:
    st.subheader("Jogadores com Mais Cartões Amarelos")
    # Agrupamos por nome, somamos os cartões e pegamos a primeira nacionalidade
    top_yellow_cards = df_players.groupby('Player Name').agg(
        Nacionalidade=('Team Initials', 'first'),
        YellowCards=('YellowCards', 'sum')
    ).sort_values(by='YellowCards', ascending=False).reset_index().head(10)
    
    # Reordenamos as colunas e renomeamos para a exibição
    top_yellow_cards = top_yellow_cards[['Player Name', 'Nacionalidade', 'YellowCards']]
    top_yellow_cards.rename(columns={'Player Name': 'Jogador', 'YellowCards': 'Cartões Amarelos'}, inplace=True)
    st.dataframe(top_yellow_cards)
st.markdown("---")


# --- NOVA SEÇÃO: ANÁLISE INDIVIDUAL POR PAÍS ---
st.header("🔍 Análise Individual por País")

# Criar lista de países únicos para o seletor
paises_home = df_matches['Home Team Name'].dropna().unique()
paises_away = df_matches['Away Team Name'].dropna().unique()
lista_paises = sorted(list(set(paises_home) | set(paises_away)))
lista_paises.insert(0, "Selecione um país...")

# Criar a caixa de seleção
pais_selecionado = st.selectbox(
    "Escolha um país para ver suas estatísticas detalhadas:",
    options=lista_paises
)

# Se um país for selecionado, mostrar as estatísticas
if pais_selecionado != "Selecione um país...":
    st.subheader(f"Desempenho Histórico de {pais_selecionado} em Copas")

    # Filtrar todas as partidas do país selecionado
    df_pais = df_matches[
        (df_matches['Home Team Name'] == pais_selecionado) | 
        (df_matches['Away Team Name'] == pais_selecionado)
    ].copy()

    # --- 2. RESUMO ESTATÍSTICO ---
    st.subheader("📊 Resumo Estatístico")

    # Calcular dados por copa
    participacoes_anos = df_pais['Year'].unique()
    copas_disputadas = len(participacoes_anos)

    # Títulos
    if pais_selecionado == 'Germany':
        titulos = df_cups[(df_cups['Winner'] == 'Germany') | (df_cups['Winner'] == 'Germany FR')].shape[0]
    else:
        titulos = df_cups[df_cups['Winner'] == pais_selecionado].shape[0]

    # Agrupar estatísticas por ano/copa
    stats_por_copa = []
    for year in participacoes_anos:
        df_copa_ano = df_pais[df_pais['Year'] == year]
        
        gols_marcados = int(df_copa_ano[df_copa_ano['Home Team Name'] == pais_selecionado]['Home Team Goals'].sum() + \
                        df_copa_ano[df_copa_ano['Away Team Name'] == pais_selecionado]['Away Team Goals'].sum())
        
        gols_sofridos = int(df_copa_ano[df_copa_ano['Home Team Name'] == pais_selecionado]['Away Team Goals'].sum() + \
                        df_copa_ano[df_copa_ano['Away Team Name'] == pais_selecionado]['Home Team Goals'].sum())
        
        vitorias = df_copa_ano[
            ((df_copa_ano['Home Team Name'] == pais_selecionado) & (df_copa_ano['Home Team Goals'] > df_copa_ano['Away Team Goals'])) |
            ((df_copa_ano['Away Team Name'] == pais_selecionado) & (df_copa_ano['Away Team Goals'] > df_copa_ano['Home Team Goals']))
        ].shape[0]

        stats_por_copa.append({'Year': year, 'Gols Marcados': gols_marcados, 'Gols Sofridos': gols_sofridos, 'Vitórias': vitorias})
    
    df_stats_por_copa = pd.DataFrame(stats_por_copa)

    # Cálculos das métricas
    media_gols_marcados = df_stats_por_copa['Gols Marcados'].mean()
    mediana_gols_sofridos = df_stats_por_copa['Gols Sofridos'].median()
    desvio_padrao_vitorias = df_stats_por_copa['Vitórias'].std()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Copas Disputadas", copas_disputadas)
    col2.metric("Copas Vencidas", titulos)
    col3.metric("Média de Gols Marcados/Copa", f"{media_gols_marcados:.2f}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Mediana de Gols Sofridos/Copa", f"{mediana_gols_sofridos:.2f}")
    col2.metric("Desvio Padrão de Vitórias/Copa", f"{desvio_padrao_vitorias:.2f}")


    # --- 3. EVOLUÇÃO HISTÓRICA ---
    st.subheader("📈 Evolução Histórica")
    fig_gols_evolucao = px.line(
        df_stats_por_copa,
        x='Year',
        y='Gols Marcados',
        title=f'Evolução de Gols Marcados por {pais_selecionado} por Copa',
        markers=True,
        labels={'Year': 'Ano', 'Gols Marcados': 'Gols Marcados na Edição'}
    )
    st.plotly_chart(fig_gols_evolucao, use_container_width=True)

    # --- 4. DISTRIBUIÇÃO DE GOLS ---
    st.subheader("🥅 Distribuição de Gols Marcados por Copa")
    fig_hist_gols = px.histogram(
        df_stats_por_copa,
        x='Gols Marcados',
        title=f"Distribuição de Gols Marcados por {pais_selecionado} nas Copas",
        labels={'Gols Marcados': 'Total de Gols em uma Edição'},
        nbins=10
    )
    fig_hist_gols.add_vline(x=media_gols_marcados, line_dash="dot", annotation_text=f"Média: {media_gols_marcados:.2f}")
    st.plotly_chart(fig_hist_gols, use_container_width=True)


    # --- 5. PRINCIPAIS JOGADORES ---
    st.subheader(f"⭐ Maiores Artilheiros de {pais_selecionado}")
    
    # Mapear nome do país para sigla
    try:
        sigla_pais = df_matches[df_matches['Home Team Name'] == pais_selecionado]['Home Team Initials'].iloc[0]
        
        df_jogadores_pais = df_players[df_players['Team Initials'] == sigla_pais]
        artilheiros = df_jogadores_pais.groupby('Player Name')['GoalsScored'].sum().sort_values(ascending=False).reset_index().head(10)
        artilheiros = artilheiros[artilheiros['GoalsScored'] > 0] # Mostrar apenas quem marcou gols

        fig_artilheiros = px.bar(
            artilheiros,
            x='GoalsScored',
            y='Player Name',
            orientation='h',
            title=f'Maiores Artilheiros de {pais_selecionado} em Copas',
            labels={'Player Name': 'Jogador', 'GoalsScored': 'Total de Gols'},
            text_auto=True
        ).update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_artilheiros, use_container_width=True)

    except (IndexError, KeyError):
        st.warning(f"Não foi possível encontrar dados de artilheiros para {pais_selecionado}.")


    # --- 6. PROBABILIDADES ---
    st.subheader("🎲 Probabilidades")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Probabilidade de ser campeão**")
        prob_campeao = (titulos / copas_disputadas) if copas_disputadas > 0 else 0
        st.metric("P(Campeão)", f"{prob_campeao:.2%}")

    with col2:
        st.markdown("**P(Vencer | Jogando em Casa)**")
        copas_em_casa = df_cups[df_cups['Country'] == pais_selecionado]
        venceu_em_casa = copas_em_casa[copas_em_casa['Winner'] == pais_selecionado].shape[0]
        num_copas_em_casa = len(copas_em_casa)
        prob_vencer_em_casa = (venceu_em_casa / num_copas_em_casa) if num_copas_em_casa > 0 else 0
        st.metric("Probabilidade", f"{prob_vencer_em_casa:.2%}")
        st.caption(f"Baseado em {venceu_em_casa} título(s) em {num_copas_em_casa} copa(s) sediada(s).")


    # --- 7. COMPARAÇÃO COM OUTROS PAÍSES ---
    st.subheader("🆚 Comparação de Desempenho")
    
    # Boxplot comparando gols marcados
    paises_comparacao = ['Brazil', 'Germany', 'Argentina', 'Italy', 'France']
    if pais_selecionado not in paises_comparacao:
        paises_comparacao.append(pais_selecionado)
    
    df_comparacao_raw = df_matches[
        df_matches['Home Team Name'].isin(paises_comparacao) | 
        df_matches['Away Team Name'].isin(paises_comparacao)
    ]
    
    # Coletar gols por país e por copa
    lista_stats_comparacao = []
    for pais in paises_comparacao:
        df_pais_comp = df_comparacao_raw[(df_comparacao_raw['Home Team Name'] == pais) | (df_comparacao_raw['Away Team Name'] == pais)]
        anos_participacao_comp = df_pais_comp['Year'].unique()
        for ano in anos_participacao_comp:
            df_ano_comp = df_pais_comp[df_pais_comp['Year'] == ano]
            gols_marcados_comp = int(df_ano_comp[df_ano_comp['Home Team Name'] == pais]['Home Team Goals'].sum() + \
                                     df_ano_comp[df_ano_comp['Away Team Name'] == pais]['Away Team Goals'].sum())
            lista_stats_comparacao.append({'País': pais, 'Gols Marcados por Copa': gols_marcados_comp})

    df_stats_comparacao = pd.DataFrame(lista_stats_comparacao)

    fig_boxplot_comparacao = px.box(
        df_stats_comparacao,
        x='País',
        y='Gols Marcados por Copa',
        color='País',
        title='Comparativo de Gols Marcados por Copa entre Grandes Seleções',
        points='all'
    )
    fig_boxplot_comparacao.update_layout(showlegend=False)
    st.plotly_chart(fig_boxplot_comparacao, use_container_width=True)

