from utils.utils import best_match
from typing import List, Union


class JsonMaker:
    """According to data model, generate json file for pdf form filling"""

    def __init__(self):
        self.actions = []

    def _getKey_Num(self, data: str, options: List[str], like=False):
        s_char = data[0].lower()
        count = 0
        matched_one = best_match(data, options)
        for elem in options:
            if elem[0].lower() == s_char:
                count += 1
                if elem.lower() == data.lower():
                    break
                elif like and f"({data})" in elem:
                    break
                elif elem.lower() == matched_one.lower():
                    break
        return (s_char, count)

    def add_skip(self, times: int, pause: float = 0):
        self.actions.append({"action_type": "Skip", "times": times, "pause": pause})

    def add_button(self, pause: float = 0):
        self.actions.append({"action_type": "Button", "pause": pause})

    def add_text(self, data: Union[str, list], pause: float = 0):
        data = data or ""
        self.actions.append({"action_type": "TextField", "data": data, "pause": pause})

    def add_radio(self, data: bool, pause: float = 0):
        self.actions.append(
            {
                "action_type": "RadioButton",
                "data": data,
                "pause": pause,
            }
        )

    def add_radio_list(self, pause: float = 0, position=0):
        self.actions.append(
            {
                "action_type": "RadioButtonList",
                "pause": pause,
                "position": position,
            }
        )

    def add_checkbox(self, data: bool, pause: float = 0):
        self.actions.append({"action_type": "CheckBox", "data": data, "pause": pause})

    def add_info(self, info: str, pause: float = 0):
        self.actions.append({"action_type": "OutputInfo", "info": info, "pause": pause})

    def add_dropdown(self, data: str, options: list[str], like=False, pause: float = 0):
        key, num = self._getKey_Num(data, options, like=like)
        self.actions.append(
            {
                "action_type": "DropdownList",
                "data": data,
                "key": key,
                "num": num,
                "like": like,
                "pause": pause,
            }
        )

    def add_date(self, the_date, noday: bool = False, pause: float = 0):
        self.actions.append(
            {
                "action_type": "DateField",
                "date": the_date,
                "noday": noday,
                "pause": pause,
            }
        )

    def add_pause(self, pause: float = 1):
        self.actions.append({"action_type": "Pause", "pause": pause})
