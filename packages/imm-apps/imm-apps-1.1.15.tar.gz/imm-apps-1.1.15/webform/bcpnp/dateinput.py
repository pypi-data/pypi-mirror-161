from webform.definition import Action
from datetime import date

# specially processing date input, with or without enter after inputing date
def inputDate(
    label: str, id: str, value: date, required=True, length=10, with_enter=False
):
    the_date = [
        {
            "action_type": Action.Input.value,
            "label": label,
            "id": id,
            "value": value.strftime("%Y-%m-%d") if value else None,
            "required": required,
            "length": length,
        }
    ]
    the_enter = (
        [{"action_type": Action.PressKey.value, "label": label, "key": "Enter"}]
        if with_enter
        else []
    )

    return the_date + the_enter


def pressEnter():
    return {
        "action_type": Action.PressKey.value,
        "label": "Enter",
        "key": "Enter",
    }
