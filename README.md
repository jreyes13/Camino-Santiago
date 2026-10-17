# 🥾 Caminos de Santiago - Repositorio Cartográfico y SIG

<p align="left">
  <img src="https://img.shields.io/badge/QGIS-3.x-589632?style=flat-square&logo=qgis&logoColor=white" alt="QGIS 3.x" />
  <img src="https://img.shields.io/badge/Formatos-GPX%20%7C%20KML-007acc?style=flat-square" alt="Formatos GPX y KML" />
  <img src="https://img.shields.io/badge/Datos-IGN%20%2F%20CNIG-lightgrey?style=flat-square" alt="Datos IGN / CNIG" />
  <img src="https://img.shields.io/badge/Licencia-GPL--3.0-blue?style=flat-square" alt="Licencia GPL-3.0" />
  <img src="https://img.shields.io/badge/Contribuidores-bienvenidos-brightgreen?style=flat-square" alt="Contribuciones bienvenidas" />
  <img src="https://img.shields.io/github/last-commit/jreyes13/Camino-Santiago?style=flat-square&color=blue" alt="Último commit" />
</p>

Repositorio abierto para la recopilación, análisis cartográfico, depuración y visualización de las rutas del **Camino de Santiago** (tanto los trazados peninsulares como las vías de conexión jacobeas en Centroeuropa), apoyado en herramientas de Sistemas de Información Geográfica (**QGIS**).

---

## 📌 Objetivos del Proyecto

- **Centralización geoespacial**: Reunir trazados jacobeos detallados por etapas y ramales, integrando tanto rutas clásicas en España como las conexiones europeas (Alemania, República Checa).
- **Cartografía y SIG con QGIS**: Mantener proyectos consolidados (`.qgz`) para visualización, edición topológica, cruce con Modelos Digitales del Terreno (MDT) y elaboración de mapas.
- **Interoperabilidad**: Proveer tracks en formatos estándar (`.gpx` y `.kml`) listos para GPS, smartphones (Komoot, Wikiloc, OsmAnd, Google Earth) o visores web.

---

## 🗺️ Fuentes y Referencias Cartográficas

Los datos y geometrías se contrastan y construyen a partir de cartografía oficial y fuentes de la comunidad jacobea:

- **[IGN - Infraestructura Nacional de Información Geográfica](https://nco.ign.es/Caminosantiago/)**: Visor oficial del Instituto Geográfico Nacional con la red de rutas del Camino de Santiago.
- **[Centro de Descargas del CNIG](https://centrodedescargas.cnig.es/CentroDescargas/mapas-camino-santiago)**: Mapas temáticos, ortofotos PNOA y capas vectoriales oficiales del Camino de Santiago.
- **[Federación Española de Asociaciones de Amigos del Camino de Santiago (FEAACS)](https://www.caminosantiago.org/cpperegrino/caminos/)**: Información histórica, trazados tradicionales, etapas y variantes oficiales.

---

## 📁 Estructura del Repositorio

El repositorio está organizado en datos vectoriales (`GPX/`) y proyectos de análisis espacial (`QGIS/`):

```text
.
├── GPX/
│   ├── 01-Camino_Frances/             # Etapas completas en GPX (Stage 1 a Stage 33)
│   ├── ES12-Camino-de-Madrid/         # Etapas y variantes del Camino de Madrid (KML)
│   ├── EU/                            # Rutas jacobeas europeas
│   │   ├── CZ/                        # Trazados en Chequia (Žitavská, Všerubská, Železná, etc.)
│   │   └── DE/                        # Red de Jakobsweg en Alemania (Via Baltica, Regia, Imperii, etc.)
│   ├── CPC.kml                        # Camino Portugués Central
│   ├── GoogleMaps_Praga_Santiago.gpx  # Trazado global Praga - Santiago de Compostela
│   └── 170615-camino-santiago-en-rep-checa-praga-radotin.gpx
├── QGIS/
│   ├── CaminoSantiago.qgz             # Proyecto cartográfico principal de QGIS
│   └── CaminoSantiago_OLD.qgz         # Versión previa del proyecto QGIS
├── LICENSE                            # Términos de licencia del repositorio
└── README.md                          # Documentación del proyecto