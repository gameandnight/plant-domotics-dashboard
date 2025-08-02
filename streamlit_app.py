import time, threading, random
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ─── Estado global ───────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = {
        "temperature": [],
        "humidity": [],
        "leaf_color": []
    }
if "last" not in st.session_state:
    st.session_state.last = {
        "temperature": None,
        "humidity": None,
        "leaf_color": None,
        "water_motor": None,
        "alert": None
    }

# ─── Función simuladora ──────────────────────────────────────────────────────────
def simulate_sensors():
    while True:
        # Simula valores
        temp = round(random.uniform(15, 30), 2)
        hum  = round(random.uniform(10, 90), 2)
        leaf = random.choice(["Verde", "Amarillo", "Seco"])
        # Guarda último
        st.session_state.last["temperature"] = temp
        st.session_state.last["humidity"]    = hum
        st.session_state.last["leaf_color"]  = leaf
        # Append histórico
        st.session_state.data["temperature"].append(temp)
        st.session_state.data["humidity"].append(hum)
        st.session_state.data["leaf_color"].append(leaf)
        # Motor y alerta
        if hum < 40:
            st.session_state.last["water_motor"] = "ENCENDER"
        else:
            st.session_state.last["water_motor"] = "APAGAR"
        if hum < 30:
            st.session_state.last["alert"] = "⚠️ Humedad críticamente baja"
        else:
            st.session_state.last["alert"] = "✅ Sistema OK"
        time.sleep(5)

# Arranca la simulación solo una vez
if "sim_thread" not in st.session_state:
    threading.Thread(target=simulate_sensors, daemon=True).start()
    st.session_state.sim_thread = True

# ─── INTERFAZ STREAMLIT ─────────────────────────────────────────────────────────
st.title("🌿 Sistema Domótico para Plantas (Demo Simulada)")
st_autorefresh(interval=2000, limit=0, key="ref")

# Últimos valores
st.subheader("Últimos valores")
lv = st.session_state.last
st.write(f"🌡️ Temperatura: {lv['temperature']} °C")
st.write(f"💧 Humedad: {lv['humidity']} %")
st.write(f"🍃 Color de hojas: {lv['leaf_color']}")
st.write(f"💦 Motor de agua: {lv['water_motor']}")
st.write(f"🚨 Alerta: {lv['alert']}")

# Promedios
st.subheader("📊 Promedios")
temp_data = st.session_state.data["temperature"]
hum_data  = st.session_state.data["humidity"]
st.write(f"Temperatura promedio: {round(sum(temp_data)/len(temp_data),2) if temp_data else 'N/A'} °C")
st.write(f"Humedad promedio: {round(sum(hum_data)/len(hum_data),2) if hum_data else 'N/A'} %")

# Gráficas
st.subheader("📈 Gráfica de temperatura y humedad")
fig, ax = plt.subplots()
if temp_data:
    ax.plot(temp_data, label="Temperatura", color="red")
if hum_data:
    ax.plot(hum_data, label="Humedad", color="blue")
ax.legend(loc="upper left", bbox_to_anchor=(1,1))
st.pyplot(fig)

leaf_data = st.session_state.data["leaf_color"]
if leaf_data:
    st.subheader("🌿 Evolución del color de las hojas")
    fig2, ax2 = plt.subplots()
    # convierto colores a índices para graficar
    mapping = {"Verde": 0, "Amarillo": 1, "Seco": 2}
    idxs = [mapping[c] for c in leaf_data]
    ax2.plot(idxs, marker="o")
    ax2.set_yticks([0,1,2])
    ax2.set_yticklabels(["Verde","Amarillo","Seco"])
    st.pyplot(fig2)

