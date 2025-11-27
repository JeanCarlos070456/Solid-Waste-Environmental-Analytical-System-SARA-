import json
import time
from datetime import datetime
import base64
import os

import streamlit as st
from streamlit_js_eval import get_geolocation
from db import insert_ponto

CATEGORY_LABELS = {
    1: "Acúmulo de Pneu",
    2: "Descarte de Eletroeletrônicos",
    3: "Descartes de Móveis e Colchões",
    4: "Descarte de Resíduos Hospitalares",
    5: "Pontos Viciados de Resíduos Comum",
    6: "Descarte de Entulhos de Obras",
}

# ===== Helpers de fundo =====

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
        background-color: rgba(255, 255, 255, 0.88);
        border-radius: 1rem;
        padding: 1.5rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ===== Helpers de tempo/parse (baseados no código da SES) =====

AWAIT_TIMEOUT = 8  # segundos máximos esperando resposta do navegador

def _now() -> float:
    return time.time()

def _parse_nav_response(data):
    """
    Mesmo padrão da SES.
    """
    if not isinstance(data, dict):
        return None

    perm = str(data.get("permission", "")).lower()
    err  = str(data.get("error", "")).lower()
    if "denied" in perm or "permission" in err or "denied" in err:
        return "denied"

    lat = data.get("latitude"); lon = data.get("longitude")
    if (lat is None or lon is None) and isinstance(data.get("coords"), dict):
        c = data["coords"]
        lat, lon = c.get("latitude"), c.get("longitude")

    if lat is None or lon is None:
        return None

    try:
        return float(lat), float(lon)
    except Exception:
        return None

# ===== Config Streamlit =====

st.set_page_config(page_title="SARA - Novo Ponto", layout="centered")
set_background("fundos/fundo_form.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo/residencia_cts.png", use_container_width=True)

st.title("Cadastro de Ponto de Descarte Irregular (Sol Nascente)-SARA")
st.write("Residência CTS- Ciência, Técnologia e Sociedade")
# Estado inicial
if "coords" not in st.session_state:
    st.session_state["coords"] = None

if "loc_phase" not in st.session_state:
    st.session_state["loc_phase"] = None

if "loc_await_t0" not in st.session_state:
    st.session_state["loc_await_t0"] = None

# ===== Formulário de dados =====

st.markdown("### Dados do ponto")

categoria_opcoes = [f"Pin {pin} - {label}" for pin, label in CATEGORY_LABELS.items()]

categoria_escolhida = st.selectbox(
    "Categoria do ponto identificado",
    options=categoria_opcoes
)

pin_num = int(categoria_escolhida.split()[1])

nome = st.text_input("Nome do ponto (descrição curta)")
pnrs = st.text_input("Classificação PNRS (opcional)")

st.markdown("### Localização")

# ===== Botão que DISPARA o pedido de localização =====

if st.button("Solicitar localização do navegador"):
    st.session_state["loc_phase"] = "await"
    st.session_state["loc_await_t0"] = _now()
    st.session_state["coords"] = None
    st.rerun()

# ===== Fase de espera: aqui é onde de fato chamamos get_geolocation() =====

if st.session_state["loc_phase"] == "await":
    t0 = st.session_state["loc_await_t0"] or _now()
    elapsed = _now() - float(t0)

    st.info("Aguardando resposta do navegador... verifique o pedido de permissão de localização.")

    try:
        data = get_geolocation()
    except Exception as e:
        data = {"error": str(e)}

    parsed = _parse_nav_response(data)

    if isinstance(parsed, tuple):
        lat, lon = parsed
        st.session_state["coords"] = {"lat": lat, "long": lon}
        st.session_state["loc_phase"] = None
        st.session_state["loc_await_t0"] = None
        st.success(f"Localização obtida: lat={lat:.6f}, long={lon:.6f}")
    elif parsed == "denied":
        st.session_state["coords"] = None
        st.session_state["loc_phase"] = None
        st.session_state["loc_await_t0"] = None
        st.error("Permissão de localização negada no navegador. Habilite o acesso para continuar.")
    else:
        if elapsed < AWAIT_TIMEOUT:
            st.rerun()
        else:
            st.session_state["coords"] = None
            st.session_state["loc_phase"] = None
            st.session_state["loc_await_t0"] = None
            st.error("Não foi possível obter a localização dentro do tempo limite. Tente novamente.")

coords = st.session_state["coords"]

# ===== Feedback pro usuário =====

if coords:
    st.info(f"Coordenadas atuais: lat={coords['lat']:.6f}, long={coords['long']:.6f}")
else:
    st.warning(
        "Nenhuma coordenada capturada ainda. "
        "Clique em **'Solicitar localização do navegador'** e permita o acesso."
    )

st.markdown("---")

# ===== Botão Finalizar: desabilitado até ter coordenadas =====

finalizar = st.button("Finalizar cadastro", disabled=(coords is None))

if finalizar:
    if not nome:
        st.error("Informe o nome do ponto.")
    elif not coords:
        st.error("Capture a localização antes de finalizar.")
    else:
        try:
            data_registro = datetime.now().strftime("%Y-%m-%d")

            insert_ponto(
                pin=pin_num,
                nome=nome,
                pnrs=pnrs,
                lat=float(coords["lat"]),
                long=float(coords["long"]),
                data_registro=data_registro,
            )
            st.success("Ponto cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")
