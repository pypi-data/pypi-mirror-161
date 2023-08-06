# Rug

Universal library for fetching Stock data from the internet - mostly unofficial
APIs - no limits, more free data.

(for Cryptocurrency alternative see [karpet](https://github.com/im-n1/karpet))

* [PyPI](https://pypi.org/project/rug/)
* [documentation](https://rug.readthedocs.io/en/latest/) ![Documentation Status](https://readthedocs.org/projects/rug/badge/?version=latest)

## Changelog

### 0.3

- new provider AlphaQuery.com
- updated imports and class names - now it's i.e. `from rug import Yahoo`

### 0.2.11

- minor fixes

### 0.2.10

- minor fixes

### 0.2.9

- `yahoo.UnofficialAPI.get_current_price()` renamed to `get_current_price_change()`

### 0.2.8

- Added: ex-date is back for dividends

### 0.2.7

- Updated: better dividends handling (i.e. missing data)

### 0.2.6

- Added: exception handling

### 0.2.5

- Fixed TipTanks API - basic info for companies with no dividends

### 0.2.4

- Fixed TipRanks API - dividends for companies with no dividends

### 0.2.3

- Fixed TipRanks API - all methods

### 0.2.2

* Minor fixes.

### 0.2.1

Method `rug.yahoo.UnofficialAPI.get_current_price()` returns market state now.

### 0.2

New portals added: YAHOO! + StockTwits

* `get_current_price()` method added
* `get_earnings_calendar` method added

### 0.1.2
* `get_dividends()` now returns dividend `amount` too

### 0.1.1
* dates are now `datetime.date` instance

### 0.1
* initial release
