import re
import pandas as pd
import fitz
import io
import tempfile
import streamlit as st
import os
# URL da imagem
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"

#Código HTML e CSS para ajustar a largura da imagem para 20% da largura da coluna e centralizar
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'


# Exibir a imagem usando HTML
st.markdown(html_code, unsafe_allow_html=True)


# Centralizar o texto abaixo da imagem
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

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
            data_previsao_pagamento = st.date_input("Data de Previsão de Pagamento", key='data_previsao_pagamento')
        # Botão para enviar o formulário
        submit_button = st.form_submit_button(label='Gerar XML para FL')

    # Remover o arquivo temporário após o processamento
    os.remove(temp_pdf_path)

    # Se o formulário foi enviado, chame a função para exportar XML
    if submit_button:
        exportar_xml(df_final, numero_ne, numero_sb, cpf_responsavel,data_previsao_pagamento)

import re
import pandas as pd
import fitz
import io
import tempfile
import streamlit as st
import os
# URL da imagem
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"

#Código HTML e CSS para ajustar a largura da imagem para 20% da largura da coluna e centralizar
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'


# Exibir a imagem usando HTML
st.markdown(html_code, unsafe_allow_html=True)


# Centralizar o texto abaixo da imagem
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

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
            data_previsao_pagamento = st.date_input("Data de Previsão de Pagamento", key='data_previsao_pagamento')
        # Botão para enviar o formulário
        submit_button = st.form_submit_button(label='Gerar XML para FL')

    # Remover o arquivo temporário após o processamento
    os.remove(temp_pdf_path)

    # Se o formulário foi enviado, chame a função para exportar XML
    if submit_button:
        exportar_xml(df_final, numero_ne, numero_sb, cpf_responsavel,data_previsao_pagamento)

# Função para exportar o DataFrame para um arquivo XML
def exportar_xml(df_final, numero_ne, numero_sb, cpf_responsavel, data_previsao_pagamento):
    # Lógica para gerar o arquivo XML com base nas variáveis fornecidas
    # Substitua esta lógica pela sua implementação real para gerar o XML

    # Exemplo básico:
    xml_content = f"""
<sb:arquivo xmlns:ns2="http://services.docHabil.cpr.siafi.tesouro.fazenda.gov.br/" xmlns:sb="http://www.tesouro.gov.br/siafi/submissao">
  <sb:header>
    <sb:codigoLayout>DH001</sb:codigoLayout>
    <sb:dataGeracao>11/11/2023</sb:dataGeracao>
    <sb:sequencialGeracao>1</sb:sequencialGeracao>
    <sb:anoReferencia>2023</sb:anoReferencia>
    <sb:ugResponsavel>120052</sb:ugResponsavel>
    <sb:cpfResponsavel>{cpf_responsavel}</sb:cpfResponsavel>
  </sb:header>
  <sb:detalhes>
    <sb:detalhe>
      <ns2:CprDhCadastrar>
        <codUgEmit>{df_final['CodigoUG'][0]}</codUgEmit>
        <anoDH>{df_final['AnoDH'][0]}</anoDH>
        <codTipoDH>{df_final['CodTipoDH'][0]}</codTipoDH>
        <dadosBasicos>
          <dtEmis>{df_final['DtEmis'][0]}</dtEmis>
          <dtVenc>{df_final['DtVenc'][0]}</dtVenc>
          <codUgPgto>{df_final['CodUgPgto'][0]}</codUgPgto>
          <vlr>{df_final['Vlr'][0]}</vlr>
          <txtObser>{df_final['TxtObser'][0]}</txtObser>
          <txtProcesso>{df_final['TxtProcesso'][0]}</txtProcesso>
          <dtAteste>{df_final['DtAteste'][0]}</dtAteste>
          <codCredorDevedor>{df_final['CodCredorDevedor'][0]}</codCredorDevedor>
          <dtPgtoReceb>{df_final['DtPgtoReceb'][0]}</dtPgtoReceb>
          <docOrigem>
            <codIdentEmit>{df_final['CodIdentEmit'][0]}</codIdentEmit>
            <dtEmis>{df_final['DtEmisDocOrigem'][0]}</dtEmis>
            <numDocOrigem>{df_final['NumDocOrigem'][0]}</numDocOrigem>
            <vlr>{df_final['VlrDocOrigem'][0]}</vlr>
          </docOrigem>
        </dadosBasicos>
        <pco>
          <numSeqItem>{df_final['NumSeqItem'][0]}</numSeqItem>
          <codSit>{df_final['CodSit'][0]}</codSit>
          <codUgEmpe>{df_final['CodUgEmpe'][0]}</codUgEmpe>
          <pcoItem>
            <numSeqItem>{df_final['NumSeqItemPco'][0]}</numSeqItem>
            <numEmpe>{df_final['NumEmpe'][0]}</numEmpe>
            <codSubItemEmpe>{df_final['CodSubItemEmpe'][0]}</codSubItemEmpe>
            <vlr>{df_final['VlrPcoItem'][0]}</vlr>
            <numClassA>{df_final['NumClassA'][0]}</numClassA>
          </pcoItem>
        </pco>
        <centroCusto>
          <numSeqItem>{df_final['NumSeqItemCentroCusto'][0]}</numSeqItem>
          <codCentroCusto>{df_final['CodCentroCusto'][0]}</codCentroCusto>
          <mesReferencia>{df_final['MesReferencia'][0]}</mesReferencia>
          <anoReferencia>{df_final['AnoReferencia'][0]}</anoReferencia>
          <codUgBenef>{df_final['CodUgBenef'][0]}</codUgBenef>
          <relPcoItem>
            <numSeqPai>{df_final['NumSeqPai'][0]}</numSeqPai>
            <numSeqItem>{df_final['NumSeqItemCentroCustoRel'][0]}</numSeqItem>
            <vlr>{df_final['VlrCentroCusto'][0]}</vlr>
          </relPcoItem>
        </centroCusto>
      </ns2:CprDhCadastrar>
    </sb:detalhe>
  </sb:detalhes>
  <sb:trailler>
    <sb:quantidadeDetalhe>1</sb:quantidadeDetalhe>
  </sb:trailler>
</sb:arquivo>
"""

    # Salvar o conteúdo do XML em um arquivo
    with open("output.xml", "w") as xml_file:
        xml_file.write(xml_content)

    st.success("Arquivo XML gerado com sucesso.")


# Solicitar ao usuário o upload do arquivo PDF
uploaded_file = st.file_uploader("Faça o UPLOAD do arquivo PDF do SIAPE gerado na transação GRCOCGRECO", type="pdf")

# Obter o conteúdo do arquivo PDF
if uploaded_file:
    pdf_content = uploaded_file.read()
    processar_pdf(pdf_content)

# Solicitar ao usuário o upload do arquivo PDF
uploaded_file = st.file_uploader("Faça o UPLOAD do arquivo PDF do SIAPE gerado na transação GRCOCGRECO", type="pdf")

# Obter o conteúdo do arquivo PDF
if uploaded_file:
    pdf_content = uploaded_file.read()
    processar_pdf(pdf_content)
