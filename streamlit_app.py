import os
import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# Configuración del broker MQTT desde variables de entorno
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

# Diccionarios globales para almacenar los datos de los sensores
sensor_data = {
    "temperature": [],
    "humidity": [],
    "leaf_color": []
}

# Diccionario para almacenar los últimos valores recibidos
last_values = {
    "temperature": None,
    "humidity": None,
    "leaf_color": None,
    "water_motor": None,
    "alert": ""
}

# Temas MQTT
TOPICS = {
    "temperature": "plant/temperature",
    "humidity": "plant/humidity",
    "leaf_color": "plant/leaf_color",
    "water_motor": "plant/water_motor",
    "alerts": "plant/alerts"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        for topic in TOPICS.values():
            client.subscribe(topic)
    else:
        print(f"Error al conectar: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode("utf-8")

    if topic == TOPICS["temperature"]:
        temp = round(float(value), 2)
        sensor_data["temperature"].append(temp)
        last_values["temperature"] = temp
    elif topic == TOPICS["humidity"]:
        hum = round(float(value), 2)
        sensor_data["humidity"].append(hum)
        last_values["humidity"] = hum
    elif topic == TOPICS["leaf_color"]:
        sensor_data["leaf_color"].append(value)
        last_values["leaf_color"] = value
    elif topic == TOPICS["water_motor"]:
        last_values["water_motor"] = "Encendido" if "ENCENDER" in value else "Apagado"
    elif topic == TOPICS["alerts"]:
        last_values["alert"] = value if "Humedad críticamente baja" in value else "Sistema funcionando con normalidad"

# Inicializar cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

# Título de la app
st.title("🌿 Sistema Domótico para Control de Plantas")

# Contenedores
last_values_container = st.empty()
averages_container = st.empty()
graph_container = st.empty()

def update_dashboard():
    # Mostrar los últimos valores
    with last_values_container.container():
        st.subheader("🌡️ Últimos valores")
        st.text(f"Temperatura: {last_values['temperature']:.2f}°C" if last_values['temperature'] is not None else "Temperatura: N/A")
        st.text(f"Humedad: {last_values['humidity']:.2f}%" if last_values['humidity'] is not None else "Humedad: N/A")
        st.text(f"Color de hojas: {last_values['leaf_color'] or 'N/A'}")
        st.text(f"Estado del motor de agua: {last_values['water_motor'] or 'N/A'}")
        st.text(f"Estado del sistema: {last_values['alert'] or 'N/A'}")

    # Mostrar promedios
    with averages_container.container():
        st.subheader("📊 Promedio de valores registrados")
        temp_avg = round(sum(sensor_data['temperature']) / len(sensor_data['temperature']), 2) if sensor_data['temperature'] else 'N/A'
        hum_avg = round(sum(sensor_data['humidity']) / len(sensor_data['humidity']), 2) if sensor_data['humidity'] else 'N/A'
        st.text(f"Temperatura Promedio: {temp_avg}°C")
        st.text(f"Humedad Promedio: {hum_avg}%")

    # Graficar datos
    with graph_container.container():
        st.subheader("📈 Gráficas de los sensores")
        fig, ax = plt.subplots()
        if sensor_data['temperature']:
            ax.plot(sensor_data['temperature'], label="Temperatura")
        if sensor_data['humidity']:
            ax.plot(sensor_data['humidity'], label="Humedad")
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        st.pyplot(fig)

        if sensor_data['leaf_color']:
            st.subheader("🌿 Evolución del Color de las Hojas")
            fig2, ax2 = plt.subplots()
            ax2.plot(range(len(sensor_data['leaf_color'])), sensor_data['leaf_color'], marker='o', label="Color de Hojas")
            ax2.legend(loc="upper left", bbox_to_anchor=(1, 1))
            st.pyplot(fig2)

# Refrescar la app cada 2 segundos
st_autorefresh(interval=2000, limit=0, key="mqtt_refresh")
update_dashboard()

