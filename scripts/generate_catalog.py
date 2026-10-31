#!/usr/bin/env python3
"""
generate_catalog.py - Scans all GPX files in the repository, calculates
geospatial metrics (distance, elevation gain/loss, bounding box), and produces:
- data/routes_catalog.json
- data/routes.geojson
- Updates or generates summary stats
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

def parse_gpx_track(gpx_path):
    """
    Parses a GPX file and extracts:
    - name, desc
    - coordinates: list of (lon, lat, ele)
    - distance_km
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

    points = []
    total_distance_km = 0.0
    ele_gain = 0.0
    ele_loss = 0.0
    elevations = []

    min_lat, max_lat = 90.0, -90.0
    min_lon, max_lon = 180.0, -180.0

    prev_lat, prev_lon, prev_ele = None, None, None

    for trkpt in root.findall('.//trkpt'):
        try:
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
        except (KeyError, ValueError):
            continue

        ele_elem = trkpt.find('ele')
        ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text else None

        points.append((lon, lat, ele) if ele is not None else (lon, lat))

        if ele is not None:
            elevations.append(ele)

        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lon = min(min_lon, lon)
        max_lon = max(max_lon, lon)

        if prev_lat is not None and prev_lon is not None:
            d = haversine_distance(prev_lat, prev_lon, lat, lon)
            total_distance_km += d

            if prev_ele is not None and ele is not None:
                diff = ele - prev_ele
                if diff > 0:
                    ele_gain += diff
                else:
                    ele_loss += abs(diff)

        prev_lat, prev_lon, prev_ele = lat, lon, ele

    if not points:
        return None

    return {
        'name': track_name,
        'description': track_desc,
        'file_path': str(gpx_path),
        'point_count': len(points),
        'distance_km': round(total_distance_km, 2),
        'min_elevation_m': round(min(elevations), 1) if elevations else None,
        'max_elevation_m': round(max(elevations), 1) if elevations else None,
        'elevation_gain_m': round(ele_gain, 1) if elevations else None,
        'elevation_loss_m': round(ele_loss, 1) if elevations else None,
        'bounds': [round(min_lon, 5), round(min_lat, 5), round(max_lon, 5), round(max_lat, 5)],
        'coordinates': points
    }

def simplify_coordinates(coords, max_points=250):
    """Downsample coordinates for lighter web map GeoJSON while preserving shape."""
    if len(coords) <= max_points:
        return coords
    step = len(coords) / max_points
    sampled = [coords[int(i * step)] for i in range(max_points)]
    if sampled[-1] != coords[-1]:
        sampled.append(coords[-1])
    return sampled

def identify_route_category(rel_path):
    parts = Path(rel_path).parts
    if len(parts) >= 2:
        if parts[1] == '01-Camino_Frances':
            return 'Camino Francés', 'ES01', '#E63946'
        elif parts[1] == 'ES12-Camino-de-Madrid':
            return 'Camino de Madrid', 'ES12', '#457B9D'
        elif parts[1] == 'ES09-Camino-Portugues-Central':
            return 'Camino Portugués Central', 'ES09', '#2A9D8F'
        elif parts[1] == 'ES10-Camino-Portugues-de-la-Costa':
            return 'Camino Portugués de la Costa', 'ES10', '#1D3557'
        elif parts[1] == 'EU' and len(parts) >= 3:
            if parts[2] == 'CZ':
                return 'Rutas Checas (Jakubská cesta)', 'EU-CZ', '#E76F51'
            elif parts[2] == 'DE':
                return 'Rutas Alemanas (Jakobsweg)', 'EU-DE', '#F4A261'
    return 'Otras Rutas', 'OTHER', '#6C757D'

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
        cat_name, cat_code, cat_color = identify_route_category(rel)

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
            'bounds': data['bounds']
        }
        route_entry['stages'].append(stage_info)

        # Build GeoJSON feature
        downsampled = simplify_coordinates(data['coordinates'])
        geojson_features.append({
            'type': 'Feature',
            'properties': {
                'route_code': cat_code,
                'route_name': cat_name,
                'stage_name': data['name'],
                'file': str(rel),
                'distance_km': data['distance_km'],
                'ele_gain': data['elevation_gain_m'],
                'ele_loss': data['elevation_loss_m'],
                'color': cat_color
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': [[p[0], p[1]] for p in downsampled]
            }
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

    return catalog

if __name__ == '__main__':
    catalog = build_catalog()
    print("\n--- RESUMEN DEL CATÁLOGO ---")
    print(f"Total de etapas/trazas analizadas: {catalog['total_tracks']}")
    print(f"Distancia total acumulada: {catalog['total_distance_km']:,} km")
    for code, r in sorted(catalog['routes'].items()):
        print(f" - [{code}] {r['name']}: {r['stages_count']} etapas / variantes, {r['total_distance_km']:,} km")
