# Plan: Linear als Ticket-System für MiroFish-Offline einrichten

## Ziel
Issue-Tracking für MiroFish-Offline-Fork in Linear aufsetzen. Claude liefert Instruktionen, User setzt in Linear um.

## Schritt 1: Linear-Workspace & Projekt anlegen (User in Linear)

1. Workspace erstellen (falls noch keiner existiert) unter https://linear.app
2. Neues Projekt anlegen: **MiroFish-Offline**
3. Labels erstellen:
   - `bug` — Fehler im Code
   - `enhancement` — Verbesserung / neues Feature
   - `upstream-diff` — Abweichung vom Upstream, die wir bewusst pflegen
   - `dx` — Developer Experience (Logging, Tooling, Config)
4. Prioritäten nutzen: Urgent / High / Medium / Low

## Schritt 2: Initiale Tickets aus bekannten Issues erstellen

### Bugs (bug)

**B1: Graph-Memory-Updater DI-Bug** — Priority: Medium
- `simulation.py:1599` übergibt kein `storage=` an `start_simulation()`
- Graph-Memory-Updates während Simulation stumm deaktiviert
- Fix: storage durchreichen (analog ReportAgent-Fix, Commit 60a574f)

**B2: Report-Agent Interview-Timeout** — Priority: Medium
- IPC-Timeout (180s) bei Agent-Interviews nach Simulation-Ende
- Simulations-Prozess beendet sich, Report-Agent interviewt ins Leere
- Sections fallen zurück auf Force-Generate (weniger tiefe Reports)

**B3: Chunker splittet mitten im Wort** — Priority: Low
- `file_parser.py:169-179` — kein Wortgrenz-Fallback bei Chunk-Split
- Erzeugt Wortfragmente als Graph-Entities (z.B. "dge" → "Department of Greendale Mobility")
- Fix: `rfind(' ')` als Fallback nach gescheiterter Satzgrenz-Suche

### Enhancements (enhancement)

**E1: Vektor-Dimensionen konfigurierbar machen** — Priority: High
- `neo4j_schema.py` und `embedding_service.py` haben Dimensionen hardcoded (aktuell 1024)
- Sollte aus Embedding-Modell oder .env abgeleitet werden
- Bei Modellwechsel muss man aktuell Code ändern + Neo4j-Volume löschen

**E2: Agent-Aktivitätszeiten auf deutsche Zeitzonen** — Priority: Medium
- Upstream-Default: chinesische Zeiten
- Im alten Fork waren diese auf CET/CEST angepasst
- Betrifft `simulation_config_generator.py` (activity_multipliers, dead/peak-Zeiten)

**E3: Config-Generator Bias reduzieren** — Priority: Low
- `simulation_config_generator.py:661-740` generiert vorweggenommene Narrative
- Initial Posts transportieren Bias implizit in die Simulation
- Langfristig: Prompt einschränken auf Topics + Posts, keine Narrative Direction

### Enhancements (enhancement) — Fortsetzung

**E4: Auto-Export Report** — Priority: High
- Report nach Generierung automatisch als MD/PDF in `backend/uploads/` ablegen
- Ermöglicht Vergleich zwischen Modell-Runs ohne manuelles Copy-Paste aus dem UI
- Aktuell: Sections liegen in `report_*/section_*.md`, aber kein gebündelter Export

**E5: Auto-Export Agent-Personas + Configs** — Priority: High
- Nach Simulation: Alle generierten Personas + Activity-Configs als JSON/MD exportieren
- Für sauberes Benchmarking: Persona-Qualität zwischen Modellen vergleichbar machen
- Twitter-Profiles (CSV) und Reddit-Profiles (JSON) werden schon gespeichert, aber Persona-Texte fehlen im Export

### Developer Experience (dx)

**D1: Debug-Logging im LLM-Client** — Priority: Low
- Request/Response-Logging (Modell, Temperature, Timing, Antwortlänge)
- Ob Thinking-Tags gestrippt wurden
- Hilfreich für Modell-Benchmarking

**D2: num_ctx + extra_body in allen 3 LLM-Call-Stellen** — Priority: Medium
- llm_client.py (hat es), simulation_config_generator.py (fehlt), oasis_profile_generator.py (fehlt)
- Ohne num_ctx-Durchreichung können die eigenständigen OpenAI-Clients mit falschem Context laufen

## Schritt 3: Claude-Workflow Integration

- In zukünftigen Sessions: vor Implementierung → Linear-Ticket referenzieren
- Nach Implementierung: Ticket-Status in Linear auf "Done" setzen
- Memory-Referenz: `reference_linear.md` enthält Backlog-Übersicht

## Offene Frage für nächste Session
- Welchen Linear-Workspace/Projektnamen hat User gewählt?
- Gibt es ein bestehendes Team oder ist das Solo-Nutzung?
- Soll GitHub-Integration (Auto-Close bei Merge) eingerichtet werden?
