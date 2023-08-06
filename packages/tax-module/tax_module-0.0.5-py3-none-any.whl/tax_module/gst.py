from typing import List, Dict

from tax_module.errors import GSTRateNotAvailable
from tax_module.models import (
    AppliedTax,
    Tax,
    TaxType,
    TransactionType,
    GSTItem,
)


class GSTModule:
    def __init__(self, rate_card: Dict):
        self._rate_card = rate_card

    def calculate_taxes(self, taxable_item: GSTItem) -> List[AppliedTax]:
        try:
            gst_rate = self._rate_card[taxable_item.item_type]
        except KeyError:
            raise GSTRateNotAvailable(
                f"No GST Rate Available for ItemType:{taxable_item.item_type}"
            )

        applicable_taxes = self._get_applicable_taxes(
            transaction_type=taxable_item.transaction_type, gst_rate=gst_rate
        )

        return [
            AppliedTax.from_taxable_amount(
                tax=tax, taxable_amount=taxable_item.amount, sum_of_taxes=gst_rate
            )
            for tax in applicable_taxes
        ]

    def _get_applicable_taxes(
        self, transaction_type: TransactionType, gst_rate: float
    ) -> List[Tax]:
        if transaction_type == TransactionType.INTER_STATE:
            return [Tax(type=TaxType.IGST, percentage=gst_rate)]

        return [
            Tax(type=TaxType.CGST, percentage=gst_rate / 2),
            Tax(type=TaxType.SGST, percentage=gst_rate / 2),
        ]


def get_gst_module(rate_card):
    return GSTModule(rate_card=rate_card)
