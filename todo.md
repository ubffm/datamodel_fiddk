# TODO: SHACL-Shape und Datenmodell-Angleichung (FIDDK)

Ziel: Core- und pipelinespezifische Regeln sauber trennen, Shapes mit der Dokumentation harmonisieren, Validierung automatisieren.

## 1) Entscheidung & Versionierung (Core vs. Pipeline)
- [ ] Core-Shapes (modellweit gültige Constraints) in diesem Repo halten (z. B. `shapes/core/`).
- [ ] Pipeline-/Projekt-spezifische Shapes im ETL-Repo pflegen (z. B. `shapes/profiles/<pipeline>/`).
- [ ] Im ETL-Repo eine feste Version der Core-Shapes referenzieren (Git-Submodule, Git-Subtree oder Release-Asset).
- [ ] Release-Tagging für dieses Repo etablieren (z. B. `v2025.x`) und in ETL pinnen.

## 2) fiddk.ttl mit Doku abgleichen (Ergänzungen/Anpassungen)
### edm:ProvidedCHO
- [ ] `edm:type` optional machen (min 0, max 1, `sh:in` beibehalten); Doku beschreibt es als optional.
- [ ] `dc:type` nicht erzwingen (min 0 lassen); die Pflicht via `sh:or` (mind. eines aus `dc:subject` | `dc:type` | `dcterms:spatial` | `dcterms:temporal`) reicht.
- [ ] `edm:currentLocation`: Entscheidung treffen. Empfehlung: 0..1 (praktikabler), Doku ggf. anpassen.
- [ ] Fehlende optionale Properties ergänzen:
  - [ ] `dc:format` (0..*)
  - [ ] `dcterms:hasFormat` (0..*)
  - [ ] `dcterms:hasVersion` (0..*)
  - [ ] `edm:isSuccessorOf` (0..*)
  - [ ] `edm:realizes` (0..*)
- [ ] Zusätze laut FIDDK-Doku ergänzen:
  - [ ] `bibo:isbn` als Literal (0..1) mit Pattern-Check: `^(97(8|9))?\d{9}(\d|X)$`
  - [ ] `bibo:issn` als Literal (0..1) mit Pattern-Check: `^\d{4}-\d{3}[\dX]$`
  - [ ] `bf:partNumber` (0..1), `bf:shelfMark` (0..1), `bf:subtitle` (0..*)

### foaf:Person
- [ ] Bereits vorhandene Regeln (ein `skos:prefLabel` je Sprach-Tag via `sh:uniqueLang`, plus SPARQL-Constraint „max. ein prefLabel ohne @lang“) als Referenz für andere Klassen übernehmen.

### foaf:Organization, edm:Place, skos:Concept, edm:Event
- [ ] `skos:prefLabel` auf „max. 1 je Sprach-Tag“ umstellen:
  - [ ] `sh:uniqueLang true` setzen.
  - [ ] SPARQL-Constraint „maximal ein `skos:prefLabel` ohne Sprach-Tag“ ergänzen (analog PersonShape).
- foaf:Organization:
  - [ ] `edm:isNextInSequence` als optionales Property ergänzen (0..*), für Vorgänger/Nachfolger-Ketten.

### edm:Place
- [ ] Koordinaten lassen (xsd:float) oder auf xsd:decimal umstellen; Empfehlung: float beibehalten.
- [ ] Wertebereiche absichern:
  - [ ] `wgs84_pos:lat` mit `sh:minInclusive -90`, `sh:maxInclusive 90`
  - [ ] `wgs84_pos:long` mit `sh:minInclusive -180`, `sh:maxInclusive 180`

### edm:WebResource
- [ ] `edm:rights` 0..1 belassen (FIDDK-Praxis).
- [ ] Optionale Warn-Constraint hinzufügen:
  - [ ] SHACL-SPARQL mit `sh:severity sh:Warning`, die warnt, wenn eine Aggregation `edm:isShownBy`/`edm:hasView` referenziert, aber auf Ebene WebResource/ Aggregation kein `edm:rights` vorhanden ist.

## 3) Validierung & CI
- [ ] Skript (pySHACL oder Apache Jena) hinzufügen, das Shapes gegen Beispieldaten prüft.
- [ ] CI-Job einrichten (GitHub Actions/GitLab CI): SHACL-Validierung bei jedem Commit/PR.
- [ ] Severity-Konzept nutzen (Violation vs. Warning), damit nicht-mandatorische Empfehlungen nicht Builds brechen.

## 4) Dokumentation synchronisieren
- [ ] Kardinalität `edm:currentLocation` in der Doku final festlegen und mit Shapes synchronisieren.
- [ ] Hinweise zu ISBN/ISSN-Formatprüfungen in die Doku aufnehmen.
- [ ] Klarstellen, dass `skos:prefLabel` je Sprach-Tag einmalig erlaubt ist (für Organization/Place/Concept/Event).
- [ ] Im Doku-Teil zu ProvidedCHO die Rolle von `dc:type` vs. OR-Regel explizit erläutern.

## 5) Beispieldaten
- [ ] Kleines Turtle-Dataset in `examples/` anlegen:
  - [ ] 1 `edm:ProvidedCHO`, 1 `ore:Aggregation`, 1–2 `edm:WebResource`
  - [ ] 1 `foaf:Person`, 1 `foaf:Organization`, 1 `edm:Place`, 1 `edm:Event`, 1 `skos:Concept`
  - [ ] Fälle für: mehrere `skos:prefLabel` mit Sprachtags, ISBN/ISSN, fehlendes `edm:rights` (für Warning).

## 6) Offene Entscheidungen (kurz klären)
- [ ] Soll `edm:currentLocation` verpflichtend sein (Doku 2025 sagt min 1) oder optional (0..1)? Empfehlung: optional.
- [ ] Soll `edm:rights` verpflichtend sein, wenn `edm:isShownBy` existiert? Empfehlung: nur Warning, nicht Pflicht.
- [ ] `xsd:float` vs. `xsd:decimal` für Koordinaten? Empfehlung: `xsd:float` + Wertebereichs-Checks.

## 7) Nächste Schritte (operativ)
- [ ] Obige Shape-Änderungen in `fiddk.ttl` umsetzen.
- [ ] Beispiel-Daten hinzufügen und Validierung grün bekommen.
- [ ] Doku aktualisieren (de und de_2025).
- [ ] Version taggen und im ETL-Repo referenzieren.
