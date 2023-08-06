from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator, EmailStr
from model.common.commonmodel import CommonModel
from model.common.address import Address
from model.common.contact import ContactBase
from model.common.mediaaccount import MediaAccount
from termcolor import colored
from model.common.jobposition import PositionBase
from model.common.jobofferbase import JobofferBase
from model.common.person import Person


class General(BaseModel):
    cra_number: str
    recruit_email: EmailStr
    has_jobbank_account: bool
    has_bc_employer_certificate: Optional[bool]
    company_intro: str
    business_intro: str
    ft_employee_number:int
    pt_employee_number:int


class ErAddress(Address):
    phone: str


class Contact(ContactBase):
    middle_name: Optional[str]
    position: str
    po_box: Optional[str]
    unit: Optional[str]
    street_number: str
    street_name: str
    city: str
    province: str
    post_code: str

    @root_validator
    def checkCanadaProvince(cls, values):
        province = values.get("province")
        if province not in [
            "AB",
            "BC",
            "MB",
            "NB",
            "NL",
            "NS",
            "NT",
            "NU",
            "ON",
            "PE",
            "QC",
            "SK",
            "YT",
        ]:
            raise ValueError(
                colored(
                    f'Since country is Canada is, the province must be one of  "AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"',
                    "red",
                )
            )
        return values


class Finance(BaseModel):
    year: int
    total_asset: float
    net_asset: float
    revenue: float
    net_income: float
    retained_earning: float


class Joboffer(JobofferBase):
    phone_country_code: str
    phone: str
    days: int
    license_request: bool
    license_description: Optional[str]
    union: bool
    payment_way: str
    ot_after_hours_unit: Optional[str]
    ot_after_hours: Optional[float]
    is_working: bool
    has_probation: bool
    probation_duration: Optional[str]
    disability_insurance: bool
    dental_insurance: bool
    empolyer_provided_persion: bool
    extended_medical_insurance: bool
    extra_benefits: Optional[str]
    offer_date: date
    supervisor_name: str
    supervisor_title: str
    employer_rep: str
    employer_rep_title: str
    vacation_pay_weeks: int
    vacation_pay_percentage: float
    duties_brief: str
    duties: str
    english_french: bool
    oral: Optional[str]
    writing: Optional[str]
    reason_for_no: Optional[str]
    other_language_required: bool
    reason_for_other: Optional[str]
    education_level: str
    specific_edu_requirement: Optional[str]
    skill_experience_requirement: Optional[str]
    other_requirements: Optional[str]

    @root_validator
    def checkProbation(cls, values):
        has_probation = values.get("has_probation", None)
        probation_duration = values.get("probation_duration")
        if has_probation and not probation_duration:
            raise ValueError(
                "Since has probation is true, but did not input probation duration"
            )
        return values

    @root_validator
    def checkLanguage(cls, values):
        english_french = values.get("english_french", None)
        oral = values.get("oral", None)
        writing = values.get("writing", None)
        reason_for_no = values.get("reason_for_no", None)
        if english_french and not oral or not writing:
            raise ValueError(
                "Since English or French is true, but did not input oral or/and writting language requirement"
            )
        if not english_french and not reason_for_no:
            raise ValueError(
                "Since there is no English or French requirement, but did not input the reason"
            )
        return values

    @root_validator
    def checkOtherLanguageReason(cls, values):
        other_language_required = values.get("other_language_required", None)
        reason_for_other = values.get("reason_for_other", None)
        if other_language_required and not reason_for_other:
            raise ValueError(
                "Since required other language in job offer sheet,but did not input the reason"
            )
        return values


class Lmi(BaseModel):
    brief_benefit: str
    job_creation_benefit: Optional[str]
    skill_transfer_benefit: Optional[str]
    fill_shortage_benefit: Optional[str]
    other_benefit: Optional[str]
    canadian_lost_job: bool
    canadian_lost_job_info: Optional[str]

    @root_validator
    def checkLabourDisput(cls, values):
        canadian_lost_job = values.get("canadian_lost_job", None)
        canadian_lost_job_info = values.get("canadian_lost_job_info", None)
        if canadian_lost_job and not canadian_lost_job_info:
            raise ValueError(
                "Since Canadian will lost job because of hiring TFW,but did not input the details about it."
            )
        return values


class Personal(Person):
    pass


class Position(PositionBase):
    pass


class LmiaRecruitment(CommonModel):
    general: General
    personal: Personal
    position: Position
    eraddress: List[ErAddress]
    contact: List[Contact]
    finance: List[Finance]
    joboffer: Joboffer
    lmi: Lmi
    address: List[Address]
    mediaaccount: List[MediaAccount]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels = self.getExcels(
                ["excel/er.xlsx", "excel/lmia.xlsx", "excel/pa.xlsx"]
            )

        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        # call parent class for validating
        super().__init__(excels, output_excel_file, globals())
