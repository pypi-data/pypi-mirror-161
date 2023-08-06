from model.common.commonmodel import FormBuilderBase
from pdfform.jsonmaker import JsonMaker
from model.common.rcic import Rcics
from datetime import date


class FormBuilder5476(FormBuilderBase):
    def __init__(self, d5476: object, rcic_id_name: str, appoint: bool = True):
        self.d5476 = d5476
        self.form = JsonMaker()
        self.appoint = appoint
        self.rcic_id_name = rcic_id_name
        self.rcic = self.get_rcic(rcic_id_name)
        self.text_speed = 0.01
        self.skip_speed = 0.01

    def get_rcic(self, rcic_id_name):
        return Rcics(self.d5476.rciclist).getRcicByIdName(rcic_id_name)

    def start(self):
        self.form.add_skip(5, pause=self.skip_speed)

    def pick_rep_purpose(self):
        if self.appoint:
            self.form.add_checkbox(True)
            self.form.add_skip(1, pause=self.skip_speed)
        else:
            self.form.add_skip(1, pause=self.skip_speed)
            self.form.add_checkbox(True)

    def add_applicant(self):
        self.form.add_text(self.d5476.personal.last_name, pause=self.text_speed)
        self.form.add_text(self.d5476.personal.first_name, pause=self.text_speed)
        self.form.add_date(self.d5476.personal.dob, pause=self.text_speed)
        # currently ignore the application number
        self.form.add_skip(2, pause=self.skip_speed)
        self.form.add_text(
            self.d5476.personal.uci, pause=self.text_speed
        ) if self.d5476.personal.uci else self.form.add_skip(1, pause=self.skip_speed)

    # following adding applicant, there are add rep or cancel rep
    def add_rep(self):
        if not self.rcic:
            raise ValueError(f"RCIC with id_name {self.rcic_id_name} is not existed.")
        self.form.add_text(self.rcic.last_name, pause=self.text_speed)
        self.form.add_text(self.rcic.first_name, pause=self.text_speed)
        # skip to organization
        self.form.add_skip(4, pause=self.skip_speed)
        self.form.add_checkbox(True)
        self.form.add_text(self.rcic.rcic_number, pause=self.text_speed)
        # employer name
        self.form.add_text(self.rcic.employer_legal_name, pause=self.text_speed)
        # skip to mailing address
        self.form.add_skip(2, pause=self.skip_speed)
        # mailing address
        self.form.add_text(self.rcic.unit, pause=self.text_speed)
        self.form.add_text(self.rcic.street_number, pause=self.text_speed)
        self.form.add_text(self.rcic.street_name, pause=self.text_speed)
        self.form.add_text(self.rcic.city, pause=self.text_speed)
        self.form.add_text(self.rcic.province, pause=self.text_speed)
        self.form.add_text(self.rcic.country, pause=self.text_speed)
        self.form.add_text(self.rcic.post_code, pause=self.text_speed)
        self.form.add_text(self.rcic.country_code, pause=self.text_speed)
        self.form.add_text(self.rcic.phone, pause=self.text_speed)
        # skip to email
        self.form.add_skip(2, pause=self.skip_speed)
        self.form.add_text(self.rcic.email, pause=self.text_speed)

        self.form.add_skip(1, pause=self.skip_speed)
        self.form.add_text(date.today().strftime("%Y-%m-%d"), pause=self.text_speed)
        # self.form.add_skip(1, pause=self.skip_speed)

        # skip to applicant date
        self.form.add_skip(7, pause=self.skip_speed)
        self.form.add_text(date.today().strftime("%Y-%m-%d"), pause=self.text_speed)

    def cancel_rep(self):
        # skip from applicant to cancel rep
        self.form.add_skip(24, pause=self.skip_speed)
        self.form.add_text(self.rcic.last_name, pause=self.text_speed)
        self.form.add_text(self.rcic.first_name, pause=self.text_speed)
        self.form.add_text(self.rcic.employer_legal_name, pause=self.text_speed)

        # skip to applicant date
        self.form.add_skip(4, pause=self.skip_speed)
        self.form.add_text(date.today().strftime("%Y-%m-%d"), pause=self.text_speed)

    def get_form(self):
        self.start()
        self.pick_rep_purpose()
        self.add_applicant()
        if self.appoint:
            self.add_rep()
        else:
            self.cancel_rep()
        return self.form
