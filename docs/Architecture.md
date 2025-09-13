# GhostMesh — Edge AI Security Copilot
**Subtitle:** Invisible protection for IoT at the edge  
**Target:** Raspberry Pi 5 (8 GB) + 1 TB SSD • MQTT bus • Python services  
**Version:** 1.0 (Hackathon) • **Date:** 2025‑09‑12  
**Status:** ✅ OPC UA Gateway Implemented and Operational

---

## 1) Purpose & Scope
GhostMesh is an edge‑resident security copilot for industrial/IoT environments. It ingests device signals (OPC UA), normalizes them to MQTT, detects anomalies in real time, explains risk in plain language, and enforces policy (throttle/isolate). Designed for a 2‑day hackathon demo with a credible path to production.

**In‑scope**
- Data flow: OPC UA → MQTT → AI detection → explanation → policy action  
- Component boundaries and interfaces  
- Minimal models (anomaly + explainer)  
- Edge security controls

**Out‑of‑scope (hackathon)**
- Fleet mgmt, SIEM integration at scale, long‑term training, OpenTelemetry

---

## 2) System Context (C4: Context)
```
[Plant / Lab]
  └─ OPC UA Devices (real/sim)

[Edge Node: Raspberry Pi 5]
  ├─ ✅ OPC UA → MQTT Gateway (opcua2mqtt) - OPERATIONAL
  ├─ ✅ MQTT Broker (Mosquitto) - OPERATIONAL
  ├─ ✅ Mock OPC UA Server - OPERATIONAL
  ├─ ✅ Anomaly Detector (z‑score analysis) - OPERATIONAL
  ├─ ✅ AI Explainer (local LLM/TinyLlama) - OPERATIONAL
  ├─ ✅ Policy Engine (isolate/throttle/unblock) - OPERATIONAL
  ├─ ✅ LLM Server (llama.cpp) - OPERATIONAL
  └─ ✅ Dashboard (Streamlit) - OPERATIONAL

[Operator]
  └─ Browser → Dashboard
```
- Operator views live telemetry, alerts, explanations; can issue control actions.

---

## 3) Current Implementation Status

### ✅ Operational Components
**OPC UA to MQTT Gateway (THE-60)**
- Async OPC UA client using `asyncua` library
- 11 node mappings for industrial equipment simulation
- Real-time data flow at ~1Hz
- JSON telemetry messages with structured schema
- MQTT topics following `factory/<line>/<asset>/<signal>` pattern
- Retained state messages to `state/<asset>` topics
- Comprehensive error handling and reconnection logic

**Infrastructure**
- Mock OPC UA server simulating Press01, Press02, and Conveyor01 equipment
- MQTT broker with authentication and ACLs
- Containerized services with Podman
- Comprehensive Makefile for build, test, and deployment

### 🔄 Planned Components
- Anomaly Detector (rolling z-score analysis)
- AI Explainer (LLM-based risk explanation)
- Policy Engine (automated response actions)
- Streamlit Dashboard (real-time monitoring UI)

## 4) End‑to‑End Data Flow
**Current Implementation (Steps 1-2)**
1) **OPC UA** device value changes → Gateway subscription receives updates. ✅
2) Gateway normalizes to **JSON** and publishes to **MQTT** topics `factory/<line>/<asset>/<signal>`. ✅

**Current Implementation (Steps 3-6)**
3) **Anomaly Detector** subscribes and computes rolling baselines; emits **alerts** to `alerts/<asset>/<signal>`. ✅
4) **AI Explainer** subscribes to alerts, generates short text explanations → `explanations/<alertId>`. 🔄
5) **Dashboard** renders telemetry/alerts/explanations; operator can publish **control** commands to `control/<asset>/<command>`. ✅
6) **Policy Engine** subscribes to alerts/control and enforces block/throttle; publishes **audit** events `audit/actions`. ✅

**Topics**
- Telemetry: `factory/<line>/<asset>/<signal>`  
- State (retained): `state/<asset>`  
- Alerts: `alerts/<asset>/<signal>`  
- Explanations: `explanations/<alertId>`  
- Control: `control/<asset>/<command>` (isolate|throttle|unblock)  
- Audit: `audit/actions`

