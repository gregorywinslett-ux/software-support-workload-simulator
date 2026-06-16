from __future__ import annotations

import json
import os
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.exports import (
    build_prompt,
    dataframe_csv,
    markdown_action_plan,
    markdown_decision_record,
    markdown_resource_kit,
    session_json,
)
from modules.models import DECISION_STATUSES, VISIBILITY_STATUSES, new_id, now_iso
from modules.qr import participant_url, qr_png_bytes
from modules.scoring import PREFERENCE_VALUES, aggregate_weights, pairwise_weights, rank_actions
from modules.state import initialise_state, load_samples_into_state, reset_session
from modules.ui_components import PHASES, card, inject_css, phase_ribbon, public_private_note


st.set_page_config(
    page_title="ITaLI Pulse Action Sprint Studio",
    page_icon="P",
    layout="wide",
)
inject_css()
initialise_state()


def configured_access_code() -> str:
    try:
        return st.secrets.get("APP_ACCESS_CODE", "")
    except Exception:
        return os.getenv("APP_ACCESS_CODE", "")


def access_allowed() -> bool:
    access_code = configured_access_code()
    if not access_code:
        return True
    if st.session_state.get("access_granted"):
        return True

    st.title("ITaLI Pulse Action Sprint Studio")
    st.caption("This prototype is access-code protected for limited review.")
    entered = st.text_input("Access code", type="password")
    if st.button("Enter", type="primary"):
        if entered == access_code:
            st.session_state.access_granted = True
            st.rerun()
        else:
            st.error("Access code not recognised.")
    return False


def selected_criteria() -> list[dict]:
    return [criterion for criterion in st.session_state.criteria if criterion.get("selected_for_pairwise")]


def theme_lookup() -> dict[str, str]:
    return {theme["theme_id"]: theme["theme_name"] for theme in st.session_state.themes}


def participant_response_form() -> None:
    st.title("ITaLI Pulse Action Sprint")
    st.caption("Anonymous individual input. Please do not enter names or sensitive personal information.")
    with st.form("participant_response"):
        theme_names = theme_lookup()
        selected = st.selectbox(
            "Relevant theme",
            options=list(theme_names.keys()),
            format_func=lambda key: theme_names[key],
        )
        pain_point = st.text_area("Where does workload pressure, role ambiguity, or cross-team friction show up?")
        proposed_action = st.text_area("What practical action or way of working could help?")
        escalation = st.text_input("Who or what area may need to help resolve it?")
        table_label = st.text_input("Optional table label")
        submitted = st.form_submit_button("Submit anonymous response", type="primary")
    if submitted:
        st.session_state.responses.append(
            {
                "response_id": new_id("R"),
                "timestamp": now_iso(),
                "selected_theme": selected,
                "pain_point": pain_point.strip(),
                "proposed_action": proposed_action.strip(),
                "escalation_responsibility": escalation.strip(),
                "optional_table_label": table_label.strip(),
                "visibility_status": "raw",
                "facilitator_notes": "",
            }
        )
        st.success("Thanks. Your anonymous response has been submitted.")


def participant_pairwise_form() -> None:
    criteria = selected_criteria()
    st.title("Criteria weighting")
    st.caption("Anonymous individual input. Compare the three criteria based on what should guide today's decision.")
    if len(criteria) != 3:
        st.warning("The facilitator has not selected exactly three criteria yet.")
        return
    options = list(PREFERENCE_VALUES.keys())
    pairs = [(0, 1), (0, 2), (1, 2)]
    with st.form("participant_pairwise"):
        choices = []
        for i, j in pairs:
            a = criteria[i]["criterion_name"]
            b = criteria[j]["criterion_name"]
            choices.append(st.radio(f"{a} vs {b}", options, index=3, horizontal=False))
        submitted = st.form_submit_button("Submit weighting", type="primary")
    if submitted:
        st.session_state.pairwise_responses.append(
            {
                "participant_response_id": new_id("PW"),
                "timestamp": now_iso(),
                "comparison_1": choices[0],
                "comparison_2": choices[1],
                "comparison_3": choices[2],
                "calculated_individual_weights": pairwise_weights(criteria, choices),
            }
        )
        st.success("Thanks. Your criteria weighting has been submitted.")


def route_participant() -> bool:
    params = st.query_params
    if params.get("role") != "participant":
        return False
    activity = params.get("activity", "responses")
    if activity == "pairwise":
        participant_pairwise_form()
    else:
        participant_response_form()
    return True


