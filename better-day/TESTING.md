# Better Day Manual Test Checklist

Use this checklist before sharing a new version.

## Launch

1. Run `python3 -m streamlit run app.py`.
2. Confirm the welcome screen loads without visible raw HTML.
3. Confirm the hero image appears.
4. Confirm no error appears in the terminal.

## Setup

1. Select `eLearning Systems and Support`.
2. Select `Team lead`.
3. Start the simulated day.
4. Confirm the briefing page says `eLearning Systems and Support` and `Team lead`.
5. Confirm it does not mention another selected team.

## Simulation

1. Begin scene 1.
2. Confirm the left rail, scene stage and right HUD all render.
3. Confirm the Climate HUD does not show raw `<div>` text.
4. Confirm the system pressure panel does not show raw `<div>` text.
5. Choose one response per scene.
6. Enter text in open-text practice moments.
7. Enter text in noticing pauses.
8. Confirm delayed consequences appear as “Earlier choice resurfacing”.
9. Confirm repair windows appear in repair scenes.

## End Of Day

1. Complete all 8 scenes.
2. Confirm the behavioural profile appears.
3. Confirm the replay map appears.
4. Confirm all three output panels appear.
5. Confirm the final panel is labelled “Copy-paste into Copilot (or your GenAI of choice) to prompt a reflection activity”.
6. Download the debrief and confirm it opens as a text file.

## Expected Result

- No visible raw HTML.
- No Streamlit exception.
- Correct team and role persist throughout the simulation.
- Final debrief includes choices, open-text responses, noticing pauses, climate indicators and system pressures.
