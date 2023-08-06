import sys

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .curve import Curve
from .engine import Engine
from .extract import Extract
from .gearbox import Gearbox
from .function import Function
from .map import Map
from .mdf import MDF
from .resistance import Resistance
from .shift import Shift
from .trigger import Trigger
from .value import Value
from .vbo import VBO
from .vehicle import Vehicle
from .watchdog import Watchdog