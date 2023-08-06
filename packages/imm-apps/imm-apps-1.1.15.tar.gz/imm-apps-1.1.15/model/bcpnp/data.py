from pydantic import BaseModel, validator, EmailStr
from datetime import date
from typing import Optional, List, Union
from model.common.employerbase import EmployerBase
from model.common.jobofferbase import JobofferBase
from model.common.contact import ContactBase
from model.common.utils import Duration
from model.common.address import Address
from pydantic.class_validators import root_validator
from model.common.utils import makeList

# bcpnp
class Bcpnp(BaseModel):
    has_applied_before: bool
    pre_file_no: Optional[str]
    account: Optional[str]
    password: Optional[str]
    submission_date: date
    case_stream: str
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

    @root_validator
    def checkAnswers(cls, values):
        questions = ["q1", "q2", "q3", "q4", "q5", "q6", "q7"]
        explanations = [q + "_explaination" for q in questions]
        qas = dict(zip(questions, explanations))
        qas["has_applied_before"] = "pre_file_no"
        for k, v in qas.items():
            if values.get(k) and not values.get(v):
                raise ValueError(
                    f"Since {k} is true, but you did not answer the question {v} in info-bcpnp sheet"
                )
        return values


# employer classes
class General(EmployerBase):
    company_intro: str
    business_intro: str
    company_more: Optional[str]
    recruit_email: EmailStr
    industry: str
    corporate_structure: str
    registration_number: str
    recruit_email: EmailStr
    ft_employee_number: int
    establish_date: date


# employer address
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
        all_fields_values = [values.get(field) for field in all_fields]

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

        required_values = [values.get(field) for field in required_fields]

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
    position: Optional[str]


# personal classes
class JobOffer(JobofferBase):
    offer_date: date
    is_working: bool
    work_start_date: Optional[date]
    supervisor_name: str
    supervisor_title: str
    other_language_required: bool
    reason_for_other: Optional[str]
    license_request: bool
    license_description: Optional[str]
    license_met: Optional[bool]
    license_met_reason: Optional[str]
    duties: list
    specific_edu_requirement: Optional[str]
    skill_experience_requirement: Optional[str]
    other_requirements: Optional[list]
    why_not_permanent: Optional[str]

    _str2bool_duties = validator("duties", allow_reuse=True, pre=True)(makeList)
    _str2bool_other_requirements = validator(
        "other_requirements", allow_reuse=True, pre=True
    )(makeList)

    @property
    def date_of_offer(self):
        return self.offer_date.strftime("%b %d, %Y")

    @property
    def start_date_say(self):
        return self.work_start_date.strftime("%b %d, %Y")

    @property
    def requirements(self):
        return [
            r
            for r in [
                self.specific_edu_requirement,
                self.skill_experience_requirement,
                *self.other_requirements,
            ]
            if r is not None
        ]


class PersonalAssess(BaseModel):
    work_experience_brief: str
    education_brief: str
    competency_brief: str
    language_brief: Optional[str]
    performance_remark: Optional[str]

    @property
    def why_qualified(self):
        qualifications = [
            self.work_experience_brief,
            self.education_brief,
            self.competency_brief,
            self.language_brief,
            self.performance_remark,
        ]
        return [q for q in qualifications if q is not None]
