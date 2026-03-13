# FFXIV Lamia Materia Price Checker

Static FFXIV materia pricing tool focused on fast buy decisions.
The web app compares Lamia listings against the cheapest listings across American datacenters (Aether, Primal, Crystal, Dynamis).

## Product Model

- Primary workflow: client-side web app in `index.html` (no backend required)
- Optional workflow: local CLI analysis script in `lamia_price_check.py`
- Deployment target: static hosting (GitHub Pages)

## Deployment Decision

Use GitHub Pages when you only need static assets (`index.html`, `items.txt`, CSS, JS) and browser-side API calls.

Use Vercel (or another backend host) only if you add server-side requirements such as:
- API proxying for CORS/rate-limit handling
- scheduled/background jobs
- secret/API key management
- server-generated responses or files

Current project state fits GitHub Pages.

## Features

- Live price fetching from Universalis + item lookup from XIVAPI
- Item list loaded from `items.txt` (single source of truth)
- World-selection UI for building a shopping itinerary
- Buy-side stack model: direct large stacks plus combined small-stack options (effective price)
- Per-world sale history modal (recent sold listings, weighted average, sale velocity)
- Route text generation + clipboard copy
- 24-hour local cache with manual **Clear Cache & Reload** control
- Responsive layout for desktop and mobile

## Web Usage

1. Open the site.
2. Click **Load Live Prices**.
3. Click world rows to add item pickups to your itinerary.
4. Click **Generate Route**.
5. Copy and use the route in-game.

## Customize Items

Edit `items.txt` and put one item name per line.

Rules:
- Blank lines are ignored.
- Lines starting with `#` are ignored as comments.
- Names must match game/API item naming closely.

## Cache and Reload Behavior

- Cached results are reused for 24 hours.
- Use **Clear Cache & Reload** to force fresh API data immediately.

## Optional CLI Workflow

`lamia_price_check.py` is kept for local/offline report generation and experimentation.
It is not required for web app usage.

Basic run:

```bash
python lamia_price_check.py
```

Outputs:
- `lamia_data.json`
- `lamia_report.txt`

## Known Limitations

- Route order is grouped/sorted by world name, not travel-optimized.
- HQ/NQ detail is not shown in the current web table.
- Combined small-stack rows are weighted-average estimates, not single seller listings.
- If some API calls fail, partial data may still render.

## Roadmap

### Now

- Keep architecture and docs aligned around static web-first usage.
- Keep optional CLI path documented separately from web usage.
- Maintain `items.txt` as canonical item list.
- Surface errors clearly when offline or API lookups fail.

### Next

- Improve user-facing failure detail (per-item retry/reporting).
- Add optional export/import for itinerary persistence.
- Deprecated backend-era artifacts have been removed (`server.py`, `ui.html`, `vercel.json`).

### Later

- Add profit margin helper columns.
- Add optional route optimization mode (while preserving manual control).
- Add richer mobile ergonomics for fast in-game checking.

## Verification Checklist

1. Edit `items.txt`, reload prices, and confirm item set changes in UI.
2. Load once, reload again, and verify cached status message appears.
3. Click **Clear Cache & Reload** and verify fresh fetch behavior.
4. Disable network and verify clear offline/error status.
5. Build itinerary, generate route, and copy route text successfully.
6. Confirm at least one item shows both `Direct` and `Combined (n)` row types when small stacks exist.
7. Click `History` for a world row and confirm recent sold entries render.

## Tonight Launch Checklist

1. Commit and push your latest changes to the default branch.
2. In GitHub repo settings, enable Pages and set source to the default branch root.
3. Wait for Pages to publish, then open the site URL.
4. Run a 5-minute smoke test:
	- Click **Load Live Prices** and confirm results render.
	- Click a few world rows and confirm itinerary count increases.
	- Click **Generate Route** and confirm modal output.
	- Click **Export Itinerary**, then **Import Itinerary** with that file.
	- Click **Clear Cache & Reload** and confirm a fresh load starts.
5. Keep one fallback plan for tonight:
	- If API calls are flaky, reload once and use cached data from the latest successful load.

## Local Preview (Optional)

If you want to test before pushing, run any static server in the project folder.

Example with Python:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

## Data Sources

- [Universalis](https://universalis.app/)
- [XIVAPI](https://xivapi.com/)

## License

MIT
