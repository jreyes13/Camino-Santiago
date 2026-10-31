#!/usr/bin/env python3
"""
fetch_osm_camino.py - Downloads official OpenStreetMap Camino relations and converts them
into standard GPX 1.1 tracks.
"""

import os
import sys
import json
import math
import ssl
import urllib.request
import re
from pathlib import Path

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
    """
    Given a list of coordinate lists [[(lat, lon), ...], ...],
    chains them into continuous segments.
    """
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

                # curr_end -> cand_start
                d1 = haversine(curr_end, c_start)
                if d1 < best_dist:
                    best_dist = d1
                    best_idx = i
                    best_reverse = False
                    best_at_start = False

                # curr_end -> cand_end (reverse cand)
                d2 = haversine(curr_end, c_end)
                if d2 < best_dist:
                    best_dist = d2
                    best_idx = i
                    best_reverse = True
                    best_at_start = False

                # cand_end -> curr_start (prepend cand)
                d3 = haversine(c_end, curr_start)
                if d3 < best_dist:
                    best_dist = d3
                    best_idx = i
                    best_reverse = False
                    best_at_start = True

                # cand_start -> curr_start (prepend cand reversed)
                d4 = haversine(c_start, curr_start)
                if d4 < best_dist:
                    best_dist = d4
                    best_idx = i
                    best_reverse = True
                    best_at_start = True

            # If within 300 meters, connect
            if best_idx is not None and best_dist < 300:
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

def relation_to_gpx(relation_id, track_name, description, output_path):
    url = f"https://api.openstreetmap.org/api/0.6/relation/{relation_id}/full.json"
    print(f"Fetching relation {relation_id} ({track_name}) from OSM API...")

    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"User-Agent": "CaminoSantiagoGIS/1.0"})
    
    with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    nodes = {}
    ways = {}
    rel = None

    for elem in data.get('elements', []):
        t = elem.get('type')
        if t == 'node':
            nodes[elem['id']] = (elem['lat'], elem['lon'])
        elif t == 'way':
            ways[elem['id']] = elem.get('nodes', [])
        elif t == 'relation' and elem.get('id') == relation_id:
            rel = elem

    ways_coords = []
    if rel and 'members' in rel:
        for m in rel['members']:
            if m.get('type') == 'way' and m.get('ref') in ways:
                node_ids = ways[m['ref']]
                coord_list = [nodes[nid] for nid in node_ids if nid in nodes]
                if len(coord_list) >= 2:
                    ways_coords.append(coord_list)
    else:
        for node_ids in ways.values():
            coord_list = [nodes[nid] for nid in node_ids if nid in nodes]
            if len(coord_list) >= 2:
                ways_coords.append(coord_list)

    if not ways_coords:
        print(f"No coordinates extracted for relation {relation_id}")
        return None

    segments = assemble_ways(ways_coords)
    total_pts = sum(len(s) for s in segments)
    print(f" -> Assembled {len(segments)} segments with {total_pts} total points.")

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

    print(f" -> Saved GPX to {output_path}")
    return segments

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

TARGET_RELATIONS = [
    # Camino Aragonés
    {
        "id": 2163936,
        "code": "ES02",
        "name": "Camino Aragonés",
        "desc": "Somport a Puente la Reina (GR 65.3)",
        "path": "GPX/ES02-Camino-Aragones/ES02-Camino-Aragones.gpx"
    },
    # Camino de Invierno
    {
        "id": 1868399,
        "code": "ES14",
        "name": "Camino de Invierno",
        "desc": "Ponferrada a Santiago de Compostela por la Ribeira Sacra",
        "path": "GPX/ES14-Camino-de-Invierno/ES14-Camino-de-Invierno.gpx"
    },
    # Vía de la Plata: 3 tramos + combinado
    {
        "id": 16949978,
        "code": "ES07",
        "name": "Vía de la Plata - Tramo 1 (Sevilla a Mérida)",
        "desc": "Sevilla a Mérida",
        "path": "GPX/ES07-Via-de-la-Plata/ES07a01-Sevilla-Merida.gpx"
    },
    {
        "id": 16949977,
        "code": "ES07",
        "name": "Vía de la Plata - Tramo 2 (Mérida a Salamanca)",
        "desc": "Mérida a Salamanca",
        "path": "GPX/ES07-Via-de-la-Plata/ES07a02-Merida-Salamanca.gpx"
    },
    {
        "id": 16949976,
        "code": "ES07",
        "name": "Vía de la Plata - Tramo 3 (Salamanca a Astorga)",
        "desc": "Salamanca a Astorga",
        "path": "GPX/ES07-Via-de-la-Plata/ES07a03-Salamanca-Astorga.gpx"
    },
    # Camino Sanabrés: 2 tramos
    {
        "id": 2164353,
        "code": "ES08",
        "name": "Camino Sanabrés - Tramo Este (Granja de Moreruela a Ourense)",
        "desc": "Granja de Moreruela a Ourense por Puebla de Sanabria",
        "path": "GPX/ES08-Camino-Sanabres/ES08a01-GranjaDeMoreruela-Ourense.gpx"
    },
    {
        "id": 2164354,
        "code": "ES08",
        "name": "Camino Sanabrés - Tramo Oeste (Ourense a Santiago)",
        "desc": "Ourense a Santiago de Compostela",
        "path": "GPX/ES08-Camino-Sanabres/ES08a02-Ourense-Santiago.gpx"
    }
]

if __name__ == '__main__':
    for item in TARGET_RELATIONS:
        try:
            print(f"\n==========================================")
            print(f"Downloading {item['name']} ({item['code']})...")
            relation_to_gpx(item['id'], item['name'], item['desc'], item['path'])
        except Exception as e:
            print(f"Error downloading {item['name']}: {e}")
