---
marp: true
theme: ghostmesh
paginate: true
headingDivider: 2
class: lead
title: GhostMesh — Pitch
description: Invisible AI defense for IoT at the edge
---

# **GhostMesh**
### Invisible AI defense for IoT at the edge
<div class="small">Raspberry Pi 5 • OPC UA → MQTT • AI anomaly explain • Policy enforcement</div>

## The Problem

- IoT & Industrial devices are booming (tens of billions coming online).
- Current defenses lean on the cloud: slow, costly, and privacy-challenged.
- Security pain points:
  <ul class="red">
    <li>Latency — cloud round-trips miss real-time threats</li>
    <li>Bandwidth — raw telemetry overwhelms networks</li>
    <li>Blind spots — unexplained anomalies stall response</li>
  </ul>

## Our Solution (Implemented Today)

**GhostMesh on a Raspberry Pi 5**
<ul class="blue">
  <li>Ingest: OPC UA → normalized JSON over MQTT</li>
  <li>Detect: rolling z-score model flags anomalies locally</li>
  <li>Explain: concise LLM summary for operators</li>
  <li>Act: isolate / throttle / unblock devices; audit every action</li>
  <li>Dashboard: live telemetry, alerts, explanations, controls</li>
</ul>

<div class="callout small">
Runs offline at the edge → fast, private, resilient.
</div>

## Demo Snapshot

<div class="columns">
<div>

**Live sequence**
<ul class="green">
  <li>Normal telemetry (stable baseline)</li>
  <li>Injected spike → alert with severity</li>
  <li>AI explanation appears</li>
  <li>Operator clicks <span class="red">Isolate</span></li>
  <li>Traffic drops; audit log records action</li>
</ul>

</div>
<div>

*(Insert dashboard screenshot or mockup on the right column.)*

</div>
</div>

## Future Use Cases

<ul class="blue">
  <li>Federated Threat Sharing — distributed immune system across sites</li>
</ul>
<ul class="green">
  <li>Predictive Maintenance — same engine prevents downtime, not just attacks</li>
</ul>
<ul class="yellow">
  <li>MITRE ATT&CK for ICS — map anomalies to known tactics</li>
</ul>
<ul class="red">
  <li>Zero-Trust Device Identity — certs/TPM to block rogue devices</li>
</ul>
<ul class="blue">
  <li>Forensics & Replay — on-box black-box recorder for compliance</li>
</ul>
<ul class="green">
  <li>Cloud SOC Integration — send summarized incidents, not raw data</li>
</ul>

## Where GhostMesh Fits

<ul class="blue">
  <li>Smart Factories — PLCs, robots, sensors</li>
  <li>Energy & Utilities — grids, turbines, SCADA</li>
  <li>Healthcare IoT — monitors, pumps</li>
  <li>Critical Infrastructure — water, transport</li>
  <li>Retail & Logistics — warehouses, tracking</li>
</ul>

<div class="small">Universal applicability in high-stakes, latency-sensitive environments.</div>

## Market Opportunity

<div class="columns">
<div>
<ul class="yellow">
  <li>Industrial IoT Security: multi-$10B by 2030</li>
  <li>Predictive Maintenance: high-growth companion market</li>
  <li>Edge Computing: >$100B trajectory by 2030</li>
</ul>
</div>
<div>
<div class="callout small">
GhostMesh rides three waves: <b>edge</b> + <b>security</b> + <b>reliability</b>.
</div>
</div>
</div>

## Why GhostMesh

<ul class="green">
  <li>Edge-native: offline, low-latency, private</li>
  <li>Affordable hardware: Raspberry Pi 5</li>
  <li>Multipurpose ROI: Security + Reliability + Compliance</li>
  <li>Scalable vision: a mesh of self-learning guardians</li>
</ul>

## Call to Action

- **Today:** Live demo on Raspberry Pi
- **Next:** Pilot deployments and federated threat sharing
- **GhostMesh** — the invisible AI shield for the edge

<div class="small">Contact: raviChillerega@theedgeworks.ai • github.com/ramaedge/ghostmesh</div>
