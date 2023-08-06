from pdfform.tr.common import TrCommon
from pdfform.tr import option_lists


class FormBuilder5709(TrCommon):
    """Form builder"""

    def start(self):
        """Add initial 3 skips"""
        self.form.add_skip(3)

    def add_header(self):
        """Add header section items"""
        personal = self.applicant.personal
        self.form.add_text(personal.uci)
        self.form.add_dropdown(
            self.applicant.trcasein.service_in, option_lists.service_language
        )

        if (
            self.applicant.spincanada.application_purpose
            == "apply or extend study permit"
        ):
            self.form.add_checkbox(True)
        else:
            self.form.add_skip(1)
        if self.applicant.spincanada.application_purpose == "restore status as student":
            self.form.add_checkbox(True)
        else:
            self.form.add_skip(1)
        if self.applicant.spincanada.application_purpose == "TRP":
            self.form.add_checkbox(True)
        else:
            self.form.add_skip(1)

    def add_study_detail(self):
        """Add study details"""
        self.form.add_info("details of study section")

        detail = self.applicant.spincanada
        self.form.add_text(detail.school_name)
        self.form.add_dropdown(
            option_lists.get_5709_study_level(detail.study_level),
            option_lists.level_of_study,
        )
        self.form.add_dropdown(detail.study_field, option_lists.field_of_study, True)

        self.form.add_dropdown(detail.province, option_lists.canada_province)
        self.form.add_dropdown(
            detail.city.upper(), option_lists.canada_province_cities[detail.province]
        )
        self.form.add_text(detail.address)
        self.form.add_text(detail.dli)
        self.form.add_text(detail.student_id)
        self.form.add_date(detail.start_date)
        self.form.add_date(detail.end_date)

        self.form.add_text(detail.tuition_cost)
        self.form.add_text(detail.room_cost)
        self.form.add_text(detail.other_cost)
        self.form.add_text(detail.fund_available)
        self.form.add_dropdown(detail.paid_person, option_lists.expense_by)
        self.form.add_skip(1)
        self.form.add_radio(detail.apply_work_permit)
        if detail.apply_work_permit:
            self.form.add_dropdown(
                detail.work_permit_type, option_lists.work_permit_student
            )
            self.form.add_text(detail.caq_number)
            self.form.add_text(detail.expiry_date)
        else:
            self.form.add_skip(3)

    def get_form(self):
        self.start()
        self.add_header()
        self.add_personal_detail()
        self.add_language()
        self.add_passport()
        self.add_national_id()
        self.add_uspr_card()
        self.add_contact_information(form_type="5708")
        self.add_coming_into_canada()
        self.add_study_detail()
        self.add_education()
        self.add_employment()
        self.add_background()
        self.add_signature()
        return self.form
