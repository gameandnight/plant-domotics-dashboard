# Plant Domotics Dashboard

Dashboard en tiempo real de sensores de planta usando MQTT y Streamlit.

## Archivos
- `streamlit_app.py`: Interfaz principal.
- `humidity.py`, `temperature.py`, `color.py`: Clientes que publican datos de prueba.
- `motor.py`: Control de motor y alertas.
- `broker.py`: Cliente de monitorización de todos los tópicos.
- `requirements.txt`: Dependencias.

## Uso
1. Define tus credenciales MQTT en `.streamlit/secrets.toml` (o en Streamlit Secrets).  
2. Ejecuta localmente con `streamlit run streamlit_app.py`.  
3. En producción, despliega en Streamlit Community Cloud.
