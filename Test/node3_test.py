# File: node3_sim.py
# Description: Simulates Sensor Node 3, which measures Total Dissolved Solids (TDS).

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
import time
import random

# --- Configuration ---
MQTT_BROKER_IP = "localhost"
MQTT_PORT = 1883
SEND_INTERVAL_SECONDS = 13 # Use a slightly different interval to make the data more varied

# --- Device Details for Node 3 ---
DEVICE_ID = "sensor_node_03"
LATITUDE = 29.6000   # Slightly different location
LONGITUDE = 76.5100
MQTT_TOPIC = "sensors/environment/update"

def generate_node3_data():
    """Creates a standardized JSON payload for Node 3."""
    payload = {
        "device_id": DEVICE_ID,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "sensors": {
            # This node's specific measurement
            "tds_ppm": round(random.uniform(250.0, 1500.0), 2),
            
            # All other possible sensor values are null for this device
            "water_level_cm": None,
            "conductivity_us_cm": None,
            "salinity_ppt": None,
            "temperature_c": None,
            "humidity_pct": None,
            "pm2_5_ug_m3": None,
            "pm10_ug_m3": None,
            "wind_speed_ms": None
        }
    }
    return json.dumps(payload)

if __name__ == "__main__":
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="tds-simulator")

    try:
        client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
        print("✅ [Node 3 Simulator] Connected to MQTT Broker.")
        client.loop_start()
        
        print(f"🚀 [Node 3 Simulator] Starting simulation for '{DEVICE_ID}'. Press CTRL+C to stop.")
        
        while True:
            message = generate_node3_data()
            result = client.publish(MQTT_TOPIC, message)
            
            if result[0] == 0:
                print(f"\n🧪 Published Node 3 Data:\n{message}")
            else:
                print(f"⚠️ [Node 3 Simulator] Failed to publish message.")

            time.sleep(SEND_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n🛑 [Node 3 Simulator] Simulation stopped.")
    except Exception as e:
        print(f"❌ [Node 3 Simulator] A critical error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 [Node 3 Simulator] Disconnected from MQTT Broker.")