def sidebar_nav() -> None:
    with st.sidebar:
        st.title("Pulse Studio")
        st.session_state.mode = st.radio("Mode", PHASES, index=PHASES.index(st.session_state.mode))
        st.divider()
        st.metric("Responses", len(st.session_state.responses))
        st.metric("Candidate actions", len(st.session_state.candidate_actions))
        st.metric("Pairwise inputs", len(st.session_state.pairwise_responses))
        st.caption("Prototype only. No authentication, cloud storage, or institutional integration.")


def page_home() -> None:
    st.title("ITaLI Pulse Action Sprint Studio")
    st.subheader("Meeting-native decision environment for workload action planning")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.session_state.session_title = st.text_input("Session title", st.session_state.session_title)
        st.session_state.duration_minutes = st.number_input("Session duration minutes", 15, 180, st.session_state.duration_minutes)
        st.session_state.facilitator_notes = st.text_area("Facilitator notes", st.session_state.facilitator_notes, height=120)
    with c2:
        st.session_state.base_url = st.text_input("Base URL for QR codes", st.session_state.base_url)
        st.info(
            "QR access from phones requires this Streamlit app to be reachable on the same network. "
            "localhost only works on the facilitator machine."
        )
    with c3:
        if st.button("Load synthetic sample data", type="primary"):
            load_samples_into_state()
            st.success("Sample responses and candidate actions loaded.")
        if st.button("Reset session data"):
            reset_session()
            st.warning("Session data reset.")
    st.markdown("### Privacy and governance note")
    st.write(
        "No names should be collected. Raw individual responses are private to facilitator view by default. "
        "The prototype stores data only in the running local session unless exported. Do not enter sensitive personal information. "
        "Production use would require institutional privacy, security, accessibility, records, and moderation review."
    )
    st.markdown("### Meeting spine")
    cols = st.columns(6)
    for col, label in zip(cols, ["Notice", "Name", "Discuss", "Prioritise", "Resolve", "Review"]):
        col.markdown(f"#### {label}")


def page_explain() -> None:
    phase_ribbon("Explain")
    st.title("Explain Mode")
    public_private_note()
    slides = st.session_state.slides
    st.progress((st.session_state.slide_index + 1) / len(slides))
    slide = slides[st.session_state.slide_index]
    c1, c2 = st.columns([1.8, 1])
    with c1:
        bullets = "".join(f"<li>{escape(item)}</li>" for item in slide["body"])
        st.markdown(
            f"<div class='slide-card'><h2>{escape(slide['title'])}</h2><ul>{bullets}</ul></div>",
            unsafe_allow_html=True,
        )
        n1, n2, n3 = st.columns([1, 1, 2])
        if n1.button("Back", disabled=st.session_state.slide_index == 0):
            st.session_state.slide_index -= 1
            st.rerun()
        if n2.button("Next", disabled=st.session_state.slide_index == len(slides) - 1, type="primary"):
            st.session_state.slide_index += 1
            st.rerun()
        n3.caption(f"Slide {st.session_state.slide_index + 1} of {len(slides)}")
    with c2:
        st.markdown("### Editable slide content")
        slide["title"] = st.text_input("Slide title", slide["title"])
        body_text = st.text_area("Body bullets, one per line", "\n".join(slide["body"]), height=220)
        slide["body"] = [line.strip() for line in body_text.splitlines() if line.strip()]
        slide["notes"] = st.text_area("Speaker notes", slide.get("notes", ""), height=140)
        uploaded = st.file_uploader("Replace slides from JSON", type=["json"])
        if uploaded:
            try:
                st.session_state.slides = json.load(uploaded)
                st.session_state.slide_index = 0
                st.success("Slides replaced from uploaded JSON.")
                st.rerun()
            except json.JSONDecodeError:
                st.error("Upload a JSON array of slides with title, body, and notes fields.")
        manual = st.text_area("Paste replacement findings or slide outline", height=120)
        if st.button("Create simple slides from pasted text") and manual.strip():
            st.session_state.slides = [
                {"title": "Uploaded Pulse findings", "body": [line.strip() for line in manual.splitlines() if line.strip()], "notes": ""}
            ]
            st.session_state.slide_index = 0
            st.rerun()


