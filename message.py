# message.py
from pathlib import Path
import base64

import streamlit as st
import streamlit.components.v1 as components

SLIDES_DIR = Path("mensagem")
SLIDES = [SLIDES_DIR / f"slide_{i}.png" for i in range(1, 5)]  # slide_1.png ... slide_4.png


def _load_slides_base64():
    imgs = []
    for p in SLIDES:
        if p.exists():
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            imgs.append(f"data:image/png;base64,{b64}")
    return imgs


def show_intro_message():
    slides_b64 = _load_slides_base64()
    if not slides_b64:
        return

    slides_js_array = "[" + ",".join(f'"{src}"' for src in slides_b64) + "]"

    html = f"""
    <style>
    #sara-overlay {{
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.45);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    #sara-modal {{
        background: #ffffff;
        border-radius: 12px;
        max-width: 1000px;
        width: 90vw;
        max-height: 90vh;
        box-shadow: 0 18px 40px rgba(0,0,0,0.35);
        border: 1px solid rgba(0,0,0,0.12);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    #sara-modal-header {{
        padding: 10px 18px 6px 18px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-bottom: 1px solid #e0e0e0;
    }}
    #sara-modal-title {{
        font-size: 1.0rem;
        font-weight: 600;
        text-align: center;
    }}
    #sara-modal-body {{
        padding: 8px 12px 4px 12px;
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    #sara-slide-img {{
        max-width: 100%;
        max-height: 70vh;
        border-radius: 8px;
        display: block;
        margin: 0 auto;
    }}
    #sara-modal-footer {{
        padding: 6px 14px 12px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #e0e0e0;
    }}
    .sara-nav-btn {{
        background: #f1f1f1;
        border-radius: 999px;
        border: none;
        padding: 4px 10px;
        cursor: pointer;
        font-size: 0.9rem;
    }}
    .sara-nav-btn:hover {{
        background: #e4e4e4;
    }}
    .sara-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 999px;
        margin: 0 2px;
        background-color: #ddd;
    }}
    .sara-dot-active {{
        background-color: #ff6b4a;
    }}
    #sara-start-btn {{
        background: #ff6b4a;
        color: #fff;
        border: none;
        border-radius: 999px;
        padding: 6px 16px;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 600;
    }}
    #sara-start-btn:hover {{
        background: #ff5a33;
    }}
    </style>

    <div id="sara-overlay">
      <div id="sara-modal">
        <div id="sara-modal-header">
          <div id="sara-modal-title">
            Bem-vindo(a) ao SARA – Sistema Analítico de Resíduos e Ambiente
          </div>
        </div>
        <div id="sara-modal-body">
          <img id="sara-slide-img" src="" alt="Apresentação SARA" />
        </div>
        <div id="sara-modal-footer">
          <div>
            <button class="sara-nav-btn" id="sara-prev-btn">◀</button>
            <span id="sara-dots"></span>
            <button class="sara-nav-btn" id="sara-next-btn">▶</button>
          </div>
          <button id="sara-start-btn">
        </div>
      </div>
    </div>

    <script>
    (function() {{
        const slides = {slides_js_array};
        let idx = 0;

        const overlay = document.getElementById("sara-overlay");
        const imgEl = document.getElementById("sara-slide-img");
        const dotsContainer = document.getElementById("sara-dots");
        const btnPrev = document.getElementById("sara-prev-btn");
        const btnNext = document.getElementById("sara-next-btn");
        const btnStart = document.getElementById("sara-start-btn");

        function renderDots() {{
            dotsContainer.innerHTML = "";
            for (let i = 0; i < slides.length; i++) {{
                const span = document.createElement("span");
                span.className = "sara-dot" + (i === idx ? " sara-dot-active" : "");
                dotsContainer.appendChild(span);
            }}
        }}

        function renderSlide() {{
            imgEl.src = slides[idx];
            renderDots();
        }}

        function closeOverlayAndScroll() {{
            overlay.style.display = "none";

            // zera a altura do iframe que contém este componente
            try {{
                var iframe = window.frameElement;
                if (iframe) {{
                    iframe.style.height = "0px";
                    iframe.style.border = "none";
                }}
            }} catch (e) {{}}

            // rola a página para aproximar o centro do mapa
            try {{
                var root = window.parent || window;
                var h = root.innerHeight || window.innerHeight || 800;
                root.scrollTo({{ top: h * 0.5, behavior: "smooth" }});
            }} catch (e) {{}}
        }}

        btnStart.onclick = closeOverlayAndScroll;

        btnPrev.onclick = function() {{
            idx = (idx - 1 + slides.length) % slides.length;
            renderSlide();
        }};
        btnNext.onclick = function() {{
            idx = (idx + 1) % slides.length;
            renderSlide();
        }};

        renderSlide();
    }})();
    </script>
    """

    # altura inicial suficiente para mostrar o popup; depois o JS zera isso
    components.html(html, height=750, width="100%")
