from pydantic import BaseModel
from termcolor import colored
from functools import reduce
from typing import List, Optional
from model.common.address import Address
from model.common.phone import Phone
from model.common.trperson import (
    COR,
    PersonId,
    Personal,
    Marriage,
    Education,
    Employment,
)
from model.common.tr import TrCaseIn, TrBackground, VrInCanada
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb5708 import FormBuilder5708
from datetime import date
import json


class M5708Model(CommonModel, BuilderModel):
    personal: Personal
    marriage: Marriage
    personid: List[PersonId]
    address: List[Address]
    education: List[Education]
    employment: List[Employment]
    phone: List[Phone]
    cor: List[COR]
    trcasein: TrCaseIn
    vrincanada: VrInCanada
    trbackground: TrBackground

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels = self.getExcels(["excel/tr.xlsx", "excel/pa.xlsx"])
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())

    # TODO: python-docx-template cannot use function returned value
    @property
    def visit_description(self):
        last_visit = self.trcasein.most_recent_entry_date
        original_visit = self.trcasein.original_entry_date
        last_place = self.trcasein.most_recent_entry_place
        original_place = self.trcasein.original_entry_place

        # if last visit existed, calculate the days
        visit_date = last_visit or original_visit
        visit_place = last_place or original_place
        days = (date.today() - visit_date).days

        apply_for = "restoration" if days > 180 else "extension"
        return f"I am applying for {apply_for}"

    @property
    def getAllDict(self):
        return {
            **self.dict(),
            "visit_description": self.visit_description,
            "subject": self.personal.subject,
            "object": self.personal.object,
            "attributive": self.personal.attributive,
            "salutation": self.personal.salutation,
            "short_name": self.personal.short_name,
        }

    def make_pdf_form(self, output_json, *args, **kwargs):
        pf = FormBuilder5708(self)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        return self.getAllDict