def page_explore() -> None:
    phase_ribbon("Explore")
    st.title("Explore Mode")
    st.caption("A dashboard-style view of the action space. Keep this focused on sense-making, not exhaustive analysis.")
    themes = st.session_state.themes
    theme_names = theme_lookup()
    selected = st.selectbox("Filter by theme", ["all"] + list(theme_names.keys()), format_func=lambda x: "All themes" if x == "all" else theme_names[x])
    display = themes if selected == "all" else [theme for theme in themes if theme["theme_id"] == selected]
    cols = st.columns(2)
    for index, theme in enumerate(display):
        with cols[index % 2]:
            card(theme["theme_name"], f"{theme['short_description']}\n\nEvidence: {theme['evidence_signal']}")
            st.write(f"Prompt: {theme['discussion_prompt']}")
            if st.button("Send this theme to collaboration prompt", key=f"send_{theme['theme_id']}"):
                st.session_state.current_collaboration_prompt = theme["discussion_prompt"]
                st.success("Collaboration prompt updated.")
    if st.session_state.responses:
        df = pd.DataFrame(st.session_state.responses)
        counts = df["selected_theme"].map(theme_names).value_counts().reset_index()
        counts.columns = ["theme", "responses"]
        st.plotly_chart(px.bar(counts, x="theme", y="responses", title="Responses by theme"), use_container_width=True)


def add_candidate_action(source_response: dict | None = None) -> None:
    with st.form(f"candidate_{source_response['response_id'] if source_response else 'manual'}"):
        title_default = source_response["proposed_action"][:70] if source_response else ""
        desc_default = source_response["proposed_action"] if source_response else ""
        theme_default = source_response["selected_theme"] if source_response else st.session_state.themes[0]["theme_id"]
        title = st.text_input("Action title", title_default)
        description = st.text_area("Action description", desc_default)
        theme = st.selectbox("Linked theme", [theme["theme_id"] for theme in st.session_state.themes], index=[theme["theme_id"] for theme in st.session_state.themes].index(theme_default), format_func=lambda x: theme_lookup()[x])
        rationale = st.text_area("Facilitator rationale", source_response.get("pain_point", "") if source_response else "")
        submitted = st.form_submit_button("Promote/create candidate action")
    if submitted and title.strip():
        st.session_state.candidate_actions.append(
            {
                "action_id": new_id("A"),
                "action_title": title.strip(),
                "action_description": description.strip(),
                "linked_theme": theme,
                "source_response_ids": [source_response["response_id"]] if source_response else [],
                "facilitator_rationale": rationale.strip(),
                "decision_status": "undecided",
            }
        )
        if source_response:
            source_response["visibility_status"] = "promoted"
        st.success("Candidate action added.")


def page_collaborate() -> None:
    phase_ribbon("Collaborate")
    st.title("Collaborate Mode")
    public_private_note()
    response_url = participant_url(st.session_state.base_url, "responses")
    c1, c2 = st.columns([0.8, 1.4])
    with c1:
        st.image(qr_png_bytes(response_url), width=230)
        st.code(response_url)
        st.caption("Staff use their own devices for anonymous individual input. Manual facilitator entry remains available.")
    with c2:
        st.session_state.current_collaboration_prompt = st.text_area(
            "Current public prompt",
            st.session_state.current_collaboration_prompt,
            height=90,
        )
        st.metric("Responses received", len(st.session_state.responses))
        if st.session_state.responses:
            df = pd.DataFrame(st.session_state.responses)
            st.dataframe(
                df[["response_id", "selected_theme", "visibility_status", "pain_point", "proposed_action"]],
                use_container_width=True,
                hide_index=True,
            )
    st.markdown("### Facilitator response inbox")
    for response in st.session_state.responses:
        with st.expander(f"{response['response_id']} - {theme_lookup().get(response['selected_theme'], response['selected_theme'])}"):
            st.write(response["pain_point"])
            st.write(response["proposed_action"])
            response["visibility_status"] = st.selectbox(
                "Visibility",
                VISIBILITY_STATUSES,
                index=VISIBILITY_STATUSES.index(response.get("visibility_status", "raw")),
                key=f"vis_{response['response_id']}",
            )
            response["facilitator_notes"] = st.text_input("Facilitator notes", response.get("facilitator_notes", ""), key=f"note_{response['response_id']}")
            add_candidate_action(response)
    st.markdown("### Manual candidate action")
    if len(st.session_state.candidate_actions) >= 7:
        st.warning("Seven candidate actions are already present. Park or combine actions before final prioritisation.")
    add_candidate_action()
    st.markdown("### Public group comments")
    with st.form("group_comment"):
        comment = st.text_area("Comment text")
        linked_theme = st.selectbox("Linked theme", [theme["theme_id"] for theme in st.session_state.themes], format_func=lambda x: theme_lookup()[x])
        display = st.checkbox("Display publicly", True)
        submitted = st.form_submit_button("Add group comment")
    if submitted and comment.strip():
        st.session_state.group_comments.append(
            {
                "comment_id": new_id("C"),
                "timestamp": now_iso(),
                "phase": "Collaborate",
                "comment_text": comment.strip(),
                "linked_theme": linked_theme,
                "display_publicly": display,
            }
        )
        st.success("Group comment added.")
    visible_comments = [comment for comment in st.session_state.group_comments if comment.get("display_publicly")]
    if visible_comments:
        st.markdown("#### Shared-screen comments")
        for item in visible_comments:
            st.info(item["comment_text"])


