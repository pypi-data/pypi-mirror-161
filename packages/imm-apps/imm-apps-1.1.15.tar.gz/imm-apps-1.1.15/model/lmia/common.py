from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator, EmailStr, validator
from model.common.commonmodel import CommonModel
from model.common.person import Person, PersonalAssess
from model.common.advertisement import (
    Advertisement,
    Advertisements,
    InterviewRecord,
    InterviewRecords,
)
from model.common.address import Address
from model.common.contact import ContactBase
from model.common.jobofferbase import JobofferBase
from model.common.jobposition import PositionBase
from termcolor import colored
from model.common.utils import makeList
import os


class LmiaCase(BaseModel):
    area_index: int
    province_index: int
    unemploy_rate: float
    area_median_wage: float
    noc_outlook: int
    reason_failed_hire_canadian: Optional[str]
    provincial_median_wage: float
    is_in_10_days_priority: bool
    top10_wages: float
    is_waived_from_advertisement: bool
    reason_for_waived: Optional[str]
    purpose_of_lmia: str
    stream_of_lmia: str
    has_another_employer: Optional[bool]
    another_employer_name: Optional[str]
    number_of_tfw: int
    duration_number: int
    duration_unit: str
    duration_reason: str
    has_attestation: bool
    use_jobbank: bool
    reason_not_use_jobbank: Optional[str]
    provide_details_even_waived: Optional[str]

    @root_validator
    def checkAdditional(cls, values):
        has_another_employer = values.get("has_another_employer", None)
        another_employer_name = values.get("another_employer_name", None)
        if has_another_employer and not another_employer_name:
            raise ValueError(
                "Since has another employer,but did not input the details about it."
            )
        noc_outlook = values.get("noc_outlook", None)
        reason_failed_hire_canadian = values.get("reason_failed_hire_canadian", None)
        if noc_outlook <= 2 and not reason_failed_hire_canadian:
            print(
                colored(
                    "Warning: since the outlook is <= 2, but it seems you didn't consider that you may be challanged by processing officer for why there is lack of labours",
                    "yellow",
                )
            )

        is_waived_from_advertisement = values.get("is_waived_from_advertisement", None)
        reason_for_waived = values.get("reason_for_waived", None)
        provide_details_even_waived = values.get("provide_details_even_waived", None)
        if is_waived_from_advertisement and not reason_for_waived:
            raise ValueError(
                f"Since the occupation is waived from minimum advertisement, but you did not enter the reason for being waived from advertisement."
            )

        if is_waived_from_advertisement and not provide_details_even_waived:
            raise ValueError(
                f"Since the occupation is waived from minimum advertisement, but you did not answer if you would like to provide details about details of recruitment."
            )

        use_jobbank = values.get("use_jobbank", None)
        reason_not_use_jobbank = values.get("reason_not_use_jobbank", None)
        if not use_jobbank and not reason_not_use_jobbank:
            raise ValueError(
                "Since you did not use jobbank,you should provide reason why did not "
            )

        return values


class General(BaseModel):
    legal_name: str
    operating_name: Optional[str]
    website: Optional[str]
    establish_date: date
    business_intro: str
    cra_number: str
    ft_employee_number: int
    pt_employee_number: int


class Lmi(BaseModel):
    laid_off_in_12: bool
    laid_off_canadians: Optional[int]
    laid_off_tfw: Optional[int]
    laid_off_reason: Optional[str]
    is_work_sharing: bool
    work_sharing_info: Optional[str]
    labour_dispute: bool
    labour_dispute_info: Optional[str]
    brief_benefit: str
    job_creation_benefit: Optional[str]
    skill_transfer_benefit: Optional[str]
    fill_shortage_benefit: Optional[str]
    other_benefit: Optional[str]
    canadian_lost_job: bool
    canadian_lost_job_info: Optional[str]
    safety_concerns: str

    @root_validator
    def checkLabourDisput(cls, values):
        canadian_lost_job = values.get("canadian_lost_job", None)
        canadian_lost_job_info = values.get("canadian_lost_job_info", None)
        if canadian_lost_job and not canadian_lost_job_info:
            raise ValueError(
                "Since Canadian will lost job because of hiring TFW,but did not input the details about it."
            )
        return values

    @root_validator
    def checkLayoff(cls, values):
        laid_off_in_12 = values.get("laid_off_in_12", None)
        laid_off_canadians = values.get("laid_off_canadians", None)
        laid_off_tfw = values.get("laid_off_tfw", None)
        laid_off_reason = values.get("laid_off_reason", None)
        if laid_off_in_12 and (
            not laid_off_canadians or not laid_off_tfw or not laid_off_reason
        ):
            raise ValueError(
                "Since there is laid of in past 12 months in info lmi sheet,but did not input how many Canadians and/or foreign workers, and/or reason of lay off."
            )
        return values

    @root_validator
    def checkWorkSharing(cls, values):
        is_work_sharing = values.get("is_work_sharing", None)
        work_sharing_info = values.get("work_sharing_info", None)
        if is_work_sharing and not work_sharing_info:
            raise ValueError(
                "Since there is work sharing in info lmi sheet,but did not input the details about it."
            )
        return values


