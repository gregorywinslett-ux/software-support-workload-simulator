# Public Deployment: Better Day

Use Streamlit Community Cloud to create a public URL.

## Current Deployment Source

The app has been committed locally on this Git branch:

```text
better-day-public-deploy
```

The app entrypoint is:

```text
better-day/app.py
```

The dependency file is:

```text
better-day/requirements.txt
```

## Step 1: Push The Branch To GitHub

From the repository root:

```bash
git push -u origin better-day-public-deploy
```

If Git asks you to log in, authenticate with your GitHub account.

## Step 2: Create The Streamlit App

1. Go to Streamlit Community Cloud:
   `https://share.streamlit.io`
2. Sign in with GitHub.
3. Select **Create app**.
4. Choose **Deploy a public app from GitHub**.
5. Use these settings:

```text
Repository: gregorywinslett-ux/software-support-workload-simulator
Branch: better-day-public-deploy
Main file path: better-day/app.py
```

6. Deploy the app.

Streamlit will install dependencies from:

```text
better-day/requirements.txt
```

## Step 3: Share The URL

After deployment completes, Streamlit will provide a public URL. Send that URL to colleagues.

Suggested wording:

> Here is a prototype of Better Day, a role-personalised reflective workday simulation for practising positive and inclusive everyday behaviours. It is not a quiz or assessment. Please try one simulated day and share feedback on realism, usefulness and tone.

## Troubleshooting

- If the app cannot find dependencies, confirm `better-day/requirements.txt` is present in the GitHub branch.
- If the hero image is missing, confirm `better-day/assets/workday-cockpit-hero.png` is present in the GitHub branch.
- If the app starts from the wrong file, confirm the Streamlit main file path is exactly `better-day/app.py`.
