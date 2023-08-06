from pydantic import BaseModel, root_validator, validator, EmailStr
from datetime import date
from typing import Optional
from model.common.utils import makeList, checkRow
from model.common.person import Person
from model.common.mixins import DurationMixin
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
    duties: list

    _str2bool_duties = validator("duties", allow_reuse=True, pre=True)(makeList)

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
    def checkRowCompletion(cls, values):
        all_fields = [
            "start_date",
            "end_date",
            "job_title",
            "noc_code",
            "weekly_hours",
            "company",
            "city",
            "province",
            "country",
            "duties",
        ]
        all_fields_values = [values.get(field, None) for field in all_fields]

        required_fields = [
            "start_date",
            "job_title",
            "noc_code",
            "weekly_hours",
            "company",
            "city",
            "country",
            "duties",
        ]
        required_values = [values.get(field, None) for field in required_fields]

        has_values = [value for value in required_values if value]

        if any(all_fields_values) and not all(required_values):
            raise ValueError(
                f"Please check the row with values ({has_values}) in table-address, some required fileds are missed."
            )
        return values
