from webform.definition import Action
from typing import Union
import base64

# This step includs actions of signing in, picking Skill Immigration automatically, select and confirm which stream to apply through
class Login:
    def __init__(
        self,
        person: object,
    ):
        self.person = person

    def encode(self, password):
        password_bytes = password.encode("ascii")
        base64_bytes = base64.b64encode(password_bytes)
        return base64_bytes.decode("ascii")

    def login(self, initial=True, previous=False):
        sign_in = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Sign in",
                "actions": [
                    {
                        "action_type": Action.GotoPage.value,
                        "url": "https://www.pnpapplication.gov.bc.ca/user/sign-in",
                    },
                    {
                        "action_type": Action.Login.value,
                        "label": "Login",
                        "account": self.person.bcpnp.account
                        or self.person.personal.user_id,
                        "password": self.person.bcpnp.password
                        and self.encode(self.person.bcpnp.password)
                        or self.encode(self.person.personal.password),
                        "account_element_id": "#userId",
                        "password_element_id": "#pass",
                    },
                ],
                "id": "#form > div:nth-child(4) > div > input",
                "next_page_tag": "#navigation__list > li:nth-child(3) > a",
            }
        ]

        pick_sk_immigration = [
            # pick skill immigration
            {
                "action_type": Action.WebPage.value,
                "page_name": "Pick skill immigration",
                "actions": [],
                "id": "body > div > main > div.layout-container > div > div > div > div:nth-child(1) > a",
                "next_page_tag": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(5) > a",
            },
        ]

        # pick a stream of bcpnp
        case_stream = {
            "EE-Skilled Worker": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(1) > a",
                "confirm": "#skills-express-skilled > form > div > label > input[type=checkbox]",
                "start": "#skills-express-skilled > form > input",
            },
            "EE-International Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(2) > a",
                "confirm": "#skills-express-intl-grad > form > div > label > input[type=checkbox]",
                "start": "#skills-express-intl-grad > form > input",
            },
            "EE-International Post-Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(3) > a",
                "confirm": "#skills-express-intl-postgrad > form > div > label > input[type=checkbox]",
                "start": "#skills-express-intl-postgrad > form > input",
            },
            "EE-Health Authority": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(1) > ul > li:nth-child(4) > a",
                "confirm": "#skills-express-health-care > form > div > label > input[type=checkbox]",
                "start": "#skills-express-health-care > form > input",
            },
            "Skilled Worker": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(1) > a",
                "confirm": "#skills-skilled > form > div > label > input[type=checkbox]",
                "start": "#skills-skilled > form > input",
            },
            "International Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(2) > a",
                "confirm": "#skills-intl-grad > form > div > label > input[type=checkbox]",
                "start": "#skills-intl-grad > form > input",
            },
            "Entry-Level and Semi-Skilled Worker": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(3) > a",
                "confirm": "#skills-entry-level > form > div > label > input[type=checkbox]",
                "start": "#skills-entry-level > form > input",
            },
            "International Post-Graduate": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(4) > a",
                "confirm": "#skills-intl-postgrad > form > div > label > input[type=checkbox]",
                "start": "#skills-intl-postgrad > form > input",
            },
            "Health Authority": {
                "link": "body > div > main > div.layout-container > div > div > div:nth-child(4) > div:nth-child(3) > ul > li:nth-child(5) > a",
                "confirm": "#skills-health-care > form > div > label > input[type=checkbox]",
                "start": "#skills-health-care > form > input",
            },
        }
        pick_stream = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Pick skill immigration",
                "actions": [
                    {
                        "action_type": Action.Button.value,
                        "label": "Pick which stream to apply through",
                        "id": case_stream[self.person.bcpnp.case_stream]["link"],
                    },
                    {
                        "action_type": Action.Checkbox.value,
                        "label": "I confirm that I qualify all the category requirements",
                        "id": case_stream[self.person.bcpnp.case_stream]["confirm"],
                        "value": True,
                    },
                ],
                "id": case_stream[self.person.bcpnp.case_stream]["start"],
                "next_page_tag": "body > div > main > div.layout-container > div > div > form > button",
            }
        ]

        confirm_profile = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Confirm profile and representative",
                "actions": [],
                "id": "body > div > main > div.layout-container > div > div > form > button",
                "next_page_tag": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > ul > li.ng-scope.active > a",
            }
        ]

        continue_page = [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Continue my registration",
                "actions": [],
                "id": "body > div.page > main > div > div > div > div > div:nth-child(2) > div > div.col-sm-5.col-sm-offset-2.tile > div > div.buttons > a.btn.btn-primary",
                # "next_page_tag": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > ul > li.ng-scope.active > a",
                "next_page_tag": "#tabset-navigation > div > div > div.form-group.pull-right > uf-save-button > button",
            },
        ]
        # 1. start a new case， if not the first registration or application
        start_new_case = (
            [
                {
                    "action_type": "WebPage",
                    "page_name": "Start a new case",
                    "actions": [],
                    "id": "body > div > main > div.layout-container > div > div > div.start-case-btn-wrapper > a",
                    "next_page_tag": "body > div > main > div.layout-container > div > div > div > div:nth-child(1) > a",
                },
            ]
            if previous == True
            else []
        )
        # 2. pick the case
        pick_case = (
            [
                {
                    "action_type": "WebPage",
                    "page_name": "Pick the current registration/application",
                    "actions": [{"action_type": "BcpnpPick"}],
                    "id": None,
                    "next_page_tag": "body > div.page > main > div > div > div > div > div:nth-child(2) > div > div.col-sm-5.col-sm-offset-2.tile > div > div.buttons > a.btn.btn-primary",
                },
            ]
            if previous == True
            else []
        )
        return (
            sign_in
            + start_new_case
            + pick_sk_immigration
            + pick_stream
            + confirm_profile
            if initial
            else sign_in + pick_case + continue_page
        )
