from webform.webcommon import WebPages, Page
from model.common.advertisement import Advertisements, InterviewRecords
from model.common.finance import Finances


class Recruitment(WebPages):
    """
    1. variation?
        yes->reason + provide detais of recruitment?    Yes -> Use job bank?    Yes/No->recruitment summary+lmi
        No->attempted recruit?  Yes->Use jobbank?   Yes/NO->recruitment summary+lmi
                                                    No ->reason+lmi
    """

    @property
    def actions(self):
        return [self.page1, *self.page2]

    @property
    def page1(self):
        has_variation_id = (
            "#\\39 484 > div > input:nth-child(1)"
            if self.app.lmiacase.is_waived_from_advertisement
            else "#\\39 484 > div > input:nth-child(4)"
        )
        page_actions = [
            self.web_element.radioElement(
                has_variation_id,
                label="Is the position subject to a variation in advertisement",
            )
        ]
        # based on yes or no variation
        next_page_tag = (
            "#\\39 486 > textarea"
            if self.app.lmiacase.is_waived_from_advertisement
            else "#\\39 488 > div > input:nth-child(4)"
        )
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Page 1 of Advertisement variation",
        ).page

    @property
    def page2(self):
        if self.app.lmiacase.is_waived_from_advertisement:
            sub_p1 = self.variation_yes()
            if self.app.lmiacase.provide_details_even_waived:
                sub_p2 = self.use_jobbank()
                sub_p3 = self.use_jobbank_follower()
                return [sub_p1, sub_p2, sub_p3]
            else:
                return [sub_p1, *self.lmi]
        else:
            sub_p1 = self.attempted_to_hire()
            # if not waived from advertisement, attemp to hire is must, so we do not check and go directly yes
            sub_p2 = self.use_jobbank()
            sub_p3 = self.use_jobbank_follower()
            return [sub_p1, sub_p2, sub_p3]

    def use_jobbank_follower(self):
        if self.app.lmiacase.use_jobbank:
            jobbank = Advertisements(self.app.advertisement).jobbank
            post_id = jobbank.advertisement_id if jobbank else ""
            isjobbank = self.web_element.inputElement(
                "#\\39 491 > input", post_id, label="Job post Id"
            )
            sub_p3_page_actions = [isjobbank, *self.recruiment_summary, *self.lmi]
        else:
            # explain why not using jobbank
            why_not_jobbank = self.web_element.areatextElement(
                "#\\39 492 > textarea",
                self.app.lmiacase.reason_not_use_jobbank,
                label="Why not using jobbank",
            )
            sub_p3_page_actions = [
                why_not_jobbank,
                *self.recruiment_summary,
                *self.lmi,
            ]
        next_page_tag = "#\\39 508 > div > input:nth-child(4)"  # Skill and knowledge transfer? No-> Id
        sub_p3 = self.web_element.pageElement(
            "#next",
            next_page_tag,
            actions=sub_p3_page_actions,
            label="Recruitment summary and LMI",
        )

        return sub_p3

    def attempted_to_hire(self):
        # if not variation, ask for attempted to recruit. It is must, so only yes here
        have_attemped = "#\\39 488 > div > input:nth-child(1)"
        page_actions = [self.web_element.radioElement(have_attemped, label="Yes")]
        next_page_tag = "#\\39 490 > div > input:nth-child(4)"  # using job bank No-id
        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="have you attempted to recruit Canadians",
        ).page

    def variation_yes(self):
        rational = self.web_element.areatextElement(
            "#\\39 486 > textarea",
            self.app.lmiacase.reason_for_waived,
            label="Creteria and reason for waiving advertisement",
        )
        provide_details_id = (
            "#\\39 487 > div > input:nth-child(1)"
            if len(self.app.interviewrecord) > 0
            else "#\\39 487 > div > input:nth-child(4)"
        )
        will_provide_details = self.web_element.radioElement(
            provide_details_id,
            label="In addition to applying for the variation, would provide recruitment details",
        )
        page_actions = [rational, will_provide_details]
        next_page_tag = "#\\39 490 > div > input:nth-child(4)"  # Using job bank? No id

        return Page(
            page_actions,
            "#next",
            next_page_tag,
            label="Page 2 of advertisement variation",
        ).page

    def use_jobbank(self):
        using_jobbank_id = (
            "#\\39 490 > div > input:nth-child(1)"
            if self.app.lmiacase.use_jobbank
            else "#\\39 490 > div > input:nth-child(4)"
        )
        next_page_tag2 = "#\\39 506 > div > input:nth-child(4)"  # Will hiring a TFW result in direct job creation -> NO id

        # use job bank?
        return Page(
            [self.web_element.radioElement(using_jobbank_id, label="Using job bank?")],
            "#next",
            next_page_tag2,
            label="Page 2.1 Using job bank",
        ).page

    @property
    def recruiment_summary(self):
        summary = InterviewRecords(self.app.interviewrecord)
        rs = [
            self.web_element.inputElement(
                "#\\39 494 > input",
                str(summary.canadian_num),
                label="number of Canadians",
            ),
            self.web_element.inputElement(
                "#\\39 495 > input",
                str(summary.total_interviewed_canadians),
                label="Total Canadians interviewed",
            ),
            self.web_element.inputElement(
                "#\\39 496 > input",
                str(summary.total_offered_canadians),
                label="Total Canadians offered",
            ),
            self.web_element.inputElement(
                "#\\39 497 > input",
                str(summary.total_hired_canadians),
                label="Total Canadians hired",
            ),
            self.web_element.inputElement(
                "#\\39 498 > input",
                str(summary.total_declined_joboffer_canadians),
                label="Total Canadians declined offer",
            ),
            self.web_element.inputElement(
                "#\\39 499 > input",
                str(summary.canadian_applied_not_interviewed_or_offered),
                label="Total Canadians applied but not interviewed or offered the job",
            ),
            self.web_element.areatextElement(
                "#\\39 500 > textarea",
                str(summary.why_canadians_not_hired),
                label="Why Canadian not hired",
                length=4000,
            ),
        ]

        return rs

    @property
    def lmi(self):
        """Labour Market Impacts"""
        employee_number = self.web_element.inputElement(
            "#\\39 502 > input", str(self.app.general.ft_employee_number)
        )
        last_revenue = Finances(self.app.finance).last_income or 0
        revenue_more_than_5m_id = (
            "#\\39 503 > div > input:nth-child(1)"
            if last_revenue >= 5000000
            else "#\\39 503 > div > input:nth-child(4)"
        )
        revenue_more_than_5m = self.web_element.radioElement(
            revenue_more_than_5m_id, label="Revenue more than 5M"
        )

        job_creation_id = (
            "#\\39 506 > div > input:nth-child(1)"
            if self.app.lmi.job_creation_benefit
            else "#\\39 506 > div > input:nth-child(4)"
        )
        job_creation = self.web_element.radioElement(
            job_creation_id, label="Job creation"
        )
        return [employee_number, revenue_more_than_5m, job_creation]
