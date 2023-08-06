from tax_module.models import TaxableItemType, PanHolderType

INDIAN_GST_RATE_CARD = {TaxableItemType.SERVICE: 5.0}


INDIAN_TDS_RATE_CARD = {
    PanHolderType.P: 0.75,
    PanHolderType.H: 0.75,
    PanHolderType.A: 1.5,
    PanHolderType.F: 1.5,
    PanHolderType.T: 1.5,
    PanHolderType.C: 1.5,
}
