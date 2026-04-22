# i18n Audit — MIR-18 Phase 2 Vorbereitung

Automatisch generiert am 2026-04-21. Basis für vue-i18n Integration und Backend-String-Extraktion.

**Total: ~185 hardcodierte Strings** identifiziert.

| Kategorie | Anzahl | Bereich |
|-----------|--------|---------|
| UI-Labels | ~80 | Buttons, Headers, Fields, Badges |
| Error-Messages | ~35 | API-Fehler, Validierungsmeldungen |
| Status-Texte | ~15 | Processing, Completed, Failed etc. |
| Progress-Messages | ~25 | Dynamische Meldungen mit Variablen |
| LLM-Prompts | ~10 | System-Prompts mit Output-Sprache |
| Report-Templates | ~20 | Report-Überschriften, Section-Titel |

---

## 1. Frontend — Vue Components

### Home.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 18 | "Offline Multi-Agent Simulation Engine" | UI-Label |
| 19 | "/ v0.1-preview" | UI-Label |
| 23-24 | "Upload Any Document" + "Predict What Happens Next" | UI-Label |
| 29 | "MiroFish Offline", "autonomous AI agents", "local optima" | UI-Label |
| 32 | "Your data never leaves your machine. The future is simulated locally" | UI-Label |
| 52 | "System Status" | UI-Label |
| 55 | "Ready" | Status-Text |
| 57 | "Local prediction engine on standby. Upload unstructured data to initialize a simulation." | UI-Label |
| 62-63 | "Free" / "Runs on your hardware" | UI-Label |
| 66-67 | "Private" / "100% offline, no cloud" | UI-Label |
| 72-73 | "Workflow Sequence" | UI-Label |
| 92-93 | "01 / Reality Seeds" + "Supported: PDF, MD, TXT" | UI-Label |
| 104-106 | "Drag & drop files here" + "or click to browse" | UI-Label |
| 118 | "Parameters" | UI-Label |
| 122 | "02 / Simulation Prompt" | UI-Label |
| 125 | "Describe your simulation or prediction goal in natural language" | Placeholder |
| 126 | "Engine: Ollama + Neo4j (local)" | UI-Label |
| 132 | "Start Engine" / "Initializing..." | Button/Status |
| 220-226 | Steps: "Graph Build", "Env Setup", "Simulation", "Report", "Interaction" + Beschreibungen | UI-Label |

### MainView.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 6 | "MIROFISH OFFLINE" | UI-Label |
| 18 | "Graph" / "Split" / "Workbench" | UI-Label |
| 25 | "Step {n}/5" | UI-Label |
| 94 | Step-Namen Array | UI-Label |
| 133-137 | "Error", "Ready", "Building Graph", "Generating Ontology", "Initializing" | Status-Text |
| 162-219 | Diverse Log-Messages ("Entering Step...", "Uploading...", "Error:...") | Progress/Error |
| 267-393 | Weitere Log/Status-Messages | Progress/Error |

### Step1GraphBuild.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 9 | "Ontology Generation" | UI-Label |
| 12-14 | "Completed" / "Generating" / "Waiting" | Status-Text |
| 27 | "Analyzing documents..." | Progress |
| 34 | "ENTITY" / "RELATION" | UI-Label |
| 44-64 | "ATTRIBUTES", "EXAMPLES", "CONNECTIONS" | UI-Label |
| 78-104 | "GENERATED ENTITY TYPES" / "GENERATED RELATION TYPES" | UI-Label |
| 113 | "GraphRAG Build" | UI-Label |
| 125 | "Based on the generated ontology, automatically chunk documents..." | UI-Label |
| 130-140 | "Entity Nodes", "Relation Edges", "SCHEMA Types" | UI-Label |
| 151 | "Build Complete" | UI-Label |
| 160 | "Graph build is complete. Please proceed to the next step..." | UI-Label |
| 167 | "Creating..." / "Enter Environment Setup" | Button |

### Step2EnvSetup.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 9 | "Simulation Instance Initialization" | UI-Label |
| 25-38 | "Project ID", "Graph ID", "Simulation ID", "Task ID" | UI-Label |
| 49 | "Generate Agent Personas" | UI-Label |
| 68-76 | "Current Agent Count", "Expected Agent Total", "Current Related Topics Count" | UI-Label |
| 83 | "Generated Agent Personas" | UI-Label |
| 97-99 | "Unknown", "Unknown Profession", "No introduction available" | Fallback |
| 121 | "Generate Dual Platform Simulation Configuration" | UI-Label |
| 133 | "LLM Based on simulation requirements..." | UI-Label |
| 142-177 | "Simulation Duration", "Duration per round", "Total rounds", "Active per hour", "Peak period", "Working hours", "Morning time period", "Valley period" | UI-Label |
| 186 | "Agent Configuration" | UI-Label |
| 208 | "Active period" | UI-Label |
| 231-262 | "Post/time", "Comment/time", "Response delay", "Activity level", "Sentiment tendency", "Influence" | UI-Label |
| 275 | "Platform 1: Square / Information flow", "Platform 2: Topic / Community" | UI-Label |
| 279-297 | "Time weight", "Popularity weight", "Relevance weight", "Virus threshold", "Echo chamber strength" | UI-Label |
| 333 | "LLM Configuration inference" | UI-Label |
| 354-406 | "Initial activation arrangement", "Narrative Guidance Direction", "Initial trending topics" etc. | UI-Label |
| 426-436 | "Preparation completed", "Simulation environment preparation completed..." | Status-Text |
| 442-504 | "Simulation Rounds Setting", "Custom", Estimation messages | UI-Label |
| 517-524 | "Return graph construction" / "Start dual world parallel simulation" | Button |
| 550-605 | Modal: "Age", "Gender", "Country/Region", "MBTI", Persona-Dimensions | UI-Label |

