"""
config.py — Tunable parameters for Hand Gesture Mouse Control
"""
import pyautogui

# ── Camera ────────────────────────────────────────────────────────────────────
CAMERA_DEFAULT_INDEX = 0          # Primary webcam index (auto-scans 0-5)
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# ── Screen ────────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = pyautogui.size()

# Active region of the camera frame used for cursor mapping (centre crop)
# Values are fractions of the frame (0.0 – 1.0)
ACTIVE_LEFT   = 0.10
ACTIVE_RIGHT  = 0.90
ACTIVE_TOP    = 0.10
ACTIVE_BOTTOM = 0.90

# ── Smoothing ─────────────────────────────────────────────────────────────────
SMOOTHING_FACTOR  = 0.25       # EMA alpha: lower = smoother but laggier

# ── Gesture Thresholds ────────────────────────────────────────────────────────
# Distances are normalised (0–1) relative to frame size
PINCH_THRESHOLD         = 0.045   # Index–Thumb → left click
RIGHT_CLICK_THRESHOLD   = 0.048   # Index–Middle tap → right click
DRAG_HOLD_FRAMES        = 12      # Frames pinch must be held before drag starts
SCROLL_SPEED            = 15      # Pixels per scroll tick

# ── Debounce ──────────────────────────────────────────────────────────────────
CLICK_COOLDOWN_FRAMES   = 18      # Min frames between consecutive clicks
RIGHT_CLICK_COOLDOWN    = 22

# ── MediaPipe ─────────────────────────────────────────────────────────────────
MP_MAX_HANDS            = 1
MP_DETECTION_CONFIDENCE = 0.55   # lowered for easier real-world detection
MP_TRACKING_CONFIDENCE  = 0.55

# ── Overlay / Display ─────────────────────────────────────────────────────────
SHOW_OVERLAY            = True
SHOW_FPS                = True
WINDOW_TITLE            = "Hand Gesture Mouse Control  |  Press Q to quit"
