from abc import ABC, abstractmethod
from collections import OrderedDict
from os import path
from typing import List, Optional

import yaml

from .loader import FileLoader
from .snippet import ConfigSnippet
from .source import ConfigSource
from .types import ConfigFile, ConfigDict, ConfigValue, ConfigKey, ConfigChainOptions


class BaseConfigParser(OrderedDict, ABC):
    """
    Key: the path of loaded yaml
    Value: the config dict of yaml
    """

    def __init__(self, *files: List[ConfigFile], **kwargs: ConfigChainOptions):
        self._reader = kwargs.pop("reader", None) or FileLoader()
        self._source = files
        self._includes = []

    @abstractmethod
    def _parse_config(self, content) -> List[ConfigDict]:
        ...

    def find(self, file: ConfigFile, key: ConfigKey) -> Optional[ConfigValue]:
        key = self._reader.key(file)
        for snippet in self.get(key):
            v = snippet.get(key, None)
            if v is not None:
                return v
        return None

    def load(self) -> None:
        [self._load(file) for file in self._source]

    def _load(self, file: ConfigFile, source: Optional[ConfigSource] = None) -> None:
        # TODO
        # reader = LocalFileReader(".")
        # reader.read(file)
        # file = path.abspath(file)
        _conf = self._parse_config(self._reader.read(file))

        configs = [self._process_directives(file, i, c) for i, c in enumerate(_conf)]
        configs = [dc for dc in configs if dc]  # filter None

        def gs(config, file, index, ps=None):
            source = ConfigSource(uri=file, index=index, loader=self)
            if ps is not None:
                source = ps + source
            return ConfigSnippet(config=config, source=source)

        snippets = [
            gs(config, file, index, source) for index, config in enumerate(configs)
        ]
        self.setdefault(self._reader.key(file), snippets)

        while self._includes:
            inc, source = self._includes.pop()
            self._load(inc, source)

    def _process_directives(
        self, file: ConfigFile, index: int, config: ConfigDict
    ) -> ConfigDict:
        if config is None:
            return None

        workdir = path.dirname(file)
        includes = config.pop("@include", None)
        if includes is not None:
            self._includes.extend(
                [
                    (
                        path.abspath(path.join(workdir, f)),
                        ConfigSource(uri=file, index=index, loader=self),
                    )
                    for f in includes
                ]
            )

        return config


class YamlConfigParser(BaseConfigParser):
    def _parse_config(self, content) -> List[ConfigDict]:
        if content is None:
            return []
        # return yaml.load_all(content, Loader=yaml.SafeLoader)
        c = yaml.load_all(content, Loader=yaml.SafeLoader)
        return c


class ConfigParser(object):
    def __new__(cls, *args: ConfigFile, **kwargs: ConfigChainOptions):
        return YamlConfigParser(*args, **kwargs)
