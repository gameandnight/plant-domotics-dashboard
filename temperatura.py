import os
import paho.mqtt.client as mqtt
import random
import time

# Configuración del broker MQTT desde variables de entorno
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

# Topic donde se publicará la temperatura
topic = "plant/temperature"

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
        # Generar un valor de temperatura aleatorio entre 15 y 30°C
        temperature = random.uniform(15, 30)
        print(f"Publicando temperatura: {temperature:.2f}°C")
        client.publish(topic, temperature)
        time.sleep(5)
except KeyboardInterrupt:
    print("Cliente de temperatura detenido")
    client.loop_stop()
