import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from itertools import zip_longest

from .base import BaseAPI
from .exceptions import DataException, HttpException


class AlphaQuery(BaseAPI):
    """
    AlphaQuery.com
    """

    class HtmlTableParser(HTMLParser):
        """
        Parses out all data from the given table and
        casts them into ``datetime.date`` or ``float``.

        Parsed data can be retrieved with ``get_data()`` method.
        """

        def __init__(self, columns, *args, **kwargs):
            """
            Constructor.

            :param int columns: Number of columns the given table has.
            """

            self.data = []
            self.columns = columns
            super().__init__(*args, **kwargs)

        def handle_data(self, data):

            if data := data.strip():
                self.data.append(self.parse_data(data))

        def parse_data(self, data):
            """
            Parses out all data from the given table and
            casts them into ``datetime.date`` or ``float``.
            """

            # Date in YYYY-MM-DD format.
            if re.match("\d{4}-\d{2}-\d{2}", data):
                return date.fromisoformat(data)

            # Dollars (positive or negative floats).
            if re.match("^\$[+-]?([0-9]*[.])?[0-9]+$", data):
                return float(data[1:])

            if "--" == data:
                return 0.0

            return data

        def get_data(self):
            """
            Splits data into ``self.columns`` list of lists
            and returns them.
            Rows are sorted chronologically.

            :return: Parsed, casted table data as rows.
            :rtype: list
            """

            data = list(zip_longest(*[iter(self.data)] * self.columns, fillvalue=""))
            sorted_data = sorted(
                data[1:],
                key=lambda row: row[0],
            )
            sorted_data.insert(0, data[0])

            return sorted_data

    def get_earnings(self):
        """
        Returns earnings for the given ``self.symbol`` as table rows
        (list of lists) where first row is table headers for comprehension.
        Rows are sorted chronologically.

        :return: List of lists with earnings.
        :rtype: list
        """

        # Get HTML.
        try:
            html = self._get(
                f"https://www.alphaquery.com/stock/{self.symbol.upper()}/earnings-history"
            )
        except Exception as e:
            raise HttpException from e

        finds = re.findall("<table.*?>.*?</table>", html.text, re.DOTALL)

        # Check if the HTML contains only one table.
        if 1 != len(finds):
            raise DataException(
                "More that one table found in HTML - don't know what to do now"
            )

        parser = self.HtmlTableParser(columns=4)
        parser.feed(finds[0])

        return parser.get_data()

    def get_revenues(self):
        """
        Returns revenues as time went in a list of tuples
        where first is a date and the second is revenue value.

        :return: List of revenues including dates.
        ;rtype: list
        """

        # 1. fetch data.
        json_data = self._get_chart_data(
            f"https://www.alphaquery.com/stock/{self.symbol.upper()}/fundamentals/quarterly/revenue"
        )

        # 2. process data.
        if json_data:
            return list(
                map(
                    lambda i: (
                        datetime.strptime(i["x"], "%Y-%m-%dT%H:%M:%SZ").date(),
                        float(i["value"] or 0.0),
                    ),
                    json_data,
                )
            )

    def _get_chart_data(self, url):

        response = self._get(
            "https://www.alphaquery.com/stock/NIO/fundamentals/quarterly/revenue"
        )
        finds = re.findall(
            "var chartIndicatorData = (.+?)var", response.text, re.DOTALL
        )

        if finds:
            try:
                return json.loads(finds[0])
            except Exception as e:
                raise DataException from e
