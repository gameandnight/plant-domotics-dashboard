import os
import time
import threading
import random

import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ─── Config Broker ────────────────────────────────────────────────────────────
BROKER   = os.getenv("MQTT_BROKER", "445a4eae8e134615a3ce69a534d296ab.s1.eu.hivemq.cloud")
PORT     = int(os.getenv("MQTT_PORT", 8883))

TOPICS = {
    "temperature": "plant/temperature",
    "humidity":    "plant/humidity",
    "leaf_color":  "plant/leaf_color",
    "water":       "plant/water_motor",
    "alerts":      "plant/alerts",
}

# ─── Estado global (session_state) ─────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = {k: [] for k in TOPICS}

if "last" not in st.session_state:
    st.session_state.last = {k: None for k in TOPICS}

# ─── MQTT Subscriber ──────────────────────────────────────────────────────────
def on_connect(c, u, f, rc):
    if rc == 0:
        for t in TOPICS.values():
            c.subscribe(t)

def on_message(c, u, msg):
    topic = msg.topic
    # invierte TOPICS dict
    name = next(k for k,v in TOPICS.items() if v==topic)
    val = msg.payload.decode()
    # numérico o texto
    try:
        val = float(val)
    except:
        pass
    st.session_state.data[name].append(val)
    st.session_state.last[name] = val

# arranca subscriber solo una vez
if "mqtt" not in st.session_state:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    st.session_state.mqtt = client

# ─── MQTT Publishers internos ─────────────────────────────────────────────────
def publisher_thread(topic, gen_func, interval=5):
    pub = mqtt.Client()
    pub.connect(BROKER, PORT, 60)
    pub.loop_start()
    while True:
        payload = gen_func()
        pub.publish(topic, payload)
        time.sleep(interval)

# sólo arrancar hilos 1 vez
if "pubs_started" not in st.session_state:
    # temperatura 15–30°C
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["temperature"], lambda: round(random.uniform(15,30),2)),
                     daemon=True).start()
    # humedad 10–90%
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["humidity"], lambda: round(random.uniform(10,90),2)),
                     daemon=True).start()
    # color hojas
    threading.Thread(target=publisher_thread,
                     args=(TOPICS["leaf_color"], lambda: random.choice(["Verde","Amarillo","Seco"])),
                     daemon=True).start()
    # motor y alertas
    def motor_and_alert():
        h = st.session_state.last["humidity"] or 50
        cmd = "ENCENDER" if h<40 else "APAGAR"
        alert = "Humedad críticamente baja" if h<30 else "Todo OK"
        return cmd, alert
    t1 = threading.Thread(
        target=publisher_thread,
        args=(TOPICS["water"], lambda: motor_and_alert()[0], 5),
        daemon=True)
    t2 = threading.Thread(
        target=publisher_thread,
        args=(TOPICS["alerts"], lambda: motor_and_alert()[1], 5),
        daemon=True)
    t1.start(); t2.start()
    st.session_state.pubs_started = True

# ─── INTERFAZ STREAMLIT ────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas")

# refresco cada 2s
st_autorefresh(interval=2000, limit=0, key="ref")

# Últimos valores
st.subheader("Últimos valores")
for k in TOPICS:
    v = st.session_state.last[k]
    st.text(f"{k.capitalize()}: {v}")

# Promedios
st.subheader("Promedios")
for k in ("temperature","humidity"):
    arr = st.session_state.data[k]
    avg = round(sum(arr)/len(arr),2) if arr else "N/A"
    st.text(f"{k.capitalize()} prom: {avg}")

# Gráfica de temperatura/humedad
st.subheader("Gráfica sensores")
fig, ax = plt.subplots()
for k,cname in [("temperature","r"),("humidity","b")]:
    arr = st.session_state.data[k]
    if arr:
        ax.plot(arr, label=k.capitalize(), color=cname)
ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

# Evolución color de hojas
cols = st.session_state.data["leaf_color"]
if cols:
    st.subheader("Color de hojas")
    fig2, ax2 = plt.subplots()
    ax2.plot(cols, marker="o")
    st.pyplot(fig2)
