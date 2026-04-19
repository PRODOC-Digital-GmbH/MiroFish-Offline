# MiroFish-Offline — Wissensbasis für Seed- & Simulations-Prompt-Design

## 1. Grundlegende Architektur (wichtig für Prompt-Strategie)

**Pipeline:**
```
Seed-Text → Chunking (~300–400 chars) → NER/Relation-Extraction
         → Knowledge-Graph (Nodes + Edges) → Entity-Filtering
         → Agent-Personas (1 pro „Person/Organization"-Entity)
         → OASIS-Simulation (Twitter/Reddit) → Report
```

**Konsequenz:** Die Anzahl der Agenten ist **keine direkte Eingabe** — sie ergibt sich aus der Anzahl **benannter Person-/Organization-Entitäten im Seed**. Man steuert Agent-Count also indirekt über Seed-Design.

**Beobachtung aus Test-Run (380-Wort-Seed, qwen2.5:14b):**
- 8 Chunks → 12 Nodes, 5 Edges → 8 Agents
- Gefilterte Entity-Typen: `Person, Organization, CouncilMember, SmallBusinessAlliance, Mayor`
- Pro Agent: Hybrid-Search liefert 5 Fakten + 23 verwandte Nodes als Persona-Grundlage

## 2. Seed-Text Best Practices

### Länge
- **Minimum funktionierend:** ~300–400 Wörter (liefert 8–12 Agenten)
- **Empfohlen für differenzierte Simulation:** 800–2000 Wörter
- **Grenze:** Graph-Build skaliert ~5–12s pro Chunk → bei >5000 Wörtern Minuten-Bereich

