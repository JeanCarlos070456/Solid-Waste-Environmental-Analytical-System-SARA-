# message.py
from pathlib import Path
import base64

import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
SLIDES_DIR = BASE_DIR / "mensagem"
SLIDES = [SLIDES_DIR / f"slide_{i}.png" for i in range(1, 5)]  # slide_1.png ... slide_4.png


def _load_slides_base64():
    imgs = []
    for p in SLIDES:
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            imgs.append(f"data:image/png;base64,{b64}")
    return imgs


def show_intro_message():
    """
    Mostra um modal (imagens) via components.html.
    O botão 'Começar' fecha e reduz o iframe (pra não sobrar espaço).
    """
    slides_b64 = _load_slides_base64()
    if not slides_b64:
        return False

    slides_js_array = "[" + ",".join(f'"{src}"' for src in slides_b64) + "]"

    html = f"""
    <style>
      #sara-overlay {{
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.45);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px;
      }}
      #sara-modal {{
        background: #ffffff;
        border-radius: 12px;
        max-width: 1000px;
        width: 92vw;
        max-height: 90vh;
        box-shadow: 0 18px 40px rgba(0,0,0,0.35);
        border: 1px solid rgba(0,0,0,0.12);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      #sara-modal-header {{
        padding: 10px 18px 8px 18px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-bottom: 1px solid #e0e0e0;
      }}
      #sara-modal-title {{
        font-size: 1.0rem;
        font-weight: 700;
        text-align: center;
      }}
      #sara-modal-body {{
        padding: 10px 12px 6px 12px;
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
      }}
      #sara-slide-img {{
        max-width: 100%;
        max-height: 70vh;
        border-radius: 10px;
        display: block;
        margin: 0 auto;
      }}
      #sara-modal-footer {{
        padding: 8px 14px 12px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #e0e0e0;
        gap: 10px;
      }}
      .sara-nav-btn {{
        background: #f1f1f1;
        border-radius: 999px;
        border: none;
        padding: 6px 12px;
        cursor: pointer;
        font-size: 0.95rem;
        font-weight: 600;
      }}
      .sara-nav-btn:hover {{ background: #e4e4e4; }}
      .sara-dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 999px;
        margin: 0 2px;
        background-color: #ddd;
      }}
      .sara-dot-active {{ background-color: #ff6b4a; }}
      #sara-start-btn {{
        background: #ff6b4a;
        color: #fff;
        border: none;
        border-radius: 999px;
        padding: 8px 16px;
        cursor: pointer;
        font-size: 0.95rem;
        font-weight: 800;
        white-space: nowrap;
      }}
      #sara-start-btn:hover {{ background: #ff5a33; }}
    </style>

    <div id="sara-overlay">
      <div id="sara-modal">
        <div id="sara-modal-header">
          <div id="sara-modal-title">Bem-vindo(a) ao SARA – Sistema Analítico de Resíduos e Ambiente</div>
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

          <button id="sara-start-btn">Começar</button>
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

        function closeOverlayAndShrink() {{
          overlay.style.display = "none";
          try {{
            var iframe = window.frameElement;
            if (iframe) {{
              iframe.style.height = "0px";
              iframe.style.border = "none";
            }}
          }} catch (e) {{}}
        }}

        btnStart.addEventListener("click", closeOverlayAndShrink);
        btnPrev.addEventListener("click", function() {{
          idx = (idx - 1 + slides.length) % slides.length;
          renderSlide();
        }});
        btnNext.addEventListener("click", function() {{
          idx = (idx + 1) % slides.length;
          renderSlide();
        }});

        // fecha clicando fora do modal
        overlay.addEventListener("click", function(e) {{
          if (e.target === overlay) closeOverlayAndShrink();
        }});

        renderSlide();
      }})();
    </script>
    """

    # precisa de altura no primeiro render pra aparecer o modal
    components.html(html, height=780, width="100%")
    return True
