import re
import pandas as pd
import fitz
import io
import tempfile
import streamlit as st
import os
from datetime import datetime


# URL da imagem
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"

#Código HTML e CSS para ajustar a largura da imagem para 20% da largura da coluna e centralizar
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'

data_geracao = datetime.now().strftime('%Y-%m-%d')
data_geracao2 = datetime.now().strftime('%d-%m-%Y')
ultimo_sequencial = 0

# Exibir a imagem usando HTML
st.markdown(html_code, unsafe_allow_html=True)


# Centralizar o texto abaixo da imagem
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

# Texto explicativo
st.write("Desconto Externo Civil - Extração dados PDF SIAPE para SIAFI")

def remove_newlines(text):
    # Expressão regular para lidar com diferentes formas de nova linha
    newline_patterns = [r'\n', r'\r\n', r'\r']

    # Itera sobre os padrões e substitui cada ocorrência por uma string vazia
    for pattern in newline_patterns:
        text = re.sub(pattern, '', text)

    return text

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
        text = remove_newlines(text)
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
    df['Qtd.Serv'] = df['Texto_Após_CNPJ'].str[38:46]
    df['Valor Bruto'] = df['Texto_Após_CNPJ'].str[46:60]
    df['Rubrica'] = df['Texto_Após_CNPJ'].str[60:67]
    df['tipo'] = df['Texto_Após_CNPJ'].str[86:112]
    df['Qtd.Linha'] = df['Texto_Após_CNPJ'].str[116:122]
    df['ValorLinha'] = df['Texto_Após_CNPJ'].str[127:138]
    df['ValorSerpro'] = df['Texto_Após_CNPJ'].str[208:216]
    df['BCO'] = df['Texto_Após_CNPJ'].str[216:219]
    df['AG'] = df['Texto_Após_CNPJ'].str[220:226]
    df['Conta'] = df['Texto_Após_CNPJ'].str[227:241]
    df['Valor Líquido'] = df['Texto_Após_CNPJ'].str[279:295]

    # Remova os pontos dos milhares e substitua a vírgula pelo ponto
    df['Valor Líquido'] = df['Valor Líquido'].str.replace('.', '').str.replace(',', '.')
    df['ValorLinha'] = df['ValorLinha'].str.replace('.', '').str.replace(',', '.')
    df['ValorSerpro'] = df['ValorSerpro'].str.replace('.', '').str.replace(',', '.')
    df['Qtd.Serv'] = df['Qtd.Serv'].str.replace('.', '').str.replace(',', '.')
    df['Qtd.Linha'] = df['Qtd.Linha'].str.replace('.', '').str.replace(',', '.')
    df['Valor Bruto'] = df['Valor Bruto'].str.replace('.', '').str.replace(',', '.')
    # Converta a coluna para tipo float
    df['Valor Líquido'] = df['Valor Líquido'].astype(float)
    df['ValorSerpro'] = df['ValorSerpro'].astype(float)
    df['Qtd.Serv'] = df['Qtd.Serv'].astype(float)
    df['Qtd.Linha'] = df['Qtd.Linha'].astype(float)
    df['Valor Bruto'] = df['Valor Bruto'].astype(float)
    # Use a função str.replace() para remover "." (ponto), "/" (barra) e "-" (hífen) da coluna 'CNPJ'
    df['CNPJ'] = df['CNPJ'].str.replace('.', '').str.replace('/', '').str.replace('-', '')

    df_final=df.drop('Texto_Após_CNPJ', axis=1)
    st.dataframe(df_final)
    st.subheader("Formulário para Geração de Arquivos .XML")
       # Adicione um formulário para capturar variáveis
    with st.form(key='my_form'):
        # Organize os elementos do formulário em duas colunas
        col1, col2 = st.columns(2)

        # Coluna 1
        with col1:
            
            numero_ne = st.text_input("Número da NE:", max_chars=12, key='numero_ne')
            numero_sb = st.text_input("Número do Subelemento:", max_chars=2, key='numero_sb')
            ano_empenho = st.text_input("Ano de Referência (4 dígitos):", max_chars=4, key='ano_empenho')
        # Coluna 2
        with col2:
            cpf_responsavel = st.text_input("CPF do Responsável:",max_chars=11, key='cpf_responsavel')
            data_previsao_pagamento = st.date_input("Data de Previsão de Pagamento", key='data_previsao_pagamento')
            data_vencimento = st.date_input("Data Vencimento", key='data_vencimento')
        # Botão para enviar o formulário
        submit_button = st.form_submit_button(label='Gerar XML para FL')

    # Remover o arquivo temporário após o processamento
    os.remove(temp_pdf_path)

    # Se o formulário foi enviado, chame a função para exportar XML
    if submit_button:
        exportar_xml(df_final, numero_ne, numero_sb,ano_empenho, cpf_responsavel,data_previsao_pagamento,valor_liquido,data_vencimento)
        exportar_xml_detalhes(df_final, numero_ne, numero_sb, ano_empenho, cpf_responsavel, data_previsao_pagamento, valor_liquido, data_vencimento)
