from webform.definition import Action
from webform.bcpnp.dashboard import DashboardApp, DashboardReg
from typing import Union


class Submit:
    def __init__(self, person: object, is_reg=False):
        self.person = person
        self.is_reg = is_reg

    def fill(self):
        check_sign = [
            {
                "action_type": Action.Checkbox.value,
                "label": "Check consent box",
                "id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(6) > div > uf-panel:nth-child(2) > div > uf-panel-body > div > uf-agreement > div > div:nth-child(1) > div.agreement-checkbox-container > div > label"
                if self.is_reg
                else "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(8) > div > uf-panel:nth-child(2) > div > uf-panel-body > div > div > uf-agreement > div > div:nth-child(1) > div.agreement-checkbox-container > div > label > input",
                "value": True,
            },
            {
                "action_type": Action.Input.value,
                "label": "Registrant full name",
                "id": "#BCPNP_App_ConsentRegName",
                "value": self.person.personal.full_name,
                "required": True,
                "length": 100,
            },
        ]
        spouse_check_sign = (
            [
                {
                    "action_type": Action.Checkbox.value,
                    "label": "Check consent box",
                    "id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(6) > div > uf-panel:nth-child(2) > div > uf-panel-body > div > uf-agreement > div > div:nth-child(1) > div.agreement-checkbox-container > div > label"
                    if self.is_reg
                    else "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > div.tab-content > ng-transclude > uf-tab:nth-child(8) > div > uf-panel:nth-child(2) > div > uf-panel-body > div > div > div > uf-agreement > div > div:nth-child(1) > div.agreement-checkbox-container > div > label > input",
                    "value": True,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Registrant full name",
                    "id": "#BCPNP_App_ConsentSpouseName",
                    "value": self.person.marriage.sp_first_name
                    + " "
                    + self.person.marriage.sp_last_name,
                    "required": True,
                    "length": 100,
                },
            ]
            if self.person.marriage.marital_status in ["Married", "Common-Law"]
            and not self.is_reg
            else []
        )

        has_rep = [
            {
                "action_type": Action.Radio.value,
                "label": "Did you hair a pair Rep?",
                "id": "#BCPNP_App_HaspaidRep-Yes1"
                if self.person.rcic.first_name
                else "#BCPNP_App_HaspaidRep-Yes2",
            },
        ]

        rep_details = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Representative Family Name(s)",
                    "id": "#BCPNP_App_RepFamilyName",
                    "value": self.person.rcic.last_name,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Representative Given Name(s)",
                    "id": "#BCPNP_App_RepGivenName",
                    "value": self.person.rcic.first_name,
                    "required": True,
                    "length": 100,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Phone number of paid representative",
                    "id": "#BCPNP_App_RepPhone",
                    "value": self.person.rcic.telephone,
                    "required": True,
                    "length": 100,
                },
            ]
            if self.person.rcic.first_name
            else []
        )
        wait = [{"action_type": Action.Wait.value, "duration": 2000}]

        dashboard = DashboardReg() if self.is_reg else DashboardApp()
        read_agree = (
            [
                {
                    "action_type": Action.Checkbox.value,
                    "label": "I have read and agree",
                    "id": "#BCPNP_PaymentRefundPolicy",
                    "value": True,
                }
            ]
            if not self.is_reg
            else []
        )
        actions = (
            # dashboard.jump("Submit")
            check_sign
            + spouse_check_sign
            + has_rep
            + rep_details
            + read_agree
            + dashboard.save
            + wait
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Submit",
                "actions": actions,
                "id": None,
            }
        ]
