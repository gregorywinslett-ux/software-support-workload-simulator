# Streamlit Community Cloud Deployment

Use this path for a lightweight review with two colleagues.

## What You Need

- A GitHub repository containing this `itali-pulse-action-sprint/` folder.
- The app entrypoint path:

```text
itali-pulse-action-sprint/app.py
```

- The dependency file:

```text
itali-pulse-action-sprint/requirements.txt
```

Streamlit Community Cloud can install dependencies from a `requirements.txt` file in the same directory as the app entrypoint.

## Suggested Review Setup

For a colleague review, use an access code so the URL is not openly usable by anyone who finds it.

In Streamlit Community Cloud, open **Advanced settings** and add this to **Secrets**:

```toml
APP_ACCESS_CODE = "choose-a-temporary-review-code"
```

Use a short-lived code and share it only with the two reviewers.

This is not institutional authentication. It is just a lightweight review gate for a prototype.

## Deploy Steps

1. Push the app folder to GitHub.
2. Go to Streamlit Community Cloud.
3. Choose **Create app**.
4. Select the GitHub repository and branch.
5. Set the main file path to:

```text
itali-pulse-action-sprint/app.py
```

6. Open **Advanced settings**.
7. Select Python 3.12 if the option is shown.
8. Paste the `APP_ACCESS_CODE` secret above.
9. Deploy.

After deployment, open the app and set **Base URL for QR codes** to the deployed Streamlit URL, for example:

```text
https://your-app-name.streamlit.app
```

## What Not To Put In The App Yet

For this review, avoid:

- identifiable staff comments;
- confidential Pulse data not already approved for this purpose;
- sensitive psychosocial hazard details;
- names, teams, or examples that point to individuals.

Use synthetic/sample data or carefully generalised text.

## If The App Fails To Build

Check:

- the app path is exactly `itali-pulse-action-sprint/app.py`;
- `requirements.txt` is in the same folder as `app.py`;
- `.venv/` has not been committed;
- the deploy logs mention any missing package.
