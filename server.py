"""
server.py — Flask REST bridge for the live gesture dashboard website.
Runs in a background thread, exposes /api/gesture for the browser to poll.
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "website"))
CORS(app)

# ── Shared mutable state (written by main loop, read by Flask) ────────────────
gesture_state: dict = {
    "gesture":  "NONE",
    "label":    "No hand detected",
    "fps":      0,
    "paused":   False,
    "active":   False,   # True when webcam is running
}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/gesture")
def get_gesture():
    return jsonify(gesture_state)


def run_server(host: str = "localhost", port: int = 5000):
    """Start Flask (blocking).  Call in a daemon thread."""
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)          # suppress request logs
    app.run(host=host, port=port, debug=False, use_reloader=False)
