"""
diagnose.py — Standalone camera + MediaPipe diagnostic.
Run this to see raw camera feed AND test hand detection directly.
Press Q to quit.
"""
import cv2
import mediapipe as mp
import numpy as np

print("=== DIAGNOSIS START ===")
print(f"OpenCV  : {cv2.__version__}")
print(f"MediaPipe: {mp.__version__}")

# ── Open camera ──────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("FAIL: Camera 0 (DSHOW) not opened. Trying index 1...")
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("FAIL: No camera found at all!")
    exit(1)

ret, test_frame = cap.read()
print(f"Camera  : {'OK' if ret else 'FAIL'}, shape={test_frame.shape if ret else None}")

# ── MediaPipe hands ───────────────────────────────────────────────────────────
mp_hands  = mp.solutions.hands
mp_draw   = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,   # LOWER threshold for easier detection
    min_tracking_confidence=0.5,
)

print("\nCamera is open. Put your HAND clearly in front of the camera.")
print("You should see your hand skeleton drawn on screen.")
print("Press Q to quit.\n")

frame_count   = 0
detect_count  = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame read failed!")
        break

    frame_count += 1
    frame = cv2.flip(frame, 1)

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    result = hands.process(rgb)
    rgb.flags.writeable = True

    detected = result.multi_hand_landmarks is not None

    if detected:
        detect_count += 1
        for hand_lm in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, hand_lm,
                mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style(),
            )

    # ── HUD ──
    status = "HAND DETECTED!" if detected else "No hand - show hand to camera"
    color  = (0, 220, 60) if detected else (60, 60, 220)
    cv2.rectangle(frame, (0,0), (frame.shape[1], 50), (15,15,15), -1)
    cv2.putText(frame, status, (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    rate = f"Detected: {detect_count}/{frame_count} frames"
    cv2.putText(frame, rate, (12, frame.shape[0]-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120,120,120), 1)

    cv2.imshow("DIAGNOSIS - Hand Detection Test | Q to quit", frame)

    if frame_count % 30 == 0:
        print(f"  Frame {frame_count}: detected={detected}  rate={detect_count}/{frame_count}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"\n=== RESULT: Detected hand in {detect_count}/{frame_count} frames ===")
