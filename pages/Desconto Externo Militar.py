import streamlit as st
import PyPDF2
import re
import pandas as pd
import logging
import pdfplumber
from datetime import datetime
from io import StringIO
from io import BytesIO
# Configuração do logging para capturar os erros
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


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

# Exibir a imagem
st.markdown(html_code, unsafe_allow_html=True)

# Títulos e explicações
st.markdown("<h1 style='text-align: center; font-size: 1.5em;'>DIRETORIA DE ADMINISTRAÇÃO DA AERONÁUTICA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; font-size: 1.2em;'>SUBDIRETORIA DE PAGAMENTO DE PESSOAL</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-size: 1em; text-decoration: underline;'>PP1 - DIVISÃO DE DESCONTOS</h3>", unsafe_allow_html=True)

# Texto explicativo
st.write("Desconto Externo Militar - Extração dados PDF SIGPP para SIAFI")

# Interface para upload de arquivo PDF
uploaded_file = st.file_uploader("Faça o upload do primeiro arquivo PDF. Este arquivo deve ser retirado no SIGPP em relatórios de empenho. (LEMBRAR DE MARCAR SOMENTE CONSIGNATÁRIAS)", type="pdf")

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

####################################################################################################

# Interface para preenchimento de RAT e JUDICIAL para cada CNPJ
if 'df_final' in globals() and not df_final.empty:
    st.subheader("Preencher valores para RAT e JUDICIAL")
    
    # Criando um novo DataFrame vazio para as reduções
    reducoes = pd.DataFrame(columns=["CNPJ", "Tipo", "Valor"])
    
    # Permite selecionar os CNPJs da lista extraída
    cnpjs = df_final['CNPJ'].unique()
    
    # Campo para selecionar os CNPJs
    selected_cnpjs = st.multiselect("Selecione os CNPJs para os quais deseja adicionar valores de RAT e JUDICIAL", cnpjs, key="cnpjs_multiselect")
    
    # Para cada CNPJ selecionado, cria campos para RAT e JUDICIAL
    for cnpj in selected_cnpjs:
        st.write(f"Preencha os valores para o CNPJ: {cnpj}")
        
        # Campo para selecionar o tipo (RAT ou JUDICIAL)
        tipo_selecionado = st.selectbox(f"Selecione o tipo para o CNPJ {cnpj}", ["RAT", "JUDICIAL"], key=f"tipo_{cnpj}")
        
        # Campo para inserir o valor para o tipo selecionado
        valor = st.number_input(f"Valor para {tipo_selecionado} do CNPJ {cnpj}", min_value=0.0, format="%.2f", key=f"valor_{cnpj}_{tipo_selecionado}")
        
        # Adicionando ao DataFrame 'reducoes' conforme o tipo
        if valor is not None:
            # Criando o DataFrame com a nova linha a ser adicionada
            nova_linha = pd.DataFrame({
                "CNPJ": [cnpj],
                "Tipo": [tipo_selecionado],
                "Valor": [valor]
            })
            # Usando pd.concat para adicionar a nova linha ao DataFrame 'reducoes'
            reducoes = pd.concat([reducoes, nova_linha], ignore_index=True)
    
    # Exibindo o DataFrame 'reducoes' com os valores preenchidos
    if not reducoes.empty:
        st.write("Valores preenchidos para RAT e JUDICIAL:")
        st.dataframe(reducoes)

####################################################################################################

# Função para extrair os dados do PDF
def extract_pdf_data(pdf_file):
    # Listas para armazenar os dados extraídos
    codigo_nome_numeros = []
    banco_agencia_conta_dados = []

    # Abre o arquivo PDF a partir do BytesIO
    with pdfplumber.open(pdf_file) as pdf:
        total_pages = len(pdf.pages)
        progress_bar = st.progress(0)  # Inicializa a barra de progresso

        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                lines = text.split("\n")  # Divide o texto em linhas
                for i, line in enumerate(lines):
                    # Verifica se a linha contém "Código Nome"
                    if "Código Nome" in line:
                        # Extrai os 4 números da linha seguinte
                        next_line = lines[i + 1] if i + 1 < len(lines) else ""
                        numeros = [word for word in next_line.split() if word.isdigit() and len(word) == 4]
                        codigo_nome_numeros.extend(numeros)

                    # Verifica se a linha contém "Banco Agência Conta"
                    if "Banco Agência Conta" in line:
                        # Extrai os 4 primeiros números ou '-' no início da linha seguinte
                        next_line = lines[i + 1] if i + 1 < len(lines) else ""
                        # Usa uma expressão regular para capturar os quatro primeiros números consecutivos
                        numeros = re.findall(r'\d{4}', next_line)
                        if len(numeros) >= 1:  # Retém apenas o primeiro número se encontrado
                            banco_agencia_conta_dados.append(numeros[0])
                        else:
                            banco_agencia_conta_dados.append(None)

            # Atualiza a barra de progresso
            progress = (page_num + 1) / total_pages
            progress_bar.progress(progress)

    # Igualar os tamanhos das listas
    max_length = max(len(codigo_nome_numeros), len(banco_agencia_conta_dados))
    codigo_nome_numeros.extend([None] * (max_length - len(codigo_nome_numeros)))
    banco_agencia_conta_dados.extend([None] * (max_length - len(banco_agencia_conta_dados)))

    # Criar o DataFrame
    df_banco = pd.DataFrame({
        "Código": codigo_nome_numeros,
        "Banco Agência Conta": banco_agencia_conta_dados
    })

    # Remove as linhas que contêm None em qualquer uma das colunas
    df_banco_clean = df_banco.dropna()

    # Remove duplicatas com base no Código
    df_banco_clean = df_banco_clean.drop_duplicates(subset='Código')

    return df_banco_clean