class ErAddress(Address):
    phone: Optional[str]

    @root_validator
    def checkRowCompletion(cls, values):
        all_fields = [
            "po_box",
            "unit",
            "street_number",
            "street_name",
            "city",
            "district",
            "province",
            "country",
            "post_code",
            "phone",
        ]
        all_fields_values = [values[field] for field in all_fields]

        required_fields = [
            "street_number",
            "street_name",
            "city",
            "country",
            "post_code",
            "phone",
        ]
        variable_type = values.get("variable_type")
        display_type = values.get("display_type")

        required_values = [values[field] for field in required_fields]

        has_values = [value for value in required_values if value]

        if (
            any(all_fields_values)
            and not all(required_values)
            and variable_type != "working_address"
        ):
            raise ValueError(
                f"Please check the row with values ({','.join(has_values)}), some required fileds are missed."
            )

        if (
            any(all_fields_values)
            and not all(required_values)
            and variable_type == "working_address"
            and display_type == "工作地点1"
        ):
            raise ValueError(
                f"Please check the row with values ({','.join(has_values)}), some required fileds are missed."
            )

        return values


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
        if province and province not in [
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
                f'Since country is Canada is, the province must be one of  "AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"'
            )
        return values


class Joboffer(JobofferBase):
    phone_country_code: str
    phone: str
    license_request: bool
    license_description: Optional[str]
    union: bool
    atypical_schedule: bool
    atypical_schedule_explain: Optional[str]
    part_time_explain: Optional[str]
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
    duties: list
    english_french: bool
    oral: Optional[str]
    writing: Optional[str]
    reason_for_no: Optional[str]
    other_language_required: bool
    reason_for_other: Optional[str]
    education_level: str
    is_trade: Optional[bool]
    trade_type: Optional[str]
    specific_edu_requirement: Optional[str]
    skill_experience_requirement: Optional[str]
    other_requirements: Optional[list]

    _str2bool_duties = validator("duties", allow_reuse=True, pre=True)(makeList)
    _str2bool_other_requirements = validator(
        "other_requirements", allow_reuse=True, pre=True
    )(makeList)

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

    @root_validator
    def checkOthers(cls, values):
        atypical_schedule = values.get("atypical_schedule", None)
        atypical_schedule_explain = values.get("atypical_schedule_explain", None)
        if atypical_schedule and not atypical_schedule_explain:
            raise ValueError(
                "Since it is atypical schedule, but you did not provide explaination."
            )

        license_request = values.get("license_request", None)
        license_description = values.get("license_description", None)
        if license_request and not license_description:
            raise ValueError(
                "Since license is required, but you did not provide details."
            )

        days = values.get("days", None)
        hours = values.get("hours", None)
        part_time_explain = values.get("part_time_explain", None)
        if not atypical_schedule and not all([days, hours]):
            raise ValueError(
                "Since it is fixed working time, but you did not provide days per week and hours per week."
            )

        if hours < 30 and not part_time_explain:
            raise ValueError(
                "Since hours per week is less than 30, you did not provide explaination."
            )
        return values


class Personal(Person):
    pass


class Position(PositionBase):
    pass


# RCIC
class Rcic(BaseModel):
    first_name: str
    last_name: str
    rcic_number: str
    email: EmailStr
    company: str
    rcic_rate: str
    how_client_know_rcic: str

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name
