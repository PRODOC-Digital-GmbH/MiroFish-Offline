# i18n Audit — MIR-18

Erstellt 2026-04-21, aktualisiert 2026-04-23 nach Code-Review mit Vollstaendigkeits- und Risikopruefung.

## Scope

**Uebersetzen:** Nur Strings die der User im Frontend sieht (UI-Labels, Status-Texte, Buttons, Placeholders, Error-Messages im UI).

**NICHT uebersetzen:**
- Backend progress_callback Messages (nicht user-facing)
- Backend logger/print Messages (intern)
- Programmatische Keys und Enum-Werte (siehe Abschnitt 5)
- LLM-Kontroll-Prompts (interne Steuerung, kein User-Output)
- NER/Ontologie Entity-Type-Namen (Schema-Keys)

---

## Uebersicht

| Kategorie | Anzahl | Bereich |
|-----------|--------|---------|
| Frontend UI-Labels | ~220 | Buttons, Headers, Fields, Badges, Tooltips |
| Frontend Status-Texte | ~30 | Processing, Completed, Failed (Display-Labels) |
| Frontend Error-Messages | ~15 | User-sichtbare Fehlermeldungen |
| Frontend Placeholders | ~10 | Input-Felder, Textareas |
| Frontend Empty States | ~15 | "No data", "Loading...", Fallbacks |
| LLM-Prompts (OUTPUT_LANGUAGE) | ~10 | Nur user-sichtbarer Output |

**Total: ~300 Strings** (davon ~185 im Original-Audit, ~115 neu identifiziert)

---

## 1. Frontend — Vue Components

### Home.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 8 | "Visit our Github" | UI-Label |
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

### Process.vue (NEU — fehlte komplett im Original-Audit)
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~ | "Live Knowledge Graph" | UI-Label |
| ~ | "Build Process" | UI-Label |
| ~ | "Name:", "UUID:", "Created:", "Properties:", "Summary:", "Labels:" | UI-Label |
| ~ | "Fact:", "Episodes:", "Valid From:", "Invalid At:", "Expired At:" | UI-Label |
| ~ | "Relationship", "Node Details" | UI-Label |
| ~ | "Build Failed", "Build Complete", "Building Graph", "Generating Ontology", "Initializing" | Status-Text |
| ~ | "Completed", "In Progress", "Waiting" | Status-Text |
| ~ | "Waiting for graph data..." | Empty State |
| ~ | "No files pending upload. Please go back to home and try again." | Error |
| ~ | "Processing failed", "Graph build failed: ..." | Error |
| ~ | "Starting graph build...", "Build complete, loading graph..." | Progress |
| ~ | "Entity Nodes", "Relationship Edges", "Entity Types" | UI-Label |
| ~ | "Project Name", "Project ID", "Graph ID", "Simulation Requirement" | UI-Label |

### Step1GraphBuild.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 9 | "Ontology Generation" | UI-Label |
| 12-14 | "Completed" / "Generating" / "Waiting" / "In Progress" | Status-Text |
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
| ~ | "Failed to create simulation: ..." | Error |
| ~ | "SYSTEM DASHBOARD", "NO_PROJECT" | UI-Label |

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
| 550-605 | Modal: "Age", "Gender", "Country/Region", "MBTI" | UI-Label |
| ~ | "Initialization", "Arranging", "Async task completed" | Status-Text |
| ~ | "40 (Recommendation)" | UI-Label |
| ~ | "Persona Introduction", "Reality Seed Related Topics", "Detailed Persona Background" | UI-Label |
| ~ | "Recommendation algorithm configuration" | UI-Label |
| ~ | "Event panoramic experience", "Behavior pattern profiling", "Unique memory imprints", "Social Relationship Network" | UI-Label |
| ~ | "rounds" | UI-Label (Einheit) |
| ~ | "NO_SIMULATION" | UI-Label (Fallback) |

### Step3Simulation.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 12 | "Info Plaza" (Twitter-Aequivalent) | UI-Label |
| 53 | "Topic Community" (Reddit-Aequivalent) | UI-Label |
| 21-30 | "ROUND", "Elapsed Time", "ACTS" | UI-Label |
| 35-88 | Display-Labels: "POST", "LIKE", "REPOST", "QUOTE", "FOLLOW", "IDLE", "COMMENT", "DISLIKE", "SEARCH", "TREND", "MUTE", "REFRESH" | UI-Label |
| 100-101 | "Starting..." / "Start Generating Report" | Button |
| 111 | "TOTAL EVENTS:" | UI-Label |
| 267 | "Waiting for agent actions..." | Status-Text |
| 275 | "SIMULATION MONITOR" | UI-Label |
| ~ | "Available Actions" | UI-Label (Tooltip) |
| ~ | "Reposted from @{user}", "Liked @{user}'s post", "Reply to post #{id}" | UI-Label |
| ~ | "Search Query:", "Followed @{user}", "Upvoted", "Downvoted", "Action Skipped" | UI-Label |
| ~ | "Dynamic graph update mode enabled" | Progress |
| ~ | "Report generation request sent, please wait..." | Progress |

