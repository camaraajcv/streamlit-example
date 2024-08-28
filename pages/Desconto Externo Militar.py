import streamlit as st
import pandas as pd
from io import BytesIO

# Verificar se o módulo openpyxl está instalado
try:
    import openpyxl
except ImportError as e:
    st.error("O módulo 'openpyxl' não está instalado. Instale-o com 'pip install openpyxl'.")
    raise e

def format_bco(value):
    return f'{int(value):03d}'

def format_agencia(value):
    numeric_value = ''.join(char for char in str(value) if char.isdigit())
    return f'{int(numeric_value):04d}' if numeric_value else ''

def process_file(uploaded_file):
    # Leia o arquivo Excel para um DataFrame
    df = pd.read_excel(uploaded_file, converters={'bco': format_bco, 'agencia': format_agencia}, dtype={'bco': str, 'agencia': str})

    # Assegure-se de que a coluna 'conta' seja uma string preenchida com zeros à esquerda
    df['conta'] = df['conta'].astype(str).str.zfill(13)

    # Converta 'valor' para numérico e arredonde
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    df['valor'] = round(df['valor'], 2)

    # Converta 'cnpj' para string e remova caracteres indesejados
    df['cnpj'] = df['cnpj'].astype(str).str.replace('[./-]', '', regex=True)

    # Remover linhas com dados ausentes
    df = df.dropna()

    # Defina 'conta' como 'FOPAG' para CNPJs específicos
    df.loc[df['cnpj'].isin(['00360305000104', '00000000000191']), 'conta'] = 'FOPAG'
    df['banco_fab'] = ''
    df.loc[df['cnpj'].isin(['00360305000104', '00000000000191']), 'banco_fab'] = '002'

    # Construir a string XML
    xml_string = '''<sb:arquivo xmlns:sb="http://www.tesouro.gov.br/siafi/submissao" xmlns:cpr="http://services.docHabil.cpr.siafi.tesouro.fazenda.gov.br/">
        <sb:header>
            <sb:codigoLayout>DH002</sb:codigoLayout>
            <sb:dataGeracao>02/08/2024</sb:dataGeracao>
            <sb:sequencialGeracao>10</sb:sequencialGeracao>
            <sb:anoReferencia>2024</sb:anoReferencia>
            <sb:ugResponsavel>120052</sb:ugResponsavel>
            <sb:cpfResponsavel>09857528740</sb:cpfResponsavel>
        </sb:header>
        <sb:detalhes>
    '''

    for index, row in df.iterrows():
        if row['cnpj'] == '00000000000191':
            codTipoOB = 'OBF'
            txtCit = '120052ECFP999'
            include_banco_txtCit = True
        elif row['cnpj'] == '00360305000104':
            codTipoOB = 'OBF'
            txtCit = '120052ECFPC019950'
            include_banco_txtCit = True
        else:
            codTipoOB = 'OBC'
            include_banco_txtCit = False
            txtCit = None

        xml_string += '''<sb:detalhe>
                <cpr:CprDhAlterarDHIncluirItens>
                    <codUgEmit>120052</codUgEmit>
                    <anoDH>2024</anoDH>
                    <codTipoDH>FL</codTipoDH>
                    <numDH>000607</numDH>
                    <dtEmis>2024-08-02</dtEmis>
                    <txtMotivo>DESC.EXT.MILITAR.JUL.</txtMotivo>
                    <deducao>
                        <numSeqItem>{}</numSeqItem>
                        <codSit>DOB005</codSit>
                        <dtVenc>2024-08-29</dtVenc>
                        <dtPgtoReceb>2024-08-02</dtPgtoReceb>
                        <codUgPgto>120052</codUgPgto>
                        <vlr>{}</vlr>
                        <txtInscrA>{}</txtInscrA>
                        <numClassA>218810199</numClassA>
                        <predoc>
                            <txtObser>DESC.EXT.MILITAR.JUL.</txtObser>
                            <predocOB>
                                <codTipoOB>{}</codTipoOB>
                                <codCredorDevedor>{}</codCredorDevedor>
                                {}
                                <numDomiBancFavo>
                                    <banco>{}</banco>
                                    <agencia>{}</agencia>
                                    <conta>{}</conta>
                                </numDomiBancFavo>
                                {}
                            </predocOB>
                        </predoc>
                    </deducao>
                    </cpr:CprDhAlterarDHIncluirItens>
            </sb:detalhe>'''.format(index + 1, row['valor'], row['cnpj'], codTipoOB, row['cnpj'],
                                    f'<txtCit>{txtCit}</txtCit>' if include_banco_txtCit and txtCit is not None else '',
                                    row['bco'], row['agencia'], row['conta'],
                                    f'<numDomiBancPgto><banco>{row["banco_fab"]}</banco><conta>UNICA</conta></numDomiBancPgto>' if include_banco_txtCit else f'<numDomiBancPgto><conta>UNICA</conta></numDomiBancPgto>')

    xml_string += '''
        </sb:detalhes>
        <sb:trailler>
            <sb:quantidadeDetalhe>{}</sb:quantidadeDetalhe>
        </sb:trailler>
    </sb:arquivo>
    '''.format(len(df))

    return xml_string

def main():
    st.title("Gerador de XML a partir de Arquivo Excel")
    
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type="xlsx")

    if uploaded_file is not None:
        xml_string = process_file(uploaded_file)
        st.download_button(
            label="Baixar XML",
            data=xml_string,
            file_name="xml_militar.xml",
            mime="application/xml"
        )
        st.text("O XML foi gerado com sucesso!")

if __name__ == "__main__":
    main()
