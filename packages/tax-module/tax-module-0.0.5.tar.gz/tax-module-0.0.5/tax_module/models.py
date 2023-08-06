from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


class AmountType(Enum):
    TAX_INCLUSIVE = "TAX_INCLUSIVE"
    TAX_EXCLUSIVE = "TAX_EXCLUSIVE"

    def __str__(self):
        return self.value


class TaxableItemType(Enum):
    GOOD = "GOOD"
    SERVICE = "SERVICE"

    def __str__(self):
        return self.value


class PanHolderType(Enum):
    P = "INDIVIDUAL"
    C = "COMPANY"
    A = "ASSOCIATION"
    F = "FIRM"
    H = "HUF"
    T = "TRUST"

    def __str__(self):
        return self.value


class TaxType(Enum):
    CGST = "CGST"
    SGST = "SGST"
    IGST = "IGST"
    TDS = "TDS"

    def __str__(self):
        return self.value


class TransactionType(Enum):
    INTER_STATE = "INTER_STATE"
    INTRA_STATE = "INTRA_STATE"

    def __str__(self):
        return self.value


@dataclass
class Amount:
    value: int
    type: AmountType

    @property
    def is_tax_inclusive(self):
        return self.type == AmountType.TAX_INCLUSIVE


@dataclass
class Tax:
    percentage: float
    type: TaxType


@dataclass
class TaxPayer:
    pan_card: str

    @property
    def pan_holder_type(self) -> PanHolderType:
        type = self.pan_card[3]
        return PanHolderType[type]


class TaxableItem(ABC):
    @property
    @abstractmethod
    def amount(self) -> Amount:
        pass


class GSTItem(TaxableItem):
    @property
    @abstractmethod
    def payer_states(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def payee_state(self) -> str:
        pass

    @property
    @abstractmethod
    def item_type(self) -> str:
        pass

    @property
    def transaction_type(self) -> TransactionType:
        if self.payee_state in self.payer_states:
            return TransactionType.INTRA_STATE

        return TransactionType.INTER_STATE


class IncomeTaxItem(TaxableItem):
    @property
    @abstractmethod
    def tax_payer(self) -> TaxPayer:
        pass

    @property
    def pan_holder_type(self) -> PanHolderType:
        return self.tax_payer.pan_holder_type


@dataclass
class AppliedTax:
    tax: Tax
    amount: float

    @classmethod
    def from_taxable_amount(cls, tax: Tax, taxable_amount: Amount, sum_of_taxes: float):
        tax_exclusive_amount = (
            (taxable_amount.value * 100 / (100 + sum_of_taxes))
            if taxable_amount.is_tax_inclusive
            else taxable_amount.value
        )
        return cls(
            amount=round((tax_exclusive_amount * tax.percentage) / 100, 2),
            tax=tax,
        )

    @classmethod
    def from_dict(cls, dikt: dict):
        return cls(
            amount=dikt["amount"],
            tax=Tax(
                percentage=dikt["tax"]["percentage"], type=TaxType(dikt["tax"]["type"])
            ),
        )
