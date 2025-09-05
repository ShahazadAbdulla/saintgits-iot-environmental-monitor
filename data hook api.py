from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import re
import os

# --- Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'unified_sensor_db',
    'user': 'root',
    'password': 'saintgits' # Directly set your password here
}

app = Flask(__name__)

def query_db(query, args=()):
    """ Helper function to query MySQL and return results as dictionaries. """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, args)
        results = cursor.fetchall()
        
        # QOL: Clean up data types for clean JSON output
        for row in results:
            for key, value in row.items():
                if isinstance(value, bytes):
                    row[key] = value.decode('utf-8')
        
        return results
    except Error as e:
        print(f"❌ Database query error: {e}")
        return None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/devices', methods=['GET'])
def get_devices():
    """ NEW ENDPOINT: Get a list of all registered sensor devices. """
    devices = query_db("SELECT * FROM devices ORDER BY last_seen DESC;")
    if devices is not None:
        return jsonify(devices)
    else:
        return jsonify({"error": "Failed to retrieve device data."}), 500

@app.route('/readings', methods=['GET'])
def get_readings():
    """ UPGRADED ENDPOINT: Get readings, now JOINed with device metadata. """
    
    query_params = []
    # QOL: Base query now uses aliases for clarity (r for readings, d for devices)
    base_query = """
        SELECT r.*, d.friendly_name, d.device_type, d.latitude, d.longitude 
        FROM readings r
        LEFT JOIN devices d ON r.device_id = d.device_id
    """
    where_clauses = []

    # Filtering by device_id (exact match on the readings table)
    device_id = request.args.get('device_id')
    if device_id:
        where_clauses.append("r.device_id = %s")
        query_params.append(device_id)
        
    # Filtering by date range
    start_date = request.args.get('start_date')
    if start_date:
        where_clauses.append("r.created_at >= %s")
        query_params.append(start_date)
    end_date = request.args.get('end_date')
    if end_date:
        where_clauses.append("r.created_at <= %s")
        query_params.append(f"{end_date} 23:59:59")
        
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Sorting (whitelisted to prevent injection)
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'DESC')
    allowed_sort_columns = ['id', 'device_id', 'created_at'] # We sort by columns on the readings table
    if sort_by in allowed_sort_columns and order.upper() in ['ASC', 'DESC']:
        base_query += f" ORDER BY r.{sort_by} {order.upper()}"

    # Limiting results (sanitized)
    limit = request.args.get('limit', '100')
    if limit.isdigit() and int(limit) > 0:
        base_query += f" LIMIT {int(limit)}"
        
    # --- Execute query and return ---
    readings = query_db(base_query, tuple(query_params))
    
    if readings is not None:
        return jsonify(readings)
    else:
        return jsonify({"error": "Failed to retrieve reading data.", "query": base_query}), 500

if __name__ == '__main__':
    print("🚀 Starting ADVANCED RELATIONAL API server...")
    print("📡 Devices endpoint: http://10.239.206.235:5002/devices")
    print("📡 Readings endpoint: http://10.239.206.235:5002/readings")
    app.run(host='0.0.0.0', port=5002)