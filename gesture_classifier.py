"""
gesture_classifier.py — Rules-based gesture classification engine
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional
import config
from hand_detector import HandDetector, Landmark


class Gesture(Enum):
    NONE        = auto()   # No hand / unknown
    IDLE        = auto()   # Fist / unclear
    MOVE        = auto()   # Index only → move cursor
    LEFT_CLICK  = auto()   # Index–Thumb pinch tap
    RIGHT_CLICK = auto()   # Index–Middle tap
    DRAG        = auto()   # Pinch hold
    SCROLL_UP   = auto()   # Two fingers moving up
    SCROLL_DOWN = auto()   # Two fingers moving down


@dataclass
class GestureState:
    gesture: Gesture = Gesture.NONE
    cursor_x: float  = 0.5     # normalised 0–1
    cursor_y: float  = 0.5
    scroll_delta: int = 0


class GestureClassifier:
    """
    Stateful gesture classifier.  Call `classify(landmarks)` each frame.
    """

    def __init__(self):
        # Internal counters
        self._pinch_hold_frames      = 0
        self._click_cooldown         = 0
        self._right_click_cooldown   = 0

        # Scroll tracking
        self._prev_middle_y: Optional[float] = None

        # Previous finger positions for velocity
        self._prev_index_y: Optional[float] = None

    # ─── Public API ───────────────────────────────────────────────────────────

    def classify(self, landmarks: Optional[List[Landmark]]) -> GestureState:
        """Main entry — returns a GestureState for the current frame."""
        self._tick_cooldowns()

        if landmarks is None:
            self._reset_hold()
            return GestureState(gesture=Gesture.NONE)

        fingers = HandDetector.fingers_up(landmarks)
        index_up, middle_up, ring_up, pinky_up = fingers

        idx_tip    = landmarks[HandDetector.INDEX_TIP]
        mid_tip    = landmarks[HandDetector.MIDDLE_TIP]
        thumb_tip  = landmarks[HandDetector.THUMB_TIP]

        pinch_dist        = HandDetector.distance(idx_tip, thumb_tip)
        idx_mid_dist      = HandDetector.distance(idx_tip, mid_tip)

        state = GestureState(cursor_x=idx_tip.x, cursor_y=idx_tip.y)

        # ── Right-click: index + middle both up and TAPPING together ──────────
        if (
            index_up and middle_up
            and not ring_up and not pinky_up
            and idx_mid_dist < config.RIGHT_CLICK_THRESHOLD
            and self._right_click_cooldown == 0
        ):
            state.gesture = Gesture.RIGHT_CLICK
            self._right_click_cooldown = config.RIGHT_CLICK_COOLDOWN
            self._pinch_hold_frames = 0
            return state

        # ── Scroll: index + middle both up, NOT tapping (spread apart) ────────
        if index_up and middle_up and not ring_up and not pinky_up:
            if idx_mid_dist >= config.RIGHT_CLICK_THRESHOLD:
                delta = self._scroll_delta(mid_tip.y)
                if delta != 0:
                    state.gesture = Gesture.SCROLL_UP if delta < 0 else Gesture.SCROLL_DOWN
                    state.scroll_delta = abs(delta)
                else:
                    state.gesture = Gesture.IDLE
                self._reset_hold()
                return state

        # ── Pinch (index+thumb) ───────────────────────────────────────────────
        if pinch_dist < config.PINCH_THRESHOLD:
            self._pinch_hold_frames += 1

            if self._pinch_hold_frames >= config.DRAG_HOLD_FRAMES:
                state.gesture = Gesture.DRAG
                return state

            if self._pinch_hold_frames == 1 and self._click_cooldown == 0:
                state.gesture = Gesture.LEFT_CLICK
                self._click_cooldown = config.CLICK_COOLDOWN_FRAMES
                return state

            state.gesture = Gesture.IDLE
            return state

        # ── Move: index up, others down ───────────────────────────────────────
        if index_up and not middle_up and not ring_up and not pinky_up:
            self._reset_hold()
            state.gesture = Gesture.MOVE
            return state

        # ── Fallback ──────────────────────────────────────────────────────────
        self._reset_hold()
        state.gesture = Gesture.IDLE
        return state

    # ─── Private ──────────────────────────────────────────────────────────────

    def _tick_cooldowns(self):
        if self._click_cooldown > 0:
            self._click_cooldown -= 1
        if self._right_click_cooldown > 0:
            self._right_click_cooldown -= 1

    def _reset_hold(self):
        self._pinch_hold_frames = 0

    def _scroll_delta(self, current_y: float) -> int:
        """Return scroll direction based on middle fingertip Y velocity."""
        if self._prev_middle_y is None:
            self._prev_middle_y = current_y
            return 0
        delta = current_y - self._prev_middle_y
        self._prev_middle_y = current_y
        SCROLL_THRESH = 0.012
        if delta < -SCROLL_THRESH:
            return -1   # moving up
        if delta > SCROLL_THRESH:
            return 1    # moving down
        return 0
