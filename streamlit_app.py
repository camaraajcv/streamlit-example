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
with st.form(key='my_form'):
    # Organize os elementos do formulário em duas colunas
    col1, col2 = st.columns(2)

    # Coluna 1
    with col1:
        st.subheader("Formulário para Geração de Arquivos .XML")
        numero_ne = st.text_input("Número da NE:", max_chars=12, key='numero_ne')
        numero_sb = st.text_input("Número do Subelemento:", max_chars=2, key='numero_sb')
        
    # Coluna 2
    with col2:
        cpf_responsavel = st.text_input("CPF do Responsável:", key='cpf_responsavel')

    # Botão para enviar o formulário
    submit_button = st.form_submit_button(label='Exportar para XML')
    # Remover o arquivo temporário após o processamento
    os.remove(temp_pdf_path)

    # Se o formulário foi enviado, chame a função para exportar XML
    if submit_button:
        exportar_xml(df_final, numero_ne, numero_sb, cpf_responsavel)

# Função para exportar o DataFrame para um arquivo XML
def exportar_xml(df_final, numero_ne, numero_sb, cpf_responsavel):
    # Lógica para gerar o arquivo XML com base nas variáveis fornecidas
    # Substitua esta lógica pela sua implementação real para gerar o XML

    # Exemplo básico:
    xml_content = f"<root><NE>{numero_ne}</NE><Subelemento>{numero_sb}</Subelemento><Responsavel>{cpf_responsavel}</Responsavel></root>"

    # Salvar o conteúdo do XML em um arquivo
    with open("output.xml", "w") as xml_file:
        xml_file.write(xml_content)

    st.success("Arquivo XML gerado com sucesso.")

# Solicitar ao usuário o upload do arquivo PDF
uploaded_file = st.file_uploader("Selecione um arquivo PDF", type="pdf")

# Obter o conteúdo do arquivo PDF
if uploaded_file:
    pdf_content = uploaded_file.read()
    processar_pdf(pdf_content)
