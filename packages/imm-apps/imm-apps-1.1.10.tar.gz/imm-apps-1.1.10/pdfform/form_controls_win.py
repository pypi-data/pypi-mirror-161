import time
from abc import ABC, abstractmethod
from datetime import date, timedelta
from pywinauto.keyboard import send_keys


class Control(ABC):
    """Pdf form input control base class"""

    verbose: bool = False

    @abstractmethod
    def fill(self):
        """Fill this control"""


class Skip(Control):
    """Skip disabled control"""

    addtional_skip = 0

    def __init__(self, times=1, pause=0, verbose=False):
        self.times = times
        self.pause = pause
        self.verbose = verbose

    def fill(self):
        if self.verbose:
            print("Skip to next")
        for _ in range(self.times):
            send_keys("{TAB}", pause=self.pause)
        Skip.addtional_skip += self.times


class Button(Control):
    def __init__(self, pause=0, verbose=False) -> None:
        self.pause = pause
        self.verbose = verbose

    def fill(self):
        if self.verbose:
            print("Click button")
        send_keys("{ENTER}", pause=self.pause)


class Pause(Control):
    """Pause for a moment"""

    def __init__(self, seconds, verbose=False):
        self.seconds = seconds
        self.verbose = verbose

    def fill(self):
        if self.verbose:
            print(f"Pause {self.seconds} seconds")
        time.sleep(self.seconds)


class TextField(Control):
    """Text field"""

    def __init__(self, data, pause=0, verbose=False):
        """data: text to fill"""
        self.data = data
        self.pause = pause
        self.verbose = verbose

    def fill(self):
        if self.verbose:
            print(f"Fill text field with {self.data}")
        if type(self.data) == list:
            for d in self.data:
                time.sleep(3)
                send_keys(str(d).replace(" ", "{SPACE}"))
            send_keys("{TAB}")
        else:
            send_keys(str(self.data).replace(" ", "{SPACE}"), pause=self.pause)
            send_keys("{TAB}")


class RadioButton(Control):
    """Radio button"""

    def __init__(self, data, pause=0, verbose=False):
        """data: False for No, True for yes"""
        self.data = data
        self.pause = pause
        self.verbose = verbose

    def fill(self):
        if self.data:
            key = "{VK_RIGHT}"
        else:
            key = "{VK_SPACE}"
        if self.verbose:
            print(f"Fill radio button with {self.data}, press {key} key")
        send_keys(key, pause=self.pause)
        send_keys("{TAB}")


# Check one button in a button list. Check the position with True
class RadioButtonList(Control):
    """Radio button List"""

    def __init__(self, pause=0, verbose=False, position=0):
        self.pause = pause
        self.verbose = verbose
        self.position = position

    def fill(self):
        if self.position > 0:
            for _ in range(1, self.position + 1):
                send_keys("{VK_RIGHT}", pause=self.pause)
        else:
            send_keys("{VK_SPACE}", pause=self.pause)

        if self.verbose:
            print(f"Fill radio button with checked in position {self.position}")

        send_keys("{TAB}")


class CheckBox(Control):
    """Check box"""

    def __init__(self, data, pause=0, verbose=False):
        self.data = data
        self.pause = pause
        self.verbose = verbose

    def fill(self):
        if self.verbose:
            print(f"Fill check box with {self.data}")
        if self.data:
            send_keys("{VK_SPACE}")
            send_keys("{TAB}")
        else:
            send_keys("{TAB}")
        time.sleep(self.pause)


class OutputInfo(Control):
    """Output log info"""

    def __init__(self, info, verbose=False):
        self.info = info
        self.verbose = verbose

    def fill(self):
        if self.verbose:
            print(f"------- {self.info} -------")


class DropdownList(Control):
    """Dropdown list"""

    def __init__(self, data, key, num, pause=0.01, verbose=False):
        self.data = data
        self.key = key
        self.num = num
        self.pause = pause  # pause seconds after press
        self.verbose = verbose

    def fill(self):
        # key, num = self.key_presses()
        if self.verbose:
            print(
                f"Select dropdown list with {self.data}, press {self.key} {self.num} time(s)"
            )
        for _ in range(self.num):
            send_keys(self.key, pause=self.pause)

        send_keys("{TAB}")


class DateField(Control):
    """Date field"""

    def __init__(self, the_date, noday: bool = False, pause=0.2, verbose=False):
        self.date = the_date or date.today() + timedelta(days=1)
        self.noday = noday
        self.pause = pause
        self.verbose = verbose

    def fill(self):
        self.date = (
            self.date.strftime("%Y-%m-%d") if type(self.date) == date else self.date
        )
        year, month, day = self.date.split("-")
        if self.noday:
            if self.verbose:
                print(f"Fill date {year}-{month}")
            send_keys(year + month, pause=self.pause)

        else:
            if self.verbose:
                print(f"Fill date {year}-{month}-{day}")
            send_keys(year, pause=self.pause)
            send_keys(month, pause=self.pause)
            send_keys(day, pause=self.pause)
        send_keys("{TAB}")
