import streamlit as st
import PyPDF2
import re
import pandas as pd
from datetime import datetime

# Funções auxiliares
from pdf_processing import extract_text_up_to_line, filter_exclude_lines, formatar_valor_brasileiro, extract_codes_and_agencia_conta_cnpj, extract_value_before_total

# URL da imagem
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"

# Código HTML e CSS para ajustar a largura da imagem e centralizar
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'

# Data de geração
data_geracao = datetime.now().strftime('%Y-%m-%d')
data_geracao2 = datetime.now().strftime('%d/%m/%Y')

# Exibir a imagem
st.markdown(html_code, unsafe_allow_html=True)

# Títulos e explicações
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

# Texto explicativo
st.write("Desconto Externo Militar - Extração dados PDF SIGPP para SIAFI")

# Interface para upload de arquivo PDF
uploaded_file = st.file_uploader("Faça o upload do primeiro arquivo PDF", type="pdf")

if uploaded_file is not None:
    start_pattern = "Natureza de Despesa: 11190000 - OUTRAS CONSIGNATARIAS"
    end_pattern_to_exclude = "Natureza de Despesa: 11199900 - DESCONTO INTERNO- APROPRIACAO UPAG"
    exclude_patterns = [
        "Relatório Emitido em",
        "Diretoria de Administração",
        "Subdiretoria",
        "Competência:",
        "Abrangência:",
        "Folha:",
        "Órgão:",
        "Módulo de PAGAMENTOS",
        "Natureza de Despesa:"
    ]

    # Processamento do primeiro PDF
    filtered_lines = extract_text_up_to_line(uploaded_file, start_pattern, end_pattern_to_exclude)
    filtered_lines = filter_exclude_lines(filtered_lines, exclude_patterns)
    
    # Extração de informações
    codes_agencias_contas_cnpjs = extract_codes_and_agencia_conta_cnpj(filtered_lines)
    valores = extract_value_before_total(filtered_lines)

    # Criação de DataFrames
    df_agencia_conta_cnpj = pd.DataFrame(codes_agencias_contas_cnpjs, columns=["Código", "Agência", "Conta", "CNPJ"])
    df_valores = pd.DataFrame(valores, columns=["Valor"])

    # Ajuste de índices
    max_len = max(len(df_agencia_conta_cnpj), len(df_valores))
    df_agencia_conta_cnpj = df_agencia_conta_cnpj.reindex(range(max_len))
    df_valores = df_valores.reindex(range(max_len))

    # Concatenar os DataFrames
    df_final = pd.concat([df_agencia_conta_cnpj, df_valores], axis=1)

    # Exibir o DataFrame
    st.subheader("Resultados Extraídos")
    st.dataframe(df_final)

    # Soma os valores
    if not df_final.empty:
        total_valor_soma = df_final["Valor"].sum()
        st.success(f"Valor total DESCONTO EXTERNO - SIGPP: {formatar_valor_brasileiro(total_valor_soma)}")

    # Solicitar novo upload para a junção de dados
    st.write("Agora, faça o upload do segundo arquivo PDF para realizar a junção dos dados com os valores extraídos.")
    uploaded_file_banco = st.file_uploader("Upload do arquivo do banco (para junção)", type="pdf")

    if uploaded_file_banco is not None:
        # Aqui você pode adicionar a lógica de leitura do segundo PDF, para realizar a junção com os dados extraídos do primeiro
        # Para simplificação, vou mostrar apenas como você faria a junção com os DataFrames

        # Exemplo do seu código de junção após ter extraído dados do segundo PDF (df_banco_clean deve ser carregado)
        # Vamos simular um DataFrame "df_banco_clean" para a junção, você pode ajustar conforme necessário.
        df_banco_clean = pd.DataFrame({
            'Código': ['1234', '5678'],  # exemplo de códigos
            'Banco Agência Conta': ['1234-5678-1234', '5678-1234-5678']  # exemplo de dados do banco
        })
        
        # Realizar a junção
        df_completo = pd.merge(df_final, df_banco_clean[['Código', 'Banco Agência Conta']], on='Código', how='left')

        # Removendo duplicatas
        df_completo = df_completo.drop_duplicates(subset=['Código'])

        # Renomeando as colunas
        df_completo.rename(columns={'Banco Agência Conta': 'bco', 'Agência': 'agencia', 'Conta': 'conta', 'CNPJ': 'cnpj', 'Valor': 'valor'}, inplace=True)

        # Limpeza de dados
        df_completo['conta'] = df_completo['conta'].str.replace('-', '', regex=False)
        df_completo['agencia'] = df_completo['agencia'].apply(lambda x: x.split('-')[0].zfill(4) + '-' + x.split('-')[1] if isinstance(x, str) and '-' in x else x)
        df_completo['agencia'] = df_completo['agencia'].str[:4]

        # Exibir o DataFrame resultante
        st.subheader("DataFrame Completo com Dados Junção Banco")
        st.dataframe(df_completo)

        # Somar todos os valores
        total_valor = df_completo['valor'].sum()
        st.success(f"Valor Total Desconto Externo (com Junção): {formatar_valor_brasileiro(total_valor)}")
