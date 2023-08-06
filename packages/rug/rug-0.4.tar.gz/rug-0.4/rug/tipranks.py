import asyncio
from datetime import datetime

import httpx

from .base import BaseAPI, Data
from .exceptions import HttpException, SymbolNotFound


class TipRanks(BaseAPI):
    """
    Unofficial API wrapper class for TipRanks.com.
    Unofficial means this class calls some hidden endpoints
    and provides data that official API doesn't. Also doesn't
    need an authorization.
    """

    def get_dividends(self):
        """
        Fetches symbol dividends with following fields:

        * yield
        * amount
        * ex_date
        * payment_date
        * record_date
        * growth_since

        :return: List of dividend objects.
        :rtype: list
        """

        try:
            response = self._get(
                f"https://tr-frontend-cdn.azureedge.net/bff/prod/stock/{self.symbol.lower()}/payload.json",
            )
        except httpx.HTTPStatusError as e:
            if 404 == e.response.status_code:
                raise SymbolNotFound
            raise HttpException from e

        data = response.json()

        dividends = []

        if data["dividend"]["history"]:
            for item in data["dividend"]["history"]:
                dividends.append(
                    {
                        "yield": float(item["yield"]),
                        "amount": float(item["amount"]),
                        "ex_date": datetime.strptime(
                            item["executionDate"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).date()
                        if item["executionDate"]
                        else None,
                        "payment_date": datetime.strptime(
                            item["payDate"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).date()
                        if item["payDate"]
                        else None,
                        "record_date": datetime.strptime(
                            item["recordDate"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).date()
                        if item["recordDate"]
                        else None,
                        "growth_since": datetime.strptime(
                            item["growthSince"], "%Y-%m-%dT%H:%M:%S.000Z"
                        )
                        if item["growthSince"]
                        else None,
                    }
                )

        return dividends

    def get_basic_info(self):
        """
        Downloads basic info. Data are:

        * company_name
        * market
        * description
        * market_cap
        * has_dividends
        * yoy_change
        * year_low
        * year_high
        * pe_ratio
        * eps
        * similar_stocks
            * ticker
            * company_name

        :return: Dict with data.
        :rtype: dict
        """

        async def download_basics(symbol):
            """
            Downloads basic info about symbol. Data are:

            * company_name
            * market
            * description
            * market_cap
            * similar_stocks
                * ticker
                * company_name
            * yoy_change

            :param str symbol: Symbol the data will be downloaded for.
            :return: Dict with data.
            :rtype: dict
            """

            try:
                data = await self._aget(
                    f"https://tr-frontend-cdn.azureedge.net/bff/prod/stock/{symbol.lower()}/payload.json"
                )
            except httpx.HTTPStatusError as e:
                if 404 == e.response.status_code:
                    raise SymbolNotFound
                raise HttpException from e

            json_data = Data(data.json())
            data = {
                "company_name": json_data["common"]["stock"]["fullName"] or "",
                "market": json_data["common"]["stock"]["market"] or "",
                "description": json_data["common"]["stock"]["description"] or "",
                "has_dividends": bool(
                    json_data["common"]["stock"]["dividend"]["yield"] or None
                ),
                "yoy_change": float(
                    json_data["common"]["stock"]["technical"]["momentum"][
                        "twelveMonths"
                    ]
                    or 0.0
                )
                * 100,
                "year_low": json_data["common"]["stock"]["priceRange"]["last52Week"][
                    "low"
                ]
                or 0.0,
                "year_high": json_data["common"]["stock"]["priceRange"]["last52Week"][
                    "high"
                ]
                or 0.0,
                "pe_ratio": json_data["common"]["stock"]["pe"] or 0.0,
                "similar_stocks": [],
            }

            # Find first non-null EPS.
            for earning in json_data["common"]["earnings"] or []:
                if earning["reportedEPS"]:
                    data["eps"] = earning["reportedEPS"]
                    break

            if json_data["similar"]["similar"] or []:
                for stock in json_data["similar"]["similar"]:
                    data["similar_stocks"].append(
                        {"ticker": stock["ticker"], "company_name": stock["name"]}
                    )

            return data

        async def download_additionals(symbol):
            """
            Downloads additional info. Data are:

            * year_low
            * year_high
            * pe_ratio
            * eps
            * market_cap

            :param str symbol: Symbol the data will be downloaded for.
            :return: Dict with data.
            :rtype: dict
            """

            data = await self._aget(
                f"https://market.tipranks.com/api/details/GetRealTimeQuotes/?tickers={symbol}"
            )
            json_data = data.json()

            # Checking if symbol was even found.
            if json_data[0]["currency"] is None:
                raise SymbolNotFound

            return {
                "year_low": json_data[0]["yLow"],
                "year_high": json_data[0]["yHigh"],
                "pe_ratio": json_data[0]["pe"],
                "eps": json_data[0]["eps"],
                "market_cap": json_data[0]["marketCap"],
            }

        async def main():

            basic, additionals = await asyncio.gather(
                download_basics(self.symbol), download_additionals(self.symbol)
            )
            basic.update(additionals)

            return basic

        return asyncio.run(main())
