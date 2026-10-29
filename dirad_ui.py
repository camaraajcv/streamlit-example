"""Identidade visual do painel de consignações da DIRAD/SDPP."""
from html import escape
import streamlit as st

LOGO_B64 = "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"

STYLES = r"""<style>
:root { --dirad-navy:#073556; --dirad-blue:#135884; --dirad-gold:#d9b65b; --dirad-ink:#18344e; --dirad-muted:#647991; --dirad-line:#dfe8f2; }
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg,#eaf2fa 0,#f6f9fd 310px,#f6f9fd 100%); color:var(--dirad-ink); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="block-container"] { max-width:1180px; padding-top:1.5rem; padding-bottom:3rem; }
html,body,[class*="css"] { font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
h1,h2,h3 { color:var(--dirad-ink); letter-spacing:-.025em; }
.dirad-hero { display:flex; align-items:center; gap:28px; padding:28px 34px; position:relative; overflow:hidden; border-radius:22px; background:linear-gradient(117deg,#082b49 0%,#0b436e 70%,#17668d 100%); color:#fff; box-shadow:0 14px 36px rgba(6,40,69,.18); margin-bottom:1.4rem; }
.dirad-hero:before { content:""; position:absolute; width:240px; height:240px; border:1px solid rgba(255,255,255,.13); border-radius:100%; right:-85px; top:-120px; }
.dirad-hero:after { content:""; position:absolute; height:3px; bottom:0; left:0; right:0; background:linear-gradient(90deg,#d8b15c,#f3d889,#75b4da); }
.dirad-crest { flex:none; border:1px solid rgba(255,255,255,.32); padding:9px 12px; border-radius:14px; background:#fff; box-shadow:0 7px 19px rgba(0,0,0,.15); }
.dirad-crest img { width:88px; height:auto; display:block; }
.dirad-hero-copy { position:relative; z-index:1; }
.dirad-eyebrow { text-transform:uppercase; color:#d6e7f4; font-size:.70rem; font-weight:750; letter-spacing:.13em; margin:0 0 6px 0; }
.dirad-hero h1 { font-size:clamp(1.5rem,3.4vw,2.3rem); color:#fff; font-weight:760; line-height:1.17; margin:0 0 8px; }
.dirad-subtitle { margin:0; color:#d5e8f5; font-size:.94rem; line-height:1.65; }
.dirad-status { margin-top:14px; display:inline-block; color:#fff; border:1px solid rgba(250,223,151,.43); background:rgba(221,179,74,.13); border-radius:999px; font-size:.73rem; font-weight:650; padding:5px 11px; }
.dirad-section { padding:10px 0 6px; margin-top:1.3rem; }
.dirad-section-label { display:block; color:#28648f; text-transform:uppercase; font-weight:800; letter-spacing:.13em; font-size:.69rem; margin-bottom:5px; }
.dirad-section h2 { color:#143952; font-weight:760; font-size:1.35rem; margin:0 0 3px; line-height:1.3; }
.dirad-section p { color:#647991; margin:0 0 12px; font-size:.9rem; line-height:1.6; }
[data-testid="stFileUploader"] { background:#fff; border:1px dashed #91b1c9; border-radius:18px; padding:12px 20px; box-shadow:0 3px 14px rgba(18,63,94,.035); }
[data-testid="stFileUploader"] section { border:0; padding:5px; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--dirad-line); border-top:3px solid #1e628d; border-radius:16px; padding:17px 19px; box-shadow:0 4px 13px rgba(9,49,82,.045); }
[data-testid="stMetricLabel"] { color:#60758b; font-weight:620; font-size:.85rem; }
[data-testid="stMetricValue"] { color:#103d62; font-weight:770; font-size:clamp(1.15rem,2vw,1.65rem); }
[data-testid="stForm"] { background:#fff; border:1px solid var(--dirad-line); border-radius:18px; padding:22px; box-shadow:0 5px 20px rgba(9,49,82,.045); }
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; border:1px solid var(--dirad-line); }
[data-testid="stTabs"] [data-baseweb="tab"] { font-weight:650; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button { background:#0b4b78; border:1px solid #0b4b78; color:#fff; font-weight:700; border-radius:11px; }
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover { background:#0b365b; border-color:#0b365b; }
.stDownloadButton > button { border-radius:11px; font-weight:650; }
.dirad-note { background:#e7f0f8; border-left:3px solid #d9b65b; border-radius:0 10px 10px 0; padding:12px 16px; color:#254a68; font-size:.91rem; margin:8px 0 12px; }
.dirad-footer { text-align:center; font-size:.76rem; color:#8294a7; border-top:1px solid #dfebf4; padding-top:20px; margin-top:34px; }
@media(max-width:740px){.dirad-hero{gap:15px;padding:19px 17px;border-radius:17px}.dirad-crest{padding:6px}.dirad-crest img{width:64px}.dirad-subtitle{font-size:.83rem}.dirad-eyebrow{font-size:.59rem}.dirad-status{font-size:.65rem}[data-testid="block-container"]{padding:1rem}.dirad-section h2{font-size:1.18rem}[data-testid="stForm"]{padding:13px}}
</style>"""


def setup():
    st.set_page_config(
        page_title="DIRAD | Consignações SIAPE",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(STYLES, unsafe_allow_html=True)


def header():
    st.markdown(
        f"""<div class="dirad-hero">
            <div class="dirad-crest"><img alt="Brasão da DIRAD" src="data:image/png;base64,{LOGO_B64}"></div>
            <div class="dirad-hero-copy">
                <div class="dirad-eyebrow">Comando da Aeronáutica · DIRAD / SDPP / PP1</div>
                <h1>Consignações SIAPE</h1>
                <p class="dirad-subtitle">Descontos externos civis · Conferência de relatórios e geração de XML para o SIAFI</p>
                <span class="dirad-status">Painel de extração e conferência financeira</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def section(number, title, detail=""):
    st.markdown(
        f"""<div class="dirad-section">
          <span class="dirad-section-label">{escape(str(number))}</span>
          <h2>{escape(title)}</h2>
          {f'<p>{escape(detail)}</p>' if detail else ''}
        </div>""",
        unsafe_allow_html=True,
    )


def note(message):
    st.markdown(f'<div class="dirad-note">{escape(message)}</div>', unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown("### DIRAD · SDPP / PP1")
        st.caption("Descontos externos civis")
        st.markdown("**Fluxo de trabalho**")
        st.markdown("1. Enviar relatório PDF do SIAPE\n2. Conferir valores e lançamentos\n3. Revisar rubricas excluídas\n4. Preencher dados para o SIAFI\n5. Baixar os arquivos XML")
        st.divider()
        st.caption("A exportação é bloqueada quando os totais extraídos não conferem com o relatório do SIAPE.")


def footer():
    st.markdown(
        '<div class="dirad-footer">Comando da Aeronáutica · DIRAD / SDPP / PP1 · Apoio ao processamento de descontos externos civis</div>',
        unsafe_allow_html=True,
    )