---

## 4) Component Layer Specs

### 4.1 OPC UA → MQTT Gateway
- **Goal:** Subscribe to configured OPC UA nodeIds and publish normalized telemetry to MQTT.  
- **Tech:** Python `asyncua`, `paho‑mqtt`, YAML mapping.  
- **Config (`mapping.yaml`)**
  ```yaml
  endpoint: "opc.tcp://localhost:4840"
  security_policy: "Basic256Sha256"
  security_mode: "Sign"
  username: "edge"
  password: "edgepass"

  mqtt:
    host: "mosquitto"
    port: 1883
    username: "iot"
    password: "iotpass"
    qos: 1
    retain_state: true

  mappings:
    - nodeId: "ns=2;s=Press01.Temperature"
      topic: "factory/A/press01/temperature"
      unit: "C"
    - nodeId: "ns=2;s=Press01.Pressure"
      topic: "factory/A/press01/pressure"
      unit: "bar"
  ```

### 4.2 MQTT Broker (Mosquitto)
- **Goal:** Decouple producers/consumers; QoS, retained liveness.  
- **Security:** Disable anonymous, per‑service users, optional TLS (demo‑optional).

### 4.3 Anomaly Detector ✅ IMPLEMENTED
- **Goal:** Online detection over sliding windows; emit alerts with rationale.  
- **Implementation:** Rolling z‑score per (asset, signal) over W=120s. Medium if z≥4; High if z≥8; 30s debounce.  
- **Features:** Efficient deque operations, edge case handling, MQTT integration, containerized deployment.
- **Optional:** IsolationForest on short windows for show‑time.

### 4.4 AI Explainer
- **Goal:** Turn alert facts into 1‑2 sentence operator guidance.  
- **LLM:** Local tiny model (e.g., Qwen‑0.5/1.8B via llama.cpp) or external API.  
- **Output:** `explanations/<alertId>` with `{ text, confidence }`.

### 4.5 Policy Engine ✅ IMPLEMENTED
- **Goal:** Map alert severity/commands to actions.  
- **Implementation:** `isolate` (app-layer blocking), `throttle` (rate limiting), `unblock` (restore).  
- **Features:** App-layer blocking with state tracking, comprehensive audit logging, auto-policy for high severity alerts.
- **Audit:** Publish `audit/actions` with result (success/fail) and unique action IDs.

### 4.6 Dashboard (Streamlit)
- **Views:** live charts (telemetry), alerts table, explanation panel, action buttons.  
- **Perf:** 1–2 Hz redraw; last 500 points per signal.

---

## 5) Schemas (JSON)

**Telemetry**
```json
{
  "assetId": "press01",
  "line": "A",
  "signal": "temperature",
  "value": 143.2,
  "unit": "C",
  "ts": "2025-09-12T11:05:11.481Z",
  "quality": "Good",
  "source": "opcua",
  "seq": 127839
}
```

**Alert**
```json
{
  "alertId": "a-9f1c3",
  "assetId": "press01",
  "signal": "temperature",
  "severity": "high",
  "reason": "z-score 9.4 vs mean 42.1±1.0 (120s)",
  "current": 143.2,
  "ts": "2025-09-12T11:05:12.010Z"
}
```

**Explanation**
```json
{
  "alertId": "a-9f1c3",
  "text": "press01 temperature spiked far beyond baseline (z=9.4). Likely fault or spoofing. Isolate and verify.",
  "confidence": 0.78,
  "ts": "2025-09-12T11:05:12.400Z"
}
```

**Control**
```json
{
  "assetId": "press01",
  "command": "isolate",
  "reason": "operator_action",
  "refAlertId": "a-9f1c3",
  "ts": "2025-09-12T11:05:13.000Z"
}
```

**Audit**
```json
{
  "actionId": "act-44d21",
  "assetId": "press01",
  "action": "isolate",
  "method": "nftables",
  "result": "success",
  "ts": "2025-09-12T11:05:13.120Z"
}
```

---

## 6) LLM Prompting Options (choose per audience)

