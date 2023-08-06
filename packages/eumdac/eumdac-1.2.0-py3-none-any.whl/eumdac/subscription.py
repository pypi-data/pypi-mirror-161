from __future__ import annotations
from .__version__ import __title__, __documentation__, __version__  # noqa

import time

import requests

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import sys
    from typing import Any
    from eumdac.datastore import DataStore
    from eumdac.collection import Collection

    if sys.version_info < (3, 9):
        from typing import Mapping
    else:
        from collections.abc import Mapping


class Subscription:
    _id: str
    datastore: DataStore
    _last_update: float
    _properties: Mapping[str, Any]
    update_margin: int = 5  # seconds

    def __init__(self, subscription_id: str, datastore: DataStore) -> None:
        self._id = subscription_id
        self.datastore = datastore
        # lazy load properties
        self._last_update = 0
        self._properties = {}

    def __str__(self) -> str:
        return self._id

    def __repr__(self) -> str:
        return f"{self.__class__}({self._id})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Subscription) and self._id == other._id

    def _update_properties(self) -> None:
        now = time.time()
        expired = now - self._last_update > self.update_margin
        if expired:
            url = self.datastore.urls.get(
                "datastore", "subscription", vars={"subscription_id": self._id}
            )
            response = requests.get(
                url,
                auth=self.datastore.token.auth,
                headers={
                    "referer": __documentation__,
                    "User-Agent": str(__title__ + "/" + __version__),
                },
            )
            response.raise_for_status()
            self._properties = response.json()
            self._last_update = now

    @property
    def url(self) -> str:
        self._update_properties()
        return self._properties["url"]

    @property
    def collection(self) -> Collection:
        self._update_properties()
        collection_id = self._properties["collectionId"]
        return self.datastore.get_collection(collection_id)

    @property
    def area_of_interest(self) -> Any:
        self._update_properties()
        return self._properties["aoi"]

    @property
    def status(self) -> str:
        self._update_properties()
        return self._properties["status"]

    def delete(self) -> None:
        url = self.datastore.urls.get(
            "datastore", "subscription", vars={"subscription_id": self._id}
        )
        response = requests.delete(url, auth=self.datastore.token.auth)
        response.raise_for_status()
