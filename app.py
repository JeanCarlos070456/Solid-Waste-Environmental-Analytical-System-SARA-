import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.features import CustomIcon
from streamlit_folium import st_folium

from sidebar import sidebar_filters
from db import fetch_pontos


# -----------------------------
# Config / Constantes
# -----------------------------
CATEGORY_LABELS = {
    1: "Acúmulo de Pneu",
    2: "Descarte de Eletroeletrônicos",
    3: "Descartes de Móveis e Colchões",
    4: "Descarte de Resíduos Hospitalares",
    5: "Pontos Viciados de Resíduos Comum",
    6: "Descarte de Entulhos de Obras",
}
ALL_PINS = tuple(CATEGORY_LABELS.keys())

BASE_DIR = Path(__file__).resolve().parent


def _resolve(rel_path: str) -> Path:
    return (BASE_DIR / rel_path).resolve()


def _to_data_url_png(path: Path) -> str | None:
    if not path.exists():
        return None
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


@st.cache_data(show_spinner=False)
def load_pin_icons_data_urls() -> dict[int, str]:
    """
    Carrega os ícones img/pin_1.png ... img/pin_6.png como data-url base64.
    Isso evita dor de cabeça com caminhos quando renderiza em HTML.
    """
    out = {}
    for pin in ALL_PINS:
        p = _resolve(f"img/pin_{pin}.png")
        data_url = _to_data_url_png(p)
        if data_url:
            out[pin] = data_url
    return out


