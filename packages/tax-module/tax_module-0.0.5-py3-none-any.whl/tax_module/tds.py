from typing import Dict, List

from tax_module.errors import TDSRateNotAvailable
from tax_module.models import (
    AppliedTax,
    Tax,
    TaxType,
    IncomeTaxItem,
)


class TDSModule:
    def __init__(self, rate_card: Dict):
        self._rate_card = rate_card

    def calculate_taxes(self, taxable_item: IncomeTaxItem) -> List[AppliedTax]:
        try:
            tds_rate = self._rate_card[taxable_item.pan_holder_type]
        except KeyError:
            raise TDSRateNotAvailable(
                f"No TDS Rate Available for pan_holder_type:{str(taxable_item.pan_holder_type)}"
            )

        applicable_taxes = [Tax(type=TaxType.TDS, percentage=tds_rate)]

        return [
            AppliedTax.from_taxable_amount(
                tax=tax, taxable_amount=taxable_item.amount, sum_of_taxes=tds_rate
            )
            for tax in applicable_taxes
        ]


def get_tds_module(rate_card):
    return TDSModule(rate_card=rate_card)
