from webform.webcommon import WebPages, Page


class EmpBenefits(WebPages):
    @property
    def actions(self):
        jo = self.app.joboffer
        has_benefit = any(
            [
                jo.disability_insurance,
                jo.dental_insurance,
                jo.empolyer_provided_persion,
                jo.extended_medical_insurance,
                jo.extra_benefits,
            ]
        )
        return [self.page1, self.page2, self.page3] if has_benefit else [self.page1,self.page21]

    @property
    def page1(self):
        jo = self.app.joboffer
        has_benefit = any(
            [
                jo.disability_insurance,
                jo.dental_insurance,
                jo.empolyer_provided_persion,
                jo.extended_medical_insurance,
                jo.extra_benefits,
            ]
        )
        has_benefit_id = (
            "#\\39 471 > div > input:nth-child(1)"
            if has_benefit
            else "#\\39 471 > div > input:nth-child(4)"
        )
        page_actions = [
            self.web_element.radioElement(
                has_benefit_id, label="Will you provide benefits to the TFW?"
            )
        ]
        # Will you be providing any other -> No id, if has benefit
        # employement benefits pay percentage #\39 481 > input
        next_page_tag =   "#\\39 476 > div > input:nth-child(4)"  if has_benefit else  "#\\39 481 > input" 
        return Page(
            page_actions, "#next", next_page_tag, label="Page 1: Employment benefits"
        ).page

    @property
    def page2(self):
        jo = self.app.joboffer
        disability_insurance_id = (
            "#\\39 472 > div > input:nth-child(1)"
            if jo.disability_insurance
            else "#\\39 472 > div > input:nth-child(4)"
        )
        dental_insurance_id = (
            "#\\39 473 > div > input:nth-child(1)"
            if jo.dental_insurance
            else "#\\39 473 > div > input:nth-child(4)"
        )
        empolyer_provided_persion_id = (
            "#\\39 474 > div > input:nth-child(1)"
            if jo.empolyer_provided_persion
            else "#\\39 474 > div > input:nth-child(4)"
        )
        extended_medical_insurance_id = (
            "#\\39 475 > div > input:nth-child(1)"
            if jo.extended_medical_insurance
            else "#\\39 475 > div > input:nth-child(4)"
        )
        extra_benefits_id = (
            "#\\39 476 > div > input:nth-child(1)"
            if jo.extra_benefits
            else "#\\39 476 > div > input:nth-child(4)"
        )
        page_actions = [
            self.web_element.radioElement(disability_insurance_id, label="Disability"),
            self.web_element.radioElement(dental_insurance_id, label="Dental"),
            self.web_element.radioElement(
                empolyer_provided_persion_id, label="Pension"
            ),
            self.web_element.radioElement(
                extended_medical_insurance_id, label="Extened medical"
            ),
            self.web_element.radioElement(extra_benefits_id, label="Other"),
        ]
        next_page_tag = "#\\39 481 > input"  # Percentage of vacation pay id
        return Page(
            page_actions, "#next", next_page_tag, label="Page 2 of employment benefits"
        ).page

    @property
    def page3(self):
        page_actions = (
            [
                self.web_element.areatextElement(
                    "#\\39 477 > textarea",
                    self.app.joboffer.extra_benefits,
                    label="Extra benefits",
                )
            ]
            if self.app.joboffer.extra_benefits
            else []
        )

        number_paid_vacation = self.web_element.inputElement(
            "#\\39 480 > input",
            str(self.app.joboffer.vacation_pay_weeks),
            label="Paid vacation days",
        )
        percetage = self.web_element.inputElement(
            "#\\39 481 > input",
            str(self.app.joboffer.vacation_pay_percentage),
            label="Percentage of vacation pay",
        )

        page_actions.extend([number_paid_vacation, percetage])

        next_page_tag = "#\\39 484 > div > input:nth-child(4)"
        return Page(
            page_actions, "#next", next_page_tag, label="Page 3 of employment benefits"
        ).page
        
    @property
    def page21(self):
        page_actions = []

        number_paid_vacation = self.web_element.inputElement(
            "#\\39 480 > input",
            str(self.app.joboffer.vacation_pay_weeks),
            label="Paid vacation days",
        )
        percetage = self.web_element.inputElement(
            "#\\39 481 > input",
            str(self.app.joboffer.vacation_pay_percentage),
            label="Percentage of vacation pay",
        )

        page_actions.extend([number_paid_vacation, percetage])

        next_page_tag = "#\\39 484 > div > input:nth-child(4)"
        return Page(
            page_actions, "#next", next_page_tag, label="Page 3 of employment benefits"
        ).page


