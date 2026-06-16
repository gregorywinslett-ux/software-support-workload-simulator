from __future__ import annotations

import json

import pandas as pd


def dataframe_csv(rows: list[dict] | pd.DataFrame) -> bytes:
    df = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")


def session_json(state: dict) -> str:
    return json.dumps(state, indent=2, ensure_ascii=False, default=str)


def markdown_action_plan(ranked: pd.DataFrame, actions: list[dict]) -> str:
    by_id = {action["action_id"]: action for action in actions}
    adopted = ranked[ranked["decision_status"].eq("adopt")].head(3)
    if adopted.empty:
        adopted = ranked.head(3)
    lines = ["# Action Plan Brief", "", "## Top actions"]
    for _, row in adopted.iterrows():
        action = by_id.get(row["action_id"], {})
        lines.extend(
            [
                f"### {row['action_title']}",
                f"- Linked theme: {action.get('linked_theme', '')}",
                f"- Description: {action.get('action_description', '')}",
                f"- Rationale: {action.get('facilitator_rationale', '')}",
                "- Suggested owner area: To be confirmed",
                "- First next step: Confirm owner, scope, and first review point",
                "- Possible metric/review point: Evidence of use, decisions made, and unresolved pressure",
                "- Dependency or risk: Needs consistent uptake and clear escalation ownership",
                "- Resource/support required: Light template, manager prompts, and meeting rhythm",
                "",
            ]
        )
    return "\n".join(lines)


def markdown_decision_record(weights: pd.DataFrame, ranked: pd.DataFrame, comments: list[dict]) -> str:
    lines = ["# Decision Record and Logic", "", "## Selected criteria"]
    for _, row in weights.iterrows():
        lines.append(f"- {row['criterion_name']}: {row['weight']:.0%} weight, spread {row['spread']:.2f}")
    lines.extend(["", "## Candidate action ranking"])
    for _, row in ranked.iterrows():
        lines.append(
            f"- {row['action_title']}: {row['weighted_score']} / 5 ({row['percentage_equivalent']}%), status {row['decision_status']}"
        )
    lines.extend(["", "## Group comments"])
    visible_comments = [comment for comment in comments if comment.get("display_publicly")]
    if visible_comments:
        lines.extend([f"- {comment['comment_text']}" for comment in visible_comments])
    else:
        lines.append("- No public group comments recorded.")
    lines.extend(["", "## Notes on process", "The ranking is advisory. Final statuses were assigned by the facilitator/group."])
    return "\n".join(lines)


def markdown_resource_kit() -> str:
    return "\n".join(
        [
            "# Resource Kit Outline",
            "",
            "- Workload visibility check-in template",
            "- Team discussion prompts using Notice -> Name -> Discuss -> Prioritise -> Resolve -> Review",
            "- Manager/team lead workload conversation prompts",
            "- Cross-team request intake template",
            "- Escalation pathway components and response expectations",
            "- Prioritisation conversation guide",
            "- Review routine for adopted actions and unresolved issues",
            "- Implementation support needs and owner map",
        ]
    )


def build_prompt(title: str, artefact: str, session_payload: str) -> str:
    return f"""You are helping draft a polished {title} for ITaLI after a Pulse action sprint.

Use the structured meeting data below. Keep the tone practical, evidence-informed, and suitable for university staff. Do not invent decisions that are not supported by the data.

Requested artefact:
{artefact}

Structured meeting data:
{session_payload}
"""
