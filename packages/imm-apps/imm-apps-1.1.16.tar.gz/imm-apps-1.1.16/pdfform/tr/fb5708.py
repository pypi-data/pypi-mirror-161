from pdfform.tr.common import TrCommon
from pdfform.tr import option_lists


class FormBuilder5708(TrCommon):
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
            self.applicant.vrincanada.application_purpose
            == "apply or extend visitor record"
        ):
            self.form.add_checkbox(True)
        else:
            self.form.add_skip(1)
        if self.applicant.vrincanada.application_purpose == "restore status as visotor":
            self.form.add_checkbox(True)
        else:
            self.form.add_skip(1)
        if self.applicant.vrincanada.application_purpose == "TRP":
            self.form.add_checkbox(True)
        else:
            self.form.add_skip(1)

    def add_visit_detail(self):
        """Add visit details"""
        self.form.add_info("details of visit section")

        visit = self.applicant.vrincanada
        self.form.add_dropdown(visit.visit_purpose, option_lists.purpose_of_vist)
        if visit.visit_purpose.lower() == "other":
            self.form.add_text(visit.other_explain)
        else:
            self.form.add_skip(1)
        self.form.add_date(visit.start_date)
        self.form.add_date(visit.end_date)
        self.form.add_text(str(visit.funds_available))
        self.form.add_dropdown(visit.paid_person, option_lists.expense_by)
        if visit.paid_person.lower() == "other":
            self.form.add_text(visit.other_payer_explain)
        else:
            self.form.add_skip(1)

        self.form.add_text(visit.name1)
        self.form.add_text(visit.relationship1)
        self.form.add_text(visit.address1)
        self.form.add_text(visit.name2)
        self.form.add_text(visit.relationship2)
        self.form.add_text(visit.address2)

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
        self.add_visit_detail()
        self.add_education()
        self.add_employment()
        self.add_background()
        self.add_signature()
        return self.form
