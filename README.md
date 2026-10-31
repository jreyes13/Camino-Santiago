# 🥾 Way of St. James (Camino de Santiago) - GIS & Cartographic Repository

<p align="left">
  <img src="https://img.shields.io/badge/QGIS-3.x-589632?style=flat-square&logo=qgis&logoColor=white" alt="QGIS 3.x" />
  <img src="https://img.shields.io/badge/Formats-GPX%20%7C%20KML%20%7C%20GeoJSON-007acc?style=flat-square" alt="GPX, KML and GeoJSON Formats" />
  <img src="https://img.shields.io/badge/Coverage-17%2C346%20km-orange?style=flat-square" alt="17,346 km covered" />
  <img src="https://img.shields.io/badge/Tracks-172%20GPX-success?style=flat-square" alt="172 GPX tracks" />
  <img src="https://img.shields.io/badge/Data-IGN%20%2F%20CNIG%20%2F%20FEAACS-lightgrey?style=flat-square" alt="Data IGN / CNIG / FEAACS" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square" alt="GPL-3.0 License" />
</p>

An open repository dedicated to collecting, processing, standardizing, and visualizing the pilgrimage routes of the **Way of St. James (*Camino de Santiago*)**—including both traditional Iberian routes and feeder pathways across Central Europe—powered by Geographic Information Systems (**QGIS**) and modern web cartography.

---

## 📊 Global Route Catalog Summary

| Code | Route / Camino | Stages & Variants | Distance (km) | Format |
| :--- | :--- | :---: | :---: | :---: |
| **ES01** | Camino Francés | 32 | 809.8 km | GPX |
| **ES09** | Camino Portugués Central | 18 | 91.4 km | GPX / KML |
| **ES10** | Camino Portugués de la Costa | 10 | 78.1 km | GPX / KML |
| **ES12** | Camino de Madrid | 24 | 453.4 km | GPX / KML |
| **EU-CZ** | Rutas Jacobeas Checas (*Jakubská cesta*) | 7 | 1,382.6 km | GPX / KML |
| **EU-DE** | Rutas Alemanas (*Jakobsweg*) | 79 | 12,190.7 km | GPX / KML |
| **OTHER** | Gran Vía Trans-Europea (Praga – Santiago) | 2 | 2,340.1 km | GPX |
| **TOTAL** | **Red Jacobea Integrada** | **172** | **17,346.0 km** | **GPX** |

---

## 🗺️ Interactive Web Viewer

Open [`index.html`](file:///Users/jreyes13/GitHub/Camino%20Santiago/index.html) in any browser (or deploy to GitHub Pages) to interact with the full route network:
- **Base Layers**: OpenStreetMap, OpenTopoMap, CartoDB Positron, Esri Satellite.
- **Stage Search & Filtering**: Filter by Camino, stage name, or distance.
- **Elevation & Statistics**: Altimetric stats and direct 1-click GPX track downloads.

---

## 📌 Project Objectives

- **Geospatial Centralization**: Bring together detailed stages, trails, and variants of Jacobean routes, linking both the core trails in Spain and broader European feeder ways (Germany, Czech Republic).
- **Cartography & GIS with QGIS**: Maintain organized QGIS projects (`.qgz`) for visualization, topological validation, digital elevation model (DEM) analysis, and map generation.
- **Interoperability**: Provide clean tracks in standard formats (`.gpx`, `.kml`, and `.geojson`) suitable for GPS units, mobile apps (Komoot, Wikiloc, OsmAnd, Google Earth), and web-based map viewers.

---

## 📁 Repository Structure

```text
.
├── GPX/
│   ├── 01-Camino_Frances/                # Camino Francés (Stages 1 through 33) [.gpx]
│   ├── ES09-Camino-Portugues-Central/    # Camino Portugués Central [.gpx]
│   ├── ES10-Camino-Portugues-de-la-Costa/# Camino Portugués de la Costa [.gpx]
│   ├── ES12-Camino-de-Madrid/            # Camino de Madrid stages & variants [.gpx & .kml]
│   ├── EU/                               # European Jacobean trails
│   │   ├── CZ/                           # Czech Republic routes (Žitavská, Všerubská, etc.) [.gpx & .kml]
│   │   └── DE/                           # German Jakobsweg network (Via Baltica, Regia, etc.) [.gpx & .kml]
│   ├── GoogleMaps_Praga_Santiago.gpx     # Trans-European route connecting Prague to Santiago
│   └── 170615-camino-santiago-en-rep-checa-praga-radotin.gpx
├── QGIS/
│   ├── CaminoSantiago.qgz                # Primary QGIS map project (repaired & validated)
│   └── CaminoSantiago_OLD.qgz            # Legacy QGIS map project
├── data/
│   ├── routes_catalog.json               # Aggregated geospatial metadata (distances, elevations)
│   ├── routes.geojson                    # Full vector network for web mapping
│   └── routes_geojson.js                 # Standalone loader for local file viewing
├── scripts/
│   ├── kml_to_gpx.py                     # Lossless KML -> GPX 1.1 converter
│   └── generate_catalog.py               # Route parser, metrics calculator & GeoJSON builder
├── index.html                            # Interactive Leaflet web map viewer
├── LICENSE                               # GPL-3.0 License
└── README.md                             # Repository documentation
```

---

## 🛠️ Tooling & Scripts

### 1. Convert KML to GPX
```bash
python3 scripts/kml_to_gpx.py <file.kml o directorio>
```

### 2. Recalculate Catalog & GeoJSON
```bash
python3 scripts/generate_catalog.py
```

---

## 🗺️ Sources & Official Cartographic References

The geospatial data and routes are referenced against and verified with official mapping agencies and recognized pilgrim federations:

- **[IGN - National Geographic Information Infrastructure](https://nco.ign.es/Caminosantiago/)**: Official interactive map of Jacobean routes across Spain provided by the National Geographic Institute of Spain (*IGN*).
- **[CNIG Download Center](https://centrodedescargas.cnig.es/CentroDescargas/mapas-camino-santiago)**: Official digital cartography, aerial photography (PNOA), digital elevation models (DEM), and vector datasets of the Camino de Santiago.
- **[FEAACS - Spanish Federation of Associations of Friends of the Camino de Santiago](https://www.caminosantiago.org/cpperegrino/caminos/)**: Historical routes, stage itineraries, official variants, and hostel networks.
