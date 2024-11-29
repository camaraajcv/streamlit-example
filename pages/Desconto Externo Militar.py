import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import re

# Função para processar o PDF e extrair CNPJs
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

    # Expressão regular para procurar CNPJ (formato xx.xxx.xxx/xxxx-xx)
    cnpj_pattern = r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
    
    # Encontrar todos os CNPJs no texto
    cnpj_matches = re.findall(cnpj_pattern, texto_completo)

    # Criar o DataFrame com os CNPJs encontrados
    df = pd.DataFrame({
        "CNPJ": cnpj_matches
    })

    return df

# Interface no Streamlit
st.title("Extração de CNPJ do PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")
    
    # Processar o PDF e exibir os resultados
    df_resultado = processar_pdf(uploaded_file)
    st.write("### CNPJs Extraídos:")
    st.dataframe(df_resultado)

    # Adicionar opção de download para o DataFrame em CSV
    csv = df_resultado.to_csv(index=False)
    st.download_button(
        label="Baixar resultados em CSV",
        data=csv,
        file_name="cnpj_extraido.csv",
        mime="text/csv",
    )






