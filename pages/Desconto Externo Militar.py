import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    # Abre o PDF
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    # Itera sobre todas as páginas do PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")
    return text

def convert_text_to_dataframe(text):
    # Ajuste esta função para o formato específico do seu PDF
    lines = text.split('\n')
    
    # Exemplo de como os dados podem ser separados por espaços ou tabs
    # Ajuste o delimitador conforme necessário
    data = [line.split() for line in lines if line.strip()]
    
    # Crie um DataFrame com colunas específicas
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