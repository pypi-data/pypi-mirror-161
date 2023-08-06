from datetime import date
from typing import Union
from urllib.parse import ParseResultBytes
from pdfform.tr import option_lists
from pdfform.jsonmaker import JsonMaker
from model.common.cor import CORs
from model.common.id import ID, IDs
from model.common.address import Address, Addresses
from model.common.phone import Phone, Phones
from model.common.educationbase import EducationBase, EducationHistory


class TrCommon:
    def __init__(
        self,
        applicant: object,
    ):
        self.applicant = applicant
        self.form = JsonMaker()

    def special_YMD_handle(self, the_date):
        the_date = the_date.strftime("%Y-%m-%d") if type(the_date) == date else the_date
        year, month, day = the_date.split("-")
        self.form.add_text(year)
        self.form.add_text(month)
        self.form.add_text(day)

    def add_personal_detail(self, form_type: str = ""):
        """Add personal detail items
        1. full name
        2. other name
        3. sex
        4. date of birth
        5. place of birth
        6. citizenship
        7. current country or territory of residence
        8. previous countries or territories of residence
        9. country or territory where applying
        10. current marital status
        11. previous mariage
        """
        personal = self.applicant.personal
        self.form.add_info("personal detail section")

        self.form.add_text(personal.last_name)
        self.form.add_text(personal.first_name)

        if personal.used_first_name:
            self.form.add_radio(True)
            self.form.add_text(personal.used_last_name)
            self.form.add_text(personal.used_first_name)
        else:
            self.form.add_radio(False)
            self.form.add_skip(2)

        self.form.add_dropdown(personal.sex, option_lists.gender, like=True, pause=0.01)
        # self.form.add_skip(1)  # TODO: remove it after testing
        self.form.add_date(personal.dob, pause=0.2)

        self.form.add_text(personal.place_of_birth)
        self.form.add_dropdown(personal.country_of_birth, option_lists.country_of_birth)

        self.form.add_dropdown(
            personal.citizen, option_lists.country_of_citizen, like=True, pause=0.01
        )

        # residence
        residence = CORs(self.applicant.cor).current
        self.form.add_dropdown(residence.country, option_lists.country_of_residence)
        status = residence.status
        self.form.add_dropdown(status, option_lists.immigration_status)
        if status.lower() in ["visitor", "worker", "student"]:
            self.form.add_skip(1)
            self.form.add_date(residence.start_date)
            self.form.add_date(residence.end_date)
        elif status.lower() in ["other"]:
            self.form.add_text("")
            self.form.add_date(residence.start_date)
            self.form.add_date(residence.end_date)
        else:
            self.form.add_skip(3)

        # previous residence
        previous_cors = CORs(self.applicant.cor).previous
        if previous_cors and len(previous_cors) > 0:
            p1 = previous_cors[0]
            p2 = previous_cors[1] if len(previous_cors) > 1 else None

            self.form.add_radio(True)
            self.form.add_dropdown(p1.country, option_lists.country_of_residence)
            self.form.add_dropdown(p1.status, option_lists.immigration_status)
            self.form.add_skip(1)
            self.form.add_date(p1.start_date)
            self.form.add_date(p1.end_date)

            if p2:
                self.form.add_dropdown(p2.country, option_lists.country_of_residence)
                self.form.add_dropdown(p2.status, option_lists.immigration_status)
                self.form.add_skip(1)
                self.form.add_date(p2.start_date)
                self.form.add_date(p2.end_date)
            else:
                self.form.add_skip(5)
        else:
            self.form.add_radio(False)
            self.form.add_skip(10)

        if form_type == "1295":
            if not self.applicant.trcase.same_as_cor:
                self.form.add_radio(False)
                tr = self.applicant.trcase
                self.form.add_dropdown(
                    tr.applying_country, option_lists.previous_country
                )
                self.form.add_dropdown(
                    tr.applying_status, option_lists.immigration_status
                )
                if tr.applying_status == "Other":
                    self.form.add_text(tr.other_explain)
                else:
                    self.form.add_skip(1)
                self.form.add_date(tr.applying_start_date)
                self.form.add_date(tr.applying_end_date)

            else:
                self.form.add_radio(True)
                self.form.add_skip(5)

        marriage = self.applicant.marriage
        status = marriage.marital_status

        self.form.add_dropdown(status, option_lists.marital_status, True)
        if status.lower() in ["married", "common-law"]:
            self.form.add_date(marriage.married_date)
            self.form.add_text(marriage.sp_last_name)
            self.form.add_text(marriage.sp_first_name)
            if form_type != "1295":
                self.form.add_radio(marriage.sp_is_canadian)
        else:
            self.form.add_skip(3 if form_type == "1295" else 4)

        if marriage.previous_married:
            self.form.add_radio(True)
            self.form.add_text(marriage.pre_sp_last_name)
            self.form.add_text(marriage.pre_sp_first_name)
            self.form.add_dropdown(
                marriage.pre_relationship_type, option_lists.relation_type
            )
            self.form.add_date(marriage.pre_start_date)
            self.form.add_date(marriage.pre_end_date)
            # speciaially dealing with
            self.special_YMD_handle(marriage.pre_sp_dob)

        else:
            self.form.add_radio(False)
            self.form.add_skip(8)

    def add_language(self):
        """Add language items`
        1. native language
        """
        self.form.add_info("language section")

        self.form.add_dropdown(
            self.applicant.personal.native_language, option_lists.native_language
        )
        self.form.add_dropdown(
            self.applicant.personal.english_french, option_lists.communication_language
        )
        if self.applicant.personal.english_french.lower() == "both":
            self.form.add_text(self.applicant.personal.which_one_better)
        else:
            self.form.add_skip(1)
        if self.applicant.personal.language_test:
            self.form.add_radio(True)
        else:
            self.form.add_radio(False)

    def add_passport(self):
        """Add passport items
        1. passport number
        2. issue country`
        3. issue date
        4. expiry date
        5. Taiwan
        6. Israeli
        """
        self.form.add_info("passport section")

        passport: ID = IDs(self.applicant.personid).passport
        self.form.add_text(passport.number)
        self.form.add_dropdown(
            passport.country, option_lists.passport_issue_country, True
        )
        self.form.add_date(passport.issue_date)
        self.form.add_date(passport.expiry_date)

        if "taiwan" in passport.country.lower():
            self.form.add_radio(True)
        else:
            self.form.add_skip(1)
        if "israel" in passport.country.lower():
            self.form.add_radio(True)
        else:
            self.form.add_skip(1)

    def add_national_id(self):
        """Add national id items
        1. if has national id
        2. id number
        3. issue country
        4. issue date
        5. expiry date
        """

        self.form.add_info("national id section")
        national_id: ID = IDs(self.applicant.personid).national_id
        if national_id.number:
            self.form.add_radio(True)
            self.form.add_text(national_id.number)
            self.form.add_dropdown(
                national_id.country, option_lists.passport_issue_country, True
            )
            if national_id.issue_date:
                self.form.add_date(national_id.issue_date)
            else:
                self.form.add_skip(1)
            if national_id.expiry_date:
                self.form.add_date(national_id.expiry_date)
            else:
                self.form.add_skip(1)
        else:
            self.form.add_radio(False)
            self.form.add_skip(4)

    def add_uspr_card(self):
        self.form.add_info("US PR card section")

        """Add US PR card items"""
        pr: ID = IDs(self.applicant.personid).pr
        if pr.country and (
            "united states" in pr.country.lower() or "usa" in pr.country.lower()
        ):
            self.form.add_radio(True)
            self.form.add_text(pr.number)
            self.form.add_date(pr.expiry_date)
        else:
            self.form.add_radio(False)
            self.form.add_skip(2)

    def add_contact_information(self, form_type: str = ""):
        """Add contact information"""

        self.form.add_info("contact information section")

        address: Address = Addresses(self.applicant.address).mailing
        residential_address: Address = Addresses(self.applicant.address).residential

        self.form.add_text(address.po_box)
        self.form.add_text(address.unit)
        self.form.add_text(address.street_number)
        self.form.add_text(address.street_name)
        self.form.add_text(address.city)
        country = address.country
        self.form.add_dropdown(country, option_lists.mailing_country)
        if country.lower() == "canada":
            self.form.add_dropdown(address.province, option_lists.canada_province)
        else:
            self.form.add_skip(1)
        self.form.add_text(address.post_code)
        if form_type == "1295":
            self.form.add_text(address.district)

        if residential_address != address:
            self.form.add_radio(False)
            self.form.add_text(residential_address.unit)
            self.form.add_text(residential_address.street_number)
            self.form.add_text(residential_address.street_name)
            self.form.add_text(residential_address.city)
            country = residential_address.country
            self.form.add_dropdown(country, option_lists.mailing_country)
            if country.lower() == "canada":
                self.form.add_dropdown(
                    residential_address.province, option_lists.canada_province
                )
            else:
                self.form.add_skip(1)
            self.form.add_text(residential_address.post_code)
            if form_type == "1295":
                self.form.add_text(residential_address.district)

        else:
            self.form.add_radio(True)
            if form_type == "1295":
                self.form.add_skip(8)
            else:
                self.form.add_skip(7)

        # telephone
        telephone: Union[Phone, None] = Phones(self.applicant.phone).PreferredPhone
        phone_type = (
            "Residence"
            if telephone.variable_type == "residential"
            else telephone.variable_type.title()
        )
        if telephone and telephone.isCanadaUs:
            pause = 3  # this place could be easily erred
            self.form.add_checkbox(True)
            self.form.add_skip(1)
            self.form.add_dropdown(phone_type, option_lists.telephone_type)
            self.form.add_skip(1)
            if form_type == "1295":  # try to work around 1295 tab order issue
                self.form.add_text(telephone.ext)
                # self.form.add_text(telephone.number, pause=pause)
                self.form.add_text(telephone.NA_format_list, pause=pause)
                self.form.add_skip(3)
            else:
                # when a valid Canada phone number finished, it will automatically tab to next control
                ext = telephone.ext if telephone.ext else ""
                self.form.add_text(telephone.number + ext, pause=1)

        else:
            pause = 0.1
            self.form.add_skip(1)
            self.form.add_checkbox(True)
            self.form.add_dropdown(phone_type, option_lists.telephone_type)
            self.form.add_text(telephone.country_code, pause=pause)
            self.form.add_text(telephone.number, pause=pause)
            self.form.add_text(telephone.ext, pause=pause)
        # alternative phone or fax is not used usually, ignore alternate telephone and fax
        self.form.add_skip(11)

        self.form.add_text(self.applicant.personal.email)

    def add_coming_into_canada(self):
        """Add coming into canada."""

        self.form.add_info("coming into Canada section")

        coming = self.applicant.trcasein
        self.form.add_date(coming.original_entry_date)
        self.form.add_text(coming.original_entry_place)
        self.form.add_dropdown(coming.original_purpose, option_lists.purpose_of_coming)

        if coming.original_purpose == "Other":
            self.form.add_text(coming.original_other_reason)
        else:
            self.form.add_skip(1)

        if coming.most_recent_entry_date:
            self.form.add_date(coming.most_recent_entry_date)
            self.form.add_text(coming.most_recent_entry_place)
            self.form.add_text(coming.doc_number)
        else:
            self.form.add_skip(3)

    def add_education(self):
        """Add education"""
        self.form.add_info("education section")

        education: Union[EducationBase, None] = EducationHistory(
            self.applicant.education
        ).highestEducation
        pause = 0.6  # tested for many times, the speed always works
        if education and education.level_in_num >= 2:  # >=2 means post secondary
            self.form.add_radio(True)
            self.form.add_date(education.start_date, True, pause=pause)
            self.form.add_text(education.field_of_study)
            self.form.add_text(education.school_name)
            self.form.add_date(education.end_date, True, pause=pause)
            self.form.add_text(education.city)
            country = education.country
            self.form.add_dropdown(country, option_lists.country_of_birth)
            if country and country.lower() == "canada":
                self.form.add_dropdown(education.province, option_lists.canada_province)
            else:
                self.form.add_skip(1)
        else:
            self.form.add_radio(False)
            self.form.add_skip(9)

    def add_employment(self, form_type: str = ""):
        """Add employment"""
        self.form.add_info("employment section")

        slots = 3  # num of slots in form
        pause = 0.5
        if self.applicant.employment:
            employments = self.applicant.employment
            for employment in employments:
                # WTF!! work around the form bug
                if slots == 2 and form_type == "1295":
                    year, month, day = employment.start_date.strftime("%Y-%m-%d").split(
                        "-"
                    )
                    self.form.add_text(year)
                    self.form.add_text(month)
                else:
                    self.form.add_date(employment.start_date, True, pause=pause)
                self.form.add_text(employment.job_title)
                self.form.add_text(employment.company)
                self.form.add_date(employment.end_date, True, pause=pause)
                self.form.add_text(employment.city)
                country = employment.country
                self.form.add_dropdown(country, option_lists.country_of_birth)
                if country.lower() == "canada":
                    self.form.add_dropdown(
                        employment.province, option_lists.canada_province
                    )
                else:
                    self.form.add_skip(1)
                slots -= 1
                if slots == 0:
                    break

        # skip emply slots
        for _ in range(slots):
            self.form.add_skip(9)

    def add_background(self):
        """Add background information"""
        self.form.add_info("background information section")
        self.form.add_skip(1)  # skip for clear section
        background: TrBackground = self.applicant.trbackground
        self.form.add_radio(background.q1a)
        self.form.add_radio(background.q1b)
        if background.q1a or background.q1b:
            self.form.add_text(background.q1c)
        else:
            self.form.add_skip(1)

        self.form.add_radio(background.q2a)
        self.form.add_radio(background.q2b)
        self.form.add_radio(background.q2c)
        if background.q2a or background.q2b or background.q2c:
            self.form.add_text(background.q2d)
        else:
            self.form.add_skip(1)

        self.form.add_radio(background.q3a)
        if background.q3a:
            self.form.add_text(background.q3b)
        else:
            self.form.add_skip(1)

        self.form.add_radio(background.q4a)
        if background.q4a:
            self.form.add_text(background.q4b)
        else:
            self.form.add_skip(1)

        self.form.add_radio(background.q5)

        self.form.add_radio(background.q6)

    def add_signature(self):
        """Add signature section"""
        self.form.add_radio(True)

        self.form.add_text(
            f"{self.applicant.personal.last_name} {self.applicant.personal.first_name}"
        )  # signature
        self.form.add_text(str(date.today()))