### Step3Simulation.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 12 | "Info Plaza" (Twitter-Äquivalent) | UI-Label |
| 53 | "Topic Community" (Reddit-Äquivalent) | UI-Label |
| 21-30 | "ROUND", "Elapsed Time", "ACTS" | UI-Label |
| 35-88 | Action-Labels: "POST", "LIKE", "REPOST", "QUOTE", "FOLLOW", "IDLE", "COMMENT", "DISLIKE", "SEARCH", "TREND", "MUTE", "REFRESH" | UI-Label |
| 100-101 | "Starting..." / "Start Generating Report" | Button |
| 111 | "TOTAL EVENTS:" | UI-Label |
| 267 | "Waiting for agent actions..." | Status-Text |
| 275 | "SIMULATION MONITOR" | UI-Label |
| 392-525 | Diverse Log-Messages (Simulation-Start, Progress, Completion) | Progress |

### Step4Report.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 11 | "Prediction Report" | UI-Label |
| 61 | "Generating {sectionTitle}..." | Progress |
| 75 | "Waiting for Report Agent..." | Status-Text |
| 92-98 | "Sections", "Elapsed", "Tools" | UI-Label |

---

## 2. Backend API-Responses

### report.py
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 32 | "Please provide simulation_id" | Error |
| 38 | "Simulation does not exist: {id}" | Error |
| 47 | "Report already exists" | Status |
| 53 | "Project does not exist: {id}" | Error |
| 57 | "Missing graph ID, please ensure graph is built" | Error |
| 61 | "Missing simulation requirement description" | Error |
| 76 | "GraphStorage not initialized — check Neo4j connection" | Error |
| 91 | "Initializing Report Agent..." | Progress |
| 128 | "Report generation task started..." | Status |
| 152 | "Report generated" | Status |
| 157 | "Please provide task_id or simulation_id" | Error |
| 178 | "Report does not exist: {id}" | Error |
| 237 | "Report deleted: {id}" | Status |
| 254-269 | Diverse Validierungsfehler | Error |

### graph.py
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 29 | "GraphStorage not initialized — check Neo4j connection" | Error |
| 53-92 | "Project does not exist", "Project deleted", "Project reset" | Error/Status |
| 170-178 | "No files uploaded", "Simulation requirement is required" | Error |
| 286 | "Graph build task started" | Status |
| 300-589 | Diverse Fehler/Status-Messages | Error/Status |

### simulation.py
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 32 | "Please provide simulation_id" | Error |
| 101-204 | Diverse Validierungs/Status-Messages | Error/Status |
| 385-720 | Prepare-Status, Progress-Messages | Progress/Status |

---

## 3. LLM-Prompts (OUTPUT_LANGUAGE-relevant)

### Bereits mit OUTPUT_LANGUAGE instrumentiert:
- `ontology_generator.py:192` — Ontologie-Generierung
- `report_agent.py:1173,1268,1816` — Report-Generierung
- `simulation_config_generator.py:598,714,877` — Config/Opinion/Behavior
- `oasis_profile_generator.py:630,644,691` — Persona-Generierung

### Noch hardcodiert (potentiell sprachrelevant):
- `report_agent.py:24` — Interview-Prompt: "Based on your persona, all your past memories and actions, reply directly to me..."
- Report-Logger Messages (Zeilen 100-287) — intern, nicht user-facing

---

## 4. Status-Enums

| Enum | Werte |
|------|-------|
| TaskStatus | processing, completed, failed |
| ReportStatus | PENDING, PLANNING, GENERATING, COMPLETED, FAILED |
| ProjectStatus | created, ontology_generated, graph_building, graph_completed, failed |
| SimulationStatus | created, preparing, ready, running, paused, stopped, completed, failed |
| RunnerStatus | idle, starting, running, paused, stopping, stopped, completed, failed |

---

## Empfehlung für Umsetzung

1. **Frontend**: vue-i18n Setup mit `$t('key')` Syntax, Locale-Files `en.json` / `de.json`
2. **Backend-Errors**: Fehler-Codes statt Strings senden, Frontend übersetzt
3. **LLM-Prompts**: OUTPUT_LANGUAGE weiter nutzen, Interview-Prompt ergänzen
4. **Enums**: Als Keys belassen, Frontend mappt auf übersetzte Labels
