"""
Shared test code for IntegerArray/FloatingArray/BooleanArray.
"""
import pytest

from pandas.compat import (
    IS64,
    is_platform_windows,
)

import pandas as pd
import pandas._testing as tm
from pandas.tests.extension import base


class Arithmetic(base.BaseArithmeticOpsTests):
    def check_opname(self, ser: pd.Series, op_name: str, other, exc=None):
        # overwriting to indicate ops don't raise an error
        super().check_opname(ser, op_name, other, exc=None)

    def _check_divmod_op(self, ser: pd.Series, op, other, exc=None):
        super()._check_divmod_op(ser, op, other, None)


class Comparison(base.BaseComparisonOpsTests):
    def _check_op(
        self, ser: pd.Series, op, other, op_name: str, exc=NotImplementedError
    ):
        if exc is None:
            result = op(ser, other)
            # Override to do the astype to boolean
            expected = ser.combine(other, op).astype("boolean")
            self.assert_series_equal(result, expected)
        else:
            with pytest.raises(exc):
                op(ser, other)

    def check_opname(self, ser: pd.Series, op_name: str, other, exc=None):
        super().check_opname(ser, op_name, other, exc=None)

    def _compare_other(self, ser: pd.Series, data, op, other):
        op_name = f"__{op.__name__}__"
        self.check_opname(ser, op_name, other)


class NumericReduce(base.BaseNumericReduceTests):
    def check_reduce(self, ser: pd.Series, op_name: str, skipna: bool):
        # overwrite to ensure pd.NA is tested instead of np.nan
        # https://github.com/pandas-dev/pandas/issues/30958

        cmp_dtype = "int64"
        if ser.dtype.kind == "f":
            # Item "dtype[Any]" of "Union[dtype[Any], ExtensionDtype]" has
            # no attribute "numpy_dtype"
            cmp_dtype = ser.dtype.numpy_dtype  # type: ignore[union-attr]

        if op_name == "count":
            result = getattr(ser, op_name)()
            expected = getattr(ser.dropna().astype(cmp_dtype), op_name)()
        else:
            result = getattr(ser, op_name)(skipna=skipna)
            expected = getattr(ser.dropna().astype(cmp_dtype), op_name)(skipna=skipna)
            if not skipna and ser.isna().any():
                expected = pd.NA
        tm.assert_almost_equal(result, expected)


class Accumulation(base.BaseAccumulateTests):
    @pytest.mark.parametrize("skipna", [True, False])
    def test_accumulate_series_raises(self, data, all_numeric_accumulations, skipna):
        pass

    def check_accumulate(self, ser: pd.Series, op_name: str, skipna: bool):
        # overwrite to ensure pd.NA is tested instead of np.nan
        # https://github.com/pandas-dev/pandas/issues/30958
        length = 64
        if not IS64 or is_platform_windows():
            # Item "ExtensionDtype" of "Union[dtype[Any], ExtensionDtype]" has
            # no attribute "itemsize"
            if not ser.dtype.itemsize == 8:  # type: ignore[union-attr]
                length = 32

        if ser.dtype.name.startswith("U"):
            expected_dtype = f"UInt{length}"
        elif ser.dtype.name.startswith("I"):
            expected_dtype = f"Int{length}"
        elif ser.dtype.name.startswith("F"):
            # Incompatible types in assignment (expression has type
            # "Union[dtype[Any], ExtensionDtype]", variable has type "str")
            expected_dtype = ser.dtype  # type: ignore[assignment]

        if op_name == "cumsum":
            result = getattr(ser, op_name)(skipna=skipna)
            expected = pd.Series(
                pd.array(
                    getattr(ser.astype("float64"), op_name)(skipna=skipna),
                    dtype=expected_dtype,
                )
            )
            tm.assert_series_equal(result, expected)
        elif op_name in ["cummax", "cummin"]:
            result = getattr(ser, op_name)(skipna=skipna)
            expected = pd.Series(
                pd.array(
                    getattr(ser.astype("float64"), op_name)(skipna=skipna),
                    dtype=ser.dtype,
                )
            )
            tm.assert_series_equal(result, expected)
        elif op_name == "cumprod":
            result = getattr(ser[:12], op_name)(skipna=skipna)
            expected = pd.Series(
                pd.array(
                    getattr(ser[:12].astype("float64"), op_name)(skipna=skipna),
                    dtype=expected_dtype,
                )
            )
            tm.assert_series_equal(result, expected)

        else:
            raise NotImplementedError(f"{op_name} not supported")
