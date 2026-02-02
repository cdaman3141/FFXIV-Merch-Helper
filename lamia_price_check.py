import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import urlopen, Request

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(WORKSPACE_DIR, "items.txt")
CACHE_PATH = os.path.join(WORKSPACE_DIR, ".item_cache.json")

AMERICAN_DCS = ["Aether", "Primal", "Crystal", "Dynamis"]

USER_AGENT = "lamia-price-check/1.0"


@dataclass
class ListingInfo:
    world: str
    price: int
    quantity: int


@dataclass
class ItemResult:
    name: str
    lamia_lowest: Optional[int]
    lamia_median: Optional[int]
    lamia_reasonable: Optional[int]
    best_listings: List[ListingInfo]


def http_get_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_cache() -> Dict[str, int]:
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: int(v) for k, v in data.items()}
    except Exception:
        return {}


def save_cache(cache: Dict[str, int]) -> None:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip()).lower()


def parse_items_from_file(path: str) -> List[str]:
    items: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            name = line.strip()
            if not name or name.startswith("#"):
                continue
            items.append(name)
    return items


def xivapi_lookup_item_id(name: str) -> Optional[int]:
    query = urlencode({"string": name, "indexes": "item", "limit": 3})
    url = f"https://xivapi.com/search?{query}"
    data = http_get_json(url)
    results = data.get("Results") or []
    if not results:
        return None

    norm = normalize_name(name)
    for r in results:
        if normalize_name(r.get("Name", "")) == norm:
            return int(r.get("ID"))
    return int(results[0].get("ID"))


def get_item_id(name: str, cache: Dict[str, int], pause: float = 0.2) -> Optional[int]:
    norm = normalize_name(name)
    if norm in cache:
        return cache[norm]
    item_id = xivapi_lookup_item_id(name)
    if item_id:
        cache[norm] = item_id
        time.sleep(pause)
    return item_id


def get_lamia_price(item_id: int, min_qty: int = 1) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Returns (lowest, median, reasonable_sell_price).
    - lowest: absolute lowest listing
    - median: median price across all listings
    - reasonable_sell_price: price where there's actual volume (quantity >= min_qty)
    """
    url = f"https://universalis.app/api/v2/Lamia/{item_id}"
    data = http_get_json(url)
    listings = data.get("listings") or []
    if not listings:
        return None, None, None
    
    prices = [int(l["pricePerUnit"]) for l in listings]
    lowest = min(prices)
    
    # Median
    sorted_prices = sorted(prices)
    median = sorted_prices[len(sorted_prices) // 2]
    
    # Reasonable sell price: price where quantity >= min_qty
    volume_listings = [l for l in listings if int(l.get("quantity", 0)) >= min_qty]
    reasonable = None
    if volume_listings:
        reasonable = int(min(l["pricePerUnit"] for l in volume_listings))
    
    return lowest, median, reasonable


def get_best_listings(item_id: int, dcs: Iterable[str], min_qty: int, limit: Optional[int] = None) -> List[ListingInfo]:
    best: List[ListingInfo] = []
    for dc in dcs:
        url = f"https://universalis.app/api/v2/{dc}/{item_id}"
        data = http_get_json(url)
        listings = data.get("listings") or []
        valid = [l for l in listings if int(l.get("quantity", 0)) >= min_qty]
        if not valid:
            continue
        for l in valid:
            best.append(
                ListingInfo(
                    world=l.get("worldName", dc),
                    price=int(l["pricePerUnit"]),
                    quantity=int(l.get("quantity", 0)),
                )
            )
    best.sort(key=lambda x: (x.price, -x.quantity, x.world))
    return best if limit is None else best[:limit]


def build_report(results: List[ItemResult]) -> str:
    lines: List[str] = []
    lines.append("LAMIA VS AMERICAN DC LOWS")
    lines.append("=" * 80)
    for r in results:
        lines.append(f"\n{r.name}")
        
        # Lamia prices
        if r.lamia_lowest is None:
            lines.append(f"  Lamia: n/a")
        else:
            lamia_str = f"lowest {r.lamia_lowest}"
            if r.lamia_median is not None:
                lamia_str += f" | median {r.lamia_median}"
            if r.lamia_reasonable is not None:
                lamia_str += f" | sell-price (qty≥10) {r.lamia_reasonable}"
            lines.append(f"  Lamia: {lamia_str}")
        
        # All listings elsewhere
        if not r.best_listings:
            lines.append("  Available elsewhere: n/a")
        else:
            lines.append("  Available elsewhere:")
            lines.append(f"    {'World':<15} {'Price':<10} {'Qty':<10}")
            lines.append(f"    {'-'*15} {'-'*10} {'-'*10}")
            for b in r.best_listings:
                lines.append(f"    {b.world:<15} {b.price:<10} {b.quantity:<10}")
    
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Lamia prices vs American DC lowest listings.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to the source list file.")
    parser.add_argument("--output", default=os.path.join(WORKSPACE_DIR, "lamia_report.txt"), help="Output report path.")
    parser.add_argument("--json-output", default=os.path.join(WORKSPACE_DIR, "lamia_data.json"), help="JSON data output path.")
    parser.add_argument("--min-qty", type=int, default=10, help="Minimum quantity for a listing to count.")
    parser.add_argument("--limit", type=int, default=None, help="Max listings per item (None = all).")
    parser.add_argument("--dcs", nargs="*", default=AMERICAN_DCS, help="Datacenters to check for buying.")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    items = parse_items_from_file(args.input)
    if not items:
        print("No items found in input file.", file=sys.stderr)
        return 1

    cache = load_cache()
    results: List[ItemResult] = []

    for name in items:
        item_id = get_item_id(name, cache)
        if not item_id:
            results.append(ItemResult(name=name, lamia_lowest=None, lamia_median=None, lamia_reasonable=None, best_listings=[]))
            continue
        lamia_lowest, lamia_median, lamia_reasonable = get_lamia_price(item_id, min_qty=args.min_qty)
        best_listings = get_best_listings(item_id, args.dcs, args.min_qty, args.limit)
        results.append(ItemResult(name=name, lamia_lowest=lamia_lowest, lamia_median=lamia_median, lamia_reasonable=lamia_reasonable, best_listings=best_listings))

    save_cache(cache)
    report = build_report(results)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    # Export JSON for UI
    json_data = []
    for r in results:
        json_data.append({
            "name": r.name,
            "lamia": {
                "lowest": r.lamia_lowest,
                "median": r.lamia_median,
                "reasonable_sell": r.lamia_reasonable,
            },
            "listings": [
                {"world": l.world, "price": l.price, "quantity": l.quantity}
                for l in r.best_listings
            ],
        })

    with open(args.json_output, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"Wrote report to {args.output}")
    print(f"Wrote JSON data to {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
