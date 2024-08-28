import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")
    return text

def convert_text_to_dataframe(text):
    lines = text.split('\n')
    
    # Lista para armazenar os dados extraídos
    data = []

    # Expressão regular para capturar a palavra "Nome" seguida de um código de 4 dígitos
    pattern = re.compile(r'Nome\s+(\S+)\s+(\d{4})')

    for line in lines:
        if line.strip():  # Ignorar linhas vazias
            # Procurar pela palavra "Nome" seguida do código
            match = pattern.search(line)
            if match:
                nome = match.group(1)
                codigo = match.group(2)
                data.append([codigo, nome])
    
    # Cria o DataFrame com as colunas "Código" e "Nome"
    columns = ["Código", "Nome"]
    df = pd.DataFrame(data, columns=columns)
    
    return df

def main():
    st.title("Upload e Leitura de PDF")

    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

    if uploaded_file is not None:
        st.write("Arquivo carregado com sucesso!")

        # Extrai o texto do PDF
        text = extract_text_from_pdf(uploaded_file)
        
        # Exibir o conteúdo do PDF em linhas numeradas
        lines = text.split('\n')
        for i, line in enumerate(lines, start=1):
            st.text(f"Linha {i}: {line}")

        # Converte o texto em um DataFrame específico
        df = convert_text_to_dataframe(text)
        
        # Exibe o DataFrame
        st.write("Dados extraídos do PDF (Código e Nome):")
        st.dataframe(df)

if __name__ == "__main__":
    main()