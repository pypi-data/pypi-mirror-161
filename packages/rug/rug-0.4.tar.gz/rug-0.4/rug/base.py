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


class Data(dict):
    """
    Dict substitution which recursivelly handles
    non-existing keys.
    """

    def __getitem__(self, key):

        try:
            data = super().__getitem__(key)

            # If the data is dict we need to wrap it with
            # this class so it will carry this logic.
            if type(data) == dict:
                return self.__class__(data)

            # Data is not a dict so we return what we found.
            return data
        except:

            # In case of non existing key we return empty self
            # which makes sure another direct key demand will
            # copy this logic.
            return self.__class__()
