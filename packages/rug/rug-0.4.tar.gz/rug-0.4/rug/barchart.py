import html
import json
import re

from .base import BaseAPI
from .exceptions import HttpException


class BarChart(BaseAPI):
    def get_ratings(self):
        """
        Returns ratings for past 4 months.
        Each months is a dict with status and it's values
        where values are in absolute number (number of analyst)
        and percents (ratio).

        Returns data in format:

        .. code-block:: json

            [
                {
                    "Strong Buy":{
                        "value":"14",
                        "percent":60.86956521739131
                    },
                    "Hold":{
                        "value":"9",
                        "percent":39.130434782608695
                    }
                },
                {
                    "Strong Buy":{
                        "value":"15",
                        "percent":65.21739130434783
                    },
                    "Hold":{
                        "value":"8",
                        "percent":34.78260869565217
                    }
                },
                {
                    "Strong Buy":{
                        "value":"15",
                        "percent":62.5
                    },
                    "Moderate Buy":{
                        "value":"1",
                        "percent":4.166666666666666
                    },
                    "Hold":{
                        "value":"8",
                        "percent":33.33333333333333
                    }
                },
                {
                    "Strong Buy":{
                        "value":"17",
                        "percent":73.91304347826086
                    },
                    "Moderate Buy":{
                        "value":"1",
                        "percent":4.3478260869565215
                    },
                    "Hold":{
                        "value":"5",
                        "percent":21.73913043478261
                    }
                }
            ]

        :return: List of each month data.
        :rtype: list
        """

        try:
            response = self._get(
                f"https://www.barchart.com/stocks/quotes/{self.symbol.upper()}/analyst-ratings"
            )
        except Exception as e:
            raise HttpException from e

        finds = re.findall(
            '<analyst-rating-pie[^>]*data-content="([^"]+)"',
            response.text,
            re.DOTALL,
        )

        if finds:
            return [json.loads(html.unescape(find)) for find in finds]

        return []
