# 🥾 Way of St. James (Camino de Santiago) - GIS & Cartographic Repository

<p align="left">
  <img src="https://img.shields.io/badge/QGIS-3.x-589632?style=flat-square&logo=qgis&logoColor=white" alt="QGIS 3.x" />
  <img src="https://img.shields.io/badge/Formats-GPX%20%7C%20KML-007acc?style=flat-square" alt="GPX and KML Formats" />
  <img src="https://img.shields.io/badge/Data-IGN%20%2F%20CNIG-lightgrey?style=flat-square" alt="Data IGN / CNIG" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square" alt="GPL-3.0 License" />
  <img src="https://img.shields.io/badge/Contributions-welcome-brightgreen?style=flat-square" alt="Contributions Welcome" />
  <img src="https://img.shields.io/github/last-commit/jreyes13/Camino-Santiago?style=flat-square&color=blue" alt="Last Commit" />
</p>

An open repository dedicated to collecting, processing, standardizing, and visualizing the pilgrimage routes of the **Way of St. James (*Camino de Santiago*)**—including both traditional Iberian routes and feeder pathways across Central Europe—powered by Geographic Information Systems (**QGIS**).

---

## 📌 Project Objectives

- **Geospatial Centralization**: Bring together detailed stages, trails, and variants of Jacobean routes, linking both the core trails in Spain and broader European feeder ways (Germany, Czech Republic).
- **Cartography & GIS with QGIS**: Maintain organized QGIS projects (`.qgz`) for visualization, topological validation, digital elevation model (DEM) analysis, and map generation.
- **Interoperability**: Provide clean tracks in standard formats (`.gpx` and `.kml`) suitable for GPS units, mobile apps (Komoot, Wikiloc, OsmAnd, Google Earth), and web-based map viewers.

---

## 🗺️ Sources & Official Cartographic References

The geospatial data and routes are referenced against and verified with official mapping agencies and recognized pilgrim federations:

- **[IGN - National Geographic Information Infrastructure](https://nco.ign.es/Caminosantiago/)**: Official interactive map of Jacobean routes across Spain provided by the National Geographic Institute of Spain (*IGN*).
- **[CNIG Download Center](https://centrodedescargas.cnig.es/CentroDescargas/mapas-camino-santiago)**: Official digital cartography, aerial photography (PNOA), digital elevation models (DEM), and vector datasets of the Camino de Santiago.
- **[FEAACS - Spanish Federation of Associations of Friends of the Camino de Santiago](https://www.caminosantiago.org/cpperegrino/caminos/)**: Historical routes, stage itineraries, official variants, and hostel networks.

---

## 📁 Repository Structure

The project is structured into spatial data files (`GPX/`) and QGIS project environments (`QGIS/`):

```text
.
├── GPX/
│   ├── 01-Camino_Frances/             # Full Camino Francés in GPX (Stages 1 through 33)
│   ├── ES12-Camino-de-Madrid/         # Camino de Madrid stages and variants (KML)
│   ├── EU/                            # European Jacobean trails
│   │   ├── CZ/                        # Czech Republic routes (Žitavská, Všerubská, Železná, etc.)
│   │   └── DE/                        # German Jakobsweg network (Via Baltica, Regia, Imperii, etc.)
│   ├── CPC.kml                        # Camino Portugués Central
│   ├── GoogleMaps_Praga_Santiago.gpx  # Trans-European route connecting Prague to Santiago
│   └── 170615-camino-santiago-en-rep-checa-praga-radotin.gpx
├── QGIS/
│   ├── CaminoSantiago.qgz             # Primary QGIS map project
│   └── CaminoSantiago_OLD.qgz         # Legacy QGIS map project
├── LICENSE                            # License terms of the repository
└── README.md                          # Repository documentation