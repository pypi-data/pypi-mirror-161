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
            ieii__ngnzz = bodo.hiframes.pd_series_ext.get_series_data(s)
            pbgx__fop = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                ieii__ngnzz)
            return pbgx__fop
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
            vaj__ycg = list()
            for qmyu__yjf in range(len(S)):
                vaj__ycg.append(S.iat[qmyu__yjf])
            return vaj__ycg
        return impl_float

    def impl(S):
        vaj__ycg = list()
        for qmyu__yjf in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, qmyu__yjf):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            vaj__ycg.append(S.iat[qmyu__yjf])
        return vaj__ycg
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    tmzri__onqq = dict(dtype=dtype, copy=copy, na_value=na_value)
    jahka__sna = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    tmzri__onqq = dict(name=name, inplace=inplace)
    jahka__sna = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', tmzri__onqq, jahka__sna,
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
        hcwz__uxdcu = ', '.join(['index_arrs[{}]'.format(qmyu__yjf) for
            qmyu__yjf in range(S.index.nlevels)])
    else:
        hcwz__uxdcu = '    bodo.utils.conversion.index_to_array(index)\n'
    vuip__cwxr = 'index' if 'index' != series_name else 'level_0'
    lryw__sng = get_index_names(S.index, 'Series.reset_index()', vuip__cwxr)
    columns = [name for name in lryw__sng]
    columns.append(series_name)
    ohw__ozd = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    ohw__ozd += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ohw__ozd += '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        ohw__ozd += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    ohw__ozd += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    ohw__ozd += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({hcwz__uxdcu}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    nuoy__zfcy = {}
    exec(ohw__ozd, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, nuoy__zfcy)
    kcles__xwoj = nuoy__zfcy['_impl']
    return kcles__xwoj


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sdxmt__wyvoh = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
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
        sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[qmyu__yjf]):
                bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
            else:
                sdxmt__wyvoh[qmyu__yjf] = np.round(arr[qmyu__yjf], decimals)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    jahka__sna = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', tmzri__onqq, jahka__sna,
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
        nvm__mipm = bodo.hiframes.pd_series_ext.get_series_data(S)
        ybck__telz = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        caxyt__ftfsy = 0
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(nvm__mipm)):
            kdhdu__nwafm = 0
            nnbf__cri = bodo.libs.array_kernels.isna(nvm__mipm, qmyu__yjf)
            isw__koa = bodo.libs.array_kernels.isna(ybck__telz, qmyu__yjf)
            if nnbf__cri and not isw__koa or not nnbf__cri and isw__koa:
                kdhdu__nwafm = 1
            elif not nnbf__cri:
                if nvm__mipm[qmyu__yjf] != ybck__telz[qmyu__yjf]:
                    kdhdu__nwafm = 1
            caxyt__ftfsy += kdhdu__nwafm
        return caxyt__ftfsy == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    tmzri__onqq = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    jahka__sna = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    tmzri__onqq = dict(level=level)
    jahka__sna = dict(level=None)
    check_unsupported_args('Series.mad', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    qcn__abuj = types.float64
    bmy__auk = types.float64
    if S.dtype == types.float32:
        qcn__abuj = types.float32
        bmy__auk = types.float32
    noma__nruxa = qcn__abuj(0)
    xjxo__woagg = bmy__auk(0)
    dicqn__liacs = bmy__auk(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        mlido__ipeo = noma__nruxa
        caxyt__ftfsy = xjxo__woagg
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(A)):
            kdhdu__nwafm = noma__nruxa
            gixe__qbs = xjxo__woagg
            if not bodo.libs.array_kernels.isna(A, qmyu__yjf) or not skipna:
                kdhdu__nwafm = A[qmyu__yjf]
                gixe__qbs = dicqn__liacs
            mlido__ipeo += kdhdu__nwafm
            caxyt__ftfsy += gixe__qbs
        zoeub__kmqh = bodo.hiframes.series_kernels._mean_handle_nan(mlido__ipeo
            , caxyt__ftfsy)
        xkwg__ykx = noma__nruxa
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(A)):
            kdhdu__nwafm = noma__nruxa
            if not bodo.libs.array_kernels.isna(A, qmyu__yjf) or not skipna:
                kdhdu__nwafm = abs(A[qmyu__yjf] - zoeub__kmqh)
            xkwg__ykx += kdhdu__nwafm
        dwad__mcji = bodo.hiframes.series_kernels._mean_handle_nan(xkwg__ykx,
            caxyt__ftfsy)
        return dwad__mcji
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    tmzri__onqq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    jahka__sna = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', tmzri__onqq, jahka__sna,
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
        hau__tluhy = 0
        yrlev__wtuy = 0
        caxyt__ftfsy = 0
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(A)):
            kdhdu__nwafm = 0
            gixe__qbs = 0
            if not bodo.libs.array_kernels.isna(A, qmyu__yjf) or not skipna:
                kdhdu__nwafm = A[qmyu__yjf]
                gixe__qbs = 1
            hau__tluhy += kdhdu__nwafm
            yrlev__wtuy += kdhdu__nwafm * kdhdu__nwafm
            caxyt__ftfsy += gixe__qbs
        dfa__uhegd = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            hau__tluhy, yrlev__wtuy, caxyt__ftfsy, ddof)
        agve__swcxe = bodo.hiframes.series_kernels._sem_handle_nan(dfa__uhegd,
            caxyt__ftfsy)
        return agve__swcxe
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', tmzri__onqq, jahka__sna,
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
        hau__tluhy = 0.0
        yrlev__wtuy = 0.0
        waf__mjkb = 0.0
        amum__rdcpg = 0.0
        caxyt__ftfsy = 0
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(A)):
            kdhdu__nwafm = 0.0
            gixe__qbs = 0
            if not bodo.libs.array_kernels.isna(A, qmyu__yjf) or not skipna:
                kdhdu__nwafm = np.float64(A[qmyu__yjf])
                gixe__qbs = 1
            hau__tluhy += kdhdu__nwafm
            yrlev__wtuy += kdhdu__nwafm ** 2
            waf__mjkb += kdhdu__nwafm ** 3
            amum__rdcpg += kdhdu__nwafm ** 4
            caxyt__ftfsy += gixe__qbs
        dfa__uhegd = bodo.hiframes.series_kernels.compute_kurt(hau__tluhy,
            yrlev__wtuy, waf__mjkb, amum__rdcpg, caxyt__ftfsy)
        return dfa__uhegd
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', tmzri__onqq, jahka__sna,
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
        hau__tluhy = 0.0
        yrlev__wtuy = 0.0
        waf__mjkb = 0.0
        caxyt__ftfsy = 0
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(A)):
            kdhdu__nwafm = 0.0
            gixe__qbs = 0
            if not bodo.libs.array_kernels.isna(A, qmyu__yjf) or not skipna:
                kdhdu__nwafm = np.float64(A[qmyu__yjf])
                gixe__qbs = 1
            hau__tluhy += kdhdu__nwafm
            yrlev__wtuy += kdhdu__nwafm ** 2
            waf__mjkb += kdhdu__nwafm ** 3
            caxyt__ftfsy += gixe__qbs
        dfa__uhegd = bodo.hiframes.series_kernels.compute_skew(hau__tluhy,
            yrlev__wtuy, waf__mjkb, caxyt__ftfsy)
        return dfa__uhegd
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', tmzri__onqq, jahka__sna,
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
        nvm__mipm = bodo.hiframes.pd_series_ext.get_series_data(S)
        ybck__telz = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        dny__utsnr = 0
        for qmyu__yjf in numba.parfors.parfor.internal_prange(len(nvm__mipm)):
            ovj__blouv = nvm__mipm[qmyu__yjf]
            yqob__zsf = ybck__telz[qmyu__yjf]
            dny__utsnr += ovj__blouv * yqob__zsf
        return dny__utsnr
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    tmzri__onqq = dict(skipna=skipna)
    jahka__sna = dict(skipna=True)
    check_unsupported_args('Series.cumsum', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(skipna=skipna)
    jahka__sna = dict(skipna=True)
    check_unsupported_args('Series.cumprod', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(skipna=skipna)
    jahka__sna = dict(skipna=True)
    check_unsupported_args('Series.cummin', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(skipna=skipna)
    jahka__sna = dict(skipna=True)
    check_unsupported_args('Series.cummax', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    jahka__sna = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        newr__jrdil = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, newr__jrdil, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    tmzri__onqq = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    jahka__sna = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(level=level)
    jahka__sna = dict(level=None)
    check_unsupported_args('Series.count', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    tmzri__onqq = dict(method=method, min_periods=min_periods)
    jahka__sna = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        krje__ckxj = S.sum()
        hak__pjenz = other.sum()
        a = n * (S * other).sum() - krje__ckxj * hak__pjenz
        tqwvl__dmrc = n * (S ** 2).sum() - krje__ckxj ** 2
        zkyj__aeyx = n * (other ** 2).sum() - hak__pjenz ** 2
        return a / np.sqrt(tqwvl__dmrc * zkyj__aeyx)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    tmzri__onqq = dict(min_periods=min_periods)
    jahka__sna = dict(min_periods=None)
    check_unsupported_args('Series.cov', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        krje__ckxj = S.mean()
        hak__pjenz = other.mean()
        zncbl__cyks = ((S - krje__ckxj) * (other - hak__pjenz)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(zncbl__cyks, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            sjroa__ncz = np.sign(sum_val)
            return np.inf * sjroa__ncz
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    tmzri__onqq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    jahka__sna = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    jahka__sna = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(axis=axis, skipna=skipna)
    jahka__sna = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(axis=axis, skipna=skipna)
    jahka__sna = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', tmzri__onqq, jahka__sna,
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
    tmzri__onqq = dict(level=level, numeric_only=numeric_only)
    jahka__sna = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', tmzri__onqq, jahka__sna,
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
        kgvd__dcv = arr[:n]
        fsnv__enm = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(kgvd__dcv, fsnv__enm,
            name)
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
        mpe__jhi = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kgvd__dcv = arr[mpe__jhi:]
        fsnv__enm = index[mpe__jhi:]
        return bodo.hiframes.pd_series_ext.init_series(kgvd__dcv, fsnv__enm,
            name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    khtr__yygzq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in khtr__yygzq:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            zyq__dkjlu = index[0]
            ytti__voylq = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                zyq__dkjlu, False))
        else:
            ytti__voylq = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kgvd__dcv = arr[:ytti__voylq]
        fsnv__enm = index[:ytti__voylq]
        return bodo.hiframes.pd_series_ext.init_series(kgvd__dcv, fsnv__enm,
            name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    khtr__yygzq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in khtr__yygzq:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            nzkss__zbguq = index[-1]
            ytti__voylq = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                nzkss__zbguq, True))
        else:
            ytti__voylq = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        kgvd__dcv = arr[len(arr) - ytti__voylq:]
        fsnv__enm = index[len(arr) - ytti__voylq:]
        return bodo.hiframes.pd_series_ext.init_series(kgvd__dcv, fsnv__enm,
            name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        nzi__tmz = bodo.utils.conversion.index_to_array(index)
        ziyh__lflg, yckik__apuw = (bodo.libs.array_kernels.
            first_last_valid_index(arr, nzi__tmz))
        return yckik__apuw if ziyh__lflg else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        nzi__tmz = bodo.utils.conversion.index_to_array(index)
        ziyh__lflg, yckik__apuw = (bodo.libs.array_kernels.
            first_last_valid_index(arr, nzi__tmz, False))
        return yckik__apuw if ziyh__lflg else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    tmzri__onqq = dict(keep=keep)
    jahka__sna = dict(keep='first')
    check_unsupported_args('Series.nlargest', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        nzi__tmz = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sdxmt__wyvoh, zaegs__rsvi = bodo.libs.array_kernels.nlargest(arr,
            nzi__tmz, n, True, bodo.hiframes.series_kernels.gt_f)
        afecv__sud = bodo.utils.conversion.convert_to_index(zaegs__rsvi)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
            afecv__sud, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    tmzri__onqq = dict(keep=keep)
    jahka__sna = dict(keep='first')
    check_unsupported_args('Series.nsmallest', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        nzi__tmz = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sdxmt__wyvoh, zaegs__rsvi = bodo.libs.array_kernels.nlargest(arr,
            nzi__tmz, n, False, bodo.hiframes.series_kernels.lt_f)
        afecv__sud = bodo.utils.conversion.convert_to_index(zaegs__rsvi)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
            afecv__sud, name)
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
    tmzri__onqq = dict(errors=errors)
    jahka__sna = dict(errors='raise')
    check_unsupported_args('Series.astype', tmzri__onqq, jahka__sna,
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
        sdxmt__wyvoh = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    tmzri__onqq = dict(axis=axis, is_copy=is_copy)
    jahka__sna = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        mpbs__osc = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[mpbs__osc],
            index[mpbs__osc], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    tmzri__onqq = dict(axis=axis, kind=kind, order=order)
    jahka__sna = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        coc__bysv = S.notna().values
        if not coc__bysv.all():
            sdxmt__wyvoh = np.full(n, -1, np.int64)
            sdxmt__wyvoh[coc__bysv] = argsort(arr[coc__bysv])
        else:
            sdxmt__wyvoh = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    tmzri__onqq = dict(axis=axis, numeric_only=numeric_only)
    jahka__sna = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', tmzri__onqq, jahka__sna,
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
        sdxmt__wyvoh = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    tmzri__onqq = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    jahka__sna = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    cgjav__mns = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xlo__zauq = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, cgjav__mns)
        rcsqi__vqy = xlo__zauq.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        sdxmt__wyvoh = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            rcsqi__vqy, 0)
        afecv__sud = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            rcsqi__vqy)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
            afecv__sud, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    tmzri__onqq = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    jahka__sna = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    orvpc__kvcx = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        xlo__zauq = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, orvpc__kvcx)
        rcsqi__vqy = xlo__zauq.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        sdxmt__wyvoh = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            rcsqi__vqy, 0)
        afecv__sud = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            rcsqi__vqy)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
            afecv__sud, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    rjd__rlojg = is_overload_true(is_nullable)
    ohw__ozd = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    ohw__ozd += '  numba.parfors.parfor.init_prange()\n'
    ohw__ozd += '  n = len(arr)\n'
    if rjd__rlojg:
        ohw__ozd += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        ohw__ozd += '  out_arr = np.empty(n, np.int64)\n'
    ohw__ozd += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    ohw__ozd += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if rjd__rlojg:
        ohw__ozd += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        ohw__ozd += '      out_arr[i] = -1\n'
    ohw__ozd += '      continue\n'
    ohw__ozd += '    val = arr[i]\n'
    ohw__ozd += '    if include_lowest and val == bins[0]:\n'
    ohw__ozd += '      ind = 1\n'
    ohw__ozd += '    else:\n'
    ohw__ozd += '      ind = np.searchsorted(bins, val)\n'
    ohw__ozd += '    if ind == 0 or ind == len(bins):\n'
    if rjd__rlojg:
        ohw__ozd += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        ohw__ozd += '      out_arr[i] = -1\n'
    ohw__ozd += '    else:\n'
    ohw__ozd += '      out_arr[i] = ind - 1\n'
    ohw__ozd += '  return out_arr\n'
    nuoy__zfcy = {}
    exec(ohw__ozd, {'bodo': bodo, 'np': np, 'numba': numba}, nuoy__zfcy)
    impl = nuoy__zfcy['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        obeq__hxcgx, ipr__plj = np.divmod(x, 1)
        if obeq__hxcgx == 0:
            pcdvk__muscw = -int(np.floor(np.log10(abs(ipr__plj)))
                ) - 1 + precision
        else:
            pcdvk__muscw = precision
        return np.around(x, pcdvk__muscw)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        midu__qfir = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(midu__qfir)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        dmhwp__svx = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            qlm__seb = bins.copy()
            if right and include_lowest:
                qlm__seb[0] = qlm__seb[0] - dmhwp__svx
            jzh__iuh = bodo.libs.interval_arr_ext.init_interval_array(qlm__seb
                [:-1], qlm__seb[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(jzh__iuh,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        qlm__seb = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            qlm__seb[0] = qlm__seb[0] - 10.0 ** -precision
        jzh__iuh = bodo.libs.interval_arr_ext.init_interval_array(qlm__seb[
            :-1], qlm__seb[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(jzh__iuh, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        tamm__fku = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        eiu__ynvyt = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        sdxmt__wyvoh = np.zeros(nbins, np.int64)
        for qmyu__yjf in range(len(tamm__fku)):
            sdxmt__wyvoh[eiu__ynvyt[qmyu__yjf]] = tamm__fku[qmyu__yjf]
        return sdxmt__wyvoh
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
            qnmt__hdqpx = (max_val - min_val) * 0.001
            if right:
                bins[0] -= qnmt__hdqpx
            else:
                bins[-1] += qnmt__hdqpx
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    tmzri__onqq = dict(dropna=dropna)
    jahka__sna = dict(dropna=True)
    check_unsupported_args('Series.value_counts', tmzri__onqq, jahka__sna,
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
    lddi__bkgm = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    ohw__ozd = 'def impl(\n'
    ohw__ozd += '    S,\n'
    ohw__ozd += '    normalize=False,\n'
    ohw__ozd += '    sort=True,\n'
    ohw__ozd += '    ascending=False,\n'
    ohw__ozd += '    bins=None,\n'
    ohw__ozd += '    dropna=True,\n'
    ohw__ozd += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    ohw__ozd += '):\n'
    ohw__ozd += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ohw__ozd += '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n'
    ohw__ozd += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if lddi__bkgm:
        ohw__ozd += '    right = True\n'
        ohw__ozd += _gen_bins_handling(bins, S.dtype)
        ohw__ozd += '    arr = get_bin_inds(bins, arr)\n'
    ohw__ozd += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    ohw__ozd += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    ohw__ozd += '    )\n'
    ohw__ozd += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if lddi__bkgm:
        ohw__ozd += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        ohw__ozd += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        ohw__ozd += '    index = get_bin_labels(bins)\n'
    else:
        ohw__ozd += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        ohw__ozd += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        ohw__ozd += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        ohw__ozd += '    )\n'
        ohw__ozd += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    ohw__ozd += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        ohw__ozd += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        puy__tobsg = 'len(S)' if lddi__bkgm else 'count_arr.sum()'
        ohw__ozd += f'    res = res / float({puy__tobsg})\n'
    ohw__ozd += '    return res\n'
    nuoy__zfcy = {}
    exec(ohw__ozd, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, nuoy__zfcy)
    impl = nuoy__zfcy['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    ohw__ozd = ''
    if isinstance(bins, types.Integer):
        ohw__ozd += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        ohw__ozd += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            ohw__ozd += '    min_val = min_val.value\n'
            ohw__ozd += '    max_val = max_val.value\n'
        ohw__ozd += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            ohw__ozd += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        ohw__ozd += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return ohw__ozd


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    tmzri__onqq = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    jahka__sna = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    ohw__ozd = 'def impl(\n'
    ohw__ozd += '    x,\n'
    ohw__ozd += '    bins,\n'
    ohw__ozd += '    right=True,\n'
    ohw__ozd += '    labels=None,\n'
    ohw__ozd += '    retbins=False,\n'
    ohw__ozd += '    precision=3,\n'
    ohw__ozd += '    include_lowest=False,\n'
    ohw__ozd += "    duplicates='raise',\n"
    ohw__ozd += '    ordered=True\n'
    ohw__ozd += '):\n'
    if isinstance(x, SeriesType):
        ohw__ozd += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        ohw__ozd += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        ohw__ozd += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        ohw__ozd += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    ohw__ozd += _gen_bins_handling(bins, x.dtype)
    ohw__ozd += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    ohw__ozd += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    ohw__ozd += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    ohw__ozd += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        ohw__ozd += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        ohw__ozd += '    return res\n'
    else:
        ohw__ozd += '    return out_arr\n'
    nuoy__zfcy = {}
    exec(ohw__ozd, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, nuoy__zfcy)
    impl = nuoy__zfcy['impl']
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
    tmzri__onqq = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    jahka__sna = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        fej__llqd = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, fej__llqd)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    tmzri__onqq = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze
        =squeeze, observed=observed, dropna=dropna)
    jahka__sna = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', tmzri__onqq, jahka__sna,
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
        stso__gzl = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            lvya__xfk = bodo.utils.conversion.coerce_to_array(index)
            xlo__zauq = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                lvya__xfk, arr), index, stso__gzl)
            return xlo__zauq.groupby(' ')['']
        return impl_index
    izghe__yzvf = by
    if isinstance(by, SeriesType):
        izghe__yzvf = by.data
    if isinstance(izghe__yzvf, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    iyylq__ezqm = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        lvya__xfk = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        xlo__zauq = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            lvya__xfk, arr), index, iyylq__ezqm)
        return xlo__zauq.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    tmzri__onqq = dict(verify_integrity=verify_integrity)
    jahka__sna = dict(verify_integrity=False)
    check_unsupported_args('Series.append', tmzri__onqq, jahka__sna,
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
            xgpl__axjnr = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            sdxmt__wyvoh = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(sdxmt__wyvoh, A, xgpl__axjnr, False)
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sdxmt__wyvoh = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    tmzri__onqq = dict(interpolation=interpolation)
    jahka__sna = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            sdxmt__wyvoh = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
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
        mil__ixwx = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(mil__ixwx, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    tmzri__onqq = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    jahka__sna = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', tmzri__onqq, jahka__sna,
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
        ecz__bby = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ecz__bby = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    ohw__ozd = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {ecz__bby}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    ncb__razd = dict()
    exec(ohw__ozd, {'bodo': bodo, 'numba': numba}, ncb__razd)
    djc__vqhq = ncb__razd['impl']
    return djc__vqhq


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        ecz__bby = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ecz__bby = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    ohw__ozd = 'def impl(S,\n'
    ohw__ozd += '     value=None,\n'
    ohw__ozd += '    method=None,\n'
    ohw__ozd += '    axis=None,\n'
    ohw__ozd += '    inplace=False,\n'
    ohw__ozd += '    limit=None,\n'
    ohw__ozd += '   downcast=None,\n'
    ohw__ozd += '):\n'
    ohw__ozd += '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    ohw__ozd += '    n = len(in_arr)\n'
    ohw__ozd += f'    out_arr = {ecz__bby}(n, -1)\n'
    ohw__ozd += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    ohw__ozd += '        s = in_arr[j]\n'
    ohw__ozd += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    ohw__ozd += '            s = value\n'
    ohw__ozd += '        out_arr[j] = s\n'
    ohw__ozd += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    ncb__razd = dict()
    exec(ohw__ozd, {'bodo': bodo, 'numba': numba}, ncb__razd)
    djc__vqhq = ncb__razd['impl']
    return djc__vqhq


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
    snzy__rqxvl = bodo.hiframes.pd_series_ext.get_series_data(value)
    for qmyu__yjf in numba.parfors.parfor.internal_prange(len(kzd__yrnr)):
        s = kzd__yrnr[qmyu__yjf]
        if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf
            ) and not bodo.libs.array_kernels.isna(snzy__rqxvl, qmyu__yjf):
            s = snzy__rqxvl[qmyu__yjf]
        kzd__yrnr[qmyu__yjf] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
    for qmyu__yjf in numba.parfors.parfor.internal_prange(len(kzd__yrnr)):
        s = kzd__yrnr[qmyu__yjf]
        if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf):
            s = value
        kzd__yrnr[qmyu__yjf] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    snzy__rqxvl = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(kzd__yrnr)
    sdxmt__wyvoh = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for uxot__siclm in numba.parfors.parfor.internal_prange(n):
        s = kzd__yrnr[uxot__siclm]
        if bodo.libs.array_kernels.isna(kzd__yrnr, uxot__siclm
            ) and not bodo.libs.array_kernels.isna(snzy__rqxvl, uxot__siclm):
            s = snzy__rqxvl[uxot__siclm]
        sdxmt__wyvoh[uxot__siclm] = s
        if bodo.libs.array_kernels.isna(kzd__yrnr, uxot__siclm
            ) and bodo.libs.array_kernels.isna(snzy__rqxvl, uxot__siclm):
            bodo.libs.array_kernels.setna(sdxmt__wyvoh, uxot__siclm)
    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    snzy__rqxvl = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(kzd__yrnr)
    sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, kzd__yrnr.dtype, (-1,))
    for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
        s = kzd__yrnr[qmyu__yjf]
        if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf
            ) and not bodo.libs.array_kernels.isna(snzy__rqxvl, qmyu__yjf):
            s = snzy__rqxvl[qmyu__yjf]
        sdxmt__wyvoh[qmyu__yjf] = s
    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    tmzri__onqq = dict(limit=limit, downcast=downcast)
    jahka__sna = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', tmzri__onqq, jahka__sna,
        package_name='pandas', module_name='Series')
    yokk__xygnk = not is_overload_none(value)
    ponvu__jcg = not is_overload_none(method)
    if yokk__xygnk and ponvu__jcg:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not yokk__xygnk and not ponvu__jcg:
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
    if ponvu__jcg:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        hgq__jpahj = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(hgq__jpahj)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(hgq__jpahj)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    gjhg__qap = element_type(S.data)
    yec__qvtt = None
    if yokk__xygnk:
        yec__qvtt = element_type(types.unliteral(value))
    if yec__qvtt and not can_replace(gjhg__qap, yec__qvtt):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {yec__qvtt} with series type {gjhg__qap}'
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
        dku__bgur = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                snzy__rqxvl = bodo.hiframes.pd_series_ext.get_series_data(value
                    )
                n = len(kzd__yrnr)
                sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, dku__bgur, (-1,))
                for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf
                        ) and bodo.libs.array_kernels.isna(snzy__rqxvl,
                        qmyu__yjf):
                        bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                        continue
                    if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf):
                        sdxmt__wyvoh[qmyu__yjf
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            snzy__rqxvl[qmyu__yjf])
                        continue
                    sdxmt__wyvoh[qmyu__yjf
                        ] = bodo.utils.conversion.unbox_if_timestamp(kzd__yrnr
                        [qmyu__yjf])
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return fillna_series_impl
        if ponvu__jcg:
            wara__qhk = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(gjhg__qap, (types.Integer, types.Float)
                ) and gjhg__qap not in wara__qhk:
                raise BodoError(
                    f"Series.fillna(): series of type {gjhg__qap} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                sdxmt__wyvoh = bodo.libs.array_kernels.ffill_bfill_arr(
                    kzd__yrnr, method)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(kzd__yrnr)
            sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, dku__bgur, (-1,))
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(kzd__yrnr[
                    qmyu__yjf])
                if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf):
                    s = value
                sdxmt__wyvoh[qmyu__yjf] = s
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        laqji__rubk = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        tmzri__onqq = dict(limit=limit, downcast=downcast)
        jahka__sna = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', tmzri__onqq,
            jahka__sna, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        gjhg__qap = element_type(S.data)
        wara__qhk = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(gjhg__qap, (types.Integer, types.Float)
            ) and gjhg__qap not in wara__qhk:
            raise BodoError(
                f'Series.{overload_name}(): series of type {gjhg__qap} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            sdxmt__wyvoh = bodo.libs.array_kernels.ffill_bfill_arr(kzd__yrnr,
                laqji__rubk)
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        yba__nkajy = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            yba__nkajy)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        naf__nlans = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(naf__nlans)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        naf__nlans = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(naf__nlans)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        naf__nlans = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(naf__nlans)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    tmzri__onqq = dict(inplace=inplace, limit=limit, regex=regex, method=method
        )
    hgh__vewtu = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', tmzri__onqq, hgh__vewtu,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    gjhg__qap = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        tfbjv__tmys = element_type(to_replace.key_type)
        yec__qvtt = element_type(to_replace.value_type)
    else:
        tfbjv__tmys = element_type(to_replace)
        yec__qvtt = element_type(value)
    xreun__ackl = None
    if gjhg__qap != types.unliteral(tfbjv__tmys):
        if bodo.utils.typing.equality_always_false(gjhg__qap, types.
            unliteral(tfbjv__tmys)
            ) or not bodo.utils.typing.types_equality_exists(gjhg__qap,
            tfbjv__tmys):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(gjhg__qap, (types.Float, types.Integer)
            ) or gjhg__qap == np.bool_:
            xreun__ackl = gjhg__qap
    if not can_replace(gjhg__qap, types.unliteral(yec__qvtt)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    atxes__sws = to_str_arr_if_dict_array(S.data)
    if isinstance(atxes__sws, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(kzd__yrnr.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(kzd__yrnr)
        sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, atxes__sws, (-1,))
        bdk__ajgg = build_replace_dict(to_replace, value, xreun__ackl)
        for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(kzd__yrnr, qmyu__yjf):
                bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                continue
            s = kzd__yrnr[qmyu__yjf]
            if s in bdk__ajgg:
                s = bdk__ajgg[s]
            sdxmt__wyvoh[qmyu__yjf] = s
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    niif__jvv = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    wde__gbz = is_iterable_type(to_replace)
    gnvnq__izanq = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    aeb__qzylg = is_iterable_type(value)
    if niif__jvv and gnvnq__izanq:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                bdk__ajgg = {}
                bdk__ajgg[key_dtype_conv(to_replace)] = value
                return bdk__ajgg
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            bdk__ajgg = {}
            bdk__ajgg[to_replace] = value
            return bdk__ajgg
        return impl
    if wde__gbz and gnvnq__izanq:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                bdk__ajgg = {}
                for unwtb__bozgk in to_replace:
                    bdk__ajgg[key_dtype_conv(unwtb__bozgk)] = value
                return bdk__ajgg
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            bdk__ajgg = {}
            for unwtb__bozgk in to_replace:
                bdk__ajgg[unwtb__bozgk] = value
            return bdk__ajgg
        return impl
    if wde__gbz and aeb__qzylg:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                bdk__ajgg = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for qmyu__yjf in range(len(to_replace)):
                    bdk__ajgg[key_dtype_conv(to_replace[qmyu__yjf])] = value[
                        qmyu__yjf]
                return bdk__ajgg
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            bdk__ajgg = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for qmyu__yjf in range(len(to_replace)):
                bdk__ajgg[to_replace[qmyu__yjf]] = value[qmyu__yjf]
            return bdk__ajgg
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
            sdxmt__wyvoh = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo
                .hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sdxmt__wyvoh = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    tmzri__onqq = dict(ignore_index=ignore_index)
    xudqk__xiiwv = dict(ignore_index=False)
    check_unsupported_args('Series.explode', tmzri__onqq, xudqk__xiiwv,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nzi__tmz = bodo.utils.conversion.index_to_array(index)
        sdxmt__wyvoh, czklq__uxqe = bodo.libs.array_kernels.explode(arr,
            nzi__tmz)
        afecv__sud = bodo.utils.conversion.index_from_array(czklq__uxqe)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
            afecv__sud, name)
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
            cck__gyrkl = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                cck__gyrkl[qmyu__yjf] = np.argmax(a[qmyu__yjf])
            return cck__gyrkl
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            pkm__nncn = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                pkm__nncn[qmyu__yjf] = np.argmin(a[qmyu__yjf])
            return pkm__nncn
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
    tmzri__onqq = dict(axis=axis, inplace=inplace, how=how)
    byqpw__zhqd = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', tmzri__onqq, byqpw__zhqd,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            coc__bysv = S.notna().values
            nzi__tmz = bodo.utils.conversion.extract_index_array(S)
            afecv__sud = bodo.utils.conversion.convert_to_index(nzi__tmz[
                coc__bysv])
            sdxmt__wyvoh = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(kzd__yrnr))
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                afecv__sud, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            nzi__tmz = bodo.utils.conversion.extract_index_array(S)
            coc__bysv = S.notna().values
            afecv__sud = bodo.utils.conversion.convert_to_index(nzi__tmz[
                coc__bysv])
            sdxmt__wyvoh = kzd__yrnr[coc__bysv]
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                afecv__sud, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    tmzri__onqq = dict(freq=freq, axis=axis, fill_value=fill_value)
    jahka__sna = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', tmzri__onqq, jahka__sna,
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
        sdxmt__wyvoh = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    tmzri__onqq = dict(fill_method=fill_method, limit=limit, freq=freq)
    jahka__sna = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', tmzri__onqq, jahka__sna,
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
        sdxmt__wyvoh = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
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
            xqgc__emvs = 'None'
        else:
            xqgc__emvs = 'other'
        ohw__ozd = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            ohw__ozd += '  cond = ~cond\n'
        ohw__ozd += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        ohw__ozd += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        ohw__ozd += '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
        ohw__ozd += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {xqgc__emvs})\n'
            )
        ohw__ozd += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        nuoy__zfcy = {}
        exec(ohw__ozd, {'bodo': bodo, 'np': np}, nuoy__zfcy)
        impl = nuoy__zfcy['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        yba__nkajy = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(yba__nkajy)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    tmzri__onqq = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    jahka__sna = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', tmzri__onqq, jahka__sna,
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
    vwq__enk = is_overload_constant_nan(other)
    if not (is_default or vwq__enk or is_scalar_type(other) or isinstance(
        other, types.Array) and other.ndim >= 1 and other.ndim <= max_ndim or
        isinstance(other, SeriesType) and (isinstance(arr, types.Array) or 
        arr.dtype in [bodo.string_type, bodo.bytes_type]) or 
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
            msrg__brsk = arr.dtype.elem_type
        else:
            msrg__brsk = arr.dtype
        if is_iterable_type(other):
            tpc__dykeb = other.dtype
        elif vwq__enk:
            tpc__dykeb = types.float64
        else:
            tpc__dykeb = types.unliteral(other)
        if not vwq__enk and not is_common_scalar_dtype([msrg__brsk, tpc__dykeb]
            ):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        tmzri__onqq = dict(level=level, axis=axis)
        jahka__sna = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), tmzri__onqq,
            jahka__sna, package_name='pandas', module_name='Series')
        orb__qzrd = other == string_type or is_overload_constant_str(other)
        wthax__wyf = is_iterable_type(other) and other.dtype == string_type
        jhrim__rlxi = S.dtype == string_type and (op == operator.add and (
            orb__qzrd or wthax__wyf) or op == operator.mul and isinstance(
            other, types.Integer))
        dkuf__kunor = S.dtype == bodo.timedelta64ns
        mggv__mfsng = S.dtype == bodo.datetime64ns
        jdqc__rjr = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        wtrzo__ufut = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        iew__jglc = dkuf__kunor and (jdqc__rjr or wtrzo__ufut
            ) or mggv__mfsng and jdqc__rjr
        iew__jglc = iew__jglc and op == operator.add
        if not (isinstance(S.dtype, types.Number) or jhrim__rlxi or iew__jglc):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        oyx__eww = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            atxes__sws = oyx__eww.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and atxes__sws == types.Array(types.bool_, 1, 'C'):
                atxes__sws = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, atxes__sws, (-1,)
                    )
                for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                    pcd__jub = bodo.libs.array_kernels.isna(arr, qmyu__yjf)
                    if pcd__jub:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(sdxmt__wyvoh,
                                qmyu__yjf)
                        else:
                            sdxmt__wyvoh[qmyu__yjf] = op(fill_value, other)
                    else:
                        sdxmt__wyvoh[qmyu__yjf] = op(arr[qmyu__yjf], other)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        atxes__sws = oyx__eww.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and atxes__sws == types.Array(
            types.bool_, 1, 'C'):
            atxes__sws = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xqegz__yhcyc = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, atxes__sws, (-1,))
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                pcd__jub = bodo.libs.array_kernels.isna(arr, qmyu__yjf)
                mmyv__xgb = bodo.libs.array_kernels.isna(xqegz__yhcyc,
                    qmyu__yjf)
                if pcd__jub and mmyv__xgb:
                    bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                elif pcd__jub:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                    else:
                        sdxmt__wyvoh[qmyu__yjf] = op(fill_value,
                            xqegz__yhcyc[qmyu__yjf])
                elif mmyv__xgb:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                    else:
                        sdxmt__wyvoh[qmyu__yjf] = op(arr[qmyu__yjf], fill_value
                            )
                else:
                    sdxmt__wyvoh[qmyu__yjf] = op(arr[qmyu__yjf],
                        xqegz__yhcyc[qmyu__yjf])
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
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
        oyx__eww = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            atxes__sws = oyx__eww.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and atxes__sws == types.Array(types.bool_, 1, 'C'):
                atxes__sws = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, atxes__sws, None)
                for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                    pcd__jub = bodo.libs.array_kernels.isna(arr, qmyu__yjf)
                    if pcd__jub:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(sdxmt__wyvoh,
                                qmyu__yjf)
                        else:
                            sdxmt__wyvoh[qmyu__yjf] = op(other, fill_value)
                    else:
                        sdxmt__wyvoh[qmyu__yjf] = op(other, arr[qmyu__yjf])
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        atxes__sws = oyx__eww.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and atxes__sws == types.Array(
            types.bool_, 1, 'C'):
            atxes__sws = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xqegz__yhcyc = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            sdxmt__wyvoh = bodo.utils.utils.alloc_type(n, atxes__sws, None)
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                pcd__jub = bodo.libs.array_kernels.isna(arr, qmyu__yjf)
                mmyv__xgb = bodo.libs.array_kernels.isna(xqegz__yhcyc,
                    qmyu__yjf)
                sdxmt__wyvoh[qmyu__yjf] = op(xqegz__yhcyc[qmyu__yjf], arr[
                    qmyu__yjf])
                if pcd__jub and mmyv__xgb:
                    bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                elif pcd__jub:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                    else:
                        sdxmt__wyvoh[qmyu__yjf] = op(xqegz__yhcyc[qmyu__yjf
                            ], fill_value)
                elif mmyv__xgb:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                    else:
                        sdxmt__wyvoh[qmyu__yjf] = op(fill_value, arr[qmyu__yjf]
                            )
                else:
                    sdxmt__wyvoh[qmyu__yjf] = op(xqegz__yhcyc[qmyu__yjf],
                        arr[qmyu__yjf])
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
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
    for op, vyghf__xete in explicit_binop_funcs_two_ways.items():
        for name in vyghf__xete:
            yba__nkajy = create_explicit_binary_op_overload(op)
            awge__jrjb = create_explicit_binary_reverse_op_overload(op)
            cyl__hpgd = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(yba__nkajy)
            overload_method(SeriesType, cyl__hpgd, no_unliteral=True)(
                awge__jrjb)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        yba__nkajy = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(yba__nkajy)
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
                wphe__qwksr = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                sdxmt__wyvoh = dt64_arr_sub(arr, wphe__qwksr)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
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
                sdxmt__wyvoh = np.empty(n, np.dtype('datetime64[ns]'))
                for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, qmyu__yjf):
                        bodo.libs.array_kernels.setna(sdxmt__wyvoh, qmyu__yjf)
                        continue
                    zweu__mgklc = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[qmyu__yjf]))
                    sbkgp__jsg = op(zweu__mgklc, rhs)
                    sdxmt__wyvoh[qmyu__yjf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        sbkgp__jsg.value)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
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
                    wphe__qwksr = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    sdxmt__wyvoh = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(wphe__qwksr))
                    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh
                        , index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                wphe__qwksr = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                sdxmt__wyvoh = op(arr, wphe__qwksr)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    ojisc__msviv = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    sdxmt__wyvoh = op(bodo.utils.conversion.
                        unbox_if_timestamp(ojisc__msviv), arr)
                    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh
                        , index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ojisc__msviv = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                sdxmt__wyvoh = op(ojisc__msviv, arr)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        yba__nkajy = create_binary_op_overload(op)
        overload(op)(yba__nkajy)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    lihdz__gnhpp = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, lihdz__gnhpp)
        for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, qmyu__yjf
                ) or bodo.libs.array_kernels.isna(arg2, qmyu__yjf):
                bodo.libs.array_kernels.setna(S, qmyu__yjf)
                continue
            S[qmyu__yjf
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                qmyu__yjf]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[qmyu__yjf]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                xqegz__yhcyc = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, xqegz__yhcyc)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        yba__nkajy = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(yba__nkajy)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                sdxmt__wyvoh = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        yba__nkajy = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(yba__nkajy)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    sdxmt__wyvoh = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh
                        , index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    xqegz__yhcyc = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    sdxmt__wyvoh = ufunc(arr, xqegz__yhcyc)
                    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh
                        , index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    xqegz__yhcyc = bodo.hiframes.pd_series_ext.get_series_data(
                        S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    sdxmt__wyvoh = ufunc(arr, xqegz__yhcyc)
                    return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh
                        , index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        yba__nkajy = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(yba__nkajy)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        cyb__oxq = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),))
        ieii__ngnzz = np.arange(n),
        bodo.libs.timsort.sort(cyb__oxq, 0, n, ieii__ngnzz)
        return ieii__ngnzz[0]
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
        owl__tfsg = get_overload_const_str(downcast)
        if owl__tfsg in ('integer', 'signed'):
            out_dtype = types.int64
        elif owl__tfsg == 'unsigned':
            out_dtype = types.uint64
        else:
            assert owl__tfsg == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            kzd__yrnr = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            sdxmt__wyvoh = pd.to_numeric(kzd__yrnr, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            jpj__pnxb = np.empty(n, np.float64)
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, qmyu__yjf):
                    bodo.libs.array_kernels.setna(jpj__pnxb, qmyu__yjf)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(jpj__pnxb,
                        qmyu__yjf, arg_a, qmyu__yjf)
            return jpj__pnxb
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            jpj__pnxb = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, qmyu__yjf):
                    bodo.libs.array_kernels.setna(jpj__pnxb, qmyu__yjf)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(jpj__pnxb,
                        qmyu__yjf, arg_a, qmyu__yjf)
            return jpj__pnxb
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        smzjk__tcrh = if_series_to_array_type(args[0])
        if isinstance(smzjk__tcrh, types.Array) and isinstance(smzjk__tcrh.
            dtype, types.Integer):
            smzjk__tcrh = types.Array(types.float64, 1, 'C')
        return smzjk__tcrh(*args)


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
    dti__ntop = bodo.utils.utils.is_array_typ(x, True)
    pyoxb__ays = bodo.utils.utils.is_array_typ(y, True)
    ohw__ozd = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        ohw__ozd += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if dti__ntop and not bodo.utils.utils.is_array_typ(x, False):
        ohw__ozd += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if pyoxb__ays and not bodo.utils.utils.is_array_typ(y, False):
        ohw__ozd += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    ohw__ozd += '  n = len(condition)\n'
    oykd__hnip = x.dtype if dti__ntop else types.unliteral(x)
    hlsj__aor = y.dtype if pyoxb__ays else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        oykd__hnip = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        hlsj__aor = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    kfza__nwpxc = get_data(x)
    vsjwl__fsp = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(ieii__ngnzz) for
        ieii__ngnzz in [kfza__nwpxc, vsjwl__fsp])
    if vsjwl__fsp == types.none:
        if isinstance(oykd__hnip, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif kfza__nwpxc == vsjwl__fsp and not is_nullable:
        out_dtype = dtype_to_array_type(oykd__hnip)
    elif oykd__hnip == string_type or hlsj__aor == string_type:
        out_dtype = bodo.string_array_type
    elif kfza__nwpxc == bytes_type or (dti__ntop and oykd__hnip == bytes_type
        ) and (vsjwl__fsp == bytes_type or pyoxb__ays and hlsj__aor ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(oykd__hnip, bodo.PDCategoricalDtype):
        out_dtype = None
    elif oykd__hnip in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(oykd__hnip, 1, 'C')
    elif hlsj__aor in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(hlsj__aor, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(oykd__hnip), numba.np.numpy_support.
            as_dtype(hlsj__aor)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(oykd__hnip, bodo.PDCategoricalDtype):
        hxc__txvyu = 'x'
    else:
        hxc__txvyu = 'out_dtype'
    ohw__ozd += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {hxc__txvyu}, (-1,))\n')
    if isinstance(oykd__hnip, bodo.PDCategoricalDtype):
        ohw__ozd += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        ohw__ozd += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    ohw__ozd += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    ohw__ozd += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if dti__ntop:
        ohw__ozd += '      if bodo.libs.array_kernels.isna(x, j):\n'
        ohw__ozd += '        setna(out_arr, j)\n'
        ohw__ozd += '        continue\n'
    if isinstance(oykd__hnip, bodo.PDCategoricalDtype):
        ohw__ozd += '      out_codes[j] = x_codes[j]\n'
    else:
        ohw__ozd += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if dti__ntop else 'x'))
    ohw__ozd += '    else:\n'
    if pyoxb__ays:
        ohw__ozd += '      if bodo.libs.array_kernels.isna(y, j):\n'
        ohw__ozd += '        setna(out_arr, j)\n'
        ohw__ozd += '        continue\n'
    if vsjwl__fsp == types.none:
        if isinstance(oykd__hnip, bodo.PDCategoricalDtype):
            ohw__ozd += '      out_codes[j] = -1\n'
        else:
            ohw__ozd += '      setna(out_arr, j)\n'
    else:
        ohw__ozd += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if pyoxb__ays else 'y'))
    ohw__ozd += '  return out_arr\n'
    nuoy__zfcy = {}
    exec(ohw__ozd, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, nuoy__zfcy)
    kcles__xwoj = nuoy__zfcy['_impl']
    return kcles__xwoj


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
        fjo__yvjc = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(fjo__yvjc, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(fjo__yvjc):
            qnzkq__szz = fjo__yvjc.data.dtype
        else:
            qnzkq__szz = fjo__yvjc.dtype
        if isinstance(qnzkq__szz, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        eud__xnb = fjo__yvjc
    else:
        cugd__ptils = []
        for fjo__yvjc in choicelist:
            if not bodo.utils.utils.is_array_typ(fjo__yvjc, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(fjo__yvjc):
                qnzkq__szz = fjo__yvjc.data.dtype
            else:
                qnzkq__szz = fjo__yvjc.dtype
            if isinstance(qnzkq__szz, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            cugd__ptils.append(qnzkq__szz)
        if not is_common_scalar_dtype(cugd__ptils):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        eud__xnb = choicelist[0]
    if is_series_type(eud__xnb):
        eud__xnb = eud__xnb.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, eud__xnb.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(eud__xnb, types.Array) or isinstance(eud__xnb,
        BooleanArrayType) or isinstance(eud__xnb, IntegerArrayType) or bodo
        .utils.utils.is_array_typ(eud__xnb, False) and eud__xnb.dtype in [
        bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {eud__xnb} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    heu__qjyqm = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        qwe__hebac = choicelist.dtype
    else:
        qwe__kqw = False
        cugd__ptils = []
        for fjo__yvjc in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(fjo__yvjc
                , 'numpy.select()')
            if is_nullable_type(fjo__yvjc):
                qwe__kqw = True
            if is_series_type(fjo__yvjc):
                qnzkq__szz = fjo__yvjc.data.dtype
            else:
                qnzkq__szz = fjo__yvjc.dtype
            if isinstance(qnzkq__szz, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            cugd__ptils.append(qnzkq__szz)
        lnol__dth, ebn__uoy = get_common_scalar_dtype(cugd__ptils)
        if not ebn__uoy:
            raise BodoError('Internal error in overload_np_select')
        hthr__gxsow = dtype_to_array_type(lnol__dth)
        if qwe__kqw:
            hthr__gxsow = to_nullable_type(hthr__gxsow)
        qwe__hebac = hthr__gxsow
    if isinstance(qwe__hebac, SeriesType):
        qwe__hebac = qwe__hebac.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        jbr__yldk = True
    else:
        jbr__yldk = False
    fir__hsu = False
    sfsoq__poub = False
    if jbr__yldk:
        if isinstance(qwe__hebac.dtype, types.Number):
            pass
        elif qwe__hebac.dtype == types.bool_:
            sfsoq__poub = True
        else:
            fir__hsu = True
            qwe__hebac = to_nullable_type(qwe__hebac)
    elif default == types.none or is_overload_constant_nan(default):
        fir__hsu = True
        qwe__hebac = to_nullable_type(qwe__hebac)
    ohw__ozd = 'def np_select_impl(condlist, choicelist, default=0):\n'
    ohw__ozd += '  if len(condlist) != len(choicelist):\n'
    ohw__ozd += (
        "    raise ValueError('list of cases must be same length as list of conditions')\n"
        )
    ohw__ozd += '  output_len = len(choicelist[0])\n'
    ohw__ozd += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    ohw__ozd += '  for i in range(output_len):\n'
    if fir__hsu:
        ohw__ozd += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif sfsoq__poub:
        ohw__ozd += '    out[i] = False\n'
    else:
        ohw__ozd += '    out[i] = default\n'
    if heu__qjyqm:
        ohw__ozd += '  for i in range(len(condlist) - 1, -1, -1):\n'
        ohw__ozd += '    cond = condlist[i]\n'
        ohw__ozd += '    choice = choicelist[i]\n'
        ohw__ozd += '    out = np.where(cond, choice, out)\n'
    else:
        for qmyu__yjf in range(len(choicelist) - 1, -1, -1):
            ohw__ozd += f'  cond = condlist[{qmyu__yjf}]\n'
            ohw__ozd += f'  choice = choicelist[{qmyu__yjf}]\n'
            ohw__ozd += f'  out = np.where(cond, choice, out)\n'
    ohw__ozd += '  return out'
    nuoy__zfcy = dict()
    exec(ohw__ozd, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': qwe__hebac}, nuoy__zfcy)
    impl = nuoy__zfcy['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        sdxmt__wyvoh = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    tmzri__onqq = dict(subset=subset, keep=keep, inplace=inplace)
    jahka__sna = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', tmzri__onqq,
        jahka__sna, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        pxcaw__xhaod = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (pxcaw__xhaod,), nzi__tmz = bodo.libs.array_kernels.drop_duplicates((
            pxcaw__xhaod,), index, 1)
        index = bodo.utils.conversion.index_from_array(nzi__tmz)
        return bodo.hiframes.pd_series_ext.init_series(pxcaw__xhaod, index,
            name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(left,
        'Series.between()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(right,
        'Series.between()')
    fbe__gacoj = element_type(S.data)
    if not is_common_scalar_dtype([fbe__gacoj, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([fbe__gacoj, right]):
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
        sdxmt__wyvoh = np.empty(n, np.bool_)
        for qmyu__yjf in numba.parfors.parfor.internal_prange(n):
            kdhdu__nwafm = bodo.utils.conversion.box_if_dt64(arr[qmyu__yjf])
            if inclusive == 'both':
                sdxmt__wyvoh[qmyu__yjf
                    ] = kdhdu__nwafm <= right and kdhdu__nwafm >= left
            else:
                sdxmt__wyvoh[qmyu__yjf
                    ] = kdhdu__nwafm < right and kdhdu__nwafm > left
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh, index,
            name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    tmzri__onqq = dict(axis=axis)
    jahka__sna = dict(axis=None)
    check_unsupported_args('Series.repeat', tmzri__onqq, jahka__sna,
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
            nzi__tmz = bodo.utils.conversion.index_to_array(index)
            sdxmt__wyvoh = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            czklq__uxqe = bodo.libs.array_kernels.repeat_kernel(nzi__tmz,
                repeats)
            afecv__sud = bodo.utils.conversion.index_from_array(czklq__uxqe)
            return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
                afecv__sud, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nzi__tmz = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        sdxmt__wyvoh = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        czklq__uxqe = bodo.libs.array_kernels.repeat_kernel(nzi__tmz, repeats)
        afecv__sud = bodo.utils.conversion.index_from_array(czklq__uxqe)
        return bodo.hiframes.pd_series_ext.init_series(sdxmt__wyvoh,
            afecv__sud, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        ieii__ngnzz = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(ieii__ngnzz)
        jlf__vkn = {}
        for qmyu__yjf in range(n):
            kdhdu__nwafm = bodo.utils.conversion.box_if_dt64(ieii__ngnzz[
                qmyu__yjf])
            jlf__vkn[index[qmyu__yjf]] = kdhdu__nwafm
        return jlf__vkn
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    hgq__jpahj = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            vgmds__wxy = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(hgq__jpahj)
    elif is_literal_type(name):
        vgmds__wxy = get_literal_value(name)
    else:
        raise_bodo_error(hgq__jpahj)
    vgmds__wxy = 0 if vgmds__wxy is None else vgmds__wxy
    vxy__iinkg = ColNamesMetaType((vgmds__wxy,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            vxy__iinkg)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