# Função para exportar o DataFrame para um arquivo XML
def exportar_xml(df_final, numero_ne, numero_sb,ano_empenho, cpf_responsavel, data_previsao_pagamento,valor_liquido,data_vencimento):
  
    xml_content = f"""
<sb:arquivo xmlns:ns2="http://services.docHabil.cpr.siafi.tesouro.fazenda.gov.br/" xmlns:sb="http://www.tesouro.gov.br/siafi/submissao">
  <sb:header>
    <sb:codigoLayout>DH001</sb:codigoLayout>
    <sb:dataGeracao>{data_geracao2}</sb:dataGeracao>
    <sb:sequencialGeracao>{ultimo_sequencial}</sb:sequencialGeracao>
    <sb:anoReferencia>{ano_empenho}</sb:anoReferencia>
    <sb:ugResponsavel>120052</sb:ugResponsavel>
    <sb:cpfResponsavel>{cpf_responsavel}</sb:cpfResponsavel>
  </sb:header>
  <sb:detalhes>
    <sb:detalhe>
      <ns2:CprDhCadastrar>
        <codUgEmit>120052</codUgEmit>
        <anoDH>{ano_empenho}</anoDH>
        <codTipoDH>FL</codTipoDH>
        <dadosBasicos>
          <dtEmis>{data_geracao}</dtEmis>
          <dtVenc>{data_vencimento}</dtVenc>
          <codUgPgto>120052</codUgPgto>
          <vlr>{valor_liquido}</vlr>
          <txtObser></txtObser>
          <txtProcesso></txtProcesso>
          <dtAteste>{data_geracao}</dtAteste>
          <codCredorDevedor></codCredorDevedor>
          <dtPgtoReceb>{data_previsao_pagamento}</dtPgtoReceb>
          <docOrigem>
            <codIdentEmit></codIdentEmit>
            <dtEmis></dtEmis>
            <numDocOrigem></numDocOrigem>
            <vlr></vlr>
          </docOrigem>
        </dadosBasicos>
        <pco>
          <numSeqItem>{ultimo_sequencial}</numSeqItem>
          <codSit></codSit>
          <codUgEmpe></codUgEmpe>
          <pcoItem>
            <numSeqItem></numSeqItem>
            <numEmpe></numEmpe>
            <codSubItemEmpe></codSubItemEmpe>
            <vlr></vlr>
            <numClassA></numClassA>
          </pcoItem>
        </pco>
        <centroCusto>
          <numSeqItem></numSeqItem>
          <codCentroCusto></codCentroCusto>
          <mesReferencia></mesReferencia>
          <anoReferencia></anoReferencia>
          <codUgBenef></codUgBenef>
          <relPcoItem>
            <numSeqPai></numSeqPai>
            <numSeqItem></numSeqItem>
            <vlr></vlr>
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
    st.success(f"Arquivo XML com DataFrame gerado com sucesso. [Baixar XML (FL-Principal)](sandbox:/download_cabecalho)")
    st.success(f"Arquivo XML com DataFrame gerado com sucesso.") 
    # Adiciona um botão de download para o arquivo XML
    # Cria um objeto BytesIO para armazenar o conteúdo do XML
    xml_io = io.BytesIO(xml_content.encode())

    # Adiciona um botão de download para o arquivo XML
    if st.button("Baixar XML (Cabeçalho e Trailler)"):
        xml_io = io.BytesIO(xml_content.encode())
        st.download_button(
            label="Baixar XML (Cabeçalho e Trailler)",
            data=xml_io,
            file_name=f"xml_cabecalho_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xml",
            mime="text/xml",
            key=f'download_button_cabecalho_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )
def exportar_xml_detalhes(df_final, numero_ne, numero_sb, ano_empenho, cpf_responsavel, data_previsao_pagamento, valor_liquido, data_vencimento):
    
    xml_content = f"""
<sb:arquivo xmlns:ns2="http://services.docHabil.cpr.siafi.tesouro.fazenda.gov.br/" xmlns:sb="http://www.tesouro.gov.br/siafi/submissao">
  <sb:detalhes>
"""

    for index, row in df_final.iterrows():
        xml_content += f"""
    <sb:detalhe>
      <ns2:CprDhCadastrar>
        <!-- ... (restante do código do detalhe) ... -->
        <pco>
          <!-- ... (restante do código do pco) ... -->
        </pco>
        <centroCusto>
          <!-- ... (restante do código do centroCusto) ... -->
        </centroCusto>
      </ns2:CprDhCadastrar>
    </sb:detalhe>
"""

    xml_content += """
  </sb:detalhes>
  <sb:trailler>
    <sb:quantidadeDetalhe>{len(df_final)}</sb:quantidadeDetalhe>
  </sb:trailler>
</sb:arquivo>
"""

    st.success(f"Arquivo XML com detalhes do DataFrame gerado com sucesso.")
    xml_io = io.BytesIO(xml_content.encode())

    if st.button("Baixar XML (Detalhes)"):
        xml_io = io.BytesIO(xml_content.encode())
        st.download_button(
            label="Baixar XML (Detalhes)",
            data=xml_io,
            file_name=f"xml_detalhes_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xml",
            mime="text/xml",
            key=f'download_button_detalhes_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )
# Função auxiliar para criar um link de download
def get_binary_file_downloader_html(bin_file, file_label='File', button_label='Save as', key='download_link'):
    bin_str = bin_file.getvalue()
    bin_str = bin_str.decode()
    href = f'data:application/octet-stream;base64,{bin_str}'
    return f'<a href="{href}" download="{file_label}.xml"><button>{button_label}</button></a>'
# Solicitar ao usuário o upload do arquivo PDF
uploaded_file = st.file_uploader("Faça o UPLOAD do arquivo PDF do SIAPE gerado na transação GRCOCGRECO", type="pdf")

# Obter o conteúdo do arquivo PDF
if uploaded_file:
    pdf_content = uploaded_file.read()
    processar_pdf(pdf_content)
if st.session_state.url_triggered == 'download_cabecalho':
    exportar_xml_cabecalho()

if st.session_state.url_triggered == 'download_detalhes':
    exportar_xml_detalhes_cabecalho()