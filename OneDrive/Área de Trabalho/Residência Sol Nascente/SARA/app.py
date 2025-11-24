import streamlit as st
import pandas as pd
import folium
from folium.features import CustomIcon
from streamlit_folium import st_folium

from sidebar import sidebar_filters
from db import fetch_pontos

CATEGORY_LABELS = {
    1: "Acúmulo de Pneu",
    2: "Descarte de Eletroeletrônicos",
    3: "Descartes de Móveis e Colchões",
    4: "Descarte de Resíduos Hospitalares",
    5: "Pontos Viciados de Resíduos Comum",
    6: "Descarte de Entulhos de Obras",
}

st.set_page_config(page_title="SARA - Mapa", layout="wide")
st.title("SARA - Sistema Analítico de Resíduos e Ambiente")

# --- Sidebar: retorna lista de pins selecionados ---
selected_pins = sidebar_filters(CATEGORY_LABELS)

# --- Carrega dados do banco ---
df = fetch_pontos(selected_pins)

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

    popup_html = f"""
    <b>{CATEGORY_LABELS.get(pin_num, f"Pin {pin_num}")}</b><br>
    Nome: {row['nome']}<br>
    PNRS: {row['pnrs'] if row['pnrs'] else '-'}
    """

    icon = CustomIcon(
        icon_image=icon_path,
        icon_size=(32, 32),
        icon_anchor=(16, 32)
    )

    folium.Marker(
        location=[row["lat"], row["long"]],
        icon=icon,
        popup=popup_html
    ).add_to(m)

# --- Renderiza o mapa no Streamlit ---
st_folium(m, width="100%", height=600)
