from typing import List, Optional
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.commonmodel import CommonModel
from model.common.employmentbase import EmploymentBase
from model.common.jobofferbase import JobofferBase
from model.common.id import ID
from model.common.person import Person
from model.common.cor import CORs, COR
from model.common.status import Status
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.bcpnp.submit import Submit
from webform.bcpnp.family import FamilyApp
from model.common.contact import ContactBase
from model.common.family import FamilyBase
from termcolor import colored
from webform.bcpnp.applicant import Applicant
from webform.bcpnp.education_app import EducationApp
from webform.bcpnp.workexperience import WorkExperience
from webform.bcpnp.joboffer_app import JobofferApp
from webform.bcpnp.submit import Submit
from webform.bcpnp.login import Login
import json


class PersonId(ID):
    pass


class CanadaRelative(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    sex: Optional[str]
    relationship: Optional[str]
    status: Optional[str]
    age: Optional[int]
    city: Optional[str]
    province: Optional[str]
    years_in_canada: Optional[int]

    @root_validator
    def checkFields(cls, values):
        last_name = values.get("last_name")
        first_name = values.get("first_name")
        sex = values.get("sex")
        relationship = values.get("relationship")
        status = values.get("status")
        age = values.get("age")
        city = values.get("city")
        province = values.get("province")
        years_in_canada = values.get("years_in_canada")

        if (
            last_name
            and first_name
            and not all(
                [sex, relationship, status, age, city, province, years_in_canada]
            )
        ):
            raise ValueError(
                f"Some fields in row of {first_name} {last_name} are missed."
            )
        return values


class Rcic(BaseModel):
    first_name: str
    last_name: str
    telephone: str


class General(BaseModel):
    legal_name: str
    operating_name: Optional[str]
    corporate_structure: str
    other_explaination: Optional[str]
    establish_date: date
    industry: str
    registration_number: str
    ft_employee_number: int
    establish_date: date
    website: Optional[str]


class Contact(ContactBase):
    position: Optional[str]

    @root_validator
    def checkFields(cls, values):
        last_name = values.get("last_name")
        first_name = values.get("first_name")
        phone = values.get("phone")
        email = values.get("email")
        position = values.get("position")

        if last_name and first_name and not all([phone, email, position]):
            raise ValueError(
                f"Some fields in row of {first_name} {last_name} are missed."
            )
        return values


class ErAddress(Address):
    phone: Optional[str]


class Joboffer(JobofferBase):
    phone: str
    is_working: bool
    license_request: bool


class Employment(EmploymentBase):
    bcpnp_qualified: bool
    phone_of_certificate_provider: Optional[str]
    website: Optional[str]
    unit: Optional[str]
    street_address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    postcode: Optional[str]
    duties: Optional[str]


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
    uci: Optional[str]

    _normalize_used_first_name = validator(
        "used_first_name", allow_reuse=True, check_fields=False
    )(normalize)
    _normalize_used_last_name = validator(
        "used_last_name", allow_reuse=True, check_fields=False
    )(normalize)

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
    province: Optional[str]
    country: Optional[str]
    is_trade: Optional[bool]
    graduate_date: Optional[date]

    @root_validator
    def checkCompletion(cls, values):
        school_name = values.get("school_name")
        city = values.get("city")
        province = values.get("province")
        country = values.get("country")
        is_trade = values.get("is_trade")
        education_level = values.get("education_level")
        field_of_study = values.get("field_of_study")

        if school_name and not all(
            [
                city,
                province,
                country,
                is_trade != None,
                education_level,
                field_of_study,
            ]
        ):
            raise ValueError(f"Some fields are missed in row of {school_name}.")
        return values


class Family(FamilyBase):
    country_of_citizenship: Optional[str]
    address: Optional[str]
    date_of_death: Optional[date]
    marital_status: Optional[str]

    @root_validator
    def checkFields(cls, values):
        last_name = values.get("last_name")
        first_name = values.get("first_name")
        date_of_birth = values.get("date_of_birth")
        place_of_birth = values.get("place_of_birth")
        birth_country = values.get("birth_country")
        marital_status = values.get("marital_status")
        address = values.get("address")

        if (
            last_name
            and first_name
            and not all(
                [
                    date_of_birth,
                    place_of_birth,
                    birth_country,
                    marital_status,
                    address,
                ]
            )
        ):
            raise ValueError(
                f"Some fields of {first_name} {last_name} in info-family sheet are not completed, please check"
            )
        return values


class Bcpnp(BaseModel):
    intended_city: str
    account: Optional[str]
    password: Optional[str]
    # has_current_app: bool
    # has_applied_before: bool
    # pre_file_no: Optional[str]
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


class BcpnpModelApp(CommonModel):
    personal: Personal
    marriage: Marriage
    cor: List[COR]
    status: Status
    general: General
    joboffer: Joboffer
    family: List[Family]
    eraddress: List[ErAddress]
    contact: List[Contact]
    bcpnp: Bcpnp
    education: List[Education]
    employment: List[Employment]
    rcic: Rcic
    canadarelative: List[CanadaRelative]

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

    def make_web_form(
        self, output_json="", initial=True, previous=False, *args, **kwargs
    ):
        actions = Login(self).login(initial=initial, previous=previous)
        for block in [Applicant, EducationApp, WorkExperience, FamilyApp, JobofferApp]:
            actions += block(self).fill()
        actions += Submit(self, is_reg=True).fill()
        with open(output_json, "w") as f:
            json.dump(actions, f, default=str, indent=3)
        print(colored(f"{output_json} has been created.", "green"))


class BcpnpEEModelApp(BcpnpModelApp):
    ee: Ee

    def __init__(self, excels=None, output_excel_file=None):
        super().__init__(excels=excels, output_excel_file=output_excel_file)
