import time
from abc import ABC, abstractmethod
from typing import Tuple
from utils.utils import best_match
from pyautogui import press, write


class Control(ABC):
    """Pdf form input control base class"""

    verbose: bool = False

    @abstractmethod
    def fill(self):
        """Fill this control"""


class Skip(Control):
    """Skip disabled control"""

    def __init__(self, times=1, pause=0):
        self.pause = pause
        self.times = times

    def fill(self):
        if self.verbose:
            print(f"Skip to next for {self.times} times")
        for i in range(self.times):
            press("tab", interval=self.pause)


class Button(Control):
    def __init__(self, pause=0):
        self.pause = pause

    def fill(self):
        if self.verbose:
            print("Click button")
        press("enter", interval=self.pause)


class Pause(Control):
    """Pause for a moment"""

    def __init__(self, pause):
        self.pause = pause

    def fill(self):
        if self.verbose:
            print(f"Pause {self.pause} seconds")
        time.sleep(self.pause)


class TextField(Control):
    """Text field"""

    def __init__(self, data, pause=0):
        """data: text to fill"""
        self.data = data
        self.pause = pause

    def fill(self):
        if self.verbose:
            print(f"Fill text field with {self.data}")
        # press(self.data.replace(" ", "{SPACE}"))
        write(self.data, interval=self.pause)
        press("tab")


class RadioButton(Control):
    """Radio button"""

    def __init__(self, data, pause=0):
        """data: False for No, True for yes"""
        self.data = data
        self.pause = pause

    def fill(self):
        if self.data:
            key = "right"  # TODO:
        else:
            key = "space"
        if self.verbose:
            print(f"Fill radio button with {self.data}, press {key} key")
        press(key, interval=self.pause)
        press("tab", interval=self.pause)


class CheckBox(Control):
    """Check box"""

    def __init__(self, data, pause=0):
        self.data = data
        self.pause = pause

    def fill(self):
        if self.verbose:
            print(f"Fill check box with {self.data}")
        if self.data:
            press("space", interval=self.pause)
            press("tab", interval=self.pause)
        else:
            press("tab", interval=self.pause)


class OutputInfo(Control):
    """Output log info"""

    def __init__(self, info, pause=0):
        self.info = info
        self.pause = pause

    def fill(self):
        if self.verbose:
            print(f"------- {self.info} -------")
            time.sleep(self.pause)


class DropdownList(Control):
    """Dropdown list"""

    def __init__(self, data, options, like: bool = False, pause=0):
        self.data = data
        self.options = options
        self.like = like
        self.pause = pause

    def key_presses(self) -> Tuple[str, int]:
        s_char = self.data[0].lower()
        count = 0
        matched_one = best_match(self.data, self.options)
        for elem in self.options:
            if elem[0].lower() == s_char:
                count += 1
                if elem.lower() == self.data.lower():
                    break
                elif self.like and f"({self.data})" in elem:
                    break
                elif elem.lower() == matched_one.lower():
                    break
        return (s_char, count)

    def fill(self):
        key, num = self.key_presses()
        if self.verbose:
            print(f"Select dropdown list with {self.data}, press {key} {num} time(s)")
        press("down", interval=self.pause)
        press(key, presses=num, interval=0.1)
        press("enter")
        press("tab", interval=self.pause)


class DateField(Control):
    """Date field"""

    def __init__(self, date, noday: bool = False, pause=0.2):
        self.date = date
        self.noday = noday
        self.pause = pause

    def fill(self):
        if self.noday:
            year, month = self.date.split("-")
            if self.verbose:
                print(f"Fill date {year}-{month}")
            write(year, interval=self.pause)
            write(month, interval=self.pause)
        else:
            year, month, day = self.date.split("-")
            if self.verbose:
                print(f"Fill date {year}-{month}-{day}")
            write(year, interval=self.pause)
            write(month, interval=self.pause)
            write(day, interval=self.pause)
        press("tab", interval=self.pause)


# TODO: Test if press needs interval?
