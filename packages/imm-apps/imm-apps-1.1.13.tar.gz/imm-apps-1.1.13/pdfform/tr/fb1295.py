from pdfform.tr.common import TrCommon
from pdfform.tr import option_lists


class FormBuilder1295(TrCommon):
    """Form builder"""
    def start(self):
        """Add initial 3 skips"""
        self.form.add_skip(3)
        
    def add_header(self):
        """Add header section items"""
        personal = self.applicant.personal

        self.form.add_text(personal.uci)
        self.form.add_dropdown(
            self.applicant.trcase.service_in, option_lists.service_language
        )

    def add_work_detail(self):
        """Add details of intended work in Canada"""

        self.form.add_info("intended work section")

        work_detail = self.applicant.wp
        self.form.add_dropdown(work_detail.work_permit_type, option_lists.work_permit)

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

    def get_form(self):
        self.start()
        self.add_header()
        self.add_personal_detail(form_type="1295")
        self.add_language()
        self.add_passport()
        self.add_national_id()
        self.add_uspr_card()
        self.add_contact_information(form_type="1295")
        self.add_work_detail()
        self.add_education()
        self.add_employment(form_type="1295")
        self.add_background()
        self.add_signature()
        return self.form
