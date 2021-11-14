import numpy as np
import pytest

from pandas import (
    DatetimeIndex,
    Index,
    NumericIndex,
    PeriodIndex,
    TimedeltaIndex,
)
import pandas._testing as tm
from pandas.core.api import Float64Index
from pandas.core.indexes.datetimelike import DatetimeIndexOpsMixin


@pytest.mark.parametrize(
    "func",
    [
        np.exp,
        np.exp2,
        np.expm1,
        np.log,
        np.log2,
        np.log10,
        np.log1p,
        np.sqrt,
        np.sin,
        np.cos,
        np.tan,
        np.arcsin,
        np.arccos,
        np.arctan,
        np.sinh,
        np.cosh,
        np.tanh,
        np.arcsinh,
        np.arccosh,
        np.arctanh,
        np.deg2rad,
        np.rad2deg,
    ],
    ids=lambda x: x.__name__,
)
def test_numpy_ufuncs_basic(index, func):
    # test ufuncs of numpy, see:
    # https://numpy.org/doc/stable/reference/ufuncs.html

    if isinstance(index, DatetimeIndexOpsMixin):
        with tm.external_error_raised((TypeError, AttributeError)):
            with np.errstate(all="ignore"):
                func(index)
    elif isinstance(index, NumericIndex):
        # coerces to float (e.g. np.sin)
        with np.errstate(all="ignore"):
            result = func(index)
            exp = Index(func(index.values), name=index.name)

        tm.assert_index_equal(result, exp)
        assert isinstance(result, Float64Index)
    else:
        # raise AttributeError or TypeError
        if len(index) == 0:
            pass
        else:
            with tm.external_error_raised((TypeError, AttributeError)):
                with np.errstate(all="ignore"):
                    func(index)


@pytest.mark.parametrize(
    "func", [np.isfinite, np.isinf, np.isnan, np.signbit], ids=lambda x: x.__name__
)
def test_numpy_ufuncs_other(index, func, request):
    # test ufuncs of numpy, see:
    # https://numpy.org/doc/stable/reference/ufuncs.html
    if isinstance(index, (DatetimeIndex, TimedeltaIndex)):

        if func in (np.isfinite, np.isinf, np.isnan):
            # numpy 1.18 changed isinf and isnan to not raise on dt64/td64
            result = func(index)
            assert isinstance(result, np.ndarray)
        else:
            with tm.external_error_raised(TypeError):
                func(index)

    elif isinstance(index, PeriodIndex):
        with tm.external_error_raised(TypeError):
            func(index)

    elif isinstance(index, NumericIndex):
        # Results in bool array
        result = func(index)
        assert isinstance(result, np.ndarray)
        assert not isinstance(result, Index)
    else:
        if len(index) == 0:
            pass
        else:
            with tm.external_error_raised(TypeError):
                func(index)
