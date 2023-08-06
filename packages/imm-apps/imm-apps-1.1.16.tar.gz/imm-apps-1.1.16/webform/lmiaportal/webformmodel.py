from webform.lmiaportal.hourspay import HoursPay
from webform.lmiaportal.login import Login
from webform.lmiaportal.dashboard import Dashboard
from webform.lmiaportal.contact import Contact
from webform.lmiaportal.wage import Wage
from webform.lmiaportal.foreignnational import ForeignNational
from webform.lmiaportal.ee import EE
from webform.lmiaportal.hws_lws import HWS_LWS
from webform.lmiaportal.transationplan import TransitionPlan
from webform.lmiaportal.cap import Cap
from webform.lmiaportal.accommodation import Accommodation
from webform.lmiaportal.hourspay import HoursPay
from webform.lmiaportal.joboffer import JobOffer
from webform.lmiaportal.empbenefits import EmpBenefits
from webform.lmiaportal.recruitment import Recruitment
from webform.lmiaportal.lmbenefits import LmBenefits
from webform.lmiaportal.layoff import Layoff
from webform.lmiaportal.upload import Upload
import json
from termcolor import colored
import os, dotenv


class WebformModel:
    """Generate json file for webform filling based on model

    Args:
        output_json:str,
        upload_dir:str,
        rcic: str = "jacky",
    """

    def __init__(self, model_variable, app, output_json, upload_dir, rcic="jacky"):
        self.model_variable = model_variable
        # self.source_excel = source_excel
        self.output_json = output_json
        self.upload_dir = upload_dir
        self.rcic = rcic
        self.app = app

    # models = {"5593": M5593Model, "5626": M5626Model, "5627": M5627Model}

    def save(self):
        # self.app = self.getApplicant()

        # login
        actions = self.login()
        # pages to fill
        actions += self.pages()

        # upload files
        actions += self.upload()
        # output actions
        # print(json.dumps(actions, indent=3, default=str))

        # output json
        self.output(actions)

    def getApplicant(self):
        # get lmia data
        the_model = WebformModel.models.get(self.model_variable)
        if not the_model:
            print(
                colored(
                    f"The model {self.model_variable} is not existed, please check.",
                    "red",
                )
            )
            return None

        app = the_model(excels=[self.source_excel])
        if not app:
            print(
                colored(
                    f"The model {self.source_excel} is not existed, please check.",
                    "red",
                )
            )
            return None
        return app

    def login(self):
        path = os.path.abspath(os.path.join(os.path.expanduser("~"), ".portalenv"))
        config = dotenv.dotenv_values(path)
        rcic_account = {
            "account": config.get(self.rcic + "_lmiaportal_account"),
            "password": config.get(self.rcic + "_lmiaportal_password"),
            "security_answers": config.get(self.rcic + "_lmiaportal_sequrity_answers"),
        }
        if (
            not rcic_account["account"]
            or not rcic_account["password"]
            or not rcic_account["security_answers"]
        ):
            print(
                colored(
                    f"{self.rcic}'s prportal account, password, and/or security answers is not existed. Check the .portalenv file in your home directory and add your profile",
                    "red",
                )
            )
            exit(1)

        security_dict = json.loads(rcic_account["security_answers"])
        l = Login(
            rcic_account["account"],
            rcic_account["password"],
            security_dict,
        )
        return l.actions

    def pages(self):
        actions = []
        modules = {
            "5593": [
                Dashboard,
                Contact,
                Wage,
                ForeignNational,
                EE,
                HoursPay,
                JobOffer,
                EmpBenefits,
                Recruitment,
                LmBenefits,
                Layoff,
            ],
            "5626": [
                Dashboard,
                Contact,
                HWS_LWS,
                TransitionPlan,
                HoursPay,
                JobOffer,
                EmpBenefits,
                Recruitment,
                LmBenefits,
                Layoff,
            ],
            "5627": [
                Dashboard,
                Contact,
                HWS_LWS,
                Accommodation,
                Cap,
                HoursPay,
                JobOffer,
                EmpBenefits,
                Recruitment,
                LmBenefits,
                Layoff,
            ],
        }
        if self.model_variable not in modules:
            raise ValueError(
                f"There is no module named: {self.model_variable} in webformmodel.py"
            )

        for module in modules.get(self.model_variable):
            actions += module(self.app).actions

        return actions

    def upload(self):
        actions = []
        if not os.path.exists(self.upload_dir):
            raise ValueError(f"The directory {self.upload_dir} is not existed")

        upload = Upload(self.app, self.upload_dir)
        actions += upload.actions
        return actions

    def output(self, actions):
        if os.path.exists(self.output_json):
            overwrite = input(
                colored(f"The file {self.output_json} is existed, overwrite?", "red")
            )
            if overwrite and overwrite[0].lower() != "y":
                return
        with open(self.output_json, "w") as f:
            json.dump(actions, f, indent=3, default=str)
            print(colored(f"{self.output_json} has been saved", "green"))
