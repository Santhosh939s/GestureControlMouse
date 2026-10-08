"""
main.py — Hand Gesture Mouse Control System (with live web dashboard)
Entry point: opens webcam, runs detection loop, drives mouse, streams state to browser.

Controls:
  Q / ESC — quit
  P       — pause / resume mouse control
  S       — toggle overlay skeleton
"""
import time
import threading
import cv2
import numpy as np
import webbrowser

import config
import server as srv
from hand_detector import HandDetector
from gesture_classifier import GestureClassifier, Gesture
from mouse_controller import MouseController

# ── Colour palette ────────────────────────────────────────────────────────────
GESTURE_COLOURS = {
    Gesture.MOVE:        (0,  200,  80),
    Gesture.LEFT_CLICK:  (60,  60, 220),
    Gesture.RIGHT_CLICK: (0,  165, 255),
    Gesture.DRAG:        (200, 100, 255),
    Gesture.SCROLL_UP:   (0,  220, 180),
    Gesture.SCROLL_DOWN: (0,  220, 180),
    Gesture.IDLE:        (120, 120, 120),
    Gesture.NONE:        (60,  60,  60),
}
ACCENT  = (0,  220, 180)
DIM     = (100, 100, 100)
WHITE   = (230, 230, 230)
DARK    = (20,  20,  20)
WARN    = (0,  165, 255)


def open_camera():
    """
    Scans camera indices (0..5) using DirectShow, Media Foundation, and Default backends.
    Validates that the camera gives a LIVE (changing) video feed, avoiding frozen/virtual devices.
    """
    def is_live(cap, samples=5):
        """Returns True if camera feed is actually live (frames change over time)."""
        frames = []
        for _ in range(samples):
            ret, f = cap.read()
            if ret and f is not None:
                frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
            time.sleep(0.04)
        if len(frames) < 2:
            return False
        diffs = [np.mean(np.abs(frames[i+1] - frames[i])) for i in range(len(frames)-1)]
        motion = np.mean(diffs)
        return motion > 0.01

    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF,  "MediaFoundation"),
        (cv2.CAP_ANY,   "Default"),
    ]

    print("  Searching for active webcam...", flush=True)
    for idx in range(6):
        for backend, bname in backends:
            cap = cv2.VideoCapture(idx, backend)
            if cap.isOpened():
                time.sleep(0.3)
                ret, frame = cap.read()
                if ret and frame is not None:
                    if is_live(cap):
                        print(f"  SUCCESS: Found live camera at index {idx} ({bname}) — resolution {frame.shape[1]}x{frame.shape[0]}", flush=True)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_WIDTH)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
                        return cap
                    else:
                        print(f"  Camera {idx} ({bname}) opened but appears static/virtual, checking next...", flush=True)
                cap.release()

    return None


def draw_overlay(frame, landmarks, status_label, gesture, fps, paused, detector):
    h, w = frame.shape[:2]

    if landmarks and config.SHOW_OVERLAY:
        detector.draw(frame, landmarks)

    # Top bar
    cv2.rectangle(frame, (0, 0), (w, 52), DARK, -1)
    cv2.putText(frame, "GESTURE MOUSE", (12, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, ACCENT, 2, cv2.LINE_AA)
    if config.SHOW_FPS:
        cv2.putText(frame, f"FPS: {fps:.0f}", (w - 110, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, DIM, 1, cv2.LINE_AA)

    # Web link
    cv2.putText(frame, "Dashboard: localhost:5000", (w // 2 - 105, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (80, 160, 80), 1, cv2.LINE_AA)

    # Bottom bar
    bar_h = 54
    cv2.rectangle(frame, (0, h - bar_h), (w, h), DARK, -1)
    col = GESTURE_COLOURS.get(gesture, DIM)
    cv2.circle(frame, (18, h - bar_h // 2), 7, col, -1)
    cv2.putText(frame, status_label, (32, h - bar_h // 2 + 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, col, 2, cv2.LINE_AA)

    if paused:
        cv2.putText(frame, "PAUSED", (w - 100, h - bar_h // 2 + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, WARN, 2, cv2.LINE_AA)

    # Active region box
    x1 = int(config.ACTIVE_LEFT  * w);  x2 = int(config.ACTIVE_RIGHT  * w)
    y1 = int(config.ACTIVE_TOP   * h);  y2 = int(config.ACTIVE_BOTTOM * h)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 50, 50), 1)
    cv2.putText(frame, "[mirrored view]", (x1 + 4, y1 + 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (70, 70, 70), 1, cv2.LINE_AA)

    # Legend
    legend = [
        ("P  Pause  |  S  Skeleton  |  Q  Quit", DIM),
    ]
    for i, (t, c) in enumerate(legend):
        cv2.putText(frame, t, (12, h - bar_h - 10 - i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, c, 1, cv2.LINE_AA)

    return frame


def main():
    print("=" * 60)
    print("  Hand Gesture Mouse Control  +  Live Web Dashboard")
    print("=" * 60)

    # ── Start Flask server in background thread ────────────────────────────────
    flask_thread = threading.Thread(
        target=srv.run_server, kwargs={"host": "localhost", "port": 5000},
        daemon=True
    )
    flask_thread.start()
    print("  Dashboard -> http://localhost:5000")

    # ── Open browser after a short delay ──────────────────────────────────────
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:5000")
    threading.Thread(target=open_browser, daemon=True).start()

    # ── Initialise gesture pipeline ───────────────────────────────────────────
    detector   = HandDetector()
    classifier = GestureClassifier()
    controller = MouseController()

    cap = open_camera()
    if cap is None:
        print("ERROR: Could not open any camera. Check connections.")
        return

    paused  = False
    prev_t  = time.time()

    srv.gesture_state["active"] = True
    print("  Camera ready.  Show your hand!\n  Press Q to quit, P to pause, S to toggle skeleton.")
    print("-" * 60)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)

        now   = time.time()
        fps   = 1.0 / max(now - prev_t, 1e-6)
        prev_t = now

        landmarks = detector.process(frame)
        state     = classifier.classify(landmarks if not paused else None)

        if not paused:
            status = controller.update(state)
        else:
            status = "PAUSED"

        # ── Push to web dashboard ──────────────────────────────────────────────
        srv.gesture_state.update({
            "gesture": state.gesture.name,
            "label":   status,
            "fps":     round(fps, 1),
            "paused":  paused,
            "active":  True,
        })

        frame = draw_overlay(frame, landmarks, status, state.gesture, fps, paused, detector)
        cv2.imshow(config.WINDOW_TITLE, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        elif key == ord('p'):
            paused = not paused
            print(f"  [{'PAUSED' if paused else 'RESUMED'}]")
        elif key == ord('s'):
            config.SHOW_OVERLAY = not config.SHOW_OVERLAY

    srv.gesture_state["active"] = False
    cap.release()
    cv2.destroyAllWindows()
    print("\n  Goodbye!")


if __name__ == "__main__":
    main()