### Step4Report.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 11 | "Prediction Report" | UI-Label |
| 61 | "Generating {sectionTitle}..." | Progress |
| 75 | "Waiting for Report Agent..." | Status-Text |
| 92-98 | "Sections", "Elapsed", "Tools" | UI-Label |
| 337 | "Report Generation Complete" | Status-Text |
| 371 | "Waiting for agent activity..." | Empty State |
| 381-382 | "CONSOLE OUTPUT", "NO_REPORT" | UI-Label |
| 350-360 | "Hide Params"/"Show Params", "Structured View"/"Raw Output", "Hide Response"/"Show Response" | UI-Label |
| 310-316 | "Iteration {n}", "Tools: Yes/No", "Final: Yes/No" | UI-Label |
| 323 | "Section '{sectionTitle}' content generated" | Progress |

**Tool-Display-Namen (Step4Report.vue):**
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~499 | "Deep Insight" (insight_forge) | UI-Label |
| ~504 | "Panorama Search" (panorama_search) | UI-Label |
| ~509 | "Agent Interview" (interview_agents) | UI-Label |
| ~514 | "Quick Search" (quick_search) | UI-Label |
| ~519 | "Graph Stats" (get_graph_statistics) | UI-Label |
| ~524 | "Entity Query" (get_entities_by_type) | UI-Label |

**InsightDisplay Sub-Component (Step4Report.vue):**
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~985 | "Deep Insight" | UI-Label |
| ~989-999 | "Facts", "Entities", "Relations" | UI-Label |
| ~1007 | "Prediction Scenario: " | UI-Label |
| ~1018-1036 | "Current Key Memory (N)", "Core Entities (N)", "Relationship Chains (N)", "Sub-questions (N)" | UI-Label |
| ~1045-1046 | "Latest Key Facts Associated in Sequential Memory", "Total N items" | UI-Label |
| ~1059 | "Collapse" / "Expand All N items" | UI-Label |
| ~1065 | "Core Entities" | UI-Label |
| ~1111 | "Drift Query Generated Sub-questions" | UI-Label |
| ~1125-1127 | "No current key memory", "No core entities", "No relationship chains" | Empty State |

**PanoramaDisplay Sub-Component (Step4Report.vue):**
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~1156 | "Panorama Search" | UI-Label |
| ~1160-1164 | "Nodes", "Edges" | UI-Label |
| ~1180-1192 | "Current Active Memory (N)", "Historical Memory (N)", "Involved Entities (N)" | UI-Label |
| ~1201-1263 | Panel-Titel + Empty States ("No current active memory", "No historical memory", "No involved entities") | UI-Label/Empty State |

### Step5Interaction.vue (NEU — fehlte komplett im Original-Audit)
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~ | "Prediction Report" | UI-Label |
| ~ | "Interactive Tools", "N agents available" | UI-Label |
| ~ | "Chat with Report Agent", "Chat with any individual", "Send survey to the world" | UI-Label |
| ~ | "Select conversation target" | UI-Label |
| ~ | "Report Agent - Chat" | UI-Label |
| ~ | "InsightForge Deep Attribution", "PanoramaSearch Panoramic Tracking", "QuickSearch Fast Retrieval", "InterviewSubAgent Virtual Interview" + Beschreibungen | UI-Label |
| ~ | "Introduction" | UI-Label |
| ~ | "You", "Report Agent" | UI-Label (Chat-Sender) |
| ~ | "Type your question..." | Placeholder |
| ~ | "Select survey targets", "Selected N / N" | UI-Label |
| ~ | "Survey Question" | UI-Label |
| ~ | "Enter the question you want to ask all selected targets..." | Placeholder |
| ~ | "Select All", "Clear", "Send Survey" | Button |
| ~ | "Survey Results", "N replies" | UI-Label |
| ~ | "Sorry, an error occurred: {msg}" | Error |
| ~ | "Please select a simulated individual first" | Error |
| ~ | "No response", "Unknown profession" | Fallback |

