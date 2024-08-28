import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")
    return text

def convert_text_to_dataframe(text):
    lines = text.split('\n')
    
    # Ajuste o código conforme o formato real do texto extraído
    # Por exemplo, se os dados são separados por espaços ou tabs
    data = []
    for line in lines:
        if line.strip():  # Ignorar linhas vazias
            # Supondo que os dados estejam separados por um delimitador, como espaço
            split_line = line.split()
            # Verifique se a linha tem o número correto de colunas
            if len(split_line) >= 5:
                data.append(split_line[:5])  # Ajuste conforme o número de colunas esperadas
    
    # Crie o DataFrame com as colunas específicas
    columns = ["Código", "Consignatária", "Banco", "Conta", "Nome"]
    df = pd.DataFrame(data, columns=columns)
    
    return df

def main():
    st.title("Upload e Leitura de PDF")

    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

    if uploaded_file is not None:
        st.write("Arquivo carregado com sucesso!")

        # Extrai o texto do PDF
        text = extract_text_from_pdf(uploaded_file)
        st.text_area("Conteúdo do PDF", text, height=300)

        # Converte o texto em um DataFrame
        df = convert_text_to_dataframe(text)
        
        # Exibe o DataFrame
        st.write("Dados extraídos do PDF:")
        st.dataframe(df)

if __name__ == "__main__":
    main()