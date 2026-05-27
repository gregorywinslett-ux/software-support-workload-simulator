# Software Support Workload Simulator

A local Streamlit app for planning software support workload, baseline capacity, and simple scenario impacts.

The app helps team leads ask:

- How much team capacity is available in the planning period?
- Which assigned work items consume that capacity?
- Which months are near or over capacity?
- What happens if we add, remove, consolidate, decommission, or change support for software?

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

## Export

The review panel includes a `Download planning summary` button. It exports a Markdown summary with:

- Appropriate-use note
- Team profile
- Capacity and workload summary
- Monthly review
- Active scenario summary, when available
- Calculation assumptions

## Manual Testing

Before sharing, run through [MANUAL_TEST_CHECKLIST.md](MANUAL_TEST_CHECKLIST.md).

The checklist covers:

- Baseline Builder with valid data
- Baseline Builder with missing data
- CSV upload with valid data
- CSV upload with missing columns
- Scenario adjustment
- Export function
- Demo data reset

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

- No login, database, persistence, external APIs, or multi-user collaboration.
- Uploaded data is held only in the current browser/session.
- The model uses simplified assumptions and should support planning conversations, not precise forecasting.
- Work item hours are spread evenly across active months.
- Role allocation for guided work items uses simple work-type defaults.
- AI interpretation is intentionally not included yet.
