import os
import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# Configuración del broker MQTT desde variables de entorno
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

# Inicializar estado si no existe
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = {
        "temperature": [],
        "humidity": [],
        "leaf_color": []
    }

if "last_values" not in st.session_state:
    st.session_state.last_values = {
        "temperature": None,
        "humidity": None,
        "leaf_color": "N/A",
        "water_motor": "N/A",
        "alert": "N/A"
    }

# Temas MQTT
TOPICS = {
    "temperature": "plant/temperature",
    "humidity": "plant/humidity",
    "leaf_color": "plant/leaf_color",
    "water_motor": "plant/water_motor",
    "alerts": "plant/alerts"
}

# Función cuando el cliente se conecta
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
        for topic in TOPICS.values():
            client.subscribe(topic)
    else:
        print(f"Error al conectar: {rc}")

# Función cuando se recibe un mensaje
def on_message(client, userdata, msg):
    topic = msg.topic
    value = msg.payload.decode("utf-8")

    if topic == TOPICS["temperature"]:
        temp = round(float(value), 2)
        st.session_state.sensor_data["temperature"].append(temp)
        st.session_state.last_values["temperature"] = temp

    elif topic == TOPICS["humidity"]:
        hum = round(float(value), 2)
        st.session_state.sensor_data["humidity"].append(hum)
        st.session_state.last_values["humidity"] = hum

    elif topic == TOPICS["leaf_color"]:
        st.session_state.sensor_data["leaf_color"].append(value)
        st.session_state.last_values["leaf_color"] = value

    elif topic == TOPICS["water_motor"]:
        st.session_state.last_values["water_motor"] = "Encendido" if "ENCENDER" in value else "Apagado"

    elif topic == TOPICS["alerts"]:
        st.session_state.last_values["alert"] = value if "Humedad críticamente baja" in value else "Sistema funcionando con normalidad"

# Inicializar cliente MQTT (solo una vez)
if "mqtt_client_started" not in st.session_state:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    st.session_state.mqtt_client_started = True

# 🌿 Título
st.title("🌿 Sistema Domótico para Control de Plantas")

# 🔄 Refresco automático cada 2 segundos
st_autorefresh(interval=2000, limit=0, key="refresh")

# 📡 Mostrar últimos valores
st.subheader("🌡️ Últimos valores")
st.text(f"Temperatura: {st.session_state.last_values['temperature']:.2f}°C" if st.session_state.last_values['temperature'] is not None else "Temperatura: N/A")
st.text(f"Humedad: {st.session_state.last_values['humidity']:.2f}%" if st.session_state.last_values['humidity'] is not None else "Humedad: N/A")
st.text(f"Color de hojas: {st.session_state.last_values['leaf_color']}")
st.text(f"Estado del motor de agua: {st.session_state.last_values['water_motor']}")
st.text(f"Estado del sistema: {st.session_state.last_values['alert']}")

# 📊 Promedios
st.subheader("📊 Promedio de valores registrados")
temp_data = st.session_state.sensor_data['temperature']
hum_data = st.session_state.sensor_data['humidity']
temp_avg = round(sum(temp_data)/len(temp_data), 2) if temp_data else 'N/A'
hum_avg = round(sum(hum_data)/len(hum_data), 2) if hum_data else 'N/A'
st.text(f"Temperatura Promedio: {temp_avg}°C")
st.text(f"Humedad Promedio: {hum_avg}%")

# 📈 Gráficas
st.subheader("📈 Gráficas de los sensores")
fig, ax = plt.subplots()
if temp_data:
    ax.plot(temp_data, label="Temperatura", color='red')
if hum_data:
    ax.plot(hum_data, label="Humedad", color='blue')
ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
st.pyplot(fig)

# 🌿 Evolución del color de hojas
leaf_data = st.session_state.sensor_data["leaf_color"]
if leaf_data:
    st.subheader("🌿 Evolución del Color de las Hojas")
    fig2, ax2 = plt.subplots()
    ax2.plot(range(len(leaf_data)), leaf_data, marker='o', label="Color de Hojas", color='green')
    ax2.legend(loc="upper left", bbox_to_anchor=(1, 1))
    st.pyplot(fig2)
