import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
pip install PyPDF2
import PyPDF2
"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:.
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""
import re
import pandas as pd
import PyPDF2
import io
import streamlit as st

# Função para processar o PDF e exibir o resultado
def processar_pdf(pdf_content):
    pdf_file = io.BytesIO(pdf_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    if pdf_reader.is_encrypted:
        st.error("O arquivo PDF possui senha. Você precisa desbloqueá-lo primeiro.")
        return

    text = ""
    num_pages = len(pdf_reader.pages)

    for i, page in enumerate(pdf_reader.pages):
        st.text(f"Processando página {i + 1} de {num_pages}")
        text += page.extract_text()

    match = re.search(r'VALOR\s+LIQUIDO\.{3,}:\s*([\d.,]+)', text)

    if match:
        valor_liquido = match.group(1)
        valor_liquido = valor_liquido.replace('.', '').replace(',', '.')
        st.success(f"Valor Líquido: {valor_liquido}")
    else:
        st.warning("Valor Líquido não encontrado.")

    cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
    cnpjs = re.findall(cnpj_pattern, text)
    text_parts = re.split(cnpj_pattern, text)

    data = {'CNPJ': cnpjs, 'Texto_Após_CNPJ': text_parts[1:]}
    df = pd.DataFrame(data)
    df['Empresa'] = df['Texto_Após_CNPJ'].str[:33]
    df['Qtd.Serv'] = df['Texto_Após_CNPJ'].str[38:43]
    df['Valor Bruto'] = df['Texto_Após_CNPJ'].str[46:60]
    df['Rubrica'] = df['Texto_Após_CNPJ'].str[61:68]
    df['BCO'] = df['Texto_Após_CNPJ'].str[219:222]
    df['AG'] = df['Texto_Após_CNPJ'].str[223:229]
    df['Conta'] = df['Texto_Após_CNPJ'].str[230:244]
    df['Valor Líquido'] = df['Texto_Após_CNPJ'].str[279:297]

    df['Valor Líquido'] = df['Valor Líquido'].str.replace('.', '').str.replace(',', '.')
    df['Valor Líquido'] = df['Valor Líquido'].astype(float)
    df['CNPJ'] = df['CNPJ'].str.replace('.', '').str.replace('/', '').str.replace('-', '')

    df_final = df.drop('Texto_Após_CNPJ', axis=1)
    st.dataframe(df_final)

    # Adicione um botão para exportar o DataFrame para um arquivo Excel
    if st.button("Exportar para Excel"):
        exportar_excel(df_final)

# Função para exportar o DataFrame para um arquivo Excel (.xls)
def exportar_excel(df_final):
    df_final.to_excel("output.xls", index=False)
    st.success("DataFrame exportado para 'output.xls'")

# Solicitar ao usuário o upload do arquivo PDF
uploaded_file = st.file_uploader("Selecione um arquivo PDF", type="pdf")

# Obter o conteúdo do arquivo PDF
if uploaded_file:
    pdf_content = uploaded_file.read()
    processar_pdf(pdf_content)




