import logging
from time import sleep

import pyautogui
import pynput
import pyperclip
from pylayout import Layout
from pynput.keyboard import Key
from pynput.mouse import Button

logger = logging.getLogger("keymouse")
logger.setLevel(logging.INFO)

logging_format = "%(asctime)s %(levelname)+8s %(name)s: %(message)s"
formatter = logging.Formatter(logging_format, "%H:%M:%S")
stream = logging.StreamHandler()
stream.setFormatter(formatter)
logger.addHandler(stream)


KEYS = {
    "cmd": Key.cmd,
    "cmd_l": Key.cmd_l,
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "tab": Key.tab,
    "shift": Key.shift,
    "backspace ": Key.backspace,
    "space": Key.space,
    "enter": Key.enter,
    "esc": Key.esc,
    "down": Key.down,
    "up": Key.up,
    "left": Key.left,
    "right": Key.right,
    "f1": Key.f1,
    "f2": Key.f2,
    "f3": Key.f3,
    "f4": Key.f4,
    "f5": Key.f5,
    "f6": Key.f6,
    "f7": Key.f7,
    "f8": Key.f8,
    "f9": Key.f9,
    "f10": Key.f10,
    "f11": Key.f11,
    "f12": Key.f12,
}

BUTTONS = {
    "left": Button.left,
    "middle": Button.middle,
    "right": Button.right,
}


class KeyMouse:
    def __init__(self) -> None:
        self._keyboard = pynput.keyboard.Controller()
        self._mouse = pynput.mouse.Controller()
        self.layout = Layout()
        self.clipboard = pyperclip
        # It is important to get layout as we need to change 0 thread language to 'us'
        cur_layout = self.layout.get()
        logger.debug(f"Layout: '{cur_layout}'")

    def press(self, key, interval=0.0, delay=0.0):
        logger.debug(f"Press: '{key}'")
        key = KEYS.get(key, key)
        sleep(delay)
        self._keyboard.press(key)
        sleep(interval)
        self._keyboard.release(key)

    def press_fixed(self, key, interval=0.0, delay=0.0):
        key = self._fix(key)
        logger.debug(f"Press fixed: '{key}'")
        key = KEYS.get(key, key)
        sleep(delay)
        self._keyboard.press(key)
        sleep(interval)
        self._keyboard.release(key)

    def hotkey(self, *keys, interval=0.0, delay=0.0, fixed=False):
        if fixed:
            keys = self._fix(*keys)
        logger.debug(f"Hotkey: '{keys}'")
        sleep(delay)
        for key in keys:
            if not isinstance(key, str):
                break
            if "click" in key:
                self._mouse.press(Button.left)
            else:
                key = KEYS.get(key, key)
                self._keyboard.press(key)
            sleep(interval)
        for key in keys:
            if not isinstance(key, str):
                raise TypeError(f"'{key}' key should be string")
            if "click" in key:
                self._mouse.release(Button.left)
            else:
                key = KEYS.get(key, key)
                self._keyboard.release(key)
            sleep(interval)

    def key_down(self, key):
        logger.debug(f"Key Down: '{key}'")
        key = KEYS.get(key, key)
        self._keyboard.press(key)

    def key_up(self, key):
        logger.debug(f"Key Up: '{key}'")
        key = KEYS.get(key, key)
        self._keyboard.release(key)

    def type(self, text, delay=0.0):
        logger.debug(f"Type: '{text}'")
        sleep(delay)
        self._keyboard.type(text)

    def scroll(self, v=0, h=0, delay=0.0):
        """v = y : vertical, h = x : horizontal"""
        logger.debug(f"Scroll: y={v} x={h}")
        v = v * (-1)
        sleep(delay)
        self._mouse.scroll(h, v)

    def click(self, x=None, y=None, button="left", clicks=1, duration=0.0, interval=0.0, tween=None, delay=0.0):
        """Move and click"""
        logger.debug(f"Click: x={x} y={y} button={button}")
        if not tween:
            tween = pyautogui.easeInOutQuad
        pyautogui.moveTo(x, y, duration=duration, tween=tween)
        sleep(delay)
        pyautogui.click(x, y, clicks, interval, button, tween=tween)

    def button_down(self, button="left"):
        logger.debug(f"Button Down: '{button}'")
        button = BUTTONS.get(button, button)
        self._mouse.press(button)

    def button_up(self, button="left"):
        logger.debug(f"Button Up: '{button}'")
        button = BUTTONS.get(button, button)
        self._mouse.release(button)

    def move(self, x, y, duration=0.0, tween=pyautogui.easeInOutQuad):
        logger.debug(f"Move: x={x} y={y}")
        pyautogui.moveTo(x, y, duration=duration, tween=tween)

    def drag(self, x, y, duration=0.0, tween=pyautogui.easeInOutQuad, button="left"):
        logger.debug(f"Drag: x={x} y={y}")
        pyautogui.dragTo(x, y, duration=duration, tween=tween, button=button)

    def position(self):
        return pyautogui.position()

    def print_mouse_position(self):
        try:
            while True:
                pos = pyautogui.position()
                positionStr = "X: " + str(pos.x).rjust(4) + " Y: " + str(pos.y).rjust(4)
                print(positionStr, end="")
                print("\b" * len(positionStr), end="", flush=True)
        except KeyboardInterrupt:
            print("\n")

    def size(self):
        pyautogui.size()

    def copy(self, delay=0.0):
        """`Ctrl + C` hotkey"""
        sleep(delay)
        self.hotkey("ctrl", "c", interval=0.1)
        logger.debug(f"Copy: '{pyperclip.paste()}'")

    def cut(self, delay=0.0):
        """`Ctrl + X` hotkey"""
        sleep(delay)
        self.hotkey("ctrl", "x", interval=0.1)
        logger.debug(f"Copy: '{pyperclip.paste()}'")

    def paste(self, delay=0.0):
        """`Ctrl + V` hotkey"""
        sleep(delay)
        self.hotkey("ctrl", "v", interval=0.1)

    def enter(self, delay=0.0):
        """`Enter` hotkey"""
        self.press("enter", delay=delay)

    def sleep(self, secs):
        sleep(secs)

    def _fix(self, *keys):
        """If layout was 'uk' at script's startup we need to translate letters for hotkeys correct work"""
        new_keys = []
        layout = self.layout.get()
        for key in keys:
            if len(key) == 1 and layout != "en":
                key = layout.translate(key, "en", layout)
            new_keys.append(key)

        return new_keys[0] if len(new_keys) == 1 else new_keys


if __name__ == "__main__":
    """
    import logging
    from keymouse import KeyMouse

    logger = logging.getLogger("keymouse")
    logger.setLevel(logging.DEBUG)

    keymouse = KeyMouse()
    """
    logger.setLevel(logging.DEBUG)
    keymouse = KeyMouse()

    keymouse.print_mouse_position()
