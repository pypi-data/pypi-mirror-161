import httpx


class BaseAPI:

    timeout = 10

    def __init__(self, symbol=None):
        """
        Constructor.

        :param str symbol: Symbol of te item we wanna get info about.
        """

        if symbol:
            self.symbol = str(symbol)

    def _get(self, *args):
        """
        TBD
        """

        try:
            response = httpx.get(*args, timeout=self.timeout)
        except Exception as exc:
            raise HttpException(
                f"Couldn't perform GET request with args {args}"
            ) from exc

        response.raise_for_status()

        return response

    async def _aget(self, *args):

        async with httpx.AsyncClient() as client:

            try:
                response = await client.get(*args, timeout=self.timeout)
            except Exception as exc:
                raise HttpException(
                    f"Couldn't perform GET request with args {args}"
                ) from exc

            response.raise_for_status()

            return response
