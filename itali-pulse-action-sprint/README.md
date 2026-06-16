# ITaLI Pulse Action Sprint Studio

A polished local Streamlit prototype for running a 45-minute all-staff action sprint focused on workload monitoring and resolution.

This is not a chatbot and not a conventional dashboard. It is a meeting-native facilitation cockpit for one facilitator/operator using a large shared screen while staff contribute anonymously through QR-accessible forms.

## Meeting Scenario

The session helps ITaLI staff move from shared understanding to practical action using this spine:

**Notice -> Name -> Discuss -> Prioritise -> Resolve -> Review**

The app supports five modes:

- **Explain**: presentation-style editable slides based on ITaLI Pulse 2026 narrative material.
- **Explore**: dashboard-style theme and evidence view.
- **Collaborate**: QR response collection, facilitator moderation, clustering, comments, and promotion to candidate actions.
- **Decide**: criteria selection, pairwise criteria weighting, action rating, advisory ranking, and final decision status.
- **Act**: action plan, decision record, resource kit outline, and copy-paste ChatGPT prompt generation.

## Install

```bash
cd "itali-pulse-action-sprint"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```

The app usually opens at:

```text
http://localhost:8501
```

## Limited Deployment

For sharing beyond your own laptop, the simplest route is GitHub + Streamlit Community Cloud. See [STREAMLIT_CLOUD.md](STREAMLIT_CLOUD.md).

For internal container or VM hosting, see [DEPLOYMENT.md](DEPLOYMENT.md).

The app includes:

- a `Dockerfile` for container hosting;
- `.streamlit/config.toml` for server defaults;
- an optional `APP_ACCESS_CODE` environment variable for a simple review gate.

Example:

```bash
APP_ACCESS_CODE="choose-a-temporary-review-code" streamlit run app.py
```

## QR Code Access

QR codes point participants to lightweight Streamlit pages such as:

```text
/?role=participant&activity=responses
/?role=participant&activity=pairwise
```

Important caveats:

- `localhost` only works on the facilitator's own machine.
- Phones need a base URL that is reachable on the same network, such as `http://192.168.x.x:8501`.
- Firewall rules, VPNs, and institutional Wi-Fi may block access.
- Manual facilitator entry should remain available as a fallback.

## Privacy and Governance

This prototype:

- should not collect names;
- treats raw individual responses as facilitator-private by default;
- stores data only in the running local Streamlit session unless exported;
- should not be used for sensitive personal information;
- has no authentication, role-based permissions, or audit trail.

Production use would require review of privacy, data retention, records management, information security, accessibility, authentication, institutional branding, mobile/network reliability, moderation protocols, and safe handling of psychosocial hazard-related comments.

## Pairwise Weighting Method

The facilitator selects exactly three criteria. Participants compare each pair using simple strength choices:

- strongly more important = 5
- moderately more important = 3
- slightly more important = 2
- about equal = 1

The app constructs a 3x3 pairwise matrix for each participant, calculates weights using the geometric mean method, then averages and normalises group weights. A simple spread indicator shows variation across individual weights.

## Weighted Action Scoring

Candidate actions are rated from 1 to 5 against each selected criterion:

- 1 very weak
- 2 weak
- 3 adequate
- 4 strong
- 5 very strong

The weighted action score is:

```text
sum(criterion rating x group criterion weight)
```

Scores are advisory only. The facilitator still assigns final statuses: adopt, refine, combine, park, or escalate.

## Exports

The Export screen provides downloads for:

- full session JSON;
- individual responses CSV;
- candidate actions CSV;
- criteria weights CSV;
- action ratings and rankings CSV;
- action plan brief Markdown;
- decision record Markdown;
- resource kit outline Markdown;
- ChatGPT prompts TXT.

## Prototype Limitations

This is a working local prototype. It does not include external APIs, cloud storage, institutional integrations, real authentication, persistent database storage, production accessibility assurance, or formal moderation workflows. The optional access code is only a lightweight review gate.

## Future Enhancements

- Persistent local project files or database storage.
- Presenter/public display mode separate from facilitator controls.
- Better cluster editing and combine/split workflows.
- Import from structured Pulse findings spreadsheets.
- DOCX export for post-meeting artefacts.
- Institutional theme and brand review.
- Production-grade privacy, security, and records controls.
