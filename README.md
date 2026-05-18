# 🌸 FlowersGarden: Jardín Virtual con IA

Este proyecto es una aplicación de Realidad Aumentada interactiva en tiempo real que permite hacer florecer imágenes en las puntas de los dedos y controlar la interfaz mediante gestos espaciales. 

---

## ⚙️ ¿Cómo funciona?

El sistema rastrea las coordenadas de la punta del dedo índice. Al detectar una colisión geométrica con los botones circulares superiores, cambia dinámicamente el tipo de flor seleccionada sin usar el mouse.
   
## 🛠️ Requisitos del Sistema

Para correr este jardín en tu computadora, vas a necesitar:

* **Python 3.14 o superior**
* Una cámara web 
* El archivo de configuración de MediaPipe: `hand_landmarker.task`

### Instalar las librerías necesarias:
Ejecuta este comando en tu terminal para instalar las dependencias principales:

```bash
pip install opencv-python numpy mediapipe
