# MIR-17: Pipeline-Timing + Content-Qualitäts-Evaluation

## Problem

Pipeline-Durchlaufzeiten stehen nur in Container-Logs und gehen bei Restart verloren. Für Modell-Benchmarking und Summit-Demo brauchen wir persistente, strukturierte Timing- und Qualitätsdaten.

## Lösung

Neuer Service `benchmark_collector.py` mit zwei Funktionen:
1. **Timing-Collector**: Sammelt Timestamps an Pipeline-Stufen, schreibt `timing.json`
2. **Content-Evaluator**: Wertet SQLite-DBs nach Simulation aus, schreibt `content_evaluation.json`

Beide Dateien landen im Simulations-Ordner (`backend/uploads/simulations/{sim_id}/`).

## Teil 1: timing.json

### Instrumentierung

Timing wird über ein Dict in `simulation_manager.py` und `simulation_runner.py` gesammelt:

```python
# In prepare_simulation() — 3 Phasen
timing["entity_reading_start"] = datetime.now().isoformat()
# ... Phase 1 ...
timing["entity_reading_end"] = datetime.now().isoformat()

timing["profile_generation_start"] = datetime.now().isoformat()
# ... Phase 2 ...
timing["profile_generation_end"] = datetime.now().isoformat()

timing["config_generation_start"] = datetime.now().isoformat()
# ... Phase 3 ...
timing["config_generation_end"] = datetime.now().isoformat()
```

Simulation-Start/Ende kommt aus `run_state.json` (`started_at`, `completed_at`).
Report-Timing wird vom Report-API-Endpoint hinzugefügt.

### Output-Format

```json
{
  "model": "qwen2.5:14b",
  "ner_model": "phi4-mini-ner",
  "embedding_model": "qwen3-embedding:0.6b-fp16",
  "output_language": "English",
  "timestamps": {
    "entity_reading_start": "...", "entity_reading_end": "...",
    "profile_generation_start": "...", "profile_generation_end": "...",
    "config_generation_start": "...", "config_generation_end": "...",
    "simulation_start": "...", "simulation_end": "...",
    "report_start": "...", "report_end": "..."
  },
  "durations_seconds": {
    "entity_reading": 12.3,
    "profile_generation": 780.5,
    "config_generation": 360.2,
    "simulation": 13200.0,
    "report": 180.0,
    "total_pipeline": 14533.0
  },
  "metrics": {
    "chunks_count": 29,
    "entities_count": 92,
    "edges_count": 38,
    "agents_count": 81,
    "avg_persona_seconds": 9.6,
    "simulation_rounds": 40,
    "total_actions": 438,
    "twitter_actions": 244,
    "reddit_actions": 194,
    "report_sections": 4,
    "llm_suggested_rounds": 336
  }
}
```

### Implementierung

- `BenchmarkCollector` Klasse mit `start_phase(name)`, `end_phase(name)`, `set_metric(key, value)`
- Instanz wird in `state.json` nicht gespeichert — stattdessen eigene `timing.json` Datei
- `save_timing(sim_dir)` schreibt die Datei
- Modell-Info wird aus `config.py` gelesen (LLM_MODEL_NAME, NER_MODEL_NAME, etc.)

## Teil 2: content_evaluation.json

### Berechnung

Nach Simulation-Ende werden die SQLite-DBs ausgewertet:

```python
def evaluate_content(sim_dir: str) -> dict
```

Liest `twitter_simulation.db` und `reddit_simulation.db`, berechnet pro Platform:

| Metrik | Quelle | Berechnung |
|--------|--------|------------|
| total_posts | post table | COUNT(*) |
| original_posts | post table | WHERE original_post_id IS NULL |
| reposts | post table | WHERE original_post_id IS NOT NULL |
| avg_length_chars | post.content | AVG(LENGTH(content)) |
| avg_length_words | post.content | AVG(word_count) |
| min/max_length_words | post.content | MIN/MAX(word_count) |
| emoji_count_total | post.content | Unicode-Emoji-Regex |
| avg_emojis_per_post | post.content | emoji_count / total_posts |
| posts_with_hashtags_pct | post.content | % mit #\w+ |
| avg_hashtags_per_post | post.content | Hashtag-Count / total_posts |
| posts_with_markdown_pct | post.content | % mit **bold**, *italic*, links |
| exact_duplicates | post.content | GROUP BY content HAVING COUNT > 1 |
| near_duplicates | post.content | Erste 50 Zeichen gleich |
| avg_likes | post.num_likes | AVG |
| avg_shares | post.num_shares | AVG |
| total_comments | comment table | COUNT(*) (Reddit) |
| language_check | post.content | % Posts mit CJK/Thai-Characters (MIR-18 Validierung) |

### Output-Format

```json
{
  "evaluated_at": "2026-04-21T18:30:00",
  "platforms": {
    "twitter": {
      "total_posts": 218,
      "original_posts": 180,
      "reposts": 38,
      "avg_length_chars": 152.3,
      "avg_length_words": 24.5,
      "min_length_words": 3,
      "max_length_words": 87,
      "emoji_total": 45,
      "avg_emojis_per_post": 0.21,
      "posts_with_hashtags_pct": 34.2,
      "avg_hashtags_per_post": 0.52,
      "posts_with_markdown_pct": 8.1,
      "exact_duplicates": 2,
      "near_duplicates": 5,
      "avg_likes": 3.2,
      "avg_shares": 1.1,
      "total_comments": 0,
      "non_target_language_pct": 0.0
    },
    "reddit": { ... }
  },
  "combined": {
    "total_posts": 412,
    "quality_score": 78.5
  }
}
```

### Quality-Score (0-100)

Einfacher gewichteter Score:
- Keine Duplikate: +30 (linear abziehen bei Duplikaten)
- Zielsprache 100%: +25 (linear abziehen bei Fremdsprache)
- Avg Wortlänge 15-50: +20 (außerhalb Penalty)
- Emoji-Nutzung 0.1-0.5/Post: +15 (zu wenig oder zu viel = Penalty)
- Hashtag-Nutzung 0.2-1.0/Post: +10

## Dateien zu ändern

| Datei | Änderung |
|-------|----------|
| `backend/app/services/benchmark_collector.py` | **NEU** — BenchmarkCollector + evaluate_content |
| `backend/app/services/simulation_manager.py` | Timing-Instrumentation in prepare_simulation() |
| `backend/app/services/simulation_runner.py` | Timing-Save nach Simulation-Ende |
| `backend/app/api/report.py` | Report-Timing in timing.json nachtragen |
| `ROADMAP.md` | Sprachstil-Metriken als Future Extension |

## Nicht im Scope

- Sprachstil-Metriken (formell vs. informal) — Future Extension
- Frontend-Dashboard für Benchmarks
- Automatischer Modell-Vergleich über mehrere Runs
