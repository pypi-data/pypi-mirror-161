from ._version import get_versions
from .base import BaseReport  # noqa: F401
from .print import PrintReport  # noqa: F401
from .tree import ProgressReport  # noqa: F401

__version__ = get_versions()["version"]
del get_versions


__all__ = ["BaseReport", "PrintReport", "ProgressReport"]
