"""Helper for maintenance: shows what a Eurostat dataset contains (its dimensions and codes).

Use it when adding a new indicator, to find the right filter codes:
    python scripts/izpete.py une_rt_m prc_hpi_q
It asks Eurostat for Latvia's most recent value(s) and prints every dimension with its codes.
"""
import sys

import requests

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}?format=JSON&lang=EN&geo=LV&lastTimePeriod=1"


def explore(ds):
    print(f"\n=== {ds} ===")
    try:
        r = requests.get(API.format(ds=ds), timeout=90)
    except Exception as e:
        print("  REQUEST FAILED:", e); return
    if r.status_code != 200:
        print("  HTTP", r.status_code, r.text[:400]); return
    d = r.json()
    print("  label:", d.get("label"))
    print("  updated:", d.get("updated"), "| values:", len(d.get("value", {})))
    for dim in d["id"]:
        cat = d["dimension"][dim]["category"]
        idx = cat["index"]; lab = cat.get("label", {})
        codes = list(idx) if isinstance(idx, dict) else idx
        shown = ", ".join(f"{c}={lab.get(c, '')[:45]}" for c in codes[:40])
        print(f"  {dim} ({len(codes)}): {shown}{' …' if len(codes) > 40 else ''}")


if __name__ == "__main__":
    for ds in sys.argv[1:]:
        explore(ds)
