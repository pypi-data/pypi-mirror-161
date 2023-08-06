from collections import namedtuple
from typing import _LiteralGenericAlias, get_args  # type: ignore # noqa

from .lookup import READOUT_PLATFORMS, READOUT_TYPES


def _todict(x: _LiteralGenericAlias) -> dict:
    return {
        i.translate({ord(c): "_" for c in "-. !@#$%^&*()[]{};:,/<>?|`~=+'\""}): i
        for i in get_args(x)
    }


class ReadoutType:
    """Readout types."""

    @classmethod
    def lookup(cls):
        values = _todict(READOUT_TYPES)
        nt = namedtuple("readout_type", values.keys())
        return nt(**values)


class ReadoutPlatform:
    """Readout platforms."""

    @classmethod
    def lookup(cls):
        values = _todict(READOUT_PLATFORMS)
        nt = namedtuple("readout_type", values.keys())
        return nt(**values)


readout_type = ReadoutType.lookup()
readout_platform = ReadoutPlatform.lookup()
