# FFXIV Lamia Materia Price Checker

Automated price comparison tool for FFXIV materia trading. Check Lamia prices vs the cheapest prices across American datacenters (Aether, Primal, Crystal, Dynamis) to find profitable buying opportunities.

## Features

- 🔍 **Live Price Fetching**: Uses the Universalis API to pull real-time market data
- 📊 **Multi-Metric Analysis**: Shows lowest, median, and realistic sell prices on Lamia
- 🌎 **Multi-DC Comparison**: Finds cheapest listings across all American datacenters
- 🎯 **Interactive UI**: Select items and worlds, auto-generate your buying route
- 📈 **Batch Processing**: Check multiple materia types in one go

## Setup

### Local Development

1. Clone the repo and navigate to it:
   ```bash
   git clone https://github.com/yourusername/ffxiv-lamia-price-checker.git
   cd ffxiv-lamia-price-checker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Edit `items.txt` with the materia you want to track

4. Run the server:
   ```bash
   python server.py
   ```

5. Open `http://localhost:5000` in your browser

### Deploy to Vercel

1. Push to GitHub
2. Go to [vercel.com](https://vercel.com) and import your repo
3. Vercel auto-detects the Python config and deploys
4. Your live site is ready at `your-project.vercel.app`

## Usage

1. Click **"Load Data"** - fetches live prices from Universalis
2. **Select items** you want to buy (checkbox next to item name)
3. **Select worlds** where you want to buy from (checkboxes in the table)
4. Click **"Generate Route"** - builds your world-hopping order
5. **Copy** the route and follow it in-game

## How It Works

- **Lamia Prices** (your sell world):
  - Lowest: absolute floor price
  - Median: middle of the market
  - Sell Price: price where you'd realistically sell (qty ≥ 10)

- **Best Listings**: All available listings across American DCs, sorted by price + quantity

## Configuration

Edit `items.txt` to change which materia to track:
```
Quickarm Materia XII
Savage Might Materia XI
Piety Materia XII
# Lines starting with # are comments
```

Run with flags:
```bash
python lamia_price_check.py --min-qty 20 --limit 50
```

- `--min-qty`: Minimum quantity for a listing to count (default: 10)
- `--limit`: Max listings per item (default: all)
- `--dcs`: Datacenters to check (default: Aether, Primal, Crystal, Dynamis)

## API Reference

**GET `/api/fetch-prices`**
- Runs the price check script and returns JSON data
- Response: `{ "success": true, "data": [...], "message": "..." }`

## Data

Data is pulled from [Universalis](https://universalis.app/), the community-run FFXIV market board API. No login required.

## Notes

- The script caches item IDs locally to reduce XIVAPI calls
- First run may take 30-60 seconds depending on item count
- Respects rate limits on both Universalis and XIVAPI

## License

MIT
