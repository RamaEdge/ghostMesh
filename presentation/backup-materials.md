# GhostMesh Backup Presentation Materials

## Overview
This document contains backup materials for the GhostMesh presentation, including recorded demos, static screenshots, and alternative presentation formats in case of technical issues.

## Backup Demo Videos

### Video 1: Full Demo (5 minutes)
**File**: `ghostmesh-full-demo.mp4`
**Content**: Complete demonstration of GhostMesh capabilities
**Script**: 
```
"Welcome to GhostMesh, the Edge AI Security Copilot for Industrial IoT.

Here's our real-time dashboard monitoring industrial equipment.
You can see temperature, pressure, and vibration readings from multiple devices.

When I inject a security anomaly, GhostMesh instantly detects the threat
and explains it in operator-friendly language.

The system automatically enforces security policies,
isolating the compromised device and logging all actions.

GhostMesh continues monitoring, ensuring your industrial IoT
stays secure 24/7.

Real-time. Intelligent. Affordable."
```

### Video 2: Quick Demo (2 minutes)
**File**: `ghostmesh-quick-demo.mp4`
**Content**: Condensed demonstration focusing on key features
**Script**:
```
"GhostMesh detects industrial IoT threats in real-time.

Normal operation shows healthy equipment readings.

Anomaly injection triggers immediate detection and AI explanation.

Automated policy enforcement protects your systems.

All for under $500, running on a Raspberry Pi 5."
```

### Video 3: Technical Deep-dive (10 minutes)
**File**: `ghostmesh-technical-demo.mp4`
**Content**: Detailed technical demonstration for judges
**Script**:
```
"Let me show you the technical architecture of GhostMesh.

OPC UA gateway ingests device signals in real-time.
MQTT broker routes messages securely.
AI detector uses z-score analysis for anomaly detection.
LLM explainer generates plain-language threat analysis.
Policy engine enforces automated responses.

All running on a Raspberry Pi 5 with sub-2-second latency."
```

## Static Screenshots

### Dashboard Screenshots
1. **Normal Operation**: `dashboard-normal.png`
   - Healthy equipment readings
   - No alerts or warnings
   - Green status indicators

2. **Anomaly Detection**: `dashboard-alert.png`
   - High temperature alert
   - Red warning indicators
   - Alert details panel

3. **AI Explanation**: `dashboard-explanation.png`
   - Plain language explanation
   - Confidence score
   - Timestamp information

4. **Policy Actions**: `dashboard-actions.png`
   - Available response options
   - Audit trail
   - Action history

### Architecture Diagrams
1. **System Overview**: `architecture-overview.png`
   - High-level system components
   - Data flow arrows
   - Service connections

2. **Technical Stack**: `architecture-technical.png`
   - Detailed component breakdown
   - Technology stack
   - Integration points

3. **Deployment Diagram**: `architecture-deployment.png`
   - Raspberry Pi 5 hardware
   - Container services
   - Network connections

## Alternative Presentation Formats

### PowerPoint Version
**File**: `ghostmesh-pitch.pptx`
**Content**: Traditional PowerPoint presentation
**Slides**: 7 slides matching Marp version
**Features**: 
- Professional templates
- Embedded videos
- Interactive elements
- Speaker notes

### PDF Version
**File**: `ghostmesh-pitch.pdf`
**Content**: Static PDF presentation
**Features**:
- High-quality graphics
- Print-friendly format
- Offline viewing
- Easy sharing

### HTML Version
**File**: `ghostmesh-pitch.html`
**Content**: Web-based presentation
**Features**:
- Responsive design
- Interactive elements
- Embedded demos
- Cross-platform compatibility

## Demo Data Backup

### Pre-recorded Data
**File**: `demo-data.json`
**Content**: Sample telemetry data for demonstration
**Format**:
```json
{
  "normal_data": [
    {"asset": "Press01", "signal": "temperature", "value": 45.2, "unit": "°C"},
    {"asset": "Press01", "signal": "pressure", "value": 12.5, "unit": "bar"},
    {"asset": "Press01", "signal": "vibration", "value": 2.1, "unit": "mm/s"}
  ],
  "anomaly_data": [
    {"asset": "Press01", "signal": "temperature", "value": 95.7, "unit": "°C"},
    {"asset": "Press01", "signal": "pressure", "value": 26.3, "unit": "bar"},
    {"asset": "Press01", "signal": "vibration", "value": 8.4, "unit": "mm/s"}
  ]
}
```

### Mock Responses
**File**: `mock-responses.json`
**Content**: Pre-generated AI explanations and policy actions
**Format**:
```json
{
  "explanations": [
    {
      "alert_id": "a-12345678",
      "text": "Reading 95.7°C is unusually high compared to normal range",
      "confidence": 0.95,
      "timestamp": "2025-09-13T19:00:00Z"
    }
  ],
  "actions": [
    {
      "action_id": "act-12345678",
      "type": "isolate",
      "asset": "Press01",
      "reason": "High temperature anomaly detected",
      "timestamp": "2025-09-13T19:00:02Z"
    }
  ]
}
```

## Technical Backup Plans

### Service Recovery
**Script**: `recovery-script.sh`
**Content**: Automated service restart and health checks
```bash
#!/bin/bash
echo "Restarting GhostMesh services..."
podman-compose down
podman-compose up -d
sleep 10
echo "Checking service health..."
podman-compose ps
echo "Services restarted successfully"
```

