from webform.definition import Action
import base64


class WebElement:
    def __init__(self):
        self.delay = None

    def encode(self, password):
        password_bytes = password.encode("ascii")
        base64_bytes = base64.b64encode(password_bytes)
        return base64_bytes.decode("ascii")

    def inputElement(
        self, id, value, label="Input", length=100, required=True, set_value=False
    ):
        return {
            "action_type": Action.Input.value,
            "label": label,
            "id": id,
            "value": value,
            "length": length,
            "required": required,
            "delay": self.delay,
            "set_value": set_value,
        }

    def areatextElement(self, id, value, label="Input", length=500, required=True):
        return {
            "action_type": Action.Areatext.value,
            "label": label,
            "id": id,
            "value": value,
            "length": length,
            "required": required,
            "delay": self.delay,
        }

    def selectElement(self, id, value, label="Select", select_by_text=False):
        return {
            "action_type": Action.Select.value,
            "label": label,
            "id": id,
            "value": value,
            "delay": self.delay,
            "select_by_text": select_by_text,
        }

    def checkboxElement(self, id, value, label="Checkbox"):
        return {
            "action_type": Action.Checkbox.value,
            "label": label,
            "id": id,
            "value": value,
            "delay": self.delay,
        }

    def radioElement(self, id, label="Radio"):
        return {
            "action_type": Action.Radio.value,
            "id": id,
            "label": label,
            "delay": self.delay,
        }

    def buttonElement(self, id, label="Button"):
        return {
            "action_type": Action.Button.value,
            "label": label,
            "id": id,
            "delay": self.delay,
        }

    def pageElement(self, id, nex_page_tag, actions=[], label="Webpage"):
        return {
            "action_type": Action.WebPage.value,
            "page_name": label,
            "actions": actions,
            "id": id,
            "next_page_tag": nex_page_tag,
        }

    def loginElement(self, account_element_id, account, password_element_id, password):
        return {
            "action_type": Action.Login.value,
            "account": account,
            "password": self.encode(password),
            "account_element_id": account_element_id,
            "password_element_id": password_element_id,
        }

    # security_answers is a dict including questions and answers
    def securityElement(
        self, question_element_id, answer_element_id, security_answers: dict
    ):
        return {
            "action_type": Action.Security.value,
            "question_element_id": question_element_id,
            "answer_element_id": answer_element_id,
            "security_answers": security_answers,
        }

    def dependantSelectElement(self, select1: dict, select2: dict):
        return {
            "action_type": Action.DependantSelect.value,
            "select1": select1,
            "select2": select2,
        }

    def pressKeyElement(self, id, value, label="Press Key"):
        return {
            "action_type": Action.PressKey.value,
            "id": id,
            "key": value,
            "label": label,
            "delay": self.delay,
        }

    def pdfElement(self, wait_for: str):
        return {
            "action_type": Action.Pdf.value,
            "wait_for": wait_for,
            "delay": self.delay,
        }

    def imgElement(self, wait_for: str):
        return {
            "action_type": Action.Image.value,
            "wait_for": wait_for,
            "delay": self.delay,
        }

    def waitElement(self, duration):
        return {"action_type": Action.Wait.value, "duration": duration}

    def uploadElement(self, id, value, label):
        return {
            "action_type": Action.Upload.value,
            "id": id,
            "filename": value,
            "label": "Upload",
            "delay": self.delay,
        }

    def gotoPageElement(self, url, wait_for=None):
        return {"action_type": Action.GotoPage.value, "url": url, "wait_for": wait_for}

    def confirmElement(self, message):
        return {"action_type": Action.Confirm.value, "message": message}

    def waitForElement(self, id):
        return {"action_type": Action.Wait4Element.value, "id": id}
