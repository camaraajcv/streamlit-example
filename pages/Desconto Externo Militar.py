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
    codigo = None
    total = None
    banco = None

    # Expressão regular para capturar um código de 4 dígitos
    code_pattern = re.compile(r'\b\d{4}\b')

    for i, line in enumerate(lines):
        if "Nome" in line and i + 1 < len(lines):
            # Procurar por um código de 4 dígitos na linha seguinte
            next_line = lines[i + 1].strip()
            match = code_pattern.search(next_line)
            if match:
                codigo = match.group()
                # Capturar o nome na linha que sucede o código
                nome = lines[i + 2].strip() if i + 2 < len(lines) else None
                # Capturar os primeiros 4 dígitos da segunda linha após o código
                banco_line = lines[i + 3].strip() if i + 3 < len(lines) else ""
                banco = banco_line[:4]
                data.append([codigo, nome, None, banco])
        
        # Procurar pela palavra "Totais" e capturar o valor na linha seguinte
        if "Totais" in line and i + 1 < len(lines):
            total = lines[i + 1].strip()
            # Atualizar a última linha do DataFrame com o total
            if data:
                data[-1][2] = total
    
    # Cria o DataFrame com as colunas "Código", "Nome", "Total" e "Banco"
    columns = ["Código", "Nome", "Total", "Banco"]
    df = pd.DataFrame(data, columns=columns)

    # Filtra para exibir apenas linhas em que "Total" não seja Null
    df = df[df["Total"].notna()]
    
    return df

def main():
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")

    if uploaded_file is not None:
        # Extrai o texto do PDF
        text = extract_text_from_pdf(uploaded_file)
        lines = text.split('\n')
        
        # Define o título e subtítulo a partir das linhas 1 e 3
        title = lines[0] if len(lines) > 0 else "Título não encontrado"
        subtitle = lines[2] if len(lines) > 2 else "Subtítulo não encontrado"

        # Exibe o título e subtítulo no app
        st.title(title)
        st.subheader(subtitle)

        # Converte o texto em um DataFrame específico
        df = convert_text_to_dataframe(text)
        
        # Exibe o DataFrame
        st.write("Dados extraídos do PDF (Código, Nome, Total e Banco):")
        st.dataframe(df)

        # Exibir o conteúdo do PDF em linhas numeradas
        st.write("Conteúdo do PDF em Linhas Numeradas:")
        for i, line in enumerate(lines, start=1):
            st.text(f"Linha {i}: {line}")

if __name__ == "__main__":
    main()