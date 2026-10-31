# 🥾 Way of St. James (Camino de Santiago) - GIS & Cartographic Repository

<p align="left">
  <a href="https://jreyes13.github.io/Camino-Santiago/"><img src="https://img.shields.io/badge/🌐_Live_Web_Map-jreyes13.github.io%2FCamino--Santiago-2A9D8F?style=for-the-badge&logo=leaflet&logoColor=white" alt="Live Web Map" /></a>
</p>

<p align="left">
  <img src="https://img.shields.io/badge/QGIS-3.x-589632?style=flat-square&logo=qgis&logoColor=white" alt="QGIS 3.x" />
  <img src="https://img.shields.io/badge/Formats-GPX%20%7C%20KML%20%7C%20GeoJSON-007acc?style=flat-square" alt="GPX, KML and GeoJSON Formats" />
  <img src="https://img.shields.io/badge/Coverage-23%2C636%20km-orange?style=flat-square" alt="23,636 km covered" />
  <img src="https://img.shields.io/badge/Tracks-218%20GPX-success?style=flat-square" alt="218 GPX tracks" />
  <img src="https://img.shields.io/badge/Data-IGN%20%2F%20CNIG%20%2F%20FEAACS%20%2F%20OSM-lightgrey?style=flat-square" alt="Data IGN / CNIG / FEAACS / OSM" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square" alt="GPL-3.0 License" />
</p>

An open repository dedicated to collecting, processing, standardizing, and visualizing the pilgrimage routes of the **Way of St. James (*Camino de Santiago*)**—including both traditional Iberian routes and feeder pathways across Central Europe—powered by Geographic Information Systems (**QGIS**) and modern web cartography.

---

## 📊 Global Route Catalog Summary

| Code | Route / Camino | Stages & Tracks | Distance (km) | Format |
| :--- | :--- | :---: | :---: | :---: |
| **ES01** | Camino Francés | 32 | 809.8 km | GPX |
| **ES02** | Camino Aragonés (Somport – Puente la Reina) | 1 | 72.9 km | GPX |
| **ES03** | Camino del Norte (Irún – Santiago, 34 etapas + trazado) | 35 | 2,160.3 km | GPX |
| **ES04** | Camino Primitivo (Oviedo – Santiago) | 1 | 411.3 km | GPX |
| **ES07** | Vía de la Plata (Sevilla – Astorga, 3 tramos) | 3 | 892.7 km | GPX |
| **ES08** | Camino Sanabrés (Granja de Moreruela – Santiago) | 2 | 1,052.3 km | GPX |
| **ES09** | Camino Portugués Central | 18 | 91.4 km | GPX / KML |
| **ES10** | Camino Portugués de la Costa | 10 | 78.1 km | GPX / KML |
| **ES11** | Camino Inglés (Ferrol – Santiago) | 1 | 191.8 km | GPX |
| **ES12** | Camino de Madrid (Madrid – Sahagún) | 24 | 453.4 km | GPX / KML |
| **ES13** | Camino de Fisterra y Muxía | 1 | 226.0 km | GPX |
| **ES14** | Camino de Invierno (Ponferrada – Santiago) | 1 | 388.4 km | GPX |
| **ES15** | Camino Mozárabe (Andalucía – Mérida) | 1 | 893.8 km | GPX |
| **EU-CZ** | Rutas Jacobeas Checas (*Jakubská cesta*) | 7 | 1,382.6 km | GPX / KML |
| **EU-DE** | Rutas Alemanas (*Jakobsweg*) | 79 | 12,190.7 km | GPX / KML |
| **OTHER** | Gran Vía Trans-Europea (Praga – Santiago) | 2 | 2,340.1 km | GPX |
| **TOTAL** | **Red Jacobea Integrada** | **218** | **23,635.6 km** | **GPX** |

---

## 🗺️ Interactive Web Viewer

👉 **Acceso directo online:** **[https://jreyes13.github.io/Camino-Santiago/](https://jreyes13.github.io/Camino-Santiago/)**

También puedes abrir directamente [`index.html`](index.html) de manera local en cualquier navegador:
- **Base Layers**: OpenStreetMap, OpenTopoMap, CartoDB Positron, Esri Satellite.
- **Stage Search & Filtering**: Búsqueda y filtrado en tiempo real por Camino, nombre de etapa o ciudad.
- **Elevation & Statistics**: Desniveles acumulados ($+$ y $-$), distancias y descarga directa en 1 clic de cada archivo `.gpx`.

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
│   ├── ES02-Camino-Aragones/             # Camino Aragonés [.gpx]
│   ├── ES03-Camino-del-Norte/            # Camino del Norte (34 etapas + completo) [.gpx]
│   ├── ES04-Camino-Primitivo/            # Camino Primitivo completo [.gpx]
│   ├── ES07-Via-de-la-Plata/             # Vía de la Plata (Sevilla, Mérida, Salamanca, Astorga) [.gpx]
│   ├── ES08-Camino-Sanabres/             # Camino Sanabrés (Granja, Ourense, Santiago) [.gpx]
│   ├── ES09-Camino-Portugues-Central/    # Camino Portugués Central [.gpx]
│   ├── ES10-Camino-Portugues-de-la-Costa/# Camino Portugués de la Costa [.gpx]
│   ├── ES11-Camino-Ingles/               # Camino Inglés completo [.gpx]
│   ├── ES12-Camino-de-Madrid/            # Camino de Madrid stages & variants [.gpx & .kml]
│   ├── ES13-Camino-Fisterra-Muxia/       # Camino de Fisterra y Muxía [.gpx]
│   ├── ES14-Camino-de-Invierno/          # Camino de Invierno [.gpx]
│   ├── ES15-Camino-Mozarabe/             # Camino Mozárabe [.gpx]
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
│   ├── import_open_pilgrimages.py        # Importer for stage-breakdown routes
│   ├── fetch_osm_camino.py               # OSM relation API fetcher & track assembler
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

### 3. Fetch Official OSM Camino Relations
```bash
python3 scripts/fetch_osm_camino.py
```

---

## 🗺️ Sources & Official Cartographic References

The geospatial data and routes are referenced against and verified with official mapping agencies and recognized pilgrim federations:

- **[IGN - National Geographic Information Infrastructure](https://nco.ign.es/Caminosantiago/)**: Official interactive map of Jacobean routes across Spain provided by the National Geographic Institute of Spain (*IGN*).
- **[CNIG Download Center](https://centrodedescargas.cnig.es/CentroDescargas/mapas-camino-santiago)**: Official digital cartography, aerial photography (PNOA), digital elevation models (DEM), and vector datasets of the Camino de Santiago.
- **[FEAACS - Spanish Federation of Associations of Friends of the Camino de Santiago](https://www.caminosantiago.org/cpperegrino/caminos/)**: Historical routes, stage itineraries, official variants, and hostel networks.
- **[OpenStreetMap & Open Pilgrimages](https://www.openstreetmap.org/)**: Community-verified collaborative cartography and high-precision GPS trace alignments.
