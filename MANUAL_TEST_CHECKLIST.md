# Manual Test Checklist

Use this checklist before sharing or deploying the Software Support Workload Simulator.

## Baseline Builder With Valid Data

- Start the app with `streamlit run app.py`.
- Leave `Baseline data source` set to `Guided builder`.
- Confirm the built-in people and work rows render without validation errors.
- Confirm the review panel shows monthly available capacity, assigned workload, remaining capacity, and over-capacity status.
- Confirm the dashboard tabs populate from the guided baseline.

## Baseline Builder With Missing Data

- Clear the team name and confirm a plain-English required-team-name message appears.
- Enter an invalid planning month such as `2026-99` and confirm a date-format message appears.
- Set FTE to `0` and confirm a positive-FTE message appears.
- Set availability outside `0` to `100` if possible and confirm the availability message appears.
- Remove all work rows and confirm the app warns that no assigned work items have been entered.

## CSV Upload With Valid Data

- Switch `Baseline data source` to `CSV upload or sample data`.
- Upload the four sample CSVs or leave the bundled sample data selected.
- Confirm the monthly review, baseline dashboard, scenario builder, and data tables render.

## CSV Upload With Missing Columns

- Upload a copy of a sample CSV with one required column removed.
- Confirm the app explains which columns are missing and suggests comparing against the sample CSV.
- Confirm the app stops before showing misleading charts.

## Scenario Adjustment

- Build an `Introduce software` or `Demand spike` scenario.
- Confirm `Scenario Impact` shows before/after role pressure.
- Confirm `Data Tables` shows a populated `Scenario adjustments` table.

## Export Function

- Click `Download planning summary` from the review panel.
- Open the Markdown file and confirm it includes appropriate-use text, monthly review rows, assumptions, and scenario summary when a scenario is active.

## Demo Data Reset

- Change builder values.
- Click `Reset demo data` in the sidebar.
- Confirm the builder returns to the built-in synthetic sample entries and scenario state is cleared.
