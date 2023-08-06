"""Module contianing the customisation class"""
from __future__ import annotations
from .__version__ import __title__, __documentation__, __version__  # noqa

import time
from datetime import datetime
from contextlib import contextmanager

import requests

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import sys
    from typing import Optional, Any, IO, Type
    from eumdac.datatailor import DataTailor
    from types import TracebackType

    if sys.version_info < (3, 9):
        from typing import MutableMapping, Mapping, Iterable, Generator
    else:
        from collections.abc import MutableMapping, Mapping, Iterable, Generator


class Customisation:
    _id: str
    datatailor: DataTailor
    update_margin: float = 0.5  # seconds
    _properties: Optional[MutableMapping[str, Any]] = None
    _deleted: bool = False
    _killed: bool = False
    _last_update: float = 0
    _creation_time_format: str = "%Y%m%dT%H%M%SZ"

    def __init__(self, customisation_id: str, datatailor: DataTailor) -> None:
        self._id = customisation_id
        self.datatailor = datatailor

    @classmethod
    def from_properties(
        cls, properties: Mapping[str, Any], datatailor: DataTailor
    ) -> Customisation:
        _properties = {**properties}
        instance = cls(_properties.pop("id"), datatailor)
        instance._last_update = time.time()
        instance._properties = _properties
        return instance

    def __str__(self) -> str:
        return self._id

    def __repr__(self) -> str:
        return f"{self.__class__}({self._id})"

    def __enter__(self) -> Customisation:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        self.delete()

    def _update_properties(self) -> None:
        if self._deleted:
            raise RuntimeError("Customisation already deleted.")
        now = time.time()
        expired = now - self._last_update > self.update_margin
        if expired or self._properties is None:
            url = self.datatailor.urls.get(
                "tailor", "customisation", vars={"customisation_id": self._id}
            )
            response = requests.get(
                url,
                auth=self.datatailor.token.auth,
                headers={
                    "referer": __documentation__,
                    "User-Agent": str(__title__ + "/" + __version__),
                },
            )
            response.raise_for_status()
            self._properties = response.json()[self._id]
            self._last_update = now

    @property
    def creation_time(self) -> datetime:
        self._update_properties()
        return datetime.strptime(
            self._properties["creation_time"], self._creation_time_format  # type: ignore[index]
        )

    @property
    def backend(self) -> str:
        self._update_properties()
        return self._properties["backend_id"]  # type: ignore[index]

    @property
    def product_type(self) -> str:
        self._update_properties()
        return self._properties["product_id"]  # type: ignore[index]

    @property
    def processing_steps(self) -> Iterable[str]:
        self._update_properties()
        return self._properties["required_processing_steps"]  # type: ignore[index]

    @property
    def status(self) -> str:
        self._update_properties()
        return self._properties["status"]  # type: ignore[index]

    @property
    def progress(self) -> int:
        self._update_properties()
        return self._properties["progress"]  # type: ignore[index]

    @property
    def duration(self) -> int:
        self._update_properties()
        return self._properties["processing_duration"]  # type: ignore[index]

    @property
    def outputs(self) -> Iterable[str]:
        self._update_properties()
        return self._properties["output_products"]  # type: ignore[index]

    @property
    def logfile(self) -> str:
        if self._deleted:
            raise RuntimeError("Customisation already deleted.")
        url = self.datatailor.urls.get(
            "tailor", "customisation log", vars={"customisation_id": self._id}
        )
        response = requests.get(
            url,
            auth=self.datatailor.token.auth,
            headers={
                "referer": __documentation__,
                "User-Agent": str(__title__ + "/" + __version__),
            },
        )
        response.raise_for_status()
        return response.json()["log_content"]

    @contextmanager
    def stream_output(self, output: str) -> Generator[IO[bytes], None, None]:
        if self._deleted:
            raise RuntimeError("Customisation already deleted.")
        if output not in self.outputs:
            raise ValueError(f"{output} not in {self.outputs}")
        url = self.datatailor.urls.get("tailor", "download")
        auth = self.datatailor.token.auth
        params = {"path": output}
        with requests.get(
            url,
            auth=auth,
            params=params,
            stream=True,
            headers={
                "referer": __documentation__,
                "User-Agent": str(__title__ + "/" + __version__),
            },
        ) as response:
            response.raise_for_status()
            response.raw.name = output.split("/")[-1]
            response.raw.decode_content = True
            yield response.raw

    def delete(self) -> None:
        if not self._deleted:
            url = self.datatailor.urls.get("tailor", "delete")
            payload = {"uuids": [self._id]}
            auth = self.datatailor.token.auth
            response = requests.patch(url, auth=auth, json=payload)
            response.raise_for_status()
            self._deleted = True

    def kill(self) -> None:
        if not self._killed:
            url = self.datatailor.urls.get(
                "tailor", "customisation", vars={"customisation_id": self._id}
            )
            auth = self.datatailor.token.auth
            response = requests.put(url, json={"status": "killed"}, auth=auth)
            response.raise_for_status()
            self._killed = True
