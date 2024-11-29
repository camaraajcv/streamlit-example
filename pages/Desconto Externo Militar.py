import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import re

# Função para processar o PDF e extrair CNPJs e Conta Corrente
def processar_pdf(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Colocar o texto em uma linha só para facilitar a busca
    texto_completo = texto_completo.replace("\n", " ")

    # Debug: Mostrar o texto completo para diagnóstico
    st.subheader("Texto Extraído do PDF (primeiros 1000 caracteres):")
    st.text(texto_completo[:1000])  # Exibe os primeiros 1000 caracteres para diagnóstico

    # Expressão regular para procurar CNPJ (formato xx.xxx.xxx/xxxx-xx)
    cnpj_pattern = r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
    # Expressão regular para procurar Conta Corrente entre "Conta Corrente:" e "CNPJ"
    conta_corrente_pattern = r"Conta Corrente:\s*(.*?)\s*CNPJ"

    # Encontrar todas as sequências de "Conta Corrente:" até "CNPJ" (e inclui apenas valores válidos)
    conta_corrente_matches = re.findall(conta_corrente_pattern, texto_completo)

    # Agora buscamos os CNPJs diretamente após uma Conta Corrente válida
    cnpj_matches = []
    for conta_corrente in conta_corrente_matches:
        # Para cada Conta Corrente, procuramos o CNPJ que vem depois dela
        cnpj_search = re.search(r"CNPJ:\s*([\d]{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", texto_completo)
        if cnpj_search:
            cnpj_matches.append(cnpj_search.group(1))  # Extrair o CNPJ
        else:
            cnpj_matches.append('')  # Se não houver CNPJ, adiciona vazio

    # Garantir que as listas de CNPJ e Conta Corrente tenham o mesmo tamanho
    # Se necessário, preenche com valores vazios
    max_len = max(len(cnpj_matches), len(conta_corrente_matches))
    cnpj_matches += [''] * (max_len - len(cnpj_matches))  # Preencher com string vazia
    conta_corrente_matches += [''] * (max_len - len(conta_corrente_matches))  # Preencher com string vazia

    # Criar o DataFrame com os CNPJs e Conta Corrente encontrados
    df = pd.DataFrame({
        "CNPJ": cnpj_matches,
        "Conta Corrente": conta_corrente_matches
    })

    # Remover linhas com CNPJ e Conta Corrente vazios
    df = df[df['CNPJ'] != '']

    return df

# Interface no Streamlit
st.title("Extração de CNPJ e Conta Corrente do PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")
    
    # Processar o PDF e exibir os resultados
    df_resultado = processar_pdf(uploaded_file)
    st.write("### CNPJs e Conta Corrente Extraídos:")
    st.dataframe(df_resultado)

    # Adicionar opção de download para o DataFrame em CSV
    csv = df_resultado.to_csv(index=False)
    st.download_button(
        label="Baixar resultados em CSV",
        data=csv,
        file_name="cnpj_conta_corrente_extraidos.csv",
        mime="text/csv",
    )










