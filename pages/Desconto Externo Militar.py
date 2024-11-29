import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import re

# Função para processar o PDF e extrair os CNPJs, Banco e Agência
def extrair_dados(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Colocar o texto em uma linha só para facilitar a busca
    texto_completo = texto_completo.replace("\n", " ")

    # Exibir o texto extraído para diagnóstico
    st.subheader("Texto Extraído (primeiros 1000 caracteres):")
    st.text(texto_completo[:1000])

    # Expressão regular para procurar CNPJs no formato 00.000.000/0000-00
    cnpj_pattern = r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
    
    # Encontrar todos os CNPJs no texto
    cnpjs_encontrados = re.findall(cnpj_pattern, texto_completo)
    
    # Remover CNPJs duplicados
    cnpjs_unicos = list(set(cnpjs_encontrados))

    # Expressão regular para capturar banco (3 dígitos após o CNPJ) e agência (4 dígitos após o banco)
    banco_agencia_pattern = r"(\d{3})\s*-\s*Agência:\s*(\d{4})"

    # Encontrar todos os bancos e agências no texto
    banco_agencia_matches = re.findall(banco_agencia_pattern, texto_completo)

    # Garantir que temos pelo menos 1 banco/agência por CNPJ
    if len(banco_agencia_matches) < len(cnpjs_unicos):
        st.warning("O número de bancos/agências encontrados é menor do que o número de CNPJs.")

    # Criar listas para armazenar os dados encontrados
    bancos = [match[0] for match in banco_agencia_matches]  # 3 primeiros dígitos (código do banco)
    agencias = [match[1] for match in banco_agencia_matches]  # 4 dígitos seguintes (agência)

    # Preencher os dados de Banco e Agência para cada CNPJ
    bancos_completos = bancos[:len(cnpjs_unicos)]
    agencias_completas = agencias[:len(cnpjs_unicos)]

    # Criar o DataFrame com as informações extraídas
    df_resultado = pd.DataFrame({
        "CNPJ": cnpjs_unicos,
        "Banco": bancos_completos,
        "Agência": agencias_completas
    })

    return df_resultado

# Interface no Streamlit
st.title("Extração de CNPJs, Banco e Agência do PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")

    # Processar o PDF e extrair os dados
    df_resultado = extrair_dados(uploaded_file)

    # Exibir os resultados
    st.write("### Dados Extraídos:")
    st.dataframe(df_resultado)

    # Adicionar opção de download para o DataFrame em CSV
    csv_resultado = df_resultado.to_csv(index=False)
    st.download_button(
        label="Baixar Dados Extraídos em CSV",
        data=csv_resultado,
        file_name="dados_extraidos.csv",
        mime="text/csv",
    )

















