from pydantic import BaseModel, EmailStr
from typing import List, Optional

# RCIC
class Rcic(BaseModel):
    first_name: str
    last_name: str
    company: str
    sex: str
    rcic_number: str

    @property
    def name(self):
        return self.first_name + " " + self.last_name


class RcicList(BaseModel):
    id_name: str
    first_name: str
    last_name: str
    employer_legal_name: str
    country_code: str
    phone: str
    email: EmailStr
    unit: Optional[str]
    street_number: str
    street_name: str
    city: str
    province: str
    country: str
    post_code: str
    rcic_number: str

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    @property
    def line1(self):
        l1 = self.unit + " " if self.unit else ""
        l1 += self.street_number + " " if self.street_number else ""
        l1 += self.street_name
        return l1


class Rcics:
    def __init__(self, rcics: List[RcicList]) -> None:
        self.rcics = rcics

    def getRcicByName(self, first_name: str, last_name: str):
        rcics = [
            rcic
            for rcic in self.rcics
            if rcic.first_name.lower() == first_name.lower()
            and rcic.last_name.lower() == last_name.lower()
        ]
        return rcics[0] if len(rcics) > 0 else None

    def getRcicByNumber(self, rcic_number: str):
        rcics = [
            rcic
            for rcic in self.rcics
            if rcic.rcic_number.lower() == rcic_number.lower()
        ]
        return rcics[0] if len(rcics) > 0 else None

    def getRcicByIdName(self, id_name: str):
        rcics = [rcic for rcic in self.rcics if rcic.id_name.lower() == id_name.lower()]
        return rcics[0] if len(rcics) > 0 else None
