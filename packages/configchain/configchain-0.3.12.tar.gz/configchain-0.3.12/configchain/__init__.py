from functools import reduce
from operator import add

from .snippet import ConfigSnippet
from .config import Config
from .configset import ConfigSet
from .types import ConfigFile, ConfigChainOptions

__version__ = "0.3.12"


def configchain(*files: ConfigFile, **kwargs: ConfigChainOptions) -> ConfigSet:
    return reduce(add, [ConfigSet.load(f, **kwargs) for f in files])
