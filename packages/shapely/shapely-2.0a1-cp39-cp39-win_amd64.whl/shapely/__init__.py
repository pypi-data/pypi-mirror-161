

""""""# start delvewheel patch
def _delvewheel_init_patch_0_0_22():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'shapely.libs'))
    if sys.version_info[:2] >= (3, 8):
        conda_workaround = os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')) and (sys.version_info[:3] < (3, 8, 13) or (3, 9, 0) <= sys.version_info[:3] < (3, 9, 9))
        if conda_workaround:
            # backup the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            conda_dll_search_modification_enable = os.environ.get('CONDA_DLL_SEARCH_MODIFICATION_ENABLE')
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = '1'
        os.add_dll_directory(libs_dir)
        if conda_workaround:
            # restore the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            if conda_dll_search_modification_enable is None:
                os.environ.pop('CONDA_DLL_SEARCH_MODIFICATION_ENABLE', None)
            else:
                os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = conda_dll_search_modification_enable
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-shapely-2.0a1')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_22()
del _delvewheel_init_patch_0_0_22
# end delvewheel patch

from .lib import GEOSException  # NOQA
from .lib import Geometry  # NOQA
from .lib import geos_version, geos_version_string  # NOQA
from .lib import geos_capi_version, geos_capi_version_string  # NOQA
from ._geometry import *  # NOQA
from .creation import *  # NOQA
from .constructive import *  # NOQA
from .predicates import *  # NOQA
from .measurement import *  # NOQA
from .set_operations import *  # NOQA
from .linear import *  # NOQA
from .coordinates import *  # NOQA
from .strtree import *  # NOQA
from .io import *  # NOQA

# Submodule always needs to be imported to ensure Geometry subclasses are registered
from shapely.geometry import (  # NOQA
    Point,
    LineString,
    Polygon,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
    GeometryCollection,
    LinearRing,
)

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
