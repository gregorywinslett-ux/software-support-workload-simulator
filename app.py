import io
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Software Support Scenario Simulator",
    layout="wide",
)


ROLES = ["Advisor", "Helpdesk", "Specialist", "Project Manager", "Manager"]
ROLE_TOTAL_COLUMNS = {
    "Advisor": "advisor_hours_total",
    "Helpdesk": "helpdesk_hours_total",
    "Specialist": "specialist_hours_total",
    "Project Manager": "pm_hours_total",
    "Manager": "manager_hours_total",
}
ROLE_UNIT_COLUMNS = {
    "Advisor": "advisor_hours_per_unit",
    "Helpdesk": "helpdesk_hours_per_unit",
    "Specialist": "specialist_hours_per_unit",
    "Project Manager": "pm_hours_per_unit",
    "Manager": "manager_hours_per_unit",
}
CALCULATED_ROLE_COLUMNS = {
    "Advisor": "calculated_advisor_hours",
    "Helpdesk": "calculated_helpdesk_hours",
    "Specialist": "calculated_specialist_hours",
    "Project Manager": "calculated_pm_hours",
    "Manager": "calculated_manager_hours",
}

SUPPORT_STATUSES = [
    "Supported",
    "Pilot",
    "Project",
    "Proposed",
    "Retiring",
    "Retired",
    "On hold",
]
SUPPORT_LEVELS = ["Full", "Standard", "Light", "Advisory only", "No support"]
SUPPORT_LEVEL_MULTIPLIERS = {
    "Full": 1.00,
    "Standard": 0.75,
    "Light": 0.50,
    "Advisory only": 0.25,
    "No support": 0.00,
}
CRITICALITY_LEVELS = ["Low", "Medium", "High", "Critical"]
ADOPTION_LEVELS = ["Low", "Medium", "High", "Very high"]
COMPLEXITY_LEVELS = ["Low", "Medium", "High"]
WORK_GROUPS = ["BAU", "Project", "Change", "Scenario", "On hold"]
CONFIDENCE_LEVELS = ["Low", "Medium", "High"]
SCENARIO_TYPES = [
    "Introduce software",
    "Remove software",
    "Consolidate software",
    "Reduce support level",
    "Increase adoption",
    "Decommission tool",
    "Project to BAU",
    "Demand spike",
    "Capacity change",
]
LIFECYCLE_PHASES = [
    "Discovery",
    "Pilot",
    "Implementation",
    "BAU support",
    "Major update",
    "Retirement",
    "Transition",
]
WORK_TYPES = [
    "Internal learning",
    "Team training",
    "User training",
    "Consultation",
    "Documentation",
    "Helpdesk support",
    "Vendor management",
    "Vendor issue resolution",
    "Internal configuration",
    "Integration support",
    "Accessibility review",
    "Procurement",
    "Legal/finance",
    "Contract management",
    "Communications",
    "Reporting",
    "Governance",
    "Project management",
    "Recurring BAU support",
    "Decommissioning",
    "Transition support",
    "Other",
]
PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]
PLANNING_UNITS = ["Monthly", "Weekly"]
DEFAULT_TEAM_PROFILE = {
    "team_name": "Software support team",
    "planning_start_month": "2026-01",
    "planning_end_month": "2026-12",
    "planning_unit": "Monthly",
    "standard_hours": 110.0,
}
WORK_TYPE_ROLE_ALLOCATION = {
    "Internal learning": {"Advisor": 0.6, "Specialist": 0.4},
    "Team training": {"Advisor": 0.7, "Specialist": 0.3},
    "User training": {"Advisor": 0.8, "Specialist": 0.2},
    "Consultation": {"Advisor": 0.85, "Specialist": 0.15},
    "Documentation": {"Advisor": 0.65, "Specialist": 0.25, "Manager": 0.1},
    "Helpdesk support": {"Helpdesk": 0.75, "Advisor": 0.15, "Specialist": 0.1},
    "Vendor management": {"Specialist": 0.55, "Manager": 0.25, "Advisor": 0.2},
    "Vendor issue resolution": {"Specialist": 0.65, "Helpdesk": 0.2, "Advisor": 0.15},
    "Internal configuration": {"Specialist": 0.75, "Advisor": 0.25},
    "Integration support": {"Specialist": 0.8, "Advisor": 0.2},
    "Accessibility review": {"Advisor": 0.55, "Specialist": 0.35, "Manager": 0.1},
    "Procurement": {"Advisor": 0.45, "Manager": 0.3, "Project Manager": 0.25},
    "Legal/finance": {"Manager": 0.5, "Project Manager": 0.3, "Advisor": 0.2},
    "Contract management": {"Manager": 0.45, "Advisor": 0.35, "Project Manager": 0.2},
    "Communications": {"Advisor": 0.65, "Project Manager": 0.25, "Manager": 0.1},
    "Reporting": {"Advisor": 0.55, "Manager": 0.25, "Specialist": 0.2},
    "Governance": {"Manager": 0.55, "Advisor": 0.25, "Project Manager": 0.2},
    "Project management": {"Project Manager": 0.8, "Manager": 0.2},
    "Recurring BAU support": {"Helpdesk": 0.45, "Advisor": 0.35, "Specialist": 0.2},
    "Decommissioning": {"Specialist": 0.45, "Project Manager": 0.35, "Advisor": 0.2},
    "Transition support": {"Advisor": 0.45, "Specialist": 0.3, "Project Manager": 0.25},
    "Other": {"Advisor": 1.0},
}

ADOPTION_MULTIPLIERS = {
    "Low": 0.80,
    "Medium": 1.00,
    "High": 1.25,
    "Very high": 1.50,
}
COMPLEXITY_MULTIPLIERS = {
    "Low": 0.85,
    "Medium": 1.00,
    "High": 1.35,
}
REMOVAL_FACTORS = {
    "immediate removal": 0.00,
    "phased removal": 0.35,
    "retire with transition support": 0.15,
}
CONSOLIDATION_FACTORS = {
    "light": {"retained_load": 0.75, "transition_multiplier": 0.75},
    "moderate": {"retained_load": 0.55, "transition_multiplier": 1.00},
    "complex": {"retained_load": 0.40, "transition_multiplier": 1.40},
}
ADOPTION_SENSITIVE_WORK_TYPES = [
    "User training",
    "Consultation",
    "Documentation",
    "Helpdesk support",
    "Internal configuration",
    "Recurring BAU support",
]

TEAM_CAPACITY_REQUIRED_COLUMNS = [
    "role",
    "fte",
    "usable_hours_per_fte_per_year",
    "available_hours_year",
    "notes",
]
SUPPORTED_SOFTWARE_REQUIRED_COLUMNS = [
    "software_id",
    "software_name",
    "support_status",
    "support_level",
    "criticality",
    "adoption_level",
    "vendor_complexity",
    "configuration_complexity",
    "integration_complexity",
    "primary_audience",
    "notes",
]
BASELINE_WORKLOAD_REQUIRED_COLUMNS = [
    "workload_id",
    "software_id",
    "software_name",
    "work_type",
    "work_group",
    "annual_volume",
    "advisor_hours_per_unit",
    "helpdesk_hours_per_unit",
    "specialist_hours_per_unit",
    "pm_hours_per_unit",
    "manager_hours_per_unit",
    "advisor_hours_total",
    "helpdesk_hours_total",
    "specialist_hours_total",
    "pm_hours_total",
    "manager_hours_total",
    "confidence",
    "notes",
]
SCENARIO_TEMPLATE_REQUIRED_COLUMNS = [
    "template_id",
    "scenario_type",
    "lifecycle_phase",
    "work_type",
    "task_name",
    "default_annual_volume",
    "advisor_hours_per_unit",
    "helpdesk_hours_per_unit",
    "specialist_hours_per_unit",
    "pm_hours_per_unit",
    "manager_hours_per_unit",
    "default_confidence",
    "notes",
]
TASK_TIME_TEMPLATE_REQUIRED_COLUMNS = [
    "template_id",
    "category",
    "task_name",
    "default_hours",
    "suggested_work_type",
    "default_priority",
    "default_confidence",
    "description",
    "source_label",
]
TASK_TIME_SUBTASK_REQUIRED_COLUMNS = [
    "template_id",
    "subtask_name",
    "subtask_hours",
]
CANONICAL_MODEL_TABLES = [
    "team_profile",
    "team_capacity",
    "people_availability",
    "assigned_work_items",
    "monthly_workload",
    "software_portfolio",
    "baseline_workload",
    "scenario_adjustments",
]
AI_INTERPRETATION_INSTRUCTIONS = """
You are an AI interpretation assistant for a team-level software support workload planning tool.

Your role is to help leaders reflect on workload, capacity, uncertainty, and scenario impacts. You do not make decisions. You do not evaluate individual staff performance. You do not present estimates as objective truth.

Use cautious, plain-English language. Treat all data as approximate and assumption-based. Focus on patterns, risks, questions, and possible mitigations for leadership discussion.

Do not infer personal details, staff capability, motivation, productivity, or performance. Do not recommend disciplinary action or individual performance management. Do not identify any person as a problem.

If the data is incomplete, uncertain, or contradictory, say so clearly. Prefer phrases such as "may suggest", "could indicate", "worth checking", and "a useful leadership question is".

Your output should include:
1. Brief summary
2. Key workload observations
3. Capacity and risk signals
4. Uncertainty and data quality cautions
5. Leadership questions
6. Possible mitigations to consider
7. Clear reminder that humans make the decisions

Keep the tone calm, practical, and non-alarmist.
""".strip()

AI_DECISION_MATRIX_INSTRUCTIONS = """
You are an AI interpretation assistant for a non-AI scenario decision matrix.

The matrix scores are calculated by the application using human-entered favourability scores and human-entered weights. Do not recalculate the scores. Do not decide which scenario should be chosen. Do not present the ranking as objectively correct.

Use only the summarised comparison object provided. Do not infer facts that are not present. Do not evaluate staff performance, individual capability, motivation, productivity, or conduct. Do not ask for or refer to API keys, secrets, raw uploaded files, staff names, or sensitive notes.

Your output must include:
1. Three cautious observations
2. Three risks or watch-points
3. Three leadership questions
4. Two possible mitigation or next-step options
5. One short senior-summary paragraph
6. One "what not to conclude from this comparison" note

Use cautious language such as "may suggest", "could indicate", "worth testing", and "based on the entered assumptions". Keep the tone calm, practical, and non-authoritative.
""".strip()

DECISION_SCENARIO_TYPES = [
    "Keep current portfolio",
    "Remove platform",
    "Introduce new tool at light support",
    "Introduce new tool at full support",
    "Consolidate tools",
    "Delay implementation",
    "Reduce support level",
    "Other",
]
DECISION_CRITERIA_DEFAULTS = [
    {
        "criterion": "Workload impact",
        "enabled": True,
        "weight_pct": 30.0,
        "favourability_guidance": "5 = manageable workload impact / highly favourable",
    },
    {
        "criterion": "Strategic value",
        "enabled": True,
        "weight_pct": 25.0,
        "favourability_guidance": "5 = strong strategic value / highly favourable",
    },
    {
        "criterion": "Risk",
        "enabled": True,
        "weight_pct": 20.0,
        "favourability_guidance": "5 = low risk / highly favourable",
    },
    {
        "criterion": "Cost",
        "enabled": True,
        "weight_pct": 10.0,
        "favourability_guidance": "5 = low cost / highly favourable",
    },
    {
        "criterion": "Complexity",
        "enabled": False,
        "weight_pct": 0.0,
        "favourability_guidance": "5 = low complexity / highly favourable",
    },
    {
        "criterion": "Student/staff benefit",
        "enabled": True,
        "weight_pct": 15.0,
        "favourability_guidance": "5 = strong student/staff benefit / highly favourable",
    },
    {
        "criterion": "Confidence in estimates",
        "enabled": False,
        "weight_pct": 0.0,
        "favourability_guidance": "5 = high confidence / highly favourable",
    },
    {
        "criterion": "Implementation effort",
        "enabled": False,
        "weight_pct": 0.0,
        "favourability_guidance": "5 = low implementation effort / highly favourable",
    },
    {
        "criterion": "Recurring BAU burden",
        "enabled": False,
        "weight_pct": 0.0,
        "favourability_guidance": "5 = low recurring BAU burden / highly favourable",
    },
    {
        "criterion": "Opportunity cost",
        "enabled": False,
        "weight_pct": 0.0,
        "favourability_guidance": "5 = low opportunity cost / highly favourable",
    },
]
DECISION_SCENARIO_COLUMNS = [
    "scenario_name",
    "short_description",
    "scenario_type",
    "expected_workload_impact",
    "implementation_effort",
    "recurring_bau_burden",
    "risk_level",
    "confidence_level",
    "notes",
]
DECISION_PROMPTS = [
    "What result surprised the group?",
    "Which criterion is driving the ranking most strongly?",
    "Would the result change if workload impact or strategic value were weighted differently?",
    "Are any criteria prerequisites rather than preferences?",
    "Is the preferred scenario feasible within the current planning period?",
    "What would need to be true for the preferred scenario to be safe to proceed?",
]


def load_sample_team_capacity():
    return pd.read_csv("sample_data/sample_team_capacity.csv")


def load_sample_supported_software():
    return pd.read_csv("sample_data/sample_supported_software.csv")


def load_sample_baseline_workload():
    return pd.read_csv("sample_data/sample_baseline_workload.csv")


def load_sample_scenario_task_templates():
    return pd.read_csv("sample_data/sample_scenario_task_templates.csv")


def load_task_time_templates():
    return pd.read_csv("sample_data/task_time_templates.csv")


def load_task_time_subtasks():
    return pd.read_csv("sample_data/task_time_subtasks.csv")


def load_task_estimate_library():
    try:
        templates_df = load_task_time_templates()
        subtasks_df = load_task_time_subtasks()
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame(), [
            "Task estimate library files are missing. Manual work entry is still available."
        ]
    except Exception as error:
        return pd.DataFrame(), pd.DataFrame(), [
            f"Task estimate library could not be loaded: {error}"
        ]

    messages = []
    template_missing = [
        column
        for column in TASK_TIME_TEMPLATE_REQUIRED_COLUMNS
        if column not in templates_df.columns
    ]
    subtask_missing = [
        column
        for column in TASK_TIME_SUBTASK_REQUIRED_COLUMNS
        if column not in subtasks_df.columns
    ]
    if template_missing:
        messages.append(
            "Task estimate templates are missing these columns: "
            + ", ".join(template_missing)
            + ". Manual work entry is still available."
        )
        templates_df = pd.DataFrame(columns=TASK_TIME_TEMPLATE_REQUIRED_COLUMNS)
    if subtask_missing:
        messages.append(
            "Task estimate subtasks are missing these columns: "
            + ", ".join(subtask_missing)
            + ". Template subtasks will not be shown."
        )
        subtasks_df = pd.DataFrame(columns=TASK_TIME_SUBTASK_REQUIRED_COLUMNS)

    if not templates_df.empty:
        templates_df = prepare_task_time_templates(templates_df)
    if not subtasks_df.empty:
        subtasks_df = prepare_task_time_subtasks(subtasks_df)
    return templates_df, subtasks_df, messages


def read_uploaded_or_sample(uploaded_file, sample_loader):
    if uploaded_file is None:
        return sample_loader(), "sample data"
    return pd.read_csv(uploaded_file), uploaded_file.name


def validate_required_columns(df, required_columns, dataset_name):
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        st.error(
            f"{dataset_name} cannot be loaded yet. Please add these missing columns: "
            + ", ".join(missing_columns)
            + "."
        )
        st.caption(
            "Tip: compare your file with the matching sample CSV in this folder."
        )
        return False
    return True


def show_unknown_values(df, column, allowed_values, dataset_name):
    if column not in df.columns:
        return
    values = set(df[column].dropna().astype(str).str.strip())
    unknown = sorted(values - set(allowed_values))
    if unknown:
        st.warning(
            f"{dataset_name} has values in `{column}` that the simulator does not recognise yet: "
            + ", ".join(unknown)
        )


def validate_team_capacity(df):
    valid = validate_required_columns(
        df, TEAM_CAPACITY_REQUIRED_COLUMNS, "Team capacity"
    )
    if not valid:
        return False
    show_unknown_values(df, "role", ROLES, "Team capacity")
    numeric_df = clean_numeric_columns(
        df, ["fte", "usable_hours_per_fte_per_year", "available_hours_year"]
    )
    valid = True
    if (numeric_df["fte"] <= 0).any():
        st.error("Team capacity needs a positive FTE value for every row.")
        valid = False
    if (numeric_df["usable_hours_per_fte_per_year"] < 0).any():
        st.error("Usable hours per FTE cannot be negative.")
        valid = False
    if (numeric_df["available_hours_year"] < 0).any():
        st.error("Available hours cannot be negative.")
        valid = False
    return valid


def validate_supported_software(df):
    valid = validate_required_columns(
        df, SUPPORTED_SOFTWARE_REQUIRED_COLUMNS, "Supported software"
    )
    if not valid:
        return False
    show_unknown_values(df, "support_status", SUPPORT_STATUSES, "Supported software")
    show_unknown_values(df, "support_level", SUPPORT_LEVELS, "Supported software")
    show_unknown_values(df, "criticality", CRITICALITY_LEVELS, "Supported software")
    show_unknown_values(df, "adoption_level", ADOPTION_LEVELS, "Supported software")
    show_unknown_values(df, "vendor_complexity", COMPLEXITY_LEVELS, "Supported software")
    show_unknown_values(
        df, "configuration_complexity", COMPLEXITY_LEVELS, "Supported software"
    )
    show_unknown_values(
        df, "integration_complexity", COMPLEXITY_LEVELS, "Supported software"
    )
    return True


def validate_baseline_workload(df):
    valid = validate_required_columns(
        df, BASELINE_WORKLOAD_REQUIRED_COLUMNS, "Baseline workload"
    )
    if not valid:
        return False
    show_unknown_values(df, "work_type", WORK_TYPES, "Baseline workload")
    show_unknown_values(df, "work_group", WORK_GROUPS, "Baseline workload")
    show_unknown_values(df, "confidence", CONFIDENCE_LEVELS, "Baseline workload")
    numeric_columns = [
        "annual_volume",
        "advisor_hours_per_unit",
        "helpdesk_hours_per_unit",
        "specialist_hours_per_unit",
        "pm_hours_per_unit",
        "manager_hours_per_unit",
        "advisor_hours_total",
        "helpdesk_hours_total",
        "specialist_hours_total",
        "pm_hours_total",
        "manager_hours_total",
    ]
    numeric_df = clean_numeric_columns(df, numeric_columns)
    if (numeric_df[numeric_columns] < 0).any().any():
        st.error("Baseline workload hours and volumes cannot be negative.")
        return False
    if numeric_df[numeric_columns].sum(axis=1).eq(0).any():
        st.warning(
            "Some workload rows have no volume or hours. They will appear as zero-hour work."
        )
    return True


def validate_scenario_task_templates(df):
    valid = validate_required_columns(
        df, SCENARIO_TEMPLATE_REQUIRED_COLUMNS, "Scenario task templates"
    )
    if not valid:
        return False
    show_unknown_values(df, "scenario_type", SCENARIO_TYPES, "Scenario task templates")
    show_unknown_values(df, "lifecycle_phase", LIFECYCLE_PHASES, "Scenario task templates")
    show_unknown_values(df, "work_type", WORK_TYPES, "Scenario task templates")
    show_unknown_values(
        df, "default_confidence", CONFIDENCE_LEVELS, "Scenario task templates"
    )
    return True


