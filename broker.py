import os
import paho.mqtt.client as mqtt

# Configuración del broker MQTT desde variables de entornoroker = os.getenv("MQTT_BROKER", "localhost")
port = int(os.getenv("MQTT_PORT", 1883))

# Callback cuando el cliente recibe una respuesta CONNACK del servidor
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado al broker MQTT ({broker}:{port}) con código {rc}")
        # Suscribirse a todos los topics relevantes
        topics = [
            ("plant/temperature", 0),
            ("plant/humidity",    0),
            ("plant/water_motor", 0),
            ("plant/alerts",      0),
            ("plant/leaf_color",  0)
        ]
        client.subscribe(topics)
    else:
        print(f"Error al conectar: {rc}")

# Callback para cuando se recibe un mensaje PUBLISH del servidor
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")

    if msg.topic == "plant/temperature":
        temperature = float(payload)
        print(f"Topic: {msg.topic} | Temperatura: {temperature:.2f}°C")

    elif msg.topic == "plant/humidity":
        humidity = float(payload)
        print(f"Topic: {msg.topic} | Humedad: {humidity:.2f}%")

    elif msg.topic == "plant/water_motor":
        print(f"Topic: {msg.topic} | Estado del motor de agua: {payload}")

    elif msg.topic == "plant/alerts":
        print(f"⚠️ ALERTA RECIBIDA: {payload}")

    elif msg.topic == "plant/leaf_color":
        print(f"Topic: {msg.topic} | Color de hojas: {payload}")

    else:
        print(f"Topic desconocido: {msg.topic} | Mensaje: {payload}")

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker y arrancar loop permanente
client.connect(broker, port, 60)
client.loop_forever()
