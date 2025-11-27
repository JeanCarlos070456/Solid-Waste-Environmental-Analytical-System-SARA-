import streamlit as st

def sidebar_filters(category_labels: dict) -> list:
    # Logo da Residência no topo da sidebar
    st.sidebar.image("logo/residencia_cts.png", use_container_width=True)
    st.sidebar.markdown("---")

    st.sidebar.header("Filtros")
    st.sidebar.write("Selecione as categorias de pontos que deseja visualizar:")

    # Monta opções do tipo "Pin 1 - Acúmulo de Pneu"
    option_map = {}
    options = []
    for pin, label in category_labels.items():
        text = f"Pin {pin} - {label}"
        options.append(text)
        option_map[text] = pin

    selected = st.sidebar.multiselect(
        "Categorias",
        options=options,
        default=options,
    )

    selected_pins = [option_map[o] for o in selected]

    st.sidebar.markdown("---")
    st.sidebar.subheader("Legenda")

    # Legenda dos pins
    for pin, label in category_labels.items():
        col_icon, col_text = st.sidebar.columns([1, 4])
        with col_icon:
            st.image(f"img/pin_{pin}.png", use_container_width=True)
        with col_text:
            st.markdown(f"**Pin {pin}**<br>{label}", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.caption("SARA - Sistema Analítico de Resíduos e Ambiente")

    return selected_pins
