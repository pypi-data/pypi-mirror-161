import asyncio
import os
import time

import aiohttp
from dotenv import load_dotenv

from getwowdata.urls import urls
from getwowdata.helpers import *


class WowApi:
    @classmethod
    async def create(cls, region: str):
        """Gets an instance of WowApi with an access token, region, and aiohttp session.

        Args:
            region (str): Each region has its own data. This specifies which regions data
                WoWApi will consume.
        Returns:
            An instance of the WowApi class.
        """
        self = WowApi()
        self.region = region
        timeout = aiohttp.ClientTimeout(connect=5, sock_read=60, sock_connect=5)
        self.session = aiohttp.ClientSession(raise_for_status=True, timeout=timeout)
        await self._get_access_token()
        return self

    async def _get_access_token(
        self, wow_api_id: str = None, wow_api_secret: str = None, retries: int = 5
    ) -> None:
        """Retrieves battle.net client id and secret from env and makes it an attribute.

        Args:
            wow_api_id (str): The id from a battle.net api client.
            wow_api_secret (str): The secret from a battle.net api client.
            retries (int): The number of times the request will be retried on failure.
        """
        load_dotenv()
        id = os.environ["wow_api_id"]
        secret = os.environ["wow_api_secret"]
        token_data = {"grant_type": "client_credentials"}
        wow_api_id = wow_api_id
        wow_api_secret = wow_api_secret

        for retry in range(retries):
            try:
                async with self.session.post(
                    urls["access_token"].format(region=self.region),
                    auth=aiohttp.BasicAuth(id, secret),
                    data=token_data,
                ) as response:
                    response = await response.json()
                    self.access_token = response["access_token"]
                    break
            except aiohttp.ClientConnectionError as e:
                print(f"access token {e}")
            except aiohttp.ClientResponseError as e:
                print(f"access token {e.status}")

    async def _fetch_get(self, url_name: str, ids: dict = {}, retries: int = 5) -> dict:
        """Preforms a aiohttp get request for the given url_name from urls.py. Accepts ids for get methods.

        Args:
            url_name (str): The name of a url from urls.py
            ids (dict): The ids that need to be send with the revelant url_name.
                Such as some item_id.
            retries (int): The number of times the request will be retried on failure.

        Returns:
            The content from an endpoint as binary or a dict depending if the request
            was made for an icon or json data, respectively.
        """
        params = {
            **{
                "access_token": self.access_token,
                "namespace": f"dynamic-{self.region}",
            }
        }
        if url_name in [
            "repice_icon", "profession_icon", "item_icon", 
            "profession_index", "profession_skill_tier",
            "profession_tier_detail", "profession_icon",
            "recipe_detail", "repice_icon", "item_classes",
            "item_subclass", "item_set_index", "item_icon"
            ]:
            params = {
                **{
                    "access_token": self.access_token,
                    "namespace": f"static-{self.region}",
                }
            }

        for retry in range(retries):
            try:
                async with self.session.get(
                    urls[url_name].format(region=self.region, **ids), params=params
                ) as response:
                    json = await response.json()
                    json["Date"] = response.headers["Date"]
                    return json

            except aiohttp.ClientConnectionError as e:
                print(f"get {e}")

            except aiohttp.ClientResponseError as e:
                print(f"get {e.status}")

    async def _fetch_search(
        self, url_name: str, extra_params: dict, retries: int = 5
    ) -> dict:
        """Preforms a aiohttp get request for the given url_name from urls.py. Accepts extra_params for search methods.

        Args:
            url_name (str): The name of a url from urls.py
            extra_params (dict): Parameters for refining a search request.
                See https://develop.battle.net/documentation/world-of-warcraft/guides/search
            retries (int): The number of times the request will be retried on failure.

        Returns:
            The search results json parsed into a dict.
        """
        params = {
            "access_token": self.access_token,
            "namespace": f"static-{self.region}",
        }

        if url_name == 'search_realm':
            params = {
            "access_token": self.access_token,
            "namespace": f"dynamic-{self.region}",
        }

        search_params = {
            **params,
            **extra_params,
        }

        for retry in range(retries):
            try:
                async with self.session.get(
                    urls[url_name].format(region=self.region), params=search_params
                ) as response:
                    json = await response.json()
                    if url_name == "search_item":
                        tasks = []
                        if json.get("results"):
                            for item in json["results"]:
                                task = asyncio.create_task(
                                    self._get_item(item["key"]["href"], params=params)
                                )
                                tasks.append(task)
                        items = await asyncio.gather(*tasks)
                        json = {}
                        json["items"] = items
                    json["Date"] = response.headers["Date"]
                    return json

            except aiohttp.ClientConnectionError as e:
                print(f"search {e}")
            except aiohttp.ClientResponseError as e:
                print(f"search {e.status}")

    async def _get_item(self, url: str, params: dict) -> dict:
        """Preforms a get request for an item inside an item search.

        This is a general session.get() but it is currently used in item_search()
        to get detailed item data from the href's in the search results.

        Args:
            url (str): The url to query.
            params (dict): The parameters needed for a successful query.
                Such as access token and namespace.

        Returns:
            The json response from the url as a dict.
        """
        for retry in range(5):
            try:
                async with self.session.get(url, params=params) as item_data:
                    item = await item_data.json(content_type=None)
                    return item
            except aiohttp.ClientConnectionError as e:
                print(f"item {e}")
            except aiohttp.ClientResponseError as e:
                print(e.status)

    async def connected_realm_search(self, **extra_params: dict) -> dict:
        """Preforms a search of all realms in that region.

        Args:
            extra_params (dict): Parameters for refining a search request.
                See https://develop.battle.net/documentation/world-of-warcraft/guides/search
            retries (int): The number of times the request will be retried on failure.

        Returns:
            The search results as json parsed into a dict.
        """
        url_name = "search_realm"
        return await self._fetch_search(url_name, extra_params=extra_params)

    async def item_search(self, **extra_params: dict) -> dict:
        """Preforms a search of all items.

        Args:
            extra_params (dict): Parameters for refining a search request.
                See https://develop.battle.net/documentation/world-of-warcraft/guides/search
            retries (int): The number of times the request will be retried on failure.

        Returns:
            The search results as json parsed into a dict.
        """
        url_name = "search_item"
        return await self._fetch_search(url_name, extra_params=extra_params)

    async def get_connected_realms_by_id(self, connected_realm_id: int) -> dict:
        """Returns the all realms in a connected realm by their connected realm id.

        Args:
            connected_realm_id (int):
                The id of a connected realm cluster.
        """
        url_name = "realm"
        ids = {"connected_realm_id": connected_realm_id}
        return await self._fetch_get(url_name, ids)

    async def get_auctions(self, connected_realm_id) -> dict:
        """Returns the all auctions in a connected realm by their connected realm id.

        Args:
            connected_realm_id (int):
                The id of a connected realm cluster.
        """
        url_name = "auction"
        ids = {"connected_realm_id": connected_realm_id}
        return await self._fetch_get(url_name, ids)

    async def get_profession_index(self) -> dict:
        """Returns the all professions."""
        url_name = "profession_index"
        return await self._fetch_get(url_name)

    async def get_profession_tiers(self, profession_id: int) -> dict:
        """Returns the all profession skill tiers in a profession by their profession id.

        A profession teir includes all the recipes from that expansion.
        Teir examples are classic, tbc, shadowlands, ...

        Args:
            profession_id (int):
                The id of a profession. Get from get_profession_index().
        """
        url_name = "profession_skill_tier"
        ids = {"profession_id": profession_id}
        return await self._fetch_get(url_name, ids)

    async def get_profession_icon(self, profession_id: int) -> dict:
        """Returns json with a link to a professions icon.

        Args:
            profession_id (int): The id of a profession. Get from get_profession_index.
        """
        url_name = "profession_icon"
        ids = {"profession_id": profession_id}
        return await self._fetch_get(url_name, ids)

    async def get_profession_tier_categories(
        self, profession_id: int, skill_tier_id: int
    ) -> dict:
        """Returns all crafts from a skill teir.

        Included in this response are the categories like belts, capes, ... and the item within them.
        This is broken down by skill tier (tbc, draenor, shadowlands).

        Args:
            profession_id (int): The profession's id. Found in get_profession_index().
            skill_tier_id (int): The skill teir id. Found in get_profession_teirs().
        """
        url_name = "profession_tier_detail"
        ids = {"profession_id": profession_id, "skill_tier_id": skill_tier_id}
        return await self._fetch_get(url_name, ids)

    async def get_recipe(self, recipe_id: int) -> dict:
        """Returns a recipe by its id.

        Args:
            recipe_id (int): The id from a recipe. Found in get_profession_tier_details().
        """
        url_name = "recipe_detail"
        ids = {"recipe_id": recipe_id}
        return await self._fetch_get(url_name, ids)

    async def get_recipe_icon(self, recipe_id: int) -> dict:
        """Returns a dict with a link to a recipes icon.

        Args:
            recipe_id (int): The id from a recipe. Found in get_profession_tier_details().
        """
        url_name = "repice_icon"
        ids = {"recipe_id": recipe_id}
        return await self._fetch_get(url_name, ids)

    async def get_item_classes(self) -> dict:
        """Returns all item classes (consumable, container, weapon, ...)."""
        url_name = "item_classes"
        return await self._fetch_get(url_name)

    async def get_item_subclasses(self, item_class_id: int) -> dict:
        """Returns all item subclasses (class: consumable, subclass: potion, elixir, ...).

        Args:
            item_class_id (int): Item class id. Found with get_item_classes().
        """
        url_name = "item_subclass"
        ids = {"item_class_id": item_class_id}
        return await self._fetch_get(url_name, ids)

    async def get_item_set_index(self) -> dict:
        """Returns all item sets. Ex: teir sets"""
        url_name = "item_set_index"
        return await self._fetch_get(url_name)

    async def get_item_icon(self, item_id: int) -> dict:
        """Returns a dict with a link to an item's icon.

        Args:
            item_id (int): The items id. Get from item_search().
        """
        url_name = "item_icon"
        ids = {"item_id": item_id}
        return await self._fetch_get(url_name, ids)

    async def get_wow_token(self) -> dict:
        """Returns data on the regions wow token such as price."""
        url_name = "wow_token"
        return await self._fetch_get(url_name)

    # TODO
    async def get_connected_realm_index(self) -> dict:
        """Returns a dict of all realm's names with their connected realm id."""
        pass

    async def close(self):
        """Closes aiohttp.ClientSession."""
        await self.session.close()


async def main():
    from pprint import pprint

    for i in range(1):
        us = await WowApi.create("us")
        start = time.time()
        json = await us.get_wow_token()
        pprint(json)
        end = time.time()
        print(end - start)
        await us.close()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
