import time, threading, random
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ─── Estado global ────────────────────────────────────────────────────────────
if "temperature" not in st.session_state:
    st.session_state.temperature = []
    st.session_state.humidity    = []
    st.session_state.leaf_color  = []
    st.session_state.water_motor = None
    st.session_state.alert       = None

# ─── Simulación en hilo ───────────────────────────────────────────────────────
def simulate():
    while True:
        temp = round(random.uniform(15, 30), 2)
        hum  = round(random.uniform(10, 90), 2)
        leaf = random.choice(["Verde","Amarillo","Seco"])

        st.session_state.temperature.append(temp)
        st.session_state.humidity.append(hum)
        st.session_state.leaf_color.append(leaf)

        st.session_state.water_motor = "ENCENDER" if hum < 40 else "APAGAR"
        st.session_state.alert       = "⚠️ Humedad críticamente baja" if hum < 30 else "✅ Sistema OK"

        time.sleep(5)

if "sim_thread" not in st.session_state:
    threading.Thread(target=simulate, daemon=True).start()
    st.session_state.sim_thread = True

# ─── UI ───────────────────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas (Demo Simulada)")
st_autorefresh(interval=2000, limit=0, key="ref")

# Últimos valores
st.subheader("Últimos valores")
st.write(f"🌡️ Temperatura: {st.session_state.temperature[-1]} °C")
st.write(f"💧 Humedad: {st.session_state.humidity[-1]} %")
st.write(f"🍃 Color de hojas: {st.session_state.leaf_color[-1]}")
st.write(f"💦 Motor de agua: {st.session_state.water_motor}")
st.write(f"🚨 Alerta: {st.session_state.alert}")

# Promedios
st.subheader("📊 Promedios")
st.write(f"Temperatura promedio: {round(sum(st.session_state.temperature)/len(st.session_state.temperature),2)} °C")
st.write(f"Humedad promedio: {round(sum(st.session_state.humidity)/len(st.session_state.humidity),2)} %")

# Gráficas
st.subheader("📈 Gráfica de temperatura y humedad")
fig, ax = plt.subplots()
ax.plot(st.session_state.temperature, label="Temperatura", color="red")
ax.plot(st.session_state.humidity,    label="Humedad",    color="blue")
ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

st.subheader("🌿 Evolución del color de las hojas")
leaf_map = {"Verde":0,"Amarillo":1,"Seco":2}
idxs = [leaf_map[c] for c in st.session_state.leaf_color]
fig2, ax2 = plt.subplots()
ax2.plot(idxs, marker="o")
ax2.set_yticks([0,1,2]); ax2.set_yticklabels(["Verde","Amarillo","Seco"])
st.pyplot(fig2)

