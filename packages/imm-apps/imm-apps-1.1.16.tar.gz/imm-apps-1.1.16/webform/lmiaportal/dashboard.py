from webform.definition import Action
from webform.webcommon import WebPages


class Dashboard(WebPages):
    @property
    def actions(self):
        return [self.pickEmployer, self.createApplication]

    @property
    def createApplication(self):
        create_button_id = "body > main > ul > li:nth-child(2) > a"
        next_page_tag = "#\\39 124 > select"
        return self.web_element.pageElement(
            create_button_id,
            next_page_tag,
            [],
            label="Dashboard create LMIA Application",
        )

    @property
    def pickEmployer(self):
        next_page_tag = "#wb-auto-11_filter > label > input[type=search]"  # filter
        action = {
            "action_type": Action.LmiaEmployerPick.value,
            "business_number": self.app.general.cra_number,
        }
        return self.web_element.pageElement(
            None, next_page_tag, actions=[action], label="Dashboard pick employer"
        )
