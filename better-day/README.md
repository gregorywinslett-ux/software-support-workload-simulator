# Better Day

Better Day is a Streamlit prototype for a role-personalised workday simulation focused on positive and inclusive everyday behaviours at ITaLI.

It is designed as reflective practice, not as an assessment. Users choose an ITaLI team and role posture, then move through a simulated workday involving ambiguity, workload pressure, cross-team dependency, inclusion moments, open-text practice and repair opportunities.

## Run locally

From this folder:

```bash
pip install -r requirements.txt
python3 -m streamlit run app.py
```

Then open the local URL Streamlit prints, usually:

```text
http://localhost:8501
```

The app is self-contained. It does not use a database, authentication, login, external services, or AI APIs.

## Public Deployment

For a public URL, deploy the app through Streamlit Community Cloud from GitHub.

Deployment settings:

- Repository: `gregorywinslett-ux/software-support-workload-simulator`
- Branch: `better-day-public-deploy`
- Main file path: `better-day/app.py`
- Requirements file: `better-day/requirements.txt`

See [PUBLIC_DEPLOYMENT.md](PUBLIC_DEPLOYMENT.md) for step-by-step instructions.

## What To Share With Colleagues

Suggested framing:

> Better Day is an early reflective simulation prototype. It is intended to help ITaLI staff practise positive and inclusive everyday behaviours in realistic workday moments. The simulation is not a quiz, assessment, compliance tool or judgement of any team. Its purpose is to notice how small choices interact with system pressures such as workload, ambiguity, role clarity, prioritisation, decision rights and cross-team dependency.

Suggested pilot activity:

1. Ask colleagues to run through one simulated day using their closest team and role posture.
2. Invite them to notice whether the situations feel plausible.
3. Ask them where the choices feel too easy, too moralising or too generic.
4. Ask them whether the final debrief feels useful enough to prompt a real reflection conversation.
5. Capture feedback using [FEEDBACK_PROMPTS.md](FEEDBACK_PROMPTS.md).

## Prototype Boundaries

- This is a local prototype, not a production service.
- It does not collect, transmit or store user responses outside the current Streamlit session.
- Open-text responses are saved only in session state and included in the downloadable debrief.
- The generated reflection prompt is designed for optional copy-paste into Copilot or another GenAI tool chosen by the user.
- Scenario wording is fictional and should be refined with ITaLI staff feedback.

## Files

- `app.py` - Streamlit app and simulation logic.
- `assets/workday-cockpit-hero.png` - local hero image used by the app.
- `.streamlit/config.toml` - Streamlit theme settings.
- `requirements.txt` - minimal Python dependencies.
- `FEEDBACK_PROMPTS.md` - prompts for colleagues reviewing the prototype.
- `TESTING.md` - manual test checklist.
- `PUBLIC_DEPLOYMENT.md` - Streamlit Community Cloud deployment steps.

## Sceptical-user test

1. Would an ITaLI staff member recognise this situation as plausible?
2. Does each decision involve a real trade-off?
3. Does the simulation avoid obvious right/wrong answers?
4. Do consequences include what remains unresolved?
5. Do delayed consequences make the workday feel connected?
6. Does the app avoid blaming individuals for systemic work-design issues?
7. Does the debrief feel reflective rather than congratulatory?
8. Are the suggested small moves specific enough to try tomorrow?
9. Does the simulation feel positive without becoming simplistic?
10. Would a sceptical user think, "Yes, this is the kind of thing that actually happens"?
