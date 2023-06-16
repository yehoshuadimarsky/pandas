""" support numpy compatibility across versions """
import numpy as np

from pandas.util.version import Version

# numpy versioning
_np_version = np.__version__
_nlv = Version(_np_version)
np_version_under1p22 = _nlv < Version("1.22")
np_version_gte1p24 = _nlv >= Version("1.24")
np_version_gte1p24p3 = _nlv >= Version("1.24.3")
is_numpy_dev = _nlv.dev is not None
_min_numpy_ver = "1.21.6"

np_percentile_argname = "interpolation" if np_version_under1p22 else "method"


if _nlv < Version(_min_numpy_ver):
    raise ImportError(
        f"this version of pandas is incompatible with numpy < {_min_numpy_ver}\n"
        f"your numpy version is {_np_version}.\n"
        f"Please upgrade numpy to >= {_min_numpy_ver} to use this pandas version"
    )


__all__ = [
    "np",
    "_np_version",
    "is_numpy_dev",
]
