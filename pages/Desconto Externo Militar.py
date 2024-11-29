import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import re

# Função para processar o PDF e extrair CNPJs e Conta Corrente
def processar_pdf(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Colocar o texto em uma linha só para facilitar a busca
    texto_completo = texto_completo.replace("\n", " ")

    # Debug: Mostrar o texto completo para diagnóstico
    st.subheader("Texto Extraído do PDF (primeiros 1000 caracteres):")
    st.text(texto_completo[:1000])  # Exibe os primeiros 1000 caracteres para diagnóstico

    # Expressão regular para procurar Conta Corrente e o CNPJ após ela
    conta_corrente_pattern = r"Conta Corrente:\s*(.*?)\s*CNPJ:\s*([\d]{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"

    # Encontrar todas as sequências de Conta Corrente e o respectivo CNPJ
    matches = re.findall(conta_corrente_pattern, texto_completo)

    # Criar listas para armazenar as informações de Conta Corrente e CNPJ
    conta_corrente_matches = [match[0] for match in matches]  # Parte 1 da correspondência: Conta Corrente
    cnpj_matches = [match[1] for match in matches]  # Parte 2 da correspondência: CNPJ

    # Criar o DataFrame com os CNPJs e Conta Corrente encontrados
    df = pd.DataFrame({
        "Conta Corrente": conta_corrente_matches,
        "CNPJ": cnpj_matches
    })

    # Garantir que a coluna "Conta Corrente" seja do tipo string
    df["Conta Corrente"] = df["Conta Corrente"].astype(str)

    # Excluir as linhas onde a "Conta Corrente" começa com "-"
    df = df[~df['Conta Corrente'].str.startswith('-')]

    # Excluir as linhas duplicadas com base no "CNPJ"
    df = df.drop_duplicates(subset="CNPJ")

    return df

# Função para processar o PDF e extrair Agências associadas aos CNPJs
def processar_agencias(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Colocar o texto em uma linha só para facilitar a busca
    texto_completo = texto_completo.replace("\n", " ")

    # Expressão regular para procurar Agência e o CNPJ após ela
    agencia_pattern = r"Agência:\s*(\d+)\s*Conta Corrente:\s*(.*?)\s*CNPJ:\s*([\d]{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"

    # Encontrar todas as sequências de Agência, Conta Corrente e o respectivo CNPJ
    matches = re.findall(agencia_pattern, texto_completo)

    # Criar listas para armazenar as informações de Agência, Conta Corrente e CNPJ
    agencia_matches = [match[0] for match in matches]  # Parte 1 da correspondência: Agência
    conta_corrente_matches = [match[1] for match in matches]  # Parte 2 da correspondência: Conta Corrente
    cnpj_matches = [match[2] for match in matches]  # Parte 3 da correspondência: CNPJ

    # Criar o DataFrame com as informações de Agência e CNPJ
    df_agencias = pd.DataFrame({
        "Agência": agencia_matches,
        "Conta Corrente": conta_corrente_matches,
        "CNPJ": cnpj_matches
    })

    # Garantir que a coluna "Conta Corrente" seja do tipo string
    df_agencias["Conta Corrente"] = df_agencias["Conta Corrente"].astype(str)

    # Excluir as linhas onde a "Conta Corrente" começa com "-"
    df_agencias = df_agencias[~df_agencias['Conta Corrente'].str.startswith('-')]

    # Excluir as linhas duplicadas com base no "CNPJ"
    df_agencias = df_agencias.drop_duplicates(subset="CNPJ")

    return df_agencias

# Interface no Streamlit
st.title("Extração de CNPJ, Conta Corrente e Agência do PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")
    
    # Processar o PDF e exibir os resultados
    df_resultado = processar_pdf(uploaded_file)
    st.write("### CNPJs e Conta Corrente Extraídos:")
    st.dataframe(df_resultado)

    # Processar Agências e exibir os resultados
    df_agencias_resultado = processar_agencias(uploaded_file)
    st.write("### Agências e CNPJs Extraídos:")
    st.dataframe(df_agencias_resultado)

    # Adicionar opção de download para os DataFrames em CSV
    csv_resultado = df_resultado.to_csv(index=False)
    st.download_button(
        label="Baixar CNPJs e Conta Corrente em CSV",
        data=csv_resultado,
        file_name="cnpj_conta_corrente_extraidos.csv",
        mime="text/csv",
    )
    
    csv_agencias = df_agencias_resultado.to_csv(index=False)
    st.download_button(
        label="Baixar Agências e CNPJs em CSV",
        data=csv_agencias,
        file_name="agencias_cnpj_extraidos.csv",
        mime="text/csv",
    )














