from __future__ import annotations

from datetime import datetime
from uuid import uuid4


DECISION_STATUSES = ["adopt", "refine", "combine", "park", "escalate", "undecided"]
VISIBILITY_STATUSES = ["raw", "hidden", "public_summary", "promoted"]

DEFAULT_CRITERIA = [
    {
        "criterion_id": "practical_impact",
        "criterion_name": "Practical impact",
        "description": "Likely to make workload monitoring and resolution better in everyday work.",
        "selected_for_pairwise": True,
    },
    {
        "criterion_id": "feasibility",
        "criterion_name": "Feasibility",
        "description": "Can be started with realistic effort, resources, and authority.",
        "selected_for_pairwise": True,
    },
    {
        "criterion_id": "clarity",
        "criterion_name": "Clarity",
        "description": "Makes responsibilities, decisions, and next steps easier to understand.",
        "selected_for_pairwise": True,
    },
    {
        "criterion_id": "fairness_consistency",
        "criterion_name": "Fairness and consistency",
        "description": "Helps similar workload issues be handled in similar ways across teams.",
        "selected_for_pairwise": False,
    },
    {
        "criterion_id": "psychological_safety",
        "criterion_name": "Psychological safety",
        "description": "Makes it safer to raise workload pressure and unacceptable behaviour concerns early.",
        "selected_for_pairwise": False,
    },
    {
        "criterion_id": "sustainability",
        "criterion_name": "Sustainability",
        "description": "Can be maintained without adding avoidable overhead.",
        "selected_for_pairwise": False,
    },
    {
        "criterion_id": "ownership",
        "criterion_name": "Ownership",
        "description": "Has a clear owner area and review point.",
        "selected_for_pairwise": False,
    },
]

DEFAULT_SLIDES = [
    {
        "title": "Where we are now",
        "body": [
            "ITaLI's overall Pulse result declined from 74% in 2025 to 72% in 2026, while remaining slightly above the UQ-wide result of 71%.",
            "The issue is not only the overall score, but the pattern of improvement and decline.",
        ],
        "notes": "Frame the session as evidence-informed and practical, not a retrospective blame exercise.",
    },
    {
        "title": "What remains strong",
        "body": [
            "Staff report strong support from direct supervisors.",
            "Supervisor feedback remains strong.",
            "Staff understand how their work contributes to UQ's strategic goals.",
            "ITaLI continues to show strengths in social responsibility and RAP-related sentiment.",
        ],
        "notes": "Name strengths before concerns so the group can build from what is working.",
    },
    {
        "title": "Where the concern is concentrated",
        "body": [
            "Lower or declining areas include workload manageability, local and university-level change, career development and learning access, role clarity, and confidence that unacceptable behaviours are addressed.",
        ],
        "notes": "Keep this as a pattern statement. Detailed analysis belongs after the meeting.",
    },
    {
        "title": "What we have learned so far",
        "body": [
            "The earlier draft action plan was too complicated for practical co-design.",
            "The attempt to use strengths to address weaknesses was analytically useful but not simple enough as a meeting frame.",
            "The next version should be more focused, practical, and easier for staff to help shape.",
        ],
        "notes": "This explains why today's session uses a simpler action sprint format.",
    },
    {
        "title": "Why workload monitoring and resolution is the focus",
        "body": [
            "Workload appears to connect multiple Pulse concerns: role clarity, change impact, cross-team requests, prioritisation, development time, escalation, and psychological safety in raising concerns.",
            "The focus is not simply 'too much work'; it is how ITaLI notices, names, discusses, prioritises, resolves, and reviews workload pressure.",
        ],
        "notes": "Introduce the spine: Notice -> Name -> Discuss -> Prioritise -> Resolve -> Review.",
    },
    {
        "title": "What today's session is asking staff to do",
        "body": [
            "Identify where workload pressure, role ambiguity, or cross-team friction shows up.",
            "Propose practical actions or ways of working.",
            "Help decide which actions should be prioritised.",
            "Contribute to an action plan brief, decision record, and resource kit outline.",
        ],
        "notes": "End with clear agency: staff are shaping the next practical action plan.",
    },
]


def new_id(prefix: str) -> str:
    return f"{prefix}{uuid4().hex[:8].upper()}"


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()
