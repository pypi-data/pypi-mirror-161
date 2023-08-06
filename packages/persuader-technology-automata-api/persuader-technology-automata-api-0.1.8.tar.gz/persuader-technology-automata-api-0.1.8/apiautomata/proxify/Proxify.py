import aiohttp
from coreutility.date_utility import get_utc_timestamp


class Proxify:

    def __init__(self, url):
        self.url = url
        self.status = None
        self.instant = get_utc_timestamp()

    @classmethod
    async def get_end_point_status(cls, obj):
        async with aiohttp.ClientSession() as session:
            async with session.get(obj.url) as response:
                response_status = response.status
                obj.status = response_status
