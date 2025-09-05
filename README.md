# IoT Environmental Monitoring Platform for Smart Cities  
*A component of the Saintgits–CCU “Integrated Command & Control Centre for Sustainable Smart Cities”*  

This repository contains the source code for a full-stack IoT platform for real-time environmental monitoring of air and water quality.  

This system serves as the foundational data collection and visualization layer for the **world's first Cross-Nation Federated AI Platform**, a collaborative initiative between **Saintgits College of Engineering, India**, and **National Chung Cheng University (CCU), Taiwan**.  

The platform was officially inaugurated on **August 25, 2025**, marking a milestone in international academic cooperation for sustainable smart city solutions.  

---

## Live Dashboard Preview  
The web dashboard provides a real-time, at-a-glance view of sensor data from multiple nodes, visualizing both live metrics and historical trends.  

---

## Core Features  
- Real-Time Data Visualization – Live gauges and charts update automatically.  
- Multi-Node Support – Ingests and processes data from diverse sensor nodes.  
- Historical Data Querying – Dedicated history page for searching past readings.  
- Decoupled & Robust Architecture – Independent MQTT ingestion ensures reliability.  
- Flexible Data Ingestion – Listener accepts varied JSON payloads for easy sensor integration.  
- Efficient Database Schema – Normalized MySQL design for device metadata + time-series data.  

---

## Technology Stack  
- **MQTT Broker** – Mosquitto  
- **Backend Services** – Python (Flask, Paho-MQTT)  
- **Database** – MySQL  
- **Frontend Dashboard** – HTML, JavaScript, Chart.js / D3.js  

---

## System Architecture  
The project follows a classic IoT data pipeline.  

<details>
<summary>Click to view Architecture Diagram</summary>

```mermaid
graph TD;
    A[Sensor Nodes/ESP32] -- JSON over MQTT --> B(MQTT Broker);
    B -- Pub/Sub --> C{Python MQTT Listener};
    C -- SQL INSERT --> D[(MySQL Database)];
    D -- SQL SELECT --> E[Flask Backend API];
    E -- REST API (JSON) --> F((Live Web Dashboard));
