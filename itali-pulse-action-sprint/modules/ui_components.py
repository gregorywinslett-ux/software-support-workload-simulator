from __future__ import annotations

from html import escape

import streamlit as st


PHASES = ["Home", "Explain", "Explore", "Collaborate", "Decide", "Act", "Export"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17212b;
            --muted: #5d6875;
            --paper: #f7f9fb;
            --line: #d7dee8;
            --uq-purple: #51247a;
            --teal: #006b68;
            --gold: #bb8a00;
            --coral: #b84a39;
        }
        .stApp { background: var(--paper); color: var(--ink); }
        h1, h2, h3 { letter-spacing: 0; }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px 14px;
        }
        .pulse-card {
            background: #ffffff;
            border: 1px solid var(--line);
            border-left: 5px solid var(--teal);
            border-radius: 8px;
            padding: 18px;
            margin: 10px 0;
            box-shadow: 0 1px 2px rgba(23,33,43,.05);
        }
        .slide-card {
            min-height: 430px;
            background: #ffffff;
            border: 1px solid #cfd7e3;
            border-radius: 8px;
            padding: 42px 52px;
            box-shadow: 0 18px 35px rgba(23,33,43,.08);
        }
        .slide-card h2 { font-size: 2.4rem; margin-bottom: 1rem; color: var(--uq-purple); }
        .slide-card li { font-size: 1.35rem; margin: .75rem 0; line-height: 1.35; }
        .private-tag, .public-tag {
            display: inline-block; border-radius: 999px; padding: 3px 9px; font-size: .78rem; font-weight: 700;
        }
        .private-tag { background: #f5e8d2; color: #5d3a00; }
        .public-tag { background: #dff0ef; color: #004f4d; }
        .ribbon {
            display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 18px 0;
        }
        .ribbon span {
            padding: 7px 11px; border-radius: 999px; border: 1px solid var(--line); background: #fff; color: var(--muted);
            font-size: .9rem; font-weight: 600;
        }
        .ribbon .active { background: var(--uq-purple); color: #fff; border-color: var(--uq-purple); }
        .small-note { color: var(--muted); font-size: .92rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def phase_ribbon(active: str) -> None:
    chips = []
    for phase in ["Explain", "Explore", "Collaborate", "Decide", "Act"]:
        klass = "active" if phase == active else ""
        chips.append(f'<span class="{klass}">{escape(phase)}</span>')
    st.markdown(f"<div class='ribbon'>{''.join(chips)}</div>", unsafe_allow_html=True)


def card(title: str, body: str, accent: str = "") -> None:
    border = f" style='border-left-color:{accent}'" if accent else ""
    st.markdown(
        f"<div class='pulse-card'{border}><h3>{escape(title)}</h3><p>{escape(body)}</p></div>",
        unsafe_allow_html=True,
    )


def public_private_note() -> None:
    st.markdown(
        "<span class='private-tag'>Facilitator private</span> "
        "<span class='public-tag'>Shared screen safe</span>",
        unsafe_allow_html=True,
    )
