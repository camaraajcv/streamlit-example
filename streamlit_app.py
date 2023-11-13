import re
import pandas as pd
import fitz
import io
import tempfile
import streamlit as st
import os

# Texto explicativo
st.write("Desconto Externo Civil - Extração dados PDF SIAPE para SIAFI")

# Função para processar o PDF e exibir o resultado
def processar_pdf(pdf_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_content)
        temp_pdf_path = temp_pdf.name

    pdf_reader = fitz.open(temp_pdf_path)

    if pdf_reader.needs_pass:
        st.error("O arquivo PDF possui senha. Você precisa desbloqueá-lo primeiro.")
        os.remove(temp_pdf_path)
        return

    text = ""
    num_pages = pdf_reader.page_count

    for i in range(num_pages):
        page = pdf_reader.load_page(i)
        text += page.get_text()

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

    # Adicione um formulário para capturar variáveis
    st.subheader("Formulário para Captura de Variáveis")
    numero_ne = st.text_input("Número da NE (Campo texto com 12 espaços):", max_chars=12, key='numero_ne')
    cpf_responsavel = st.text_input("CPF do Responsável:", key='cpf_responsavel')

    # Adicione um botão para exportar o DataFrame para um arquivo Excel
    if st.button("Exportar para Excel", key='exportar_excel'):
        exportar_excel(df_final, numero_ne, cpf_responsavel)

    # Remover o arquivo temporário após o processamento
    os.remove(temp_pdf_path)



# Solicitar ao usuário o upload do arquivo PDF
uploaded_file = st.file_uploader("Selecione um arquivo PDF", type="pdf")

# Obter o conteúdo do arquivo PDF
if uploaded_file:
    pdf_content = uploaded_file.read()
    processar_pdf(pdf_content)
