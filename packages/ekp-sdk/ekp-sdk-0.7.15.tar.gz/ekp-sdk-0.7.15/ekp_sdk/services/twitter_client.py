from ekp_sdk.services.limiter import Limiter
from ekp_sdk.services.rest_client import RestClient


class TwitterClient:
    def __init__(
        self,
        rest_client: RestClient,
        auth_token: str,
    ):
        self.auth_token = auth_token
        self.rest_client = rest_client
        self.limiter = Limiter(1000, 1)
        self.base_url = "https://api.twitter.com/1.1"

    async def get_user_info_by_screen_name(self, screen_name):

        def fn(data, text, response):
            return None if response.status in [404,403] else data
        
        url = f"{self.base_url}/users/show.json?screen_name={screen_name}"
        
        return await self.__get(url, fn=fn, allowed_response_codes=[200,404, 403])

    async def __get(self, url, fn=lambda data, text, response: data, allowed_response_codes=[200]):
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        result = await self.rest_client.get(
            url,
            fn,
            limiter=self.limiter,
            headers=headers,
            allowed_response_codes=allowed_response_codes
        )

        return result
