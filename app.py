# File: app.py (FINAL, INTEGRATED & MULTI-NODE VERSION)

from flask import Flask, jsonify, render_template, request
import mysql.connector
from mysql.connector import errorcode
import datetime # Import the datetime library for formatting

# --- CONFIGURATION ---
DB_HOST = "localhost"
DB_NAME = "unified_sensor_db"
DB_USER = "root"
DB_PASS = "saintgits" # Your real password

# MODIFIED: Updated device IDs and made 'water' a list of all water-related nodes
DEVICE_MAP = {
    'air': 'sensor_node_01',
    'water': ['sensor_node_02', 'sensor_node_03'] # A list of ALL water nodes
}

app = Flask(__name__)

def get_db_connection():
    # This function is correct and doesn't need changes.
    try:
        conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# --- AIR QUALITY API Endpoints ---
# This section is unchanged as it works perfectly for the single air sensor.
@app.route('/get_latest_data')
def get_latest_data():
    sql = """
        SELECT device_id, temperature_c, humidity_pct, pm2_5_ug_m3, pm10_ug_m3, 
               wind_speed_ms, created_at
        FROM readings
        WHERE device_id = %s ORDER BY created_at DESC LIMIT 1;
    """
    params = (DEVICE_MAP['air'],)
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        reading = cursor.fetchone()
        
        if reading and isinstance(reading.get('created_at'), datetime.datetime):
            reading['time_utc'] = reading['created_at'].strftime('%Y-%m-%dT%H:%M:%S')

        return jsonify([reading] if reading else [])
    except Exception as e:
        print(f"Database fetch error: {e}")
        return jsonify({"error": "Could not retrieve data"}), 500
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

@app.route('/get_history')
def get_history():
    sql = """
        SELECT temperature_c, humidity_pct, pm2_5_ug_m3, pm10_ug_m3, wind_speed_ms,
               created_at
        FROM readings
        WHERE device_id = %s ORDER BY created_at DESC LIMIT 20;
    """
    params = (DEVICE_MAP['air'],)
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        history = list(reversed(cursor.fetchall()))
        
        for row in history:
            if isinstance(row.get('created_at'), datetime.datetime):
                row['time_label'] = row['created_at'].strftime('%H:%M:%S')

        return jsonify(history)
    except Exception as e:
        print(f"Database history fetch error: {e}")
        return jsonify({"error": "Could not retrieve history"}), 500
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()


# --- IMPLEMENTED: WATER QUALITY API Endpoints ---
# This section has been upgraded to handle multiple water nodes.
@app.route('/get_latest_water_data')
def get_latest_water_data():
    # IMPLEMENTED: A sophisticated query to get the single latest value for each metric
    # from the relevant water sensors, creating a unified view for the dashboard gauges.
    sql = """
    SELECT 
        (SELECT water_level_cm FROM readings WHERE device_id = 'sensor_node_02' AND water_level_cm IS NOT NULL ORDER BY created_at DESC LIMIT 1) AS water_level_pct,
        (SELECT conductivity_us_cm FROM readings WHERE device_id = 'sensor_node_02' AND conductivity_us_cm IS NOT NULL ORDER BY created_at DESC LIMIT 1) AS conductivity_us_cm,
        (SELECT tds_ppm FROM readings WHERE device_id = 'sensor_node_03' AND tds_ppm IS NOT NULL ORDER BY created_at DESC LIMIT 1) AS tds_ppm,
        (SELECT MAX(created_at) FROM readings WHERE device_id IN ('sensor_node_02', 'sensor_node_03')) AS created_at
    """
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        reading = cursor.fetchone()

        if reading and isinstance(reading.get('created_at'), datetime.datetime):
            reading['time_utc'] = reading['created_at'].strftime('%Y-%m-%dT%H:%M:%S')

        return jsonify([reading] if reading else [])
    except Exception as e:
        print(f"Database fetch error in /get_latest_water_data: {e}")
        return jsonify({"error": "Could not retrieve water data"}), 500
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()


@app.route('/get_water_history')
def get_water_history():
    # IMPLEMENTED: Fetches a combined history from ALL water nodes using the IN clause.
    sql_template = """
        SELECT device_id, water_level_cm AS water_level_pct, salinity_ppt, 
               conductivity_us_cm, tds_ppm, created_at
        FROM readings
        WHERE device_id IN ({}) ORDER BY created_at DESC LIMIT 40; 
    """ # Increased limit to 40 to get a mix of data
    
    water_devices = DEVICE_MAP['water']
    placeholders = ', '.join(['%s'] * len(water_devices))
    sql = sql_template.format(placeholders)
    params = tuple(water_devices)

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        history = list(reversed(cursor.fetchall()))
        
        for row in history:
            if isinstance(row.get('created_at'), datetime.datetime):
                row['time_label'] = row['created_at'].strftime('%H:%M:%S')

        return jsonify(history)
    except Exception as e:
        print(f"Database history fetch error in /get_water_history: {e}")
        return jsonify({"error": "Could not retrieve water history"}), 500
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()


# --- SEARCH Endpoint (Unchanged but will work with all nodes) ---
@app.route('/search')
def search_history():
    query_date = request.args.get('date')
    if not query_date:
        return jsonify({"error": "A date parameter is required."}), 400
    
    sql = """
        SELECT 
            device_id, created_at,
            temperature_c, humidity_pct, pm2_5_ug_m3, pm10_ug_m3, 
            wind_speed_ms, water_level_cm, salinity_ppt, tds_ppm
        FROM readings 
        WHERE DATE(created_at) = %s 
        ORDER BY created_at DESC;
    """
    params = (query_date,)
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        results = cursor.fetchall()

        for row in results:
            if isinstance(row.get('created_at'), datetime.datetime):
                row['time_utc'] = row['created_at'].strftime('%Y-%m-%dT%H:%i:%S')

        return jsonify(results)
    except Exception as e:
        print(f"Database search error: {e}")
        return jsonify({"error": "Could not perform search"}), 500
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()


# --- HTML Page Routes (UNCHANGED) ---
@app.route('/air')
def air_dashboard(): return render_template('air.html')
@app.route('/history')
def history_page(): return render_template('history.html')
@app.route('/water')
def water_dashboard(): return render_template('water.html')
@app.route('/')
def intro_page(): return render_template('intro.html')

if __name__ == '__main__':
    print("🚀 Starting Integrated Dashboard Server (FINAL MULTI-NODE VERSION)...")
    print(f"   Connected to YOUR database: {DB_NAME}")
    app.run(host='0.0.0.0', port=5000, debug=True)