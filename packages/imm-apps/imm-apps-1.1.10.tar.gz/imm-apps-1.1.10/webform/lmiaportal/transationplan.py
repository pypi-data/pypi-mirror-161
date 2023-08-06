from webform.webcommon import WebPages, Page

#  Transition plan
class TransitionPlan(WebPages):
    @property
    def actions(self):
        tp_waivable = True if self.app.emp5626.tp_waivable else False
        return (
            [self.page1, self.page2, self.pages_after_if_exempted]
            if tp_waivable
            else [self.page1, self.page2, self.completed_tp, self.transition_plan]
        )

    @property
    def page1(self):
        """Is this application for a seasonal occupation?"""
        is_seasonal = True if self.app.emp5626.is_in_seasonal_industry else False
        for_seasonal_id = (
            "#\\39 349 > div > input:nth-child(1)"
            if is_seasonal
            else "#\\39 349 > div > input:nth-child(4)"
        )
        for_seasonal = self.web_element.radioElement(
            for_seasonal_id, label="Yes" if is_seasonal else "No"
        )
        next_page_tag = "#\\39 358 > div > input:nth-child(4)"  # wish to consider be exempted? No id
        return Page(
            [for_seasonal],
            "#next",
            next_page_tag,
            label="Is this for a seasonal occupation?",
        ).page

    @property
    def page2(self):
        is_seasonal = True if self.app.emp5626.is_in_seasonal_industry else False
        # if tp waived, hour and pay has same position no id
        # if not, have you completed a TP? No id
        next_page_tag = (
            "#\\39 433 > div > input:nth-child(4)"
            if self.app.emp5626.tp_waivable
            else "#\\39 362 > div > input:nth-child(4)"
        )
        if is_seasonal:
            return Page(
                [*self.seasonal_position, *self.hw_tp, self.do_you_wish],
                "#next",
                next_page_tag,
                label="Seasonal positions and high wage Transition Plan",
            ).page
        else:
            return Page(
                [*self.hw_tp, self.do_you_wish],
                "#next",
                next_page_tag,
                label="High wage Transition Plan",
            ).page

    @property
    def seasonal_position(self):
        how_many_canadians_past = self.web_element.inputElement(
            "#\\39 354 > input",
            str(self.app.emp5626.last_canadian_number),
            label="How many Canadians last peak period?",
        )
        how_many_tfws_past = self.web_element.inputElement(
            "#\\39 355 > input",
            str(self.app.emp5626.last_tfw_number),
            label="How many TFWs last peak period?",
        )
        from_month = self.web_element.selectElement(
            "#\\39 352 > select",
            self.app.emp5626.start_month,
            label="Start month of last peak season",
        )
        to_month = self.web_element.selectElement(
            "#\\39 353 > select",
            self.app.emp5626.end_month,
            label="End month of last peak season",
        )
        return [how_many_canadians_past, how_many_tfws_past, from_month, to_month]

    @property
    def hw_tp(self):
        how_many_canadians = self.web_element.inputElement(
            "#\\39 356 > input",
            str(self.app.emp5626.current_canadian_number),
            label="How many Canadians currently?",
        )
        how_many_tfws = self.web_element.inputElement(
            "#\\39 357 > input",
            str(self.app.emp5626.current_tfw_number),
            label="How many TFWs currently?",
        )
        return [how_many_canadians, how_many_tfws]

    @property
    def do_you_wish(self):
        tp_waivable = True if self.app.emp5626.tp_waivable else False
        consider_exempted_id = (
            "#\\39 358 > div > input:nth-child(1)"
            if tp_waivable
            else "#\\39 358 > div > input:nth-child(4)"
        )
        consider_exempted = self.web_element.radioElement(
            consider_exempted_id, label="Yes" if tp_waivable else "No"
        )
        # if waivable, goto hours and pay has same position, No id
        # else, goto "have you completed a TP?" id No
        # next_page_tag = (
        #     "#\\39 433 > div > input:nth-child(4)"
        #     if tp_waivable
        #     else "#\\39 362 > div > input:nth-child(4)"
        # )
        # return Page(
        #     [consider_exempted],
        #     "#next",
        #     next_page_tag,
        #     label="Is the application wavied from Transition Plan?",
        # ).page
        return consider_exempted

    # exempted functions
    @property
    def pages_after_if_exempted(self):
        page_actions = [
            self.exemption_criteria,
            self.details_support_exemption,
            self.hours_pay,
        ]
        next_page_tag = (
            "#\\39 438 > div > input:nth-child(4)"  # atypical schedule? No id
        )
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Exemption criteria and has same position",
        ).page

    @property
    def exemption_criteria(self):
        criteria_types = {
            "Caregiver positions in health care institutions": "#\\39 360 > div > input:nth-child(1)",
            "Limited duration positions": "#\\39 360 > div > input:nth-child(4)",
            "On-farm primary agricultural positions": "#\\39 360 > div > input:nth-child(7)",
            "Positions within a specialized occupation": "#\\39 360 > div > input:nth-child(10)",
            "Unique skills or traits": "#\\39 360 > div > input:nth-child(13)",
        }
        return self.web_element.radioElement(
            criteria_types.get(self.app.emp5626.waive_creteria),
            label="Which transition plan exemption?",
        )

    @property
    def details_support_exemption(self):
        return self.web_element.areatextElement(
            "#\\39 361 > textarea",
            self.app.emp5626.waive_creteria,
            label="Details to support the exemption",
        )

    # not exempted functions
    @property
    def completed_tp(self):
        is_completed_id = (
            "#\\39 362 > div > input:nth-child(1)"
            if self.app.emp5626.has_finished_tp
            else "#\\39 362 > div > input:nth-child(4)"
        )
        is_completed = self.web_element.radioElement(
            is_completed_id, label="Yes" if self.app.emp5626.has_finished_tp else "No"
        )
        next_page_tag = "#\\39 433 > div > input:nth-child(4)"  # Hours and pay has same position NO id
        return Page(
            [is_completed],
            "#next",
            next_page_tag,
            label="Have you completed a Transition Plan?",
        ).page

    @property
    def transition_plan(self):
        actions = [self.pre_tp_description] if self.app.emp5626.has_finished_tp else []
        actions.extend([*self.add_tps, self.hours_pay])
        next_page_tag = (
            "#\\39 438 > div > input:nth-child(4)"  # atypical schedule id no
        )
        return Page(actions, "#next", next_page_tag, label="Transition Plan").page

    @property
    def pre_tp_description(self):
        return self.web_element.areatextElement(
            "#\\39 364 > textarea",
            self.app.emp5626.finished_tp_result,
            label="Previous transition plan activity description",
        )

    def add_tp(self, index):
        add = self.web_element.buttonElement("#addActivities", label="Add")
        wait_for_element = self.web_element.waitForElement(
            "#\\39 373 > textarea"
        )  # wait for new elements appear, additional employer comments id

        title = self.web_element.inputElement(
            "#\\39 370 > input",
            getattr(self.app.emp5626, f"activity{index}_title"),
            label="Title",
        )
        description = self.web_element.areatextElement(
            "#\\39 371 > textarea",
            getattr(self.app.emp5626, f"activity{index}_description"),
            label="Activity description",
        )
        outcome = self.web_element.areatextElement(
            "#\\39 372 > textarea",
            getattr(self.app.emp5626, f"activity{index}_outcome"),
            label="Activity outcome",
        )
        comment = self.web_element.areatextElement(
            "#\\39 373 > textarea",
            getattr(self.app.emp5626, f"activity{index}_comment"),
            label="Employer comment",
        )

        save = self.web_element.buttonElement("#saveActivities", label="Save")
        wait1s = self.web_element.waitElement(1000)
        return [
            add,
            wait_for_element,
            title,
            description,
            outcome,
            comment,
            save,
            wait1s,
        ]

    @property
    def add_tps(self):
        tps = []
        for i in range(1, 6):
            tp = self.add_tp(i)
            tps.extend(tp)

        confirm = self.web_element.checkboxElement(
            "#\\39 376 > input", True, label="I have read"
        )
        tps.append(confirm)
        return tps

    @property
    def hours_pay(self):
        has_same_id = (
            "#\\39 433 > div > input:nth-child(1)"
            if self.app.position.has_same
            else "#\\39 433 > div > input:nth-child(4)"
        )
        return self.web_element.radioElement(
            has_same_id, label="Has same employee in the position"
        )
