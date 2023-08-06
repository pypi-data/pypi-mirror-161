"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType
from bodo.libs.str_ext import string_type
from bodo.utils.transform import is_var_size_item_array_type
from bodo.utils.typing import BodoError, ColNamesMetaType, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_index_names, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, is_str_arr_type, raise_bodo_error, to_nullable_type, to_str_arr_if_dict_array


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    if isinstance(s.data, bodo.DatetimeArrayType):

        def impl(s):
            klc__yygi = bodo.hiframes.pd_series_ext.get_series_data(s)
            blgvz__tgbz = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                klc__yygi)
            return blgvz__tgbz
        return impl
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s, 'Series.dtype'
        )
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(s,
        'Series.dtypes')
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.tolist()')
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            sbeib__ufs = list()
            for qmpom__kxle in range(len(S)):
                sbeib__ufs.append(S.iat[qmpom__kxle])
            return sbeib__ufs
        return impl_float

    def impl(S):
        sbeib__ufs = list()
        for qmpom__kxle in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, qmpom__kxle):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            sbeib__ufs.append(S.iat[qmpom__kxle])
        return sbeib__ufs
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    qcpap__pip = dict(dtype=dtype, copy=copy, na_value=na_value)
    bwxxw__yad = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    qcpap__pip = dict(name=name, inplace=inplace)
    bwxxw__yad = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        evyyz__pgonz = ', '.join(['index_arrs[{}]'.format(qmpom__kxle) for
            qmpom__kxle in range(S.index.nlevels)])
    else:
        evyyz__pgonz = '    bodo.utils.conversion.index_to_array(index)\n'
    thw__pmhn = 'index' if 'index' != series_name else 'level_0'
    tsv__bdnq = get_index_names(S.index, 'Series.reset_index()', thw__pmhn)
    columns = [name for name in tsv__bdnq]
    columns.append(series_name)
    vbk__czhd = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    vbk__czhd += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    vbk__czhd += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        vbk__czhd += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    vbk__czhd += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    vbk__czhd += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({evyyz__pgonz}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    qkx__fbce = {}
    exec(vbk__czhd, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, qkx__fbce)
    cromv__ilt = qkx__fbce['_impl']
    return cromv__ilt


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.round()')

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        fznk__wuy = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[qmpom__kxle]):
                bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
            else:
                fznk__wuy[qmpom__kxle] = np.round(arr[qmpom__kxle], decimals)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sum()'
        )

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.product()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    qcpap__pip = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    bwxxw__yad = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.any()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_any(A)
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.equals()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.equals()')
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        phuxz__itk = bodo.hiframes.pd_series_ext.get_series_data(S)
        ufirt__vwmmx = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        hfzpl__oih = 0
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(phuxz__itk)
            ):
            mej__odal = 0
            cib__qqd = bodo.libs.array_kernels.isna(phuxz__itk, qmpom__kxle)
            bztg__tgvqv = bodo.libs.array_kernels.isna(ufirt__vwmmx,
                qmpom__kxle)
            if cib__qqd and not bztg__tgvqv or not cib__qqd and bztg__tgvqv:
                mej__odal = 1
            elif not cib__qqd:
                if phuxz__itk[qmpom__kxle] != ufirt__vwmmx[qmpom__kxle]:
                    mej__odal = 1
            hfzpl__oih += mej__odal
        return hfzpl__oih == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    qcpap__pip = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=
        level)
    bwxxw__yad = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    qcpap__pip = dict(level=level)
    bwxxw__yad = dict(level=None)
    check_unsupported_args('Series.mad', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    vkuk__btnbe = types.float64
    fjvbz__zhp = types.float64
    if S.dtype == types.float32:
        vkuk__btnbe = types.float32
        fjvbz__zhp = types.float32
    ubdbr__wdwi = vkuk__btnbe(0)
    norxi__uidhg = fjvbz__zhp(0)
    jrz__ieav = fjvbz__zhp(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        vjl__yvijv = ubdbr__wdwi
        hfzpl__oih = norxi__uidhg
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(A)):
            mej__odal = ubdbr__wdwi
            uqghs__syhos = norxi__uidhg
            if not bodo.libs.array_kernels.isna(A, qmpom__kxle) or not skipna:
                mej__odal = A[qmpom__kxle]
                uqghs__syhos = jrz__ieav
            vjl__yvijv += mej__odal
            hfzpl__oih += uqghs__syhos
        ssy__fhmoc = bodo.hiframes.series_kernels._mean_handle_nan(vjl__yvijv,
            hfzpl__oih)
        ospsy__rosuz = ubdbr__wdwi
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(A)):
            mej__odal = ubdbr__wdwi
            if not bodo.libs.array_kernels.isna(A, qmpom__kxle) or not skipna:
                mej__odal = abs(A[qmpom__kxle] - ssy__fhmoc)
            ospsy__rosuz += mej__odal
        umk__eawak = bodo.hiframes.series_kernels._mean_handle_nan(ospsy__rosuz
            , hfzpl__oih)
        return umk__eawak
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    qcpap__pip = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.mean()')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.sem()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        tajbk__onpul = 0
        vwzay__ewy = 0
        hfzpl__oih = 0
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(A)):
            mej__odal = 0
            uqghs__syhos = 0
            if not bodo.libs.array_kernels.isna(A, qmpom__kxle) or not skipna:
                mej__odal = A[qmpom__kxle]
                uqghs__syhos = 1
            tajbk__onpul += mej__odal
            vwzay__ewy += mej__odal * mej__odal
            hfzpl__oih += uqghs__syhos
        rro__ddtz = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            tajbk__onpul, vwzay__ewy, hfzpl__oih, ddof)
        wiu__npnp = bodo.hiframes.series_kernels._sem_handle_nan(rro__ddtz,
            hfzpl__oih)
        return wiu__npnp
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.kurtosis()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        tajbk__onpul = 0.0
        vwzay__ewy = 0.0
        ecbpt__czmml = 0.0
        xvepm__hwuk = 0.0
        hfzpl__oih = 0
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(A)):
            mej__odal = 0.0
            uqghs__syhos = 0
            if not bodo.libs.array_kernels.isna(A, qmpom__kxle) or not skipna:
                mej__odal = np.float64(A[qmpom__kxle])
                uqghs__syhos = 1
            tajbk__onpul += mej__odal
            vwzay__ewy += mej__odal ** 2
            ecbpt__czmml += mej__odal ** 3
            xvepm__hwuk += mej__odal ** 4
            hfzpl__oih += uqghs__syhos
        rro__ddtz = bodo.hiframes.series_kernels.compute_kurt(tajbk__onpul,
            vwzay__ewy, ecbpt__czmml, xvepm__hwuk, hfzpl__oih)
        return rro__ddtz
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.skew()')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        tajbk__onpul = 0.0
        vwzay__ewy = 0.0
        ecbpt__czmml = 0.0
        hfzpl__oih = 0
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(A)):
            mej__odal = 0.0
            uqghs__syhos = 0
            if not bodo.libs.array_kernels.isna(A, qmpom__kxle) or not skipna:
                mej__odal = np.float64(A[qmpom__kxle])
                uqghs__syhos = 1
            tajbk__onpul += mej__odal
            vwzay__ewy += mej__odal ** 2
            ecbpt__czmml += mej__odal ** 3
            hfzpl__oih += uqghs__syhos
        rro__ddtz = bodo.hiframes.series_kernels.compute_skew(tajbk__onpul,
            vwzay__ewy, ecbpt__czmml, hfzpl__oih)
        return rro__ddtz
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.var()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.std()'
        )

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.dot()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.dot()')

    def impl(S, other):
        phuxz__itk = bodo.hiframes.pd_series_ext.get_series_data(S)
        ufirt__vwmmx = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        cwhep__wloun = 0
        for qmpom__kxle in numba.parfors.parfor.internal_prange(len(phuxz__itk)
            ):
            ruxec__cpmqy = phuxz__itk[qmpom__kxle]
            ctaq__zvpe = ufirt__vwmmx[qmpom__kxle]
            cwhep__wloun += ruxec__cpmqy * ctaq__zvpe
        return cwhep__wloun
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    qcpap__pip = dict(skipna=skipna)
    bwxxw__yad = dict(skipna=True)
    check_unsupported_args('Series.cumsum', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumsum()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    qcpap__pip = dict(skipna=skipna)
    bwxxw__yad = dict(skipna=True)
    check_unsupported_args('Series.cumprod', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cumprod()')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    qcpap__pip = dict(skipna=skipna)
    bwxxw__yad = dict(skipna=True)
    check_unsupported_args('Series.cummin', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummin()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    qcpap__pip = dict(skipna=skipna)
    bwxxw__yad = dict(skipna=True)
    check_unsupported_args('Series.cummax', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.cummax()')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    qcpap__pip = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    bwxxw__yad = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        njktv__uuplr = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, njktv__uuplr, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    qcpap__pip = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    bwxxw__yad = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if is_overload_none(mapper) or not is_scalar_type(mapper):
        raise BodoError(
            "Series.rename_axis(): 'mapper' is required and must be a scalar type."
            )

    def impl(S, mapper=None, index=None, columns=None, axis=None, copy=True,
        inplace=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        index = index.rename(mapper)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.abs()'
        )

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    qcpap__pip = dict(level=level)
    bwxxw__yad = dict(level=None)
    check_unsupported_args('Series.count', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    qcpap__pip = dict(method=method, min_periods=min_periods)
    bwxxw__yad = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        beqz__fuj = S.sum()
        dykxi__ukni = other.sum()
        a = n * (S * other).sum() - beqz__fuj * dykxi__ukni
        gen__gbh = n * (S ** 2).sum() - beqz__fuj ** 2
        olxob__igp = n * (other ** 2).sum() - dykxi__ukni ** 2
        return a / np.sqrt(gen__gbh * olxob__igp)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    qcpap__pip = dict(min_periods=min_periods)
    bwxxw__yad = dict(min_periods=None)
    check_unsupported_args('Series.cov', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        beqz__fuj = S.mean()
        dykxi__ukni = other.mean()
        ayfh__zar = ((S - beqz__fuj) * (other - dykxi__ukni)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(ayfh__zar, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            rom__qch = np.sign(sum_val)
            return np.inf * rom__qch
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    qcpap__pip = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.min()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    qcpap__pip = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.max()'
        )

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    qcpap__pip = dict(axis=axis, skipna=skipna)
    bwxxw__yad = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmin()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    qcpap__pip = dict(axis=axis, skipna=skipna)
    bwxxw__yad = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.idxmax()')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_increasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.is_monotonic_decreasing')
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    qcpap__pip = dict(level=level, numeric_only=numeric_only)
    bwxxw__yad = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ffhyc__exysw = arr[:n]
        lbcoe__xbhn = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(ffhyc__exysw,
            lbcoe__xbhn, name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        izfif__saaew = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ffhyc__exysw = arr[izfif__saaew:]
        lbcoe__xbhn = index[izfif__saaew:]
        return bodo.hiframes.pd_series_ext.init_series(ffhyc__exysw,
            lbcoe__xbhn, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    rptjd__qouot = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in rptjd__qouot:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            qenh__rpcvl = index[0]
            xry__dei = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                qenh__rpcvl, False))
        else:
            xry__dei = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ffhyc__exysw = arr[:xry__dei]
        lbcoe__xbhn = index[:xry__dei]
        return bodo.hiframes.pd_series_ext.init_series(ffhyc__exysw,
            lbcoe__xbhn, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    rptjd__qouot = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in rptjd__qouot:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            pqjgh__xlg = index[-1]
            xry__dei = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                pqjgh__xlg, True))
        else:
            xry__dei = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ffhyc__exysw = arr[len(arr) - xry__dei:]
        lbcoe__xbhn = index[len(arr) - xry__dei:]
        return bodo.hiframes.pd_series_ext.init_series(ffhyc__exysw,
            lbcoe__xbhn, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kvfxc__owowy = bodo.utils.conversion.index_to_array(index)
        lbqo__vitvg, yopdg__shnmt = (bodo.libs.array_kernels.
            first_last_valid_index(arr, kvfxc__owowy))
        return yopdg__shnmt if lbqo__vitvg else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kvfxc__owowy = bodo.utils.conversion.index_to_array(index)
        lbqo__vitvg, yopdg__shnmt = (bodo.libs.array_kernels.
            first_last_valid_index(arr, kvfxc__owowy, False))
        return yopdg__shnmt if lbqo__vitvg else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    qcpap__pip = dict(keep=keep)
    bwxxw__yad = dict(keep='first')
    check_unsupported_args('Series.nlargest', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kvfxc__owowy = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy, njncw__rol = bodo.libs.array_kernels.nlargest(arr,
            kvfxc__owowy, n, True, bodo.hiframes.series_kernels.gt_f)
        kqnwv__jacp = bodo.utils.conversion.convert_to_index(njncw__rol)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
            kqnwv__jacp, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    qcpap__pip = dict(keep=keep)
    bwxxw__yad = dict(keep='first')
    check_unsupported_args('Series.nsmallest', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        kvfxc__owowy = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy, njncw__rol = bodo.libs.array_kernels.nlargest(arr,
            kvfxc__owowy, n, False, bodo.hiframes.series_kernels.lt_f)
        kqnwv__jacp = bodo.utils.conversion.convert_to_index(njncw__rol)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
            kqnwv__jacp, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
@overload_method(HeterogeneousSeriesType, 'astype', inline='always',
    no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    qcpap__pip = dict(errors=errors)
    bwxxw__yad = dict(errors='raise')
    check_unsupported_args('Series.astype', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.astype()')

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    qcpap__pip = dict(axis=axis, is_copy=is_copy)
    bwxxw__yad = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        kkm__lcxvx = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[kkm__lcxvx],
            index[kkm__lcxvx], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    qcpap__pip = dict(axis=axis, kind=kind, order=order)
    bwxxw__yad = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xrii__riei = S.notna().values
        if not xrii__riei.all():
            fznk__wuy = np.full(n, -1, np.int64)
            fznk__wuy[xrii__riei] = argsort(arr[xrii__riei])
        else:
            fznk__wuy = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    qcpap__pip = dict(axis=axis, numeric_only=numeric_only)
    bwxxw__yad = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_str(method):
        raise BodoError(
            "Series.rank(): 'method' argument must be a constant string")
    if not is_overload_constant_str(na_option):
        raise BodoError(
            "Series.rank(): 'na_option' argument must be a constant string")

    def impl(S, axis=0, method='average', numeric_only=None, na_option=
        'keep', ascending=True, pct=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    qcpap__pip = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    bwxxw__yad = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    wwy__wpgzo = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sik__bdt = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, wwy__wpgzo)
        hlodw__lnq = sik__bdt.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        fznk__wuy = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            hlodw__lnq, 0)
        kqnwv__jacp = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            hlodw__lnq)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
            kqnwv__jacp, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    qcpap__pip = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    bwxxw__yad = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    nwjem__sav = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sik__bdt = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, nwjem__sav)
        hlodw__lnq = sik__bdt.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        fznk__wuy = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            hlodw__lnq, 0)
        kqnwv__jacp = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            hlodw__lnq)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
            kqnwv__jacp, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    laj__wuzb = is_overload_true(is_nullable)
    vbk__czhd = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    vbk__czhd += '  numba.parfors.parfor.init_prange()\n'
    vbk__czhd += '  n = len(arr)\n'
    if laj__wuzb:
        vbk__czhd += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        vbk__czhd += '  out_arr = np.empty(n, np.int64)\n'
    vbk__czhd += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    vbk__czhd += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if laj__wuzb:
        vbk__czhd += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        vbk__czhd += '      out_arr[i] = -1\n'
    vbk__czhd += '      continue\n'
    vbk__czhd += '    val = arr[i]\n'
    vbk__czhd += '    if include_lowest and val == bins[0]:\n'
    vbk__czhd += '      ind = 1\n'
    vbk__czhd += '    else:\n'
    vbk__czhd += '      ind = np.searchsorted(bins, val)\n'
    vbk__czhd += '    if ind == 0 or ind == len(bins):\n'
    if laj__wuzb:
        vbk__czhd += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        vbk__czhd += '      out_arr[i] = -1\n'
    vbk__czhd += '    else:\n'
    vbk__czhd += '      out_arr[i] = ind - 1\n'
    vbk__czhd += '  return out_arr\n'
    qkx__fbce = {}
    exec(vbk__czhd, {'bodo': bodo, 'np': np, 'numba': numba}, qkx__fbce)
    impl = qkx__fbce['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        pzw__ajm, lvf__hhk = np.divmod(x, 1)
        if pzw__ajm == 0:
            bzwa__wsi = -int(np.floor(np.log10(abs(lvf__hhk)))) - 1 + precision
        else:
            bzwa__wsi = precision
        return np.around(x, bzwa__wsi)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        ajfv__nqs = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(ajfv__nqs)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        skd__syy = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            fbqb__vbyb = bins.copy()
            if right and include_lowest:
                fbqb__vbyb[0] = fbqb__vbyb[0] - skd__syy
            exkhg__xukwl = bodo.libs.interval_arr_ext.init_interval_array(
                fbqb__vbyb[:-1], fbqb__vbyb[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(exkhg__xukwl,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        fbqb__vbyb = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            fbqb__vbyb[0] = fbqb__vbyb[0] - 10.0 ** -precision
        exkhg__xukwl = bodo.libs.interval_arr_ext.init_interval_array(
            fbqb__vbyb[:-1], fbqb__vbyb[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(exkhg__xukwl,
            None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        odtzb__melj = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        htgzg__mok = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        fznk__wuy = np.zeros(nbins, np.int64)
        for qmpom__kxle in range(len(odtzb__melj)):
            fznk__wuy[htgzg__mok[qmpom__kxle]] = odtzb__melj[qmpom__kxle]
        return fznk__wuy
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            jpkwr__yfu = (max_val - min_val) * 0.001
            if right:
                bins[0] -= jpkwr__yfu
            else:
                bins[-1] += jpkwr__yfu
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    qcpap__pip = dict(dropna=dropna)
    bwxxw__yad = dict(dropna=True)
    check_unsupported_args('Series.value_counts', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    vsprl__yryuf = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    vbk__czhd = 'def impl(\n'
    vbk__czhd += '    S,\n'
    vbk__czhd += '    normalize=False,\n'
    vbk__czhd += '    sort=True,\n'
    vbk__czhd += '    ascending=False,\n'
    vbk__czhd += '    bins=None,\n'
    vbk__czhd += '    dropna=True,\n'
    vbk__czhd += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    vbk__czhd += '):\n'
    vbk__czhd += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    vbk__czhd += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    vbk__czhd += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if vsprl__yryuf:
        vbk__czhd += '    right = True\n'
        vbk__czhd += _gen_bins_handling(bins, S.dtype)
        vbk__czhd += '    arr = get_bin_inds(bins, arr)\n'
    vbk__czhd += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    vbk__czhd += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    vbk__czhd += '    )\n'
    vbk__czhd += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if vsprl__yryuf:
        vbk__czhd += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        vbk__czhd += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        vbk__czhd += '    index = get_bin_labels(bins)\n'
    else:
        vbk__czhd += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        vbk__czhd += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        vbk__czhd += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        vbk__czhd += '    )\n'
        vbk__czhd += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    vbk__czhd += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        vbk__czhd += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        jurid__rkaxf = 'len(S)' if vsprl__yryuf else 'count_arr.sum()'
        vbk__czhd += f'    res = res / float({jurid__rkaxf})\n'
    vbk__czhd += '    return res\n'
    qkx__fbce = {}
    exec(vbk__czhd, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, qkx__fbce)
    impl = qkx__fbce['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    vbk__czhd = ''
    if isinstance(bins, types.Integer):
        vbk__czhd += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        vbk__czhd += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            vbk__czhd += '    min_val = min_val.value\n'
            vbk__czhd += '    max_val = max_val.value\n'
        vbk__czhd += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            vbk__czhd += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        vbk__czhd += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return vbk__czhd


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    qcpap__pip = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    bwxxw__yad = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    vbk__czhd = 'def impl(\n'
    vbk__czhd += '    x,\n'
    vbk__czhd += '    bins,\n'
    vbk__czhd += '    right=True,\n'
    vbk__czhd += '    labels=None,\n'
    vbk__czhd += '    retbins=False,\n'
    vbk__czhd += '    precision=3,\n'
    vbk__czhd += '    include_lowest=False,\n'
    vbk__czhd += "    duplicates='raise',\n"
    vbk__czhd += '    ordered=True\n'
    vbk__czhd += '):\n'
    if isinstance(x, SeriesType):
        vbk__czhd += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        vbk__czhd += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        vbk__czhd += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        vbk__czhd += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    vbk__czhd += _gen_bins_handling(bins, x.dtype)
    vbk__czhd += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    vbk__czhd += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    vbk__czhd += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    vbk__czhd += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        vbk__czhd += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        vbk__czhd += '    return res\n'
    else:
        vbk__czhd += '    return out_arr\n'
    qkx__fbce = {}
    exec(vbk__czhd, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, qkx__fbce)
    impl = qkx__fbce['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.unique, inline='always', no_unliteral=True)
def overload_unique(values):
    if not is_series_type(values) and not (bodo.utils.utils.is_array_typ(
        values, False) and values.ndim == 1):
        raise BodoError(
            "pd.unique(): 'values' must be either a Series or a 1-d array")
    if is_series_type(values):

        def impl(values):
            arr = bodo.hiframes.pd_series_ext.get_series_data(values)
            return bodo.allgatherv(bodo.libs.array_kernels.unique(arr), False)
        return impl
    else:
        return lambda values: bodo.allgatherv(bodo.libs.array_kernels.
            unique(values), False)


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    qcpap__pip = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    bwxxw__yad = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        qulh__dhzm = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, qulh__dhzm)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    qcpap__pip = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    bwxxw__yad = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )
        ulqzd__vfxe = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            diaf__fck = bodo.utils.conversion.coerce_to_array(index)
            sik__bdt = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                diaf__fck, arr), index, ulqzd__vfxe)
            return sik__bdt.groupby(' ')['']
        return impl_index
    kbqdx__dieai = by
    if isinstance(by, SeriesType):
        kbqdx__dieai = by.data
    if isinstance(kbqdx__dieai, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    ysoe__bqpnz = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        diaf__fck = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        sik__bdt = bodo.hiframes.pd_dataframe_ext.init_dataframe((diaf__fck,
            arr), index, ysoe__bqpnz)
        return sik__bdt.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    qcpap__pip = dict(verify_integrity=verify_integrity)
    bwxxw__yad = dict(verify_integrity=False)
    check_unsupported_args('Series.append', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.append()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(to_append,
        'Series.append()')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.isin()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(values,
        'Series.isin()')
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            mncam__jipo = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            fznk__wuy = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(fznk__wuy, A, mncam__jipo, False)
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    qcpap__pip = dict(interpolation=interpolation)
    bwxxw__yad = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            fznk__wuy = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        arrca__fnray = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(arrca__fnray, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    qcpap__pip = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    bwxxw__yad = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.describe()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        sapqq__mgsj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        sapqq__mgsj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    vbk__czhd = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {sapqq__mgsj}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    fvq__fgt = dict()
    exec(vbk__czhd, {'bodo': bodo, 'numba': numba}, fvq__fgt)
    izx__urjsf = fvq__fgt['impl']
    return izx__urjsf


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        sapqq__mgsj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        sapqq__mgsj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    vbk__czhd = 'def impl(S,\n'
    vbk__czhd += '     value=None,\n'
    vbk__czhd += '    method=None,\n'
    vbk__czhd += '    axis=None,\n'
    vbk__czhd += '    inplace=False,\n'
    vbk__czhd += '    limit=None,\n'
    vbk__czhd += '   downcast=None,\n'
    vbk__czhd += '):\n'
    vbk__czhd += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    vbk__czhd += '    n = len(in_arr)\n'
    vbk__czhd += f'    out_arr = {sapqq__mgsj}(n, -1)\n'
    vbk__czhd += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    vbk__czhd += '        s = in_arr[j]\n'
    vbk__czhd += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    vbk__czhd += '            s = value\n'
    vbk__czhd += '        out_arr[j] = s\n'
    vbk__czhd += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    fvq__fgt = dict()
    exec(vbk__czhd, {'bodo': bodo, 'numba': numba}, fvq__fgt)
    izx__urjsf = fvq__fgt['impl']
    return izx__urjsf


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
    fruoz__rsp = bodo.hiframes.pd_series_ext.get_series_data(value)
    for qmpom__kxle in numba.parfors.parfor.internal_prange(len(bzy__nhiwq)):
        s = bzy__nhiwq[qmpom__kxle]
        if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle
            ) and not bodo.libs.array_kernels.isna(fruoz__rsp, qmpom__kxle):
            s = fruoz__rsp[qmpom__kxle]
        bzy__nhiwq[qmpom__kxle] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
    for qmpom__kxle in numba.parfors.parfor.internal_prange(len(bzy__nhiwq)):
        s = bzy__nhiwq[qmpom__kxle]
        if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle):
            s = value
        bzy__nhiwq[qmpom__kxle] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    fruoz__rsp = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(bzy__nhiwq)
    fznk__wuy = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for zvq__kvhqs in numba.parfors.parfor.internal_prange(n):
        s = bzy__nhiwq[zvq__kvhqs]
        if bodo.libs.array_kernels.isna(bzy__nhiwq, zvq__kvhqs
            ) and not bodo.libs.array_kernels.isna(fruoz__rsp, zvq__kvhqs):
            s = fruoz__rsp[zvq__kvhqs]
        fznk__wuy[zvq__kvhqs] = s
        if bodo.libs.array_kernels.isna(bzy__nhiwq, zvq__kvhqs
            ) and bodo.libs.array_kernels.isna(fruoz__rsp, zvq__kvhqs):
            bodo.libs.array_kernels.setna(fznk__wuy, zvq__kvhqs)
    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    fruoz__rsp = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(bzy__nhiwq)
    fznk__wuy = bodo.utils.utils.alloc_type(n, bzy__nhiwq.dtype, (-1,))
    for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
        s = bzy__nhiwq[qmpom__kxle]
        if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle
            ) and not bodo.libs.array_kernels.isna(fruoz__rsp, qmpom__kxle):
            s = fruoz__rsp[qmpom__kxle]
        fznk__wuy[qmpom__kxle] = s
    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    qcpap__pip = dict(limit=limit, downcast=downcast)
    bwxxw__yad = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    eoifh__kir = not is_overload_none(value)
    ithic__vgv = not is_overload_none(method)
    if eoifh__kir and ithic__vgv:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not eoifh__kir and not ithic__vgv:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if ithic__vgv:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        vcyis__kfo = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(vcyis__kfo)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(vcyis__kfo)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    kru__lcyx = element_type(S.data)
    hkw__foihm = None
    if eoifh__kir:
        hkw__foihm = element_type(types.unliteral(value))
    if hkw__foihm and not can_replace(kru__lcyx, hkw__foihm):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {hkw__foihm} with series type {kru__lcyx}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if S.data == bodo.dict_str_arr_type:
                raise_bodo_error(
                    "Series.fillna(): 'inplace' not supported for dictionary-encoded string arrays yet."
                    )
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        zvjfw__cdz = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                fruoz__rsp = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(bzy__nhiwq)
                fznk__wuy = bodo.utils.utils.alloc_type(n, zvjfw__cdz, (-1,))
                for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle
                        ) and bodo.libs.array_kernels.isna(fruoz__rsp,
                        qmpom__kxle):
                        bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                        continue
                    if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle):
                        fznk__wuy[qmpom__kxle
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            fruoz__rsp[qmpom__kxle])
                        continue
                    fznk__wuy[qmpom__kxle
                        ] = bodo.utils.conversion.unbox_if_timestamp(bzy__nhiwq
                        [qmpom__kxle])
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return fillna_series_impl
        if ithic__vgv:
            paa__wry = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(kru__lcyx, (types.Integer, types.Float)
                ) and kru__lcyx not in paa__wry:
                raise BodoError(
                    f"Series.fillna(): series of type {kru__lcyx} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                fznk__wuy = bodo.libs.array_kernels.ffill_bfill_arr(bzy__nhiwq,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(bzy__nhiwq)
            fznk__wuy = bodo.utils.utils.alloc_type(n, zvjfw__cdz, (-1,))
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(bzy__nhiwq[
                    qmpom__kxle])
                if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle):
                    s = value
                fznk__wuy[qmpom__kxle] = s
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        mfuy__webaj = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        qcpap__pip = dict(limit=limit, downcast=downcast)
        bwxxw__yad = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', qcpap__pip,
            bwxxw__yad, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        kru__lcyx = element_type(S.data)
        paa__wry = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(kru__lcyx, (types.Integer, types.Float)
            ) and kru__lcyx not in paa__wry:
            raise BodoError(
                f'Series.{overload_name}(): series of type {kru__lcyx} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            fznk__wuy = bodo.libs.array_kernels.ffill_bfill_arr(bzy__nhiwq,
                mfuy__webaj)
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        gmxj__mch = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(gmxj__mch
            )


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        sjmvv__btlwn = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(sjmvv__btlwn)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        sjmvv__btlwn = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(sjmvv__btlwn)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        sjmvv__btlwn = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(sjmvv__btlwn)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    qcpap__pip = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    puucn__iwdrb = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', qcpap__pip, puucn__iwdrb,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    kru__lcyx = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        kux__zcbbh = element_type(to_replace.key_type)
        hkw__foihm = element_type(to_replace.value_type)
    else:
        kux__zcbbh = element_type(to_replace)
        hkw__foihm = element_type(value)
    akym__fblnv = None
    if kru__lcyx != types.unliteral(kux__zcbbh):
        if bodo.utils.typing.equality_always_false(kru__lcyx, types.
            unliteral(kux__zcbbh)
            ) or not bodo.utils.typing.types_equality_exists(kru__lcyx,
            kux__zcbbh):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(kru__lcyx, (types.Float, types.Integer)
            ) or kru__lcyx == np.bool_:
            akym__fblnv = kru__lcyx
    if not can_replace(kru__lcyx, types.unliteral(hkw__foihm)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    had__qbz = to_str_arr_if_dict_array(S.data)
    if isinstance(had__qbz, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bzy__nhiwq.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(bzy__nhiwq)
        fznk__wuy = bodo.utils.utils.alloc_type(n, had__qbz, (-1,))
        mplq__dkx = build_replace_dict(to_replace, value, akym__fblnv)
        for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(bzy__nhiwq, qmpom__kxle):
                bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                continue
            s = bzy__nhiwq[qmpom__kxle]
            if s in mplq__dkx:
                s = mplq__dkx[s]
            fznk__wuy[qmpom__kxle] = s
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    aayik__qflt = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    mpfzd__mqbw = is_iterable_type(to_replace)
    flpa__mlzcs = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    ean__ucmp = is_iterable_type(value)
    if aayik__qflt and flpa__mlzcs:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                mplq__dkx = {}
                mplq__dkx[key_dtype_conv(to_replace)] = value
                return mplq__dkx
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            mplq__dkx = {}
            mplq__dkx[to_replace] = value
            return mplq__dkx
        return impl
    if mpfzd__mqbw and flpa__mlzcs:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                mplq__dkx = {}
                for qulhr__euus in to_replace:
                    mplq__dkx[key_dtype_conv(qulhr__euus)] = value
                return mplq__dkx
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            mplq__dkx = {}
            for qulhr__euus in to_replace:
                mplq__dkx[qulhr__euus] = value
            return mplq__dkx
        return impl
    if mpfzd__mqbw and ean__ucmp:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                mplq__dkx = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for qmpom__kxle in range(len(to_replace)):
                    mplq__dkx[key_dtype_conv(to_replace[qmpom__kxle])] = value[
                        qmpom__kxle]
                return mplq__dkx
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            mplq__dkx = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for qmpom__kxle in range(len(to_replace)):
                mplq__dkx[to_replace[qmpom__kxle]] = value[qmpom__kxle]
            return mplq__dkx
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.diff()')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            fznk__wuy = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    qcpap__pip = dict(ignore_index=ignore_index)
    pwjht__dci = dict(ignore_index=False)
    check_unsupported_args('Series.explode', qcpap__pip, pwjht__dci,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kvfxc__owowy = bodo.utils.conversion.index_to_array(index)
        fznk__wuy, ekfc__mje = bodo.libs.array_kernels.explode(arr,
            kvfxc__owowy)
        kqnwv__jacp = bodo.utils.conversion.index_from_array(ekfc__mje)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
            kqnwv__jacp, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.digitize()')
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            jcpus__wbdta = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                jcpus__wbdta[qmpom__kxle] = np.argmax(a[qmpom__kxle])
            return jcpus__wbdta
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            poyga__plm = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                poyga__plm[qmpom__kxle] = np.argmin(a[qmpom__kxle])
            return poyga__plm
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    qcpap__pip = dict(axis=axis, inplace=inplace, how=how)
    yre__ebuf = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', qcpap__pip, yre__ebuf,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xrii__riei = S.notna().values
            kvfxc__owowy = bodo.utils.conversion.extract_index_array(S)
            kqnwv__jacp = bodo.utils.conversion.convert_to_index(kvfxc__owowy
                [xrii__riei])
            fznk__wuy = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(bzy__nhiwq))
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                kqnwv__jacp, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            kvfxc__owowy = bodo.utils.conversion.extract_index_array(S)
            xrii__riei = S.notna().values
            kqnwv__jacp = bodo.utils.conversion.convert_to_index(kvfxc__owowy
                [xrii__riei])
            fznk__wuy = bzy__nhiwq[xrii__riei]
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                kqnwv__jacp, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    qcpap__pip = dict(freq=freq, axis=axis, fill_value=fill_value)
    bwxxw__yad = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.shift()')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    qcpap__pip = dict(fill_method=fill_method, limit=limit, freq=freq)
    bwxxw__yad = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.pct_change()')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
            f'Series.{func_name}()')
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
            f'Series.{func_name}()')
        _validate_arguments_mask_where(f'Series.{func_name}', 'Series', S,
            cond, other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            cuac__elizi = 'None'
        else:
            cuac__elizi = 'other'
        vbk__czhd = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            vbk__czhd += '  cond = ~cond\n'
        vbk__czhd += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        vbk__czhd += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        vbk__czhd += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        vbk__czhd += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {cuac__elizi})\n'
            )
        vbk__czhd += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        qkx__fbce = {}
        exec(vbk__czhd, {'bodo': bodo, 'np': np}, qkx__fbce)
        impl = qkx__fbce['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        gmxj__mch = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(gmxj__mch)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    qcpap__pip = dict(inplace=inplace, level=level, errors=errors, try_cast
        =try_cast)
    bwxxw__yad = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name=module_name)
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if isinstance(S, bodo.hiframes.pd_index_ext.RangeIndexType):
        arr = types.Array(types.int64, 1, 'C')
    else:
        arr = S.data
    if isinstance(other, SeriesType):
        _validate_self_other_mask_where(func_name, module_name, arr, other.data
            )
    else:
        _validate_self_other_mask_where(func_name, module_name, arr, other)
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )


def _validate_self_other_mask_where(func_name, module_name, arr, other,
    max_ndim=1, is_default=False):
    if not (isinstance(arr, types.Array) or isinstance(arr,
        BooleanArrayType) or isinstance(arr, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(arr, False) and arr.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() {module_name} data with type {arr} not yet supported'
            )
    jwgp__pcdcl = is_overload_constant_nan(other)
    if not (is_default or jwgp__pcdcl or is_scalar_type(other) or 
        isinstance(other, types.Array) and other.ndim >= 1 and other.ndim <=
        max_ndim or isinstance(other, SeriesType) and (isinstance(arr,
        types.Array) or arr.dtype in [bodo.string_type, bodo.bytes_type]) or
        is_str_arr_type(other) and (arr.dtype == bodo.string_type or 
        isinstance(arr, bodo.CategoricalArrayType) and arr.dtype.elem_type ==
        bodo.string_type) or isinstance(other, BinaryArrayType) and (arr.
        dtype == bodo.bytes_type or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type == bodo.bytes_type) or
        (not (isinstance(other, (StringArrayType, BinaryArrayType)) or 
        other == bodo.dict_str_arr_type) and (isinstance(arr.dtype, types.
        Integer) and (bodo.utils.utils.is_array_typ(other) and isinstance(
        other.dtype, types.Integer) or is_series_type(other) and isinstance
        (other.dtype, types.Integer))) or (bodo.utils.utils.is_array_typ(
        other) and arr.dtype == other.dtype or is_series_type(other) and 
        arr.dtype == other.dtype)) and (isinstance(arr, BooleanArrayType) or
        isinstance(arr, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for {module_name}."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            gmzvd__atfo = arr.dtype.elem_type
        else:
            gmzvd__atfo = arr.dtype
        if is_iterable_type(other):
            qgis__nml = other.dtype
        elif jwgp__pcdcl:
            qgis__nml = types.float64
        else:
            qgis__nml = types.unliteral(other)
        if not jwgp__pcdcl and not is_common_scalar_dtype([gmzvd__atfo,
            qgis__nml]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        qcpap__pip = dict(level=level, axis=axis)
        bwxxw__yad = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), qcpap__pip,
            bwxxw__yad, package_name='pandas', module_name='Series')
        jwtm__razk = other == string_type or is_overload_constant_str(other)
        gvon__xxw = is_iterable_type(other) and other.dtype == string_type
        myu__lmbs = S.dtype == string_type and (op == operator.add and (
            jwtm__razk or gvon__xxw) or op == operator.mul and isinstance(
            other, types.Integer))
        lunbg__yjlc = S.dtype == bodo.timedelta64ns
        hwwk__gnff = S.dtype == bodo.datetime64ns
        rtim__qyhk = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        pmsq__erfx = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        uhr__rypy = lunbg__yjlc and (rtim__qyhk or pmsq__erfx
            ) or hwwk__gnff and rtim__qyhk
        uhr__rypy = uhr__rypy and op == operator.add
        if not (isinstance(S.dtype, types.Number) or myu__lmbs or uhr__rypy):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        ttgb__lnyp = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            had__qbz = ttgb__lnyp.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and had__qbz == types.Array(types.bool_, 1, 'C'):
                had__qbz = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                fznk__wuy = bodo.utils.utils.alloc_type(n, had__qbz, (-1,))
                for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                    zwvrj__fgyv = bodo.libs.array_kernels.isna(arr, qmpom__kxle
                        )
                    if zwvrj__fgyv:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(fznk__wuy,
                                qmpom__kxle)
                        else:
                            fznk__wuy[qmpom__kxle] = op(fill_value, other)
                    else:
                        fznk__wuy[qmpom__kxle] = op(arr[qmpom__kxle], other)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        had__qbz = ttgb__lnyp.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and had__qbz == types.Array(
            types.bool_, 1, 'C'):
            had__qbz = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            vyamz__jti = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            fznk__wuy = bodo.utils.utils.alloc_type(n, had__qbz, (-1,))
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                zwvrj__fgyv = bodo.libs.array_kernels.isna(arr, qmpom__kxle)
                krjfh__wkx = bodo.libs.array_kernels.isna(vyamz__jti,
                    qmpom__kxle)
                if zwvrj__fgyv and krjfh__wkx:
                    bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                elif zwvrj__fgyv:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                    else:
                        fznk__wuy[qmpom__kxle] = op(fill_value, vyamz__jti[
                            qmpom__kxle])
                elif krjfh__wkx:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                    else:
                        fznk__wuy[qmpom__kxle] = op(arr[qmpom__kxle],
                            fill_value)
                else:
                    fznk__wuy[qmpom__kxle] = op(arr[qmpom__kxle],
                        vyamz__jti[qmpom__kxle])
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        ttgb__lnyp = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            had__qbz = ttgb__lnyp.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and had__qbz == types.Array(types.bool_, 1, 'C'):
                had__qbz = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                fznk__wuy = bodo.utils.utils.alloc_type(n, had__qbz, None)
                for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                    zwvrj__fgyv = bodo.libs.array_kernels.isna(arr, qmpom__kxle
                        )
                    if zwvrj__fgyv:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(fznk__wuy,
                                qmpom__kxle)
                        else:
                            fznk__wuy[qmpom__kxle] = op(other, fill_value)
                    else:
                        fznk__wuy[qmpom__kxle] = op(other, arr[qmpom__kxle])
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        had__qbz = ttgb__lnyp.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and had__qbz == types.Array(
            types.bool_, 1, 'C'):
            had__qbz = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            vyamz__jti = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            fznk__wuy = bodo.utils.utils.alloc_type(n, had__qbz, None)
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                zwvrj__fgyv = bodo.libs.array_kernels.isna(arr, qmpom__kxle)
                krjfh__wkx = bodo.libs.array_kernels.isna(vyamz__jti,
                    qmpom__kxle)
                fznk__wuy[qmpom__kxle] = op(vyamz__jti[qmpom__kxle], arr[
                    qmpom__kxle])
                if zwvrj__fgyv and krjfh__wkx:
                    bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                elif zwvrj__fgyv:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                    else:
                        fznk__wuy[qmpom__kxle] = op(vyamz__jti[qmpom__kxle],
                            fill_value)
                elif krjfh__wkx:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                    else:
                        fznk__wuy[qmpom__kxle] = op(fill_value, arr[
                            qmpom__kxle])
                else:
                    fznk__wuy[qmpom__kxle] = op(vyamz__jti[qmpom__kxle],
                        arr[qmpom__kxle])
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, ykqdj__lkdy in explicit_binop_funcs_two_ways.items():
        for name in ykqdj__lkdy:
            gmxj__mch = create_explicit_binary_op_overload(op)
            frgw__kvp = create_explicit_binary_reverse_op_overload(op)
            yvkbu__agkgi = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(gmxj__mch)
            overload_method(SeriesType, yvkbu__agkgi, no_unliteral=True)(
                frgw__kvp)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        gmxj__mch = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(gmxj__mch)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wxcg__sakl = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                fznk__wuy = dt64_arr_sub(arr, wxcg__sakl)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                fznk__wuy = np.empty(n, np.dtype('datetime64[ns]'))
                for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, qmpom__kxle):
                        bodo.libs.array_kernels.setna(fznk__wuy, qmpom__kxle)
                        continue
                    wuwt__jfgkn = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[qmpom__kxle]))
                    bes__vpaav = op(wuwt__jfgkn, rhs)
                    fznk__wuy[qmpom__kxle
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        bes__vpaav.value)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    wxcg__sakl = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    fznk__wuy = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(wxcg__sakl))
                    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wxcg__sakl = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                fznk__wuy = op(arr, wxcg__sakl)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    cfc__bag = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    fznk__wuy = op(bodo.utils.conversion.unbox_if_timestamp
                        (cfc__bag), arr)
                    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                cfc__bag = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                fznk__wuy = op(cfc__bag, arr)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        gmxj__mch = create_binary_op_overload(op)
        overload(op)(gmxj__mch)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    owmr__xwrxr = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, owmr__xwrxr)
        for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, qmpom__kxle
                ) or bodo.libs.array_kernels.isna(arg2, qmpom__kxle):
                bodo.libs.array_kernels.setna(S, qmpom__kxle)
                continue
            S[qmpom__kxle
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                qmpom__kxle]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[qmpom__kxle]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                vyamz__jti = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, vyamz__jti)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        gmxj__mch = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(gmxj__mch)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                fznk__wuy = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        gmxj__mch = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(gmxj__mch)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    fznk__wuy = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    vyamz__jti = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    fznk__wuy = ufunc(arr, vyamz__jti)
                    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    vyamz__jti = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    fznk__wuy = ufunc(arr, vyamz__jti)
                    return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        gmxj__mch = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(gmxj__mch)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        tlowg__kzbwk = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.
            copy(),))
        klc__yygi = np.arange(n),
        bodo.libs.timsort.sort(tlowg__kzbwk, 0, n, klc__yygi)
        return klc__yygi[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        ikp__vltjk = get_overload_const_str(downcast)
        if ikp__vltjk in ('integer', 'signed'):
            out_dtype = types.int64
        elif ikp__vltjk == 'unsigned':
            out_dtype = types.uint64
        else:
            assert ikp__vltjk == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            bzy__nhiwq = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            fznk__wuy = pd.to_numeric(bzy__nhiwq, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index,
                name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            zft__oiem = np.empty(n, np.float64)
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, qmpom__kxle):
                    bodo.libs.array_kernels.setna(zft__oiem, qmpom__kxle)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(zft__oiem,
                        qmpom__kxle, arg_a, qmpom__kxle)
            return zft__oiem
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            zft__oiem = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, qmpom__kxle):
                    bodo.libs.array_kernels.setna(zft__oiem, qmpom__kxle)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(zft__oiem,
                        qmpom__kxle, arg_a, qmpom__kxle)
            return zft__oiem
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        jvmnc__ios = if_series_to_array_type(args[0])
        if isinstance(jvmnc__ios, types.Array) and isinstance(jvmnc__ios.
            dtype, types.Integer):
            jvmnc__ios = types.Array(types.float64, 1, 'C')
        return jvmnc__ios(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'numpy.where()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(y,
        'numpy.where()')
    lfhet__rdgrw = bodo.utils.utils.is_array_typ(x, True)
    htxx__ipkeq = bodo.utils.utils.is_array_typ(y, True)
    vbk__czhd = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        vbk__czhd += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if lfhet__rdgrw and not bodo.utils.utils.is_array_typ(x, False):
        vbk__czhd += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if htxx__ipkeq and not bodo.utils.utils.is_array_typ(y, False):
        vbk__czhd += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    vbk__czhd += '  n = len(condition)\n'
    qvye__twcev = x.dtype if lfhet__rdgrw else types.unliteral(x)
    ygee__njqlu = y.dtype if htxx__ipkeq else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        qvye__twcev = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        ygee__njqlu = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    vbh__ynbuz = get_data(x)
    zov__ojlbn = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(klc__yygi) for
        klc__yygi in [vbh__ynbuz, zov__ojlbn])
    if zov__ojlbn == types.none:
        if isinstance(qvye__twcev, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif vbh__ynbuz == zov__ojlbn and not is_nullable:
        out_dtype = dtype_to_array_type(qvye__twcev)
    elif qvye__twcev == string_type or ygee__njqlu == string_type:
        out_dtype = bodo.string_array_type
    elif vbh__ynbuz == bytes_type or (lfhet__rdgrw and qvye__twcev ==
        bytes_type) and (zov__ojlbn == bytes_type or htxx__ipkeq and 
        ygee__njqlu == bytes_type):
        out_dtype = binary_array_type
    elif isinstance(qvye__twcev, bodo.PDCategoricalDtype):
        out_dtype = None
    elif qvye__twcev in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(qvye__twcev, 1, 'C')
    elif ygee__njqlu in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(ygee__njqlu, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(qvye__twcev), numba.np.numpy_support.
            as_dtype(ygee__njqlu)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(qvye__twcev, bodo.PDCategoricalDtype):
        iza__lglyr = 'x'
    else:
        iza__lglyr = 'out_dtype'
    vbk__czhd += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {iza__lglyr}, (-1,))\n')
    if isinstance(qvye__twcev, bodo.PDCategoricalDtype):
        vbk__czhd += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        vbk__czhd += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    vbk__czhd += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    vbk__czhd += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if lfhet__rdgrw:
        vbk__czhd += '      if bodo.libs.array_kernels.isna(x, j):\n'
        vbk__czhd += '        setna(out_arr, j)\n'
        vbk__czhd += '        continue\n'
    if isinstance(qvye__twcev, bodo.PDCategoricalDtype):
        vbk__czhd += '      out_codes[j] = x_codes[j]\n'
    else:
        vbk__czhd += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if lfhet__rdgrw else 'x'))
    vbk__czhd += '    else:\n'
    if htxx__ipkeq:
        vbk__czhd += '      if bodo.libs.array_kernels.isna(y, j):\n'
        vbk__czhd += '        setna(out_arr, j)\n'
        vbk__czhd += '        continue\n'
    if zov__ojlbn == types.none:
        if isinstance(qvye__twcev, bodo.PDCategoricalDtype):
            vbk__czhd += '      out_codes[j] = -1\n'
        else:
            vbk__czhd += '      setna(out_arr, j)\n'
    else:
        vbk__czhd += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if htxx__ipkeq else 'y'))
    vbk__czhd += '  return out_arr\n'
    qkx__fbce = {}
    exec(vbk__czhd, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, qkx__fbce)
    cromv__ilt = qkx__fbce['_impl']
    return cromv__ilt


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        pgpc__ylrip = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(pgpc__ylrip, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(pgpc__ylrip):
            xhy__drhu = pgpc__ylrip.data.dtype
        else:
            xhy__drhu = pgpc__ylrip.dtype
        if isinstance(xhy__drhu, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        bsb__rbmkr = pgpc__ylrip
    else:
        oqj__aebgk = []
        for pgpc__ylrip in choicelist:
            if not bodo.utils.utils.is_array_typ(pgpc__ylrip, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(pgpc__ylrip):
                xhy__drhu = pgpc__ylrip.data.dtype
            else:
                xhy__drhu = pgpc__ylrip.dtype
            if isinstance(xhy__drhu, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            oqj__aebgk.append(xhy__drhu)
        if not is_common_scalar_dtype(oqj__aebgk):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        bsb__rbmkr = choicelist[0]
    if is_series_type(bsb__rbmkr):
        bsb__rbmkr = bsb__rbmkr.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, bsb__rbmkr.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(bsb__rbmkr, types.Array) or isinstance(bsb__rbmkr,
        BooleanArrayType) or isinstance(bsb__rbmkr, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(bsb__rbmkr, False) and bsb__rbmkr.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {bsb__rbmkr} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    chndp__tixbs = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        wyo__wxl = choicelist.dtype
    else:
        abplk__agyze = False
        oqj__aebgk = []
        for pgpc__ylrip in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                pgpc__ylrip, 'numpy.select()')
            if is_nullable_type(pgpc__ylrip):
                abplk__agyze = True
            if is_series_type(pgpc__ylrip):
                xhy__drhu = pgpc__ylrip.data.dtype
            else:
                xhy__drhu = pgpc__ylrip.dtype
            if isinstance(xhy__drhu, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            oqj__aebgk.append(xhy__drhu)
        bgie__hphu, wvzgw__qlbl = get_common_scalar_dtype(oqj__aebgk)
        if not wvzgw__qlbl:
            raise BodoError('Internal error in overload_np_select')
        amjt__gexhd = dtype_to_array_type(bgie__hphu)
        if abplk__agyze:
            amjt__gexhd = to_nullable_type(amjt__gexhd)
        wyo__wxl = amjt__gexhd
    if isinstance(wyo__wxl, SeriesType):
        wyo__wxl = wyo__wxl.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        fifuf__cyab = True
    else:
        fifuf__cyab = False
    lteb__mfre = False
    imqs__qgql = False
    if fifuf__cyab:
        if isinstance(wyo__wxl.dtype, types.Number):
            pass
        elif wyo__wxl.dtype == types.bool_:
            imqs__qgql = True
        else:
            lteb__mfre = True
            wyo__wxl = to_nullable_type(wyo__wxl)
    elif default == types.none or is_overload_constant_nan(default):
        lteb__mfre = True
        wyo__wxl = to_nullable_type(wyo__wxl)
    vbk__czhd = 'def np_select_impl(condlist, choicelist, default=0):\n'
    vbk__czhd += '  if len(condlist) != len(choicelist):\n'
    vbk__czhd += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    vbk__czhd += '  output_len = len(choicelist[0])\n'
    vbk__czhd += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    vbk__czhd += '  for i in range(output_len):\n'
    if lteb__mfre:
        vbk__czhd += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif imqs__qgql:
        vbk__czhd += '    out[i] = False\n'
    else:
        vbk__czhd += '    out[i] = default\n'
    if chndp__tixbs:
        vbk__czhd += '  for i in range(len(condlist) - 1, -1, -1):\n'
        vbk__czhd += '    cond = condlist[i]\n'
        vbk__czhd += '    choice = choicelist[i]\n'
        vbk__czhd += '    out = np.where(cond, choice, out)\n'
    else:
        for qmpom__kxle in range(len(choicelist) - 1, -1, -1):
            vbk__czhd += f'  cond = condlist[{qmpom__kxle}]\n'
            vbk__czhd += f'  choice = choicelist[{qmpom__kxle}]\n'
            vbk__czhd += f'  out = np.where(cond, choice, out)\n'
    vbk__czhd += '  return out'
    qkx__fbce = dict()
    exec(vbk__czhd, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': wyo__wxl}, qkx__fbce)
    impl = qkx__fbce['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        fznk__wuy = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    qcpap__pip = dict(subset=subset, keep=keep, inplace=inplace)
    bwxxw__yad = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        fgbwq__pjvp = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (fgbwq__pjvp,), kvfxc__owowy = bodo.libs.array_kernels.drop_duplicates(
            (fgbwq__pjvp,), index, 1)
        index = bodo.utils.conversion.index_from_array(kvfxc__owowy)
        return bodo.hiframes.pd_series_ext.init_series(fgbwq__pjvp, index, name
            )
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    gtcw__whatz = element_type(S.data)
    if not is_common_scalar_dtype([gtcw__whatz, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([gtcw__whatz, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        fznk__wuy = np.empty(n, np.bool_)
        for qmpom__kxle in numba.parfors.parfor.internal_prange(n):
            mej__odal = bodo.utils.conversion.box_if_dt64(arr[qmpom__kxle])
            if inclusive == 'both':
                fznk__wuy[qmpom__kxle
                    ] = mej__odal <= right and mej__odal >= left
            else:
                fznk__wuy[qmpom__kxle] = mej__odal < right and mej__odal > left
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    qcpap__pip = dict(axis=axis)
    bwxxw__yad = dict(axis=None)
    check_unsupported_args('Series.repeat', qcpap__pip, bwxxw__yad,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.repeat()')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            kvfxc__owowy = bodo.utils.conversion.index_to_array(index)
            fznk__wuy = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            ekfc__mje = bodo.libs.array_kernels.repeat_kernel(kvfxc__owowy,
                repeats)
            kqnwv__jacp = bodo.utils.conversion.index_from_array(ekfc__mje)
            return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
                kqnwv__jacp, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kvfxc__owowy = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        fznk__wuy = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        ekfc__mje = bodo.libs.array_kernels.repeat_kernel(kvfxc__owowy, repeats
            )
        kqnwv__jacp = bodo.utils.conversion.index_from_array(ekfc__mje)
        return bodo.hiframes.pd_series_ext.init_series(fznk__wuy,
            kqnwv__jacp, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        klc__yygi = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(klc__yygi)
        zgiwj__zbni = {}
        for qmpom__kxle in range(n):
            mej__odal = bodo.utils.conversion.box_if_dt64(klc__yygi[
                qmpom__kxle])
            zgiwj__zbni[index[qmpom__kxle]] = mej__odal
        return zgiwj__zbni
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    vcyis__kfo = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            qhof__pnj = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(vcyis__kfo)
    elif is_literal_type(name):
        qhof__pnj = get_literal_value(name)
    else:
        raise_bodo_error(vcyis__kfo)
    qhof__pnj = 0 if qhof__pnj is None else qhof__pnj
    bht__gpjqy = ColNamesMetaType((qhof__pnj,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            bht__gpjqy)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
