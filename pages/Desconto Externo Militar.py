import streamlit as st
import PyPDF2
import pdfplumber
import re
import pandas as pd
from datetime import datetime

# Função para extrair texto até um padrão de início e fim
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
            return lines[start_index + 1: end_index]
        else:
            return ["Padrão não encontrado no texto."]
    except Exception as e:
        st.error(f"Erro ao processar o PDF com PyPDF2: {e}")
        return []

# Função para excluir padrões de linhas
def filter_exclude_lines(filtered_text, exclude_patterns):
    filtered_lines = []
    for line in filtered_text:
        if not any(line.startswith(pattern) for pattern in exclude_patterns):
            filtered_lines.append(line)
    return filtered_lines

# Função para formatar valores em moeda brasileira
def formatar_valor_brasileiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para extrair códigos, agências, contas e CNPJ
def extract_codes_and_agencia_conta_cnpj(filtered_text):
    codes_agencias_contas_cnpjs = []
    for i, line in enumerate(filtered_text):
        code_match = re.match(r"^\d{4}", line)
        if code_match:
            code = code_match.group(0)
            agencia, conta, cnpj = extract_agencia_conta_cnpj(filtered_text, i)
            codes_agencias_contas_cnpjs.append((code, agencia, conta, cnpj))
    return codes_agencias_contas_cnpjs

# Função para extrair agência, conta e CNPJ
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

# Função para extrair valores antes do total
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

# Função para extrair dados do PDF usando pdfplumber
def extract_pdf_data(pdf_file):
    # Listas para armazenar os dados extraídos
    codigo_nome_numeros = []
    banco_agencia_conta_dados = []

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    lines = text.split("\n")  # Divide o texto em linhas
                    for i, line in enumerate(lines):
                        # Verifica se a linha contém "Código Nome"
                        if "Código Nome" in line:
                            # Extrai os 4 números da linha seguinte
                            next_line = lines[i + 1] if i + 1 < len(lines) else ""
                            numeros = [word for word in next_line.split() if word.isdigit() and len(word) == 4]
                            codigo_nome_numeros.extend(numeros)

                        # Verifica se a linha contém "Banco Agência Conta"
                        if "Banco Agência Conta" in line:
                            # Extrai os 4 primeiros números ou '-' no início da linha seguinte
                            next_line = lines[i + 1] if i + 1 < len(lines) else ""
                            # Usa uma expressão regular para capturar os quatro primeiros números consecutivos
                            numeros = re.findall(r'\d{4}', next_line)
                            if len(numeros) >= 1:  # Retém apenas o primeiro número se encontrado
                                banco_agencia_conta_dados.append(numeros[0])
                            else:
                                banco_agencia_conta_dados.append(None)
    except Exception as e:
        st.error(f"Erro ao processar o PDF com pdfplumber: {e}")

    # Igualar os tamanhos das listas
    max_length = max(len(codigo_nome_numeros), len(banco_agencia_conta_dados))
    codigo_nome_numeros.extend([None] * (max_length - len(codigo_nome_numeros)))
    banco_agencia_conta_dados.extend([None] * (max_length - len(banco_agencia_conta_dados)))

    # Criar o DataFrame
    df_banco = pd.DataFrame({
        "Código": codigo_nome_numeros,
        "Banco Agência Conta": banco_agencia_conta_dados
    })

    # Remove as linhas que contêm None em qualquer uma das colunas
    df_banco_clean = df_banco.dropna()

    return df_banco_clean

# Interface do Streamlit
st.title("Extrator de Dados de PDF")

# Exibição de logo
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'
st.markdown(html_code, unsafe_allow_html=True)

# Títulos
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

# Interface para upload de arquivo PDF
uploaded_file = st.file_uploader("Faça o upload do primeiro arquivo PDF", type="pdf")

if uploaded_file is not None:
    start_pattern = "Natureza de Despesa: 11190000 - OUTRAS CONSIGNATARIAS"
    end_pattern_to_exclude = "Natureza de Despesa: 11199900 - DESCONTO INTERNO- APROPRIACAO UPAG"
    exclude_patterns = [
        "Relatório Emitido em",
        "Diretoria de Administração",
        "Subdiretoria",
        "Competência:",
        "Abrangência:",
        "Folha:",
        "Órgão:",
        "Módulo de PAGAMENTOS",
        "Natureza de Despesa:"
    ]

    # Processamento do primeiro PDF
    filtered_lines = extract_text_up_to_line(uploaded_file, start_pattern, end_pattern_to_exclude)
    filtered_lines = filter_exclude_lines(filtered_lines, exclude_patterns)
    
    # Extração de informações
    codes_agencias_contas_cnpjs = extract_codes_and_agencia_conta_cnpj(filtered_lines)
    valores = extract_value_before_total(filtered_lines)

    # Criação de DataFrames
    df_agencia_conta_cnpj = pd.DataFrame(codes_agencias_contas_cnpjs, columns=["Código", "Agência", "Conta", "CNPJ"])
    df_valores = pd.DataFrame(valores, columns=["Valor"])

    # Ajuste de índices
    max_len = max(len(df_agencia_conta_cnpj), len(df_valores))
    df_agencia_conta_cnpj = df_agencia_conta_cnpj.reindex(range(max_len))
    df_valores = df_valores.reindex(range(max_len))

    # Concatenar os DataFrames
    df_final = pd.concat([df_agencia_conta_cnpj, df_valores], axis=1)

    # Exibir o DataFrame
    st.subheader("Resultados Extraídos")
    st.dataframe(df_final)

    # Soma os valores
    if not df_final.empty:
        total_valor_soma = df_final["Valor"].sum()
        st.success(f"Valor total DESCONTO EXTERNO - SIGPP: {formatar_valor_brasileiro(total_valor_soma)}")

    # Processamento de PDF para segunda parte
    df_banco_clean = extract_pdf_data(uploaded_file)
    st.subheader("Dados Bancários Extraídos")
    st.dataframe(df_banco_clean)
