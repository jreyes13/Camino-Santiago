#!/usr/bin/env python3
"""
download_all_remaining.py - Unified downloader for:
1. France: 4 Historical Routes (Via Podiensis, Lemovicensis, Turonensis, Tolosana, Piémont)
2. Portugal: Complete Camino Portugués (Lisbon to Santiago & Costa)
3. Spain connectors: Camino del Salvador, Camino Vasco del Interior, Camino Olvidado, Camino del Ebro, Camino Catalán, Camino de Levante, Camino del Sureste.

Runs completely unattended in a single execution.
"""

import os
import sys
import json
import math
import ssl
import urllib.request
import urllib.parse
import re
from pathlib import Path

def get_opener():
    ctx = ssl._create_unverified_context()
    return ctx

def haversine(p1, p2):
    R = 6371000.0  # meters
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def assemble_ways(ways_coords):
    if not ways_coords:
        return []

    remaining = [list(w) for w in ways_coords if len(w) >= 2]
    segments = []

    while remaining:
        current_seg = remaining.pop(0)
        extended = True
        while extended:
            extended = False
            curr_start = current_seg[0]
            curr_end = current_seg[-1]

            best_idx = None
            best_dist = float('inf')
            best_reverse = False
            best_at_start = False

            for i, cand in enumerate(remaining):
                c_start, c_end = cand[0], cand[-1]

                d1 = haversine(curr_end, c_start)
                if d1 < best_dist:
                    best_dist = d1
                    best_idx = i
                    best_reverse = False
                    best_at_start = False

                d2 = haversine(curr_end, c_end)
                if d2 < best_dist:
                    best_dist = d2
                    best_idx = i
                    best_reverse = True
                    best_at_start = False

                d3 = haversine(c_end, curr_start)
                if d3 < best_dist:
                    best_dist = d3
                    best_idx = i
                    best_reverse = False
                    best_at_start = True

                d4 = haversine(c_start, curr_start)
                if d4 < best_dist:
                    best_dist = d4
                    best_idx = i
                    best_reverse = True
                    best_at_start = True

            # If within 400 meters, connect
            if best_idx is not None and best_dist < 400:
                cand = remaining.pop(best_idx)
                if best_reverse:
                    cand.reverse()
                if best_at_start:
                    current_seg = cand + current_seg
                else:
                    current_seg = current_seg + cand
                extended = True

        segments.append(current_seg)

    return segments

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def write_gpx_file(output_path, track_name, description, segments):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="CaminoSantiago-GIS (https://github.com/jreyes13/Camino-Santiago)"\n')
        f.write('  xmlns="http://www.topografix.com/GPX/1/1">\n')
        f.write('  <metadata>\n')
        f.write(f'    <name>{escape_xml(track_name)}</name>\n')
        if description:
            f.write(f'    <desc>{escape_xml(description)}</desc>\n')
        f.write('  </metadata>\n')
        f.write('  <trk>\n')
        f.write(f'    <name>{escape_xml(track_name)}</name>\n')
        if description:
            f.write(f'    <desc>{escape_xml(description)}</desc>\n')
        for seg in segments:
            f.write('    <trkseg>\n')
            for lat, lon in seg:
                f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"/>\n')
            f.write('    </trkseg>\n')
        f.write('  </trk>\n')
        f.write('</gpx>\n')

def fetch_osm_relation_recursive(relation_id, ctx, visited=None):
    if visited is None:
        visited = set()
    if relation_id in visited:
        return []
    visited.add(relation_id)

    url = f"https://api.openstreetmap.org/api/0.6/relation/{relation_id}/full.json"
    req = urllib.request.Request(url, headers={"User-Agent": "CaminoSantiagoGIS/1.0"})

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"   [!] Failed fetching relation {relation_id}: {e}")
        return []

    nodes = {}
    ways = {}
    child_relations = []
    root_rel = None

    for elem in data.get('elements', []):
        t = elem.get('type')
        if t == 'node':
            nodes[elem['id']] = (elem['lat'], elem['lon'])
        elif t == 'way':
            ways[elem['id']] = elem.get('nodes', [])
        elif t == 'relation':
            if elem.get('id') == relation_id:
                root_rel = elem
                for m in elem.get('members', []):
                    if m.get('type') == 'relation':
                        child_relations.append(m.get('ref'))

    ways_coords = []
    # If the relation contains direct ways
    if ways:
        for node_ids in ways.values():
            coord_list = [nodes[nid] for nid in node_ids if nid in nodes]
            if len(coord_list) >= 2:
                ways_coords.append(coord_list)

    # If it's a super-relation, recursively fetch its children
    if child_relations:
        print(f"   [i] Relation {relation_id} is a super-relation with {len(child_relations)} sub-routes. Fetching children...")
        for cid in child_relations:
            c_coords = fetch_osm_relation_recursive(cid, ctx, visited)
            ways_coords.extend(c_coords)

    return ways_coords

