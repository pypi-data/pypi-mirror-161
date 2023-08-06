from pydantic import BaseModel
from typing import List
from utils.utils import formatMoney


class Finance(BaseModel):
    year: int
    total_asset: float
    net_asset: float
    revenue: float
    net_income: float
    retained_earning: float

    @property
    def formatted_revenue(self):
        return formatMoney(self.revenue)

    @property
    def formatted_net_income(self):
        return formatMoney(self.net_income)

    @property
    def formatted_retained_earning(self):
        return formatMoney(self.retained_earning)


class Finances:
    def __init__(self, finances: List[Finance]) -> None:
        self.finances = finances

    @property
    def last_income(self):
        if len(self.finances) > 0:
            return self.finances[0].revenue
