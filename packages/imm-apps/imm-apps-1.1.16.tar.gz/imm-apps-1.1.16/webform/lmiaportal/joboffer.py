from webform.webcommon import WebPages, Page


class JobOffer(WebPages):
    @property
    def actions(self):
        return [self.page1, *self.page2, self.page3, self.page4]

    @property
    def page1(self):
        if self.app.joboffer.english_french:
            # radio_id = "#\\39 456 > div > input:nth-child(7)"
            radio_id = (
                "#\\39 456 > div > input:nth-child(1)"  # 5593 TODO: 5593 5626的情况不一样
            )
            next_page_tag = (
                "#\\39 461 > div > input:nth-child(4)"  # require other language-> NO id
            )

        elif self.app.joboffer.is_primary_agriculture_position:
            radio_id = "#\\39 456 > div > input:nth-child(4)"
            next_page_tag = (
                "#\\39 463 > div > input:nth-child(4)"  # minimum education -> No id
            )
        else:
            radio_id = "#\\39 456 > div > input:nth-child(1)"
            next_page_tag = (
                "#\\39 463 > div > input:nth-child(4)"  # minimum education -> No id
            )

        page_actions = [
            self.web_element.inputElement(
                "#\\39 452 > input", self.app.joboffer.job_title, label="Job title"
            ),
            self.web_element.areatextElement(
                "#\\39 453 > textarea", self.app.joboffer.duties, label="Job duties"
            ),
            self.web_element.areatextElement(
                "#\\39 454 > textarea",
                self.app.position.why_hire,
                label="The rational for opening this position",
            ),
            self.web_element.inputElement(
                "#\\39 455 > input",
                self.app.joboffer.work_start_date,
                label="Expected employment start date",
                set_value=True,
            ),
            self.web_element.radioElement(
                radio_id,
                label="Require the ability to communicate in a specific language?",
            ),
        ]

        return Page(
            page_actions, "#next", next_page_tag, label="Page 1 of job offer"
        ).page

    @property
    def page2(self):
        # has minimum edu required
        minimum_edu_req_id = (
            "#\\39 463 > div > input:nth-child(1)"
            if self.app.joboffer.education_level
            else "#\\39 463 > div > input:nth-child(4)"
        )
        minimum_edu_req = self.web_element.radioElement(
            minimum_edu_req_id, label="Minimum education reuqired"
        )

        next_page_tag = "#\\39 467 > div > input:nth-child(4)"  # Is the occupation regulated -> No id
        # if required English/French
        if self.app.joboffer.english_french:
            oral_ids = {
                "English": "#\\39 459 > div > input:nth-child(1)",
                "French": "#\\39 459 > div > input:nth-child(4)",
                "English and French": "#\\39 459 > div > input:nth-child(7)",
                "English or French": "#\\39 459 > div > input:nth-child(10)",
            }
            writting_ids = {
                "English": "#\\39 460 > div > input:nth-child(1)",
                "French": "#\\39 460 > div > input:nth-child(4)",
                "English and French": "#\\39 460 > div > input:nth-child(7)",
                "English or French": "#\\39 460 > div > input:nth-child(10)",
            }
            other_language_id = (
                "#\\39 461 > div > input:nth-child(1)"
                if self.app.joboffer.other_language_required
                else "#\\39 461 > div > input:nth-child(4)"
            )
            oral = self.web_element.radioElement(
                oral_ids.get(self.app.joboffer.oral), label="Oral"
            )
            writting = self.web_element.radioElement(
                writting_ids.get(self.app.joboffer.writing), label="Writting"
            )
            other_language = self.web_element.radioElement(
                other_language_id, label="Require other language than English/French"
            )
            next_page_tag = (
                "#\\39 463 > div > input:nth-child(4)"  # minumum edu -> NO id
            )
            # page 1 of yes, input details
            p1 = Page(
                [oral, writting, other_language],
                "#next",
                next_page_tag,
                label="Page 2 Language English/French detail",
            ).page

            p2_actions = (
                [
                    self.web_element.areatextElement(
                        "#\\39 462 > textarea",
                        self.app.joboffer.reason_for_other,
                        label="Reason for other language required",
                    )
                ]
                if self.app.joboffer.other_language_required
                else []
            )
            p2_actions.append(minimum_edu_req)
            p2 = Page(
                p2_actions,
                "#next",
                next_page_tag,
                label="Page 2:has language required of Job offer detail",
            ).page

            return [p1, p2]

        elif self.app.joboffer.is_primary_agriculture_position:
            return [
                Page(
                    [minimum_edu_req],
                    "#next",
                    next_page_tag,
                    label="Page 2: language exempted for primary agriculture",
                ).page
            ]
        else:
            # if not required English/French
            rationale = self.web_element.areatextElement(
                "#\\39 457 > textarea",
                self.app.joboffer.reason_for_no,
                label="Rationale for no English/French requirement",
            )
            return [
                Page(
                    [rationale, minimum_edu_req],
                    "#next",
                    next_page_tag,
                    label="Page 2: no language required",
                ).page
            ]

    @property
    def page3(self):
        # education

        if self.app.joboffer.is_trade:
            trade_types = {
                "Apprenticeship diploma/certificate": "#\\39 464 > div > input:nth-child(1)",
                "Trade diploma/certificate": "#\\39 464 > div > input:nth-child(34)",
                "Vocational school diploma/certificate": "#\\39 464 > div > input:nth-child(37)",
            }
            minimum_edu_id = trade_types.get(self.app.joboffer.trade_type)
        else:
            minimum_edu_ids = {
                "Doctor": "#\\39 464 > div > label:nth-child(14)",
                "Master": "#\\39 464 > div > input:nth-child(16)",
                "Post-graduate diploma": None,
                "Bachelor": "#\\39 464 > div > input:nth-child(4)",
                "Associate": None,
                "Diploma/Certificate": "#\\39 464 > div > input:nth-child(7)",
                "High school": "#\\39 464 > div > input:nth-child(31)",
                "Less than high school": "#\\39 464 > div > input:nth-child(19)",
            }
            minimum_edu_id = minimum_edu_ids.get(self.app.joboffer.education_level)
        minimum_edu = self.web_element.radioElement(
            minimum_edu_id, label="Indicate the minimum education"
        )

        specific_edu = self.web_element.areatextElement(
            "#\\39 465 > textarea",
            self.app.joboffer.specific_edu_requirement,
            label="Specific education requirement",
        )
        experience = self.web_element.areatextElement(
            "#\\39 466 > textarea",
            self.app.joboffer.skill_experience_requirement,
            label="Experience requirement",
        )
        license_required_id = (
            "#\\39 467 > div > input:nth-child(1)"
            if self.app.joboffer.license_request
            else "#\\39 467 > div > input:nth-child(4)"
        )
        license_required = self.web_element.radioElement(
            license_required_id, label="Is the occupation regulated?"
        )
        page_actions = [minimum_edu, specific_edu, experience, license_required]
        next_page_tag = "#\\39 470 > div > input:nth-child(4)"  # is the position part of a union -> No id
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Page 3: Education of job offer details",
        ).page

    @property
    def page4(self):
        page_actions = (
            [
                self.web_element.areatextElement(
                    "#\39 468 > textarea",
                    self.app.joboffer.license_description,
                    label="License body",
                )
            ]
            if self.app.joboffer.license_request
            else []
        )

        union_id = (
            "#\\39 470 > div > input:nth-child(1)"
            if self.app.joboffer.union
            else "#\\39 470 > div > input:nth-child(4)"
        )
        page_actions.append(
            self.web_element.radioElement(
                union_id, label="Is the position part of a union?"
            )
        )
        next_page_tag = (
            "#\\39 471 > div > input:nth-child(4)"  # will you provide benefits -> No id
        )
        return Page(page_actions, "#next", next_page_tag, label="Union").page
