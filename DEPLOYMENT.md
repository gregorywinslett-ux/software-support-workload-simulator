# Deployment Guide

This app is prepared for Streamlit Community Cloud deployment through GitHub.

## 1. Create Or Use A GitHub Repository

Create a new GitHub repository, or use an existing repository that is intended for this simulator.

Recommended repository contents:

- `app.py`
- `requirements.txt`
- `README.md`
- `DEPLOYMENT.md`
- `CHANGELOG.md`
- `MANUAL_TEST_CHECKLIST.md`
- `.gitignore`
- `sample_data/`

Do not include real team data, secrets, local caches, virtual environments, or private files.

## 2. Commit The Project Files

From the project root:

```bash
git add app.py requirements.txt README.md DEPLOYMENT.md CHANGELOG.md MANUAL_TEST_CHECKLIST.md .gitignore sample_data
git commit -m "Prepare Streamlit deployment"
git push
```

If your workspace contains other learning projects, commit only the simulator files listed above.

## 3. Open Streamlit Community Cloud

Go to Streamlit Community Cloud and sign in with GitHub:

```text
https://share.streamlit.io/
```

## 4. Connect The GitHub Repository

Create a new app and choose:

- Repository: the GitHub repository containing this simulator
- Branch: the branch you want to deploy, usually `main`
- Main file path: `app.py`

The app should install dependencies from `requirements.txt`.

## 5. Deploy

Start the deployment. The core simulator should launch without secrets, API keys, databases, or external services.

## 6. Test Demo Mode After Deployment

After the app opens:

- Confirm the app loads without uploaded files.
- Confirm `Guided builder` is selected by default.
- Click `Reset demo data`.
- Confirm the monthly review and dashboard populate with synthetic data.
- Confirm no real staff, team, institution, confidential, or sensitive data appears.

## 7. Test CSV Upload

Use the files in `sample_data/` to test upload behavior:

- `sample_team_capacity.csv`
- `sample_supported_software.csv`
- `sample_baseline_workload.csv`
- `sample_scenario_task_templates.csv`

Confirm the dashboard and scenario simulator still load.

## 8. Test Export

Click `Download planning summary` and confirm the Markdown file downloads.

The export should include:

- appropriate-use note
- team profile
- monthly review
- assumptions
- active scenario summary, if a scenario has been built

Also open the `Scenario Decision Matrix` tab and confirm:

- default scenarios and criteria appear;
- active weights total 100%;
- scenario scores can be edited;
- the ranked list and chart update;
- `Download decision matrix summary` downloads a Markdown file;
- no API key or secret appears in the export.

## 9. Test Scenario Decision Matrix

The Scenario Decision Matrix is a non-AI comparison tool. It should work without secrets, API keys, databases, or external services.

After deployment:

1. Open the `Scenario Decision Matrix` tab.
2. Confirm the default criteria are visible.
3. Confirm scoring uses favourability language, where 5 is favourable.
4. Change one criterion weight and confirm a warning appears if active weights no longer total 100%.
5. Click `Normalise active weights to 100%` and confirm the warning clears.
6. Change scenario scores and confirm the ranking and chart update.
7. Add the current simulator scenario from the Scenario Impact output, if available.
8. Download the Markdown summary.

## 10. Final Sharing Check

Before sharing with colleagues:

- Run the manual checks in `MANUAL_TEST_CHECKLIST.md`.
- Confirm no real or sensitive data is committed.
- Confirm `.streamlit/secrets.toml` is not committed.
- Confirm the core app does not require login, a database, or API keys.
- Confirm colleagues understand the privacy and appropriate-use cautions.
- Confirm the Scenario Decision Matrix is described as a facilitation aid, not an automatic decision.

## 11. Optional AI-Assisted Interpretation

The app includes optional AI interpretation for workload outputs and optional AI reflection for the Scenario Decision Matrix. Both remain disabled unless an OpenAI API key is configured.

To enable it in Streamlit Community Cloud:

1. Open the deployed app settings.
2. Go to `Secrets`.
3. Add:

```toml
OPENAI_API_KEY = "your-key-here"
# Optional:
OPENAI_MODEL = "gpt-5"
```

4. Save the secrets.
5. Restart or redeploy the app if Streamlit asks you to.
6. Open the `AI-Assisted Interpretation` tab.
7. Confirm the privacy warning appears.
8. Click `Generate cautious AI interpretation`.
9. Confirm the output is cautious and framed as leadership reflection only.
10. Open the `Scenario Decision Matrix` tab.
11. Confirm the comparison AI section says it receives only the summarised comparison object.
12. If testing with an API key, click `Generate cautious AI interpretation of comparison`.
13. Confirm the output does not make the decision or describe the ranking as objectively correct.

Do not commit `.streamlit/secrets.toml`, `.env`, API keys, or screenshots containing secrets.

If no API key is configured, the AI tab should show a disabled-state message and the rest of the simulator should continue working normally.

The Scenario Decision Matrix AI summary sends only:

- decision question;
- scenario names and short descriptions;
- active criteria and weights;
- total weighted scores and ranked order;
- major trade-offs;
- flagged caveats.

It does not send API keys, raw uploaded files, staff names, person-level capacity data, sensitive notes, confidential operational detail, or raw scenario notes.
