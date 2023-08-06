from termcolor import colored
from utils.utils import checkContinuity
from typing import List, Optional, Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.id import ID
from model.common.person import Person
from datetime import date
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.prportal.data.country import country_residence
from model.common.mixins import DatePeriod


class PersonId(ID):
    pass


class PRCase(BaseModel):
    imm_program: str
    imm_category: str
    imm_under: Optional[str]
    communication_language: str
    interview_language: str
    need_translator: bool
    intended_province: str
    intended_city: str


class COR(DatePeriod):
    country: str
    status: str
    explanation: Optional[str]


class CORs(object):
    def __init__(self, cors: List[COR]):
        self.cors = cors
        self.checkFirstEndDate()

    @property
    def current(self):
        if len(self.cors) >= 1:
            return self.cors[0]
        else:
            raise ValueError(
                colored(
                    f"table-cor must have values, and the first line must be current residence country.",
                    "red",
                )
            )

    # In table cor, the first line is defined as current residence, so the end date must bigger than today
    def checkFirstEndDate(self):
        if (
            len(self.cors) > 0
            and self.cors[0].end_date
            and self.cors[0].end_date < date.today()
        ):
            raise ValueError(
                colored(
                    f"In tabel-cor, the current residence end date {self.cors[0].end_date} is earlier than today",
                    "red",
                )
            )


class Marriage(BaseModel):
    marital_status: str
    married_date: Optional[date]
    sp_last_name: Optional[str]
    sp_first_name: Optional[str]
    previous_married: bool
    pre_sp_last_name: Optional[str]
    pre_sp_first_name: Optional[str]
    pre_sp_dob: Optional[date]
    pre_relationship_type: Optional[str]
    pre_start_date: Optional[date]
    pre_end_date: Optional[date]

    @validator("pre_end_date")
    def endDateBigger(cls, pre_end_date, values):
        pre_start_date = values.get("pre_start_date")
        if not pre_start_date:
            return pre_end_date
        the_date = pre_end_date or date.today()
        if (the_date - pre_start_date).days <= 0:
            raise ValueError(
                f"Expiry date {the_date} is earlier than issue date {pre_start_date} for the ID"
                if pre_end_date
                else f"{pre_start_date} is later than today"
            )
        return pre_end_date

    @root_validator
    def checkPreviousMarriage(cls, values):
        pre_marriaged = values.get("previous_married")
        pre_sp_last_name = values.get("pre_sp_last_name")
        pre_sp_first_name = values.get("pre_sp_first_name")
        pre_sp_dob = values.get("pre_sp_dob")
        pre_start_date = values.get("pre_start_date")
        pre_end_date = values.get("pre_end_date")
        pre_relationship_type = values.get("pre_relationship_type")

        if pre_marriaged and not all(
            [
                pre_sp_first_name,
                pre_sp_last_name,
                pre_sp_dob,
                pre_start_date,
                pre_end_date,
                pre_relationship_type,
            ]
        ):
            raise ValueError(
                f"Since previous married is true, but you did not answer all the questions for previous spouse: first/last name, dob,relationship type, start/end date"
            )
        return values

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


