# 🖐️ Gesture Control Mouse

> Control your computer mouse smoothly and contactlessly using real-time hand gestures captured via your webcam, powered by **MediaPipe**, **OpenCV**, and **PyAutoGUI**, complete with a **live interactive web dashboard**!

---

## 🌟 Highlights

- **✨ Touchless Cursor Navigation**: Move the mouse naturally with fluid Exponential Moving Average (EMA) smoothing.
- **👆 Intuitive Gestures**: Left click, right click, click & drag, and vertical scrolling with zero physical contact.
- **🌐 Real-Time Web Dashboard**: Built-in Flask dashboard (`localhost:5000`) showing live gesture states, SVG hand visualizers, FPS meter, and system status.
- **⚡ Smart Camera Engine**: Automatically probes and selects the best active camera interface (DirectShow, Media Foundation, Default) with live-motion verification.
- **🎛️ Fully Configurable**: Tweak smoothing factors, active screen margins, gesture distance thresholds, and cooldown timings via `config.py`.

---

## 🏗️ Architecture

```
                      ┌──────────────────────┐
                      │   Webcam Stream      │
                      └──────────┬───────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │  OpenCV Frame Flip   │
                      └──────────┬───────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │ MediaPipe 21 Joints  │
                      └──────────┬───────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │  Gesture Classifier  │
                      └────┬────────────┬────┘
                           │            │
            ┌──────────────┘            └──────────────┐
            ▼                                          ▼
┌─────────────────────────┐               ┌─────────────────────────┐
│     Mouse Controller    │               │    Flask Web Server     │
│   (EMA Smooth & Action) │               │       (/api/gesture)    │
└───────────┬─────────────┘               └────────────┬────────────┘
            │                                          │
            ▼                                          ▼
┌─────────────────────────┐               ┌─────────────────────────┐
│     OS Mouse Driver     │               │   Live Web Dashboard    │
│  (Click, Drag, Scroll)  │               │   (localhost:5000)      │
└─────────────────────────┘               └─────────────────────────┘
```

---

## ✋ Supported Gestures

| Gesture | Hand Pose | Mouse Action | Description |
| :--- | :--- | :--- | :--- |
| **Move Cursor** | **Index finger ONLY** extended | Move Cursor | Direct 1:1 mapped coordinate tracking with EMA jitter smoothing. |
| **Left Click** | **Index + Thumb pinch tap** | Single Left Click | Pinching index and thumb briefly triggers a left-click with debounce protection. |
| **Right Click** | **Index + Middle tips touching** | Single Right Click | Raising index and middle fingers together and tapping tips triggers a right-click. |
| **Scroll Up / Down** | **Index + Middle spread apart** | Scroll Wheel Up / Down | Spread index and middle fingers; move your hand upward to scroll up or downward to scroll down. |
| **Click & Drag** | **Index + Thumb pinch & hold** | Hold Left Click & Drag | Pinching for 12+ frames initiates click-and-drag. Release the pinch to drop. |
| **Idle / Pause** | **Closed Fist** | Pause Tracking | Closing fingers into a fist pauses cursor movement without exiting. |

---

## ⌨️ In-App Hotkeys

| Key | Function |
| :---: | :--- |
| <kbd>P</kbd> | **Pause / Resume** mouse control |
| <kbd>S</kbd> | **Toggle skeleton** overlay on OpenCV HUD |
| <kbd>Q</kbd> or <kbd>ESC</kbd> | **Quit** application and release camera |

---

## 🚀 Getting Started & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Santhosh939s/gesture-control-mouse.git
cd gesture-control-mouse
```

### 2. Install Dependencies
Make sure you have Python 3.9+ (Python 3.10+ recommended) installed.
```bash
pip install -r requirements.txt
```

---

## 💻 How to Run

### Method 1: One-Click Launcher (Windows)
Double-click `run.bat` or execute in terminal:
```cmd
.\run.bat
```

### Method 2: Command Line
```bash
python main.py
```

Once started:
1. The camera window will appear with an on-screen HUD.
2. The web dashboard will automatically open in your default browser at **`http://localhost:5000`**.

---

## 📁 Project Structure

```
gesture-control-mouse/
├── config.py              # Tunable system, camera, smoothing, and gesture thresholds
├── hand_detector.py       # MediaPipe Hands wrapper (21 3D landmarks & joint metrics)
├── gesture_classifier.py  # Rule-based gesture state classification engine
├── mouse_controller.py    # PyAutoGUI integration with coordinate mapping & EMA filter
├── server.py              # Flask server hosting the REST API bridge
├── main.py                # Main orchestration loop and OpenCV HUD overlay
├── run.bat                # Windows quick launcher batch file
├── requirements.txt       # Python package dependencies
├── website/
│   └── index.html         # Live dashboard with SVG gesture animations & stats
└── README.md              # Project documentation
```

---

## ⚙️ Configuration Options (`config.py`)

You can customize the application behavior in `config.py`:

```python
# Screen active region (fraction of frame used for screen mapping)
ACTIVE_LEFT   = 0.10
ACTIVE_RIGHT  = 0.90
ACTIVE_TOP    = 0.10
ACTIVE_BOTTOM = 0.90

# Exponential Moving Average smoothing (0.0 = max smoothing/lag, 1.0 = raw/jittery)
SMOOTHING_FACTOR = 0.25

# Gesture distance thresholds (normalized 0.0 - 1.0)
PINCH_THRESHOLD       = 0.045   # Index–Thumb pinch
RIGHT_CLICK_THRESHOLD = 0.048   # Index–Middle tap
DRAG_HOLD_FRAMES      = 12      # Frames pinch must be held before drag starts
SCROLL_SPEED          = 15      # Pixels per scroll tick
```

---

## 🛠️ Troubleshooting & Tips

- **Camera Permission / Access Denied**: Ensure Windows Camera Privacy Settings (*Settings > Privacy & Security > Camera*) have "Let desktop apps access your camera" enabled.
- **Lighting & Background**: Ensure adequate lighting and contrast between your hand and the background for optimal MediaPipe detection.
- **Jittery Cursor**: Lower `SMOOTHING_FACTOR` (e.g. `0.15` to `0.20`) in `config.py` for smoother movement.
- **Reaching Screen Edges**: Adjust `ACTIVE_LEFT`, `ACTIVE_RIGHT`, `ACTIVE_TOP`, `ACTIVE_BOTTOM` to shrink/expand the active bounding region.

---

## 📜 License

This project is licensed under the MIT License. Feel free to use and customize it!
