"""
Rebuild the standalone dashboard after editing species_scores.csv.

Usage:  python3 rebuild_dashboard.py

Reads:   species_scores.csv, criterion_keys.csv, captive_breeding_v2.html (template)
Writes:  captive_breeding_v2.html with fresh embedded data (backup saved as .bak)

Needs only pandas (or edit to use csv module if pandas unavailable).
"""
import json
import re
import shutil

import pandas as pd

CRITERIA = [
    "iucn_status", "population_state", "trend_distribution",
    "husbandry_potential", "recovery_potential",
    "genetic_viability", "institutional_significance",
]

species = pd.read_csv("species_scores.csv")
keys = pd.read_csv("criterion_keys.csv")

records = []
for _, r in species.iterrows():
    rec = {"taxa": r["taxa"], "common": r["common_name"],
           "latin": r["latin_name"], "raw": {}, "n": {}}
    for c in CRITERIA:
        key = keys[keys["criterion"] == c]
        lookup = dict(zip(key["level"].str.strip(), key["score"]))
        val = str(r[c]).strip()
        if val not in lookup:
            raise SystemExit(
                f"Unrecognized level '{val}' for {c} "
                f"({r['latin_name']}). Add it to criterion_keys.csv first.")
        lo, hi = key["score"].min(), key["score"].max()
        rec["raw"][c] = val
        rec["n"][c] = round((lookup[val] - lo) / (hi - lo), 6)
    records.append(rec)

html = open("captive_breeding_v2.html", encoding="utf-8").read()
shutil.copy("captive_breeding_v2.html", "captive_breeding_v2.html.bak")
payload = "const DATA = " + json.dumps(records) + ";\n"
new_html, n = re.subn(
    r"const DATA = \[.*?\];\n",
    lambda m: payload,
    html, count=1, flags=re.S)
if n != 1:
    raise SystemExit("Could not find DATA block in HTML — template changed?")
open("captive_breeding_v2.html", "w", encoding="utf-8").write(new_html)
print(f"Rebuilt with {len(records)} species. Backup: captive_breeding_v2.html.bak")
