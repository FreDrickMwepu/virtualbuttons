import streamlit as st
import cv2
import mediapipe as mp
import numpy as np


# Set page config for dark theme
st.set_page_config(
    page_title="Virtual LED Controller",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Button configuration
buttons = [
    {"label": "Red LED", "color": (0, 0, 255), "command": "R"},
    {"label": "Green LED", "color": (0, 255, 0), "command": "G"},
    {"label": "Blue LED", "color": (255, 0, 0), "command": "B"}
]

# Initialize session state for buttons
for button in buttons:
    state_key = f"{button['label']}_state"
    if state_key not in st.session_state:
        st.session_state[state_key] = False

def process_frame(frame, buttons):
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    for button in buttons:
        x, y = 100, buttons.index(button) * 120 + 100
        cv2.rectangle(frame, (x, y), (x + 200, y + 100), button["color"], 2)
        cv2.putText(frame, button["label"], (x + 10, y + 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, button["color"], 2)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, _ = frame.shape
            x, y = int(index_tip.x * w), int(index_tip.y * h)
            
            for button in buttons:
                button_y = buttons.index(button) * 120 + 100
                if 100 <= x <= 300 and button_y <= y <= button_y + 100:
                    st.session_state[f"{button['label']}_state"] = not st.session_state[f"{button['label']}_state"]
    
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Streamlit UI
st.title("Virtual LED Controller")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Camera Feed")
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend
    frame_placeholder = st.empty()
    
    while True:
        ret, frame = camera.read()
        if not ret:
            st.error("Failed to access camera")
            break
            
        processed_frame = process_frame(frame, buttons)
        frame_placeholder.image(processed_frame, channels="RGB")

with col2:
    st.header("LED Status")
    for button in buttons:
        button_label = button['label']
        state_key = f"{button_label}_state"
        if state_key not in st.session_state:
            st.session_state[state_key] = False
        state = 'ON' if st.session_state[state_key] else 'OFF'
        st.write(f"{button_label}: {state}")

# Cleanup
camera.release()
cv2.destroyAllWindows()