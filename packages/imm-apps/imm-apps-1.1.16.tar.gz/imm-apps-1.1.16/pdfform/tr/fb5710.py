from pdfform.tr.common import TrCommon
from pdfform.tr import option_lists


class FormBuilder5710(TrCommon):
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

        # apply WP for same employer, apply WP for new employer,restore status as worker,, TRP with new employer
        if self.applicant.wpincanada.application_purpose == "restore status as worker":
            self.form.add_checkbox(True)  # pick apply for wp with same employer
            self.form.add_skip(1)
            self.form.add_checkbox(True)  # pick restore status
            self.form.add_skip(1)
        elif self.applicant.wpincanada.application_purpose == "TRP with same employer":
            self.form.add_checkbox(True)  # pick apply for wp with same employer
            self.form.add_skip(2)
            self.form.add_checkbox(True)  # pick restore status
        elif self.applicant.wpincanada.application_purpose == "TRP with new employer":
            self.form.add_skip(1)
            self.form.add_checkbox(True)  # pick apply for wp with same employer
            self.form.add_skip(1)
            self.form.add_checkbox(True)  # pick restore status
        else:
            if (
                self.applicant.wpincanada.application_purpose
                == "apply WP for same employer"
            ):
                self.form.add_checkbox(True)
                self.form.add_skip(3)
            else:
                self.form.add_skip(1)
            if (
                self.applicant.wpincanada.application_purpose
                == "apply WP for new employer"
            ):
                self.form.add_checkbox(True)
                self.form.add_skip(2)

    def add_work_detail(self):
        """Add details of intended work in Canada"""

        self.form.add_info("intended work section")

        work_detail = self.applicant.wpincanada

        self.form.add_dropdown(
            work_detail.work_permit_type, option_lists.work_permit_ex
        )
        if work_detail.work_permit_type == "Other":
            self.form.add_text(work_detail.other_explain)
        else:
            self.form.add_skip(1)

        if work_detail.employer_name:
            self.form.add_text(work_detail.employer_name)
        else:
            self.form.add_text("Not applicable")

        if work_detail.employer_name:
            self.form.add_text(work_detail.employer_address)
        else:
            self.form.add_text("Not applicable")

        province = work_detail.work_province
        if province:
            self.form.add_dropdown(province, option_lists.canada_province)
        else:
            self.form.add_skip(1)

        if work_detail.work_city:
            self.form.add_dropdown(
                work_detail.work_city.upper(),
                option_lists.canada_province_cities[province],
            )
        else:
            self.form.add_skip(1)

        if work_detail.employer_address:
            self.form.add_text(work_detail.employer_address)
        else:
            self.form.add_text("TO BE DETERMINED")

        if work_detail.job_title:
            self.form.add_text(work_detail.job_title)
        else:
            self.form.add_text("TO BE DETERMINED")

        if work_detail.brief_duties:
            self.form.add_text(work_detail.brief_duties)
        else:
            self.form.add_text("TO BE DETERMINED")

        if work_detail.start_date:
            self.form.add_date(work_detail.start_date)
        else:
            self.form.add_skip(1)

        if work_detail.end_date:
            self.form.add_date(work_detail.end_date)
        else:
            self.form.add_skip(1)

        if work_detail.lmia_num_or_offer_num:
            self.form.add_text(work_detail.lmia_num_or_offer_num)
        else:
            self.form.add_skip(1)

        if work_detail.caq_number:
            self.form.add_text(work_detail.caq_number)
            self.form.add_date(work_detail.expiry_date)
        else:
            self.form.add_skip(2)
        self.form.add_radio(work_detail.pnp_certificated)

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
        self.add_work_detail()
        self.add_education()
        self.add_employment()
        self.add_background()
        self.add_signature()
        return self.form
