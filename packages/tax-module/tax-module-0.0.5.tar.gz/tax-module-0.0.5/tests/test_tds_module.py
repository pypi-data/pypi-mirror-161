import pytest

from tax_module.errors import TDSRateNotAvailable
from tax_module.indian_tax import INDIAN_TDS_RATE_CARD
from tax_module.models import TaxType, AmountType
from tax_module.tds import TDSModule
from tests.factories import amount_dm, income_tax_item_dm, tax_payer_dm


class TestCalculateTDS:
    def test_tds_module_calculates_tds_on_tax_exclusive_amount_with_individual_pan_holder_type(
        self,
    ):
        fake_rate_card = INDIAN_TDS_RATE_CARD

        tds_module = TDSModule(rate_card=fake_rate_card)
        taxable_item = income_tax_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_EXCLUSIVE),
            tax_payer=tax_payer_dm(pan_card="ABCPY1234K"),
        )
        applied_taxes = tds_module.calculate_taxes(taxable_item)

        assert len(applied_taxes) == 1

        assert {TaxType.TDS} == {applied_tax.tax.type for applied_tax in applied_taxes}

        assert {0.75} == {applied_tax.tax.percentage for applied_tax in applied_taxes}
        assert {7.5} == {applied_tax.amount for applied_tax in applied_taxes}

    def test_tds_module_calculates_tds_on_tax_inclusive_amount_with_individual_pan_holder_type(
        self,
    ):
        fake_rate_card = INDIAN_TDS_RATE_CARD

        tds_module = TDSModule(rate_card=fake_rate_card)
        taxable_item = income_tax_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_INCLUSIVE),
            tax_payer=tax_payer_dm(pan_card="ABCPY1234K"),
        )
        applied_taxes = tds_module.calculate_taxes(taxable_item)

        assert len(applied_taxes) == 1

        assert {TaxType.TDS} == {applied_tax.tax.type for applied_tax in applied_taxes}

        assert {0.75} == {applied_tax.tax.percentage for applied_tax in applied_taxes}
        assert {7.44} == {applied_tax.amount for applied_tax in applied_taxes}

    def test_tds_module_raises_error_when_tds_rate_card_not_provided(self):
        fake_rate_card = {}

        tds_module = TDSModule(rate_card=fake_rate_card)
        taxable_item = income_tax_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_INCLUSIVE),
            tax_payer=tax_payer_dm(pan_card="ABCPY1234K"),
        )

        with pytest.raises(TDSRateNotAvailable):
            tds_module.calculate_taxes(taxable_item)
