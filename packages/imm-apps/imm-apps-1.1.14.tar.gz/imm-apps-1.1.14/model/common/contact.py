from pydantic import BaseModel, EmailStr, root_validator
from typing import Optional, List
from model.common.utils import checkRow


class ContactBase(BaseModel):
    variable_type: Optional[str]
    display_type: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]

    # class Config:
    #     anystr_lower = True

    @root_validator
    def checkCompletion(cls, values):
        all_fields = ["last_name", "first_name", "phone", "email"]
        required_fields = ["last_name", "first_name", "phone", "email"]
        variable_type=values.get("variable_type")
        if variable_type=="primary":
            checkRow(values, all_fields, required_fields)
        return values
    
    @property
    def full_name(self):
        return self.first_name+' '+self.last_name if self.first_name and self.last_name else None

class Contacts(object):
    def __init__(self, contacts: List[ContactBase]):
        self.contacts = contacts

    def _specific_contact(self, v_type):
        contact = [
            contact for contact in self.contacts if contact.variable_type == v_type
        ]
        return contact[0] if contact else None

    @property
    def primary(self):
        return self._specific_contact("primary")

    @property
    def second(self):
        return self._specific_contact("second")

    @property
    def preferredContact(self):
        for contact_type in ["primary", "second"]:
            contact = self._specific_contact(contact_type)
            if contact and contact.last_name:
                return contact