def page_decide() -> None:
    phase_ribbon("Decide")
    st.title("Decide Mode")
    tabs = st.tabs(["Criteria selection", "Pairwise weighting", "Action rating"])
    with tabs[0]:
        st.markdown("### Select exactly three criteria")
        for criterion in st.session_state.criteria:
            c1, c2, c3 = st.columns([0.25, 0.75, 2])
            criterion["selected_for_pairwise"] = c1.checkbox("Use", criterion["selected_for_pairwise"], key=f"use_{criterion['criterion_id']}")
            criterion["criterion_name"] = c2.text_input("Criterion", criterion["criterion_name"], key=f"name_{criterion['criterion_id']}")
            criterion["description"] = c3.text_input("Description", criterion["description"], key=f"desc_{criterion['criterion_id']}")
        with st.form("add_criterion"):
            name = st.text_input("Add custom criterion")
            description = st.text_input("Custom criterion description")
            submitted = st.form_submit_button("Add criterion")
        if submitted and name.strip():
            st.session_state.criteria.append(
                {
                    "criterion_id": new_id("CR").lower(),
                    "criterion_name": name.strip(),
                    "description": description.strip(),
                    "selected_for_pairwise": False,
                }
            )
            st.rerun()
        criteria = selected_criteria()
        if len(criteria) != 3:
            st.warning(f"Select exactly three criteria before pairwise weighting. Current selection: {len(criteria)}.")
        else:
            cols = st.columns(3)
            for col, criterion in zip(cols, criteria):
                col.metric(criterion["criterion_name"], "selected")
                col.write(criterion["description"])
    with tabs[1]:
        criteria = selected_criteria()
        if len(criteria) != 3:
            st.warning("Pairwise weighting is available after exactly three criteria are selected.")
        else:
            pairwise_url = participant_url(st.session_state.base_url, "pairwise")
            c1, c2 = st.columns([0.8, 1.4])
            with c1:
                st.image(qr_png_bytes(pairwise_url), width=230)
                st.code(pairwise_url)
            with c2:
                weights = aggregate_weights(st.session_state.pairwise_responses, criteria)
                st.metric("Pairwise responses", len(st.session_state.pairwise_responses))
                st.plotly_chart(px.bar(weights, x="criterion_name", y="weight", error_y="spread", range_y=[0, 1]), use_container_width=True)
                st.dataframe(weights, use_container_width=True, hide_index=True)
                if st.button("Lock weights for action rating", type="primary"):
                    st.session_state.weights_locked = True
                    st.success("Weights locked.")
    with tabs[2]:
        criteria = selected_criteria()
        weights = aggregate_weights(st.session_state.pairwise_responses, criteria) if len(criteria) == 3 else pd.DataFrame()
        actions = st.session_state.candidate_actions[:7]
        if len(criteria) != 3:
            st.warning("Select three criteria before rating actions.")
        elif not actions:
            st.warning("Promote candidate actions from Collaborate mode first.")
        else:
            for action in actions:
                st.markdown(f"#### {action['action_title']}")
                action["decision_status"] = st.selectbox(
                    "Final decision status",
                    DECISION_STATUSES,
                    index=DECISION_STATUSES.index(action.get("decision_status", "undecided")),
                    key=f"status_{action['action_id']}",
                )
                st.session_state.ratings.setdefault(action["action_id"], {})
                cols = st.columns(3)
                for col, criterion in zip(cols, criteria):
                    st.session_state.ratings[action["action_id"]].setdefault(criterion["criterion_id"], {"rating": 3, "rationale": ""})
                    cell = st.session_state.ratings[action["action_id"]][criterion["criterion_id"]]
                    cell["rating"] = col.slider(
                        criterion["criterion_name"],
                        1,
                        5,
                        int(cell.get("rating", 3)),
                        key=f"rate_{action['action_id']}_{criterion['criterion_id']}",
                    )
                    cell["rationale"] = col.text_input("Rationale", cell.get("rationale", ""), key=f"rat_{action['action_id']}_{criterion['criterion_id']}")
            ranked = rank_actions(actions, st.session_state.ratings, weights)
            st.markdown("### Advisory ranking")
            st.dataframe(ranked, use_container_width=True, hide_index=True)


