<h1 align="center" id="title">IoT Environmental Monitoring Platform for Smart Cities</h1>

<p align="center">
  <img src="https://socialify.git.ci/siddoit/saintgits-iot-environmental-monitor/image?custom_description=A+full-stack+IoT+platform+for+real-time+environmental+monitoring&description=1&forks=1&language=1&name=1&pattern=Transparent&stargazers=1&theme=Auto" alt="project-image">
</p>

<p id="description" align="center">
  A full-stack IoT system designed to collect, store, and visualize real-time air and water quality data from multiple sensor nodes.  
  This platform serves as the foundational data layer for the Saintgits-CCU “Integrated Command & Control Centre for Sustainable Smart Cities,” an international research initiative between India and Taiwan.  
</p>

---

<h2>Project Screenshots</h2>

<p align="center">
  <img src="assets/dashboard.png" alt="project-screenshot" width="900">
</p>

---

<h2>Features</h2>

<ul>
  <li>Real-Time Data Visualization – The dashboard displays live data using gauges and line charts, automatically refreshing every few seconds.</li>
  <li>Multi-Node Support – Ingests and processes data from diverse sensor nodes simultaneously, with dedicated dashboards for air and water quality.</li>
  <li>Historical Data Querying – A history page allows users to select a date and retrieve all sensor readings, organized neatly in tables by sensor node.</li>
  <li>Decoupled & Robust Architecture – MQTT ingestion runs as an independent service, ensuring uninterrupted data collection regardless of web server status.</li>
  <li>Flexible Data Ingestion – The listener accepts varied JSON payloads, making it easy to integrate new sensors without modifying backend logic.</li>
  <li>Efficient Database Schema – Normalized MySQL schema separates device metadata from high-frequency time-series data for performance and integrity.</li>
</ul>

---

<h2>System Architecture</h2>

<details>
<summary>Click to view Architecture Diagram</summary>

```graph TD;
    A[Sensor Nodes/ESP32] -- JSON over MQTT --> B(MQTT Broker);
    B -- Pub/Sub --> C{Python MQTT Listener};
    C -- SQL INSERT --> D[(MySQL Database)];
    D -- SQL SELECT --> E[Flask Backend API];
    E -- REST API (JSON) --> F((Live Web Dashboard));
```
</details> <p> <b>Components:</b><br> • Sensor Nodes: IoT devices publishing JSON payloads via MQTT<br> • MQTT Broker: Central message bus (e.g., Mosquitto)<br> • Python MQTT Listener (<code>mqtt_listener.py</code>): Parses and stores data in MySQL<br> • MySQL Database (<code>db.sql</code>): Stores metadata and sensor readings<br> • Flask API (<code>app.py</code>): Provides REST endpoints and serves dashboards<br> • Web Dashboard: HTML/JS interface for visualization<br> </p>


<h2>Installation Steps</h2> <p><b>1. Clone the Repository</b></p>

```
git clone https://github.com/your-username/iot-environmental-monitor.git
cd iot-environmental-monitor
```
<p><b>2. Set Up the Database</b></p> <p> Open your MySQL client (Workbench or CLI). Execute <code>db.sql</code> to create the <code>unified_sensor_db</code> database and tables. Update database credentials (<code>DB_HOST</code>, <code>DB_NAME</code>, <code>DB_USER</code>, <code>DB_PASS</code>) in <code>app.py</code> and <code>mqtt_listener.py</code>. </p> <p><b>3. Install Python Dependencies</b></p>

```
# Windows installer
./install_dependencies.bat  

# Or manually
pip install -r requirements.txt
```
<p><b>4. Run the Application</b></p>

Terminal 1 – Start MQTT Listener
```
python mqtt_listener.py
```
Terminal 2 – Start Flask Server
```
python app.py
```
Access dashboard at: http://localhost:5000
<h2>Built With</h2> <ul> <li>Backend: Python (Flask, Paho-MQTT)</li> <li>Database: MySQL</li> <li>Frontend: HTML, CSS, JavaScript (Chart.js)</li> <li>Protocol: MQTT</li> </ul>
<h2>Acknowledgements</h2> <p> This achievement was possible only through immense collaboration and guidance. </p> <p> <b>Special thanks to:</b><br> • Prof. Dr. Pao-Ann Hsiung (CCU)<br> • Dr. Yang Lung-Jieh<br> • Delegation from the Taipei Economic and Cultural Center in India </p> <p> <b>Saintgits Team:</b><br> • Database, Server & Dashboards – Sidharth Sajith, Shahazad Abdulla, Govind Krishna C, Tharun Oommen Jacob<br> • Air Quality Node – Nakul Krishna Ajayan, Abin Abraham, Abhishek P J, Tom Toms<br> • Water Level & Salinity Node – Rishikesh R, Elena Elizabeth Cherian<br> • Drinking Water Quality Node – Emil Phil Vinod </p> <p> <b>Faculty Mentors:</b><br> Nishant Sir, Jyothish Sir, Dr. Pradeep Chandrasekhar, and many others for their constant support and guidance. </p>
<h2>License</h2>

This project is licensed under the MIT License.

---
