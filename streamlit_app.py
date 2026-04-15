import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import locale
import folium
from streamlit_folium import st_folium
from datetime import date, timedelta
from io import BytesIO
import requests
import polyline # Biblioteca para decodificar a geometria da rota
from streamlit_option_menu import option_menu
import base64 # <<< LINHA ADICIONADA PARA CORRIGIR O ERRO
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap, BoundaryNorm
import altair as alt
import numpy as np # Adicione esta linha no topo do seu arquivo se ainda não tiver
import math
import folium
from streamlit_folium import st_folium
import requests
import polyline # Biblioteca para decodificar a geometria da rota
from folium import plugins # <<< ADICIONE ESTA LINHA
from folium.plugins import Fullscreen
import textwrap
import re


# --- 1. CONFIGURAÇÕES DA PÁGINA E ESTILO ---
st.set_page_config(
    page_title="📊 Dashboard de Viagens",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Detect current theme (light/dark) to apply CSS properly ---
def _km_get_theme_type():
    """Return 'light' or 'dark' when possible; otherwise None."""
    try:
        ctx = getattr(st, "context", None)
        if ctx is not None and isinstance(getattr(ctx, "theme", None), dict):
            t = ctx.theme.get("type")
            if isinstance(t, str):
                t = t.lower().strip()
                if t in ("light", "dark"):
                    return t
    except Exception:
        pass

    # Fallback: config option (may not reflect runtime toggle in some versions)
    try:
        base = st.get_option("theme.base")
        if isinstance(base, str):
            base = base.lower().strip()
            if base in ("light", "dark"):
                return base
    except Exception:
        pass

    return None

_KM_THEME = _km_get_theme_type()

# CSS para customizar a aparência do título baseado na imagem de referência
st.markdown("""
    <style>
            
    /* --- IMPORTANDO FONTES E ÍCONES --- */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&display=swap' );
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css' ); /* <<< ADICIONE ESTA LINHA */
            
/* ▼▼▼ NOVO ESTILO PARA O SELETOR DE ROTA ▼▼▼ */

/* Container que envolve o rótulo e o seletor */
.custom-selectbox-container {
    margin-top: 15px; /* Espaço acima */
    margin-bottom: 25px; /* Espaço abaixo */
}

/* Estilo para o rótulo (label) "SELECIONE A ROTA..." */
.custom-selectbox-label {
    font-family: "Poppins", "Segoe UI", sans-serif;
    font-size: 0.9rem; /* Tamanho da fonte */
    font-weight: 600; /* Negrito */
    color: #A0AEC0; /* Cinza claro, menos chamativo */
    text-transform: uppercase; /* Caixa alta */
    letter-spacing: 0.8px; /* Espaçamento entre letras */
    margin-bottom: 8px; /* Espaço entre o rótulo e a caixa */
    display: flex;
    align-items: center;
    gap: 6px; /* Espaço entre o ícone e o texto */
}

/* Estilo para o próprio seletor (a caixa de seleção) */
.stSelectbox > div {
    background-color: #1A202C; /* Fundo escuro (azul-acinzentado) */
    border: 1px solid #2D3748; /* Borda sutil */
    border-radius: 10px; /* Bordas arredondadas */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* Sombra interna suave */
    transition: border-color 0.3s ease, box-shadow 0.3s ease; /* Animação suave */
}

/* Efeito ao passar o mouse (hover) */
.stSelectbox > div:hover {
    border-color: #4A90E2; /* Borda azul ao passar o mouse */
    box-shadow: 0 0 10px rgba(74, 144, 226, 0.3); /* Brilho azul */
}

/* Cor do texto dentro do seletor */
.stSelectbox div[data-baseweb="select"] > div {
    color: #E2E8F0;
}

/* Cor da setinha (dropdown arrow) */
.stSelectbox svg {
    color: #A0AEC0;
}

/* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */

            
    /* ▼▼▼ ADICIONE ESTE NOVO ESTILO PARA O BOTÃO DE DOWNLOAD ▼▼▼ */
    .custom-download-button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px; /* Espaço entre o ícone e o texto */
        background-color: #2c3e50; /* Cor de fundo do botão */
        color: #ffffff; /* Cor do texto */
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #34495e;
        text-decoration: none; /* Remove o sublinhado do link */
        font-weight: bold;
        transition: background-color 0.3s ease, border-color 0.3s ease;
        width: 100%; /* Faz o botão ocupar a largura total do contêiner */
        box-sizing: border-box; /* Garante que padding e border não aumentem a largura */
    }
    .custom-download-button:hover {
        background-color: #34495e; /* Cor ao passar o mouse */
        border-color: #4a90e2;
        color: #ffffff; /* Mantém a cor do texto no hover */
    }
    .custom-download-button i {
        font-size: 1.2em; /* Tamanho do ícone */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            

    /* --- GERAL --- */
    body {
        font-family: "Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif;
        background-color: #0e1117; /* Cor de fundo mais escura */
    }

    /* --- TÍTULO PRINCIPAL --- */
    .main-title {
        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%); /* Gradiente azul claro */
        border-radius: 15px; /* Bordas arredondadas */
        padding: 18px 20px; /* Espaçamento interno */
        margin: 20px 0; /* Margem superior e inferior */
        text-align: center; /* Centraliza o texto */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); /* Sombra suave */
        border: 1px solid #b3d9ff; /* Borda sutil */
    }
    
    .main-title h1 {
        color: #2c3e50; /* Wet Asphalt */
        font-size: 2.0rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-family: "Poppins", "Montserrat", sans-serif; /* 🔹 usando Google Fonts */
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }

    /* --- ABAS ESTILO DASHBOARD PREMIUM --- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1A1D29; 
        padding: 8px;
        border-radius: 14px;
        border: 1px solid #2C2F3A;
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-family: "Poppins", "Montserrat", sans-serif;
        padding: 20px 0;
        border-radius: 12px;
        background: #222433;
        color: #ffffff;
        border: 1px solid #2C2F3A;
        transition: all 0.3s ease;
        flex-grow: 1;
        flex-basis: 0;
        text-align: center;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #2A2D3D;
        color: #ffffff;
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59,130,246,0.2);
    }

    /* CÓDIGO NOVO - COM CORES DIFERENTES POR ABA */

/* Estilo base para a aba INATIVA (como já estava) */
.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: "Poppins", "Montserrat", sans-serif;
    padding: 20px 0;
    border-radius: 12px;
    background: #222433; /* Cor cinza escuro para inativas */
    color: #a0a0a0;      /* Cor do texto cinza claro para inativas */
    border: 1px solid #2C2F3A;
    transition: all 0.3s ease;
    flex-grow: 1;
    flex-basis: 0;
    text-align: center;
}

/* Efeito HOVER (passar o mouse) para todas as abas */
.stTabs [data-baseweb="tab"]:hover {
    background: #2A2D3D;
    color: #ffffff;
    border-color: #4a90e2; /* Borda azul ao passar o mouse */
}

/* --- A MÁGICA ACONTECE AQUI: CORES PARA CADA ABA ATIVA --- */

/* Aba 1 (Visão Geral) - Azul */
.stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: #ffffff;
    border-color: #2563eb;
}

/* Aba 2 (Análise Financeira) - Verde */
.stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: #ffffff;
    border-color: #16a34a;
}

/* Aba 3 (Performance) - Laranja */
.stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    color: #ffffff;
    border-color: #ea580c;
}

/* Aba 4 (Motoristas) - Roxo */
.stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    color: #ffffff;
    border-color: #7c3aed;
}

/* Aba 5 (Análise de Rotas) - Vermelho */
.stTabs [data-baseweb="tab"]:nth-child(5)[aria-selected="true"] {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: #ffffff;
    border-color: #dc2626;
}
            
/* Aba 6 (Análise Temporal) - Ciano/Azul-Petróleo */
.stTabs [data-baseweb="tab"]:nth-child(6)[aria-selected="true"] {
    background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); /* Gradiente Ciano */
    color: #ffffff;
    border-color: #0d9488;
}


    .stTabs [data-baseweb="tab-highlight"] {
        background: transparent !important;
    }

    /* === ÍCONES FONT AWESOME NAS ABAS === */
.stTabs [data-baseweb="tab"]::before {
    font-family: "Font Awesome 6 Free"; /* Usa a fonte dos ícones */
    font-weight: 900; /* Necessário para ícones sólidos */
    margin-right: 10px;
    display: inline-block;
    vertical-align: middle;
}

/* Mapeia cada aba para um ícone específico */
.stTabs [data-baseweb="tab"]:nth-child(1)::before { content: "\\f080"; } /* fa-chart-bar (Visão Geral) */
.stTabs [data-baseweb="tab"]:nth-child(2)::before { content: "\\f201"; } /* fa-chart-pie (Análise Financeira) */
.stTabs [data-baseweb="tab"]:nth-child(3)::before { content: "\\f0e7"; } /* fa-bolt (Performance) */
.stTabs [data-baseweb="tab"]:nth-child(4)::before { content: "\\f2c2"; } /* fa-id-card (Motoristas) */
.stTabs [data-baseweb="tab"]:nth-child(5)::before { content: "\\f542"; } /* fa-route (Análise de Rotas) */
.stTabs [data-baseweb="tab"]:nth-child(6)::before { content: "\\f133"; } /* fa-calendar-days (Análise Temporal) */

    /* --- MÉTRICAS MELHORADAS --- */
    .stMetric {
        background: linear-gradient(135deg, #1e2139 0%, #262a47 100%) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        border: 1px solid #3a4063 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        border-color: #4a90e2 !important;
    }
    
    .stMetric > div:nth-child(1) {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #9ca3af !important;
        margin-bottom: 8px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stMetric > div:nth-child(2) {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
    }

    .kpi-container {
        background: linear-gradient(135deg, #1a1d35 0%, #2d3348 100%);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #3a4063;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .kpi-container:hover {
        transform: translateY(-3px);
        /* Sombra 1: Brilho azul | Sombra 2: Sombra escura para profundidade */
        box-shadow: 0 0 15px rgba(74, 144, 226, 0.5), 0 8px 25px rgba(0, 0, 0, 0.3);
        border-color: #4a90e2; 
    }

    
    /* DEPOIS */
    .kpi-title {
        font-size: 14px;
        font-weight: 500;
        color: #FFFFFF; /* BRANCO */
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
        /* ... */
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF; /* Cor padrão para Performance & Operacional (Branco) */
        line-height: 1.1;
    }
    
    /* Cor para métricas POSITIVAS (Financeiro Positivo) */
    .kpi-value.receita,
    .kpi-value.lucro { 
        color: #22c55e; /* Verde */
    }

    /* Cor para CUSTOS (Financeiro Negativo) */
    .kpi-value.custo { 
        color: #f59e0b; /* Laranja/Amarelo */
    }

    /* === KPIs FINANCEIROS EXECUTIVOS (estilo bancário premium) === */
    .finance-kpi-card {
        --accent: #7aa2d6;
        --accent-glow: rgba(122, 162, 214, 0.14);
        --accent-border: rgba(122, 162, 214, 0.34);
        --panel-top: #121925;
        --panel-bottom: #0a1018;
        position: relative;
        overflow: hidden;
        min-height: 136px;
        border-radius: 20px;
        padding: 15px 15px 13px 15px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.035) 0%, rgba(255,255,255,0) 16%),
            linear-gradient(180deg, var(--panel-top) 0%, var(--panel-bottom) 100%);
        border: 1px solid rgba(92, 110, 138, 0.26);
        box-shadow: 0 18px 38px rgba(2,6,23,0.48), inset 0 1px 0 rgba(255,255,255,0.05);
        color: #f8fafc;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }

    .finance-kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, var(--accent) 0%, rgba(255,255,255,0.06) 100%);
        pointer-events: none;
    }

    .finance-kpi-card::after {
        content: "";
        position: absolute;
        right: -52px;
        bottom: -44px;
        width: 168px;
        height: 132px;
        background: linear-gradient(135deg, rgba(255,255,255,0.00) 18%, var(--accent-glow) 52%, rgba(255,255,255,0.00) 84%);
        transform: rotate(-11deg);
        pointer-events: none;
        opacity: 0.95;
    }

    .finance-kpi-card:hover {
        transform: translateY(-3px);
        border-color: var(--accent-border);
        box-shadow: 0 22px 44px rgba(2,6,23,0.58), 0 0 0 1px rgba(122,162,214,0.08);
    }

    .finance-kpi-card.receita {
        --accent: #d4ebff;
        --accent-glow: rgba(125, 190, 255, 0.24);
        --accent-border: rgba(125, 190, 255, 0.34);
        --panel-top: #1c5dac;
        --panel-bottom: #0a2d63;
    }

    .finance-kpi-card.receita .finance-kpi-title {
        color: #ffffff;
    }

    .finance-kpi-card.custo,
    .finance-kpi-card.lucro,
    .finance-kpi-card.margem {
        --accent: #d4ebff;
        --accent-glow: rgba(125, 190, 255, 0.24);
        --accent-border: rgba(125, 190, 255, 0.34);
        --panel-top: #1c5dac;
        --panel-bottom: #0a2d63;
    }

    .finance-kpi-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        position: relative;
        z-index: 1;
    }

    .finance-kpi-title {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 0.70rem;
        font-weight: 700;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.85px;
        line-height: 1.38;
        min-height: 34px;
        padding-right: 4px;
    }

    .finance-kpi-title .help-icon {
        margin-left: 6px;
    }

    .finance-kpi-icon {
        width: 38px;
        height: 38px;
        min-width: 38px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--accent);
        background: linear-gradient(180deg, rgba(7, 12, 20, 0.24) 0%, rgba(7, 12, 20, 0.12) 100%);
        border: 1px solid rgba(255, 255, 255, 0.14);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 8px 16px rgba(2,6,23,0.18);
        backdrop-filter: blur(3px);
        -webkit-backdrop-filter: blur(3px);
        font-size: 0.95rem;
    }

    .finance-kpi-value {
        position: relative;
        z-index: 1;
        margin-top: 13px;
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.82rem;
        font-weight: 800;
        color: #f5f7fb;
        letter-spacing: -0.65px;
        line-height: 1.05;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .finance-kpi-divider {
        position: relative;
        z-index: 1;
        height: 1px;
        margin: 13px 0 10px 0;
        background: linear-gradient(90deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.72) 16%, rgba(255,255,255,0.28) 100%);
        box-shadow: 0 0 1px rgba(255,255,255,0.55);
    }

    .finance-kpi-footer {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(7, 12, 20, 0.28);
        border: 1px solid rgba(255, 255, 255, 0.14);
        color: #f1f5f9;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.15px;
        backdrop-filter: blur(3px);
        -webkit-backdrop-filter: blur(3px);
    }

    .finance-kpi-footer i {
        font-size: 0.84rem;
        color: var(--accent);
        opacity: 1;
    }

    /* ... */


    /* --- SIDEBAR --- */
    .css-1d391kg {
        background-color: #1E1E1E;
    }
    .css-1d391kg .stSelectbox [data-baseweb="select"] > div {
        background-color: #333333;
    }
    .css-1d391kg .stDateInput input {
        background-color: #333333;
    }

    /* === BOTÕES PREMIUM: navegar Dia Específico (◀/▶) === */
    section[data-testid="stSidebar"] div.st-key-btn_prev_dia > button,
    section[data-testid="stSidebar"] div.st-key-btn_next_dia > button {
        height: 40px;
        width: 40px;
        border-radius: 14px;
        padding: 0;
        border: 1px solid rgba(255,255,255,.18);
        background: rgba(255,255,255,.06);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        box-shadow: 0 8px 20px rgba(0,0,0,.22);
        transition: transform .06s ease, background .15s ease, border-color .15s ease, box-shadow .15s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    section[data-testid="stSidebar"] div.st-key-btn_prev_dia > button:hover,
    section[data-testid="stSidebar"] div.st-key-btn_next_dia > button:hover {
        background: rgba(255,255,255,.10);
        border-color: rgba(255,255,255,.30);
        box-shadow: 0 12px 26px rgba(0,0,0,.28);
    }

    section[data-testid="stSidebar"] div.st-key-btn_prev_dia > button:active,
    section[data-testid="stSidebar"] div.st-key-btn_next_dia > button:active {
        transform: scale(0.98);
    }

    section[data-testid="stSidebar"] div.st-key-btn_prev_dia > button p,
    section[data-testid="stSidebar"] div.st-key-btn_next_dia > button p {
        font-size: 18px;
        margin: 0;
        line-height: 1;
    }

    /* Light theme tweaks */
    html[data-theme="light"] section[data-testid="stSidebar"] div.st-key-btn_prev_dia > button,
    html[data-theme="light"] section[data-testid="stSidebar"] div.st-key-btn_next_dia > button {
        border: 1px solid rgba(15,23,42,.12) !important;
        background: rgba(15,23,42,.04) !important;
        box-shadow: 0 12px 26px rgba(15,23,42,.08) !important;
    }

    html[data-theme="light"] section[data-testid="stSidebar"] div.st-key-btn_prev_dia > button:hover,
    html[data-theme="light"] section[data-testid="stSidebar"] div.st-key-btn_next_dia > button:hover {
        background: rgba(15,23,42,.06) !important;
        border-color: rgba(59,130,246,.35) !important;
        box-shadow: 0 16px 32px rgba(15,23,42,.10) !important;
    }


    /* === AJUSTES PARA O MAPA (Folium/Leaflet) === */
    .leaflet-tile {
        border: none !important;
        box-shadow: none !important;
        image-rendering: optimizeSpeed !important;
        transform: translateZ(0);
    }
    .leaflet-container {
        background: #000;
    }
            
    /* --- NOVO ESTILO PARA O ÍCONE DE AJUDA (TOOLTIP) --- */
    .help-icon {
        position: relative; /* Necessário para o posicionamento do tooltip */
        display: inline-block;
        margin-left: 8px; /* Espaço entre o título e o ícone */
        cursor: help; /* Muda o cursor para indicar que é um item de ajuda */
    }

    .help-icon .tooltip-text {
        visibility: hidden; /* Oculta o balão de dica por padrão */
        width: 250px; /* Largura do balão */
        background-color: #2c3e50; /* Cor de fundo escura */
        color: #fff; /* Cor do texto */
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        border: 1px solid #3498db; /* Borda azul */
        
        /* Posicionamento do balão */
        position: absolute;
        z-index: 1;
        bottom: 125%; /* Posiciona acima do ícone */
        left: 50%;
        margin-left: -125px; /* Metade da largura para centralizar */
        
        /* Efeito de fade */
        opacity: 0;
        transition: opacity 0.3s;
    }

    /* Mostra o balão de dica ao passar o mouse sobre o ícone */
    .help-icon:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
            
    /* ▼▼▼ NOVO ESTILO PARA O TÍTULO DA ABA DE MOTORISTAS ▼▼▼ */
    .title-block-motoristas {
        background: #1C1A29; /* Fundo escuro */
        
        /* Bordas laterais na cor roxa para combinar com a aba */
        border-left: 5px solid #8b5cf6;
        border-right: 5px solid #8b5cf6;
        
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-motoristas h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .title-block-motoristas .fa-bullseye {
        font-size: 2.0rem; /* Tamanho do ícone */
        color: #8b5cf6;   /* Cor do ícone (roxo) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            

    /* ▼▼▼ NOVO ESTILO PARA O TÍTULO DA ABA DE ROTAS ▼▼▼ */
    .title-block-rotas {
        background: #1C1A29; /* Fundo escuro */
        
        /* Bordas laterais na cor vermelha para combinar com a aba */
        border-left: 5px solid #ef4444;
        border-right: 5px solid #ef4444;
        
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-rotas h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    .title-block-rotas .fa-route {
        font-size: 2.0rem; /* Tamanho do ícone */
        color: #ef4444;   /* Cor do ícone (vermelho) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            

    /* ▼▼▼ ESTILO CORRIGIDO PARA O TÍTULO DA ABA FINANCEIRA ▼▼▼ */
    .title-block-financeira {
        background: #1C1A29;
        border-left: 5px solid #22c55e; /* Borda verde */
        border-right: 5px solid #22c55e; /* Borda verde */
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-financeira h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Regra genérica para QUALQUER ícone dentro deste bloco de título */
    .title-block-financeira i {
        font-size: 2.0rem;
        color: #22c55e;   /* Cor do ícone (VERDE) */
    }
    /* ▲▲▲ FIM DO ESTILO CORRIGIDO ▲▲▲ */
            
    /* ▼▼▼ ADICIONE ESTE NOVO ESTILO PARA O TÍTULO DE PERFORMANCE ▼▼▼ */
    .title-block-performance {
        background: #1C1A29;
        
        /* Bordas laterais para combinar com a aba de Performance (Laranja) */
        border-left: 5px solid #f97316;
        border-right: 5px solid #f97316;
        
        padding: 5px 30px;
        margin: 20px 0 25px 0; /* Aumenta a margem superior para dar espaço */
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
            
    /* ▼▼▼ NOVO ESTILO PARA O TÍTULO DA ABA TEMPORAL ▼▼▼ */
    .title-block-temporal {
        background: #1C1A29; /* Fundo escuro padrão */
        
        /* Bordas laterais na cor CIANO para combinar com a aba */
        border-left: 5px solid #14b8a6;
        border-right: 5px solid #14b8a6;
        
        padding: 5px 30px;
        margin: 10px 0 25px 0;
        border-radius: 12px;
        width: 100%;
        box-sizing: border-box;
        
        /* Centraliza o ícone e o texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    .title-block-temporal h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Ícone específico para este bloco de título */
    .title-block-temporal .fa-chart-simple {
        font-size: 2.0rem; /* Tamanho do ícone */
        color: #14b8a6;   /* Cor do ícone (Ciano) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */

    .title-block-performance h2 {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.5px;
    }

    /* Ícone específico para este bloco de título */
    .title-block-performance .fa-chart-line {
        font-size: 2.0rem;
        color: #f97316;   /* Cor do ícone (Laranja) */
    }
    /* ▲▲▲ FIM DO NOVO ESTILO ▲▲▲ */
            
    /* ▼▼▼ ESTILO ATUALIZADO PARA TÍTULOS DE SEÇÃO MODERNOS ▼▼▼ */
    .section-title-modern {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.5rem; /* Aumentei um pouco para mais destaque */
        font-weight: 700;  /* <<< PRINCIPAL MUDANÇA AQUI: de 600 para 700 (bold) */
        color: #FFFFFF;    /* Cor branca pura para mais contraste */
        margin-top: 25px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: 0.5px; /* Adiciona um leve espaçamento entre as letras */
    }
    /* ▲▲▲ FIM DO ESTILO ATUALIZADO ▲▲▲ */

    

/* ================================
   LIGHT THEME (auto) — overrides
   Works when Streamlit sets html/body data-theme="light"
   ================================ */

html[data-theme="light"],
body[data-theme="light"]{
    color-scheme: light !important;
}

/* App background + base text */
html[data-theme="light"] body{
    background-color: #f6f8fb !important;
    color: #0f172a !important;
}

html[data-theme="light"] [data-testid="stAppViewContainer"]{
    background-color: #f6f8fb !important;
}

/* Sidebar */
html[data-theme="light"] section[data-testid="stSidebar"]{
    background: #ffffff !important;
    border-right: 1px solid rgba(15, 23, 42, 0.08) !important;
}

/* Make common text readable */
html[data-theme="light"] h1,
html[data-theme="light"] h2,
html[data-theme="light"] h3,
html[data-theme="light"] h4,
html[data-theme="light"] h5,
html[data-theme="light"] h6,
html[data-theme="light"] p,
html[data-theme="light"] label,
html[data-theme="light"] .stMarkdown{
    color: #0f172a !important;
}

/* Tabs (top navigation) */
html[data-theme="light"] .stTabs [data-baseweb="tab-list"]{
    background-color: #ffffff !important;
    border: 1px solid rgba(15, 23, 42, 0.10) !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06) !important;
}

html[data-theme="light"] .stTabs [data-baseweb="tab"]{
    background: #f1f5f9 !important;
    color: #334155 !important;
    border: 1px solid rgba(15, 23, 42, 0.10) !important;
    box-shadow: none !important;
}

html[data-theme="light"] .stTabs [data-baseweb="tab"]:hover{
    background: #e2e8f0 !important;
    color: #0f172a !important;
    border-color: rgba(59, 130, 246, 0.35) !important;
    box-shadow: 0 8px 22px rgba(59, 130, 246, 0.12) !important;
}

/* Selected tabs keep your gradients — just guarantee contrast */
html[data-theme="light"] .stTabs [data-baseweb="tab"][aria-selected="true"]{
    color: #ffffff !important;
}

/* Streamlit metric cards */
html[data-theme="light"] .stMetric{
    background: #ffffff !important;
    border: 1px solid rgba(15, 23, 42, 0.10) !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08) !important;
}

html[data-theme="light"] .stMetric:hover{
    transform: translateY(-2px) !important;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.10) !important;
    border-color: rgba(59, 130, 246, 0.35) !important;
}

html[data-theme="light"] .stMetric > div:nth-child(1){
    color: #64748b !important;
}
html[data-theme="light"] .stMetric > div:nth-child(2){
    color: #0f172a !important;
}

/* Inputs (Selectbox / dropdown look) */
html[data-theme="light"] .stSelectbox > div,
html[data-theme="light"] div[data-baseweb="select"] > div{
    background-color: #ffffff !important;
    border: 1px solid rgba(15, 23, 42, 0.12) !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06) !important;
}

html[data-theme="light"] .stSelectbox *{
    color: #0f172a !important;
}

/* Custom KPI cards */
html[data-theme="light"] .kpi-container,
html[data-theme="light"] .card-info,
html[data-theme="light"] .detail-card,
html[data-theme="light"] .ocupacao-card-custom{
    background: #ffffff !important;
    border: 1px solid rgba(15, 23, 42, 0.10) !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08) !important;
}

html[data-theme="light"] .kpi-title,
html[data-theme="light"] .card-title{
    color: #64748b !important;
}

html[data-theme="light"] .kpi-value,
html[data-theme="light"] .card-value{
    color: #0f172a !important;
}

html[data-theme="light"] .finance-kpi-card{
    background: linear-gradient(180deg, #ffffff 0%, #f5f8fc 100%) !important;
    box-shadow: 0 16px 30px rgba(15,23,42,0.10) !important;
    border-color: rgba(148,163,184,0.22) !important;
}

html[data-theme="light"] .finance-kpi-title{
    color: #5b6b7f !important;
}

html[data-theme="light"] .finance-kpi-icon{
    background: linear-gradient(180deg, #f8fbff 0%, #eef4fa 100%) !important;
    border-color: rgba(148,163,184,0.22) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 8px 18px rgba(15,23,42,0.06) !important;
}

html[data-theme="light"] .finance-kpi-value{
    color: #0f172a !important;
}

html[data-theme="light"] .finance-kpi-divider{
    background: linear-gradient(90deg, rgba(148,163,184,0.00) 0%, rgba(148,163,184,0.40) 18%, rgba(148,163,184,0.14) 100%) !important;
}

html[data-theme="light"] .finance-kpi-footer{
    background: rgba(248,250,252,0.98) !important;
    border-color: rgba(148,163,184,0.24) !important;
    color: #475569 !important;
}

/* Section titles / labels */
html[data-theme="light"] .section-title-modern,
html[data-theme="light"] .detail-section-title,
html[data-theme="light"] .detail-card-title,
html[data-theme="light"] .frota-title{
    color: #0f172a !important;
}

/* Title blocks (headers) */
html[data-theme="light"] .title-block-modern,
html[data-theme="light"] .title-block-performance,
html[data-theme="light"] .title-block-rotas,
html[data-theme="light"] .title-block-temporal,
html[data-theme="light"] .title-block-financeira,
html[data-theme="light"] .title-block-motoristas{
    background: linear-gradient(90deg, rgba(241,245,249,0.95) 0%, rgba(255,255,255,0.85) 100%) !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06) !important;
}

html[data-theme="light"] .title-block-modern h2,
html[data-theme="light"] .title-block-performance h2,
html[data-theme="light"] .title-block-rotas h2,
html[data-theme="light"] .title-block-temporal h2,
html[data-theme="light"] .title-block-financeira h2,
html[data-theme="light"] .title-block-motoristas h2{
    color: #0f172a !important;
}

/* Day-of-week badge */
html[data-theme="light"] .dia-semana-box{
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid rgba(15, 23, 42, 0.10) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06) !important;
}

/* Download button */
html[data-theme="light"] .custom-download-button{
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid rgba(15, 23, 42, 0.12) !important;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08) !important;
}
html[data-theme="light"] .custom-download-button:hover{
    background-color: #f1f5f9 !important;
    border-color: rgba(59, 130, 246, 0.35) !important;
}

/* Fix: main title padding (was 'px') */
html[data-theme="light"] .main-title{
    padding: 18px 20px !important;
}

</style>
            
""", unsafe_allow_html=True)


if _KM_THEME == "light":
    st.markdown("""
    <style>
    /* ================================
       FORCE LIGHT PALETTE (runtime)
       Applies only when Streamlit theme is Light (detected via st.context / config)
       ================================ */

    :root { color-scheme: light !important; }

    body {
        background-color: #f6f8fb !important;
        color: #0f172a !important;
    }
    [data-testid="stAppViewContainer"]{
        background-color: #f6f8fb !important;
    }

    section[data-testid="stSidebar"]{
        background: #ffffff !important;
        border-right: 1px solid rgba(15, 23, 42, 0.08) !important;
    }

    /* Text */
    h1,h2,h3,h4,h5,h6,p,label,.stMarkdown{
        color: #0f172a !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"]{
        background-color: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.10) !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06) !important;
    }
    .stTabs [data-baseweb="tab"]{
        background: #f1f5f9 !important;
        color: #334155 !important;
        border: 1px solid rgba(15, 23, 42, 0.10) !important;
        box-shadow: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover{
        background: #e2e8f0 !important;
        color: #0f172a !important;
        border-color: rgba(59, 130, 246, 0.35) !important;
        box-shadow: 0 8px 22px rgba(59, 130, 246, 0.12) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"]{
        color: #ffffff !important;
    }

    /* Inputs */
    .stSelectbox > div,
    div[data-baseweb="select"] > div{
        background-color: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06) !important;
    }
    .stSelectbox *{
        color: #0f172a !important;
    }
    .custom-selectbox-label{
        color: #64748b !important;
    }

    /* Custom cards */
    .kpi-container,
    .card-info,
    .detail-card,
    .ocupacao-card-custom{
        background: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.10) !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08) !important;
    }
    .kpi-title,
    .card-title{
        color: #64748b !important;
    }
    .kpi-value,
    .card-value{
        color: #0f172a !important;
    }

    .finance-kpi-card{
        background: linear-gradient(180deg, #ffffff 0%, #f5f8fc 100%) !important;
        box-shadow: 0 16px 30px rgba(15,23,42,0.10) !important;
        border-color: rgba(148,163,184,0.22) !important;
    }

    .finance-kpi-title{
        color: #5b6b7f !important;
    }

    .finance-kpi-icon{
        background: linear-gradient(180deg, #f8fbff 0%, #eef4fa 100%) !important;
        border-color: rgba(148,163,184,0.22) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 8px 18px rgba(15,23,42,0.06) !important;
    }

    .finance-kpi-value{
        color: #0f172a !important;
    }

    .finance-kpi-divider{
        background: linear-gradient(90deg, rgba(148,163,184,0.00) 0%, rgba(148,163,184,0.40) 18%, rgba(148,163,184,0.14) 100%) !important;
    }

    .finance-kpi-footer{
        background: rgba(248,250,252,0.98) !important;
        border-color: rgba(148,163,184,0.24) !important;
        color: #475569 !important;
    }

    /* Section titles */
    .section-title-modern,
    .detail-section-title,
    .detail-card-title,
    .frota-title{
        color: #0f172a !important;
    }

    /* Header blocks */
    .title-block-modern,
    .title-block-performance,
    .title-block-rotas,
    .title-block-temporal,
    .title-block-financeira,
    .title-block-motoristas{
        background: linear-gradient(90deg, rgba(241,245,249,0.95) 0%, rgba(255,255,255,0.85) 100%) !important;
        border: 1px solid rgba(15, 23, 42, 0.10) !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06) !important;
    }
    .title-block-modern h2,
    .title-block-performance h2,
    .title-block-rotas h2,
    .title-block-temporal h2,
    .title-block-financeira h2,
    .title-block-motoristas h2{
        color: #0f172a !important;
    }

    /* Day-of-week badge */
    .dia-semana-box{
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid rgba(15, 23, 42, 0.10) !important;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06) !important;
    }

    /* Download button */
    .custom-download-button{
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08) !important;
    }
    .custom-download-button:hover{
        background-color: #f1f5f9 !important;
        border-color: rgba(59, 130, 246, 0.35) !important;
        color: #0f172a !important;
    }

    /* Altair/Vega charts: ensure labels/titles are readable in Light */
    .vega-embed svg text{
        fill: #0f172a !important;
    }
    .vega-embed .role-axis text,
    .vega-embed .role-legend text{
        fill: #334155 !important;
    }

    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    /* === OVERRIDE PREMIUM DO TÍTULO DE OCUPAÇÃO === */
    .title-block-financeira {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 12% 50%, rgba(34, 197, 94, 0.12) 0%, transparent 22%),
            radial-gradient(circle at 88% 50%, rgba(34, 197, 94, 0.10) 0%, transparent 20%),
            linear-gradient(90deg, #111827 0%, #171c2f 45%, #101522 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-left: 3px solid #22c55e !important;
        border-right: 3px solid #22c55e !important;
        padding: 14px 28px !important;
        margin: 12px 0 24px 0 !important;
        border-radius: 18px !important;
        width: 100%;
        box-sizing: border-box;

        display: flex;
        align-items: center;
        justify-content: center;
        gap: 14px;

        box-shadow:
            0 12px 30px rgba(0, 0, 0, 0.32),
            inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);

        transition: all 0.25s ease;
    }

    .title-block-financeira:hover {
        transform: translateY(-1px);
        box-shadow:
            0 16px 34px rgba(0, 0, 0, 0.38),
            0 0 0 1px rgba(34, 197, 94, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    }

    .title-block-financeira::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
            90deg,
            rgba(34, 197, 94, 0.10) 0%,
            rgba(255, 255, 255, 0.02) 18%,
            rgba(255, 255, 255, 0.01) 50%,
            rgba(255, 255, 255, 0.02) 82%,
            rgba(34, 197, 94, 0.10) 100%
        );
        pointer-events: none;
    }

    .title-block-financeira::after {
        content: "";
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 72%;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255,255,255,0.18) 50%,
            transparent 100%
        );
        pointer-events: none;
    }

    .title-block-financeira h2 {
        position: relative;
        z-index: 1;
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 1.70rem !important;
        font-weight: 700;
        color: #ffffff !important;
        margin: 0;
        letter-spacing: -0.3px;
        line-height: 1.15;
    }

    .title-block-financeira i {
        position: relative;
        z-index: 1;
        width: 44px;
        height: 44px;
        min-width: 44px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 1.12rem !important;
        color: #22c55e !important;

        background: linear-gradient(180deg, rgba(34, 197, 94, 0.18) 0%, rgba(34, 197, 94, 0.07) 100%) !important;
        border: 1px solid rgba(34, 197, 94, 0.22) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.05),
            0 8px 20px rgba(0,0,0,0.22) !important;
    }

    html[data-theme="light"] .title-block-financeira {
        background:
            radial-gradient(circle at 12% 50%, rgba(34, 197, 94, 0.10) 0%, transparent 22%),
            radial-gradient(circle at 88% 50%, rgba(34, 197, 94, 0.08) 0%, transparent 20%),
            linear-gradient(90deg, #ffffff 0%, #f8fbff 48%, #f4f8fd 100%) !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        border-left: 3px solid #22c55e !important;
        border-right: 3px solid #22c55e !important;
        box-shadow:
            0 14px 32px rgba(15, 23, 42, 0.08),
            inset 0 1px 0 rgba(255,255,255,0.85) !important;
    }

    html[data-theme="light"] .title-block-financeira h2 {
        color: #0f172a !important;
    }

    html[data-theme="light"] .title-block-financeira::after {
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(15,23,42,0.12) 50%,
            transparent 100%
        ) !important;
    }

    html[data-theme="light"] .title-block-financeira i {
        color: #16a34a !important;
        background: linear-gradient(180deg, rgba(34, 197, 94, 0.14) 0%, rgba(34, 197, 94, 0.05) 100%) !important;
        border: 1px solid rgba(34, 197, 94, 0.18) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.75),
            0 10px 22px rgba(15,23,42,0.08) !important;
    }

    @media (max-width: 900px) {
        .title-block-financeira {
            padding: 12px 18px !important;
            border-radius: 16px !important;
            gap: 10px !important;
        }

        .title-block-financeira h2 {
            font-size: 1.25rem !important;
            text-align: center;
        }

        .title-block-financeira i {
            width: 38px;
            height: 38px;
            min-width: 38px;
            border-radius: 12px;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* === CARDS PREMIUM PARA A VISÃO GERAL (mesmo estilo da Análise Financeira) === */
    .finance-kpi-card.overview-slate {
        --accent: #d7ddff;
        --accent-glow: rgba(129, 140, 248, 0.22);
        --accent-border: rgba(129, 140, 248, 0.34);
        --panel-top: #202744;
        --panel-bottom: #2f385f;
    }

    .finance-kpi-card.overview-blue {
        --accent: #cfe3ff;
        --accent-glow: rgba(59, 130, 246, 0.20);
        --accent-border: rgba(59, 130, 246, 0.34);
        --panel-top: #123562;
        --panel-bottom: #1d4ed8;
    }

    .finance-kpi-card.overview-teal {
        --accent: #cbfbf1;
        --accent-glow: rgba(45, 212, 191, 0.22);
        --accent-border: rgba(45, 212, 191, 0.34);
        --panel-top: #0f3f46;
        --panel-bottom: #0f8b8d;
    }

    .finance-kpi-card.overview-orange {
        --accent: #ffe6c7;
        --accent-glow: rgba(251, 146, 60, 0.22);
        --accent-border: rgba(251, 146, 60, 0.34);
        --panel-top: #7c4318;
        --panel-bottom: #ea580c;
    }

    .finance-kpi-card.overview-indigo {
        --accent: #e2d9ff;
        --accent-glow: rgba(167, 139, 250, 0.22);
        --accent-border: rgba(167, 139, 250, 0.34);
        --panel-top: #312457;
        --panel-bottom: #4f46e5;
    }

    .finance-kpi-card.overview-emerald {
        --accent: #d1fae5;
        --accent-glow: rgba(16, 185, 129, 0.22);
        --accent-border: rgba(16, 185, 129, 0.34);
        --panel-top: #134e4a;
        --panel-bottom: #0f9d74;
    }

    .finance-kpi-card.compact-card {
        min-height: 118px;
        padding: 14px 14px 12px 14px;
        border-radius: 18px;
    }

    .finance-kpi-card.compact-card .finance-kpi-title {
        min-height: auto;
        font-size: 0.68rem;
        line-height: 1.32;
        color: #ffffff;
    }

    .finance-kpi-card.compact-card .finance-kpi-icon {
        width: 34px;
        height: 34px;
        min-width: 34px;
        border-radius: 12px;
        font-size: 0.88rem;
    }

    .finance-kpi-card.compact-card .finance-kpi-value {
        margin-top: 12px;
        font-size: 1.82rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        line-height: 1.05;
    }

    .finance-kpi-card.compact-card .finance-kpi-divider {
        margin: 11px 0 9px 0;
    }

    .finance-kpi-card.compact-card .finance-kpi-footer {
        padding: 4px 9px;
        font-size: 0.72rem;
        gap: 7px;
    }

    .finance-kpi-card.performance-reference {
        --accent: #d7e8ff;
        --accent-glow: rgba(59, 130, 246, 0.18);
        --accent-border: rgba(96, 165, 250, 0.28);
        --panel-top: #0b1f3a;
        --panel-bottom: #123f7a;
    }

    .finance-kpi-card.performance-reference.compact-card {
        min-height: 122px;
        padding: 14px 14px 12px 14px;
        border-radius: 18px;
    }

    .finance-kpi-card.performance-reference.compact-card .finance-kpi-title {
        min-height: 32px;
        font-size: 0.70rem;
        line-height: 1.32;
        color: #ffffff;
    }

    .finance-kpi-card.performance-reference.compact-card .finance-kpi-icon {
        width: 36px;
        height: 36px;
        min-width: 36px;
        border-radius: 13px;
        font-size: 0.90rem;
        color: #f3f8ff;
        background: linear-gradient(180deg, rgba(2, 6, 23, 0.36) 0%, rgba(2, 6, 23, 0.18) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 8px 18px rgba(0,0,0,0.24);
    }

    .finance-kpi-card.performance-reference.compact-card .finance-kpi-value {
        margin-top: 12px;
        font-size: 1.86rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        line-height: 1.05;
        color: #ffffff;
    }

    .finance-kpi-card.performance-reference.compact-card .finance-kpi-footer {
        background: rgba(2, 6, 23, 0.30);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #f8fbff;
    }

    .finance-kpi-card.performance-reference.compact-card .finance-kpi-footer i {
        color: #d7e8ff;
    }

    html[data-theme="light"] .finance-kpi-card.performance-reference {
        background: linear-gradient(180deg, #1b4f95 0%, #123c73 100%) !important;
        border-color: rgba(18, 60, 115, 0.30) !important;
        box-shadow: 0 16px 32px rgba(15, 23, 42, 0.16) !important;
    }

    html[data-theme="light"] .finance-kpi-card.performance-reference .finance-kpi-title,
    html[data-theme="light"] .finance-kpi-card.performance-reference .finance-kpi-value,
    html[data-theme="light"] .finance-kpi-card.performance-reference .finance-kpi-footer {
        color: #ffffff !important;
    }

    html[data-theme="light"] .finance-kpi-card.performance-reference .finance-kpi-footer {
        background: rgba(255,255,255,0.10) !important;
        border-color: rgba(255,255,255,0.14) !important;
    }

    /* Linha separadora branca reforçada para todos os cards */
    .finance-kpi-card .finance-kpi-divider,
    .finance-kpi-card.overview-slate .finance-kpi-divider,
    .finance-kpi-card.overview-blue .finance-kpi-divider,
    .finance-kpi-card.overview-teal .finance-kpi-divider,
    .finance-kpi-card.overview-orange .finance-kpi-divider,
    .finance-kpi-card.overview-indigo .finance-kpi-divider,
    .finance-kpi-card.overview-emerald .finance-kpi-divider,
    .finance-kpi-card.compact-card .finance-kpi-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.72) 16%, rgba(255,255,255,0.28) 100%);
        box-shadow: 0 0 1px rgba(255,255,255,0.55);
    }

    html[data-theme="light"] .finance-kpi-card.overview-slate,
    html[data-theme="light"] .finance-kpi-card.overview-blue,
    html[data-theme="light"] .finance-kpi-card.overview-teal,
    html[data-theme="light"] .finance-kpi-card.overview-orange,
    html[data-theme="light"] .finance-kpi-card.overview-indigo,
    html[data-theme="light"] .finance-kpi-card.overview-emerald {
        box-shadow: 0 16px 32px rgba(15,23,42,0.10) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* === UPGRADE VISUAL DOS CARDS FINANCEIROS === */
    .finance-kpi-card.modern-finance-card {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 16%),
            linear-gradient(
                180deg,
                rgba(6, 18, 40, 0.00) 0%,
                rgba(6, 18, 40, 0.00) 56%,
                rgba(5, 16, 36, 0.16) 74%,
                rgba(3, 10, 24, 0.42) 100%
            ),
            linear-gradient(
                135deg,
                var(--panel-top) 0%,
                #14509c 48%,
                var(--panel-bottom) 100%
            ) !important;
        min-height: 116px !important;
        padding: 12px 14px 10px 14px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.42), inset 0 1px 0 rgba(255,255,255,0.06) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .finance-kpi-card.modern-finance-card .finance-kpi-header {
        gap: 10px;
        margin-bottom: 0;
    }

    .finance-kpi-card.modern-finance-card .finance-kpi-title {
        min-height: unset !important;
        line-height: 1.10 !important;
        margin: 0 !important;
        padding-right: 2px !important;
    }

    .finance-kpi-card.modern-finance-card .finance-kpi-value {
        margin-top: 4px;
        text-shadow: 0 6px 18px rgba(2, 6, 23, 0.18);
    }

    .finance-kpi-card.modern-finance-card::before {
        height: 3px !important;
        opacity: 0.95;
    }

    .finance-kpi-card.modern-finance-card::after {
        right: -38px;
        bottom: -32px;
        width: 178px;
        height: 144px;
        opacity: 1;
    }

    .finance-kpi-card.modern-finance-card .finance-kpi-divider {
        margin: 8px 0 7px 0;
    }

    .finance-kpi-bottom-row {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        min-height: 28px;
    }

    .finance-kpi-bottom-row .finance-kpi-footer {
        margin: 0;
        flex: 0 1 auto;
    }

    .finance-kpi-bottom-row .finance-kpi-change {
        margin: 0 0 0 auto;
        flex: 0 0 auto;
    }

    .finance-kpi-change {
        position: relative;
        z-index: 1;
        margin-top: 0;
        margin-left: auto;
        display: flex;
        width: fit-content;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;
        padding: 4px 9px;
        border-radius: 999px;
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.12px;
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(7, 12, 20, 0.28);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        white-space: nowrap;
    }

    .finance-kpi-change i {
        font-size: 0.75rem;
    }

    .finance-kpi-change small {
        font-size: 0.67rem;
        font-weight: 600;
        opacity: 0.92;
        text-transform: uppercase;
        letter-spacing: 0.25px;
        white-space: nowrap;
    }

    .finance-kpi-change.positive {
        color: #86efac;
        border-color: rgba(34,197,94,0.62);
        background: rgba(7, 12, 20, 0.28);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 0 0 1px rgba(34,197,94,0.14);
    }

    .finance-kpi-change.positive i {
        color: #4ade80;
    }

    .finance-kpi-change.negative {
        color: #fca5a5;
        border-color: rgba(239,68,68,0.62);
        background: rgba(7, 12, 20, 0.28);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 0 0 1px rgba(239,68,68,0.14);
    }

    .finance-kpi-change.negative i {
        color: #f87171;
    }

    .finance-kpi-change.neutral {
        color: #e2e8f0;
        border-color: rgba(148,163,184,0.28);
        background: rgba(7, 12, 20, 0.28);
    }

    html[data-theme="light"] .finance-kpi-card.modern-finance-card {
        box-shadow: 0 18px 34px rgba(15,23,42,0.10), inset 0 1px 0 rgba(255,255,255,0.72) !important;
    }

    html[data-theme="light"] .finance-kpi-change {
        background: rgba(248,250,252,0.98);
        border-color: rgba(148,163,184,0.24);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.75);
    }

    html[data-theme="light"] .finance-kpi-change.positive {
        color: #166534;
        border-color: rgba(22,163,74,0.42);
        background: rgba(248,250,252,0.98);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.75), 0 0 0 1px rgba(34,197,94,0.10);
    }

    html[data-theme="light"] .finance-kpi-change.positive i {
        color: #16a34a;
    }

    html[data-theme="light"] .finance-kpi-change.negative {
        color: #b91c1c;
        border-color: rgba(220,38,38,0.42);
        background: rgba(248,250,252,0.98);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.75), 0 0 0 1px rgba(239,68,68,0.10);
    }

    html[data-theme="light"] .finance-kpi-change.negative i {
        color: #dc2626;
    }

    html[data-theme="light"] .finance-kpi-change.neutral {
        color: #475569;
        border-color: rgba(148,163,184,0.24);
        background: rgba(248,250,252,0.98);
    }
    </style>
""", unsafe_allow_html=True)

# Configura o locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
    except locale.Error:
        pass

# =================================================
# 🔹 CONFIGURAÇÕES GLOBAIS E REGRAS DE NEGÓCIO
# =================================================

# --- DICIONÁRIO DE ROTAS COMPOSTAS ---
# A ordem é importante: rotas mais abrangentes (com mais siglas) devem vir primeiro.
ROTAS_COMPOSTAS = {
    # Rotas com múltiplos destinos
    "ROTA SÃO PAULO": {"CSL", "PBA", "ATB", "SPO"},
    "ROTA GOIÂNIA": {"PDA", "CDS", "GYN"},
    "ROTA COXIM": {"SNR", "PGO", "COX"},
    "ROTA BATAGUASSU": {"SRP", "BLD", "BAT"},
    "ROTA RIO BRILHANTE": {"RBT", "DOU"}, # Nome padronizado
    "ROTA SÃO GABRIEL": {"RVM", "SGO"},
    "ROTA MARACAJU": {"SDL", "MJU"},
    "ROTA JARDIM": {"NQU", "JDM"},
    "ROTA BODOQUENA": {"MDA", "BDQ"},
    "ROTA COSTA RICA": {"CMP", "CRC"},
    "ROTA IVINHEMA": {"NSU", "IVM"},
    "ROTA RIBAS": {"ACL", "RRP"},

    # Rotas com um único destino principal
    "ROTA DOURADOS": {"DOU"},
    "ROTA NOVA ANDRADINA": {"NAD"},
    "ROTA BONITO": {"BTO"},
    "ROTA AQUIDAUANA": {"AQU"},
    "ROTA PONTA PORÃ": {"PPR"},
    "ROTA TRÊS LAGOAS": {"TLG"},
    "ROTA CORUMBÁ": {"COR"},
}

# --- DICIONÁRIO PARA ORDENAÇÃO GEOGRÁFICA ---
# Define a sequência exata em que os destinos devem aparecer.
ORDEM_DAS_ROTAS = {
    # Rotas Compostas (na ordem de entrega desejada)
    "ROTA GOIÂNIA": ["PDA", "CDS", "GYN"],
    "ROTA COXIM": ["SNR", "PGO", "COX"],
    "ROTA SÃO PAULO": ["CSL", "PBA", "ATB", "SPO"],
    "ROTA BATAGUASSU": ["SRP", "BLD", "BAT"],
    "ROTA RIO BRILHANTE": ["RBT", "DOU"], # Nome padronizado
    "ROTA SÃO GABRIEL": ["RVM", "SGO"],
    "ROTA MARACAJU": ["SDL", "MJU"],
    "ROTA JARDIM": ["NQU", "JDM"],
    "ROTA BODOQUENA": ["MDA", "BDQ"],
    "ROTA COSTA RICA": ["CMP", "CRC"],
    "ROTA IVINHEMA": ["NSU", "IVM"],
    "ROTA RIBAS": ["ACL", "RRP"],

    # Rotas de destino único
    "ROTA DOURADOS": ["DOU"],
    "ROTA NOVA ANDRADINA": ["NAD"],
    "ROTA BONITO": ["BTO"],
    "ROTA AQUIDAUANA": ["AQU"],
    "ROTA PONTA PORÃ": ["PPR"],
    "ROTA TRÊS LAGOAS": ["TLG"],
    "ROTA CORUMBÁ": ["COR"],
}

# --- DICIONÁRIO PARA MAPEAMENTO DE SIGLA PARA NOME COMPLETO ---
# "Traduz" as siglas para os nomes completos que serão exibidos nos cards.
MAPA_SIGLA_NOME_COMPLETO = {
    # Rota Goiânia
    "PDA": "PARAISO DAS AGUAS/MS",
    "CDS": "CHAPADAO DO SUL/MS",
    "GYN": "GOIANIA/GO",

    # Rota Coxim
    "SNR": "SONORA/MS",
    "PGO": "PEDRO GOMES/MS",
    "COX": "COXIM/MS",

    # Rota São Paulo
    "CSL": "CASSILANDIA/MS",
    "PBA": "PARANAIBA/MS",
    "ATB": "APARECIDA DO TABOADO/MS",
    "SPO": "SAO PAULO/SP",

    # Rota Bataguassu
    "SRP": "SANTA RITA DO PARDO/MS",
    "BLD": "BRASILANDIA/MS",
    "BAT": "BATAGUASSU/MS",

    # Rota Rio Brilhante
    "RBT": "RIO BRILHANTE/MS",
    "DOU": "DOURADOS/MS",

    # Rota São Gabriel
    "RVM": "RIO VERDE DE MATO GROSSO/MS",
    "SGO": "SAO GABRIEL DO OESTE/MS",

    # Rota Maracaju
    "SDL": "SIDROLANDIA/MS",
    "MJU": "MARACAJU/MS",

    # Rota Jardim
    "NQU": "NIOAQUE/MS",
    "JDM": "JARDIM/MS",

    # Rota Bodoquena
    "MDA": "MIRANDA/MS",
    "BDQ": "BODOQUENA/MS",

    # Rota Costa Rica
    "CMP": "CAMAPUA/MS",
    "CRC": "COSTA RICA/MS",

    # Rota Ivinhema
    "NSU": "NOVA ALVORADA DO SUL/MS",
    "IVM": "IVINHEMA/MS",

    # Rota Ribas
    "ACL": "AGUA CLARA/MS",
    "RRP": "RIBAS DO RIO PARDO/MS",

    # Rotas de Destino Único
    "NAD": "NOVA ANDRADINA/MS",
    "BTO": "BONITO/MS",
    "AQU": "AQUIDAUANA/MS",
    "PPR": "PONTA PORA/MS",
    "TLG": "TRES LAGOAS/MS",
    "COR": "CORUMBA/MS"
}

# =================================================
# 🔹 MAPA PARA COORDENADAS DO MAPA
# =================================================
MAPA_ROTA_CIDADE = {
    # Rotas Compostas (Múltiplos Destinos)
    "ROTA COXIM": "Coxim, MS",
    "ROTA SÃO PAULO": "São Paulo, SP",
    "ROTA GOIÂNIA": "Goiânia, GO",
    "ROTA BATAGUASSU": "Bataguassu, MS",
    "ROTA RIO BRILHANTE": "Rio Brilhante, MS", # Nome padronizado
    "ROTA SÃO GABRIEL": "São Gabriel do Oeste, MS",
    "ROTA MARACAJU": "Maracaju, MS",
    "ROTA JARDIM": "Jardim, MS",
    "ROTA BODOQUENA": "Bodoquena, MS",
    "ROTA COSTA RICA": "Costa Rica, MS",
    "ROTA IVINHEMA": "Ivinhema, MS",
    "ROTA RIBAS": "Ribas do Rio Pardo, MS",

    # Rotas de Destino Único
    "ROTA DOURADOS": "Dourados, MS",
    "ROTA NOVA ANDRADINA": "Nova Andradina, MS",
    "ROTA BONITO": "Bonito, MS",
    "ROTA AQUIDAUANA": "Aquidauana, MS",
    "ROTA PONTA PORÃ": "Ponta Porã, MS",
    "ROTA TRÊS LAGOAS": "Três Lagoas, MS",
    "ROTA CORUMBÁ": "Corumbá, MS",
}


def classificar_viagens_do_dia(df):
    """
    Classifica as viagens com base na coluna 'CONFERENTE CARGA'.
    - Se 'CONFERENTE CARGA' começar com o código "253", a viagem é 'Viagem Extra'.
    - Caso contrário, é 'Rota Completa'.
    """
    # 1. Define o nome da coluna que será usada para a verificação.
    coluna_verificacao = 'CONFERENTE CARGA'

    # 2. Verifica se a coluna de verificação existe no DataFrame.
    if coluna_verificacao not in df.columns:
        # Se não existir, assume que todas são 'Rota Completa' e exibe um aviso.
        df['TIPO_VIAGEM_CALCULADO'] = 'Rota Completa'
        st.warning(f"Aviso: Coluna '{coluna_verificacao}' não encontrada. Não foi possível classificar 'Viagens Extras'.")
        return df

    # 3. Aplica a lógica de classificação.
    #    - Garante que a coluna seja do tipo string para usar funções de texto.
    #    - Usa .str.startswith("253") para verificar se o texto começa com o código.
    #    - 'na=False' trata valores nulos (NaN) como se não correspondessem.
    df['TIPO_VIAGEM_CALCULADO'] = np.where(
        df[coluna_verificacao].astype(str).str.strip().str.startswith("253", na=False),
        'Viagem Extra',      # Valor se a condição for verdadeira
        'Rota Completa'      # Valor se a condição for falsa
    )

    return df


def normalizar_tipo_veiculo_dashboard(valor):
    """Padroniza o tipo de veículo exibido no dashboard."""
    if pd.isna(valor):
        return valor
    valor_normalizado = str(valor).upper().strip()
    return 'TRUCK' if valor_normalizado == '3/4 - CAMINHAO PEQUE' else valor_normalizado


def obter_tipo_veiculo_base(row, coluna='TIPO_CAVALO'):
    """Retorna o tipo original para cálculos internos, preservando regras de capacidade/custo."""
    valor_base = row.get(f'{coluna}_ORIGINAL', row.get(coluna, ''))
    if pd.isna(valor_base):
        return ''
    return str(valor_base).upper().strip()

# --- 2. FUNÇÕES DE APOIO ---
@st.cache_data
def carregar_dados(caminho):
    """Carrega e pré-processa os dados do arquivo Excel."""
    df = pd.read_excel(caminho, sheet_name=0)

    # Converte colunas de data
    for col in ['EMIS_MANIF', 'DIA_SAIDA_MANIF', 'DIA_CHEGADA_MANIF', 'DATA PREV CHEGADA']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # =========================================================
    # 🕔 CRIA DATA OPERACIONAL (VIRADA DE DIA)
    # =========================================================

    # Cria datetime real de saída (data + hora)
    df['DT_SAIDA_MANIF'] = pd.to_datetime(
        df['DIA_SAIDA_MANIF'].astype(str) + ' ' +
        df['HORA_SAIDA_MANIF'].astype(str),
        errors='coerce'
    )

    # Regra de virada de dia (05:00)
    HORA_CORTE_OPERACIONAL = 5

    df['DATA_OPERACIONAL'] = (
        df['DT_SAIDA_MANIF'] - pd.Timedelta(hours=HORA_CORTE_OPERACIONAL)
    ).dt.date

    # ▼▼▼ LINHA ADICIONADA PARA GARANTIR COMPATIBILIDADE ▼▼▼
    # Converte a coluna para o tipo datetime completo, necessário para os filtros.
    df['DATA_OPERACIONAL'] = pd.to_datetime(df['DATA_OPERACIONAL'])
    # ▲▲▲ FIM DA ADIÇÃO ▲▲▲

    # Garante que as colunas de texto sejam string
    for col_texto in ['LACRES', 'SITUACAO', 'OBSERVAÇÕES']:
        if col_texto in df.columns:
            df[col_texto] = df[col_texto].astype(str)

    if 'TIPO_CAVALO' in df.columns:
        df['TIPO_CAVALO_ORIGINAL'] = df['TIPO_CAVALO'].apply(
            lambda x: str(x).upper().strip() if pd.notna(x) else x
        )
        df['TIPO_CAVALO'] = df['TIPO_CAVALO_ORIGINAL'].apply(normalizar_tipo_veiculo_dashboard)

    return df


    # =========================================================

    # Garante que as colunas de texto sejam string
    for col_texto in ['LACRES', 'SITUACAO', 'OBSERVAÇÕES']:
        if col_texto in df.columns:
            df[col_texto] = df[col_texto].astype(str)

    return df

@st.cache_data
def carregar_capacidades(caminho_capacidades):
    """Carrega os dados de capacidade, convertendo toneladas para KG."""
    try:
        df_caps = pd.read_excel(caminho_capacidades)
        
        # 1. Limpa os nomes das colunas
        df_caps.columns = df_caps.columns.str.strip().str.upper()
        
        # 2. Encontra a coluna de placa
        coluna_placa_encontrada = None
        nomes_placa_possiveis = ['PLACA_CARRETA', 'PLACA'] 
        for nome in nomes_placa_possiveis:
            if nome in df_caps.columns:
                coluna_placa_encontrada = nome
                break 
        
        if not coluna_placa_encontrada:
            raise KeyError(f"Nenhuma coluna de PLACA encontrada. Colunas disponíveis: {list(df_caps.columns)}")

        # 3. Encontra a coluna de capacidade
        coluna_capacidade_encontrada = None
        nomes_capacidade_possiveis = ['CAPACIDADE_KG', 'CAPACIDADE', 'PESO', 'CAPACIDADE (KG)'] 
        for nome in nomes_capacidade_possiveis:
            if nome in df_caps.columns:
                coluna_capacidade_encontrada = nome
                break

        if not coluna_capacidade_encontrada:
            raise KeyError(f"Nenhuma coluna de CAPACIDADE encontrada. Colunas disponíveis: {list(df_caps.columns)}")

        # --- ▼▼▼ A MÁGICA ACONTECE AQUI ▼▼▼ ---
        # 4. Converte o valor da capacidade de Toneladas para KG
        #    Garante que o valor seja numérico antes de multiplicar
        df_caps[coluna_capacidade_encontrada] = pd.to_numeric(df_caps[coluna_capacidade_encontrada], errors='coerce').fillna(0) * 1000
        # --- ▲▲▲ FIM DA MUDANÇA ▲▲▲ ---

        # 5. Renomeia as colunas para o padrão do script
        df_caps.rename(columns={
            coluna_placa_encontrada: 'PLACA_CARRETA',
            coluna_capacidade_encontrada: 'CAPACIDADE_KG'
        }, inplace=True)

        # Garante que a coluna da placa seja do tipo texto para a junção
        df_caps['PLACA_CARRETA'] = df_caps['PLACA_CARRETA'].astype(str)
        return df_caps

    except FileNotFoundError:
        st.error(f"❌ **Erro: O arquivo de capacidades '{caminho_capacidades}' não foi encontrado.**")
        return pd.DataFrame()
    except KeyError as e: 
        st.error(f"❌ **Erro de Coluna no arquivo 'cadastro_veiculos.xlsx':** {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro inesperado ao ler o arquivo de capacidades: {e}")
        return pd.DataFrame()

def to_excel(df):
    """
    Converte um DataFrame do Pandas para um arquivo Excel em memória,
    com auto-ajuste da largura das colunas.
    """
    output = BytesIO()
    # Cria um ExcelWriter usando o engine 'xlsxwriter' para ter mais controle
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DadosFiltrados')
        
        # Acessa o workbook e a worksheet para customização
        workbook = writer.book
        worksheet = writer.sheets['DadosFiltrados']
        
        # Itera sobre as colunas do DataFrame para ajustar a largura
        for i, col in enumerate(df.columns):
            # Encontra o comprimento máximo do conteúdo na coluna (incluindo o cabeçalho)
            column_len = max(df[col].astype(str).map(len).max(), len(col))
            # Adiciona um pouco de espaço extra (padding)
            worksheet.set_column(i, i, column_len + 2)
            
    # Pega os dados binários do arquivo Excel gerado na memória
    processed_data = output.getvalue()
    return processed_data

def obter_info_periodo(df, data_inicio=None, data_fim=None):
    """Retorna informações sobre o período selecionado com base na EMISSÃO."""
    # (Esta função sua permanece inalterada)
    if data_inicio and data_fim:
        df_periodo = df[(df['EMIS_MANIF'].dt.date >= data_inicio) & \
                       (df['EMIS_MANIF'].dt.date <= data_fim)]
    elif data_inicio:
        df_periodo = df[df['EMIS_MANIF'].dt.date == data_inicio]
    else:
        df_periodo = df
    
    num_registros = len(df_periodo)
    num_veiculos = df_periodo['PLACA_CAVALO'].nunique()
    num_motoristas = df_periodo['MOTORISTA'].nunique()
    
    return num_registros, num_veiculos, num_motoristas

# ▼▼▼ COLE AS FUNÇÕES DE FORMATAÇÃO AQUI ▼▼▼

def formatar_moeda(valor):
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    try:
        return locale.currency(valor, grouping=True)
    except (NameError, TypeError, ValueError):
        try:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return "R$ 0,00"

def formatar_percentual(valor):
    """Formata um número como percentual com vírgula (ex: 82,1%)."""
    try:
        return f"{valor:.0f}%"
    except (ValueError, TypeError):
        return "0,0%"

def formatar_numero(valor, casas_decimais=0):
    """Formata um número com separador de milhar e vírgula decimal (padrão BR)."""
    try:
        return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0"


def normalizar_nome_coluna(nome):
    import unicodedata
    return unicodedata.normalize('NFKD', str(nome)).encode('ASCII', 'ignore').decode('ASCII').upper().strip()


def localizar_primeira_coluna_disponivel(df_base, nomes_candidatos):
    mapa_colunas = {normalizar_nome_coluna(col): col for col in df_base.columns}
    for nome in nomes_candidatos:
        col_encontrada = mapa_colunas.get(normalizar_nome_coluna(nome))
        if col_encontrada:
            return col_encontrada
    return None


def somar_primeira_coluna_disponivel(df_base, nomes_candidatos):
    col_encontrada = localizar_primeira_coluna_disponivel(df_base, nomes_candidatos)
    if col_encontrada:
        return pd.to_numeric(df_base[col_encontrada], errors='coerce').fillna(0).sum()
    return 0


def obter_nome_coluna_peso_calculo(df_base):
    return localizar_primeira_coluna_disponivel(
        df_base,
        [
            'PESO CALCULO (KG)',
            'PESO CÁLCULO (KG)',
            'PESO CALCULADO (KG)',
            'PESO CALCULO KG',
            'PESO CÁLCULO KG',
            'PESO_CALCULO_KG'
        ]
    )


def somar_peso_calculo(df_base):
    total = somar_primeira_coluna_disponivel(
        df_base,
        [
            'PESO CALCULO (KG)',
            'PESO CÁLCULO (KG)',
            'PESO CALCULADO (KG)',
            'PESO CALCULO KG',
            'PESO CÁLCULO KG',
            'PESO_CALCULO_KG'
        ]
    )
    if total == 0 and 'PESO REAL (KG)' in df_base.columns:
        return pd.to_numeric(df_base['PESO REAL (KG)'], errors='coerce').fillna(0).sum()
    return total


def garantir_coluna_peso_calculo(df_base, nome_saida='Peso Cálculo (KG)', usar_fallback_real=True):
    """Cria/atualiza uma coluna padrão de peso cálculo a partir da primeira coluna disponível."""
    if df_base is None:
        return df_base

    coluna_origem = obter_nome_coluna_peso_calculo(df_base)
    if coluna_origem is None and usar_fallback_real and 'PESO REAL (KG)' in df_base.columns:
        coluna_origem = 'PESO REAL (KG)'

    if coluna_origem is None:
        if nome_saida not in df_base.columns:
            df_base[nome_saida] = 0.0
    else:
        df_base[nome_saida] = pd.to_numeric(df_base[coluna_origem], errors='coerce').fillna(0)

    return df_base


def obter_cor_ocupacao(percentual):
    """Retorna gradiente da barra de ocupação em padrão visual do dashboard."""
    try:
        percentual = float(percentual)
    except (TypeError, ValueError):
        percentual = 0

    if percentual < 50:
        return "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)"
    elif percentual <= 80:
        return "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)"
    return "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)"


def obter_cor_ociosidade(percentual):
    """Retorna gradiente da barra de ociosidade em padrão visual do dashboard."""
    try:
        percentual = float(percentual)
    except (TypeError, ValueError):
        percentual = 0

    if percentual < 20:
        return "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)"
    elif percentual <= 50:
        return "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)"
    return "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)"


def render_financial_kpi_card(
    titulo,
    valor,
    classe="receita",
    icone="fa-chart-simple",
    rodape="Indicador financeiro",
    variacao_percentual=None,
    modo_variacao="higher_better",
    variacao_label="vs dia ant."
):
    """Renderiza KPI financeiro com visual premium e chip de comparação diária."""
    status_variacao, icone_variacao = obter_status_variacao_card(variacao_percentual, modo_variacao)

    bloco_variacao = ""
    if variacao_percentual is not None:
        bloco_variacao = (
            f"<div class='finance-kpi-change {status_variacao}'>"
            f"<i class='fa-solid {icone_variacao}'></i>"
            f"<span>{formatar_variacao_compacta(variacao_percentual)}</span>"
            f"<small>{variacao_label}</small>"
            f"</div>"
        )

    bloco_inferior = (
        f"<div class='finance-kpi-bottom-row'>"
        f"<div class='finance-kpi-footer'><i class='fa-solid {icone}'></i><span>{rodape}</span></div>"
        f"{bloco_variacao}"
        f"</div>"
    )

    card_html = textwrap.dedent(f"""
    <div class='finance-kpi-card {classe} modern-finance-card'>
        <div class='finance-kpi-header'>
            <div class='finance-kpi-title'>{titulo}</div>
            <div class='finance-kpi-icon'><i class='fa-solid {icone}'></i></div>
        </div>
        <div class='finance-kpi-value'>{valor}</div>
        <div class='finance-kpi-divider'></div>
        {bloco_inferior}
    </div>
    """).strip()

    st.markdown(card_html, unsafe_allow_html=True)


def render_overview_kpi_card(
    titulo,
    valor,
    icone="fa-chart-simple",
    rodape="Indicador operacional",
    classe="overview-slate",
    compact=True,
    extra_classes=""
):
    """Renderiza cards da Visão Geral no mesmo padrão premium da Análise Financeira."""
    classes_list = [classe]
    if compact:
        classes_list.append("compact-card")
    if extra_classes:
        classes_list.append(extra_classes)

    classes = " ".join(classes_list)

    st.markdown(f"""
        <div class='finance-kpi-card {classes}'>
            <div class='finance-kpi-header'>
                <div class='finance-kpi-title'>{titulo}</div>
                <div class='finance-kpi-icon'><i class='fa-solid {icone}'></i></div>
            </div>
            <div class='finance-kpi-value'>{valor}</div>
            <div class='finance-kpi-divider'></div>
            <div class='finance-kpi-footer'>
                <i class='fa-solid {icone}'></i>
                <span>{rodape}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_performance_reference_kpi_card(titulo, valor, icone="fa-chart-simple", rodape="Indicador de performance"):
    """Renderiza os KPIs da aba Performance no mesmo visual premium do card de referência azul."""
    st.markdown(f"""
        <div class='finance-kpi-card performance-reference compact-card'>
            <div class='finance-kpi-header'>
                <div class='finance-kpi-title'>{titulo}</div>
                <div class='finance-kpi-icon'><i class='fa-solid {icone}'></i></div>
            </div>
            <div class='finance-kpi-value'>{valor}</div>
            <div class='finance-kpi-divider'></div>
            <div class='finance-kpi-footer'>
                <i class='fa-solid {icone}'></i>
                <span>{rodape}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    


def formatar_variacao_compacta(valor):
    """Formata a variação percentual em texto curto para o chip do card."""
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return "—"

    if math.isnan(valor) or math.isinf(valor):
        return "—"

    sinal = "+" if valor > 0 else ""
    return f"{sinal}{valor:.1f}%".replace(".", ",")


def obter_status_variacao_card(variacao_percentual, modo_variacao="higher_better"):
    """Define a cor da variação considerando se subir ou cair é melhor."""
    if variacao_percentual is None:
        return "neutral", "fa-minus"

    try:
        variacao_percentual = float(variacao_percentual)
    except (TypeError, ValueError):
        return "neutral", "fa-minus"

    if math.isnan(variacao_percentual) or math.isinf(variacao_percentual) or abs(variacao_percentual) < 0.05:
        return "neutral", "fa-minus"

    positiva = variacao_percentual > 0
    desempenho_favoravel = positiva if modo_variacao == "higher_better" else not positiva

    if desempenho_favoravel:
        return "positive", "fa-arrow-trend-up"
    return "negative", "fa-arrow-trend-down"


def calcular_variacao_percentual(valor_atual, valor_anterior):
    """Calcula a variação percentual entre o valor atual e o valor anterior."""
    try:
        valor_atual = float(valor_atual)
        valor_anterior = float(valor_anterior)
    except (TypeError, ValueError):
        return None

    if math.isnan(valor_atual) or math.isnan(valor_anterior) or math.isinf(valor_atual) or math.isinf(valor_anterior):
        return None

    if abs(valor_anterior) < 1e-9:
        return None

    return ((valor_atual - valor_anterior) / abs(valor_anterior)) * 100


def calcular_resumo_financeiro(df_base):
    """Centraliza o cálculo dos KPIs financeiros principais."""
    resumo_padrao = {
        "receita_total": 0.0,
        "custo_ctrb_os": 0.0,
        "custo_icms": 0.0,
        "custo_total": 0.0,
        "lucro_estimado": 0.0,
        "margem_lucro": 0.0,
    }

    if df_base is None or df_base.empty:
        return resumo_padrao

    receita_total = pd.to_numeric(df_base.get('FRETE-R$', pd.Series(dtype='float64')), errors='coerce').fillna(0).sum()
    custo_icms = pd.to_numeric(df_base.get('ICMS-R$', pd.Series(dtype='float64')), errors='coerce').fillna(0).sum()

    custo_ctrb_os = 0.0
    df_custo = df_base.copy()
    if 'VIAGEM_ID' not in df_custo.columns:
        df_custo['VIAGEM_ID'] = df_custo.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

    resumo_viagens_custo = df_custo.groupby('VIAGEM_ID').agg(
        PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
        CUSTO_OS=('OS-R$', 'max'),
        CUSTO_CTRB=('CTRB-R$', 'max'),
        DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.astype(str).unique()))
    ).reset_index()

    def _calcular_custo_final_viagem(row):
        custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
        destinos_str = str(row.get('DESTINOS', '')).upper()
        if 'GYN' in destinos_str or 'SPO' in destinos_str:
            return custo_base / 2
        return custo_base

    if not resumo_viagens_custo.empty:
        resumo_viagens_custo['CUSTO_FINAL_VIAGEM'] = resumo_viagens_custo.apply(_calcular_custo_final_viagem, axis=1)
        custo_ctrb_os = pd.to_numeric(resumo_viagens_custo['CUSTO_FINAL_VIAGEM'], errors='coerce').fillna(0).sum()

    custo_total = custo_ctrb_os + custo_icms
    lucro_estimado = receita_total - custo_total
    margem_lucro = (lucro_estimado / receita_total * 100) if receita_total > 0 else 0.0

    return {
        "receita_total": receita_total,
        "custo_ctrb_os": custo_ctrb_os,
        "custo_icms": custo_icms,
        "custo_total": custo_total,
        "lucro_estimado": lucro_estimado,
        "margem_lucro": margem_lucro,
    }


def construir_serie_financeira(df_base, frequencia="D"):
    """Cria uma série temporal de Receita, Custo e Lucro usando a mesma lógica financeira dos KPIs."""
    colunas_saida = ['PERIODO_DT', 'PERIODO_LABEL', 'Receita', 'Custo', 'Lucro']

    if df_base is None or df_base.empty:
        return pd.DataFrame(columns=colunas_saida)

    coluna_data = None
    for candidato in ['DATA_OPERACIONAL', 'DATA_EMISSAO']:
        if candidato in df_base.columns:
            coluna_data = candidato
            break

    if coluna_data is None:
        return pd.DataFrame(columns=colunas_saida)

    df_serie = df_base.copy()
    df_serie['_DATA_SERIE'] = pd.to_datetime(df_serie[coluna_data], errors='coerce')
    df_serie = df_serie.dropna(subset=['_DATA_SERIE']).copy()

    if df_serie.empty:
        return pd.DataFrame(columns=colunas_saida)

    frequencia = str(frequencia).upper().strip()
    meses_unicos = df_serie['_DATA_SERIE'].dt.to_period('M').nunique()

    if frequencia == 'W':
        periodos = df_serie['_DATA_SERIE'].dt.to_period('W')
        df_serie['_PERIODO_DT'] = periodos.apply(lambda p: p.start_time)
        freq_reindex = '7D'
    elif frequencia == 'M':
        periodos = df_serie['_DATA_SERIE'].dt.to_period('M')
        df_serie['_PERIODO_DT'] = periodos.apply(lambda p: p.start_time)
        freq_reindex = 'MS'
    else:
        df_serie['_PERIODO_DT'] = df_serie['_DATA_SERIE'].dt.normalize()
        freq_reindex = 'D'

    registros = []
    for periodo_dt, grupo in df_serie.groupby('_PERIODO_DT', sort=True):
        resumo = calcular_resumo_financeiro(grupo)
        ts = pd.Timestamp(periodo_dt)

        if frequencia == 'W':
            periodo_label = f"Sem {ts.strftime('%d/%m')}"
        elif frequencia == 'M':
            periodo_label = ts.strftime('%m/%Y')
        else:
            periodo_label = ts.strftime('%d') if meses_unicos == 1 else ts.strftime('%d/%m')

        registros.append({
            'PERIODO_DT': ts,
            'PERIODO_LABEL': periodo_label,
            'Receita': resumo['receita_total'],
            'Custo': resumo['custo_total'],
            'Lucro': resumo['lucro_estimado'],
        })

    if not registros:
        return pd.DataFrame(columns=colunas_saida)

    serie = pd.DataFrame(registros, columns=colunas_saida).sort_values('PERIODO_DT').reset_index(drop=True)

    if len(serie) >= 2:
        faixa_completa = pd.date_range(
            start=serie['PERIODO_DT'].min(),
            end=serie['PERIODO_DT'].max(),
            freq=freq_reindex
        )
        serie = (
            serie.set_index('PERIODO_DT')
            .reindex(faixa_completa)
            .rename_axis('PERIODO_DT')
            .reset_index()
        )
        serie[['Receita', 'Custo', 'Lucro']] = serie[['Receita', 'Custo', 'Lucro']].fillna(0)

        def _formatar_label(ts):
            if frequencia == 'W':
                return f"Sem {ts.strftime('%d/%m')}"
            if frequencia == 'M':
                return ts.strftime('%m/%Y')
            return ts.strftime('%d') if meses_unicos == 1 else ts.strftime('%d/%m')

        serie['PERIODO_LABEL'] = serie['PERIODO_DT'].apply(_formatar_label)

    return serie[colunas_saida]


def aplicar_filtros_para_comparacao_dia(df_base):
    """Reaplica os filtros principais sobre o dia anterior para comparação diária dos cards."""
    df_comp = df_base.copy()
    if df_comp.empty:
        return df_comp

    if 'VIAGEM_ID' not in df_comp.columns:
        df_comp['VIAGEM_ID'] = df_comp.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

    if tipo_viagem_sel != "Todas":
        df_classificado = classificar_viagens_do_dia(df_comp)
        if 'TIPO_VIAGEM_CALCULADO' in df_classificado.columns:
            df_comp = df_classificado[df_classificado['TIPO_VIAGEM_CALCULADO'] == tipo_viagem_sel].copy()

    if busca_placa:
        df_comp = df_comp[df_comp['PLACA_CAVALO'].astype(str).str.contains(busca_placa.strip(), case=False, na=False)]
    elif busca_lacre:
        df_comp = df_comp[df_comp['LACRES'].astype(str).str.contains(busca_lacre.strip(), case=False, na=False)]
    else:
        if viagem_especifica_sel != "(Todos)" or grupo_rota_sel != "(Todos)":
            return pd.DataFrame(columns=df_comp.columns)

        if motorista_sel != "(Todos)":
            df_comp = df_comp[df_comp["MOTORISTA"] == motorista_sel]

        if desempenho_ctrb_sel != "(Todos)" and not df_comp.empty:
            df_temp_desempenho = df_comp.copy()
            if 'VIAGEM_ID' not in df_temp_desempenho.columns:
                df_temp_desempenho['VIAGEM_ID'] = df_temp_desempenho.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

            resumo_viagens_desempenho = df_temp_desempenho.groupby('VIAGEM_ID').agg(
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'),
                FRETE_TOTAL=('FRETE-R$', 'sum'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.astype(str).unique()))
            ).reset_index()

            def _calcular_custo_desempenho(row):
                custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base

            resumo_viagens_desempenho['CUSTO_FINAL'] = resumo_viagens_desempenho.apply(_calcular_custo_desempenho, axis=1)
            resumo_viagens_desempenho['CTRB_FRETE_PERC'] = (
                resumo_viagens_desempenho['CUSTO_FINAL'] /
                resumo_viagens_desempenho['FRETE_TOTAL'].replace(0, np.nan)
            ).fillna(0) * 100

            viagens_filtradas_ids = []
            if desempenho_ctrb_sel == "Bom (Até 25%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[resumo_viagens_desempenho['CTRB_FRETE_PERC'] <= 25]['VIAGEM_ID']
            elif desempenho_ctrb_sel == "Regular (Entre 26 a 45%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[(resumo_viagens_desempenho['CTRB_FRETE_PERC'] > 25) & (resumo_viagens_desempenho['CTRB_FRETE_PERC'] <= 45)]['VIAGEM_ID']
            elif desempenho_ctrb_sel == "Péssimo (Acima de 45%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[resumo_viagens_desempenho['CTRB_FRETE_PERC'] > 45]['VIAGEM_ID']

            df_comp = df_comp[df_comp['VIAGEM_ID'].isin(viagens_filtradas_ids)]

        if destinos_sel:
            df_comp = df_comp[df_comp['CIDADE_UF_DEST'].astype(str).isin(destinos_sel)].copy()

    if placa_sel != "(Todos)":
        df_comp = df_comp[df_comp["PLACA_CAVALO"] == placa_sel]
    if tipo_sel != "(Todos)":
        df_comp = df_comp[df_comp["TIPO_CAVALO"] == tipo_sel]
    if proprietario_sel != "(Todos)":
        df_comp = df_comp[df_comp["PROPRIETARIO_CAVALO"] == proprietario_sel]

    return df_comp

    # ▼▼▼ COLE AS NOVAS FUNÇÕES DO MAPA AQUI ▼▼▼

@st.cache_data
def get_coords(cidade_nome):
    """Busca as coordenadas (latitude, longitude) de uma cidade usando a API Nominatim."""
    try:
        # Usamos um user_agent para identificar nossa aplicação, uma boa prática para APIs públicas
        headers = {'User-Agent': 'MeuDashboardStreamlit/1.0'}
        url = f"https://nominatim.openstreetmap.org/search?q={cidade_nome}&format=json&limit=1"
        response = requests.get(url, headers=headers, timeout=10 ) # Adicionado timeout
        response.raise_for_status() # Lança um erro para respostas ruins (4xx ou 5xx)
        data = response.json()
        if data:
            # Retorna as coordenadas como uma tupla de floats
            return (float(data[0]['lat']), float(data[0]['lon']))
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar coordenadas para {cidade_nome}: {e}")
    except (KeyError, IndexError):
        st.warning(f"Não foi possível encontrar coordenadas para '{cidade_nome}'.")
    return None

@st.cache_data
def get_route(coord_origem, coord_destino):
    """Obtém a rota (geometria polyline) entre duas coordenadas usando a API do OSRM."""
    if not coord_origem or not coord_destino:
        return None
    
    # Formata as coordenadas para a URL da API
    lon_orig, lat_orig = coord_origem[1], coord_origem[0]
    lon_dest, lat_dest = coord_destino[1], coord_destino[0]
    
    url = f"http://router.project-osrm.org/route/v1/driving/{lon_orig},{lat_orig};{lon_dest},{lat_dest}?overview=full&geometries=polyline"
    
    try:
        response = requests.get(url, timeout=10 ) # Adicionado timeout
        response.raise_for_status()
        data = response.json()
        if data['routes']:
            # Decodifica a geometria polyline para uma lista de coordenadas (lat, lon)
            route_polyline = data['routes'][0]['geometry']
            return polyline.decode(route_polyline)
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao buscar a rota: {e}")
    except (KeyError, IndexError):
        st.warning("Não foi possível obter a geometria da rota.")
    return None

def criar_mapa_folium(coord_origem, coord_destino, nome_cidade_destino, rota_coords):
    """
    Cria e configura o mapa Folium com múltiplas camadas, marcadores,
    a linha da rota e um controle para alternar as camadas.
    """
    if not coord_origem or not coord_destino:
        return None

    # Calcula o ponto central do mapa
    map_center = [
        (coord_origem[0] + coord_destino[0]) / 2,
        (coord_origem[1] + coord_destino[1]) / 2
    ]

    # Cria o mapa base (a primeira camada será a padrão)
    m = folium.Map(location=map_center, zoom_start=7, tiles=None)

    # --- CAMADAS DE FUNDO ---

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        attr='Google',
        name='🌄 Terreno (Google Maps)'
    ).add_to(m)

    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='🌃 Modo Escuro (CartoDB)'
    ).add_to(m)

    folium.TileLayer(
        'OpenStreetMap',
        name='🗺️ Ruas (OpenStreetMap)'
    ).add_to(m)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr='Google',
        name='🛰️ Satélite (Google Maps)'
    ).add_to(m)

    # --- GRUPO DE ELEMENTOS (rota + marcadores) ---
    feature_group = folium.FeatureGroup(name="🚚 Trajeto da Viagem").add_to(m)

    # Marcador de Origem
    folium.Marker(
        location=coord_origem,
        popup="<b>Origem:</b><br>Campo Grande, MS",
        tooltip="Origem",
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    ).add_to(feature_group)

    # Marcador de Destino
    folium.Marker(
        location=coord_destino,
        popup=f"<b>Destino:</b><br>{nome_cidade_destino}",
        tooltip="Destino",
        icon=folium.Icon(color='red', icon='truck', prefix='fa')
    ).add_to(feature_group)

    # Linha da rota (se existir)
    if rota_coords:
        folium.PolyLine(
            locations=rota_coords,
            color='#1E90FF',
            weight=5,
            opacity=0.9
        ).add_to(feature_group)

    # --- CONTROLE DE CAMADAS ---
    folium.LayerControl(collapsed=False).add_to(m)
    
    Fullscreen(position='topright', title='Tela cheia', title_cancel='Sair').add_to(m)

    return m

# ▼▼▼ COLE A NOVA FUNÇÃO AQUI ▼▼▼
def ordenar_destinos_geograficamente(destinos_da_viagem, rotas_completas, ordem_das_rotas):
    """
    Ordena uma lista de siglas de destino com base na ordem geográfica pré-definida
    para a rota correspondente. Funciona para todas as rotas.
    """
    # 1. Converte as siglas da viagem para um conjunto (set) para facilitar a comparação
    destinos_set = set(destinos_da_viagem)
    
    # 2. Identifica a qual rota principal esta viagem pertence
    nome_rota_identificada = None
    # Itera sobre o dicionário de rotas compostas para encontrar a correspondência
    for nome_rota, siglas_rota in rotas_completas.items():
        if siglas_rota.issubset(destinos_set):
            nome_rota_identificada = nome_rota
            break # Para na primeira correspondência encontrada (importante pela ordem do dicionário)

    # 3. Se uma rota foi identificada, busca sua ordem específica
    if nome_rota_identificada:
        # Pega a lista de ordem para a rota encontrada (ex: ["SRP", "BLD", "BAT"])
        ordem_especifica = ordem_das_rotas.get(nome_rota_identificada, [])
        
        # Cria um mapa de posição para a ordenação (ex: {'SRP': 0, 'BLD': 1, 'BAT': 2})
        mapa_de_ordem = {sigla: pos for pos, sigla in enumerate(ordem_especifica)}
        
        # Ordena os destinos da viagem usando o mapa
        destinos_ordenados = sorted(destinos_da_viagem, key=lambda d: mapa_de_ordem.get(d, 99))
        
        return ' / '.join(destinos_ordenados)
    
    # 4. Fallback: Se nenhuma rota composta for encontrada, ordena alfabeticamente
    # Isso lida com rotas de destino único ou combinações não previstas.
    return ' / '.join(sorted(destinos_da_viagem))
# ▲▲▲ FIM DA NOVA FUNÇÃO ▲▲▲


# --- 3. CARREGAMENTO DOS DADOS ---
caminho_do_arquivo = os.path.join("Arquivos", "Relatorio_de_Viagens.xlsx")
try:
    df_bruto = carregar_dados(caminho_do_arquivo)
except FileNotFoundError:
    st.error(f"❌ **Erro: O arquivo '{caminho_do_arquivo}' não foi encontrado.**")
    st.stop()

# --- INÍCIO DA MUDANÇA ---
# 1. Define a lista de proprietários que você quer manter
proprietarios_desejados = [
    'KM TRANSPORTES ROD. DE CARGAS LTDA',
    'MARCELO H LEMOS BERALDO E CIA LTDA ME'
]

# 2. Filtra o DataFrame para conter apenas os proprietários da lista
df_original = df_bruto[df_bruto['PROPRIETARIO_CAVALO'].isin(proprietarios_desejados)].copy()

### FILTRO 1: REMOVER MANIFESTOS CANCELADOS ###
if 'SITUACAO' in df_original.columns:
    df_original['SITUACAO'] = df_original['SITUACAO'].astype(str)
    df_original = df_original[df_original['SITUACAO'].str.upper().str.strip() != 'CANCELADO']
else:
    st.warning("⚠️ A coluna 'SITUACAO' não foi encontrada. Não foi possível filtrar manifestos cancelados.")
### FIM DO FILTRO 1 ###

### FILTRO 2: REMOVER RETIRADAS DE TERENOS (CONFERENTE 224) ###
if 'CONFERENTE CARGA' in df_original.columns:
    df_original['CONFERENTE CARGA'] = df_original['CONFERENTE CARGA'].astype(str)
    padrao_terenos_conf = "224 - ERISSCGR"
    df_original = df_original[~df_original['CONFERENTE CARGA'].str.contains(padrao_terenos_conf, case=False, na=False)]
else:
    st.warning("⚠️ A coluna 'CONFERENTE CARGA' não foi encontrada. Não foi possível filtrar as retiradas de Terenos.")
### FIM DO FILTRO 2 ###


# ▼▼▼ NOVO FILTRO ADICIONADO AQUI ▼▼▼
### FILTRO 3: REMOVER VIAGENS COM DESTINO TERENOS (TRN) ###
if 'DEST_MANIF' in df_original.columns:
    # Garante que a coluna seja do tipo string para a comparação
    df_original['DEST_MANIF'] = df_original['DEST_MANIF'].astype(str)
    
    # Remove todas as linhas onde a sigla do destino é exatamente 'TRN'
    # .str.strip() remove espaços em branco antes e depois da sigla
    df_original = df_original[df_original['DEST_MANIF'].str.strip().str.upper() != 'TRN']
else:
    st.warning("⚠️ A coluna 'DEST_MANIF' não foi encontrada. Não foi possível filtrar viagens para Terenos.")
### ▲▲▲ FIM DO NOVO FILTRO ▲▲▲


# 3. (Opcional) Adiciona um aviso se nenhum dado for encontrado após os filtros
if df_original.empty:
    st.warning("⚠️ Nenhum dado encontrado para os proprietários e filtros aplicados. Verifique o arquivo de origem.")
    st.stop()
# --- FIM DA MUDANÇA ---

# ▼▼▼ NOVA LÓGICA FIXA DE CAPACIDADE BASEADA EM PLACA + TIPO ▼▼▼

# Dicionário fixo de capacidades por tipo
CAPACIDADES_FIXAS = {
    "TRUCK": 14000,
    "BI-TRUCK": 19000,
    "CARRETA": 25000,
    "TOCO": 10000
}

# Lista de placas BI-TRUCK informadas
PLACAS_BITRUCK = [
    "REW6J23",
    "GBQ0I23",
    "RWG9G33",
    "SFH1C15"
]

def identificar_tipo(row):

    # tenta detectar automaticamente o nome da coluna de placa
    possiveis_colunas_placa = ['PLACA', 'PLACA_CAVALO', 'PLACA_CARRETA',
                               'Veículo (Placa)', 'VEÍCULO (PLACA)', 'VEICULO', 'VEÍCULO']

    placa = None
    for col in possiveis_colunas_placa:
        if col in row.index:
            placa = str(row[col]).strip().upper()
            break

    # se não encontrou placa
    if placa is None:
        tipo_bruto = str(row.get("TIPO_CAVALO", "")).upper().strip()
    else:
        tipo_bruto = str(row.get("TIPO_CAVALO", "")).upper().strip()

    # Normalizações
    if placa in PLACAS_BITRUCK:
        return "BI-TRUCK"

    # Aqui está a correção principal:
    if tipo_bruto in ["CAVALO", "CAV", "CAVALINHO"]:
        return "CARRETA"

    if tipo_bruto in ["CARRETA"]:
        return "CARRETA"

    if tipo_bruto in ["TRUCK"]:
        return "TRUCK"

    if tipo_bruto in ["TOCO"]:
        return "TOCO"

    return "TRUCK"  # fallback seguro


# Gera a nova coluna TIPO_CORRIGIDO
df_original['TIPO_CORRIGIDO'] = df_original.apply(identificar_tipo, axis=1)

# Função de capacidade
def obter_capacidade(tipo):
    return CAPACIDADES_FIXAS.get(tipo.upper(), 0)

# Capacidade final usada nos cálculos
df_original['CAPACIDADE_KG'] = df_original['TIPO_CORRIGIDO'].apply(obter_capacidade)

# (Opcional) capacidade do cavalo (se quiser manter)
df_original['CAPAC_CAVALO'] = df_original['CAPACIDADE_KG']

# ▲▲▲ FIM DA NOVA LÓGICA FIXA DE CAPACIDADE ▲▲▲


# ▼▼▼ ADICIONE O NOVO CÓDIGO AQUI ▼▼▼

# --- NOVO FILTRO PARA REMOVER DADOS INDESEJADOS ---
# 1. Define os valores que queremos excluir
motoristas_para_excluir = ['RETIRA']
placas_para_excluir = ['TROCAUN']

# 2. Aplica os filtros para remover as linhas correspondentes
#    O símbolo '~' significa 'NÃO', então estamos mantendo as linhas que NÃO estão na lista.
df_original = df_original[~df_original['MOTORISTA'].isin(motoristas_para_excluir)]
df_original = df_original[~df_original['PLACA_CAVALO'].isin(placas_para_excluir)]
# --- FIM DO NOVO FILTRO ---

# --- GARANTE A EXISTÊNCIA DA COLUNA DIA_EMISSAO_STR ---
if 'EMIS_MANIF' in df_original.columns:
    df_original['DIA_EMISSAO_STR'] = df_original['EMIS_MANIF'].dt.strftime('%d/%m/%Y')
else:
    df_original['DIA_EMISSAO_STR'] = ''
# --- FIM DO AJUSTE ---

# ✅ Conversão automática para colunas numéricas (corrige formatos BR e EUA)
colunas_numericas = ['FRETE-R$', 'CTRB-R$', 'OS-R$', 'ICMS-R$', 'PESO REAL (KG)', 'PESO CALCULO (KG)', 'PESO CÁLCULO (KG)', 'PESO CALCULADO (KG)', 'M3', 'MERCADORIA-R$', 'VOLUMES']

for col in colunas_numericas:
    if col in df_original.columns:
        # Limpa a coluna, mantendo apenas dígitos, ponto, vírgula e sinal de menos
        df_original[col] = (
            df_original[col]
            .astype(str)
            .str.replace(r'[^\d.,-]', '', regex=True)
            .str.strip()
        )

        # --- NOVA FUNÇÃO DE CONVERSÃO (MAIS SEGURA) ---
        def converter_numero_robusto(valor_str):
            if pd.isna(valor_str) or valor_str == '':
                return 0.0
            
            # Conta a ocorrência de pontos e vírgulas
            num_pontos = valor_str.count('.')
            num_virgulas = valor_str.count(',')

            # Caso 1: Formato brasileiro (ex: "1.234,56" ou "1234,56")
            # A vírgula é o separador decimal.
            if num_virgulas == 1 and (num_pontos == 0 or valor_str.rfind('.') < valor_str.rfind(',')):
                return float(valor_str.replace('.', '').replace(',', '.'))
            
            # Caso 2: Formato americano (ex: "1,234.56" ou "1234.56")
            # O ponto é o separador decimal.
            elif num_pontos == 1 and (num_virgulas == 0 or valor_str.rfind(',') < valor_str.rfind('.')):
                 return float(valor_str.replace(',', ''))

            # Caso 3: Formato com múltiplos separadores de milhar (ex: "1.234.567,89" ou "1,234,567.89")
            # Remove todos os separadores de milhar e converte o decimal
            if num_virgulas > 0 and num_pontos > 0:
                if valor_str.rfind(',') > valor_str.rfind('.'): # Decimal é vírgula
                    return float(valor_str.replace('.', '').replace(',', '.'))
                else: # Decimal é ponto
                    return float(valor_str.replace(',', ''))
            
            # Caso 4: Número sem separador decimal claro (trata como inteiro ou float simples)
            try:
                # Tenta converter diretamente (pode funcionar para "123" ou "123.45")
                return float(valor_str)
            except ValueError:
                # Se falhar, tenta o formato com vírgula decimal
                try:
                    return float(valor_str.replace(',', '.'))
                except ValueError:
                    return 0.0 # Retorna 0 se todas as tentativas falharem

        # Aplica a nova função
        df_original[col] = df_original[col].apply(converter_numero_robusto)

# Cria a coluna padrão usada em todo o dashboard
df_original = garantir_coluna_peso_calculo(df_original)

# ========================================
# 🔹 SIDEBAR DE FILTROS
# ========================================

periodo_sidebar = st.sidebar.expander("📅 Período de Emissão", expanded=True)

periodo_sidebar.markdown("""
    <style>
    section[data-testid="stSidebar"] [data-testid="stExpander"] details summary p {
        font-family: "Poppins", "Segoe UI", sans-serif;
        font-weight: 700;
        letter-spacing: 0.2px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
        padding: 3px 0;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] p {
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 🔴 TROCA 1 — BASE DE DATA (AGORA USANDO DATA_OPERACIONAL)
df_sem_na_emissao = df_original.dropna(subset=['DATA_OPERACIONAL'])
min_data_emissao = df_sem_na_emissao['DATA_OPERACIONAL'].min().date()
max_data_emissao = df_sem_na_emissao['DATA_OPERACIONAL'].max().date()
total_registros = len(df_sem_na_emissao)

# 🛡️ flag global de controle
dados_periodo_validos = True

# Define o valor padrão somente na primeira carga da sessão
# A dashboard passa a iniciar sempre em "Dia Específico" com a data operacional mais recente.
if "periodo_tipo" not in st.session_state:
    st.session_state["periodo_tipo"] = "Dia Específico"

periodo_tipo = periodo_sidebar.radio(
    "Filtrar por data OPERACIONAL:", # <-- Texto atualizado para clareza
    ["Dia Específico", "Mês Completo", "Período Personalizado"],
    key="periodo_tipo"
)

data_padrao_inteligente = max_data_emissao

# Garante que, ao iniciar a sessão, a data selecionada seja sempre a mais recente disponível.
if "data_emissao_especifica" not in st.session_state:
    st.session_state["data_emissao_especifica"] = data_padrao_inteligente
elif st.session_state["data_emissao_especifica"] < min_data_emissao or st.session_state["data_emissao_especifica"] > max_data_emissao:
    st.session_state["data_emissao_especifica"] = data_padrao_inteligente

df_periodo_filtrado = df_original.copy()

# =========================================================
# 📅 DIA ESPECÍFICO
# =========================================================
if periodo_tipo == "Dia Específico":

    periodo_sidebar.markdown("""
        <style>
        .dia-semana-box {
            height: 40px;
            border-radius: 14px;
            background: rgba(255,255,255,.06);
            border: 1px solid rgba(255,255,255,.18);
            color: rgba(255,255,255,.88);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            letter-spacing: .3px;
        }
        </style>
    """, unsafe_allow_html=True)

        # Mantém a data selecionada em sessão (pra poder alterar via botões)
    if "data_emissao_especifica" not in st.session_state:
        st.session_state["data_emissao_especifica"] = data_padrao_inteligente

    # Nome do dia da semana (pt-BR) para mostrar ao lado do título
    _DIAS_SEMANA_FULL = [
        "Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira",
        "Sexta-Feira", "Sábado", "Domingo"
    ]
    dia_semana_nome = _DIAS_SEMANA_FULL[st.session_state["data_emissao_especifica"].weekday()]

    periodo_sidebar.markdown(
        f'📜 <span style="font-weight:700">Selecione o Dia:</span> '
        f'<span style="margin-left:6px; font-weight:700; opacity:.85;">{dia_semana_nome}</span>',
        unsafe_allow_html=True
    )

    c_prev, c_pick, c_next = periodo_sidebar.columns([0.85, 4.3, 0.85])

    with c_prev:
        prev_clicked = st.button("❮", use_container_width=True, key="btn_prev_dia", help="Dia anterior")

    with c_next:
        next_clicked = st.button("❯", use_container_width=True, key="btn_next_dia", help="Próximo dia")

    if prev_clicked:
        st.session_state["data_emissao_especifica"] = max(
            min_data_emissao,
            st.session_state["data_emissao_especifica"] - timedelta(days=1)
        )
        st.rerun()

    if next_clicked:
        st.session_state["data_emissao_especifica"] = min(
            max_data_emissao,
            st.session_state["data_emissao_especifica"] + timedelta(days=1)
        )
        st.rerun()

    with c_pick:
        data_emissao_especifica = st.date_input(
            "Dia",
            value=st.session_state["data_emissao_especifica"],
            min_value=min_data_emissao,
            max_value=max_data_emissao,
            format="DD/MM/YYYY",
            key="data_emissao_especifica",
            label_visibility="collapsed"
        )
# 🔴 TROCA 2 — FILTRO DIA ESPECÍFICO PELA DATA OPERACIONAL
    df_periodo_filtrado = df_original[
        df_original['DATA_OPERACIONAL'].dt.date == data_emissao_especifica
    ]

    # A função obter_info_periodo ainda usa EMIS_MANIF, vamos mantê-la por enquanto
    # para não quebrar outras partes, mas o filtro principal está correto.
    num_reg, num_veic, num_mot = obter_info_periodo(
        df_original, data_emissao_especifica
    )

    if len(df_periodo_filtrado) > 0:
        periodo_sidebar.info(f"📜 {len(df_periodo_filtrado)} Manifestos • 🚚 {df_periodo_filtrado['PLACA_CAVALO'].nunique()} Veículos")
    else:
        periodo_sidebar.warning(
            f"⚠️ Nenhum registro encontrado para "
            f"{data_emissao_especifica.strftime('%d/%m/%Y')}"
        )

    if df_periodo_filtrado.empty:
        st.warning("📭 Não há manifestos para a data operacional selecionada.")
        dados_periodo_validos = False


# =========================================================
# 🗓️ MÊS COMPLETO
# =========================================================
elif periodo_tipo == "Mês Completo":

    # 🔴 TROCA 3 — MÊS BASEADO NA DATA OPERACIONAL
    meses = df_sem_na_emissao['DATA_OPERACIONAL'].dt.to_period("M").unique().astype(str)
    meses_ordenados = sorted(meses, reverse=True)

    meses_formatados = {
        m: pd.Period(m).strftime("%B/%Y").capitalize()
        for m in meses_ordenados
    }

    lista_meses = list(meses_formatados.values())

    mes_formatado_sel = periodo_sidebar.selectbox(
        "🗓️ Selecione o Mês:",
        lista_meses,
        index=0,
        key="mes_completo_padrao"
    )

    mes_emissao_completo = [
        k for k, v in meses_formatados.items()
        if v == mes_formatado_sel
    ][0]

    # 🔴 TROCA 4 — FILTRO MÊS PELA DATA OPERACIONAL
    df_periodo_filtrado = df_original[
        df_original['DATA_OPERACIONAL']
        .dt.to_period("M")
        .astype(str) == mes_emissao_completo
    ]

    if df_periodo_filtrado.empty:
        st.warning("📭 Não há manifestos no mês selecionado.")
        dados_periodo_validos = False
    else:
        periodo_sidebar.success(
            f"✅ {len(df_periodo_filtrado)} registros para {mes_formatado_sel}"
        )


# =========================================================
# 📆 PERÍODO PERSONALIZADO
# =========================================================
elif periodo_tipo == "Período Personalizado":

    periodo_emissao_sel = periodo_sidebar.date_input(
        "🗓️ Selecione o intervalo:",
        [min_data_emissao, max_data_emissao],
        format="DD/MM/YYYY"
    )

    if len(periodo_emissao_sel) == 2:
        # 🔴 TROCA 5 — INTERVALO PELA DATA OPERACIONAL
        df_periodo_filtrado = df_original[
            (df_original['DATA_OPERACIONAL'].dt.date >= periodo_emissao_sel[0]) &
            (df_original['DATA_OPERACIONAL'].dt.date <= periodo_emissao_sel[1])
        ]

        num_reg = len(df_periodo_filtrado)
        num_veic = df_periodo_filtrado['PLACA_CAVALO'].nunique()
        num_mot = df_periodo_filtrado['MOTORISTA'].nunique()

        if num_reg > 0:
            dias_periodo = (periodo_emissao_sel[1] - periodo_emissao_sel[0]).days + 1
            periodo_sidebar.success(f"✅ {num_reg} registros encontrados")
            periodo_sidebar.info(
                f"📅 {dias_periodo} dias • 🚚 {num_veic} veículos • 👨‍✈️ {num_mot} motoristas"
            )
        else:
            periodo_sidebar.warning("⚠️ Nenhum registro encontrado no período selecionado")


# --- FILTROS DE VIAGEM (COM AMBOS OS SELETORES) ---
with st.sidebar.expander("👨‍✈️ Filtros de Viagem", expanded=True):

    # ▼▼▼ NOVO FILTRO DE TIPO DE VIAGEM ▼▼▼
  
    tipo_viagem_sel = st.radio(
        "⚙️ Tipo de Viagem",
        ["Todas", "Viagem Extra"], 
        horizontal=True,
        key="tipo_viagem_sel"
    )
    # ▲▲▲ FIM DO NOVO FILTRO ▲▲▲
    
    # --- NOVO FILTRO DE DESEMPENHO DE CTRB/FRETE (%) ---
    opcoes_desempenho = ["(Todos)", "Bom (Até 25%)", "Regular (Entre 26 a 45%)", "Péssimo (Acima de 45%)"]
    desempenho_ctrb_sel = st.selectbox(
        "📊 Desempenho CTRB/Frete",
        options=opcoes_desempenho,
        key="filtro_desempenho_sidebar"
    )
    # --- FIM DO NOVO FILTRO ---



    motorista_sel = st.selectbox("👤 Motorista", ["(Todos)"] + sorted(df_periodo_filtrado["MOTORISTA"].dropna().unique()))
    # --- FILTRO DE DESTINO MÚLTIPLO ---
    # Gera a lista de opções de destino, removendo valores nulos e ordenando
    lista_destinos = sorted(df_periodo_filtrado["CIDADE_UF_DEST"].dropna().unique())
    
    # Usa st.multiselect para permitir a seleção de múltiplas cidades
    destinos_sel = st.multiselect(
        "📍 Destinos Finais", 
        options=lista_destinos,
        placeholder="Selecione uma ou mais cidades" # Texto que aparece quando nada está selecionado
    )


    # Garante que a coluna de data formatada existe para ambos os filtros
    if 'EMIS_MANIF' in df_periodo_filtrado.columns:
        df_periodo_filtrado['DIA_EMISSAO_STR'] = df_periodo_filtrado['EMIS_MANIF'].dt.strftime('%d/%m/%Y')
    else:
        df_periodo_filtrado['DIA_EMISSAO_STR'] = ''


    # --- INÍCIO: LÓGICA DO FILTRO DE VIAGEM ESPECÍFICA (O ANTIGO) ---
    rotas_df_antigo = df_periodo_filtrado.dropna(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA', 'DEST_MANIF']).copy()

    if not rotas_df_antigo.empty:
        # Agrupa por viagem e cria a lista de destinos
        rotas_df_antigo = rotas_df_antigo.groupby(
            ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']
        ).agg(
            Destinos=('DEST_MANIF', lambda x: ' - '.join(sorted(x.unique())))
        ).reset_index()

        # Formata o nome do motorista
        def formatar_nome_motorista(nome_completo):
            partes = str(nome_completo).strip().split()
            if not partes: return ""
            preposicoes = ['DA', 'DE', 'DO', 'DOS']
            if len(partes) >= 3 and partes[1].upper() in preposicoes:
                return f"{partes[0]} {partes[1]} {partes[2]}"
            elif len(partes) >= 2:
                return f"{partes[0]} {partes[1]}"
            else:
                return partes[0]

        rotas_df_antigo['NOME_CURTO_MOTORISTA'] = rotas_df_antigo['MOTORISTA'].apply(formatar_nome_motorista)
        
        # Cria o rótulo para o selectbox
        rotas_df_antigo['NOME_ROTA_ANTIGO'] = (
            "📍 " + rotas_df_antigo['Destinos'] + 
            " 👨‍✈️ " + rotas_df_antigo['NOME_CURTO_MOTORISTA']
        )
        lista_rotas_antigas = ["(Todos)"] + sorted(rotas_df_antigo['NOME_ROTA_ANTIGO'].unique())
    else:
        lista_rotas_antigas = ["(Todos)"]
        rotas_df_antigo = pd.DataFrame()

    # Só habilita o filtro de viagem quando o período estiver em Dia Específico
    habilitar_filtro_viagem_dia = (periodo_tipo == "Dia Específico")

    # Cria o selectbox para a VIAGEM ESPECÍFICA
    viagem_especifica_sel = st.selectbox(
        "🗺️ Selecione uma Rota do Dia",
        lista_rotas_antigas,
        index=0,
        disabled=not habilitar_filtro_viagem_dia,
        help="Disponível apenas quando o filtro de data OPERACIONAL estiver em 'Dia Específico'."
    )

    # Se não estiver em Dia Específico, força '(Todos)'
    if habilitar_filtro_viagem_dia:
        st.session_state["viagem_especifica"] = viagem_especifica_sel
    else:
        viagem_especifica_sel = "(Todos)"
        st.session_state["viagem_especifica"] = "(Todos)"



    # --- INÍCIO: LÓGICA DO FILTRO DE GRUPO DE ROTAS (ATUALIZADO) ---

    # Dicionário que define as rotas completas e suas siglas.
    # A ORDEM É IMPORTANTE: As rotas mais abrangentes (com mais destinos) devem vir primeiro.
    ROTAS_COMPLETAS = {
        # Rotas compostas (mais destinos primeiro)
        "ROTA COXIM": {"COX", "PGO", "SNR"},
        "ROTA SÃO PAULO": {"CSL", "PBA", "ATB", "SPO"},
        "ROTA GOIÂNIA": {"PDA", "CDS", "GYN"},
        "ROTA BATAGUASSU": {"BAT", "BLD", "SRP"},
        "ROTA RIO BRILHANTE/DOURADOS": {"RBT", "DOU"},
        "ROTA SÃO GABRIEL": {"SGO", "RVM"},
        "ROTA MARACAJU": {"MJU", "SDL"},
        "ROTA JARDIM": {"JDM", "NQU"},
        "ROTA BODOQUENA": {"BDQ", "MDA"},
        "ROTA COSTA RICA": {"CRC", "CMP"},
        "ROTA IVINHEMA": {"IVM", "NSU"},
        "ROTA RIBAS": {"ACL", "RRP"},

        # Rotas com um único destino principal (ou que podem aparecer sozinhas)
        "ROTA DOURADOS": {"DOU"},
        "ROTA RIO BRILHANTE": {"RBT"},
        "ROTA NOVA ANDRADINA": {"NAD"},
        "ROTA BONITO": {"BTO"},
        "ROTA AQUIDAUANA": {"AQU"},
        "ROTA PONTA PORÃ": {"PPR"},
        "ROTA TRÊS LAGOAS": {"TLG"},
        "ROTA CORUMBÁ": {"COR"},
    }

    # Dicionário reverso para mapear uma sigla individual ao nome completo da sua rota principal.
    # Isso garante que "BAT" sozinho seja mapeado para "ROTA BATAGUASSU".
    MAPA_SIGLA_PARA_ROTA = {
        sigla: nome_rota
        for nome_rota, siglas in ROTAS_COMPLETAS.items()
        for sigla in siglas
    }


    if not df_periodo_filtrado.empty and all(col in df_periodo_filtrado.columns for col in ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA', 'DEST_MANIF']):
        # Agrupa as viagens para obter uma lista única de destinos para cada uma
        viagens_agrupadas = df_periodo_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA'])['DEST_MANIF'].unique().reset_index()

        def obter_nome_rota_padronizado(lista_destinos_da_viagem):
            """
            Identifica a rota correta para um conjunto de destinos, dando prioridade
            às rotas compostas e tratando corretamente as rotas individuais.
            """
            destinos_set = {str(d).upper() for d in lista_destinos_da_viagem}

            # 1. VERIFICA AS ROTAS COMPLETAS (DA MAIS ABRANGENTE PARA A MENOS)
            for nome_rota, destinos_rota in ROTAS_COMPLETAS.items():
                if destinos_rota.issubset(destinos_set):
                    return nome_rota

            # 2. SE NENHUMA ROTA COMPLETA CORRESPONDER, USA O MAPEAMENTO INDIVIDUAL
            nomes_de_rota_encontrados = set()
            for sigla in destinos_set:
                # Busca o nome da rota para a sigla no mapa reverso.
                # Se não encontrar, cria um nome genérico "ROTA [SIGLA]".
                nome_encontrado = MAPA_SIGLA_PARA_ROTA.get(sigla, f"ROTA {sigla}")
                nomes_de_rota_encontrados.add(nome_encontrado)
            
            if nomes_de_rota_encontrados:
                # Junta os nomes únicos, ordenados alfabeticamente.
                return ' / '.join(sorted(list(nomes_de_rota_encontrados)))

            return "ROTA INDEFINIDA"

        # Aplica a função para criar a coluna com o nome padronizado da rota
        viagens_agrupadas['NOME_ROTA_PADRAO'] = viagens_agrupadas['DEST_MANIF'].apply(obter_nome_rota_padronizado)
        
        # Gera a lista de opções para o selectbox
        lista_rotas_padronizadas = ["(Todos)"] + sorted(viagens_agrupadas['NOME_ROTA_PADRAO'].unique())
    else:
        lista_rotas_padronizadas = ["(Todos)"]
        viagens_agrupadas = pd.DataFrame()

    # Cria o selectbox para o GRUPO DE ROTAS
    grupo_rota_sel = st.selectbox("🗺️ Filtro de Rotas (Grupo)", lista_rotas_padronizadas)
    # --- FIM: LÓGICA DO FILTRO DE GRUPO DE ROTAS ---


# --- FILTROS DE VEÍCULOS ---
with st.sidebar.expander("🚛 Filtros de Veículos", expanded=True):
    placa_sel = st.selectbox("🚚 Placa do Cavalo", ["(Todos)"] + sorted(df_periodo_filtrado["PLACA_CAVALO"].dropna().unique()))
    tipo_sel = st.selectbox("⚙️ Tipo do Veículo", ["(Todos)"] + sorted(df_periodo_filtrado["TIPO_CAVALO"].dropna().unique()))
    proprietario_sel = st.selectbox("🏢 Proprietário", ["(Todos)"] + sorted(df_periodo_filtrado["PROPRIETARIO_CAVALO"].dropna().unique()))

# --- BUSCA RÁPIDA ---
with st.sidebar.expander("🔎 Busca Rápida", expanded=False):
    busca_placa = st.text_input("Buscar por Placa", placeholder="Digite a placa...")
    busca_lacre = st.text_input("Buscar por Lacres", placeholder="Digite o lacre...")

# ========================================
# 🔹 APLICAÇÃO FINAL DOS FILTROS (LÓGICA CORRIGIDA E FINAL)
# ========================================

# Começa com os dados já filtrados pelo período (Dia, Mês, etc.)
df_filtrado = df_periodo_filtrado.copy()

# --- ETAPA FUNDAMENTAL: GARANTIR A EXISTÊNCIA DO VIAGEM_ID ---
# Cria a coluna VIAGEM_ID no DataFrame principal ANTES de qualquer outro filtro de viagem.
# Isso garante que a coluna estará sempre disponível para as lógicas subsequentes.
if not df_filtrado.empty:
    if 'VIAGEM_ID' not in df_filtrado.columns:
        df_filtrado['VIAGEM_ID'] = df_filtrado.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()
else:
    # Se o dataframe estiver vazio, garante que a coluna exista para evitar erros posteriores
    df_filtrado['VIAGEM_ID'] = pd.Series(dtype='int')
# --- FIM DA ETAPA FUNDAMENTAL ---


# --- PASSO 1: APLICA O FILTRO DE TIPO DE VIAGEM (EXTRA vs COMPLETA) PRIMEIRO ---
# Este filtro é o mais complexo e precisa ser aplicado antes dos outros.
if tipo_viagem_sel != "Todas":
    if not df_filtrado.empty:
        # A função de classificação precisa do contexto do dia inteiro para funcionar.
        # Portanto, ela é aplicada ANTES de outros filtros de viagem.
        df_classificado = classificar_viagens_do_dia(df_filtrado)
        
        # Agora, filtramos o resultado com base na seleção do usuário
        df_filtrado = df_classificado[df_classificado['TIPO_VIAGEM_CALCULADO'] == tipo_viagem_sel].copy()

# --- PASSO 2: APLICA OS OUTROS FILTROS EM CASCATA ---
# A variável 'rota_sel_visivel' é usada para controlar a exibição de detalhes posteriormente.
rota_sel_visivel = "(Todos)"

# Prioridade máxima: Busca Rápida
if busca_placa:
    df_filtrado = df_original[df_original['PLACA_CAVALO'].str.contains(busca_placa.strip(), case=False, na=False)]
elif busca_lacre:
    df_filtrado = df_original[df_original['LACRES'].str.contains(busca_lacre.strip(), case=False, na=False)]

# Filtros de Viagem (só são aplicados se a busca rápida não foi usada)
else:
    if viagem_especifica_sel != "(Todos)":
        viagem_selecionada = rotas_df_antigo[rotas_df_antigo['NOME_ROTA_ANTIGO'] == viagem_especifica_sel]
        if not viagem_selecionada.empty:
            placa_rota = viagem_selecionada['PLACA_CAVALO'].iloc[0]
            data_emissao_rota = viagem_selecionada['DIA_EMISSAO_STR'].iloc[0]
            motorista_rota = viagem_selecionada['MOTORISTA'].iloc[0]
            df_filtrado = df_filtrado[
                (df_filtrado['PLACA_CAVALO'] == placa_rota) &
                (df_filtrado['DIA_EMISSAO_STR'] == data_emissao_rota) &
                (df_filtrado['MOTORISTA'] == motorista_rota)
            ]
        rota_sel_visivel = viagem_especifica_sel

    elif grupo_rota_sel != "(Todos)":
        if not viagens_agrupadas.empty:
            viagens_do_grupo = viagens_agrupadas[viagens_agrupadas['NOME_ROTA_PADRAO'] == grupo_rota_sel]
            chaves_viagens = list(zip(viagens_do_grupo['PLACA_CAVALO'], viagens_do_grupo['DIA_EMISSAO_STR'], viagens_do_grupo['MOTORISTA']))
            if chaves_viagens:
                df_filtrado = df_filtrado[pd.MultiIndex.from_frame(df_filtrado[['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']]).isin(chaves_viagens)]
            else:
                df_filtrado = pd.DataFrame(columns=df_filtrado.columns)
        rota_sel_visivel = "(Todos)"

    else:  # Filtros individuais
        if motorista_sel != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["MOTORISTA"] == motorista_sel]

        # --- NOVO: APLICA O FILTRO DE DESEMPENHO DE CTRB/FRETE ---
        if desempenho_ctrb_sel != "(Todos)":
            # 1. Precisamos calcular o CTRB/Frete (%) para cada viagem antes de filtrar.
            # Agrupa por viagem para obter os valores corretos.
            df_temp_desempenho = df_filtrado.copy()
            if 'VIAGEM_ID' not in df_temp_desempenho.columns:
                df_temp_desempenho['VIAGEM_ID'] = df_temp_desempenho.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

            resumo_viagens_desempenho = df_temp_desempenho.groupby('VIAGEM_ID').agg(
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'),
                FRETE_TOTAL=('FRETE-R$', 'sum'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique()))
            ).reset_index()

            # 2. Calcula o custo e o percentual
            def calcular_custo_viagem_temp(row):
                custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base
            
            resumo_viagens_desempenho['CUSTO_FINAL'] = resumo_viagens_desempenho.apply(calcular_custo_viagem_temp, axis=1)
            resumo_viagens_desempenho['CTRB_FRETE_PERC'] = (resumo_viagens_desempenho['CUSTO_FINAL'] / resumo_viagens_desempenho['FRETE_TOTAL'] * 100).fillna(0)

            # --- INÍCIO DA CORREÇÃO ---

            # 3. Inicializa a variável para garantir que ela sempre exista, evitando o NameError.
            viagens_filtradas_ids = []

            # 4. Filtra as viagens com base na faixa de desempenho selecionada (COM OS TEXTOS ATUALIZADOS)
            if desempenho_ctrb_sel == "Bom (Até 25%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[resumo_viagens_desempenho['CTRB_FRETE_PERC'] <= 25]['VIAGEM_ID']
            elif desempenho_ctrb_sel == "Regular (Entre 26 a 45%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[(resumo_viagens_desempenho['CTRB_FRETE_PERC'] > 25) & (resumo_viagens_desempenho['CTRB_FRETE_PERC'] <= 45)]['VIAGEM_ID']
            elif desempenho_ctrb_sel == "Péssimo (Acima de 45%)":
                viagens_filtradas_ids = resumo_viagens_desempenho[resumo_viagens_desempenho['CTRB_FRETE_PERC'] > 45]['VIAGEM_ID']
            
            # 5. Aplica o filtro final no DataFrame principal.
            #    Se 'viagens_filtradas_ids' estiver vazia, o dataframe resultante também ficará vazio.
            df_filtrado = df_filtrado[df_filtrado['VIAGEM_ID'].isin(viagens_filtradas_ids)]
            
            # --- FIM DA CORREÇÃO ---
        # --- FIM DO FILTRO DE DESEMPENHO ---


        
        # --- INÍCIO DA NOVA LÓGICA DE FILTRO DE DESTINO ---
        if destinos_sel:
            # Aqui o filtro deve mostrar somente os registros das cidades selecionadas,
            # e não exigir que a viagem inteira tenha exatamente o mesmo conjunto de destinos.
            df_filtrado = df_filtrado[
                df_filtrado['CIDADE_UF_DEST'].astype(str).isin(destinos_sel)
            ].copy()

        # A variável abaixo não muda, continua como está
        rota_sel_visivel = "(Todos)"
        # --- FIM DA NOVA LÓGICA DE FILTRO DE DESTINO ---

# Filtros finais de veículo (aplicados sobre qualquer resultado anterior)
if placa_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["PLACA_CAVALO"] == placa_sel]
if tipo_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["TIPO_CAVALO"] == tipo_sel]
if proprietario_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["PROPRIETARIO_CAVALO"] == proprietario_sel]

# ========================================
# 🔹 CORPO PRINCIPAL DO DASHBOARD
# ========================================

# --- INÍCIO DA CORREÇÃO ---

# 1. Mover o cálculo de custo e distância para o escopo global, após os filtros.
#    Isso garante que as variáveis estarão disponíveis para todas as abas.

# Dicionário de custo por KM, baseado no tipo do veículo.
custo_km_por_tipo = {
    'TOCO': 3.50,
    'TRUCK': 4.50,
    'CAVALO': 6.75,
    'CARRETA': 6.75
}

# Inicializa as variáveis para evitar erros caso o DataFrame esteja vazio.
valor_por_km = 0
custo_ctrb_os = 0
distancia_estimada_km = 0

# Garante que há dados filtrados para evitar erros de índice.
if not df_filtrado.empty:
    # Determina o tipo de veículo (usando o mais frequente se houver vários).
    tipo_veiculo = df_filtrado['TIPO_CAVALO'].mode()[0] if 'TIPO_CAVALO' in df_filtrado.columns and not df_filtrado['TIPO_CAVALO'].dropna().empty else "PADRAO"
    
    # Busca o valor do custo por KM no dicionário.
    valor_por_km = custo_km_por_tipo.get(str(tipo_veiculo).upper(), 0)

    # --- Lógica de Custo Centralizada (reutilizada da sua tab1) ---
    # Esta lógica calcula o custo total de CTRB/OS corretamente, considerando as regras de negócio.
    df_custo = df_filtrado.copy()
    if 'VIAGEM_ID' not in df_custo.columns:
        df_custo['VIAGEM_ID'] = df_custo.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

    resumo_viagens_custo = df_custo.groupby('VIAGEM_ID').agg(
        PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
        CUSTO_OS=('OS-R$', 'max'),
        CUSTO_CTRB=('CTRB-R$', 'max'),
        DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique()))
    ).reset_index()

    def calcular_custo_viagem_com_regra(row):
        custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
        destinos_str = str(row.get('DESTINOS', '')).upper()
        if 'GYN' in destinos_str or 'SPO' in destinos_str:
            return custo_base / 2
        return custo_base

    if not resumo_viagens_custo.empty:
        resumo_viagens_custo['CUSTO_FINAL_VIAGEM'] = resumo_viagens_custo.apply(calcular_custo_viagem_com_regra, axis=1)
        custo_ctrb_os = resumo_viagens_custo['CUSTO_FINAL_VIAGEM'].sum()

    # Agora, calcula a distância estimada com as variáveis já definidas.
    if valor_por_km > 0 and custo_ctrb_os > 0:
        distancia_estimada_km = custo_ctrb_os / valor_por_km

# --- INÍCIO DA CORREÇÃO ---
# Adiciona a coluna SOMENTE se o DataFrame não estiver vazio para evitar o ValueError
if not df_filtrado.empty:
    df_filtrado.loc[:, 'DISTANCIA_ESTIMADA_KM'] = distancia_estimada_km
else:
    # Se o DataFrame estiver vazio, mas a coluna for esperada em outras partes do código,
    # é uma boa prática garantir que ela exista, mesmo que vazia.
    df_filtrado['DISTANCIA_ESTIMADA_KM'] = pd.Series(dtype='float64')
# --- FIM DA CORREÇÃO ---

# Resumo financeiro centralizado para reutilização nas abas e na comparação diária
resumo_financeiro_atual = calcular_resumo_financeiro(df_filtrado)
receita_total = resumo_financeiro_atual["receita_total"]
custo_ctrb_os = resumo_financeiro_atual["custo_ctrb_os"]
custo_icms = resumo_financeiro_atual["custo_icms"]
custo_total = resumo_financeiro_atual["custo_total"]
lucro_estimado = resumo_financeiro_atual["lucro_estimado"]
margem_lucro = resumo_financeiro_atual["margem_lucro"]

variacoes_financeiras = {
    "receita_total": None,
    "custo_ctrb_os": None,
    "custo_icms": None,
    "custo_total": None,
    "lucro_estimado": None,
    "margem_lucro": None,
}
variacao_label_financeira = "vs dia ant."

if periodo_tipo == "Dia Específico":
    data_ref_comp = st.session_state.get("data_emissao_especifica", data_padrao_inteligente)
    data_anterior_comp = data_ref_comp - timedelta(days=1)

    if data_anterior_comp >= min_data_emissao:
        df_dia_anterior = df_original[df_original['DATA_OPERACIONAL'].dt.date == data_anterior_comp].copy()
        df_dia_anterior_filtrado = aplicar_filtros_para_comparacao_dia(df_dia_anterior)
        resumo_financeiro_dia_anterior = calcular_resumo_financeiro(df_dia_anterior_filtrado)

        variacoes_financeiras = {
            "receita_total": calcular_variacao_percentual(receita_total, resumo_financeiro_dia_anterior["receita_total"]),
            "custo_ctrb_os": calcular_variacao_percentual(custo_ctrb_os, resumo_financeiro_dia_anterior["custo_ctrb_os"]),
            "custo_icms": calcular_variacao_percentual(custo_icms, resumo_financeiro_dia_anterior["custo_icms"]),
            "custo_total": calcular_variacao_percentual(custo_total, resumo_financeiro_dia_anterior["custo_total"]),
            "lucro_estimado": calcular_variacao_percentual(lucro_estimado, resumo_financeiro_dia_anterior["lucro_estimado"]),
            "margem_lucro": calcular_variacao_percentual(margem_lucro, resumo_financeiro_dia_anterior["margem_lucro"]),
        }
elif periodo_tipo == "Mês Completo":
    variacao_label_financeira = "vs mês ant."
    try:
        mes_ref_comp = pd.Period(mes_emissao_completo, freq="M")
        mes_anterior_comp = mes_ref_comp - 1
        df_mes_anterior = df_original[
            df_original['DATA_OPERACIONAL'].dt.to_period("M") == mes_anterior_comp
        ].copy()

        if not df_mes_anterior.empty:
            df_mes_anterior_filtrado = aplicar_filtros_para_comparacao_dia(df_mes_anterior)
            resumo_financeiro_mes_anterior = calcular_resumo_financeiro(df_mes_anterior_filtrado)

            variacoes_financeiras = {
                "receita_total": calcular_variacao_percentual(receita_total, resumo_financeiro_mes_anterior["receita_total"]),
                "custo_ctrb_os": calcular_variacao_percentual(custo_ctrb_os, resumo_financeiro_mes_anterior["custo_ctrb_os"]),
                "custo_icms": calcular_variacao_percentual(custo_icms, resumo_financeiro_mes_anterior["custo_icms"]),
                "custo_total": calcular_variacao_percentual(custo_total, resumo_financeiro_mes_anterior["custo_total"]),
                "lucro_estimado": calcular_variacao_percentual(lucro_estimado, resumo_financeiro_mes_anterior["lucro_estimado"]),
                "margem_lucro": calcular_variacao_percentual(margem_lucro, resumo_financeiro_mes_anterior["margem_lucro"]),
            }
    except Exception:
        pass

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Visão Geral", 
    "Análise Financeira", 
    "Performance da Frota", 
    "Desempenho de Motoristas", 
    "Gestão de Rotas",
    "Análise Temporal" 
])


# --- ABA 1: VISÃO GERAL (PROFISSIONALIZADA) ---
with tab1:
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # ==============================
        # 1. CÁLCULOS PRINCIPAIS (COM LÓGICA DE CUSTO DINÂMICO E DISTÂNCIA)
        # ==============================
        receita_total = df_filtrado.get('FRETE-R$', pd.Series(0)).sum()

        # --- ### INÍCIO DA NOVA LÓGICA DE CUSTO CENTRALIZADA ### ---
        custo_ctrb_os = 0
        if not df_filtrado.empty:
            # 1. Cria uma cópia para trabalhar
            df_custo = df_filtrado.copy()

            # 2. Identifica cada viagem única para o agrupamento
            if 'VIAGEM_ID' not in df_custo.columns:
                df_custo['VIAGEM_ID'] = df_custo.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

            # 3. Agrupa por viagem para obter os valores corretos
            resumo_viagens_custo = df_custo.groupby('VIAGEM_ID').agg(
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique()))
            ).reset_index()

            # 4. Função para calcular o custo final por viagem (com a regra de divisão)
            def calcular_custo_viagem_com_regra(row):
                custo_base = 0
                if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    custo_base = row['CUSTO_OS']
                else:
                    custo_base = row['CUSTO_CTRB']

                # Aplica a regra de divisão
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                
                return custo_base

            # 5. Aplica a função para cada viagem e soma os resultados
            if not resumo_viagens_custo.empty:
                resumo_viagens_custo['CUSTO_FINAL_VIAGEM'] = resumo_viagens_custo.apply(calcular_custo_viagem_com_regra, axis=1)
                
                # 6. O custo total agora é a soma dos custos já processados
                custo_ctrb_os = resumo_viagens_custo['CUSTO_FINAL_VIAGEM'].sum()
        # --- ### FIM DA NOVA LÓGICA DE CUSTO CENTRALIZADA ### ---
                    
        # Cálculos financeiros usando a nova variável 'custo_ctrb_os'
        custo_icms = df_filtrado.get('ICMS-R$', pd.Series(0)).sum()
        custo_total = custo_ctrb_os + custo_icms # <<< USA O CUSTO JÁ CORRIGIDO
        lucro_estimado = receita_total - custo_total
        margem_lucro = (lucro_estimado / receita_total * 100) if receita_total > 0 else 0

        valor_mercadoria_total = df_filtrado.get('MERCADORIA-R$', pd.Series(0)).sum()

        # Cálculos operacionais
        peso_total = somar_peso_calculo(df_filtrado)

        # Corrige M3 nulo ou texto inválido antes do somatório
        if 'M3' in df_filtrado.columns:
            df_filtrado['M3'] = pd.to_numeric(df_filtrado['M3'], errors='coerce').fillna(0)


        # Volume bruto da base
        volume_total = df_filtrado.get('M3', pd.Series(0)).sum()

        # --- Correção: normalização da unidade do volume ---
        if volume_total > 1000:  
            volume_total_m3 = volume_total / 10000
        else:
            volume_total_m3 = volume_total  # já está em m³

        # --- Capacidades e ociosidade (LÓGICA UNIFICADA E CORRIGIDA) ---

        # 1. Define a capacidade de PESO dinamicamente a partir da coluna do arquivo externo.
        #    Usa a média se houver múltiplos veículos ou um padrão de 25000 kg se a coluna não existir.
        capacidade_peso_kg = df_filtrado['CAPACIDADE_KG'].mean() if 'CAPACIDADE_KG' in df_filtrado.columns and not df_filtrado.empty else 25000
        
        # 2. Define a capacidade de VOLUME a partir de um dicionário (pois não vem do arquivo).
        capacidades_volume_por_tipo = {
            'TOCO': 55, 'TRUCK': 75, 'CAVALO': 110, 'PADRAO': 80
        }
        tipo_veiculo_selecionado = df_filtrado['TIPO_CAVALO'].iloc[0] if not df_filtrado.empty and 'TIPO_CAVALO' in df_filtrado.columns else "PADRAO"
        capacidade_volume_m3 = capacidades_volume_por_tipo.get(str(tipo_veiculo_selecionado).upper(), 80)

        # 3. Calcula a ociosidade com base nas capacidades definidas acima.
        ociosidade_peso = (1 - (peso_total / capacidade_peso_kg)) * 100 if capacidade_peso_kg > 0 else 0
        ociosidade_volume = (1 - (volume_total_m3 / capacidade_volume_m3)) * 100 if capacidade_volume_m3 > 0 else 0
        
        # --- FIM DO BLOCO CORRIGIDO ---

        # Infos de identificação (necessárias para os cálculos seguintes)
        nome_completo_motorista = df_filtrado['MOTORISTA'].iloc[0]

        # Infos de identificação (necessárias para os cálculos seguintes)
        nome_completo_motorista = df_filtrado['MOTORISTA'].iloc[0]

        # --- LÓGICA PARA PEGAR O PRIMEIRO E ÚLTIMO NOME ---
        partes_nome = nome_completo_motorista.split()
        if len(partes_nome) > 1:
            # Junta o primeiro nome (partes_nome[0]) com o último (partes_nome[-1])
            motorista_principal = f"{partes_nome[0]} {partes_nome[-1]}"
        else:
            # Caso o nome tenha apenas uma palavra, usa o nome completo
            motorista_principal = nome_completo_motorista
        # --- FIM DA LÓGICA ---

        placa_cavalo = df_filtrado['PLACA_CAVALO'].iloc[0]
        placa_carreta = df_filtrado['PLACA_CARRETA'].iloc[0] if 'PLACA_CARRETA' in df_filtrado.columns else "N/A"
        tipo_veiculo = df_filtrado['TIPO_CAVALO'].iloc[0] if 'TIPO_CAVALO' in df_filtrado.columns else "N/A"
        proprietario_veiculo = df_filtrado['PROPRIETARIO_CAVALO'].iloc[0] if 'PROPRIETARIO_CAVALO' in df_filtrado.columns else "N/A"

        
        # --- CÁLCULO DE DISTÂNCIA ESTIMADA (POSICIONADO CORRETAMENTE) ---
        custo_km_por_tipo = {
            'TOCO': 3.50,
            'TRUCK': 4.50,
            'CAVALO': 6.75,
            'CARRETA': 6.75
        }
        # Usa str(tipo_veiculo) para mais segurança caso o valor seja nulo
        valor_por_km = custo_km_por_tipo.get(str(tipo_veiculo).upper(), 0)
        
        # Usa a variável de custo dinâmico 'custo_ctrb_os' para o cálculo
        if valor_por_km > 0 and custo_ctrb_os > 0:
            distancia_estimada_km = custo_ctrb_os / valor_por_km
        else:
            distancia_estimada_km = 0

        # --- IDENTIFICAÇÃO DO DESTINO E OUTROS DETALHES ---
        ordem_geografica_cidades = {
            'PARAISO DAS AGUAS/MS': 1,
            'CHAPADAO DO SUL/MS': 2,
            'GOIANIA/GO': 3,
        }

        destinos_da_viagem = df_filtrado['CIDADE_UF_DEST'].dropna().unique()
        if len(destinos_da_viagem) > 0:
            destino_principal = sorted(destinos_da_viagem, key=lambda d: ordem_geografica_cidades.get(d, 99))[-1]
        else:
            destino_principal = "N/A"

        data_emissao = df_filtrado['EMIS_MANIF'].min()
        num_manifestos = df_filtrado['NUM_MANIF'].nunique()
        num_lacres = df_filtrado['LACRES'].nunique()

        # ==============================
        # 2. CABEÇALHO EXECUTIVO COM ÍCONES (7 KPIs)
        # ==============================
        # Mantido desativado para preservar o layout original dos cards,
        # como na visão anterior aprovada pelo usuário.

        st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-coins"></i> Análise Financeira</h3>', unsafe_allow_html=True)

        kpi_f1, kpi_f2, kpi_f3, kpi_f4, kpi_f5 = st.columns(5)

        # Configura o locale para português do Brasil sem quebrar no servidor
        def configurar_locale_br():
            locais_tentativa = [
                "pt_BR.UTF-8",          # Linux mais comum
                "pt_BR.utf8",           # variação Linux
                "Portuguese_Brazil.1252",  # Windows
                ""                      # locale padrão do sistema
            ]
        
            for loc in locais_tentativa:
                try:
                    locale.setlocale(locale.LC_ALL, loc)
                    return loc
                except locale.Error:
                    continue
        
            return None
        
        LOCALE_ATIVO = configurar_locale_br()

        # ===============================================
        # Função para calcular distância real com OSRM
        # ===============================================
        import requests

        def calcular_distancia_osrm(lat_origem, lon_origem, lat_dest, lon_dest):
            """
            Calcula a distância real (dirigindo) entre origem e destino usando OSRM.
            Retorna em KM arredondado.
            """
            try:
                url = f"http://router.project-osrm.org/route/v1/driving/{lon_origem},{lat_origem};{lon_dest},{lat_dest}?overview=false"
                resposta = requests.get(url ).json()
                distancia_metros = resposta["routes"][0]["distance"]
                return round(distancia_metros / 1000, 1)  # distância em KM
            except Exception:
                return None

        # --- Lógica para determinar o título e o ícone do KPI de Custo ---
        titulo_kpi_custo = "📄 Custo CTRB / OS" # Título padrão
        if not df_filtrado.empty:
            # Pega o primeiro proprietário dos dados filtrados para decidir o título
            proprietario_principal = df_filtrado['PROPRIETARIO_CAVALO'].iloc[0]
            
            # Se houver mais de um proprietário nos dados (visão geral), mantém o título genérico
            if df_filtrado['PROPRIETARIO_CAVALO'].nunique() > 1:
                titulo_kpi_custo = "📄 Custo CTRB / OS"
            elif proprietario_principal == 'KM TRANSPORTES ROD. DE CARGAS LTDA':
                titulo_kpi_custo = "📄 Custo CTRB"
            elif proprietario_principal == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                titulo_kpi_custo = "📋 Custo OS" # Ícone diferente para OS

        # Configuração dos KPIs financeiros no novo estilo premium
        kpis_financeiros = [
            {
                "coluna": kpi_f1,
                "titulo": "Receita Total",
                "valor": formatar_moeda(receita_total),
                "classe": "receita",
                "icone": "fa-sack-dollar",
                "rodape": "Entrada total",
                "variacao": variacoes_financeiras.get("receita_total"),
                "modo_variacao": "higher_better"
            },
            {
                "coluna": kpi_f2,
                "titulo": titulo_kpi_custo.replace("📄 ", "").replace("📋 ", ""),
                "valor": formatar_moeda(custo_ctrb_os),
                "classe": "custo",
                "icone": "fa-file-invoice-dollar",
                "rodape": "Custo base",
                "variacao": variacoes_financeiras.get("custo_ctrb_os"),
                "modo_variacao": "lower_better"
            },
            {
                "coluna": kpi_f3,
                "titulo": "ICMS",
                "valor": formatar_moeda(custo_icms),
                "classe": "custo",
                "icone": "fa-receipt",
                "rodape": "Tributação",
                "variacao": variacoes_financeiras.get("custo_icms"),
                "modo_variacao": "lower_better"
            },
            {
                "coluna": kpi_f4,
                "titulo": """Custo Total
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Soma de CTRB + ICMS.<br>
                            Representa o custo total da viagem.
                        </span>
                    </span>""",
                "valor": formatar_moeda(custo_total),
                "classe": "custo",
                "icone": "fa-wallet",
                "rodape": "CTRB + ICMS",
                "variacao": variacoes_financeiras.get("custo_total"),
                "modo_variacao": "lower_better"
            },
            {
                "coluna": kpi_f5,
                "titulo": """Lucro Líquido
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Receita − (CTRB + ICMS).<br>
                            Lucro final após custos.
                        </span>
                    </span>""",
                "valor": formatar_moeda(lucro_estimado),
                "classe": "lucro",
                "icone": "fa-chart-line",
                "rodape": "Resultado final",
                "variacao": variacoes_financeiras.get("lucro_estimado"),
                "modo_variacao": "higher_better"
            },
        ]

        # Renderiza os KPIs financeiros no novo layout
        for info in kpis_financeiros:
            with info['coluna']:
                render_financial_kpi_card(
                    titulo=info['titulo'],
                    valor=info['valor'],
                    classe=info['classe'],
                    icone=info['icone'],
                    rodape=info['rodape'],
                    variacao_percentual=info.get('variacao'),
                    modo_variacao=info.get('modo_variacao', 'higher_better'),
                    variacao_label=info.get('variacao_label', variacao_label_financeira)
                )

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # ==============================
        # 4. INDICADORES DE PERFORMANCE
        # ==============================
        st.markdown("""
        <style>
        .trend-performance-title {
            font-family: "Poppins", "Segoe UI", sans-serif;
            font-size: 1.28rem;
            font-weight: 700;
            color: #f8fafc;
            margin: 0;
            letter-spacing: -0.2px;
        }
        .trend-performance-subtitle {
            font-size: 0.82rem;
            color: #94a3b8;
            margin-top: 4px;
            margin-bottom: 8px;
        }
        html[data-theme="light"] .trend-performance-title {
            color: #0f172a;
        }
        html[data-theme="light"] .trend-performance-subtitle {
            color: #64748b;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<h3 class="section-title-modern"><i class="fa-solid fa-chart-simple"></i> Indicadores de Performance</h3>', unsafe_allow_html=True)

        # CORREÇÃO: Usando a variável 'custo_ctrb_os' que foi definida na seção de cálculos
        custo_transferencia = (custo_ctrb_os / receita_total * 100) if receita_total > 0 else 0
        custo_faturamento = (custo_total / receita_total * 100) if receita_total > 0 else 0

        kpis_performance = [
            {
                "titulo": """Custo de Transferência
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Indica quanto do valor do frete foi gasto em custos de transporte entre filiais.
                        </span>
                    </span>""",
                "valor": formatar_percentual(custo_transferencia),
                "icone": "fa-arrow-right-arrow-left",
                "rodape": "Eficiência logística",
                "classe": "overview-teal"
            },
            {
                "titulo": """Custo Total
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Soma de CTRB + ICMS. Valor consolidado do custo total da operação no período.
                        </span>
                    </span>""",
                "valor": formatar_moeda(custo_total),
                "icone": "fa-wallet",
                "rodape": "Visão consolidada",
                "classe": "overview-teal"
            },
            {
                "titulo": """Lucro Líquido (%)
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Percentual que mostra quanto da receita permaneceu como lucro após todos os custos.
                        </span>
                    </span>""",
                "valor": formatar_percentual(margem_lucro),
                "icone": "fa-chart-line",
                "rodape": "Margem operacional",
                "classe": "overview-teal"
            },
            {
                "titulo": """Custo Total (%)
                    <span class="help-icon">ℹ️
                        <span class="tooltip-text">
                            Percentual da receita comprometido pelo custo total da operação no período.
                        </span>
                    </span>""",
                "valor": formatar_percentual(custo_faturamento),
                "icone": "fa-percent",
                "rodape": "Peso no faturamento",
                "classe": "overview-teal"
            }
        ]

        col_cards_perf, col_chart_perf = st.columns([1.00, 1.42], gap="large")

        with col_cards_perf:
            linha_superior = st.columns(2, gap="medium")
            for info, coluna_card in zip(kpis_performance[:2], linha_superior):
                with coluna_card:
                    render_overview_kpi_card(
                        titulo=info['titulo'],
                        valor=info['valor'],
                        icone=info['icone'],
                        rodape=info['rodape'],
                        classe=info['classe']
                    )

            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

            linha_inferior = st.columns(2, gap="medium")
            for info, coluna_card in zip(kpis_performance[2:], linha_inferior):
                with coluna_card:
                    render_overview_kpi_card(
                        titulo=info['titulo'],
                        valor=info['valor'],
                        icone=info['icone'],
                        rodape=info['rodape'],
                        classe=info['classe']
                    )

            total_viagens_perf = df_filtrado.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroups if not df_filtrado.empty else 0

            if not df_filtrado.empty:
                entregas_por_viagem_perf = df_filtrado.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR'])['DEST_MANIF'].nunique()
                total_entregas_perf = entregas_por_viagem_perf.sum()

                df_perf_resumo = df_filtrado.copy()
                if 'VIAGEM_ID' not in df_perf_resumo.columns:
                    df_perf_resumo['VIAGEM_ID'] = df_perf_resumo.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

                resumo_viagens_perf = df_perf_resumo.groupby('VIAGEM_ID').agg(
                    PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                    CUSTO_OS=('OS-R$', 'max'),
                    CUSTO_CTRB=('CTRB-R$', 'max'),
                    DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.dropna().astype(str).unique())),
                    TIPO_VEICULO=('TIPO_CAVALO', 'first')
                ).reset_index()

                def calcular_custo_viagem_perf(row):
                    custo_base = row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']
                    destinos_str = str(row.get('DESTINOS', '')).upper()
                    if 'GYN' in destinos_str or 'SPO' in destinos_str:
                        return custo_base / 2
                    return custo_base

                custo_km_por_tipo_perf = {'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75, 'PADRAO': 6.75}

                resumo_viagens_perf['CUSTO_FINAL'] = resumo_viagens_perf.apply(calcular_custo_viagem_perf, axis=1)
                resumo_viagens_perf['DISTANCIA_ESTIMADA'] = resumo_viagens_perf.apply(
                    lambda row: row['CUSTO_FINAL'] / custo_km_por_tipo_perf.get(str(row.get('TIPO_VEICULO', 'PADRAO')).upper(), 0)
                    if custo_km_por_tipo_perf.get(str(row.get('TIPO_VEICULO', 'PADRAO')).upper(), 0) > 0 else 0,
                    axis=1
                )
                distancia_total_perf = resumo_viagens_perf['DISTANCIA_ESTIMADA'].sum()
            else:
                total_entregas_perf = 0
                distancia_total_perf = 0

            custo_por_km_perf = (custo_ctrb_os / distancia_total_perf) if distancia_total_perf > 0 else 0
            distancia_media_perf = (distancia_total_perf / total_viagens_perf) if total_viagens_perf > 0 else 0
            peso_medio_perf = (peso_total / total_viagens_perf) if total_viagens_perf > 0 else 0
            entregas_media_perf = (total_entregas_perf / total_viagens_perf) if total_viagens_perf > 0 else 0

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <style>
            .efficiency-panel {
                position: relative;
                overflow: hidden;
                margin-top: 4px;
                padding: 16px 16px 14px 16px;
                border-radius: 24px;
                background:
                    radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.16) 0%, transparent 28%),
                    radial-gradient(circle at 100% 100%, rgba(129, 140, 248, 0.16) 0%, transparent 30%),
                    linear-gradient(180deg, rgba(8, 17, 38, 0.98) 0%, rgba(7, 14, 30, 0.99) 100%);
                border: 1px solid rgba(96, 165, 250, 0.18);
                box-shadow: 0 18px 38px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255,255,255,0.05);
            }
            .efficiency-panel::before {
                content: "";
                position: absolute;
                inset: 0;
                border-radius: 24px;
                padding: 1px;
                background: linear-gradient(135deg, rgba(56,189,248,0.24), rgba(255,255,255,0.03), rgba(129,140,248,0.24));
                -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
                pointer-events: none;
            }
            .efficiency-panel::after {
                content: "";
                position: absolute;
                left: 16px;
                right: 16px;
                top: 60px;
                height: 1px;
                background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(148,163,184,0.18) 18%, rgba(148,163,184,0.22) 50%, rgba(148,163,184,0.18) 82%, rgba(255,255,255,0) 100%);
                pointer-events: none;
            }
            .efficiency-header {
                position: relative;
                z-index: 1;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 16px;
            }
            .efficiency-title-wrap {
                display: flex;
                align-items: center;
                gap: 12px;
                min-width: 0;
            }
            .efficiency-title-icon {
                width: 38px;
                height: 38px;
                min-width: 38px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #dbeafe;
                background: linear-gradient(180deg, rgba(59,130,246,0.28) 0%, rgba(14,165,233,0.14) 100%);
                border: 1px solid rgba(125, 211, 252, 0.22);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 10px 20px rgba(2, 6, 23, 0.22);
                font-size: 0.92rem;
            }
            .efficiency-title-block {
                min-width: 0;
            }
            .efficiency-title {
                color: #f8fafc;
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 1.06rem;
                font-weight: 700;
                letter-spacing: -0.2px;
                line-height: 1.05;
                margin-bottom: 4px;
            }
            .efficiency-subtitle {
                color: #8ea5c4;
                font-size: 0.72rem;
                font-weight: 500;
                line-height: 1.2;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .efficiency-summary-pill {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 6px 10px;
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.42);
                border: 1px solid rgba(148, 163, 184, 0.16);
                color: #dbeafe;
                font-size: 0.68rem;
                font-weight: 700;
                letter-spacing: 0.12px;
                white-space: nowrap;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }
            .efficiency-summary-pill i {
                color: #7dd3fc;
                font-size: 0.70rem;
            }
            .efficiency-grid {
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 11px;
            }
            .efficiency-mini-card {
                position: relative;
                min-width: 0;
                overflow: hidden;
                isolation: isolate;
                padding: 12px 12px 11px 12px;
                border-radius: 18px;
                background:
                    linear-gradient(180deg, rgba(19, 35, 72, 0.92) 0%, rgba(11, 22, 47, 0.96) 100%);
                border: 1px solid rgba(148, 163, 184, 0.14);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 12px 24px rgba(2, 6, 23, 0.14);
                transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
            }
            .efficiency-mini-card::before {
                content: "";
                position: absolute;
                top: 0;
                left: 12px;
                right: 12px;
                height: 2px;
                border-radius: 999px;
                background: linear-gradient(90deg, rgba(125,211,252,0.85) 0%, rgba(96,165,250,0.18) 100%);
                opacity: 0.95;
            }
            .efficiency-mini-card.warning-card::before {
                background: linear-gradient(90deg, rgba(251,191,36,0.90) 0%, rgba(245,158,11,0.18) 100%);
            }
            .efficiency-mini-card:hover {
                transform: translateY(-3px);
                border-color: rgba(125, 211, 252, 0.24);
                box-shadow: 0 16px 28px rgba(2, 6, 23, 0.24), inset 0 1px 0 rgba(255,255,255,0.05);
            }
            .efficiency-mini-top {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 10px;
                margin-bottom: 8px;
            }
            .efficiency-mini-label {
                font-size: 0.68rem;
                font-weight: 700;
                color: #cbd5e1;
                letter-spacing: 0.18px;
                line-height: 1.2;
                text-transform: uppercase;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .efficiency-mini-icon {
                width: 30px;
                height: 30px;
                min-width: 30px;
                border-radius: 11px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #dbeafe;
                background: linear-gradient(180deg, rgba(59,130,246,0.22) 0%, rgba(14,165,233,0.10) 100%);
                border: 1px solid rgba(125,211,252,0.16);
                font-size: 0.76rem;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }
            .efficiency-mini-card.warning-card .efficiency-mini-icon {
                color: #fde68a;
                background: linear-gradient(180deg, rgba(245,158,11,0.24) 0%, rgba(245,158,11,0.10) 100%);
                border-color: rgba(245,158,11,0.18);
            }
            .efficiency-mini-value {
                color: #f8fafc;
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 1.20rem;
                font-weight: 800;
                line-height: 1.04;
                letter-spacing: -0.4px;
                margin-bottom: 10px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-shadow: 0 8px 18px rgba(2, 6, 23, 0.16);
            }
            .efficiency-mini-pill {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 9px;
                border-radius: 999px;
                background: rgba(16, 185, 129, 0.14);
                border: 1px solid rgba(16, 185, 129, 0.16);
                color: #a7f3d0;
                font-size: 0.64rem;
                font-weight: 700;
                letter-spacing: 0.12px;
            }
            .efficiency-mini-pill i {
                font-size: 0.62rem;
            }
            .efficiency-mini-pill.warning {
                background: rgba(245, 158, 11, 0.14);
                border-color: rgba(245, 158, 11, 0.16);
                color: #fde68a;
            }
            html[data-theme="light"] .efficiency-panel {
                background:
                    radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.10) 0%, transparent 28%),
                    radial-gradient(circle at 100% 100%, rgba(129, 140, 248, 0.10) 0%, transparent 30%),
                    linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
                border-color: rgba(15, 23, 42, 0.08);
                box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
            }
            html[data-theme="light"] .efficiency-panel::after {
                background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(148, 163, 184, 0.20) 18%, rgba(148, 163, 184, 0.24) 50%, rgba(148, 163, 184, 0.20) 82%, rgba(255,255,255,0) 100%);
            }
            html[data-theme="light"] .efficiency-title {
                color: #0f172a;
            }
            html[data-theme="light"] .efficiency-subtitle {
                color: #64748b;
            }
            html[data-theme="light"] .efficiency-summary-pill {
                background: rgba(255,255,255,0.84);
                border-color: rgba(148, 163, 184, 0.20);
                color: #1e3a8a;
            }
            html[data-theme="light"] .efficiency-mini-card {
                background: linear-gradient(180deg, rgba(241, 245, 249, 0.96) 0%, rgba(248, 250, 252, 0.99) 100%);
                border-color: rgba(148, 163, 184, 0.16);
                box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06), inset 0 1px 0 rgba(255,255,255,0.75);
            }
            html[data-theme="light"] .efficiency-mini-card:hover {
                border-color: rgba(59, 130, 246, 0.22);
                box-shadow: 0 14px 24px rgba(15, 23, 42, 0.10), inset 0 1px 0 rgba(255,255,255,0.85);
            }
            html[data-theme="light"] .efficiency-mini-label {
                color: #475569;
            }
            html[data-theme="light"] .efficiency-mini-value {
                color: #0f172a;
                text-shadow: none;
            }
            @media (max-width: 1350px) {
                .efficiency-grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }
            @media (max-width: 760px) {
                .efficiency-header {
                    flex-direction: column;
                    align-items: flex-start;
                }
                .efficiency-summary-pill {
                    align-self: flex-start;
                }
                .efficiency-grid {
                    grid-template-columns: 1fr;
                }
            }
            </style>
            """, unsafe_allow_html=True)

            eficiencia_html = f"""
            <div class="efficiency-panel">
                <div class="efficiency-header">
                    <div class="efficiency-title-wrap">
                        <div class="efficiency-title-icon"><i class="fa-solid fa-gauge-high"></i></div>
                        <div class="efficiency-title-block">
                            <div class="efficiency-title">Indicadores de Eficiência</div>
                            <div class="efficiency-subtitle">Complemento operacional para leitura rápida da performance</div>
                        </div>
                    </div>
                    <div class="efficiency-summary-pill"><i class="fa-solid fa-sparkles"></i> 4 KPIs</div>
                </div>
                <div class="efficiency-grid">
                    <div class="efficiency-mini-card">
                        <div class="efficiency-mini-top">
                            <div class="efficiency-mini-label">CTRB / Frete</div>
                            <div class="efficiency-mini-icon"><i class="fa-solid fa-route"></i></div>
                        </div>
                        <div class="efficiency-mini-value">{formatar_percentual(custo_transferencia)}</div>
                        <div class="efficiency-mini-pill"><i class="fa-solid fa-circle-check"></i> Eficiência logística</div>
                    </div>
                    <div class="efficiency-mini-card">
                        <div class="efficiency-mini-top">
                            <div class="efficiency-mini-label">Distância Média</div>
                            <div class="efficiency-mini-icon"><i class="fa-solid fa-road"></i></div>
                        </div>
                        <div class="efficiency-mini-value">{formatar_numero(distancia_media_perf)} km</div>
                        <div class="efficiency-mini-pill"><i class="fa-solid fa-route"></i> Percurso médio</div>
                    </div>
                    <div class="efficiency-mini-card warning-card">
                        <div class="efficiency-mini-top">
                            <div class="efficiency-mini-label">Custo / km</div>
                            <div class="efficiency-mini-icon"><i class="fa-solid fa-gauge-high"></i></div>
                        </div>
                        <div class="efficiency-mini-value">{formatar_moeda(custo_por_km_perf)}</div>
                        <div class="efficiency-mini-pill warning"><i class="fa-solid fa-gauge"></i> Custo rodado</div>
                    </div>
                    <div class="efficiency-mini-card">
                        <div class="efficiency-mini-top">
                            <div class="efficiency-mini-label">Peso Médio</div>
                            <div class="efficiency-mini-icon"><i class="fa-solid fa-boxes-stacked"></i></div>
                        </div>
                        <div class="efficiency-mini-value">{formatar_numero(peso_medio_perf)} kg</div>
                        <div class="efficiency-mini-pill"><i class="fa-solid fa-weight-hanging"></i> Carga média</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(eficiencia_html, unsafe_allow_html=True)

        with col_chart_perf:
            st.markdown("""
            <style>
            .performance-chart-shell {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at top left, rgba(34, 211, 238, 0.14) 0%, transparent 24%),
                    radial-gradient(circle at 82% 14%, rgba(59, 130, 246, 0.14) 0%, transparent 24%),
                    linear-gradient(180deg, rgba(7, 16, 34, 0.96) 0%, rgba(4, 11, 24, 0.98) 100%);
                border: 1px solid rgba(56, 189, 248, 0.14);
                border-radius: 28px;
                padding: 18px 20px 14px 20px;
                box-shadow: 0 22px 48px rgba(0, 0, 0, 0.30), inset 0 1px 0 rgba(255,255,255,0.05);
            }
            .performance-chart-shell::before {
                content: "";
                position: absolute;
                top: 0;
                left: 20px;
                right: 20px;
                height: 1px;
                background: linear-gradient(90deg, rgba(34, 211, 238, 0.00) 0%, rgba(34, 211, 238, 0.82) 22%, rgba(96, 165, 250, 0.30) 50%, rgba(34, 211, 238, 0.82) 78%, rgba(34, 211, 238, 0.00) 100%);
                pointer-events: none;
            }
            .performance-chart-shell::after {
                content: "";
                position: absolute;
                right: -42px;
                top: -34px;
                width: 180px;
                height: 180px;
                background: radial-gradient(circle, rgba(56, 189, 248, 0.14) 0%, rgba(56, 189, 248, 0.00) 72%);
                pointer-events: none;
            }
            .performance-chart-head {
                position: relative;
                z-index: 1;
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-bottom: 10px;
            }
            .performance-chart-kicker-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                flex-wrap: wrap;
            }
            .performance-chart-pill {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 7px 13px;
                border-radius: 999px;
                background: linear-gradient(180deg, rgba(10, 35, 72, 0.92) 0%, rgba(8, 24, 48, 0.96) 100%);
                border: 1px solid rgba(59, 130, 246, 0.22);
                color: #dbeafe;
                font-size: 0.73rem;
                font-weight: 700;
                letter-spacing: 0.28px;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 10px 22px rgba(0,0,0,0.20);
            }
            .performance-chart-pill-dot {
                width: 8px;
                height: 8px;
                border-radius: 999px;
                background: linear-gradient(180deg, #22d3ee 0%, #2563eb 100%);
                box-shadow: 0 0 12px rgba(34, 211, 238, 0.55);
            }
            .performance-chart-kicker-badge {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 6px 11px;
                border-radius: 999px;
                background: rgba(9, 18, 38, 0.56);
                border: 1px solid rgba(148, 163, 184, 0.16);
                color: #9fb2cc;
                font-size: 0.70rem;
                font-weight: 600;
                letter-spacing: 0.18px;
                backdrop-filter: blur(6px);
                -webkit-backdrop-filter: blur(6px);
            }
            .performance-chart-title-row {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 16px;
            }
            .performance-chart-title-group {
                display: flex;
                align-items: flex-start;
                gap: 14px;
                min-width: 0;
            }
            .performance-chart-title-icon {
                width: 48px;
                height: 48px;
                min-width: 48px;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #dff6ff;
                background: linear-gradient(180deg, rgba(34, 211, 238, 0.22) 0%, rgba(37, 99, 235, 0.18) 100%);
                border: 1px solid rgba(96, 165, 250, 0.18);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 10px 24px rgba(0,0,0,0.18);
                font-size: 1.05rem;
            }
            .performance-chart-title-wrap {
                display: flex;
                flex-direction: column;
                gap: 6px;
                min-width: 0;
            }
            .performance-chart-title {
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 1.32rem;
                font-weight: 700;
                color: #f8fafc;
                margin: 0;
                line-height: 1.1;
                letter-spacing: -0.3px;
            }
            .performance-chart-subtitle {
                font-size: 0.84rem;
                color: #93a4bf;
                margin: 0;
                line-height: 1.45;
            }
            .performance-chart-meta {
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
                margin-top: 4px;
            }
            .performance-chart-meta-chip {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 6px 10px;
                border-radius: 999px;
                background: rgba(9, 18, 38, 0.48);
                border: 1px solid rgba(148, 163, 184, 0.12);
                color: #c7d2fe;
                font-size: 0.72rem;
                font-weight: 600;
            }
            .performance-chart-meta-chip i {
                color: #38bdf8;
                font-size: 0.74rem;
            }
            .performance-chart-filter-label {
                font-size: 0.68rem;
                text-transform: uppercase;
                letter-spacing: 0.9px;
                color: #7dd3fc;
                font-weight: 700;
                margin: 2px 0 8px 2px;
            }
            div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] > div {
                min-height: 48px;
                border-radius: 16px;
                background: linear-gradient(180deg, rgba(18, 27, 49, 0.96) 0%, rgba(12, 20, 38, 0.98) 100%) !important;
                border: 1px solid rgba(96, 165, 250, 0.16) !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 12px 24px rgba(0,0,0,0.16) !important;
                transition: all 0.22s ease;
            }
            div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] > div:hover {
                border-color: rgba(56, 189, 248, 0.32) !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 14px 28px rgba(0,0,0,0.20), 0 0 0 1px rgba(34, 211, 238, 0.06) !important;
            }
            div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] span,
            div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] div {
                color: #f8fafc !important;
                font-weight: 600;
            }
            div.st-key-overview_financial_trend_tab1 svg {
                color: #7dd3fc !important;
            }
            html[data-theme="light"] .performance-chart-shell {
                background:
                    radial-gradient(circle at top left, rgba(34, 211, 238, 0.10) 0%, transparent 26%),
                    radial-gradient(circle at 82% 14%, rgba(59, 130, 246, 0.10) 0%, transparent 26%),
                    linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
                border-color: rgba(15, 23, 42, 0.08);
                box-shadow: 0 18px 34px rgba(15, 23, 42, 0.08);
            }
            html[data-theme="light"] .performance-chart-shell::before {
                background: linear-gradient(90deg, rgba(34, 211, 238, 0.00) 0%, rgba(34, 211, 238, 0.40) 22%, rgba(37, 99, 235, 0.18) 50%, rgba(34, 211, 238, 0.40) 78%, rgba(34, 211, 238, 0.00) 100%);
            }
            html[data-theme="light"] .performance-chart-pill {
                background: linear-gradient(180deg, rgba(219, 234, 254, 0.98) 0%, rgba(239, 246, 255, 0.99) 100%);
                border-color: rgba(59, 130, 246, 0.18);
                color: #1d4ed8;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.85), 0 8px 20px rgba(15,23,42,0.06);
            }
            html[data-theme="light"] .performance-chart-kicker-badge,
            html[data-theme="light"] .performance-chart-meta-chip {
                background: rgba(241, 245, 249, 0.96);
                border-color: rgba(148, 163, 184, 0.20);
                color: #475569;
            }
            html[data-theme="light"] .performance-chart-title-icon {
                color: #1d4ed8;
                background: linear-gradient(180deg, rgba(191, 219, 254, 0.82) 0%, rgba(224, 242, 254, 0.90) 100%);
                border-color: rgba(59, 130, 246, 0.16);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.84), 0 10px 22px rgba(15,23,42,0.08);
            }
            html[data-theme="light"] .performance-chart-title {
                color: #0f172a;
            }
            html[data-theme="light"] .performance-chart-subtitle {
                color: #64748b;
            }
            html[data-theme="light"] .performance-chart-filter-label {
                color: #0284c7;
            }
            html[data-theme="light"] div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] > div,
            html[data-theme="light"] div.st-key-overview_financial_mode_tab1 [data-baseweb="select"] > div {
                background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
                border-color: rgba(59, 130, 246, 0.16) !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 10px 20px rgba(15,23,42,0.06) !important;
            }
            html[data-theme="light"] div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] span,
            html[data-theme="light"] div.st-key-overview_financial_trend_tab1 [data-baseweb="select"] div,
            html[data-theme="light"] div.st-key-overview_financial_mode_tab1 [data-baseweb="select"] span,
            html[data-theme="light"] div.st-key-overview_financial_mode_tab1 [data-baseweb="select"] div {
                color: #0f172a !important;
            }
            html[data-theme="light"] div.st-key-overview_financial_trend_tab1 svg,
            html[data-theme="light"] div.st-key-overview_financial_mode_tab1 svg {
                color: #2563eb !important;
            }
            @media (max-width: 900px) {
                .performance-chart-title-row {
                    flex-direction: column;
                    align-items: stretch;
                }
                .performance-chart-title {
                    font-size: 1.16rem;
                }
                .performance-chart-shell {
                    padding: 16px 16px 12px 16px;
                }
            }
            </style>
            """, unsafe_allow_html=True)

            titulo_grafico_col, filtro_grafico_col = st.columns([0.68, 0.32], gap="medium")

            indice_padrao = 0 if periodo_tipo in ["Mês Completo", "Período Personalizado"] else 0
            with filtro_grafico_col:
                filtro_modo_col, filtro_gran_col = st.columns([0.52, 0.48], gap="small")
                with filtro_modo_col:
                    modo_visualizacao = st.selectbox(
                        'Modo do gráfico',
                        options=['Por período', 'Acumulado'],
                        index=0,
                        key='overview_financial_mode_tab1',
                        label_visibility='collapsed'
                    )
                with filtro_gran_col:
                    granularidade_tendencia = st.selectbox(
                        'Granularidade do gráfico',
                        options=['Diária', 'Semanal', 'Mensal'],
                        index=indice_padrao,
                        key='overview_financial_trend_tab1',
                        label_visibility='collapsed'
                    )

            mapa_frequencia = {
                'Diária': 'D',
                'Semanal': 'W',
                'Mensal': 'M'
            }

            mapa_unidade_periodo = {
                'Diária': 'dia',
                'Semanal': 'semana',
                'Mensal': 'mês'
            }
            unidade_periodo = mapa_unidade_periodo.get(granularidade_tendencia, 'período')
            subtitulo_grafico = (
                f"Acompanhe a evolução por {unidade_periodo} com leitura mais clara, elegante e executiva."
                if modo_visualizacao == 'Por período'
                else "Acompanhe a trajetória acumulada do período com leitura mais clara, elegante e executiva."
            )
            chip_modo_grafico = (
                f"Valores por {unidade_periodo}"
                if modo_visualizacao == 'Por período'
                else "Acumulado do período"
            )

            with titulo_grafico_col:
                st.markdown(f"""
                <div class="performance-chart-head">
                    <div class="performance-chart-kicker-row">
                    </div>
                    <div class="performance-chart-title-row">
                        <div class="performance-chart-title-group">
                            <div class="performance-chart-title-icon"><i class="fa-solid fa-chart-line"></i></div>
                            <div class="performance-chart-title-wrap">
                                <div class="performance-chart-title">Evolução de Receita x Custo x Lucro</div>
                                <div class="performance-chart-subtitle">{subtitulo_grafico}</div>
                                <div class="performance-chart-meta">
                                    <span class="performance-chart-meta-chip"><i class="fa-solid fa-wave-square"></i> Receita, custo e lucro</span>
                                    <span class="performance-chart-meta-chip"><i class="fa-regular fa-calendar"></i> {chip_modo_grafico}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if periodo_tipo == "Dia Específico" and 'DATA_OPERACIONAL' in df_original.columns:
                mes_referencia = pd.Timestamp(data_emissao_especifica).to_period('M')
                df_base_tendencia = df_original[
                    df_original['DATA_OPERACIONAL'].dt.to_period('M') == mes_referencia
                ].copy()
            else:
                df_base_tendencia = df_periodo_filtrado.copy()

            # Reaplica os mesmos filtros dos cards financeiros para que os valores do gráfico
            # e do tooltip usem exatamente a mesma lógica da Análise Financeira.
            df_base_tendencia = aplicar_filtros_para_comparacao_dia(df_base_tendencia)
            if df_base_tendencia.empty and not df_filtrado.empty:
                df_base_tendencia = df_filtrado.copy()

            serie_financeira = construir_serie_financeira(
                df_base_tendencia,
                mapa_frequencia.get(granularidade_tendencia, 'D')
            )

            if len(serie_financeira) < 2:
                serie_financeira_alternativa = construir_serie_financeira(
                    df_filtrado,
                    mapa_frequencia.get(granularidade_tendencia, 'D')
                )
                if len(serie_financeira_alternativa) > len(serie_financeira):
                    serie_financeira = serie_financeira_alternativa

            if not serie_financeira.empty:
                serie_financeira = serie_financeira.sort_values('PERIODO_DT').reset_index(drop=True)
                serie_financeira[['Receita', 'Custo', 'Lucro']] = (
                    serie_financeira[['Receita', 'Custo', 'Lucro']]
                    .apply(pd.to_numeric, errors='coerce')
                    .fillna(0)
                )

                # No modo diário, exibe somente dias úteis (segunda a sexta).
                if granularidade_tendencia == 'Diária':
                    serie_financeira = serie_financeira[
                        serie_financeira['PERIODO_DT'].dt.dayofweek < 5
                    ].copy()

                # Remove dias/períodos sem movimentação para não poluir o gráfico com pontos zerados.
                serie_financeira = serie_financeira[
                    serie_financeira[['Receita', 'Custo', 'Lucro']].abs().sum(axis=1) > 0
                ].copy()

                if not serie_financeira.empty:
                    mapa_dias_semana = {
                        0: 'Segunda-feira',
                        1: 'Terça-feira',
                        2: 'Quarta-feira',
                        3: 'Quinta-feira',
                        4: 'Sexta-feira',
                        5: 'Sábado',
                        6: 'Domingo'
                    }

                    serie_financeira['PERIODO_TOOLTIP'] = serie_financeira['PERIODO_DT'].dt.strftime('%d/%m/%Y')
                    serie_financeira['DIA_SEMANA_TOOLTIP'] = serie_financeira['PERIODO_DT'].dt.dayofweek.map(mapa_dias_semana)
                    titulo_valor_periodo = '💰 Valor do período'

                    if granularidade_tendencia == 'Semanal':
                        serie_financeira['PERIODO_TOOLTIP'] = serie_financeira['PERIODO_DT'].apply(
                            lambda ts: f"{ts.strftime('%d/%m/%Y')} a {(ts + pd.Timedelta(days=6)).strftime('%d/%m/%Y')}"
                        )
                        serie_financeira['DIA_SEMANA_TOOLTIP'] = serie_financeira['PERIODO_DT'].dt.dayofweek.map(mapa_dias_semana).apply(
                            lambda dia: f"Semana iniciando em {dia}"
                        )
                        serie_financeira['PERIODO_EIXO'] = serie_financeira['PERIODO_DT'].dt.strftime('%d/%m')
                        titulo_valor_periodo = '💰 Valor da semana'
                    elif granularidade_tendencia == 'Mensal':
                        serie_financeira['PERIODO_TOOLTIP'] = serie_financeira['PERIODO_DT'].dt.strftime('%m/%Y')
                        serie_financeira['DIA_SEMANA_TOOLTIP'] = serie_financeira['PERIODO_DT'].dt.strftime('%B de %Y').str.capitalize()
                        serie_financeira['PERIODO_EIXO'] = serie_financeira['PERIODO_DT'].dt.strftime('%m/%Y')
                        titulo_valor_periodo = '💰 Valor do mês'
                    else:
                        serie_financeira['PERIODO_EIXO'] = serie_financeira['PERIODO_DT'].dt.strftime('%d/%m')
                        titulo_valor_periodo = '💰 Valor do dia'

                    for serie_nome in ['Receita', 'Custo', 'Lucro']:
                        serie_financeira[f'{serie_nome}_PERIODO'] = serie_financeira[serie_nome]
                        serie_financeira[f'{serie_nome}_ACUMULADO'] = serie_financeira[serie_nome].cumsum()

                    ordem_periodos = serie_financeira['PERIODO_EIXO'].tolist()
                    configuracao_series = {
                        'Receita': {'label': '🔵 Receita', 'cor': '#1ea7ff'},
                        'Custo': {'label': '🟠 Custo', 'cor': '#f59e0b'},
                        'Lucro': {'label': '🟢 Lucro', 'cor': '#22c55e'}
                    }

                    registros_long = []
                    for serie_nome in ['Receita', 'Custo', 'Lucro']:
                        df_temp = serie_financeira[['PERIODO_DT', 'PERIODO_LABEL', 'PERIODO_TOOLTIP', 'DIA_SEMANA_TOOLTIP', 'PERIODO_EIXO']].copy()
                        df_temp['Serie'] = serie_nome
                        df_temp['SerieLabel'] = configuracao_series.get(serie_nome, {}).get('label', serie_nome)
                        df_temp['ValorPeriodo'] = serie_financeira[f'{serie_nome}_PERIODO']
                        df_temp['ValorAcumulado'] = serie_financeira[f'{serie_nome}_ACUMULADO']
                        df_temp['ValorPeriodoFmt'] = df_temp['ValorPeriodo'].apply(formatar_moeda)
                        df_temp['ValorAcumuladoFmt'] = df_temp['ValorAcumulado'].apply(formatar_moeda)
                        registros_long.append(df_temp)

                    serie_financeira_long = pd.concat(registros_long, ignore_index=True)

                    dominio_legenda = [
                        configuracao_series['Receita']['label'],
                        configuracao_series['Custo']['label'],
                        configuracao_series['Lucro']['label']
                    ]
                    cores_legenda = [
                        configuracao_series['Receita']['cor'],
                        configuracao_series['Custo']['cor'],
                        configuracao_series['Lucro']['cor']
                    ]

                    campo_valor_grafico = 'ValorPeriodo' if modo_visualizacao == 'Por período' else 'ValorAcumulado'
                    tooltip_grafico = [
                        alt.Tooltip('PERIODO_TOOLTIP:N', title='📅 Período'),
                        alt.Tooltip('DIA_SEMANA_TOOLTIP:N', title='🗓️ Dia da semana'),
                        alt.Tooltip('SerieLabel:N', title='✨ Indicador')
                    ]
                    if modo_visualizacao == 'Por período':
                        tooltip_grafico.extend([
                            alt.Tooltip('ValorPeriodoFmt:N', title=titulo_valor_periodo),
                            alt.Tooltip('ValorAcumuladoFmt:N', title='📈 Acumulado até aqui')
                        ])
                    else:
                        tooltip_grafico.extend([
                            alt.Tooltip('ValorAcumuladoFmt:N', title='📈 Valor acumulado'),
                            alt.Tooltip('ValorPeriodoFmt:N', title=titulo_valor_periodo)
                        ])

                    base_tendencia = alt.Chart(serie_financeira_long).encode(
                        x=alt.X(
                            'PERIODO_EIXO:N',
                            sort=ordem_periodos,
                            title=None,
                            axis=alt.Axis(
                                labelAngle=0,
                                labelColor='#cbd5e1',
                                labelFontSize=11,
                                labelOverlap=False,
                                tickColor='#22324f',
                                domain=False,
                                grid=False
                            )
                        ),
                        y=alt.Y(
                            f'{campo_valor_grafico}:Q',
                            title=None,
                            axis=alt.Axis(
                                format='~s',
                                labelColor='#cbd5e1',
                                labelFontSize=11,
                                tickColor='#22324f',
                                domain=False,
                                grid=True,
                                gridColor='rgba(71, 85, 105, 0.22)'
                            )
                        ),
                        color=alt.Color(
                            'SerieLabel:N',
                            title=None,
                            scale=alt.Scale(
                                domain=dominio_legenda,
                                range=cores_legenda
                            ),
                            legend=alt.Legend(
                                orient='top',
                                direction='horizontal',
                                columns=3,
                                labelColor='#e2e8f0',
                                symbolType='stroke',
                                symbolStrokeWidth=4,
                                padding=6,
                                offset=10
                            )
                        ),
                        tooltip=tooltip_grafico
                    )

                    linhas_tendencia = base_tendencia.mark_line(interpolate='linear', strokeWidth=3.2)
                    pontos_tendencia = base_tendencia.mark_circle(size=34, opacity=0.95)

                    chart_tendencia_financeira = (
                        linhas_tendencia + pontos_tendencia
                    ).properties(height=450).configure(
                        background='transparent'
                    ).configure_view(
                        stroke=None,
                        fill='transparent'
                    ).configure_legend(
                        labelFontSize=12,
                        symbolSize=400,
                        title=None
                    )

                    st.altair_chart(chart_tendencia_financeira, use_container_width=True)
                else:
                    st.info('Não há dias com movimentação para exibir nesse gráfico com os filtros atuais.')
            else:
                st.info('Não há dados suficientes para montar a evolução financeira com os filtros atuais.')

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
        # 🌟 CSS PROFISSIONAL PARA A SEÇÃO DE OCUPAÇÃO
        st.markdown("""
        <style>
            .occupancy-title-block {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at 12% 18%, rgba(37, 99, 235, 0.20), transparent 24%),
                    radial-gradient(circle at 88% 20%, rgba(16, 185, 129, 0.16), transparent 26%),
                    linear-gradient(135deg, rgba(7, 15, 30, 0.98) 0%, rgba(9, 19, 36, 0.96) 42%, rgba(5, 12, 24, 0.99) 100%);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 22px;
                padding: 18px 26px;
                margin: 22px 0 18px 0;
                box-shadow: 0 22px 54px rgba(2, 6, 23, 0.42), inset 0 1px 0 rgba(255,255,255,0.05);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 18px;
                isolation: isolate;
            }
            .occupancy-title-block::before {
                content: "";
                position: absolute;
                inset: 0;
                border-radius: 22px;
                padding: 1px;
                background: linear-gradient(90deg, rgba(96,165,250,0.34), rgba(16,185,129,0.34), rgba(96,165,250,0.16));
                -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
                -webkit-mask-composite: xor;
                mask-composite: exclude;
                pointer-events: none;
                opacity: 0.95;
            }
            .occupancy-title-block::after {
                content: "";
                position: absolute;
                right: -76px;
                top: -64px;
                width: 260px;
                height: 260px;
                background: radial-gradient(circle, rgba(16,185,129,0.16) 0%, rgba(16,185,129,0.00) 72%);
                pointer-events: none;
                z-index: 0;
            }
            .occupancy-title-icon {
                width: 60px;
                height: 60px;
                min-width: 60px;
                border-radius: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(180deg, rgba(15,23,42,0.92) 0%, rgba(15,23,42,0.72) 100%);
                border: 1px solid rgba(96,165,250,0.26);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 14px 28px rgba(2, 6, 23, 0.28);
                position: relative;
                z-index: 1;
            }
            .occupancy-title-icon::after {
                content: "";
                position: absolute;
                inset: -1px;
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(96,165,250,0.18), rgba(16,185,129,0.14));
                opacity: 0.95;
                z-index: -1;
            }
            .occupancy-title-icon i {
                font-size: 1.55rem;
                color: #dbeafe;
                text-shadow: 0 0 18px rgba(96,165,250,0.18);
            }
            .occupancy-title-content {
                text-align: center;
                position: relative;
                z-index: 1;
            }
            .occupancy-title-content .eyebrow {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                padding: 6px 14px;
                margin-bottom: 10px;
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.52);
                border: 1px solid rgba(96,165,250,0.18);
                color: #a5f3fc;
                font-size: 0.74rem;
                font-weight: 800;
                letter-spacing: 1.05px;
                text-transform: uppercase;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
            }
            .occupancy-title-content h2 {
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 2.2rem;
                font-weight: 800;
                color: #f8fafc;
                margin: 0;
                letter-spacing: -0.6px;
                line-height: 1.1;
            }
            .occupancy-title-content p {
                margin: 8px 0 0 0;
                font-size: 0.96rem;
                color: rgba(226, 232, 240, 0.72);
                letter-spacing: 0.15px;
            }
            html[data-theme="light"] .occupancy-title-block {
                background:
                    radial-gradient(circle at 10% 14%, rgba(59,130,246,0.10), transparent 24%),
                    radial-gradient(circle at 88% 18%, rgba(16,185,129,0.10), transparent 28%),
                    linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%) !important;
                border: 1px solid rgba(15,23,42,0.08) !important;
                box-shadow: 0 18px 40px rgba(15,23,42,0.08) !important;
            }
            html[data-theme="light"] .occupancy-title-block::before {
                background: linear-gradient(90deg, rgba(59,130,246,0.18), rgba(16,185,129,0.18), rgba(59,130,246,0.08)) !important;
            }
            html[data-theme="light"] .occupancy-title-icon {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.96) 100%) !important;
                border: 1px solid rgba(59,130,246,0.12) !important;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 12px 24px rgba(15,23,42,0.08) !important;
            }
            html[data-theme="light"] .occupancy-title-icon i {
                color: #2563eb !important;
                text-shadow: none !important;
            }
            html[data-theme="light"] .occupancy-title-content .eyebrow {
                background: rgba(239,246,255,0.98) !important;
                color: #0284c7 !important;
                border-color: rgba(59,130,246,0.14) !important;
            }
            html[data-theme="light"] .occupancy-title-content h2 {
                color: #0f172a !important;
            }
            html[data-theme="light"] .occupancy-title-content p {
                color: rgba(51,65,85,0.82) !important;
            }

            .occupancy-main-card {
                position: relative;
                overflow: hidden;
                min-height: 152px;
                border-radius: 20px;
                padding: 18px 18px 16px 18px;
                background:
                    linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.00) 18%),
                    linear-gradient(135deg, #191f33 0%, #171a2b 52%, #101524 100%);
                border: 1px solid rgba(148, 163, 184, 0.14);
                box-shadow: 0 18px 36px rgba(2, 6, 23, 0.34), inset 0 1px 0 rgba(255,255,255,0.04);
                transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
                margin-bottom: 12px;
            }
            .occupancy-main-card:hover,
            .occupancy-idle-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 22px 42px rgba(2, 6, 23, 0.42);
            }
            .occupancy-main-card::after {
                content: "";
                position: absolute;
                right: -42px;
                bottom: -46px;
                width: 170px;
                height: 130px;
                background: linear-gradient(135deg, rgba(255,255,255,0.0) 20%, var(--accent-glow) 56%, rgba(255,255,255,0.0) 85%);
                transform: rotate(-8deg);
                pointer-events: none;
            }
            .occupancy-theme-peso {
                --accent: #60a5fa;
                --accent-strong: #2563eb;
                --accent-glow: rgba(96, 165, 250, 0.18);
                --accent-soft: rgba(96, 165, 250, 0.14);
            }
            .occupancy-theme-volume {
                --accent: #38bdf8;
                --accent-strong: #0ea5e9;
                --accent-glow: rgba(56, 189, 248, 0.18);
                --accent-soft: rgba(56, 189, 248, 0.14);
            }
            .occupancy-main-header {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 16px;
                position: relative;
                z-index: 1;
            }
            .occupancy-title-wrap {
                display: flex;
                flex-direction: column;
                gap: 12px;
                min-width: 0;
            }
            .occupancy-card-title {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 1.18rem;
                font-weight: 800;
                color: #f8fafc;
                letter-spacing: 0.2px;
                line-height: 1.3;
            }
            .occupancy-card-title i {
                color: var(--accent);
                font-size: 1.14rem;
            }
            .occupancy-percent {
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 2.1rem;
                line-height: 1;
                font-weight: 800;
                letter-spacing: -0.8px;
                color: #f8fafc;
                white-space: nowrap;
            }
            .occupancy-status-pill {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                width: fit-content;
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 0.80rem;
                font-weight: 700;
                letter-spacing: 0.2px;
                border: 1px solid transparent;
            }
            .occupancy-status-util-low,
            .occupancy-status-idle-high {
                color: #fde68a;
                background: rgba(245, 158, 11, 0.14);
                border-color: rgba(245, 158, 11, 0.24);
            }
            .occupancy-status-util-ideal,
            .occupancy-status-idle-ideal {
                color: #bfdbfe;
                background: rgba(59, 130, 246, 0.14);
                border-color: rgba(59, 130, 246, 0.24);
            }
            .occupancy-status-util-high,
            .occupancy-status-idle-low {
                color: #bbf7d0;
                background: rgba(34, 197, 94, 0.14);
                border-color: rgba(34, 197, 94, 0.24);
            }
            .occupancy-progress-track {
                position: relative;
                z-index: 1;
                width: 100%;
                height: 10px;
                margin: 16px 0 14px 0;
                border-radius: 999px;
                overflow: hidden;
                background: rgba(148, 163, 184, 0.16);
                box-shadow: inset 0 1px 2px rgba(2,6,23,0.28);
            }
            .occupancy-progress-fill {
                height: 100%;
                border-radius: inherit;
                box-shadow: 0 0 18px rgba(96, 165, 250, 0.16);
                transition: width 1.1s ease-in-out;
            }
            .occupancy-divider {
                position: relative;
                z-index: 1;
                height: 1px;
                background: linear-gradient(90deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.42) 12%, rgba(255,255,255,0.18) 100%);
                margin: 0 0 18px 0;
            }
            .occupancy-chip-row {
                position: relative;
                z-index: 1;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: nowrap;
                gap: 12px;
            }
            .occupancy-chip {
                display: inline-flex;
                align-items: center;
                gap: 9px;
                padding: 9px 16px;
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.34);
                border: 1px solid rgba(255,255,255,0.10);
                font-size: 0.90rem;
                font-weight: 700;
                color: #e2e8f0;
                line-height: 1;
                white-space: nowrap;
            }
            .occupancy-chip:last-child {
                margin-left: auto;
            }
            .occupancy-chip i {
                color: var(--accent);
                font-size: 0.92rem;
            }

            .occupancy-idle-card {
                position: relative;
                overflow: hidden;
                min-height: 152px;
                border-radius: 16px;
                padding: 16px 16px 14px 16px;
                background:
                    linear-gradient(180deg, rgba(255,255,255,0.025) 0%, rgba(255,255,255,0.00) 18%),
                    linear-gradient(135deg, rgba(24, 31, 51, 0.96) 0%, rgba(18, 24, 38, 0.98) 55%, rgba(13, 18, 31, 0.98) 100%);
                border: 1px solid rgba(148, 163, 184, 0.16);
                box-shadow: 0 14px 28px rgba(2, 6, 23, 0.28);
                transition: transform .22s ease, box-shadow .22s ease;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .occupancy-idle-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 14px;
                margin-bottom: 12px;
            }
            .occupancy-idle-title-wrap {
                display: flex;
                flex-direction: column;
                gap: 12px;
                min-width: 0;
            }
            .occupancy-idle-title {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 1.18rem;
                font-weight: 800;
                color: #f8fafc;
                line-height: 1.25;
            }
            .occupancy-idle-title i {
                color: #94a3b8;
                font-size: 1.14rem;
            }
            .occupancy-idle-percent {
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 1.95rem;
                line-height: 1;
                font-weight: 800;
                letter-spacing: -0.8px;
                color: #e2e8f0;
                white-space: nowrap;
            }
            .occupancy-idle-progress-track {
                width: 100%;
                height: 9px;
                border-radius: 999px;
                overflow: hidden;
                background: rgba(148, 163, 184, 0.14);
                margin: 0 0 12px 0;
            }
            .occupancy-idle-progress-fill {
                height: 100%;
                border-radius: inherit;
                box-shadow: 0 0 18px rgba(96, 165, 250, 0.16);
                transition: width 1.1s ease-in-out;
            }
            .occupancy-idle-divider {
                position: relative;
                z-index: 1;
                height: 1px;
                background: linear-gradient(90deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.72) 16%, rgba(255,255,255,0.28) 100%);
                box-shadow: 0 0 1px rgba(255,255,255,0.55);
                margin: 0 0 18px 0;
            }
            .occupancy-idle-footer {
                position: relative;
                z-index: 1;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: nowrap;
                gap: 12px;
                color: #e5e7eb;
            }
            .occupancy-idle-footer .occupancy-chip {
                background: rgba(15, 23, 42, 0.36);
                border-color: rgba(148, 163, 184, 0.22);
                color: #f8fafc;
            }
            .occupancy-idle-footer .occupancy-chip i {
                color: #94a3b8;
                font-size: 0.92rem;
            }
            .occupancy-idle-footer .occupancy-chip:last-child {
                margin-left: auto;
            }
            .occupancy-idle-value {
                font-size: 1rem;
                font-weight: 700;
                color: #f8fafc;
                white-space: nowrap;
            }
            .occupancy-idle-hint {
                font-size: 0.84rem;
                color: rgba(226, 232, 240, 0.70);
                text-transform: uppercase;
                letter-spacing: 0.45px;
            }

            .ctrb-gauge-wrap {
                display: flex;
                justify-content: center;
                margin: 18px 0 24px 0;
            }
            .ctrb-gauge-card {
                width: min(100%, 720px);
            }
            .ctrb-gauge-card::before {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0.00) 42%);
                pointer-events: none;
            }
            .ctrb-gauge-header {
                position: relative;
                z-index: 1;
                text-align: center;
                margin-bottom: 6px;
            }
            .ctrb-gauge-title {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 1.18rem;
                font-weight: 800;
                color: #f8fafc;
                line-height: 1.2;
                text-align: center;
            }
            .ctrb-gauge-title i {
                color: #38bdf8;
            }
            .ctrb-gauge-subtitle {
                margin-top: 8px;
                font-size: 0.84rem;
                color: rgba(226,232,240,0.78);
            }
            .ctrb-gauge-svg-wrap {
                position: relative;
                z-index: 1;
                display: flex;
                justify-content: center;
                margin-top: 8px;
            }
            .ctrb-gauge-svg {
                width: 100%;
                max-width: 520px;
                height: auto;
                overflow: visible;
            }
            .ctrb-gauge-value {
                position: relative;
                z-index: 1;
                margin-top: -10px;
                text-align: center;
                font-family: "Poppins", "Segoe UI", sans-serif;
                font-size: 3rem;
                font-weight: 800;
                line-height: 1;
                letter-spacing: -1px;
                color: #f8fafc;
                text-shadow: 0 0 20px rgba(255,255,255,0.10);
            }
            .ctrb-gauge-status {
                position: relative;
                z-index: 1;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin: 12px auto 0 auto;
                padding: 8px 18px;
                border-radius: 999px;
                border: 1px solid rgba(255,255,255,0.14);
                font-size: 0.95rem;
                font-weight: 700;
                min-width: 170px;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
            }
            .ctrb-gauge-status-good {
                color: #dcfce7;
                background: linear-gradient(135deg, rgba(22,163,74,0.22) 0%, rgba(34,197,94,0.12) 100%);
                border-color: rgba(34,197,94,0.35);
            }
            .ctrb-gauge-status-regular {
                color: #fef3c7;
                background: linear-gradient(135deg, rgba(217,119,6,0.22) 0%, rgba(250,204,21,0.10) 100%);
                border-color: rgba(250,204,21,0.35);
            }
            .ctrb-gauge-status-bad {
                color: #fee2e2;
                background: linear-gradient(135deg, rgba(220,38,38,0.22) 0%, rgba(239,68,68,0.10) 100%);
                border-color: rgba(248,113,113,0.35);
            }
            .ctrb-gauge-footer {
                position: relative;
                z-index: 1;
                margin-top: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
            }
            .ctrb-gauge-chip {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 6px 11px;
                border-radius: 999px;
                background: rgba(15,23,42,0.42);
                border: 1px solid rgba(255,255,255,0.10);
                color: #e2e8f0;
                font-size: 0.84rem;
                font-weight: 600;
                white-space: nowrap;
            }
            .ctrb-gauge-chip i {
                color: #60a5fa;
            }
            .ctrb-gauge-tick-label {
                font-size: 10px;
                font-weight: 700;
                fill: #e2e8f0;
            }
            .ctrb-gauge-tick-line {
                stroke: rgba(255,255,255,0.20);
                stroke-width: 1.4;
                stroke-linecap: round;
            }


            @media (max-width: 900px) {
                .occupancy-title-block {
                    flex-direction: column;
                    text-align: center;
                    padding: 18px 16px;
                }
                .occupancy-title-content h2 {
                    font-size: 1.45rem;
                }
                .occupancy-main-header,
                .occupancy-idle-header,
                .occupancy-idle-footer,
                .occupancy-chip-row {
                    flex-direction: column;
                    align-items: flex-start;
                }
                .occupancy-percent,
                .occupancy-idle-percent {
                    font-size: 1.65rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        # --- TÍTULO NO MESMO ESTILO DO "PAINEL DE DESEMPENHO GERAL" ---
        st.markdown("""
            <div class="title-block-financeira" style="margin: 12px 0 22px 0;">
                <i class="fa-solid fa-chart-column"></i>
                <h2>Análise de Ocupação de Carga por Tipo de Veículo</h2>
            </div>
        """, unsafe_allow_html=True)

        # ===============================================
        # 🧭 OPTION MENU DINÂMICO E ANÁLISE DE OCUPAÇÃO (VERSÃO FINAL COM IDENTIFICAÇÃO POR PLACA)
        # ===============================================

        # --- INÍCIO DA LÓGICA DA CATEGORIA DE VIAGEM ---

        df_com_categoria = df_filtrado.copy()

        # ▼▼▼ INÍCIO DA CORREÇÃO ▼▼▼
        def definir_categoria_viagem(row):
            """
            Define a categoria da viagem com uma lógica aprimorada:
            1. Verifica se a placa do cavalo pertence à lista de BI-TRUCKs.
            2. Se não, verifica se é uma CARRETA.
            3. Se não, usa o TIPO_CAVALO como fallback.
            """
            # 1. Lista de placas que são BI-TRUCKs
            placas_bitruck = {"REW6J23", "RWG9G33", "GBQ0I23", "SFH1C15"}
            
            placa_cavalo_atual = row.get('PLACA_CAVALO')

            # 2. Lógica de identificação prioritária
            if placa_cavalo_atual in placas_bitruck:
                return 'BI-TRUCK'

            # 3. Lógica para CARRETA (permanece a mesma)
            placa_carreta = row.get('PLACA_CARRETA')
            if pd.notna(placa_carreta) and placa_carreta != 'nan' and placa_carreta != placa_cavalo_atual:
                return 'CARRETA' 
            
            # 4. Fallback: Se não for BI-TRUCK nem CARRETA, usa o tipo da coluna
            return str(row.get('TIPO_CAVALO', 'INDEFINIDO')).upper()
        # ▲▲▲ FIM DA CORREÇÃO ▲▲▲

        if not df_com_categoria.empty:
            df_com_categoria['CATEGORIA_VIAGEM'] = df_com_categoria.apply(definir_categoria_viagem, axis=1)
        else:
            df_com_categoria['CATEGORIA_VIAGEM'] = pd.Series(dtype='str')


        # --- LAYOUT FIXO DO SELETOR (mantém igual ao da visão de Mês Completo) ---
        opcoes_seletor = ["TODOS", "TRUCK", "BI-TRUCK", "CARRETA"]
        icones_seletor = ["grid-fill", "truck", "truck-flatbed", "truck-front"]

        # 6. Cria o seletor dinâmico
        selecionar_veiculo = option_menu(
            menu_title=None,
            options=opcoes_seletor,
            icons=icones_seletor,
            menu_icon=None,
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {
                    "padding": "10px",
                    "background": "linear-gradient(135deg, rgba(7,15,30,0.96) 0%, rgba(15,23,42,0.90) 60%, rgba(10,17,32,0.96) 100%)",
                    "border-radius": "22px",
                    "border": "1px solid rgba(148,163,184,0.14)",
                    "box-shadow": "0 20px 44px rgba(2,6,23,0.32), inset 0 1px 0 rgba(255,255,255,0.04)",
                    "justify-content": "center",
                    "gap": "6px"
                },
                "icon": {
                    "font-size": "15px",
                    "margin-right": "8px",
                    "display": "inline-flex",
                    "align-items": "center"
                },
                "nav-link": {
                    "font-size": "13px",
                    "font-weight": "800",
                    "color": "#cbd5e1",
                    "padding": "13px 28px",
                    "border-radius": "16px",
                    "margin": "0px 4px",
                    "background": "linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)",
                    "border": "1px solid rgba(255,255,255,0.04)",
                    "text-align": "center",
                    "transition": "all .18s ease"
                },
                "nav-link:hover": {
                    "background": "linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%)",
                    "color": "#ffffff",
                    "border": "1px solid rgba(148,163,184,0.12)"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, rgba(29,78,216,0.96) 0%, rgba(30,64,175,0.98) 58%, rgba(15,23,42,0.96) 100%)",
                    "color": "#FFFFFF",
                    "border": "1.5px solid rgba(147,197,253,0.92)",
                    "box-shadow": "0 0 0 1px rgba(96,165,250,0.18), 0 14px 26px rgba(37,99,235,0.30), inset 0 1px 0 rgba(255,255,255,0.16)"
                },
            },
        )


        # 7. Cria o DataFrame final para análise ('df_para_analise')
        df_para_analise = df_com_categoria.copy()
        if selecionar_veiculo != "TODOS":
            df_para_analise = df_para_analise[df_para_analise['CATEGORIA_VIAGEM'] == selecionar_veiculo]


        # ===============================================
        # FUNÇÕES DE APOIO DA ÁREA DE OCUPAÇÃO
        # ===============================================
        def obter_status_utilizacao(percentual):
            if percentual < 50:
                return "Baixa ocupação", "occupancy-status-util-low"
            elif percentual <= 80:
                return "Faixa ideal", "occupancy-status-util-ideal"
            return "Alta utilização", "occupancy-status-util-high"


        def obter_status_ociosidade(percentual):
            if percentual < 20:
                return "Baixa ociosidade", "occupancy-status-idle-low"
            elif percentual <= 50:
                return "Faixa ideal", "occupancy-status-idle-ideal"
            return "Alta ociosidade", "occupancy-status-idle-high"


        def obter_estilo_utilizacao(percentual):
            if percentual < 50:
                return {
                    "barra": "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)",
                    "brilho": "0 0 18px rgba(245, 158, 11, 0.22)",
                    "percentual": "#fde68a"
                }
            elif percentual <= 80:
                return {
                    "barra": "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)",
                    "brilho": "0 0 18px rgba(96, 165, 250, 0.20)",
                    "percentual": "#dbeafe"
                }
            return {
                "barra": "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)",
                "brilho": "0 0 18px rgba(34, 197, 94, 0.20)",
                "percentual": "#bbf7d0"
            }


        def obter_estilo_ociosidade(percentual):
            if percentual < 20:
                return {
                    "barra": "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)",
                    "brilho": "0 0 18px rgba(34, 197, 94, 0.20)",
                    "percentual": "#bbf7d0",
                    "icone": "#4ade80"
                }
            elif percentual <= 50:
                return {
                    "barra": "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)",
                    "brilho": "0 0 18px rgba(96, 165, 250, 0.20)",
                    "percentual": "#dbeafe",
                    "icone": "#60a5fa"
                }
            return {
                "barra": "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)",
                "brilho": "0 0 18px rgba(245, 158, 11, 0.22)",
                "percentual": "#fde68a",
                "icone": "#fbbf24"
            }


        def renderizar_card_ocupacao_moderno(
            titulo,
            ocup_perc,
            total_valor,
            cap_total,
            unidade,
            ociosidade_perc,
            potencial_nao_utilizado,
            icone_topo,
            icone_ociosidade,
            titulo_ociosidade,
            tema="peso"
        ):
            status_txt, status_cls = obter_status_utilizacao(ocup_perc)
            status_txt_idle, status_cls_idle = obter_status_ociosidade(ociosidade_perc)
            estilo_ocup = obter_estilo_utilizacao(ocup_perc)
            estilo_idle = obter_estilo_ociosidade(ociosidade_perc)
            classe_tema = "occupancy-theme-peso" if tema == "peso" else "occupancy-theme-volume"
            decimais_total = 3 if unidade == 'M³' else 0
            decimais_cap = 2 if unidade == 'M³' else 0
            decimais_potencial = 2 if unidade == 'M³' else 0

            st.markdown(f"""
                <div class="occupancy-main-card {classe_tema}">
                    <div class="occupancy-main-header">
                        <div class="occupancy-title-wrap">
                            <div class="occupancy-card-title">
                                <i class="fa-solid {icone_topo}"></i>
                                <span>{titulo}</span>
                            </div>
                            <span class="occupancy-status-pill {status_cls}">{status_txt}</span>
                        </div>
                        <div class="occupancy-percent" style="color: {estilo_ocup['percentual']};">{ocup_perc:.0f}%</div>
                    </div>
                    <div class="occupancy-progress-track">
                        <div class="occupancy-progress-fill" style="width: {min(ocup_perc, 100)}%; background: {estilo_ocup['barra']}; box-shadow: {estilo_ocup['brilho']};"></div>
                    </div>
                    <div class="occupancy-divider"></div>
                    <div class="occupancy-chip-row">
                        <span class="occupancy-chip"><i class="fa-solid fa-cubes-stacked"></i> Total: {formatar_numero(total_valor, decimais_total)} {unidade}</span>
                        <span class="occupancy-chip"><i class="fa-solid fa-database"></i> Capacidade: {formatar_numero(cap_total, decimais_cap)} {unidade}</span>
                    </div>
                </div>
                <div class="occupancy-idle-card">
                    <div class="occupancy-idle-header">
                        <div class="occupancy-idle-title-wrap">
                            <div class="occupancy-idle-title">
                                <i class="{icone_ociosidade}" style="color: {estilo_idle['icone']};"></i>
                                <span>{titulo_ociosidade}</span>
                            </div>
                            <span class="occupancy-status-pill {status_cls_idle}">{status_txt_idle}</span>
                        </div>
                        <div class="occupancy-idle-percent" style="color: {estilo_idle['percentual']};">{ociosidade_perc:.0f}%</div>
                    </div>
                    <div class="occupancy-idle-progress-track">
                        <div class="occupancy-idle-progress-fill" style="width: {min(ociosidade_perc, 100)}%; background: {estilo_idle['barra']}; box-shadow: {estilo_idle['brilho']};"></div>
                    </div>
                    <div class="occupancy-idle-divider"></div>
                    <div class="occupancy-idle-footer">
                        <span class="occupancy-chip"><i class="{icone_ociosidade}" style="color: {estilo_idle['icone']};"></i> Total não utilizado: {formatar_numero(potencial_nao_utilizado, decimais_potencial)} {unidade}</span>
                        <span class="occupancy-chip"><i class="fa-solid fa-circle-minus" style="color: {estilo_idle['icone']};"></i> Não utilizado</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


        def obter_status_ctrb_frete_global(percentual):
            if percentual <= 25:
                return "Dentro da meta", "ctrb-gauge-status-good"
            elif percentual <= 45:
                return "Faixa de atenção", "ctrb-gauge-status-regular"
            return "Acima da meta", "ctrb-gauge-status-bad"

        def calcular_resumo_ctrb_frete_global(df_dados):
            if df_dados.empty:
                return None

            df_temp = df_dados.copy()

            if 'VIAGEM_ID' not in df_temp.columns:
                df_temp['VIAGEM_ID'] = df_temp.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

            resumo_ctrb = df_temp.groupby('VIAGEM_ID').agg(
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'),
                FRETE_TOTAL=('FRETE-R$', 'sum'),
                DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.astype(str).dropna().unique()))
            ).reset_index()

            def calcular_custo_ctrb_card(row):
                custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base

            resumo_ctrb['CUSTO_FINAL'] = resumo_ctrb.apply(calcular_custo_ctrb_card, axis=1)
            frete_total = pd.to_numeric(resumo_ctrb['FRETE_TOTAL'], errors='coerce').fillna(0).sum()
            custo_total = pd.to_numeric(resumo_ctrb['CUSTO_FINAL'], errors='coerce').fillna(0).sum()
            percentual_ponderado = (custo_total / frete_total * 100) if frete_total > 0 else 0

            return {
                'percentual': percentual_ponderado,
                'qtd_viagens': int(len(resumo_ctrb)),
                'custo_total': custo_total,
                'frete_total': frete_total
            }

        def polar_para_cartesiano_global(cx, cy, raio, angulo_graus):
            angulo_rad = math.radians(angulo_graus)
            return (
                cx + (raio * math.cos(angulo_rad)),
                cy - (raio * math.sin(angulo_rad))
            )

        def descrever_arco_svg_global(cx, cy, raio, angulo_inicial, angulo_final):
            x1, y1 = polar_para_cartesiano_global(cx, cy, raio, angulo_inicial)
            x2, y2 = polar_para_cartesiano_global(cx, cy, raio, angulo_final)
            large_arc = 1 if abs(angulo_final - angulo_inicial) > 180 else 0
            return f"M {x1:.2f} {y1:.2f} A {raio:.2f} {raio:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"

        def renderizar_gauge_ctrb_frete_global(percentual, qtd_viagens, filtro_atual):
            percentual_clamp = max(0, min(percentual, 100))
            status_txt, status_cls = obter_status_ctrb_frete_global(percentual_clamp)

            cx, cy, raio = 150, 148, 108
            arco_total = descrever_arco_svg_global(cx, cy, raio, 180, 0)
            arco_externo = descrever_arco_svg_global(cx, cy, raio + 7, 180, 0)
            arco_interno = descrever_arco_svg_global(cx, cy, raio - 17, 180, 0)
            arco_verde = descrever_arco_svg_global(cx, cy, raio, 180, 135)
            arco_amarelo = descrever_arco_svg_global(cx, cy, raio, 135, 99)
            arco_vermelho = descrever_arco_svg_global(cx, cy, raio, 99, 0)

            angulo_ponteiro = 180 - (percentual_clamp / 100 * 180)
            ponta_x, ponta_y = polar_para_cartesiano_global(cx, cy, raio - 21, angulo_ponteiro)
            base_luz_x, base_luz_y = polar_para_cartesiano_global(cx, cy, raio - 33, angulo_ponteiro)
            truck_x, truck_y = polar_para_cartesiano_global(cx, cy, raio + 2, angulo_ponteiro)
            truck_rot = 90 - angulo_ponteiro

            def marcador_tick(valor, extra=0):
                ang = 180 - (valor / 100 * 180)
                x1, y1 = polar_para_cartesiano_global(cx, cy, raio + 6 + extra, ang)
                x2, y2 = polar_para_cartesiano_global(cx, cy, raio - 10, ang)
                lx, ly = polar_para_cartesiano_global(cx, cy, raio + 24 + extra, ang)
                return (x1, y1, x2, y2, lx, ly)

            ticks = {
                0: marcador_tick(0),
                25: marcador_tick(25),
                45: marcador_tick(45),
                100: marcador_tick(100)
            }

            minor_ticks = []
            for valor in [10, 20, 35, 55, 70, 85]:
                ang = 180 - (valor / 100 * 180)
                x1, y1 = polar_para_cartesiano_global(cx, cy, raio + 4, ang)
                x2, y2 = polar_para_cartesiano_global(cx, cy, raio - 4, ang)
                minor_ticks.append((x1, y1, x2, y2))

            status_map = {
                "ctrb-gauge-status-good": ("rgba(6, 78, 59, 0.34)", "rgba(34,197,94,0.72)", "#dcfce7", "#22c55e"),
                "ctrb-gauge-status-regular": ("rgba(120, 53, 15, 0.34)", "rgba(245,158,11,0.72)", "#fef3c7", "#f59e0b"),
                "ctrb-gauge-status-bad": ("rgba(127, 29, 29, 0.34)", "rgba(239,68,68,0.72)", "#fee2e2", "#ef4444"),
            }
            status_bg, status_border, status_fg, status_glow = status_map.get(
                status_cls, ("rgba(6, 78, 59, 0.34)", "rgba(34,197,94,0.72)", "#dcfce7", "#22c55e")
            )
            filtro_label = "Sem faixa selecionada" if filtro_atual == "(Todos)" else filtro_atual

            minor_ticks_html = ''.join(
                f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="rgba(226,232,240,0.16)" stroke-width="1.5" stroke-linecap="round"/>'
                for x1, y1, x2, y2 in minor_ticks
            )
            major_ticks_html = ''.join(
                (
                    f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="rgba(226,232,240,0.42)" stroke-width="2.2" stroke-linecap="round"/>'
                    f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" dominant-baseline="middle" '
                    f'font-size="12" font-weight="800" fill="#ffffff">{valor}%</text>'
                )
                for valor, (x1, y1, x2, y2, lx, ly) in ticks.items()
            )

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8" />
              <style>
                html, body {{
                  margin: 0;
                  padding: 0;
                  background: transparent;
                  overflow: hidden;
                  font-family: 'Segoe UI', 'Inter', sans-serif;
                }}
                .gauge-card {{
                  position: relative;
                  width: 100%;
                  min-height: 320px;
                  border-radius: 24px;
                  overflow: hidden;
                  background:
                    radial-gradient(circle at 50% 115%, rgba(34,197,94,0.09) 0%, rgba(34,197,94,0.00) 42%),
                    radial-gradient(circle at 50% -10%, rgba(96,165,250,0.16) 0%, rgba(96,165,250,0.00) 46%),
                    linear-gradient(180deg, rgba(17,24,39,0.98) 0%, rgba(10,16,30,0.98) 100%);
                  border: 1px solid rgba(59,130,246,0.18);
                  box-shadow: 0 18px 48px rgba(2,6,23,0.52), inset 0 1px 0 rgba(255,255,255,0.05);
                  padding: 12px 12px 18px 12px;
                }}
                .gauge-wrap {{ display:flex; flex-direction:column; align-items:center; justify-content:center; }}
                .gauge-top-pill {{
                  display:inline-flex; align-items:center; gap:8px; margin-top:6px; margin-bottom:8px;
                  padding:4px 12px; border-radius:999px; font-size:10px; font-weight:800; letter-spacing:1.1px;
                  color:#dbeafe; text-transform:uppercase; background:rgba(37,99,235,0.18); border:1px solid rgba(96,165,250,0.24);
                }}
                .gauge-title {{ font-size:20px; font-weight:900; color:#ffffff; margin:4px 0 2px 0; text-align:center; }}
                .gauge-sub {{ font-size:9px; font-weight:800; letter-spacing:2.2px; fill:#bfdbfe; opacity:0.75; text-transform:uppercase; }}
                .gauge-value {{ font-size:34px; font-weight:900; color:#ffffff; line-height:1; margin-top:-10px; text-align:center; }}
                .gauge-status {{
                  display:inline-flex; align-items:center; justify-content:center; margin-top:8px;
                  padding:6px 14px; border-radius:999px; font-size:12px; font-weight:800;
                  background:{status_bg}; border:1px solid {status_border}; color:{status_fg}; box-shadow:0 0 22px rgba(0,0,0,0.18), 0 0 12px {status_glow}22;
                }}
                .gauge-footer {{ display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin-top:12px; }}
                .gauge-chip {{
                  display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border-radius:999px;
                  background:rgba(15,23,42,0.55); border:1px solid rgba(148,163,184,0.16); color:#e2e8f0;
                  font-size:11px; font-weight:700;
                }}
                .gauge-chip i {{ opacity:0.9; }}
              </style>
            </head>
            <body>
              <div class="gauge-card">
                <div class="gauge-wrap">
                  <div class="gauge-top-pill"><i>◉</i><span>Custo de Transferência</span></div>
                  <div class="gauge-title">Monitoramento CTRB/Frete</div>
                  <svg width="300" height="172" viewBox="0 0 300 172" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow:visible; margin-top:2px;">
                    <defs>
                      <linearGradient id="ringBg" x1="0" y1="0" x2="300" y2="0" gradientUnits="userSpaceOnUse">
                        <stop stop-color="rgba(148,163,184,0.18)"/>
                        <stop offset="1" stop-color="rgba(148,163,184,0.05)"/>
                      </linearGradient>
                      <linearGradient id="greenArc" x1="42" y1="160" x2="132" y2="70" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#22c55e"/>
                        <stop offset="1" stop-color="#4ade80"/>
                      </linearGradient>
                      <linearGradient id="yellowArc" x1="110" y1="58" x2="196" y2="58" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#f59e0b"/>
                        <stop offset="1" stop-color="#facc15"/>
                      </linearGradient>
                      <linearGradient id="redArc" x1="168" y1="72" x2="258" y2="160" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#ef4444"/>
                        <stop offset="1" stop-color="#f87171"/>
                      </linearGradient>
                      <radialGradient id="hubGrad" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({cx} {cy}) rotate(90) scale(16)">
                        <stop stop-color="#ffffff"/>
                        <stop offset="0.45" stop-color="#dbeafe"/>
                        <stop offset="1" stop-color="#334155"/>
                      </radialGradient>
                    </defs>
                    <path d="{arco_total}" stroke="url(#ringBg)" stroke-width="26" stroke-linecap="round" opacity="0.28"/>
                    <path d="{arco_externo}" stroke="rgba(255,255,255,0.06)" stroke-width="2" stroke-linecap="round"/>
                    <path d="{arco_interno}" stroke="rgba(15,23,42,0.85)" stroke-width="2" stroke-linecap="round"/>
                    <path d="{arco_verde}" stroke="url(#greenArc)" stroke-width="22" stroke-linecap="round" filter="drop-shadow(0 0 8px rgba(34,197,94,0.35))"/>
                    <path d="{arco_amarelo}" stroke="url(#yellowArc)" stroke-width="22" stroke-linecap="round" filter="drop-shadow(0 0 8px rgba(245,158,11,0.32))"/>
                    <path d="{arco_vermelho}" stroke="url(#redArc)" stroke-width="22" stroke-linecap="round" filter="drop-shadow(0 0 8px rgba(239,68,68,0.32))"/>
                    {minor_ticks_html}
                    {major_ticks_html}
                    <text x="150" y="114" text-anchor="middle" class="gauge-sub">Performance Operacional</text>
                    <g transform="translate({truck_x:.2f} {truck_y:.2f}) rotate({truck_rot:.2f})">
                      <rect x="-10" y="-6" rx="2" ry="2" width="14" height="8" fill="rgba(191,219,254,0.82)" opacity="0.16"/>
                      <path d="M-10 0 H2 L6 -4 H12 V4 H-10 Z" fill="rgba(226,232,240,0.52)" opacity="0.18"/>
                    </g>
                    <line x1="{cx}" y1="{cy}" x2="{ponta_x:.2f}" y2="{ponta_y:.2f}" stroke="#e2e8f0" stroke-width="4.2" stroke-linecap="round" filter="drop-shadow(0 0 4px rgba(255,255,255,0.25))"/>
                    <circle cx="{base_luz_x:.2f}" cy="{base_luz_y:.2f}" r="2.5" fill="rgba(148,163,184,0.35)"/>
                    <circle cx="{cx}" cy="{cy}" r="12" fill="url(#hubGrad)" stroke="rgba(255,255,255,0.22)" stroke-width="2"/>
                    <circle cx="{cx}" cy="{cy}" r="4" fill="#ffffff" opacity="0.92"/>
                  </svg>
                  <div class="gauge-value">{percentual_clamp:.0f}%</div>
                  <div class="gauge-status">{status_txt}</div>
                  <div class="gauge-footer">
                    <div class="gauge-chip">● Filtro: {filtro_label}</div>
                    <div class="gauge-chip">◉ Base: {qtd_viagens} viagem(ns)</div>
                  </div>
                </div>
              </div>
            </body>
            </html>
            """

            components.html(html, height=335)

        # ===============================================
        # LÓGICA DE OCUPAÇÃO (sempre no layout padrão, inclusive em Viagem Específica)
        # ===============================================
        if True:

            # --- 1. FUNÇÕES DE LÓGICA DE COR (COM AJUSTE) ---
            def obter_cor_ocupacao(percentual):
                if percentual < 50: return "linear-gradient(90deg, #dc2626 0%, #ef4444 100%)"
                elif percentual < 80: return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"
                else: return "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)"

            def obter_cor_ociosidade(percentual):
                return "linear-gradient(90deg, #f59e0b 0%, #facc15 100%)"

            # CÓDIGO FINAL E CORRIGIDO (VERSÃO 5)

            def calcular_dados_ocupacao_geral(df_dados):
                if df_dados.empty:
                    return None

                dados = {}
                if 'VIAGEM_UNICA_ID' not in df_dados.columns:
                    df_dados['VIAGEM_UNICA_ID'] = df_dados.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).ngroup()
                
                # Garante que as colunas são numéricas
                df_dados['M3'] = pd.to_numeric(df_dados['M3'], errors='coerce').fillna(0)
                df_dados = garantir_coluna_peso_calculo(df_dados)
                df_dados['Peso Cálculo (KG)'] = pd.to_numeric(df_dados['Peso Cálculo (KG)'], errors='coerce').fillna(0)

                # DataFrame com cada viagem única no período
                viagens_unicas = df_dados.drop_duplicates(subset=['VIAGEM_UNICA_ID']).copy()

                # --- LÓGICA DE CAPACIDADE DE PESO ---
                capacidades_padrao_veiculo_sozinho = {'TRUCK': 16000, 'TOCO': 10000, '3/4 - CAMINHAO PEQUE': 4500}
                def get_capacidade_viagem_peso(row):
                    if pd.notna(row['PLACA_CARRETA']) and row['PLACA_CARRETA'] != '' and row['CAPACIDADE_KG'] > 0:
                        return row['CAPACIDADE_KG']
                    if row['CAPAC_CAVALO'] > 0:
                        return row['CAPAC_CAVALO']
                    tipo_veiculo = obter_tipo_veiculo_base(row)
                    return capacidades_padrao_veiculo_sozinho.get(tipo_veiculo, 0)
                
                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)
                
                # Soma a capacidade de peso de cada viagem
                dados['cap_total_peso'] = viagens_unicas['CAPACIDADE_PESO_VIAGEM'].sum()
                # Soma o peso total transportado em todas as viagens
                dados['total_peso'] = somar_peso_calculo(df_dados)
                
                # --- LÓGICA DE CAPACIDADE DE VOLUME ---
                capacidades_volume_por_tipo = {'TRUCK': 75, 'CAVALO': 110, 'TOCO': 55, '3/4 - CAMINHAO PEQUE': 40, 'PADRAO': 80}
                viagens_unicas['CAP_VOL_VIAGEM'] = viagens_unicas.get('TIPO_CAVALO_ORIGINAL', viagens_unicas['TIPO_CAVALO']).map(capacidades_volume_por_tipo).fillna(80)
                
                # Soma a capacidade de volume de cada viagem
                dados['cap_total_volume'] = viagens_unicas['CAP_VOL_VIAGEM'].sum()
                # Soma o volume total transportado em todas as viagens
                dados['total_volume'] = df_dados['M3'].sum()

                # --- CÁLCULO DOS PERCENTUAIS DE OCUPAÇÃO (MÉDIA DO PERÍODO) ---
                # Agora, o percentual é a divisão do total transportado pela capacidade total ofertada no período.
                # Isso representa a OCUPAÇÃO MÉDIA de todas as viagens.
                dados['ocup_peso_perc'] = (dados['total_peso'] / dados['cap_total_peso'] * 100) if dados['cap_total_peso'] > 0 else 0
                dados['ociosidade_peso_perc'] = 100 - dados['ocup_peso_perc']
                dados['potencial_nao_utilizado_kg'] = max(0, dados['cap_total_peso'] - dados['total_peso'])
                
                dados['ocup_volume_perc'] = (dados['total_volume'] / dados['cap_total_volume'] * 100) if dados['cap_total_volume'] > 0 else 0
                dados['ociosidade_volume_perc'] = 100 - dados['ocup_volume_perc']
                dados['potencial_nao_utilizado_m3'] = max(0, dados['cap_total_volume'] - dados['total_volume'])
                
                return dados
            # --- 3. FUNÇÕES AUXILIARES E RENDERIZAÇÃO DOS CARDS ---
            def obter_status_utilizacao(percentual):
                if percentual < 50:
                    return "Baixa ocupação", "occupancy-status-util-low"
                elif percentual <= 80:
                    return "Faixa ideal", "occupancy-status-util-ideal"
                return "Alta utilização", "occupancy-status-util-high"


            def obter_status_ociosidade(percentual):
                if percentual < 20:
                    return "Baixa ociosidade", "occupancy-status-idle-low"
                elif percentual <= 50:
                    return "Faixa ideal", "occupancy-status-idle-ideal"
                return "Alta ociosidade", "occupancy-status-idle-high"


            def obter_estilo_utilizacao(percentual):
                if percentual < 50:
                    return {
                        "barra": "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)",
                        "brilho": "0 0 18px rgba(245, 158, 11, 0.22)",
                        "percentual": "#fde68a"
                    }
                elif percentual <= 80:
                    return {
                        "barra": "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)",
                        "brilho": "0 0 18px rgba(96, 165, 250, 0.20)",
                        "percentual": "#dbeafe"
                    }
                return {
                    "barra": "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)",
                    "brilho": "0 0 18px rgba(34, 197, 94, 0.20)",
                    "percentual": "#bbf7d0"
                }


            def obter_estilo_ociosidade(percentual):
                if percentual < 20:
                    return {
                        "barra": "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)",
                        "brilho": "0 0 18px rgba(34, 197, 94, 0.20)",
                        "percentual": "#bbf7d0",
                        "icone": "#4ade80"
                    }
                elif percentual <= 50:
                    return {
                        "barra": "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)",
                        "brilho": "0 0 18px rgba(96, 165, 250, 0.20)",
                        "percentual": "#dbeafe",
                        "icone": "#60a5fa"
                    }
                return {
                    "barra": "linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)",
                    "brilho": "0 0 18px rgba(245, 158, 11, 0.22)",
                    "percentual": "#fde68a",
                    "icone": "#fbbf24"
                }


            def obter_status_ctrb_frete(percentual):
                if percentual <= 25:
                    return "Dentro da meta", "ctrb-gauge-status-good"
                elif percentual <= 45:
                    return "Faixa de atenção", "ctrb-gauge-status-regular"
                return "Acima da meta", "ctrb-gauge-status-bad"

            def calcular_resumo_ctrb_frete(df_dados):
                if df_dados.empty:
                    return None

                df_temp = df_dados.copy()

                if 'VIAGEM_ID' not in df_temp.columns:
                    df_temp['VIAGEM_ID'] = df_temp.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

                resumo_ctrb = df_temp.groupby('VIAGEM_ID').agg(
                    PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                    CUSTO_OS=('OS-R$', 'max'),
                    CUSTO_CTRB=('CTRB-R$', 'max'),
                    FRETE_TOTAL=('FRETE-R$', 'sum'),
                    DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.astype(str).dropna().unique()))
                ).reset_index()

                def calcular_custo_ctrb_card(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    destinos_str = str(row.get('DESTINOS', '')).upper()
                    if 'GYN' in destinos_str or 'SPO' in destinos_str:
                        return custo_base / 2
                    return custo_base

                resumo_ctrb['CUSTO_FINAL'] = resumo_ctrb.apply(calcular_custo_ctrb_card, axis=1)
                frete_total = pd.to_numeric(resumo_ctrb['FRETE_TOTAL'], errors='coerce').fillna(0).sum()
                custo_total = pd.to_numeric(resumo_ctrb['CUSTO_FINAL'], errors='coerce').fillna(0).sum()

                percentual_ponderado = (custo_total / frete_total * 100) if frete_total > 0 else 0

                return {
                    'percentual': percentual_ponderado,
                    'qtd_viagens': int(len(resumo_ctrb)),
                    'custo_total': custo_total,
                    'frete_total': frete_total
                }

            def polar_para_cartesiano(cx, cy, raio, angulo_graus):
                angulo_rad = math.radians(angulo_graus)
                return (
                    cx + (raio * math.cos(angulo_rad)),
                    cy - (raio * math.sin(angulo_rad))
                )

            def descrever_arco_svg(cx, cy, raio, angulo_inicial, angulo_final):
                x1, y1 = polar_para_cartesiano(cx, cy, raio, angulo_inicial)
                x2, y2 = polar_para_cartesiano(cx, cy, raio, angulo_final)
                large_arc = 1 if abs(angulo_final - angulo_inicial) > 180 else 0
                return f"M {x1:.2f} {y1:.2f} A {raio:.2f} {raio:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"

            def renderizar_gauge_ctrb_frete_global(percentual, qtd_viagens, filtro_atual):
                percentual_clamp = max(0, min(percentual, 100))
                status_txt, status_cls = obter_status_ctrb_frete(percentual_clamp)

                # AUMENTADO
                cx, cy, raio = 150, 148, 108
                arco_total = descrever_arco_svg(cx, cy, raio, 180, 0)
                arco_externo = descrever_arco_svg(cx, cy, raio + 7, 180, 0)
                arco_interno = descrever_arco_svg(cx, cy, raio - 17, 180, 0)
                arco_verde = descrever_arco_svg(cx, cy, raio, 180, 135)
                arco_amarelo = descrever_arco_svg(cx, cy, raio, 135, 99)
                arco_vermelho = descrever_arco_svg(cx, cy, raio, 99, 0)

                angulo_ponteiro = 180 - (percentual_clamp / 100 * 180)
                ponta_x, ponta_y = polar_para_cartesiano(cx, cy, raio - 21, angulo_ponteiro)
                base_luz_x, base_luz_y = polar_para_cartesiano(cx, cy, raio - 33, angulo_ponteiro)
                truck_x, truck_y = polar_para_cartesiano(cx, cy, raio + 2, angulo_ponteiro)
                truck_rot = 90 - angulo_ponteiro

                def marcador_tick(valor, extra=0):
                    ang = 180 - (valor / 100 * 180)
                    x1, y1 = polar_para_cartesiano(cx, cy, raio + 6 + extra, ang)
                    x2, y2 = polar_para_cartesiano(cx, cy, raio - 10, ang)
                    lx, ly = polar_para_cartesiano(cx, cy, raio + 24 + extra, ang)
                    return (x1, y1, x2, y2, lx, ly)

                ticks = {
                    0: marcador_tick(0),
                    25: marcador_tick(25),
                    45: marcador_tick(45),
                    100: marcador_tick(100)
                }

                minor_ticks = []
                for valor in [10, 20, 35, 55, 70, 85]:
                    ang = 180 - (valor / 100 * 180)
                    x1, y1 = polar_para_cartesiano(cx, cy, raio + 4, ang)
                    x2, y2 = polar_para_cartesiano(cx, cy, raio - 4, ang)
                    minor_ticks.append((x1, y1, x2, y2))

                status_map = {
                    "ctrb-gauge-status-good": ("rgba(6, 78, 59, 0.34)", "rgba(34,197,94,0.72)", "#dcfce7", "#22c55e"),
                    "ctrb-gauge-status-regular": ("rgba(120, 53, 15, 0.34)", "rgba(245,158,11,0.72)", "#fef3c7", "#f59e0b"),
                    "ctrb-gauge-status-bad": ("rgba(127, 29, 29, 0.34)", "rgba(239,68,68,0.72)", "#fee2e2", "#ef4444"),
                }
                status_bg, status_border, status_fg, status_glow = status_map.get(
                    status_cls, ("rgba(6, 78, 59, 0.34)", "rgba(34,197,94,0.72)", "#dcfce7", "#22c55e")
                )
                filtro_label = "Sem faixa selecionada" if filtro_atual == "(Todos)" else filtro_atual

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="utf-8" />
                  <style>
                    html, body {{
                      margin: 0;
                      padding: 0;
                      background: transparent;
                      font-family: 'Segoe UI', 'Inter', sans-serif;
                    }}
                    .g-wrap {{
                      width: 100%;
                      display: flex;
                      justify-content: center;
                      align-items: flex-start;
                    }}
                    .g-card {{
                      width: 100%;
                      max-width: 590px;
                      min-height: 430px;
                      border-radius: 24px;
                      padding: 16px 18px 22px 18px;
                      box-sizing: border-box;
                      overflow: hidden;
                      position: relative;
                      background:
                        radial-gradient(circle at 50% 0%, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.00) 34%),
                        radial-gradient(circle at 8% 10%, rgba(59,130,246,0.20) 0%, rgba(59,130,246,0.00) 28%),
                        radial-gradient(circle at 92% 6%, rgba(16,185,129,0.18) 0%, rgba(16,185,129,0.00) 26%),
                        linear-gradient(180deg, #122338 0%, #0b1730 48%, #08111f 100%);
                      border: 1px solid rgba(255,255,255,0.08);
                      box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 22px 40px rgba(2,6,23,0.34);
                    }}
                    .g-card::before {{
                      content: '';
                      position: absolute;
                      inset: 0;
                      background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.00) 24%);
                      pointer-events: none;
                    }}
                    .g-header {{
                      position: relative;
                      z-index: 2;
                      text-align: center;
                      margin-bottom: 2px;
                    }}
                    .g-kicker {{
                      display: inline-flex;
                      align-items: center;
                      gap: 10px;
                      padding: 6px 13px;
                      border-radius: 999px;
                      background: rgba(15,23,42,0.48);
                      border: 1px solid rgba(148,163,184,0.16);
                      color: #c7d2fe;
                      font-size: 10px;
                      font-weight: 900;
                      letter-spacing: 1px;
                      text-transform: uppercase;
                    }}
                    .g-title {{
                      margin-top: 10px;
                      color: #f8fafc;
                      font-weight: 900;
                      font-size: 21px;
                      line-height: 1.15;
                      letter-spacing: 0.2px;
                      text-shadow: 0 2px 14px rgba(0,0,0,0.30);
                    }}
                    .g-title i {{
                      font-style: normal;
                      margin-right: 10px;
                      filter: drop-shadow(0 0 8px rgba(56,189,248,0.24));
                    }}
                    .g-svg {{
                      width: 100%;
                      display: flex;
                      justify-content: center;
                      margin-top: 2px;
                      position: relative;
                      z-index: 2;
                    }}
                    svg {{
                      width: 352px;
                      height: 204px;
                      overflow: visible;
                    }}
                    .tick-major {{
                      stroke: rgba(255,255,255,0.32);
                      stroke-width: 1.8;
                      stroke-linecap: round;
                    }}
                    .tick-minor {{
                      stroke: rgba(255,255,255,0.18);
                      stroke-width: 1.05;
                      stroke-linecap: round;
                    }}
                    .tick-label {{
                      fill: #f8fafc;
                      font-size: 10px;
                      font-weight: 900;
                      letter-spacing: 0.3px;
                    }}
                    .meta-label {{
                      fill: rgba(226,232,240,0.72);
                      font-size: 8px;
                      font-weight: 800;
                      letter-spacing: 0.9px;
                      text-transform: uppercase;
                    }}
                    .g-value {{
                      text-align: center;
                      margin-top: -2px;
                      color: #ffffff;
                      font-size: 44px;
                      font-weight: 900;
                      line-height: 1;
                      letter-spacing: -1px;
                      position: relative;
                      z-index: 2;
                      text-shadow: 0 4px 18px rgba(0,0,0,0.42), 0 0 18px rgba(56,189,248,0.14);
                    }}
                    .g-caption {{
                      text-align: center;
                      color: rgba(191,219,254,0.92);
                      font-size: 10px;
                      font-weight: 800;
                      letter-spacing: 1px;
                      text-transform: uppercase;
                      position: relative;
                      z-index: 2;
                      margin-top: 6px;
                    }}
                    .g-status {{
                      margin: 14px auto 12px auto;
                      width: fit-content;
                      padding: 9px 20px;
                      border-radius: 999px;
                      background: {status_bg};
                      border: 1px solid {status_border};
                      color: {status_fg};
                      font-size: 13px;
                      font-weight: 900;
                      position: relative;
                      z-index: 2;
                      box-shadow: inset 0 1px 0 rgba(255,255,255,0.10), 0 0 18px rgba(0,0,0,0.12);
                    }}
                    .g-foot {{
                      display: flex;
                      flex-wrap: wrap;
                      justify-content: center;
                      gap: 12px;
                      margin-top: 4px;
                      padding-bottom: 2px;
                      position: relative;
                      z-index: 2;
                    }}
                    .g-chip {{
                      display: inline-flex;
                      align-items: center;
                      gap: 7px;
                      padding: 8px 13px;
                      border-radius: 999px;
                      background: rgba(15,23,42,0.42);
                      border: 1px solid rgba(255,255,255,0.10);
                      color: #e2e8f0;
                      font-size: 11px;
                      font-weight: 800;
                      line-height: 1;
                      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
                    }}
                    .g-chip i {{
                      font-style: normal;
                      font-size: 12px;
                    }}
                    .g-chip.filter i {{ color: #fbbf24; }}
                    .g-chip.base i {{ color: #60a5fa; }}
                  </style>
                </head>
                <body>
                  <div class="g-wrap">
                    <div class="g-card">
                      <div class="g-header">
                        <div class="g-kicker">⚙️ Custo de Transferência</div>
                        <div class="g-title">Monitoramento CTRB/Frete</div>
                      </div>
                      <div class="g-svg">
                        <svg viewBox="0 0 300 184" xmlns="http://www.w3.org/2000/svg">
                          <defs>
                            <linearGradient id="metalRing" x1="0%" y1="0%" x2="100%" y2="100%">
                              <stop offset="0%" stop-color="#dbe4ee" stop-opacity="0.40"/>
                              <stop offset="24%" stop-color="#6b7b92" stop-opacity="0.28"/>
                              <stop offset="50%" stop-color="#1f2937" stop-opacity="0.16"/>
                              <stop offset="78%" stop-color="#95a4ba" stop-opacity="0.28"/>
                              <stop offset="100%" stop-color="#f8fafc" stop-opacity="0.38"/>
                            </linearGradient>
                            <linearGradient id="needleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" stop-color="#dbeafe" stop-opacity="0.56"/>
                              <stop offset="68%" stop-color="#ffffff" stop-opacity="0.96"/>
                              <stop offset="100%" stop-color="#ffffff" stop-opacity="1"/>
                            </linearGradient>
                            <radialGradient id="hubGrad" cx="50%" cy="38%" r="62%">
                              <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.96"/>
                              <stop offset="28%" stop-color="#cbd5e1" stop-opacity="0.88"/>
                              <stop offset="58%" stop-color="#334155" stop-opacity="0.95"/>
                              <stop offset="100%" stop-color="#020617" stop-opacity="1"/>
                            </radialGradient>
                            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                              <feGaussianBlur stdDeviation="3.5" result="blur"/>
                              <feMerge>
                                <feMergeNode in="blur"/>
                                <feMergeNode in="SourceGraphic"/>
                              </feMerge>
                            </filter>
                            <filter id="softShadow" x="-50%" y="-50%" width="200%" height="200%">
                              <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#020617" flood-opacity="0.60"/>
                            </filter>
                          </defs>

                          <ellipse cx="150" cy="144" rx="108" ry="17" fill="rgba(2,6,23,0.38)"/>
                          <path d="{arco_externo}" fill="none" stroke="url(#metalRing)" stroke-width="4" stroke-linecap="round" opacity="0.86"/>
                          <path d="{arco_total}" fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="22" stroke-linecap="round"/>
                          <path d="{arco_interno}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="3" stroke-linecap="round"/>
                          <path d="{arco_verde}" fill="none" stroke="#22c55e" stroke-width="18" stroke-linecap="round" filter="url(#glow)"/>
                          <path d="{arco_amarelo}" fill="none" stroke="#f59e0b" stroke-width="18" stroke-linecap="round" filter="url(#glow)"/>
                          <path d="{arco_vermelho}" fill="none" stroke="#ef4444" stroke-width="18" stroke-linecap="round" filter="url(#glow)"/>

                          {''.join([f'<line class="tick-minor" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>' for x1, y1, x2, y2 in minor_ticks])}
                          <line class="tick-major" x1="{ticks[0][0]:.2f}" y1="{ticks[0][1]:.2f}" x2="{ticks[0][2]:.2f}" y2="{ticks[0][3]:.2f}"/>
                          <line class="tick-major" x1="{ticks[25][0]:.2f}" y1="{ticks[25][1]:.2f}" x2="{ticks[25][2]:.2f}" y2="{ticks[25][3]:.2f}"/>
                          <line class="tick-major" x1="{ticks[45][0]:.2f}" y1="{ticks[45][1]:.2f}" x2="{ticks[45][2]:.2f}" y2="{ticks[45][3]:.2f}"/>
                          <line class="tick-major" x1="{ticks[100][0]:.2f}" y1="{ticks[100][1]:.2f}" x2="{ticks[100][2]:.2f}" y2="{ticks[100][3]:.2f}"/>

                          <text class="tick-label" x="{ticks[0][4]:.2f}" y="{ticks[0][5] + 4:.2f}" text-anchor="middle">0%</text>
                          <text class="tick-label" x="{ticks[25][4]:.2f}" y="{ticks[25][5] - 2:.2f}" text-anchor="middle">25%</text>
                          <text class="tick-label" x="{ticks[45][4]:.2f}" y="{ticks[45][5] - 2:.2f}" text-anchor="middle">45%</text>
                          <text class="tick-label" x="{ticks[100][4]:.2f}" y="{ticks[100][5] + 4:.2f}" text-anchor="middle">100%</text>

                          <line x1="{cx}" y1="{cy}" x2="{base_luz_x:.2f}" y2="{base_luz_y:.2f}" stroke="rgba(56,189,248,0.16)" stroke-width="8" stroke-linecap="round"/>
                          <line x1="{cx}" y1="{cy}" x2="{ponta_x:.2f}" y2="{ponta_y:.2f}" stroke="url(#needleGrad)" stroke-width="4.8" stroke-linecap="round" filter="url(#softShadow)"/>
                          <circle cx="{cx}" cy="{cy}" r="14" fill="url(#hubGrad)" stroke="rgba(248,250,252,0.34)" stroke-width="1.8"/>
                          <circle cx="{cx}" cy="{cy}" r="5" fill="#f8fafc"/>


                          <text class="meta-label" x="150" y="106" text-anchor="middle">PERFORMANCE OPERACIONAL</text>
                        </svg>
                      </div>
                      <div class="g-value">{percentual_clamp:.0f}%</div>
                      <div class="g-status">{status_txt}</div>
                      <div class="g-foot">
                        <span class="g-chip filter"><i>⛃</i> Filtro: {filtro_label}</span>
                        <span class="g-chip base"><i>◉</i> Base: {qtd_viagens} viagem(ns)</span>
                      </div>
                    </div>
                  </div>
                </body>
                </html>
                """

                components.html(html, height=520, scrolling=False)


            def renderizar_card_ocupacao_moderno(
                titulo,
                ocup_perc,
                total_valor,
                cap_total,
                unidade,
                ociosidade_perc,
                potencial_nao_utilizado,
                icone_topo,
                icone_ociosidade,
                titulo_ociosidade,
                tema="peso"
            ):
                status_txt, status_cls = obter_status_utilizacao(ocup_perc)
                status_txt_idle, status_cls_idle = obter_status_ociosidade(ociosidade_perc)
                estilo_ocup = obter_estilo_utilizacao(ocup_perc)
                estilo_idle = obter_estilo_ociosidade(ociosidade_perc)
                classe_tema = "occupancy-theme-peso" if tema == "peso" else "occupancy-theme-volume"
                decimais_total = 3 if unidade == 'M³' else 0
                decimais_cap = 2 if unidade == 'M³' else 0
                decimais_potencial = 2 if unidade == 'M³' else 0

                st.markdown(f"""
                    <div class="occupancy-main-card {classe_tema}">
                        <div class="occupancy-main-header">
                            <div class="occupancy-title-wrap">
                                <div class="occupancy-card-title">
                                    <i class="fa-solid {icone_topo}"></i>
                                    <span>{titulo}</span>
                                </div>
                                <span class="occupancy-status-pill {status_cls}">{status_txt}</span>
                            </div>
                            <div class="occupancy-percent" style="color: {estilo_ocup['percentual']};">{ocup_perc:.0f}%</div>
                        </div>
                        <div class="occupancy-progress-track">
                            <div class="occupancy-progress-fill" style="width: {min(ocup_perc, 100)}%; background: {estilo_ocup['barra']}; box-shadow: {estilo_ocup['brilho']};"></div>
                        </div>
                        <div class="occupancy-divider"></div>
                        <div class="occupancy-chip-row">
                            <span class="occupancy-chip"><i class="fa-solid fa-cubes-stacked"></i> Total: {formatar_numero(total_valor, decimais_total)} {unidade}</span>
                            <span class="occupancy-chip"><i class="fa-solid fa-database"></i> Capacidade: {formatar_numero(cap_total, decimais_cap)} {unidade}</span>
                        </div>
                    </div>
                    <div class="occupancy-idle-card">
                        <div class="occupancy-idle-header">
                            <div class="occupancy-idle-title-wrap">
                                <div class="occupancy-idle-title">
                                    <i class="{icone_ociosidade}" style="color: {estilo_idle['icone']};"></i>
                                    <span>{titulo_ociosidade}</span>
                                </div>
                                <span class="occupancy-status-pill {status_cls_idle}">{status_txt_idle}</span>
                            </div>
                            <div class="occupancy-idle-percent" style="color: {estilo_idle['percentual']};">{ociosidade_perc:.0f}%</div>
                        </div>
                        <div class="occupancy-idle-progress-track">
                            <div class="occupancy-idle-progress-fill" style="width: {min(ociosidade_perc, 100)}%; background: {estilo_idle['barra']}; box-shadow: {estilo_idle['brilho']};"></div>
                        </div>
                        <div class="occupancy-idle-divider"></div>
                        <div class="occupancy-idle-footer">
                            <span class="occupancy-chip"><i class="{icone_ociosidade}" style="color: {estilo_idle['icone']};"></i> Total não utilizado: {formatar_numero(potencial_nao_utilizado, decimais_potencial)} {unidade}</span>
                            <span class="occupancy-chip"><i class="fa-solid fa-circle-minus" style="color: {estilo_idle['icone']};"></i> Não utilizado</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # --- 4. RENDERIZAÇÃO FINAL ---

            resumo_ctrb_card = calcular_resumo_ctrb_frete_global(df_para_analise)
            dados_agregados = calcular_dados_ocupacao_geral(df_para_analise)

            total_peso_calculo_ind = somar_peso_calculo(df_para_analise)
            if total_peso_calculo_ind == 0:
                total_peso_calculo_ind = dados_agregados.get('total_peso', 0) if dados_agregados else 0

            total_peso_ind = total_peso_calculo_ind
            total_cubagem_ind = dados_agregados.get('total_volume', 0) if dados_agregados else 0
            total_ctrb_ind = resumo_ctrb_card.get('custo_total', 0) if resumo_ctrb_card else 0
            total_frete_ind = resumo_ctrb_card.get('frete_total', 0) if resumo_ctrb_card else 0
            total_icms_ind = pd.to_numeric(df_para_analise.get('ICMS-R$', pd.Series(dtype='float64')), errors='coerce').fillna(0).sum()
            total_mercadoria_ind = pd.to_numeric(df_para_analise.get('MERCADORIA-R$', pd.Series(dtype='float64')), errors='coerce').fillna(0).sum()
            total_qtd_ctrc_ind = pd.to_numeric(df_para_analise.get('QTDE_CTRC', pd.Series(dtype='float64')), errors='coerce').fillna(0).sum()
            total_volumes_ind = pd.to_numeric(df_para_analise.get('VOLUMES', pd.Series(dtype='float64')), errors='coerce').fillna(0).sum()
            total_viagens_ind = df_para_analise.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroups if not df_para_analise.empty else 0
            ocupacao_peso_ind = dados_agregados.get('ocup_peso_perc', 0) if dados_agregados else 0
            ctrb_frete_ind = (total_ctrb_ind / total_frete_ind * 100) if total_frete_ind > 0 else 0

            def formatar_resumo_mil(valor, decimais=1):
                valor = float(valor or 0)
                valor_mil = valor / 1000
                if decimais == 0:
                    return f"R$ {formatar_numero(valor_mil, 0)} mil"
                fator = 10 ** decimais
                valor_mil = math.floor(valor_mil * fator) / fator if valor_mil >= 0 else math.ceil(valor_mil * fator) / fator
                return f"R$ {formatar_numero(valor_mil, decimais)} mil"

            badge_ops_viagens = f"{formatar_numero(total_viagens_ind)} viagens"
            badge_ops_distancia = f"Distância: {formatar_numero(distancia_estimada_km, 0)} km"
            badge_fin_frete = f"Frete: {formatar_resumo_mil(total_frete_ind, 0)}"
            badge_fin_custo_km = f"Custo / KM: {formatar_moeda(valor_por_km)}"

            def preparar_dados_grafico_ocupacao(df_dados):
                if df_dados.empty:
                    return pd.DataFrame()

                df_chart = df_dados.copy()

                if 'CATEGORIA_VIAGEM' not in df_chart.columns:
                    df_chart['CATEGORIA_VIAGEM'] = df_chart.apply(definir_categoria_viagem, axis=1)

                if 'VIAGEM_UNICA_ID' not in df_chart.columns:
                    df_chart['VIAGEM_UNICA_ID'] = df_chart.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).ngroup()

                df_chart = garantir_coluna_peso_calculo(df_chart)
                df_chart['Peso Cálculo (KG)'] = pd.to_numeric(df_chart['Peso Cálculo (KG)'], errors='coerce').fillna(0)
                df_chart['M3'] = pd.to_numeric(df_chart.get('M3', 0), errors='coerce').fillna(0)

                viagens_unicas = df_chart.drop_duplicates(subset=['VIAGEM_UNICA_ID']).copy()
                capacidades_padrao_veiculo_sozinho = {
                    'TRUCK': 16000,
                    'TOCO': 10000,
                    '3/4 - CAMINHAO PEQUE': 4500
                }

                def get_capacidade_viagem_peso(row):
                    if pd.notna(row['PLACA_CARRETA']) and row['PLACA_CARRETA'] != '' and row['CAPACIDADE_KG'] > 0:
                        return row['CAPACIDADE_KG']
                    if row['CAPAC_CAVALO'] > 0:
                        return row['CAPAC_CAVALO']
                    tipo_veiculo = obter_tipo_veiculo_base(row)
                    return capacidades_padrao_veiculo_sozinho.get(tipo_veiculo, 0)

                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)

                carga_tipo = (
                    df_chart.groupby('CATEGORIA_VIAGEM', dropna=False)['Peso Cálculo (KG)']
                    .sum()
                    .reset_index(name='CARGA_KG')
                )
                capacidade_tipo = (
                    viagens_unicas.groupby('CATEGORIA_VIAGEM', dropna=False)['CAPACIDADE_PESO_VIAGEM']
                    .sum()
                    .reset_index(name='CAPACIDADE_KG')
                )
                viagens_tipo = (
                    viagens_unicas.groupby('CATEGORIA_VIAGEM', dropna=False)['VIAGEM_UNICA_ID']
                    .nunique()
                    .reset_index(name='TOTAL_VIAGENS')
                )

                resumo_tipo = carga_tipo.merge(capacidade_tipo, on='CATEGORIA_VIAGEM', how='outer')
                resumo_tipo = resumo_tipo.merge(viagens_tipo, on='CATEGORIA_VIAGEM', how='left').fillna(0)
                resumo_tipo['TIPO_VEICULO'] = resumo_tipo['CATEGORIA_VIAGEM'].fillna('INDEFINIDO').replace('', 'INDEFINIDO')
                resumo_tipo = resumo_tipo[resumo_tipo['CARGA_KG'] > 0].copy()

                if resumo_tipo.empty:
                    return resumo_tipo

                total_carga = resumo_tipo['CARGA_KG'].sum()
                resumo_tipo['PARTICIPACAO_PERC'] = (resumo_tipo['CARGA_KG'] / total_carga * 100).round(2)
                resumo_tipo['OCUPACAO_PERC'] = np.where(
                    resumo_tipo['CAPACIDADE_KG'] > 0,
                    resumo_tipo['CARGA_KG'] / resumo_tipo['CAPACIDADE_KG'] * 100,
                    0
                )

                ordem_prioridade = {
                    'TRUCK': 0,
                    'BI-TRUCK': 1,
                    'CARRETA': 2,
                    'TOCO': 3,
                    '3/4 - CAMINHAO PEQUE': 4,
                    'INDEFINIDO': 98
                }

                resumo_tipo['ORDEM_TIPO'] = resumo_tipo['TIPO_VEICULO'].map(ordem_prioridade).fillna(99)
                resumo_tipo = resumo_tipo.sort_values(['ORDEM_TIPO', 'PARTICIPACAO_PERC'], ascending=[True, False]).reset_index(drop=True)
                resumo_tipo['TIPO_LABEL'] = resumo_tipo['TIPO_VEICULO'].replace({'3/4 - CAMINHAO PEQUE': 'TRUCK'})

                paleta_cores = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ef4444']
                resumo_tipo['COR'] = [paleta_cores[i % len(paleta_cores)] for i in range(len(resumo_tipo))]
                resumo_tipo['CARGA_TON'] = resumo_tipo['CARGA_KG'] / 1000
                resumo_tipo['TOTAL_VIAGENS'] = resumo_tipo['TOTAL_VIAGENS'].astype(int)
                return resumo_tipo

            def preparar_faixas_ocupacao_viagens(df_dados):
                if df_dados.empty:
                    return None

                df_faixas = df_dados.copy()

                if 'CATEGORIA_VIAGEM' not in df_faixas.columns:
                    df_faixas['CATEGORIA_VIAGEM'] = df_faixas.apply(definir_categoria_viagem, axis=1)

                if 'VIAGEM_UNICA_ID' not in df_faixas.columns:
                    df_faixas['VIAGEM_UNICA_ID'] = df_faixas.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).ngroup()

                df_faixas = garantir_coluna_peso_calculo(df_faixas)
                df_faixas['Peso Cálculo (KG)'] = pd.to_numeric(df_faixas['Peso Cálculo (KG)'], errors='coerce').fillna(0)

                viagens_unicas = df_faixas.drop_duplicates(subset=['VIAGEM_UNICA_ID']).copy()
                capacidades_padrao_veiculo_sozinho = {
                    'TRUCK': 16000,
                    'TOCO': 10000,
                    '3/4 - CAMINHAO PEQUE': 4500
                }

                def get_capacidade_viagem_peso(row):
                    if pd.notna(row['PLACA_CARRETA']) and row['PLACA_CARRETA'] != '' and row['CAPACIDADE_KG'] > 0:
                        return row['CAPACIDADE_KG']
                    if row['CAPAC_CAVALO'] > 0:
                        return row['CAPAC_CAVALO']
                    tipo_veiculo = obter_tipo_veiculo_base(row)
                    return capacidades_padrao_veiculo_sozinho.get(tipo_veiculo, 0)

                def ordenar_siglas_faixa(siglas_texto):
                    siglas_unicas = []
                    siglas_vistas = set()

                    for item in siglas_texto.fillna(''):
                        for sigla in [parte.strip().upper() for parte in str(item).split('/') if str(parte).strip()]:
                            if sigla not in siglas_vistas:
                                siglas_vistas.add(sigla)
                                siglas_unicas.append(sigla)

                    return ' / '.join(siglas_unicas) if siglas_unicas else '—'

                def ordenar_nomes_rotas_faixa(rotas_texto):
                    rotas_unicas = []
                    rotas_vistas = set()

                    for item in rotas_texto.fillna(''):
                        nome_rota = str(item).strip()
                        nome_rota = re.sub(r'^ROTA\s+', '', nome_rota, flags=re.IGNORECASE).strip()

                        if nome_rota and nome_rota not in rotas_vistas:
                            rotas_vistas.add(nome_rota)
                            rotas_unicas.append(nome_rota)

                    return ' / '.join(rotas_unicas) if rotas_unicas else '—'

                def ordenar_sigla_principal_rota_faixa(rotas_texto):
                    rotas_unicas = []
                    rotas_vistas = set()

                    mapa_sigla_principal_rota = {
                        "COXIM": "COX",
                        "SÃO PAULO": "SPO",
                        "GOIÂNIA": "GYN",
                        "BATAGUASSU": "BAT",
                        "RIO BRILHANTE/DOURADOS": "RBT/DOU",
                        "SÃO GABRIEL": "SGO",
                        "MARACAJU": "MJU",
                        "JARDIM": "JDM",
                        "BODOQUENA": "BDQ",
                        "COSTA RICA": "CRC",
                        "IVINHEMA": "IVM",
                        "RIBAS": "ACL",
                        "DOURADOS": "DOU",
                        "RIO BRILHANTE": "RBT",
                        "NOVA ANDRADINA": "NAD",
                        "BONITO": "BTO",
                        "AQUIDAUANA": "AQU",
                        "PONTA PORÃ": "PPR",
                        "TRÊS LAGOAS": "TLG",
                        "CORUMBÁ": "COR",
                    }

                    for item in rotas_texto.fillna(''):
                        nome_rota = str(item).strip()
                        nome_rota = re.sub(r'^ROTA\s+', '', nome_rota, flags=re.IGNORECASE).strip()
                        sigla_rota = mapa_sigla_principal_rota.get(nome_rota, nome_rota)

                        if sigla_rota and sigla_rota not in rotas_vistas:
                            rotas_vistas.add(sigla_rota)
                            rotas_unicas.append(sigla_rota)

                    return ' / '.join(rotas_unicas) if rotas_unicas else '—'

                def obter_nome_rota_para_faixa(destinos):
                    destinos_validos = [
                        str(dest).strip().upper()
                        for dest in destinos
                        if pd.notna(dest) and str(dest).strip()
                    ]
                    if not destinos_validos:
                        return '—'

                    if 'obter_nome_rota_padronizado' in globals() and callable(obter_nome_rota_padronizado):
                        try:
                            return obter_nome_rota_padronizado(destinos_validos)
                        except Exception:
                            pass

                    siglas_ordenadas = ordenar_destinos_geograficamente(
                        sorted(set(destinos_validos)),
                        ROTAS_COMPOSTAS,
                        ORDEM_DAS_ROTAS
                    )
                    return f"ROTA {siglas_ordenadas}" if siglas_ordenadas != '—' else '—'

                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)

                carga_por_viagem = (
                    df_faixas.groupby('VIAGEM_UNICA_ID', dropna=False)['Peso Cálculo (KG)']
                    .sum()
                    .reset_index(name='CARGA_KG')
                )

                siglas_por_viagem = (
                    df_faixas.groupby('VIAGEM_UNICA_ID', dropna=False)['DEST_MANIF']
                    .agg(lambda x: ordenar_destinos_geograficamente(
                        sorted({str(dest).strip().upper() for dest in x if pd.notna(dest) and str(dest).strip()}),
                        ROTAS_COMPOSTAS,
                        ORDEM_DAS_ROTAS
                    ) if any(pd.notna(dest) and str(dest).strip() for dest in x) else '—')
                    .reset_index(name='SIGLAS_ROTA')
                )

                nomes_rotas_por_viagem = (
                    df_faixas.groupby('VIAGEM_UNICA_ID', dropna=False)['DEST_MANIF']
                    .agg(obter_nome_rota_para_faixa)
                    .reset_index(name='NOMES_ROTAS')
                )

                resumo_viagens_ocup = viagens_unicas[[
                    'VIAGEM_UNICA_ID',
                    'CATEGORIA_VIAGEM',
                    'CAPACIDADE_PESO_VIAGEM'
                ]].merge(carga_por_viagem, on='VIAGEM_UNICA_ID', how='left')

                resumo_viagens_ocup = resumo_viagens_ocup.merge(
                    siglas_por_viagem,
                    on='VIAGEM_UNICA_ID',
                    how='left'
                )

                resumo_viagens_ocup = resumo_viagens_ocup.merge(
                    nomes_rotas_por_viagem,
                    on='VIAGEM_UNICA_ID',
                    how='left'
                )

                resumo_viagens_ocup['CARGA_KG'] = pd.to_numeric(
                    resumo_viagens_ocup['CARGA_KG'], errors='coerce'
                ).fillna(0)
                resumo_viagens_ocup = resumo_viagens_ocup[resumo_viagens_ocup['CAPACIDADE_PESO_VIAGEM'] > 0].copy()

                if resumo_viagens_ocup.empty:
                    return None

                resumo_viagens_ocup['OCUPACAO_PERC'] = np.where(
                    resumo_viagens_ocup['CAPACIDADE_PESO_VIAGEM'] > 0,
                    resumo_viagens_ocup['CARGA_KG'] / resumo_viagens_ocup['CAPACIDADE_PESO_VIAGEM'] * 100,
                    0
                )

                resumo_viagens_ocup['FAIXA_OCUPACAO'] = np.select(
                    [
                        resumo_viagens_ocup['OCUPACAO_PERC'] < 60,
                        (resumo_viagens_ocup['OCUPACAO_PERC'] >= 60) & (resumo_viagens_ocup['OCUPACAO_PERC'] <= 80),
                        resumo_viagens_ocup['OCUPACAO_PERC'] > 80
                    ],
                    ['baixa', 'media', 'alta'],
                    default='baixa'
                )

                contagens = resumo_viagens_ocup['FAIXA_OCUPACAO'].value_counts()
                siglas_faixa = (
                    resumo_viagens_ocup.groupby('FAIXA_OCUPACAO', dropna=False)['SIGLAS_ROTA']
                    .apply(ordenar_siglas_faixa)
                    .to_dict()
                )
                nomes_faixa = (
                    resumo_viagens_ocup.groupby('FAIXA_OCUPACAO', dropna=False)['NOMES_ROTAS']
                    .apply(ordenar_nomes_rotas_faixa)
                    .to_dict()
                )
                sigla_principal_faixa = (
                    resumo_viagens_ocup.groupby('FAIXA_OCUPACAO', dropna=False)['NOMES_ROTAS']
                    .apply(ordenar_sigla_principal_rota_faixa)
                    .to_dict()
                )

                exibir_nomes_rotas = periodo_tipo in ["Dia Específico", "Mês Completo", "Período Personalizado"]

                return {
                    'baixa': int(contagens.get('baixa', 0)),
                    'media': int(contagens.get('media', 0)),
                    'alta': int(contagens.get('alta', 0)),
                    'siglas_baixa': nomes_faixa.get('baixa', '—') if exibir_nomes_rotas else sigla_principal_faixa.get('baixa', '—'),
                    'siglas_media': nomes_faixa.get('media', '—') if exibir_nomes_rotas else sigla_principal_faixa.get('media', '—'),
                    'siglas_alta': nomes_faixa.get('alta', '—') if exibir_nomes_rotas else sigla_principal_faixa.get('alta', '—'),
                    'total_viagens': int(resumo_viagens_ocup['VIAGEM_UNICA_ID'].nunique()),
                    'ocupacao_media': float(resumo_viagens_ocup['OCUPACAO_PERC'].mean()),
                }

            def formatar_qtd_viagens(qtd):
                qtd = int(qtd or 0)
                return f"{qtd} viagem" if qtd == 1 else f"{qtd} viagens"

            resumo_grafico_ocupacao = preparar_dados_grafico_ocupacao(df_para_analise)
            resumo_faixas_ocupacao = preparar_faixas_ocupacao_viagens(df_para_analise) if selecionar_veiculo != "TODOS" else None
            st.markdown("""
                <style>
                .occupancy-mini-section-title {
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 14px;
                    margin: 10px 0 12px 0;
                    padding: 13px 16px;
                    border-radius: 20px;
                    border: 1px solid rgba(148,163,184,0.14);
                    background: linear-gradient(135deg, rgba(7,15,30,0.96) 0%, rgba(15,23,42,0.88) 100%);
                    box-shadow: 0 14px 28px rgba(2,6,23,0.22), inset 0 1px 0 rgba(255,255,255,0.04);
                    isolation: isolate;
                }
                .occupancy-mini-section-title::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(90deg, rgba(59,130,246,0.12) 0%, rgba(59,130,246,0.02) 55%, rgba(255,255,255,0.00) 100%);
                    pointer-events: none;
                    z-index: 0;
                }
                .occupancy-mini-section-title.finance::before {
                    background: linear-gradient(90deg, rgba(16,185,129,0.12) 0%, rgba(16,185,129,0.02) 55%, rgba(255,255,255,0.00) 100%);
                }
                .occupancy-mini-section-head {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    min-width: 0;
                    position: relative;
                    z-index: 1;
                }
                .occupancy-mini-section-title i {
                    width: 36px;
                    height: 36px;
                    min-width: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 12px;
                    color: #ffffff;
                    background: linear-gradient(135deg, rgba(29,78,216,0.94) 0%, rgba(59,130,246,0.62) 100%);
                    box-shadow: 0 10px 18px rgba(37,99,235,0.20);
                    position: relative;
                    z-index: 1;
                    font-size: 0.92rem;
                }
                .occupancy-mini-section-title.finance i {
                    background: linear-gradient(135deg, rgba(5,150,105,0.92) 0%, rgba(16,185,129,0.62) 100%);
                    box-shadow: 0 10px 18px rgba(16,185,129,0.18);
                }
                .occupancy-mini-section-title .label-wrap {
                    display: flex;
                    flex-direction: column;
                    gap: 2px;
                    min-width: 0;
                    position: relative;
                    z-index: 1;
                }
                .occupancy-mini-section-title .eyebrow {
                    color: #93c5fd;
                    font-size: 0.62rem;
                    font-weight: 800;
                    letter-spacing: 0.9px;
                    text-transform: uppercase;
                    line-height: 1;
                }
                .occupancy-mini-section-title.finance .eyebrow {
                    color: #86efac;
                }
                .occupancy-mini-section-title .title {
                    color: #ffffff;
                    font-size: 1rem;
                    font-weight: 800;
                    line-height: 1.1;
                    letter-spacing: 0.1px;
                }
                .occupancy-mini-badges {
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-left: auto;
                    position: relative;
                    z-index: 1;
                }
                .occupancy-mini-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 8px 12px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.06);
                    border: 1px solid rgba(148,163,184,0.18);
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
                    backdrop-filter: blur(6px);
                    -webkit-backdrop-filter: blur(6px);
                    white-space: nowrap;
                }
                .occupancy-mini-badge .badge-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 999px;
                    background: #60a5fa;
                    box-shadow: 0 0 10px rgba(96,165,250,0.45);
                    flex-shrink: 0;
                }
                .occupancy-mini-section-title.finance .occupancy-mini-badge .badge-dot {
                    background: #34d399;
                    box-shadow: 0 0 10px rgba(52,211,153,0.40);
                }
                .occupancy-mini-badge .badge-value {
                    color: #e2e8f0;
                    font-size: 0.76rem;
                    font-weight: 700;
                    letter-spacing: 0.08px;
                    line-height: 1;
                }
                .executive-badge-rail {
                    position: relative;
                    overflow: hidden;
                    margin: 0 0 18px 0;
                    padding: 9px 14px;
                    min-height: 48px;
                    border-radius: 18px;
                    border: 1px solid rgba(59,130,246,0.18);
                    background: linear-gradient(135deg, rgba(7,15,30,0.94) 0%, rgba(10,18,34,0.90) 100%);
                    box-shadow: 0 12px 24px rgba(2,6,23,0.20), inset 0 1px 0 rgba(255,255,255,0.04);
                    isolation: isolate;
                }
                .executive-badge-rail::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(90deg, rgba(59,130,246,0.12) 0%, rgba(59,130,246,0.03) 55%, rgba(255,255,255,0.00) 100%);
                    pointer-events: none;
                    z-index: 0;
                }
                .executive-badge-rail.finance {
                    border-color: rgba(16,185,129,0.18);
                }
                .executive-badge-rail.finance::before {
                    background: linear-gradient(90deg, rgba(16,185,129,0.12) 0%, rgba(16,185,129,0.03) 55%, rgba(255,255,255,0.00) 100%);
                }
                .executive-badge-rail .occupancy-mini-badges {
                    width: 100%;
                    justify-content: flex-start;
                    flex-wrap: nowrap;
                    gap: 8px;
                    margin-left: 0;
                    overflow-x: auto;
                    scrollbar-width: none;
                    position: relative;
                    z-index: 1;
                }
                .executive-badge-rail .occupancy-mini-badges::-webkit-scrollbar {
                    display: none;
                }
                .executive-badge-rail .occupancy-mini-badge {
                    padding: 7px 11px;
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(148,163,184,0.16);
                }
                .executive-group-shell {
                    position: relative;
                    height: 100%;
                    padding: 12px 12px 14px 12px;
                    border-radius: 26px;
                    border: 1px solid rgba(148,163,184,0.12);
                    background: linear-gradient(135deg, rgba(7,15,30,0.42) 0%, rgba(15,23,42,0.18) 100%);
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
                    overflow: hidden;
                }
                .executive-group-shell::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    background: radial-gradient(circle at top left, rgba(59,130,246,0.10) 0%, rgba(59,130,246,0.00) 42%);
                    pointer-events: none;
                }
                .executive-group-shell.finance::before {
                    background: radial-gradient(circle at top left, rgba(16,185,129,0.10) 0%, rgba(16,185,129,0.00) 42%);
                }
                .executive-group-shell .occupancy-mini-section-title {
                    margin: 0 0 10px 0;
                }
                .executive-group-shell .occupancy-mini-badges {
                    gap: 6px;
                }
                .executive-group-shell .occupancy-mini-badge {
                    padding: 6px 10px;
                }
                .finance-kpi-card.exec-kpi-compact-card {
                    min-height: 118px !important;
                    padding: 13px 14px 11px 14px !important;
                    border-radius: 18px !important;
                }
                .finance-kpi-card.exec-kpi-compact-card .finance-kpi-header {
                    gap: 9px;
                }
                .finance-kpi-card.exec-kpi-compact-card .finance-kpi-title {
                    min-height: unset !important;
                    font-size: 0.64rem !important;
                    line-height: 1.16 !important;
                    letter-spacing: 0.55px !important;
                }
                .finance-kpi-card.exec-kpi-compact-card .finance-kpi-icon {
                    width: 34px;
                    height: 34px;
                    min-width: 34px;
                    border-radius: 12px;
                    font-size: 0.86rem;
                }
                .finance-kpi-card.exec-kpi-compact-card .finance-kpi-value {
                    margin-top: 10px !important;
                    font-size: 1.58rem !important;
                    line-height: 1.04 !important;
                    letter-spacing: -0.5px !important;
                }
                .finance-kpi-card.exec-kpi-compact-card .finance-kpi-divider {
                    margin: 10px 0 8px 0 !important;
                }
                .finance-kpi-card.exec-kpi-compact-card .finance-kpi-footer {
                    padding: 4px 9px !important;
                    font-size: 0.68rem !important;
                    gap: 6px !important;
                }
                .occupancy-chart-panel {
                    position: relative;
                    overflow: hidden;
                    margin-top: 0;
                    border-radius: 24px;
                    padding: 18px 18px 16px 18px;
                    min-height: 100%;
                    background:
                        radial-gradient(circle at top right, rgba(59,130,246,0.16) 0%, rgba(59,130,246,0.00) 32%),
                        linear-gradient(135deg, rgba(9,14,29,0.98) 0%, rgba(16,24,40,0.94) 100%);
                    border: 1px solid rgba(96,165,250,0.22);
                    box-shadow: 0 16px 32px rgba(2,6,23,0.22), inset 0 1px 0 rgba(255,255,255,0.04);
                }
                .occupancy-chart-panel::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.00) 30%);
                    pointer-events: none;
                }
                .occupancy-chart-header {
                    position: relative;
                    z-index: 1;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 14px;
                }
                .occupancy-chart-header-icon {
                    width: 44px;
                    height: 44px;
                    min-width: 44px;
                    border-radius: 14px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, rgba(29,78,216,0.92) 0%, rgba(59,130,246,0.64) 100%);
                    color: #ffffff;
                    font-size: 1rem;
                    box-shadow: 0 10px 20px rgba(37,99,235,0.24);
                }
                .occupancy-chart-header-copy {
                    min-width: 0;
                    display: flex;
                    flex-direction: column;
                    gap: 2px;
                }
                .occupancy-chart-header-copy .eyebrow {
                    color: #93c5fd;
                    font-size: 0.62rem;
                    font-weight: 800;
                    letter-spacing: 0.9px;
                    text-transform: uppercase;
                    line-height: 1;
                }
                .occupancy-chart-header-copy .title {
                    color: #f8fafc;
                    font-family: "Poppins", "Segoe UI", sans-serif;
                    font-size: 1.06rem;
                    font-weight: 700;
                    line-height: 1.15;
                }
                .occupancy-chart-stats {
                    position: relative;
                    z-index: 1;
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 10px;
                    margin-bottom: 12px;
                }
                .occupancy-chart-stat {
                    padding: 11px 12px;
                    border-radius: 16px;
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(148,163,184,0.16);
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
                }
                .occupancy-chart-stat .label {
                    display: block;
                    color: #94a3b8;
                    font-size: 0.66rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.7px;
                    line-height: 1;
                    margin-bottom: 6px;
                }
                .occupancy-chart-stat .value {
                    display: block;
                    color: #f8fafc;
                    font-size: 1.10rem;
                    font-weight: 800;
                    line-height: 1.05;
                }
                .occupancy-chart-caption {
                    position: relative;
                    z-index: 1;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 7px;
                    margin: 4px 0 8px 0;
                    color: #cbd5e1;
                    font-size: 0.72rem;
                    font-weight: 700;
                }
                .occupancy-chart-caption .dot {
                    width: 7px;
                    height: 7px;
                    border-radius: 999px;
                    background: #60a5fa;
                    box-shadow: 0 0 10px rgba(96,165,250,0.40);
                }
                .occupancy-chart-legend {
                    position: relative;
                    z-index: 1;
                    display: grid;
                    gap: 10px;
                    margin-top: 8px;
                }
                .occupancy-chart-layout {
                    display: grid;
                    grid-template-columns: minmax(300px, 1.14fr) minmax(310px, 1fr);
                    align-items: center;
                    gap: 22px;
                    margin-top: 10px;
                }
                .occupancy-chart-plot {
                    min-width: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .occupancy-chart-legend.occupancy-chart-legend-side {
                    margin-top: 0;
                    align-content: start;
                    height: 100%;
                }
                .occupancy-chart-legend-side .occupancy-chart-legend-item {
                    min-height: 62px;
                }
                .occupancy-chart-legend-item {
                    --accent: #60a5fa;
                    position: relative;
                    overflow: hidden;
                    display: grid;
                    grid-template-columns: auto 1fr auto;
                    align-items: center;
                    gap: 13px;
                    padding: 13px 14px;
                    min-height: 70px;
                    border-radius: 18px;
                    background: linear-gradient(135deg, rgba(15,23,42,0.96) 0%, rgba(30,41,59,0.92) 100%);
                    border: 1px solid rgba(148,163,184,0.16);
                    box-shadow: 0 10px 22px rgba(2,6,23,0.18), inset 0 1px 0 rgba(255,255,255,0.04);
                    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
                }
                .occupancy-chart-legend-item::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 16%, transparent) 0%, rgba(255,255,255,0) 58%);
                    pointer-events: none;
                }
                .occupancy-chart-legend-item::after {
                    content: "";
                    position: absolute;
                    left: 0;
                    top: 0;
                    bottom: 0;
                    width: 3px;
                    background: var(--accent);
                    box-shadow: 0 0 14px color-mix(in srgb, var(--accent) 55%, transparent);
                    opacity: 0.95;
                }
                .occupancy-chart-legend-item:hover {
                    transform: translateY(-1px);
                    border-color: color-mix(in srgb, var(--accent) 38%, rgba(148,163,184,0.16));
                    box-shadow: 0 14px 28px rgba(2,6,23,0.24), inset 0 1px 0 rgba(255,255,255,0.05);
                }
                .occupancy-chart-legend-dot {
                    position: relative;
                    z-index: 1;
                    width: 12px;
                    height: 12px;
                    border-radius: 999px;
                    flex-shrink: 0;
                    box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 18%, transparent), 0 0 12px color-mix(in srgb, var(--accent) 38%, transparent);
                }
                .occupancy-chart-legend-main {
                    position: relative;
                    z-index: 1;
                    min-width: 0;
                    display: flex;
                    flex-direction: column;
                    gap: 3px;
                }
                .occupancy-chart-legend-main .name {
                    color: #f8fafc;
                    font-size: 0.88rem;
                    font-weight: 800;
                    line-height: 1.05;
                    letter-spacing: 0.15px;
                }
                .occupancy-chart-legend-main .meta {
                    color: #a7b4c7;
                    font-size: 0.72rem;
                    font-weight: 700;
                    line-height: 1.2;
                }
                .occupancy-chart-legend-value {
                    position: relative;
                    z-index: 1;
                    color: #f8fafc;
                    font-size: 0.80rem;
                    font-weight: 800;
                    text-align: right;
                    white-space: nowrap;
                    padding: 5px 9px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.07);
                    border: 1px solid rgba(255,255,255,0.10);
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
                }
                .occupancy-range-panel {
                    margin-top: 12px;
                    padding: 14px 14px 13px 14px;
                    border-radius: 20px;
                    background:
                        radial-gradient(circle at top right, rgba(59,130,246,0.16) 0%, rgba(59,130,246,0.00) 32%),
                        linear-gradient(135deg, rgba(9,14,29,0.98) 0%, rgba(16,24,40,0.94) 100%);
                    border: 1px solid rgba(96,165,250,0.18);
                    box-shadow: 0 14px 28px rgba(2,6,23,0.22), inset 0 1px 0 rgba(255,255,255,0.04);
                }
                .occupancy-range-header {
                    display: flex;
                    flex-direction: column;
                    gap: 2px;
                    margin-bottom: 10px;
                }
                .occupancy-range-header .eyebrow {
                    color: #93c5fd;
                    font-size: 0.62rem;
                    font-weight: 800;
                    letter-spacing: 0.9px;
                    text-transform: uppercase;
                    line-height: 1;
                }
                .occupancy-range-header .title {
                    color: #f8fafc;
                    font-family: "Poppins", "Segoe UI", sans-serif;
                    font-size: 0.94rem;
                    font-weight: 700;
                    line-height: 1.2;
                }
                .occupancy-range-list {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                .occupancy-range-item {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 12px;
                    padding: 10px 11px;
                    border-radius: 16px;
                    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
                    border: 1px solid rgba(255,255,255,0.08);
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
                }
                .occupancy-range-item.low {
                    border-left: 3px solid #ef4444;
                }
                .occupancy-range-item.mid {
                    border-left: 3px solid #f59e0b;
                }
                .occupancy-range-item.high {
                    border-left: 3px solid #22c55e;
                }
                .occupancy-range-copy {
                    display: flex;
                    align-items: flex-start;
                    gap: 9px;
                    min-width: 0;
                }
                .occupancy-range-dot {
                    width: 10px;
                    height: 10px;
                    min-width: 10px;
                    border-radius: 999px;
                    margin-top: 4px;
                    box-shadow: 0 0 12px currentColor;
                }
                .occupancy-range-item.low .occupancy-range-dot {
                    color: #ef4444;
                    background: #ef4444;
                }
                .occupancy-range-item.mid .occupancy-range-dot {
                    color: #f59e0b;
                    background: #f59e0b;
                }
                .occupancy-range-item.high .occupancy-range-dot {
                    color: #22c55e;
                    background: #22c55e;
                }
                .occupancy-range-text {
                    display: flex;
                    flex-direction: column;
                    gap: 2px;
                    min-width: 0;
                }
                .occupancy-range-label {
                    color: #f8fafc;
                    font-size: 0.78rem;
                    font-weight: 800;
                    line-height: 1.1;
                }
                .occupancy-range-meta {
                    color: #94a3b8;
                    font-size: 0.67rem;
                    font-weight: 700;
                    line-height: 1.25;
                    white-space: normal;
                    overflow-wrap: anywhere;
                }
                .occupancy-range-badge {
                    color: #f8fafc;
                    font-size: 0.72rem;
                    font-weight: 800;
                    white-space: nowrap;
                    padding: 6px 10px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.10);
                }
                .occupancy-range-footer {
                    margin-top: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    flex-wrap: wrap;
                }
                .occupancy-range-chip {
                    display: inline-flex;
                    align-items: center;
                    gap: 7px;
                    padding: 6px 10px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.06);
                    border: 1px solid rgba(255,255,255,0.10);
                    color: #dbeafe;
                    font-size: 0.71rem;
                    font-weight: 800;
                }
                .occupancy-chart-slot {
                    position: relative;
                    overflow: hidden;
                    min-height: 278px;
                    height: 100%;
                    margin-top: 10px;
                    border-radius: 22px;
                    padding: 18px 18px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    gap: 12px;
                    background:
                        radial-gradient(circle at top right, rgba(59,130,246,0.18) 0%, rgba(59,130,246,0.00) 30%),
                        linear-gradient(135deg, rgba(9,14,29,0.98) 0%, rgba(16,24,40,0.94) 100%);
                    border: 1px dashed rgba(96,165,250,0.34);
                    box-shadow: 0 16px 32px rgba(2,6,23,0.22), inset 0 1px 0 rgba(255,255,255,0.04);
                }
                .occupancy-chart-slot::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.00) 32%);
                    pointer-events: none;
                }
                .occupancy-chart-slot-icon {
                    width: 58px;
                    height: 58px;
                    border-radius: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, rgba(29,78,216,0.92) 0%, rgba(59,130,246,0.64) 100%);
                    color: #ffffff;
                    font-size: 1.35rem;
                    box-shadow: 0 12px 24px rgba(37,99,235,0.26);
                    position: relative;
                    z-index: 1;
                }
                .occupancy-chart-slot-title {
                    position: relative;
                    z-index: 1;
                    color: #f8fafc;
                    font-family: "Poppins", "Segoe UI", sans-serif;
                    font-size: 1.04rem;
                    font-weight: 700;
                    line-height: 1.2;
                }
                .occupancy-chart-slot-subtitle {
                    position: relative;
                    z-index: 1;
                    color: #94a3b8;
                    font-size: 0.82rem;
                    line-height: 1.45;
                    max-width: 270px;
                }
                .occupancy-chart-slot-chip {
                    position: relative;
                    z-index: 1;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 7px 12px;
                    border-radius: 999px;
                    background: rgba(255,255,255,0.06);
                    border: 1px solid rgba(148,163,184,0.18);
                    color: #e2e8f0;
                    font-size: 0.73rem;
                    font-weight: 700;
                }
                html[data-theme="light"] .occupancy-mini-section-title {
                    background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.96) 100%) !important;
                    border: 1px solid rgba(15,23,42,0.08) !important;
                    box-shadow: 0 14px 28px rgba(15,23,42,0.08) !important;
                }
                html[data-theme="light"] .occupancy-mini-section-title .title {
                    color: #0f172a !important;
                }
                html[data-theme="light"] .occupancy-mini-section-title .eyebrow {
                    color: #2563eb !important;
                }
                html[data-theme="light"] .occupancy-mini-section-title.finance .eyebrow {
                    color: #059669 !important;
                }
                html[data-theme="light"] .occupancy-mini-badge {
                    background: rgba(255,255,255,0.78) !important;
                    border: 1px solid rgba(148,163,184,0.26) !important;
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65) !important;
                }
                html[data-theme="light"] .occupancy-mini-badge .badge-value {
                    color: #334155 !important;
                }
                html[data-theme="light"] .executive-badge-rail {
                    background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.96) 100%) !important;
                    border: 1px solid rgba(59,130,246,0.16) !important;
                    box-shadow: 0 12px 24px rgba(15,23,42,0.06) !important;
                }
                html[data-theme="light"] .executive-badge-rail.finance {
                    border-color: rgba(16,185,129,0.16) !important;
                }
                html[data-theme="light"] .executive-group-shell {
                    background: linear-gradient(135deg, rgba(255,255,255,0.88) 0%, rgba(248,250,252,0.76) 100%) !important;
                    border: 1px solid rgba(148,163,184,0.18) !important;
                    box-shadow: 0 12px 24px rgba(15,23,42,0.05) !important;
                }
                html[data-theme="light"] .occupancy-chart-panel {
                    background:
                        radial-gradient(circle at top right, rgba(59,130,246,0.12) 0%, rgba(59,130,246,0.00) 30%),
                        linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.96) 100%) !important;
                    border: 1px solid rgba(59,130,246,0.18) !important;
                    box-shadow: 0 14px 28px rgba(15,23,42,0.08) !important;
                }
                html[data-theme="light"] .occupancy-chart-header-copy .eyebrow {
                    color: #2563eb !important;
                }
                html[data-theme="light"] .occupancy-chart-header-copy .title,
                html[data-theme="light"] .occupancy-chart-stat .value,
                html[data-theme="light"] .occupancy-chart-legend-main .name {
                    color: #0f172a !important;
                }
                html[data-theme="light"] .occupancy-chart-stat {
                    background: rgba(255,255,255,0.78) !important;
                    border: 1px solid rgba(148,163,184,0.22) !important;
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.65) !important;
                }
                html[data-theme="light"] .occupancy-chart-legend-item {
                    background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.94) 100%) !important;
                    border: 1px solid rgba(148,163,184,0.22) !important;
                    box-shadow: 0 10px 24px rgba(15,23,42,0.08), inset 0 1px 0 rgba(255,255,255,0.7) !important;
                }
                html[data-theme="light"] .occupancy-chart-stat .label,
                html[data-theme="light"] .occupancy-chart-caption,
                html[data-theme="light"] .occupancy-chart-legend-main .meta {
                    color: #475569 !important;
                }
                html[data-theme="light"] .occupancy-chart-legend-value {
                    color: #334155 !important;
                    background: rgba(255,255,255,0.88) !important;
                    border: 1px solid rgba(148,163,184,0.24) !important;
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7) !important;
                }
                html[data-theme="light"] .occupancy-range-panel {
                    background:
                        radial-gradient(circle at top right, rgba(59,130,246,0.12) 0%, rgba(59,130,246,0.00) 32%),
                        linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.96) 100%) !important;
                    border: 1px solid rgba(59,130,246,0.16) !important;
                    box-shadow: 0 14px 28px rgba(15,23,42,0.08) !important;
                }
                html[data-theme="light"] .occupancy-range-header .eyebrow {
                    color: #2563eb !important;
                }
                html[data-theme="light"] .occupancy-range-header .title,
                html[data-theme="light"] .occupancy-range-label,
                html[data-theme="light"] .occupancy-range-badge {
                    color: #0f172a !important;
                }
                html[data-theme="light"] .occupancy-range-meta {
                    color: #475569 !important;
                }
                html[data-theme="light"] .occupancy-range-item {
                    background: rgba(255,255,255,0.82) !important;
                    border: 1px solid rgba(148,163,184,0.22) !important;
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.72) !important;
                }
                html[data-theme="light"] .occupancy-range-badge,
                html[data-theme="light"] .occupancy-range-chip {
                    background: rgba(255,255,255,0.86) !important;
                    border: 1px solid rgba(148,163,184,0.24) !important;
                }
                html[data-theme="light"] .occupancy-range-chip {
                    color: #334155 !important;
                }
                html[data-theme="light"] .occupancy-chart-slot {
                    background:
                        radial-gradient(circle at top right, rgba(59,130,246,0.12) 0%, rgba(59,130,246,0.00) 30%),
                        linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(241,245,249,0.96) 100%) !important;
                    border: 1px dashed rgba(59,130,246,0.24) !important;
                    box-shadow: 0 14px 28px rgba(15,23,42,0.08) !important;
                }
                @media (max-width: 1100px) {
                    .occupancy-chart-layout {
                        grid-template-columns: 1fr;
                        align-items: start;
                    }
                    .occupancy-chart-legend.occupancy-chart-legend-side {
                        margin-top: 10px;
                    }
                }
                html[data-theme="light"] .occupancy-chart-slot-title {
                    color: #0f172a !important;
                }
                html[data-theme="light"] .occupancy-chart-slot-subtitle,
                html[data-theme="light"] .occupancy-chart-slot-chip {
                    color: #475569 !important;
                }
                html[data-theme="light"] .occupancy-chart-slot-chip {
                    background: rgba(255,255,255,0.78) !important;
                    border: 1px solid rgba(148,163,184,0.26) !important;
                }
                @media (max-width: 1320px) {
                    .occupancy-mini-section-title {
                        align-items: flex-start;
                        flex-direction: column;
                    }
                    .occupancy-mini-badges {
                        width: 100%;
                        justify-content: flex-start;
                        margin-left: 0;
                    }
                    .executive-badge-rail .occupancy-mini-badges {
                        flex-wrap: wrap;
                        overflow-x: visible;
                    }
                    .occupancy-chart-slot {
                        min-height: 244px;
                    }
                }
                </style>
            """, unsafe_allow_html=True)

            cards_area, chart_area = st.columns([1.92, 1.08], gap="large")

            with cards_area:
                col_ind_ops, col_ind_fin = st.columns(2, gap="medium")

                with col_ind_ops:
                    st.markdown(f"""
                        <div class="executive-badge-rail ops">
                            <div class="occupancy-mini-badges">
                                <span class="occupancy-mini-badge"><span class="badge-dot"></span><span class="badge-value">{badge_ops_viagens}</span></span>
                                <span class="occupancy-mini-badge"><span class="badge-dot"></span><span class="badge-value">{badge_ops_distancia}</span></span>
                            </div>
                        </div>
                        <div class="executive-group-shell ops">
                        <div class="occupancy-mini-section-title">
                            <div class="occupancy-mini-section-head">
                                <i class="fa-solid fa-gears"></i>
                                <div class="label-wrap">
                                    <span class="eyebrow">Indicadores executivos</span>
                                    <span class="title">Indicadores Operacionais</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    op1, op2 = st.columns(2, gap="small")
                    with op1:
                        render_overview_kpi_card(
                            titulo="QTD. CTRC",
                            valor=formatar_numero(total_qtd_ctrc_ind),
                            icone="fa-file-lines",
                            rodape="Documentos emitidos",
                            classe="overview-blue",
                            extra_classes="exec-kpi-compact-card"
                        )
                    with op2:
                        render_overview_kpi_card(
                            titulo="Volumes",
                            valor=formatar_numero(total_volumes_ind),
                            icone="fa-boxes-stacked",
                            rodape="Volumes movimentados",
                            classe="overview-blue",
                            extra_classes="exec-kpi-compact-card"
                        )

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                    op3, op4 = st.columns(2, gap="small")
                    with op3:
                        render_overview_kpi_card(
                            titulo="Peso Cálculo (KG)",
                            valor=f"{formatar_numero(total_peso_ind)} KG",
                            icone="fa-weight-hanging",
                            rodape="Peso de cálculo",
                            classe="overview-blue",
                            extra_classes="exec-kpi-compact-card"
                        )
                    with op4:
                        render_overview_kpi_card(
                            titulo="Cubagem Total (M³)",
                            valor=f"{formatar_numero(total_cubagem_ind, 3)} M³",
                            icone="fa-cubes-stacked",
                            rodape="Cubagem movimentada",
                            classe="overview-blue",
                            extra_classes="exec-kpi-compact-card"
                        )
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_ind_fin:
                    st.markdown(f"""
                        <div class="executive-badge-rail finance">
                            <div class="occupancy-mini-badges">
                                <span class="occupancy-mini-badge"><span class="badge-dot"></span><span class="badge-value">{badge_fin_frete}</span></span>
                                <span class="occupancy-mini-badge"><span class="badge-dot"></span><span class="badge-value">{badge_fin_custo_km}</span></span>
                            </div>
                        </div>
                        <div class="executive-group-shell finance">
                        <div class="occupancy-mini-section-title finance">
                            <div class="occupancy-mini-section-head">
                                <i class="fa-solid fa-sack-dollar"></i>
                                <div class="label-wrap">
                                    <span class="eyebrow">Indicadores executivos</span>
                                    <span class="title">Indicadores Financeiros</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    fin1, fin2 = st.columns(2, gap="small")
                    with fin1:
                        render_overview_kpi_card(
                            titulo="CTRB Total (R$)",
                            valor=formatar_moeda(total_ctrb_ind),
                            icone="fa-file-invoice-dollar",
                            rodape="Custo total do período",
                            classe="overview-emerald",
                            extra_classes="exec-kpi-compact-card"
                        )
                    with fin2:
                        render_overview_kpi_card(
                            titulo="Frete Total (R$)",
                            valor=formatar_moeda(total_frete_ind),
                            icone="fa-money-bill-wave",
                            rodape="Receita do período",
                            classe="overview-emerald",
                            extra_classes="exec-kpi-compact-card"
                        )

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                    fin3, fin4 = st.columns(2, gap="small")
                    with fin3:
                        render_overview_kpi_card(
                            titulo="ICMS (R$)",
                            valor=formatar_moeda(total_icms_ind),
                            icone="fa-receipt",
                            rodape="Tributação do período",
                            classe="overview-emerald",
                            extra_classes="exec-kpi-compact-card"
                        )
                    with fin4:
                        render_overview_kpi_card(
                            titulo="Valor de Mercadoria (R$)",
                            valor=formatar_moeda(total_mercadoria_ind),
                            icone="fa-box-open",
                            rodape="Valor total transportado",
                            classe="overview-emerald",
                            extra_classes="exec-kpi-compact-card"
                        )
                    st.markdown('</div>', unsafe_allow_html=True)

            with chart_area:
                if not resumo_grafico_ocupacao.empty:
                    ordem_legenda = resumo_grafico_ocupacao['TIPO_LABEL'].tolist()
                    cores_legenda = resumo_grafico_ocupacao['COR'].tolist()
                    carga_total_grafico = resumo_grafico_ocupacao['CARGA_KG'].sum()
                    capacidade_total_grafico = resumo_grafico_ocupacao['CAPACIDADE_KG'].sum()
                    ocupacao_media_grafico = (carga_total_grafico / capacidade_total_grafico * 100) if capacidade_total_grafico > 0 else 0

                    st.markdown(f"""
                        <div class="occupancy-chart-panel">
                            <div class="occupancy-chart-header">
                                <div class="occupancy-chart-header-icon"><i class="fa-solid fa-chart-pie"></i></div>
                                <div class="occupancy-chart-header-copy">
                                    <span class="title">Ocupação de carga por tipo de veículo</span>
                                </div>
                            </div>
                            <div class="occupancy-chart-stats">
                                <div class="occupancy-chart-stat">
                                    <span class="label">Ocupação média</span>
                                    <span class="value">{formatar_percentual(ocupacao_media_grafico)}</span>
                                </div>
                                <div class="occupancy-chart-stat">
                                    <span class="label">Carga total</span>
                                    <span class="value">{formatar_numero(carga_total_grafico / 1000, 1)} t</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    chart_ocupacao_tipo = alt.Chart(resumo_grafico_ocupacao).mark_arc(
                        innerRadius=82,
                        outerRadius=124,
                        cornerRadius=12,
                        stroke='#0f172a',
                        strokeWidth=1.8
                    ).encode(
                        theta=alt.Theta('CARGA_KG:Q'),
                        color=alt.Color(
                            'TIPO_LABEL:N',
                            scale=alt.Scale(domain=ordem_legenda, range=cores_legenda),
                            legend=None
                        ),
                        order=alt.Order('ORDEM_TIPO:Q', sort='ascending'),
                        tooltip=[
                            alt.Tooltip('TIPO_LABEL:N', title='Tipo'),
                            alt.Tooltip('PARTICIPACAO_PERC:Q', title='Participação', format='.1f'),
                            alt.Tooltip('OCUPACAO_PERC:Q', title='Ocupação', format='.1f'),
                            alt.Tooltip('CARGA_KG:Q', title='Carga (kg)', format=',.0f'),
                            alt.Tooltip('TOTAL_VIAGENS:Q', title='Viagens')
                        ]
                    ).properties(height=300)

                    legenda_itens = []
                    for _, row in resumo_grafico_ocupacao.iterrows():
                        legenda_itens.append(
                            (
                                f"<div class='occupancy-chart-legend-item' style='--accent: {row['COR']};'>"
                                f"<span class='occupancy-chart-legend-dot' style='background: {row['COR']};'></span>"
                                f"<div class='occupancy-chart-legend-main'>"
                                f"<span class='name'>{row['TIPO_LABEL']}</span>"
                                f"<span class='meta'>{formatar_percentual(row['PARTICIPACAO_PERC'])} da carga • {formatar_percentual(row['OCUPACAO_PERC'])} ocupação</span>"
                                f"</div>"
                                f"<span class='occupancy-chart-legend-value'>{formatar_numero(row['CARGA_TON'], 1)} t</span>"
                                f"</div>"
                            )
                        )

                    legenda_html = ''.join(legenda_itens).strip()

                    if selecionar_veiculo == "TODOS":
                        st.markdown("<div class='occupancy-chart-layout'>", unsafe_allow_html=True)
                        graf_col, leg_col = st.columns([1.22, 0.98], gap="medium")

                        with graf_col:
                            st.markdown("<div class='occupancy-chart-plot'>", unsafe_allow_html=True)
                            st.altair_chart(
                                chart_ocupacao_tipo.configure_view(stroke=None),
                                use_container_width=True
                            )
                            st.markdown("</div>", unsafe_allow_html=True)

                        with leg_col:
                            st.markdown(
                                f"<div class='occupancy-chart-legend occupancy-chart-legend-side'>{legenda_html}</div>",
                                unsafe_allow_html=True
                            )

                        st.markdown("</div>", unsafe_allow_html=True)

                    elif resumo_faixas_ocupacao and resumo_faixas_ocupacao.get('total_viagens', 0) > 0:
                        insight_html = f"""
                            <div class="occupancy-range-panel">
                                <div class="occupancy-range-header">
                                    <span class="eyebrow">{selecionar_veiculo} em foco</span>
                                    <span class="title">Distribuição por faixa de ocupação</span>
                                </div>
                                <div class="occupancy-range-list">
                                    <div class="occupancy-range-item low">
                                        <div class="occupancy-range-copy">
                                            <span class="occupancy-range-dot"></span>
                                            <div class="occupancy-range-text">
                                                <span class="occupancy-range-label">Baixa ocupação</span>
                                                <span class="occupancy-range-meta">{resumo_faixas_ocupacao['siglas_baixa']}</span>
                                            </div>
                                        </div>
                                        <span class="occupancy-range-badge">{formatar_qtd_viagens(resumo_faixas_ocupacao['baixa'])}</span>
                                    </div>
                                    <div class="occupancy-range-item mid">
                                        <div class="occupancy-range-copy">
                                            <span class="occupancy-range-dot"></span>
                                            <div class="occupancy-range-text">
                                                <span class="occupancy-range-label">Faixa média</span>
                                                <span class="occupancy-range-meta">{resumo_faixas_ocupacao['siglas_media']}</span>
                                            </div>
                                        </div>
                                        <span class="occupancy-range-badge">{formatar_qtd_viagens(resumo_faixas_ocupacao['media'])}</span>
                                    </div>
                                    <div class="occupancy-range-item high">
                                        <div class="occupancy-range-copy">
                                            <span class="occupancy-range-dot"></span>
                                            <div class="occupancy-range-text">
                                                <span class="occupancy-range-label">Alta ocupação</span>
                                                <span class="occupancy-range-meta">{resumo_faixas_ocupacao['siglas_alta']}</span>
                                            </div>
                                        </div>
                                        <span class="occupancy-range-badge">{formatar_qtd_viagens(resumo_faixas_ocupacao['alta'])}</span>
                                    </div>
                                </div>
                                <div class="occupancy-range-footer">
                                    <span class="occupancy-range-chip"><i class="fa-solid fa-road"></i><span>Base: {formatar_qtd_viagens(resumo_faixas_ocupacao['total_viagens'])}</span></span>
                                    <span class="occupancy-range-chip"><i class="fa-solid fa-chart-line"></i><span>Média: {formatar_percentual(resumo_faixas_ocupacao['ocupacao_media'])}</span></span>
                                </div>
                            </div>
                        """
                        st.markdown(insight_html, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="occupancy-chart-slot">
                            <div class="occupancy-chart-slot-icon"><i class="fa-solid fa-chart-pie"></i></div>
                            <div class="occupancy-chart-slot-title">Análise de Ocupação de Carga</div>
                            <div class="occupancy-chart-slot-subtitle">Não há dados suficientes para montar o gráfico de pizza por tipo de veículo com os filtros atuais.</div>
                            <div class="occupancy-chart-slot-chip"><i class="fa-solid fa-filter-circle-xmark"></i><span>Ajuste os filtros</span></div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
            
            if dados_agregados:
                col_esq, col_meio, col_dir = st.columns([1.02, 0.96, 1.02], gap="medium")
                deslocamento_ocupacao_lateral_px = 34

                with col_esq:
                    st.markdown(f"<div style='height: {deslocamento_ocupacao_lateral_px}px;'></div>", unsafe_allow_html=True)
                    renderizar_card_ocupacao_moderno(
                        titulo="Ocupação de Peso (KG)",
                        ocup_perc=dados_agregados['ocup_peso_perc'],
                        total_valor=dados_agregados['total_peso'],
                        cap_total=dados_agregados['cap_total_peso'],
                        unidade="KG",
                        ociosidade_perc=dados_agregados['ociosidade_peso_perc'],
                        potencial_nao_utilizado=dados_agregados['potencial_nao_utilizado_kg'],
                        icone_topo="fa-weight-hanging",
                        icone_ociosidade="fa-solid fa-scale-unbalanced-flip",
                        titulo_ociosidade="Ociosidade de Peso",
                        tema="peso"
                    )


                with col_meio:
                    if resumo_ctrb_card:
                        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                        renderizar_gauge_ctrb_frete_global(
                            percentual=resumo_ctrb_card['percentual'],
                            qtd_viagens=resumo_ctrb_card['qtd_viagens'],
                            filtro_atual=desempenho_ctrb_sel
                        )

                with col_dir:
                    st.markdown(f"<div style='height: {deslocamento_ocupacao_lateral_px}px;'></div>", unsafe_allow_html=True)
                    renderizar_card_ocupacao_moderno(
                        titulo="Ocupação de Cubagem (M³)",
                        ocup_perc=dados_agregados['ocup_volume_perc'],
                        total_valor=dados_agregados['total_volume'],
                        cap_total=dados_agregados['cap_total_volume'],
                        unidade="M³",
                        ociosidade_perc=dados_agregados['ociosidade_volume_perc'],
                        potencial_nao_utilizado=dados_agregados['potencial_nao_utilizado_m3'],
                        icone_topo="fa-boxes-stacked",
                        icone_ociosidade="fa-solid fa-box-open",
                        titulo_ociosidade="Ociosidade de Cubagem",
                        tema="volume"
                    )
            else:
                if resumo_ctrb_card:
                    gauge_left, gauge_center, gauge_right = st.columns([1, 1.12, 1], gap="large")
                    with gauge_center:
                        renderizar_gauge_ctrb_frete_global(
                            percentual=resumo_ctrb_card['percentual'],
                            qtd_viagens=resumo_ctrb_card['qtd_viagens'],
                            filtro_atual=desempenho_ctrb_sel
                        )
                st.info(f"Nenhum dado de ocupação encontrado para '{selecionar_veiculo}' no período selecionado.")

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # CÓDIGO NOVO E CORRIGIDO

        # ==============================
        # 8. TABELA RESUMIDA E DETALHES DA VIAGEM (VERSÃO FINAL COM AGRUPAMENTO CORRIGIDO)
        # ==============================
        st.subheader("📋 Resumo das Viagens no Período")

        df_viagens = df_para_analise.copy()

        if not df_viagens.empty:
            if 'VIAGEM_ID' not in df_viagens.columns:
                df_viagens['VIAGEM_ID'] = df_viagens.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup() + 1
            
            def juntar_unicos(series):
                return ', '.join(series.dropna().astype(str).unique())

            # --- INÍCIO DA CORREÇÃO NO AGRUPAMENTO ---
            def obter_primeiro_valido(series):
                """
                Dentro de um grupo, encontra e retorna o primeiro valor que não é nulo/vazio.
                Isso garante que a placa da carreta seja capturada mesmo que não esteja na primeira linha.
                """
                for valor in series:
                    if pd.notna(valor) and str(valor).strip() != '' and str(valor).lower() != 'nan':
                        return valor
                return None # Retorna None se nenhum valor válido for encontrado

            # O agrupamento agora usa a nova função 'obter_primeiro_valido' para as placas
            resumo_viagens = df_viagens.groupby('VIAGEM_ID').agg(
                EMISSÃO=('EMIS_MANIF', 'first'),
                NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                SITUACAO=('SITUACAO', 'first'),
                CONFERENTE_CARGA=('CONFERENTE CARGA', 'first'), # <<< ADICIONE ESTA LINHA
                MOTORISTA=('MOTORISTA', 'first'),
                PLACA_CAVALO=('PLACA_CAVALO', 'first'),
                PLACA_CARRETA=('PLACA_CARRETA', obter_primeiro_valido), # <-- LÓGICA CORRIGIDA AQUI
                CAPAC_CAVALO=('CAPAC_CAVALO', 'first'),
                CAP_CARRETA=('CAPACIDADE_KG', 'first'), 
                TIPO_VEICULO=('TIPO_CAVALO', 'first'),
                DESTINOS=('DEST_MANIF', lambda x: ordenar_destinos_geograficamente(x.unique(), ROTAS_COMPOSTAS, ORDEM_DAS_ROTAS)),
                PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                CUSTO_OS_TOTAL=('OS-R$', 'max'),
                CUSTO_CTRB_TOTAL=('CTRB-R$', 'max'),
                FRETE_TOTAL=('FRETE-R$', 'sum'),
                NUM_OS_LISTA=('NUM_OS', juntar_unicos),
                NUM_CTRB_LISTA=('NUM_CTRB', juntar_unicos),
                ICMS=('ICMS-R$', 'sum'),
                PESO_KG=('Peso Cálculo (KG)', 'sum'),
                M3=('M3', 'sum'),
                VOLUMES=('VOLUMES', 'sum'),
                VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                ENTREGAS=('DEST_MANIF', 'nunique'),
                QTDE_CTRC=('QTDE_CTRC', 'sum')
            ).reset_index()
            # --- FIM DA CORREÇÃO NO AGRUPAMENTO ---

            resumo_viagens.rename(columns={
                'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 
                'TIPO_VEICULO': 'TIPO_CAVALO', 'DESTINOS': 'DEST_MANIF',
                'PROPRIETARIO': 'PROPRIETARIO_CAVALO', 'CUSTO_OS_TOTAL': 'OS-R$',
                'CUSTO_CTRB_TOTAL': 'CTRB-R$', 'FRETE_TOTAL': 'FRETE-R$',
                'NUM_OS_LISTA': 'NUM_OS', 'NUM_CTRB_LISTA': 'NUM_CTRB',
                'ICMS': 'ICMS-R$', 'PESO_KG': 'Peso Cálculo (KG)',
                'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
            }, inplace=True)

            def obter_capacidade_real_viagem(row):
                capacidade_carreta = row.get('CAP_CARRETA', 0)
                if pd.notna(capacidade_carreta) and capacidade_carreta > 0:
                    return capacidade_carreta
                else:
                    return row.get('CAPAC_CAVALO', 0)
            
            def obter_placa_veiculo_formatada(row):
                placa_cavalo = row.get('PLACA_CAVALO', 'N/A')
                placa_carreta = row.get('PLACA_CARRETA', 'N/A')
                
                if pd.notna(placa_carreta) and placa_carreta != 'nan' and placa_carreta != placa_cavalo:
                    return f"{placa_cavalo} / {placa_carreta}"
                else:
                    return placa_cavalo

            resumo_viagens['Capacidade (KG)'] = resumo_viagens.apply(obter_capacidade_real_viagem, axis=1)
            resumo_viagens['Veículo (Placa)'] = resumo_viagens.apply(obter_placa_veiculo_formatada, axis=1)

            # ✅ Ajusta VIAGEM para começar em 1 (como COLUNA, não índice)
            resumo_viagens = resumo_viagens.reset_index(drop=True)
            resumo_viagens['VIAGEM'] = range(1, len(resumo_viagens) + 1)

            def calcular_custo_final(row):
                custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                destinos_str = str(row.get('DEST_MANIF', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base

            def obter_numero_documento(row):
                return row['NUM_OS'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['NUM_CTRB']

            def calcular_distancia_viagem(row):
                custo_km_por_tipo = {'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75}
                tipo_veiculo = obter_tipo_veiculo_base(row) or 'PADRAO'
                valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                custo_viagem = row['Custo (CTRB/OS)']
                if valor_km > 0 and custo_viagem > 0:
                    return custo_viagem / valor_km
                return 0.0

            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_final, axis=1)
            resumo_viagens['Nº Documento Custo'] = resumo_viagens.apply(obter_numero_documento, axis=1)
            resumo_viagens['DISTANCIA'] = resumo_viagens.apply(calcular_distancia_viagem, axis=1)

            def calcular_ctrb_frete_numerico(row):
                try:
                    custo = float(row['Custo (CTRB/OS)'])
                    frete = float(row['FRETE-R$'])
                    return (custo / frete) * 100 if frete > 0 else 0.0
                except (ValueError, TypeError):
                    return 0.0

            resumo_viagens['CTRB/Frete (%)_valor'] = resumo_viagens.apply(calcular_ctrb_frete_numerico, axis=1)
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.0f}%")

            # Formatação final para exibição
            resumo_viagens['EMIS_MANIF'] = pd.to_datetime(resumo_viagens['EMIS_MANIF']).dt.strftime('%d/%m/%Y')
            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens['Custo (CTRB/OS)'].astype(float).apply(formatar_moeda)
            resumo_viagens['FRETE-R$'] = resumo_viagens['FRETE-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['ICMS-R$'] = resumo_viagens['ICMS-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['MERCADORIA-R$'] = resumo_viagens['MERCADORIA-R$'].astype(float).apply(formatar_moeda)
            candidatos_peso_calculo = [
                'Peso Cálculo (KG)', 'PESO CÁLCULO (KG)', 'PESO CALCULO (KG)',
                'PESO CALCULADO (KG)', 'PESO_CALCULO_KG', 'PESO REAL (KG)'
            ]
            coluna_peso_calculo = next((col for col in candidatos_peso_calculo if col in resumo_viagens.columns), None)
            if coluna_peso_calculo is None:
                resumo_viagens['Peso Cálculo (KG)'] = 0.0
            else:
                resumo_viagens['Peso Cálculo (KG)'] = pd.to_numeric(
                    resumo_viagens[coluna_peso_calculo], errors='coerce'
                ).fillna(0)
            resumo_viagens['Peso Cálculo (KG)'] = resumo_viagens['Peso Cálculo (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            resumo_viagens['M3'] = resumo_viagens['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))
            resumo_viagens['VOLUMES'] = resumo_viagens['VOLUMES'].astype(int)
            resumo_viagens['ENTREGAS'] = resumo_viagens['ENTREGAS'].astype(int)
            resumo_viagens['QTDE_CTRC'] = resumo_viagens['QTDE_CTRC'].astype(int)
            resumo_viagens['Capacidade (KG)'] = resumo_viagens['Capacidade (KG)'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg')
            resumo_viagens['DISTANCIA'] = resumo_viagens['DISTANCIA'].astype(float).apply(lambda x: f"{int(x):,} km".replace(",", "."))

            resumo_viagens.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto',
                'TIPO_CAVALO': 'TIPO', 'DEST_MANIF': 'DESTINOS', 'Nº Documento Custo': 'Nº CTRB/OS',
                'QTDE_CTRC': 'Qtd. CTRCs',
                'SITUACAO': 'SITUAÇÃO',
                'CONFERENTE_CARGA': 'CONFERENTE' # <<< ADICIONE ESTA LINHA
            }, inplace=True)

            # --- ORDEM FINAL DAS COLUNAS AJUSTADA CONFORME SOLICITADO ---
            ordem_final = [
                'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUAÇÃO',
                'CONFERENTE',
                'TIPO',
                'Veículo (Placa)',
                'MOTORISTA',
                'CTRB/Frete (%)',
                'DESTINOS',
                'DISTANCIA',
                'FRETE-R$',
                'Custo (CTRB/OS)',
                'ENTREGAS',
                'Peso Cálculo (KG)',
                'Capacidade (KG)',
                'M3',
                'Nº CTRB/OS',
                'ICMS-R$', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
            ]

            colunas_para_exibir = [col for col in ordem_final if col in resumo_viagens.columns]
            df_para_exibir = resumo_viagens[colunas_para_exibir].copy()

            df_para_exibir_ordenado = df_para_exibir.sort_values(by='VIAGEM', ascending=True)

            # 2. Define a função de cores que recebe o valor diretamente
            def colorir_celula_ctrb(valor_texto):
                """
                Recebe o valor da célula como texto (ex: "26%"), converte para número e retorna o estilo.
                - BOM (0 a 25%): Verde
                - REGULAR (26 a 45%): Amarelo
                - PÉSSIMO (>= 46%): Vermelho
                """
                try:
                    # Remove o '%' e converte para número
                    v = float(valor_texto.strip('%'))
                except (ValueError, TypeError):
                    return '' # Sem estilo se a célula estiver vazia ou não for um número

                if 0 <= v <= 25:
                    return 'background-color: #2E7D32; color: white;'
                elif 26 <= v <= 45:
                    return 'background-color: #FF8F00; color: white;'
                elif v >= 46:
                    return 'background-color: #C62828; color: white;'
                
                return '' # Cor padrão

            # 3. Aplica a função de estilo diretamente na coluna desejada
            #    O método .style.map() passa o valor de cada célula para a função.
            styled_df = df_para_exibir_ordenado.style.map(
                colorir_celula_ctrb,
                subset=['CTRB/Frete (%)']
            )

            # 4. Exibe o DataFrame estilizado
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # 5. Adiciona a legenda visual de cores logo abaixo da tabela
            st.markdown("""
            <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 20px; font-size: 14px;">
                <b style="color: #E0E0E0;">Legenda de Desempenho:</b>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                    <span style="color: #E0E0E0;">Bom </span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                    <span style="color: #E0E0E0;">Regular </span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                    <span style="color: #E0E0E0;">Péssimo </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")     

            try:
                excel_bytes_resumo = to_excel(resumo_viagens)
                st.download_button(
                    label="📥 Download Resumo (Excel)",
                    data=excel_bytes_resumo,
                    file_name="resumo_viagens_filtradas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_resumo"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel para o resumo: {e}")


        # =========================================================
        # 🔹 TABELA DE DETALHES (DOCUMENTOS)
        # =========================================================
        # A tabela detalhada aparecerá se uma VIAGEM ESPECÍFICA ou um GRUPO DE ROTAS for selecionado.
        if rota_sel_visivel != "(Todos)" or grupo_rota_sel != "(Todos)":
        
            # Adiciona um separador visual e um título para a nova seção
            st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)
            
            # Título dinâmico: muda conforme o filtro usado
            if rota_sel_visivel != "(Todos)":
                st.subheader("📄 Detalhes dos Documentos da Viagem")
            else: # Se chegou aqui, é porque o grupo_rota_sel foi usado
                st.subheader(f"📄 Detalhes dos Documentos do Grupo: {grupo_rota_sel}")

            # O 'df_filtrado' já contém os dados corretos para a viagem ou grupo de rotas selecionado.
            # Vamos criar uma cópia para trabalhar com segurança.
            df_detalhado_base = df_filtrado.copy()

            # 1. FUNÇÕES PARA UNIFICAR AS COLUNAS DE CUSTO
            def calcular_custo_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)

            def obter_numero_documento_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('NUM_OS', '')
                return row.get('NUM_CTRB', '')

            # 2. APLICA AS FUNÇÕES PARA CRIAR AS NOVAS COLUNAS UNIFICADAS
            df_detalhado_base['Custo (CTRB/OS)'] = df_detalhado_base.apply(calcular_custo_unificado, axis=1)
            df_detalhado_base['Nº CTRB/OS'] = df_detalhado_base.apply(obter_numero_documento_unificado, axis=1)

            # 3. DEFINE A LISTA FINAL DE COLUNAS PARA EXIBIR
            colunas_para_exibir_detalhe = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS', 'Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'Peso Cálculo (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            
            # 4. Garante que apenas colunas existentes sejam usadas
            colunas_existentes_detalhe = [col for col in colunas_para_exibir_detalhe if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes_detalhe].copy()

            # 5. Renomeia as colunas para uma apresentação mais limpa
            df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino', 'PLACA_CAVALO': 'PLACA', 'TIPO_CAVALO': 'TIPO', 
                'QTDE_CTRC': 'Qtd. CTRCs'
            }, inplace=True)

            # 6. Formata as colunas para exibição
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')
            
            colunas_moeda_det = ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)
            
            if 'Peso Cálculo (KG)' in df_detalhado_final.columns:
                df_detalhado_final['Peso Cálculo (KG)'] = df_detalhado_final['Peso Cálculo (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].apply(lambda x: x / 10000 if x > 1000 else x).apply(lambda x: formatar_numero(x, 3))

            # 7. Exibe a tabela final
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)
            
            # 8. Adiciona o botão de download
            try:
                excel_bytes_detalhado = to_excel(df_detalhado_base[colunas_existentes_detalhe])
                nome_arquivo = f"detalhes_{grupo_rota_sel.replace('/', '_') if grupo_rota_sel != '(Todos)' else 'viagem_especifica'}.xlsx"

                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado_tab1"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel detalhado: {e}")

                # ▼▼▼ INSIRA ESTE BLOCO DE CÓDIGO COMPLETO AQUI ▼▼▼

# ==================================================================
# ABA 2 (ANÁLISE FINANCEIRA)
# ==================================================================
with tab2:
    # Título estilizado para a aba
    st.markdown("""
        <div class="title-block-financeira">
            <i class="fa-solid fa-coins"></i>
            <h2>Análise Financeira Avançada</h2>
        </div>
    """, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # KPIs financeiros que foram movidos da primeira aba
        kpi_f1, kpi_f2, kpi_f3, kpi_f4, kpi_f5 = st.columns(5)

        # Lógica para determinar o título do KPI de Custo
        titulo_kpi_custo = "📄 Custo CTRB / OS" # Título padrão
        if not df_filtrado.empty:
            if df_filtrado['PROPRIETARIO_CAVALO'].nunique() > 1:
                titulo_kpi_custo = "📄 Custo CTRB / OS"
            elif df_filtrado['PROPRIETARIO_CAVALO'].iloc[0] == 'KM TRANSPORTES ROD. DE CARGAS LTDA':
                titulo_kpi_custo = "📄 Custo CTRB"
            elif df_filtrado['PROPRIETARIO_CAVALO'].iloc[0] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                titulo_kpi_custo = "📋 Custo OS"

        # Dicionário com os KPIs financeiros em estilo premium
        kpis_financeiros = [
            {"coluna": kpi_f1, "titulo": "Receita Total", "valor": formatar_moeda(receita_total), "classe": "receita", "icone": "fa-sack-dollar", "rodape": "Entrada total", "variacao": variacoes_financeiras.get("receita_total"), "modo_variacao": "higher_better"},
            {"coluna": kpi_f2, "titulo": titulo_kpi_custo.replace("📄 ", "").replace("📋 ", ""), "valor": formatar_moeda(custo_ctrb_os), "classe": "custo", "icone": "fa-file-invoice-dollar", "rodape": "Custo base", "variacao": variacoes_financeiras.get("custo_ctrb_os"), "modo_variacao": "lower_better"},
            {"coluna": kpi_f3, "titulo": "ICMS", "valor": formatar_moeda(custo_icms), "classe": "custo", "icone": "fa-receipt", "rodape": "Tributação", "variacao": variacoes_financeiras.get("custo_icms"), "modo_variacao": "lower_better"},
            {"coluna": kpi_f4, "titulo": "Custo Total", "valor": formatar_moeda(custo_total), "classe": "custo", "icone": "fa-wallet", "rodape": "CTRB + ICMS", "variacao": variacoes_financeiras.get("custo_total"), "modo_variacao": "lower_better"},
            {"coluna": kpi_f5, "titulo": "Lucro Líquido", "valor": formatar_moeda(lucro_estimado), "classe": "lucro", "icone": "fa-chart-line", "rodape": "Resultado final", "variacao": variacoes_financeiras.get("lucro_estimado"), "modo_variacao": "higher_better"}
        ]

        # Itera e exibe cada KPI
        for info in kpis_financeiros:
            with info['coluna']:
                render_financial_kpi_card(
                    titulo=info['titulo'],
                    valor=info['valor'],
                    classe=info['classe'],
                    icone=info['icone'],
                    rodape=info['rodape'],
                    variacao_percentual=info.get('variacao'),
                    modo_variacao=info.get('modo_variacao', 'higher_better'),
                    variacao_label=info.get('variacao_label', variacao_label_financeira)
                )
        
        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
        
        # Futuramente, você pode adicionar gráficos e outras análises aqui.
        # st.info("Área reservada para gráficos de análise financeira.")

# ==================================================================
# ABA 3 (PERFORMANCE DA FROTA) - COM ESTILO E COR ATUALIZADOS
# ==================================================================
with tab3:
    # --- CSS E HTML PARA O TÍTULO PERSONALIZADO ---
    st.markdown("""
    <style>
        .title-block-performance {
            /* ▼▼▼ COR DE FUNDO ATUALIZADA AQUI ▼▼▼ */
            background: #1C1A29; /* Azul/Roxo bem escuro, como na imagem */
            
            /* Bordas laterais na cor laranja para combinar com o tema */
            border-left: 5px solid #f97316;
            border-right: 5px solid #f97316;
            
            padding: 5px 30px; /* Espaçamento interno */
            margin: 10px 0 25px 0; /* Margem para separar do conteúdo */
            border-radius: 12px; /* Bordas arredondadas */
            width: 100%;
            box-sizing: border-box;
            
            /* Centraliza o ícone e o texto */
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px; /* Espaço entre o ícone e o texto */
            
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); /* Sombra suave */
        }

        .title-block-performance h2 {
            font-family: "Poppins", "Segoe UI", sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff; /* Cor do texto */
            margin: 0;
            letter-spacing: 0.5px;
        }

        .title-block-performance .fa-bolt-lightning {
            font-size: 2.0rem; /* Tamanho do ícone */
            color: #f97316; /* Cor do ícone (laranja) */
        }
    </style>
    
    <div class="title-block-performance">
        <i class="fa-solid fa-bolt-lightning"></i>
        <h2>Performance da Frota: Frota vs. Terceiros</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # --- SELETOR DE PROPRIETÁRIO ---
        selecao_proprietario = option_menu(
            menu_title=None,
            options=["TODOS", "FROTA KM", "TERCEIROS"],
            icons=["collection-fill", "building", "person-badge"],
            menu_icon="cast", default_index=0, orientation="horizontal",
            key="select_proprietario_tab3", # Chave única para evitar erro de ID duplicado
            styles={
                "container": {"padding": "6px", "background-color": "rgba(30, 30, 40, 0.4)", "border-radius": "16px", "justify-content": "center"},
                "icon": {"color": "#FFFFFF", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "font-weight": "600", "color": "#E5E7EB", "padding": "10px 26px", "border-radius": "12px", "margin": "0px 6px", "background-color": "rgba(255, 255, 255, 0.05)"},
                "nav-link:hover": {"background-color": "rgba(255,255,255,0.12)", "color": "#fff"},
                "nav-link-selected": {"background": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)", "color": "white"},
            }
        )

        # --- ▼▼▼ LÓGICA DE FILTRAGEM CORRIGIDA E CENTRALIZADA ▼▼▼ ---
        # Começa com o df_filtrado (que já vem da sidebar) e aplica o filtro desta aba
        df_viagens = df_filtrado.copy()
        if selecao_proprietario == "FROTA KM":
            df_viagens = df_viagens[df_viagens['PROPRIETARIO_CAVALO'] == 'KM TRANSPORTES ROD. DE CARGAS LTDA']
        elif selecao_proprietario == "TERCEIROS":
            df_viagens = df_viagens[df_viagens['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME']
        # Se 'TODOS' estiver selecionado, df_viagens permanece como uma cópia completa de df_filtrado.

        # --- 4. CÁLCULO E EXIBIÇÃO DOS KPIs ---
        if not df_viagens.empty:
            # Adiciona VIAGEM_ID ao df_viagens JÁ FILTRADO
            df_viagens["VIAGEM_ID"] = df_viagens.groupby(["MOTORISTA", "PLACA_CAVALO", "DIA_EMISSAO_STR"], sort=False).ngroup() + 1
            
            # Define capacidades
            capacidades = {
                'TOCO': {'peso_kg': 10000, 'volume_m3': 55}, 'TRUCK': {'peso_kg': 16000, 'volume_m3': 75},
                'CAVALO': {'peso_kg': 25000, 'volume_m3': 110}, 'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
            }
            df_viagens['CAPACIDADE_PESO'] = df_viagens.get('TIPO_CAVALO_ORIGINAL', df_viagens['TIPO_CAVALO']).map(lambda x: capacidades.get(str(x).upper(), capacidades['PADRAO'])['peso_kg'])

            # Agrupa por viagem para obter os valores corretos para os cálculos
            resumo_por_viagem = df_viagens.groupby('VIAGEM_ID').agg(
                FRETE_VIAGEM=('FRETE-R$', 'sum'), CUSTO_OS=('OS-R$', 'max'),
                CUSTO_CTRB=('CTRB-R$', 'max'), PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                TIPO_VEICULO=('TIPO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
                PESO_VIAGEM=('Peso Cálculo (KG)', 'sum'), ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'),
                CAPACIDADE_PESO_VIAGEM=('CAPACIDADE_PESO', 'first')
            ).reset_index()

            # Função para calcular o custo ajustado por viagem
            def calcular_custo_ajustado_viagem(row):
                custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                destinos_str = str(row.get('DESTINOS', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str:
                    return custo_base / 2
                return custo_base
            resumo_por_viagem['CUSTO_AJUSTADO'] = resumo_por_viagem.apply(calcular_custo_ajustado_viagem, axis=1)

            # --- DISTÂNCIA TOTAL UNIFICADA (SOMA DAS VIAGENS INDIVIDUAIS) ---
            custo_km_por_tipo = {
                'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75, 'PADRAO': 0
            }

            # Função para calcular a distância de uma única viagem
            def calcular_distancia_individual(row):
                tipo_veiculo = str(row.get('TIPO_VEICULO', 'PADRAO')).upper()
                valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                custo_viagem = row['CUSTO_AJUSTADO']
                
                if valor_km > 0 and custo_viagem > 0:
                    return custo_viagem / valor_km
                return 0.0

            # Aplica a função para criar uma nova coluna de distância em cada viagem
            resumo_por_viagem['DISTANCIA_VIAGEM'] = resumo_por_viagem.apply(calcular_distancia_individual, axis=1)

            # A distância total agora é a SOMA das distâncias de cada viagem
            distancia_total = resumo_por_viagem['DISTANCIA_VIAGEM'].sum()


            # --- CÁLCULOS COMPLEMENTARES ---
            total_viagens = resumo_por_viagem['VIAGEM_ID'].nunique()
            distancia_media = distancia_total / total_viagens if total_viagens > 0 else 0

            # Conta uma entrega para cada destino em cada viagem
            # --- Contagem de entregas idêntica à aba "Visão Geral" ---
            if not df_viagens.empty:
                entregas_por_viagem = df_viagens.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR'])['DEST_MANIF'].nunique()
                total_entregas = entregas_por_viagem.sum()
            else:
                total_entregas = 0

            peso_total = resumo_por_viagem['PESO_VIAGEM'].sum()
            peso_medio_viagem = peso_total / total_viagens if total_viagens > 0 else 0
            
            capacidade_total = resumo_por_viagem['CAPACIDADE_PESO_VIAGEM'].sum()
            ocupacao_media = (peso_total / capacidade_total * 100) if capacidade_total > 0 else 0
            
            custo_total_kpi = custo_ctrb_os
            frete_total_kpi = resumo_por_viagem['FRETE_VIAGEM'].sum()
            perc_custo_frete = (custo_total_kpi / frete_total_kpi * 100) if frete_total_kpi > 0 else 0

            # Funções de formatação e exibição dos KPIs
            def fmt_num_kpi(v, suf=""): return f"{v:,.0f}{suf}".replace(",", ".")
            def fmt_perc_kpi(v): return f"{v:.0f}%"

            # ▼▼▼ CÓDIGO ATUALIZADO ▼▼▼
            kpi_view = option_menu(
                menu_title=None,
                options=["Médias e Índices", "Valores Totais"],
                icons=["graph-up-arrow", "calculator"],
                menu_icon="cast", 
                default_index=0, 
                orientation="horizontal",
                key="kpi_view_selector_tab3", # Chave única
                styles={
                    # 🔹 Container principal (fundo translúcido com leve blur)
                    "container": {
                        "padding": "6px",
                        "background-color": "rgba(30, 30, 40, 0.4)", # Fundo semi-transparente
                        "border-radius": "16px",
                        "backdrop-filter": "blur(10px)", # Efeito de vidro
                        "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.3)",
                        "justify-content": "center",
                        "margin-bottom": "25px", # Mantém a margem inferior
                    },
                    # 🔹 Ícones
                    "icon": {
                        "color": "#A3A3A3",
                        "font-size": "16px", # Ajustado para consistência
                    },
                    # 🔹 Botões inativos
                    "nav-link": {
                        "font-size": "14px",
                        "font-weight": "600",
                        "color": "#E5E7EB",
                        "padding": "10px 26px",
                        "border-radius": "12px",
                        "margin": "0px 6px",
                        "background-color": "rgba(255, 255, 255, 0.05)", # Fundo sutil
                        "transition": "all 0.4s ease-in-out", # Animação suave
                    },
                    # 🔹 Efeito hover (passar o mouse)
                    "nav-link:hover": {
                        "background-color": "rgba(255, 255, 255, 0.12)",
                        "color": "#fff",
                        "transform": "translateY(-2px)",
                    },
                    # 🔹 Botão selecionado — Estilo refinado com brilho
                    "nav-link-selected": {
                        "background-color": "#222433", # Fundo escuro
                        "color": "#FFFFFF",           # Texto branco
                        "border": "1.5px solid #f97316", # Borda laranja (cor da aba)
                        "box-shadow": "0 0 15px rgba(249, 115, 22, 0.6)", # Brilho (glow) laranja
                        "transform": "translateY(-2px)",
                    },
                }
            )
            # ▲▲▲ FIM DO CÓDIGO ATUALIZADO ▲▲▲


            kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

            if kpi_view == 'Médias e Índices':
                kpis_data = {
                    kpi1: {"titulo": "TOTAL DE VIAGENS", "valor": fmt_num_kpi(total_viagens), "icone": "fa-route", "rodape": "Saídas consolidadas"},
                    kpi2: {"titulo": "DISTÂNCIA MÉDIA", "valor": fmt_num_kpi(distancia_media, " km"), "icone": "fa-road", "rodape": "Média por viagem"},
                    kpi3: {"titulo": "TOTAL DE ENTREGAS", "valor": fmt_num_kpi(total_entregas), "icone": "fa-boxes-stacked", "rodape": "Destinos atendidos"},
                    kpi4: {"titulo": "PESO MÉDIO / VIAGEM", "valor": fmt_num_kpi(peso_medio_viagem, " kg"), "icone": "fa-weight-hanging", "rodape": "Carga média"},
                    kpi5: {"titulo": "OCUPAÇÃO MÉDIA", "valor": fmt_perc_kpi(ocupacao_media), "icone": "fa-chart-column", "rodape": "Eficiência de carga"},
                    kpi6: {"titulo": "CTRB / FRETE", "valor": fmt_perc_kpi(perc_custo_frete), "icone": "fa-scale-balanced", "rodape": "Relação de custo"},
                }
            else:  # kpi_view == 'Valores Totais'
                kpis_data = {
                    kpi1: {"titulo": "TOTAL DE VIAGENS", "valor": fmt_num_kpi(total_viagens), "icone": "fa-route", "rodape": "Saídas consolidadas"},
                    kpi2: {"titulo": "DISTÂNCIA TOTAL", "valor": f"{int(distancia_total):,} km".replace(",", "."), "icone": "fa-map-location-dot", "rodape": "Percurso acumulado"},
                    kpi3: {"titulo": "TOTAL DE ENTREGAS", "valor": fmt_num_kpi(total_entregas), "icone": "fa-boxes-stacked", "rodape": "Destinos atendidos"},
                    kpi4: {"titulo": "PESO TOTAL", "valor": fmt_num_kpi(peso_total, " kg"), "icone": "fa-weight-hanging", "rodape": "Carga total"},
                    kpi5: {"titulo": "CUSTO TOTAL (CTRB/OS)", "valor": formatar_moeda(custo_total_kpi), "icone": "fa-money-check-dollar", "rodape": "Custo consolidado"},
                    kpi6: {"titulo": "FRETE TOTAL", "valor": formatar_moeda(frete_total_kpi), "icone": "fa-sack-dollar", "rodape": "Receita apurada"},
                }

            for coluna, info in kpis_data.items():
                with coluna:
                    render_performance_reference_kpi_card(
                        titulo=info['titulo'],
                        valor=info['valor'],
                        icone=info['icone'],
                        rodape=info['rodape']
                    )

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # --- TABELA DE RESUMO DAS VIAGENS ---
        titulo_tabela_resumo = f"### 📋 Resumo das Viagens ({selecao_proprietario})"
        st.markdown(titulo_tabela_resumo)

        if not df_viagens.empty:

            def juntar_unicos(series): return ', '.join(series.dropna().astype(str).unique())
            resumo_viagens = df_viagens.groupby('VIAGEM_ID').agg(
                EMISSÃO=('EMIS_MANIF', 'first'),
                NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                SITUACAO=('SITUACAO', 'first'), MOTORISTA=('MOTORISTA', 'first'),
                PLACA_CAVALO=('PLACA_CAVALO', 'first'), PLACA_CARRETA=('PLACA_CARRETA', 'first'),
                TIPO_VEICULO=('TIPO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
                PROPRIETARIO_CAVALO=('PROPRIETARIO_CAVALO', 'first'), # <-- MUDANÇA: Nome da coluna original
                CUSTO_OS_TOTAL=('OS-R$', 'max'),
                CUSTO_CTRB_TOTAL=('CTRB-R$', 'max'), FRETE_TOTAL=('FRETE-R$', 'sum'),
                ICMS=('ICMS-R$', 'sum'), PESO_KG=('Peso Cálculo (KG)', 'sum'), M3=('M3', 'sum'),
                VOLUMES=('VOLUMES', 'sum'), VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                ENTREGAS=('DEST_MANIF', 'nunique'), QTDE_CTRC=('QTDE_CTRC', 'sum')
            ).reset_index()

            # Renomeia colunas para processamento
            resumo_viagens.rename(columns={
                'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 'TIPO_VEICULO': 'TIPO_CAVALO', 
                'DESTINOS': 'DEST_MANIF', 'CUSTO_OS_TOTAL': 'OS-R$', 'CUSTO_CTRB_TOTAL': 'CTRB-R$', 
                'FRETE_TOTAL': 'FRETE-R$', 'ICMS': 'ICMS-R$', 'PESO_KG': 'Peso Cálculo (KG)', 
                'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
            }, inplace=True)

            # Funções de cálculo
            def calcular_custo_final(row):
                custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                destinos_str = str(row.get('DEST_MANIF', '')).upper()
                if 'GYN' in destinos_str or 'SPO' in destinos_str: return custo_base / 2
                return custo_base
            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_final, axis=1)

            def calcular_ctrb_frete_numerico(row):
                try:
                    custo = float(row['Custo (CTRB/OS)'])
                    frete = float(row['FRETE-R$'])
                    return (custo / frete) * 100 if frete > 0 else 0.0
                except (ValueError, TypeError): return 0.0
            resumo_viagens['CTRB/Frete (%)_valor'] = resumo_viagens.apply(calcular_ctrb_frete_numerico, axis=1)
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.0f}%")

            # Formatação para exibição
            resumo_viagens['EMIS_MANIF'] = pd.to_datetime(resumo_viagens['EMIS_MANIF']).dt.strftime('%d/%m/%Y')
            resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens['Custo (CTRB/OS)'].astype(float).apply(formatar_moeda)
            resumo_viagens['FRETE-R$'] = resumo_viagens['FRETE-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['ICMS-R$'] = resumo_viagens['ICMS-R$'].astype(float).apply(formatar_moeda)
            resumo_viagens['MERCADORIA-R$'] = resumo_viagens['MERCADORIA-R$'].astype(float).apply(formatar_moeda)
            candidatos_peso_calculo = [
                'Peso Cálculo (KG)', 'PESO CÁLCULO (KG)', 'PESO CALCULO (KG)',
                'PESO CALCULADO (KG)', 'PESO_CALCULO_KG', 'PESO REAL (KG)'
            ]
            coluna_peso_calculo = next((col for col in candidatos_peso_calculo if col in resumo_viagens.columns), None)
            if coluna_peso_calculo is None:
                resumo_viagens['Peso Cálculo (KG)'] = 0.0
            else:
                resumo_viagens['Peso Cálculo (KG)'] = pd.to_numeric(
                    resumo_viagens[coluna_peso_calculo], errors='coerce'
                ).fillna(0)
            resumo_viagens['Peso Cálculo (KG)'] = resumo_viagens['Peso Cálculo (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            resumo_viagens['M3'] = resumo_viagens['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))
            resumo_viagens['VOLUMES'] = resumo_viagens['VOLUMES'].astype(int)
            resumo_viagens['ENTREGAS'] = resumo_viagens['ENTREGAS'].astype(int)
            resumo_viagens['QTDE_CTRC'] = resumo_viagens['QTDE_CTRC'].astype(int)
            
            # Renomeia colunas para exibição final
            resumo_viagens.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'TIPO_CAVALO': 'TIPO', 
                'DEST_MANIF': 'DESTINOS', 'QTDE_CTRC': 'Qtd. CTRCs', 'SITUACAO': 'SITUAÇÃO',
                'PROPRIETARIO_CAVALO': 'PROPRIETÁRIO' # <-- MUDANÇA 1: Renomeia a coluna para exibição
            }, inplace=True)

            # ▼▼▼ MUDANÇA 2: Adiciona 'PROPRIETÁRIO' na ordem de exibição ▼▼▼
            ordem_final = [
                'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUACAO', 'MOTORISTA', 'DESTINOS', 
                'ENTREGAS', 'TIPO', 
                'PROPRIETÁRIO', # <-- COLUNA ADICIONADA AQUI
                'PLACA_CAVALO', 'PLACA_CARRETA', 'Custo (CTRB/OS)', 'CTRB/Frete (%)', 
                'FRETE-R$', 'ICMS-R$', 'Peso Cálculo (KG)', 'M3', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
            ]
            # ▲▲▲ FIM DA MUDANÇA 2 ▲▲▲

            colunas_para_exibir = [col for col in ordem_final if col in resumo_viagens.columns]
            df_para_exibir = resumo_viagens[colunas_para_exibir].copy()

            # ▼▼▼ INÍCIO DA MUDANÇA: APLICA A FUNÇÃO PARA ENCURTAR O NOME ▼▼▼
            def encurtar_proprietario(nome):
                if 'MARCELO H LEMOS' in nome:
                    return 'MARCELO LEMOS BERALDO'
                if 'KM TRANSPORTES' in nome:
                    return 'KM TRANSPORTES'
                return nome # Retorna o nome original se não for nenhum dos dois

            df_para_exibir['PROPRIETÁRIO'] = df_para_exibir['PROPRIETÁRIO'].apply(encurtar_proprietario)
            # ▲▲▲ FIM DA MUDANÇA ▲▲▲

            styled_df = df_para_exibir.style.background_gradient(cmap='Reds', subset=['CTRB/Frete (%)'], gmap=resumo_viagens['CTRB/Frete (%)_valor'])
            
            # Exibição da tabela de resumo
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Botão de download do resumo
            excel_bytes_resumo = to_excel(df_para_exibir)
            st.download_button(
                label=f"📤 Exportar Resumo ({selecao_proprietario})", data=excel_bytes_resumo,
                file_name=f"resumo_performance_{selecao_proprietario}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_tab3_resumo_{selecao_proprietario}"
            )

            # --- ▼▼▼ BLOCO ATUALIZADO: TABELA DE DADOS DETALHADOS ▼▼▼ ---
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
            titulo_tabela_detalhada = f"### 📄 Dados Detalhados das Viagens ({selecao_proprietario})"
            st.markdown(titulo_tabela_detalhada)

            # Usamos o DataFrame 'df_viagens', que já está filtrado por Frota ou Terceiros
            df_detalhado_base = df_viagens.copy()

            # 1. Funções para unificar as colunas de custo
            def calcular_custo_unificado(row):
                """Retorna o valor de OS-R$ para TERCEIROS e CTRB-R$ para os demais."""
                if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)

            def obter_numero_documento_unificado(row):
                """Retorna o NUM_OS para TERCEIROS e NUM_CTRB para os demais."""
                if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('NUM_OS', '')
                return row.get('NUM_CTRB', '')

            # 2. Aplica as funções para criar as novas colunas unificadas
            df_detalhado_base['Custo CTRB/OS'] = df_detalhado_base.apply(calcular_custo_unificado, axis=1)
            df_detalhado_base['Nº CTRB/OS'] = df_detalhado_base.apply(obter_numero_documento_unificado, axis=1)

            # 3. Define a lista de colunas que você quer exibir, incluindo as novas
            colunas_para_exibir = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS',          # <-- Coluna unificada
                'Custo CTRB/OS',       # <-- Coluna unificada
                'FRETE-R$', 'ICMS-R$', 'Peso Cálculo (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]

            # 4. Garante que apenas colunas existentes sejam usadas para evitar erros
            colunas_existentes = [col for col in colunas_para_exibir if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes].copy()

            # 5. Renomeia as colunas para uma apresentação mais limpa
            df_detalhado_final = df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO',
                'NUM_MANIF': 'Nº Manifesto',
                'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino',
                'PLACA_CAVALO': 'PLACA',
                'TIPO_CAVALO': 'TIPO',
                'QTDE_CTRC': 'Qtd. CTRCs'
            })

            # 6. Formata os valores (data, moeda, peso, etc.)
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')

            # Formata todas as colunas de moeda, incluindo a nova coluna de custo
            colunas_moeda = ['Custo CTRB/OS', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)

            # Formata peso e M3
            if 'Peso Cálculo (KG)' in df_detalhado_final.columns:
                df_detalhado_final['Peso Cálculo (KG)'] = df_detalhado_final['Peso Cálculo (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))

            # 7. Exibe a tabela detalhada final com as colunas corretas
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)

            # 8. Botão de download para os dados detalhados (agora com as colunas unificadas)
            excel_bytes_detalhado = to_excel(df_detalhado_final)
            st.download_button(
                label=f"📤 Exportar Detalhes ({selecao_proprietario})",
                data=excel_bytes_detalhado,
                file_name=f"detalhes_viagens_{selecao_proprietario}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_tab3_detalhes_{selecao_proprietario}"
            )
            # --- ▲▲▲ FIM DO BLOCO ATUALIZADO ▲▲▲ ---

        else:
            st.info(f"Nenhuma viagem encontrada para o grupo '{selecao_proprietario}' no período selecionado.")


with tab4:
    # Adicione a importação do Altair no início do seu script
    import altair as alt

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # -----------------------------
        # 1️⃣ PREPARAÇÃO DE DADOS E KPIs (sem alterações)
        # -----------------------------
        df_aux = df_filtrado.copy()
        df_aux["DATA_EMISSAO"] = df_aux["EMIS_MANIF"].dt.date
        df_aux["VIAGEM_ID"] = df_aux.groupby(["MOTORISTA", "PLACA_CAVALO", "DATA_EMISSAO"], sort=False).ngroup() + 1

        capacidades = {
            'TOCO': {'peso_kg': 10000, 'volume_m3': 55}, 'TRUCK': {'peso_kg': 16000, 'volume_m3': 75},
            'CAVALO': {'peso_kg': 25000, 'volume_m3': 110}, 'PADRAO': {'peso_kg': 25000, 'volume_m3': 80}
        }
        df_aux['CAPACIDADE_PESO'] = df_aux.get('TIPO_CAVALO_ORIGINAL', df_aux['TIPO_CAVALO']).map(lambda x: capacidades.get(str(x).upper(), capacidades['PADRAO'])['peso_kg'])

        # Mantém a mesma regra de custo de transferência usada no painel geral:
        # usa CTRB ou OS por viagem e divide por 2 nas rotas GYN/SPO.
        resumo_por_viagem = df_aux.groupby('VIAGEM_ID').agg(
            MOTORISTA=('MOTORISTA', 'first'),
            PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
            FRETE_VIAGEM=('FRETE-R$', 'sum'),
            CUSTO_OS=('OS-R$', 'max'),
            CUSTO_CTRB=('CTRB-R$', 'max'),
            DESTINOS=('DEST_MANIF', lambda x: ' / '.join(pd.Series(x).dropna().astype(str).unique())),
            PESO_VIAGEM=('Peso Cálculo (KG)', 'sum'),
            ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'),
            CAPACIDADE_PESO_VIAGEM=('CAPACIDADE_PESO', 'first'),
            DISTANCIA_ESTIMADA=('DISTANCIA_ESTIMADA_KM', 'first')
        ).reset_index()

        def calcular_custo_transferencia_viagem(row):
            custo_base = row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']
            destinos_str = str(row.get('DESTINOS', '')).upper()
            if 'GYN' in destinos_str or 'SPO' in destinos_str:
                return custo_base / 2
            return custo_base

        resumo_por_viagem['CUSTO_UNICO_VIAGEM'] = resumo_por_viagem.apply(calcular_custo_transferencia_viagem, axis=1)

        resumo_motorista = resumo_por_viagem.groupby('MOTORISTA').agg(
            TOTAL_VIAGENS=('VIAGEM_ID', 'nunique'),
            FRETE_TOTAL=('FRETE_VIAGEM', 'sum'),
            CUSTO_TRANSFERENCIA_TOTAL=('CUSTO_UNICO_VIAGEM', 'sum'),
            PESO_TOTAL=('PESO_VIAGEM', 'sum'),
            TOTAL_ENTREGAS=('ENTREGAS_VIAGEM', 'sum'),
            CAPACIDADE_TOTAL_PESO=('CAPACIDADE_PESO_VIAGEM', 'sum'),
            DISTANCIA_TOTAL=('DISTANCIA_ESTIMADA', 'sum')
        ).reset_index()

        resumo_motorista["DISTANCIA_MEDIA_VIAGEM"] = (resumo_motorista["DISTANCIA_TOTAL"] / resumo_motorista["TOTAL_VIAGENS"]).fillna(0)
        resumo_motorista["MEDIA_ENTREGAS_VIAGEM"] = (resumo_motorista["TOTAL_ENTREGAS"] / resumo_motorista["TOTAL_VIAGENS"]).fillna(0)
        resumo_motorista["PESO_MEDIO_VIAGEM"] = (resumo_motorista["PESO_TOTAL"] / resumo_motorista["TOTAL_VIAGENS"]).fillna(0)
        resumo_motorista["OCUPACAO_MEDIA_CARGA"] = (resumo_motorista["PESO_TOTAL"] / resumo_motorista["CAPACIDADE_TOTAL_PESO"] * 100).fillna(0)
        resumo_motorista["PERC_CUSTO_FRETE"] = (resumo_motorista["CUSTO_TRANSFERENCIA_TOTAL"] / resumo_motorista["FRETE_TOTAL"] * 100).fillna(0)

        if motorista_sel != "(Todos)" and motorista_sel in resumo_motorista["MOTORISTA"].values:
            df_motorista = df_aux[df_aux["MOTORISTA"] == motorista_sel]
            dados_m = resumo_motorista[resumo_motorista["MOTORISTA"] == motorista_sel].iloc[0]
        else:
            df_motorista = df_aux.copy()
            dados_m = pd.Series({
                "TOTAL_VIAGENS": resumo_motorista["TOTAL_VIAGENS"].sum(), "TOTAL_ENTREGAS": resumo_motorista["TOTAL_ENTREGAS"].sum(),
                "DISTANCIA_MEDIA_VIAGEM": resumo_motorista["DISTANCIA_TOTAL"].sum() / resumo_motorista["TOTAL_VIAGENS"].sum() if resumo_motorista["TOTAL_VIAGENS"].sum() > 0 else 0,
                "MEDIA_ENTREGAS_VIAGEM": resumo_motorista["TOTAL_ENTREGAS"].sum() / resumo_motorista["TOTAL_VIAGENS"].sum() if resumo_motorista["TOTAL_VIAGENS"].sum() > 0 else 0,
                "PESO_MEDIO_VIAGEM": resumo_motorista["PESO_TOTAL"].sum() / resumo_motorista["TOTAL_VIAGENS"].sum() if resumo_motorista["TOTAL_VIAGENS"].sum() > 0 else 0,
                "OCUPACAO_MEDIA_CARGA": resumo_motorista["PESO_TOTAL"].sum() / resumo_motorista["CAPACIDADE_TOTAL_PESO"].sum() * 100 if resumo_motorista["CAPACIDADE_TOTAL_PESO"].sum() > 0 else 0,
                "PERC_CUSTO_FRETE": resumo_motorista["CUSTO_TRANSFERENCIA_TOTAL"].sum() / resumo_motorista["FRETE_TOTAL"].sum() * 100 if resumo_motorista["FRETE_TOTAL"].sum() > 0 else 0,
            })

        # --- BLOCO DE IDENTIFICAÇÃO DO MOTORISTA (ATUALIZADO) ---
        if motorista_sel != "(Todos)":
            st.markdown("### <i class='fa-solid fa-id-card-clip'></i> Identificação do Motorista", unsafe_allow_html=True)
            
            # Inicializa as variáveis para o caso de o dataframe estar vazio
            placa_frequente, tipo_veiculo_frequente, destino_frequente, ultima_viagem_data = "N/A", "N/A", "N/A", "N/A"
            capacidade_kg_frequente = 0

            if not df_motorista.empty:
                placa_frequente = df_motorista['PLACA_CAVALO'].mode()[0]
                tipo_veiculo_frequente = df_motorista['TIPO_CAVALO'].mode()[0]
                destino_frequente = df_motorista['CIDADE_UF_DEST'].mode()[0]
                ultima_viagem_data = df_motorista['EMIS_MANIF'].max().strftime('%d/%m/%Y')
                
                # Busca a capacidade correspondente ao tipo de veículo
                capacidade_info = capacidades.get(str(tipo_veiculo_frequente).upper(), capacidades['PADRAO'])
                capacidade_kg_frequente = capacidade_info['peso_kg']

            # Layout com 5 colunas
            id1, id2, id3, id4, id5 = st.columns(5)
            
            with id1:
                partes_nome = motorista_sel.split()
                nome_formatado = f"{partes_nome[0]} {partes_nome[1]}" if len(partes_nome) > 1 else motorista_sel
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-user-tie'></i> Motorista</div><div class='kpi-value'>{nome_formatado}</div></div>", unsafe_allow_html=True)
            
            with id2:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-truck'></i> Veículo Frequente</div><div class='kpi-value'>{placa_frequente}</div></div>", unsafe_allow_html=True)
            
            # ▼▼▼ KPI CORRIGIDO PARA FICAR EM UMA ÚNICA LINHA ▼▼▼
            with id3:
                # Formata a capacidade para exibição
                capacidade_formatada = f"Cap. {formatar_numero(capacidade_kg_frequente)} kg"
                
                st.markdown(f"""
                    <div class='kpi-container' style='text-align: center;'>
                        <div class='kpi-title'><i class='fa-solid fa-gear'></i> Tipo / Capacidade</div>
                        <div class='kpi-value'>
                            {tipo_veiculo_frequente} - <span style='font-size: 1rem; color: #d1d5db; font-weight: 500;'>{capacidade_formatada}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with id4:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-map-location-dot'></i> Destino Frequente</div><div class='kpi-value'>{destino_frequente}</div></div>", unsafe_allow_html=True)
            
            with id5:
                st.markdown(f"<div class='kpi-container' style='text-align: center;'><div class='kpi-title'><i class='fa-solid fa-calendar-days'></i> Última Viagem</div><div class='kpi-value'>{ultima_viagem_data}</div></div>", unsafe_allow_html=True)
            
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # --- PAINEL EXECUTIVO / HERO DA ABA DE MOTORISTAS ---
        def fmt_num(v, suf=""): return f"{v:,.0f}{suf}".replace(",", ".")
        def fmt_perc(v): return f"{v:.0f}%".replace(".", ",")

        def formatar_nome_curto(nome_completo):
            partes = str(nome_completo).strip().split()
            if not partes:
                return ""
            preposicoes = ['DA', 'DE', 'DO', 'DOS']
            if len(partes) >= 3 and partes[1].upper() in preposicoes:
                return f"{partes[0]} {partes[1]} {partes[2]}"
            if len(partes) >= 2:
                return f"{partes[0]} {partes[1]}"
            return partes[0]

        def obter_iniciais_nome(nome):
            partes = [p for p in str(nome).strip().split() if p]
            if not partes:
                return "--"
            if len(partes) == 1:
                return partes[0][:2].upper()
            return (partes[0][0] + partes[1][0]).upper()

        def classificar_desempenho_motorista(valor):
            try:
                valor = float(valor)
            except (TypeError, ValueError):
                valor = 0
            if valor <= 25:
                return "Performance estável", "status-bom", "fa-shield-halved"
            if valor <= 45:
                return "Atenção operacional", "status-regular", "fa-triangle-exclamation"
            return "Custo elevado", "status-critico", "fa-siren-on"

        resumo_motorista['NOME_CURTO'] = resumo_motorista['MOTORISTA'].apply(formatar_nome_curto)
        qtd_motoristas_contexto = int(resumo_motorista['MOTORISTA'].nunique()) if not resumo_motorista.empty else 0
        qtd_placas_contexto = int(df_motorista['PLACA_CAVALO'].nunique()) if not df_motorista.empty else 0
        qtd_destinos_contexto = int(df_motorista['DEST_MANIF'].nunique()) if not df_motorista.empty else 0
        perc_medio_contexto = float(resumo_motorista['PERC_CUSTO_FRETE'].mean()) if not resumo_motorista.empty else 0
        ocup_media_contexto = float(resumo_motorista['OCUPACAO_MEDIA_CARGA'].mean()) if not resumo_motorista.empty else 0
        top_motorista_curto = "N/A"
        if not resumo_motorista.empty:
            top_motorista_curto = formatar_nome_curto(resumo_motorista.sort_values('PERC_CUSTO_FRETE', ascending=True).iloc[0]['MOTORISTA'])

        motorista_label_painel = formatar_nome_curto(motorista_sel) if motorista_sel != "(Todos)" else "TODOS"
        iniciais_painel = obter_iniciais_nome(motorista_label_painel)
        status_texto, status_classe, status_icone = classificar_desempenho_motorista(dados_m["PERC_CUSTO_FRETE"])
        if motorista_sel == "(Todos)":
            status_texto, status_classe, status_icone = "AGUARDANDO SELEÇÃO", "status-wait", "fa-wand-magic-sparkles"
            ranking_chip_texto = "RANKING EM ESPERA"
            ranking_chip_icone = "fa-trophy"
            titulo_relacao_motorista = "Relação de Ocorrências por Motorista"
        else:
            ranking_chip_texto = f"Top ranking: {top_motorista_curto}"
            ranking_chip_icone = "fa-trophy"
            titulo_relacao_motorista = "Relação de Ocorrências por Motorista"
        texto_contexto = (
            "Selecione um motorista com ocorrência para abrir a visão<br>individual e destacar o impacto no ranking."
            if motorista_sel == "(Todos)"
            else "Visão individual do motorista selecionado com KPIs, filtros e ranking operacional detalhado."
        )
        data_atualizacao_motorista = df_motorista['EMIS_MANIF'].max() if not df_motorista.empty else df_aux['EMIS_MANIF'].max()
        data_atualizacao_txt = data_atualizacao_motorista.strftime('%d/%m/%Y') if pd.notna(data_atualizacao_motorista) else "N/A"

        st.markdown("""
            <style>
            .motoristas-hero-card {
                position: relative;
                overflow: hidden;
                border-radius: 24px;
                padding: 18px 20px 20px 20px;
                background:
                    radial-gradient(circle at 8% 14%, rgba(96,165,250,.16) 0%, rgba(96,165,250,0) 24%),
                    radial-gradient(circle at 92% 18%, rgba(168,85,247,.14) 0%, rgba(168,85,247,0) 28%),
                    linear-gradient(90deg, #17305f 0%, #071430 42%, #091433 68%, #2a163f 100%);
                border: 1px solid rgba(126, 152, 210, 0.24);
                box-shadow: 0 22px 48px rgba(2,6,23,.34), inset 0 1px 0 rgba(255,255,255,.04);
                margin-bottom: 20px;
            }
            .motoristas-hero-card::before {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(180deg, rgba(255,255,255,.03) 0%, rgba(255,255,255,0) 20%, rgba(255,255,255,.02) 100%);
                pointer-events: none;
            }
            .motoristas-hero-top {
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: 130px minmax(0, 1.42fr) 20px minmax(360px, 0.98fr);
                gap: 18px;
                align-items: start;
            }
            .motoristas-avatar {
                width: 120px;
                height: 165px;
                min-width: 120px;
                min-height: 165px;
                max-width: 120px;
                max-height: 165px;
                box-sizing: border-box;
                border-radius: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                align-self: start;
                justify-self: center;
                margin-top: 2px;
                font-family: 'Poppins', sans-serif;
                font-size: 1.6rem;
                font-weight: 800;
                letter-spacing: -.5px;
                color: #f8fbff;
                background:
                    linear-gradient(180deg, rgba(255,255,255,.14) 0%, rgba(255,255,255,.04) 100%),
                    linear-gradient(180deg, rgba(66,89,145,.92) 0%, rgba(24,37,75,.96) 100%);
                border: 1px solid rgba(255,255,255,.14);
                box-shadow: inset 0 1px 0 rgba(255,255,255,.08), inset 0 -18px 22px rgba(8,14,30,.22), 0 12px 28px rgba(2,6,23,.18);
            }
            .motoristas-hero-main {
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-width: 0;
                padding-right: 6px;
            }
            .motoristas-hero-main h3 {
                margin: 0;
                font-family: 'Poppins', sans-serif;
                font-size: 2.15rem;
                font-weight: 800;
                color: #ffffff;
                letter-spacing: -.8px;
                line-height: 1;
            }
            .motoristas-hero-kicker {
                color: #dbe7ff;
                font-size: .92rem;
                margin: 8px 0 14px 0;
                font-weight: 600;
                letter-spacing: .1px;
            }
            .motoristas-hero-desc {
                color: #eef4ff;
                font-size: 1rem;
                line-height: 1.5;
                max-width: 520px;
                margin-bottom: 16px;
            }
            .motoristas-pill-row {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }
            .motoristas-pill {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                padding: 10px 15px;
                border-radius: 999px;
                border: 1px solid rgba(255,255,255,.16);
                background: linear-gradient(180deg, rgba(18,28,56,.74) 0%, rgba(12,20,40,.46) 100%);
                color: #f8fbff;
                font-size: .78rem;
                font-weight: 800;
                box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 8px 18px rgba(2,6,23,.12);
                backdrop-filter: blur(4px);
                -webkit-backdrop-filter: blur(4px);
            }
            .motoristas-pill.status-wait {
                color: #ffe6ad;
                border-color: rgba(245, 158, 11, .30);
                background: linear-gradient(180deg, rgba(53,40,14,.78) 0%, rgba(36,28,12,.54) 100%);
            }
            .motoristas-side-divider {
                width: 4px;
                height: 96px;
                border-radius: 999px;
                background: linear-gradient(180deg, #60a5fa 0%, #8b5cf6 100%);
                box-shadow: 0 0 16px rgba(96,165,250,.22);
                justify-self: center;
            }
            .motoristas-side-info {
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 12px;
                min-width: 0;
                min-height: 138px;
                padding: 0 6px 0 0;
                background: transparent;
                border: none;
                box-shadow: none;
            }
            .motoristas-side-kicker {
                color: #ffe5bb;
                font-family: 'Poppins', sans-serif;
                font-size: .98rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1.15px;
            }
            .motoristas-side-title {
                color: #ffffff;
                font-family: 'Poppins', sans-serif;
                font-size: 1.22rem;
                font-weight: 800;
                line-height: 1.16;
                letter-spacing: -.2px;
            }
            .motoristas-side-date {
                color: #dbe7ff;
                font-size: .92rem;
                font-weight: 600;
            }
            .motoristas-hero-bottom {
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
                margin-top: 14px;
                padding-top: 12px;
                border-top: 1px solid rgba(255,255,255,.08);
            }
            .motoristas-info-panel {
                position: relative;
                overflow: hidden;
                border-radius: 22px;
                padding: 20px;
                border: 1px solid rgba(255,255,255,.10);
                box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 16px 32px rgba(2,6,23,.18);
            }
            .motoristas-info-panel::before {
                content: "";
                position: absolute;
                top: 0;
                left: 18px;
                width: calc(100% - 36px);
                height: 1px;
                background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.18) 50%, rgba(255,255,255,0) 100%);
                pointer-events: none;
            }
            .motoristas-info-panel.blue {
                background: linear-gradient(135deg, rgba(37,99,235,.24) 0%, rgba(15,23,42,.70) 100%);
            }
            .motoristas-info-panel.purple {
                background: linear-gradient(135deg, rgba(168,85,247,.22) 0%, rgba(30,16,52,.72) 100%);
            }
            .motoristas-panel-title {
                font-family: 'Poppins', sans-serif;
                font-size: 1.05rem;
                font-weight: 800;
                color: #ffffff;
                margin-bottom: 12px;
            }
            .motoristas-panel-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 10px;
            }
            .motoristas-big-number {
                font-family: 'Poppins', sans-serif;
                font-size: 3rem;
                font-weight: 800;
                color: #ffffff;
                line-height: 1;
                margin-bottom: 12px;
            }
            .motoristas-badge {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 6px 12px;
                border-radius: 999px;
                background: rgba(255,255,255,.08);
                border: 1px solid rgba(255,255,255,.12);
                color: #f2f7ff;
                font-size: .78rem;
                font-weight: 700;
            }
            .motoristas-mini-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }
            .motoristas-mini-card {
                border-radius: 16px;
                padding: 14px 14px 12px 14px;
                background: rgba(10,17,31,.38);
                border: 1px solid rgba(255,255,255,.08);
            }
            .motoristas-mini-label {
                font-size: .70rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #9fb3d9;
                margin-bottom: 7px;
            }
            .motoristas-mini-value {
                color: #ffffff;
                font-size: 1.55rem;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 5px;
            }
            .motoristas-mini-caption {
                color: #d2def7;
                font-size: .83rem;
            }
            .motoristas-filter-shell {
                border-radius: 20px;
                padding: 16px 16px 14px 16px;
                background: linear-gradient(180deg, rgba(7,14,29,.96) 0%, rgba(4,10,24,.98) 100%);
                border: 1px solid rgba(96,165,250,.15);
                box-shadow: 0 16px 32px rgba(2,6,23,.32);
                margin-bottom: 14px;
            }
            .motoristas-filter-head {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 10px;
            }
            .motoristas-filter-title {
                color: #ffffff;
                font-family: 'Poppins', sans-serif;
                font-size: 1.1rem;
                font-weight: 800;
                margin-bottom: 4px;
            }
            .motoristas-filter-subtitle {
                color: #c7d7f7;
                font-size: .86rem;
                line-height: 1.45;
            }
            .motoristas-filter-icon {
                width: 56px;
                height: 56px;
                min-width: 56px;
                border-radius: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #f5ecff;
                background: linear-gradient(180deg, rgba(255,255,255,.14) 0%, rgba(255,255,255,.05) 100%);
                border: 1px solid rgba(255,255,255,.10);
                font-size: 1rem;
            }
            .motoristas-filter-pills {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 10px;
            }
            .motoristas-filter-caption {
                color: #e4edff;
                font-size: .82rem;
                margin-top: 8px;
            }
            .driver-metric-card {
                position: relative;
                overflow: hidden;
                border-radius: 18px;
                padding: 16px 16px 13px 16px;
                background: linear-gradient(180deg, rgba(30,41,75,.92) 0%, rgba(43,51,88,.92) 100%);
                border: 1px solid rgba(120,136,192,.22);
                box-shadow: 0 14px 28px rgba(2,6,23,.28);
                min-height: 122px;
            }
            .driver-metric-title {
                color: #ffffff;
                font-size: .82rem;
                font-weight: 800;
                letter-spacing: .7px;
                text-transform: uppercase;
                margin-bottom: 12px;
                min-height: 34px;
            }
            .driver-metric-value {
                color: #ffffff;
                font-family: 'Poppins', sans-serif;
                font-size: 2rem;
                font-weight: 800;
                line-height: 1;
                margin-bottom: 12px;
            }
            .driver-metric-divider {
                height: 1px;
                background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.72) 18%, rgba(255,255,255,.20) 100%);
                margin: 10px 0 10px 0;
            }
            .driver-metric-foot {
                color: #d4dff7;
                font-size: .78rem;
                display: inline-flex;
                align-items: center;
                gap: 7px;
                border-radius: 999px;
                padding: 4px 10px;
                background: rgba(7,12,20,.26);
                border: 1px solid rgba(255,255,255,.10);
            }
            .status-bom { color: #c9ffd8; }
            .status-regular { color: #ffe8b2; }
            .status-critico { color: #ffd3d3; }
            @media (max-width: 1200px) {
                .motoristas-hero-top { grid-template-columns: 120px 1fr; align-items: start; }
                .motoristas-avatar { width: 104px; height: 145px; min-width: 104px; min-height: 145px; max-width: 104px; max-height: 145px; box-sizing: border-box; border-radius: 18px; }
                .motoristas-side-divider { display: none; }
                .motoristas-side-info { grid-column: span 2; min-height: auto; padding-top: 4px; }
            }
            @media (max-width: 900px) {
                .motoristas-hero-top, .motoristas-hero-bottom, .motoristas-mini-grid { grid-template-columns: 1fr; }
                .motoristas-avatar { justify-self: flex-start; }
                .motoristas-big-number { font-size: 2.35rem; }
                .motoristas-side-divider { display: none; }
            }
            </style>
        """, unsafe_allow_html=True)

        painel_top_esq, painel_top_dir = st.columns([2.28, 0.92], gap="large")

        with painel_top_esq:
            st.markdown(f"""
                <div class="motoristas-hero-card">
                    <div class="motoristas-hero-top">
                        <div class="motoristas-avatar">{iniciais_painel}</div>
                        <div class="motoristas-hero-main">
                            <h3>{motorista_label_painel}</h3>
                            <div class="motoristas-hero-desc">{texto_contexto}</div>
                            <div class="motoristas-pill-row">
                                <span class="motoristas-pill {status_classe}"><i class="fa-solid {status_icone}"></i> {status_texto}</span>
                                <span class="motoristas-pill"><i class="fa-solid {ranking_chip_icone}"></i> {ranking_chip_texto}</span>
                            </div>
                        </div>
                        <div class="motoristas-side-divider"></div>
                        <div class="motoristas-side-info">
                            <div class="motoristas-side-kicker">Expedição • KM Transportes</div>
                            <div class="motoristas-side-title">{titulo_relacao_motorista}</div>
                            <div class="motoristas-side-date"><i class="fa-solid fa-clock"></i> Atualizado em: {data_atualizacao_txt}</div>
                        </div>
                    </div>
                    <div class="motoristas-hero-bottom">
                        <div class="motoristas-info-panel blue">
                            <div class="motoristas-panel-top">
                                <div class="motoristas-panel-title">Operação</div>
                                <span class="motoristas-badge"><i class="fa-solid fa-users"></i> {qtd_motoristas_contexto} motoristas</span>
                            </div>
                            <div class="motoristas-big-number">{fmt_num(dados_m['TOTAL_VIAGENS'])}</div>
                            <div class="motoristas-mini-grid">
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Total de Entregas</div>
                                    <div class="motoristas-mini-value">{fmt_num(dados_m['TOTAL_ENTREGAS'])}</div>
                                    <div class="motoristas-mini-caption">Entregas consolidadas no recorte</div>
                                </div>
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Placas no recorte</div>
                                    <div class="motoristas-mini-value">{fmt_num(qtd_placas_contexto)}</div>
                                    <div class="motoristas-mini-caption">Veículos utilizados no período</div>
                                </div>
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Peso Médio</div>
                                    <div class="motoristas-mini-value">{fmt_num(dados_m['PESO_MEDIO_VIAGEM'], ' kg')}</div>
                                    <div class="motoristas-mini-caption">Carga média por viagem</div>
                                </div>
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Distância Média</div>
                                    <div class="motoristas-mini-value">{fmt_num(dados_m['DISTANCIA_MEDIA_VIAGEM'], ' km')}</div>
                                    <div class="motoristas-mini-caption">Média de deslocamento</div>
                                </div>
                            </div>
                        </div>
                        <div class="motoristas-info-panel purple">
                            <div class="motoristas-panel-top">
                                <div class="motoristas-panel-title">Performance</div>
                                <span class="motoristas-badge"><i class="fa-solid fa-signal"></i> {fmt_perc(perc_medio_contexto)} taxa média</span>
                            </div>
                            <div class="motoristas-big-number">{fmt_perc(dados_m['PERC_CUSTO_FRETE'])}</div>
                            <div class="motoristas-mini-grid">
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Ocupação Média</div>
                                    <div class="motoristas-mini-value">{fmt_perc(dados_m['OCUPACAO_MEDIA_CARGA'])}</div>
                                    <div class="motoristas-mini-caption">Eficiência de uso da capacidade</div>
                                </div>
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Destinos</div>
                                    <div class="motoristas-mini-value">{fmt_num(qtd_destinos_contexto)}</div>
                                    <div class="motoristas-mini-caption">Abrangência operacional analisada</div>
                                </div>
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Melhor CTRB/Frete</div>
                                    <div class="motoristas-mini-value">{top_motorista_curto}</div>
                                    <div class="motoristas-mini-caption">Menor índice no período</div>
                                </div>
                                <div class="motoristas-mini-card">
                                    <div class="motoristas-mini-label">Ocupação do grupo</div>
                                    <div class="motoristas-mini-value">{fmt_perc(ocup_media_contexto)}</div>
                                    <div class="motoristas-mini-caption">Média geral de todos os motoristas</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with painel_top_dir:
            st.markdown(f"""
                <div class="motoristas-filter-shell">
                    <div class="motoristas-filter-head">
                        <div>
                            <div class="motoristas-filter-title">📌 Indicadores por Motorista</div>
                            <div class="motoristas-filter-subtitle">Selecione um nome para ver KPIs e os registros detalhados.</div>
                        </div>
                        <div class="motoristas-filter-icon"><i class="fa-solid fa-user"></i></div>
                    </div>
                    <div class="motoristas-filter-pills">
                        <span class="motoristas-pill"><i class="fa-solid fa-users"></i> Todos</span>
                        <span class="motoristas-pill"><i class="fa-solid fa-route"></i> {fmt_num(dados_m['TOTAL_VIAGENS'])} viagens</span>
                        <span class="motoristas-pill"><i class="fa-solid fa-chart-line"></i> {fmt_perc(dados_m['PERC_CUSTO_FRETE'])}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            lista_motoristas_ranking = ["(Todos)"] + sorted(resumo_motorista['NOME_CURTO'].unique())
            motorista_ranking_sel = st.selectbox(
                'Escolha um motorista para filtrar o ranking:',
                options=lista_motoristas_ranking,
                key="filtro_motorista_ranking"
            )
            st.caption("💡 Escolha um nome para ver somente esse motorista no ranking.")

            st.markdown(f"""
                <div class="motoristas-filter-shell">
                    <div class="motoristas-filter-head">
                        <div>
                            <div class="motoristas-filter-title">📊 Faixa de Desempenho</div>
                            <div class="motoristas-filter-subtitle">Filtre o ranking pelo nível de CTRB/Frete do grupo analisado.</div>
                        </div>
                        <div class="motoristas-filter-icon"><i class="fa-solid fa-gauge-high"></i></div>
                    </div>
                    <div class="motoristas-filter-pills">
                        <span class="motoristas-pill"><i class="fa-solid fa-shield-halved"></i> Bom</span>
                        <span class="motoristas-pill"><i class="fa-solid fa-triangle-exclamation"></i> Regular</span>
                        <span class="motoristas-pill"><i class="fa-solid fa-siren-on"></i> Crítico</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            opcoes_desempenho = ["(Todos)", "Bom (0-25%)", "Regular (26-45%)", "Péssimo (>45%)"]
            desempenho_sel = st.selectbox(
                'Filtre por Desempenho de CTRB/Frete (%):',
                options=opcoes_desempenho,
                key="filtro_desempenho_ctrb"
            )
            st.caption("💡 Você pode combinar os dois filtros para isolar um motorista específico dentro de uma faixa de desempenho.")

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        kpi_cols = st.columns(6)
        kpis_operacionais = [
            {"titulo": "TOTAL DE VIAGENS", "valor": fmt_num(dados_m["TOTAL_VIAGENS"]), "icone": "fa-route", "rodape": "Base operacional selecionada"},
            {"titulo": "DISTÂNCIA MÉDIA", "valor": fmt_num(dados_m["DISTANCIA_MEDIA_VIAGEM"], " km"), "icone": "fa-road", "rodape": "Deslocamento médio por viagem"},
            {"titulo": "TOTAL DE ENTREGAS", "valor": fmt_num(dados_m["TOTAL_ENTREGAS"]), "icone": "fa-dolly", "rodape": "Entregas consolidadas no período"},
            {"titulo": "PESO MÉDIO / VIAGEM", "valor": fmt_num(dados_m["PESO_MEDIO_VIAGEM"], " kg"), "icone": "fa-weight-hanging", "rodape": "Carga média movimentada"},
            {"titulo": "OCUPAÇÃO MÉDIA", "valor": fmt_perc(dados_m["OCUPACAO_MEDIA_CARGA"]), "icone": "fa-chart-column", "rodape": "Eficiência de utilização do veículo"},
            {"titulo": "CTRB / FRETE", "valor": fmt_perc(dados_m["PERC_CUSTO_FRETE"]), "icone": "fa-scale-balanced", "rodape": "Custo de transferência do motorista"},
        ]

        for coluna, info in zip(kpi_cols, kpis_operacionais):
            with coluna:
                render_performance_reference_kpi_card(
                    titulo=info['titulo'],
                    valor=info['valor'],
                    icone=info['icone'],
                    rodape=info['rodape']
                )

        st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # --- ▼▼▼ BLOCO ATUALIZADO: RANKING DE MOTORISTAS (COM FILTROS LADO A LADO) ▼▼▼

        # Só exibe o ranking se houver dados para comparar
        if not resumo_motorista.empty:
            st.markdown("### 🏆 Ranking de Motoristas no Período")

            # --- 3. FILTRAGEM DOS DADOS PARA OS GRÁFICOS ---
            # Começa com o dataframe completo do resumo
            df_para_graficos = resumo_motorista.copy()

            # Filtro 1: Aplica o filtro de desempenho CTRB/Frete
            if desempenho_sel == "Bom (0-25%)":
                df_para_graficos = df_para_graficos[df_para_graficos['PERC_CUSTO_FRETE'] <= 25]
            elif desempenho_sel == "Regular (26-45%)":
                df_para_graficos = df_para_graficos[(df_para_graficos['PERC_CUSTO_FRETE'] > 25) & (df_para_graficos['PERC_CUSTO_FRETE'] <= 45)]
            elif desempenho_sel == "Péssimo (>45%)":
                df_para_graficos = df_para_graficos[df_para_graficos['PERC_CUSTO_FRETE'] > 45]
            
            # Filtro 2: Aplica o filtro de motorista sobre o resultado do primeiro filtro
            if motorista_ranking_sel != "(Todos)":
                df_para_graficos = df_para_graficos[df_para_graficos['NOME_CURTO'] == motorista_ranking_sel]

            # --- 4. CRIAÇÃO DAS COLUNAS E GRÁFICOS ---
            # (O restante do código dos gráficos permanece o mesmo)
            col_rank1, col_rank2 = st.columns(2)

            with col_rank1:
                opcoes_ranking = {
                    'Performance das Viagens - CTRB/Frete (%)': {
                        'coluna_valor': 'PERC_CUSTO_FRETE', 'coluna_ordem': 'PERC_CUSTO_FRETE',
                        'titulo_eixo': 'CTRB / Frete (%)', 'ordem': 'ascending',
                        'formato_label': "format(datum.PERC_CUSTO_FRETE, '.0f') + '%'"
                    },
                    'Produtividade - Nº de Viagens': {
                        'coluna_valor': 'TOTAL_VIAGENS', 'coluna_ordem': 'TOTAL_VIAGENS',
                        'titulo_eixo': 'Nº de Viagens', 'ordem': 'descending',
                        'formato_label': "format(datum.TOTAL_VIAGENS, '.0f')"
                    },
                    'Performance Operacional - Peso Médio KG': {
                        'coluna_valor': 'PESO_MEDIO_VIAGEM', 'coluna_ordem': 'PESO_MEDIO_VIAGEM',
                        'titulo_eixo': 'Peso Médio por Viagem (kg)', 'ordem': 'descending',
                        'formato_label': "format(datum.PESO_MEDIO_VIAGEM, ',.0f') + ' kg'"
                    },
                    'Ordem Alfabética - Motorista': {
                        'coluna_valor': 'PERC_CUSTO_FRETE', 'coluna_ordem': 'NOME_CURTO',
                        'titulo_eixo': 'CTRB / Frete (%)', 'ordem': 'ascending',
                        'formato_label': "format(datum.PERC_CUSTO_FRETE, '.0f') + '%'"
                    }
                }
                selecao_ranking = st.selectbox(
                    'Selecione a métrica para o ranking:',
                    options=list(opcoes_ranking.keys())
                )
                
                config_selecionada = opcoes_ranking[selecao_ranking]
                coluna_valor_selecionada = config_selecionada['coluna_valor']
                coluna_ordem_selecionada = config_selecionada['coluna_ordem']
                titulo_eixo_selecionado = config_selecionada['titulo_eixo']
                ordem_selecionada = config_selecionada['ordem']
                formato_label_selecionado = config_selecionada['formato_label']

                # Verifica se há dados para plotar após a filtragem
                if not df_para_graficos.empty:
                    ranking_dinamico_df = df_para_graficos.sort_values(
                        by=coluna_ordem_selecionada, 
                        ascending=(ordem_selecionada == 'ascending')
                    )

                    if periodo_tipo in ["Mês Completo", "Período Personalizado"]:
                        ranking_dinamico_df = ranking_dinamico_df.head(15)

                    if selecao_ranking == 'Performance das Viagens - CTRB/Frete (%)':
                        ranking_dinamico_df['cor_barra'] = ranking_dinamico_df[coluna_valor_selecionada].apply(
                            lambda x: '#2E7D32' if x <= 25 else ('#FF8F00' if x <= 45 else '#C62828')
                        )
                        color_condition = alt.Color('cor_barra:N', scale=None)
                    else:
                        color_condition = alt.Color(f'{coluna_valor_selecionada}:Q',
                                        scale=alt.Scale(scheme='reds', reverse=(ordem_selecionada == 'ascending')),
                                        legend=None)

                    barras_dinamicas = alt.Chart(ranking_dinamico_df).mark_bar(
                        cornerRadius=5, height=25
                    ).encode(
                        x=alt.X(f'{coluna_valor_selecionada}:Q', title=titulo_eixo_selecionado, axis=alt.Axis(format='.0f')),
                        y=alt.Y('NOME_CURTO:N', 
                                title=None, 
                                sort=alt.EncodingSortField(field=coluna_ordem_selecionada, op="min", order=ordem_selecionada),
                                axis=alt.Axis(labelFontSize=14, labelLimit=0)
                            ),
                        color=color_condition,
                        tooltip=[
                            alt.Tooltip('NOME_CURTO', title='Motorista'),
                            alt.Tooltip('PERC_CUSTO_FRETE', title='CTRB/Frete', format='.1f'),
                            alt.Tooltip('TOTAL_VIAGENS', title='Nº de Viagens'),
                            alt.Tooltip('PESO_MEDIO_VIAGEM', title='Peso Médio', format=',.0f')
                        ]
                    )
                    
                    texto_dinamico = barras_dinamicas.transform_calculate(
                        text_label=formato_label_selecionado
                    ).mark_text(
                        align='left', baseline='middle', dx=5, fontSize=14
                    ).encode(
                        text=alt.Text('text_label:N'), color=alt.value('white')
                    )

                    chart_dinamico = (barras_dinamicas + texto_dinamico).properties(
                        title={"text": selecao_ranking, "anchor": "start", "fontSize": 16, "fontWeight": "bold"},
                        height=alt.Step(35)
                    ).configure_view(stroke=None).configure_axis(grid=False).configure_title(color='white')
                    
                    st.altair_chart(chart_dinamico, use_container_width=True)

                    if selecao_ranking == 'Performance das Viagens - CTRB/Frete (%)':
                        st.markdown("""
                        <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 15px; font-size: 14px;">
                            <b style="color: #E0E0E0;">CTRB/Frete (%):</b>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px; border: 1px solid #4A4A4A;"></div>
                                <span style="color: #E0E0E0;">Bom</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px; border: 1px solid #4A4A4A;"></div>
                                <span style="color: #E0E0E0;">Regular</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px; border: 1px solid #4A4A4A;"></div>
                                <span style="color: #E0E0E0;">Péssimo</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhum motorista encontrado para os filtros selecionados.")


            with col_rank2:
                opcoes_ranking_op = {
                    'Eficiência Operacional (Ocupação Média)': {
                        'coluna_valor': 'OCUPACAO_MEDIA_CARGA', 'coluna_ordem': 'OCUPACAO_MEDIA_CARGA',
                        'titulo_eixo': 'Ocupação Média (%)', 'ordem': 'descending', 'cor_esquema': 'greens',
                        'formato_label': "format(datum.OCUPACAO_MEDIA_CARGA, '.0f') + '%'"
                    },
                    'Performance de Entrega (Média de Entregas)': {
                        'coluna_valor': 'MEDIA_ENTREGAS_VIAGEM', 'coluna_ordem': 'MEDIA_ENTREGAS_VIAGEM',
                        'titulo_eixo': 'Média de Entregas por Viagem', 'ordem': 'descending', 'cor_esquema': 'bluepurple',
                        'formato_label': "format(datum.MEDIA_ENTREGAS_VIAGEM, '.1f')"
                    },
                    'Performance de Distância (Distância Média)': {
                        'coluna_valor': 'DISTANCIA_MEDIA_VIAGEM', 'coluna_ordem': 'DISTANCIA_MEDIA_VIAGEM',
                        'titulo_eixo': 'Distância Média por Viagem (km)', 'ordem': 'descending', 'cor_esquema': 'teals',
                        'formato_label': "format(datum.DISTANCIA_MEDIA_VIAGEM, ',.0f') + ' km'"
                    },
                    'Ordem Alfabética (Motorista)': {
                        'coluna_valor': 'OCUPACAO_MEDIA_CARGA', 'coluna_ordem': 'NOME_CURTO',
                        'titulo_eixo': 'Ocupação Média (%)', 'ordem': 'ascending', 'cor_esquema': 'greens',
                        'formato_label': "format(datum.OCUPACAO_MEDIA_CARGA, '.0f') + '%'"
                    }
                }
                selecao_ranking_op = st.selectbox(
                    'Selecione a métrica para o ranking operacional:',
                    options=list(opcoes_ranking_op.keys())
                )

                config_selecionada_op = opcoes_ranking_op[selecao_ranking_op]
                coluna_valor_op = config_selecionada_op['coluna_valor']
                coluna_ordem_op = config_selecionada_op['coluna_ordem']
                titulo_eixo_op = config_selecionada_op['titulo_eixo']
                ordem_op = config_selecionada_op['ordem']
                cor_esquema_op = config_selecionada_op['cor_esquema']
                formato_label_op = config_selecionada_op['formato_label']

                if not df_para_graficos.empty:
                    ranking_dinamico_op_df = df_para_graficos.sort_values(
                        by=coluna_ordem_op, ascending=(ordem_op == 'ascending')
                    )

                    if periodo_tipo in ["Mês Completo", "Período Personalizado"]:
                        ranking_dinamico_op_df = ranking_dinamico_op_df.head(15)

                    barras_dinamicas_op = alt.Chart(ranking_dinamico_op_df).mark_bar(
                        cornerRadius=5, height=25
                    ).encode(
                        x=alt.X(f'{coluna_valor_op}:Q', title=titulo_eixo_op, axis=alt.Axis(format='.0f')),
                        y=alt.Y('NOME_CURTO:N', title=None, 
                                sort=alt.EncodingSortField(field=coluna_ordem_op, op="min", order=ordem_op),
                                axis=alt.Axis(labelFontSize=14, labelLimit=0)),
                        color=alt.Color(f'{coluna_valor_op}:Q', scale=alt.Scale(scheme=cor_esquema_op, reverse=(ordem_op == 'ascending')), legend=None),
                        tooltip=[
                            alt.Tooltip('NOME_CURTO', title='Motorista'),
                            alt.Tooltip('OCUPACAO_MEDIA_CARGA', title='Ocupação Média', format='.1f'),
                            alt.Tooltip('MEDIA_ENTREGAS_VIAGEM', title='Média de Entregas', format='.1f'),
                            alt.Tooltip('DISTANCIA_MEDIA_VIAGEM', title='Distância Média', format=',.0f')
                        ]
                    )
                    
                    texto_dinamico_op = barras_dinamicas_op.transform_calculate(
                        text_label=formato_label_op
                    ).mark_text(
                        align='left', baseline='middle', dx=5, fontSize=14
                    ).encode(
                        text=alt.Text('text_label:N'), color=alt.value('white')
                    )

                    chart_dinamico_op = (barras_dinamicas_op + texto_dinamico_op).properties(
                        title={"text": selecao_ranking_op, "anchor": "start", "fontSize": 16, "fontWeight": "bold"},
                        height=alt.Step(35)
                    ).configure_view(stroke=None).configure_axis(grid=False).configure_title(color='white')
                    
                    st.altair_chart(chart_dinamico_op, use_container_width=True)
                else:
                    # Esta mensagem já existe na coluna da esquerda, não precisa repetir.
                    pass
            
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

        # --- ▲▲▲ FIM DO BLOCO ATUALIZADO ▲▲▲

                # Tabela de Resumo das Viagens
        if motorista_sel != "(Todos)":
            st.markdown(f"### 📋 Resumo das Viagens 👨‍✈️{motorista_sel}")
        else:
            st.markdown("### 📋 Resumo de Todas as Viagens no Período")

        df_agrupado = df_motorista.copy()
        coluna_peso_resumo = obter_nome_coluna_peso_calculo(df_agrupado) or 'PESO REAL (KG)'
        
        # Agrupa os dados por viagem para criar o resumo
        resumo_viagens = df_agrupado.groupby('VIAGEM_ID').agg(
            EMISSÃO=('EMIS_MANIF', 'first'), PLACA=('PLACA_CAVALO', 'first'), TIPO=('TIPO_CAVALO', 'first'),
            MOTORISTA=('MOTORISTA', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())),
            FRETE=('FRETE-R$', 'sum'), CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
            PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), ICMS=('ICMS-R$', 'sum'), PESO_KG=(coluna_peso_resumo, 'sum'),
            M3=('M3', 'sum'), VOLUMES=('VOLUMES', 'sum'), VALOR_MERC=('MERCADORIA-R$', 'sum'),
            ENTREGAS=('DEST_MANIF', 'nunique'), QTDE_CTRC=('QTDE_CTRC', 'sum')
        ).reset_index()

        # Calcula colunas adicionais
        def calcular_custo_viagem(row):
            return row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']

        resumo_viagens['Custo (CTRB/OS)'] = resumo_viagens.apply(calcular_custo_viagem, axis=1)
        resumo_viagens['CTRB/Frete (%)'] = ((resumo_viagens['Custo (CTRB/OS)'] / resumo_viagens['FRETE']) * 100).fillna(0)
        
        def calcular_distancia_por_viagem(row):
            tipo_veiculo = str(row.get('TIPO', 'PADRAO')).upper()
            valor_por_km = custo_km_por_tipo.get(tipo_veiculo, 0)
            custo_da_viagem = row['Custo (CTRB/OS)']
            return (custo_da_viagem / valor_por_km) if valor_por_km > 0 and custo_da_viagem > 0 else 0

        resumo_viagens['Distância (KM)'] = resumo_viagens.apply(calcular_distancia_por_viagem, axis=1)
        
        def corrigir_volume_numerico(valor):
            try:
                valor_float = float(valor)
                return valor_float / 10000 if valor_float > 1000 else valor_float
            except (ValueError, TypeError): return 0.0
        resumo_viagens['M3_corrigido'] = resumo_viagens['M3'].apply(corrigir_volume_numerico)

        # Renomeia as colunas para exibição
        resumo_viagens.rename(columns={
            'VIAGEM_ID': '🧭 Viagem', 'TIPO': 'Tipo Veículo', 'DESTINOS': 'Destinos da Rota', 
            'PESO_KG': 'Peso Total', 'M3_corrigido': 'Volume Total (M³)', 'VOLUMES': 'Volumes Totais', 
            'VALOR_MERC': 'Valor Mercadoria', 'QTDE_CTRC': 'Qtd. CTRCs',
        }, inplace=True)

        # --- INÍCIO DO CÓDIGO ATUALIZADO ---

        # 1. Define a ordem das colunas e cria a lista ANTES de usá-la
        ordem_final_renomeada = [
            '🧭 Viagem', 'EMISSÃO', 'PLACA', 'Tipo Veículo', 'Destinos da Rota', 'MOTORISTA', 'Distância (KM)',
            'ENTREGAS', 'Custo (CTRB/OS)', 'CTRB/Frete (%)', 'FRETE', 'ICMS', 'Peso Total',
            'Volume Total (M³)', 'Qtd. CTRCs', 'Volumes Totais', 'Valor Mercadoria'
        ]
        colunas_para_exibir_e_exportar = [col for col in ordem_final_renomeada if col in resumo_viagens.columns]

        # 2. Cria o DataFrame para exportação com os dados brutos (antes da formatação)
        df_para_exportar = resumo_viagens[colunas_para_exibir_e_exportar].copy()

        # 3. Funções de formatação reutilizáveis
        def formatar_moeda_br(valor):
            try: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError): return "R$ 0,00"

        def formatar_peso_br(valor):
            try: return f"{valor:,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError): return "0,00 kg"

        # 4. Aplica a formatação em cada coluna do DataFrame que será exibido
        if 'EMISSÃO' in resumo_viagens.columns:
            resumo_viagens['EMISSÃO'] = pd.to_datetime(resumo_viagens['EMISSÃO']).dt.strftime('%d/%m/%Y')
        
        colunas_moeda = ['Custo (CTRB/OS)', 'FRETE', 'Valor Mercadoria', 'ICMS']
        for col in colunas_moeda:
            if col in resumo_viagens.columns:
                resumo_viagens[col] = resumo_viagens[col].apply(formatar_moeda_br)

        if 'Peso Total' in resumo_viagens.columns:
            resumo_viagens['Peso Total'] = resumo_viagens['Peso Total'].apply(formatar_peso_br)
        
        if 'Distância (KM)' in resumo_viagens.columns:
            resumo_viagens['Distância (KM)'] = resumo_viagens['Distância (KM)'].apply(lambda x: f"{int(x)} km")
        
        if 'Volume Total (M³)' in resumo_viagens.columns:
            resumo_viagens['Volume Total (M³)'] = resumo_viagens['Volume Total (M³)' ].apply(lambda x: f"{x:,.3f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # 5. Lógica de estilização para a coluna de percentual
        resumo_viagens['CTRB/Frete (%)_valor_numerico'] = resumo_viagens['CTRB/Frete (%)']

        if 'CTRB/Frete (%)' in resumo_viagens.columns:
            resumo_viagens['CTRB/Frete (%)'] = resumo_viagens['CTRB/Frete (%)'].apply(lambda x: f"{x:,.0f}%".replace(",", "."))

        # 6. Seleciona as colunas para exibição ANTES de aplicar o estilo
        df_para_exibir_formatado = resumo_viagens[colunas_para_exibir_e_exportar]

        # 7. Aplica o estilo ao DataFrame já fatiado
        styled_df = df_para_exibir_formatado.style.background_gradient(
            cmap='Reds', 
            subset=['CTRB/Frete (%)'], 
            gmap=resumo_viagens['CTRB/Frete (%)_valor_numerico'] # gmap ainda usa o df original com dados numéricos
        )

        # 8. Exibe o DataFrame ESTILIZADO
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # --- FIM DO CÓDIGO ATUALIZADO ---

        # O botão de download continua usando o df_para_exportar (não formatado)
        excel_bytes = to_excel(df_para_exportar)
        st.download_button(
            label="📤 Exportar Resumo para Excel", data=excel_bytes,
            file_name=f"resumo_viagens_{motorista_sel.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        
        # ▼▼▼ SUBSTITUA O BLOCO DA TABELA "DETALHES" POR ESTE ▼▼▼

        # A tabela detalhada só aparece se um motorista específico for selecionado.
        if motorista_sel != "(Todos)":
            st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("📄 Detalhes dos Documentos da Viagem")

            df_detalhado_base = df_motorista.copy()

            # 1. Funções para unificar as colunas de custo
            def calcular_custo_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('OS-R$', 0.0)
                return row.get('CTRB-R$', 0.0)

            def obter_numero_documento_unificado(row):
                if row.get('PROPRIETARIO_CAVALO') == 'MARCELO H LEMOS BERALDO E CIA LTDA ME':
                    return row.get('NUM_OS', '')
                return row.get('NUM_CTRB', '')

            # 2. Aplica as funções para criar as novas colunas
            df_detalhado_base['Custo (CTRB/OS)'] = df_detalhado_base.apply(calcular_custo_unificado, axis=1)
            df_detalhado_base['Nº CTRB/OS'] = df_detalhado_base.apply(obter_numero_documento_unificado, axis=1)

            # 3. Define a lista de colunas a serem exibidas
            colunas_para_exibir = [
                'EMIS_MANIF', 'NUM_MANIF', 'SITUACAO', 'MOTORISTA', 'DEST_MANIF', 'PLACA_CAVALO', 'TIPO_CAVALO',
                'Nº CTRB/OS',          # <-- Coluna unificada
                'Custo (CTRB/OS)',     # <-- Coluna unificada
                'FRETE-R$', 'ICMS-R$', 'Peso Cálculo (KG)',
                'M3', 'VOLUMES', 'QTDE_CTRC', 'MERCADORIA-R$'
            ]
            
            colunas_existentes = [col for col in colunas_para_exibir if col in df_detalhado_base.columns]
            df_detalhado_final = df_detalhado_base[colunas_existentes].copy()

            # 4. Renomeia as colunas para a exibição
            df_detalhado_final.rename(columns={
                'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'SITUACAO': 'SITUAÇÃO',
                'DEST_MANIF': 'Destino', 'PLACA_CAVALO': 'PLACA', 'TIPO_CAVALO': 'TIPO',
                'QTDE_CTRC': 'Qtd. CTRCs'
            }, inplace=True)

            # 5. Formata os valores
            df_detalhado_final['EMISSÃO'] = pd.to_datetime(df_detalhado_final['EMISSÃO']).dt.strftime('%d/%m/%Y')
            
            colunas_moeda_det = ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']
            for col in colunas_moeda_det:
                if col in df_detalhado_final.columns:
                    df_detalhado_final[col] = df_detalhado_final[col].apply(formatar_moeda)
                    
            df_detalhado_final = garantir_coluna_peso_calculo(df_detalhado_final)
            if 'Peso Cálculo (KG)' in df_detalhado_final.columns:
                df_detalhado_final['Peso Cálculo (KG)'] = df_detalhado_final['Peso Cálculo (KG)'].apply(lambda x: formatar_numero(x, 2) + ' kg')
                
            if 'M3' in df_detalhado_final.columns:
                df_detalhado_final['M3'] = df_detalhado_final['M3'].apply(corrigir_volume_numerico).apply(lambda x: formatar_numero(x, 3))

            # 6. Exibe a tabela final
            st.dataframe(df_detalhado_final, use_container_width=True, hide_index=True)
            
            # 7. Botão de download
            try:
                excel_bytes_detalhado = to_excel(df_detalhado_final)
                st.download_button(
                    label="📥 Download Detalhado (Excel)",
                    data=excel_bytes_detalhado,
                    file_name=f"detalhes_motorista_{motorista_sel.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_detalhado_motorista"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar o arquivo Excel detalhado: {e}")

# ==================================================================
# ABA 5: GESTÃO DE ROTAS (VERSÃO SIMPLIFICADA)
# ==================================================================
with tab5:

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:

        # --- TÍTULO DA SEÇÃO DE OCUPAÇÃO ---
        st.markdown("""
            <div class="title-block-rotas">
                <i class="fa-solid fa-route"></i>
                <h2>Análise de Ocupação de Carga por Rota</h2>
            </div>
        """, unsafe_allow_html=True)

        # --- FILTROS DE TIPO DE VIAGEM E ROTA (COM A OPÇÃO "TODAS") ---
        tipo_viagem_ocupacao_sel = option_menu(
            menu_title=None,
            # 1. Adiciona a nova opção "TODAS AS ROTAS" no início
            options=["TODAS AS ROTAS", "ROTA COMPLETA", "VIAGEM EXTRA"],
            # 2. Adiciona o ícone correspondente para a nova opção
            icons=["collection-fill", "arrow-repeat", "exclamation-octagon-fill"],
            menu_icon="filter-circle",
            default_index=0, # Começa com "TODAS AS ROTAS" selecionado
            orientation="horizontal",
            key="option_menu_tipo_viagem_tab5",
            styles={
                "container": {
                    "padding": "5px",
                    "background-color": "#1F2937",
                    "border-radius": "999px",
                    "margin-bottom": "25px",
                    "display": "flex",
                    "justify-content": "center"
                },
                "icon": {
                    "color": "#9CA3AF",
                    "font-size": "16px"
                },
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "600",
                    "color": "#D1D5DB",
                    "text-transform": "uppercase",
                    "padding": "10px 25px",
                    "border-radius": "999px",
                    "margin": "0px",
                    "transition": "all 0.3s ease"
                },
                "nav-link:hover": {
                    "background-color": "rgba(255, 255, 255, 0.05)",
                    "color": "#FFFFFF"
                },
                "nav-link-selected": {
                    "background-color": "#ef4444",
                    "color": "#FFFFFF",
                    "box-shadow": "0 2px 10px rgba(0, 0, 0, 0.3)"
                },
            }
        )
        
        # --- SINCRONIZAÇÃO DO FILTRO DE VIAGEM COM A SELEÇÃO DO MENU ---
        df_filtrado_por_tipo = df_filtrado.copy()
        if not df_filtrado_por_tipo.empty:
            # A função de classificação é chamada para garantir que a coluna exista
            df_classificado_completo = classificar_viagens_do_dia(df_filtrado)

            # Filtra APENAS se a opção não for "TODAS AS ROTAS"
            if tipo_viagem_ocupacao_sel == "ROTA COMPLETA":
                df_filtrado_por_tipo = df_classificado_completo[
                    df_classificado_completo['TIPO_VIAGEM_CALCULADO'] == "Rota Completa"
                ].copy()
            elif tipo_viagem_ocupacao_sel == "VIAGEM EXTRA":
                df_filtrado_por_tipo = df_classificado_completo[
                    df_classificado_completo['TIPO_VIAGEM_CALCULADO'] == "Viagem Extra"
                ].copy()
            # Se for "TODAS AS ROTAS", df_filtrado_por_tipo já é a cópia completa e não fazemos nada
            
            # Garante que, em qualquer caso, o dataframe final seja o classificado
            # para que a lógica subsequente funcione.
            else: # tipo_viagem_ocupacao_sel == "TODAS AS ROTAS"
                df_filtrado_por_tipo = df_classificado_completo.copy()


        # --- SE EXISTIR DADOS APÓS O FILTRO ---
        if not df_filtrado_por_tipo.empty:
            viagens_agrupadas_rotas = df_filtrado_por_tipo.groupby(
                ['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']
            )['DEST_MANIF'].unique().reset_index()

            viagens_agrupadas_rotas['NOME_ROTA_PADRAO'] = viagens_agrupadas_rotas['DEST_MANIF'].apply(obter_nome_rota_padronizado)
            lista_opcoes_rotas = ["(Todas as Rotas)"] + sorted(viagens_agrupadas_rotas['NOME_ROTA_PADRAO'].unique())

            # --- INÍCIO DA MODERNIZAÇÃO DO SELETOR ---
            # Envolve o seletor em uma div para aplicar o CSS customizado
            st.markdown("""
                <div class="custom-selectbox-container">
                    <div class="custom-selectbox-label">
                        <i class="fa-solid fa-map-signs"></i>
                        Selecione a Rota para Análise
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # O label é removido do selectbox e colocado no markdown acima
            rota_selecionada_ocupacao = st.selectbox(
                label="selectbox_ocupacao_por_rota_label", # Label interno para o Streamlit
                label_visibility="collapsed", # Esconde o label padrão
                options=lista_opcoes_rotas,
                key="selectbox_ocupacao_por_rota"
            )
           
            df_para_ocupacao = pd.DataFrame()
            if rota_selecionada_ocupacao == "(Todas as Rotas)":
                df_para_ocupacao = df_filtrado_por_tipo.copy()
            else:
                viagens_da_rota_selecionada = viagens_agrupadas_rotas[
                    viagens_agrupadas_rotas['NOME_ROTA_PADRAO'] == rota_selecionada_ocupacao
                ]
                chaves_viagens_rota = list(zip(
                    viagens_da_rota_selecionada['PLACA_CAVALO'],
                    viagens_da_rota_selecionada['DIA_EMISSAO_STR'],
                    viagens_da_rota_selecionada['MOTORISTA']
                ))
                if chaves_viagens_rota:
                    df_para_ocupacao = df_filtrado_por_tipo[
                        pd.MultiIndex.from_frame(df_filtrado_por_tipo[['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']]).isin(chaves_viagens_rota)
                    ]

            # --- CÁLCULO E EXIBIÇÃO DOS CARDS DE OCUPAÇÃO ---
            def obter_status_utilizacao_tab5(percentual):
                if percentual < 60:
                    return "Baixa ocupação", "occupancy-status-util-low"
                if percentual < 85:
                    return "Dentro da meta", "occupancy-status-util-ideal"
                return "Alta ocupação", "occupancy-status-util-high"

            def obter_status_ociosidade_tab5(percentual):
                if percentual > 40:
                    return "Alta ociosidade", "occupancy-status-idle-high"
                if percentual > 15:
                    return "Atenção", "occupancy-status-idle-ideal"
                return "Baixa ociosidade", "occupancy-status-idle-low"

            def obter_estilo_utilizacao_tab5(percentual):
                if percentual < 60:
                    return {
                        'barra': 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)',
                        'brilho': '0 0 18px rgba(245, 158, 11, 0.24)',
                        'percentual': '#fde68a'
                    }
                if percentual < 85:
                    return {
                        'barra': 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
                        'brilho': '0 0 18px rgba(59, 130, 246, 0.24)',
                        'percentual': '#bfdbfe'
                    }
                return {
                    'barra': 'linear-gradient(90deg, #22c55e 0%, #4ade80 100%)',
                    'brilho': '0 0 18px rgba(34, 197, 94, 0.24)',
                    'percentual': '#bbf7d0'
                }

            def obter_estilo_ociosidade_tab5(percentual):
                if percentual > 40:
                    return {
                        'barra': 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)',
                        'brilho': '0 0 18px rgba(245, 158, 11, 0.22)',
                        'percentual': '#fde68a',
                        'icone': '#fbbf24'
                    }
                if percentual > 15:
                    return {
                        'barra': 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%)',
                        'brilho': '0 0 18px rgba(59, 130, 246, 0.22)',
                        'percentual': '#bfdbfe',
                        'icone': '#60a5fa'
                    }
                return {
                    'barra': 'linear-gradient(90deg, #22c55e 0%, #4ade80 100%)',
                    'brilho': '0 0 18px rgba(34, 197, 94, 0.22)',
                    'percentual': '#bbf7d0',
                    'icone': '#4ade80'
                }

            def renderizar_card_ocupacao_moderno_tab5(
                titulo,
                ocup_perc,
                total_valor,
                cap_total,
                unidade,
                ociosidade_perc,
                potencial_nao_utilizado,
                icone_topo,
                icone_ociosidade,
                titulo_ociosidade,
                tema="peso"
            ):
                status_txt, status_cls = obter_status_utilizacao_tab5(ocup_perc)
                status_txt_idle, status_cls_idle = obter_status_ociosidade_tab5(ociosidade_perc)
                estilo_ocup = obter_estilo_utilizacao_tab5(ocup_perc)
                estilo_idle = obter_estilo_ociosidade_tab5(ociosidade_perc)
                classe_tema = "occupancy-theme-peso" if tema == "peso" else "occupancy-theme-volume"
                decimais_total = 3 if unidade == 'M³' else 0
                decimais_cap = 2 if unidade == 'M³' else 0
                decimais_potencial = 2 if unidade == 'M³' else 0

                st.markdown(f"""
                    <div class="occupancy-main-card {classe_tema}">
                        <div class="occupancy-main-header">
                            <div class="occupancy-title-wrap">
                                <div class="occupancy-card-title">
                                    <i class="fa-solid {icone_topo}"></i>
                                    <span>{titulo}</span>
                                </div>
                                <span class="occupancy-status-pill {status_cls}">{status_txt}</span>
                            </div>
                            <div class="occupancy-percent" style="color: {estilo_ocup['percentual']};">{ocup_perc:.0f}%</div>
                        </div>
                        <div class="occupancy-progress-track">
                            <div class="occupancy-progress-fill" style="width: {min(ocup_perc, 100)}%; background: {estilo_ocup['barra']}; box-shadow: {estilo_ocup['brilho']};"></div>
                        </div>
                        <div class="occupancy-divider"></div>
                        <div class="occupancy-chip-row">
                            <span class="occupancy-chip"><i class="fa-solid fa-cubes-stacked"></i> Total: {formatar_numero(total_valor, decimais_total)} {unidade}</span>
                            <span class="occupancy-chip"><i class="fa-solid fa-database"></i> Capacidade: {formatar_numero(cap_total, decimais_cap)} {unidade}</span>
                        </div>
                    </div>
                    <div class="occupancy-idle-card">
                        <div class="occupancy-idle-header">
                            <div class="occupancy-idle-title-wrap">
                                <div class="occupancy-idle-title">
                                    <i class="{icone_ociosidade}" style="color: {estilo_idle['icone']};"></i>
                                    <span>{titulo_ociosidade}</span>
                                </div>
                                <span class="occupancy-status-pill {status_cls_idle}">{status_txt_idle}</span>
                            </div>
                            <div class="occupancy-idle-percent" style="color: {estilo_idle['percentual']};">{ociosidade_perc:.0f}%</div>
                        </div>
                        <div class="occupancy-idle-progress-track">
                            <div class="occupancy-idle-progress-fill" style="width: {min(ociosidade_perc, 100)}%; background: {estilo_idle['barra']}; box-shadow: {estilo_idle['brilho']};"></div>
                        </div>
                        <div class="occupancy-idle-divider"></div>
                        <div class="occupancy-idle-footer">
                            <span class="occupancy-chip"><i class="{icone_ociosidade}" style="color: {estilo_idle['icone']};"></i> Total não utilizado: {formatar_numero(potencial_nao_utilizado, decimais_potencial)} {unidade}</span>
                            <span class="occupancy-chip"><i class="fa-solid fa-circle-minus" style="color: {estilo_idle['icone']};"></i> Não utilizado</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            def calcular_dados_ocupacao(df_dados):
                """
                VERSÃO CORRIGIDA: Remove a divisão por 10.000 da cubagem,
                assumindo que os dados do Excel já estão em M³.
                """
                if df_dados.empty:
                    return None

                dados = {}

                viagens_unicas = df_dados.drop_duplicates(subset=['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).copy()

                def get_capacidade_viagem_peso(row):
                    if obter_tipo_veiculo_base(row) == 'CAVALO':
                        return row.get('CAPACIDADE_KG', 0)
                    return row.get('CAPAC_CAVALO', 0)

                viagens_unicas['CAPACIDADE_PESO_VIAGEM'] = viagens_unicas.apply(get_capacidade_viagem_peso, axis=1)
                dados['cap_total_peso'] = viagens_unicas['CAPACIDADE_PESO_VIAGEM'].sum()
                dados['total_peso'] = somar_peso_calculo(df_dados)

                capacidades_volume_por_tipo = {'TRUCK': 75, 'CAVALO': 110, 'TOCO': 55, 'PADRAO': 80}
                viagens_unicas['CAP_VOL_VIAGEM'] = viagens_unicas.get('TIPO_CAVALO_ORIGINAL', viagens_unicas['TIPO_CAVALO']).map(capacidades_volume_por_tipo).fillna(capacidades_volume_por_tipo['PADRAO'])
                dados['cap_total_volume'] = viagens_unicas['CAP_VOL_VIAGEM'].sum()
                dados['total_volume'] = df_dados['M3'].sum()

                dados['ocup_peso_perc'] = (dados['total_peso'] / dados['cap_total_peso'] * 100) if dados['cap_total_peso'] > 0 else 0
                dados['ociosidade_peso_perc'] = 100 - dados['ocup_peso_perc']
                dados['potencial_nao_utilizado_kg'] = max(0, dados['cap_total_peso'] - dados['total_peso'])

                dados['ocup_volume_perc'] = (dados['total_volume'] / dados['cap_total_volume'] * 100) if dados['cap_total_volume'] > 0 else 0
                dados['ociosidade_volume_perc'] = 100 - dados['ocup_volume_perc']
                dados['potencial_nao_utilizado_m3'] = max(0, dados['cap_total_volume'] - dados['total_volume'])

                return dados

            def obter_status_ctrb_frete_tab5(percentual):
                if percentual <= 25:
                    return "Dentro da meta", "ctrb-gauge-status-good"
                elif percentual <= 45:
                    return "Faixa de atenção", "ctrb-gauge-status-regular"
                return "Acima da meta", "ctrb-gauge-status-bad"

            def calcular_resumo_ctrb_frete_tab5(df_dados):
                if df_dados.empty:
                    return None

                df_temp = df_dados.copy()

                if 'VIAGEM_ID' not in df_temp.columns:
                    df_temp['VIAGEM_ID'] = df_temp.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

                resumo_ctrb = df_temp.groupby('VIAGEM_ID').agg(
                    PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                    CUSTO_OS=('OS-R$', 'max'),
                    CUSTO_CTRB=('CTRB-R$', 'max'),
                    FRETE_TOTAL=('FRETE-R$', 'sum'),
                    DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.astype(str).dropna().unique()))
                ).reset_index()

                def calcular_custo_ctrb_card(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    destinos_str = str(row.get('DESTINOS', '')).upper()
                    if 'GYN' in destinos_str or 'SPO' in destinos_str:
                        return custo_base / 2
                    return custo_base

                resumo_ctrb['CUSTO_FINAL'] = resumo_ctrb.apply(calcular_custo_ctrb_card, axis=1)
                frete_total = pd.to_numeric(resumo_ctrb['FRETE_TOTAL'], errors='coerce').fillna(0).sum()
                custo_total = pd.to_numeric(resumo_ctrb['CUSTO_FINAL'], errors='coerce').fillna(0).sum()
                percentual_ponderado = (custo_total / frete_total * 100) if frete_total > 0 else 0

                return {
                    'percentual': percentual_ponderado,
                    'qtd_viagens': int(len(resumo_ctrb)),
                    'custo_total': custo_total,
                    'frete_total': frete_total
                }

            def polar_para_cartesiano_tab5(cx, cy, raio, angulo_graus):
                angulo_rad = math.radians(angulo_graus)
                return (
                    cx + (raio * math.cos(angulo_rad)),
                    cy - (raio * math.sin(angulo_rad))
                )

            def descrever_arco_svg_tab5(cx, cy, raio, angulo_inicial, angulo_final):
                x1, y1 = polar_para_cartesiano_tab5(cx, cy, raio, angulo_inicial)
                x2, y2 = polar_para_cartesiano_tab5(cx, cy, raio, angulo_final)
                large_arc = 1 if abs(angulo_final - angulo_inicial) > 180 else 0
                return f"M {x1:.2f} {y1:.2f} A {raio:.2f} {raio:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f}"

            def renderizar_gauge_ctrb_frete_tab5(percentual, qtd_viagens, filtro_rota, filtro_tipo):
                percentual_clamp = max(0, min(percentual, 100))
                status_txt, status_cls = obter_status_ctrb_frete_tab5(percentual_clamp)

                cx, cy, raio = 150, 148, 108
                arco_total = descrever_arco_svg_tab5(cx, cy, raio, 180, 0)
                arco_externo = descrever_arco_svg_tab5(cx, cy, raio + 7, 180, 0)
                arco_interno = descrever_arco_svg_tab5(cx, cy, raio - 17, 180, 0)
                arco_verde = descrever_arco_svg_tab5(cx, cy, raio, 180, 135)
                arco_amarelo = descrever_arco_svg_tab5(cx, cy, raio, 135, 99)
                arco_vermelho = descrever_arco_svg_tab5(cx, cy, raio, 99, 0)

                angulo_ponteiro = 180 - (percentual_clamp / 100 * 180)
                ponta_x, ponta_y = polar_para_cartesiano_tab5(cx, cy, raio - 21, angulo_ponteiro)
                base_luz_x, base_luz_y = polar_para_cartesiano_tab5(cx, cy, raio - 33, angulo_ponteiro)

                def marcador_tick(valor, extra=0):
                    ang = 180 - (valor / 100 * 180)
                    x1, y1 = polar_para_cartesiano_tab5(cx, cy, raio + 6 + extra, ang)
                    x2, y2 = polar_para_cartesiano_tab5(cx, cy, raio - 10, ang)
                    lx, ly = polar_para_cartesiano_tab5(cx, cy, raio + 24 + extra, ang)
                    return (x1, y1, x2, y2, lx, ly)

                ticks = {
                    0: marcador_tick(0),
                    25: marcador_tick(25),
                    45: marcador_tick(45),
                    100: marcador_tick(100)
                }

                minor_ticks = []
                for valor in [10, 20, 35, 55, 70, 85]:
                    ang = 180 - (valor / 100 * 180)
                    x1, y1 = polar_para_cartesiano_tab5(cx, cy, raio + 4, ang)
                    x2, y2 = polar_para_cartesiano_tab5(cx, cy, raio - 4, ang)
                    minor_ticks.append((x1, y1, x2, y2))

                status_map = {
                    "ctrb-gauge-status-good": ("rgba(6, 78, 59, 0.34)", "rgba(34,197,94,0.72)", "#dcfce7"),
                    "ctrb-gauge-status-regular": ("rgba(120, 53, 15, 0.34)", "rgba(245,158,11,0.72)", "#fef3c7"),
                    "ctrb-gauge-status-bad": ("rgba(127, 29, 29, 0.34)", "rgba(239,68,68,0.72)", "#fee2e2"),
                }
                status_bg, status_border, status_fg = status_map.get(
                    status_cls, ("rgba(6, 78, 59, 0.34)", "rgba(34,197,94,0.72)", "#dcfce7")
                )

                rota_label = "Todas as Rotas" if filtro_rota == "(Todas as Rotas)" else filtro_rota
                tipo_label = filtro_tipo.title() if filtro_tipo else "Todas as Rotas"

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="utf-8" />
                  <style>
                    html, body {{
                      margin: 0;
                      padding: 0;
                      background: transparent;
                      font-family: 'Segoe UI', 'Inter', sans-serif;
                    }}
                    .g-wrap {{
                      width: 100%;
                      display: flex;
                      justify-content: center;
                      align-items: flex-start;
                    }}
                    .g-card {{
                      width: 100%;
                      max-width: 590px;
                      min-height: 430px;
                      border-radius: 24px;
                      padding: 16px 18px 22px 18px;
                      box-sizing: border-box;
                      overflow: hidden;
                      position: relative;
                      background:
                        radial-gradient(circle at 50% 0%, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.00) 34%),
                        radial-gradient(circle at 8% 10%, rgba(59,130,246,0.20) 0%, rgba(59,130,246,0.00) 28%),
                        radial-gradient(circle at 92% 6%, rgba(16,185,129,0.18) 0%, rgba(16,185,129,0.00) 26%),
                        linear-gradient(180deg, #122338 0%, #0b1730 48%, #08111f 100%);
                      border: 1px solid rgba(255,255,255,0.08);
                      box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 22px 40px rgba(2,6,23,0.34);
                    }}
                    .g-card::before {{
                      content: '';
                      position: absolute;
                      inset: 0;
                      background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.00) 24%);
                      pointer-events: none;
                    }}
                    .g-header {{
                      position: relative;
                      z-index: 2;
                      text-align: center;
                      margin-bottom: 2px;
                    }}
                    .g-kicker {{
                      display: inline-flex;
                      align-items: center;
                      gap: 10px;
                      padding: 6px 13px;
                      border-radius: 999px;
                      background: rgba(15,23,42,0.48);
                      border: 1px solid rgba(148,163,184,0.16);
                      color: #c7d2fe;
                      font-size: 10px;
                      font-weight: 900;
                      letter-spacing: 1px;
                      text-transform: uppercase;
                    }}
                    .g-title {{
                      margin-top: 10px;
                      color: #f8fafc;
                      font-weight: 900;
                      font-size: 21px;
                      line-height: 1.15;
                      letter-spacing: 0.2px;
                      text-shadow: 0 2px 14px rgba(0,0,0,0.30);
                    }}
                    .g-svg {{
                      width: 100%;
                      display: flex;
                      justify-content: center;
                      margin-top: 2px;
                      position: relative;
                      z-index: 2;
                    }}
                    svg {{
                      width: 352px;
                      height: 204px;
                      overflow: visible;
                    }}
                    .tick-major {{ stroke: rgba(255,255,255,0.32); stroke-width: 1.8; stroke-linecap: round; }}
                    .tick-minor {{ stroke: rgba(255,255,255,0.18); stroke-width: 1.05; stroke-linecap: round; }}
                    .tick-label {{ fill: #f8fafc; font-size: 10px; font-weight: 900; letter-spacing: 0.3px; }}
                    .meta-label {{ fill: rgba(226,232,240,0.72); font-size: 8px; font-weight: 800; letter-spacing: 0.9px; text-transform: uppercase; }}
                    .g-value {{
                      text-align: center;
                      margin-top: -2px;
                      color: #ffffff;
                      font-size: 44px;
                      font-weight: 900;
                      line-height: 1;
                      letter-spacing: -1px;
                      position: relative;
                      z-index: 2;
                      text-shadow: 0 4px 18px rgba(0,0,0,0.42), 0 0 18px rgba(56,189,248,0.14);
                    }}
                    .g-status {{
                      margin: 14px auto 12px auto;
                      width: fit-content;
                      padding: 9px 20px;
                      border-radius: 999px;
                      background: {status_bg};
                      border: 1px solid {status_border};
                      color: {status_fg};
                      font-size: 13px;
                      font-weight: 900;
                      position: relative;
                      z-index: 2;
                      box-shadow: inset 0 1px 0 rgba(255,255,255,0.10), 0 0 18px rgba(0,0,0,0.12);
                    }}
                    .g-foot {{
                      display: flex;
                      flex-wrap: wrap;
                      justify-content: center;
                      gap: 12px;
                      margin-top: 4px;
                      padding-bottom: 2px;
                      position: relative;
                      z-index: 2;
                    }}
                    .g-chip {{
                      display: inline-flex;
                      align-items: center;
                      gap: 7px;
                      padding: 8px 13px;
                      border-radius: 999px;
                      background: rgba(15,23,42,0.42);
                      border: 1px solid rgba(255,255,255,0.10);
                      color: #e2e8f0;
                      font-size: 11px;
                      font-weight: 800;
                      line-height: 1;
                      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
                    }}
                    .g-chip i {{ font-style: normal; font-size: 12px; }}
                    .g-chip.filter i {{ color: #fbbf24; }}
                    .g-chip.base i {{ color: #60a5fa; }}
                  </style>
                </head>
                <body>
                  <div class="g-wrap">
                    <div class="g-card">
                      <div class="g-header">
                        <div class="g-kicker">⚙️ Custo de Transferência</div>
                        <div class="g-title">Monitoramento CTRB/Frete por Rota</div>
                      </div>
                      <div class="g-svg">
                        <svg viewBox="0 0 300 184" xmlns="http://www.w3.org/2000/svg">
                          <defs>
                            <linearGradient id="metalRing" x1="0%" y1="0%" x2="100%" y2="100%">
                              <stop offset="0%" stop-color="#dbe4ee" stop-opacity="0.40"/>
                              <stop offset="24%" stop-color="#6b7b92" stop-opacity="0.28"/>
                              <stop offset="50%" stop-color="#1f2937" stop-opacity="0.16"/>
                              <stop offset="78%" stop-color="#95a4ba" stop-opacity="0.28"/>
                              <stop offset="100%" stop-color="#f8fafc" stop-opacity="0.38"/>
                            </linearGradient>
                            <linearGradient id="needleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" stop-color="#dbeafe" stop-opacity="0.56"/>
                              <stop offset="68%" stop-color="#ffffff" stop-opacity="0.96"/>
                              <stop offset="100%" stop-color="#ffffff" stop-opacity="1"/>
                            </linearGradient>
                            <radialGradient id="hubGrad" cx="50%" cy="38%" r="62%">
                              <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.96"/>
                              <stop offset="28%" stop-color="#cbd5e1" stop-opacity="0.88"/>
                              <stop offset="58%" stop-color="#334155" stop-opacity="0.95"/>
                              <stop offset="100%" stop-color="#020617" stop-opacity="1"/>
                            </radialGradient>
                            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                              <feGaussianBlur stdDeviation="3.5" result="blur"/>
                              <feMerge>
                                <feMergeNode in="blur"/>
                                <feMergeNode in="SourceGraphic"/>
                              </feMerge>
                            </filter>
                            <filter id="softShadow" x="-50%" y="-50%" width="200%" height="200%">
                              <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#020617" flood-opacity="0.60"/>
                            </filter>
                          </defs>

                          <ellipse cx="150" cy="144" rx="108" ry="17" fill="rgba(2,6,23,0.38)"/>
                          <path d="{arco_externo}" fill="none" stroke="url(#metalRing)" stroke-width="4" stroke-linecap="round" opacity="0.86"/>
                          <path d="{arco_total}" fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="22" stroke-linecap="round"/>
                          <path d="{arco_interno}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="3" stroke-linecap="round"/>
                          <path d="{arco_verde}" fill="none" stroke="#22c55e" stroke-width="18" stroke-linecap="round" filter="url(#glow)"/>
                          <path d="{arco_amarelo}" fill="none" stroke="#f59e0b" stroke-width="18" stroke-linecap="round" filter="url(#glow)"/>
                          <path d="{arco_vermelho}" fill="none" stroke="#ef4444" stroke-width="18" stroke-linecap="round" filter="url(#glow)"/>

                          {''.join([f'<line class="tick-minor" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>' for x1, y1, x2, y2 in minor_ticks])}
                          <line class="tick-major" x1="{ticks[0][0]:.2f}" y1="{ticks[0][1]:.2f}" x2="{ticks[0][2]:.2f}" y2="{ticks[0][3]:.2f}"/>
                          <line class="tick-major" x1="{ticks[25][0]:.2f}" y1="{ticks[25][1]:.2f}" x2="{ticks[25][2]:.2f}" y2="{ticks[25][3]:.2f}"/>
                          <line class="tick-major" x1="{ticks[45][0]:.2f}" y1="{ticks[45][1]:.2f}" x2="{ticks[45][2]:.2f}" y2="{ticks[45][3]:.2f}"/>
                          <line class="tick-major" x1="{ticks[100][0]:.2f}" y1="{ticks[100][1]:.2f}" x2="{ticks[100][2]:.2f}" y2="{ticks[100][3]:.2f}"/>

                          <text class="tick-label" x="{ticks[0][4]:.2f}" y="{ticks[0][5] + 4:.2f}" text-anchor="middle">0%</text>
                          <text class="tick-label" x="{ticks[25][4]:.2f}" y="{ticks[25][5] - 2:.2f}" text-anchor="middle">25%</text>
                          <text class="tick-label" x="{ticks[45][4]:.2f}" y="{ticks[45][5] - 2:.2f}" text-anchor="middle">45%</text>
                          <text class="tick-label" x="{ticks[100][4]:.2f}" y="{ticks[100][5] + 4:.2f}" text-anchor="middle">100%</text>

                          <line x1="{cx}" y1="{cy}" x2="{base_luz_x:.2f}" y2="{base_luz_y:.2f}" stroke="rgba(56,189,248,0.16)" stroke-width="8" stroke-linecap="round"/>
                          <line x1="{cx}" y1="{cy}" x2="{ponta_x:.2f}" y2="{ponta_y:.2f}" stroke="url(#needleGrad)" stroke-width="4.8" stroke-linecap="round" filter="url(#softShadow)"/>
                          <circle cx="{cx}" cy="{cy}" r="14" fill="url(#hubGrad)" stroke="rgba(248,250,252,0.34)" stroke-width="1.8"/>
                          <circle cx="{cx}" cy="{cy}" r="5" fill="#f8fafc"/>

                          <text class="meta-label" x="150" y="106" text-anchor="middle">PERFORMANCE OPERACIONAL DA ROTA</text>
                        </svg>
                      </div>
                      <div class="g-value">{percentual_clamp:.0f}%</div>
                      <div class="g-status">{status_txt}</div>
                      <div class="g-foot">
                        <span class="g-chip filter"><i>⛃</i> Rota: {rota_label}</span>
                        <span class="g-chip base"><i>◉</i> Base: {qtd_viagens} viagem(ns) · {tipo_label}</span>
                      </div>
                    </div>
                  </div>
                </body>
                </html>
                """

                components.html(html, height=520, scrolling=False)

            dados_agregados = calcular_dados_ocupacao(df_para_ocupacao)
            resumo_ctrb_card_tab5 = calcular_resumo_ctrb_frete_tab5(df_para_ocupacao)

            if dados_agregados:
                col_esq, col_meio, col_dir = st.columns([1.02, 0.96, 1.02], gap="medium")
                deslocamento_ocupacao_lateral_px = 34

                with col_esq:
                    st.markdown(f"<div style='height: {deslocamento_ocupacao_lateral_px}px;'></div>", unsafe_allow_html=True)
                    renderizar_card_ocupacao_moderno_tab5(
                        titulo="Ocupação de Peso (KG)",
                        ocup_perc=dados_agregados['ocup_peso_perc'],
                        total_valor=dados_agregados['total_peso'],
                        cap_total=dados_agregados['cap_total_peso'],
                        unidade="KG",
                        ociosidade_perc=dados_agregados['ociosidade_peso_perc'],
                        potencial_nao_utilizado=dados_agregados['potencial_nao_utilizado_kg'],
                        icone_topo="fa-weight-hanging",
                        icone_ociosidade="fa-solid fa-scale-unbalanced-flip",
                        titulo_ociosidade="Ociosidade de Peso",
                        tema="peso"
                    )

                with col_meio:
                    if resumo_ctrb_card_tab5:
                        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                        renderizar_gauge_ctrb_frete_tab5(
                            percentual=resumo_ctrb_card_tab5['percentual'],
                            qtd_viagens=resumo_ctrb_card_tab5['qtd_viagens'],
                            filtro_rota=rota_selecionada_ocupacao,
                            filtro_tipo=tipo_viagem_ocupacao_sel
                        )

                with col_dir:
                    st.markdown(f"<div style='height: {deslocamento_ocupacao_lateral_px}px;'></div>", unsafe_allow_html=True)
                    renderizar_card_ocupacao_moderno_tab5(
                        titulo="Ocupação de Cubagem (M³)",
                        ocup_perc=dados_agregados['ocup_volume_perc'],
                        total_valor=dados_agregados['total_volume'],
                        cap_total=dados_agregados['cap_total_volume'],
                        unidade="M³",
                        ociosidade_perc=dados_agregados['ociosidade_volume_perc'],
                        potencial_nao_utilizado=dados_agregados['potencial_nao_utilizado_m3'],
                        icone_topo="fa-boxes-stacked",
                        icone_ociosidade="fa-solid fa-box-open",
                        titulo_ociosidade="Ociosidade de Cubagem",
                        tema="volume"
                    )
            else:
                if resumo_ctrb_card_tab5:
                    gauge_left, gauge_center, gauge_right = st.columns([1, 1.12, 1], gap="large")
                    with gauge_center:
                        renderizar_gauge_ctrb_frete_tab5(
                            percentual=resumo_ctrb_card_tab5['percentual'],
                            qtd_viagens=resumo_ctrb_card_tab5['qtd_viagens'],
                            filtro_rota=rota_selecionada_ocupacao,
                            filtro_tipo=tipo_viagem_ocupacao_sel
                        )
                st.info(f"Nenhum dado de ocupação para calcular para a rota '{rota_selecionada_ocupacao}' no período e tipo de viagem selecionados.")

            # =================================================================
            # 🔹 DETALHES POR DESTINO DENTRO DA ROTA (VERSÃO FINAL CORRIGIDA)
            # =================================================================

            def fmt_moeda(valor):
                """Formata número como moeda brasileira: R$ 1.234,56"""
                if pd.isna(valor):
                    return "R$ 0,00"
                return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            def fmt_num(valor):
                """Formata número inteiro com separador de milhar"""
                if pd.isna(valor):
                    return "0"
                return f"{int(valor):,}".replace(",", ".")

            # =================================================================
            # 🔹 DETALHES POR DESTINO DENTRO DA ROTA (VERSÃO FINAL CORRIGIDA)
            # =================================================================

            # Esta condição verifica se uma rota específica ou uma viagem específica foi selecionada.
            if rota_selecionada_ocupacao != "(Todas as Rotas)" or viagem_especifica_sel != "(Todos)":

                # --- 1. Adiciona um separador e o CSS específico para os novos cards ---
                st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

                # --- INÍCIO DA NOVA LÓGICA PARA O TÍTULO ---
                titulo_analise = ""

                # Se uma VIAGEM ESPECÍFICA for selecionada, monta o título detalhado
                if viagem_especifica_sel != "(Todos)":
                    # Busca os detalhes da viagem selecionada no dataframe 'rotas_df_antigo'
                    viagem_selecionada_info = rotas_df_antigo[rotas_df_antigo['NOME_ROTA_ANTIGO'] == viagem_especifica_sel]
                    
                    if not viagem_selecionada_info.empty:
                        # Pega a primeira (e única) linha de resultado
                        info = viagem_selecionada_info.iloc[0]
                        
                        # Extrai os dados para o título
                        destinos = info['Destinos'] # Já vem formatado como 'DOU - RBT'
                        motorista = info['NOME_CURTO_MOTORISTA']
                        
                        # Monta o título no formato desejado
                        titulo_analise = f"{destinos}  | 👨‍✈️ {motorista}"
                    else:
                        # Fallback caso não encontre a informação
                        titulo_analise = "Viagem Específica"

                # Se um GRUPO DE ROTAS for selecionado, usa o nome do grupo
                elif rota_selecionada_ocupacao != "(Todas as Rotas)":
                    titulo_analise = rota_selecionada_ocupacao
                # --- FIM DA NOVA LÓGICA PARA O TÍTULO ---


                # ✅ TÍTULO ATUALIZADO COM OS DETALHES DA VIAGEM
                st.markdown(
                    f'<h3 class="section-title-modern">'
                    f'<i class="fa-solid fa-chart-line"></i> '
                    f'Análise Operacional – <span style="color:#3B82F6;">{titulo_analise}</span>'
                    f'</h3>',
                    unsafe_allow_html=True
                )

                st.markdown("""
                <style>
                .detail-section-title {
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #FFFFFF;
                    margin-top: 1.5rem;
                    margin-bottom: 0.8rem;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .detail-card {
                    background-color: #1F2937;
                    border-radius: 12px;
                    padding: 20px;
                    border: 1px solid #374151;
                    height: 100%;
                    margin-bottom: 1rem;
                }
                .detail-card-title {
                    font-size: 1.2rem;          /* <<< TAMANHO DA FONTE AUMENTADO */
                    font-weight: 700;           /* <<< PESO DA FONTE AUMENTADO (BOLD) */
                    color: #FFFFFF;             /* Cor mais branca para destaque */
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start; /* <<< ALTERADO DE 'center' PARA 'flex-start' */
                    gap: 12px;                  /* Espaço entre o ícone e o texto */
                    text-transform: uppercase;  /* Garante que o texto fique em maiúsculas */
                }
                            
                .detail-card-title .fa-map-pin { color: #EF4444; }
                .detail-grid {  
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                }
                .metric-item {
                    background-color: #111827;
                    padding: 12px;
                    border-radius: 8px;
                }
                .metric-label {
                    font-size: 0.9rem;      /* <<< TAMANHO DA FONTE AUMENTADO */
                    color: #B0B8C4;         /* Cor um pouco mais clara para legibilidade */
                    margin-bottom: 8px;     /* Aumenta o espaço entre o rótulo e o valor */
                    display: flex;
                    align-items: center;
                    gap: 10px;               /* Aumenta o espaço entre o ícone e o texto */
                    font-weight: 500;       /* Deixa a fonte um pouco mais encorpada */
}
                .metric-value {
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: #FFFFFF;
                }
                .metric-label .fa-weight-hanging { color: #F59E0B; }
                .metric-label .fa-cube { color: #3B82F6; }
                .metric-label .fa-hand-holding-dollar { color: #22C55E; }
                .metric-label .fa-truck-ramp-box { color: #22C55E; }
                .metric-label .fa-file-invoice { color: #8B5CF6; }
                .metric-label .fa-boxes-stacked { color: #F97316; }
                </style>
                """, unsafe_allow_html=True)

                # --- 2. AGREGA OS DADOS por cidade, usando o DataFrame da rota selecionada ---
                carga_por_cidade = df_para_ocupacao.groupby('CIDADE_UF_DEST').agg(
                    PESO_TOTAL=(obter_nome_coluna_peso_calculo(df_para_ocupacao) or 'PESO REAL (KG)', 'sum'),
                    VOLUME_TOTAL=('M3', 'sum'),
                    FRETE_TOTAL=('FRETE-R$', 'sum'),
                    VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                    QTDE_CTRC=('QTDE_CTRC', 'sum'),
                    QTDE_VOLUME=('VOLUMES', 'sum')
                ).reset_index()

                # ▼▼▼ INÍCIO DA CORREÇÃO FINAL E MAIS ROBUSTA ▼▼▼

                # 1. Cria um dicionário reverso para "traduzir" NOME COMPLETO -> SIGLA
                mapa_nome_para_sigla = {nome.upper(): sigla for sigla, nome in MAPA_SIGLA_NOME_COMPLETO.items()}

                # 2. Adiciona uma coluna temporária 'SIGLA' ao DataFrame 'carga_por_cidade'
                carga_por_cidade['SIGLA'] = carga_por_cidade['CIDADE_UF_DEST'].str.upper().map(mapa_nome_para_sigla)

                # 3. Busca a ordem correta das SIGLAS para a rota selecionada
                rota_selecionada = rota_selecionada_ocupacao
                ordem_siglas_correta = ORDEM_DAS_ROTAS.get(rota_selecionada, [])

                # 4. Se uma ordem foi encontrada, usa-a para ordenar o DataFrame pelas SIGLAS
                if ordem_siglas_correta:
                    # Converte a coluna 'SIGLA' para uma categoria ordenada
                    carga_por_cidade['SIGLA'] = pd.Categorical(
                        carga_por_cidade['SIGLA'],
                        categories=ordem_siglas_correta,
                        ordered=True
                    )
                    # Ordena o DataFrame com base na ordem das siglas e remove a coluna temporária
                    carga_por_cidade = carga_por_cidade.sort_values('SIGLA').drop(columns=['SIGLA'])

                # ▲▲▲ FIM DA CORREÇÃO FINAL ▲▲▲


                # --- BLOCO DE KPIs POR CIDADE ---
                num_cidades = len(carga_por_cidade)
                cols = st.columns(num_cidades if num_cidades > 0 else 1)

                def fmt_m3(valor):
                    """Formata volume em m³ com 3 casas decimais e separador brasileiro"""
                    if pd.isna(valor):
                        return "0,000"
                    return f"{round(valor, 3):,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


                for i, row in carga_por_cidade.iterrows():
                    with cols[i]:
                        html = f"""
                <div class="detail-card">
                <div class="detail-card-title">
                    <i class="fa-solid fa-map-pin"></i> {row['CIDADE_UF_DEST']}
                </div>

                <div class="detail-section-title"><i class="fa-solid fa-chart-line"></i> Indicadores de Performance</div>
                <div class="detail-grid">
                    <div class="metric-item">
                    <div class="metric-label"><i class="fa-solid fa-hand-holding-dollar"></i> Frete Total</div>
                    <div class="metric-value">{fmt_moeda(row['FRETE_TOTAL'])}</div>
                    </div>
                    <div class="metric-item">
                    <div class="metric-label"><i class="fa-solid fa-truck-ramp-box"></i> Mercadoria</div>
                    <div class="metric-value">{fmt_moeda(row['VALOR_MERCADORIA'])}</div>
                    </div>
                    <div class="metric-item">
                    <div class="metric-label"><i class="fa-solid fa-weight-hanging"></i> Peso</div>
                    <div class="metric-value">{fmt_num(row['PESO_TOTAL'])} kg</div>
                    </div>
                    <div class="metric-item">
                    <div class="metric-label"><i class="fa-solid fa-cube"></i> Cubagem</div>
                    <div class="metric-value">{fmt_m3(row['VOLUME_TOTAL'])} M³</div>
                    </div>
                </div>

                <div class="detail-section-title"><i class="fa-solid fa-gears"></i> Indicadores Operacionais</div>
                <div class="detail-grid">
                    <div class="metric-item">
                    <div class="metric-label"><i class="fa-solid fa-file-invoice"></i> CTRCs</div>
                    <div class="metric-value">{fmt_num(row['QTDE_CTRC'])}</div>
                    </div>
                    <div class="metric-item">
                    <div class="metric-label"><i class="fa-solid fa-boxes-stacked"></i> Qtd. Volumes</div>
                    <div class="metric-value">{fmt_num(row['QTDE_VOLUME'])}</div>
                    </div>
                </div>
                </div>
                """
                        st.markdown(html, unsafe_allow_html=True)
       
            st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

            # --- SEÇÃO DE INDICADORES DE PERFORMANCE ---
            kpi_view_rotas = option_menu(
                menu_title=None,
                options=["MÉDIAS E ÍNDICES", "VALORES TOTAIS"],  # 🔠 Maiúsculo
                icons=["graph-up-arrow", "calculator"],
                menu_icon=None,  # 🔇 remove ícone global
                default_index=0,
                orientation="horizontal",
                key="kpi_view_selector_tab5",
                styles={
                    "container": {
                        "padding": "6px",
                        "background-color": "rgba(30, 30, 40, 0.4)",
                        "border-radius": "16px",
                        "justify-content": "center",
                        "margin-bottom": "25px"
                    },
                    "icon": {
                        "color": "#A3A3A3",
                        "font-size": "16px"
                    },
                    "nav-link": {
                        "font-size": "14px",
                        "font-weight": "700",              # negrito mais forte
                        "color": "#E5E7EB",
                        "text-transform": "uppercase",     # 🔠 força maiúsculo
                        "padding": "10px 26px",
                        "border-radius": "12px",
                        "margin": "0px 6px",
                        "background-color": "rgba(255, 255, 255, 0.05)",
                        "transition": "all 0.3s ease"
                    },
                    "nav-link:hover": {
                        "background-color": "rgba(255,255,255,0.12)",
                        "color": "#FFFFFF"
                    },
                    "nav-link-selected": {
                        "background-color": "#222433",
                        "color": "#FFFFFF",
                        "border": "1.5px solid #ef4444",
                        "box-shadow": "0 0 15px rgba(239, 68, 68, 0.6)"
                    },
                }
            )

            if not df_para_ocupacao.empty:
                coluna_peso_ocupacao = obter_nome_coluna_peso_calculo(df_para_ocupacao) or 'PESO REAL (KG)'
                resumo_viagens_kpi = df_para_ocupacao.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).agg(CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'), PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), TIPO_VEICULO=('TIPO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', lambda x: ' / '.join(x.unique())), PESO_VIAGEM=(coluna_peso_ocupacao, 'sum'), ENTREGAS_VIAGEM=('DEST_MANIF', 'nunique'), FRETE_VIAGEM=('FRETE-R$', 'sum'), CAPACIDADE_PESO=('CAPACIDADE_KG', 'first'), CAPACIDADE_PESO_CAVALO=('CAPAC_CAVALO', 'first')).reset_index()
                def calcular_custo_ajustado(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    if 'GYN' in str(row['DESTINOS']) or 'SPO' in str(row['DESTINOS']): return custo_base / 2
                    return custo_base
                resumo_viagens_kpi['CUSTO_AJUSTADO'] = resumo_viagens_kpi.apply(calcular_custo_ajustado, axis=1)
                custo_km_por_tipo = {'TOCO': 3.50, 'TRUCK': 4.50, 'CAVALO': 6.75, 'CARRETA': 6.75}
                def calcular_distancia_viagem(row):
                    valor_km = custo_km_por_tipo.get(str(row['TIPO_VEICULO']).upper(), 0)
                    if valor_km > 0: return row['CUSTO_AJUSTADO'] / valor_km
                    return 0
                resumo_viagens_kpi['DISTANCIA_VIAGEM'] = resumo_viagens_kpi.apply(calcular_distancia_viagem, axis=1)
                def get_capacidade_correta(row):
                    if row['TIPO_VEICULO'] == 'CAVALO': return row['CAPACIDADE_PESO']
                    return row['CAPACIDADE_PESO_CAVALO']
                resumo_viagens_kpi['CAPACIDADE_VIAGEM'] = resumo_viagens_kpi.apply(get_capacidade_correta, axis=1)
                total_viagens = len(resumo_viagens_kpi)
                distancia_total = resumo_viagens_kpi['DISTANCIA_VIAGEM'].sum()
                total_entregas = resumo_viagens_kpi['ENTREGAS_VIAGEM'].sum()
                peso_total = resumo_viagens_kpi['PESO_VIAGEM'].sum()
                custo_total_kpi = resumo_viagens_kpi['CUSTO_AJUSTADO'].sum()
                frete_total_kpi = resumo_viagens_kpi['FRETE_VIAGEM'].sum()
                capacidade_total_kpi = resumo_viagens_kpi['CAPACIDADE_VIAGEM'].sum()
                distancia_media = distancia_total / total_viagens if total_viagens > 0 else 0
                peso_medio_viagem = peso_total / total_viagens if total_viagens > 0 else 0
                ocupacao_media = (peso_total / capacidade_total_kpi * 100) if capacidade_total_kpi > 0 else 0
                perc_custo_frete = (custo_total_kpi / frete_total_kpi * 100) if frete_total_kpi > 0 else 0
                kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
                if kpi_view_rotas.upper() == "MÉDIAS E ÍNDICES":
                    kpis_data = [{'titulo': "🗺️ TOTAL DE VIAGENS", "valor": f"{total_viagens}"}, {'titulo': "🚛 DISTÂNCIA MÉDIA", "valor": f"{int(distancia_media):,} km".replace(",", ".")}, {'titulo': "📦 TOTAL DE ENTREGAS", "valor": f"{total_entregas}"}, {'titulo': "⚖️ PESO MÉDIO / VIAGEM", "valor": f"{int(peso_medio_viagem):,} kg".replace(",", ".")}, {'titulo': "📈 OCUPAÇÃO MÉDIA", "valor": f"{ocupacao_media:.0f}%"}, {'titulo': "📊 % CUSTO / FRETE", "valor": f"{perc_custo_frete:.0f}%"}]
                else:
                    kpis_data = [{'titulo': "🗺️ TOTAL DE VIAGENS", "valor": f"{total_viagens}"}, {'titulo': "🚛 DISTÂNCIA TOTAL", "valor": f"{int(distancia_total):,} km".replace(",", ".")}, {'titulo': "📦 TOTAL DE ENTREGAS", "valor": f"{total_entregas}"}, {'titulo': "⚖️ PESO TOTAL", "valor": f"{int(peso_total):,} kg".replace(",", ".")}, {'titulo': "💰 CUSTO TOTAL (CTRB/OS)", "valor": formatar_moeda(custo_total_kpi)}, {'titulo': "💵 FRETE TOTAL", "valor": formatar_moeda(frete_total_kpi)}]
                colunas_kpi = [kpi1, kpi2, kpi3, kpi4, kpi5, kpi6]
                for i, info in enumerate(kpis_data):
                    with colunas_kpi[i]:
                        st.markdown(f"""<div class='kpi-container' style='text-align: center;'><div class='kpi-title'>{info['titulo']}</div><div class='kpi-value'>{info['valor']}</div></div>""", unsafe_allow_html=True)
            else:
                st.info("Não há dados de performance para exibir para a seleção atual.")

            # --- ▼▼▼ INÍCIO DO BLOCO DE GRÁFICOS DE BARRAS (COM LÓGICA ATUALIZADA) ▼▼▼

            # A exibição dos gráficos agora depende apenas de haver dados
            if not df_para_ocupacao.empty:
                st.markdown('<hr style="border: 1px solid #333; margin: 20px 0;">', unsafe_allow_html=True)

                # 1. PREPARAÇÃO DOS DADOS (AGORA COM LÓGICA CONDICIONAL)
                coluna_peso_ocupacao = obter_nome_coluna_peso_calculo(df_para_ocupacao) or 'PESO REAL (KG)'
                resumo_viagens_base = df_para_ocupacao.groupby(['PLACA_CAVALO', 'DIA_EMISSAO_STR', 'MOTORISTA']).agg(
                    CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
                    PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'), DESTINOS=('DEST_MANIF', 'unique'),
                    PESO_VIAGEM=(coluna_peso_ocupacao, 'sum'), FRETE_VIAGEM=('FRETE-R$', 'sum'),
                    TIPO_VEICULO=('TIPO_CAVALO', 'first'), CAPACIDADE_PESO_CARRETA=('CAPACIDADE_KG', 'first'),
                    CAPACIDADE_PESO_CAVALO=('CAPAC_CAVALO', 'first')
                ).reset_index()

                def get_capacidade_correta(row):
                    if row['TIPO_VEICULO'] == 'CAVALO': return row['CAPACIDADE_PESO_CARRETA']
                    return row['CAPACIDADE_PESO_CAVALO']
                resumo_viagens_base['CAPACIDADE_VIAGEM'] = resumo_viagens_base.apply(get_capacidade_correta, axis=1)

                def calcular_custo_ajustado(row):
                    custo_base = row['CUSTO_CTRB'] if row['PROPRIETARIO'] != 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_OS']
                    if any(dest in str(row['DESTINOS']) for dest in ['GYN', 'SPO']): return custo_base / 2
                    return custo_base
                resumo_viagens_base['CUSTO_AJUSTADO'] = resumo_viagens_base.apply(calcular_custo_ajustado, axis=1)
                
                resumo_viagens_base['NOME_ROTA'] = resumo_viagens_base['DESTINOS'].apply(obter_nome_rota_padronizado)

                # --- LÓGICA PRINCIPAL CORRIGIDA: Agrupa os dados para o gráfico ---
                df_grafico = resumo_viagens_base.groupby('NOME_ROTA').agg(
                    CTRB_FRETE_PERC=('FRETE_VIAGEM', lambda x: (resumo_viagens_base.loc[x.index, 'CUSTO_AJUSTADO'].sum() / x.sum() * 100) if x.sum() > 0 else 0),
                    OCUPACAO_KG_PERC=('PESO_VIAGEM', lambda x: (x.sum() / resumo_viagens_base.loc[x.index, 'CAPACIDADE_VIAGEM'].sum() * 100) if resumo_viagens_base.loc[x.index, 'CAPACIDADE_VIAGEM'].sum() > 0 else 0),
                    TOTAL_VIAGENS=('NOME_ROTA', 'size')
                ).reset_index()

                # As variáveis para o Altair agora são sempre as mesmas
                tooltip_label = 'NOME_ROTA'
                titulo_tooltip = 'Rota'
                eixo_y_ordenacao = 'NOME_ROTA'

                # Cria a nova coluna 'LABEL_EIXO_Y' substituindo 'ROTA ' pelo ícone
                coluna_fonte = 'NOME_ROTA' if 'NOME_ROTA' in df_grafico.columns else 'VIAGEM_LABEL'
                if coluna_fonte in df_grafico.columns:
                    df_grafico['LABEL_EIXO_Y'] = df_grafico[coluna_fonte].str.replace('ROTA ', 'ROTA 📍 ', regex=False)
                else:
                    df_grafico['LABEL_EIXO_Y'] = ''

                # --- 2. CRIAÇÃO DOS GRÁFICOS LADO A LADO ---
                col_graf1, col_graf2 = st.columns(2, gap="large")

                # ===============================================
                # 🔴 GRÁFICO 1 - Performance das Viagens
                # ===============================================
                with col_graf1:
                    opcoes_ranking_ctrb = {
                        'Performance das Viagens - CTRB/Frete (%)': 'CTRB_FRETE_PERC',
                        'Ordem Alfabética': eixo_y_ordenacao
                    }
                    selecao_ranking_ctrb = st.selectbox(
                        'Selecione a métrica para o ranking:',
                        options=list(opcoes_ranking_ctrb.keys()),
                        key='ranking_ctrb_selector'
                    )

                    # --- INÍCIO DA LÓGICA DE CORES ATUALIZADA ---
                    # 1. Pré-calcula a cor para cada rota com base nas faixas de desempenho
                    df_grafico['cor_barra'] = df_grafico['CTRB_FRETE_PERC'].apply(
                        # Se <= 25, é Verde (Bom). Se <= 45, é Laranja (Regular). Senão, é Vermelho (Péssimo).
                        lambda x: '#2E7D32' if x <= 25 else ('#FF8F00' if x <= 45 else '#C62828')
                    )
                    
                    # 2. Define a cor no Altair para usar a coluna pré-calculada
                    color_condition = alt.Color(
                        'cor_barra:N', # Usa a coluna 'cor_barra' como uma categoria de cor
                        scale=None     # Diz ao Altair para usar os valores hexadecimais diretamente
                    )
                    # --- FIM DA LÓGICA DE CORES ATUALIZADA ---

                    ordenacao_ctrb = alt.EncodingSortField(
                        field=opcoes_ranking_ctrb[selecao_ranking_ctrb],
                        op="min",
                        order='ascending' # 'ascending' para mostrar os melhores (menores %) no topo
                    )

                    st.markdown("##### Performance das Viagens")

                    barras_ctrb = alt.Chart(df_grafico).mark_bar(cornerRadius=5).encode(
                        x=alt.X('CTRB_FRETE_PERC:Q', title='CTRB/Frete (%)', axis=alt.Axis(format='.0f', titleFontSize=14, labelFontSize=12)),
                        y=alt.Y('LABEL_EIXO_Y:N', title=None, sort=ordenacao_ctrb, 
                                axis=alt.Axis(labelFontSize=14, labelLimit=0)
                            ),
                        color=color_condition, # Aplica a cor condicional
                        tooltip=[
                            alt.Tooltip(tooltip_label, title=titulo_tooltip),
                            alt.Tooltip('CTRB_FRETE_PERC', title='CTRB/Frete', format='.1f'),
                            alt.Tooltip('TOTAL_VIAGENS:Q', title='Total de Viagens') if 'TOTAL_VIAGENS' in df_grafico.columns else alt.Tooltip('MOTORISTA', title='Motorista')
                        ]
                    )

                    texto_ctrb = alt.Chart(df_grafico).mark_text(
                        align='left', baseline='middle', dx=5, fontSize=14, color='white'
                    ).transform_calculate(
                        label_text="format(datum.CTRB_FRETE_PERC, '.0f') + '%'"
                    ).encode(
                        y=alt.Y('LABEL_EIXO_Y:N', sort=ordenacao_ctrb),
                        x='CTRB_FRETE_PERC:Q',
                        text='label_text:N'
                    )

                    chart_final_ctrb = (barras_ctrb + texto_ctrb).properties(
                        height=alt.Step(40)
                    ).configure_view(stroke=None).configure_axis(grid=False)

                    st.altair_chart(chart_final_ctrb, use_container_width=True)

                    # --- ▼▼▼ NOVO BLOCO: LEGENDA DE DESEMPENHO ▼▼▼ ---
                    st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 15px; font-size: 14px;">
                        <b style="color: #E0E0E0;">CTRB/Frete (%):</b>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                            <span style="color: #E0E0E0;">Bom</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                            <span style="color: #E0E0E0;">Regular</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px; border: 1px solid #E0E0E0;"></div>
                            <span style="color: #E0E0E0;">Péssimo</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # --- ▲▲▲ FIM DO NOVO BLOCO ▲▲▲ ---

                # ===============================================
                # 🟢 GRÁFICO 2 - Eficiência Operacional
                # ===============================================
                with col_graf2:
                    opcoes_ranking_ocupacao = {
                        'Eficiência Operacional - Ocupação Média (KG)': 'OCUPACAO_KG_PERC',
                        'Ordem Alfabética': eixo_y_ordenacao
                    }
                    selecao_ranking_ocupacao = st.selectbox(
                        'Selecione a métrica para o ranking:',
                        options=list(opcoes_ranking_ocupacao.keys()),
                        key='ranking_ocupacao_selector'
                    )

                    ordenacao_ocupacao = alt.EncodingSortField(
                        field=opcoes_ranking_ocupacao[selecao_ranking_ocupacao],
                        op="min",
                        order='ascending' if selecao_ranking_ocupacao == 'Ordem Alfabética' else 'descending'
                    )

                    st.markdown("##### Eficiência Operacional")

                    barras_ocupacao = alt.Chart(df_grafico).mark_bar(cornerRadius=5).encode(
                        x=alt.X('OCUPACAO_KG_PERC:Q', title='Ocupação Média (KG)', 
                            axis=alt.Axis(format='.0f', titleFontSize=14, labelFontSize=12)),
                        
                        y=alt.Y('LABEL_EIXO_Y:N', title=None, sort=ordenacao_ocupacao,
                            axis=alt.Axis(labelFontSize=14, labelLimit=0)),
                        
                        color=alt.Color('OCUPACAO_KG_PERC:Q', scale=alt.Scale(scheme='greens'), legend=None),
                        
                        tooltip=[
                            alt.Tooltip(tooltip_label, title=titulo_tooltip),
                            alt.Tooltip('OCUPACAO_KG_PERC', title='Ocupação KG', format='.1f'),
                            alt.Tooltip('TOTAL_VIAGENS:Q', title='Total de Viagens') if 'TOTAL_VIAGENS' in df_grafico.columns else alt.Tooltip('PESO_VIAGEM', title='Peso Total', format=',.0f')
                        ]
                    )

                    texto_ocupacao = alt.Chart(df_grafico).mark_text(
                        align='left', baseline='middle', dx=5, fontSize=14, color='white'
                    ).transform_calculate(
                        label_text="format(datum.OCUPACAO_KG_PERC, '.0f') + '%'"
                    ).encode(
                        y=alt.Y('LABEL_EIXO_Y:N', sort=ordenacao_ocupacao),
                        x='OCUPACAO_KG_PERC:Q',
                        text='label_text:N'
                    )

                    chart_final_ocupacao = (barras_ocupacao + texto_ocupacao).properties(
                        height=alt.Step(40)
                    ).configure_view(stroke=None).configure_axis(grid=False)

                    st.altair_chart(chart_final_ocupacao, use_container_width=True)

                # ▼▼▼ INÍCIO DO NOVO BLOCO: TABELA DE RESUMO DAS VIAGENS NA ABA DE ROTAS ▼▼▼

                st.markdown('<hr style="border: 1px solid #333; margin: 30px 0;">', unsafe_allow_html=True)

                # --- Título dinâmico para a tabela ---
                if rota_selecionada_ocupacao == "(Todas as Rotas)":
                    st.subheader("📋 Resumo de Todas as Viagens no Período")
                else:
                    # Formata o nome da rota para ficar mais limpo no título
                    nome_rota_titulo = rota_selecionada_ocupacao.replace("ROTA ", "")
                    st.subheader(f"📋 Resumo das Viagens: {nome_rota_titulo}")

                # ▼▼▼ INÍCIO DO BLOCO DO MAPA DINÂMICO ▼▼▼
                # Condição 1: O filtro de período na sidebar deve ser "Dia Específico"
                # Condição 2: Uma rota específica (qualquer uma, exceto "Todas") deve ser selecionada nesta aba
                if periodo_tipo == "Dia Específico" and rota_selecionada_ocupacao != "(Todas as Rotas)":
                    
                    # Busca o nome da cidade correspondente à rota selecionada no dicionário que você adicionou
                    nome_cidade_destino = MAPA_ROTA_CIDADE.get(rota_selecionada_ocupacao)
                    
                    # Se encontrou uma cidade correspondente no dicionário...
                    if nome_cidade_destino:
                        st.markdown("#### 🗺️ Trajeto da Viagem")

                        # Busca as coordenadas da origem (fixa) e do destino (dinâmico)
                        coord_origem = get_coords("Campo Grande, MS")
                        coord_destino = get_coords(nome_cidade_destino)

                        # Se ambas as coordenadas foram encontradas com sucesso...
                        if coord_origem and coord_destino:
                            # Busca a rota entre os dois pontos
                            rota_desenhada = get_route(coord_origem, coord_destino)
                            
                            # Cria o mapa passando o nome da cidade de destino para o popup
                            mapa_viagem = criar_mapa_folium(coord_origem, coord_destino, nome_cidade_destino, rota_desenhada)
                            
                            # Exibe o mapa no Streamlit
                            if mapa_viagem:
                                st_folium(mapa_viagem, width=None, height=450, use_container_width=True)
                            else:
                                st.error("Não foi possível gerar o mapa da viagem.")
                        else:
                            st.warning(f"Coordenadas para '{nome_cidade_destino}' não encontradas. O mapa não pode ser exibido.")
                    else:
                        # Opcional: Informa ao usuário que a rota selecionada não tem um mapa configurado
                        st.info(f"A rota '{rota_selecionada_ocupacao}' não possui um trajeto de mapa pré-configurado.")
                # ▲▲▲ FIM DO BLOCO DO MAPA DINÂMICO ▲▲▲

                # O DataFrame 'df_para_ocupacao' já contém os dados filtrados pela rota selecionada
                df_viagens_tabela = df_para_ocupacao.copy()

                if not df_viagens_tabela.empty:
                    # 1. Agrupamento dos dados por viagem
                    if 'VIAGEM_ID' not in df_viagens_tabela.columns:
                        df_viagens_tabela['VIAGEM_ID'] = df_viagens_tabela.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup() + 1
                    
                    def obter_primeiro_valido(series):
                        for valor in series:
                            if pd.notna(valor) and str(valor).strip() != '' and str(valor).lower() != 'nan':
                                return valor
                        return None

                    coluna_peso_resumo_tab5 = obter_nome_coluna_peso_calculo(df_viagens_tabela) or 'PESO REAL (KG)'
                    resumo_viagens_tabela = df_viagens_tabela.groupby('VIAGEM_ID').agg(
                        EMISSÃO=('EMIS_MANIF', 'first'),
                        NUM_MANIF_LISTA=('NUM_MANIF', lambda x: f"{x.dropna().astype(str).iloc[0]} (+{len(x.dropna().unique()) - 1})" if len(x.dropna().unique()) > 1 else (x.dropna().astype(str).iloc[0] if not x.dropna().empty else "")),
                        SITUACAO=('SITUACAO', 'first'),
                        MOTORISTA=('MOTORISTA', 'first'),
                        PLACA_CAVALO=('PLACA_CAVALO', 'first'),
                        PLACA_CARRETA=('PLACA_CARRETA', obter_primeiro_valido),
                        CAPAC_CAVALO=('CAPAC_CAVALO', 'first'),
                        CAP_CARRETA=('CAPACIDADE_KG', 'first'), 
                        TIPO_VEICULO=('TIPO_CAVALO', 'first'),
                        DESTINOS=('DEST_MANIF', lambda x: ordenar_destinos_geograficamente(x.unique(), ROTAS_COMPOSTAS, ORDEM_DAS_ROTAS)),
                        PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                        CUSTO_OS_TOTAL=('OS-R$', 'max'),
                        CUSTO_CTRB_TOTAL=('CTRB-R$', 'max'),
                        FRETE_TOTAL=('FRETE-R$', 'sum'),
                        ICMS=('ICMS-R$', 'sum'),
                        PESO_KG=(coluna_peso_resumo_tab5, 'sum'),
                        M3=('M3', 'sum'),
                        VOLUMES=('VOLUMES', 'sum'),
                        VALOR_MERCADORIA=('MERCADORIA-R$', 'sum'),
                        ENTREGAS=('DEST_MANIF', 'nunique'),
                        QTDE_CTRC=('QTDE_CTRC', 'sum')
                    ).reset_index()

                    resumo_viagens_tabela.rename(columns={
                        'VIAGEM_ID': 'VIAGEM', 'EMISSÃO': 'EMIS_MANIF', 'TIPO_VEICULO': 'TIPO_CAVALO', 'DESTINOS': 'DEST_MANIF',
                        'PROPRIETARIO': 'PROPRIETARIO_CAVALO', 'CUSTO_OS_TOTAL': 'OS-R$', 'CUSTO_CTRB_TOTAL': 'CTRB-R$',
                        'FRETE_TOTAL': 'FRETE-R$', 'ICMS': 'ICMS-R$', 'PESO_KG': 'Peso Cálculo (KG)',
                        'VALOR_MERCADORIA': 'MERCADORIA-R$', 'NUM_MANIF_LISTA': 'NUM_MANIF'
                    }, inplace=True)

                    # ✅ Ajusta VIAGEM para começar em 1 (como coluna, não índice)
                    resumo_viagens_tabela['VIAGEM'] = range(1, len(resumo_viagens_tabela) + 1)


                    # 2. Funções de cálculo e formatação
                    def obter_capacidade_real_viagem(row):
                        capacidade_carreta = row.get('CAP_CARRETA', 0)
                        return capacidade_carreta if pd.notna(capacidade_carreta) and capacidade_carreta > 0 else row.get('CAPAC_CAVALO', 0)
                    
                    def obter_placa_veiculo_formatada(row):
                        placa_cavalo, placa_carreta = row.get('PLACA_CAVALO', 'N/A'), row.get('PLACA_CARRETA', 'N/A')
                        return f"{placa_cavalo} / {placa_carreta}" if pd.notna(placa_carreta) and placa_carreta != 'nan' and placa_carreta != placa_cavalo else placa_cavalo

                    resumo_viagens_tabela['Capacidade (KG)'] = resumo_viagens_tabela.apply(obter_capacidade_real_viagem, axis=1)
                    resumo_viagens_tabela['Veículo (Placa)'] = resumo_viagens_tabela.apply(obter_placa_veiculo_formatada, axis=1)

                    def calcular_custo_final(row):
                        custo_base = row['OS-R$'] if row['PROPRIETARIO_CAVALO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CTRB-R$']
                        return custo_base / 2 if any(dest in str(row.get('DEST_MANIF', '')).upper() for dest in ['GYN', 'SPO']) else custo_base

                    def calcular_distancia_viagem(row):
                        tipo_veiculo = obter_tipo_veiculo_base(row) or 'PADRAO'
                        valor_km = custo_km_por_tipo.get(tipo_veiculo, 0)
                        custo_viagem = row['Custo (CTRB/OS)']
                        return custo_viagem / valor_km if valor_km > 0 and custo_viagem > 0 else 0.0

                    resumo_viagens_tabela['Custo (CTRB/OS)'] = resumo_viagens_tabela.apply(calcular_custo_final, axis=1)
                    resumo_viagens_tabela['DISTANCIA'] = resumo_viagens_tabela.apply(calcular_distancia_viagem, axis=1)
                    resumo_viagens_tabela['CTRB/Frete (%)_valor'] = (resumo_viagens_tabela['Custo (CTRB/OS)'] / resumo_viagens_tabela['FRETE-R$'] * 100).fillna(0)
                    resumo_viagens_tabela['CTRB/Frete (%)'] = resumo_viagens_tabela['CTRB/Frete (%)_valor'].apply(lambda x: f"{x:.0f}%")

                    # 3. Formatação para exibição
                    resumo_viagens_tabela['EMIS_MANIF'] = pd.to_datetime(resumo_viagens_tabela['EMIS_MANIF']).dt.strftime('%d/%m/%Y')
                    for col_moeda in ['Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'MERCADORIA-R$']:
                        resumo_viagens_tabela[col_moeda] = resumo_viagens_tabela[col_moeda].astype(float).apply(formatar_moeda)
                    candidatos_peso_calculo_tabela = [
                        'Peso Cálculo (KG)', 'PESO CÁLCULO (KG)', 'PESO CALCULO (KG)',
                        'PESO CALCULADO (KG)', 'PESO_CALCULO_KG', 'PESO REAL (KG)'
                    ]
                    coluna_peso_calculo_tabela = next(
                        (col for col in candidatos_peso_calculo_tabela if col in resumo_viagens_tabela.columns),
                        None
                    )
                    if coluna_peso_calculo_tabela is None:
                        resumo_viagens_tabela['Peso Cálculo (KG)'] = 0.0
                    else:
                        resumo_viagens_tabela['Peso Cálculo (KG)'] = pd.to_numeric(
                            resumo_viagens_tabela[coluna_peso_calculo_tabela], errors='coerce'
                        ).fillna(0)
                    resumo_viagens_tabela['Peso Cálculo (KG)'] = resumo_viagens_tabela['Peso Cálculo (KG)'].apply(
                        lambda x: formatar_numero(x, 0) + ' kg'
                    )
                    resumo_viagens_tabela['M3'] = resumo_viagens_tabela['M3'].astype(float).apply(lambda x: formatar_numero(x, 3))
                    resumo_viagens_tabela['Capacidade (KG)'] = resumo_viagens_tabela['Capacidade (KG)'].astype(float).apply(lambda x: formatar_numero(x, 0) + ' kg')
                    resumo_viagens_tabela['DISTANCIA'] = resumo_viagens_tabela['DISTANCIA'].astype(float).apply(lambda x: f"{int(x):,} km".replace(",", "."))
                    resumo_viagens_tabela['VOLUMES'] = resumo_viagens_tabela['VOLUMES'].astype(int)


                    resumo_viagens_tabela.rename(columns={
                        'EMIS_MANIF': 'EMISSÃO', 'NUM_MANIF': 'Nº Manifesto', 'TIPO_CAVALO': 'TIPO', 'DEST_MANIF': 'DESTINOS',
                        'QTDE_CTRC': 'Qtd. CTRCs', 'SITUACAO': 'SITUAÇÃO'
                    }, inplace=True)

                    # 4. Definição da ordem final e exibição
                    ordem_final_tabela = [
                        'VIAGEM', 'EMISSÃO', 'Nº Manifesto', 'SITUAÇÃO', 'MOTORISTA', 'CTRB/Frete (%)', 'DESTINOS',
                        'DISTANCIA', 'ENTREGAS', 'TIPO', 'Veículo (Placa)', 'Peso Cálculo (KG)', 'Capacidade (KG)',
                        'M3', 'Custo (CTRB/OS)', 'FRETE-R$', 'ICMS-R$', 'VOLUMES', 'Qtd. CTRCs', 'MERCADORIA-R$'
                    ]
                    colunas_para_exibir_tabela = [col for col in ordem_final_tabela if col in resumo_viagens_tabela.columns]
                    df_para_exibir_tabela = resumo_viagens_tabela[colunas_para_exibir_tabela].sort_values(by='VIAGEM', ascending=True)

                    def colorir_celula_ctrb(valor_texto):
                        try:
                            v = float(valor_texto.strip('%'))
                            if 0 <= v <= 25: return 'background-color: #2E7D32; color: white;'
                            elif 26 <= v <= 45: return 'background-color: #FF8F00; color: white;'
                            elif v >= 46: return 'background-color: #C62828; color: white;'
                        except (ValueError, TypeError): pass
                        return ''

                    styled_df_tabela = df_para_exibir_tabela.style.map(colorir_celula_ctrb, subset=['CTRB/Frete (%)'])
                    
                    st.dataframe(styled_df_tabela, use_container_width=True, hide_index=True)

                    # 5. Legenda e botão de download
                    st.markdown("""
                    <div style="display: flex; align-items: center; justify-content: flex-start; gap: 25px; font-family: sans-serif; margin-top: 20px; font-size: 14px;">
                        <b style="color: #E0E0E0;">Legenda de Desempenho:</b>
                        <div style="display: flex; align-items: center; gap: 10px;"><div style="width: 16px; height: 16px; background-color: #2E7D32; border-radius: 4px;"></div><span style="color: #E0E0E0;">Bom</span></div>
                        <div style="display: flex; align-items: center; gap: 10px;"><div style="width: 16px; height: 16px; background-color: #FF8F00; border-radius: 4px;"></div><span style="color: #E0E0E0;">Regular</span></div>
                        <div style="display: flex; align-items: center; gap: 10px;"><div style="width: 16px; height: 16px; background-color: #C62828; border-radius: 4px;"></div><span style="color: #E0E0E0;">Péssimo</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("")

                    try:
                        excel_bytes_tabela = to_excel(df_para_exibir_tabela)
                        st.download_button(
                            label="📥 Download Resumo da Rota (Excel)",
                            data=excel_bytes_tabela,
                            file_name=f"resumo_rota_{rota_selecionada_ocupacao.replace(' / ', '_')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_resumo_rota_tab5"
                        )
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar o arquivo Excel para o resumo da rota: {e}")

            # --- ▲▲▲ FIM DO BLOCO DE GRÁFICOS DE BARRAS ---

        else:
            st.info(f"Não há viagens do tipo '{tipo_viagem_ocupacao_sel}' para analisar no período selecionado.")

# ==================================================================
# ABA 6: ANÁLISE TEMPORAL DE ROTAS
# ==================================================================
with tab6:
    # Título estilizado para a nova aba
    st.markdown("""
        <div class="title-block-temporal">
            <i class="fa-solid fa-chart-simple"></i>
            <h2>Painel de Performance por Rota</h2>
        </div>
    """, unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
    else:
        # --- 1. PREPARAÇÃO AVANÇADA DOS DADOS ---
        df_temporal = df_filtrado.copy()
        
        # Garante que a data de emissão e o dia da semana existem
        df_temporal['EMISSAO_DATE'] = pd.to_datetime(df_temporal['EMIS_MANIF']).dt.date
        df_temporal['DIA_SEMANA_NUM'] = pd.to_datetime(df_temporal['EMIS_MANIF']).dt.dayofweek
        dias_semana_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        df_temporal['DIA_SEMANA'] = df_temporal['DIA_SEMANA_NUM'].map(dias_semana_map)

        # Identifica cada viagem única
        df_temporal['VIAGEM_ID'] = df_temporal.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()

        # Agrega os dados por VIAGEM para cálculos corretos
        resumo_viagens_temporal = df_temporal.groupby('VIAGEM_ID').agg(
            FRETE_VIAGEM=('FRETE-R$', 'sum'),
            CUSTO_OS=('OS-R$', 'max'),
            CUSTO_CTRB=('CTRB-R$', 'max'),
            ICMS_VIAGEM=('ICMS-R$', 'sum'),
            PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
            DESTINOS=('DEST_MANIF', 'unique'),
            PESO_VIAGEM=('Peso Cálculo (KG)', 'sum'),
            TIPO_VEICULO=('TIPO_CAVALO', 'first'),
            CAPACIDADE_CARRETA=('CAPACIDADE_KG', 'first'),
            CAPACIDADE_CAVALO=('CAPAC_CAVALO', 'first'),
            DIA_SEMANA=('DIA_SEMANA', 'first'),
            DIA_SEMANA_NUM=('DIA_SEMANA_NUM', 'first')
        ).reset_index()

        # Calcula métricas de performance por VIAGEM
        def get_capacidade_viagem(row):
            return row['CAPACIDADE_CARRETA'] if row['TIPO_VEICULO'] == 'CAVALO' else row['CAPACIDADE_CAVALO']
        
        def calcular_custo_viagem(row):
            custo = row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']
            return custo / 2 if any(d in str(row['DESTINOS']) for d in ['GYN', 'SPO']) else custo

        resumo_viagens_temporal['CAPACIDADE_VIAGEM'] = resumo_viagens_temporal.apply(get_capacidade_viagem, axis=1)
        resumo_viagens_temporal['CUSTO_VIAGEM'] = resumo_viagens_temporal.apply(calcular_custo_viagem, axis=1)
        resumo_viagens_temporal['LUCRO_VIAGEM'] = resumo_viagens_temporal['FRETE_VIAGEM'] - (resumo_viagens_temporal['CUSTO_VIAGEM'] + resumo_viagens_temporal['ICMS_VIAGEM'])
        resumo_viagens_temporal['OCUPACAO_PERC'] = (resumo_viagens_temporal['PESO_VIAGEM'] / resumo_viagens_temporal['CAPACIDADE_VIAGEM'] * 100).fillna(0)
        resumo_viagens_temporal['CUSTO_FRETE_PERC'] = (resumo_viagens_temporal['CUSTO_VIAGEM'] / resumo_viagens_temporal['FRETE_VIAGEM'] * 100).fillna(0)
        resumo_viagens_temporal['NOME_ROTA'] = resumo_viagens_temporal['DESTINOS'].apply(obter_nome_rota_padronizado)

        # --- 2. CRIAÇÃO DAS ABAS INTERNAS (IDEIA 1) ---
        aba_totais, aba_medias, aba_ranking = st.tabs(["📈 Totais por Dia", "📊 Médias & Performance", "🏁 Ranking de Rotas"])

        # --- ABA 1: TOTAIS POR DIA ---
        with aba_totais:
            st.markdown("#### Análise de Volume Total por Dia da Semana")
            
            # Agrupa os dados por dia da semana para os totais
            totais_dia_semana = resumo_viagens_temporal.groupby(['DIA_SEMANA_NUM', 'DIA_SEMANA']).agg(
                TOTAL_VIAGENS=('VIAGEM_ID', 'nunique'),
                FRETE_TOTAL=('FRETE_VIAGEM', 'sum'),
                CUSTO_TOTAL=('CUSTO_VIAGEM', 'sum'),
                LUCRO_TOTAL=('LUCRO_VIAGEM', 'sum')
            ).reset_index().sort_values('DIA_SEMANA_NUM')

            # Gráfico de totais
            base_totais = alt.Chart(totais_dia_semana).encode(x=alt.X('DIA_SEMANA:N', sort=None, title="Dia da Semana"))

            barras_frete = base_totais.mark_bar(opacity=0.8, color="#22c55e").encode(
                y=alt.Y('FRETE_TOTAL:Q', title='Valor Total (R$)'),
                tooltip=[alt.Tooltip('DIA_SEMANA', title='Dia'), alt.Tooltip('FRETE_TOTAL', title='Frete Total', format='$,.2f')]
            )
            
            linha_lucro = base_totais.mark_line(point=True, color="#3b82f6", strokeWidth=3).encode(
                y=alt.Y('LUCRO_TOTAL:Q', title='Lucro Total (R$)'),
                tooltip=[alt.Tooltip('LUCRO_TOTAL', title='Lucro Total', format='$,.2f')]
            )

            chart_totais = alt.layer(barras_frete, linha_lucro).resolve_scale(y='independent').properties(
                title="Frete Total (Barras) vs. Lucro Total (Linha) por Dia da Semana",
                height=400
            ).configure_axis(labelFontSize=12, titleFontSize=14).configure_title(fontSize=16)
            
            st.altair_chart(chart_totais, use_container_width=True)

        # --- ABA 2: MÉDIAS & PERFORMANCE (COM GRÁFICO HÍBRIDO - IDEIA 2 e 4) ---
        with aba_medias:
            st.markdown("#### Performance Média das Rotas")
            
            metrica_selecionada = st.radio(
                "Selecione a métrica principal para análise:",
                options=['Custo/Frete (%)', 'Ocupação Média (KG)', 'Lucro Médio (R$)'],
                horizontal=True,
                key="metrica_media_selector"
            )

            medias_por_rota = resumo_viagens_temporal.groupby('NOME_ROTA').agg(
                CUSTO_FRETE_MEDIO=('CUSTO_FRETE_PERC', 'mean'),
                OCUPACAO_MEDIA=('OCUPACAO_PERC', 'mean'),
                LUCRO_MEDIO=('LUCRO_VIAGEM', 'mean'),
                TOTAL_VIAGENS=('VIAGEM_ID', 'nunique')
            ).reset_index()

            if metrica_selecionada == 'Custo/Frete (%)':
                col_barra, col_linha, titulo_barra = 'CUSTO_FRETE_MEDIO', 'OCUPACAO_MEDIA', 'Custo/Frete Médio (%)'
                color_scale = alt.Scale(scheme='redyellowgreen', reverse=True)
            elif metrica_selecionada == 'Ocupação Média (KG)':
                col_barra, col_linha, titulo_barra = 'OCUPACAO_MEDIA', 'CUSTO_FRETE_MEDIO', 'Ocupação Média (%)'
                color_scale = alt.Scale(scheme='redyellowgreen', reverse=False)
            else: # Lucro Médio
                col_barra, col_linha, titulo_barra = 'LUCRO_MEDIO', 'OCUPACAO_MEDIA', 'Lucro Médio por Viagem (R$)'
                color_scale = alt.Scale(scheme='redyellowgreen', reverse=False)

            # =============================================================
            # ▼▼▼ LINHA CORRIGIDA/ADICIONADA AQUI ▼▼▼
            # Define o gráfico base ANTES de usá-lo
            base_medias = alt.Chart(medias_por_rota).encode(
                x=alt.X('NOME_ROTA:N', sort='-y', title=None, axis=alt.Axis(labelAngle=-45))
            )
            # ▲▲▲ FIM DA CORREÇÃO ▲▲▲
            # =============================================================

            # Barras verticais com gradiente de cor
            barras_medias = base_medias.mark_bar().encode(
                y=alt.Y(f'{col_barra}:Q', title=titulo_barra),
                color=alt.Color(f'{col_barra}:Q',
                                scale=color_scale,
                                legend=None),
                tooltip=[
                    alt.Tooltip('NOME_ROTA', title='Rota'),
                    alt.Tooltip('CUSTO_FRETE_MEDIO', title='Custo/Frete Médio', format='.1f'),
                    alt.Tooltip('OCUPACAO_MEDIA', title='Ocupação Média', format='.1f'),
                    alt.Tooltip('LUCRO_MEDIO', title='Lucro Médio', format='$,.2f'),
                    alt.Tooltip('TOTAL_VIAGENS', title='Nº de Viagens')
                ]
            )

            # Linha sobreposta
            linha_medias = base_medias.mark_line(point=alt.OverlayMarkDef(color="#FFFFFF", size=60), color="#FFFFFF", strokeWidth=2).encode(
                y=alt.Y(f'{col_linha}:Q', title=f"{col_linha.replace('_', ' ').title()} (%)")
            )
            
            chart_hibrido = alt.layer(barras_medias, linha_medias).resolve_scale(y='independent').properties(
                title=f"Análise Híbrida: {titulo_barra} (Barras) vs. {col_linha.replace('_', ' ').title()} (Linha)",
                height=450
            )
            
            st.altair_chart(chart_hibrido, use_container_width=True)

            # ... (resto do código com o scatter plot) ...


            # --- SEÇÃO DE CORRELAÇÃO (IDEIA 6) ---
            st.markdown("---")
            st.markdown("#### Análise de Correlação: Eficiência vs. Rentabilidade")
            
            scatter_plot = alt.Chart(medias_por_rota).mark_circle(size=100, opacity=0.8).encode(
                x=alt.X('OCUPACAO_MEDIA:Q', title='Eficiência de Ocupação (%)', scale=alt.Scale(zero=False)),
                y=alt.Y('CUSTO_FRETE_MEDIO:Q', title='Performance de Custo/Frete (%)', scale=alt.Scale(zero=False)),
                color=alt.Color('LUCRO_MEDIO:Q', scale=alt.Scale(scheme='viridis'), title='Lucro Médio (R$)'),
                size=alt.Size('TOTAL_VIAGENS:Q', title='Nº de Viagens'),
                tooltip=[
                    alt.Tooltip('NOME_ROTA', title='Rota'),
                    alt.Tooltip('OCUPACAO_MEDIA', title='Ocupação Média', format='.1f'),
                    alt.Tooltip('CUSTO_FRETE_MEDIO', title='Custo/Frete Médio', format='.1f'),
                    alt.Tooltip('LUCRO_MEDIO', title='Lucro Médio', format='$,.2f')
                ]
            ).properties(
                title="Correlação entre Ocupação, Custo/Frete e Lucro",
                height=400
            ).interactive()

            st.altair_chart(scatter_plot, use_container_width=True)

        # --- ABA 3: RANKING & DESTAQUES (CORREÇÃO FINAL E DEFINITIVA) ---
        with aba_ranking:
            st.markdown("#### Destaques de Performance das Rotas no Período")
        
            # Garante que há dados para processar
            if not df_filtrado.empty:
                # 1. REPROCESSA os dados a partir do df_filtrado (original da sidebar)
                #    para garantir que TODAS as viagens (completas e extras) sejam incluídas.
                df_ranking_base = df_filtrado.copy()
                df_ranking_base['VIAGEM_ID'] = df_ranking_base.groupby(['MOTORISTA', 'PLACA_CAVALO', 'DIA_EMISSAO_STR']).ngroup()
        
                # 2. Agrega por viagem para obter os valores corretos
                resumo_viagens_ranking = df_ranking_base.groupby('VIAGEM_ID').agg(
                    FRETE_VIAGEM=('FRETE-R$', 'sum'),
                    CUSTO_OS=('OS-R$', 'max'), CUSTO_CTRB=('CTRB-R$', 'max'),
                    ICMS_VIAGEM=('ICMS-R$', 'sum'), PROPRIETARIO=('PROPRIETARIO_CAVALO', 'first'),
                    DESTINOS=('DEST_MANIF', 'unique'), PESO_VIAGEM=('Peso Cálculo (KG)', 'sum'),
                    TIPO_VEICULO=('TIPO_CAVALO', 'first'),
                    # Captura as capacidades de forma separada para a lógica correta
                    CAPACIDADE_CARRETA=('CAPACIDADE_KG', 'first'),
                    CAPACIDADE_CAVALO=('CAPAC_CAVALO', 'first')
                ).reset_index()
        
                # 3. Aplica as mesmas funções de cálculo robustas usadas na Aba 5
                def get_capacidade_correta_viagem(row):
                    # Se for um CAVALO, a capacidade é a da CARRETA. Senão, é a do próprio veículo (TRUCK/TOCO).
                    if row['TIPO_VEICULO'] == 'CAVALO':
                        return row['CAPACIDADE_CARRETA']
                    return row['CAPACIDADE_CAVALO']
        
                def calcular_custo_correto_viagem(row):
                    custo = row['CUSTO_OS'] if row['PROPRIETARIO'] == 'MARCELO H LEMOS BERALDO E CIA LTDA ME' else row['CUSTO_CTRB']
                    # Regra de divisão para rotas longas
                    return custo / 2 if any(d in str(row['DESTINOS']) for d in ['GYN', 'SPO']) else custo
        
                resumo_viagens_ranking['CAPACIDADE_VIAGEM'] = resumo_viagens_ranking.apply(get_capacidade_correta_viagem, axis=1)
                resumo_viagens_ranking['CUSTO_VIAGEM'] = resumo_viagens_ranking.apply(calcular_custo_correto_viagem, axis=1)
                resumo_viagens_ranking['LUCRO_VIAGEM'] = resumo_viagens_ranking['FRETE_VIAGEM'] - (resumo_viagens_ranking['CUSTO_VIAGEM'] + resumo_viagens_ranking['ICMS_VIAGEM'])
                resumo_viagens_ranking['CUSTO_FRETE_PERC'] = (resumo_viagens_ranking['CUSTO_VIAGEM'] / resumo_viagens_ranking['FRETE_VIAGEM'] * 100).fillna(0)
                resumo_viagens_ranking['NOME_ROTA'] = resumo_viagens_ranking['DESTINOS'].apply(obter_nome_rota_padronizado)
        
                # 4. Agrupa por ROTA para obter os valores finais para os destaques e ranking
                dados_agregados_rota = resumo_viagens_ranking.groupby('NOME_ROTA').agg(
                    CUSTO_FRETE_MEDIO=('CUSTO_FRETE_PERC', 'mean'),
                    LUCRO_MEDIO=('LUCRO_VIAGEM', 'mean'),
                    TOTAL_VIAGENS=('VIAGEM_ID', 'nunique'),
                    # A OCUPAÇÃO CORRETA: SOMA DOS PESOS / SOMA DAS CAPACIDADES
                    PESO_TOTAL_ROTA=('PESO_VIAGEM', 'sum'),
                    CAPACIDADE_TOTAL_ROTA=('CAPACIDADE_VIAGEM', 'sum')
                ).reset_index()
        
                # Calcula a ocupação média da forma correta
                dados_agregados_rota['OCUPACAO_MEDIA'] = (
                    dados_agregados_rota['PESO_TOTAL_ROTA'] / dados_agregados_rota['CAPACIDADE_TOTAL_ROTA'] * 100
                ).fillna(0)
        
                # O restante do código para exibir os cards e a tabela permanece o mesmo
                if not dados_agregados_rota.empty:
                    # ... (código dos 4 cards de destaque, sem alterações) ...
                    rota_destaque = dados_agregados_rota.loc[dados_agregados_rota['CUSTO_FRETE_MEDIO'].idxmin()]
                    rota_baixa_eficiencia = dados_agregados_rota.loc[dados_agregados_rota['OCUPACAO_MEDIA'].idxmin()]
                    rota_mais_rentavel = dados_agregados_rota.loc[dados_agregados_rota['LUCRO_MEDIO'].idxmax()]
                    ponto_atencao = dados_agregados_rota[
                        (dados_agregados_rota['CUSTO_FRETE_MEDIO'] > dados_agregados_rota['CUSTO_FRETE_MEDIO'].quantile(0.75)) &
                        (dados_agregados_rota['OCUPACAO_MEDIA'] < dados_agregados_rota['OCUPACAO_MEDIA'].quantile(0.25))
                    ]
        
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                            <div class='kpi-container' style='text-align: left; border-left: 5px solid #22c55e;'>
                                <div class='kpi-title'>🥇 Rota Destaque (Custo/Frete %)</div>
                                <div class='kpi-value' style='color: #22c55e;'>{rota_destaque['NOME_ROTA']}</div>
                                <p style='color: #d1d5db; font-size: 1rem;'>{rota_destaque['CUSTO_FRETE_MEDIO']:.0f}%</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                            <div class='kpi-container' style='text-align: left; border-left: 5px solid #f59e0b;'>
                                <div class='kpi-title'>🐢 Rota com Menor Eficiência</div>
                                <div class='kpi-value' style='color: #f59e0b;'>{rota_baixa_eficiencia['NOME_ROTA']}</div>
                                <p style='color: #d1d5db; font-size: 1rem;'>{rota_baixa_eficiencia['OCUPACAO_MEDIA']:.0f}% Ocupação</p>
                            </div>
                        """, unsafe_allow_html=True)
        
                    with col3:
                        st.markdown(f"""    
                            <div class='kpi-container' style='text-align: left; border-left: 5px solid #3b82f6;'>
                                <div class='kpi-title'>💰 Rota Mais Rentável</div>
                                <div class='kpi-value' style='color: #3b82f6;'>{rota_mais_rentavel['NOME_ROTA']}</div>
                                <p style='color: #d1d5db; font-size: 1rem;'>R$ {rota_mais_rentavel['LUCRO_MEDIO']:,.2f} / viagem</p>
                            </div>
                        """, unsafe_allow_html=True)
        
                    with col4:
                        nome_atencao = ponto_atencao['NOME_ROTA'].iloc[0] if not ponto_atencao.empty else "N/A"
                        st.markdown(f"""
                            <div class='kpi-container' style='text-align: left; border-left: 5px solid #ef4444;'>
                                <div class='kpi-title'>⚙️ Ponto de Atenção</div>
                                <div class='kpi-value' style='color: #ef4444;'>{nome_atencao}</div>
                                <p style='color: #d1d5db; font-size: 1rem;'>Alto Custo & Baixa Ocupação</p>
                            </div>
                        """, unsafe_allow_html=True)
        
                st.markdown("---")
                st.markdown("#### Ranking Completo das Rotas")
        
                df_ranking = dados_agregados_rota.sort_values('LUCRO_MEDIO', ascending=False).reset_index(drop=True)
                df_ranking.index += 1
        
                df_ranking['CUSTO_FRETE_MEDIO'] = df_ranking['CUSTO_FRETE_MEDIO'].apply(lambda x: f"{x:.1f}%")
                df_ranking['OCUPACAO_MEDIA'] = df_ranking['OCUPACAO_MEDIA'].apply(lambda x: f"{x:.1f}%")
                df_ranking['LUCRO_MEDIO'] = df_ranking['LUCRO_MEDIO'].apply(lambda x: f"R$ {x:,.2f}")
                df_ranking.rename(columns={'TOTAL_VIAGENS': 'Nº de Viagens'}, inplace=True)
        
                st.dataframe(df_ranking[['NOME_ROTA', 'LUCRO_MEDIO', 'CUSTO_FRETE_MEDIO', 'OCUPACAO_MEDIA', 'Nº de Viagens']], use_container_width=True)
        
            else:
                st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados.")
