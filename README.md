IoT Environmental Monitoring Platform for Smart Cities
A component of the Saintgits-CCU "Integrated Command & Control Centre for Sustainable Smart Cities"
This repository contains the source code for a full-stack IoT platform for real-time environmental monitoring of air and water quality. This system serves as the foundational data collection and visualization layer for the world's first Cross-Nation Federated AI Platform, a collaborative initiative between Saintgits College of Engineering, India, and National Chung Cheng University (CCU), Taiwan.

The platform was officially inaugurated on August 25, 2025, marking a significant milestone in international academic cooperation for developing sustainable smart city solutions.

📊 Live Dashboard Preview
The web dashboard provides a real-time, at-a-glance view of sensor data from multiple nodes, visualizing both live metrics and historical trends.

✨ Core Features
📈 Real-Time Data Visualization: Live gauges and charts update automatically to show the latest sensor readings.

📡 Multi-Node Support: Ingests and processes data from different types of sensor nodes simultaneously.

📂 Historical Data Querying: A dedicated history page allows users to search and view all sensor readings from a specific date.

⚙️ Decoupled & Robust Architecture: An independent MQTT ingestion service ensures reliable data collection.

🔌 Flexible Data Ingestion: The listener can handle varied JSON payloads, making it easy to add new sensor types without backend changes.

🗃️ Efficient Database Schema: Uses a normalized MySQL schema to efficiently store device metadata and time-series data.

🛠️ Technology Stack
🏗️ System Architecture
The project follows a classic and effective IoT data pipeline.

<details>
<summary>Click to view Architecture Diagram</summary>

graph TD;
    A[Sensor Nodes/ESP32] -- JSON over MQTT --> B(MQTT Broker);
    B -- Pub/Sub --> C{Python MQTT Listener};
    C -- SQL INSERT --> D[(MySQL Database)];
    D -- SQL SELECT --> E[Flask Backend API];
    E -- REST API (JSON) --> F((Live Web Dashboard));

</details>

Sensor Nodes (Implied): IoT devices publish environmental data as JSON payloads to an MQTT broker.

MQTT Broker: A central message bus (e.g., Mosquitto) that routes messages.

Python MQTT Listener (mqtt_listener.py): A persistent background service that subscribes to the broker, receives data, and stores it in the database.

MySQL Database (db.sql): Stores all device information and sensor readings.

Flask Web Server (app.py): Provides a RESTful API to query the database and serves the HTML dashboard pages.

Web Dashboard (HTML/JS files): The user-facing interface that fetches data from the Flask API and visualizes it.

🚀 Getting Started
Follow these steps to set up and run the project locally.

Prerequisites
Python 3.x

MySQL Server

An MQTT Broker (e.g., Mosquitto) running on its default port (1883).

Installation
Clone the repository:

git clone [https://github.com/your-username/iot-environmental-monitor.git](https://github.com/your-username/iot-environmental-monitor.git)
cd iot-environmental-monitor

Set up the database:

Open your MySQL client (e.g., MySQL Workbench, command line).

Run the db.sql script provided in the repository. This will create the unified_sensor_db database and all necessary tables.

Important: Update the database credentials (DB_HOST, DB_NAME, DB_USER, DB_PASS) in app.py and mqtt_listener.py to match your local MySQL setup.

Install Python dependencies:

Run the installer script (on Windows) or use pip directly:

# Double-click 'install_dependencies.bat' on Windows, or run:
pip install -r requirements.txt

Running the Application
You need to run two components in separate terminals.

Terminal 1: Start the MQTT Listener
This service must be running to collect data.

python mqtt_listener.py

You should see a confirmation that it has connected to the MQTT broker and the database.

Terminal 2: Start the Flask Web Server
This serves the dashboard.

python app.py

The server will start. You can now access the dashboard at http://localhost:5000.

Acknowledgements
This project is a proud outcome of the international collaboration between the AI Center at National Chung Cheng University, Taiwan, led by Prof. Dr. Pao-Ann Hsiung, and Saintgits College of Engineering, India.
