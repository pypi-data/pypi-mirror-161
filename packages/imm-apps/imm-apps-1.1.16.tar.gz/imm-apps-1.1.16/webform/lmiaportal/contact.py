from model.common.contact import Contacts
from webform.webcommon import WebPages

"""
3rd party information and stream determination

"""


class Contact(WebPages):
    @property
    def getPrimaryContact(self):
        return Contacts(self.app.contact).primary.full_name

    @property
    def actions(self):
        return [self.employerContactPage, *self.thirdpartyInfoPages]

    @property
    def employerContactPage(self):
        next_page_tag = "#\\39 130 > div > input:nth-child(1)"  # Yes button for rep

        select_contact = self.web_element.selectElement(
            "#\\39 124 > select",
            self.getPrimaryContact,
            label="Select employer contact",
            select_by_text=True,
        )
        wait1s = self.web_element.waitElement(1000)
        confirm = self.web_element.checkboxElement(
            "#\\39 125 > input", True, label="Confirm it's primary contact"
        )
        add = self.web_element.buttonElement("#addContact", label="Add")
        third_party = self.web_element.radioElement(
            "#\\39 127 > div > input:nth-child(1)", label="Yes"
        )
        page_actions = [select_contact, wait1s, confirm, add, wait1s, third_party]
        return self.web_element.pageElement(
            "#next", next_page_tag, page_actions, label="Employer contact"
        )

    @property
    def thirdpartyInfoPages(self):
        # RCIC name and if paid
        actions1 = [
            self.web_element.selectElement(
                "#\\39 129 > select",
                self.app.rcic.full_name,
                label="Third party",
                select_by_text=True,
            ),
            self.web_element.radioElement(
                "#\\39 130 > div > input:nth-child(1)", label="Is the third party paid?"
            ),
        ]
        page1 = self.web_element.pageElement(
            "#next",
            "#\\39 131 > div > input:nth-child(10)",
            actions=actions1,
            label="Third party representative information",
        )

        # rcic regulator
        actions2 = [
            self.web_element.checkboxElement(
                "#\\39 131 > div > input:nth-child(1)", True, label="ICCRC"
            )
        ]
        page2 = self.web_element.pageElement(
            "#next", "#\\39 132 > input", actions=actions2, label="ICCRC info"
        )

        # RCIC number and LMIA stream
        # EE(Express Entry: 5593),HWS(High Wage Stream: 5626),WS(Low Wage Stream: 5627),
        # GTS(Global Talent Stream: 5624, 5625),AC (Academic: 5626),AG (Agriculture: 5519, 5510), CG(CareGiver 5604)
        stream_ids = {
            "GTS": "#\\39 137 > div > input:nth-child(1)",
            "AG": "#\\39 137 > div > input:nth-child(7)",
            "EE": "#\\39 137 > div > input:nth-child(10)",
            "AC": "#\\39 137 > div > input:nth-child(13)",
            "HWS": "#\\39 137 > div > input:nth-child(16)",
            "LWS": "#\\39 137 > div > input:nth-child(16)",
            "CG": "#\\39 137 > div > input:nth-child(19)",
        }
        actions3 = [
            self.web_element.inputElement(
                "#\\39 132 > input",
                self.app.rcic.rcic_number,
                label="Third party number",
                length=10,
            ),
            self.web_element.radioElement(
                stream_ids.get(self.app.lmiacase.stream_of_lmia),
                label="Stream determination",
            ),
        ]

        # After stream determination
        gts_tag = "#\\39 139 > div > input:nth-child(4)"
        wage_tag = "#\\39 158 > input"
        wage_compare_provincial = "#\\39 138 > div > input:nth-child(1)"
        stream_next_tags = {
            "GTS": gts_tag,
            "AG": wage_tag,
            "EE": wage_tag,
            "AC": wage_tag,
            "HWS": wage_compare_provincial,
            "LWS": wage_compare_provincial,
            "CG": wage_tag,
        }
        page3 = self.web_element.pageElement(
            "#next",
            stream_next_tags.get(self.app.lmiacase.stream_of_lmia),
            actions=actions3,
            label="Third party information and stream determination",
        )

        return [page1, page2, page3]
