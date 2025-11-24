# SARA - Sistema Analítico de Resíduos e Ambiente

Sistema em Python + Streamlit para mapear pontos de descarte irregular de resíduos sólidos, usando pins específicos para cada categoria.

## Estrutura

- `app.py` – Mapa com os pontos cadastrados e filtros na sidebar.
- `form.py` – Formulário para cadastro de novos pontos (usa geolocalização do navegador).
- `sidebar.py` – Funções da barra lateral (filtros dos pins).
- `db.py` – Conexão e funções de acesso ao banco SQLite.
- `tabela.py` – Script para criação da tabela `pontos`.
- `img/` – Contém os arquivos de ícone:
  - `pin_1.png` – Acúmulo de Pneu
  - `pin_2.png` – Descarte de Eletroeletrônicos
  - `pin_3.png` – Descartes de Móveis e Colchões
  - `pin_4.png` – Descarte de Resíduos Hospitalares
  - `pin_5.png` – Pontos Viciados de Resíduos Comum
  - `pin_6.png` – Descarte de Entulhos de Obras

## Dependências

```bash
pip install streamlit folium streamlit-folium streamlit-javascript pandas
