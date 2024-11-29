import streamlit as st
import re
import pandas as pd
from PyPDF2 import PdfReader

# Função para extrair o texto do PDF
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para processar o texto e extrair os dados desejados
def process_pdf_content(text):
    # Procurar por "Natureza de Despesa:" e capturar o texto subsequente
    naturezas = re.findall(r"Natureza de Despesa:\s*(.+)", text)
    
    # Procurar sequenciais de 4 dígitos e o texto subsequente
    om_matches = re.findall(r"(\d{4})\s+(.+)", text)
    oms = [{"Sequencial": match[0], "OM": match[1]} for match in om_matches]
    
    # Criar DataFrame
    data = {"Natureza de Despesa": naturezas}
    df_natureza = pd.DataFrame(data)

    df_om = pd.DataFrame(oms)

    return df_natureza, df_om

# Início do app
st.title("Extração de Dados de PDF")

# Upload do arquivo PDF
uploaded_file = st.file_uploader("Faça o upload de um arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Extrair o texto do PDF
    pdf_text = extract_text_from_pdf(uploaded_file)
    
    # Processar o texto para extrair os dados
    df_natureza, df_om = process_pdf_content(pdf_text)
    
    # Exibir os resultados
    st.subheader("Natureza de Despesa")
    st.write(df_natureza)
    
    st.subheader("OM")
    st.write(df_om)
    
    # Disponibilizar os DataFrames para download
    if not df_natureza.empty:
        csv_natureza = df_natureza.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Natureza de Despesa (CSV)",
            data=csv_natureza,
            file_name="natureza_despesa.csv",
            mime="text/csv"
        )
    
    if not df_om.empty:
        csv_om = df_om.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar OM (CSV)",
            data=csv_om,
            file_name="om.csv",
            mime="text/csv"
        )