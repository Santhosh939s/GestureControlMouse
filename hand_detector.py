"""
hand_detector.py — MediaPipe hand landmark detection wrapper
Compatible with mediapipe >= 0.10.x using the modern Hands solution.
"""
import cv2
import mediapipe as mp
from mediapipe.python.solutions import hands as mp_hands_module
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import drawing_styles as mp_styles
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
import config


@dataclass
class Landmark:
    x: float   # normalised 0–1
    y: float
    z: float


class HandDetector:
    """
    Wraps MediaPipe Hands to expose a clean list of 21 Landmark objects
    and helper utilities (finger state, distance, draw).
    """

    # MediaPipe landmark indices
    WRIST       = 0
    THUMB_CMC   = 1;  THUMB_MCP  = 2;  THUMB_IP   = 3;  THUMB_TIP   = 4
    INDEX_MCP   = 5;  INDEX_PIP  = 6;  INDEX_DIP  = 7;  INDEX_TIP   = 8
    MIDDLE_MCP  = 9;  MIDDLE_PIP = 10; MIDDLE_DIP = 11; MIDDLE_TIP  = 12
    RING_MCP    = 13; RING_PIP   = 14; RING_DIP   = 15; RING_TIP    = 16
    PINKY_MCP   = 17; PINKY_PIP  = 18; PINKY_DIP  = 19; PINKY_TIP   = 20

    # Tips and their corresponding PIP joints (for up/down detection)
    FINGER_TIPS = [INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
    FINGER_PIPS = [INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP]

    def __init__(self):
        self._hands = mp_hands_module.Hands(
            static_image_mode=False,
            max_num_hands=config.MP_MAX_HANDS,
            min_detection_confidence=config.MP_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MP_TRACKING_CONFIDENCE,
        )
        self._mp_hands  = mp_hands_module
        self._mp_draw   = mp_drawing
        self._mp_styles = mp_styles

        # Cache the last raw result for drawing
        self._last_result = None

    def process(self, frame_bgr: np.ndarray) -> Optional[List[Landmark]]:
        """
        Process a BGR frame. Returns a list of 21 Landmark objects if a hand
        is detected, otherwise None.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self._hands.process(rgb)
        rgb.flags.writeable = True

        self._last_result = result

        if not result.multi_hand_landmarks:
            return None

        lm_list = result.multi_hand_landmarks[0].landmark
        return [Landmark(lm.x, lm.y, lm.z) for lm in lm_list]

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def distance(lm_a: Landmark, lm_b: Landmark) -> float:
        """Euclidean distance in normalised space."""
        return np.hypot(lm_a.x - lm_b.x, lm_a.y - lm_b.y)

    @staticmethod
    def fingers_up(landmarks: List[Landmark]) -> List[bool]:
        """
        Returns [index_up, middle_up, ring_up, pinky_up].
        Thumb excluded (use thumb_up for thumb).
        """
        tips = HandDetector.FINGER_TIPS
        pips = HandDetector.FINGER_PIPS
        return [landmarks[tips[i]].y < landmarks[pips[i]].y for i in range(4)]

    @staticmethod
    def thumb_up(landmarks: List[Landmark]) -> bool:
        """Rough thumb-up check via x-axis (works for right hand)."""
        return landmarks[HandDetector.THUMB_TIP].x < landmarks[HandDetector.THUMB_IP].x

    def draw(self, frame: np.ndarray, landmarks: List[Landmark]) -> np.ndarray:
        """Draw hand skeleton on frame using the cached mediapipe result."""
        if self._last_result and self._last_result.multi_hand_landmarks:
            for hand_lm in self._last_result.multi_hand_landmarks:
                self._mp_draw.draw_landmarks(
                    frame,
                    hand_lm,
                    self._mp_hands.HAND_CONNECTIONS,
                    self._mp_styles.get_default_hand_landmarks_style(),
                    self._mp_styles.get_default_hand_connections_style(),
                )
        return frame
