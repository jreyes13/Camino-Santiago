#!/usr/bin/env python3
"""
kml_to_gpx.py - Converts KML Placemarks with LineStrings into valid GPX 1.1 files.
Works with standard Python library (no external dependencies required).
"""

import sys
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_coordinates_text(coord_text):
    """
    Parses KML coordinate text like 'lon,lat,ele lon,lat,ele' or lines of 'lon,lat[,ele]'.
    Returns a list of tuples: (lat, lon, ele_or_None).
    """
    pts = []
    tokens = coord_text.strip().split()
    for tok in tokens:
        parts = tok.split(',')
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                ele = float(parts[2]) if len(parts) >= 3 else None
                pts.append((lat, lon, ele))
            except ValueError:
                continue
    return pts

def extract_linestrings_from_kml(kml_path):
    """
    Extracts all Placemarks with LineString or MultiGeometry from a KML file.
    Returns list of dicts: {'name': str, 'description': str, 'segments': [list of pts]}
    """
    # Remove XML declaration if it has encoding issues or namespace issues
    with open(kml_path, 'rb') as f:
        content = f.read()

    # Normalize XML content
    content_str = content.decode('utf-8', errors='ignore')
    # Strip default namespace to simplify ElementTree parsing
    content_str = re.sub(r'xmlns="[^"]+"', '', content_str, count=1)

    root = ET.fromstring(content_str)
    
    placemarks = root.findall('.//Placemark')
    results = []

    for pm in placemarks:
        name_elem = pm.find('name')
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else Path(kml_path).stem
        
        desc_elem = pm.find('description')
        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ''

        coord_elems = pm.findall('.//coordinates')
        segments = []
        for c_elem in coord_elems:
            if c_elem.text:
                pts = parse_coordinates_text(c_elem.text)
                if pts:
                    segments.append(pts)
        
        if segments:
            results.append({
                'name': name,
                'description': desc,
                'segments': segments
            })
            
    return results

def write_gpx(output_path, track_name, description, segments):
    """
    Writes a GPX 1.1 file from given segments.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="CaminoSantiago-GIS (https://github.com/jreyes13/Camino-Santiago)"\n')
        f.write('  xmlns="http://www.topografix.com/GPX/1/1"\n')
        f.write('  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
        f.write('  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">\n')
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
            for lat, lon, ele in seg:
                if ele is not None:
                    f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"><ele>{ele:.1f}</ele></trkpt>\n')
                else:
                    f.write(f'      <trkpt lat="{lat:.6f}" lon="{lon:.6f}"/>\n')
            f.write('    </trkseg>\n')
        
        f.write('  </trk>\n')
        f.write('</gpx>\n')

def escape_xml(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def convert_kml_file(kml_path, output_dir=None):
    """
    Converts a single KML file. If it has multiple Placemarks, creates either separate GPX files or one combined.
    """
    kml_p = Path(kml_path)
    if output_dir is None:
        out_d = kml_p.parent
    else:
        out_d = Path(output_dir)

    tracks = extract_linestrings_from_kml(kml_path)
    if not tracks:
        return []

    created_files = []
    if len(tracks) == 1:
        tr = tracks[0]
        out_file = out_d / f"{kml_p.stem}.gpx"
        write_gpx(out_file, tr['name'], tr['description'], tr['segments'])
        created_files.append(out_file)
    else:
        # Multiple placemarks: save individual and also a merged one
        for i, tr in enumerate(tracks):
            safe_name = re.sub(r'[^\w\-_\.]', '_', tr['name'])
            out_file = out_d / f"{safe_name}.gpx"
            write_gpx(out_file, tr['name'], tr['description'], tr['segments'])
            created_files.append(out_file)
            
    return created_files

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 kml_to_gpx.py <file.kml or directory> [output_dir]")
        sys.exit(1)
    
    target = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None

    if os.path.isfile(target):
        res = convert_kml_file(target, out_arg)
        print(f"Created {len(res)} GPX files from {target}")
    elif os.path.isdir(target):
        count = 0
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.lower().endswith('.kml'):
                    p = os.path.join(root, file)
                    out_d = out_arg if out_arg else root
                    res = convert_kml_file(p, out_d)
                    count += len(res)
        print(f"Converted {count} GPX tracks from directory {target}")
