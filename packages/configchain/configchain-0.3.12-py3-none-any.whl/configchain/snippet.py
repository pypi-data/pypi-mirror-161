from collections import OrderedDict
from copy import copy, deepcopy
from typing import Optional

from .source import ConfigSource
from .types import ConfigDict, ConfigKey, ConfigValue
from .utils import dict_merge, config_merger


class ConfigSnippet(OrderedDict):
    def __init__(self, config: ConfigDict, source: ConfigSource):
        super().__init__(config)
        self.source = source

    def __add__(self, other: "ConfigSnippet") -> "ConfigSnippet":
        if other is None:
            return copy(self)

        return ConfigSnippet(
            config=dict_merge(self, other, config_merger),
            source=self.source + other.source,
        )

    def __copy__(self) -> "ConfigSnippet":
        return ConfigSnippet(
            config={k: copy(v) for k, v in self.items()}, source=self.source
        )

    def __deepcopy__(self, memodict={}) -> "ConfigSnippet":
        return ConfigSnippet(
            config={k: deepcopy(v, memodict) for k, v in self.items()},
            source=self.source,
        )

    def find(self, key: ConfigKey) -> Optional[ConfigValue]:
        v = self.get(key, None)
        if v is not None:
            return v
        return self.source.find(key)
