#include <DHT.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>

#define DHTPIN 4
#define DHTTYPE DHT22

#define ssid "" // Insert your wifi SSID
#define password_wifi "" // Insert your wifi password

const char *mqtt_server = "broker.hivemq.com";
const char *mqtt_user = ""; // Insert your MQTT username (if needed)
const char *mqtt_password = ""; // Insert your MQTT password (if needed)
const int mqtt_port = 1883;
const char *dados = "python/data";

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

char buffer[512];
StaticJsonDocument<260> doc;

void callback(char* topic, byte* payload, unsigned int length) {
  int i = 0;
  Serial.println("Message arrived:topic: " + String(topic));
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password_wifi);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting...");
  }
  Serial.println("Connected to wifi!");

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  while (!client.connected())
  {
    String client_id = "ESP32";
    client_id += String(WiFi.macAddress());
    Serial.printf("Client %s connects to the broker.\n", client_id.c_str());


    if (client.connect(client_id.c_str(), mqtt_user, mqtt_password))
    {
      Serial.println("Connected to MQTT broker!");
    }
    else 
    {
      Serial.print("Failed to connect with state ");
      Serial.println(client.state());
      delay(1000);
    }
  }

  dht.begin();
}


void loop() {
  delay(5000);

  float tc = dht.readTemperature();
  float tf = dht.readTemperature(true);
  float h = dht.readHumidity();

  if (isnan(h) || isnan(tc) || isnan(tf)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }
  Serial.println("Celsius: " );
  Serial.println(tc);

  double new_tc = (int)(tc * 100 + 0.5)/ 100.0;
  Serial.println("Farenheit: ");
  Serial.println(tf);
  double new_tf = (int)(tf * 100 + 0.5)/ 100.0;
  Serial.println("Humidity: ");
  Serial.println(h);
  double new_h = (int)(h * 100 + 0.5)/ 100.0;
  doc["temp_celsius"] = new_tc;
  doc["temp_farenheit"] = new_tf;
  doc["humidity"] = new_h;
  size_t n = serializeJson(doc, buffer);
  Serial.println("Data in JSON: ");
  Serial.println(buffer);
  client.publish(dados, buffer, n);
  Serial.println("Data sent to MQTT!");
}
