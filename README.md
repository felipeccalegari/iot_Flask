# Internet of Things project with Flask

This project is a variation of my previous repository called "TCC" (my final project for University). It's focus was to build an IoT application to measure the current temperature in Celsius and Fahrenheit alongisde with humidity with the DHT22 sensor. The micro controller utilized was the ESP32 where it's connected to local wi-fi and a MQTT Broker to transfer data. Main differences in here compared to my old project is that now it was used the humidity and Fahrenheit temperature functions to get those values. Another difference is how the data was sent to MQTT, which in this case it was sent to a single topic (python/data) in a JSON format with the help of the ArduinoJson library. 

The backend of the application was now built using Python with the Flask framework, which in the previous project was built using Javascript with the Node.js framework. Essentially, the Flask application connects to the MQTT broker and subscribes to the "python/data" topic. After that, the data is sent to a database called "mqtt" in PostgreSQL in a table also called "mqtt". Each value (temperature in Celsius, temperature in Fahrenheit and humidity) is stored in its own column. In total, it has been used 5 routes that the user can use to visualize the data using the 5000 port ("/", "/tempc", "tempf", "humid", "database_data", which this last one would just display the raw data coming from the database). The frontend was now used basic HTML and CSS (in the previous project it was used the Grafana platform to display the data).

Lastly, just like in my previous project, the application would be running through Docker containers since it was it's original purpose: deploy an IoT application with Docker containers. It was created a simple Docker image for the Flask application and then in the Docker Compose it was configured the containers for Flask and PostgreSQL.

## Routes:
 - "/" route: 3 displays showing final data received in the MQTT broker and a chart with all 3 measures (Celsius, Fahrenheit and humidity).
 - "/tempc" route: 1 display showing final temperature in Celsius from MQTT and chart with the Celsius temperature stored in the database.
- "/tempf" route: 1 display showing final temperature in Fahrenheit from MQTT and chart with the Fahrenheit temperature stored in the database.
- "/humid" route: 1 display showing final humidity in % from MQTT and chart with the humidity stored in the database.

### Running the application:

 - Make sure to change the wi-fi and MQTT credentials from the .ino file in the esp32 folder.
 - With Docker and Docker Compose installed, simply type the command `docker compose up -d` in your local terminal and Docker will run the containers.
 - Access the application using [localhost:5000](localhost:5000).

### Circuit diagram:

![Alt text](https://github.com/felipeccalegari/iot_Flask/blob/master/esp32/dht22_esp32/tcc_esquematico_dht22.png)
