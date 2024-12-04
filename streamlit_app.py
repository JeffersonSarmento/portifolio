import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título do aplicativo
st.title("Painel de Performance: Canais e Faturamento")
st.sidebar.header("Configurações")

# Upload de arquivo CSV
uploaded_file = st.sidebar.file_uploader("Faça o upload do arquivo de dados", type=["csv"])

if uploaded_file is not None:
    # Carregar os dados
    data = pd.read_csv(uploaded_file)

    # Limpeza e Tratamento Inicial
    data.columns = data.columns.str.lower().str.strip()  # Padronizando os nomes das colunas

    # Tratando a coluna 'cod_ciclo' para string sem vírgula
    data['cod_ciclo'] = data['cod_ciclo'].astype(str).str.replace(',', '')

    # Substituindo valores nulos em colunas financeiras com 0
    financial_cols = [
        'vlr_desconto_real', 'vlr_rbv_tabela_so_tt', 'vlr_rbv_real_so_tt',
        'vlr_preco_base', 'vlr_preco_venda', 'vlr_preco_tabela', 'vlr_desconto_real2'
    ]
    data[financial_cols] = data[financial_cols].fillna(0)

    # Criando métricas de análise
    data['vlr_receita_real'] = data['vlr_rbv_real_so_tt'] - data['vlr_desconto_real']
    data['percentual_desconto'] = (
        (data['vlr_desconto_real'] / data['vlr_rbv_tabela_so_tt']) * 100
    ).fillna(0)

    # Agregando informações para análise por canal, categoria e ciclo
    summary = data.groupby(['cod_canal', 'des_categoria_material', 'cod_ciclo'], as_index=False).agg({
        'vlr_desconto_real': 'sum',
        'vlr_rbv_real_so_tt': 'sum',
        'vlr_receita_real': 'sum',
        'percentual_desconto': 'mean'
    }).rename(columns={
        'vlr_desconto_real': 'total_desconto',
        'vlr_rbv_real_so_tt': 'total_receita',
        'vlr_receita_real': 'receita_liquida',
        'percentual_desconto': 'desconto_medio'
    })

    # Exibição de tabela de resumo
    st.subheader("Resumo de Desempenho")
    st.dataframe(summary)

    # Gráficos
    st.subheader("Gráficos")

    # Gráfico 1: Receita Total por Canal
    st.write("### Receita Total por Canal")
    receita_por_canal = summary.groupby('cod_canal')['total_receita'].sum()
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars = ax1.bar(
        receita_por_canal.index,
        receita_por_canal.values,
        color='green',
        width=0.5  # Reduzindo a largura das barras
    )
    
    # Adicionando os valores ao final de cada barra
    for bar in bars:
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (0.01 * bar.get_height()),
            f"R${bar.get_height():,.2f}",  # Formatação como moeda
            ha='center',
            va='bottom',
            fontsize=10,
            color='black'
        )

    # Ajustando o eixo Y para incrementos regulares de 50 milhões
    max_value = receita_por_canal.max()
    step_size = 50_000_000  # Escala do eixo Y: 50 milhões
    ax1.set_yticks(range(0, int(max_value) + step_size, step_size))
    ax1.set_yticklabels([f"{int(tick / 1_000_000)}M" for tick in ax1.get_yticks()])

    # Títulos e rótulos
    ax1.set_title("Receita Total por Canal", fontsize=14)
    ax1.set_ylabel("Receita (em milhões)", fontsize=12)
    ax1.set_xlabel("Canal", fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Renderizando o gráfico no Streamlit
    st.pyplot(fig1)

    # Gráfico 2: Percentual Médio de Desconto por Categoria (Rosca)
    st.write("### Percentual Médio de Desconto por Categoria")
    desconto_por_categoria = summary.groupby('des_categoria_material')['desconto_medio'].mean()
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax2.pie(
        desconto_por_categoria,
        labels=desconto_por_categoria.index,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        colors=plt.cm.Paired.colors  # Usando uma paleta de cores diferente
    )
    circle = plt.Circle((0, 0), 0.70, color='white')
    fig2.gca().add_artist(circle)

    ax2.set_title("Percentual Médio de Desconto por Categoria")
    st.pyplot(fig2)

    # Gráfico 3: Receita Líquida por Ano
    st.write("### Receita Líquida por Ano")
    data['ano'] = data['cod_ciclo'].str[:4]
    receita_por_ano = data.groupby('ano')['vlr_receita_real'].sum().reset_index()
    receita_por_ano['vlr_receita_real'] = receita_por_ano['vlr_receita_real'] / 1_000_000

    fig3, ax3 = plt.subplots(figsize=(12, 6))
    bars = ax3.bar(
        receita_por_ano['ano'],
        receita_por_ano['vlr_receita_real'],
        color=plt.cm.tab10.colors
    )

    for bar in bars:
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{bar.get_height():.1f}M",
            ha='center',
            va='bottom'
        )

    ax3.set_title("Receita Líquida por Ano")
    ax3.set_ylabel("Receita Líquida (em milhões)")
    ax3.set_xlabel("Ano")
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig3)

    # Gráfico 4: Porcentagem de Vendas por Canal e Ano
    st.write("### Porcentagem de Vendas por Canal e Ano")
    receita_por_ano_canal = data.groupby(['ano', 'cod_canal'])['vlr_receita_real'].sum().reset_index()
    total_por_ano = receita_por_ano_canal.groupby('ano')['vlr_receita_real'].sum().reset_index()
    total_por_ano.rename(columns={'vlr_receita_real': 'total'}, inplace=True)
    receita_por_ano_canal = receita_por_ano_canal.merge(total_por_ano, on='ano')
    receita_por_ano_canal['percentual'] = (receita_por_ano_canal['vlr_receita_real'] / receita_por_ano_canal['total']) * 100

    fig4, ax4 = plt.subplots(figsize=(10, 6))
    canais = receita_por_ano_canal['cod_canal'].unique()
    anos = receita_por_ano_canal['ano'].unique()
    bar_width = 0.35
    x = range(len(anos))

    for i, canal in enumerate(canais):
        canal_data = receita_por_ano_canal[receita_por_ano_canal['cod_canal'] == canal]
        ax4.bar(
            [pos + i * bar_width for pos in x],
            canal_data['percentual'],
            bar_width,
            label=f"Canal {canal}"
        )
        for pos, perc in zip(x, canal_data['percentual']):
            ax4.text(
                pos + i * bar_width,
                perc + 1,
                f"{perc:.1f}%",
                ha='center',
                fontsize=10
            )

    ax4.set_xticks([pos + bar_width / 2 for pos in x])
    ax4.set_xticklabels(anos)
    ax4.set_title("Porcentagem de Vendas por Canal e Ano", fontsize=14)
    ax4.set_ylabel("Porcentagem (%)", fontsize=12)
    ax4.legend(title="Canais")
    ax4.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig4)

else:
    st.info("Por favor, faça o upload de um arquivo CSV para começar a análise.")
