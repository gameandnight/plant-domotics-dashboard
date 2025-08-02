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

# ─── Simulación en cada recarga ──────────────────────────────────────────────────
# Cada vez que la app se ejecuta (o recarga), generamos un nuevo punto:
temp = round(random.uniform(15, 30), 2)
hum  = round(random.uniform(10, 90), 2)
leaf = random.choice(["Verde", "Amarillo", "Seco"])

st.session_state.temperature.append(temp)
st.session_state.humidity.append(hum)
st.session_state.leaf_color.append(leaf)
st.session_state.water_motor = "ENCENDER" if hum < 40 else "APAGAR"
st.session_state.alert       = "⚠️ Humedad críticamente baja" if hum < 30 else "✅ Sistema OK"

# ─── INTERFAZ STREAMLIT ─────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas (Demo Simulada)")

# Recarga cada 2 segundos
st_autorefresh(interval=2000, limit=0, key="auto")

# ─ Últimos valores ──────────────────────────────────────────────────────────────
st.subheader("Últimos valores")
st.write(f"🌡️ Temperatura: {st.session_state.temperature[-1]} °C")
st.write(f"💧 Humedad: {st.session_state.humidity[-1]} %")
st.write(f"🍃 Color de hojas: {st.session_state.leaf_color[-1]}")
st.write(f"💦 Motor de agua: {st.session_state.water_motor}")
st.write(f"🚨 Alerta: {st.session_state.alert}")

# ─ Promedios ────────────────────────────────────────────────────────────────────
st.subheader("📊 Promedios")
temp_avg = round(sum(st.session_state.temperature) / len(st.session_state.temperature), 2)
hum_avg  = round(sum(st.session_state.humidity)    / len(st.session_state.humidity),    2)
st.write(f"Temperatura promedio: {temp_avg} °C")
st.write(f"Humedad promedio: {hum_avg} %")

# ─ Gráfica de temperatura y humedad ────────────────────────────────────────────
st.subheader("📈 Gráfica de Temperatura y Humedad")
fig, ax = plt.subplots()
ax.plot(st.session_state.temperature, label="Temperatura", color="red")
ax.plot(st.session_state.humidity,    label="Humedad",    color="blue")
ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

# ─ Evolución del color de las hojas ────────────────────────────────────────────
st.subheader("🌿 Evolución del Color de las Hojas")
mapping = {"Verde": 0, "Amarillo": 1, "Seco": 2}
idxs = [mapping[c] for c in st.session_state.leaf_color]
fig2, ax2 = plt.subplots()
ax2.plot(idxs, marker="o")
ax2.set_yticks([0,1,2])
ax2.set_yticklabels(["Verde","Amarillo","Seco"])
st.pyplot(fig2)
