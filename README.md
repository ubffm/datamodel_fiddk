# fiddk – Fachinformationsdienst Darstellende Kunst – Validator & Dokumentation

Dieses Repository bündelt:
- SHACL-Shapes (TTL) für das FID DK EDM Application Profile,
- einen Validator (Python-API und CLI) auf Basis von rdflib + pySHACL,
- einen Luigi-Task für Batch‑Validierung,
- sowie begleitende fachliche Dokumentation.

Die Projektseite: https://www.performing-arts.eu  
Allgemeine Projektbeschreibung (de): http://www.ub.uni-frankfurt.de/projekte/theater.html

## Inhalte

- `src/fiddk_validater/validator.py` – Kernfunktionen `validate` und `validate_to_files` (ruft pySHACL auf, lädt RDF/Shapes, serialisiert Reports).
- `src/fiddk_validater/cli.py`, `src/fiddk_validater/__main__.py` – Kommandozeilen-Interface (`python -m fiddk_validater`).
- `src/fiddk_validater/luigi_tasks.py` – Luigi-Task `ValidateRDFTask` für Workflow/Batch.
- `src/fiddk_validater/shapes/*.ttl` – SHACL-Shapes für `Aggregation`, `ProvidedCHO`, `WebResource`, `Person`, `Organization`, `Place`, `TimeSpan`, `Concept`, `Event`.
- `documentation/DataModel_FIDDK_de.md` – Ausführliche Modellbeschreibung inkl. FIDDK‑Abweichungen/Erweiterungen.

## Voraussetzungen

- Python 3.10+
- Abhängigkeiten: `rdflib`, `pyshacl`, `luigi`

## Installation

- Entwicklung/Editable:
```bash
pip install -e .
```

- Alternativ ohne Installation aus dem Repo heraus nutzen (setzt nur voraus, dass `src` im `PYTHONPATH` liegt).

## CLI-Nutzung

- Mit mitgelieferten Shapes:
```bash
python -m fiddk_validater -d pfad/zur/daten.ttl -r build/shacl-report.ttl --inference rdfs
```

- Mit eigenem Shapes‑Verzeichnis:
```bash
python -m fiddk_validater -d daten.ttl -s src/fiddk_validater/shapes -r build/report.ttl --report-format turtle
```

- Wichtige Optionen:
  - `-d/--data`: RDF-Daten
  - `-s/--shapes`: SHACL-Datei oder -Verzeichnis (optional; Standard: eingepackte Shapes)
  - `-r/--report`: Report-Datei (RDF)
  - `--data-format`, `--shapes-format`, `--report-format`: explizite Formate (z. B. `turtle`, `xml`, `json-ld`)
  - `--inference`: `none` | `rdfs` | `owlrl` (Standard `rdfs`)
  - `--no-text`: unterdrückt zusätzlichen Text‑Report (`.txt`)

- Exit‑Codes: `0` bei Konformität, `2` bei Verstößen. Ausgabe: „Konform: ja/nein“.

## Luigi-Task

- Beispielaufruf:
```bash
python -m luigi --module fiddk_validater.luigi_tasks ValidateRDFTask --data-path daten.ttl --report-path build/report.ttl --shacl-path src/fiddk_validater/shapes --inference rdfs --write-text-report True --fail-on-violation True
```

- Parameter (Auszug): `data_path`, `shacl_path` (optional), `report_path`, `data_format`/`shacl_format`/`report_format` (optional), `inference` (`rdfs`), `advanced`/`debug` (False), `write_text_report` (True), `fail_on_violation` (False/True).

## Python‑API

- `validate(data_path, shacl_path=None, data_format=None, shacl_format=None, inference="rdfs", advanced=False, debug=False) -> (conforms: bool, results_graph: rdflib.Graph, results_text: str)`
- `validate_to_files(data_path, shacl_path, report_path, ..., write_text_report=True) -> bool`  
  Schreibt RDF‑Report (Format aus Endung oder explizit) und optional `.txt`.

## Hinweise zu den Shapes (Kurzüberblick)

- `ProvidedCHO`: `edm:type` genau 1 (eine(r) von `TEXT`/`IMAGE`/`SOUND`/`VIDEO`/`3D`); wenn `TEXT`, dann muss `dc:language` vorhanden sein; `bibo:isbn`/`bibo:issn` mit Formatprüfung; umfangreiche `rdau`‑Rollen.
- `Aggregation`: `edm:aggregatedCHO`, `edm:dataProvider`, `edm:provider` jeweils 1; mindestens eines von `edm:isShownAt` oder `edm:isShownBy`.
- `WebResource`: `dc:format` prüft MIME‑Pattern; `edm:rights` optional (0..1 IRI).
- `Person`/`Organization`/`Place`/`Concept`: `skos:prefLabel` pro Sprach‑Tag eindeutig; zusätzlicher SPARQL‑Check für max. ein Label ohne Sprach‑Tag.
- `TimeSpan`: `edm:begin`/`edm:end` je max. 1 Literal; Anzeigeform via `skos:prefLabel`.
- `Event`: `edm:happenedAt` und `edm:occurredAt` können Literal oder IRI sein; `foaf:depiction`/`foaf:homepage` max. 1 IRI.

## Dokumentation

- Fachliches Datenmodell und FIDDK‑Spezifika: `documentation/DataModel_FIDDK_de.md` (inkl. Unterschiede zu EDM und FIDDK‑Erweiterungen).

## Mitwirkung & Tests

- Änderungen an Shapes in `src/fiddk_validater/shapes/` vornehmen und mit der CLI/Validator‑API testen.
- Für automatisierte Validierung in Workflows eignet sich der Luigi‑Task.
- Pull Requests sind willkommen.

### Tests ausführen

- Dev‑Abhängigkeiten inkl. pytest installieren:
  - `pip install -e ".[dev]"`
- Tests starten:
  - `pytest -q`
- Einzelnen Test ausführen:
  - `pytest -q tests/test_validation_edm.py::test_valid_minimal_conforms`
