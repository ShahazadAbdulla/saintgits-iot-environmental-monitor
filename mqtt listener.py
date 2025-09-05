# File: mqtt_to_mysql.py
# Version: 4.1 (Production Ready - Relational Model)
# Description: Subscribes to MQTT, upserts device metadata, and dynamically inserts 
#              time-series readings into a normalized, multi-table database.

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import mysql.connector
from mysql.connector import Error
import json
import os
import time

# --- Configuration ---
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'YourNewPassword') # Default password if not set

MQTT_BROKER_IP = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_TO_SUBSCRIBE = "iot/data/#"

DB_CONFIG = {
    'host': 'localhost',
    'database': 'unified_sensor_db',
    'user': 'root',
    'password': 'saintgits'
}

# (The db_connect and on_connect functions are identical to the previous version)
def db_connect(config):
    """ Connect to the MySQL database with retry logic. """
    conn = None
    attempt = 1
    while not conn and attempt <= 5:
        try:
            conn = mysql.connector.connect(**config)
            if conn.is_connected():
                print("✅ MySQL connection successful.")
                return conn
        except Error as e:
            print(f"⚠️ MySQL connection error (Attempt {attempt}/5): {e}")
            time.sleep(5)
            attempt += 1
    return None

def on_connect(client, userdata, flags, rc, properties=None):
    """ Callback for when the client connects to the MQTT broker. """
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC_TO_SUBSCRIBE)
        print(f"👂 Subscribed to topic: {MQTT_TOPIC_TO_SUBSCRIBE}")
    else:
        print(f"❌ Failed to connect to MQTT Broker, return code {rc}\n")


# --- THIS IS THE NEW, UPGRADED on_message FUNCTION ---
def on_message(client, userdata, msg):
    """ Callback for when a PUBLISH message is received. Handles relational data insertion. """
    conn = userdata['db_conn']
    print(f"\n📩 Message received-> Topic: {msg.topic}")
    
    try:
        payload_str = msg.payload.decode()
        data = json.loads(payload_str)
        
        device_id = data.get('device_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        sensor_readings = data.get('sensors', {})
        
        if not device_id or not isinstance(sensor_readings, dict):
            print("❌ Error: Invalid data format. 'device_id' and 'sensors' object required. Ignoring.")
            return

        cursor = conn.cursor()

        # Step 1: UPSERT device metadata into the 'devices' table.
        # This registers the device or updates its location/last_seen time.
        sql_upsert_device = """
            INSERT INTO devices (device_id, latitude, longitude)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                latitude = VALUES(latitude), 
                longitude = VALUES(longitude),
                last_seen = CURRENT_TIMESTAMP;
        """
        cursor.execute(sql_upsert_device, (device_id, latitude, longitude))
        
        # Step 2: Dynamically prepare the INSERT for the 'readings' table.
        # This is the magic that handles any type of sensor.
        columns = ['device_id']
        values = [device_id]
        
        # Define a whitelist of all possible valid sensor keys to prevent junk data
        allowed_keys = [
            'temperature_c', 'humidity_pct', 'pm2_5_ug_m3', 'pm10_ug_m3',
            'wind_speed_ms', 'water_level_cm', 'salinity_ppt',
            'conductivity_us_cm', 'tds_ppm' # <-- ADD THESE TWO KEYS
        ]
        
        for key, value in sensor_readings.items():
            if key in allowed_keys and value is not None:
                columns.append(key)
                values.append(value)
        
        # Only proceed if we have at least one valid sensor reading
        if len(columns) > 1:
            placeholders = ', '.join(['%s'] * len(values))
            sql_insert_reading = f"INSERT INTO readings ({', '.join(columns)}) VALUES ({placeholders});"
            
            cursor.execute(sql_insert_reading, tuple(values))
            print(f"✔️ Successfully processed & stored data for device: {device_id}")
        else:
            print(f"ℹ️ Message from {device_id} contained no valid sensor readings to store.")

        conn.commit()
        cursor.close()

    except json.JSONDecodeError:
        print(f"❌ Error: Received message is not valid JSON. Ignoring.\nPayload: {msg.payload.decode()}")
    except Error as e:
        if e.errno == mysql.connector.errorcode.CR_SERVER_GONE_ERROR:
            print("⚠️ MySQL server connection lost. Reconnecting...")
            userdata['db_conn'] = db_connect(DB_CONFIG)
            if userdata['db_conn']:
                print("✅ Reconnected to MySQL.")
            else:
                print("❌ Failed to reconnect to MySQL. Shutting down.")
                client.loop_stop()
        else:
            print(f"❌ Database insertion error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == '__main__':
    # (The __main__ block is identical to the previous version)
    db_connection = db_connect(DB_CONFIG)
    if db_connection is None:
        print("Could not connect to the database. Exiting.")
        exit()

    client_userdata = {'db_conn': db_connection}
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="relational-ingestion-service", userdata=client_userdata)
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
        print("🚀 MQTT Ingestion Service started. Waiting for messages...")
        client.loop_forever()
    except ConnectionRefusedError:
        print("\n❌ Connection to MQTT Broker was refused. Is Mosquitto running?")
    except Exception as e:
        print(f"\n❌ A critical error occurred: {e}")