def download_osm_route(item, ctx):
    name = item["name"]
    code = item["code"]
    rel_id = item["rel_id"]
    output_path = item["path"]
    desc = item.get("desc", name)

    print(f"\n---> [{code}] {name} (OSM Relation: {rel_id})")
    ways_coords = fetch_osm_relation_recursive(rel_id, ctx)
    if not ways_coords:
        print(f"   [-] No coordinates found for {name}.")
        return False

    segments = assemble_ways(ways_coords)
    total_pts = sum(len(s) for s in segments)
    write_gpx_file(output_path, name, desc, segments)
    print(f"   [+] Saved GPX to {output_path} ({len(segments)} segments, {total_pts} points)")
    return True

def search_relation_id(query, ctx):
    """Searches Nominatim for a hiking/pilgrimage relation ID matching query."""
    q_enc = urllib.parse.quote(query)
    url = f"https://nominatim.openstreetmap.org/search?q={q_enc}&format=json&extratags=1"
    req = urllib.request.Request(url, headers={"User-Agent": "CaminoSantiagoGIS/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for d in data:
                if d.get("osm_type") == "relation":
                    return int(d.get("osm_id"))
    except Exception as e:
        print(f"Error searching Nominatim for '{query}': {e}")
    return None

def main():
    ctx = get_opener()

    # 1. FRANCE
    france_routes = [
        {
            "code": "FR01",
            "name": "Via Podiensis (Le Puy)",
            "rel_id": 138227,
            "desc": "Le Puy-en-Velay a Saint-Jean-Pied-de-Port (GR 65)",
            "path": "GPX/EU/FR/FR01-Via-Podiensis/FR01-Via-Podiensis.gpx"
        },
        {
            "code": "FR02",
            "name": "Via Lemovicensis (Vézelay)",
            "rel_id": 1106898,
            "desc": "Vézelay a Saint-Palais / Ostabat (GR 654)",
            "path": "GPX/EU/FR/FR02-Via-Lemovicensis/FR02-Via-Lemovicensis.gpx"
        },
        {
            "code": "FR03",
            "name": "Via Turonensis (París - Tours)",
            "rel_id": 187781,
            "desc": "París y Tours a Saint-Jean-Pied-de-Port (GR 655)",
            "path": "GPX/EU/FR/FR03-Via-Turonensis/FR03-Via-Turonensis.gpx"
        },
        {
            "code": "FR04",
            "name": "Via Tolosana (Arlés)",
            "rel_id": 389715,
            "desc": "Arlés a Somport / Camino Aragonés (GR 653)",
            "path": "GPX/EU/FR/FR04-Via-Tolosana/FR04-Via-Tolosana.gpx"
        },
        {
            "code": "FR05",
            "name": "Voie du Piémont Pyrénéen",
            "rel_id": 368453,
            "desc": "Narbona y Lourdes a Saint-Jean-Pied-de-Port (GR 78)",
            "path": "GPX/EU/FR/FR05-Voie-Piemont-Pyreneen/FR05-Voie-Piemont-Pyreneen.gpx"
        }
    ]

    # 2. PORTUGAL (Full route from Lisbon and Porto)
    portugal_routes = [
        {
            "code": "PT01",
            "name": "Camino Portugués Central (Lisboa - Oporto - Valença)",
            "rel_id": 385135,
            "desc": "Lisboa a Coimbra, Oporto y Valença do Minho",
            "path": "GPX/EU/PT/PT01-Camino-Portugues-Central/PT01-Camino-Portugues-Central.gpx"
        }
    ]

    # Also download Open-Pilgrimages full Portuguese route if available
    try:
        pt_url = "https://raw.githubusercontent.com/walktalkmeditate/open-pilgrimages/main/routes/camino-portugues/route.gpx"
        pt_out = "GPX/EU/PT/PT01-Camino-Portugues-Central/PT01-Camino-Portugues-OpenPilgrimages.gpx"
        os.makedirs(os.path.dirname(pt_out), exist_ok=True)
        print("\n---> Downloading Camino Portugués from Open-Pilgrimages...")
        urllib.request.urlretrieve(pt_url, pt_out)
        print(f"   [+] Saved {pt_out}")
    except Exception as e:
        print(f"   [-] Open-pilgrimages portugues: {e}")

    # 3. SPANISH CONNECTORS
    spain_connectors = [
        {
            "code": "ES17",
            "name": "Camino del Ebro",
            "rel_id": 62932,
            "desc": "Deltebre y Tortosa a Zaragoza y Logroño (enlace con Camino Francés)",
            "path": "GPX/ES17-Camino-del-Ebro/ES17-Camino-del-Ebro.gpx"
        },
        {
            "code": "ES18",
            "name": "Camino Catalán por Lleida",
            "rel_id": 382741,
            "desc": "Sant Pere de Rodes / Barcelona a Lleida y Logroño",
            "path": "GPX/ES18-Camino-Catalan/ES18-Camino-Catalan-Lleida.gpx"
        },
        {
            "code": "ES16",
            "name": "Camino de Levante",
            "rel_id": 3624753,
            "desc": "Valencia a Albacete, Toledo y Zamora",
            "path": "GPX/ES16-Camino-de-Levante/ES16-Camino-de-Levante.gpx"
        },
        {
            "code": "ES19",
            "name": "Camino del Sureste",
            "rel_id": 2401811,
            "desc": "Alicante a Albacete, Medina del Campo y Benavente",
            "path": "GPX/ES19-Camino-del-Sureste/ES19-Camino-del-Sureste.gpx"
        },
        {
            "code": "ES21",
            "name": "Camino Olvidado",
            "rel_id": 17264003,
            "desc": "Bilbao a Villafranca del Bierzo por la montaña cantábrica",
            "path": "GPX/ES21-Camino-Olvidado/ES21-Camino-Olvidado.gpx"
        }
    ]

    # Search dynamically for Camino del Salvador and Camino Vasco if needed
    print("\n---> Searching for Camino del Salvador relation...")
    salvador_id = search_relation_id("Camino de San Salvador", ctx) or search_relation_id("Camino del Salvador", ctx)
    if salvador_id:
        spain_connectors.append({
            "code": "ES25",
            "name": "Camino del Salvador (León - Oviedo)",
            "rel_id": salvador_id,
            "desc": "León a Oviedo (GR 100.5)",
            "path": "GPX/ES25-Camino-del-Salvador/ES25-Camino-del-Salvador.gpx"
        })
    else:
        print("   [!] Camino del Salvador relation not found via search; using fallback.")

    print("\n---> Searching for Camino Vasco del Interior relation...")
    vasco_id = search_relation_id("Camino Vasco del Interior", ctx)
    if vasco_id:
        spain_connectors.append({
            "code": "ES05",
            "name": "Camino Vasco del Interior",
            "rel_id": vasco_id,
            "desc": "Irún a Vitoria y Santo Domingo de la Calzada / Burgos",
            "path": "GPX/ES05-Camino-Vasco-Interior/ES05-Camino-Vasco-Interior.gpx"
        })

    all_targets = france_routes + portugal_routes + spain_connectors
    print(f"\n=======================================================")
    print(f"Starting unified download of {len(all_targets)} route networks...")
    print(f"=======================================================")

    count_ok = 0
    for target in all_targets:
        ok = download_osm_route(target, ctx)
        if ok:
            count_ok += 1

    print(f"\n=======================================================")
    print(f"Finished downloads: {count_ok}/{len(all_targets)} routes downloaded successfully.")
    print(f"=======================================================")

if __name__ == '__main__':
    main()
