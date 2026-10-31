#!/usr/bin/env python3
"""
import_open_pilgrimages.py - Downloads and processes stage tracks for:
- Camino del Norte (ES03)
- Camino Primitivo (ES04)
- Camino Inglés (ES11)
and converts each stage JSON into standard GPX 1.1 files.
"""

import os
import sys
import json
import urllib.request
import re
from pathlib import Path

BASE_RAW = "https://raw.githubusercontent.com/walktalkmeditate/open-pilgrimages/main/routes"

ROUTES = [
    {
        "id": "camino-norte",
        "code": "ES03",
        "folder": "GPX/ES03-Camino-del-Norte",
        "name": "Camino del Norte"
    },
    {
        "id": "camino-primitivo",
        "code": "ES04",
        "folder": "GPX/ES04-Camino-Primitivo",
        "name": "Camino Primitivo"
    },
    {
        "id": "camino-ingles",
        "code": "ES11",
        "folder": "GPX/ES11-Camino-Ingles",
        "name": "Camino Inglés"
    }
]

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def write_stage_gpx(out_path, title, route_name, points):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="CaminoSantiago-GIS (https://github.com/jreyes13/Camino-Santiago)"\n')
        f.write('  xmlns="http://www.topografix.com/GPX/1/1">\n')
        f.write('  <metadata>\n')
        f.write(f'    <name>{escape_xml(title)}</name>\n')
        f.write(f'    <desc>{escape_xml(route_name)}</desc>\n')
        f.write('  </metadata>\n')
        f.write('  <trk>\n')
        f.write(f'    <name>{escape_xml(title)}</name>\n')
        f.write('    <trkseg>\n')
        for pt in points:
            lat = pt.get("lat")
            lon = pt.get("lon")
            ele = pt.get("ele")
            if lat is not None and lon is not None:
                if ele is not None:
                    f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"><ele>{ele:.1f}</ele></trkpt>\n')
                else:
                    f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"/>\n')
        f.write('    </trkseg>\n')
        f.write('  </trk>\n')
        f.write('</gpx>\n')

def fetch_and_process():
    for r in ROUTES:
        route_id = r["id"]
        out_folder = r["folder"]
        os.makedirs(out_folder, exist_ok=True)
        print(f"\nProcessing {r['name']} ({r['code']})...")

        # 1. Download full route.gpx
        full_gpx_url = f"{BASE_RAW}/{route_id}/route.gpx"
        full_gpx_path = os.path.join(out_folder, f"{r['code']}-{route_id}-completo.gpx")
        try:
            print(f" Downloading full route GPX...")
            urllib.request.urlretrieve(full_gpx_url, full_gpx_path)
            print(f" Saved {full_gpx_path}")
        except Exception as e:
            print(f" Error fetching full route GPX: {e}")

        # 2. Query contents of ways to get all stages
        api_url = f"https://api.github.com/repos/walktalkmeditate/open-pilgrimages/contents/routes/{route_id}/ways"
        req = urllib.request.Request(api_url, headers={"User-Agent": "CaminoSantiagoGIS/1.0"})
        try:
            with urllib.request.urlopen(req) as resp:
                items = json.loads(resp.read().decode())
                stage_files = [it["name"] for it in items if it["name"].startswith("stage-") and it["name"].endswith(".json")]
                stage_files.sort()
                print(f" Found {len(stage_files)} stage files.")
                
                for sf in stage_files:
                    stage_url = f"{BASE_RAW}/{route_id}/ways/{sf}"
                    with urllib.request.urlopen(stage_url) as s_resp:
                        s_data = json.loads(s_resp.read().decode())
                        title = s_data.get("title", sf.replace(".json", ""))
                        pts = s_data.get("route", [])
                        
                        safe_title = re.sub(r'[^\w\-_\. ]', '', title).replace(' ', '_')
                        stage_num = sf.replace('.json', '').replace('stage-', '')
                        out_stage_gpx = os.path.join(out_folder, f"{r['code']}-Etapa-{stage_num}_{safe_title}.gpx")
                        
                        write_stage_gpx(out_stage_gpx, title, r["name"], pts)
                        print(f"  -> Generated {os.path.basename(out_stage_gpx)} ({len(pts)} pts)")
        except Exception as e:
            print(f" Error processing stages for {route_id}: {e}")

if __name__ == "__main__":
    fetch_and_process()
