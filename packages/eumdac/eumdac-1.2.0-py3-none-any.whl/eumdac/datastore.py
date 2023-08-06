from __future__ import annotations
from .__version__ import __title__, __documentation__, __version__  # noqa

import requests

from eumdac.collection import Collection
from eumdac.product import Product
from eumdac.subscription import Subscription
from eumdac.token import AccessToken, URLs

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import sys
    from typing import Optional

    if sys.version_info < (3, 9):
        from typing import Mapping, Iterable
    else:
        from collections.abc import Mapping, Iterable


class DataStore:
    token: AccessToken
    urls: URLs
    _collections: Mapping[str, Collection]

    def __init__(self, token: AccessToken) -> None:
        self.token = token
        self.urls = token.urls
        self._collections = {}

    def _load_collections(self) -> None:
        if self._collections:
            return
        url = self.urls.get("datastore", "browse collections")
        response = requests.get(
            url,
            params={"format": "json"},
            auth=self.token.auth,
            headers={
                "referer": __documentation__,
                "User-Agent": str(__title__ + "/" + __version__),
            },
        )
        response.raise_for_status()
        collection_ids = [item["title"] for item in response.json()["links"]]
        self._collections = {
            collection_id: Collection(collection_id, self) for collection_id in collection_ids
        }

    @property
    def collections(self) -> Iterable[Collection]:
        self._load_collections()
        return list(self._collections.values())

    @property
    def subscriptions(self) -> Iterable[Subscription]:
        url = self.urls.get("datastore", "subscriptions")
        response = requests.get(
            url,
            auth=self.token.auth,
            headers={
                "referer": __documentation__,
                "User-Agent": str(__title__ + "/" + __version__),
            },
        )
        response.raise_for_status()
        return [Subscription(properties["uuid"], self) for properties in response.json()]

    def get_collection(self, collection_id: str) -> Collection:
        """collection factory"""
        self._load_collections()
        try:
            return self._collections[collection_id]
        except KeyError as error:
            raise KeyError(f"unknown collection {collection_id}") from error

    def get_product(self, collection_id: str, product_id: str) -> Product:
        """product factory"""
        return Product(collection_id, product_id, self)

    def get_subscription(self, subscription_id: str) -> Subscription:
        """subscription factory"""
        return Subscription(subscription_id, self)

    def new_subscription(
        self, collection: Collection, url: str, area_of_interest: Optional[str] = None
    ) -> Subscription:
        """create new subscription"""
        parameters = {"collectionId": collection._id, "url": url}
        if area_of_interest is not None:
            parameters["aoi"] = area_of_interest
        subscriptions_url = self.urls.get("datastore", "subscriptions")
        response = requests.post(subscriptions_url, json=parameters, auth=self.token.auth)
        response.raise_for_status()
        subscription_id = response.json()
        return Subscription(subscription_id, self)
