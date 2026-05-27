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

Start the deployment. The app should launch without secrets, API keys, databases, or external services.

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

## 9. Final Sharing Check

Before sharing with colleagues:

- Run the manual checks in `MANUAL_TEST_CHECKLIST.md`.
- Confirm no real or sensitive data is committed.
- Confirm `.streamlit/secrets.toml` is not committed.
- Confirm the app does not require login, a database, external APIs, or API keys.
- Confirm colleagues understand the privacy and appropriate-use cautions.
