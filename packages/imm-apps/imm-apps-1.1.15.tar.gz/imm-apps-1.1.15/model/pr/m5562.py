from model.common.commonmodel import CommonModel
from datetime import date
from pydantic import BaseModel, root_validator
from typing import List
from model.common.mixins import DatePeriod
from model.common.utils import checkRow


class Travel(DatePeriod):
    length: int
    destination: str
    purpose: str

    @root_validator
    def checkCompletion(cls, values):
        all_fields = ["start_date", "end_date", "length", "destination", "purpose"]
        required_fields = ["start_date", "end_date", "length", "destination", "purpose"]
        checkRow(values, all_fields, required_fields)
        return values


class Personal(BaseModel):
    last_name: str
    first_name: str


class M5562Model(CommonModel):
    travel: List[Travel]
    personal: Personal

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            excels = self.getExcels(["excel/pa.xlsx"])
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        super().__init__(excels, output_excel_file, globals())
