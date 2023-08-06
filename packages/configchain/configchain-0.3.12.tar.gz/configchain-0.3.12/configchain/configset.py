from functools import singledispatch
from itertools import chain
from typing import List, Optional, Dict
from collections import OrderedDict, abc
from operator import add
import re

from .config import Config
from .parser import ConfigParser
from .snippet import ConfigSnippet
from .types import ConfigFile, WILDCARD, ConfigName, ConfigChainOptions
from .utils import dict_merge_with_wildcard, merge_profile_with_wildcard


def auto_complete_config_name(
    file, config_name_statement, root_config_name, root_config_name_source
):
    if len(file) == 0:
        return

    names = [get_config_name(config_name_statement, config) for config in file]
    if names[0] != "*":
        _, _, config_name_source = extract_config_name(config_name_statement, file[0])
        [other.update(config_name_source) for other in file[1:]]
    else:
        if root_config_name != "*":
            [other.update(root_config_name_source) for other in file]


def auto_complete(config_name_statement, loader):
    # set default name for configs in the one file
    root_config_snippet = list(loader.values())[0][0]
    root_config_name = get_config_name(config_name_statement, root_config_snippet)
    _, _, root_config_name_source = extract_config_name(
        config_name_statement, root_config_snippet
    )
    for file in loader.values():
        auto_complete_config_name(
            file, config_name_statement, root_config_name, root_config_name_source,
        )


class ConfigSet(OrderedDict):
    @classmethod
    def load(cls, *args: ConfigFile, **kwargs: ConfigChainOptions) -> "ConfigSet":
        loader = ConfigParser(*args, **kwargs)
        loader.load()

        config_name_statement = kwargs.get("name", WILDCARD)

        try:
            auto_complete(config_name_statement, loader)
        except:
            pass

        named_snippets = OrderedDict()
        for snippet in chain(*loader.values()):
            named_snippets.setdefault(
                get_config_name(config_name_statement, snippet), [],
            ).append(snippet)

        named_configs = {
            name: Config.from_snippets(snippets, **kwargs)
            for name, snippets in named_snippets.items()
        }

        merge_profile_with_wildcard(named_configs)
        return cls(named_configs)

    def __add__(self, other: "ConfigSet") -> "ConfigSet":
        return dict_merge_with_wildcard(self, other, add)

    def config_names(self) -> List[ConfigName]:
        return self.keys()


@singledispatch
def get_config_name(_getter, _snippet: ConfigSnippet) -> ConfigName:
    return WILDCARD


@get_config_name.register
def _(config_name_getter: abc.Callable, snippet: ConfigSnippet) -> ConfigName:
    return config_name_getter(snippet)


def extract_config_name(config_name_statement, snippet) -> (List, str, Dict):
    reg = r"\${(\w+)}"
    matches = re.findall(reg, config_name_statement)
    vars = {v: snippet.find(v) for v in matches}
    return matches, reg, vars


@get_config_name.register
def _(config_name_statement: str, snippet: ConfigSnippet) -> ConfigName:
    matches, reg, vars = extract_config_name(config_name_statement, snippet)
    if (
        len(matches) > 0
        and len(
            [
                exist
                for exist in [vars.get(m, None) for m in matches]
                if exist is not None
            ]
        )
        == 0
    ):
        return WILDCARD

    def sub(var):
        (key,) = var.groups()
        return str(vars.get(key, None))

    return re.sub(reg, sub, config_name_statement)


@get_config_name.register
def _(config_name_keys: abc.MutableSequence, snippet: ConfigSnippet) -> ConfigName:
    ids = [
        str(n) for n in [snippet.find(key) for key in config_name_keys] if n is not None
    ]
    if ids:
        return "-".join(ids)
    else:
        return WILDCARD
