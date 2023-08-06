from collections import OrderedDict
from functools import reduce
from operator import add
from typing import List, Optional, Callable

from .snippet import ConfigSnippet
from .types import WILDCARD, ProfileKey, ProfileName, PROFILE_NAME_KEY, ConfigChainOptions
from .utils import list_groupby, dict_merge_with_wildcard, merge_profile_with_wildcard


class Config(OrderedDict):
    @classmethod
    def from_snippets(cls, snippets: List[ConfigSnippet], **kwargs: ConfigChainOptions) -> "Config":
        profile = kwargs.get("profile", PROFILE_NAME_KEY)
        profile_getter: Callable[["ConfigSnippet"], ProfileName] = lambda x: x.get(
            profile, WILDCARD
        )

        def groupby_profile_and_merge(
            snippets: List[ConfigSnippet],
        ) -> List[ConfigSnippet]:
            return [reduce(add, g) for g in list_groupby(snippets, profile_getter)]

        profile_snippets = groupby_profile_and_merge(snippets)
        config = OrderedDict({profile_getter(s): s for s in profile_snippets})
        merge_profile_with_wildcard(config)
        return Config(config)

    def __add__(self, other: "Config") -> "Config":
        return dict_merge_with_wildcard(self, other, add)

    def profile_names(self) -> List[ProfileName]:
        return self.keys()

    def get_profile(
        self, key: ProfileKey, default: Optional[ConfigSnippet] = WILDCARD
    ) -> Optional[ConfigSnippet]:
        return self.get(key, self.get(default, None))
