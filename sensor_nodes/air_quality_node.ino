#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SDS011.h>   // Library for SDS011
#include <DHT.h>      // Library for DHT11

// ===============================================================
//                          CONFIGURATION
// ===============================================================

// --- Wi-Fi Credentials ---
const char* ssid = "qwerty";        // <<-- CHANGE THIS
const char* password = "12345678";  // <<-- CHANGE THIS

// --- MQTT Broker Details ---
const char* mqtt_server_ip = "broker.hivemq.com";  // Public broker
const int mqtt_port = 1883;

// --- Device-Specific Details ---
const char* DEVICE_ID = "sensor_node_01"; 
const float LATITUDE = 40.7128;   // Example latitude (change to your location)
const float LONGITUDE = -74.0060;
const char* MQTT_TOPIC = "iot/data/air_quality"; 

// ===============================================================

// --- Global Clients ---
WiFiClient espClient;
PubSubClient client(espClient);

long lastMsg = 0;   
const long interval = 10000; // Interval between messages (10s)

// --- Wind Speed Sensor Config ---
const int sensorPin = 34;  // ADC input pin for 4–20mA signal (via resistor)
const float R = 150.0;     // Resistor in ohms
const float VREF = 3.9;    // ESP32 ADC ref voltage
const int ADC_MAX = 4095;  // 12-bit ADC

// --- SDS011 Sensor Config ---
SDS011 sds;  
float pm25, pm10;
int error;
#define SDS_RX 14   // ESP32 pin connected to SDS011 TX
#define SDS_TX 12   // ESP32 pin connected to SDS011 RX

// --- DHT11 Sensor Config ---
#define DHTPIN 15     // GPIO where DHT11 is connected
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- Function Prototypes ---
void setup_wifi();
void reconnect();

void setup() {
  Serial.begin(115200);
  Serial.println("\n\nBooting up Air Quality Node...");

  // Connect WiFi
  setup_wifi();

  // Configure MQTT
  client.setServer(mqtt_server_ip, mqtt_port);
  Serial.println("-> MQTT client configured.");

  // SDS011 init
  sds.begin(SDS_RX, SDS_TX);
  Serial.println("-> SDS011 initialized.");

  // DHT init
  dht.begin();
  Serial.println("-> DHT11 initialized.");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;

    // --- Read windspeed sensor ---
    int adcVal = analogRead(sensorPin);
    float voltage = (adcVal * VREF) / ADC_MAX;
    float current_mA = (voltage / R) * 1000.0;   // I = V/R, in mA
    float windSpeed = ((current_mA - 3.7) / 16.3) * 70.0; // map 4–20mA to 0–70 m/s
    if (windSpeed < 0) windSpeed = 0;

    // --- Read SDS011 sensor ---
    float pm25_val = NAN;
    float pm10_val = NAN;
    error = sds.read(&pm25, &pm10);
    if (!error) {
      pm25_val = pm25;
      pm10_val = pm10;
      //Serial.printf("-> SDS011: PM2.5=%.2f µg/m³, PM10=%.2f µg/m³\n", pm25_val, pm10_val);
    } else {
      Serial.println("!!! SDS011 read error");
    }

    // --- Read DHT11 sensor ---
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("!!! DHT11 read error");
    } else {
      //Serial.printf("-> DHT11: Temp=%.1f °C, Humidity=%.1f %%\n", temperature, humidity);
    }

    // --- BUILD JSON PAYLOAD ---
    StaticJsonDocument<512> doc;

    doc["device_id"] = DEVICE_ID;
    doc["latitude"] = LATITUDE;
    doc["longitude"] = LONGITUDE;

    JsonObject sensorReadings = doc.createNestedObject("sensors");
    sensorReadings["temperature_c"] = isnan(temperature) ? 0 : temperature;
    sensorReadings["humidity_pct"]  = isnan(humidity) ? 0 : humidity;
    sensorReadings["pm2_5_ug_m3"] = isnan(pm25_val) ? 0 : pm25_val;
    sensorReadings["pm10_ug_m3"]  = isnan(pm10_val) ? 0 : pm10_val;
    sensorReadings["wind_speed_ms"] = round(windSpeed * 100.0) / 100.0; // 2 decimals
    sensorReadings["water_level_cm"] = nullptr;
    sensorReadings["salinity_ppt"] = nullptr;

    char char_payload[512];
    serializeJson(doc, char_payload);

    // --- Publish to MQTT ---
    Serial.println("--------------------");
    Serial.print("Publishing message to topic: ");
    Serial.println(MQTT_TOPIC);
    Serial.println(char_payload);
    
    client.publish(MQTT_TOPIC, char_payload);
  }
}

void setup_wifi() {
  delay(10);
  Serial.print("-> Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (retries++ >= 20) { 
      Serial.println("\n!!! ERROR: WiFi failed, rebooting...");
      ESP.restart(); 
    }
  }
  Serial.println("\n-> WiFi connected!");
  Serial.print("   IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("-> Attempting MQTT connection...");
    if (client.connect(DEVICE_ID)) {
      Serial.println(" connected!");
    } else {
      Serial.print(" failed, rc=");
      Serial.print(client.state());
      Serial.println(" | Retrying in 5s...");
      delay(5000);
    }
  }
}
