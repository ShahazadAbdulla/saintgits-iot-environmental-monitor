# File: node2_sim.py
# Description: Simulates Sensor Node 2, which measures Water Level and Conductivity.

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
import time
import random

# --- Configuration ---
MQTT_BROKER_IP = "localhost"
MQTT_PORT = 1883
SEND_INTERVAL_SECONDS = 10 # Send data every 10 seconds

# --- Device Details for Node 2 ---
DEVICE_ID = "sensor_node_02"
LATITUDE = 29.5883   # Example location 1
LONGITUDE = 76.5054
MQTT_TOPIC = "iot/data/water_level"

def generate_node2_data():
    """Creates a standardized JSON payload for Node 2."""
    payload = {
        "device_id": DEVICE_ID,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "sensors": {
            # This node's specific measurements
            "water_level_cm": round(random.uniform(50.0, 200.0), 2),
            "conductivity_us_cm": round(random.uniform(500.0, 2500.0), 2),
            
            # All other possible sensor values are null for this device
            "tds_ppm": None,
            "salinity_ppt": None,
            "temperature_c": None,
            "humidity_pct": None,
            "pm2_5_ug_m3": None,
            "pm10_ug_m3": None,
            "wind_speed_ms": None
        }
    }
    return json.dumps(payload) # Convert the dictionary to a valid JSON string

if __name__ == "__main__":
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="level-conductivity-simulator")

    try:
        client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
        print("✅ [Node 2 Simulator] Connected to MQTT Broker.")
        client.loop_start() # Handles network in the background
        
        print(f"🚀 [Node 2 Simulator] Starting simulation for '{DEVICE_ID}'. Press CTRL+C to stop.")
        
        while True:
            message = generate_node2_data()
            result = client.publish(MQTT_TOPIC, message)
            
            if result[0] == 0:
                print(f"\n💧 Published Node 2 Data:\n{message}")
            else:
                print(f"⚠️ [Node 2 Simulator] Failed to publish message.")

            time.sleep(SEND_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n🛑 [Node 2 Simulator] Simulation stopped.")
    except Exception as e:
        print(f"❌ [Node 2 Simulator] A critical error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 [Node 2 Simulator] Disconnected from MQTT Broker.")