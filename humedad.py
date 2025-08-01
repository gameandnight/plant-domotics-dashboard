import os
import paho.mqtt.client as mqtt
import random
import time

# Configuración del broker MQTT desde variables de entorno
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

# Topic donde se publicará la humedad
topic = "plant/humidity"

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
        # Generar un valor de humedad aleatorio entre 10% y 90%
        humidity = random.uniform(10, 90)
        print(f"Publicando humedad: {humidity:.2f}%")
        client.publish(topic, humidity)
        time.sleep(5)
except KeyboardInterrupt:
    print("Cliente de humedad detenido")
    client.loop_stop()
