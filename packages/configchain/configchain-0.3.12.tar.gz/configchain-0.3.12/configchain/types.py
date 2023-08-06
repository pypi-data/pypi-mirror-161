from typing import TypeVar, List, Union, Mapping, Callable

ConfigFile = str
ConfigName = str

ConfigKey = str
ConfigValue = Union[List[Union[str, int]], "ConfigDict", str, int]
ConfigDict = Mapping[ConfigKey, ConfigValue]

ProfileKey = str
ProfileName = str

ConfigNameStatement = str
ConfigNameGetter = Union[ConfigNameStatement, List[ConfigKey], Callable[["ConfigSnippet"], ConfigName]]
ConfigChainOptions = Union[ConfigNameGetter, ProfileName]

WILDCARD = "*"
PROFILE_NAME_KEY = "profile"

KT = TypeVar("KT")
VT = TypeVar("VT")
