from model.lmia.common import *
from model.common.commonmodel import CommonModel
from webform.lmiaportal.webformmodel import WebformModel
from model.common.contact import Contacts
from model.common.finance import Finance


class Emp5627(BaseModel):
    named: bool
    provide_accommodation: bool
    description: Optional[str]
    rent_unit: str
    rent_amount: float
    accommodation_type: str
    explain: Optional[str]
    bedrooms: str
    people: str
    bathrooms: str
    other: Optional[str]
    cap_exempted: bool
    which_exemption: Optional[str]
    exemption_rationale: Optional[str]
    is_in_seasonal_industry: Optional[bool]
    four_week_start_date: Optional[date]
    four_week_end_date: Optional[date]
    q_a: Optional[int]
    q_b: Optional[int]
    q_c: Optional[int]
    q_d: Optional[int]
    q_e: Optional[int]
    q_f: Optional[int]
    q_g: Optional[int]
    q_h: Optional[int]

    @root_validator
    def checkAnswers(cls, values):
        cap_exempted = values.get("cap_exempted", None)
        explanations = [
            values.get(var, None)
            for var in [
                "which_exemption",
                "exemption_rationale",
            ]
        ]
        if cap_exempted and not all(v is not None for v in explanations):
            raise ValueError(
                "Since CAP exempted, you didn't input all the information about the which exemptin and/or the rationale."
            )

        not_exempted_info = [
            values.get(var, None)
            for var in [
                "is_in_seasonal_industry",
                "four_week_start_date",
                "four_week_end_date",
                "q_a",
                "q_b",
                "q_c",
                "q_d",
                "q_e",
                "q_f",
                "q_g",
                "q_h",
            ]
        ]
        if not cap_exempted and not all(v is not None for v in not_exempted_info):
            raise ValueError(
                "Since the application is not CAP exempted, you didn't input all the information required for CAP claculation."
            )

        provide_accommodation = values.get("provide_accommodation", None)
        description = values.get("description", None)
        if not provide_accommodation and not description:
            raise ValueError(
                "You don't provide accommodation, but did not provide the explaination on how to assist the TFW."
            )

        provide_accommodation = values.get("provide_accommodation", None)
        provide_accommodation_details = [
            values.get(var, None)
            for var in [
                "rent_unit",
                "rent_amount",
                "accommodation_type",
                "bedrooms",
                "people",
                "bathrooms",
            ]
        ]
        if provide_accommodation and not all(
            v is not None for v in provide_accommodation_details
        ):
            raise ValueError(
                "Since employer provides accommodation, you didn't input all the information about the accommodation."
            )

        accommodation_type = values.get("accommodation_type", None)
        explain = values.get("explain", None)
        if accommodation_type == "other" and not explain:
            raise ValueError(
                "Since accommodation type is 'other', but you didn't describe it."
            )
        return values


class Personal(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    sex: Optional[str]
    dob: Optional[date]
    citizen: Optional[str]


class M5627Model(CommonModel):
    lmiacase: LmiaCase
    general: General
    lmi: Lmi
    emp5627: Emp5627
    eraddress: List[ErAddress]
    contact: List[Contact]
    finance: List[Finance]
    joboffer: Joboffer
    personal: Personal
    personalassess: PersonalAssess
    position: Position
    advertisement: List[Advertisement]
    interviewrecord: List[InterviewRecord]
    rcic: Rcic

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.path.pardir)
            )
            excels = self.getExcels(
                [
                    "excel/recruitment.xlsx",
                    "excel/pa.xlsx",
                    "excel/er.xlsx",
                    "excel/rep.xlsx",
                    "excel/lmia.xlsx",
                ]
            )
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        # call parent class for validating
        super().__init__(excels, output_excel_file, globals())
        # check if TFW is named, details must be included in personal sheet
        # self.checkTFW()

    def checkTFW(self):
        if self.emp5627.named and not all(
            [
                self.personal.first_name,
                self.personal.last_name,
                self.personal.sex,
                self.personal.citizen,
                self.personal.dob,
            ]
        ):
            raise ValueError(
                "Since TFW is name required, you haven't input all information required in info-personal sheet."
            )

    def make_web_form(self, output_json, upload_dir, rcic, *args, **kwargs):
        args = {
            "model_variable": "5627",
            "app": self,
            "output_json": output_json,
            "upload_dir": upload_dir,
            "rcic": rcic,
        }
        wf = WebformModel(**args)
        wf.save()

    def make_pdf_form(self, *args, **kwargs):
        pass

    @property
    def context(self, *args, **kwargs):
        interview = InterviewRecords(self.interviewrecord)
        primary_contact = Contacts(self.contact).primary
        return {
            **self.dict(),
            "formatted_finance": [
                {
                    "year": f.year,
                    "formatted_revenue": f.formatted_revenue,
                    "formatted_net_income": f.formatted_net_income,
                    "formatted_retained_earning": f.formatted_retained_earning,
                }
                for f in self.finance
            ],
            "num_of_job_posts": Advertisements(self.advertisement).amount,
            "why_qualified": self.personalassess.why_qualified,
            "adv_summary": [
                {
                    "start_date": a.start_date,
                    "end_date": a.end_date,
                    "media": a.media,
                    "days": a.days,
                }
                for a in self.advertisement
            ],
            "high_wage": True
            if float(self.joboffer.hourly_rate) >= self.lmiacase.provincial_median_wage
            else False,
            "rs": {
                "resume_num": interview.resume_num,
                "canadian_num": interview.canadian_num,
                "unknown_num": interview.unknown_num,
                "foreigner_num": interview.foreigner_num,
                "total_canadian": interview.total_canadian,
                "total_interviewed_canadians": interview.total_interviewed_canadians,
                "canadian_records": interview.canadian_records,
            },
            "primary_contact": primary_contact,
        }
