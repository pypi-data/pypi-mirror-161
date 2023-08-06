from pydantic import BaseModel, EmailStr
from model.common.commonmodel import CommonModel
import os
from typing import List
from pydantic import BaseModel
from model.common.advertisement import Advertisement,InterviewRecord

class RecruitmentSummary(BaseModel):
    apply_email:EmailStr
    interview_process_evidence:bool
    joboffer_email:bool
    joboffer_email_reply:bool
    
class LmiaApplication(CommonModel):
    
    advertisement:List[Advertisement]
    interviewrecord:List[InterviewRecord]
    recruitmentsummary:RecruitmentSummary
        
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            path=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
            excels=self.getExcels(['excel/recruitment.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())

