import streamlit as st
import PyPDF2
import re
import pandas as pd
import logging
import pdfplumber
from datetime import datetime
from io import StringIO
from io import BytesIO
# Configuração do logging para capturar os erros
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Funções auxiliares diretamente no código

def extract_text_up_to_line(pdf_file, start_pattern, end_pattern):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        lines = text.split("\n")

        start_index = next((i for i, line in enumerate(lines) if start_pattern in line), None)
        end_index = next((i for i, line in enumerate(lines) if end_pattern in line), None)

        if start_index is not None and end_index is not None:
            return lines[start_index + 1 : end_index]
        else:
            return ["Padrão não encontrado no texto."]
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
        return []

def filter_exclude_lines(filtered_text, exclude_patterns):
    filtered_lines = []
    for line in filtered_text:
        if not any(line.startswith(pattern) for pattern in exclude_patterns):
            filtered_lines.append(line)
    return filtered_lines

def formatar_valor_brasileiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def extract_codes_and_agencia_conta_cnpj(filtered_text):
    codes_agencias_contas_cnpjs = []
    for i, line in enumerate(filtered_text):
        code_match = re.match(r"^\d{4}", line)
        if code_match:
            code = code_match.group(0)
            agencia, conta, cnpj = extract_agencia_conta_cnpj(filtered_text, i)
            codes_agencias_contas_cnpjs.append((code, agencia, conta, cnpj))
    return codes_agencias_contas_cnpjs

def extract_agencia_conta_cnpj(filtered_text, start_index):
    agencia = None
    conta = None
    cnpj = None

    if start_index + 1 < len(filtered_text):
        line = filtered_text[start_index + 1]
        agencia_match = re.search(r"Agência:\s*([^\s]+)\s*Conta Corrente:", line)
        if agencia_match:
            agencia = agencia_match.group(1)

        conta_match = re.search(r"Conta Corrente:\s*([\d\-]+)\s*CNPJ:", line)
        if conta_match:
            conta = conta_match.group(1)

        cnpj_match = re.search(r"CNPJ:\s*([\d./-]+)", line)
        if cnpj_match:
            cnpj = cnpj_match.group(1)

    return agencia, conta, cnpj

def extract_value_before_total(filtered_text):
    valores = []
    collecting = False
    total_sum = 0

    for i, line in enumerate(filtered_text):
        if re.match(r"^\d{4}", line):
            if collecting:
                valores.append([total_sum])
            collecting = True
            total_sum = 0

        if collecting and line.startswith("05"):
            value_match = re.search(r"(\d{1,3}(\.\d{3})*(\,\d{2}))\s*$", line)
            if value_match:
                value_str = value_match.group(1)
                value = value_str.replace(".", "").replace(",", ".")
                total_sum += float(value)

        if "Total" in line and collecting:
            valores.append([total_sum])
            collecting = False

    return valores

# Formulário para o usuário
st.title("Redução de Valores e Geração de XML")

# Campos do formulário para gerar XML
data_geracao = st.date_input("Data de Geração")
cpf_responsavel = st.text_input("CPF Responsável")

# Campos adicionais
numDH = st.text_input("Número do DH (numDH)")
txtMotivo = st.text_input("Motivo (txtMotivo)", "DESC.EXT.MIL.DEZ")
txtMotivo = txtMotivo[:16]  # Limitar a 16 caracteres
dtVenc = st.date_input("Data de Vencimento (dtVenc)")

# Formulário de Reduções
tipo_reducao = st.selectbox("Escolha o tipo de redução", ["", "RAT", "Judicial", "Outros"])
cnpj_selecionado = st.selectbox("Selecione o CNPJ", ["CNPJ 1", "CNPJ 2", "CNPJ 3"])  # Simulação de lista de CNPJs
valor_reducao = st.number_input("Informe o valor a ser reduzido", min_value=0.0, step=0.01)

# Gerar XML
if st.button("Gerar XML"):
    # Verificar se os campos obrigatórios foram preenchidos
    if cpf_responsavel and numDH and txtMotivo and dtVenc:
        # Definindo variáveis fixas
        sequencial_geracao = "100"
        ano_referencia = datetime.now().year
        anoDH = datetime.now().year
        dtPgtoReceb = data_geracao  # A data de pagamento será a mesma de geração

        # Construção da string XML
        xml_string = '''<sb:arquivo xmlns:sb="http://www.tesouro.gov.br/siafi/submissao" xmlns:cpr="http://services.docHabil.cpr.siafi.tesouro.fazenda.gov.br/">
            <sb:header>
                <sb:codigoLayout>{}</sb:codigoLayout>
                <sb:dataGeracao>{}</sb:dataGeracao>
                <sb:sequencialGeracao>{}</sb:sequencialGeracao>
                <sb:anoReferencia>{}</sb:anoReferencia>
                <sb:ugResponsavel>{}</sb:ugResponsavel>
                <sb:cpfResponsavel>{}</sb:cpfResponsavel>
            </sb:header>
            <sb:detalhes>
        '''.format("DH002", data_geracao.strftime("%d/%m/%Y"), sequencial_geracao, ano_referencia, "120052", cpf_responsavel)

        # Adicionando um detalhe (um exemplo de como seria inserido no XML)
        xml_string += '''<sb:detalhe>
                <cpr:CprDhAlterarDHIncluirItens>
                    <codUgEmit>120052</codUgEmit>
                    <anoDH>{}</anoDH>
                    <codTipoDH>FL</codTipoDH>
                    <numDH>{}</numDH>
                    <dtEmis>{}</dtEmis>
                    <txtMotivo>{}</txtMotivo>
                    <deducao>
                        <numSeqItem>{}</numSeqItem>
                        <codSit>DOB005</codSit>
                        <dtVenc>{}</dtVenc>
                        <dtPgtoReceb>{}</dtPgtoReceb>
                    </deducao>
                </cpr:CprDhAlterarDHIncluirItens>
            </sb:detalhe>
        '''.format(anoDH, numDH, data_geracao.strftime("%d/%m/%Y"), txtMotivo, "1", dtVenc.strftime("%d/%m/%Y"), dtPgtoReceb.strftime("%d/%m/%Y"))

        # Fechamento do XML
        xml_string += "</sb:detalhes></sb:arquivo>"

        # Exibir o XML gerado
        st.text_area("XML Gerado", xml_string, height=300)

    else:
        st.error("Por favor, preencha todos os campos para gerar o XML.")