import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd

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

    # Procurar por "CNPJ:" e extrair os CNPJs encontrados
    cnpj_matches = []
    cnpj_start = texto_completo.find("CNPJ:")
    while cnpj_start != -1:
        cnpj_end = texto_completo.find(" ", cnpj_start + 5)  # Procurar o espaço após o CNPJ
        if cnpj_end == -1:
            cnpj_end = len(texto_completo)  # Caso não tenha espaço, pegar até o final do texto
        cnpj_matches.append(texto_completo[cnpj_start + 5:cnpj_end].strip())  # Captura o CNPJ
        cnpj_start = texto_completo.find("CNPJ:", cnpj_end)  # Buscar próximo CNPJ

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





