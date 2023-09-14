import psycopg2
from psycopg2 import OperationalError
import time
from flask import Flask, render_template
from paho.mqtt import client as mqtt_client
import json
import random

app = Flask(__name__)

broker = "broker.hivemq.com"
mqtt_port = 1883
topic_mqtt = "python/data"
client_id = f'publish-{random.randint(0,1000)}'


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    app.logger.info("Connnected to MQTT")
    client.subscribe(topic_mqtt)

def conecta_db():
    conn = None
    while not conn:
        try:
            conn = psycopg2.connect(
                dbname="mqtt",
                user="postgres",
                password="postgres",
                host="postgres"
            )
            print("Database connection successful")
        except OperationalError as e:
            print(e)
            time.sleep(5)
    return conn

conecta_db()

def criar_db(sql):
    con = conecta_db()
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()

sql_criar = 'CREATE TABLE IF NOT EXISTS mqtt(id SERIAL PRIMARY KEY, tempc FLOAT, tempf FLOAT, humid FLOAT, hora TIMESTAMP NOT NULL DEFAULT NOW())'

criar_db(sql_criar)

client = mqtt_client.Client()
client.on_connect = on_connect

client.connect(broker, mqtt_port, 60)

def on_message(client, userdata, msg):
    con = conecta_db()
    cur = con.cursor()
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        temp_celsius = data["temp_celsius"]
        temp_fahrenheit = data["temp_farenheit"]
        humidity = data["humidity"]

        insert_query = "INSERT INTO mqtt (tempc, tempf, humid) VALUES (%s, %s, %s);"
        cur.execute(insert_query, (temp_celsius, temp_fahrenheit, humidity))
        con.commit()

        app.config['latest_data'] = data
    except Exception as e:
        print(f"Error parsing JSON: {e}")

print('Dados inseridos!')

client.on_message = on_message

@app.route('/latest_data')
def latest_data():
    latest_data = app.config.get('latest_data', {})
    return json.dumps(latest_data)

@app.route('/database_data')
def database_data():
    try:
        app.logger.info('abriu a rota db')
        con = conecta_db()
        cur = con.cursor()
        app.logger.info('Conectado ao db na rota do db')
        cur.execute('SELECT id, tempc, tempf, humid FROM mqtt;')
        app.logger.info('executou select')
        data_entries = cur.fetchall()
        cur.close()
        con.close()
        app.logger.info(data_entries)
        return render_template('database_data_template.html', data_entries=data_entries)
    except Exception as e:
        error_text = 'Error: ' + str(e)
        return error_text


@app.route('/')
def alldata():
    try:
        conn = conecta_db()
        cur = conn.cursor()

        cur.execute("SELECT hora, tempc, tempf, humid FROM mqtt;")
        rows = cur.fetchall()

        labels = [row[0].strftime('%H:%M:%S') for row in rows]

        tempc_data = [row[1] for row in rows]
        tempf_data = [row[2] for row in rows]
        humid_data = [row[3] for row in rows]

        labels_json = json.dumps(labels)
        tempc_data_json = json.dumps(tempc_data)
        tempf_data_json = json.dumps(tempf_data)
        humid_data_json = json.dumps(humid_data)

        conn.close()
        latest_data = app.config.get('latest_data', {})

        return render_template('display_chart.html', data=latest_data, labels_json=labels_json, tempc_data_json=tempc_data_json, tempf_data_json=tempf_data_json, humid_data_json=humid_data_json)

    except Exception as e:
        error_text = 'Error: ' + str(e)
        return error_text

@app.route('/tempc')
def tempc():
    try:
        conn = conecta_db()
        cur = conn.cursor()

        cur.execute("SELECT hora, tempc FROM mqtt ORDER BY hora LIMIT 30;")
        rows = cur.fetchall()

        labels = [row[0].strftime('%H:%M:%S') for row in rows]

        tempc_data = [row[1] for row in rows]

        labels_json = json.dumps(labels)
        tempc_data_json = json.dumps(tempc_data)

        conn.close()
        latest_data = app.config.get('latest_data', {})

        return render_template('info_celsius.html', data=latest_data, labels_json=labels_json, tempc_data_json=tempc_data_json)

    except Exception as e:
        error_text = 'Error: ' + str(e)
        return error_text

@app.route('/tempf')
def tempf():
    try:
        conn = conecta_db()
        cur = conn.cursor()

        cur.execute("SELECT hora, tempf FROM mqtt ORDER BY hora LIMIT 30;")
        rows = cur.fetchall()

        labels = [row[0].strftime('%H:%M:%S') for row in rows]

        tempf_data = [row[1] for row in rows]


        labels_json = json.dumps(labels)
        tempf_data_json = json.dumps(tempf_data)


        conn.close()
        latest_data = app.config.get('latest_data', {})

        return render_template('info_faren.html', data=latest_data, labels_json=labels_json, tempf_data_json=tempf_data_json)

    except Exception as e:
        error_text = 'Error: ' + str(e)
        return error_text

@app.route('/humid')
def humid():
    try:
        conn = conecta_db()
        cur = conn.cursor()

        cur.execute("SELECT hora, humid FROM mqtt ORDER BY hora LIMIT 30;")
        rows = cur.fetchall()

        labels = [row[0].strftime('%H:%M:%S') for row in rows]

        humid_data = [row[1] for row in rows]


        labels_json = json.dumps(labels)
        humid_data_json = json.dumps(humid_data)


        conn.close()
        latest_data = app.config.get('latest_data', {})

        return render_template('info_humid.html', data=latest_data, labels_json=labels_json, humid_data_json=humid_data_json)

    except Exception as e:
        error_text = 'Error: ' + str(e)
        return error_text
    

if __name__ == '__main__':
    client.loop_start()
    app.run(host='0.0.0.0', debug=True)
    