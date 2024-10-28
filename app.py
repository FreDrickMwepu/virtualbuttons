import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Define button properties
button_width = 200
button_height = 100
button_spacing = 20  # Space between buttons

# Define button positions, sizes, and colors dynamically
buttons = []
num_buttons = 5  # Number of buttons
start_x = 100
start_y = 100
colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 255, 255)]  # Red, Blue, Green, Yellow, White

for i in range(num_buttons):
    x = start_x
    y = start_y + i * (button_height + button_spacing)
    buttons.append({"pos": (x, y), "size": (button_width, button_height), "label": f"Button {i + 1}", "color": colors[i]})

# Function to draw buttons
def draw_buttons(image, buttons):
    for button in buttons:
        x, y = button["pos"]
        w, h = button["size"]
        color = button["color"]
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, button["label"], (x + 10, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

# Function to check if a point is inside a button
def is_point_in_button(point, button):
    x, y = button["pos"]
    w, h = button["size"]
    px, py = point
    return x <= px <= x + w and y <= py <= y + h

# Capture video from webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect hands
    result = hands.process(rgb_frame)

    # Draw buttons
    draw_buttons(frame, buttons)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check if the index finger tip is over any button
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, _ = frame.shape
            finger_pos = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))

            for button in buttons:
                if is_point_in_button(finger_pos, button):
                    cv2.putText(frame, f"{button['label']} Pressed", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow('Virtual Buttons', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()