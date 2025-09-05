-- This command will completely delete your existing database, including all tables and data,
-- allowing you to start fresh with the correct new structure.
DROP DATABASE IF EXISTS unified_sensor_db;

-- Re-create the database.
CREATE DATABASE unified_sensor_db;

-- Switch to the new database so the following commands work on it.
USE unified_sensor_db;


-- Table 1: Stores metadata about each unique sensor device.
-- This structure is complete and correct.
CREATE TABLE devices (
    device_id VARCHAR(255) PRIMARY KEY,
    device_type VARCHAR(50) NULL,
    friendly_name VARCHAR(100) NULL,
    latitude DECIMAL(9, 6) NULL,
    longitude DECIMAL(10, 6) NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP
);


-- Table 2: Stores the actual time-series data from all sensors.
-- This is the new, fully updated version with all necessary columns.
CREATE TABLE readings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(255) NOT NULL,
    
    -- Air Quality Sensor Columns
    temperature_c DECIMAL(5, 2) NULL,
    humidity_pct DECIMAL(5, 2) NULL,
    pm2_5_ug_m3 DECIMAL(6, 2) NULL,
    pm10_ug_m3 DECIMAL(6, 2) NULL,
    wind_speed_ms DECIMAL(5, 2) NULL,
    
    -- Water Quality Sensor Columns
    water_level_cm DECIMAL(7, 2) NULL,
    salinity_ppt DECIMAL(5, 2) NULL,
    conductivity_us_cm DECIMAL(8, 2) NULL, -- This column was missing
    tds_ppm DECIMAL(7, 2) NULL,            -- This column was missing
    
    -- Timestamp and the critical link to the 'devices' table
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);