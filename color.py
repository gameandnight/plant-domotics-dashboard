import os
import paho.mqtt.client as mqtt
import random
import time

# Configuración del broker MQTT desde variables de entorno
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

# Topic donde se publicará el color de las hojas
topic = "plant/leaf_color"

# Callback cuando el cliente se conecta al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado al broker MQTT ({BROKER}:{PORT}) con código {rc}")
    else:
        print(f"Error al conectar al broker: {rc}")

# Crear cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)

# Iniciar loop en segundo plano
client.loop_start()

try:
    while True:
        # Generar un valor aleatorio para el color de las hojas
        leaf_color = random.choice(["Verde", "Amarillo", "Seco"])
        print(f"Publicando color de hojas: {leaf_color}")
        client.publish(topic, leaf_color)
        time.sleep(5)
except KeyboardInterrupt:
    print("Cliente de color de hojas detenido")
    client.loop_stop()
