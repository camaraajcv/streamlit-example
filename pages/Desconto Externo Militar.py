import streamlit as st
import PyPDF2
import re
from datetime import datetime
# URL da imagem
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"

#Código HTML e CSS para ajustar a largura da imagem para 20% da largura da coluna e centralizar
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'

data_geracao = datetime.now().strftime('%Y-%m-%d')
data_geracao2 = datetime.now().strftime('%d/%m/%Y')


# Exibir a imagem usando HTML
st.markdown(html_code, unsafe_allow_html=True)


# Centralizar o texto abaixo da imagem
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

# Texto explicativo
st.write("Desconto Externo Militar - Extração dados PDF SIGPP para SIAFI")


import streamlit as st
import PyPDF2
import re
import pandas as pd

# Funções auxiliares
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

# Interface Streamlit
st.title("Processador de PDF")

uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

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

    # Processa o arquivo
    filtered_lines = extract_text_up_to_line(uploaded_file, start_pattern, end_pattern_to_exclude)
    filtered_lines = filter_exclude_lines(filtered_lines, exclude_patterns)
    codes_agencias_contas_cnpjs = extract_codes_and_agencia_conta_cnpj(filtered_lines)
    valores = extract_value_before_total(filtered_lines)

    # DataFrame com as informações extraídas
    df_agencia_conta_cnpj = pd.DataFrame(codes_agencias_contas_cnpjs, columns=["Código", "Agência", "Conta", "CNPJ"])
    df_valores = pd.DataFrame(valores, columns=["Valor"])

    # Ajusta os índices
    max_len = max(len(df_agencia_conta_cnpj), len(df_valores))
    df_agencia_conta_cnpj = df_agencia_conta_cnpj.reindex(range(max_len))
    df_valores = df_valores.reindex(range(max_len))

    # DataFrame final
    df_final = pd.concat([df_agencia_conta_cnpj, df_valores], axis=1)

    # Exibe o DataFrame final
    st.subheader("Resultados Extraídos")
    st.dataframe(df_final)

    # Soma os valores
    if not df_final.empty:
        total_valor_soma = df_final["Valor"].sum()
        st.write(f"Valor total da coluna 'Valor': {total_valor_soma:.2f}")

