# Academic Succession Studio

A premium workshop application for retirement planning, capability continuity, succession planning and workforce design for senior academic roles.

## Run Immediately

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 4177
```

Then visit `http://127.0.0.1:4177/academic-succession-studio/`.

The standalone page loads React, Tailwind and Framer Motion from CDNs, persists locally with `localStorage`, and supports JSON import/export plus executive report exports.

## Included Sample Data

The app opens with a sample transition scenario based on Kelly's UQ transition note. It includes example capabilities, named relationship handovers, knowledge-capture actions and memory-vault assets covering TEFA, HEDx, Lead Through Learning, gender parity work, teaching handovers and committee/program continuity.

## Workshop Handover

1. Open the public GitHub Pages link.
2. Work through Discovery, Scenario, then Executive.
3. Use **Save Session** before finishing.
4. Send the downloaded `.json` file to the next person.
5. They open the same link and use **Load Session**.

The session is also saved automatically in the current browser. Use **Save Session** when someone else needs to continue on another computer.

## Future Vite Setup

When `npm` is available:

```bash
npm install
npm run dev
```
