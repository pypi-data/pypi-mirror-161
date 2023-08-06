from .context import DATADIR
from email.policy import default
from textwrap import indent
from typing import List,Optional
from model.experience.resumedata import Personal,Language,PersonalAssess,Education, Employment
from model.common.commonmodel import CommonModel
from model.common.phone import Phone,Phones 
from model.common.address import Address,Addresses

class ResumeModel(CommonModel):
    personal:Personal
    phone:List[Phone]
    personalassess:PersonalAssess
    education:List[Education]
    language:Optional[List[Language]]
    employment:Optional[List[Employment]]
    address:List[Address]
    
    
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self,excels=None,output_excel_file=None):
        if output_excel_file:
            excels=self.getExcels(['excel/pa.xlsx'])
        else:
            if excels is None and len(excels)==0:
                raise ValueError('You must input excel file list as source data for validation')
        # call parent class for validating
        super().__init__(excels,output_excel_file,globals())
        
    def context(self, doc_type=None):
        return {
            **self.dict(),
            "phone": Phones(self.phone).PreferredPhone.international_format_full,
            "address": Addresses(self.address).PreferredAddress.full_address,
            "full_name": self.personal.full_name,
        }
    

