# Deployment Notes

For sharing with two colleagues beyond your own laptop, the easiest path is GitHub + Streamlit Community Cloud. See [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md).

Use the internal container/VM path only if the review needs institution-managed hosting, stricter access controls, or non-public infrastructure.

## Option A: Streamlit Community Cloud

Recommended for quick prototype review.

- Push this folder to GitHub.
- Deploy `itali-pulse-action-sprint/app.py`.
- Add `APP_ACCESS_CODE` in Streamlit secrets.
- Share the Streamlit URL and temporary access code with reviewers.

## Option B: Internal Container Or VM

Use an internal UQ-managed host, VM, container service, or similar environment if it can:

- run Docker or Python;
- serve HTTPS through an institutional reverse proxy;
- restrict access to UQ users or a small allowed group where possible;
- set environment variables securely;
- avoid public indexing.

## Container Deployment

Build the image:

```bash
docker build -t itali-pulse-action-sprint .
```

Run locally or on a host:

```bash
docker run --rm -p 8501:8501 \
  -e APP_ACCESS_CODE="choose-a-temporary-review-code" \
  itali-pulse-action-sprint
```

Then open:

```text
http://localhost:8501
```

On a server, put the app behind HTTPS and share the HTTPS URL with colleagues.

## Optional Access Code

Set `APP_ACCESS_CODE` to require a simple access code before anyone can view the app:

```bash
APP_ACCESS_CODE="choose-a-temporary-review-code" streamlit run app.py
```

This is only a light review gate, not institutional authentication. For production use, rely on proper identity, access control, logging, and records settings.

## Base URL for QR Codes

After deployment, set the app's **Base URL for QR codes** field to the public/internal HTTPS URL, for example:

```text
https://itali-pulse-review.example.edu.au
```

The QR links use:

```text
/?role=participant&activity=responses
/?role=participant&activity=pairwise
```

If `APP_ACCESS_CODE` is enabled, participants will need the access code before using the QR forms.

## Data Handling

This prototype stores session data in Streamlit session memory. Data may disappear if the server restarts or the session resets. Export anything that needs to be retained.

For the colleague review:

- use synthetic/sample data where possible;
- avoid real sensitive staff comments;
- export only what is needed;
- delete exported files when no longer needed.

## Production Readiness Gaps

Before using this for formal staff consultation, review:

- privacy;
- data retention;
- records management;
- information security;
- authentication and role-based permissions;
- accessibility;
- institutional branding;
- network reliability;
- moderation and escalation protocols;
- safe handling of psychosocial hazard-related comments.
