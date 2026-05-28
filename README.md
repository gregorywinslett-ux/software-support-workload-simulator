# Software Support Workload Simulator

A local Streamlit app for planning software support workload, baseline capacity, and simple scenario impacts.

The app helps team leads ask:

- How much team capacity is available in the planning period?
- Which assigned work items consume that capacity?
- Which months are near or over capacity?
- What happens if we add, remove, consolidate, decommission, or change support for software?
- How do several possible scenarios compare when weighted against shared decision criteria?

## Who It Is For

This tool is intended for team leads, service owners, and planning conversations about software support workload. It is not a performance management system and should not be used to measure individual staff performance.

Use generic role labels such as `Advisor pool`, `Helpdesk role`, or `Specialist capacity` instead of staff names when possible.

## App Type and Deployment Path

This is a Streamlit/Python app.

- Entry point: `app.py`
- Dependencies: `requirements.txt`
- Built-in synthetic demo data: `sample_data/*.csv`

The most appropriate simple sharing path is Streamlit Community Cloud connected to a GitHub repository. GitHub Pages is not suitable because this is not a static HTML/CSS/JavaScript app.

## Run Locally

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the app:

```bash
python3 -m streamlit run app.py
```

Then open the local URL Streamlit prints, usually:

```text
http://localhost:8501
```

## Data Input Options

The app has two input pathways. Both are transformed into the same internal data model before the dashboard and simulator use them.

### 1. Guided Baseline Builder

Use this when you want to enter planning data directly in the app:

- Team profile
- People or role availability
- Assigned work items
- Monthly review

The builder creates clean internal tables for team capacity, people availability, assigned work items, monthly workload, baseline workload, and scenario adjustments.

### 2. CSV Upload or Sample Data

Use this when you already have CSV files or want to use the bundled demo data.

Expected files, also available in `sample_data/`:

- `sample_data/sample_team_capacity.csv`
- `sample_data/sample_supported_software.csv`
- `sample_data/sample_baseline_workload.csv`
- `sample_data/sample_scenario_task_templates.csv`

If no files are uploaded, the app uses the bundled synthetic sample data.

### CSV Columns

`sample_team_capacity.csv`

- `role`
- `fte`
- `usable_hours_per_fte_per_year`
- `available_hours_year`
- `notes`

`sample_supported_software.csv`

- `software_id`
- `software_name`
- `support_status`
- `support_level`
- `criticality`
- `adoption_level`
- `vendor_complexity`
- `configuration_complexity`
- `integration_complexity`
- `primary_audience`
- `notes`

`sample_baseline_workload.csv`

- `workload_id`
- `software_id`
- `software_name`
- `work_type`
- `work_group`
- `annual_volume`
- `advisor_hours_per_unit`
- `helpdesk_hours_per_unit`
- `specialist_hours_per_unit`
- `pm_hours_per_unit`
- `manager_hours_per_unit`
- `advisor_hours_total`
- `helpdesk_hours_total`
- `specialist_hours_total`
- `pm_hours_total`
- `manager_hours_total`
- `confidence`
- `notes`

`sample_scenario_task_templates.csv`

- `template_id`
- `scenario_type`
- `lifecycle_phase`
- `work_type`
- `task_name`
- `default_annual_volume`
- `advisor_hours_per_unit`
- `helpdesk_hours_per_unit`
- `specialist_hours_per_unit`
- `pm_hours_per_unit`
- `manager_hours_per_unit`
- `default_confidence`
- `notes`

## Demo Mode

The sidebar includes a `Reset demo data` button.

Use demo mode before sharing with colleagues or testing a public deployment. Demo data is synthetic and is intended to avoid accidental use of sensitive real team data.

## Privacy and Appropriate Use

- This tool is a planning aid, not an individual performance measurement system.
- Do not enter sensitive personal information, HR information, health information, or individual performance notes.
- Generic role labels can be used instead of staff names.
- Public or shared deployments should use synthetic or non-sensitive data only.
- The app does not add login, a database, external APIs, or multi-user collaboration.

## Canonical Internal Model

Both the Baseline Builder and CSV pathway are transformed into these internal tables:

- `team_profile`: team name, planning period, planning unit, standard hours.
- `team_capacity`: role-level capacity used by the dashboard and scenarios.
- `people_availability`: raw staff, role, or pool availability entries.
- `assigned_work_items`: normalized work items with work type, month range, hours, priority, and confidence.
- `monthly_workload`: monthly available capacity, assigned workload, remaining capacity, and over-capacity flag.
- `software_portfolio`: supported software metadata.
- `baseline_workload`: simulator-ready workload rows with calculated role-hour columns.
- `scenario_adjustments`: current scenario impact summary.

## Calculation Assumptions

Capacity:

```text
effective_fte = FTE x availability percentage
available_hours = effective_fte x standard hours
```

For monthly planning, standard hours are treated as monthly hours per FTE. For weekly planning, weekly hours are converted to annual and monthly equivalents.

Monthly workload is spread evenly across each work item's active month range.

Over-capacity is flagged when monthly assigned workload is greater than monthly available capacity.

Scenario adjustments create a revised workload or capacity table and compare it with the baseline.

## Scenario Modelling

The scenario simulator supports:

- Introduce software
- Remove software
- Consolidate software
- Reduce support level
- Increase adoption
- Decommission tool
- Project to BAU
- Demand spike
- Capacity change