def clean_text_columns(df, columns, defaults=None):
    cleaned_df = df.copy()
    defaults = defaults or {}
    for column in columns:
        cleaned_df[column] = cleaned_df[column].fillna("").astype(str).str.strip()
        if column in defaults:
            cleaned_df[column] = cleaned_df[column].replace("", defaults[column])
    return cleaned_df


def clean_numeric_columns(df, columns):
    cleaned_df = df.copy()
    for column in columns:
        cleaned_df[column] = (
            pd.to_numeric(cleaned_df[column], errors="coerce").fillna(0).astype(float)
        )
    return cleaned_df


def prepare_team_capacity(df):
    prepared_df = clean_text_columns(df, ["role", "notes"])
    prepared_df = clean_numeric_columns(
        prepared_df, ["fte", "usable_hours_per_fte_per_year", "available_hours_year"]
    )
    prepared_df["usable_hours_per_fte_per_year"] = prepared_df[
        "usable_hours_per_fte_per_year"
    ].replace(0, 1320)
    missing_capacity = prepared_df["available_hours_year"] <= 0
    prepared_df.loc[missing_capacity, "available_hours_year"] = (
        prepared_df.loc[missing_capacity, "fte"]
        * prepared_df.loc[missing_capacity, "usable_hours_per_fte_per_year"]
    )
    return prepared_df


def prepare_supported_software(df):
    return clean_text_columns(
        df,
        SUPPORTED_SOFTWARE_REQUIRED_COLUMNS,
        {
            "support_status": "Supported",
            "support_level": "Standard",
            "criticality": "Medium",
            "adoption_level": "Medium",
            "vendor_complexity": "Medium",
            "configuration_complexity": "Medium",
            "integration_complexity": "Medium",
            "primary_audience": "Teaching staff",
        },
    )


def prepare_baseline_workload(df):
    text_columns = [
        "workload_id",
        "software_id",
        "software_name",
        "work_type",
        "work_group",
        "confidence",
        "notes",
    ]
    numeric_columns = [
        "annual_volume",
        "advisor_hours_per_unit",
        "helpdesk_hours_per_unit",
        "specialist_hours_per_unit",
        "pm_hours_per_unit",
        "manager_hours_per_unit",
        "advisor_hours_total",
        "helpdesk_hours_total",
        "specialist_hours_total",
        "pm_hours_total",
        "manager_hours_total",
    ]
    prepared_df = clean_text_columns(
        df,
        text_columns,
        {
            "software_name": "Unknown software",
            "work_type": "Other",
            "work_group": "BAU",
            "confidence": "Medium",
        },
    )
    prepared_df = clean_numeric_columns(prepared_df, numeric_columns)
    return calculate_workload_hours(prepared_df)


def prepare_scenario_task_templates(df):
    text_columns = [
        "template_id",
        "scenario_type",
        "lifecycle_phase",
        "work_type",
        "task_name",
        "default_confidence",
        "notes",
    ]
    numeric_columns = [
        "default_annual_volume",
        "advisor_hours_per_unit",
        "helpdesk_hours_per_unit",
        "specialist_hours_per_unit",
        "pm_hours_per_unit",
        "manager_hours_per_unit",
    ]
    prepared_df = clean_text_columns(
        df,
        text_columns,
        {
            "scenario_type": "Introduce software",
            "lifecycle_phase": "Implementation",
            "work_type": "Other",
            "default_confidence": "Medium",
        },
    )
    return clean_numeric_columns(prepared_df, numeric_columns)


def prepare_task_time_templates(df):
    text_columns = [
        "template_id",
        "category",
        "task_name",
        "suggested_work_type",
        "default_priority",
        "default_confidence",
        "description",
        "source_label",
    ]
    prepared_df = clean_text_columns(
        df,
        text_columns,
        {
            "category": "Uncategorised",
            "suggested_work_type": "Other",
            "default_priority": "Medium",
            "default_confidence": "Medium",
            "source_label": "Sanitised task time estimate library",
        },
    )
    prepared_df = clean_numeric_columns(prepared_df, ["default_hours"])
    prepared_df = prepared_df[prepared_df["default_hours"] > 0].copy()
    return prepared_df[TASK_TIME_TEMPLATE_REQUIRED_COLUMNS]


def prepare_task_time_subtasks(df):
    prepared_df = clean_text_columns(df, ["template_id", "subtask_name"])
    prepared_df = clean_numeric_columns(prepared_df, ["subtask_hours"])
    prepared_df = prepared_df[
        (prepared_df["template_id"] != "")
        & (prepared_df["subtask_name"] != "")
        & (prepared_df["subtask_hours"] >= 0)
    ].copy()
    return prepared_df[TASK_TIME_SUBTASK_REQUIRED_COLUMNS]


def parse_month_label(value):
    try:
        return pd.Period(str(value).strip(), freq="M")
    except (ValueError, TypeError):
        return None


def month_labels_between(start_month, end_month):
    if start_month is None or end_month is None or end_month < start_month:
        return []
    return [str(month) for month in pd.period_range(start_month, end_month, freq="M")]


def month_overlap(item_start, item_end, period_months):
    if item_start is None or item_end is None or item_end < item_start:
        return []
    return [
        month
        for month in period_months
        if item_start <= pd.Period(month, freq="M") <= item_end
    ]


def get_monthly_hours_per_fte(standard_hours, planning_unit):
    if planning_unit == "Weekly":
        return standard_hours * 52 / 12
    return standard_hours


def get_annual_hours_per_fte(standard_hours, planning_unit):
    if planning_unit == "Weekly":
        return standard_hours * 52
    return standard_hours * 12


def get_default_people_entries():
    return pd.DataFrame(
        [
            {
                "entry_label": "Advisor pool",
                "simulator_role": "Advisor",
                "employment_type": "Full-time",
                "fte": 2.0,
                "availability_pct": 80.0,
                "notes": "Use role labels or anonymised entries.",
            },
            {
                "entry_label": "Helpdesk pool",
                "simulator_role": "Helpdesk",
                "employment_type": "Full-time",
                "fte": 1.0,
                "availability_pct": 80.0,
                "notes": "",
            },
            {
                "entry_label": "Specialist pool",
                "simulator_role": "Specialist",
                "employment_type": "Part-time",
                "fte": 0.5,
                "availability_pct": 70.0,
                "notes": "",
            },
        ]
    )


def get_default_work_items():
    return pd.DataFrame(
        [
            {
                "work_title": "Recurring support tickets",
                "work_type": "Helpdesk support",
                "start_month": "2026-01",
                "end_month": "2026-12",
                "estimated_hours": 720.0,
                "priority": "High",
                "confidence": "Medium",
                "notes": "Shared support demand estimate.",
            },
            {
                "work_title": "Training and consultation",
                "work_type": "User training",
                "start_month": "2026-02",
                "end_month": "2026-11",
                "estimated_hours": 360.0,
                "priority": "Medium",
                "confidence": "Medium",
                "notes": "",
            },
        ]
    )


def reset_demo_data():
    st.session_state["builder_team_name"] = DEFAULT_TEAM_PROFILE["team_name"]
    st.session_state["builder_start_month"] = DEFAULT_TEAM_PROFILE[
        "planning_start_month"
    ]
    st.session_state["builder_end_month"] = DEFAULT_TEAM_PROFILE["planning_end_month"]
    st.session_state["builder_planning_unit"] = DEFAULT_TEAM_PROFILE["planning_unit"]
    st.session_state["builder_standard_hours"] = DEFAULT_TEAM_PROFILE["standard_hours"]
    st.session_state["builder_people_df"] = get_default_people_entries()
    st.session_state["builder_work_df"] = get_default_work_items()
    for key in [
        "baseline_signature",
        "scenario_df",
        "scenario_capacity_df",
        "scenario_name",
        "scenario_detail_df",
        "scenario_summary_df",
        "role_delta_df",
        "work_type_delta_df",
        "canonical_model",
        "task_estimate_library_status",
    ]:
        st.session_state.pop(key, None)


def validate_builder_inputs(profile, people_df, work_df):
    errors = []
    warnings = []
    start_month = parse_month_label(profile["planning_start_month"])
    end_month = parse_month_label(profile["planning_end_month"])
    period_months = month_labels_between(start_month, end_month)

    if not str(profile["team_name"]).strip():
        errors.append("Team name is required.")
    if start_month is None:
        errors.append("Planning start month must use YYYY-MM format.")
    if end_month is None:
        errors.append("Planning end month must use YYYY-MM format.")
    if start_month is not None and end_month is not None and end_month < start_month:
        errors.append("Planning end month must be the same as or after the start month.")
    if profile["standard_hours"] <= 0:
        errors.append("Standard hours assumption must be greater than zero.")

    people_df = people_df.fillna("")
    if people_df.empty:
        errors.append("Add at least one staff or role entry.")
    for row_number, row in enumerate(people_df.itertuples(index=False), start=1):
        if not str(row.entry_label).strip():
            errors.append(f"People row {row_number}: entry label is required.")
        if row.simulator_role not in ROLES:
            errors.append(f"People row {row_number}: choose a valid simulator role.")
        fte = to_float(row.fte)
        availability_pct = to_float(row.availability_pct)
        if fte <= 0:
            errors.append(f"People row {row_number}: FTE must be greater than zero.")
        if not 0 <= availability_pct <= 100:
            errors.append(
                f"People row {row_number}: availability percentage must be between 0 and 100."
            )

    work_df = work_df.fillna("")
    if work_df.empty:
        warnings.append("No assigned work items have been entered yet.")
    for row_number, row in enumerate(work_df.itertuples(index=False), start=1):
        item_start = parse_month_label(row.start_month)
        item_end = parse_month_label(row.end_month)
        if not str(row.work_title).strip():
            errors.append(f"Work row {row_number}: work title is required.")
        if row.work_type not in WORK_TYPES:
            errors.append(f"Work row {row_number}: choose a valid work type.")
        if item_start is None:
            errors.append(f"Work row {row_number}: start month must use YYYY-MM format.")
        if item_end is None:
            errors.append(f"Work row {row_number}: end month must use YYYY-MM format.")
        if item_start is not None and item_end is not None and item_end < item_start:
            errors.append(f"Work row {row_number}: end month must not be before start month.")
        if to_float(row.estimated_hours) <= 0:
            errors.append(f"Work row {row_number}: estimated hours must be greater than zero.")
        if row.priority not in PRIORITY_LEVELS:
            errors.append(f"Work row {row_number}: choose a valid priority.")
        if row.confidence not in CONFIDENCE_LEVELS:
            errors.append(f"Work row {row_number}: choose a valid confidence.")
        if period_months and item_start is not None and item_end is not None:
            if not month_overlap(item_start, item_end, period_months):
                warnings.append(
                    f"Work row {row_number}: no months overlap the planning period."
                )

    return errors, warnings, period_months


