#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ---------- WiFi ----------
#define WIFI_SSID "Bong"
#define WIFI_PASS "Runner555"

// ---------- MQTT ----------
#define MQTT_SERVER "10.166.32.26"  // replace with your broker IP
#define MQTT_PORT 1883
#define MQTT_TOPIC "iot/data/water_quality"

// ---------- TDS Sensor Setup ----------
#define TdsSensorPin 34
const int VREF = 3300;    // mV
const int SCOUNT = 30;    // sample count
int analogBuffer[SCOUNT];
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0;
int copyIndex = 0;
float averageVoltage = 0;
float tdsValue = 0;

// ---------- WiFi + MQTT ----------
WiFiClient espClient;
PubSubClient client(espClient);

int getMedianNum(int bArray[], int iFilterLen) {
  int bTab[iFilterLen];
  for (byte i = 0; i < iFilterLen; i++) bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0)
    bTemp = bTab[(iFilterLen - 1) / 2];
  else
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  return bTemp;
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected!");
  Serial.println(WiFi.localIP());
}

void connectToMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("esp32_water_quality")) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(TdsSensorPin, INPUT);

  connectToWiFi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
  connectToMQTT();
}

void loop() {
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop();

  // Collect sensor data
  static unsigned long analogSampleTimepoint = millis();
  if (millis() - analogSampleTimepoint > 40U) {
    analogSampleTimepoint = millis();
    analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);
    analogBufferIndex++;
    if (analogBufferIndex == SCOUNT) analogBufferIndex = 0;
  }

  // Every 5 minutes publish JSON
  static unsigned long publishTimepoint = millis();
  if (millis() - publishTimepoint > 300000U) { // 300000ms = 5 min
    publishTimepoint = millis();

    for (copyIndex = 0; copyIndex < SCOUNT; copyIndex++) {
      analogBufferTemp[copyIndex] = analogBuffer[copyIndex];
    }

    averageVoltage = getMedianNum(analogBufferTemp, SCOUNT) * (float)VREF / 4095.0 / 1000.0;

    tdsValue = (133.42 * averageVoltage * averageVoltage * averageVoltage
                - 255.86 * averageVoltage * averageVoltage
                + 857.39 * averageVoltage) * 0.5;

    Serial.print("TDS Value: "); Serial.print(tdsValue, 2); Serial.println(" ppm");
    Serial.print("Voltage: "); Serial.print(averageVoltage, 3); Serial.println(" V");

    // Build JSON payload
    StaticJsonDocument<200> doc;
    doc["device_id"] = "sensor_node_03";
    JsonObject sensors = doc.createNestedObject("sensors");
    sensors["tds_ppm"] = tdsValue;
    sensors["sensor_voltage"] = averageVoltage;

    char payload[200];
    serializeJson(doc, payload);

    // Publish to MQTT
    if (client.publish(MQTT_TOPIC, payload)) {
      Serial.println("MQTT Publish success:");
      Serial.println(payload);
    } else {
      Serial.println("MQTT Publish failed!");
    }
  }
}
