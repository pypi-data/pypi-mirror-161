"""This module contains classes to interact with customisations"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from collections.abc import Mapping

import requests

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import sys
    from typing import Any, Type, Optional, Union

    if sys.version_info < (3, 9):
        from typing import MutableMapping, Sequence
    else:
        from collections.abc import MutableMapping, Sequence
    from eumdac.datatailor import DataTailor


def _none_filter(*args: Any, **kwargs: Any) -> MutableMapping[str, Any]:
    return {k: v for k, v in dict(*args, **kwargs).items() if v is not None}


class AsDictMixin:
    def asdict(self) -> MutableMapping[str, Any]:
        return asdict(self, dict_factory=_none_filter)


@dataclass
class Filter(AsDictMixin):
    __endpoint = "filters"
    id: Optional[str] = None
    bands: Optional[list] = None  # type: ignore[type-arg]
    name: Optional[str] = None
    product: Optional[str] = None


@dataclass
class RegionOfInterest(AsDictMixin):
    __endpoint = "rois"
    id: Optional[str] = None
    name: Optional[str] = None
    NSWE: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Quicklook(AsDictMixin):
    __endpoint = "quicklooks"
    id: Optional[str] = None
    name: Optional[str] = None
    resample_method: Optional[str] = None
    stretch_method: Optional[str] = None
    product: Optional[str] = None
    format: Optional[str] = None
    nodatacolor: Optional[str] = None
    filter: Union[None, dict, Filter] = None  # type: ignore[type-arg]
    x_size: Optional[int] = None

    def __post_init__(self) -> None:
        if self.filter is not None and isinstance(self.filter, dict):
            self.filter = Filter(**self.filter)


@dataclass
class Chain(AsDictMixin):
    __endpoint = "chains"
    __submodels = {"filter": Filter, "roi": RegionOfInterest, "quicklook": Quicklook}
    id: Optional[str] = None
    product: Optional[str] = None
    format: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    aggregation: Optional[str] = None
    projection: Optional[str] = None
    roi: Union[None, dict, RegionOfInterest] = None  # type: ignore[type-arg]
    filter: Union[None, dict, Filter] = None  # type: ignore[type-arg]
    quicklook: Union[None, dict, Quicklook] = None  # type: ignore[type-arg]
    resample_method: Optional[str] = None
    resample_resolution: Optional[list] = None  # type: ignore[type-arg]
    compression: Optional[dict] = None  # type: ignore[type-arg]

    def __post_init__(self) -> None:
        for name, Model in self.__submodels.items():
            attr = getattr(self, name)
            if attr is not None and isinstance(attr, Mapping):
                setattr(self, name, Model(**attr))


if TYPE_CHECKING:  # pragma: no cover
    CrudModelClass = Union[Type[Filter], Type[RegionOfInterest], Type[Quicklook], Type[Chain]]
    CrudModel = Union[Filter, RegionOfInterest, Quicklook, Chain]


class DataTailorCRUD:
    datatailor: DataTailor
    Model: CrudModelClass
    endpoint: str
    url: str

    def __init__(self, datatailor: DataTailor, Model: CrudModelClass) -> None:
        self.datatailor = datatailor
        self.Model = Model
        endpoint = getattr(Model, f"_{Model.__name__}__endpoint")
        self.url = datatailor.urls.get("tailor", endpoint)

    def search(
        self, product: Optional[str] = None, format: Optional[str] = None
    ) -> Sequence[CrudModel]:
        params = _none_filter(product=product, format=format)
        auth = self.datatailor.token.auth
        response = self._request("GET", self.url, auth=auth, params=params)
        return [self.Model(**data) for data in response.json()["data"]]

    def create(self, model: CrudModel) -> None:
        auth = self.datatailor.token.auth
        payload = model.asdict()
        self._request("POST", self.url, auth=auth, json=payload)

    def read(self, model_id: str) -> CrudModel:
        url = f"{self.url}/{model_id}"
        auth = self.datatailor.token.auth
        response = self._request("GET", url, auth=auth)
        return self.Model(**response.json())

    def update(self, model: CrudModel) -> None:
        data = model.asdict()
        url = f"{self.url}/{data['id']}"
        auth = self.datatailor.token.auth
        self._request("PUT", url, auth=auth, json=data)

    def delete(self, model: Union[str, CrudModel]) -> None:
        if isinstance(model, str):
            model_id = model
        else:
            model_id = model.id  # type: ignore[assignment]
        url = f"{self.url}/{model_id}"
        auth = self.datatailor.token.auth
        self._request("DELETE", url, auth=auth)

    def _request(self, method: str, url: str, **options: Any) -> requests.Response:
        response = requests.request(method, url, **options)
        response.raise_for_status()
        return response
