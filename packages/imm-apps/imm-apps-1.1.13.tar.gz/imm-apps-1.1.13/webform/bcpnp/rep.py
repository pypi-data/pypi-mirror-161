from tkinter import Label
from webform.formcontrol import WebElement
from webform.webcommon import Page
from model.common.rcic import Rcics


class Representative:
    def __init__(self, rep: object, rcic_id_name):
        self.rep = rep
        self.we = WebElement()
        self.rcic = Rcics(self.rep.rciclist).getRcicByIdName(rcic_id_name)

    def fill(self):
        return [self.gotoRepPage, self.repPage]

    @property
    def gotoRepPage(self):
        page_actions = [
            self.we.buttonElement(
                "#navigation__list > li:nth-child(5) > a", label="Representative"
            ),
        ]
        next_page_tag = "#lastName"
        page = Page(
            page_actions,
            "body > div > main > div.layout-container > div > div > a",
            next_page_tag=next_page_tag,
            label="Add representative",
        )
        return page

    @property
    def repPage(self):
        page_actions = self.repInfo + self.repType + self.repAuth
        next_page_tag = (
            "body > div > main > div.layout-container > div > div > a:nth-child(3)"
        )
        return Page(
            page_actions,
            "#form > div > div > input",
            next_page_tag,
            label="Save representative",
        )

    @property
    def repInfo(self):
        return [
            self.we.inputElement("#lastName", self.rcic.last_name, label="Last name"),
            self.we.inputElement(
                "#firstName", self.rcic.first_name, label="First name"
            ),
            self.we.inputElement(
                "#organization", self.rcic.employer_legal_name, label="Employer name"
            ),
            self.we.inputElement("#phone", self.rcic.phone, label="Phone"),
            self.we.inputElement("#phoneSecondary", "", "Secondary phone"),
            self.we.inputElement("#email", self.rcic.email, label="Email"),
            self.we.selectElement("#country", self.rcic.country, label="Country"),
            self.we.inputElement("#addressLine", self.rcic.line1, label="Address line"),
            self.we.inputElement("#city", self.rcic.city, label="City"),
            self.we.inputElement("#state", self.rcic.province, label="Province"),
            self.we.inputElement("#postalCode", self.rcic.post_code, label="Post code"),
        ]

    @property
    def repType(self):
        return [
            self.we.radioElement(
                "#form > fieldset:nth-child(7) > div > div:nth-child(1) > div > div:nth-child(3) > label > input[type=radio]",
                label="Paid",
            ),
            self.we.radioElement(
                "#form > fieldset:nth-child(7) > div > div:nth-child(2) > div > div:nth-child(3) > label > input[type=radio]",
                label="Yes ICCRC",
            ),
            self.we.inputElement(
                "#crcMembershipId", self.rcic.rcic_number, label="RCIC number"
            ),
        ]

    @property
    def repAuth(self):
        return [
            self.we.checkboxElement(
                "#form > fieldset:nth-child(8) > div > div:nth-child(2) > label > input[type=checkbox]:nth-child(2)",
                True,
                label="Authorise Rep",
            ),
            self.we.checkboxElement(
                "#form > fieldset:nth-child(8) > div > div:nth-child(3) > label > input[type=checkbox]:nth-child(2)",
                True,
                label="Authorise BCPNP",
            ),
            # self.we.uploadElement("#form > fieldset:nth-child(8) > div > div.row > div > div.input-group.file-wrapper > div > button",rep_ee,label="Upload rep form for employee")
            # self.we.uploadElement("#form > fieldset:nth-child(9) > div > div > div > div.input-group.file-wrapper > div > button",rep_er,label="Upload rep form for employer")
        ]
