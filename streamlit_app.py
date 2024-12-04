
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título do aplicativo
st.title("Análise de Promoções e Produtos")
st.sidebar.header("Configurações")

# Upload de arquivo CSV
uploaded_file = st.sidebar.file_uploader("Faça o upload do arquivo de dados", type=["csv"])

if uploaded_file is not None:
    # Carregar os dados
    data = pd.read_csv(uploaded_file)

    # Limpeza e Tratamento Inicial
    data.columns = data.columns.str.lower().str.strip()  # Padronizando os nomes das colunas

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

    # Receita Total por Canal
    st.write("### Receita Total por Canal")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    summary.groupby('cod_canal')['total_receita'].sum().plot(kind='bar', ax=ax1)
    ax1.set_title("Receita Total por Canal")
    ax1.set_ylabel("Receita Total")
    ax1.set_xlabel("Canal")
    st.pyplot(fig1)

    # Percentual Médio de Desconto por Categoria
    st.write("### Percentual Médio de Desconto por Categoria")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    summary.groupby('des_categoria_material')['desconto_medio'].mean().plot(kind='bar', ax=ax2)
    ax2.set_title("Percentual Médio de Desconto por Categoria")
    ax2.set_ylabel("Percentual Médio de Desconto")
    ax2.set_xlabel("Categoria")
    st.pyplot(fig2)

    # Receita Líquida por Ciclo
    st.write("### Receita Líquida por Ciclo")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    summary.groupby('cod_ciclo')['receita_liquida'].sum().plot(kind='line', marker='o', ax=ax3)
    ax3.set_title("Receita Líquida por Ciclo")
    ax3.set_ylabel("Receita Líquida")
    ax3.set_xlabel("Ciclo")
    ax3.grid(True)
    st.pyplot(fig3)

else:
    st.info("Por favor, faça o upload de um arquivo CSV para começar a análise.")
