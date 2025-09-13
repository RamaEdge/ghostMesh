# GhostMesh Demo Flow Documentation

## Demo Overview

### Purpose
Demonstrate GhostMesh's real-time anomaly detection, AI-powered threat explanation, and automated policy enforcement capabilities in a live industrial IoT environment.

### Duration
- **Full Demo**: 5-7 minutes
- **Quick Demo**: 2-3 minutes
- **Backup Demo**: 1-2 minutes (recorded)

### Audience
- **Primary**: Hackathon judges, investors, potential customers
- **Secondary**: Technical teams, security professionals, industrial operators

## Pre-Demo Setup

### System Requirements
- **Hardware**: Raspberry Pi 5 with GhostMesh deployed
- **Services**: All GhostMesh services running (OPC UA, MQTT, AI, Dashboard)
- **Network**: Stable internet connection for dashboard access
- **Backup**: Recorded demo video ready to play

### Demo Environment
- **Mock OPC UA Server**: Simulating industrial equipment
- **Real-time Dashboard**: Live monitoring interface
- **MQTT Broker**: Message routing and storage
- **AI Services**: Anomaly detection and LLM explanation

### Pre-Demo Checklist
- [ ] All services running and healthy
- [ ] Dashboard accessible and responsive
- [ ] Mock data flowing normally
- [ ] Backup demo video ready
- [ ] Network connection stable
- [ ] Demo script rehearsed

## Demo Flow (Live)

### 1. Introduction (30 seconds)
**"Let me show you GhostMesh in action"**

- **Open Dashboard**: Navigate to GhostMesh dashboard
- **Show Normal Operation**: Point out healthy equipment readings
- **Explain Interface**: Highlight key dashboard elements
- **Set Context**: "This is monitoring real industrial equipment"

**Key Points:**
- Real-time telemetry data
- Clean, operator-friendly interface
- Multiple equipment types (presses, conveyors)
- Normal operating parameters

### 2. Normal Operation (45 seconds)
**"Here's what normal operation looks like"**

- **Temperature Readings**: Show normal temperature ranges (40-50°C)
- **Pressure Values**: Display typical pressure readings (10-15 bar)
- **Vibration Levels**: Point out normal vibration patterns (1-3 mm/s)
- **Status Indicators**: All equipment showing "Running" status

**Key Points:**
- Consistent, predictable patterns
- All values within normal ranges
- No alerts or warnings
- System operating smoothly

### 3. Anomaly Injection (60 seconds)
**"Now let's simulate a security threat"**

- **Click "Inject Demo Anomaly"**: Use dashboard button
- **Show Immediate Response**: Point out instant alert generation
- **Highlight Detection**: Temperature spike to 95°C
- **Explain Process**: "AI detected this in under 2 seconds"

**Key Points:**
- One-click anomaly injection
- Immediate visual feedback
- Clear alert indicators
- Real-time detection

### 4. AI Explanation (90 seconds)
**"Here's where GhostMesh gets intelligent"**

- **Show Alert Details**: Click on the generated alert
- **Read AI Explanation**: "Reading 95.7°C is unusually high compared to normal range"
- **Explain Reasoning**: Point out this is operator-friendly language
- **Show Confidence**: Display confidence score
- **Highlight Timestamp**: Show detection time

**Key Points:**
- Plain language explanations
- No technical jargon
- Confidence scoring
- Timestamp tracking

### 5. Policy Enforcement (60 seconds)
**"Now watch the automated response"**

- **Show Policy Actions**: Point out available actions
- **Demonstrate Isolation**: Show device isolation capability
- **Explain Automation**: "This happens automatically based on policies"
- **Show Audit Trail**: Display action logging

**Key Points:**
- Automated policy enforcement
- Multiple response options
- Audit trail maintenance
- Configurable policies

### 6. System Recovery (30 seconds)
**"And here's the recovery process"**

- **Show Normalization**: Point out values returning to normal
- **Explain Debounce**: "System prevents false positives"
- **Show Status**: Equipment returning to healthy state
- **Highlight Resilience**: "System continues monitoring"

**Key Points:**
- Automatic recovery
- Debounce protection
- Continuous monitoring
- System resilience

## Demo Flow (Backup - Recorded)

### Video Structure (2 minutes)
1. **Opening (15s)**: GhostMesh logo and tagline
2. **Normal Operation (30s)**: Dashboard showing healthy equipment
3. **Anomaly Injection (30s)**: Button click and immediate alert
4. **AI Explanation (30s)**: Alert details and plain language explanation
5. **Policy Enforcement (30s)**: Automated response actions
6. **Recovery (15s)**: System returning to normal

### Video Script
```
"GhostMesh: Edge AI Security Copilot for Industrial IoT

Here's our real-time dashboard monitoring industrial equipment.
All systems are operating normally with healthy readings.

When I inject a security anomaly, GhostMesh instantly detects the threat
and explains it in operator-friendly language.

The system automatically enforces security policies,
isolating the compromised device and logging all actions.

GhostMesh continues monitoring, ensuring your industrial IoT
stays secure 24/7.

Real-time. Intelligent. Affordable."
```

