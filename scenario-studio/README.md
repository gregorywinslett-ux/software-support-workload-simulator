# Scenario Studio

Scenario Studio is a facilitator-operated scenario-thinking workshop prototype based on the Wright & Cairns intuitive logics method.

## Run locally

From this folder:

```bash
python3 -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

The app is dependency-free for this prototype so it can run in this workspace without npm. It uses browser local storage for autosave, import/export JSON, native drag-and-drop, and a print-ready report view.

## Run with Streamlit

From the repository root:

```bash
python3 -m streamlit run scenario-studio/streamlit_app.py
```

For Streamlit Community Cloud:

- Repository: `gregorywinslett-ux/software-support-workload-simulator`
- Branch: `main`
- Main file path: `scenario-studio/streamlit_app.py`
- Requirements file: repository root `requirements.txt`

The Streamlit wrapper embeds the static prototype in an iframe with its CSS and JavaScript inlined, so no npm build step is required.

## Prototype Coverage

- Setup, focal question scoring, driving forces, clustering, plausible extremes
- Impact/uncertainty matrix and pairwise comparison
- Scenario matrix, sketches, timelines, critique and strategic implications
- Parking lot, decision log, facilitator prompts and step timer
- Sample data loader for immediate demonstration
- JSON export/import, clipboard summary, text exports and printable report
- Room mode for participant-facing display
- Undo history, schema-versioned local storage and import validation
- Decision gates, workshop health meter and live output strip
- Guided mode with plain-English method explanations, examples, common traps and reassurance copy
- Persistent method glossary and transformation map from issue framing to action
- Data lineage cues from forces to clusters, axes, scenarios and actions
- Facilitator command palette (`Cmd/Ctrl+K`)
- Presentation summary, workshop recap, force constellation, early warning dashboard and action portfolio views
- Enhanced strategic action table with owner, timeframe, effort, confidence and next-decision fields

## Notes

The requested production stack was React + TypeScript + Tailwind. This workspace does not currently include npm, so the prototype has been implemented as a self-contained local web app with typed JSDoc data models, schema migration and component-style render functions. The UI and data model are intentionally structured so it can be migrated cleanly into React components later.
