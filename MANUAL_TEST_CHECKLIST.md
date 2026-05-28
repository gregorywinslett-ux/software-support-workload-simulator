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

## Scenario Decision Matrix

- Open the `Scenario Decision Matrix` tab.
- Confirm the default scenarios, default criteria, and default scores appear.
- Confirm active criteria weights total 100%.
- Change an active weight so the total is not 100% and confirm a warning appears.
- Click `Normalise active weights to 100%` and confirm the active weights rebalance.
- Change several 1 to 5 scores and confirm the ranked list and chart update.
- Confirm lower-is-better criteria use favourability wording, for example risk score 5 means low risk.
- If a scenario has been built, click `Add current simulator scenario to matrix` and confirm its workload impact summary appears.
- Click `Download decision matrix summary` and confirm the Markdown file includes the decision question, scenarios, criteria, scores, ranking, caveats, and decision prompts.

## Export Function

- Click `Download planning summary` from the review panel.
- Open the Markdown file and confirm it includes appropriate-use text, monthly review rows, assumptions, and scenario summary when a scenario is active.

## AI Disabled State

- Open the app without configuring `OPENAI_API_KEY`.
- Click the `AI-Assisted Interpretation` tab.
- Confirm the app shows a clear message that AI is not configured.
- Confirm the rest of the simulator still works.
- Confirm the minimized summary expander does not include staff names, raw uploaded files, free-text notes, raw work item titles, or software names.

## AI Enabled State

- Configure `OPENAI_API_KEY` in Streamlit secrets.
- Open the `AI-Assisted Interpretation` tab.
- Confirm the privacy and appropriate-use warning appears.
- Click `Generate cautious AI interpretation`.
- Confirm the output is cautious, non-decisive, and framed as leadership reflection only.
- Confirm the output does not evaluate individual staff performance.
- Click `Download AI interpretation` and confirm a Markdown file downloads.

## AI Decision Matrix Reflection

- With no `OPENAI_API_KEY`, confirm the Scenario Decision Matrix AI section shows a disabled-state message and the non-AI matrix still works.
- With `OPENAI_API_KEY` configured, click `Generate cautious AI interpretation of comparison`.
- Confirm the output is cautious and does not make the decision.
- Confirm it does not describe the ranking as objectively correct.
- Confirm it does not mention staff performance or individual capability.

## Demo Data Reset

- Change builder values.
- Click `Reset demo data` in the sidebar.
- Confirm the builder returns to the built-in synthetic sample entries and scenario state is cleared.
