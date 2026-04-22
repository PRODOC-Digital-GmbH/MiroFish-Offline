# Session-Handoff: MiroFish-Offline (2026-04-21)

## Was wurde in dieser Session erreicht

### Tickets implementiert & geschlossen (9 Tickets)
- **MIR-5**: Graph-Memory-Updater DI-Bug — `storage` an `start_simulation()` durchgereicht
- **MIR-6**: Report-Agent Interview-Timeout — Pre-Check auf Runner-Status, Timeout 180→45s
- **MIR-7**: Chunker Wortgrenzen — `rfind(' ')` Fallback in `file_parser.py`
- **MIR-9**: Zeitzonen CET/Berlin — Peak 18-22, Work 9-17 in `simulation_config_generator.py`
- **MIR-11**: Auto-Export Report — Named copy `{thema}_{modell}_{datum}.md` in reports/
- **MIR-12**: Auto-Export Personas — `profiles_full.json` mit allen Feldern inkl. Entity-Linkage
- **MIR-14**: num_ctx/extra_body in allen 3 LLM-Call-Stellen
- **MIR-16**: Separates NER-Modell — `NER_MODEL_NAME=phi4-mini-ner` in .env, eigener LLMClient
- **MIR-18 Phase 1**: Konfigurierbare Output-Sprache — `OUTPUT_LANGUAGE=English` in .env, in allen Prompts

### Weitere Fixes (nicht als Ticket)
- Persona-Prompt von 2000 auf 500 Wörter reduziert (OOM-Fix)
- CSS-Dropdown-Overlap im Interaction-Panel gefixt (z-index)
- Agent-Interview-Timeout auf 180s erhöht (OASIS braucht ~2 Min pro Interview)
- Named Symlinks für Simulations-Ordner (analog Report-Copies)
- `.env.example` aktualisiert mit NER_MODEL_NAME und OUTPUT_LANGUAGE
- Docker VM Memory von 7.6 GB auf 32 GB erhöht (User-Einstellung)
- Ollama `phi4-mini-ner` Modelfile mit num_ctx=4096 erstellt (3.3 GB statt 28 GB)

### Linear-Integration
- GitHub Webhook verifiziert (PRODOC-Digital-GmbH/MiroFish-Offline)
- Magic Words: `Part of MIR-XX` → In Progress, `Fixes MIR-XX` → Done
- 18 Tickets angelegt (MIR-5 bis MIR-18)

### Offene Tickets
| Ticket | Prio | Thema |
|---|---|---|
| MIR-8 | High | Vektor-Dimensionen konfigurierbar |
| MIR-10 | Low | Config-Generator Bias reduzieren |
| MIR-13 | Low | Debug-Logging LLM-Client |
| MIR-15 | Low | Auto-Run Pipeline / Headless API |
| MIR-17 | Medium | Pipeline-Timing persistent + Content-Qualitäts-Evaluation |
| MIR-18 Phase 2 | — | i18n-Architektur (Sprach-Strings extrahieren, vue-i18n) |

## Kritische Erkenntnisse

### OOM-Crashes bei >60 Agenten
- **Docker VM Memory** muss ≥16 GB sein (jetzt auf 32 GB)
- **Persona-Texte** max 500 Wörter (OASIS schickt vollen Text als System-Prompt bei jedem Call)
- **NER-Modell separat** halten (phi4-mini-ner, 3.3 GB) damit es nicht mit Simulation konkurriert
- Alle drei Fixes zusammen nötig für stabile Runs mit 70+ Agenten

### Modell-Vergleich: Ministral-3 vs. Qwen 2.5:14b
| Phase | Ministral-3 | Qwen 2.5:14b | Speedup |
|---|---|---|---|
| Ontology | 2 Min | 1 Min | 2x |
| Graph Build (29 Chunks) | 4 Min | 2 Min | 2x |
| Persona Gen (72→81 Agents) | ~30 Min | 13 Min | 2.3x |
| Config Gen | ~12 Min | 6 Min | 2x |
| RAM (Ollama) | 24 GB | 17 GB | -30% |
| Vorgeschlagene Runden | 72 | 336 | — |
| Report-Größe | 25.8 KB | 13.5 KB | — |
| Sprachproblem | Nein | Ja (Chinesisch/Thai) | Fix: MIR-18 |

### IPC-Probleme beim Agent-Chat
- Simulations-Umgebung bleibt im Wait-Mode nach Abschluss (PID lebt, env_status="alive")
- Aber IPC-Command-Processing scheint nach einiger Zeit zu blockieren
- Workaround: Container-Restart + Simulation neu starten
- Interview-Timeout auf 180s (OASIS braucht ~2 Min für Antwort mit vollem Persona-Kontext)

## Aktueller Stand

### .env Konfiguration
```
LLM_MODEL_NAME=qwen2.5:14b
NER_MODEL_NAME=phi4-mini-ner
EMBEDDING_MODEL=qwen3-embedding:0.6b-fp16
OUTPUT_LANGUAGE=English
```

### Ollama-Modelle (geladen)
- qwen2.5:14b (17 GB, 32k Context) — Haupt-LLM
- phi4-mini-ner (3.3 GB, 4k Context) — NER-Extraction
- qwen3-embedding:0.6b-fp16 (6.4 GB) — Embeddings

### Git-Status
- Branch: main, up to date with origin
- Letzter Commit: `c58d148` (MIR-7/18)
- 6 Commits in dieser Session gepusht

### Neo4j
- Enthält Daten aus Ministral-3 und Qwen-Runs
- Kann bei Bedarf bereinigt werden: `docker compose exec neo4j cypher-shell -u neo4j -p mirofish "MATCH (n) DETACH DELETE n"`

## Nächste Schritte (für neuen Chat)

1. **Container neu bauen** (`docker compose up -d --build mirofish`) — enthält MIR-7, MIR-18 Fixes
2. **Demo-Run mit Qwen 2.5:14b** — gleiche Testdaten, prüfen ob OUTPUT_LANGUAGE=English greift
3. **Prüfen ob Agent-Chat funktioniert** nach Simulation-Ende (180s Timeout)
4. Falls Sprachproblem gelöst: **Demo-Run mit Ministral-3** für Summit-Daten (bessere Social-Media-Posts)
5. Offene Tickets nach Priorität abarbeiten
