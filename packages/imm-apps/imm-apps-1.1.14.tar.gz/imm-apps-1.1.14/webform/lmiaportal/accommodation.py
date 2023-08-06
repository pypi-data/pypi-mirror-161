from webform.webcommon import WebPages, Page

# 1. Accomadation for LWS
class Accommodation(WebPages):
    @property
    def actions(self):
        return [self.page1, *self.page2]

    @property
    def page1(self):
        provide_accommodation_id = (
            "#\\39 378 > div > input:nth-child(1)"
            if self.app.emp5627.provide_accommodation
            else "#\\39 378 > div > input:nth-child(4)"
        )
        provide_accommodation = self.web_element.radioElement(
            provide_accommodation_id,
            label="Yes" if self.app.emp5627.provide_accommodation else "No",
        )

        # next page tag: if provide, wait for rent amount id, if no then wait for the id of explaination
        next_page_tag = (
            "#\\39 382 > input"
            if self.app.emp5627.provide_accommodation
            else "#\\39 379 > textarea"
        )
        return Page(
            [provide_accommodation],
            "#next",
            next_page_tag,
            label="Provide TFW accommodation?",
        ).page

    @property
    def page2(self):
        """includes sub pages if yes to provide the accommodation"""
        # question for if exempted from CAP
        is_exempted_id = (
            "#\\39 391 > div > input:nth-child(1)"
            if self.app.emp5627.cap_exempted
            else "#\\39 391 > div > input:nth-child(4)"
        )
        is_exempted = self.web_element.radioElement(
            is_exempted_id, "Yes" if self.app.emp5627.cap_exempted else "No"
        )

        if self.app.emp5627.provide_accommodation:
            sub_p1 = self.accommodation_details1()
            sub_p2 = self.accommodation_details2(is_exempted)
            return [sub_p1, sub_p2]
        else:
            explain_why_not_provide = self.web_element.areatextElement(
                "#\\39 379 > textarea",
                self.app.emp5627.description,
                label="Explain how to assist TFW for accommodation",
            )
            # if exempted from CAP, then goto hours and pay, no id,
            # if not, then goto ask if it is seasonal, no id
            next_page_tag = (
                "#\\39 433 > div > input:nth-child(4)"
                if self.app.emp5627.cap_exempted
                else "#\\39 395 > div > input:nth-child(4)"
            )
            return [
                Page(
                    [explain_why_not_provide, is_exempted],
                    "#next",
                    next_page_tag,
                    label="Accommodation explaination",
                ).page
            ]

    def accommodation_details1(self):
        accommodation_types = {
            "apartment": "#\\39 384 > div > input:nth-child(1)",
            "dorm": "#\\39 384 > div > input:nth-child(4)",
            "house": "#\\39 384 > div > input:nth-child(7)",
            "other": "#\\39 384 > div > input:nth-child(7)",
        }
        a_type = self.app.emp5627.accommodation_type
        accommodation_type = self.web_element.radioElement(
            accommodation_types.get(a_type), label=a_type
        )

        amount = self.web_element.inputElement(
            "#\\39 382 > input", str(self.app.emp5627.rent_amount), label="rent amount"
        )
        unit = self.web_element.selectElement(
            "#\\39 383 > select", self.app.emp5627.rent_unit, select_by_text=True
        )
        next_page_tag = (
            "#\\39 391 > div > input:nth-child(4)"  # exempted from CAP no id
        )
        return Page(
            [accommodation_type, amount, unit],
            "#next",
            next_page_tag,
            label="Accommodation details type and rent amount",
        ).page

    def accommodation_details2(self, is_exempted):
        accommodation_actions = [
            self.web_element.inputElement(
                "#\\39 386 > input",
                self.app.emp5627.bedrooms,
                label="How many bed rooms",
            ),
            self.web_element.inputElement(
                "#\\39 387 > input",
                self.app.emp5627.people,
                label="How many occupants?",
            ),
            self.web_element.inputElement(
                "#\\39 388 > input",
                self.app.emp5627.bathrooms,
                label="How many bathrooms?",
            ),
            self.web_element.areatextElement(
                "#\\39 389 > textarea",
                self.app.emp5627.other or "N/A",
                label="other description",
            ),
            is_exempted,
        ]
        #  if cap exempted, go directly to hours and pay. no id
        # if not, goto ask if in seasonal industry. No id
        next_page_tag = (
            "#\\39 433 > div > input:nth-child(4)"
            if self.app.emp5627.cap_exempted
            else "#\\39 395 > div > input:nth-child(4)"
        )
        return Page(
            accommodation_actions,
            "#next",
            next_page_tag,
            label="Accommodation details 2",
        ).page
