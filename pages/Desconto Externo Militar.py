import streamlit as st
import re
from PyPDF2 import PdfReader

# Função para processar o PDF e extrair os dados desejados
def processar_pdf(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Buscar "Natureza de Despesa:" e o texto subsequente
    natureza_despesa = re.findall(r"Natureza de Despesa:\s*(.+)", texto_completo)

    # Buscar padrões de "XXXX - " seguido do texto (onde XXXX são 4 números)
    om_matches = re.findall(r"(\d{4} - .+)", texto_completo)

    # Criar um DataFrame para exibir os resultados no Streamlit
    import pandas as pd
    df = pd.DataFrame({
        "Natureza de Despesa": natureza_despesa if natureza_despesa else ["Não encontrado"],
        "OM": om_matches if om_matches else ["Não encontrado"]
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