def session_payload() -> dict:
    criteria = selected_criteria()
    weights = aggregate_weights(st.session_state.pairwise_responses, criteria) if len(criteria) == 3 else pd.DataFrame()
    ranked = rank_actions(st.session_state.candidate_actions[:7], st.session_state.ratings, weights) if not weights.empty else pd.DataFrame()
    return {
        "session_title": st.session_state.session_title,
        "duration_minutes": st.session_state.duration_minutes,
        "slides": st.session_state.slides,
        "themes": st.session_state.themes,
        "responses": st.session_state.responses,
        "group_comments": st.session_state.group_comments,
        "candidate_actions": st.session_state.candidate_actions,
        "criteria": criteria,
        "pairwise_response_count": len(st.session_state.pairwise_responses),
        "weights": weights.to_dict("records") if not weights.empty else [],
        "ratings": st.session_state.ratings,
        "ranked_actions": ranked.to_dict("records") if not ranked.empty else [],
    }


def artefacts() -> tuple[str, str, str, pd.DataFrame, pd.DataFrame]:
    criteria = selected_criteria()
    weights = aggregate_weights(st.session_state.pairwise_responses, criteria) if len(criteria) == 3 else pd.DataFrame()
    ranked = rank_actions(st.session_state.candidate_actions[:7], st.session_state.ratings, weights) if not weights.empty else pd.DataFrame()
    plan = markdown_action_plan(ranked, st.session_state.candidate_actions) if not ranked.empty else "# Action Plan Brief\n\nNo ranked actions yet."
    record = markdown_decision_record(weights, ranked, st.session_state.group_comments) if not weights.empty else "# Decision Record and Logic\n\nNo decision data yet."
    kit = markdown_resource_kit()
    return plan, record, kit, weights, ranked


def page_act() -> None:
    phase_ribbon("Act")
    st.title("Act Mode")
    plan, record, kit, _, _ = artefacts()
    payload = session_json(session_payload())
    prompts = {
        "Action plan brief prompt": build_prompt("action plan brief", plan, payload),
        "Decision record prompt": build_prompt("decision record and logic", record, payload),
        "Resource kit prompt": build_prompt("resource kit outline", kit, payload),
        "Combined master prompt": build_prompt("complete post-meeting artefact pack", f"{plan}\n\n{record}\n\n{kit}", payload),
    }
    tabs = st.tabs(["Action plan brief", "Decision record", "Resource kit", "ChatGPT prompts"])
    with tabs[0]:
        st.text_area("Preview", plan, height=520)
    with tabs[1]:
        st.text_area("Preview", record, height=520)
    with tabs[2]:
        st.text_area("Preview", kit, height=520)
    with tabs[3]:
        for title, prompt in prompts.items():
            st.text_area(title, prompt, height=280)


def page_export() -> None:
    st.title("Export")
    plan, record, kit, weights, ranked = artefacts()
    payload = session_payload()
    prompt_bundle = "\n\n---\n\n".join(
        [
            build_prompt("action plan brief", plan, session_json(payload)),
            build_prompt("decision record and logic", record, session_json(payload)),
            build_prompt("resource kit outline", kit, session_json(payload)),
        ]
    )
    c1, c2 = st.columns(2)
    c1.download_button("Full session JSON", session_json(payload), "itali_pulse_session.json", "application/json")
    c1.download_button("Individual responses CSV", dataframe_csv(st.session_state.responses), "individual_responses.csv", "text/csv")
    c1.download_button("Candidate actions CSV", dataframe_csv(st.session_state.candidate_actions), "candidate_actions.csv", "text/csv")
    c1.download_button("Criteria weights CSV", dataframe_csv(weights), "criteria_weights.csv", "text/csv")
    c2.download_button("Action ratings and rankings CSV", dataframe_csv(ranked), "action_rankings.csv", "text/csv")
    c2.download_button("Action plan brief Markdown", plan, "action_plan_brief.md", "text/markdown")
    c2.download_button("Decision record Markdown", record, "decision_record.md", "text/markdown")
    c2.download_button("Resource kit outline Markdown", kit, "resource_kit_outline.md", "text/markdown")
    st.download_button("ChatGPT prompts TXT", prompt_bundle, "chatgpt_prompts.txt", "text/plain")


if access_allowed() and not route_participant():
    sidebar_nav()
    mode = st.session_state.mode
    if mode == "Home":
        page_home()
    elif mode == "Explain":
        page_explain()
    elif mode == "Explore":
        page_explore()
    elif mode == "Collaborate":
        page_collaborate()
    elif mode == "Decide":
        page_decide()
    elif mode == "Act":
        page_act()
    elif mode == "Export":
        page_export()
