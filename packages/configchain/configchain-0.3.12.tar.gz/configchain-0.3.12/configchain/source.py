from typing import List, Tuple, Union, Optional
from dataclasses import dataclass, field
from functools import reduce
from pathlib import Path

from .types import ConfigKey, ConfigValue
from .utils import list_uniq


@dataclass(frozen=True)
class ConfigSource:
    uri: str
    index: str
    loader: "ConfigLoader" = field(repr=False, default=None, hash=False)

    @property
    def name(self) -> str:
        return Path(self.uri).stem

    def __repr__(self) -> str:
        return f"{self.name}:{self.index}"

    def __add__(
        self, other: "ConfigSource"
    ) -> Union["ConfigSource", "MergedConfigSource"]:
        if self == other:
            return self
        return MergedConfigSource(sources=list([self])) + other

    def find(self, key: ConfigKey) -> Optional[ConfigValue]:
        if self.loader is None:
            return None
        return self.loader.find(self.uri, key)


@dataclass(frozen=True)
class MergedConfigSource:
    sources: List[ConfigSource]

    def __add__(
        self, other: Union[ConfigSource, "MergedConfigSource"]
    ) -> "MergedConfigSource":
        if isinstance(other, ConfigSource):
            source = list([other])
        if isinstance(other, MergedConfigSource):
            source = other.sources
        return MergedConfigSource(sources=list_uniq(self.sources + source))

    def __str__(self) -> str:
        def create_breadcrumb(a: Tuple[str, str], s: ConfigSource) -> Tuple[str, str]:
            name, breadcrumb = a
            n = s.name
            if n == name:
                return n, f"{breadcrumb}-{s.index}"
            else:
                return n, f"{breadcrumb}-{n}-{s.index}"

        return reduce(create_breadcrumb, self.sources, ("", ""))[1].lstrip("-")

    def find(self, key: ConfigKey) -> Optional[ConfigValue]:
        for loader, uri in reversed([(s.loader, s.uri) for s in self.sources]):
            v = loader.find(uri, key)
            if v is not None:
                return v
        return None
