from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.rcic import RcicList
from model.common.contact import ContactBase
from pdfform.bcpnp.fbrep import FormBuilderBcRep
import json
from termcolor import colored
from model.common.employerbase import EmployerBase
from webform.bcpnp.rep import Representative


class General(EmployerBase):
    pass


class Contact(ContactBase):
    pass


class Personal(BaseModel):
    last_name: str
    first_name: str
    sex: str
    dob: date
    uci: Optional[str]


class MRepModel(CommonModel, BuilderModel):
    rciclist: List[RcicList]
    personal: Personal
    general: General
    contact: List[Contact]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels = self.getExcels(
                ["excel/pa.xlsx", "excel/rep.xlsx", "excel/er.xlsx"]
            )
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        # call parent class for validating
        super().__init__(excels, output_excel_file, globals())

    def make_pdf_form(self, output_json, rcic_id_name, *args, **kwargs):
        pf = FormBuilderBcRep(self, rcic_id_name)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic_id_name, *args, **kwargs):
        # actions = Representative(self, rcic_id_name).fill()
        # with open(output_json, "w") as output:
        #     json.dump(actions, output, indent=3, default=str)
        # print(colored(f"{output_json} has been created. ", "green"))
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")