class Personal(Person):
    used_last_name: Optional[str]
    used_first_name: Optional[str]
    native_last_name: str
    native_first_name: str
    height: int
    eye_color: str
    country_of_birth: str
    place_of_birth: str
    uci: Optional[str]
    citizen2: Optional[str]
    native_language: str
    english_french: str
    which_one_better: Optional[str]
    language_test: bool
    current_occupation: str
    intended_occupation: Optional[str]
    email: EmailStr
    primary_school_years: int
    secondary_school_years: int
    post_secondary_school_years: int
    other_school_years: int
    other_explanation: Optional[str]
    relationship_to_pa: Optional[str]
    accompany_to_canada: Optional[bool]
    dependant_type: Optional[str]

    _normalize_used_first_name = validator(
        "used_first_name", allow_reuse=True, check_fields=False
    )(normalize)
    _normalize_used_last_name = validator(
        "used_last_name", allow_reuse=True, check_fields=False
    )(normalize)

    @root_validator
    def checkAnswers(cls, values):
        english_french = values.get("english_french")
        explanations = values.get("which_one_better")
        if english_french == "Both" and not explanations:
            raise ValueError(
                colored(
                    f"Since you answered you can speak both English and French, but you did not answer the question 'which on is better' in info-personal sheet",
                    "red",
                )
            )
        return values

    @root_validator
    def checkRelationship(cls, values):
        relationship = values.get("relationship_to_pa")
        accompany_to_canada = values.get("accompany_to_canada")
        dependant_type = values.get("dependant_type")

        if relationship and (accompany_to_canada == None):
            raise ValueError(
                colored(
                    f"In info-personal, since {values['first_name']} {values['last_name']} is {relationship} to principle applicant, but you did not pick if accompany to Canada.",
                    "red",
                )
            )

        if (
            relationship
            and relationship
            in ["Adopted Child", "Child", "Grandchild", "Step-Child", "Step-Grandchild"]
            and dependant_type == None
        ):
            raise ValueError(
                colored(
                    f"In info-personal, since {values['first_name']} {values['last_name']} is {relationship} to principle applicant, but you did not pick dependant type",
                    "red",
                )
            )
        return values


class Education(EducationBase):
    city: Optional[str]
    country: Optional[str]


class Family(BaseModel):
    relationship: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    native_last_name: Optional[str]
    native_first_name: Optional[str]
    date_of_birth: Optional[date]
    date_of_death: Optional[date]
    place_of_birth: Optional[str]
    birth_country: Optional[str]
    marital_status: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]

    @root_validator
    def checkFields(cls, values):
        last_name = values.get("last_name")
        first_name = values.get("first_name")
        native_last_name = values.get("native_last_name")
        native_first_name = values.get("native_first_name")
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
                    native_last_name,
                    native_first_name,
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


class Travel(DatePeriod):
    length: int
    destination: str
    purpose: str


class PRBackground(BaseModel):
    q1: bool
    q2: bool
    q3: bool
    q4: bool
    q5: bool
    q6: bool
    q7: bool
    q8: bool
    q9: bool
    q10: bool
    q11: bool
    details: Optional[str]


class History(DatePeriod):
    activity: str
    city_and_country: str
    status: str
    name_of_company_or_school: str

    @property
    def __str__(self):
        return "table-history"


class Member(DatePeriod):
    organization_name: str
    organization_type: str
    position: str
    city: str
    country: str


class Government(DatePeriod):
    country: str
    department: str
    position: str


class Military(DatePeriod):
    country: str
    service_detail: str
    rank: str
    combat_detail: Optional[str]
    reason_for_end: Optional[str]


class AddressHistory(DatePeriod):
    street_and_number: str
    city: str
    province: str
    country: str
    post_code: str

    @property
    def __str__(self):
        return "table-addresshistory"


class Status(BaseModel):
    last_entry_date: Optional[date]
    last_entry_place: Optional[str]


class PrModel(CommonModel):
    personal: Personal
    status: Status
    cor: List[COR]
    marriage: Marriage
    address: List[Address]
    phone: List[Phone]
    personid: List[PersonId]
    prcase: PRCase
    family: List[Family]
    travel: List[Travel]
    prbackground: PRBackground
    education: List[Education]
    history: List[History]
    member: List[Member]
    government: List[Government]
    military: List[Military]
    addresshistory: List[AddressHistory]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None, check=True):
        # check continuity only if check is required and with excels
        should_check = check and excels
        if output_excel_file:
            excels = self.getExcels(["excel/pr.xlsx", "excel/pa.xlsx"])
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())

        if should_check:
            [
                self.check(item, excels[0])
                for item in [self.history, self.addresshistory]
            ]

    def check(self, items: List[object], excel_file):
        results = []
        # construct list suitable for checkContinuity
        for item in items:
            results.append(list(item.__dict__.values()))

        # check
        continued, sorted_list, msg = checkContinuity(results)

        if not continued:
            print(
                colored(
                    f"There are {len(msg)} error(s) in sheet {items[0].__str__} of {excel_file}",
                    "red",
                )
            )
            [print(index, "\t", m) for index, m in enumerate(msg)]