# Interface do Streamlit
st.subheader("Extraindo código do Banco de arquivo SIGPP")
# Adicionando CSS para substituir o texto padrão "Drag and drop file here"
# Inicializa o df_banco_clean como None ou um valor vazio
df_banco_clean = None

pdf_file = st.file_uploader("Selecione o arquivo PDF do SIGPP de repasse às consignatárias", type="pdf")

if pdf_file:
    st.write(f"Arquivo selecionado: {pdf_file.name}")
    st.write("Processando o PDF... Aguarde um momento enquanto extraímos os dados.")
    
    df_banco_clean = extract_pdf_data(pdf_file)
    
    if df_banco_clean is not None and not df_banco_clean.empty:
        st.write("Códigos de Bancos sincronizados!")
    else:
        st.warning("Nenhum dado foi extraído do PDF.")
else:
    st.info("Por favor, faça o upload de um arquivo PDF para processar os dados.")

if 'df_final' in globals():
    # Verifica se df_banco_clean existe
    if 'df_banco_clean' in globals():
        df_completo = pd.merge(df_final, df_banco_clean[['Código', 'Banco Agência Conta']], on='Código', how='left')
    else:
        df_completo = df_final.copy()  # Caso df_banco_clean não exista, mantém df_final sem alterações
else:
    print("Erro: df_final não está definido.")

# Renomeando as colunas para manter consistência
df_completo.rename(columns={'Banco Agência Conta': 'bco', 'Agência': 'agencia', 'Conta': 'conta', 'CNPJ': 'cnpj', 'Valor': 'valor'}, inplace=True)

# Remover o caractere '-' da coluna 'conta'
df_completo['conta'] = df_completo['conta'].str.replace('-', '', regex=False)

# Ajustando a coluna 'agencia' para garantir que os números antes do '-' tenham 4 dígitos
df_completo['agencia'] = df_completo['agencia'].apply(lambda x: x.split('-')[0].zfill(4) + '-' + x.split('-')[1] if isinstance(x, str) and '-' in x else x)

# Extraindo os 4 primeiros dígitos da coluna 'agencia'
df_completo['agencia'] = df_completo['agencia'].str[:4]

# Excluir as linhas onde a coluna 'valor' seja igual a zero
df_completo = df_completo[df_completo['valor'] != 0]

# Preencher os valores de RAT e Judicial
df_completo['rat'] = 0.00
df_completo['judicial'] = 0.00

# Interface para preencher valores de RAT e Judicial
selected_cnpjs = st.multiselect("Selecione os CNPJs para os quais deseja adicionar valores de RAT e JUDICIAL", df_completo['cnpj'].unique())

for cnpj in selected_cnpjs:
    # Campos de entrada para RAT e JUDICIAL
    rat_value = st.number_input(f"Valor para RAT do CNPJ {cnpj}", min_value=0.0, format="%.2f", key=f"rat_{cnpj}")
    judicial_value = st.number_input(f"Valor para JUDICIAL do CNPJ {cnpj}", min_value=0.0, format="%.2f", key=f"judicial_{cnpj}")
    
    # Atualizando as colunas 'rat' e 'judicial' para o CNPJ selecionado
    df_completo.loc[df_completo['cnpj'] == cnpj, 'rat'] = rat_value
    df_completo.loc[df_completo['cnpj'] == cnpj, 'judicial'] = judicial_value

# Calculando o valor final
df_completo['outros'] = 0.00
df_completo['valor_final'] = df_completo['valor'] - df_completo['rat'] - df_completo['judicial'] - df_completo['outros']

# Excluindo os CNPJs especificados
cnpjs_a_excluir = ['34054254000104', '00753422000138']
st.warning("Excluídos os CNPJ 34054254000104 (Clube de Aeronáutica) e 00753422000138 (Clube de Aeronáutica de Brasília)")

# Filtrando o dataframe
df2 = df_completo[~df_completo['cnpj'].isin(cnpjs_a_excluir)]

# Exibindo o DataFrame
st.dataframe(df2)

# Cálculo e exibição dos valores de acordo com o CNPJ
valor_clube_aeronautica = df_completo[df_completo['cnpj'] == '34054254000104']['valor'].sum()
valor_clube_aeronautica_brasilia = df_completo[df_completo['cnpj'] == '00753422000138']['valor'].sum()

# Exibindo os valores com as mensagens correspondentes
if valor_clube_aeronautica > 0:
    st.success(f"Valor do Clube de Aeronáutica é {formatar_valor_brasileiro(valor_clube_aeronautica)}")