### GraphPanel.vue (NEU — fehlte komplett im Original-Audit)
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~ | "Graph Relationship Visualization" | UI-Label |
| ~ | "Refresh", "Refresh graph" | Button/Tooltip |
| ~ | "Maximize" / "Restore" | Tooltip |
| ~ | "GraphRAG short-term/long-term memory updating in real-time" | UI-Label |
| ~ | "Updating in real-time..." | Status-Text |
| ~ | "Some content is still being processed. It is recommended to manually refresh the graph later" | Status-Text |
| ~ | "Node Details", "Relationship" | UI-Label |
| ~ | "Name:", "UUID:", "Created:", "Properties:", "Summary:", "Labels:", "None" | UI-Label |
| ~ | "Self Relations", "RELATED_TO", "Unknown" | UI-Label (Fallback) |
| ~ | "Loading graph data...", "Waiting for ontology generation..." | Status-Text |
| ~ | "Entity Types", "Show Edge Labels" | UI-Label |

### HistoryDatabase.vue (NEU — fehlte komplett im Original-Audit)
| Zeile | String | Kategorie |
|-------|--------|-----------|
| ~ | "Simulation Records" | UI-Label |
| ~ | "Graph Construction", "Environment Setup", "Analysis Report" | UI-Label |
| ~ | "No Files", "Loading..." | Status-Text |
| ~ | "Simulation Requirement", "Associated Files", "No Associated Files" | UI-Label |
| ~ | "Simulation Playback" | UI-Label |
| ~ | "Step1", "Step2", "Step4" | Button-Label |
| ~ | Hinweis zu Step3/Step5 History Playback | UI-Label |
| ~ | "Unnamed Simulation", "Not Started" | Fallback |
| ~ | "{N}/{N} rounds", "Unknown File" | UI-Label |

### View-Wrapper (SimulationView, SimulationRunView, ReportView, InteractionView)
| Datei | String | Kategorie |
|-------|--------|-----------|
| SimulationView.vue | "Step 2/5", "Env Setup", "Preparing" | UI-Label/Status |
| SimulationRunView.vue | "Step 3/5", "Simulation", "Running" | UI-Label/Status |
| ReportView.vue | "Step 4/5", "Report", "Generating" | UI-Label/Status |
| InteractionView.vue | "Step 5/5", "Interaction", "Processing", "Ready" | UI-Label/Status |

### MainView.vue
| Zeile | String | Kategorie |
|-------|--------|-----------|
| 6 | "MIROFISH OFFLINE" | UI-Label |
| 18 | "Graph" / "Split" / "Workbench" | UI-Label |
| 25 | "Step {n}/5" | UI-Label |
| 94 | Step-Namen Array | UI-Label |
| 133-137 | "Error", "Ready", "Building Graph", "Generating Ontology", "Initializing" | Status-Text |

---

## 2. Backend — NICHT uebersetzen

Backend API-Responses (Error-Messages, Progress-Messages, Status-Texte) werden **nicht** uebersetzt.

**Begruendung:**
- Backend-Fehlermeldungen erreichen den User nur als technische Fallback-Info
- Progress-Messages (task_manager.update_task) werden im Frontend nicht direkt angezeigt — das Frontend hat eigene Status-Texte
- Uebersetzung wuerde API-Contracts verkomplizieren ohne User-Nutzen
- Fehler-Codes statt Strings waeren langfristig besser, aber out-of-scope fuer MIR-18

**Betrifft:** Alle Strings in `report.py`, `graph.py`, `simulation.py`, `simulation_manager.py`, `report_agent.py` (progress_callback), `task.py`, `project.py`.

---

## 3. LLM-Prompts — OUTPUT_LANGUAGE

### Bereits korrekt instrumentiert (keine Aenderung noetig):
- `ontology_generator.py:192` — Ontologie-Beschreibungen (Entity-Type-Namen bleiben Englisch)
- `report_agent.py:1173,1268,1816` — Report Plan/Section/Chat
- `simulation_config_generator.py:598,714,877` — Config/Opinion/Behavior
- `oasis_profile_generator.py:630,644,691` — Persona-Generierung

### Noch zu ergaenzen (OUTPUT_LANGUAGE hinzufuegen):
- `graph_tools.py:1417-1427` — Interview-Fragen-Generierung (Fragen erscheinen im Report)
- `graph_tools.py:1470-1484` — Interview-Summary (wird in Report eingebettet)

