#!/usr/bin/env python3
"""
generate_catalog.py - Scans all GPX files in the repository, calculates
geospatial metrics (distance, elevation gain/loss, bounding box), eliminates
discontinuities/jumps, and produces:
- data/routes_catalog.json
- data/routes.geojson
- data/routes_geojson.js
"""

import os
import sys
import math
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in kilometers."""
    R = 6371.0088  # Mean Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def parse_gpx_track(gpx_path, max_jump_km=0.5):
    """
    Parses a GPX file and extracts:
    - name, desc
    - segments: list of coordinate segments (split at jumps > max_jump_km)
    - distance_km (strictly continuous walking distance, excluding teleports)
    - elevation min, max, gain (+), loss (-)
    - bounds: [min_lon, min_lat, max_lon, max_lat]
    """
    try:
        tree = ET.parse(gpx_path)
    except Exception as e:
        print(f"Error parsing {gpx_path}: {e}")
        return None

    root = tree.getroot()
    # Strip namespace for ease
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

    name_elem = root.find('.//trk/name')
    if name_elem is None or not name_elem.text:
        name_elem = root.find('.//metadata/name')
    track_name = name_elem.text.strip() if name_elem is not None and name_elem.text else Path(gpx_path).stem

    desc_elem = root.find('.//trk/desc')
    if desc_elem is None or not desc_elem.text:
        desc_elem = root.find('.//metadata/desc')
    track_desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ''

    # Discover track segments
    raw_segs = root.findall('.//trkseg')
    if not raw_segs:
        # Check routes or flat points
        raw_segs = root.findall('.//rte')
        if not raw_segs:
            raw_segs = [root]

    clean_segments = []
    total_distance_km = 0.0
    ele_gain = 0.0
    ele_loss = 0.0
    elevations = []

    min_lat, max_lat = 90.0, -90.0
    min_lon, max_lon = 180.0, -180.0
    total_point_count = 0

    for seg_elem in raw_segs:
        curr_subseg = []
        prev_lat, prev_lon, prev_ele = None, None, None

        pts_elems = seg_elem.findall('.//trkpt')
        if not pts_elems:
            pts_elems = seg_elem.findall('.//rtept')

        for pt_elem in pts_elems:
            try:
                lat = float(pt_elem.attrib['lat'])
                lon = float(pt_elem.attrib['lon'])
            except (KeyError, ValueError):
                continue

            ele_elem = pt_elem.find('ele')
            ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text else None

            pt_coords = (round(lon, 6), round(lat, 6), round(ele, 1) if ele is not None else None)
            if ele is not None:
                elevations.append(ele)

            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)
            min_lon = min(min_lon, lon)
            max_lon = max(max_lon, lon)

            if prev_lat is not None and prev_lon is not None:
                d = haversine_distance(prev_lat, prev_lon, lat, lon)
                if d > max_jump_km:
                    # Jump detected: break line so no straight diagonal chord is drawn
                    if len(curr_subseg) >= 2:
                        clean_segments.append(curr_subseg)
                    curr_subseg = []
                else:
                    total_distance_km += d
                    if prev_ele is not None and ele is not None:
                        diff = ele - prev_ele
                        if diff > 0:
                            ele_gain += diff
                        else:
                            ele_loss += abs(diff)

            curr_subseg.append(pt_coords)
            total_point_count += 1
            prev_lat, prev_lon, prev_ele = lat, lon, ele

        if len(curr_subseg) >= 2:
            clean_segments.append(curr_subseg)

    if not clean_segments:
        return None

    return {
        'name': track_name,
        'description': track_desc,
        'file_path': str(gpx_path),
        'point_count': total_point_count,
        'segment_count': len(clean_segments),
        'distance_km': round(total_distance_km, 2),
        'min_elevation_m': round(min(elevations), 1) if elevations else None,
        'max_elevation_m': round(max(elevations), 1) if elevations else None,
        'elevation_gain_m': round(ele_gain, 1) if elevations else None,
        'elevation_loss_m': round(ele_loss, 1) if elevations else None,
        'bounds': [round(min_lon, 5), round(min_lat, 5), round(max_lon, 5), round(max_lat, 5)],
        'segments': clean_segments
    }

def simplify_segment(pts, epsilon=0.00008):
    """
    Ramer-Douglas-Peucker (RDP) iterative polyline simplification.
    Preserves true curves and switchbacks with ~8m precision while eliminating
    redundant collinear points. Never introduces artificial chord jumps.
    """
    if len(pts) <= 2:
        return pts

    stack = [(0, len(pts) - 1)]
    keep = [False] * len(pts)
    keep[0] = True
    keep[-1] = True

    while stack:
        start, end = stack.pop()
        x1, y1 = pts[start][0], pts[start][1]
        x2, y2 = pts[end][0], pts[end][1]
        dx = x2 - x1
        dy = y2 - y1
        den = math.hypot(dy, dx)

        dmax = 0.0
        index = 0
        if den == 0:
            for i in range(start + 1, end):
                d = math.hypot(pts[i][0] - x1, pts[i][1] - y1)
                if d > dmax:
                    index, dmax = i, d
        else:
            for i in range(start + 1, end):
                d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / den
                if d > dmax:
                    index, dmax = i, d

        if dmax > epsilon:
            keep[index] = True
            stack.append((start, index))
            stack.append((index, end))

    return [pts[i] for i in range(len(pts)) if keep[i]]

def identify_route_category(rel_path):
    parts = Path(rel_path).parts
    filename = Path(rel_path).name

    if len(parts) >= 2:
        folder = parts[1]
        if folder == '01-Camino_Frances':
            return 'Camino Francés', 'ES01', '#E63946', 'es_main'
        elif folder == 'ES02-Camino-Aragones':
            return 'Camino Aragonés', 'ES02', '#D90429', 'es_main'
        elif folder == 'ES03-Camino-del-Norte':
            return 'Camino del Norte', 'ES03', '#1D3557', 'es_main'
        elif folder == 'ES04-Camino-Primitivo':
            return 'Camino Primitivo', 'ES04', '#8338EC', 'es_main'
        elif folder == 'ES05-Camino-Vasco-Interior':
            return 'Camino Vasco del Interior', 'ES05', '#588157', 'es_connectors'
        elif folder == 'ES07-Via-de-la-Plata':
            return 'Vía de la Plata', 'ES07', '#FB8500', 'es_main'
        elif folder == 'ES08-Camino-Sanabres':
            return 'Camino Sanabrés', 'ES08', '#023047', 'es_main'
        elif folder == 'ES09-Camino-Portugues-Central':
            return 'Camino Portugués Central (España)', 'ES09', '#2A9D8F', 'pt'
        elif folder == 'ES10-Camino-Portugues-de-la-Costa':
            return 'Camino Portugués de la Costa (España)', 'ES10', '#0077B6', 'pt'
        elif folder == 'ES11-Camino-Ingles':
            return 'Camino Inglés', 'ES11', '#3A86FF', 'es_main'
        elif folder == 'ES12-Camino-de-Madrid':
            return 'Camino de Madrid', 'ES12', '#457B9D', 'es_connectors'
        elif folder == 'ES13-Camino-Fisterra-Muxia':
            return 'Camino de Fisterra y Muxía', 'ES13', '#E76F51', 'es_main'
        elif folder == 'ES14-Camino-de-Invierno':
            return 'Camino de Invierno', 'ES14', '#6A994E', 'es_main'
        elif folder == 'ES15-Camino-Mozarabe':
            return 'Camino Mozárabe', 'ES15', '#BC6C25', 'es_connectors'
        elif folder == 'ES16-Camino-de-Levante':
            return 'Camino de Levante', 'ES16', '#D4A373', 'es_connectors'
        elif folder == 'ES17-Camino-del-Ebro':
            return 'Camino del Ebro', 'ES17', '#0096C7', 'es_connectors'
        elif folder == 'ES18-Camino-Catalan':
            return 'Camino Catalán', 'ES18', '#F77F00', 'es_connectors'
        elif folder == 'ES19-Camino-del-Sureste':
            return 'Camino del Sureste', 'ES19', '#AE2012', 'es_connectors'
        elif folder == 'ES21-Camino-Olvidado':
            return 'Camino Olvidado', 'ES21', '#606C38', 'es_connectors'
        elif folder == 'ES25-Camino-del-Salvador':
            return 'Camino del Salvador', 'ES25', '#7209B7', 'es_connectors'
        elif folder == 'EU' and len(parts) >= 3:
            if parts[2] == 'CZ':
                return 'Rutas Checas (Jakubská cesta)', 'EU-CZ', '#E76F51', 'eu_central'
            elif parts[2] == 'DE':
                return 'Rutas Alemanas (Jakobsweg)', 'EU-DE', '#F4A261', 'eu_central'
            elif parts[2] == 'FR':
                return 'Rutas Francesas (Voies de Saint-Jacques)', 'EU-FR', '#3D5A80', 'fr'
            elif parts[2] == 'PT':
                return 'Camino Portugués en Portugal', 'EU-PT', '#058C42', 'pt'

    if 'GoogleMaps_Praga_Santiago' in filename or 'checa' in filename.lower():
        return 'Europa Central (Praga - Santiago)', 'EU-CZ', '#E76F51', 'eu_central'

    return 'Otras Rutas', 'OTHER', '#6C757D', 'other'

def build_catalog(repo_root='.'):
    gpx_dir = Path(repo_root) / 'GPX'
    all_gpx = sorted(list(gpx_dir.rglob('*.gpx')))
    print(f"Found {len(all_gpx)} GPX files to analyze...")

    catalog = {
        'total_tracks': 0,
        'total_distance_km': 0.0,
        'routes': {}
    }

    geojson_features = []

    for gpx_file in all_gpx:
        rel = gpx_file.relative_to(repo_root)
        cat_name, cat_code, cat_color, region_group = identify_route_category(rel)

        data = parse_gpx_track(gpx_file)
        if not data:
            continue

        catalog['total_tracks'] += 1
        catalog['total_distance_km'] += data['distance_km']

        if cat_code not in catalog['routes']:
            catalog['routes'][cat_code] = {
                'code': cat_code,
                'name': cat_name,
                'color': cat_color,
                'region_group': region_group,
                'total_distance_km': 0.0,
                'stages_count': 0,
                'stages': []
            }

        route_entry = catalog['routes'][cat_code]
        route_entry['total_distance_km'] += data['distance_km']
        route_entry['stages_count'] += 1

        stage_info = {
            'name': data['name'],
            'file': str(rel),
            'distance_km': data['distance_km'],
            'elevation_gain_m': data['elevation_gain_m'],
            'elevation_loss_m': data['elevation_loss_m'],
            'min_elevation_m': data['min_elevation_m'],
            'max_elevation_m': data['max_elevation_m'],
            'point_count': data['point_count'],
            'segment_count': data['segment_count'],
            'bounds': data['bounds']
        }
        route_entry['stages'].append(stage_info)

        # Simplify segments individually to avoid connecting gaps
        simplified_segs = [simplify_segment(seg) for seg in data['segments']]

        if len(simplified_segs) == 1:
            geom = {
                'type': 'LineString',
                'coordinates': [[p[0], p[1]] for p in simplified_segs[0]]
            }
        else:
            geom = {
                'type': 'MultiLineString',
                'coordinates': [[[p[0], p[1]] for p in s] for s in simplified_segs]
            }

        geojson_features.append({
            'type': 'Feature',
            'properties': {
                'route_code': cat_code,
                'route_name': cat_name,
                'region_group': region_group,
                'stage_name': data['name'],
                'file': str(rel),
                'distance_km': data['distance_km'],
                'ele_gain': data['elevation_gain_m'],
                'ele_loss': data['elevation_loss_m'],
                'color': cat_color
            },
            'geometry': geom
        })

    catalog['total_distance_km'] = round(catalog['total_distance_km'], 1)
    for r in catalog['routes'].values():
        r['total_distance_km'] = round(r['total_distance_km'], 1)

    os.makedirs(Path(repo_root) / 'data', exist_ok=True)

    catalog_path = Path(repo_root) / 'data' / 'routes_catalog.json'
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"Wrote catalog to {catalog_path}")

    geojson_path = Path(repo_root) / 'data' / 'routes.geojson'
    geojson_data = {
        'type': 'FeatureCollection',
        'features': geojson_features
    }
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False)
    print(f"Wrote GeoJSON to {geojson_path}")

    geojson_js_path = Path(repo_root) / 'data' / 'routes_geojson.js'
    with open(geojson_js_path, 'w', encoding='utf-8') as f:
        f.write('window.ROUTES_GEOJSON = ' + json.dumps(geojson_data, ensure_ascii=False) + ';')
    print(f"Wrote GeoJSON JS to {geojson_js_path}")

    return catalog

if __name__ == '__main__':
    catalog = build_catalog()
    print("\n===============================")
    print("   RESUMEN GENERAL ACTUALIZADO  ")
    print("===============================")
    print(f"Total de archivos GPX procesados: {catalog['total_tracks']}")
    print(f"Distancia total continua acumulada: {catalog['total_distance_km']:,} km")
    for code, r in sorted(catalog['routes'].items()):
        print(f" - [{code:5}] {r['name']:38}: {r['stages_count']:3} archivos, {r['total_distance_km']:>9.1f} km ({r['region_group']})")