### Struktur
- **Benannte Entitäten sichtbar machen:** Jede Stakeholder-Gruppe/Person, die als Agent erscheinen soll, muss **namentlich** im Seed stehen. Generische Referenzen („some residents", „the public") werden nicht zu Agenten.
- **Rollen-/Organisations-Labels:** Titel wie „Mayor", „Council Member", „Director of X", „Alliance" werden vom Extractor als Entity-Typen erkannt → bessere Persona-Differenzierung.
- **Zitate und Positionen:** Direkte Zitate mit klarer Position („said X: 'we will…'") geben dem LLM Persona-Material. Neutrale Deskription liefert blassere Personas.
- **Stakeholder-Diversität:** Mindestens 3–5 unterscheidbare Lager/Gruppen, sonst läuft die Simulation im Echo-Chamber.

### Was zu vermeiden ist
- **Vorweggenommene Ergebnisse im Seed:** Sätze wie „this will likely fail" oder „most people supported" priming den Extractor und die spätere Config-Generation.
- **Zu viele Nebenfiguren:** Jeder benannte Nebenakteur wird ggf. zum Agent → verdünnt die Kerndynamik. Fokus auf Hauptakteure.
- **Abstrakte Begriffe:** „Society", „the economy" → keine Agenten, nur Noise im Graph.

## 3. Simulations-Prompt Best Practices

### Was der Simulations-Prompt steuert
- Er fließt als `simulation_requirement` in die **Config-Generation** (Timeline, Activity-Levels, Initial Posts) und prägt die Persona-Ausprägung.

### Struktur
- **Klar benannte Stakeholder-Gruppen** aus dem Seed referenzieren
- **Konkrete Erkenntnisfragen** („Which group shifts first?", „What narrative dominates at month 3?") statt generischer Ziele
- **Output-Format** am Ende spezifizieren (Sentiment-Split pro Gruppe, Top-Narratives, Empfehlung etc.)
- **Keine Hypothesen als Setzung**: Nicht „show how retailers will suffer", sondern „track how retailer sentiment evolves"

## 4. Bekannter Bias-Risiko (WICHTIG für Prompt-Design)

Der `simulation_config_generator` (Schritt 2) erzeugt aus Seed+Prompt automatisch:
- **Narrative Guidance Direction** (nur Anzeige, fließt NICHT in Simulation)
- **Sentiment Bias / Stance / Influence Weight** (nur Anzeige, fließt NICHT in Simulation)
- **`active_hours`, `activity_level`** (fließen EIN)
- **Initial Posts** (fließen als Seed-Timeline EIN — Bias-Risiko!)

Die **Initial Posts** können voreingenommene Wertungen transportieren. Sie werden im selben LLM-Call generiert wie die Narrative → wenn die Narrative bereits eine Richtung festlegt, bekommen die Initial Posts oft diese Richtung als implizites Framing.

**Code-Ref:** `backend/app/services/simulation_config_generator.py:661–740`

**Mitigation:** Seed und Simulations-Prompt möglichst **hypothesenfrei** formulieren, damit die Initial-Post-Generation keinen Spin transportiert.

## 5. Modell-Empfehlungen (Apple Silicon, getestet)

| Modell | Eignung | Notizen |
|---|---|---|
| **qwen2.5:14b** | ✓ Baseline | Stock-README-Default, gut für Smoke-Tests. Graph-Extraktion etwas sparsam (5 Edges bei 380-Wörter-Seed). |
| **qwen2.5:32b** | ✓ Empfohlen | Bessere Extraktion, bei 128 GB RAM/Mac Studio problemlos. |
| **ministral-3:14b-instruct-2512-q8_0** | ✓✓ Sehr gut | 0 NER-Fehler, 55 Nodes/86 Edges bei längerem Seed, braucht Modelfile mit `num_ctx=32768` (sonst 59 GB KV-Cache!). |
| **Thinking-Modelle** (Qwen3, gemma4, DeepSeek-R1, GLM 4.7) | ✗ Ungeeignet | `think:false` über /v1 wird ignoriert → leere Antworten, 30% Chunk-Verlust. Ollama-Issue #15293. |
| **LM Studio statt Ollama** | ✗ | Nur 1 parallele Request, MiroFish braucht 5+ parallel für Persona-Generation. |

## 6. Embedding-Modelle

- **Default: `nomic-embed-text`** (768-dim) — funktioniert stabil
- **`qwen3-embedding:0.6b-fp16`** (1024-dim) — alternativ, andere Dim!
- **KRITISCH:** Embedder-Wechsel erfordert Neo4j-Volume-Reset (`docker compose down -v`) wegen Vektorindex-Dimensionen.

## 7. Infrastruktur-Fallstricke

- **Docker Memory-Limit:** Default ~7.6 GB → OOM bei Dual-World-Sim (Twitter+Reddit parallel). Fix: `deploy.resources.limits.memory: 32g` in docker-compose.yml.
- **Ollama im Docker-Container auf Mac:** Kein GPU/MLX-Zugriff → praktisch unbenutzbar. Auf Host laufen lassen, Container via `host.docker.internal` verbinden.
- **Context-Fenster:** MiroFish-Prompts brauchen **max ~5000 Token Input**, aber `OLLAMA_NUM_CTX=8192` führt bei großen Prompts zu leeren Antworten. Empfehlung: `num_ctx=32768` per Modelfile.
- **Report-Agent:** Upstream erzwingt seit Commit `313fe64` **English-only Output** — deutsche Seed-Texte gehen, aber der Report kommt in Englisch.

## 8. Aktuelle Known-Issues im Code (beobachtet, nicht kritisch)

- `SimulationRunner.start_simulation(...)` bekommt kein `storage=`-Argument → Graph-Memory-Update-Feature scheitert stumm (Simulation läuft trotzdem). Pfad: `backend/app/api/simulation.py:1599`. Dieselbe DI-Bug-Klasse wie der bereits gefixte ReportAgent-Fall (Commit `60a574f`).

## 9. Upstream-Quellen (für Deep Research sinnvoll)

- Upstream: https://github.com/666ghj/MiroFish (Cloud-Variante, DashScope+Zep)
- Offline-Fork-Basis: https://github.com/nikmcfly/MiroFish-Offline (Neo4j+Ollama)
- Live-Demo: https://666ghj.github.io/mirofish-demo/
- Relevante Videos (chinesisch): „Wuhan University Public Opinion Simulation", „Dream of the Red Chamber"
- Ollama-Issue Thinking-Problem: https://github.com/ollama/ollama/issues/15293
- Design-Paper/Blogs: „MiroFish: Swarm-Intelligence with 1M Agents" (Medium, März 2026), Dev.to Artikel

## 10. Offene Fragen für tieferes Research

- Wie skaliert Qualität der Simulation mit Agent-Count (8 vs 30 vs 100)?
- Welche Seed-Struktur reduziert Config-Generator-Bias am stärksten?
- Existieren publizierte Prompts/Seeds aus der Wuhan-University-Demo oder dem „Dream of Red Chamber"-Run?
- Welche Metriken nutzt der MiroFish-Report, um „Vorhersagequalität" zu bewerten?
- Gibt es Community-Best-Practices zu Initial-Post-Entbiasing?
- Wie geht man mit Multilingual-Seeds um (DE→Report-EN-Zwang)?
