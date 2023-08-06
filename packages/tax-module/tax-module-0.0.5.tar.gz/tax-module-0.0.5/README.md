# tax-module
This module will take care of taxation related logic of Shuttl Platform. 

<!-- Use markdown-toc to build the following section -->

<!-- toc -->

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Running Tests](#running-tests)
- [Releasing](#releasing)

<!-- tocstop -->

## Installation

`pip install tax-module`

## Basic Usage


```python
from tax_module import GSTModule
from tax_module.indian_tax import INDIAN_GST_RATE_CARD
from tax_module.models import GSTItem

rate_card = INDIAN_GST_RATE_CARD or {} # use existing rate card or pass in rate_card of your choice

gst_module = GSTModule(rate_card=rate_card)

class SomeTaxableItem(GSTItem):
    pass # Implement all abstract methods of GSTItem


taxes = gst_module.calculate_taxes(
    taxable_item=SomeTaxableItem
)
```

## Future Prospects for Rate Card

Currently, we don't have proper categorisation of taxable items. We only have two basic categories - `Service` and `Good`.
In future, We are planning to introduce Taxable Item category and subcategory based on which gst rate will differ and it will closely resonate with real taxation system. 

## Running Tests

- pip install ".[test]"
- pytest

## Releasing

- `make bump_patch_version`
- Update [the Changelog](https://github.com/Shuttl-Tech/tax-module/blob/master/Changelog.md)
- Commit changes to `Changelog`, `setup.py` and `setup.cfg`.
- `make release` (this'll push a tag that will trigger a Drone build)