from typing import List, Optional, Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.employmentbase import EmploymentBase
from model.common.jobofferbase import JobofferBase
from model.common.id import ID
from model.common.person import Person
from model.common.language import LanguageBase
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from termcolor import colored
from webform.bcpnp.joboffer_reg import JobofferReg
from webform.bcpnp.login import Login
from webform.bcpnp.registrant import Registrant
from webform.bcpnp.education_reg import EducationReg
from webform.bcpnp.employment import EmploymentReg
from webform.bcpnp.language import LanguageReg
from webform.bcpnp.joboffer_reg import JobofferReg
from webform.bcpnp.submit import Submit
import json


class PersonId(ID):
    pass


class Rcic(BaseModel):
    first_name: str
    last_name: str
    telephone: str


class Language(LanguageBase):
    test_date: Optional[date]
    report_date: Optional[date]
    registration_number: Optional[str]
    pin: Optional[str]


class General(BaseModel):
    legal_name: str
    operating_name: Optional[str]


class ErAddress(Address):
    pass


class Joboffer(JobofferBase):
    phone: str
    is_working: bool


class Employment(EmploymentBase):
    bcpnp_qualified: bool


class Marriage(BaseModel):
    marital_status: Optional[str]
    married_date: Optional[date]
    sp_last_name: Optional[str]
    sp_first_name: Optional[str]
    sp_in_canada: Optional[bool]
    sp_canada_status: Optional[str]
    sp_canada_status_end_date: Optional[date]
    sp_in_canada_other: Optional[str]
    sp_in_canada_work: Optional[bool]
    sp_canada_occupation: Optional[str]
    sp_canada_employer: Optional[str]

    @root_validator
    def checkCurrentMarriage(cls, values):
        marital_status = values.get("marital_status")
        married_date = values.get("married_date")
        sp_last_name = values.get("sp_last_name")
        sp_first_name = values.get("sp_first_name")

        if marital_status in ["Common-Law", "Married"] and not all(
            [married_date, sp_last_name, sp_first_name]
        ):
            raise ValueError(
                f"Marital stauts is {marital_status}, but you did not answer all the questions for spouse: first/last name, or marriage date"
            )
        return values

    @root_validator
    def checkCanadaStatus(cls, values):
        sp_in_canada = values.get("sp_in_canada")
        sp_canada_status = values.get("sp_canada_status")
        sp_canada_status_end_date = values.get("sp_canada_status_end_date")
        sp_in_canada_other = values.get("sp_in_canada_other")

        if sp_in_canada and not all([sp_canada_status, sp_canada_status_end_date]):
            raise ValueError(
                f"Spouse is in Canada, but you did not answer all the questions for spouse status and/or status end date",
                "red",
            )
        if sp_canada_status == "Other" and not sp_in_canada_other:
            raise ValueError(
                f"Spouse is in Canada and status is other, but you did not give the explanation"
            )
        return values

    @root_validator
    def checkWorkInCanada(cls, values):
        sp_in_canada_work = values.get("sp_in_canada_work")
        sp_canada_occupation = values.get("sp_canada_occupation")
        sp_canada_employer = values.get("sp_canada_employer")

        if sp_in_canada_work and not all([sp_canada_occupation, sp_canada_employer]):
            raise ValueError(
                colored(
                    f"Spouse is working in Canada, but you did not answer all the questions for spouse occupation and/or employer",
                    "red",
                )
            )
        return values


class Personal(Person):
    email: EmailStr
    used_last_name: Optional[str]
    used_first_name: Optional[str]
    place_of_birth: str
    country_of_birth: str
    did_eca: bool
    eca_supplier: Optional[str]
    eca_number: Optional[str]
    ita_assessed: bool
    ita_assess_number: Optional[str]

    _normalize_used_first_name = validator(
        "used_first_name", allow_reuse=True, check_fields=False
    )(normalize)
    _normalize_used_last_name = validator(
        "used_last_name", allow_reuse=True, check_fields=False
    )(normalize)

    @root_validator
    def checkECA(cls, values):
        did_eca = values.get("did_eca")
        eca_supplier = values.get("eca_supplier")
        eca_number = values.get("eca_number")

        if did_eca and not all([eca_supplier, eca_number]):
            raise ValueError(f"Did ECA,but not input ECA number and/or ECA supplier")
        return values

    @root_validator
    def checkITA(cls, values):
        ita_assessed = values.get("ita_assessed")
        ita_assess_number = values.get("ita_assess_number")

        if ita_assessed and not ita_assess_number:
            raise ValueError(
                f"You selected ITA as Yes,but not input ITA assessment number"
            )
        return values

    @property
    def user_id(self):
        dob = self.dob.strftime(("%Y-%m-%d"))
        return (
            self.last_name[0].upper()
            + self.first_name[0]
            + dob.split("-")[0]
            + dob.split("-")[1]
            + dob.split("-")[2]
        )

    @property
    def password(self):
        return "Super" + str(datetime.today().year) + "!"


class Education(EducationBase):
    city: Optional[str]
    country: Optional[str]
    is_trade: Optional[bool]


class Bcpnp(BaseModel):
    account: Optional[str]
    password: Optional[str]
    # has_current_app: bool
    has_applied_before: bool
    pre_file_no: Optional[str]
    submission_date: Optional[date]
    case_stream: Optional[str]
    q1: bool
    q1_explaination: Optional[str]
    q2: bool
    q2_explaination: Optional[str]
    q3: bool
    q3_explaination: Optional[str]
    q4: bool
    q4_file_number: Optional[str]
    q4_explaination: Optional[str]
    q5: bool
    q5_explaination: Optional[str]
    q6: bool
    q6_explaination: Optional[str]
    q7: bool
    q7_explaination: Optional[str]


class Ee(BaseModel):
    ee_profile_no: str
    ee_expiry_date: date
    ee_jsvc: str
    ee_score: str
    ee_noc: str
    ee_job_title: str


class BcpnpModelReg(CommonModel, BuilderModel):
    personal: Personal
    general: General
    joboffer: Joboffer
    address: List[Address]
    eraddress: List[ErAddress]
    phone: List[Phone]
    personid: List[PersonId]
    bcpnp: Bcpnp
    education: List[Education]
    employment: List[Employment]
    language: List[Language]
    rcic: Rcic
    marriage: Marriage

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels = self.getExcels(
                ["excel/er.xlsx", "excel/pa.xlsx", "excel/bcpnp.xlsx", "excel/rep.xlsx"]
            )
        else:
            if excels is None or len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())

    def context(self, *args, **kwargs):
        pass

    def make_pdf_form(self, *args, **kwargs):
        pass

    def make_web_form(
        self, output_json="", initial=True, previous=False, *args, **kwargs
    ):
        actions = Login(self).login(initial=initial, previous=previous)
        for block in [
            Registrant,
            EducationReg,
            EmploymentReg,
            JobofferReg,
            LanguageReg,
        ]:
            actions += block(self).fill()
        actions += Submit(self, is_reg=True).fill()
        with open(output_json, "w") as f:
            json.dump(actions, f, default=str, indent=3)
        print(colored(f"{output_json} has been created.", "green"))


class BcpnpEEModelReg(BcpnpModelReg):
    ee: Ee

    def __init__(self, excels=None, output_excel_file=None):
        super().__init__(excels=excels, output_excel_file=output_excel_file)
