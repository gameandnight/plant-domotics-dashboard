import time, threading, random
import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ─── BROKER PÚBLICO (sin auth, sin TLS) ─────────────────────────────────────────
BROKER = "broker.hivemq.com"
PORT   = 1883

TOPICS = {
    "temperature": "plant/temperature",
    "humidity":    "plant/humidity",
    "leaf_color":  "plant/leaf_color",
    "water":       "plant/water_motor",
    "alerts":      "plant/alerts",
}

# ─── ESTADO GLOBAL ───────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = {k: [] for k in TOPICS}
if "last" not in st.session_state:
    st.session_state.last = {k: None for k in TOPICS}
if "conn_rc" not in st.session_state:
    st.session_state.conn_rc = None

# ─── CALLBACKS MQTT ─────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    st.session_state.conn_rc = rc
    for topic in TOPICS.values():
        client.subscribe(topic)

def on_message(client, userdata, msg):
    name = next(k for k,v in TOPICS.items() if v == msg.topic)
    val = msg.payload.decode()
    try:
        val = float(val)
    except:
        pass
    st.session_state.data[name].append(val)
    st.session_state.last[name] = val

# ─── INICIO SUBSCRIBER EN HILO DEDICADO ────────────────────────────────────────
def start_mqtt_subscriber():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if "mqtt_sub_started" not in st.session_state:
    threading.Thread(target=start_mqtt_subscriber, daemon=True).start()
    st.session_state.mqtt_sub_started = True

# ─── PUBLISHERS INTERNOS ────────────────────────────────────────────────────────
def publisher_thread(topic, gen_func, interval=5):
    pub = mqtt.Client()
    pub.connect(BROKER, PORT, 60)
    pub.loop_start()
    while True:
        pub.publish(topic, gen_func())
        time.sleep(interval)

if "pubs_started" not in st.session_state:
    threading.Thread(
        target=publisher_thread,
        args=(TOPICS["temperature"], lambda: round(random.uniform(15,30),2), 5),
        daemon=True
    ).start()
    threading.Thread(
        target=publisher_thread,
        args=(TOPICS["humidity"], lambda: round(random.uniform(10,90),2), 5),
        daemon=True
    ).start()
    threading.Thread(
        target=publisher_thread,
        args=(TOPICS["leaf_color"], lambda: random.choice(["Verde","Amarillo","Seco"]), 5),
        daemon=True
    ).start()
    def motor_and_alert():
        h = st.session_state.last["humidity"] or 50
        cmd = "ENCENDER" if h < 40 else "APAGAR"
        alert = "Humedad críticamente baja" if h < 30 else "Todo OK"
        return cmd, alert
    threading.Thread(
        target=publisher_thread,
        args=(TOPICS["water"],  lambda: motor_and_alert()[0], 5),
        daemon=True
    ).start()
    threading.Thread(
        target=publisher_thread,
        args=(TOPICS["alerts"], lambda: motor_and_alert()[1], 5),
        daemon=True
    ).start()
    st.session_state.pubs_started = True

# ─── INTERFAZ STREAMLIT ─────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas")

# Refrescar cada 2 segundos
st_autorefresh(interval=2000, limit=0, key="ref")

st.subheader("🔌 Estado de conexión MQTT (RC)")
st.write(st.session_state.conn_rc)

st.subheader("Últimos valores")
for key in TOPICS:
    st.write(f"{key}: {st.session_state.last[key]}")

st.subheader("Promedios")
for key in ("temperature", "humidity"):
    arr = st.session_state.data[key]
    avg = round(sum(arr)/len(arr), 2) if arr else "N/A"
    st.write(f"{key} promedio: {avg}")

st.subheader("Gráfica sensores")
fig, ax = plt.subplots()
for key, color in [("temperature", "r"), ("humidity", "b")]:
    arr = st.session_state.data[key]
    if arr:
        ax.plot(arr, label=key, color=color)
ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

cols = st.session_state.data["leaf_color"]
if cols:
    st.subheader("Color de hojas")
    fig2, ax2 = plt.subplots()
    ax2.plot(cols, marker="o")
    st.pyplot(fig2)

