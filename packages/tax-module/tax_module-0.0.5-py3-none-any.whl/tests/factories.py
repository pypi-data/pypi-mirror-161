from shuttlis.utils import uuid4_str
from typing import List

from tax_module.models import (
    AmountType,
    Amount,
    TaxableItemType,
    GSTItem,
    IncomeTaxItem,
    TaxPayer,
)


def tax_payer_dm(pan_card: str = None):
    return TaxPayer(pan_card=pan_card or "ABCPD1234H")


def amount_dm(amount: int = None, type: AmountType = None):
    return Amount(value=amount or 100, type=type or AmountType.TAX_INCLUSIVE)


def gst_item_dm(
    amount: Amount = None,
    payer_states: List[str] = None,
    payee_state: str = None,
    item_type: TaxableItemType = None,
):
    class FakeGSTItem(GSTItem):
        @property
        def amount(self):
            return amount or amount_dm()

        @property
        def payer_states(self) -> List[str]:
            return payer_states or [uuid4_str()]

        @property
        def payee_state(self) -> str:
            return payee_state or uuid4_str()

        @property
        def item_type(self):
            return item_type or TaxableItemType.SERVICE

    return FakeGSTItem()


def income_tax_item_dm(
    amount: Amount = None,
    tax_payer: TaxPayer = None,
):
    class FakeIncomeTaxItem(IncomeTaxItem):
        @property
        def amount(self):
            return amount or amount_dm()

        @property
        def tax_payer(self) -> TaxPayer:
            return tax_payer or tax_payer_dm()

    return FakeIncomeTaxItem()
