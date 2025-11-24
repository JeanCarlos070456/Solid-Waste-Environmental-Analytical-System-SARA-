import streamlit as st

def sidebar_filters(category_labels: dict) -> list:
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
    st.sidebar.caption("SARA - Sistema Analítico de Resíduos e Ambiente")

    return selected_pins
