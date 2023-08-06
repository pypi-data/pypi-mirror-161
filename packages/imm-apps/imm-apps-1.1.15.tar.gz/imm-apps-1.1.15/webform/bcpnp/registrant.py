from webform.definition import Action
from typing import Union
from webform.bcpnp.dateinput import inputDate, pressEnter


class Registrant:
    def __init__(self, person: object):
        self.person = person

    def fill(self):
        current_previous_application = [
            {
                "action_type": Action.Radio.value,
                "label": "Do you currently have any other active registrations or applications with the BC Provincial Nominee Program?",
                "id": "#BCPNP_App_ActiveApplication-Yes"
                if self.person.bcpnp.q1
                else "#BCPNP_App_ActiveApplication-No",
            },
            {
                "action_type": Action.Radio.value,
                "label": "Have you applied to the BC Provincial Nominee Program in the past?",
                "id": "#BCPNP_App_PreviousApp-Yes"
                if self.person.bcpnp.has_applied_before
                else "#BCPNP_App_PreviousApp-No",
            },
        ]
        previous_file_number = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Previous file number",
                    "id": "#BCPNP_App_CurPrevApplicationsDetails",
                    "value": self.person.bcpnp.pre_file_no,
                    "required": True,
                    "length": 100,
                }
            ]
            if self.person.bcpnp.has_applied_before
            else []
        )

        ee_profile = (
            [
                {
                    "action_type": Action.Input.value,
                    "label": "Express entry profile number",
                    "id": "#syncA_App_EE_ProfileNumber",
                    "value": self.person.ee.ee_profile_no,
                    "required": True,
                    "length": 30,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Express entry profile submission expiry date",
                    "id": "#syncA_App_EE_ExpiryDate",
                    "value": self.person.ee.ee_expiry_date.strftime("%Y-%m-%d"),
                    "required": True,
                    "length": 10,
                },
                pressEnter(),
                {
                    "action_type": Action.Input.value,
                    "label": "Job seeker validation code (JSVC)",
                    "id": "#syncA_App_EE_ValidCode",
                    "value": self.person.ee.ee_jsvc,
                    "required": True,
                    "length": 30,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Comprehensive ranking score (CRS)",
                    "id": "#syncA_App_EE_CRS",
                    "value": self.person.ee.ee_score,
                    "required": True,
                    "length": 30,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "NOC (as supplied on your IRCC Express Entry profile)",
                    "id": "#syncA_App_Job_NOC_EE",
                    "value": self.person.ee.ee_noc,
                    "required": True,
                    "length": 30,
                },
                {
                    "action_type": Action.Input.value,
                    "label": "Job title (as supplied on your IRCC Express Entry profile)",
                    "id": "#syncA_App_Job_Title_EE",
                    "value": self.person.ee.ee_job_title,
                    "required": True,
                    "length": 30,
                },
            ]
            if self.person.bcpnp.case_stream.startswith("EE_")
            else []
        )

        # dashboard = DashboardReg()

        actions = (
            # dashboard.jump("Registrant")
            current_previous_application
            + previous_file_number
            + ee_profile
            # + dashboard.save
        )
        return [
            {
                "action_type": Action.WebPage.value,
                "page_name": "Registrant",
                "actions": actions,
                "id": "body > div > main > div.layout-container > div > div > div > uf-form > div > ng-transclude > div > uf-tabset > div > ul > li:nth-child(2) > a",
                "next_page_tag": "#BCPNP_App_Edu_CA-No",
            }
        ]