def to_float(value, default=0.0):
    if pd.isna(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def allocate_work_hours_by_role(work_type, total_hours):
    allocation = WORK_TYPE_ROLE_ALLOCATION.get(work_type, WORK_TYPE_ROLE_ALLOCATION["Other"])
    return {role: total_hours * allocation.get(role, 0) for role in ROLES}


def get_default_period_months():
    start_month = parse_month_label(DEFAULT_TEAM_PROFILE["planning_start_month"])
    end_month = parse_month_label(DEFAULT_TEAM_PROFILE["planning_end_month"])
    return month_labels_between(start_month, end_month)


def get_csv_team_profile(capacity_source="CSV or sample data"):
    profile = DEFAULT_TEAM_PROFILE.copy()
    profile["team_name"] = capacity_source
    profile["source"] = "csv_upload_or_sample"
    return profile


def build_people_availability_from_builder(people_df, profile):
    annual_hours_per_fte = get_annual_hours_per_fte(
        float(profile["standard_hours"]), profile["planning_unit"]
    )
    rows = []
    for row in people_df.fillna("").itertuples(index=False):
        effective_fte = to_float(row.fte) * to_float(row.availability_pct) / 100
        rows.append(
            {
                "entry_id": f"PERSON-{len(rows) + 1:03d}",
                "entry_label": str(row.entry_label).strip(),
                "role": str(row.simulator_role).strip(),
                "employment_type": str(row.employment_type).strip(),
                "raw_fte": to_float(row.fte),
                "availability_pct": to_float(row.availability_pct),
                "effective_fte": effective_fte,
                "available_hours_year": effective_fte * annual_hours_per_fte,
                "notes": str(row.notes).strip(),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "entry_id",
            "entry_label",
            "role",
            "employment_type",
            "raw_fte",
            "availability_pct",
            "effective_fte",
            "available_hours_year",
            "notes",
        ],
    )


def build_team_capacity_from_availability(availability_df, profile):
    annual_hours_per_fte = get_annual_hours_per_fte(
        float(profile["standard_hours"]), profile["planning_unit"]
    )
    if availability_df.empty:
        return pd.DataFrame(columns=TEAM_CAPACITY_REQUIRED_COLUMNS)

    capacity_df = (
        availability_df.groupby("role", as_index=False)
        .agg(
            fte=("effective_fte", "sum"),
            available_hours_year=("available_hours_year", "sum"),
            notes=("entry_label", lambda labels: "Built from: " + ", ".join(labels)),
        )
        .copy()
    )
    capacity_df["usable_hours_per_fte_per_year"] = annual_hours_per_fte
    return capacity_df[TEAM_CAPACITY_REQUIRED_COLUMNS]


def build_people_availability_from_capacity(capacity_df):
    rows = []
    for row in capacity_df.fillna("").itertuples(index=False):
        rows.append(
            {
                "entry_id": f"CAPACITY-{len(rows) + 1:03d}",
                "entry_label": str(row.role).strip(),
                "role": str(row.role).strip(),
                "employment_type": "Role capacity",
                "raw_fte": to_float(row.fte),
                "availability_pct": 100.0,
                "effective_fte": to_float(row.fte),
                "available_hours_year": to_float(row.available_hours_year),
                "notes": str(row.notes).strip(),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "entry_id",
            "entry_label",
            "role",
            "employment_type",
            "raw_fte",
            "availability_pct",
            "effective_fte",
            "available_hours_year",
            "notes",
        ],
    )


def build_assigned_work_items_from_builder(work_df, profile, period_months):
    rows = []
    for row in work_df.fillna("").itertuples(index=False):
        item_start = parse_month_label(row.start_month)
        item_end = parse_month_label(row.end_month)
        rows.append(
            {
                "work_item_id": f"WORK-{len(rows) + 1:03d}",
                "work_title": str(row.work_title).strip(),
                "work_type": str(row.work_type).strip(),
                "work_group": "BAU",
                "software_id": "GUIDED-BASELINE",
                "software_name": str(profile["team_name"]).strip() or "Guided baseline",
                "start_month": str(row.start_month).strip(),
                "end_month": str(row.end_month).strip(),
                "active_months": month_overlap(item_start, item_end, period_months),
                "estimated_hours": to_float(row.estimated_hours),
                "priority": str(row.priority).strip() or "Medium",
                "confidence": str(row.confidence).strip() or "Medium",
                "notes": str(row.notes).strip(),
                "source": "guided_baseline_builder",
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "work_item_id",
            "work_title",
            "work_type",
            "work_group",
            "software_id",
            "software_name",
            "start_month",
            "end_month",
            "active_months",
            "estimated_hours",
            "priority",
            "confidence",
            "notes",
            "source",
        ],
    )


def build_assigned_work_items_from_workload(workload_df, period_months):
    rows = []
    start_month = period_months[0] if period_months else ""
    end_month = period_months[-1] if period_months else ""
    for row in workload_df.fillna("").itertuples(index=False):
        rows.append(
            {
                "work_item_id": str(row.workload_id).strip(),
                "work_title": f"{row.software_name} - {row.work_type}",
                "work_type": str(row.work_type).strip(),
                "work_group": str(row.work_group).strip(),
                "software_id": str(row.software_id).strip(),
                "software_name": str(row.software_name).strip(),
                "start_month": start_month,
                "end_month": end_month,
                "active_months": period_months,
                "estimated_hours": to_float(row.calculated_total_hours),
                "priority": "Medium",
                "confidence": str(row.confidence).strip() or "Medium",
                "notes": str(row.notes).strip(),
                "source": "csv_upload_or_sample",
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "work_item_id",
            "work_title",
            "work_type",
            "work_group",
            "software_id",
            "software_name",
            "start_month",
            "end_month",
            "active_months",
            "estimated_hours",
            "priority",
            "confidence",
            "notes",
            "source",
        ],
    )


def build_baseline_workload_from_work_items(work_items_df):
    workload_rows = []
    for row in work_items_df.fillna("").itertuples(index=False):
        active_month_count = max(1, len(row.active_months))
        monthly_hours = to_float(row.estimated_hours) / active_month_count
        role_hours = allocate_work_hours_by_role(row.work_type, monthly_hours * 12)
        workload_rows.append(
            {
                "workload_id": row.work_item_id,
                "software_id": row.software_id,
                "software_name": row.software_name,
                "work_type": row.work_type,
                "work_group": row.work_group,
                "annual_volume": 1,
                "advisor_hours_per_unit": 0,
                "helpdesk_hours_per_unit": 0,
                "specialist_hours_per_unit": 0,
                "pm_hours_per_unit": 0,
                "manager_hours_per_unit": 0,
                "advisor_hours_total": role_hours["Advisor"],
                "helpdesk_hours_total": role_hours["Helpdesk"],
                "specialist_hours_total": role_hours["Specialist"],
                "pm_hours_total": role_hours["Project Manager"],
                "manager_hours_total": role_hours["Manager"],
                "confidence": row.confidence,
                "notes": (
                    f"{row.work_title}; priority={row.priority}; active={row.start_month}"
                    f" to {row.end_month}; estimated_hours={to_float(row.estimated_hours):.0f}. "
                    f"{row.notes}"
                ).strip(),
            }
        )
    workload_df = pd.DataFrame(workload_rows, columns=BASELINE_WORKLOAD_REQUIRED_COLUMNS)
    if workload_df.empty:
        workload_df = pd.DataFrame(columns=BASELINE_WORKLOAD_REQUIRED_COLUMNS)
    return prepare_baseline_workload(workload_df)


def calculate_monthly_workload(capacity_df, work_items_df, period_months):
    monthly_capacity = capacity_df["available_hours_year"].sum() / 12
    monthly_rows = []
    for month in period_months:
        assigned_hours = 0.0
        for row in work_items_df.itertuples(index=False):
            if month in row.active_months:
                assigned_hours += to_float(row.estimated_hours) / max(
                    1, len(row.active_months)
                )
        remaining_capacity = monthly_capacity - assigned_hours
        monthly_rows.append(
            {
                "month": month,
                "monthly_available_capacity": monthly_capacity,
                "monthly_assigned_workload": assigned_hours,
                "remaining_capacity": remaining_capacity,
                "over_capacity": remaining_capacity < 0,
            }
        )
    return pd.DataFrame(monthly_rows)


def build_review_summary(work_items_df, monthly_workload_df):
    high_priority_df = work_items_df[
        work_items_df["priority"].isin(["High", "Critical"])
    ].copy()
    low_confidence_df = work_items_df[work_items_df["confidence"] == "Low"].copy()
    return {
        "over_capacity_months": monthly_workload_df.loc[
            monthly_workload_df["over_capacity"], "month"
        ].tolist(),
        "high_priority_work_items": high_priority_df,
        "low_confidence_work_items": low_confidence_df,
    }


def build_planning_summary_markdown(canonical_model):
    profile = canonical_model["team_profile"]
    monthly_df = canonical_model["monthly_workload"]
    capacity_df = canonical_model["team_capacity"]
    work_items_df = canonical_model["assigned_work_items"]
    review_summary = canonical_model["review_summary"]
    scenario_adjustments_df = canonical_model["scenario_adjustments"]
    over_capacity_months = review_summary["over_capacity_months"]
    template_mask = work_items_df["notes"].fillna("").str.contains(
        "Task estimate library template", case=False, regex=False
    )
    template_item_count = int(template_mask.sum())
    template_hours = float(work_items_df.loc[template_mask, "estimated_hours"].sum())

    lines = [
        "# Software Support Workload Planning Summary",
        "",
        "## Appropriate Use",
        "",
        "This summary is a planning aid for team-level workload conversations. It is not an individual performance measurement system.",
        "",
        "## Team Profile",
        "",
        f"- Team: {profile.get('team_name', 'Not set')}",
        f"- Planning period: {profile.get('planning_start_month', '')} to {profile.get('planning_end_month', '')}",
        f"- Planning unit: {profile.get('planning_unit', 'Monthly')}",
        f"- Standard hours assumption: {profile.get('standard_hours', DEFAULT_TEAM_PROFILE['standard_hours'])}",
        f"- Data source: {canonical_model.get('source', 'unknown')}",
        "",
        "## Capacity and Workload",
        "",
        f"- Annual available capacity: {capacity_df['available_hours_year'].sum():,.0f} hours",
        f"- Assigned work items: {len(work_items_df):,}",
        f"- Work items from task estimate templates: {template_item_count:,}",
        f"- Estimated hours from task estimate templates: {template_hours:,.0f}",
        f"- Over-capacity months: {', '.join(over_capacity_months) if over_capacity_months else 'None'}",
        f"- High-priority work items: {len(review_summary['high_priority_work_items']):,}",
        f"- Low-confidence work items: {len(review_summary['low_confidence_work_items']):,}",
        "",
        "## Monthly Review",
        "",
        "| Month | Available capacity | Assigned workload | Remaining capacity | Over capacity |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in monthly_df.itertuples(index=False):
        lines.append(
            f"| {row.month} | {row.monthly_available_capacity:,.0f} | "
            f"{row.monthly_assigned_workload:,.0f} | {row.remaining_capacity:,.0f} | "
            f"{'Yes' if row.over_capacity else 'No'} |"
        )

    if not scenario_adjustments_df.empty:
        scenario = scenario_adjustments_df.iloc[0]
        lines.extend(
            [
                "",
                "## Active Scenario",
                "",
                f"- Scenario: {scenario['scenario_name']}",
                f"- Baseline hours: {scenario['baseline_total_hours']:,.0f}",
                f"- Scenario hours: {scenario['scenario_total_hours']:,.0f}",
                f"- Hours delta: {scenario['hours_delta']:,.0f}",
                f"- Percentage delta: {scenario['percentage_delta']:.1f}%",
            ]
        )

    lines.extend(
        [
            "",
            "## Assumptions",
            "",
            "- Capacity is calculated as FTE multiplied by availability percentage and standard hours.",
            "- Monthly workload is spread evenly across each work item's active month range.",
            "- Over-capacity is flagged when assigned workload exceeds available capacity in a month.",
            "- Scenario adjustments change workload or capacity according to the scenario builder assumptions.",
            "- Task estimate library items are sanitised planning estimates and should be reviewed for local context.",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def get_openai_secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def get_openai_api_key():
    return get_openai_secret("OPENAI_API_KEY", "")


def get_openai_model():
    return get_openai_secret("OPENAI_MODEL", "gpt-5")


def build_workload_summary_for_ai(work_items_df):
    if work_items_df.empty:
        return []

    rows = []
    for work_type, group_df in work_items_df.groupby("work_type"):
        priority_counts = group_df["priority"].value_counts().to_dict()
        rows.append(
            {
                "work_type": work_type,
                "assigned_hours": float(round(group_df["estimated_hours"].sum(), 1)),
                "priority_mix": {
                    "critical": int(priority_counts.get("Critical", 0)),
                    "high": int(priority_counts.get("High", 0)),
                    "medium": int(priority_counts.get("Medium", 0)),
                    "low": int(priority_counts.get("Low", 0)),
                },
                "low_confidence_count": int((group_df["confidence"] == "Low").sum()),
            }
        )
    return sorted(rows, key=lambda row: row["assigned_hours"], reverse=True)


def build_ai_summary_object(canonical_model, baseline_df, capacity_df):
    monthly_df = canonical_model.get("monthly_workload", pd.DataFrame())
    baseline_df = canonical_model.get("baseline_workload", baseline_df)
    capacity_df = canonical_model.get("team_capacity", capacity_df)
    work_items_df = canonical_model.get("assigned_work_items", pd.DataFrame())
    role_pressure_df = calculate_role_pressure(baseline_df, capacity_df)
    review_summary = canonical_model.get("review_summary", {})
    high_priority_df = review_summary.get("high_priority_work_items", pd.DataFrame())
    low_confidence_df = review_summary.get("low_confidence_work_items", pd.DataFrame())

    total_available = float(capacity_df["available_hours_year"].sum())
    total_assigned = float(baseline_df["calculated_total_hours"].sum())
    utilisation = total_assigned / total_available * 100 if total_available else 0
    template_mask = work_items_df["notes"].fillna("").str.contains(
        "Task estimate library template", case=False, regex=False
    )
    template_item_count = int(template_mask.sum())
    template_hours = float(work_items_df.loc[template_mask, "estimated_hours"].sum())

    summary = {
        "app_context": {
            "tool_name": "Software Support Workload Simulator",
            "purpose": "Team-level workload planning and scenario reflection",
            "important_limits": [
                "Planning aid only",
                "Not a performance management system",
                "Outputs are estimates based on user assumptions",
            ],
        },
        "team_profile": {
            "team_label": "Withheld - use generic role/team labels only",
            "planning_period_start": canonical_model.get("team_profile", {}).get(
                "planning_start_month", ""
            ),
            "planning_period_end": canonical_model.get("team_profile", {}).get(
                "planning_end_month", ""
            ),
            "planning_unit": canonical_model.get("team_profile", {}).get(
                "planning_unit", "Monthly"
            ),
            "standard_hours_assumption": canonical_model.get("team_profile", {}).get(
                "standard_hours", DEFAULT_TEAM_PROFILE["standard_hours"]
            ),
        },
        "baseline_summary": {
            "total_available_hours": round(total_available, 1),
            "total_assigned_hours": round(total_assigned, 1),
            "remaining_capacity_hours": round(total_available - total_assigned, 1),
            "utilisation_percent": round(utilisation, 1),
            "over_capacity_months": review_summary.get("over_capacity_months", []),
            "low_confidence_item_count": int(len(low_confidence_df)),
            "high_priority_item_count": int(len(high_priority_df)),
            "task_template_item_count": template_item_count,
            "task_template_estimated_hours": round(template_hours, 1),
        },
        "monthly_summary": [
            {
                "month": row.month,
                "available_capacity_hours": round(row.monthly_available_capacity, 1),
                "assigned_workload_hours": round(row.monthly_assigned_workload, 1),
                "remaining_capacity_hours": round(row.remaining_capacity, 1),
                "over_capacity": bool(row.over_capacity),
            }
            for row in monthly_df.itertuples(index=False)
        ],
        "role_summary": [
            {
                "role": row.role,
                "available_hours": round(row.available_hours, 1),
                "assigned_hours": round(row.committed_hours, 1),
                "remaining_hours": round(row.remaining_capacity, 1),
                "utilisation_percent": round(row.utilisation_pct, 1),
                "status": row.overload_status,
            }
            for row in role_pressure_df.itertuples(index=False)
        ],
        "workload_summary": build_workload_summary_for_ai(work_items_df),
        "scenario_summary": None,
        "scenario_role_deltas": [],
        "scenario_work_type_deltas": [],
        "known_uncertainties": [
            "Some estimates may be low confidence",
            "Workload is spread evenly across active months",
            "Role allocation uses simplified assumptions",
            "The summary excludes staff names, free-text notes, raw uploaded files, and raw work rows",
        ],
        "excluded_data_notice": {
            "individual_names_sent": False,
            "sensitive_notes_sent": False,
            "raw_uploaded_files_sent": False,
            "free_text_notes_sent": False,
            "raw_work_item_titles_sent": False,
            "software_names_sent": False,
        },
    }

    scenario_summary_df = st.session_state.get("scenario_summary_df", pd.DataFrame())
    role_delta_df = st.session_state.get("role_delta_df", pd.DataFrame())
    work_type_delta_df = st.session_state.get("work_type_delta_df", pd.DataFrame())
    scenario_name = st.session_state.get("scenario_name", "No scenario built")

    if not scenario_summary_df.empty:
        scenario = scenario_summary_df.iloc[0]
        summary["scenario_summary"] = {
            "scenario_name": scenario_name,
            "baseline_total_hours": round(scenario["baseline_total_hours"], 1),
            "scenario_total_hours": round(scenario["scenario_total_hours"], 1),
            "hours_delta": round(scenario["hours_delta"], 1),
            "percentage_delta": round(scenario["percentage_delta"], 1),
            "roles_over_capacity": int(scenario["roles_over_capacity"]),
            "low_confidence_assumptions": int(scenario["low_confidence_assumptions"]),
            "uncertainty_flag": bool(scenario["uncertainty_flag"]),
        }

    if not role_delta_df.empty:
        summary["scenario_role_deltas"] = [
            {
                "role": row.role,
                "baseline_assigned_hours": round(row.committed_hours_baseline, 1),
                "scenario_assigned_hours": round(row.committed_hours_scenario, 1),
                "hours_delta": round(row.role_hours_delta, 1),
                "revised_utilisation_percent": round(row.revised_utilisation_pct, 1),
                "revised_status": row.revised_overload_status,
            }
            for row in role_delta_df.itertuples(index=False)
        ]

    if not work_type_delta_df.empty:
        changed_df = work_type_delta_df[
            work_type_delta_df["work_type_hours_delta"].abs() > 0
        ].copy()
        summary["scenario_work_type_deltas"] = [
            {
                "work_type": row.work_type,
                "hours_delta": round(row.work_type_hours_delta, 1),
            }
            for row in changed_df.head(12).itertuples(index=False)
        ]

    return summary


def validate_ai_summary(ai_summary):
    if not ai_summary:
        return False, "There is no workload summary available yet."
    if not ai_summary.get("monthly_summary"):
        return False, "Complete the baseline review before using AI interpretation."
    if not ai_summary.get("role_summary"):
        return False, "Role capacity data is missing, so the AI summary is incomplete."
    if ai_summary["baseline_summary"]["total_available_hours"] <= 0:
        return False, "Available capacity is zero, so there is not enough information to interpret."
    return True, ""


def build_ai_user_prompt(ai_summary):
    summary_json = json.dumps(ai_summary, indent=2)
    return (
        "Interpret the following workload planning summary.\n\n"
        "Use only the provided summary. Do not assume facts that are not present. "
        "Do not evaluate individual staff. Do not make final decisions.\n\n"
        "Return cautious leadership observations, risks, questions, and possible mitigations.\n\n"
        f"Workload summary:\n{summary_json}"
    )


def generate_ai_interpretation(ai_summary, api_key, model):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        reasoning={"effort": "low"},
        max_output_tokens=1400,
        input=[
            {
                "role": "developer",
                "content": AI_INTERPRETATION_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": build_ai_user_prompt(ai_summary),
            },
        ],
    )
    return response.output_text


def build_ai_interpretation_markdown(ai_text, ai_summary):
    scenario_name = "No scenario built"
    if ai_summary.get("scenario_summary"):
        scenario_name = ai_summary["scenario_summary"]["scenario_name"]
    lines = [
        "# AI-Assisted Workload Interpretation",
        "",
        "> Planning aid only. This output is not a decision, forecast, or performance assessment.",
        "",
        f"- Scenario: {scenario_name}",
        f"- Data sent excludes individual names, free-text notes, raw uploaded files, raw work item titles, and software names.",
        "",
        ai_text,
    ]
    return "\n".join(lines).encode("utf-8")


def get_default_decision_scenarios():
    return pd.DataFrame(
        [
            {
                "scenario_name": "Keep current portfolio",
                "short_description": "Continue with the current supported software mix.",
                "scenario_type": "Keep current portfolio",
                "expected_workload_impact": "Baseline workload remains largely unchanged.",
                "implementation_effort": "Low",
                "recurring_bau_burden": "Moderate",
                "risk_level": "Low",
                "confidence_level": "Medium",
                "notes": "Use as the comparison baseline.",
            },
            {
                "scenario_name": "Introduce new tool - light support",
                "short_description": "Add a new tool with advisory or light support.",
                "scenario_type": "Introduce new tool at light support",
                "expected_workload_impact": "Adds implementation and some recurring support work.",
                "implementation_effort": "Medium",
                "recurring_bau_burden": "Low",
                "risk_level": "Medium",
                "confidence_level": "Low",
                "notes": "Adjust using the Scenario Impact tab if an estimate is available.",
            },
            {
                "scenario_name": "Reduce support level",
                "short_description": "Reduce support intensity for a lower-value or mature platform.",
                "scenario_type": "Reduce support level",
                "expected_workload_impact": "May reduce recurring workload but could shift demand elsewhere.",
                "implementation_effort": "Low",
                "recurring_bau_burden": "Low",
                "risk_level": "Medium",
                "confidence_level": "Medium",
                "notes": "Check stakeholder impact before treating savings as certain.",
            },
        ],
        columns=DECISION_SCENARIO_COLUMNS,
    )


def get_default_decision_criteria():
    return pd.DataFrame(DECISION_CRITERIA_DEFAULTS)


def get_active_decision_criteria(criteria_df):
    if criteria_df.empty:
        return pd.DataFrame(columns=["criterion", "enabled", "weight_pct"])
    active_df = criteria_df[criteria_df["enabled"] == True].copy()
    active_df["weight_pct"] = active_df["weight_pct"].apply(to_float)
    return active_df


def get_default_decision_scores(scenarios_df, criteria_df):
    active_criteria = get_active_decision_criteria(criteria_df)["criterion"].tolist()
    rows = []
    for scenario_name in scenarios_df["scenario_name"].fillna("").tolist():
        row = {"scenario_name": scenario_name}
        for criterion in active_criteria:
            row[criterion] = 3
        rows.append(row)
    return pd.DataFrame(rows)


def align_decision_scores(scores_df, scenarios_df, criteria_df):
    active_criteria = get_active_decision_criteria(criteria_df)["criterion"].tolist()
    desired_columns = ["scenario_name"] + active_criteria
    existing_scores = {}
    if not scores_df.empty and "scenario_name" in scores_df.columns:
        for row in scores_df.fillna("").to_dict("records"):
            existing_scores[str(row.get("scenario_name", ""))] = row

    rows = []
    for scenario_name in scenarios_df["scenario_name"].fillna("").tolist():
        clean_name = str(scenario_name).strip()
        if not clean_name:
            continue
        existing = existing_scores.get(clean_name, {})
        row = {"scenario_name": clean_name}
        for criterion in active_criteria:
            row[criterion] = int(to_float(existing.get(criterion, 3), 3))
        rows.append(row)
    return pd.DataFrame(rows, columns=desired_columns)


def normalise_decision_weights(criteria_df):
    normalised_df = criteria_df.copy()
    active_mask = normalised_df["enabled"] == True
    active_total = normalised_df.loc[active_mask, "weight_pct"].apply(to_float).sum()
    if active_total <= 0:
        active_count = int(active_mask.sum())
        if active_count:
            normalised_df.loc[active_mask, "weight_pct"] = round(100 / active_count, 1)
    else:
        normalised_df.loc[active_mask, "weight_pct"] = (
            normalised_df.loc[active_mask, "weight_pct"].apply(to_float)
            / active_total
            * 100
        ).round(1)
    normalised_df.loc[~active_mask, "weight_pct"] = 0.0
    return normalised_df


def validate_decision_matrix_inputs(decision_question, scenarios_df, criteria_df, scores_df):
    errors = []
    warnings = []
    if not str(decision_question).strip():
        errors.append("Add a decision question before relying on the comparison.")
    if scenarios_df.empty or len(scenarios_df) < 2:
        errors.append("Add at least two scenarios to compare.")
    else:
        blank_names = scenarios_df["scenario_name"].fillna("").astype(str).str.strip() == ""
        if blank_names.any():
            errors.append("Each scenario needs a scenario name.")
    active_criteria = get_active_decision_criteria(criteria_df)
    if active_criteria.empty:
        errors.append("Enable at least one decision criterion.")
    weight_total = active_criteria["weight_pct"].sum() if not active_criteria.empty else 0
    if active_criteria.empty or abs(weight_total - 100) > 0.05:
        warnings.append(
            f"Active criteria weights currently total {weight_total:.1f}%. Aim for 100%."
        )
    if not scores_df.empty:
        for criterion in active_criteria["criterion"].tolist():
            invalid_scores = ~scores_df[criterion].apply(lambda value: 1 <= to_float(value) <= 5)
            if invalid_scores.any():
                errors.append(f"Scores for {criterion} must be between 1 and 5.")
    return errors, warnings


def calculate_decision_matrix_scores(scenarios_df, criteria_df, scores_df):
    active_criteria = get_active_decision_criteria(criteria_df)
    score_rows = []
    contribution_rows = []
    scenario_lookup = {
        str(row.scenario_name).strip(): row
        for row in scenarios_df.fillna("").itertuples(index=False)
    }

    for _, row in scores_df.fillna("").iterrows():
        scenario_name = str(row["scenario_name"]).strip()
        if not scenario_name:
            continue
        total_score = 0.0
        for criterion in active_criteria.itertuples(index=False):
            score = to_float(row.get(criterion.criterion, 3), 3)
            weight_fraction = to_float(criterion.weight_pct) / 100
            weighted_score = score * weight_fraction
            total_score += weighted_score
            contribution_rows.append(
                {
                    "scenario_name": scenario_name,
                    "criterion": criterion.criterion,
                    "score": score,
                    "weight_pct": to_float(criterion.weight_pct),
                    "weighted_score": weighted_score,
                }
            )
        scenario = scenario_lookup.get(scenario_name)
        score_rows.append(
            {
                "rank": 0,
                "scenario_name": scenario_name,
                "scenario_type": getattr(scenario, "scenario_type", ""),
                "total_weighted_score": total_score,
            }
        )

    results_df = pd.DataFrame(score_rows)
    if not results_df.empty:
        results_df = results_df.sort_values(
            "total_weighted_score", ascending=False
        ).reset_index(drop=True)
        results_df["rank"] = results_df.index + 1
    contribution_df = pd.DataFrame(contribution_rows)
    return results_df, contribution_df


def get_decision_tradeoffs(results_df, contribution_df):
    if results_df.empty or contribution_df.empty:
        return []
    tradeoffs = []
    top_name = results_df.iloc[0]["scenario_name"]
    top_contrib = contribution_df[
        contribution_df["scenario_name"] == top_name
    ].sort_values("weighted_score", ascending=False)
    if not top_contrib.empty:
        strengths = ", ".join(top_contrib.head(3)["criterion"].tolist())
        tradeoffs.append(f"{top_name} is mainly lifted by: {strengths}.")

    low_scores = contribution_df[contribution_df["score"] <= 2].copy()
    if not low_scores.empty:
        for scenario_name, group_df in low_scores.groupby("scenario_name"):
            criteria = ", ".join(group_df["criterion"].head(3).tolist())
            tradeoffs.append(f"{scenario_name} has weaker favourability on: {criteria}.")
    return tradeoffs[:6]


def get_score_for(contribution_df, scenario_name, criterion):
    matching = contribution_df[
        (contribution_df["scenario_name"] == scenario_name)
        & (contribution_df["criterion"] == criterion)
    ]
    if matching.empty:
        return None
    return float(matching.iloc[0]["score"])


def build_decision_recommendation_summary(results_df, contribution_df):
    if results_df.empty:
        return "Add scenarios and scores to generate a recommendation summary."

    top = results_df.iloc[0]
    second = results_df.iloc[1] if len(results_df) > 1 else None
    top_contrib = contribution_df[
        contribution_df["scenario_name"] == top["scenario_name"]
    ].sort_values("weighted_score", ascending=False)
    strongest = ", ".join(top_contrib.head(3)["criterion"].tolist()) or "the active criteria"

    lines = [
        f"Highest-ranked scenario: **{top['scenario_name']}** with a weighted score of {top['total_weighted_score']:.2f} out of 5.",
        f"It ranks highest because its strongest weighted criteria are: {strongest}.",
    ]
    if second is not None:
        lines.append(
            f"Second-ranked scenario: **{second['scenario_name']}** with a weighted score of {second['total_weighted_score']:.2f} out of 5."
        )

    tradeoffs = get_decision_tradeoffs(results_df, contribution_df)
    if tradeoffs:
        lines.append("Key trade-offs: " + " ".join(tradeoffs))

    strategic_workload_flags = []
    low_workload_low_value_flags = []
    for scenario_name in results_df["scenario_name"].tolist():
        strategic = get_score_for(contribution_df, scenario_name, "Strategic value")
        workload = get_score_for(contribution_df, scenario_name, "Workload impact")
        if strategic is not None and workload is not None:
            if strategic >= 4 and workload <= 2:
                strategic_workload_flags.append(scenario_name)
            if workload >= 4 and strategic <= 2:
                low_workload_low_value_flags.append(scenario_name)

    if strategic_workload_flags:
        lines.append(
            "High strategic value but weaker workload feasibility: "
            + ", ".join(strategic_workload_flags)
            + "."
        )
    if low_workload_low_value_flags:
        lines.append(
            "Low workload impact but weaker strategic value: "
            + ", ".join(low_workload_low_value_flags)
            + "."
        )

    lines.append(
        "Caution: this score is a facilitation aid. It is not an automatic decision or objective truth."
    )
    return "\n\n".join(lines)


def build_decision_comparison_summary_object(
    decision_question,
    scenarios_df,
    criteria_df,
    results_df,
    contribution_df,
):
    active_criteria = get_active_decision_criteria(criteria_df)
    tradeoffs = get_decision_tradeoffs(results_df, contribution_df)
    ranked_order = (
        results_df[["rank", "scenario_name", "total_weighted_score"]].to_dict("records")
        if not results_df.empty
        else []
    )
    scenario_rows = []
    for row in scenarios_df.fillna("").itertuples(index=False):
        scenario_rows.append(
            {
                "scenario_name": str(row.scenario_name).strip(),
                "short_description": str(row.short_description).strip(),
                "scenario_type": str(row.scenario_type).strip(),
            }
        )
    return {
        "decision_question": str(decision_question).strip(),
        "scenarios": scenario_rows,
        "active_criteria": [
            {
                "criterion": row.criterion,
                "weight_pct": round(to_float(row.weight_pct), 1),
                "favourability_guidance": row.favourability_guidance,
            }
            for row in active_criteria.itertuples(index=False)
        ],
        "ranked_order": ranked_order,
        "scenario_scores": ranked_order,
        "major_tradeoffs": tradeoffs,
        "flagged_caveats": [
            "Scores are based on human judgement",
            "Weights reflect values and priorities, not objective truth",
            "All criteria are scored for favourability, so high risk/cost/complexity means a lower score",
            "The AI must not make the decision or treat the ranking as objectively correct",
        ],
        "excluded_data_notice": {
            "api_keys_sent": False,
            "raw_uploaded_files_sent": False,
            "staff_names_sent": False,
            "person_level_capacity_sent": False,
            "sensitive_notes_sent": False,
            "confidential_operational_detail_sent": False,
            "raw_scenario_notes_sent": False,
        },
    }


def validate_decision_ai_summary(summary):
    if not summary:
        return False, "There is no decision comparison summary available yet."
    if len(summary.get("scenarios", [])) < 2:
        return False, "Add at least two scenarios before using AI interpretation."
    if not summary.get("active_criteria"):
        return False, "Enable and weight at least one criterion first."
    if not summary.get("ranked_order"):
        return False, "Score the scenarios before using AI interpretation."
    return True, ""


def build_decision_ai_user_prompt(summary):
    summary_json = json.dumps(summary, indent=2)
    return (
        "Interpret this non-AI scenario decision matrix summary for leadership reflection.\n\n"
        "Use only the provided summary. Do not recalculate scores. Do not make the decision. "
        "Do not describe the ranking as objectively correct.\n\n"
        f"Decision matrix summary:\n{summary_json}"
    )


def generate_ai_decision_interpretation(summary, api_key, model):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        reasoning={"effort": "low"},
        max_output_tokens=1200,
        input=[
            {
                "role": "developer",
                "content": AI_DECISION_MATRIX_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": build_decision_ai_user_prompt(summary),
            },
        ],
    )
    return response.output_text


def build_decision_matrix_markdown(
    decision_question,
    scenarios_df,
    criteria_df,
    scores_df,
    results_df,
    recommendation_text,
    ai_text="",
):
    active_criteria = get_active_decision_criteria(criteria_df)
    lines = [
        "# Scenario Decision Matrix Summary",
        "",
        "> Planning and facilitation aid only. This is not an automatic decision.",
        "",
        "## Decision Question",
        "",
        str(decision_question).strip() or "Not entered",
        "",
        "## Scenarios Compared",
        "",
    ]
    for row in scenarios_df.fillna("").itertuples(index=False):
        lines.append(
            f"- **{row.scenario_name}** ({row.scenario_type}): {row.short_description}"
        )

    lines.extend(["", "## Active Criteria and Weights", "", "| Criterion | Weight | Guidance |", "| --- | ---: | --- |"])
    for row in active_criteria.itertuples(index=False):
        lines.append(
            f"| {row.criterion} | {to_float(row.weight_pct):.1f}% | {row.favourability_guidance} |"
        )

    lines.extend(["", "## Scenario Scores", ""])
    if not scores_df.empty:
        lines.append(dataframe_to_markdown_table(scores_df))

    lines.extend(["", "## Ranked Recommendation", ""])
    if not results_df.empty:
        lines.append(dataframe_to_markdown_table(results_df))
    lines.extend(["", recommendation_text, "", "## Caveats", ""])
    lines.extend(
        [
            "- Scores depend on human judgement.",
            "- Weights reflect values and priorities, not objective truth.",
            "- All scoring is favourability scoring: 5 is favourable even when the underlying criterion is normally lower-is-better.",
            "- AI interpretation, if included, is reflective and not authoritative.",
        ]
    )
    lines.extend(["", "## Decision Prompts", ""])
    lines.extend([f"- {prompt}" for prompt in DECISION_PROMPTS])

    if ai_text:
        lines.extend(
            [
                "",
                "## Optional AI Interpretation",
                "",
                "> AI output is included as reflection material only. It does not make the decision.",
                "",
                ai_text,
            ]
        )
    return "\n".join(lines).encode("utf-8")


def dataframe_to_markdown_table(df):
    if df.empty:
        return ""
    columns = df.columns.tolist()
    lines = [
        "| " + " | ".join(str(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in df.fillna("").itertuples(index=False):
        values = []
        for value in row:
            if isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_canonical_data_model(
    source,
    profile,
    capacity_df,
    software_df,
    baseline_df,
    people_availability_df,
    assigned_work_items_df,
    period_months,
):
    monthly_workload_df = calculate_monthly_workload(
        capacity_df, assigned_work_items_df, period_months
    )
    return {
        "source": source,
        "team_profile": profile,
        "team_capacity": capacity_df,
        "people_availability": people_availability_df,
        "assigned_work_items": assigned_work_items_df,
        "monthly_workload": monthly_workload_df,
        "software_portfolio": software_df,
        "baseline_workload": baseline_df,
        "scenario_adjustments": pd.DataFrame(),
        "review_summary": build_review_summary(
            assigned_work_items_df, monthly_workload_df
        ),
        "period_months": period_months,
        "model_tables": CANONICAL_MODEL_TABLES,
    }


def build_guided_capacity_data(profile, people_df, work_df, period_months):
    people_availability_df = build_people_availability_from_builder(people_df, profile)
    capacity_df = build_team_capacity_from_availability(people_availability_df, profile)
    assigned_work_items_df = build_assigned_work_items_from_builder(
        work_df, profile, period_months
    )
    workload_df = build_baseline_workload_from_work_items(assigned_work_items_df)
    software_df = pd.DataFrame(
        [
            {
                "software_id": "GUIDED-BASELINE",
                "software_name": str(profile["team_name"]).strip() or "Guided baseline",
                "support_status": "Supported",
                "support_level": "Standard",
                "criticality": "Medium",
                "adoption_level": "Medium",
                "vendor_complexity": "Medium",
                "configuration_complexity": "Medium",
                "integration_complexity": "Medium",
                "primary_audience": "Internal support planning",
                "notes": "Generated from the guided Baseline Capacity Builder.",
            }
        ],
        columns=SUPPORTED_SOFTWARE_REQUIRED_COLUMNS,
    )
    return build_canonical_data_model(
        source="guided_baseline_builder",
        profile={**profile, "source": "guided_baseline_builder"},
        capacity_df=capacity_df,
        software_df=software_df,
        baseline_df=workload_df,
        people_availability_df=people_availability_df,
        assigned_work_items_df=assigned_work_items_df,
        period_months=period_months,
    )


def build_csv_canonical_data_model(
    raw_capacity_df,
    raw_software_df,
    raw_workload_df,
    capacity_source,
):
    profile = get_csv_team_profile(capacity_source)
    period_months = get_default_period_months()
    capacity_df = prepare_team_capacity(raw_capacity_df)
    software_df = prepare_supported_software(raw_software_df)
    baseline_df = prepare_baseline_workload(raw_workload_df)
    people_availability_df = build_people_availability_from_capacity(capacity_df)
    assigned_work_items_df = build_assigned_work_items_from_workload(
        baseline_df, period_months
    )
    return build_canonical_data_model(
        source="csv_upload_or_sample",
        profile=profile,
        capacity_df=capacity_df,
        software_df=software_df,
        baseline_df=baseline_df,
        people_availability_df=people_availability_df,
        assigned_work_items_df=assigned_work_items_df,
        period_months=period_months,
    )


def calculate_workload_hours(df):
    calculated_df = df.copy()
    for role in ROLES:
        unit_column = ROLE_UNIT_COLUMNS[role]
        total_column = ROLE_TOTAL_COLUMNS[role]
        calculated_column = CALCULATED_ROLE_COLUMNS[role]
        calculated_from_units = calculated_df["annual_volume"] * calculated_df[unit_column]
        calculated_df[calculated_column] = calculated_df[total_column].where(
            calculated_df[total_column] > 0, calculated_from_units
        )

    calculated_df["calculated_total_hours"] = calculated_df[
        list(CALCULATED_ROLE_COLUMNS.values())
    ].sum(axis=1)
    return calculated_df


def calculate_role_pressure(workload_df, capacity_df):
    rows = []
    for role in ROLES:
        committed_hours = workload_df[CALCULATED_ROLE_COLUMNS[role]].sum()
        role_capacity = capacity_df.loc[capacity_df["role"] == role, "available_hours_year"]
        available_hours = role_capacity.sum() if not role_capacity.empty else 0
        remaining_capacity = available_hours - committed_hours
        utilisation_pct = (
            committed_hours / available_hours * 100 if available_hours > 0 else 0
        )
        rows.append(
            {
                "role": role,
                "committed_hours": committed_hours,
                "available_hours": available_hours,
                "remaining_capacity": remaining_capacity,
                "utilisation_pct": utilisation_pct,
                "overload_status": classify_overload(utilisation_pct, available_hours),
            }
        )
    return pd.DataFrame(rows)


def classify_overload(utilisation_pct, available_hours=1):
    if available_hours <= 0:
        return "No capacity set"
    if utilisation_pct < 85:
        return "Under capacity"
    if utilisation_pct <= 100:
        return "Near capacity"
    if utilisation_pct <= 115:
        return "Over capacity"
    return "Significantly over capacity"


def apply_baseline_filters(workload_df, software_df):
    st.sidebar.header("Baseline Filters")
    merged_df = workload_df.merge(
        software_df[
            [
                "software_id",
                "support_status",
                "support_level",
                "criticality",
                "adoption_level",
                "vendor_complexity",
                "configuration_complexity",
                "integration_complexity",
            ]
        ],
        on="software_id",
        how="left",
    )
    for column in [
        "support_status",
        "support_level",
        "criticality",
        "adoption_level",
        "vendor_complexity",
        "configuration_complexity",
        "integration_complexity",
    ]:
        merged_df[column] = merged_df[column].fillna("Unknown")

    filter_columns = [
        "software_name",
        "support_status",
        "support_level",
        "criticality",
        "adoption_level",
        "work_type",
        "work_group",
        "confidence",
    ]
    filtered_df = merged_df.copy()
    for column in filter_columns:
        options = sorted(filtered_df[column].dropna().astype(str).unique().tolist())
        if options:
            selected = st.sidebar.multiselect(
                column.replace("_", " ").title(),
                options=options,
                default=options,
            )
            filtered_df = filtered_df[filtered_df[column].astype(str).isin(selected)]
    return filtered_df


def get_complexity_multiplier(
    adoption_level,
    vendor_complexity,
    configuration_complexity,
    integration_complexity,
):
    return (
        ADOPTION_MULTIPLIERS[adoption_level]
        * COMPLEXITY_MULTIPLIERS[vendor_complexity]
        * COMPLEXITY_MULTIPLIERS[configuration_complexity]
        * COMPLEXITY_MULTIPLIERS[integration_complexity]
    )


def templates_to_workload_rows(
    templates_df,
    selected_template_ids,
    software_id,
    software_name,
    work_group,
    volume_multiplier=1.0,
    hours_multiplier=1.0,
    confidence_override=None,
    notes_prefix="Scenario",
):
    selected_templates = templates_df[
        templates_df["template_id"].isin(selected_template_ids)
    ].copy()
    rows = []
    for offset, template in selected_templates.reset_index(drop=True).iterrows():
        confidence = confidence_override or template["default_confidence"]
        rows.append(
            {
                "workload_id": f"SCN-{offset + 1:03d}-{template['template_id']}",
                "software_id": software_id,
                "software_name": software_name,
                "work_type": template["work_type"],
                "work_group": work_group,
                "annual_volume": template["default_annual_volume"] * volume_multiplier,
                "advisor_hours_per_unit": template["advisor_hours_per_unit"]
                * hours_multiplier,
                "helpdesk_hours_per_unit": template["helpdesk_hours_per_unit"]
                * hours_multiplier,
                "specialist_hours_per_unit": template["specialist_hours_per_unit"]
                * hours_multiplier,
                "pm_hours_per_unit": template["pm_hours_per_unit"] * hours_multiplier,
                "manager_hours_per_unit": template["manager_hours_per_unit"]
                * hours_multiplier,
                "advisor_hours_total": 0,
                "helpdesk_hours_total": 0,
                "specialist_hours_total": 0,
                "pm_hours_total": 0,
                "manager_hours_total": 0,
                "confidence": confidence,
                "notes": f"{notes_prefix}. Template {template['template_id']}: {template['notes']}",
            }
        )
    if not rows:
        return pd.DataFrame(columns=BASELINE_WORKLOAD_REQUIRED_COLUMNS)
    return calculate_workload_hours(pd.DataFrame(rows))


def build_introduce_software_scenario(
    baseline_df,
    templates_df,
    new_software_name,
    support_level,
    criticality,
    adoption_level,
    vendor_complexity,
    configuration_complexity,
    integration_complexity,
    lifecycle_phase,
    selected_template_ids,
    demand_multiplier,
    confidence,
):
    if not new_software_name.strip() or not selected_template_ids:
        return baseline_df.copy(), "Introduce software", pd.DataFrame(), True

    support_multiplier = SUPPORT_LEVEL_MULTIPLIERS[support_level]
    complexity_multiplier = get_complexity_multiplier(
        adoption_level,
        vendor_complexity,
        configuration_complexity,
        integration_complexity,
    )
    phase_templates = templates_df[templates_df["lifecycle_phase"] == lifecycle_phase]
    selected_ids = [
        template_id
        for template_id in selected_template_ids
        if template_id in set(phase_templates["template_id"])
    ]

    added_rows = templates_to_workload_rows(
        templates_df,
        selected_ids,
        "SCN-NEW",
        new_software_name.strip(),
        "Scenario",
        volume_multiplier=demand_multiplier,
        hours_multiplier=support_multiplier * complexity_multiplier,
        confidence_override=confidence,
        notes_prefix=(
            f"Introduce software at {support_level} support, {criticality} criticality, "
            f"{adoption_level} adoption"
        ),
    )
    scenario_df = pd.concat([baseline_df, added_rows], ignore_index=True)
    uncertainty_flag = confidence == "Low" or (not added_rows.empty and (added_rows["confidence"] == "Low").any())
    return scenario_df, "Introduce software", added_rows, uncertainty_flag


def build_remove_software_scenario(
    baseline_df,
    templates_df,
    selected_software_names,
    removal_mode,
):
    if not selected_software_names:
        return baseline_df.copy(), "Remove software", pd.DataFrame(), False

    scenario_df = baseline_df.copy()
    mask = scenario_df["software_name"].isin(selected_software_names)
    affected_rows = scenario_df[mask].copy()
    if affected_rows.empty:
        return scenario_df, "Remove software", affected_rows, False

    remaining_factor = REMOVAL_FACTORS[removal_mode]
    for role in ROLES:
        column = CALCULATED_ROLE_COLUMNS[role]
        total_column = ROLE_TOTAL_COLUMNS[role]
        scenario_df.loc[mask, column] = scenario_df.loc[mask, column] * remaining_factor
        scenario_df.loc[mask, total_column] = scenario_df.loc[mask, column]
    scenario_df.loc[mask, "annual_volume"] = scenario_df.loc[mask, "annual_volume"] * remaining_factor
    scenario_df.loc[mask, "work_group"] = "Scenario"
    scenario_df.loc[mask, "notes"] = (
        scenario_df.loc[mask, "notes"].astype(str) + f" Removal mode: {removal_mode}."
    )
    scenario_df.loc[mask, "calculated_total_hours"] = scenario_df.loc[
        mask, list(CALCULATED_ROLE_COLUMNS.values())
    ].sum(axis=1)

    transition_rows = pd.DataFrame()
    if removal_mode == "retire with transition support":
        transition_templates = templates_df[
            templates_df["scenario_type"].isin(["Remove software", "Decommission tool"])
        ]
        transition_rows = templates_to_workload_rows(
            transition_templates,
            transition_templates["template_id"].tolist(),
            "SCN-RETIRE",
            " / ".join(selected_software_names) + " retirement",
            "Scenario",
            volume_multiplier=max(1, len(selected_software_names)),
            hours_multiplier=1.0,
            confidence_override="Medium",
            notes_prefix="Retirement and transition support",
        )
        scenario_df = pd.concat([scenario_df, transition_rows], ignore_index=True)

    scenario_detail = pd.concat([affected_rows, transition_rows], ignore_index=True)
    uncertainty_flag = (affected_rows["confidence"] == "Low").any() if not affected_rows.empty else False
    return scenario_df, "Remove software", scenario_detail, uncertainty_flag


def build_consolidate_software_scenario(
    baseline_df,
    templates_df,
    selected_software_names,
    destination_tool,
    consolidation_intensity,
):
    if len(selected_software_names) < 2 or not destination_tool.strip():
        return baseline_df.copy(), "Consolidate software", pd.DataFrame(), True

    scenario_df = baseline_df.copy()
    mask = scenario_df["software_name"].isin(selected_software_names)
    affected_rows = scenario_df[mask].copy()
    if affected_rows.empty:
        return scenario_df, "Consolidate software", affected_rows, False

    settings = CONSOLIDATION_FACTORS[consolidation_intensity]
    retained_load = settings["retained_load"]
    for role in ROLES:
        column = CALCULATED_ROLE_COLUMNS[role]
        total_column = ROLE_TOTAL_COLUMNS[role]
        scenario_df.loc[mask, column] = scenario_df.loc[mask, column] * retained_load
        scenario_df.loc[mask, total_column] = scenario_df.loc[mask, column]
    scenario_df.loc[mask, "annual_volume"] = scenario_df.loc[mask, "annual_volume"] * retained_load
    scenario_df.loc[mask, "software_name"] = destination_tool.strip()
    scenario_df.loc[mask, "software_id"] = "SCN-CONSOLIDATED"
    scenario_df.loc[mask, "work_group"] = "Scenario"
    scenario_df.loc[mask, "notes"] = (
        scenario_df.loc[mask, "notes"].astype(str)
        + f" Consolidated into {destination_tool.strip()}."
    )
    scenario_df.loc[mask, "calculated_total_hours"] = scenario_df.loc[
        mask, list(CALCULATED_ROLE_COLUMNS.values())
    ].sum(axis=1)

    transition_templates = templates_df[
        templates_df["scenario_type"] == "Consolidate software"
    ]
    transition_rows = templates_to_workload_rows(
        transition_templates,
        transition_templates["template_id"].tolist(),
        "SCN-CONSOLIDATED",
        destination_tool.strip(),
        "Scenario",
        volume_multiplier=max(1, len(selected_software_names)),
        hours_multiplier=settings["transition_multiplier"],
        confidence_override="Medium" if consolidation_intensity != "complex" else "Low",
        notes_prefix=f"{consolidation_intensity.title()} consolidation transition",
    )
    scenario_df = pd.concat([scenario_df, transition_rows], ignore_index=True)
    scenario_detail = pd.concat([affected_rows, transition_rows], ignore_index=True)
    uncertainty_flag = consolidation_intensity == "complex" or (affected_rows["confidence"] == "Low").any()
    return scenario_df, "Consolidate software", scenario_detail, uncertainty_flag


def build_reduce_support_level_scenario(
    baseline_df,
    selected_software_name,
    new_support_level,
):
    scenario_df = baseline_df.copy()
    mask = scenario_df["software_name"] == selected_software_name
    affected_rows = scenario_df[mask].copy()
    if affected_rows.empty:
        return scenario_df, "Reduce support level", affected_rows, False

    multiplier = SUPPORT_LEVEL_MULTIPLIERS[new_support_level]
    for role in ROLES:
        column = CALCULATED_ROLE_COLUMNS[role]
        total_column = ROLE_TOTAL_COLUMNS[role]
        scenario_df.loc[mask, column] = scenario_df.loc[mask, column] * multiplier
        scenario_df.loc[mask, total_column] = scenario_df.loc[mask, column]
    scenario_df.loc[mask, "annual_volume"] = scenario_df.loc[mask, "annual_volume"] * multiplier
    scenario_df.loc[mask, "work_group"] = "Scenario"
    scenario_df.loc[mask, "notes"] = (
        scenario_df.loc[mask, "notes"].astype(str)
        + f" Support level changed to {new_support_level}."
    )
    scenario_df.loc[mask, "calculated_total_hours"] = scenario_df.loc[
        mask, list(CALCULATED_ROLE_COLUMNS.values())
    ].sum(axis=1)
    uncertainty_flag = (affected_rows["confidence"] == "Low").any()
    return scenario_df, "Reduce support level", affected_rows, uncertainty_flag


def build_increase_adoption_scenario(
    baseline_df,
    selected_software_name,
    adoption_increase_pct,
):
    scenario_df = baseline_df.copy()
    mask = scenario_df["software_name"] == selected_software_name
    sensitive_mask = mask & scenario_df["work_type"].isin(ADOPTION_SENSITIVE_WORK_TYPES)
    less_sensitive_mask = mask & ~scenario_df["work_type"].isin(ADOPTION_SENSITIVE_WORK_TYPES)
    affected_rows = scenario_df[mask].copy()
    if affected_rows.empty:
        return scenario_df, "Increase adoption", affected_rows, False

    sensitive_multiplier = 1 + adoption_increase_pct / 100
    less_sensitive_multiplier = 1 + adoption_increase_pct / 300
    for target_mask, multiplier in [
        (sensitive_mask, sensitive_multiplier),
        (less_sensitive_mask, less_sensitive_multiplier),
    ]:
        for role in ROLES:
            column = CALCULATED_ROLE_COLUMNS[role]
            total_column = ROLE_TOTAL_COLUMNS[role]
            scenario_df.loc[target_mask, column] = (
                scenario_df.loc[target_mask, column] * multiplier
            )
            scenario_df.loc[target_mask, total_column] = scenario_df.loc[target_mask, column]
        scenario_df.loc[target_mask, "annual_volume"] = (
            scenario_df.loc[target_mask, "annual_volume"] * multiplier
        )
        scenario_df.loc[target_mask, "calculated_total_hours"] = scenario_df.loc[
            target_mask, list(CALCULATED_ROLE_COLUMNS.values())
        ].sum(axis=1)
    scenario_df.loc[mask, "work_group"] = "Scenario"
    scenario_df.loc[mask, "notes"] = (
        scenario_df.loc[mask, "notes"].astype(str)
        + f" Adoption increased by {adoption_increase_pct}%."
    )
    uncertainty_flag = (affected_rows["confidence"] == "Low").any()
    return scenario_df, "Increase adoption", affected_rows, uncertainty_flag


def build_project_to_bau_scenario(
    baseline_df,
    templates_df,
    selected_name,
    bau_support_level,
    recurring_intensity,
):
    scenario_df = baseline_df.copy()
    mask = (
        (scenario_df["software_name"] == selected_name)
        | (scenario_df["software_id"] == selected_name)
    ) & scenario_df["work_group"].isin(["Project", "Change", "Scenario"])
    affected_rows = scenario_df[mask].copy()

    intensity_multiplier = {"Light": 0.35, "Moderate": 0.55, "High": 0.85}[
        recurring_intensity
    ]
    support_multiplier = SUPPORT_LEVEL_MULTIPLIERS[bau_support_level]

    recurring_templates = templates_df[
        templates_df["scenario_type"] == "Project to BAU"
    ]
    recurring_rows = templates_to_workload_rows(
        recurring_templates,
        recurring_templates["template_id"].tolist(),
        "SCN-BAU",
        selected_name,
        "BAU",
        volume_multiplier=1.0,
        hours_multiplier=intensity_multiplier * support_multiplier,
        confidence_override="Medium",
        notes_prefix=f"Recurring BAU estimate at {bau_support_level} support",
    )
    scenario_df = pd.concat([scenario_df, recurring_rows], ignore_index=True)
    uncertainty_flag = affected_rows.empty or (affected_rows["confidence"] == "Low").any()
    scenario_detail = pd.concat([affected_rows, recurring_rows], ignore_index=True)
    return scenario_df, "Project to BAU", scenario_detail, uncertainty_flag


def build_demand_spike_scenario(
    baseline_df,
    affected_work_types,
    demand_increase_pct,
    duration_months,
):
    scenario_df = baseline_df.copy()
    if not affected_work_types or duration_months <= 0:
        return scenario_df, "Demand spike", pd.DataFrame(), True

    mask = scenario_df["work_type"].isin(affected_work_types)
    affected_rows = scenario_df[mask].copy()
    if affected_rows.empty:
        return scenario_df, "Demand spike", affected_rows, False

    annualised_multiplier = 1 + (demand_increase_pct / 100) * (duration_months / 12)
    for role in ROLES:
        column = CALCULATED_ROLE_COLUMNS[role]
        total_column = ROLE_TOTAL_COLUMNS[role]
        scenario_df.loc[mask, column] = scenario_df.loc[mask, column] * annualised_multiplier
        scenario_df.loc[mask, total_column] = scenario_df.loc[mask, column]
    scenario_df.loc[mask, "annual_volume"] = scenario_df.loc[mask, "annual_volume"] * annualised_multiplier
    scenario_df.loc[mask, "work_group"] = "Scenario"
    scenario_df.loc[mask, "notes"] = (
        scenario_df.loc[mask, "notes"].astype(str)
        + f" Demand spike: {demand_increase_pct}% for {duration_months} months."
    )
    scenario_df.loc[mask, "calculated_total_hours"] = scenario_df.loc[
        mask, list(CALCULATED_ROLE_COLUMNS.values())
    ].sum(axis=1)
    uncertainty_flag = (affected_rows["confidence"] == "Low").any()
    return scenario_df, "Demand spike", affected_rows, uncertainty_flag


def build_decommission_tool_scenario(
    baseline_df,
    templates_df,
    selected_software_name,
    transition_months,
    confidence,
):
    if not selected_software_name:
        return baseline_df.copy(), "Decommission tool", pd.DataFrame(), True

    scenario_df, _, removed_rows, low_from_baseline = build_reduce_support_level_scenario(
        baseline_df, selected_software_name, "No support"
    )
    retire_templates = templates_df[
        templates_df["scenario_type"] == "Decommission tool"
    ]
    transition_rows = templates_to_workload_rows(
        retire_templates,
        retire_templates["template_id"].tolist(),
        "SCN-DECOM",
        f"{selected_software_name} decommissioning",
        "Scenario",
        volume_multiplier=max(0.25, transition_months / 6),
        hours_multiplier=1.0,
        confidence_override=confidence,
        notes_prefix=f"Decommissioning over {transition_months} months",
    )
    scenario_df = pd.concat([scenario_df, transition_rows], ignore_index=True)
    uncertainty_flag = confidence == "Low" or low_from_baseline
    scenario_detail = pd.concat([removed_rows, transition_rows], ignore_index=True)
    return scenario_df, "Decommission tool", scenario_detail, uncertainty_flag


def build_capacity_change_scenario(
    baseline_df,
    capacity_df,
    selected_role,
    fte_delta,
):
    scenario_capacity_df = capacity_df.copy()
    mask = scenario_capacity_df["role"] == selected_role
    if mask.any():
        scenario_capacity_df.loc[mask, "fte"] = (
            scenario_capacity_df.loc[mask, "fte"] + fte_delta
        ).clip(lower=0)
        scenario_capacity_df.loc[mask, "available_hours_year"] = (
            scenario_capacity_df.loc[mask, "fte"]
            * scenario_capacity_df.loc[mask, "usable_hours_per_fte_per_year"]
        )
        scenario_capacity_df.loc[mask, "notes"] = (
            scenario_capacity_df.loc[mask, "notes"].astype(str)
            + f" Scenario capacity change: {fte_delta:+.2f} FTE."
        )
    return baseline_df.copy(), scenario_capacity_df, "Capacity change", pd.DataFrame(), False


def calculate_scenario_impact(
    baseline_df,
    scenario_df,
    capacity_df,
    uncertainty_flag=False,
    scenario_capacity_df=None,
):
    scenario_capacity_df = scenario_capacity_df if scenario_capacity_df is not None else capacity_df
    baseline_pressure = calculate_role_pressure(baseline_df, capacity_df)
    scenario_pressure = calculate_role_pressure(scenario_df, scenario_capacity_df)
    baseline_total = baseline_pressure["committed_hours"].sum()
    scenario_total = scenario_pressure["committed_hours"].sum()
    hours_delta = scenario_total - baseline_total
    percentage_delta = hours_delta / baseline_total * 100 if baseline_total else 0

    role_delta_df = baseline_pressure[
        ["role", "committed_hours", "available_hours"]
    ].merge(
        scenario_pressure[["role", "committed_hours", "available_hours"]],
        on="role",
        suffixes=("_baseline", "_scenario"),
    )
    role_delta_df = role_delta_df.rename(
        columns={
            "available_hours_baseline": "baseline_available_hours",
            "available_hours_scenario": "available_hours",
        }
    )
    role_delta_df["role_hours_delta"] = (
        role_delta_df["committed_hours_scenario"]
        - role_delta_df["committed_hours_baseline"]
    )
    role_delta_df["revised_utilisation_pct"] = role_delta_df.apply(
        lambda row: row["committed_hours_scenario"] / row["available_hours"] * 100
        if row["available_hours"] > 0
        else 0,
        axis=1,
    )
    role_delta_df["revised_overload_status"] = role_delta_df.apply(
        lambda row: classify_overload(
            row["revised_utilisation_pct"], row["available_hours"]
        ),
        axis=1,
    )

    baseline_work_type = baseline_df.groupby("work_type", as_index=False)[
        "calculated_total_hours"
    ].sum()
    scenario_work_type = scenario_df.groupby("work_type", as_index=False)[
        "calculated_total_hours"
    ].sum()
    work_type_delta_df = baseline_work_type.merge(
        scenario_work_type,
        on="work_type",
        how="outer",
        suffixes=("_baseline", "_scenario"),
    ).fillna(0)
    work_type_delta_df["work_type_hours_delta"] = (
        work_type_delta_df["calculated_total_hours_scenario"]
        - work_type_delta_df["calculated_total_hours_baseline"]
    )
    work_type_delta_df = work_type_delta_df.sort_values(
        "work_type_hours_delta", ascending=False
    )

    low_confidence_assumptions = int((scenario_df["confidence"] == "Low").sum())
    summary_df = pd.DataFrame(
        [
            {
                "baseline_total_hours": baseline_total,
                "scenario_total_hours": scenario_total,
                "hours_delta": hours_delta,
                "percentage_delta": percentage_delta,
                "roles_over_capacity": int(
                    role_delta_df["revised_overload_status"].isin(
                        ["Over capacity", "Significantly over capacity"]
                    ).sum()
                ),
                "low_confidence_assumptions": low_confidence_assumptions,
                "uncertainty_flag": bool(
                    uncertainty_flag or low_confidence_assumptions > 0
                ),
            }
        ]
    )
    return summary_df, role_delta_df, work_type_delta_df


def generate_leadership_prompts(
    scenario_name,
    baseline_df,
    scenario_df,
    capacity_df,
    scenario_summary_df,
    role_delta_df,
    work_type_delta_df,
):
    prompts = []
    if scenario_summary_df.empty:
        return ["Build a scenario first, then return here for interpretation."]

    summary = scenario_summary_df.iloc[0]
    hours_delta = summary["hours_delta"]
    pct_delta = summary["percentage_delta"]
    overloaded = role_delta_df[
        role_delta_df["revised_overload_status"].isin(
            ["Over capacity", "Significantly over capacity"]
        )
    ]
    if not overloaded.empty:
        role_text = ", ".join(
            f"{row.role} ({row.revised_utilisation_pct:.0f}%)"
            for row in overloaded.itertuples()
        )
        prompts.append(
            f"Roles under pressure after this scenario: {role_text}. This should trigger a scope, service-level, or resourcing decision."
        )
    else:
        prompts.append(
            "No role is above available capacity after this scenario, but near-capacity roles still need watching before peak teaching periods."
        )

    if hours_delta > 0:
        prompts.append(
            f"{scenario_name} adds approximately {hours_delta:,.0f} annual hours ({pct_delta:.1f}%). The leadership question is what existing work will move, stop, or be resourced."
        )
    elif hours_delta < 0:
        prompts.append(
            f"{scenario_name} removes approximately {abs(hours_delta):,.0f} annual hours ({abs(pct_delta):.1f}%). Check whether those hours are genuinely recoverable or tied to fixed service commitments."
        )
    else:
        prompts.append(
            "The scenario has no net workload change in this model. That usually means the assumptions are incomplete or the effect is mostly about risk, timing, or quality."
        )

    top_work_type_changes = work_type_delta_df[
        work_type_delta_df["work_type_hours_delta"].abs() > 0
    ].copy()
    if not top_work_type_changes.empty:
        top_work_type_changes["abs_delta"] = top_work_type_changes[
            "work_type_hours_delta"
        ].abs()
        top_work_type_changes = top_work_type_changes.sort_values(
            "abs_delta", ascending=False
        ).head(3)
        drivers = ", ".join(
            f"{row.work_type} ({row.work_type_hours_delta:+,.0f}h)"
            for row in top_work_type_changes.itertuples()
        )
        prompts.append(f"The main work type changes are: {drivers}.")

    scenario_groups = set(scenario_df["work_group"].dropna())
    if scenario_name in ["Introduce software", "Project to BAU"] or "BAU" in scenario_groups:
        prompts.append(
            "Watch for hidden BAU. Training, documentation, release testing, vendor management, configuration, and recurring support tickets often persist after implementation."
        )

    if scenario_name in ["Demand spike", "Consolidate software", "Decommission tool", "Remove software"]:
        prompts.append(
            "This impact may be temporary rather than recurring. Separate short-term transition pressure from steady-state annual support before making staffing decisions."
        )

    if bool(summary["uncertainty_flag"]):
        prompts.append(
            "Several estimates are low-confidence. Treat this scenario as a planning prompt rather than a forecast."
        )

    prompts.append(
        "The portfolio question remains: which tools justify their support burden, risk, and complexity?"
    )
    return prompts


def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")


def format_hours(value):
    return f"{value:,.0f}"


def make_gauge(committed_hours, available_hours, title):
    utilisation = committed_hours / available_hours * 100 if available_hours else 0
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=utilisation,
            number={"suffix": "%"},
            delta={"reference": 100},
            title={"text": title},
            gauge={
                "axis": {"range": [0, max(140, utilisation + 10)]},
                "bar": {"color": "#26648e"},
                "steps": [
                    {"range": [0, 85], "color": "#d8f3dc"},
                    {"range": [85, 100], "color": "#fff3b0"},
                    {"range": [100, 115], "color": "#ffd6a5"},
                    {"range": [115, max(140, utilisation + 10)], "color": "#ffadad"},
                ],
                "threshold": {
                    "line": {"color": "#222222", "width": 4},
                    "thickness": 0.75,
                    "value": 100,
                },
            },
        )
    )
    fig.update_layout(height=310, margin=dict(l=20, r=20, t=45, b=20))
    return fig


def make_role_pressure_chart(role_pressure_df):
    chart_df = role_pressure_df.melt(
        id_vars=["role", "utilisation_pct", "overload_status"],
        value_vars=["committed_hours", "available_hours"],
        var_name="measure",
        value_name="hours",
    )
    chart_df["measure"] = chart_df["measure"].replace(
        {"committed_hours": "Committed", "available_hours": "Available"}
    )
    fig = px.bar(
        chart_df,
        x="role",
        y="hours",
        color="measure",
        barmode="group",
        text_auto=".0f",
        color_discrete_map={"Committed": "#26648e", "Available": "#8ecae6"},
    )
    fig.update_layout(height=360, legend_title_text="", xaxis_title="", yaxis_title="Hours")
    return fig


def make_before_after_role_chart(role_delta_df):
    chart_df = role_delta_df.melt(
        id_vars=["role", "available_hours"],
        value_vars=["committed_hours_baseline", "committed_hours_scenario"],
        var_name="state",
        value_name="hours",
    )
    chart_df["state"] = chart_df["state"].replace(
        {
            "committed_hours_baseline": "Baseline",
            "committed_hours_scenario": "Scenario",
        }
    )
    fig = px.bar(
        chart_df,
        x="role",
        y="hours",
        color="state",
        barmode="group",
        text_auto=".0f",
        color_discrete_map={"Baseline": "#8ecae6", "Scenario": "#26648e"},
    )
    fig.add_scatter(
        x=role_delta_df["role"],
        y=role_delta_df["available_hours"],
        mode="markers",
        marker=dict(color="#c1121f", size=11, symbol="line-ew"),
        name="Available",
    )
    fig.update_layout(height=390, xaxis_title="", yaxis_title="Annual hours")
    return fig


def make_composition_chart(df):
    chart_df = (
        df.groupby("work_group", as_index=False)["calculated_total_hours"]
        .sum()
        .sort_values("calculated_total_hours", ascending=False)
    )
    fig = px.pie(
        chart_df,
        names="work_group",
        values="calculated_total_hours",
        hole=0.48,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=360, legend_title_text="")
    return fig


def make_software_burden_chart(df):
    chart_df = (
        df.groupby("software_name", as_index=False)["calculated_total_hours"]
        .sum()
        .sort_values("calculated_total_hours", ascending=True)
        .tail(15)
    )
    fig = px.bar(
        chart_df,
        x="calculated_total_hours",
        y="software_name",
        orientation="h",
        text_auto=".0f",
        color="calculated_total_hours",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=460,
        xaxis_title="Annual hours",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    return fig


def make_work_type_heatmap(df):
    role_columns = list(CALCULATED_ROLE_COLUMNS.values())
    chart_df = df.groupby("work_type")[role_columns].sum().reset_index()
    chart_df = chart_df.rename(columns={v: k for k, v in CALCULATED_ROLE_COLUMNS.items()})
    long_df = chart_df.melt(
        id_vars="work_type", value_vars=ROLES, var_name="role", value_name="hours"
    )
    fig = px.density_heatmap(
        long_df,
        x="role",
        y="work_type",
        z="hours",
        color_continuous_scale="YlGnBu",
        text_auto=".0f",
    )
    fig.update_layout(height=560, xaxis_title="", yaxis_title="")
    return fig


def make_delta_chart(df, x_column, y_column, title):
    chart_df = df.copy()
    if chart_df.empty:
        return go.Figure()
    chart_df["direction"] = chart_df[y_column].apply(
        lambda value: "Added" if value >= 0 else "Removed"
    )
    fig = px.bar(
        chart_df,
        x=x_column,
        y=y_column,
        color="direction",
        text_auto=".0f",
        title=title,
        color_discrete_map={"Added": "#26648e", "Removed": "#c1121f"},
    )
    fig.update_layout(height=360, xaxis_title="", yaxis_title="Hours delta")
    return fig


def make_decision_score_chart(results_df):
    if results_df.empty:
        return go.Figure()
    chart_df = results_df.sort_values("total_weighted_score", ascending=True)
    fig = px.bar(
        chart_df,
        x="total_weighted_score",
        y="scenario_name",
        orientation="h",
        text="total_weighted_score",
        color="total_weighted_score",
        color_continuous_scale="Teal",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        height=max(320, 70 * len(chart_df)),
        xaxis_title="Total weighted score out of 5",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    fig.update_xaxes(range=[0, 5])
    return fig


def show_summary_cards(summary_df):
    summary = summary_df.iloc[0]
    cols = st.columns(6)
    cols[0].metric("Baseline hours", format_hours(summary["baseline_total_hours"]))
    cols[1].metric("Scenario hours", format_hours(summary["scenario_total_hours"]))
    cols[2].metric("Hours delta", format_hours(summary["hours_delta"]))
    cols[3].metric("Change", f"{summary['percentage_delta']:.1f}%")
    cols[4].metric("Roles over capacity", int(summary["roles_over_capacity"]))
    cols[5].metric(
        "Low-confidence rows", int(summary["low_confidence_assumptions"])
    )


def show_top_workload_drivers(df):
    columns = [
        "workload_id",
        "software_name",
        "work_type",
        "work_group",
        "annual_volume",
        "calculated_total_hours",
        "confidence",
        "notes",
    ]
    st.dataframe(
        df[columns].sort_values("calculated_total_hours", ascending=False).head(10),
        width="stretch",
        hide_index=True,
    )


def show_support_portfolio_map(software_df, workload_df):
    burden = (
        workload_df.groupby("software_id", as_index=False)["calculated_total_hours"]
        .sum()
        .rename(columns={"calculated_total_hours": "annual_hours"})
    )
    map_df = software_df.merge(burden, on="software_id", how="left")
    map_df["annual_hours"] = map_df["annual_hours"].fillna(0)
    fig = px.scatter(
        map_df,
        x="support_level",
        y="criticality",
        size="annual_hours",
        color="support_status",
        facet_col="adoption_level",
        hover_name="software_name",
        hover_data=[
            "vendor_complexity",
            "configuration_complexity",
            "integration_complexity",
            "primary_audience",
            "annual_hours",
        ],
        category_orders={
            "support_level": SUPPORT_LEVELS,
            "criticality": CRITICALITY_LEVELS,
            "adoption_level": ADOPTION_LEVELS,
        },
        size_max=36,
    )
    fig.update_layout(height=430, xaxis_title="Support level", yaxis_title="Criticality")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(
        map_df[
            [
                "software_id",
                "software_name",
                "support_status",
                "support_level",
                "criticality",
                "adoption_level",
                "vendor_complexity",
                "configuration_complexity",
                "integration_complexity",
                "annual_hours",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


def get_uploaded_data():
    with st.sidebar.expander("Upload your own CSVs"):
        capacity_file = st.file_uploader("Team capacity CSV", type=["csv"])
        software_file = st.file_uploader("Supported software CSV", type=["csv"])
        workload_file = st.file_uploader("Baseline workload CSV", type=["csv"])
        templates_file = st.file_uploader("Scenario task templates CSV", type=["csv"])

    capacity_df, capacity_source = read_uploaded_or_sample(
        capacity_file, load_sample_team_capacity
    )
    software_df, software_source = read_uploaded_or_sample(
        software_file, load_sample_supported_software
    )
    workload_df, workload_source = read_uploaded_or_sample(
        workload_file, load_sample_baseline_workload
    )
    templates_df, templates_source = read_uploaded_or_sample(
        templates_file, load_sample_scenario_task_templates
    )
    st.sidebar.caption(
        "Sources: "
        f"capacity={capacity_source}, software={software_source}, "
        f"workload={workload_source}, templates={templates_source}"
    )
    sources = {
        "capacity": capacity_source,
        "software": software_source,
        "workload": workload_source,
        "templates": templates_source,
    }
    return capacity_df, software_df, workload_df, templates_df, sources


def show_sidebar_demo_controls():
    st.sidebar.markdown("### Demo Mode")
    st.sidebar.caption(
        "Use the built-in synthetic sample data when sharing or testing the app. "
        "Avoid uploading real sensitive team data to shared deployments."
    )
    if st.sidebar.button("Reset demo data"):
        reset_demo_data()
        st.rerun()


def get_builder_profile_inputs():
    profile = {}
    col1, col2 = st.columns(2)
    with col1:
        profile["team_name"] = st.text_input(
            "Team name",
            value=st.session_state.get(
                "builder_team_name", DEFAULT_TEAM_PROFILE["team_name"]
            ),
            key="builder_team_name",
        )
        profile["planning_unit"] = st.radio(
            "Planning unit",
            PLANNING_UNITS,
            index=PLANNING_UNITS.index(
                st.session_state.get(
                    "builder_planning_unit", DEFAULT_TEAM_PROFILE["planning_unit"]
                )
            ),
            horizontal=True,
            key="builder_planning_unit",
        )
    with col2:
        period_cols = st.columns(2)
        with period_cols[0]:
            profile["planning_start_month"] = st.text_input(
                "Planning start month",
                value=st.session_state.get(
                    "builder_start_month",
                    DEFAULT_TEAM_PROFILE["planning_start_month"],
                ),
                help="Use YYYY-MM format.",
                key="builder_start_month",
            )
        with period_cols[1]:
            profile["planning_end_month"] = st.text_input(
                "Planning end month",
                value=st.session_state.get(
                    "builder_end_month",
                    DEFAULT_TEAM_PROFILE["planning_end_month"],
                ),
                help="Use YYYY-MM format.",
                key="builder_end_month",
            )
        default_hours = float(
            st.session_state.get(
                "builder_standard_hours", DEFAULT_TEAM_PROFILE["standard_hours"]
            )
        )
        profile["standard_hours"] = st.number_input(
            "Standard hours assumption per FTE",
            min_value=1.0,
            max_value=250.0,
            value=default_hours,
            step=1.0,
            help="Use monthly hours when planning monthly, or weekly hours when planning weekly.",
            key="builder_standard_hours",
        )
    return profile


def show_assumptions_panel():
    with st.expander("Assumptions", expanded=False):
        st.markdown(
            """
- Capacity is calculated as `FTE x availability percentage x standard hours`.
- Part-time entries use the FTE value you enter, then the availability percentage reduces that available capacity further.
- Monthly workload is spread evenly across each work item's active month range.
- Over-capacity is flagged when assigned workload is greater than available capacity for a month.
- Scenario adjustments create a revised workload or capacity table, then compare it with the baseline model.
- This is a planning aid for team-level conversations, not a precise measurement system or individual performance tool.
            """
        )


def show_canonical_review(canonical_model, expanded=True):
    review_summary = canonical_model["review_summary"]
    monthly_workload_df = canonical_model["monthly_workload"]
    high_priority_df = review_summary["high_priority_work_items"]
    low_confidence_df = review_summary["low_confidence_work_items"]

    with st.expander("Review baseline capacity", expanded=expanded):
        st.dataframe(
            monthly_workload_df,
            width="stretch",
            hide_index=True,
            column_config={
                "month": "Month",
                "monthly_available_capacity": st.column_config.NumberColumn(
                    "Monthly available capacity", format="%.0f"
                ),
                "monthly_assigned_workload": st.column_config.NumberColumn(
                    "Monthly assigned workload", format="%.0f"
                ),
                "remaining_capacity": st.column_config.NumberColumn(
                    "Remaining capacity", format="%.0f"
                ),
                "over_capacity": "Over capacity",
            },
        )

        over_capacity_months = review_summary["over_capacity_months"]
        if over_capacity_months:
            st.error("Over-capacity months: " + ", ".join(over_capacity_months))
        else:
            st.success("No over-capacity months in the current baseline.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("High-priority work items")
            if high_priority_df.empty:
                st.info("No high-priority work items have been flagged.")
            else:
                st.dataframe(high_priority_df, width="stretch", hide_index=True)
        with col2:
            st.subheader("Low-confidence work items")
            if low_confidence_df.empty:
                st.info("No low-confidence work items have been flagged.")
            else:
                st.dataframe(low_confidence_df, width="stretch", hide_index=True)

        st.download_button(
            "Download planning summary",
            data=build_planning_summary_markdown(canonical_model),
            file_name="planning_summary.md",
            mime="text/markdown",
            key=f"planning_summary_download_{canonical_model.get('source', 'baseline')}",
        )


def show_task_estimate_library(profile, templates_df, subtasks_df):
    st.markdown("##### Add from task estimate library")
    st.caption(
        "Templates are planning aids, not performance measures. Review and adjust "
        "the estimate for local context. Use generic role or workstream labels and "
        "avoid sensitive personal information."
    )

    if templates_df.empty:
        st.info(
            "Task estimate templates are not available. You can still add work manually below."
        )
        return

    categories = sorted(templates_df["category"].dropna().unique().tolist())
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox(
            "Task category",
            categories,
            key="task_library_category",
        )
    category_templates = templates_df[
        templates_df["category"] == selected_category
    ].copy()
    template_labels = {
        f"{row.task_name} ({row.default_hours:g} hrs)": row.template_id
        for row in category_templates.itertuples(index=False)
    }
    with col2:
        selected_label = st.selectbox(
            "Task template",
            list(template_labels.keys()),
            key="task_library_template",
        )

    selected_template_id = template_labels[selected_label]
    selected_template = category_templates[
        category_templates["template_id"] == selected_template_id
    ].iloc[0]

    controls = st.columns(4)
    with controls[0]:
        quantity = st.number_input(
            "Quantity",
            min_value=0.1,
            max_value=1000.0,
            value=1.0,
            step=1.0,
            key="task_library_quantity",
        )
    with controls[1]:
        multiplier = st.number_input(
            "Multiplier",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Use this for local complexity or scale adjustments.",
            key="task_library_multiplier",
        )
    with controls[2]:
        start_month = st.text_input(
            "Start month",
            value=profile.get(
                "planning_start_month", DEFAULT_TEAM_PROFILE["planning_start_month"]
            ),
            help="Use YYYY-MM format.",
            key="task_library_start_month",
        )
    with controls[3]:
        end_month = st.text_input(
            "End month",
            value=profile.get(
                "planning_end_month", DEFAULT_TEAM_PROFILE["planning_end_month"]
            ),
            help="Use YYYY-MM format.",
            key="task_library_end_month",
        )

    settings = st.columns(3)
    with settings[0]:
        priority = st.selectbox(
            "Priority",
            PRIORITY_LEVELS,
            index=PRIORITY_LEVELS.index(selected_template.default_priority)
            if selected_template.default_priority in PRIORITY_LEVELS
            else PRIORITY_LEVELS.index("Medium"),
            key="task_library_priority",
        )
    with settings[1]:
        confidence = st.selectbox(
            "Confidence",
            CONFIDENCE_LEVELS,
            index=CONFIDENCE_LEVELS.index(selected_template.default_confidence)
            if selected_template.default_confidence in CONFIDENCE_LEVELS
            else CONFIDENCE_LEVELS.index("Medium"),
            key="task_library_confidence",
        )
    with settings[2]:
        work_type = st.selectbox(
            "Work type",
            WORK_TYPES,
            index=WORK_TYPES.index(selected_template.suggested_work_type)
            if selected_template.suggested_work_type in WORK_TYPES
            else WORK_TYPES.index("Other"),
            key="task_library_work_type",
        )

    estimated_hours = (
        to_float(selected_template.default_hours) * to_float(quantity) * to_float(multiplier)
    )
    st.metric("Calculated estimated hours", f"{estimated_hours:,.1f}")
    st.caption(
        f"Calculation: {selected_template.default_hours:g} default hours x "
        f"{quantity:g} quantity x {multiplier:g} multiplier."
    )

    selected_subtasks = subtasks_df[
        subtasks_df["template_id"] == selected_template_id
    ].copy()
    if not selected_subtasks.empty:
        with st.expander("Preview subtask breakdown", expanded=False):
            st.caption(
                "Subtasks are shown to explain the estimate. They are not exact time records."
            )
            st.dataframe(
                selected_subtasks,
                width="stretch",
                hide_index=True,
                column_config={
                    "template_id": None,
                    "subtask_name": "Subtask",
                    "subtask_hours": st.column_config.NumberColumn(
                        "Hours", format="%.1f"
                    ),
                },
            )
            st.metric(
                "Subtask total",
                f"{selected_subtasks['subtask_hours'].sum():,.1f} hours",
            )

    if st.button("Add selected estimate to assigned work"):
        if parse_month_label(start_month) is None or parse_month_label(end_month) is None:
            st.error("Start month and end month must use YYYY-MM format.")
            return
        if parse_month_label(end_month) < parse_month_label(start_month):
            st.error("End month must be the same as or after the start month.")
            return

        new_row = {
            "work_title": selected_template.task_name,
            "work_type": work_type,
            "start_month": start_month,
            "end_month": end_month,
            "estimated_hours": round(estimated_hours, 1),
            "priority": priority,
            "confidence": confidence,
            "notes": (
                f"Task estimate library template {selected_template.template_id}; "
                f"quantity={quantity:g}; multiplier={multiplier:g}; "
                "sanitised planning estimate."
            ),
        }
        st.session_state["builder_work_df"] = pd.concat(
            [
                st.session_state["builder_work_df"],
                pd.DataFrame([new_row]),
            ],
            ignore_index=True,
        )
        st.success("Task estimate added to assigned work.")
        st.rerun()


def show_guided_builder():
    st.header("Baseline Capacity Builder")
    st.info(
        "This tool is a planning aid for team-level workload conversations. "
        "It is not an individual performance measurement system."
    )
    st.caption(
        "Privacy note: use role labels, pools, or anonymised entries. Do not enter "
        "sensitive personal information, HR information, health information, or "
        "individual performance notes."
    )
    st.warning(
        "For public or shared deployments, use synthetic or non-sensitive data only. "
        "Generic role labels are safer than staff names."
    )
    show_assumptions_panel()

    if "builder_people_df" not in st.session_state:
        st.session_state["builder_people_df"] = get_default_people_entries()
    if "builder_work_df" not in st.session_state:
        st.session_state["builder_work_df"] = get_default_work_items()

    task_templates_df, task_subtasks_df, task_library_messages = load_task_estimate_library()
    for message in task_library_messages:
        st.warning(message)

    with st.expander("1. Intro and planning principles", expanded=True):
        st.markdown(
            """
Use this builder to sketch baseline capacity, assigned work, and uncertainty before
you run scenario changes. Keep entries at a team, role, or workstream level where
possible.
            """
        )

    with st.expander("2. Team profile", expanded=True):
        profile = get_builder_profile_inputs()

    with st.expander("3. People and availability", expanded=True):
        people_df = st.data_editor(
            st.session_state["builder_people_df"],
            width="stretch",
            num_rows="dynamic",
            column_config={
                "entry_label": st.column_config.TextColumn(
                    "Staff or role label", required=True
                ),
                "simulator_role": st.column_config.SelectboxColumn(
                    "Simulator role", options=ROLES, required=True
                ),
                "employment_type": st.column_config.SelectboxColumn(
                    "Full-time/part-time",
                    options=["Full-time", "Part-time", "Role pool", "Other"],
                    required=True,
                ),
                "fte": st.column_config.NumberColumn(
                    "FTE", min_value=0.01, max_value=20.0, step=0.1, required=True
                ),
                "availability_pct": st.column_config.NumberColumn(
                    "Availability %",
                    min_value=0.0,
                    max_value=100.0,
                    step=5.0,
                    required=True,
                ),
                "notes": st.column_config.TextColumn("Notes"),
            },
            key="builder_people_editor",
        )
        st.session_state["builder_people_df"] = people_df

    with st.expander("4. Assigned work", expanded=True):
        show_task_estimate_library(profile, task_templates_df, task_subtasks_df)
        st.markdown("##### Manual assigned work")
        work_df = st.data_editor(
            st.session_state["builder_work_df"],
            width="stretch",
            num_rows="dynamic",
            column_config={
                "work_title": st.column_config.TextColumn("Work title", required=True),
                "work_type": st.column_config.SelectboxColumn(
                    "Work type", options=WORK_TYPES, required=True
                ),
                "start_month": st.column_config.TextColumn(
                    "Start month", help="Use YYYY-MM format.", required=True
                ),
                "end_month": st.column_config.TextColumn(
                    "End month", help="Use YYYY-MM format.", required=True
                ),
                "estimated_hours": st.column_config.NumberColumn(
                    "Estimated hours",
                    min_value=0.0,
                    max_value=100000.0,
                    step=10.0,
                    required=True,
                ),
                "priority": st.column_config.SelectboxColumn(
                    "Priority", options=PRIORITY_LEVELS, required=True
                ),
                "confidence": st.column_config.SelectboxColumn(
                    "Confidence", options=CONFIDENCE_LEVELS, required=True
                ),
                "notes": st.column_config.TextColumn("Notes"),
            },
            key="builder_work_editor",
        )
        st.session_state["builder_work_df"] = work_df

    errors, warnings, period_months = validate_builder_inputs(profile, people_df, work_df)
    if errors:
        st.subheader("Validation")
        for error in errors:
            st.error(error)
    for warning in warnings:
        st.warning(warning)

    if errors:
        return None

    canonical_model = build_guided_capacity_data(profile, people_df, work_df, period_months)
    st.session_state["canonical_model"] = canonical_model

    st.markdown("#### 5. Review")
    show_canonical_review(canonical_model, expanded=True)

    st.success("Guided baseline is ready for the dashboard and scenario simulator.")
    return canonical_model


def initialise_scenario_state(baseline_df, capacity_df):
    baseline_signature = (
        pd.util.hash_pandas_object(baseline_df, index=True).sum(),
        pd.util.hash_pandas_object(capacity_df, index=True).sum(),
    )
    baseline_changed = st.session_state.get("baseline_signature") != baseline_signature
    if baseline_changed:
        st.session_state["baseline_signature"] = baseline_signature
        st.session_state["scenario_df"] = baseline_df.copy()
        st.session_state["scenario_capacity_df"] = capacity_df.copy()
        st.session_state["scenario_name"] = "No scenario built"
        st.session_state["scenario_detail_df"] = pd.DataFrame()
        st.session_state["uncertainty_flag"] = False
    if "scenario_df" not in st.session_state:
        st.session_state["scenario_df"] = baseline_df.copy()
    if "scenario_capacity_df" not in st.session_state:
        st.session_state["scenario_capacity_df"] = capacity_df.copy()
    if "scenario_name" not in st.session_state:
        st.session_state["scenario_name"] = "No scenario built"
    if "scenario_detail_df" not in st.session_state:
        st.session_state["scenario_detail_df"] = pd.DataFrame()
    if "uncertainty_flag" not in st.session_state:
        st.session_state["uncertainty_flag"] = False
    update_scenario_impact_state(
        baseline_df,
        st.session_state["scenario_df"],
        capacity_df,
        st.session_state["scenario_capacity_df"],
    )


def update_scenario_impact_state(
    baseline_df,
    scenario_df,
    capacity_df,
    scenario_capacity_df=None,
):
    summary_df, role_delta_df, work_type_delta_df = calculate_scenario_impact(
        baseline_df,
        scenario_df,
        capacity_df,
        st.session_state.get("uncertainty_flag", False),
        scenario_capacity_df,
    )
    st.session_state["scenario_summary_df"] = summary_df
    st.session_state["role_delta_df"] = role_delta_df
    st.session_state["work_type_delta_df"] = work_type_delta_df
    if "canonical_model" in st.session_state and not summary_df.empty:
        summary = summary_df.iloc[0]
        st.session_state["canonical_model"]["scenario_adjustments"] = pd.DataFrame(
            [
                {
                    "scenario_name": st.session_state.get(
                        "scenario_name", "No scenario built"
                    ),
                    "baseline_total_hours": summary["baseline_total_hours"],
                    "scenario_total_hours": summary["scenario_total_hours"],
                    "hours_delta": summary["hours_delta"],
                    "percentage_delta": summary["percentage_delta"],
                    "uncertainty_flag": bool(summary["uncertainty_flag"]),
                }
            ]
        )


def show_baseline_current_state_tab(filtered_df, capacity_df, software_df):
    if filtered_df.empty:
        st.info("No workload rows match the current filters.")
        return

    role_pressure_df = calculate_role_pressure(filtered_df, capacity_df)
    committed = role_pressure_df["committed_hours"].sum()
    available = role_pressure_df["available_hours"].sum()
    remaining = available - committed

    gauge_col, card_col = st.columns([1.1, 1.5])
    with gauge_col:
        st.plotly_chart(
            make_gauge(committed, available, "Baseline utilisation"),
            width="stretch",
        )
    with card_col:
        cols = st.columns(3)
        cols[0].metric("Committed hours", format_hours(committed))
        cols[1].metric("Available hours", format_hours(available))
        cols[2].metric("Remaining capacity", format_hours(remaining))
        cols = st.columns(3)
        cols[0].metric("Utilisation", f"{committed / available * 100 if available else 0:.1f}%")
        cols[1].metric("Workload rows", len(filtered_df))
        cols[2].metric("Low-confidence rows", int((filtered_df["confidence"] == "Low").sum()))

    left, right = st.columns(2)
    with left:
        st.subheader("Role pressure")
        st.plotly_chart(make_role_pressure_chart(role_pressure_df), width="stretch")
    with right:
        st.subheader("Workload composition")
        st.plotly_chart(make_composition_chart(filtered_df), width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("Software burden")
        st.plotly_chart(make_software_burden_chart(filtered_df), width="stretch")
    with right:
        st.subheader("Top 10 workload drivers")
        show_top_workload_drivers(filtered_df)

    st.subheader("Work type by role")
    st.plotly_chart(make_work_type_heatmap(filtered_df), width="stretch")

    st.subheader("Support portfolio map")
    show_support_portfolio_map(software_df, filtered_df)

    st.download_button(
        "Download filtered baseline workload",
        data=convert_df_to_csv(filtered_df),
        file_name="filtered_baseline_workload.csv",
        mime="text/csv",
        key="baseline_tab_filtered_download",
    )


def show_scenario_builder_tab(baseline_df, software_df, templates_df, capacity_df):
    st.markdown("Build one intervention, then inspect its impact in the next tab.")
    scenario_type = st.selectbox("Scenario type", SCENARIO_TYPES)

    scenario_df = baseline_df.copy()
    scenario_capacity_df = capacity_df.copy()
    detail_df = pd.DataFrame()
    scenario_name = scenario_type
    uncertainty_flag = False

    if scenario_type == "Introduce software":
        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("New software name", "New supported platform")
            support_level = st.selectbox("Support level", SUPPORT_LEVELS)
            criticality = st.selectbox("Criticality", CRITICALITY_LEVELS, index=2)
        with col2:
            adoption_level = st.selectbox("Adoption level", ADOPTION_LEVELS, index=2)
            vendor_complexity = st.selectbox("Vendor complexity", COMPLEXITY_LEVELS, index=1)
            configuration_complexity = st.selectbox(
                "Configuration complexity", COMPLEXITY_LEVELS, index=1
            )
        with col3:
            integration_complexity = st.selectbox(
                "Integration complexity", COMPLEXITY_LEVELS, index=1
            )
            lifecycle_phase = st.selectbox(
                "Lifecycle phase",
                ["Pilot", "Implementation", "BAU support", "Major update"],
            )
            demand_multiplier = st.number_input(
                "Demand multiplier", min_value=0.1, max_value=5.0, value=1.0, step=0.1
            )
            confidence = st.selectbox("Confidence level", CONFIDENCE_LEVELS, index=1)

        available_templates = templates_df[
            (templates_df["scenario_type"] == "Introduce software")
            & (templates_df["lifecycle_phase"] == lifecycle_phase)
        ]
        selected_ids = select_templates(available_templates)
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_introduce_software_scenario(
            baseline_df,
            templates_df,
            new_name,
            support_level,
            criticality,
            adoption_level,
            vendor_complexity,
            configuration_complexity,
            integration_complexity,
            lifecycle_phase,
            selected_ids,
            demand_multiplier,
            confidence,
        )

    elif scenario_type == "Remove software":
        selected = st.multiselect(
            "Existing tools to remove",
            sorted(baseline_df["software_name"].dropna().unique().tolist()),
        )
        removal_mode = st.radio(
            "Removal mode",
            ["immediate removal", "phased removal", "retire with transition support"],
            horizontal=True,
        )
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_remove_software_scenario(
            baseline_df, templates_df, selected, removal_mode
        )

    elif scenario_type == "Consolidate software":
        selected = st.multiselect(
            "Tools to consolidate",
            sorted(baseline_df["software_name"].dropna().unique().tolist()),
        )
        destination = st.text_input("Destination or replacement tool", "Consolidated platform")
        intensity = st.radio(
            "Consolidation intensity", ["light", "moderate", "complex"], horizontal=True
        )
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_consolidate_software_scenario(
            baseline_df, templates_df, selected, destination, intensity
        )

    elif scenario_type == "Reduce support level":
        selected = st.selectbox(
            "Existing tool",
            sorted(baseline_df["software_name"].dropna().unique().tolist()),
        )
        new_level = st.selectbox("New support level", SUPPORT_LEVELS, index=2)
        st.caption(
            "Multipliers: "
            + ", ".join(
                f"{level} = {multiplier:.2f}"
                for level, multiplier in SUPPORT_LEVEL_MULTIPLIERS.items()
            )
        )
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_reduce_support_level_scenario(
            baseline_df, selected, new_level
        )

    elif scenario_type == "Increase adoption":
        selected = st.selectbox(
            "Existing tool",
            sorted(baseline_df["software_name"].dropna().unique().tolist()),
        )
        increase_pct = st.radio("Adoption increase", [10, 20, 50, 100], horizontal=True)
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_increase_adoption_scenario(
            baseline_df, selected, increase_pct
        )

    elif scenario_type == "Project to BAU":
        candidates = sorted(
            set(
                baseline_df.loc[
                    baseline_df["work_group"].isin(["Project", "Change", "Scenario"]),
                    "software_name",
                ].dropna()
            )
            | set(
                software_df.loc[
                    software_df["support_status"].isin(["Project", "Proposed", "Pilot"]),
                    "software_name",
                ].dropna()
            )
        )
        selected = st.selectbox("Project or proposed tool", candidates or ["No project rows"])
        support_level = st.selectbox("BAU support level", SUPPORT_LEVELS, index=1)
        intensity = st.radio("Recurring support intensity", ["Light", "Moderate", "High"], horizontal=True)
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_project_to_bau_scenario(
            baseline_df, templates_df, selected, support_level, intensity
        )

    elif scenario_type == "Demand spike":
        selected_work_types = st.multiselect(
            "Work types affected",
            WORK_TYPES,
            default=["User training", "Consultation", "Helpdesk support"],
        )
        increase_pct = st.slider("Temporary demand increase percentage", 10, 150, 50, 10)
        duration_months = st.slider("Duration in months", 1, 12, 3)
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_demand_spike_scenario(
            baseline_df, selected_work_types, increase_pct, duration_months
        )

    elif scenario_type == "Decommission tool":
        selected = st.selectbox(
            "Tool to decommission",
            sorted(baseline_df["software_name"].dropna().unique().tolist()),
        )
        transition_months = st.slider("Transition period in months", 1, 18, 6)
        confidence = st.selectbox("Confidence level", CONFIDENCE_LEVELS, index=1)
        scenario_df, scenario_name, detail_df, uncertainty_flag = build_decommission_tool_scenario(
            baseline_df, templates_df, selected, transition_months, confidence
        )

    elif scenario_type == "Capacity change":
        selected_role = st.selectbox("Role affected", ROLES)
        fte_delta = st.number_input(
            "FTE change",
            min_value=-3.0,
            max_value=3.0,
            value=-0.5,
            step=0.1,
            help="Use negative values for capacity loss and positive values for added capacity.",
        )
        scenario_df, scenario_capacity_df, scenario_name, detail_df, uncertainty_flag = (
            build_capacity_change_scenario(
                baseline_df,
                capacity_df,
                selected_role,
                fte_delta,
            )
        )

    st.session_state["scenario_df"] = scenario_df
    st.session_state["scenario_capacity_df"] = scenario_capacity_df
    st.session_state["scenario_name"] = scenario_name
    st.session_state["scenario_detail_df"] = detail_df
    st.session_state["uncertainty_flag"] = uncertainty_flag
    update_scenario_impact_state(
        baseline_df, scenario_df, capacity_df, scenario_capacity_df
    )

    st.subheader("Scenario preview")
    summary_df = st.session_state["scenario_summary_df"]
    show_summary_cards(summary_df)
    if detail_df.empty:
        st.info("This scenario has no matching rows yet. Check the inputs or select task templates.")
    else:
        st.dataframe(detail_df, width="stretch", hide_index=True)


def select_templates(templates_df):
    if templates_df.empty:
        st.warning("No templates match this scenario type and lifecycle phase.")
        return []
    labels = {
        f"{row.template_id} - {row.task_name} ({row.work_type})": row.template_id
        for row in templates_df.itertuples()
    }
    selected_labels = st.multiselect(
        "Applicable task templates",
        options=list(labels.keys()),
        default=list(labels.keys()),
    )
    return [labels[label] for label in selected_labels]


def show_scenario_impact_tab(baseline_df, capacity_df):
    scenario_df = st.session_state.get("scenario_df", baseline_df)
    scenario_name = st.session_state.get("scenario_name", "No scenario built")
    summary_df = st.session_state["scenario_summary_df"]
    role_delta_df = st.session_state["role_delta_df"]
    work_type_delta_df = st.session_state["work_type_delta_df"]

    st.caption(f"Active scenario: {scenario_name}")
    show_summary_cards(summary_df)

    left, right = st.columns(2)
    with left:
        st.subheader("Before/after role pressure")
        st.plotly_chart(make_before_after_role_chart(role_delta_df), width="stretch")
    with right:
        summary = summary_df.iloc[0]
        st.subheader("Scenario utilisation")
        st.plotly_chart(
            make_gauge(
                summary["scenario_total_hours"],
                role_delta_df["available_hours"].sum(),
                "Scenario utilisation",
            ),
            width="stretch",
        )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            make_delta_chart(
                role_delta_df,
                "role",
                "role_hours_delta",
                "Scenario delta by role",
            ),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            make_delta_chart(
                work_type_delta_df.head(12),
                "work_type",
                "work_type_hours_delta",
                "Scenario delta by work type",
            ),
            width="stretch",
        )

    st.subheader("Scenario impact table")
    st.dataframe(role_delta_df, width="stretch", hide_index=True)

    st.subheader("Scenario-adjusted workload")
    st.dataframe(scenario_df, width="stretch", hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download scenario-adjusted workload",
            data=convert_df_to_csv(scenario_df),
            file_name="scenario_adjusted_workload.csv",
            mime="text/csv",
            key="impact_tab_adjusted_download",
        )
    with col2:
        st.download_button(
            "Download scenario impact summary",
            data=build_summary_download(summary_df, role_delta_df, work_type_delta_df),
            file_name="scenario_impact_summary.csv",
            mime="text/csv",
            key="impact_tab_summary_download",
        )


def build_summary_download(summary_df, role_delta_df, work_type_delta_df):
    buffer = io.StringIO()
    summary_df.to_csv(buffer, index=False)
    buffer.write("\nRole impact\n")
    role_delta_df.to_csv(buffer, index=False)
    buffer.write("\nWork type impact\n")
    work_type_delta_df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def show_leadership_interpretation_tab(baseline_df, capacity_df):
    scenario_df = st.session_state.get("scenario_df", baseline_df)
    scenario_name = st.session_state.get("scenario_name", "No scenario built")
    summary_df = st.session_state["scenario_summary_df"]
    role_delta_df = st.session_state["role_delta_df"]
    work_type_delta_df = st.session_state["work_type_delta_df"]
    prompts = generate_leadership_prompts(
        scenario_name,
        baseline_df,
        scenario_df,
        capacity_df,
        summary_df,
        role_delta_df,
        work_type_delta_df,
    )
    for prompt in prompts:
        st.info(prompt)

    st.subheader("Evidence behind the interpretation")
    left, right = st.columns(2)
    with left:
        st.dataframe(
            role_delta_df.sort_values("revised_utilisation_pct", ascending=False),
            width="stretch",
            hide_index=True,
        )
    with right:
        changed = work_type_delta_df[
            work_type_delta_df["work_type_hours_delta"].abs() > 0
        ].copy()
        st.dataframe(changed.head(10), width="stretch", hide_index=True)


def show_ai_interpretation_tab(baseline_df, capacity_df):
    canonical_model = st.session_state.get("canonical_model")
    if not canonical_model:
        st.info("Complete the baseline builder or load CSV data before using AI interpretation.")
        return

    st.subheader("Optional AI-assisted interpretation")
    st.warning(
        "This optional feature sends a minimized workload summary to OpenAI. "
        "It does not send staff names, raw uploaded files, free-text notes, raw work item titles, "
        "or software names. Do not use the output for individual performance management."
    )
    st.caption(
        "The AI output is draft reflection material only. It may be incomplete or wrong. "
        "Human judgement is required for all decisions."
    )

    ai_summary = build_ai_summary_object(canonical_model, baseline_df, capacity_df)
    summary_valid, summary_message = validate_ai_summary(ai_summary)
    if not summary_valid:
        st.error(summary_message)
        return

    with st.expander("Review the minimized summary that would be sent", expanded=False):
        st.json(ai_summary, expanded=False)

    api_key = get_openai_api_key()
    model = get_openai_model()
    if not api_key:
        st.info(
            "AI interpretation is not configured. The simulator still works without AI. "
            "Add `OPENAI_API_KEY` in Streamlit secrets to enable this optional feature."
        )
        st.code(
            'OPENAI_API_KEY = "your-key-here"\n# Optional:\nOPENAI_MODEL = "gpt-5"',
            language="toml",
        )
        return

    st.caption(f"Configured model: `{model}`")
    if st.button("Generate cautious AI interpretation"):
        with st.spinner("Generating cautious interpretation..."):
            try:
                ai_text = generate_ai_interpretation(ai_summary, api_key, model)
            except Exception as error:
                st.error(
                    "The AI interpretation request failed. Your workload data has not "
                    "been changed. Please try again later or use the rule-based "
                    "Leadership Interpretation tab."
                )
                st.caption(f"Technical detail: {error}")
                return
        st.session_state["ai_interpretation_text"] = ai_text
        st.session_state["ai_interpretation_summary"] = ai_summary

    ai_text = st.session_state.get("ai_interpretation_text", "")
    if ai_text:
        st.subheader("AI-assisted interpretation")
        st.markdown(ai_text)
        st.download_button(
            "Download AI interpretation",
            data=build_ai_interpretation_markdown(ai_text, ai_summary),
            file_name="ai_interpretation.md",
            mime="text/markdown",
            key="ai_interpretation_download",
        )
        st.info(
            "Reminder: this is a planning aid. Treat the output as a starting point "
            "for discussion, not as a decision or objective assessment."
        )


def show_scenario_decision_matrix_tab(baseline_df, capacity_df):
    st.subheader("Scenario Decision Matrix")
    st.caption(
        "Compare options using transparent, human-entered favourability scores. "
        "The matrix calculates scores; people still make the decision."
    )
    st.warning(
        "Use synthetic or non-sensitive scenario labels and descriptions in shared deployments. "
        "Do not enter sensitive staff, HR, health, or confidential operational details."
    )

    if "decision_question" not in st.session_state:
        st.session_state["decision_question"] = (
            "Which software-support scenario is most suitable for the current planning period?"
        )
    if "decision_scenarios_df" not in st.session_state:
        st.session_state["decision_scenarios_df"] = get_default_decision_scenarios()
    if "decision_criteria_df" not in st.session_state:
        st.session_state["decision_criteria_df"] = get_default_decision_criteria()
    if "decision_scores_df" not in st.session_state:
        st.session_state["decision_scores_df"] = get_default_decision_scores(
            st.session_state["decision_scenarios_df"],
            st.session_state["decision_criteria_df"],
        )

    st.markdown("#### Decision question")
    decision_question = st.text_input(
        "Decision question",
        value=st.session_state["decision_question"],
        help="Frame the comparison as the leadership question you are trying to answer.",
        key="decision_question_input",
    )
    st.session_state["decision_question"] = decision_question

    summary_df = st.session_state.get("scenario_summary_df", pd.DataFrame())
    scenario_name = st.session_state.get("scenario_name", "No scenario built")
    if not summary_df.empty:
        scenario_summary = summary_df.iloc[0]
        impact_note = (
            f"{scenario_name}: baseline {scenario_summary['baseline_total_hours']:.0f} hours, "
            f"scenario {scenario_summary['scenario_total_hours']:.0f} hours, "
            f"delta {scenario_summary['hours_delta']:.0f} hours "
            f"({scenario_summary['percentage_delta']:.1f}%)."
        )
        st.info(
            "Current Scenario Impact output is available. You can copy this into "
            f"the matrix workload impact or notes: {impact_note}"
        )
        if st.button("Add current simulator scenario to matrix"):
            scenarios_df = st.session_state["decision_scenarios_df"].copy()
            new_row = {
                "scenario_name": scenario_name,
                "short_description": "Scenario imported from the workload simulator.",
                "scenario_type": "Other"
                if scenario_name == "No scenario built"
                else scenario_name.split(" - ")[0],
                "expected_workload_impact": impact_note,
                "implementation_effort": "Check scenario assumptions",
                "recurring_bau_burden": "Check scenario assumptions",
                "risk_level": "Check scenario assumptions",
                "confidence_level": "Low"
                if bool(scenario_summary.get("uncertainty_flag", False))
                else "Medium",
                "notes": "Imported as summary text only; review before using.",
            }
            scenarios_df = scenarios_df[
                scenarios_df["scenario_name"].fillna("").astype(str).str.strip()
                != scenario_name
            ]
            scenarios_df = pd.concat(
                [scenarios_df, pd.DataFrame([new_row])], ignore_index=True
            )
            st.session_state["decision_scenarios_df"] = scenarios_df
            st.session_state["decision_scores_df"] = align_decision_scores(
                st.session_state["decision_scores_df"],
                scenarios_df,
                st.session_state["decision_criteria_df"],
            )
            st.rerun()

    st.markdown("#### 1. Scenarios to compare")
    scenarios_df = st.data_editor(
        st.session_state["decision_scenarios_df"],
        width="stretch",
        num_rows="dynamic",
        column_config={
            "scenario_name": st.column_config.TextColumn("Scenario name", required=True),
            "short_description": st.column_config.TextColumn(
                "Short description", help="Use non-sensitive summary wording."
            ),
            "scenario_type": st.column_config.SelectboxColumn(
                "Scenario type", options=DECISION_SCENARIO_TYPES, required=True
            ),
            "expected_workload_impact": st.column_config.TextColumn(
                "Expected workload impact"
            ),
            "implementation_effort": st.column_config.TextColumn(
                "Implementation effort"
            ),
            "recurring_bau_burden": st.column_config.TextColumn(
                "Recurring BAU burden"
            ),
            "risk_level": st.column_config.TextColumn("Risk level"),
            "confidence_level": st.column_config.SelectboxColumn(
                "Confidence level", options=CONFIDENCE_LEVELS, required=True
            ),
            "notes": st.column_config.TextColumn(
                "Optional notes", help="Notes stay local and are not sent to AI."
            ),
        },
        key="decision_scenarios_editor",
    )
    st.session_state["decision_scenarios_df"] = scenarios_df

    st.markdown("#### 2. Decision criteria and weights")
    st.caption(
        "Weights should total 100%. Scoring is always favourability scoring: "
        "1 = weak/unfavourable, 5 = very strong/favourable."
    )
    criteria_df = st.session_state["decision_criteria_df"].copy()
    active_weight_total = get_active_decision_criteria(criteria_df)["weight_pct"].sum()
    cols = st.columns([1, 2])
    with cols[0]:
        st.metric("Active weight total", f"{active_weight_total:.1f}%")
    with cols[1]:
        if st.button("Normalise active weights to 100%"):
            st.session_state["decision_criteria_df"] = normalise_decision_weights(
                criteria_df
            )
            st.session_state["decision_scores_df"] = align_decision_scores(
                st.session_state["decision_scores_df"],
                scenarios_df,
                st.session_state["decision_criteria_df"],
            )
            st.rerun()

    criteria_df = st.data_editor(
        st.session_state["decision_criteria_df"],
        width="stretch",
        num_rows="dynamic",
        column_config={
            "criterion": st.column_config.TextColumn("Criterion", required=True),
            "enabled": st.column_config.CheckboxColumn("Use", default=True),
            "weight_pct": st.column_config.NumberColumn(
                "Weight %",
                min_value=0.0,
                max_value=100.0,
                step=5.0,
                required=True,
            ),
            "favourability_guidance": st.column_config.TextColumn(
                "Favourability guidance"
            ),
        },
        key="decision_criteria_editor",
    )
    st.session_state["decision_criteria_df"] = criteria_df

    st.markdown("#### 3. Scenario scoring")
    active_criteria = get_active_decision_criteria(criteria_df)
    score_guidance = [
        "1 = weak / unfavourable",
        "2 = limited",
        "3 = moderate",
        "4 = strong",
        "5 = very strong / favourable",
    ]
    st.caption("; ".join(score_guidance))
    with st.expander("Favourability guidance for lower-is-better criteria"):
        st.markdown(
            """
- Workload impact score 5 = manageable workload impact / highly favourable.
- Risk score 5 = low risk / highly favourable.
- Cost score 5 = low cost / highly favourable.
- Complexity score 5 = low complexity / highly favourable.
- Implementation effort score 5 = low implementation effort / highly favourable.
- Recurring BAU burden score 5 = low recurring BAU burden / highly favourable.
- Opportunity cost score 5 = low opportunity cost / highly favourable.
            """
        )

    scores_df = align_decision_scores(
        st.session_state["decision_scores_df"], scenarios_df, criteria_df
    )
    score_column_config = {"scenario_name": st.column_config.TextColumn("Scenario")}
    for criterion in active_criteria["criterion"].tolist():
        score_column_config[criterion] = st.column_config.NumberColumn(
            criterion, min_value=1, max_value=5, step=1, required=True
        )
    scores_df = st.data_editor(
        scores_df,
        width="stretch",
        hide_index=True,
        disabled=["scenario_name"],
        column_config=score_column_config,
        key="decision_scores_editor",
    )
    st.session_state["decision_scores_df"] = scores_df

    errors, warnings = validate_decision_matrix_inputs(
        decision_question, scenarios_df, criteria_df, scores_df
    )
    for warning in warnings:
        st.warning(warning)
    if errors:
        for error in errors:
            st.error(error)
        return

    results_df, contribution_df = calculate_decision_matrix_scores(
        scenarios_df, criteria_df, scores_df
    )
    recommendation_text = build_decision_recommendation_summary(
        results_df, contribution_df
    )
    comparison_summary = build_decision_comparison_summary_object(
        decision_question,
        scenarios_df,
        criteria_df,
        results_df,
        contribution_df,
    )
    st.session_state["decision_comparison_summary"] = comparison_summary

    st.markdown("#### 4. Results")
    left, right = st.columns([1, 1.2])
    with left:
        st.subheader("Ranked scenarios")
        st.dataframe(
            results_df,
            width="stretch",
            hide_index=True,
            column_config={
                "total_weighted_score": st.column_config.NumberColumn(
                    "Total weighted score", format="%.2f"
                )
            },
        )
    with right:
        st.subheader("Visual comparison")
        st.plotly_chart(make_decision_score_chart(results_df), width="stretch")

    st.subheader("Criterion-by-criterion scoring")
    st.dataframe(
        contribution_df,
        width="stretch",
        hide_index=True,
        column_config={
            "score": st.column_config.NumberColumn("Score", format="%.0f"),
            "weight_pct": st.column_config.NumberColumn("Weight %", format="%.1f"),
            "weighted_score": st.column_config.NumberColumn(
                "Weighted score", format="%.2f"
            ),
        },
    )

    st.subheader("Recommendation summary")
    st.markdown(recommendation_text)

    st.subheader("Decision prompts")
    for prompt in DECISION_PROMPTS:
        st.info(prompt)

    st.subheader("Optional AI reflection on this comparison")
    st.caption(
        "The AI does not calculate scores or make the decision. It receives only a "
        "summarised comparison object: decision question, scenario names and short "
        "descriptions, active criteria and weights, ranked scores, trade-offs, and caveats."
    )
    with st.expander("Review the comparison summary that would be sent", expanded=False):
        st.json(comparison_summary, expanded=False)

    decision_ai_valid, decision_ai_message = validate_decision_ai_summary(
        comparison_summary
    )
    api_key = get_openai_api_key()
    model = get_openai_model()
    if not decision_ai_valid:
        st.error(decision_ai_message)
    elif not api_key:
        st.info(
            "AI comparison interpretation is not configured. The decision matrix "
            "still works without AI. Add `OPENAI_API_KEY` in Streamlit secrets to "
            "enable optional AI reflection."
        )
    else:
        st.caption(f"Configured model: `{model}`")
        if st.button("Generate cautious AI interpretation of comparison"):
            with st.spinner("Generating cautious comparison reflection..."):
                try:
                    decision_ai_text = generate_ai_decision_interpretation(
                        comparison_summary, api_key, model
                    )
                except Exception as error:
                    st.error(
                        "The AI comparison request failed. The decision matrix has "
                        "not been changed. Please use the non-AI recommendation "
                        "summary and try again later."
                    )
                    st.caption(f"Technical detail: {error}")
                    decision_ai_text = ""
                if decision_ai_text:
                    st.session_state["decision_ai_interpretation_text"] = (
                        decision_ai_text
                    )

    decision_ai_text = st.session_state.get("decision_ai_interpretation_text", "")
    if decision_ai_text:
        st.markdown("##### AI comparison interpretation")
        st.markdown(decision_ai_text)
        st.info(
            "Reminder: this output is reflective only. It should not be treated as "
            "a decision, instruction, or objective assessment."
        )

    st.download_button(
        "Download decision matrix summary",
        data=build_decision_matrix_markdown(
            decision_question,
            scenarios_df,
            criteria_df,
            scores_df,
            results_df,
            recommendation_text,
            decision_ai_text,
        ),
        file_name="scenario_decision_matrix_summary.md",
        mime="text/markdown",
        key="decision_matrix_summary_download",
    )


def show_data_tables_tab(
    filtered_df,
    baseline_df,
    software_df,
    capacity_df,
    templates_df,
):
    scenario_df = st.session_state.get("scenario_df", baseline_df)
    scenario_capacity_df = st.session_state.get("scenario_capacity_df", capacity_df)
    summary_df = st.session_state["scenario_summary_df"]
    canonical_model = st.session_state.get("canonical_model", {})

    st.subheader("Filtered baseline workload")
    st.dataframe(filtered_df, width="stretch", hide_index=True)
    st.download_button(
        "Download filtered baseline workload",
        data=convert_df_to_csv(filtered_df),
        file_name="filtered_baseline_workload.csv",
        mime="text/csv",
        key="data_tab_filtered_download",
    )

    st.subheader("Baseline workload data")
    st.dataframe(baseline_df, width="stretch", hide_index=True)

    st.subheader("Supported software data")
    st.dataframe(software_df, width="stretch", hide_index=True)

    st.subheader("Team capacity data")
    st.dataframe(capacity_df, width="stretch", hide_index=True)

    if canonical_model:
        st.subheader("People / role availability")
        st.dataframe(
            canonical_model["people_availability"], width="stretch", hide_index=True
        )

        st.subheader("Assigned work items")
        st.dataframe(
            canonical_model["assigned_work_items"], width="stretch", hide_index=True
        )

        st.subheader("Monthly workload")
        st.dataframe(canonical_model["monthly_workload"], width="stretch", hide_index=True)

        st.subheader("Scenario adjustments")
        st.dataframe(
            canonical_model["scenario_adjustments"], width="stretch", hide_index=True
        )
        st.download_button(
            "Download planning summary",
            data=build_planning_summary_markdown(canonical_model),
            file_name="planning_summary.md",
            mime="text/markdown",
            key="data_tab_planning_summary_download",
        )

    st.subheader("Scenario capacity data")
    st.dataframe(scenario_capacity_df, width="stretch", hide_index=True)

    st.subheader("Scenario task templates")
    st.dataframe(templates_df, width="stretch", hide_index=True)

    st.subheader("Scenario-adjusted workload data")
    st.dataframe(scenario_df, width="stretch", hide_index=True)
    st.download_button(
        "Download scenario-adjusted workload",
        data=convert_df_to_csv(scenario_df),
        file_name="scenario_adjusted_workload.csv",
        mime="text/csv",
        key="data_tab_adjusted_download",
    )

    st.subheader("Scenario summary table")
    st.dataframe(summary_df, width="stretch", hide_index=True)
    st.download_button(
        "Download scenario impact summary",
        data=build_summary_download(
            summary_df,
            st.session_state["role_delta_df"],
            st.session_state["work_type_delta_df"],
        ),
        file_name="scenario_impact_summary.csv",
        mime="text/csv",
        key="data_tab_summary_download",
    )


def show_schema_beginner_notes_tab():
    st.subheader("Data schema")
    schema = {
        "sample_data/sample_team_capacity.csv": TEAM_CAPACITY_REQUIRED_COLUMNS,
        "sample_data/sample_supported_software.csv": SUPPORTED_SOFTWARE_REQUIRED_COLUMNS,
        "sample_data/sample_baseline_workload.csv": BASELINE_WORKLOAD_REQUIRED_COLUMNS,
        "sample_data/sample_scenario_task_templates.csv": SCENARIO_TEMPLATE_REQUIRED_COLUMNS,
        "sample_data/task_time_templates.csv": TASK_TIME_TEMPLATE_REQUIRED_COLUMNS,
        "sample_data/task_time_subtasks.csv": TASK_TIME_SUBTASK_REQUIRED_COLUMNS,
    }
    for file_name, columns in schema.items():
        with st.expander(
            file_name, expanded=file_name == "sample_data/sample_baseline_workload.csv"
        ):
            st.dataframe(pd.DataFrame({"required_column": columns}), hide_index=True)

    st.subheader("Beginner notes")
    st.markdown(
        """
- The four CSV files connect through `software_id`. The software table describes the portfolio; the workload table describes annual workload rows for each tool.
- Team capacity is calculated as `fte x usable_hours_per_fte_per_year` when `available_hours_year` is blank or zero.
- Workload hours are calculated as `annual_volume x hours_per_unit` unless an explicit role total is supplied.
- Scenario templates are reusable assumptions. The builder turns selected templates into scenario workload rows.
- Task estimate templates are sanitised planning estimates. They can prefill assigned work rows in the Baseline Capacity Builder.
- Support-level multipliers reduce or expand the workload estimate for support intensity.
- Demand multipliers change annual volume or annualised spike pressure.
- Overload status comes from role utilisation: below 85% is under capacity, 85% to 100% is near capacity, 100% to 115% is over capacity, and above 115% is significantly over capacity.
- Leadership prompts are plain Python rules. They inspect role pressure, scenario deltas, work type changes, and low-confidence assumptions.
- Edit the sample CSV files in `sample_data/` to change the demo model. Edit the lists and multipliers near the top of `app.py` to add work types or change scenario rules.
        """
    )


def apply_style():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem;}
        div[data-testid="stMetric"] {
            background: #f7f9fc;
            border: 1px solid #e3e8ef;
            border-radius: 8px;
            padding: 0.8rem 1rem;
        }
        h1, h2, h3 {color: #18344f;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    apply_style()
    st.title("Software Support Scenario Simulator")
    st.caption(
        "Baseline -> Intervention -> Impact -> Interpretation for software support workload planning."
    )
    st.info(
        "Appropriate use: this simulator supports team planning conversations. "
        "It should not be used as a performance management system or as a store for "
        "sensitive personal information."
    )
    show_sidebar_demo_controls()

    data_source = st.sidebar.radio(
        "Baseline data source",
        ["Guided builder", "CSV upload or sample data"],
        help="Use the guided builder in this session, or continue with the existing CSV pathway.",
    )
    (
        raw_capacity_df,
        raw_software_df,
        raw_workload_df,
        raw_templates_df,
        sources,
    ) = get_uploaded_data()

    templates_valid = validate_scenario_task_templates(raw_templates_df)
    if not templates_valid:
        st.stop()
    templates_df = prepare_scenario_task_templates(raw_templates_df)

    if data_source == "Guided builder":
        canonical_model = show_guided_builder()
        if canonical_model is None:
            st.stop()
        capacity_df = canonical_model["team_capacity"]
        software_df = canonical_model["software_portfolio"]
        baseline_df = canonical_model["baseline_workload"]
    else:
        valid = all(
            [
                validate_team_capacity(raw_capacity_df),
                validate_supported_software(raw_software_df),
                validate_baseline_workload(raw_workload_df),
            ]
        )
        if not valid:
            st.stop()

        canonical_model = build_csv_canonical_data_model(
            raw_capacity_df,
            raw_software_df,
            raw_workload_df,
            sources["capacity"],
        )
        st.session_state["canonical_model"] = canonical_model
        capacity_df = canonical_model["team_capacity"]
        software_df = canonical_model["software_portfolio"]
        baseline_df = canonical_model["baseline_workload"]
        show_assumptions_panel()
        show_canonical_review(canonical_model, expanded=False)

    known_ids = set(software_df["software_id"])
    unknown_ids = sorted(set(baseline_df["software_id"]) - known_ids)
    if unknown_ids:
        st.sidebar.warning(
            "Workload rows reference unknown software_id values: "
            + ", ".join(unknown_ids)
        )
    if (capacity_df["available_hours_year"] <= 0).any():
        st.sidebar.warning(
            "One or more roles have zero available capacity. Check the FTE, "
            "availability, or annual hours assumptions before relying on the results."
        )

    filtered_df = apply_baseline_filters(baseline_df, software_df)
    initialise_scenario_state(baseline_df, capacity_df)

    tabs = st.tabs(
        [
            "Baseline Current State",
            "Scenario Builder",
            "Scenario Impact",
            "Scenario Decision Matrix",
            "Leadership Interpretation",
            "AI-Assisted Interpretation",
            "Data Tables",
            "Data Schema / Beginner Notes",
        ]
    )
    with tabs[0]:
        show_baseline_current_state_tab(filtered_df, capacity_df, software_df)
    with tabs[1]:
        show_scenario_builder_tab(baseline_df, software_df, templates_df, capacity_df)
    with tabs[2]:
        show_scenario_impact_tab(baseline_df, capacity_df)
    with tabs[3]:
        show_scenario_decision_matrix_tab(baseline_df, capacity_df)
    with tabs[4]:
        show_leadership_interpretation_tab(baseline_df, capacity_df)
    with tabs[5]:
        show_ai_interpretation_tab(baseline_df, capacity_df)
    with tabs[6]:
        show_data_tables_tab(
            filtered_df,
            baseline_df,
            software_df,
            capacity_df,
            templates_df,
        )
    with tabs[7]:
        show_schema_beginner_notes_tab()


if __name__ == "__main__":
    main()
