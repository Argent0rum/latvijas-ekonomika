"""Downloads every indicator in config/raditaji.yaml for every country in config/valstis.yaml
from the Eurostat API and saves one file the dashboard reads: docs/data/dati.json.

Run by GitHub Actions every day. If one indicator fails (e.g. Eurostat is busy or a code changed),
the previous data for that indicator is kept and the problem is written to docs/data/statuss.json.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data"
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}"
START = "2000"


def fetch(dataset, filters, geos, tries=4):
    """Ask Eurostat for one dataset, filtered, for the given countries. Returns the JSON-stat answer."""
    params = [("format", "JSON"), ("lang", "EN"), ("sinceTimePeriod", START)]
    params += [(k, v) for k, v in filters.items()]
    params += [("geo", g) for g in geos]
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(API.format(ds=dataset), params=params, timeout=120)
            if r.status_code == 200:
                return r.json()
            msg = f"HTTP {r.status_code}: {r.text[:300]}"
            if r.status_code in (400, 404):
                raise ValueError(msg)          # wrong code or filter: retrying won't help
        except ValueError:
            raise
        except Exception as e:  # network trouble
            msg = str(e)
        if attempt < tries:
            time.sleep(5 * attempt)
    raise RuntimeError(msg)


def to_series(d):
    """JSON-stat -> {geo: [[period, value, flag], ...]} (only the geo and time dimensions may vary)."""
    ids, sizes = d["id"], d["size"]
    cats = {}
    for dim in ids:
        idx = d["dimension"][dim]["category"]["index"]
        pos = idx if isinstance(idx, list) else sorted(idx, key=idx.get)
        cats[dim] = pos
    for dim, n in zip(ids, sizes):
        if dim not in ("geo", "time") and n != 1:
            raise ValueError(f"filter not specific enough: dimension '{dim}' has {n} values — add it to 'filtri'")
    strides = {dim: 1 for dim in ids}
    acc = 1
    for dim, n in reversed(list(zip(ids, sizes))):
        strides[dim] = acc
        acc *= n
    status = d.get("status", {}) or {}
    out = {}
    for flat_s, val in d.get("value", {}).items():
        flat = int(flat_s)
        geo = cats["geo"][(flat // strides["geo"]) % len(cats["geo"])]
        per = cats["time"][(flat // strides["time"]) % len(cats["time"])]
        out.setdefault(geo, []).append([per, val, status.get(flat_s, "")])
    for geo in out:
        out[geo].sort(key=lambda r: r[0])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load((ROOT / "config" / "raditaji.yaml").read_text())
    countries = yaml.safe_load((ROOT / "config" / "valstis.yaml").read_text())
    geos = [c["kods"] for c in countries]
    prev_path = OUT / "dati.json"
    prev = {i["id"]: i for i in json.loads(prev_path.read_text())["raditaji"]} if prev_path.exists() else {}

    indicators, status = [], []
    for ind in cfg["raditaji"]:
        rec = {k: v for k, v in ind.items() if k not in ("filtri", "papildinat_ar")}
        rec["avots_url"] = f"https://ec.europa.eu/eurostat/databrowser/view/{ind['datu_kopa']}/default/table"
        try:
            d = fetch(ind["datu_kopa"], ind["filtri"], geos)
            series = to_series(d)
            rec["atjaunots_eurostat"] = d.get("updated")
            ext = ind.get("papildinat_ar")
            if ext:   # fill earlier years from an older dataset (e.g. inflation before the 2026 classification change)
                try:
                    old = to_series(fetch(ext["datu_kopa"], ext["filtri"], geos))
                    for g, rows in old.items():
                        first = series[g][0][0] if series.get(g) else "9999"
                        series[g] = [r for r in rows if r[0] < first] + series.get(g, [])
                except Exception as e:
                    print(f"  (older series for {ind['id']} skipped: {e})")
            rec["dati"] = series
            latest = {g: (s[-1][0] if s else None) for g, s in series.items()}
            status.append({"id": ind["id"], "ok": True, "punkti": sum(len(s) for s in series.values()), "jaunakais": latest})
            print(f"OK   {ind['id']:<24} " + ", ".join(f"{g}:{p}" for g, p in latest.items()))
        except Exception as e:
            status.append({"id": ind["id"], "ok": False, "kluda": str(e)[:400]})
            print(f"FAIL {ind['id']:<24} {e}")
            if ind["id"] in prev:     # keep yesterday's numbers rather than showing nothing
                rec["dati"] = prev[ind["id"]].get("dati", {})
                rec["atjaunots_eurostat"] = prev[ind["id"]].get("atjaunots_eurostat")
            else:
                rec["dati"] = {}
        indicators.append(rec)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    data = {"generets": now, "valstis": countries, "kategorijas": cfg["kategorijas"], "raditaji": indicators}
    prev_body = json.loads(prev_path.read_text()) if prev_path.exists() else None
    if prev_body and {k: v for k, v in prev_body.items() if k != "generets"} == {k: v for k, v in data.items() if k != "generets"}:
        print("No changes since last run.")
        return
    prev_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    (OUT / "statuss.json").write_text(json.dumps({"generets": now, "raditaji": status}, ensure_ascii=False, indent=1))
    ok = sum(s["ok"] for s in status)
    print(f"\nSaved docs/data/dati.json — {ok}/{len(status)} indicators OK")


if __name__ == "__main__":
    main()
