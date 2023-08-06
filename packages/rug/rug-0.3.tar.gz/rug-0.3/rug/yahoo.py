import httpx

from .base import BaseAPI
from .exceptions import HttpException, RugException, SymbolNotFound


class Yahoo(BaseAPI):
    def get_current_price_change(self):
        """
        Fetches current market price inc. pre/post market
        prices/percent/value changes. Also returns current
        market state (pre-market, open, post-market, closed).

        Fetched stucture has following fields:

        * state (pre-market, open, post-market, closed)
        * pre_market
            * change
                * percents
                * value
            * value
        * current_market
            * change
                * percents
                * value
            * value
        * post_market
            * change
                * percents
                * value
            * value

        Returned dict looks like:

        .. code-block:: python

            {
                "state": "open",
                "pre_market": {
                    "change": {
                        "percents": -1.32476,
                        "value": -1.42001
                    },
                    "value": 105.77
                },
                "current_market": {
                    "change": {
                        "percents": -1.6046284000000002,
                        "value": -1.7200012
                    },
                    "value": 105.47
                },
                "post_market": {
                    "change": {
                        "percents": 0.0,
                        "value": 0.0
                    },
                    "value": 0.0
                }
            }

        :return: Current/Pre/Post market numbers (all are floats).
        :rtype: dict
        """

        def parse_state(state):

            # No state at all.
            if not state:
                return None

            state = state.lower()

            if state.startswith("pre"):
                return "pre-market"

            if state.startswith("post"):
                return "post-market"

            if "closed" == state:
                return "closed"

            if state in ("regular", "open"):
                return "open"

            raise RugException("Unknown market state")

        try:
            response = self._get(
                f"https://query1.finance.yahoo.com/v11/finance/quoteSummary/{self.symbol}?modules=price"
            )
        except httpx.HTTPStatusError as e:
            if 404 == e.response.status_code:
                raise SymbolNotFound
            raise HttpException from e

        data = response.json()
        data = data["quoteSummary"]["result"][0]["price"]

        return {
            "state": parse_state(data.get("marketState")),
            "pre_market": {
                "change": {
                    "percents": float(
                        data.get("preMarketChangePercent", {}).get("raw", 0)
                    )
                    * 100,
                    "value": float(data.get("preMarketChange", {}).get("raw", 0)),
                },
                "value": float(data.get("preMarketPrice", {}).get("raw", 0)),
            },
            "current_market": {
                "change": {
                    "percents": float(
                        data.get("regularMarketChangePercent", {}).get("raw", 0)
                    )
                    * 100,
                    "value": float(data.get("regularMarketChange", {}).get("raw", 0)),
                },
                "value": float(data.get("regularMarketPrice", {}).get("raw", 0)),
            },
            "post_market": {
                "change": {
                    "percents": float(
                        data.get("postMarketChangePercent", {}).get("raw", 0)
                    )
                    * 100,
                    "value": float(data.get("postMarketChange", {}).get("raw", 0)),
                },
                "value": float(data.get("postMarketPrice", {}).get("raw", 0)),
            },
        }
