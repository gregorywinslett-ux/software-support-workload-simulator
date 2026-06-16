from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.models import DEFAULT_CRITERIA, DEFAULT_SLIDES


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_sample_themes() -> list[dict]:
    return pd.read_csv(DATA_DIR / "sample_themes.csv").to_dict("records")


def load_sample_responses() -> list[dict]:
    return pd.read_csv(DATA_DIR / "sample_responses.csv").to_dict("records")


def load_sample_session() -> dict:
    with open(DATA_DIR / "sample_session.json", "r", encoding="utf-8") as handle:
        return json.load(handle)


def initialise_state() -> None:
    defaults = {
        "mode": "Home",
        "session_title": "ITaLI Pulse Action Sprint",
        "duration_minutes": 45,
        "facilitator_notes": "",
        "base_url": "http://localhost:8501",
        "slide_index": 0,
        "slides": DEFAULT_SLIDES.copy(),
        "themes": load_sample_themes(),
        "responses": [],
        "group_comments": [],
        "candidate_actions": [],
        "criteria": [criterion.copy() for criterion in DEFAULT_CRITERIA],
        "pairwise_responses": [],
        "ratings": {},
        "weights_locked": False,
        "current_collaboration_prompt": "Where does workload pressure, role ambiguity, or cross-team friction show up?",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def load_samples_into_state() -> None:
    sample = load_sample_session()
    st.session_state.responses = load_sample_responses()
    st.session_state.candidate_actions = sample["candidate_actions"]
    st.session_state.facilitator_notes = sample["facilitator_notes"]


def reset_session() -> None:
    for key in [
        "responses",
        "group_comments",
        "candidate_actions",
        "pairwise_responses",
        "ratings",
        "weights_locked",
    ]:
        st.session_state.pop(key, None)
    initialise_state()
