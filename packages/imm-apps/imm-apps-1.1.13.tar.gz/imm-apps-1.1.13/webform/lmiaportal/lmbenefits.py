from webform.webcommon import WebPages, Page


class LmBenefits(WebPages):
    @property
    def actions(self):
        return [self.page1, self.page2, self.page3]

    @property
    def page1(self):
        job_creation = (
            [
                self.web_element.areatextElement(
                    "#\\39 507 > textarea",
                    self.app.lmi.job_creation_benefit,
                    label="Details for job creation",
                )
            ]
            if self.app.lmi.job_creation_benefit
            else []
        )
        skill_transfer_id = (
            "#\\39 508 > div > input:nth-child(1)"
            if self.app.lmi.skill_transfer_benefit
            else "#\\39 508 > div > input:nth-child(4)"
        )
        skill_transfer = self.web_element.radioElement(
            skill_transfer_id, label="Skill transfer"
        )

        page_actions = [*job_creation, skill_transfer]
        next_page_tag = (
            "#\\39 510 > div > input:nth-child(4)"  # labour shortage ? No-id
        )

        return Page(page_actions, "#next", next_page_tag, label="Job creation").page

    @property
    def page2(self):
        skill_transfer = (
            [
                self.web_element.areatextElement(
                    "#\\39 509 > textarea",
                    self.app.lmi.skill_transfer_benefit,
                    label="Details for skill transfer",
                )
            ]
            if self.app.lmi.skill_transfer_benefit
            else []
        )
        labour_shortage_id = (
            "#\\39 510 > div > input:nth-child(1)"
            if self.app.lmi.skill_transfer_benefit
            else "#\39 510 > div > input:nth-child(4)"
        )
        labour_shortage = self.web_element.radioElement(
            labour_shortage_id, label="Skill transfer"
        )

        page_actions = [*skill_transfer, labour_shortage]
        next_page_tag = "#\\39 513 > div > input:nth-child(4)"  # lay off ? No-id

        return Page(page_actions, "#next", next_page_tag, label="Skill transfer").page

    @property
    def page3(self):
        labour_shortage = (
            [
                self.web_element.areatextElement(
                    "#\\39 511 > textarea",
                    self.app.lmi.fill_shortage_benefit,
                    label="Details for filling labour",
                )
            ]
            if self.app.lmi.fill_shortage_benefit
            else []
        )

        other_benefit = self.web_element.areatextElement(
            "#\\39 512 > textarea", self.app.lmi.other_benefit, label="Other benefits"
        )

        layoff_id = (
            "#\\39 513 > div > input:nth-child(1)"
            if self.app.lmi.laid_off_in_12
            else "#\\39 513 > div > input:nth-child(4)"
        )
        layoff = self.web_element.radioElement(
            layoff_id, label="Has laid off in past 12 months?"
        )

        page_actions = [*labour_shortage, other_benefit, layoff]
        next_page_tag = "#\\39 518 > div > input:nth-child(4)"  # hiring will lead to lay-offs ? No-id

        return Page(page_actions, "#next", next_page_tag, label="Skill transfer").page
