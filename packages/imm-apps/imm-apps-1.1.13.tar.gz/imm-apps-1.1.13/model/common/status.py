from datetime import date
from pkg_resources import working_set
from pydantic import BaseModel, root_validator
from typing import Optional, List
from termcolor import colored


class Status(BaseModel):
    current_country: str
    current_country_status: str
    current_workpermit_type: Optional[str]
    has_vr: Optional[bool]
    current_status_start_date: date
    current_status_end_date: date
    other_status_explaination: Optional[str]
    last_entry_date: Optional[date]
    last_entry_place: Optional[date]

    @root_validator
    def checkWorkerType(cls, values):
        current_status = values.get("current_country_status")
        workpermit_type = values.get("current_workpermit_type")
        if current_status == "Worker" and workpermit_type == None:
            raise ValueError(
                colored(
                    f"Since current stauts is {current_status}, but you did not answer the question followed '工签类别' in info-status sheet",
                    "red",
                )
            )
        return values
