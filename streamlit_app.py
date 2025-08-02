import time
import threading
import random

import streamlit as st
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ─── Estado global ───────────────────────────────────────────────────────────────
if "temperature" not in st.session_state:
    st.session_state.temperature = []
    st.session_state.humidity    = []
    st.session_state.leaf_color  = []
    st.session_state.water_motor = None
    st.session_state.alert       = None

# ─── Función de simulación (hilo daemon) ────────────────────────────────────────
def simulate():
    while True:
        # Generar datos aleatorios
        temp = round(random.uniform(15, 30), 2)
        hum  = round(random.uniform(10, 90), 2)
        leaf = random.choice(["Verde", "Amarillo", "Seco"])

        # Actualizar último valor
        st.session_state.temperature.append(temp)
        st.session_state.humidity.append(hum)
        st.session_state.leaf_color.append(leaf)

        # Lógica de motor y alerta
        st.session_state.water_motor = "ENCENDER" if hum < 40 else "APAGAR"
        st.session_state.alert       = (
            "⚠️ Humedad críticamente baja" if hum < 30 else "✅ Sistema OK"
        )

        time.sleep(5)

# Arrancar la simulación solo una vez
if "sim_thread" not in st.session_state:
    threading.Thread(target=simulate, daemon=True).start()
    st.session_state.sim_thread = True

# ─── INTERFAZ STREAMLIT ─────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas (Demo Simulada)")

# Refrescar automáticamente cada 2 segundos
st_autorefresh(interval=2000, limit=0, key="auto")

# ─ Últimos valores ──────────────────────────────────────────────────────────────
st.subheader("Últimos valores")
if st.session_state.temperature:
    st.write(f"🌡️ Temperatura: {st.session_state.temperature[-1]} °C")
    st.write(f"💧 Humedad: {st.session_state.humidity[-1]} %")
    st.write(f"🍃 Color de hojas: {st.session_state.leaf_color[-1]}")
    st.write(f"💦 Motor de agua: {st.session_state.water_motor}")
    st.write(f"🚨 Alerta: {st.session_state.alert}")
else:
    st.write("Esperando primeros datos...")

# ─ Promedios ────────────────────────────────────────────────────────────────────
st.subheader("📊 Promedios")
if st.session_state.temperature:
    temp_avg = round(sum(st.session_state.temperature) / len(st.session_state.temperature), 2)
    hum_avg  = round(sum(st.session_state.humidity)    / len(st.session_state.humidity),    2)
    st.write(f"Temperatura promedio: {temp_avg} °C")
    st.write(f"Humedad promedio: {hum_avg} %")
else:
    st.write("No hay suficientes datos para calcular promedios.")

# ─ Gráfica de temperatura y humedad ────────────────────────────────────────────
st.subheader("📈 Gráfica de Temperatura y Humedad")
fig, ax = plt.subplots()
if st.session_state.temperature:
    ax.plot(st.session_state.temperature, label="Temperatura", color="red")
    ax.plot(st.session_state.humidity,    label="Humedad",    color="blue")
    ax.legend(loc="upper left", bbox_to_anchor=(1,1))
    st.pyplot(fig)
else:
    st.write("A la espera de datos para graficar...")

# ─ Evolución del color de las hojas ────────────────────────────────────────────
st.subheader("🌿 Evolución del Color de las Hojas")
leaf_data = st.session_state.leaf_color
if leaf_data:
    # Mapeo para graficar
    mapping = {"Verde": 0, "Amarillo": 1, "Seco": 2}
    idxs = [mapping[c] for c in leaf_data]
    fig2, ax2 = plt.subplots()
    ax2.plot(idxs, marker="o")
    ax2.set_yticks([0,1,2])
    ax2.set_yticklabels(["Verde","Amarillo","Seco"])
    st.pyplot(fig2)
else:
    st.write("A la espera de datos de color de hojas...")