**Operator (plain English)**  
_System:_ “You are GhostMesh, an edge security assistant. Explain in ≤2 sentences for a technician. Suggest likely cause and next step.”

**Analyst (cyber SOC)**  
_System:_ “You are GhostMesh, an edge cybersecurity copilot. Use technical language, reference potential techniques, and propose an action.”

**Hybrid (default)**  
_System:_ “Explain with a balance of technical detail and plain English. ≤2 sentences plus a recommended action.”

**Alert‑style (concise)**  
_System:_ “Return a single‑line alert (≤15 words).”

**Context JSON passed to LLM**: `assetId, signal, current, mean, std, zscore, window, severity, lastNReadings[]`

---

## 7) Security Architecture

**Comms & Auth**  
- OPC UA: Username/Password (demo), target: Basic256Sha256 + Sign/Sign&Encrypt.  
- MQTT: No anonymous; per‑service users; least‑privilege ACLs.  
- TLS: Optional for hackathon; recommended in prod.

**Enforcement**  
- Network: `nftables` per device IP/MAC; `tc` for throttle.  
- App‑layer: broker ACL denylist; service‑side ignore as safe fallback.

**Hardening**  
- Non‑root containers, minimal images, locked‑down ports.  
- Mosquitto persistence + strong passwords.  
- Local firewall on Pi; dashboard limited to LAN.

**Threat Model (STRIDE)**  
- Spoofing: per‑device creds / pin MAC/IP.  
- Tampering: TLS + schema validation (future signing).  
- Repudiation: `audit/actions` with IDs.  
- Info disclosure: limited payloads, no secrets in topics.  
- DoS: rate limits in detector & broker; `tc` throttling.  
- EoP: least privilege; only Policy can execute system commands.

---

## 8) Deployment (Raspberry Pi 5)

**Repo layout**
```
ghostmesh/
├─ docker-compose.yml
├─ mosquitto/
│  ├─ mosquitto.conf
│  └─ passwd
├─ opcua2mqtt/
│  ├─ Dockerfile  ├─ requirements.txt  ├─ mapping.yaml  └─ opcua2mqtt.py
├─ anomaly/
│  ├─ Dockerfile  ├─ requirements.txt  └─ main.py
├─ policy/
│  ├─ Dockerfile  ├─ requirements.txt  └─ policy.py
└─ dashboard/
   ├─ Dockerfile  ├─ requirements.txt  └─ app.py
```

**docker‑compose.yml (sketch)**
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

---

## 9) Demo Script (Operator Journey)
1) **Normal:** telemetry streams; green status.  
2) **Inject anomaly:** spike/flood; detector emits alert with z‑score reason.  
3) **Explain:** explainer posts 1–2 sentence summary.  
4) **Act:** click **Isolate**; traffic for asset drops; audit event logged.  
5) **Recover:** **Unblock**; normal flow resumes; alert clears.

---

## 10) Future Product Use Cases (Roadmap Teasers)
- **Federated threat sharing** between edge nodes (distributed immune system).  
- **Predictive maintenance** using the same anomaly engine.  
- **MITRE ATT&CK for ICS mapping** on alerts.  
- **Zero‑trust device identity** (certs/TPM attestation).  
- **Forensics & replay** from local SSD; compliance reports (NIS2/IEC 62443).  
- **Cloud SIEM integration** with summarized incidents.  
- **Adaptive policies** (RL) that learn optimal responses.

---

## 11) Risks & Mitigations
- **OPC UA instability:** use local simulator to de‑risk demo.  
- **False positives:** conservative thresholds; operator override.  
- **Policy misfires:** default to app‑layer blocks; nftables as advanced.  
- **Resource limits:** small LLM or API; low UI refresh rate.

---

## Appendix — Broker ACL Sketch
```
user gateway
topic write factory/#
topic write state/#

user detector
topic read  factory/#
topic write alerts/#

user explainer
topic read  alerts/#
topic write explanations/#

user policy
topic read  alerts/# control/#
topic write audit/#

user dashboard
topic read  factory/# alerts/# explanations/# state/# audit/#
topic write control/#
```
