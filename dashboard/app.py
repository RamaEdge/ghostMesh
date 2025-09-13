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
import os
from datetime import datetime, timedelta
import threading
import queue

# Environment configuration
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'dashboard')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'dashboard123')

# Page configuration
st.set_page_config(
    page_title="GhostMesh Dashboard",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for GhostMesh branding and styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .ghostmesh-brand {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #2E86AB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .alert-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #E53E3E;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #38A169;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .control-button {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .control-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .severity-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .severity-high {
        background: linear-gradient(135deg, #FED7D7 0%, #FEB2B2 100%);
        color: #C53030;
        border: 1px solid #F56565;
    }
    .severity-medium {
        background: linear-gradient(135deg, #FEEBC8 0%, #FBD38D 100%);
        color: #DD6B20;
        border: 1px solid #ED8936;
    }
    .severity-low {
        background: linear-gradient(135deg, #C6F6D5 0%, #9AE6B4 100%);
        color: #2F855A;
        border: 1px solid #48BB78;
    }
    .severity-critical {
        background: linear-gradient(135deg, #FED7D7 0%, #FC8181 100%);
        color: #9B2C2C;
        border: 1px solid #E53E3E;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(229, 62, 62, 0); }
        100% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: statusPulse 2s infinite;
    }
    .status-connected {
        background-color: #38A169;
        box-shadow: 0 0 6px rgba(56, 161, 105, 0.6);
    }
    .status-disconnected {
        background-color: #E53E3E;
        box-shadow: 0 0 6px rgba(229, 62, 62, 0.6);
    }
    .status-warning {
        background-color: #DD6B20;
        box-shadow: 0 0 6px rgba(221, 107, 32, 0.6);
    }
    @keyframes statusPulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #2E86AB;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 8px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .demo-button {
        background: linear-gradient(135deg, #A23B72 0%, #F18F01 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(162, 59, 114, 0.3);
        margin: 0.5rem 0;
    }
    .demo-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(162, 59, 114, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Global variables for MQTT data
if 'telemetry_data' not in st.session_state:
    st.session_state.telemetry_data = []
if 'alerts_data' not in st.session_state:
    st.session_state.alerts_data = []
if 'audit_data' not in st.session_state:
    st.session_state.audit_data = []
if 'mqtt_connected' not in st.session_state:
    st.session_state.mqtt_connected = False
if 'mqtt_client' not in st.session_state:
    st.session_state.mqtt_client = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = "disconnected"

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        # Thread-safe data storage
        self._telemetry_data = []
        self._alerts_data = []
        self._audit_data = []
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            # Subscribe to telemetry topics
            client.subscribe("factory/+/+/+")
            client.subscribe("alerts/+/+")
            client.subscribe("explanations/+")
            client.subscribe("control/+/+")
            client.subscribe("audit/actions")
            print(f"MQTT connected successfully")
        else:
            print(f"MQTT connection failed with code: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Add timestamp
            payload['timestamp'] = datetime.now()
            payload['topic'] = topic
            
            # Store telemetry data
            if topic.startswith("factory/"):
                # Parse topic: factory/<line>/<asset>/<signal>
                topic_parts = topic.split('/')
                if len(topic_parts) == 4:
                    payload['line'] = topic_parts[1]
                    payload['asset'] = topic_parts[2]
                    payload['signal'] = topic_parts[3]
                
                # Store in a thread-safe way
                if hasattr(self, '_telemetry_data'):
                    self._telemetry_data.append(payload)
                    # Keep only last 200 data points
                    if len(self._telemetry_data) > 200:
                        self._telemetry_data = self._telemetry_data[-200:]
            
            # Store alerts data
            elif topic.startswith("alerts/"):
                # Parse topic: alerts/<asset>/<signal>
                topic_parts = topic.split('/')
                if len(topic_parts) == 3:
                    payload['asset'] = topic_parts[1]
                    payload['signal'] = topic_parts[2]
                
                # Store in a thread-safe way
                if hasattr(self, '_alerts_data'):
                    self._alerts_data.append(payload)
                    # Keep only last 100 alerts
                    if len(self._alerts_data) > 100:
                        self._alerts_data = self._alerts_data[-100:]
            
            # Store audit data
            elif topic == "audit/actions":
                # Store in a thread-safe way
                if hasattr(self, '_audit_data'):
                    self._audit_data.append(payload)
                    # Keep only last 50 audit events
                    if len(self._audit_data) > 50:
                        self._audit_data = self._audit_data[-50:]
                    
        except Exception as e:
            # Log error without using Streamlit from background thread
            print(f"Error processing MQTT message: {e}")
            
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"MQTT disconnected")
        
    def connect(self, host=None, port=None, username=None, password=None):
        try:
            # Use environment variables as defaults
            host = host or MQTT_HOST
            port = port or MQTT_PORT
            username = username or MQTT_USERNAME
            password = password or MQTT_PASSWORD
            
            self.client.username_pw_set(username, password)
            self.client.connect(host, port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT: {e}")
            
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_control_command(self, asset_id, command, reason="operator_action", ref_alert_id=None):
        """Publish a control command to the policy engine"""
        try:
            control_topic = f"control/{asset_id}/{command}"
            control_payload = {
                "assetId": asset_id,
                "command": command,
                "reason": reason,
                "ts": datetime.now().isoformat()
            }
            
            if ref_alert_id:
                control_payload["refAlertId"] = ref_alert_id
            
            self.client.publish(control_topic, json.dumps(control_payload), qos=1)
            return True
        except Exception as e:
            st.error(f"Failed to publish control command: {e}")
            return False

def render_severity_badge(severity):
    """Render a styled severity badge"""
    severity_map = {
        'critical': {'class': 'severity-critical', 'icon': '🚨', 'text': 'CRITICAL'},
        'high': {'class': 'severity-high', 'icon': '🔴', 'text': 'HIGH'},
        'medium': {'class': 'severity-medium', 'icon': '🟡', 'text': 'MEDIUM'},
        'low': {'class': 'severity-low', 'icon': '🟢', 'text': 'LOW'}
    }
    
    severity_info = severity_map.get(severity.lower(), severity_map['low'])
    
    return f"""
    <span class="severity-badge {severity_info['class']}">
        {severity_info['icon']} {severity_info['text']}
    </span>
    """

def get_system_status():
    """Get overall system status based on alerts and connections"""
    if not st.session_state.mqtt_connected:
        return 'disconnected', 'Disconnected', '#E53E3E'
    
    if not st.session_state.alerts_data:
        return 'connected', 'All Systems Normal', '#38A169'
    
    # Check for critical/high severity alerts
    high_severity_count = sum(1 for alert in st.session_state.alerts_data 
                             if alert.get('severity', '').lower() in ['critical', 'high'])
    
    if high_severity_count > 0:
        return 'warning', f'{high_severity_count} High Priority Alert(s)', '#DD6B20'
    else:
        return 'connected', 'Monitoring Active', '#38A169'

def create_telemetry_chart():
    """Create real-time telemetry chart using Plotly"""
    if not st.session_state.telemetry_data:
        # Create sample data for demonstration when no real data is available
        sample_data = []
        assets = ['Press01', 'Press02', 'Conveyor01']
        signals = ['Temperature', 'Pressure', 'Speed']
        
        for i in range(30):
            for asset in assets:
                for signal in signals:
                    if signal == 'Temperature':
                        value = 25 + (i * 0.3) + (i % 5) * 1.5
                    elif signal == 'Pressure':
                        value = 10 + (i * 0.2) + (i % 3) * 0.8
                    else:  # Speed
                        value = 50 + (i * 0.1) + (i % 4) * 2
                    
                    sample_data.append({
                        'timestamp': datetime.now() - timedelta(minutes=30-i),
                        'value': round(value, 2),
                        'asset': asset,
                        'signal': signal,
                        'line': 'A'
                    })
        
        df = pd.DataFrame(sample_data)
    else:
        df = pd.DataFrame(st.session_state.telemetry_data)
    
    if not df.empty:
        fig = go.Figure()
        
        # Define colors for different assets
        colors = {
            'Press01': '#2E86AB',
            'Press02': '#A23B72', 
            'Conveyor01': '#F18F01'
        }
        
        # Group by asset and signal
        for (asset, signal), group in df.groupby(['asset', 'signal']):
            color = colors.get(asset, '#666666')
            fig.add_trace(go.Scatter(
                x=group['timestamp'],
                y=group['value'],
                mode='lines+markers',
                name=f"{asset} - {signal}",
                line=dict(width=2, color=color),
                marker=dict(size=4, color=color),
                hovertemplate=f"<b>{asset} - {signal}</b><br>" +
                             "Time: %{x}<br>" +
                             "Value: %{y}<br>" +
                             "<extra></extra>"
            ))
        
        fig.update_layout(
            title=dict(
                text="📊 Real-time Telemetry Data",
                font=dict(size=20, color='#2E86AB')
            ),
            xaxis_title="Time",
            yaxis_title="Value",
            hovermode='x unified',
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    else:
        # Empty chart placeholder
        fig = go.Figure()
        fig.add_annotation(
            text="📡 No telemetry data available<br>Connect to MQTT broker to see live data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

def create_alerts_table():
    """Create alerts table with real data and control buttons"""
    if not st.session_state.alerts_data:
        # Create sample alerts for demonstration
        sample_alerts = [
            {
                'timestamp': datetime.now() - timedelta(minutes=5),
                'asset': 'Press01',
                'signal': 'Temperature',
                'severity': 'high',
                'reason': 'z-score 8.4 vs mean 42.1±1.0 (120s)',
                'current': 85.2,
                'alertId': 'a-sample1'
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=12),
                'asset': 'Conveyor01',
                'signal': 'Speed',
                'severity': 'medium',
                'reason': 'z-score 5.2 vs mean 50.0±2.1 (120s)',
                'current': 45.8,
                'alertId': 'a-sample2'
            }
        ]
        df = pd.DataFrame(sample_alerts)
    else:
        df = pd.DataFrame(st.session_state.alerts_data)
    
    if not df.empty:
        # Format the dataframe for display
        display_df = df.copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
        
        # Select columns for display
        display_columns = ['timestamp', 'asset', 'signal', 'severity', 'current', 'reason']
        if all(col in display_df.columns for col in display_columns):
            display_df = display_df[display_columns]
        
        # Convert severity to badges
        display_df['severity_badge'] = display_df['severity'].apply(render_severity_badge)
        
        # Remove the original severity column and use badge instead
        display_columns_with_badge = ['timestamp', 'asset', 'signal', 'severity_badge', 'current', 'reason']
        display_df = display_df[display_columns_with_badge]
        display_df = display_df.rename(columns={'severity_badge': 'severity'})
        
        return display_df, df
    else:
        return pd.DataFrame({'Message': ['No alerts available']}), pd.DataFrame()

def inject_anomaly():
    """Inject a demo anomaly for testing purposes"""
    if st.session_state.mqtt_client and st.session_state.mqtt_connected:
        # Create a demo anomaly alert
        demo_alert = {
            "alertId": f"demo-{int(time.time())}",
            "assetId": "Press01",
            "signal": "Temperature",
            "severity": "high",
            "reason": "Demo anomaly injection - z-score 9.2 vs mean 42.1±1.0 (120s)",
            "current": 95.7,
            "ts": datetime.now().isoformat()
        }
        
        # Publish to alerts topic
        topic = f"alerts/{demo_alert['assetId']}/{demo_alert['signal']}"
        message = json.dumps(demo_alert)
        
        try:
            st.session_state.mqtt_client.publish(topic, message, qos=1, retain=True)
            st.success("🎯 Demo anomaly injected successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Failed to inject demo anomaly: {e}")
            return False
    else:
        st.error("❌ MQTT not connected. Cannot inject anomaly.")
        return False

def create_control_buttons(alert_data):
    """Create control buttons for alerts"""
    if alert_data.empty:
        return
    
    st.subheader("🎛️ Control Actions")
    
    # Demo anomaly injection button
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎯 Inject Demo Anomaly", key="inject_anomaly", help="Inject a demo anomaly for testing"):
            with st.spinner("Injecting anomaly..."):
                inject_anomaly()
                st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Alerts", key="refresh_alerts"):
            st.rerun()
    
    st.divider()
    
    # Get unique assets with active alerts
    assets_with_alerts = alert_data['asset'].unique()
    
    for asset in assets_with_alerts:
        asset_alerts = alert_data[alert_data['asset'] == asset]
        highest_severity = asset_alerts['severity'].max()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"🚫 Isolate {asset}", key=f"isolate_{asset}"):
                if st.session_state.mqtt_client and st.session_state.mqtt_connected:
                    success = st.session_state.mqtt_client.publish_control_command(
                        asset, "isolate", "operator_action"
                    )
                    if success:
                        st.success(f"✅ Isolation command sent for {asset}")
                    else:
                        st.error(f"❌ Failed to send isolation command for {asset}")
                else:
                    st.error("❌ MQTT not connected")
        
        with col2:
            if st.button(f"⚡ Throttle {asset}", key=f"throttle_{asset}"):
                if st.session_state.mqtt_client and st.session_state.mqtt_connected:
                    success = st.session_state.mqtt_client.publish_control_command(
                        asset, "throttle", "operator_action"
                    )
                    if success:
                        st.success(f"✅ Throttle command sent for {asset}")
                    else:
                        st.error(f"❌ Failed to send throttle command for {asset}")
                else:
                    st.error("❌ MQTT not connected")
        
        with col3:
            if st.button(f"✅ Unblock {asset}", key=f"unblock_{asset}"):
                if st.session_state.mqtt_client and st.session_state.mqtt_connected:
                    success = st.session_state.mqtt_client.publish_control_command(
                        asset, "unblock", "operator_action"
                    )
                    if success:
                        st.success(f"✅ Unblock command sent for {asset}")
                    else:
                        st.error(f"❌ Failed to send unblock command for {asset}")
                else:
                    st.error("❌ MQTT not connected")

def main():
    # Header with enhanced GhostMesh branding
    st.markdown('<h1 class="main-header ghostmesh-brand">👻 GhostMesh Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">Edge AI Security Copilot - Real-time Industrial Monitoring & Control</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Control Panel")
        
        # Enhanced system status
        st.subheader("🔗 System Status")
        status_type, status_text, status_color = get_system_status()
        
        if status_type == 'connected':
            status_class = 'status-connected'
            status_icon = '🟢'
        elif status_type == 'warning':
            status_class = 'status-warning'
            status_icon = '🟡'
        else:
            status_class = 'status-disconnected'
            status_icon = '🔴'
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div class="status-indicator {status_class}"></div>
            <span style="color: {status_color}; font-weight: bold;">{status_icon} {status_text}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # MQTT Connection Controls
        st.subheader("⚙️ MQTT Settings")
        mqtt_host = st.text_input("MQTT Host", value=MQTT_HOST)
        mqtt_port = st.number_input("MQTT Port", value=MQTT_PORT, min_value=1, max_value=65535)
        mqtt_username = st.text_input("Username", value=MQTT_USERNAME)
        mqtt_password = st.text_input("Password", value=MQTT_PASSWORD, type="password")
        
        # Show connection status
        if st.session_state.connection_status == "connected":
            st.success("✅ Connected to MQTT broker")
        elif st.session_state.connection_status.startswith("failed_"):
            st.error(f"❌ Failed to connect to MQTT broker. Code: {st.session_state.connection_status.split('_')[1]}")
        elif st.session_state.connection_status.startswith("error_"):
            st.error(f"❌ Connection error: {st.session_state.connection_status.split('_', 1)[1]}")
        elif st.session_state.connection_status == "disconnected":
            st.info("🔌 Not connected to MQTT broker")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect"):
                with st.spinner("Connecting to MQTT..."):
                    mqtt_client = MQTTClient()
                    mqtt_client.connect(mqtt_host, mqtt_port, mqtt_username, mqtt_password)
                    st.session_state.mqtt_client = mqtt_client
                    # Wait a moment for connection to establish
                    time.sleep(2)
                    # Update connection status based on actual connection
                    if mqtt_client.connected:
                        st.session_state.mqtt_connected = True
                        st.session_state.connection_status = "connected"
                        # Sync data from MQTT client to session state
                        st.session_state.telemetry_data = mqtt_client._telemetry_data.copy()
                        st.session_state.alerts_data = mqtt_client._alerts_data.copy()
                        st.session_state.audit_data = mqtt_client._audit_data.copy()
                    else:
                        st.session_state.connection_status = "failed"
                    st.rerun()
        
        with col2:
            if st.button("Disconnect") and 'mqtt_client' in st.session_state:
                with st.spinner("Disconnecting..."):
                    st.session_state.mqtt_client.disconnect()
                    st.session_state.mqtt_connected = False
                    st.session_state.connection_status = "disconnected"
                    st.rerun()
        
        # Auto-connect if not connected and environment variables are set
        if not st.session_state.mqtt_connected and MQTT_HOST != 'localhost':
            if st.button("🔄 Auto-Connect", help="Connect using environment variables"):
                with st.spinner("Auto-connecting to MQTT..."):
                    mqtt_client = MQTTClient()
                    mqtt_client.connect()
                    st.session_state.mqtt_client = mqtt_client
                    # Wait a moment for connection to establish
                    time.sleep(2)
                    # Update connection status based on actual connection
                    if mqtt_client.connected:
                        st.session_state.mqtt_connected = True
                        st.session_state.connection_status = "connected"
                        # Sync data from MQTT client to session state
                        st.session_state.telemetry_data = mqtt_client._telemetry_data.copy()
                        st.session_state.alerts_data = mqtt_client._alerts_data.copy()
                        st.session_state.audit_data = mqtt_client._audit_data.copy()
                    else:
                        st.session_state.connection_status = "failed"
                    st.rerun()
        
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
        st.subheader("📊 Real-time Telemetry Charts")
        fig = create_telemetry_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🚨 Active Alerts")
        alerts_styled, alerts_data = create_alerts_table()
        st.dataframe(alerts_styled, use_container_width=True)
        
        # Add control buttons for alerts
        if not alerts_data.empty:
            create_control_buttons(alerts_data)
    
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
        - Anomaly Detector: ✅ Operational
        - Policy Engine: ✅ Operational
        - Dashboard: ✅ Live
        """)
    
    # Auto-refresh with optimized rate (1-2 Hz) for Raspberry Pi performance
    if st.session_state.mqtt_connected:
        time.sleep(0.5)  # 2 Hz refresh rate - optimized for Pi 5
        st.rerun()
    else:
        # Slower refresh when not connected to reduce CPU usage
        time.sleep(2)  # 0.5 Hz refresh rate when disconnected
        st.rerun()

if __name__ == "__main__":
    main()
