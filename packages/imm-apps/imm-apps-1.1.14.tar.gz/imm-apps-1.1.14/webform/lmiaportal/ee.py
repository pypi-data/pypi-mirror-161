from webform.webcommon import WebPages

# 1. EE
class EE(WebPages):
    @property
    def actions(self):
        return [self.page1, self.page2, self.page3]

    @property
    def page1(self):
        support_what = (
            "#\\39 340 > div > input:nth-child(1)"
            if self.app.lmiacase.purpose_of_lmia == "Support Permanent Resident only"
            else "#\\39 340 > div > input:nth-child(4)"
        )
        joined_employer = (
            "#\39 341 > div > input:nth-child(1)"
            if self.app.lmiacase.has_another_employer
            else "#\\39 341 > div > input:nth-child(4)"
        )
        page_actions = [
            self.web_element.radioElement(
                support_what, label="Support PR only or WP&PR"
            ),
            self.web_element.radioElement(
                joined_employer, label="Supported by another employer?"
            ),
        ]

        return self.web_element.pageElement(
            "#next", "#\\39 342 > textarea", page_actions, label="LMIA purpose"
        )

    @property
    def page2(self):
        has_worked_is_working = (
            "#\\39 344 > div > input:nth-child(1)"
            if self.app.position.worked_working
            else "#\\39 344 > div > input:nth-child(4)"
        )
        page_actions = [
            self.web_element.areatextElement(
                "#\\39 342 > textarea",
                self.app.position.who_current_fill,
                label="Who is currently filling in this position",
            ),
            self.web_element.areatextElement(
                "#\\39 343 > textarea",
                self.app.position.how_did_you_find,
                label="How did you find?",
            ),
            self.web_element.radioElement(
                has_worked_is_working,
                label="Has previously employed or is currently employed",
            ),
        ]
        next_page_tag="#\\39 345 > textarea" if self.app.position.worked_working else "#\\39 346 > textarea "
        return self.web_element.pageElement(
            "#next", next_page_tag, page_actions, label="PR position info"
        )

    @property
    def page3(self):
        has_someone_in_same_position_id = (
            "#\\39 433 > div > input:nth-child(1)"
            if self.app.position.has_same
            else "#\\39 433 > div > input:nth-child(4)"
        )
        page_actions=[
            self.web_element.areatextElement(
                "#\\39 345 > textarea" ,
                self.app.position.worked_working_details,
                label="Worked details",
            )
        ] if self.app.position.worked_working else []
        
        page_actions += [
            self.web_element.areatextElement(
                "#\\39 346 > textarea" ,
                self.app.personalassess.why_qualified_say,
                label="Why the TFW qualfied",
            ),
            self.web_element.areatextElement(
                "#\\39 347 > textarea",
                self.app.position.how_when_offer,
                label="How and when did you offer the job",
            ),
            self.web_element.radioElement(
                has_someone_in_same_position_id,
                label="Has other employee in the same position?",
            ),
        ]
        next_page_tag = "#\\39 438 > div > input:nth-child(4)"  # has atypical schedule
        return self.web_element.pageElement(
            "#next", next_page_tag, page_actions, label="PR position info"
        )
