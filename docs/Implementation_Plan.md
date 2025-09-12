# GhostMesh — 2‑Day Hackathon Implementation Proposal
**Goal:** Ship a compelling edge security demo on a Raspberry Pi 5 that detects IoT anomalies (OPC UA → MQTT), explains them via LLM, and enforces policy — with time left for polish, testing, and a tight presentation.

**Team Assumption:** 1–3 people  
**Hardware:** Raspberry Pi 5 (8GB) + 1TB SSD, active cooling  
**Tech Stack:** Python (asyncua, paho‑mqtt, Streamlit), Mosquitto, Docker Compose, optional local LLM (llama.cpp/qwen)

---

## 1) Deliverables (by end of Day 2)
1. **Running demo on Pi** with: Gateway, MQTT, Anomaly Detector, Policy Engine, Dashboard.
2. **Dash demo script**: live telemetry → anomaly → explanation → isolate → recover.
3. **Presentation deck** (5–7 slides) + 90‑sec pitch script.
4. **Repo structure** with `docker-compose.yml`, configs, and README (quick start).
5. **Short demo video** (30–45s screen recording, optional but powerful).
6. **Architecture doc** (done) + **Implementation plan** (this doc).

**Definition of Done (DoD)**
- Alert fires on simulated anomaly within ≤2s.  
- Dashboard shows telemetry, alert card, explanation text.  
- Clicking **Isolate** stops data from targeted asset; **Unblock** resumes.  
- Audit event logged for actions.  
- Demo runs offline (no cloud dependency).

---

## 2) High‑Level Scope
- **In‑scope:** Local OPC UA simulator → Gateway → MQTT → Anomaly → Explainer → Policy → Dashboard.
- **Out‑of‑scope (timebox):** TLS everywhere, SIEM integration, OTel metrics (note as roadmap).

---

## 3) Two‑Day Schedule (CET)
**Bias: build early, test often, keep a buffer.**

### Day 1 — Build Core (09:00–21:00)
| Time | Track | Tasks | Owner |
|---|---|---|---|
| 09:00–09:30 | Setup | Pi health check, update, Docker & Compose, git repo init | Ops |
| 09:30–10:30 | MQTT | Bring up Mosquitto with users & ACLs; smoke test with CLI sub/pub | Backend |
| 10:30–12:00 | Gateway | Implement OPC UA → MQTT (mapping.yaml, asyncua); connect to local OPC UA sim | Backend |
| 12:00–12:30 | UI | Streamlit skeleton: telemetry chart, alerts table placeholders | Frontend |
| 12:30–13:30 | Lunch + buffer | — | — |
| 13:30–15:00 | Detector | Rolling z‑score detector; topics subscribe/publish; debounce; severity | ML |
| 15:00–16:00 | Policy | App‑layer block first (broker ACL or filter), audit log topic | Backend |
| 16:00–17:00 | UI | Wire telemetry/alerts/control actions; basic theming “GhostMesh” | Frontend |
| 17:00–18:30 | Integration | Full flow: sim → gateway → MQTT → detector → alert → UI | All |
| 18:30–19:30 | Testing | Induce anomaly/flood; verify alert latency & isolate behavior | QA |
| 19:30–20:30 | Explainer | LLM call (local tiny or API); plug explanation panel | ML |
| 20:30–21:00 | Stabilize | Pin versions, compose profiles, write quick start in README | All |

**Outcome Day 1:** End‑to‑end demo works without hardcrashes. One anomaly path solid. README usable.

### Day 2 — Polish, Test, Present (09:00–18:00)
| Time | Track | Tasks | Owner |
|---|---|---|---|
| 09:00–10:00 | Hardening | Non‑root containers, env vars, minimal images; cap UI refresh | Backend |
| 10:00–11:00 | UX polish | Severity badges, color states, one‑click “Inject Anomaly” | Frontend |
| 11:00–12:00 | Tests | Latency measurement, false‑positive check, recovery behavior | QA |
| 12:00–12:30 | Buffer | Fix findings | All |
| 12:30–13:15 | Deck | 6–7 slide deck draft + pitch script | PM |
| 13:15–14:00 | Recording | Optional 30–45s demo video (screen capture + quick narration) | PM |
| 14:00–15:00 | Full Rehearsal #1 | Dry run end‑to‑end, timing, fix rough edges | All |
| 15:00–16:00 | Full Rehearsal #2 | Run on battery/backup network, test failure modes | All |
| 16:00–17:00 | Final Polish | Freeze repo/tag, export deck to PDF, create one‑page | All |
| 17:00–18:00 | Quiet Hour | No new features. Only fixes & practice. | All |

**Buffers:** ~2.5 hours across the schedule + Quiet Hour before judging.

---

## 4) Work Breakdown & Ownership
- **Gateway:** async OPC UA client, JSON normalize, publish to `factory/#`, retained `state/#` (Owner: Backend).
- **Detector:** rolling window (120s), z‑score, debounce, severity thresholds; publish `alerts/#` (Owner: ML).
- **Policy:** subscribe `alerts/#` & `control/#`, app‑layer block/unblock, publish `audit/actions` (Owner: Backend).
- **Dashboard:** charts (telemetry), alert table, explanation panel, action buttons (Owner: Frontend).
- **LLM Explainer:** local tiny model or API; prompt template; `explanations/<alertId>` (Owner: ML).
- **Ops:** Mosquitto config, users/ACL, docker‑compose, README, scripts (Owner: Ops/PM).

---

## 5) Testing Plan (fast + meaningful)
**Unit-ish checks**
- Gateway publishes for each mapping; retained `state/<asset>` present.
- Detector outputs alert for synthetic spike; no alert in steady state.
- Policy blocks target asset (messages disappear from UI), then unblocks.