### NICHT uebersetzen (Pipeline/Schema bricht):
- `ner_extractor.py` — NER-Prompt muss Englisch bleiben (Entity-Types = Neo4j-Schema-Keys)
- `ontology_generator.py` Entity-Type `name`-Felder — Englisch/PascalCase erzwungen (Zeile 47, 61)
- `simulation_config_generator.py:872` — `stance`-Enum (`supportive/opposing/neutral/observer`) muss Englisch bleiben
- `simulation.py:24` — Interview-Prefix (LLM-Kontrollanweisung, nicht im Output sichtbar)
- `graph_tools.py:1151-1161` — Interview-Prefix mit Regex-abhaengigem `"Question X:"` Pattern
- `graph_tools.py:949-955` — Sub-Query-Generierung (intern, beeinflusst Retrieval-Qualitaet)
- `graph_tools.py:1355-1367` — Agent-Selection (intern, JSON-Output)
- `graph_tools.py:475-547` — Tool-Descriptions fuer LLM (LLM-intern, nicht user-facing)
- `report_agent.py:591-611,770-793,797-826` — ReACT User-Prompts und Control-Messages (LLM-intern)

### Bekannter Fehler im Original-Audit:
Der Interview-Prompt wurde `report_agent.py:24` zugeordnet — korrekt ist `simulation.py:24`.

---

## 4. OASIS Simulation Output

### Agent-Post-Sprache
Gesteuert durch die **Persona** (`bio`, `persona` Felder), die durch OUTPUT_LANGUAGE in `oasis_profile_generator.py` kontrolliert wird. Agenten posten in der Sprache ihrer Persona. Kein separater Language-Override noetig.

### Initial Posts
`simulation_config_generator.py` Event-Config generiert `initial_posts[].content` — bereits mit OUTPUT_LANGUAGE instrumentiert.

---

## 5. NICHT UEBERSETZEN — Programmatische Keys

Diese Strings werden in Frontend UND/ODER Backend als programmatische Schluessel per String-Vergleich genutzt. Uebersetzen bricht die Funktionalitaet.

### Enum-Werte (Backend → API → Frontend String-Vergleich)

| Enum | Werte | Frontend-Vergleich |
|------|-------|--------------------|
| TaskStatus | `processing`, `completed`, `failed`, `pending` | `task.status === 'completed'` in MainView.vue, Process.vue, Step2EnvSetup.vue |
| ProjectStatus | `created`, `ontology_generated`, `graph_building`, `graph_completed`, `failed` | `res.data.status === 'ontology_generated'` in MainView.vue, Process.vue |
| SimulationStatus | `created`, `preparing`, `ready`, `running`, `paused`, `stopped`, `completed`, `failed` | `data.status === 'completed'` in Step2EnvSetup.vue, SimulationView.vue |
| RunnerStatus | `idle`, `starting`, `running`, `paused`, `stopping`, `stopped`, `completed`, `failed` | `data.runner_status === 'completed'` in Step3Simulation.vue |
| ReportStatus | `pending`, `planning`, `generating`, `completed`, `failed` | API-Contract fuer `/api/report/check/` |

### Progress-Stage-Keys (Backend → API → Frontend String-Vergleich)

| Key | Frontend-Vergleich |
|-----|--------------------|
| `reading`, `generating_profiles`, `generating_config`, `copying_scripts` | `data.generation_stage === 'generating_profiles'` in Step2EnvSetup.vue |

### Agent-Log Action-Keys (Backend → JSONL → Frontend Template-Conditionals)

| Key | Frontend-Vergleich |
|-----|--------------------|
| `planning_start`, `planning_complete`, `section_start`, `section_content`, `section_complete`, `report_start`, `report_complete` | `v-if="log.action === 'planning_start'"` in Step4Report.vue |

### OASIS Action-Types (DB-Schema → API → Frontend Mapping)

| DB-Wert | Frontend-Vergleich |
|---------|--------------------|
| `CREATE_POST`, `REPOST`, `LIKE_POST`, `QUOTE_POST`, `FOLLOW`, `CREATE_COMMENT`, `SEARCH_POSTS`, `UPVOTE_POST`, `DOWNVOTE_POST`, `DO_NOTHING` | `action.action_type === 'CREATE_POST'` in Step3Simulation.vue |

**Strategie:** Diese Werte als Keys belassen. Das Frontend mappt sie auf uebersetzte Display-Labels via vue-i18n (z.B. `$t('status.' + task.status)`).

---

## 6. Empfehlung fuer Umsetzung

1. **Frontend:** vue-i18n Setup mit `$t('key')` Syntax, Locale-Files `en.json` / `de.json`
2. **Enum-Display:** Frontend mappt programmatische Keys auf uebersetzte Labels
3. **LLM-Prompts:** 2 Prompts in graph_tools.py mit OUTPUT_LANGUAGE ergaenzen
4. **Backend:** Keine Uebersetzung — Fehler-Codes waeren langfristig besser, aber separates Ticket
5. **OASIS:** Keine Aenderung noetig — Persona-Sprache steuert Post-Sprache