### Network Backup
**Plan**: Mobile hotspot with backup internet connection
**Equipment**: 
- Mobile phone with hotspot capability
- Backup WiFi router
- Ethernet cable for direct connection

### Hardware Backup
**Plan**: Secondary Raspberry Pi 5 with pre-configured system
**Setup**: 
- Identical hardware configuration
- Pre-deployed GhostMesh system
- Ready-to-use demo environment

## Presentation Backup Plans

### Plan A: Live Demo
- **Primary**: Live system demonstration
- **Backup**: Recorded demo video
- **Fallback**: Static screenshots with narration

### Plan B: Recorded Demo
- **Primary**: Pre-recorded demo video
- **Backup**: Static screenshots with narration
- **Fallback**: Architecture diagrams with explanation

### Plan C: Static Presentation
- **Primary**: Screenshots and diagrams
- **Backup**: Architecture overview
- **Fallback**: Business case and ROI analysis

## Emergency Procedures

### Technical Failure
1. **Assess**: Determine scope of technical issue
2. **Switch**: Move to backup demo method
3. **Continue**: Maintain presentation flow
4. **Recover**: Attempt to fix primary system
5. **Resume**: Return to live demo if possible

### Network Issues
1. **Check**: Verify network connectivity
2. **Switch**: Use mobile hotspot
3. **Continue**: Proceed with demo
4. **Monitor**: Watch for connection stability
5. **Adapt**: Adjust demo pace as needed

### Hardware Failure
1. **Identify**: Determine hardware issue
2. **Switch**: Use backup hardware
3. **Continue**: Resume demonstration
4. **Document**: Note issue for follow-up
5. **Plan**: Arrange hardware replacement

## Success Metrics

### Demo Success Criteria
- [ ] All key features demonstrated
- [ ] Audience engagement maintained
- [ ] Technical questions answered
- [ ] Business value communicated
- [ ] Next steps established

### Backup Success Criteria
- [ ] Smooth transition to backup method
- [ ] No loss of presentation quality
- [ ] Audience unaware of technical issues
- [ ] All objectives achieved
- [ ] Professional impression maintained

## Post-Presentation Follow-up

### Immediate Actions
- **Thank Audience**: Express appreciation for attention
- **Answer Questions**: Address remaining questions
- **Provide Materials**: Share backup materials and contact info
- **Schedule Follow-up**: Arrange deeper discussions

### Follow-up Materials
- **Demo Videos**: All recorded demonstrations
- **Technical Docs**: Architecture and implementation details
- **Business Case**: ROI analysis and cost benefits
- **Contact Info**: Team contact information and next steps

### Success Tracking
- **Engagement**: Questions asked, interest expressed
- **Technical**: Understanding of capabilities demonstrated
- **Business**: Interest in pilot program or partnership
- **Next Steps**: Follow-up meetings scheduled

## Contact Information

### Primary Contact
- **Name**: Ravi Chillerega
- **Email**: ravi@ghostmesh.dev
- **Phone**: [Phone Number]
- **LinkedIn**: [LinkedIn Profile]

### Technical Contact
- **Name**: Technical Team
- **Email**: tech@ghostmesh.dev
- **GitHub**: github.com/ghostmesh
- **Documentation**: docs.ghostmesh.dev

### Business Contact
- **Name**: Business Team
- **Email**: business@ghostmesh.dev
- **Website**: ghostmesh.dev
- **Demo**: demo.ghostmesh.dev

## File Organization

### Directory Structure
```
presentation/
├── ghostmesh-pitch.md          # Main Marp presentation
├── pitch-script.md             # 90-second pitch script
├── branding.md                 # Branding guidelines
├── demo-flow.md                # Demo flow documentation
├── backup-materials.md         # This file
├── videos/                     # Demo videos
│   ├── ghostmesh-full-demo.mp4
│   ├── ghostmesh-quick-demo.mp4
│   └── ghostmesh-technical-demo.mp4
├── screenshots/                # Static images
│   ├── dashboard-normal.png
│   ├── dashboard-alert.png
│   ├── dashboard-explanation.png
│   └── dashboard-actions.png
├── diagrams/                   # Architecture diagrams
│   ├── architecture-overview.png
│   ├── architecture-technical.png
│   └── architecture-deployment.png
├── data/                       # Demo data
│   ├── demo-data.json
│   └── mock-responses.json
└── scripts/                    # Backup scripts
    └── recovery-script.sh
```

### File Naming Convention
- **Presentations**: `ghostmesh-[type].md`
- **Videos**: `ghostmesh-[type]-demo.mp4`
- **Images**: `[component]-[state].png`
- **Data**: `[type]-data.json`
- **Scripts**: `[action]-script.sh`

## Quality Assurance

### Pre-Presentation Checklist
- [ ] All backup materials available
- [ ] Videos play correctly
- [ ] Screenshots are clear and current
- [ ] Scripts are tested and working
- [ ] Contact information is accurate
- [ ] File organization is complete

### Post-Presentation Review
- [ ] Identify any technical issues
- [ ] Note audience feedback
- [ ] Update materials as needed
- [ ] Plan improvements for next presentation
- [ ] Document lessons learned
