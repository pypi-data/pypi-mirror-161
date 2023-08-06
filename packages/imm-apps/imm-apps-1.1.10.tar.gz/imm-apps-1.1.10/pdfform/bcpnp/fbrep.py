from model.common.commonmodel import FormBuilderBase
from pdfform.jsonmaker import JsonMaker
from model.common.rcic import Rcics
from model.common.contact import Contacts
from datetime import date


class FormBuilderBcRep(FormBuilderBase):
    def __init__(self, data_bcrep: object, rcic_id_name: str, *arg, **kwargs):
        self.data_bcrep = data_bcrep
        self.form = JsonMaker()
        self.rcic_id_name = rcic_id_name
        self.rcic = self.get_rcic(rcic_id_name)
        self.text_speed = 0.01
        self.skip_speed = 0.01

    def get_rcic(self, rcic_id_name):
        return Rcics(self.data_bcrep.rciclist).getRcicByIdName(rcic_id_name)

    def start(self):
        self.form.add_skip(1, pause=self.skip_speed)

    def add_applicant(self):
        self.form.add_text(self.data_bcrep.personal.last_name, pause=self.text_speed)
        self.form.add_text(self.data_bcrep.personal.first_name, pause=self.text_speed)
        self.form.add_date(self.data_bcrep.personal.dob, pause=self.text_speed)

    def add_employer(self):

        contact = Contacts(self.data_bcrep.contact).preferredContact
        # self.form.add_date(self.data_bcrep.general.legal_name, pause=self.text_speed)
        self.form.add_date("unigenius", pause=self.text_speed)
        self.form.add_text(contact.last_name, pause=self.text_speed)
        self.form.add_text(contact.first_name, pause=self.text_speed)
        self.form.add_skip(1, pause=self.skip_speed)

    @property
    def line1(self):
        # l1 = self.rcic.po_box + " " if self.rcic.po_box else ""
        l1 = self.rcic.unit + " " if self.rcic.unit else ""
        l1 += self.rcic.street_number + " " if self.rcic.street_number else ""
        l1 += self.rcic.street_name
        # l1 += ", " + self.rcic.district + ", " if self.rcic.district else ""
        return l1

    def add_rep(self):
        if not self.rcic:
            raise ValueError(f"RCIC with id_name {self.rcic_id_name} is not existed.")
        self.form.add_text(self.rcic.last_name, pause=self.text_speed)
        self.form.add_text(self.rcic.first_name, pause=self.text_speed)
        # employer name
        self.form.add_text(self.rcic.employer_legal_name, pause=self.text_speed)
        self.form.add_text(self.rcic.phone, pause=self.text_speed)
        self.form.add_skip(1, pause=self.skip_speed)
        self.form.add_text(self.rcic.rcic_number, pause=self.text_speed)
        self.form.add_text(self.rcic.email, pause=self.text_speed)
        self.form.add_text(self.line1, pause=self.text_speed)
        self.form.add_text(self.rcic.city, pause=self.text_speed)
        self.form.add_text(self.rcic.province, pause=self.text_speed)
        self.form.add_text(self.rcic.country, pause=self.text_speed)
        self.form.add_text(self.rcic.post_code, pause=self.text_speed)

        # check iccrc button
        self.form.add_checkbox(True)
        # skip one step for id number
        self.form.add_skip(1, pause=self.skip_speed)
        self.form.add_text(self.rcic.rcic_number, pause=self.text_speed)

    def add_date(self):
        # skip to rep date
        self.form.add_skip(5, pause=self.skip_speed)
        self.form.add_text(date.today().strftime("%d-%b-%Y"), pause=self.text_speed)
        self.form.add_text(date.today().strftime("%d-%b-%Y"), pause=self.text_speed)

    def get_form(self):
        self.start()
        self.add_applicant()
        self.add_employer()
        self.add_rep()
        self.add_date()
        return self.form
