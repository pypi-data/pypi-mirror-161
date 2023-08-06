from webform.webcommon import WebPages, Page


class Layoff(WebPages):
    @property
    def actions(self):
        return [self.page1, self.page2, self.page3, self.page4]

    @property
    def page1(self):
        lead2layoff = (
            [
                self.web_element.inputElement(
                    "#\\39 515 > input",
                    str(self.app.lmi.laid_off_canadians),
                    label="number of laid off Canadians",
                ),
                self.web_element.inputElement(
                    "#\\39 516 > input",
                    str(self.app.lmi.laid_off_tfw),
                    label="number of laid off TFWs",
                ),
                self.web_element.areatextElement(
                    "#\\39 517 > textarea",
                    self.app.lmi.laid_off_reason,
                    label="reason for lay-off",
                ),
            ]
            if self.app.lmi.laid_off_in_12
            else []
        )

        lead2jobloss_id = (
            "#\\39 518 > div > input:nth-child(1)"
            if self.app.lmi.laid_off_in_12
            else "#\\39 518 > div > input:nth-child(4)"
        )
        lead2joblosss = self.web_element.radioElement(
            lead2jobloss_id, label="Leads to lay off?"
        )

        page_actions = [*lead2layoff, lead2joblosss]
        next_page_tag = (
            "#\\39 520 > div > input:nth-child(4)"  # receiving work-sharing ? No-id
        )

        return Page(page_actions, "#next", next_page_tag, label="lay off").page

    @property
    def page2(self):
        layoff_details = (
            [
                self.web_element.areatextElement(
                    "#\\39 519 > textarea",
                    self.app.lmi.canadian_lost_job_info,
                    label="details of leading to layoff",
                )
            ]
            if self.app.lmi.canadian_lost_job
            else []
        )

        workshaing_id = (
            "#\\39 520 > div > input:nth-child(1)"
            if self.app.lmi.is_work_sharing
            else "#\\39 520 > div > input:nth-child(4)"
        )
        worksharing = self.web_element.radioElement(
            workshaing_id, label="Has work sharing?"
        )

        page_actions = [*layoff_details, worksharing]
        next_page_tag = "#\\39 522 > div > input:nth-child(4)"  # is there any labour dispute ? No-id

        return Page(
            page_actions, "#next", next_page_tag, label="leading to job loss"
        ).page

    @property
    def page3(self):
        page_actions = [
            self.web_element.radioElement(
                "#\\39 522 > div > input:nth-child(1)"
                if self.app.lmi.labour_dispute
                else "#\\39 522 > div > input:nth-child(4)",
                label="has labour dispute?",
            )
        ]

        next_page_tag = "#documents"  # Documents button to uploading files

        return Page(page_actions, "#next", next_page_tag, label="labour dispute").page

    @property
    def page4(self):
        page_actions = (
            [
                self.web_element.areatextElement(
                    "#\\39 523 > textarea",
                    self.app.lmi.labour_dispute_info,
                    label="Labour dispute details",
                )
            ]
            if self.app.lmi.labour_dispute
            else []
        )

        next_page_tag = "#uploadDocument"  # Documents upload button to uploading files

        return Page(
            page_actions, "#documents", next_page_tag, label="labour dispute details"
        ).page
