import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd

# Função para processar o PDF e extrair os dados desejados
def processar_pdf(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Buscar "CNPJ:" e os próximos 18 caracteres (CNPJ formatado)
    cnpj_matches = re.findall(r"CNPJ:\s*([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", texto_completo)

    # Buscar "Agência:" e os próximos 6 caracteres (número da agência)
    agencia_matches = re.findall(r"Agência:\s*(\d{6})", texto_completo)

    # Garantir que as listas tenham o mesmo tamanho
    max_length = max(len(cnpj_matches), len(agencia_matches))
    cnpj_matches.extend(["Não encontrado"] * (max_length - len(cnpj_matches)))
    agencia_matches.extend(["Não encontrado"] * (max_length - len(agencia_matches)))

    # Criar o DataFrame
    df = pd.DataFrame({
        "CNPJ": cnpj_matches,
        "Agência": agencia_matches
    })

    return df

# Interface no Streamlit
st.title("Extração de Dados de PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")
    
    # Processar o PDF e exibir os resultados
    df_resultado = processar_pdf(uploaded_file)
    st.write("### Dados Extraídos:")
    st.dataframe(df_resultado)

    # Adicionar opção de download para o DataFrame em CSV
    csv = df_resultado.to_csv(index=False)
    st.download_button(
        label="Baixar resultados em CSV",
        data=csv,
        file_name="resultado_extracao.csv",
        mime="text/csv",
    )