The scenario impact tab compares the baseline against the revised scenario model.

## Scenario Decision Matrix

The `Scenario Decision Matrix` tab lets users compare multiple software-support options side by side. It is non-AI and transparent: users define the scenarios, choose criteria, set weights, enter scores, and the app calculates the ranking.

Default criteria include:

- workload impact
- strategic value
- risk
- cost
- complexity
- student/staff benefit
- confidence in estimates
- implementation effort
- recurring BAU burden
- opportunity cost

Criteria can be enabled or disabled. Active weights should sum to 100%, and the app shows a warning if they do not. The `Normalise active weights to 100%` button can rebalance active criteria.

Scoring uses a 1 to 5 favourability scale:

- 1 = weak / unfavourable
- 2 = limited
- 3 = moderate
- 4 = strong
- 5 = very strong / favourable

For lower-is-better criteria, the score is still favourability. For example, risk score 5 means low risk, cost score 5 means low cost, workload impact score 5 means manageable workload impact, and complexity score 5 means low complexity.

The total weighted score is calculated as:

```text
weighted criterion score = criterion score x (criterion weight / 100)
total scenario score = sum of weighted criterion scores
```

The matrix produces a ranked scenario list, a criterion-by-criterion scoring table, a visual comparison chart, a rule-based recommendation summary, decision prompts, and a Markdown export.

The decision matrix can use workload impact values from the existing Scenario Impact tab as summary text. It remains connected to the workload forecast but does not depend on it.

## Export

The review panel includes a `Download planning summary` button. The decision matrix includes a `Download decision matrix summary` button.

Exports can include:

- Appropriate-use note
- Team profile
- Capacity and workload summary
- Monthly review
- Active scenario summary, when available
- Calculation assumptions
- Decision question
- Scenarios compared
- Active criteria and weights
- Scenario scores and ranking
- Caveats and decision prompts
- Optional AI comparison interpretation, if generated

## Optional AI-Assisted Interpretation

The app includes an optional `AI-Assisted Interpretation` tab. It is disabled unless an OpenAI API key is configured in Streamlit secrets.

The AI feature is designed as a cautious leadership reflection aid. It can suggest observations, risks, questions, and possible mitigations, but it must not make decisions or evaluate staff performance.

The minimized summary sent to OpenAI excludes:

- individual staff names
- raw uploaded files
- free-text private notes
- raw work item titles
- software names
- sensitive personal information

The AI output should be treated as draft reflection material only. Human judgement is required for all decisions.

The Scenario Decision Matrix also has an optional AI reflection section. The AI does not calculate scores or make the decision. It can only interpret a summarised comparison object containing:

- decision question
- scenario names and short descriptions
- active criteria and weights
- total weighted scores
- ranked order
- major trade-offs
- flagged caveats

The AI comparison summary excludes API keys, raw uploaded files, staff names, person-level capacity data, sensitive notes, confidential operational detail, and raw scenario notes.

### Enable Locally

Create a local file called `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "your-key-here"
# Optional:
OPENAI_MODEL = "gpt-5"
```

Do not commit `.streamlit/secrets.toml` to GitHub.

### Enable In Streamlit Community Cloud

Open the deployed app settings, go to `Secrets`, and add:

```toml
OPENAI_API_KEY = "your-key-here"
# Optional:
OPENAI_MODEL = "gpt-5"
```

If no API key is configured, the app still works normally and shows a clear disabled-state message in the AI tab.

## Manual Testing

Before sharing, run through [MANUAL_TEST_CHECKLIST.md](MANUAL_TEST_CHECKLIST.md).

The checklist covers:

- Baseline Builder with valid data
- Baseline Builder with missing data
- CSV upload with valid data
- CSV upload with missing columns
- Scenario adjustment
- Scenario Decision Matrix scoring and export
- Export function
- Demo data reset
- AI disabled state
- AI enabled state, if an API key is configured

## Deployment Notes

Recommended path: Streamlit Community Cloud via GitHub.

Commit the app files, requirements file, README, deployment notes, changelog, test checklist, and synthetic sample CSVs in `sample_data/`. Do not commit local caches, `.DS_Store`, virtual environments, Streamlit secrets, local/private data folders, or real team data.

For Streamlit Community Cloud:

1. Push the repository to GitHub.
2. Create a new Streamlit app from the repository.
3. Set the main file path to `app.py`.
4. Confirm the app installs from `requirements.txt`.
5. Test with demo data before inviting colleagues.

See [DEPLOYMENT.md](DEPLOYMENT.md) for a step-by-step deployment checklist.

## Known Limitations

- No login, database, persistence, or multi-user collaboration.
- The optional AI tab calls OpenAI only when an API key is configured and the user clicks the generation button.
- Uploaded data is held only in the current browser/session.
- The model uses simplified assumptions and should support planning conversations, not precise forecasting.
- Work item hours are spread evenly across active months.
- Role allocation for guided work items uses simple work-type defaults.
- AI interpretation is optional, cautionary, and not authoritative.
- Scenario Decision Matrix scoring depends on human judgement.
- Decision weights reflect values and priorities, not objective truth.
- AI interpretation of matrix results is reflective, not authoritative.
- The tool supports structured deliberation, not automated decision-making.
