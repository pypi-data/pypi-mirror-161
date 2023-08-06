from turtle import position
from model.common.advertisement import Advertisements, InterviewRecords
from pdfform.jsonmaker import JsonMaker
from model.common.address import Addresses

# from model.bcpnp.jobofferform import JobOfferFormModel
from model.common.contact import Contacts
from assess.policy.bcpnp.data import bc_tech_pilot
from datetime import date
import json
from termcolor import colored


class FormBuilderEmployerDeclaration:
    """Form builder"""

    def __init__(self, jof: object):
        self.jof = jof
        self.form = JsonMaker()
        self.text_speed = 0.01

    def start(self):
        self.form.add_skip(1)

    def employee(self):
        self.form.add_text(self.jof.personal.last_name, pause=self.text_speed)
        self.form.add_text(self.jof.personal.first_name, pause=self.text_speed)

    def employer(self):
        self.form.add_text(self.jof.general.legal_name, pause=self.text_speed)
        self.form.add_text(self.jof.general.operating_name or "", pause=self.text_speed)

        mailing_address = Addresses(self.jof.eraddress).mailing
        business_address = Addresses(self.jof.eraddress).business

        self.form.add_text(mailing_address.line1, pause=self.text_speed)
        self.form.add_text(mailing_address.city, pause=self.text_speed)
        self.form.add_text(mailing_address.province, pause=self.text_speed)
        self.form.add_text(mailing_address.country, pause=self.text_speed)
        self.form.add_text(mailing_address.post_code, pause=self.text_speed)

        if mailing_address == business_address:
            self.form.add_skip(5)
        else:
            self.form.add_text(business_address.line1, pause=self.text_speed)
            self.form.add_text(business_address.city, pause=self.text_speed)
            self.form.add_text(business_address.province, pause=self.text_speed)
            self.form.add_text(business_address.country, pause=self.text_speed)
            self.form.add_text(business_address.post_code, pause=self.text_speed)
        # contact
        contact = Contacts(self.jof.contact).primary
        self.form.add_text(contact.last_name, pause=self.text_speed)
        self.form.add_text(contact.first_name, pause=self.text_speed)
        self.form.add_text(contact.position, pause=self.text_speed)
        self.form.add_text(contact.phone, pause=self.text_speed)
        self.form.add_text(contact.email, pause=self.text_speed)

        # other
        self.form.add_text(self.jof.general.website, pause=self.text_speed)
        self.form.add_text(
            str(self.jof.general.ft_employee_number), pause=self.text_speed
        )
        self.form.add_text(
            self.jof.general.establish_date.strftime("%d/%m/%y"), pause=self.text_speed
        )

        self.form.add_text(self.jof.general.industry, pause=self.text_speed)

        if self.jof.general.corporate_structure == "Incorporated":
            self.form.add_checkbox(True)
            self.form.add_skip(2)
        elif self.jof.general.corporate_structure == "Limited Liability Partnership":
            self.form.add_skip(1)
            self.form.add_checkbox(True)
            self.form.add_skip(1)
        elif self.jof.general.corporate_structure == "Extra-provincially-registered":
            self.form.add_skip(2)
            self.form.add_checkbox(True)
        self.form.add_text(self.jof.general.registration_number, pause=self.text_speed)
        # other corporate structure
        if (
            self.jof.general.corporate_structure == "federally-incorporated"
            or self.jof.general.corporate_structure == "Other"
        ):

            self.form.add_skip(4)
            self.form.add_checkbox(True)
            self.form.add_text(
                self.jof.general.corporate_structure, pause=self.text_speed
            )
        else:
            self.form.add_skip(2)

    def joboffer(self):
        self.form.add_text(self.jof.joboffer.job_title, pause=self.text_speed)
        self.form.add_text(self.jof.joboffer.hourly_rate, pause=self.text_speed)
        self.form.add_text(self.jof.joboffer.annual_rate, pause=self.text_speed)
        self.form.add_text(self.jof.joboffer.weekly_hours, pause=self.text_speed)

        work_locations = Addresses(self.jof.eraddress).workings
        # first work location
        if len(work_locations) < 1:
            raise ValueError("Work location missed")
        self.form.add_text(work_locations[0].line1, pause=self.text_speed)
        self.form.add_text(work_locations[0].city, pause=self.text_speed)
        self.form.add_text(work_locations[0].post_code, pause=self.text_speed)
        self.form.add_text(work_locations[0].phone, pause=self.text_speed)
        if len(work_locations) >= 2:
            self.form.add_text(work_locations[1].line1, pause=self.text_speed)
            self.form.add_text(work_locations[1].city, pause=self.text_speed)
            self.form.add_text(work_locations[1].post_code, pause=self.text_speed)
            self.form.add_text(work_locations[1].phone, pause=self.text_speed)
        else:
            self.form.add_skip(4)

    def tech(self):
        if self.jof.joboffer.noc in bc_tech_pilot:
            if self.jof.joboffer.permanent:
                self.form.add_radio(True)
                self.form.add_skip(5)  # messy skip :(
            else:
                self.form.add_radio(False)
                self.form.add_text(
                    self.jof.joboffer.work_end_date.strftime("%d-%b-%Y"),
                    pause=self.text_speed,
                )
                self.form.add_skip(3)
                self.form.add_text(
                    self.jof.joboffer.why_not_permanent, pause=self.text_speed
                )
        else:
            self.form.add_skip(5)

    def position(self):
        self.form.add_info("3c. Position details")
        # new position
        self.form.add_radio_list(
            pause=0.1,
            position=1
            if self.jof.position.is_new
            else 2,  # here 1 and 2 is special, normally should be 0 or 1
        )
        self.form.add_radio_list(
            pause=0.1, position=1 if self.jof.position.under_cba else 2
        )
        if self.jof.position.under_cba:
            self.form.add_text(self.jof.position.which_union, pause=self.text_speed)
        # else:
        #     self.form.add_skip(1)

        # employee number in same position
        self.form.add_text(
            self.jof.position.has_same_number
            if self.jof.position.has_same_number
            else 0,
            pause=self.text_speed,
        )
        self.form.add_text(
            self.jof.position.vacancies_number
            if self.jof.position.vacancies_number
            else 0,
            pause=self.text_speed,
        )
        self.form.add_text(
            self.jof.position.laidoff_with12 if self.jof.position.laidoff_with12 else 0,
            pause=self.text_speed,
        )
        self.form.add_text(
            self.jof.position.laidoff_current
            if self.jof.position.laidoff_current
            else 0,
            pause=self.text_speed,
        )
        # language requirement
        self.form.add_radio_list(
            position=0 if self.jof.joboffer.other_language_required else 1
        )
        if self.jof.joboffer.other_language_required:
            self.form.add_text(
                self.jof.joboffer.reason_for_other, pause=self.text_speed
            )
        else:
            self.form.add_skip(1)

        # lmia status
        self.form.add_radio_list(position=0 if self.jof.position.lmia_refused else 1)
        if self.jof.position.lmia_refused:
            self.form.add_text(
                self.jof.position.lmia_refused_reason, pause=self.text_speed
            )
        else:
            self.form.add_skip(1)

        # license issue
        if self.jof.joboffer.license_request:
            if self.jof.joboffer.license_met:
                self.form.add_radio_list(position=0)
                self.form.add_text(
                    self.jof.joboffer.license_met_reason, pause=self.text_speed
                )
            else:
                self.form.add_radio_list(position=1)
                self.form.add_text(
                    self.jof.joboffer.license_met_reason, pause=self.text_speed
                )
        else:
            self.form.add_radio_list(position=2)

    def recruit(self):
        ads = Advertisements(self.jof.advertisement)
        interviews = InterviewRecords(self.jof.interviewrecord)
        recruited = True if ads.amount > 0 else False
        if recruited:
            self.form.add_radio(True)
            self.form.add_text(interviews.resume_num, pause=self.text_speed)
            self.form.add_text(ads.min_days, pause=self.text_speed)
            self.form.add_text(interviews.summary, pause=self.text_speed)
            self.form.add_text(
                self.jof.personalassess.why_qualified_say, pause=self.text_speed
            )
            self.form.add_text(
                self.jof.recruitmentsummary.reasons_not_hire_canadians,
                pause=self.text_speed,
            )
            self.form.add_skip(1)
        else:
            self.form.add_radio(False)
            self.form.add_skip(6)

    def sign(self):
        contact = Contacts(self.jof.contact).primary
        # messy skip in pdf
        self.form.add_text(contact.last_name, pause=self.text_speed)
        self.form.add_text(contact.position, pause=self.text_speed)
        self.form.add_skip(21)
        self.form.add_text(contact.first_name, pause=self.text_speed)
        self.form.add_text(date.today().strftime("%d-%b-%Y"), pause=self.text_speed)

    def get_form(self):
        self.start()
        self.employee()
        self.employer()
        self.joboffer()
        self.tech()
        self.position()
        self.recruit()
        self.sign()
        return self.form

    def save(self, flename: str):
        actions = self.get_form().actions
        with open(flename, "w") as output:
            json.dump(actions, output, indent=3, default=str)
        print(colored(f"{flename} has been created", "green"))
