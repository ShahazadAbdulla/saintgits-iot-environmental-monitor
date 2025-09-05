IoT Environmental Monitoring Platform for Smart Cities
A component of the Saintgits-CCU "Integrated Command & Control Centre for Sustainable Smart Cities"
This repository contains the source code for a full-stack IoT platform for real-time environmental monitoring of air and water quality. This system serves as the foundational data collection and visualization layer for the world's first Cross-Nation Federated AI Platform, a collaborative initiative between Saintgits College of Engineering, India, and National Chung Cheng University (CCU), Taiwan.

The platform was officially inaugurated on August 25, 2025, marking a significant milestone in international academic cooperation for developing sustainable smart city solutions.

📊 Live Dashboard Preview
The web dashboard provides a real-time, at-a-glance view of sensor data from multiple nodes, visualizing both live metrics and historical trends.

✨ Core Features
Real-Time Data Visualization: Live gauges and charts update automatically to show the latest sensor readings for air and water quality.

Multi-Node Support: The system is designed to ingest data from different types of sensor nodes simultaneously.

Historical Data Querying: A dedicated history page allows users to search for and view all sensor readings from a specific date, organized by node.

Decoupled & Robust Architecture: An independent MQTT ingestion service ensures reliable data collection, even if the web server is offline or restarting.

Flexible Data Ingestion: The listener can handle varied JSON payloads, making it easy to add new sensor types without backend code changes.

Efficient Database Schema: Uses a normalized MySQL schema to efficiently store device metadata and high-frequency time-series data.

🛠️ Technology Stack
Backend: Python, Flask

Data Ingestion: Paho-MQTT

Database: MySQL

Frontend: HTML, CSS, JavaScript

Charting Library: Chart.js

Protocols: MQTT

⚙️ System Architecture
The project follows a classic and effective IoT data pipeline:

Sensor Nodes (Implied): IoT devices (like ESP32s) publish environmental data as JSON payloads to an MQTT broker.

MQTT Broker: A central message bus (like Mosquitto) that routes messages from publishers to subscribers.

Python MQTT Listener (mqtt_listener.py): A persistent background service that subscribes to the MQTT broker, receives the data, and stores it in the MySQL Database.

MySQL Database: Stores all device information and sensor readings.

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

Important: Make sure the database user, password, and host in all .py files match your MySQL setup.

Install Python dependencies:

Run the install_dependencies.bat script (on Windows) or install manually using pip:

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

The server will start, and you can access the dashboard at http://localhost:5000.

Acknowledgements
This project is a proud outcome of the international collaboration between the AI Center at National Chung Cheng University, Taiwan, led by Prof. Dr. Pao-Ann Hsiung, and Saintgits College of Engineering, India.
