from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


APP_DIR = Path(__file__).parent


def build_embedded_html() -> str:
    html = (APP_DIR / "index.html").read_text(encoding="utf-8")
    css = (APP_DIR / "src" / "styles.css").read_text(encoding="utf-8")
    js = (APP_DIR / "src" / "app.js").read_text(encoding="utf-8")

    html = html.replace('<link rel="stylesheet" href="./src/styles.css" />', f"<style>{css}</style>")
    html = html.replace('<script type="module" src="./src/app.js"></script>', f"<script type=\"module\">{js}</script>")
    return html


st.set_page_config(
    page_title="Scenario Studio",
    page_icon="SS",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      #MainMenu, footer, header { visibility: hidden; }
      .block-container {
        padding: 0;
        max-width: none;
      }
      iframe {
        display: block;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(build_embedded_html(), height=1100, scrolling=True)
