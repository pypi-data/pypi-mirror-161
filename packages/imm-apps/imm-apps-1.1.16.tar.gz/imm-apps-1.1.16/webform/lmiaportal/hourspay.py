from webform.webcommon import WebPages, Page


class HoursPay(WebPages):
    """Hours and Pay. Common module for all streams"""

    @property
    def actions(self):
        return (
            [self.page1, self.page2, self.page3, self.page3_1, self.page4]
            if self.app.joboffer.ot_ratio >= 1.0
            else [self.page1, self.page2, self.page3, self.page4]
        )

    @property
    def page1(self):
        atypical_schedule_id = (
            "#\\39 438 > div > input:nth-child(1)"
            if self.app.joboffer.atypical_schedule
            else "#\\39 438 > div > input:nth-child(4)"
        )
        page_actions = [
            self.web_element.inputElement(
                "#\\39 436 > input",
                str(self.app.joboffer.hours / self.app.joboffer.days),
                label="how many hours per day",
            ),
            self.web_element.inputElement(
                "#\\39 437 > input",
                str(self.app.joboffer.hours),
                label="how many hours per week",
            ),
            self.web_element.radioElement(
                atypical_schedule_id, label="Is atypical schedule?"
            ),
        ]
        next_page_tag = (
            "#\\39 440 > div > input:nth-child(4)"  # job offer full-time-> No
        )
        return Page(
            page_actions, "#next", next_page_tag, label="Page 1 of huors and pay"
        ).page

    @property
    def page2(self):
        is_fulltime_id = (
            "#\\39 440 > div > input:nth-child(1)"
            if self.app.joboffer.is_full_time
            else "#\\39 440 > div > input:nth-child(4)"
        )
        page_actions = (
            [
                self.web_element.areatextElement(
                    "#\\39 439 > textarea",
                    self.app.joboffer.atypical_schedule_explain,
                    label="details of atypical schedule",
                )
            ]
            if not self.app.joboffer.is_full_time
            else []
        )
        page_actions.append(
            self.web_element.radioElement(
                is_fulltime_id, label="is this job offer full time?"
            )
        )
        next_page_tag = "#\\39 442 > div > input:nth-child(4)"
        return Page(
            page_actions, "#next", next_page_tag, label="Page 2 of hours and pay"
        ).page

    @property
    def page3(self):
        has_overtime_pay = True if self.app.joboffer.ot_ratio >= 1.0 else False
        page_actions = (
            [
                self.web_element.areatextElement(
                    "#\\39 441 > textarea",
                    self.app.joboffer.part_time_explain,
                    label="part time job offer explaination",
                )
            ]
            if not self.app.joboffer.is_full_time
            else []
        )
        has_overtime_rate_id = (
            "#\\39 442 > div > input:nth-child(1)"
            if has_overtime_pay
            else "#\\39 442 > div > input:nth-child(4)"
        )
        page_actions.append(
            self.web_element.radioElement(
                has_overtime_rate_id, label="Is there an overtime rate?"
            )
        )
        # if has overtime pay, will has 1 more page for the details, otherwise, go directly to contingent wage page
        next_page_tag = (
            "#\\39 444 > div > input:nth-child(7)"
            if has_overtime_pay
            else "#\\39 449 > div > input:nth-child(4)"
        )
        return Page(
            page_actions, "#next", next_page_tag, label="Page 3 of hours and pay"
        ).page

    @property
    def page3_1(self):
        overtime_determined_ids = {
            "day": "#\\39 444 > div > input:nth-child(1)",
            "week": "#\\39 444 > div > input:nth-child(4)",
            "both": "#\39 444 > div > input:nth-child(7)",
        }
        id = overtime_determined_ids.get(self.app.joboffer.ot_after_hours_unit)
        page_actions = [
            self.web_element.inputElement(
                "#\\39 443 > input",
                str(self.app.joboffer.overtime_rate),
                label="What is the overtime wage?",
            ),
            self.web_element.radioElement(id, label="overtime determined by"),
        ]
        next_page_tag = "#\\39 449 > div > input:nth-child(4)"  # contingent wage No
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Page 3.1: details about overtime wage",
        ).page

    @property
    def page4(self):
        has_overtime_pay = True if self.app.joboffer.ot_ratio >= 1.0 else False
        overtime_hours_ids = {
            "day": "#\\39 445 > input",
            "week": "#\\39 446 > input",
            "both": "#\\39 447 > input",
        }
        id = overtime_hours_ids.get(self.app.joboffer.ot_after_hours_unit)
        page_actions = (
            [
                self.web_element.inputElement(
                    id, str(self.app.joboffer.ot_after_hours), label="how many hours"
                )
            ]
            if has_overtime_pay
            else []
        )

        # We have no contingent wage based on my practice, so here we make it easier by only say no
        page_actions.append(
            self.web_element.radioElement(
                "#\\39 449 > div > input:nth-child(4)",
                label="Answer No for contingent wage",
            )
        )

        next_page_tag = "#\\39 452 > input"
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Page 4 contingent wage in hours and pay",
        ).page
