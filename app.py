import base64
import os

import streamlit as st
import pandas as pd
import folium
from folium.features import CustomIcon
from streamlit_folium import st_folium

from sidebar import sidebar_filters
from db import fetch_pontos
from message import show_intro_message  # <-- NOVO IMPORT

CATEGORY_LABELS = {
    1: "Acúmulo de Pneu",
    2: "Descarte de Eletroeletrônicos",
    3: "Descartes de Móveis e Colchões",
    4: "Descarte de Resíduos Hospitalares",
    5: "Pontos Viciados de Resíduos Comum",
    6: "Descarte de Entulhos de Obras",
}


def set_background(image_path: str):
    """Define uma imagem de fundo a partir de um arquivo local."""
    if not os.path.exists(image_path):
        st.warning(f"Imagem de fundo não encontrada: {image_path}")
        return

    with open(image_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
    }}
    .block-container {{
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 1rem;
        padding: 1.5rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_pontos_cached(selected_pins_tuple):
    """
    Carrega pontos do banco com cache por combinação de pins selecionados.

    selected_pins_tuple: tuple(...) com os pins (1..6)
    """
    # converte de volta pra lista porque o fetch_pontos espera lista
    return fetch_pontos(list(selected_pins_tuple))


st.set_page_config(page_title="SARA - Mapa", layout="wide")
set_background("fundos/fundo_mapa.png")

# --- Mensagem de apresentação (slides) ---
show_intro_message()

st.title("SARA - Sistema Analítico de Resíduos e Ambiente (Sol Nascente)")

# --- Sidebar: retorna lista de pins selecionados ---
selected_pins = sidebar_filters(CATEGORY_LABELS)

# --- Carrega dados do banco (agora cacheado por filtro) ---
df = load_pontos_cached(tuple(sorted(selected_pins)))  # sort pra ordem não quebrar o cache

if df.empty:
    st.warning("Nenhum ponto cadastrado ainda ou filtros muito restritivos.")
    st.stop()

# --- Centro do mapa (média das coordenadas) ---
center_lat = df["lat"].mean()
center_long = df["long"].mean()

m = folium.Map(location=[center_lat, center_long], zoom_start=13, tiles="OpenStreetMap")

for _, row in df.iterrows():
    pin_num = int(row["pin"])
    icon_path = f"img/pin_{pin_num}.png"

    categoria = CATEGORY_LABELS.get(pin_num, f"Pin {pin_num}")
    pnrs_val = row["pnrs"] if row["pnrs"] else "-"

    popup_html = f"""
    <div style="font-size: 13px; font-family: Arial, sans-serif;">
      <table style="border-collapse: collapse;">
        <tr>
          <td style="font-weight:600; padding-right:6px;">Categoria:</td>
          <td>{categoria}</td>
        </tr>
        <tr>
          <td style="font-weight:600; padding-right:6px;">Nome do ponto:</td>
          <td>{row['nome']}</td>
        </tr>
        <tr>
          <td style="font-weight:600; padding-right:6px;">Classificação PNRS:</td>
          <td>{pnrs_val}</td>
        </tr>
        <tr>
          <td style="font-weight:600; padding-right:6px;">Data registro:</td>
          <td>{row['data_registro']}</td>
        </tr>
      </table>
    </div>
    """

    icon = CustomIcon(
        icon_image=icon_path,
        icon_size=(42, 42),
        icon_anchor=(16, 32),
    )

    folium.Marker(
        location=[row["lat"], row["long"]],
        icon=icon,
        popup=popup_html,
    ).add_to(m)

# --- Renderiza o mapa no Streamlit ---
st_folium(m, width="100%", height=750)