def set_background(image_rel_path: str):
    image_path = _resolve(image_rel_path)
    if not image_path.exists():
        st.warning(f"Imagem de fundo não encontrada: {image_path}")
        return

    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
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

    /* Faixa fixa/sticky acima do mapa */
    .sara-intro-sticky {{
        position: sticky;
        top: 0.75rem;
        z-index: 50;
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(0,0,0,0.10);
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.10);
        padding: 14px 16px;
        margin: 6px 0 14px 0;
        backdrop-filter: blur(6px);
    }}
    .sara-intro-title {{
        font-weight: 900;
        font-size: 16px;
        margin: 0 0 8px 0;
    }}
    .sara-intro-text {{
        font-size: 13.5px;
        line-height: 1.35;
        margin: 0;
        opacity: 0.95;
    }}
    .sara-intro-note {{
        font-size: 12px;
        opacity: 0.75;
        margin-top: 10px;
    }}

    /* Grade dos mini-cards */
    .sara-pin-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
    }}
    @media (max-width: 900px) {{
        .sara-pin-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}
    .sara-pin-card {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 10px;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.08);
        background: rgba(255,255,255,0.9);
    }}
    .sara-pin-icon {{
        width: 36px;
        height: 36px;
        flex: 0 0 36px;
        border-radius: 10px;
        object-fit: contain;
        background: rgba(0,0,0,0.03);
        padding: 4px;
    }}
    .sara-pin-text {{
        display: flex;
        flex-direction: column;
        gap: 2px;
        min-width: 0;
    }}
    .sara-pin-title {{
        font-weight: 900;
        font-size: 13px;
        line-height: 1.05;
    }}
    .sara-pin-desc {{
        font-size: 12px;
        opacity: 0.82;
        line-height: 1.15;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_pontos_cached(selected_pins_tuple: tuple[int, ...]):
    pins = list(selected_pins_tuple) if selected_pins_tuple else list(ALL_PINS)
    return fetch_pontos(pins)


def scroll_to_anchor(anchor_id: str, y_offset_px: int = 80):
    """
    Rola a página até um elemento HTML com id=anchor_id.
    """
    js = f"""
    <script>
      (function() {{
        const el = parent.document.getElementById("{anchor_id}");
        if (!el) return;
        el.scrollIntoView({{ behavior: "smooth", block: "start" }});
        setTimeout(() => {{
          try {{
            parent.window.scrollBy(0, -{int(y_offset_px)});
          }} catch (e) {{}}
        }}, 250);
      }})();
    </script>
    """
    components.html(js, height=0)


def render_intro_sticky(pin_icons_data: dict[int, str]):
    """
    Renderiza a faixa sticky com instruções + mini cards dos 6 pins.
    """
    cards = []
    for pin in ALL_PINS:
        label = CATEGORY_LABELS.get(pin, f"Pin {pin}")
        icon_src = pin_icons_data.get(pin)
        img_html = (
            f'<img class="sara-pin-icon" src="{icon_src}" alt="Pin {pin}"/>'
            if icon_src
            else '<div class="sara-pin-icon"></div>'
        )

        cards.append(f"""
        <div class="sara-pin-card">
          {img_html}
          <div class="sara-pin-text">
            <div class="sara-pin-title">Pin {pin}</div>
            <div class="sara-pin-desc" title="{label}">{label}</div>
          </div>
        </div>
        """)

    grid_html = "\n".join(cards)

    st.markdown(
        f"""
        <div class="sara-intro-sticky">
          <div class="sara-intro-title">Guia rápido do SARA</div>

          <p class="sara-intro-text">
            Este mapa mostra pontos de resíduos no Sol Nascente classificados por categoria .
            Use os filtros na lateral para ligar/desligar categorias. Clique nos Alfinetes para ver detalhes do registro.
          </p>

          <div class="sara-pin-grid">
            {grid_html}
          </div>

          <div class="sara-intro-note">
            Quando estiver pronto, clique em <b>Prosseguir</b> para focar no mapa.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# App
# -----------------------------
st.set_page_config(page_title="SARA - Mapa", layout="wide")
set_background("fundos/fundo_mapa.png")

st.title("SARA - Sistema Analítico de Resíduos e Ambiente (Sol Nascente)")

# Estado da intro fixa
if "intro_dismissed" not in st.session_state:
    st.session_state["intro_dismissed"] = False
if "scrolled_to_map" not in st.session_state:
    st.session_state["scrolled_to_map"] = False

# Sidebar: filtros
selected_pins = sidebar_filters(CATEGORY_LABELS)
selected_pins = tuple(sorted(selected_pins)) if selected_pins else tuple()

df = load_pontos_cached(selected_pins)
if df is None or df.empty:
    st.warning("Nenhum ponto cadastrado ainda ou filtros muito restritivos.")
    st.stop()

# Faixa sticky com mini-cards (até clicar em Prosseguir)
if not st.session_state["intro_dismissed"]:
    pin_icons_data = load_pin_icons_data_urls()
    render_intro_sticky(pin_icons_data)

    col_a, col_b = st.columns([1, 6])
    with col_a:
        if st.button("Prosseguir", type="primary"):
            st.session_state["intro_dismissed"] = True
            st.session_state["scrolled_to_map"] = False  # garante scroll na próxima render
            st.rerun()
    with col_b:
        st.empty()

# Âncora antes do mapa (para rolagem)
st.markdown('<div id="mapa-anchor"></div>', unsafe_allow_html=True)

# Se acabou de clicar em Prosseguir, rola até o mapa (1x)
if st.session_state["intro_dismissed"] and not st.session_state["scrolled_to_map"]:
    st.session_state["scrolled_to_map"] = True
    scroll_to_anchor("mapa-anchor", y_offset_px=80)

center_lat = float(df["lat"].mean())
center_long = float(df["long"].mean())

m = folium.Map(location=[center_lat, center_long], zoom_start=13, tiles="OpenStreetMap")

# Pins no mapa
for _, row in df.iterrows():
    pin_num = int(row["pin"])
    icon_path = _resolve(f"img/pin_{pin_num}.png")

    categoria = CATEGORY_LABELS.get(pin_num, f"Pin {pin_num}")
    pnrs_val = row["pnrs"] if row.get("pnrs") else "-"

    popup_html = f"""
    <div style="font-size: 13px; font-family: Arial, sans-serif;">
      <table style="border-collapse: collapse;">
        <tr><td style="font-weight:600; padding-right:6px;">Categoria:</td><td>{categoria}</td></tr>
        <tr><td style="font-weight:600; padding-right:6px;">Nome do ponto:</td><td>{row["nome"]}</td></tr>
        <tr><td style="font-weight:600; padding-right:6px;">Classificação PNRS:</td><td>{pnrs_val}</td></tr>
        <tr><td style="font-weight:600; padding-right:6px;">Data registro:</td><td>{row["data_registro"]}</td></tr>
      </table>
    </div>
    """

    if icon_path.exists():
        icon = CustomIcon(
            icon_image=str(icon_path),
            icon_size=(42, 42),
            icon_anchor=(16, 32),
        )
        folium.Marker(
            location=[row["lat"], row["long"]],
            icon=icon,
            popup=popup_html,
        ).add_to(m)
    else:
        folium.Marker(
            location=[row["lat"], row["long"]],
            popup=popup_html,
        ).add_to(m)

# fit bounds
try:
    bounds = [
        [float(df["lat"].min()), float(df["long"].min())],
        [float(df["lat"].max()), float(df["long"].max())],
    ]
    m.fit_bounds(bounds, padding=(30, 30))
except Exception:
    pass

# Renderiza mapa
st_folium(
    m,
    width=1200,
    height=550,
    returned_objects=[],
)
