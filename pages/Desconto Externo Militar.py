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
    
    data = []
    nome = None

    # Expressão regular para capturar um código de 4 dígitos
    code_pattern = re.compile(r'\b\d{4}\b')

    for i, line in enumerate(lines):
        if "Nome" in line:
            nome = line.split("Nome")[-1].strip()  # Captura o nome após a palavra "Nome"
            if i + 1 < len(lines):  # Verifica se existe uma próxima linha
                next_line = lines[i + 1].strip()
                # Procurar por um código de 4 dígitos na linha seguinte
                match = code_pattern.search(next_line)
                if match:
                    codigo = match.group()
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