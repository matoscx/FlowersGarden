import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

# --- CONFIGURACIÓN DE MEDIAPIPE ---
model_path = "hand_landmarker.task"
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2) 
detector = vision.HandLandmarker.create_from_options(options)

# --- CARGA DE ASSETS ---
def load_flower(path, size=(100, 100)):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return np.zeros((*size, 4), dtype=np.uint8)
    return cv2.resize(img, size)

flower_files = ["flower_yellow.png", "flower_blue.png", "flower_violet.png", "flower_pink.png"]
flowers = [load_flower(f) for f in flower_files]
flower_index = 0  # Comienza en Amarillo

# --- CONFIGURACIÓN DE BOTONES CIRCULARES (Centros y Radio) ---
# Tonos Pastel en BGR: Amarillo, Azul cielo, Violeta suave, Rosado pastel
PASTEL_COLORS = [(180, 255, 255), (255, 220, 180), (255, 180, 220), (220, 180, 255)]
BUTTON_CENTERS = [(50, 40), (150, 40), (250, 40), (350, 40)]
BUTTON_RADIUS = 30
WINDOW_NAME = "Jardin Virtual de Carol"

def overlay_image(background, overlay, x, y):
    bh, bw = background.shape[:2]
    oh, ow = overlay.shape[:2]
    x1, y1 = x - ow // 2, y - oh
    x2, y2 = x1 + ow, y1 + oh
    if x1 < 0 or y1 < 0 or x2 > bw or y2 > bh:
        return background
    overlay_img = overlay[:, :, :3]
    mask = overlay[:, :, 3] / 255.0
    for c in range(3):
        background[y1:y2, x1:x2, c] = (background[y1:y2, x1:x2, c] * (1 - mask) + overlay_img[:, :, c] * mask)
    return background

cap = cv2.VideoCapture(0)
cv2.namedWindow(WINDOW_NAME)

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # --- DIBUJAR BOTONES CIRCULARES EN PANTALLA ---
    for i, center in enumerate(BUTTON_CENTERS):
        # Indicador estético para el botón activo (Borde exterior negro sutil)
        if i == flower_index:
            cv2.circle(frame, center, BUTTON_RADIUS + 4, (0, 0, 0), 2)
            
        # Círculo relleno del color pastel
        cv2.circle(frame, center, BUTTON_RADIUS, PASTEL_COLORS[i], -1)
        # Borde blanco fino para acabado limpio
        cv2.circle(frame, center, BUTTON_RADIUS, (255, 255, 255), 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:
            
            # --- DETECCIÓN TOUCH VIRTUAL (Usando la punta del índice: ID 8) ---
            index_tip = hand_landmarks[8]
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            
            for i, center in enumerate(BUTTON_CENTERS):
                # Calcular distancia entre el dedo índice y el centro del botón
                touch_distance = math.sqrt((ix - center[0])**2 + (iy - center[1])**2)
                if touch_distance <= BUTTON_RADIUS:
                    flower_index = i  # Cambia el color de manera interactiva con el dedo

            # --- DISEÑO ESTÉTICO DE LAS MANOS (PUNTOS CON GLOW) ---
            # Definimos el color del brillo según la flor seleccionada
            current_glow_color = PASTEL_COLORS[flower_index]
            
            # Capa de brillo exterior (Círculo más grande detrás)
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 7, current_glow_color, -1)
                
            # Capa central blanca pura (Núcleo del punto)
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)

            # --- FLORES EN LAS PUNTAS ---
            tips_ids = [4, 8, 12, 16, 20]
            for tip_id in tips_ids:
                tx, ty = int(hand_landmarks[tip_id].x * w), int(hand_landmarks[tip_id].y * h)
                
                # Renderizar la flor del color seleccionado
                frame = overlay_image(frame, flowers[flower_index], tx, ty)

    cv2.imshow(WINDOW_NAME, frame)
    
    # --- CONTROL DE CIERRE ---
    # Verificar si cerraron la ventana desde la 'X'
    if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
        break
        
    # Detectar la tecla 'C' o 'c' para cerrar
    key = cv2.waitKey(1) & 0xFF
    if key == ord("c") or key == ord("C"): 
        break

cap.release()
cv2.destroyAllWindows()