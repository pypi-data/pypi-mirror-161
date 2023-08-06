from re import L
from turtle import position
from webform.webcommon import WebPages, Page

# 1. Cap for LWS
class Cap(WebPages):
    @property
    def actions(self):
        return [*self.page1s]

    @property
    def page1s(self):
        has_same_position_id = (
            "#\\39 433 > div > input:nth-child(1)"
            if self.app.position.has_same
            else "#\\39 433 > div > input:nth-child(4)"
        )
        has_same_position = self.web_element.radioElement(
            has_same_position_id, label="Yes" if self.app.position.has_same else "No"
        )
        if self.app.emp5627.cap_exempted:
            which_exemption_action = self.which_exemption
            rationale = self.web_element.areatextElement(
                "#\\39 393 > textarea", self.app.emp5627.exemption_rationale
            )
            next_page_tag = "#\\39 438 > div > input:nth-child(4)"

            return [
                Page(
                    [which_exemption_action, rationale, has_same_position],
                    "#next",
                    next_page_tag,
                    label="CAP exemption yes",
                ).page
            ]
        else:
            in_seasonal_industry = self.inSeasonalIndustry
            is_in = self.app.emp5627.is_in_seasonal_industry
            if is_in:
                return [in_seasonal_industry, self.wish_to_go1, self.page2]
            else:
                return [in_seasonal_industry, self.wish_to_go2, self.page2]

    @property
    def page2(self):
        has_someone_in_same_position_id = (
            "#\\39 433 > div > input:nth-child(1)"
            if self.app.position.has_same
            else "#\\39 433 > div > input:nth-child(4)"
        )
        has_someone_in_same_position = self.web_element.radioElement(
            has_someone_in_same_position_id,
            label="Yes" if self.app.position.has_same else "No",
        )
        next_page_tag = "#\\39 438 > div > input:nth-child(4)"  # atypical No id
        return self.web_element.pageElement(
            "#next",
            next_page_tag,
            [has_someone_in_same_position],
            label="Has same position?",
        )

    @property
    def which_exemption(self):
        exemption_types = {
            "Caregiver positions in a health care facility (NOC 3012, 3233, and 3413)": "#\\39 392 > div > input:nth-child(1)",
            "On-farm primary agricultural positions": "#\\39 392 > div > input:nth-child(4)",
            "Position for the Global Talent Stream": "#\\39 392 > div > input:nth-child(7)",
            "Position(s) is/are highly mobile": "#\\39 392 > div > input:nth-child(10)",
            "Position(s) is/are truly temporary": "#\\39 392 > div > input:nth-child(13)",
            "Seasonal 270-day exemption": "#\\39 392 > div > input:nth-child(16)",
        }
        exemption_id = exemption_types.get(self.app.emp5627.which_exemption)
        return self.web_element.radioElement(
            exemption_id, label=self.app.emp5627.which_exemption
        )

    @property
    def inSeasonalIndustry(self):
        is_in = self.app.emp5627.is_in_seasonal_industry
        is_in_id = (
            "#\\39 395 > div > input:nth-child(1)"
            if is_in
            else "#\\39 395 > div > input:nth-child(4)"
        )
        is_in_action = self.web_element.radioElement(
            is_in_id, label="Yes" if is_in else "No"
        )
        # if yes in, next page tag is: do you wish to continue, no id
        # if no, do you wish to continue. no id, but different value
        next_page_tag = (
            "#\\39 429 > div > input:nth-child(4)"
            if is_in
            else "#\\39 411 > div > input:nth-child(4)"
        )
        return Page(
            [is_in_action],
            "#next",
            next_page_tag,
            label="low wage, is in seasonal page?",
        ).page

    @property
    def wish_to_go1(self):
        # answer the question always as Yes
        wish_to_go_id = "#\\39 429 > div > input:nth-child(1)"
        to_go = self.web_element.radioElement(wish_to_go_id, label="Yes")

        # CAP calculation
        add = self.web_element.buttonElement("#addSeasonal", label="Add")
        wait_for = self.web_element.waitForElement("#\\39 420 > select")
        # use first word of employer name as keyword to pick
        employer_name_keyword = self.app.general.legal_name.split(" ")[0]
        employer = self.web_element.selectElement(
            "#\\39 420 > select",
            employer_name_keyword,
            label="pick employer",
            select_by_text=True,
        )
        from_date = self.web_element.inputElement(
            "#\\39 421 > input",
            self.app.emp5627.four_week_start_date,
            label="From",
            set_value=True,
        )
        to_date = self.web_element.inputElement(
            "#\\39 422 > input",
            self.app.emp5627.four_week_end_date,
            label="To",
            set_value=True,
        )
        q_a = self.web_element.inputElement(
            "#\\39 423 > input", str(self.app.emp5627.q_a), label="Question A"
        )
        q_b = self.web_element.inputElement(
            "#\\39 424 > input", str(self.app.emp5627.q_b), label="Question B"
        )
        q_c = self.web_element.inputElement(
            "#\\39 425 > input", str(self.app.emp5627.q_c), label="Question C"
        )
        q_d = self.web_element.inputElement(
            "#\\39 426 > input", str(self.app.emp5627.q_d), label="Question D"
        )
        q_e = self.web_element.inputElement(
            "#\\39 427 > input", str(self.app.emp5627.q_e), label="Question E"
        )
        q_f = self.web_element.inputElement(
            "#\\39 417 > input", str(self.app.emp5627.q_f), label="Question F"
        )
        q_g = self.web_element.inputElement(
            "#\\39 418 > input", str(self.app.emp5627.q_g), label="Question G"
        )
        q_h = self.web_element.inputElement(
            "#\\39 419 > input", str(self.app.emp5627.q_h), label="Question H"
        )
        save = self.web_element.buttonElement("#saveSeasonal", label="Save")
        # wait_for_after_save = self.web_element.waitForElement(
        # "#seasonalTable > tbody > tr > td:nth-child(23) > button.btn.btn-default.editSeasonal"
        # )  # wait for table's edit button
        wait_for_after_save = self.web_element.waitElement(1000)
        page_actions = [
            to_go,
            add,
            wait_for,
            employer,
            from_date,
            to_date,
            q_a,
            q_b,
            q_c,
            q_d,
            q_e,
            q_f,
            q_g,
            q_h,
            save,
            wait_for_after_save,
        ]
        # return page
        next_page_tag = "#\\39 433 > div > input:nth-child(4)"  # Hours and pay No id
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Wish to go and CAP calculation?",
        ).page

    @property
    def wish_to_go2(self):
        # answer the question always as Yes
        wish_to_go_id = "#\\39 411 > div > input:nth-child(1)"
        to_go = self.web_element.radioElement(wish_to_go_id, label="Yes")

        # CAP calculation
        add = self.web_element.buttonElement("#addImpactcap", label="Add")
        wait_for = self.web_element.waitForElement("#\\39 420 > select")
        # use first word of employer name as keyword to pick
        employer_name_keyword = self.app.general.legal_name.split(" ")[0]
        employer = self.web_element.selectElement(
            "#\\39 399 > select",
            employer_name_keyword,
            label="pick employer",
            select_by_text=True,
        )
        from_date = self.web_element.inputElement(
            "#\\39 400 > input",
            self.app.emp5627.four_week_start_date,
            label="From",
            set_value=True,
        )
        to_date = self.web_element.inputElement(
            "#\\39 401 > input",
            self.app.emp5627.four_week_end_date,
            label="To",
            set_value=True,
        )
        q_a = self.web_element.inputElement(
            "#\\39 402 > input", str(self.app.emp5627.q_a), label="Question A"
        )
        q_b = self.web_element.inputElement(
            "#\\39 403 > input", str(self.app.emp5627.q_b), label="Question B"
        )
        q_c = self.web_element.inputElement(
            "#\\39 404 > input", str(self.app.emp5627.q_c), label="Question C"
        )
        q_d = self.web_element.inputElement(
            "#\\39 405 > input", str(self.app.emp5627.q_d), label="Question D"
        )
        q_e = self.web_element.inputElement(
            "#\\39 406 > input", str(self.app.emp5627.q_e), label="Question E"
        )
        q_f = self.web_element.inputElement(
            "#\\39 407 > input", str(self.app.emp5627.q_f), label="Question F"
        )
        q_g = self.web_element.inputElement(
            "#\\39 408 > input", str(self.app.emp5627.q_g), label="Question G"
        )
        q_h = self.web_element.inputElement(
            "#\\39 409 > input", str(self.app.emp5627.q_h), label="Question H"
        )
        save = self.web_element.buttonElement("#saveImpactcap", label="Save")
        # wait_for_after_save = self.web_element.waitForElement(
        #     "#impactcapTable > tbody > tr > td:nth-child(23) > button.btn.btn-default.editImpactcap"
        # )  # wait for table's edit button
        wait_for_after_save = self.web_element.waitElement(1000)

        page_actions = [
            to_go,
            add,
            wait_for,
            employer,
            from_date,
            to_date,
            q_a,
            q_b,
            q_c,
            q_d,
            q_e,
            q_f,
            q_g,
            q_h,
            save,
            wait_for_after_save,
        ]
        # return page
        next_page_tag = "#\\39 433 > div > input:nth-child(4)"  # Hours and pay No id
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Wish to go and CAP calculation?",
        ).page