**Integration tests**
- **Latency:** time from injected anomaly → alert emitted (target ≤2s).
- **Rate spike:** flood one asset; ensure detector emits once (debounce ok) and Policy throttles/blocks.
- **Recovery:** after unblock, telemetry resumes within ≤2s.
- **Negative:** malformed payload ignored; no crash.

**Observability basics**
- Log counts every 60s: processed messages, alerts emitted, actions taken.
- Dashboard status indicator: broker connected? last message age per asset.

---

## 6) Demo Script (90–120 seconds)
1. **Intro (10s):** “This is GhostMesh — invisible AI defense at the edge.”
2. **Normal (15s):** Live telemetry flowing, green status.
3. **Anomaly (20s):** Click “Inject Anomaly”; alert pops with severity and reason (z‑score).
4. **Explain (15s):** Explanation text appears (“likely spoofing or sensor fault; isolate device”).
5. **Act (20s):** Click **Isolate**; target asset’s line flattens; audit log entry shows.
6. **Recover (10s):** Click **Unblock**; readings resume.
7. **Close (10s):** “Runs offline on a Pi. Next: federated threat sharing + predictive maintenance.”

**Backup script (if something misbehaves)**
- Play the short recording showing the above sequence while you talk; keep containers running but don’t rely on live demo if the network’s noisy.

---

## 7) Risk Register & Mitigations
- **OPC UA flakiness:** Use local simulator (FreeOPCUA/Node‑RED); keep mapping minimal (2–3 nodes).  
- **False positives:** Start conservative (z≥4 medium, z≥8 high); debounce state changes.  
- **Policy misfire:** Default to app‑layer block first; nftables only if time permits.  
- **Performance spikes:** Limit UI redraw to 1–2 Hz; cap retained points (≤500).  
- **Network dependency:** Keep everything on Pi; no internet required; have hotspot fallback.

---

## 8) Implementation Details (quick start snippets)
**Repo layout**
```
ghostmesh/
├─ docker-compose.yml
├─ mosquitto/
│  ├─ mosquitto.conf
│  └─ passwd
├─ opcua2mqtt/      (asyncua + paho-mqtt)
├─ anomaly/         (z-score detector)
├─ policy/          (block/unblock + audit)
└─ dashboard/       (Streamlit UI)
```

**Compose (minimal)**
```yaml
services:
  mosquitto:
    image: eclipse-mosquitto:2
    ports: ["1883:1883"]
    volumes:
      - ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
      - ./mosquitto/passwd:/mosquitto/config/passwd:ro

  opcua2mqtt:
    build: ./opcua2mqtt
    depends_on: [mosquitto]
    environment: [ "MQTT_HOST=mosquitto" ]

  anomaly:
    build: ./anomaly
    depends_on: [mosquitto]
    environment: [ "MQTT_HOST=mosquitto", "MQTT_QOS=1" ]

  policy:
    build: ./policy
    depends_on: [mosquitto]
    environment: [ "MQTT_HOST=mosquitto" ]

  dashboard:
    build: ./dashboard
    depends_on: [mosquitto]
    ports: ["8501:8501"]
    environment: [ "MQTT_HOST=mosquitto" ]
```

**Mosquitto config**
```
listener 1883
persistence true
allow_anonymous false
password_file /mosquitto/config/passwd
```

**LLM prompt templates (selectable mode)**
- **Operator:** “Explain for a technician in ≤2 sentences; include likely cause and next step.”
- **Analyst:** “Security‑focused; reference technique and action.”
- **Hybrid:** Balanced; ≤2 sentences + action.
- **Alert:** One‑line (≤15 words).

**Context JSON passed to LLM**: `assetId, signal, current, mean, std, zscore, window, severity, lastNReadings[]`

---

## 9) Presentation Outline (6–7 slides)
1. **Title:** GhostMesh — Invisible AI Defense at the Edge (logo + tagline).
2. **Problem:** IoT attacks outpace cloud‑only defenses; latency + bandwidth + privacy.
3. **Solution:** Edge copilot on a Pi: detect → explain → act (OPC UA → MQTT).
4. **How it works:** Simple diagram + topics; z‑score + explain + isolate.
5. **Demo:** 4‑step flow screenshots or short GIF.
6. **Impact & Roadmap:** Federated threat sharing, predictive maintenance, MITRE ICS mapping.
7. **Why now:** Cheap edge hardware, modern MQTT/OPC UA, lightweight LLMs.

---

## 10) Stretch Goals (only if green across the board)
- **Simple TLS** for MQTT (self‑signed) and basic OPC UA Sign mode.
- **Rate anomaly** detector (packets/sec) in addition to value anomaly.
- **“Dark mode” polish** + branded theme; record and embed a tiny GIF in the deck.

---

## 11) Final Checklists

**Pre‑demo Device Checklist**
- [ ] Fan running; Pi temps stable < 70°C  
- [ ] SSD mounted; 2+ GB free  
- [ ] `docker ps` shows all services healthy  
- [ ] Dashboard reachable from laptop/phone  
- [ ] OPC UA sim producing values; mapping OK  
- [ ] Inject‑anomaly button functional  
- [ ] Block/unblock works reliably; audit event emitted

**Repo & Assets Checklist**
- [ ] README quick start (3 commands)  
- [ ] Architecture + Implementation docs (md)  
- [ ] Deck (PDF) + Pitch script (txt)  
- [ ] Optional 30–45s video

---

## 12) 3‑Command Quick Start (for judges/mentors)
```bash
git clone <repo> && cd ghostmesh
docker compose up -d --build
open http://<pi-ip>:8501   # Streamlit dashboard
```
