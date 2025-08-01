import os
import paho.mqtt.client as mqtt
import time

# Configuración del broker MQTT desde variables de entorno
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

# Definición de topics
HUMIDITY_TOPIC = "plant/humidity"
MOTOR_TOPIC = "plant/water_motor"
ALERT_TOPIC = "plant/alerts"

# Variable global para almacenar la última lectura de humedad
humidity = None

# Callback cuando se recibe un mensaje

def on_message(client, userdata, msg):
    global humidity
    try:
        humidity = float(msg.payload.decode())
        print(f"Humedad recibida: {humidity:.2f}%")
    except ValueError:
        print("Error al convertir la humedad recibida.")

# Callback de conexión
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado al broker MQTT ({BROKER}:{PORT}) con código {rc}")
        client.subscribe(HUMIDITY_TOPIC)
    else:
        print(f"Error al conectar al broker: {rc}")

# Inicializar cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        if humidity is not None:
            # Control del motor de agua
            if humidity < 40:
                print(f"Humedad baja ({humidity:.2f}%), encendiendo motor de agua...")
                client.publish(MOTOR_TOPIC, "ENCENDER")
            else:
                print(f"Humedad suficiente ({humidity:.2f}%), el motor de agua está apagado.")
                client.publish(MOTOR_TOPIC, "APAGAR")

            # Publicar alertas
            if humidity < 30:
                alert_msg = "⚠️ ALERTA: Humedad críticamente baja. Se recomienda revisar el sistema."
            else:
                alert_msg = "Sistema funcionando con normalidad"
            print(alert_msg)
            client.publish(ALERT_TOPIC, alert_msg)

        time.sleep(5)
except KeyboardInterrupt:
    print("Cliente del motor de agua detenido")
    client.loop_stop()
    client.disconnect()
