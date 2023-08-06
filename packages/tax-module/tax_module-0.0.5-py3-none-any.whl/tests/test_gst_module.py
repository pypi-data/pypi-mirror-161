import pytest

from tax_module.errors import GSTRateNotAvailable
from tax_module.gst import GSTModule
from tax_module.models import TaxableItemType, TaxType, AmountType
from tests.factories import gst_item_dm, amount_dm


class TestCalculateGSTWithSamePayerPayeeStates:
    def test_gst_module_calculates_cgst_and_sgst_on_tax_exclusive_amount(self):
        fake_rate_card = {TaxableItemType.SERVICE: 5}

        gst_module = GSTModule(rate_card=fake_rate_card)
        taxable_item = gst_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_EXCLUSIVE),
            payer_states=["ABC"],
            payee_state="ABC",
            item_type=TaxableItemType.SERVICE,
        )
        applied_taxes = gst_module.calculate_taxes(taxable_item)

        assert len(applied_taxes) == 2

        assert {TaxType.CGST, TaxType.SGST} == {
            applied_tax.tax.type for applied_tax in applied_taxes
        }

        assert {2.5, 2.5} == {
            applied_tax.tax.percentage for applied_tax in applied_taxes
        }
        assert {25, 25} == {applied_tax.amount for applied_tax in applied_taxes}

    def test_gst_module_calculates_cgst_and_sgst_on_tax_inclusive_amount(self):
        fake_rate_card = {TaxableItemType.SERVICE: 5}

        gst_module = GSTModule(rate_card=fake_rate_card)
        taxable_item = gst_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_INCLUSIVE),
            payer_states=["ABC"],
            payee_state="ABC",
            item_type=TaxableItemType.SERVICE,
        )
        applied_taxes = gst_module.calculate_taxes(taxable_item)

        assert len(applied_taxes) == 2

        assert {TaxType.CGST, TaxType.SGST} == {
            applied_tax.tax.type for applied_tax in applied_taxes
        }

        assert {2.5, 2.5} == {
            applied_tax.tax.percentage for applied_tax in applied_taxes
        }
        assert {23.81, 23.81} == {applied_tax.amount for applied_tax in applied_taxes}


class TestCalculateGSTWithDifferentPayerPayeeStates:
    def test_gst_module_calculates_only_igst(self):
        fake_rate_card = {TaxableItemType.SERVICE: 5}

        gst_module = GSTModule(rate_card=fake_rate_card)
        taxable_item = gst_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_EXCLUSIVE),
            payer_states=["ABC"],
            payee_state="DEF",
            item_type=TaxableItemType.SERVICE,
        )
        applied_taxes = gst_module.calculate_taxes(taxable_item)

        assert len(applied_taxes) == 1

        assert {TaxType.IGST} == {applied_tax.tax.type for applied_tax in applied_taxes}
        assert {5} == {applied_tax.tax.percentage for applied_tax in applied_taxes}
        assert {50} == {applied_tax.amount for applied_tax in applied_taxes}

    def test_gst_module_raises_error_when_gst_rate_not_available(self):
        fake_rate_card = {}

        gst_module = GSTModule(rate_card=fake_rate_card)
        taxable_item = gst_item_dm(
            amount=amount_dm(amount=1000, type=AmountType.TAX_EXCLUSIVE),
            payer_states=["ABC"],
            payee_state="DEF",
            item_type=TaxableItemType.SERVICE,
        )

        with pytest.raises(GSTRateNotAvailable):
            gst_module.calculate_taxes(taxable_item)
