# Changelog

## v0.7 - Scenario Decision Matrix

- Added non-AI `Scenario Decision Matrix` tab for comparing multiple software-support scenarios.
- Added editable scenarios, editable criteria, criteria enable/disable controls, and weighted scoring.
- Added favourability scoring guidance for lower-is-better criteria such as risk, cost, complexity, workload impact, implementation effort, recurring BAU burden, and opportunity cost.
- Added ranked results, criterion-by-criterion scoring, visual comparison chart, rule-based recommendation summary, decision prompts, and Markdown export.
- Added optional AI reflection on summarised decision matrix results while preserving existing AI secrets handling and workload interpretation.
- Updated README and deployment notes with decision matrix workflow, privacy limits, AI summary boundaries, and limitations.

## v0.6 - Optional AI-Assisted Interpretation

- Added optional `AI-Assisted Interpretation` tab.
- Added minimized AI summary object that excludes staff names, raw files, free-text notes, raw work item titles, and software names.
- Added disabled state when no OpenAI API key is configured.
- Added guarded OpenAI Responses API call when an API key is present.
- Added Markdown export for AI interpretation output.
- Updated README, deployment notes, and manual test checklist.

## v0.5 - Streamlit Deployment Preparation

- Confirmed `app.py` as the Streamlit Community Cloud entry point.
- Moved synthetic demo CSVs into `sample_data/`.
- Updated repository hygiene with Python, Streamlit, local data, and private data exclusions.
- Added Streamlit Community Cloud deployment instructions.
- Added explicit deployment checklist and GitHub commit guidance.

## v0.4 - Pre-Deployment Hardening

- Added privacy and appropriate-use notices.
- Added demo reset controls.
- Added assumptions panel.
- Added planning summary export.
- Added manual test checklist.
- Updated README for sharing and deployment readiness.

## v0.3 - Canonical Data Model And Validation

- Added a canonical in-session data model for builder and CSV pathways.
- Normalized team capacity, people availability, assigned work, monthly workload, baseline workload, and scenario adjustments.
- Improved plain-English validation and review messages.

## v0.2 - Baseline Capacity Builder

- Added guided setup panels for team profile, people availability, assigned work, and review.
- Added monthly capacity and workload review before the dashboard.
- Preserved CSV upload as an alternate input pathway.

## v0.1 - Initial Prototype

- Added Streamlit dashboard for baseline workload.
- Added scenario simulator for common support planning questions.
- Added sample CSV data and scenario task templates.
