import os, time, threading, random
import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# Configuración
BROKER   = st.secrets["MQTT_BROKER"]
PORT     = int(st.secrets["MQTT_PORT"])
USERNAME = st.secrets["MQTT_USERNAME"]
PASSWORD = st.secrets["MQTT_PASSWORD"]

TOPICS = {
    "temperature": "plant/temperature",
    "humidity":    "plant/humidity",
    "leaf_color":  "plant/leaf_color",
    "water":       "plant/water_motor",
    "alerts":      "plant/alerts",
}

# Estado
if "data" not in st.session_state:
    st.session_state.data = {k: [] for k in TOPICS}
if "last" not in st.session_state:
    st.session_state.last = {k: None for k in TOPICS}
if "msg_count" not in st.session_state:
    st.session_state.msg_count = {k: 0 for k in TOPICS}
if "conn_rc" not in st.session_state:
    st.session_state.conn_rc = None

# Funciones MQTT
def mqtt_configure_client(c):
    c.username_pw_set(USERNAME, PASSWORD)
    c.tls_set()

def on_connect(c, u, flags, rc):
    st.session_state.conn_rc = rc
    if rc == 0:
        for t in TOPICS.values():
            c.subscribe(t)
    else:
        print(f"MQTT connect error: {rc}")

def on_message(c, u, msg):
    name = next(k for k,v in TOPICS.items() if v == msg.topic)
    val = msg.payload.decode()
    try: val = float(val)
    except: pass
    st.session_state.data[name].append(val)
    st.session_state.last[name] = val
    st.session_state.msg_count[name] += 1

# Arranca subscriber
if "mqtt_sub" not in st.session_state:
    client = mqtt.Client()
    mqtt_configure_client(client)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    st.session_state.mqtt_sub = True

# Publicadores internos (igual que antes)...
def publisher_thread(topic, gen, interval=5):
    pub = mqtt.Client(); mqtt_configure_client(pub)
    pub.connect(BROKER, PORT, 60); pub.loop_start()
    while True:
        pub.publish(topic, gen())
        time.sleep(interval)

if "pubs_started" not in st.session_state:
    threading.Thread(target=publisher_thread, args=(TOPICS["temperature"], lambda: round(random.uniform(15,30),2),5),daemon=True).start()
    threading.Thread(target=publisher_thread, args=(TOPICS["humidity"], lambda: round(random.uniform(10,90),2),5),daemon=True).start()
    threading.Thread(target=publisher_thread, args=(TOPICS["leaf_color"], lambda: random.choice(["Verde","Amarillo","Seco"]),5),daemon=True).start()
    def ma(): h=st.session_state.last["humidity"] or 50; return ("ENCENDER" if h<40 else "APAGAR","Humedad críticamente baja" if h<30 else "Todo OK")
    threading.Thread(target=publisher_thread, args=(TOPICS["water"], lambda: ma()[0],5),daemon=True).start()
    threading.Thread(target=publisher_thread, args=(TOPICS["alerts"],lambda:ma()[1],5),daemon=True).start()
    st.session_state.pubs_started=True

# UI
st.title("🌿 Sistema Domótico para Plantas (DEBUG MODE)")

# Mostrar RC de conexión
st.write("🔌 MQTT connect RC:", st.session_state.conn_rc)

# Mostrar conteo de mensajes recibidos
st.subheader("🧮 Mensajes recibidos por tópico")
for k,cnt in st.session_state.msg_count.items():
    st.write(f"{k}: {cnt}")

# Mostrar últimos valores
st.subheader("Últimos valores")
for k,v in st.session_state.last.items():
    st.write(f"{k}: {v}")

# Mostrar datos crudos (solo primeros 5 de cada uno)
st.subheader("📑 Datos crudos (primeros 5 elementos por tópico)")
for k, arr in st.session_state.data.items():
    st.write(f"{k}: {arr[:5]}")

# También refrescar
st_autorefresh(interval=2000, limit=0, key="ref")

# (Opcional, no dibujar gráficas aún para centrarnos en debug)

