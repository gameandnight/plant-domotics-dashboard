import os
import time
import threading
import random

import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ─── Config Broker desde Secrets o ENV ─────────────────────────────────────────
# En Streamlit Cloud define en Settings → Secrets: MQTT_BROKER, MQTT_PORT,
# MQTT_USERNAME y MQTT_PASSWORD.
BROKER   = st.secrets.get("MQTT_BROKER", os.getenv("MQTT_BROKER", "localhost"))
PORT     = int(st.secrets.get("MQTT_PORT",   os.getenv("MQTT_PORT", 1883)))
USERNAME = st.secrets.get("MQTT_USERNAME", os.getenv("MQTT_USERNAME", None))
PASSWORD = st.secrets.get("MQTT_PASSWORD", os.getenv("MQTT_PASSWORD", None))

TOPICS = {
    "temperature": "plant/temperature",
    "humidity":    "plant/humidity",
    "leaf_color":  "plant/leaf_color",
    "water":       "plant/water_motor",
    "alerts":      "plant/alerts",
}

# ─── Estado global ──────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = {k: [] for k in TOPICS}
if "last" not in st.session_state:
    st.session_state.last = {k: None for k in TOPICS}

# ─── Funciones MQTT ─────────────────────────────────────────────────────────────
def mqtt_configure_client(client):
    # Autenticación
    if USERNAME and PASSWORD:
        client.username_pw_set(USERNAME, PASSWORD)
    # TLS para puerto 8883
    if PORT == 8883:
        client.tls_set()  # usa certificados CA por defecto

def on_connect(c, u, f, rc):
    if rc == 0:
        for t in TOPICS.values():
            c.subscribe(t)
    else:
        st.error(f"Error MQTT connect: {rc}")

def on_message(c, u, msg):
    topic = msg.topic
    name = next(k for k,v in TOPICS.items() if v==topic)
    val = msg.payload.decode()
    try:
        val = float(val)
    except:
        pass
    st.session_state.data[name].append(val)
    st.session_state.last[name] = val

# ─── Arrancar Subscriber ────────────────────────────────────────────────────────
if "mqtt_sub" not in st.session_state:
    sub = mqtt.Client()
    mqtt_configure_client(sub)
    sub.on_connect = on_connect
    sub.on_message = on_message
    sub.connect(BROKER, PORT, 60)
    sub.loop_start()
    st.session_state.mqtt_sub = True

# ─── Publisher interno ─────────────────────────────────────────────────────────
def publisher_thread(topic, gen_func, interval=5):
    pub = mqtt.Client()
    mqtt_configure_client(pub)
    pub.connect(BROKER, PORT, 60)
    pub.loop_start()
    while True:
        payload = gen_func()
        pub.publish(topic, payload)
        time.sleep(interval)

if "pubs_started" not in st.session_state:
    # Temperatura
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["temperature"], lambda: round(random.uniform(15,30),2), 5),
                     daemon=True).start()
    # Humedad
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["humidity"], lambda: round(random.uniform(10,90),2), 5),
                     daemon=True).start()
    # Color hojas
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["leaf_color"], lambda: random.choice(["Verde","Amarillo","Seco"]), 5),
                     daemon=True).start()
    # Motor y alertas
    def motor_and_alert():
        h = st.session_state.last["humidity"] or 50
        return ("ENCENDER" if h<40 else "APAGAR", 
                "Humedad críticamente baja" if h<30 else "Todo OK")
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["water"],  lambda: motor_and_alert()[0], 5),
                     daemon=True).start()
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["alerts"], lambda: motor_and_alert()[1], 5),
                     daemon=True).start()
    st.session_state.pubs_started = True

# ─── UI de Streamlit ───────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas")
st_autorefresh(interval=2000, limit=0, key="ref")

st.subheader("Últimos valores")
for k in TOPICS:
    st.text(f"{k.capitalize()}: {st.session_state.last[k]}")

st.subheader("Promedios")
for k in ("temperature","humidity"):
    arr = st.session_state.data[k]
    avg = round(sum(arr)/len(arr),2) if arr else "N/A"
    st.text(f"{k.capitalize()} prom: {avg}")

st.subheader("Gráfica sensores")
fig, ax = plt.subplots()
for k,c in [("temperature","r"),("humidity","b")]:
    arr = st.session_state.data[k]
    if arr:
        ax.plot(arr, label=k.capitalize(), color=c)
ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

cols = st.session_state.data["leaf_color"]
if cols:
    st.subheader("Color de hojas")
    fig2, ax2 = plt.subplots()
    ax2.plot(cols, marker="o")
    st.pyplot(fig2)
