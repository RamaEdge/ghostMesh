"""
GhostMesh Dashboard
Edge AI Security Copilot - Streamlit Web Interface

This dashboard provides real-time monitoring of:
- OPC UA telemetry data
- Anomaly alerts
- System status
- Policy actions
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime, timedelta
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="GhostMesh Dashboard",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff2f2;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
        margin: 0.5rem 0;
    }
    .success-card {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00aa44;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Global variables for MQTT data
if 'telemetry_data' not in st.session_state:
    st.session_state.telemetry_data = []
if 'alerts_data' not in st.session_state:
    st.session_state.alerts_data = []
if 'mqtt_connected' not in st.session_state:
    st.session_state.mqtt_connected = False

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            st.session_state.mqtt_connected = True
            st.success("✅ Connected to MQTT broker")
            # Subscribe to telemetry topics
            client.subscribe("factory/+/+/+")
            client.subscribe("alerts/+/+")
            client.subscribe("explanations/+")
            client.subscribe("control/+/+")
            client.subscribe("audit/actions")
        else:
            st.error(f"❌ Failed to connect to MQTT broker. Code: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Add timestamp
            payload['timestamp'] = datetime.now()
            payload['topic'] = topic
            
            # Store telemetry data
            if topic.startswith("factory/"):
                st.session_state.telemetry_data.append(payload)
                # Keep only last 100 data points
                if len(st.session_state.telemetry_data) > 100:
                    st.session_state.telemetry_data = st.session_state.telemetry_data[-100:]
            
            # Store alerts data
            elif topic.startswith("alerts/"):
                st.session_state.alerts_data.append(payload)
                # Keep only last 50 alerts
                if len(st.session_state.alerts_data) > 50:
                    st.session_state.alerts_data = st.session_state.alerts_data[-50:]
                    
        except Exception as e:
            st.error(f"Error processing MQTT message: {e}")
            
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        st.session_state.mqtt_connected = False
        st.warning("⚠️ Disconnected from MQTT broker")
        
    def connect(self, host="localhost", port=1883, username="dashboard", password="dashboard123"):
        try:
            self.client.username_pw_set(username, password)
            self.client.connect(host, port, 60)
            self.client.loop_start()
        except Exception as e:
            st.error(f"Failed to connect to MQTT: {e}")
            
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

def create_telemetry_chart():
    """Create telemetry chart placeholder using Plotly"""
    if not st.session_state.telemetry_data:
        # Create sample data for demonstration
        sample_data = []
        for i in range(20):
            sample_data.append({
                'timestamp': datetime.now() - timedelta(minutes=20-i),
                'value': 25 + (i * 0.5) + (i % 3) * 2,
                'asset': 'Press01',
                'signal': 'Temperature'
            })
        
        df = pd.DataFrame(sample_data)
    else:
        df = pd.DataFrame(st.session_state.telemetry_data)
    
    if not df.empty:
        fig = go.Figure()
        
        # Group by asset and signal
        for (asset, signal), group in df.groupby(['asset', 'signal']):
            fig.add_trace(go.Scatter(
                x=group['timestamp'],
                y=group['value'],
                mode='lines+markers',
                name=f"{asset} - {signal}",
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Real-time Telemetry Data",
            xaxis_title="Time",
            yaxis_title="Value",
            hovermode='x unified',
            height=400
        )
        
        return fig
    else:
        # Empty chart placeholder
        fig = go.Figure()
        fig.add_annotation(
            text="No telemetry data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig

def create_alerts_table():
    """Create alerts table placeholder"""
    if not st.session_state.alerts_data:
        # Create sample alerts for demonstration
        sample_alerts = [
            {
                'timestamp': datetime.now() - timedelta(minutes=5),
                'asset': 'Press01',
                'signal': 'Temperature',
                'severity': 'High',
                'message': 'Temperature above normal threshold',
                'value': 85.2
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=12),
                'asset': 'Conveyor01',
                'signal': 'Speed',
                'severity': 'Medium',
                'message': 'Speed deviation detected',
                'value': 45.8
            }
        ]
        df = pd.DataFrame(sample_alerts)
    else:
        df = pd.DataFrame(st.session_state.alerts_data)
    
    if not df.empty:
        # Format the dataframe for display
        display_df = df.copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
        
        # Color code severity
        def color_severity(val):
            if val == 'High':
                return 'background-color: #ffebee'
            elif val == 'Medium':
                return 'background-color: #fff3e0'
            elif val == 'Low':
                return 'background-color: #e8f5e8'
            return ''
        
        styled_df = display_df.style.applymap(color_severity, subset=['severity'])
        return styled_df
    else:
        return pd.DataFrame({'Message': ['No alerts available']})

def main():
    # Header
    st.markdown('<h1 class="main-header">👻 GhostMesh Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Edge AI Security Copilot - Real-time Industrial Monitoring</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Control Panel")
        
        # MQTT Connection Status
        st.subheader("Connection Status")
        if st.session_state.mqtt_connected:
            st.success("🟢 MQTT Connected")
        else:
            st.error("🔴 MQTT Disconnected")
        
        # MQTT Connection Controls
        st.subheader("MQTT Settings")
        mqtt_host = st.text_input("MQTT Host", value="localhost")
        mqtt_port = st.number_input("MQTT Port", value=1883, min_value=1, max_value=65535)
        mqtt_username = st.text_input("Username", value="dashboard")
        mqtt_password = st.text_input("Password", value="dashboard123", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect"):
                mqtt_client = MQTTClient()
                mqtt_client.connect(mqtt_host, mqtt_port, mqtt_username, mqtt_password)
                st.session_state.mqtt_client = mqtt_client
        
        with col2:
            if st.button("Disconnect") and 'mqtt_client' in st.session_state:
                st.session_state.mqtt_client.disconnect()
        
        # Refresh controls
        st.subheader("Data Controls")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("🗑️ Clear Data"):
            st.session_state.telemetry_data = []
            st.session_state.alerts_data = []
            st.rerun()
    
    # Main content area
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Assets",
            value=len(set([d.get('asset', 'Unknown') for d in st.session_state.telemetry_data])) or 3,
            delta="2"
        )
    
    with col2:
        st.metric(
            label="Active Alerts",
            value=len(st.session_state.alerts_data) or 2,
            delta="1"
        )
    
    with col3:
        st.metric(
            label="Data Points",
            value=len(st.session_state.telemetry_data) or 20,
            delta="5"
        )
    
    with col4:
        uptime = "2h 15m"  # Placeholder
        st.metric(
            label="System Uptime",
            value=uptime,
            delta="0m"
        )
    
    # Charts and tables
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Telemetry Charts")
        fig = create_telemetry_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Active Alerts")
        alerts_df = create_alerts_table()
        st.dataframe(alerts_df, use_container_width=True)
    
    # Additional information
    st.subheader("📋 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Available MQTT Topics:**
        - `factory/<line>/<asset>/<signal>` - Telemetry data
        - `alerts/<asset>/<signal>` - Anomaly alerts
        - `explanations/<alertId>` - Alert explanations
        - `control/<asset>/<command>` - Control commands
        - `audit/actions` - Policy actions
        """)
    
    with col2:
        st.markdown("""
        **System Status:**
        - MQTT Broker: ✅ Running
        - OPC UA Gateway: ✅ Connected
        - Mock OPC UA Server: ✅ Active
        - Anomaly Detector: 🚧 Planned
        - Policy Engine: 🚧 Planned
        """)
    
    # Auto-refresh
    if st.session_state.mqtt_connected:
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()
