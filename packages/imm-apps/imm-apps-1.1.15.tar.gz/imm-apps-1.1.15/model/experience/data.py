from pydantic import BaseModel, validator, EmailStr, root_validator
from model.common.utils import makeList
from model.common.person import Person
from model.common.employmentbase import EmploymentBase
from model.common.utils import checkRow
from pydantic import BaseModel, root_validator, validator, EmailStr
from typing import Optional
from model.common.utils import makeList, checkRow
from model.common.person import Person
from model.common.employmentbase import EmploymentBase
from model.common.educationbase import EducationBase


class PersonalAssess(BaseModel):
    self_description: Optional[str]
    skill_list: list
    activity: Optional[list]

    _str2bool_activity = validator("activity", allow_reuse=True, pre=True)(makeList)
    _str2bool_skill_list = validator("skill_list", allow_reuse=True, pre=True)(makeList)


class Personal(Person):
    email: Optional[EmailStr]

    @property
    def birth_day(self):
        return self.dob.strftime("%b %d, %Y")


class Education(EducationBase):
    city: str
    country: str
    description: Optional[str]

    @root_validator
    def checkRowCompletion(cls, values):
        all_fields = [
            "start_date",
            "end_date",
            "school_name",
            "education_level",
            "field_of_study",
            "city",
            "country",
            "description",
        ]
        required_fields = [
            "start_date",
            "school_name",
            "education_level",
            "field_of_study",
            "city",
            "country",
        ]

        checkRow(values, all_fields, required_fields)

        return values


class Language(BaseModel):
    reading: str
    writting: str
    listening: str
    speaking: str
    test_type: str
    remark: Optional[str]

    @root_validator
    def checkRowCompletion(cls, values):

        all_fields = [
            "reading",
            "writting",
            "listening",
            "speaking",
            "test_type",
            "remark",
        ]
        required_fields = ["reading", "writting", "listening", "speaking", "test_type"]
        checkRow(values, all_fields, required_fields)

        return values


class Employment(EmploymentBase):
    department: Optional[str]
    duties: list
    company_brief: str
    fullname_of_certificate_provider: Optional[str]
    position_of_certificate_provider: Optional[str]
    department_of_certificate_provider: Optional[str]
    phone_of_certificate_provider: Optional[str]
    email_of_certificate_provider: Optional[EmailStr]
    employment_certificate: bool

    _normalize_duties = validator("duties", allow_reuse=True, pre=True)(makeList)

    @root_validator
    def checkCanadaProvince(cls, values):
        country = values.get("country")
        province = values.get("province")
        if country.lower() == "canada" and province not in [
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

    @root_validator
    def checkCompletion(cls, values):
        all_fields = [
            "job_title",
            "noc_code",
            "weekly_hours",
            "company",
            "city",
            "province",
            "country",
            "department",
            "duties",
            "company_brief",
            "fullname_of_certificate_provider",
            "position_of_certificate_provider",
            "department_of_certificate_provider",
            "phone_of_certificate_provider",
            "email_of_certificate_provider",
            "employment_certificate",
        ]
        required_fields = [
            "job_title",
            "noc_code",
            "weekly_hours",
            "company",
            "city",
            "province",
            "country",
            "duties",
            "company_brief",
            "fullname_of_certificate_provider",
            "position_of_certificate_provider",
            "phone_of_certificate_provider",
            "email_of_certificate_provider",
            "employment_certificate",
        ]

        checkRow(values, all_fields, required_fields)

        return values
