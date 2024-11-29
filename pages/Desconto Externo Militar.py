import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd

# Função para processar o PDF e extrair os dados desejados
def processar_pdf(file):
    # Ler o conteúdo do PDF
    pdf_reader = PdfReader(file)
    texto_completo = ""
    for pagina in pdf_reader.pages:
        texto_completo += pagina.extract_text()

    # Mostrar uma amostra do texto extraído (para diagnóstico)
    st.subheader("Texto Extraído do PDF:")
    st.text(texto_completo[:1000])  # Exibe os primeiros 1000 caracteres

    # Buscar "CNPJ:" e os próximos 18 caracteres (CNPJ formatado)
    cnpj_matches = re.findall(r"CNPJ:\s*([\d]{2}\.[\d]{3}\.[\d]{3}/[\d]{4}-[\d]{2})", texto_completo)

    # Buscar "Agência:" e capturar os números ou hífen após "Agência:"
    agencia_matches = []
    for cnpj in cnpj_matches:
        # Alterar a regex para capturar as variações de números e hífens após "Agência:"
        agencia_match = re.findall(r"Agência:\s*([0-9\-]+)", texto_completo)
        
        # Se a agência for encontrada, adicione à lista, caso contrário adicione 'Não encontrado'
        if agencia_match:
            agencia_matches.append(agencia_match[0].strip())  # Remove qualquer espaço extra
        else:
            agencia_matches.append("Não encontrado")

    # Garantir que as listas de CNPJ e Agência tenham o mesmo tamanho
    max_length = len(cnpj_matches)
    agencia_matches.extend(["Não encontrado"] * (max_length - len(agencia_matches)))

    # Criar o DataFrame apenas com os CNPJs encontrados
    df = pd.DataFrame({
        "CNPJ": cnpj_matches,
        "Agência": agencia_matches
    })

    return df

# Interface no Streamlit
st.title("Extração de Dados de PDF")
uploaded_file = st.file_uploader("Faça o upload do arquivo PDF", type="pdf")

if uploaded_file is not None:
    st.success("Arquivo carregado com sucesso!")
    
