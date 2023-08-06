from model.common.address import Addresses
from webform.webcommon import WebPages

from typing import Union

# 1. EE
class Wage(WebPages):
    @property
    def explain_calculation(self):
        return self.app.joboffer.how_to_convert_to_hourly_rate

    @property
    def actions(self):
        return [self.wagePage1, self.wagePage2]

    # hourly rate
    @property
    def wagePage1(self):
        page_actions = [
            self.web_element.inputElement(
                "#\\39 158 > input", self.app.joboffer.hourly_rate, label="hourly rate"
            ),
            self.web_element.radioElement(
                "#\\39 159 > div > input:nth-child(1)"
                if self.app.joboffer.wage_unit != "hourly"
                else "#\\39 159 > div > input:nth-child(4)",
                label="Yes" if self.app.joboffer.wage_unit != "hourly" else "No",
            ),
        ]
        next_page_tag = "#\\39 175 > select"  # Duration selector
        return self.web_element.pageElement(
            "#next", next_page_tag, page_actions, label="Wage hourly rate"
        )

    # Wage details about how to calculate and Duration
    @property
    def wagePage2(self):
        # explain how to convert the hourly rate if it's converted from other way
        is_hourly_rate_converted = (
            True if self.app.joboffer.wage_unit != "hourly" else False
        )
        explain_calculation = (
            self.web_element.areatextElement(
                "#\\39 160 > textarea", self.explain_calculation
            )
            if is_hourly_rate_converted
            else None
        )

        duration_justification = self.web_element.areatextElement(
            "#\\39 176 > textarea",
            self.app.lmiacase.duration_reason,
            label="Duration justification",
        )
        number_of_tfw = self.web_element.inputElement(
            "#\\39 177 > input", str(self.app.lmiacase.number_of_tfw)
        )
        duration_number = self.web_element.inputElement(
            "#\\39 174 > input",
            str(self.app.lmiacase.duration_number),
            label="Employment duration",
        )
        duration_unit_types = {
            "years": "Y",
            "months": "M",
            "weeks": "W",
            "days": "D",
            "permanent": "P",
        }
        duration_unit = self.web_element.selectElement(
            "#\\39 175 > select",
            duration_unit_types.get(self.app.lmiacase.duration_unit),
            label="Employment duration unit",
        )

        page_actions = []

        if is_hourly_rate_converted:
            page_actions.append(explain_calculation)

        page_actions += [
            *self.work_location,
            duration_justification,
            number_of_tfw,
            duration_number,
            duration_unit,
        ]
        match self.app.lmiacase.stream_of_lmia:
            case "EE":
                next_page_tag = "#\\39 181 > div > input:nth-child(1)"  # Yes
            case "LWS" | "HWS":
                next_page_tag = (
                    "#\\39 180 > div > input:nth-child(4)"  # provide name: No id
                )
            case _:
                next_page_tag = "#\\39 181 > div > input:nth-child(1)"  # Yes

        return self.web_element.pageElement(
            "#next", next_page_tag, page_actions, label="Wage hourly rate"
        )

    @property
    def work_location(self):
        locations_actions = []

        work_locations = Addresses(self.app.eraddress).workings or []
        business_location = Addresses(self.app.eraddress).business

        for location in work_locations:
            add = self.web_element.buttonElement(
                "#addWorkloctn", label="Add a work location"
            )
            # wait until the checkbox appears
            wait = self.web_element.waitForElement("#\\39 171 > input")
            operating_name = self.web_element.inputElement(
                "#\\39 163 > input",
                self.app.general.operating_name
                if self.app.general.operating_name
                else self.app.general.legal_name,
                length=200,
            )
            business_activities = self.web_element.areatextElement(
                "#\\39 164 > textarea",
                self.app.general.business_intro,
                label="Business activities",
            )
            safety_concerns = self.web_element.areatextElement(
                "#\\39 165 > textarea", self.app.lmi.safety_concerns
            )
            # select the work location, if location equals to business location, select "primary business address' else select by line 1 of address
            is_primary = location == business_location
            if is_primary:
                sub_work_location = self.web_element.selectElement(
                    "#\\39 162 > select",
                    "Primary business address",
                    select_by_text=True,
                )
            else:
                sub_work_location = self.web_element.selectElement(
                    "#\\39 162 > select", location.line1, select_by_text=True
                )
            is_primary_check = self.web_element.checkboxElement(
                "#\\39 171 > input", is_primary, "Is this the primary work location?"
            )
            save = self.web_element.buttonElement("#saveWorkloctn", label="Save")
            wait1s = self.web_element.waitElement(1000)

            locations_actions += [
                add,
                wait,
                operating_name,
                business_activities,
                safety_concerns,
                sub_work_location,
                is_primary_check,
                save,
                wait1s,
            ]

        return locations_actions
