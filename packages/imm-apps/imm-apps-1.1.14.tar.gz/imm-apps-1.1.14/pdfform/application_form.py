from pdfform.form_controls_win import (
    Control,
    RadioButtonList,
    TextField,
    RadioButton,
    CheckBox,
    DropdownList,
    DateField,
    Skip,
    Pause,
    OutputInfo,
    Button,
)


class ApplicationForm:
    """Application for filling PDF form according to json file"""

    def __init__(self, actions=None, verbose=False):
        self.verbose = verbose
        if actions is not None:
            self._actions = list(actions)
        else:
            self._actions = []

    def add_step(self, action: dict):
        match action.get("action_type"):
            case "Skip":
                control = Skip(
                    action.get("times"), action.get("pause"), verbose=self.verbose
                )
                self._actions.append(control)
            case "TextField":
                control = TextField(
                    action.get("data"), pause=action.get("pause"), verbose=self.verbose
                )
                self._actions.append(control)
            case "RadioButton":
                control = RadioButton(
                    action.get("data"),
                    pause=action.get("pause"),
                    verbose=self.verbose,
                )
                self._actions.append(control)

            case "RadioButtonList":
                control = RadioButtonList(
                    pause=action.get("pause"),
                    verbose=self.verbose,
                    position=action.get("position"),
                )
                self._actions.append(control)

            case "CheckBox":
                control = CheckBox(
                    action.get("data"), pause=action.get("pause"), verbose=self.verbose
                )
                self._actions.append(control)
            case "DropdownList":
                control = DropdownList(
                    action.get("data"),
                    action.get("key"),
                    action.get("num"),
                    pause=action.get("pause"),
                    verbose=self.verbose,
                )
                self._actions.append(control)
            case "DateField":
                control = DateField(
                    action.get("date"),
                    noday=action.get("noday"),
                    pause=action.get("pause"),
                    verbose=self.verbose,
                )
                self._actions.append(control)
            case "Pause":
                control = Pause(action.get("pause"), verbose=self.verbose)
                self._actions.append(control)
            case "OutputInfo":
                control = OutputInfo(action.get("info"), verbose=self.verbose)
                self._actions.append(control)
            case "Button":
                control = Button(action.get("pause"), verbose=self.verbose)
                self._actions.append(control)
            case _:
                raise ValueError(f"{action.get('action_type')} is invalid")

    def fill_form(self, start: int = 0, verbose: bool = False):
        """Perform the fill pdf form action"""
        if start != 0:
            action = Skip(times=start, verbose=self.verbose)
            action.fill()
        step = 0
        for action in self._actions[start:]:
            if verbose:
                print(
                    f"step: {step + start}---skip: {step+start+Skip.addtional_skip-3}",
                    end="\t",
                )
                step += 1
            action.fill()
