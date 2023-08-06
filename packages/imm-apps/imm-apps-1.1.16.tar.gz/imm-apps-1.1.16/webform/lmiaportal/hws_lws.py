from webform.webcommon import WebPages
from webform.lmiaportal.wage import Wage
from webform.lmiaportal.foreignnational import ForeignNational

# 1. Common part of High Wage stream and Low Wage Stream
class HWS_LWS(WebPages):
    @property
    def actions(self):
        return [self.page1, *self.page2, *self.page3]

    @property
    def page1(self):
        """Check if Quebec's facilitated process.
        We assume that we don't do Quebec LMIA, so here are all answer no
        """
        answer_no = self.web_element.radioElement(
            "#\\39 138 > div > input:nth-child(4)", label="No"
        )
        next_page_tag = "#\\39 159 > div > input:nth-child(4)"  # wage converted? No id
        return self.web_element.pageElement(
            "#next",
            next_page_tag,
            [answer_no],
            label="No for Quebec facilitated process",
        )

    @property
    def page2(self):
        """Wage and work location, which is same as EE"""
        return Wage(self.app).actions

    @property
    def page3(self):
        """Provide TFW's name? and if so, TFW's details"""
        named = (
            self.app.lmiacase.stream_of_lmia == "LWS" and self.app.emp5627.named
        ) or (self.app.lmiacase.stream_of_lmia == "HWS" and self.app.emp5626.named)

        provide_tfw_name_id = (
            "#\\39 180 > div > input:nth-child(1)"
            if named
            else "#\\39 180 > div > input:nth-child(4)"
        )
        provide_tfw_name = self.web_element.radioElement(
            provide_tfw_name_id,
            label="Yes" if named else "No",
        )

        if named:
            next_page_tag = (
                "#\\39 181 > div > input:nth-child(4)"  # use online feature No id
            )
            provide_name_page = self.web_element.pageElement(
                "#next", next_page_tag, [provide_tfw_name], label="Provide TFW's name?"
            )
            foreign_national_pages = ForeignNational(self.app).actions
            return [provide_name_page, *foreign_national_pages]
        else:
            # provide accomadation No id if LWS, else if in seasonal occupation if HWS
            next_page_tag = (
                "#\\39 378 > div > input:nth-child(4)"
                if self.app.lmiacase.stream_of_lmia == "LWS"
                else "#\\39 349 > div > input:nth-child(4)"
            )
            return [
                self.web_element.pageElement(
                    "#next",
                    next_page_tag,
                    [provide_tfw_name],
                    label="Provide TFW's name?",
                )
            ]
