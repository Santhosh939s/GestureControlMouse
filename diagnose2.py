"""
diagnose2.py - Pure text diagnostic, no window needed.
Saves 5 test frames as images so we can see what the camera sees.
"""
import cv2, sys, os, time
import mediapipe as mp
import numpy as np

print("=== HAND GESTURE SYSTEM DIAGNOSTIC ===", flush=True)
print(f"OpenCV   : {cv2.__version__}", flush=True)
print(f"MediaPipe: {mp.__version__}", flush=True)
print(f"Python   : {sys.version}", flush=True)

# ── Step 1: Open camera ───────────────────────────────────────────────────────
print("\n[1] Opening camera...", flush=True)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
time.sleep(1)  # let camera warm up

if not cap.isOpened():
    print("    FAIL: Camera 0 DSHOW not opened", flush=True)
    sys.exit(1)

ret, frame = cap.read()
if not ret or frame is None:
    print("    FAIL: Could not read frame", flush=True)
    sys.exit(1)

h, w = frame.shape[:2]
print(f"    OK: Camera opened. Frame size = {w}x{h}", flush=True)

# Save raw frame so we can SEE what camera sees
out_dir = os.path.dirname(os.path.abspath(__file__))
raw_path = os.path.join(out_dir, "debug_raw_frame.jpg")
cv2.imwrite(raw_path, frame)
print(f"    Saved raw frame -> debug_raw_frame.jpg", flush=True)

# ── Step 2: Test brightness ────────────────────────────────────────────────────
print("\n[2] Checking image brightness...", flush=True)
gray       = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
brightness = gray.mean()
print(f"    Average brightness: {brightness:.1f}/255", flush=True)
if brightness < 30:
    print("    WARNING: Image is very dark! Check your lighting.", flush=True)
elif brightness > 230:
    print("    WARNING: Image is very bright/overexposed!", flush=True)
else:
    print("    OK: Brightness looks normal.", flush=True)

# ── Step 3: MediaPipe detection on 30 frames ──────────────────────────────────
print("\n[3] Running MediaPipe on 30 frames (keep your hand in frame)...", flush=True)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.4,   # very low threshold
    min_tracking_confidence=0.4,
)

detected_frames = 0
total_frames    = 30

for i in range(total_frames):
    ret, frame = cap.read()
    if not ret:
        print(f"    Frame {i}: read FAILED", flush=True)
        continue

    frame = cv2.flip(frame, 1)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        detected_frames += 1
        # Save the first detected frame with skeleton
        if detected_frames == 1:
            from mediapipe.python.solutions import drawing_utils as mp_draw
            from mediapipe.python.solutions import drawing_styles as mp_styles
            vis = frame.copy()
            for lm in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    vis, lm,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )
            det_path = os.path.join(out_dir, "debug_detected_hand.jpg")
            cv2.imwrite(det_path, vis)
            print(f"    HAND DETECTED at frame {i}! Saved -> debug_detected_hand.jpg", flush=True)

    if i % 10 == 9:
        print(f"    Progress: {i+1}/{total_frames} | Detected in {detected_frames} frames so far", flush=True)

    time.sleep(0.033)  # ~30fps

cap.release()

# ── Result ────────────────────────────────────────────────────────────────────
print(f"\n=== RESULT ===", flush=True)
print(f"Detected hand in {detected_frames}/{total_frames} frames ({detected_frames/total_frames*100:.0f}%)", flush=True)

if detected_frames == 0:
    print("\n  DIAGNOSIS: MediaPipe could NOT detect your hand.", flush=True)
    print("  Possible causes:", flush=True)
    print("  1. Hand was not in camera view during the test", flush=True)
    print("  2. Poor lighting (check debug_raw_frame.jpg)", flush=True)
    print("  3. Camera showing wrong source (virtual camera?)", flush=True)
    print("  4. Hand too close or too far from camera", flush=True)
else:
    print("\n  DIAGNOSIS: MediaPipe IS working! Hand detection OK.", flush=True)
    print("  Issue may be in gesture classification thresholds.", flush=True)
