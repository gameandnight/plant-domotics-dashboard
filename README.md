# Plant Domotics Dashboard

Dashboard en tiempo real de sensores de planta usando MQTT y Streamlit.

## Archivos
- `streamlit_app.py`: Interfaz principal.
- `humidity.py`, `temperature.py`, `color.py`: Clientes que publican datos de prueba.
- `motor.py`: Control de motor y alertas.
- `broker.py`: Cliente de monitorización de todos los tópicos.
- `requirements.txt`: Dependencias.

## Despliegue y Uso

1. **Localmente**  
   - Crea el archivo de secretos en `.streamlit/secrets.toml` (no subirlo al repo):
     ```toml
     MQTT_BROKER = "tu.broker.publico"
     MQTT_PORT   = "1883"
     ```
   - Ejecuta:
     ```bash
     streamlit run streamlit_app.py
     ```

2. **En producción (Streamlit Community Cloud)**  
   - Sube tu código a GitHub (rama `main`).  
   - En Streamlit Cloud, crea una nueva app apuntando a ese repo.  
   - En **Settings → Secrets**, añade:
     ```
     MQTT_BROKER = tu.broker.publico
     MQTT_PORT   = 1883
     ```
   - Haz clic en **Deploy**.

## Descripción

- Se publican datos de prueba de **humedad**, **temperatura** y **color de hojas** desde scripts Python que usan `paho-mqtt`.  
- El script `motor.py` controla un motor de riego según la humedad y envía alertas críticas.  
- `streamlit_app.py` muestra gráficas y valores en tiempo real.

## Licencia

MIT