## Demo Scenarios

### Scenario 1: Temperature Anomaly
- **Trigger**: High temperature reading (95°C)
- **Detection**: Immediate alert generation
- **Explanation**: "Reading 95.7°C is unusually high compared to normal range"
- **Action**: Device isolation and operator notification

### Scenario 2: Pressure Spike
- **Trigger**: Sudden pressure increase (25+ bar)
- **Detection**: Real-time anomaly detection
- **Explanation**: "Pressure reading 26.3 bar exceeds safe operating limits"
- **Action**: Emergency shutdown and maintenance alert

### Scenario 3: Vibration Anomaly
- **Trigger**: Unusual vibration pattern (8+ mm/s)
- **Detection**: Pattern recognition alert
- **Explanation**: "Vibration levels indicate potential mechanical failure"
- **Action**: Predictive maintenance scheduling

### Scenario 4: Communication Failure
- **Trigger**: Device communication loss
- **Detection**: Connectivity monitoring
- **Explanation**: "Device Press01 has lost communication for 30 seconds"
- **Action**: Network diagnostics and failover activation

## Demo Troubleshooting

### Common Issues
1. **Dashboard Not Loading**
   - **Solution**: Check network connection, refresh page
   - **Backup**: Use recorded demo video

2. **Anomaly Injection Fails**
   - **Solution**: Check MQTT connection, restart services
   - **Backup**: Use pre-recorded anomaly data

3. **AI Explanation Missing**
   - **Solution**: Check LLM service status, restart explainer
   - **Backup**: Show static explanation examples

4. **Policy Actions Not Working**
   - **Solution**: Check policy engine status, verify permissions
   - **Backup**: Show policy configuration interface

### Recovery Procedures
- **Service Restart**: `podman-compose restart [service]`
- **Full System Restart**: `podman-compose down && podman-compose up -d`
- **Backup Demo**: Switch to recorded video
- **Manual Demo**: Walk through screenshots

## Demo Metrics

### Key Performance Indicators
- **Detection Latency**: <2 seconds (target)
- **Explanation Quality**: Plain language, actionable
- **System Uptime**: 99.9% availability
- **False Positive Rate**: <5%

### Demo Success Criteria
- [ ] All services running smoothly
- [ ] Dashboard responsive and clear
- [ ] Anomaly detection working
- [ ] AI explanations generated
- [ ] Policy actions executed
- [ ] Audience engagement maintained

## Post-Demo Follow-up

### Immediate Actions
- **Answer Questions**: Address technical and business questions
- **Provide Materials**: Share demo video, documentation, contact info
- **Schedule Follow-up**: Arrange deeper technical discussions
- **Collect Feedback**: Gather audience reactions and suggestions

### Follow-up Materials
- **Demo Video**: Recorded version for sharing
- **Technical Deep-dive**: Architecture and implementation details
- **Business Case**: ROI calculator and cost analysis
- **Pilot Program**: Information about trial deployments

### Success Metrics
- **Engagement**: Questions asked, interest expressed
- **Technical**: Understanding of capabilities demonstrated
- **Business**: Interest in pilot program or partnership
- **Next Steps**: Follow-up meetings scheduled

## Demo Script Variations

### Technical Audience
- **Focus**: Architecture, algorithms, performance metrics
- **Depth**: Detailed technical explanations
- **Tools**: Code snippets, configuration examples
- **Questions**: Implementation details, scalability

### Business Audience
- **Focus**: ROI, cost savings, business impact
- **Depth**: High-level benefits and use cases
- **Tools**: Cost calculators, case studies
- **Questions**: Pricing, deployment, support

### Mixed Audience
- **Focus**: Balanced technical and business content
- **Depth**: Moderate detail with clear explanations
- **Tools**: Visual diagrams, simple metrics
- **Questions**: Both technical and business aspects

## Demo Environment Setup

### Development Environment
```bash
# Start all services
podman-compose up -d

# Check service status
podman-compose ps

# View logs
podman-compose logs -f

# Access dashboard
open http://localhost:8501
```

### Production Environment
- **Hardware**: Raspberry Pi 5 with 8GB RAM, 1TB SSD
- **OS**: Ubuntu 22.04 LTS
- **Services**: All GhostMesh services containerized
- **Network**: Dedicated network segment for demo
- **Backup**: Redundant systems and recorded demos

### Demo Data
- **Normal Range**: Temperature 40-50°C, Pressure 10-15 bar
- **Anomaly Values**: Temperature 95°C, Pressure 25+ bar
- **Equipment Types**: Presses, conveyors, sensors
- **Update Frequency**: 1-second intervals
- **Data Volume**: 100+ data points per minute