if valor_clube_aeronautica_brasilia > 0:
    st.success(f"Valor do Clube de Aeronáutica de Brasília é {formatar_valor_brasileiro(valor_clube_aeronautica_brasilia)}")

soma_valores = df2['valor'].sum()
st.success("Valor Total Desconto Externo Sem Clubes: " + formatar_valor_brasileiro(soma_valores))

########################################RED8UCAO#########################################################################




################################### XML #########################

# Preenchendo campos do XML
st.subheader("Preencher Dados para Gerar XML")

# Campos adicionais que o usuário deve preencher para gerar o XML
data_geracao = st.date_input("Data de Geração")
cpf_responsavel = st.text_input("CPF Responsável")

# Preenchendo campos obrigatórios
numDH = st.text_input("Número do DH (numDH)")
txtMotivo = st.text_input("Motivo (txtMotivo)", "DESC.EXT.MIL.DEZ")
txtMotivo = txtMotivo[:16]  # Limitar a 16 caracteres
dtVenc = st.date_input("Data de Vencimento (dtVenc)")

# Quando o usuário clicar para gerar o XML
if st.button("Gerar XML"):
    # Garantindo que os campos obrigatórios sejam preenchidos
    if cpf_responsavel and numDH and txtMotivo and dtVenc:
        # Definindo variáveis fixas
        sequencial_geracao = "100"
        ano_referencia = datetime.now().year
        anoDH = datetime.now().year
        dtPgtoReceb = data_geracao  # A data de pagamento será a mesma de geração

        # Construção da string XML
        xml_string = '''<sb:arquivo xmlns:sb="http://www.tesouro.gov.br/siafi/submissao" xmlns:cpr="http://services.docHabil.cpr.siafi.tesouro.fazenda.gov.br/">
            <sb:header>
                <sb:codigoLayout>{}</sb:codigoLayout>
                <sb:dataGeracao>{}</sb:dataGeracao>
                <sb:sequencialGeracao>{}</sb:sequencialGeracao>
                <sb:anoReferencia>{}</sb:anoReferencia>
                <sb:ugResponsavel>{}</sb:ugResponsavel>
                <sb:cpfResponsavel>{}</sb:cpfResponsavel>
            </sb:header>
            <sb:detalhes>
        '''.format("DH002", data_geracao.strftime("%d/%m/%Y"), sequencial_geracao, ano_referencia, "120052", cpf_responsavel)

        # Loop sobre as linhas do DataFrame
        for index, row in df2.iterrows():
            # Define o valor de codTipoOB com base no valor de codCredorDevedor
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
                include_banco_txtCit = False  # Não incluir para outros CNPJs
                txtCit = None  # Definir txtCit como None para indicar que não deve ser incluído

            xml_string += '''<sb:detalhe>
                    <cpr:CprDhAlterarDHIncluirItens>
                        <codUgEmit>120052</codUgEmit>
                        <anoDH>{}</anoDH>
                        <codTipoDH>FL</codTipoDH>
                        <numDH>{}</numDH>
                        <dtEmis>{}</dtEmis>
                        <txtMotivo>{}</txtMotivo>
                        <deducao>
                            <numSeqItem>{}</numSeqItem>
                            <codSit>DOB005</codSit>
                            <dtVenc>{}</dtVenc>
                            <dtPgtoReceb>{}</dtPgtoReceb>
                            <codUgPgto>120052</codUgPgto>
                            <vlr>{}</vlr>
                            <txtInscrA>{}</txtInscrA>
                            <numClassA>218810199</numClassA>
                            <predoc>
                                <txtObser>{}</txtObser>  
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
                </sb:detalhe>'''.format(anoDH, numDH, data_geracao.strftime("%Y-%m-%d"), txtMotivo,
                                       index + 1, dtVenc.strftime("%Y-%m-%d"), dtPgtoReceb.strftime("%Y-%m-%d"),
                                       row['valor'], row['cnpj'], txtMotivo, codTipoOB, row['cnpj'], f'<txtCit>{txtCit}</txtCit>' if include_banco_txtCit and txtCit is not None else '',
                                       row['bco'], row['agencia'], row['conta'],
                                       f'<numDomiBancPgto><banco>{row["banco_fab"]}</banco><conta>UNICA</conta></numDomiBancPgto>' if include_banco_txtCit else f'<numDomiBancPgto><conta>UNICA</conta></numDomiBancPgto>')

        # Finalize a string XML
        xml_string += '''
            </sb:detalhes>
            <sb:trailler>
                <sb:quantidadeDetalhe>{}</sb:quantidadeDetalhe>
            </sb:trailler>
        </sb:arquivo>
        '''.format(len(df2))

        # Converter o conteúdo para bytes
        xml_bytes = xml_string.encode('utf-8')

        # Criação do arquivo XML em memória e permitir o download
        st.download_button(
            label="Baixar XML",
            data=xml_bytes,
            file_name="arquivo_militar.xml",
            mime="application/xml"
        )

    else:
        st.error("Por favor, preencha todos os campos obrigatórios antes de gerar o XML.")