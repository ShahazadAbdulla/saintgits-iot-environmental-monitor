monitor ---
  Serial.println("-------------------------");
  Serial.print("Distance to Water: "); Serial.print(distance_to_water_cm); Serial.println(" cm");
  Serial.print("Calculated Water Level: "); Serial.print(water_level_cm); Serial.println(" cm");
  Serial.print("Salinity: "); Serial.print(salinity_ppt); Serial.println(" ppt");
  Serial.print("LED State: "); Serial.println(digitalRead(LED_BUILTIN) == HIGH ? "ON" : "OFF");
  Serial.print("Published to MQTT: "); Serial.println(jsonBuffer);
  
  delay(readingInterval);
}#include <Arduino.h>
#include "DFRobot_EC10.h"
#include <EEPROM.h>

// Libraries for WiFi, MQTT, and JSON
#include <WiFi.h>
#include "PubSubClient.h"
#include "ArduinoJson.h"

/*
 * ====================================================================================
 * COMBINED SKETCH for Salinity, Water Level, and Local LED Indicator
 * ------------------------------------------------------------------------------------
 * This sketch merges two functionalities:
 * 1. Reads Salinity (DFRobot EC10) and Water Level (Ultrasonic), then publishes
 *    the data to an MQTT broker in JSON format.
 * 2. Controls the ESP32's built-in LED based on the distance measured by the
 *    ultrasonic sensor (turns ON if distance > 25cm).
 * ====================================================================================
 */

// ======================= CONFIGURATION =======================
// --- WiFi Settings ---
const char* ssid = "SAINTGITS";
const char* password = "saintgitswifi";

// --- MQTT Broker Settings ---
const char* mqtt_server = "10.05.40.201";
const int   mqtt_port = 1883;
const char* mqtt_topic = "iot/data/water_level";
const char* device_id = "sensor_node_02";

// ====================== SENSOR & TIMING ======================
// --- EC Sensor ---
DFRobot_EC10 ec;
float voltage, ecValue;
float temperature = 25;
#define EC_PIN 34

// --- Water Level Sensor (Using Pins from your second sketch) ---
#define ULTRASONIC_TRIG_PIN 5
#define ULTRASONIC_ECHO_PIN 18
const float SENSOR_MOUNT_HEIGHT_CM = 80; // Your tank/container height from the sensor

// --- Onboard LED for local status ---
#define LED_BUILTIN 2 // Most ESP32s use GPIO 2 for the onboard LED

// --- Timing ---
const long readingInterval = 5000; // Reads sensors and publishes every 5 seconds.

// ===================== CLIENT INITIALIZATION ==================
WiFiClient espClient;
PubSubClient client(espClient);

// MODIFICATION: To get both distance AND level easily, we'll use a small helper struct.
struct WaterMeasurement {
  float distance_cm;
  float level_cm;
};

// MODIFICATION: This function now returns the struct with both values.
WaterMeasurement readWaterSensor() {
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

  long duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000); // 30ms timeout
  float distance = duration * 0.0343 / 2.0;
  Serial.print("distance: ");
  Serial.println(distance);
  float level = SENSOR_MOUNT_HEIGHT_CM - distance;

  if (level < 0) {
    level = 0;
  }
  
  // Return both values neatly packaged
  return {distance, level};
}

void setup_wifi() {
  delay(10); Serial.println(); Serial.print("Connecting to "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(""); Serial.println("WiFi connected"); Serial.print("IP address: "); Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(device_id)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Configure pin modes for all components
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT); // <-- ADDED from your second sketch

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  ec.begin();
  Serial.println("Starting measurements: Salinity, Water Level, and LED Control.");
}

void loop() {
  // This code will now run continuously without stopping.

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // --- Take Sensor Readings ---
  // 1. Read Salinity
  voltage = analogRead(EC_PIN) / 4095.0 * 3300;
  ecValue = ec.readEC(voltage, temperature);
  float salinity_ppt = (ecValue * 0.55);

  // 2. Read Water Level and Distance
  WaterMeasurement measurement = readWaterSensor();
  float water_level_cm = measurement.level_cm;
  float distance_to_water_cm = measurement.distance_cm; // <-- Now we have distance!

  // --- Control LED based on Distance ---
  // This logic is merged from your second sketch.
  if (distance_to_water_cm > 25) {
    digitalWrite(LED_BUILTIN, HIGH); // Turn the LED ON
  } else {
    digitalWrite(LED_BUILTIN, LOW);  // Turn the LED OFF
  }

  // --- Create JSON Payload ---
  StaticJsonDocument<384> jsonDoc;
  jsonDoc["device_id"] = device_id;
  JsonObject sensors = jsonDoc.createNestedObject("sensors");
  sensors["water_level_cm"] = water_level_cm;
  sensors["salinity_ppt"] = salinity_ppt;

  // --- Serialize and Publish ---
  char jsonBuffer[384];
  serializeJson(jsonDoc, jsonBuffer);
  client.publish(mqtt_topic, jsonBuffer);
  
  // --- Debug output to Serial M
