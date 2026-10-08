"""
mouse_controller.py — Translates GestureState into real mouse actions via PyAutoGUI
"""
import pyautogui
import config
from gesture_classifier import Gesture, GestureState


# Safety net: disable PyAutoGUI fail-safe corner detection during drag
pyautogui.FAILSAFE = True
pyautogui.PAUSE    = 0         # Remove built-in delay (we control timing via FPS)


class MouseController:
    """
    Consumes GestureState objects and drives the OS mouse accordingly.
    Applies exponential moving average smoothing to cursor position.
    """

    def __init__(self):
        self._smooth_x: float = config.SCREEN_W / 2
        self._smooth_y: float = config.SCREEN_H / 2
        self._dragging: bool  = False

    def update(self, state: GestureState) -> str:
        """
        Apply the gesture to the mouse.  Returns a human-readable status label
        for the overlay.
        """
        if state.gesture == Gesture.NONE:
            self._end_drag()
            return "No hand detected"

        if state.gesture == Gesture.IDLE:
            self._end_drag()
            return "Idle"

        # ── Cursor position (shared by MOVE, DRAG, LEFT_CLICK, RIGHT_CLICK) ──
        if state.gesture in (
            Gesture.MOVE, Gesture.LEFT_CLICK,
            Gesture.RIGHT_CLICK, Gesture.DRAG
        ):
            self._move_cursor(state.cursor_x, state.cursor_y)

        # ── Dispatch gesture ───────────────────────────────────────────────────
        if state.gesture == Gesture.MOVE:
            self._end_drag()
            return "Move"

        if state.gesture == Gesture.LEFT_CLICK:
            self._end_drag()
            pyautogui.click()
            return "LEFT CLICK ●"

        if state.gesture == Gesture.RIGHT_CLICK:
            self._end_drag()
            pyautogui.rightClick()
            return "RIGHT CLICK ◎"

        if state.gesture == Gesture.DRAG:
            if not self._dragging:
                pyautogui.mouseDown()
                self._dragging = True
            return "DRAG ✥"

        if state.gesture == Gesture.SCROLL_UP:
            pyautogui.scroll(config.SCROLL_SPEED)
            return "Scroll ↑"

        if state.gesture == Gesture.SCROLL_DOWN:
            pyautogui.scroll(-config.SCROLL_SPEED)
            return "Scroll ↓"

        return "—"

    # ─── Private ──────────────────────────────────────────────────────────────

    def _move_cursor(self, norm_x: float, norm_y: float):
        """Map normalised (0–1) hand position to screen coords with smoothing."""
        # Remap from active region to full screen
        ax = config.ACTIVE_LEFT
        bx = config.ACTIVE_RIGHT
        ay = config.ACTIVE_TOP
        by = config.ACTIVE_BOTTOM

        # Clamp and re-normalise
        rx = (norm_x - ax) / (bx - ax)
        ry = (norm_y - ay) / (by - ay)
        rx = max(0.0, min(1.0, rx))
        ry = max(0.0, min(1.0, ry))

        # Note: frame is already mirrored via cv2.flip(frame, 1) in main loop,
        # so norm_x maps directly to screen coordinates (moving hand right moves cursor right).
        target_x = rx * config.SCREEN_W
        target_y = ry * config.SCREEN_H

        # Exponential moving average
        α = config.SMOOTHING_FACTOR
        self._smooth_x = α * target_x + (1 - α) * self._smooth_x
        self._smooth_y = α * target_y + (1 - α) * self._smooth_y

        pyautogui.moveTo(int(self._smooth_x), int(self._smooth_y))

    def _end_drag(self):
        if self._dragging:
            pyautogui.mouseUp()
            self._dragging = False
