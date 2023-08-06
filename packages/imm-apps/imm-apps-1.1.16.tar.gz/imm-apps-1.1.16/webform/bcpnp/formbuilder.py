from webform.bcpnp.register import Register
from webform.bcpnp.bcpnpmodel_reg import BcpnpModelReg, BcpnpEEModelReg
from webform.bcpnp.bcpnpmodel_app import BcpnpEEModelApp, BcpnpModelApp
from webform.bcpnp.login import Login
from webform.bcpnp.registrant import Registrant
from webform.bcpnp.education_reg import EducationReg
from webform.bcpnp.employment import EmploymentReg
from webform.bcpnp.joboffer_reg import JobofferReg
from webform.bcpnp.language import LanguageReg
from webform.bcpnp.rep import Representative
from webform.bcpnp.submit import Submit
from pathlib import Path
from abc import ABC, abstractmethod
from webform.bcpnp.applicant import Applicant
from webform.bcpnp.education_app import EducationApp
from webform.bcpnp.workexperience import WorkExperience
from webform.bcpnp.family import FamilyApp
from webform.bcpnp.joboffer_app import JobofferApp
from webform.bcpnp.rep import Representative
from model.bcpnp.mrep import RcicList
from model.bcpnp.mrep import MRepModel


class Builder(ABC):
    def __init__(self, excels) -> None:
        if len(excels) > 0 and not Path(excels[0]).exists():
            raise FileExistsError(f"{excels[0]} is not existed")

    @abstractmethod
    def make_web_form(self, *args, **kwargs):
        raise NotImplementedError("This class must be implemented. ")


class ProfileBuilder(Builder):
    def __init__(self, excels, model: object):
        super().__init__(excels)
        self.applicant = model(excels=excels)

    def make_web_form(self):
        # signing in, pick skill immigration, select stream and confirm
        actions = Login(self.applicant).login()
        # Registrant
        actions += Registrant(self.applicant).fill()
        return actions


class RegBuilder(Builder):
    action_blocks = [
        Registrant,
        EducationReg,
        EmploymentReg,
        JobofferReg,
        LanguageReg,
        Submit,
    ]

    def __init__(self, excels, is_ee: bool = False):
        super().__init__(excels)
        self.applicant = (
            BcpnpEEModelReg(excels=excels) if is_ee else BcpnpModelReg(excels=excels)
        )

    def make_web_form(self, initial=True, previous=False):
        actions = Login(self.applicant).login(initial=initial, previous=previous)
        for block in RegBuilder.action_blocks:
            actions += block(self.applicant).fill()

        return actions


class AppBuilder(Builder):
    action_blocks = [
        Applicant,
        EducationApp,
        WorkExperience,
        FamilyApp,
        JobofferApp,
        Submit,
    ]

    def __init__(self, excels, is_ee: bool = False):
        super().__init__(excels)
        self.applicant = (
            BcpnpEEModelApp(excels=excels) if is_ee else BcpnpModelApp(excels=excels)
        )

    def make_web_form(self, initial=True, previous=False):
        actions = Login(self.applicant).login(initial=initial, previous=previous)
        for block in AppBuilder.action_blocks:
            actions += block(self.applicant).fill()

        return actions
