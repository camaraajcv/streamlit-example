import streamlit as st
import PyPDF2
import re
import pandas as pd
from datetime import datetime

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

# URL da imagem
image_url = "https://www.fab.mil.br/om/logo/mini/dirad2.jpg"

# Código HTML e CSS para ajustar a largura da imagem e centralizar
html_code = f'<div style="display: flex; justify-content: center;"><img src="{image_url}" alt="Imagem" style="width:8vw;"/></div>'

# Data de geração
data_geracao = datetime.now().strftime('%Y-%m-%d')
data_geracao2 = datetime.now().strftime('%d/%m/%Y')

# Exibir a imagem
st.markdown(html_code, unsafe_allow_html=True)

# Títulos e explicações
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

# Texto explicativo
st.write("Desconto Externo Militar - Extração dados PDF SIGPP para SIAFI")

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

    # Solicitar novo upload para a junção de dados
    st.write("Agora, faça o upload do segundo arquivo PDF para realizar a junção dos dados com os valores extraídos.")
    uploaded_file_banco = st.file_uploader("Upload do arquivo do banco (para junção)", type="pdf")

    if uploaded_file_banco is not None:
        # Processamento do segundo PDF
        filtered_lines_banco = extract_text_up_to_line(uploaded_file_banco, start_pattern, end_pattern_to_exclude)
        filtered_lines_banco = filter_exclude_lines(filtered_lines_banco, exclude_patterns)

        # Criação de DataFrame para o banco
        df_banco_clean = pd.DataFrame({
            'Código': ['1234', '5678'],  # exemplo de códigos
            'Banco Agência Conta': ['1234-5678-1234', '5678-1234-5678']  # exemplo de dados do banco
        })
        
        # Junção entre os DataFrames
        df_completo = pd.merge(df_final, df_banco_clean[['Código', 'Banco Agência Conta']], on='Código', how='left')

        # Removendo duplicatas com base na coluna 'Código'
        df_completo = df_completo.drop_duplicates(subset=['Código'])

        # Renomeando as colunas
        df_completo.rename(columns={'Banco Agência Conta': 'bco', 'Agência': 'agencia', 'Conta': 'conta', 'CNPJ': 'cnpj', 'Valor': 'valor'}, inplace=True)

        # Limpeza de dados na coluna 'conta'
        df_completo['conta'] = df_completo['conta'].astype(str).str.replace('-', '', regex=False)

        # Ajustando a coluna 'agencia'
        df_completo['agencia'] = df_completo['agencia'].apply(lambda x: x.split('-')[0].zfill(4) + '-' + x.split('-')[1] if isinstance(x, str) and '-' in x else x)

        # Exibindo o DataFrame final
        st.subheader("DataFrame Completo com Dados Junção Banco")
        st.dataframe(df_completo)

        # Somando todos os valores
        total_valor = df_completo['valor'].sum()
        st.success(f"Valor Total Desconto Externo (com Junção): {formatar_valor_brasileiro(total_valor)}")
