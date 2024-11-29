import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import re

# Função para processar o PDF e extrair CNPJs no formato padrão
def extrair_cnpjs(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Colocar o texto em uma linha só para facilitar a busca
    texto_completo = texto_completo.replace("\n", " ")

    return texto_completo

# Interface no Streamlit
st.title("Extração de CNPJs do PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")

    # Processar o PDF e extrair o texto completo
    texto_extraido = extrair_cnpjs(uploaded_file)
    
    # Exibir o texto extraído
    st.write("### Texto Extraído do PDF (Primeiros 1000 caracteres):")
    st.text(texto_extraido[:1000])  # Exibe os primeiros 1000 caracteres para diagnóstico

    # Expressão regular para procurar CNPJs no formato 00.000.000/0000-00
    cnpj_pattern = r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"

    # Encontrar todos os CNPJs no texto
    cnpjs_encontrados = re.findall(cnpj_pattern, texto_extraido)

    # Remover CNPJs duplicados
    cnpjs_unicos = list(set(cnpjs_encontrados))

    # Criar um DataFrame com os CNPJs encontrados
    df_cnpjs = pd.DataFrame({
        "CNPJ": cnpjs_unicos
    })

    # Exibir os resultados
    st.write("### CNPJs Extraídos:")
    st.dataframe(df_cnpjs)

    # Adicionar opção de download para o DataFrame em CSV
    csv_resultado = df_cnpjs.to_csv(index=False)
    st.download_button(
        label="Baixar CNPJs Extraídos em CSV",
        data=csv_resultado,
        file_name="cnpjs_extraidos.csv",
        mime="text/csv",
    )
















