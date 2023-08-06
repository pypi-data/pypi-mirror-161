from webform.webcommon import WebPages


class ForeignNational(WebPages):
    @property
    def actions(self):
        return [self.page1, self.page2]

    @property
    def page1(self):
        # Now we only consider one FN, so no for batch processing
        radio_id = "#\\39 181 > div > input:nth-child(4)"
        page_actions = [
            self.web_element.radioElement(radio_id, "Add FN info at one time")
        ]
        return self.web_element.pageElement(
            "#next", "#\\39 183 > input", page_actions, label="Add FN in one time"
        )

    @property
    def page2(self):
        page_actions = [
            self.web_element.buttonElement(
                "#addWorkers", label="Add a foreign national"
            ),
            self.web_element.inputElement(
                "#\\39 183 > input", self.app.personal.first_name, label="First name"
            ),
            self.web_element.inputElement(
                "#\\39 184 > input",
                self.app.personal.last_name,
                label="Last name",
                set_value=True,
            ),
            self.web_element.inputElement(
                "#\\39 185 > input", self.app.personal.dob, label="DOB", set_value=True
            ),
            self.web_element.selectElement(
                "#\\39 186 > select",
                self.app.personal.citizen,
                label="Country",
                select_by_text=True,
            ),
            self.web_element.buttonElement("#saveWorkers", label="Save"),
            self.web_element.waitForElement(
                "#addWorkers"
            ),  # wait for saving and new add appeas
            self.web_element.waitElement(
                1500
            ),  # TODO: if there are any other solutions?
        ]
        match self.app.lmiacase.stream_of_lmia:
            case "EE":
                next_page_tag = "#\\39 340 > div > input:nth-child(1)"
            case "LWS":
                next_page_tag = (
                    "#\\39 378 > div > input:nth-child(4)"  # provide accomadation No id
                )
            case "HWS":
                next_page_tag = "#\\39 349 > div > input:nth-child(4)"
            case _:
                next_page_tag = "#\\39 340 > div > input:nth-child(1)"

        return self.web_element.pageElement(
            "#next",
            next_page_tag,
            page_actions,
            label="Foreign national information",
        )
