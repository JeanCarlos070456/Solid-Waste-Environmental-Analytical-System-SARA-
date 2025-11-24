import json
import time

import streamlit as st
from streamlit_js_eval import get_geolocation  # <- MESMO PACOTE DOS MAPAS DA SES

from db import insert_ponto

CATEGORY_LABELS = {
    1: "Acúmulo de Pneu",
    2: "Descarte de Eletroeletrônicos",
    3: "Descartes de Móveis e Colchões",
    4: "Descarte de Resíduos Hospitalares",
    5: "Pontos Viciados de Resíduos Comum",
    6: "Descarte de Entulhos de Obras",
}

# ===== Helpers de tempo/parse (baseados no código da SES) =====

AWAIT_TIMEOUT = 8  # segundos máximos esperando resposta do navegador

def _now() -> float:
    return time.time()

def _parse_nav_response(data):
    """
    Mesmo padrão da SES:

    Espera algo tipo:
      - {"latitude": ..., "longitude": ...}
      - {"coords": {"latitude": ..., "longitude": ...}}
      - {"error": "..."} ou {"permission": "denied"}

    Retorna:
      - (lat, lon) -> sucesso
      - "denied"   -> usuário negou / permissão recusada
      - None       -> ainda sem dados
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
st.title("Cadastro de Ponto de Descarte Irregular")

# Estado inicial
if "coords" not in st.session_state:
    st.session_state["coords"] = None

# 'loc_phase' controla o fluxo de geolocalização:
#   None      -> parado
#   'await'   -> aguardando resposta do navegador
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

# Extrai o número do pin (ex.: "Pin 1 - ..." -> 1)
pin_num = int(categoria_escolhida.split()[1])

nome = st.text_input("Nome do ponto (descrição curta)")
pnrs = st.text_input("Classificação PNRS (opcional)")

st.markdown("### Localização")

# ===== Botão que DISPARA o pedido de localização =====

if st.button("Solicitar localização do navegador"):
    # Marca que estamos aguardando o navegador responder
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
        # Ex.: {'coords': {'latitude': -15.8, 'longitude': -47.9}, 'timestamp': ..., 'permission': 'granted'}
        # print para debug se quiser:
        # st.write("DEBUG geolocation:", data)
    except Exception as e:
        data = {"error": str(e)}

    parsed = _parse_nav_response(data)

    if isinstance(parsed, tuple):
        # Sucesso: temos (lat, lon)
        lat, lon = parsed
        st.session_state["coords"] = {"lat": lat, "long": lon}
        st.session_state["loc_phase"] = None
        st.session_state["loc_await_t0"] = None
        st.success(f"Localização obtida: lat={lat:.6f}, long={lon:.6f}")
    elif parsed == "denied":
        # Usuário negou permissão
        st.session_state["coords"] = None
        st.session_state["loc_phase"] = None
        st.session_state["loc_await_t0"] = None
        st.error("Permissão de localização negada no navegador. Habilite o acesso para continuar.")
    else:
        # Ainda não chegou nada útil do navegador
        if elapsed < AWAIT_TIMEOUT:
            # Ainda dentro do timeout: força rerun pra tentar de novo
            st.rerun()
        else:
            # Passou do timeout e não conseguiu
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
            insert_ponto(
                pin=pin_num,
                nome=nome,
                pnrs=pnrs,
                lat=float(coords["lat"]),
                long=float(coords["long"]),
            )
            st.success("Ponto cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")
