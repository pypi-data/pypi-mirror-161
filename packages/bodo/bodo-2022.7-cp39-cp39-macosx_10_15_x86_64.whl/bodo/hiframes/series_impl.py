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
            fpoqb__zsyx = bodo.hiframes.pd_series_ext.get_series_data(s)
            bua__fvy = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                fpoqb__zsyx)
            return bua__fvy
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
            fbp__kqdsy = list()
            for eam__gfspg in range(len(S)):
                fbp__kqdsy.append(S.iat[eam__gfspg])
            return fbp__kqdsy
        return impl_float

    def impl(S):
        fbp__kqdsy = list()
        for eam__gfspg in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, eam__gfspg):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            fbp__kqdsy.append(S.iat[eam__gfspg])
        return fbp__kqdsy
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    rmhax__vecjn = dict(dtype=dtype, copy=copy, na_value=na_value)
    ersr__hjqd = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    rmhax__vecjn = dict(name=name, inplace=inplace)
    ersr__hjqd = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', rmhax__vecjn, ersr__hjqd,
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
        vayyl__ublr = ', '.join(['index_arrs[{}]'.format(eam__gfspg) for
            eam__gfspg in range(S.index.nlevels)])
    else:
        vayyl__ublr = '    bodo.utils.conversion.index_to_array(index)\n'
    cyae__kngqz = 'index' if 'index' != series_name else 'level_0'
    lqjab__bmk = get_index_names(S.index, 'Series.reset_index()', cyae__kngqz)
    columns = [name for name in lqjab__bmk]
    columns.append(series_name)
    opr__rdoo = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    opr__rdoo += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    opr__rdoo += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        opr__rdoo += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    opr__rdoo += (
        '    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)\n'
        )
    opr__rdoo += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({vayyl__ublr}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    vzy__ylrbt = {}
    exec(opr__rdoo, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, vzy__ylrbt)
    madks__scmaq = vzy__ylrbt['_impl']
    return madks__scmaq


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hvl__lhz = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
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
        hvl__lhz = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for eam__gfspg in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[eam__gfspg]):
                bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
            else:
                hvl__lhz[eam__gfspg] = np.round(arr[eam__gfspg], decimals)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    ersr__hjqd = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', rmhax__vecjn, ersr__hjqd,
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
        cdqk__krkx = bodo.hiframes.pd_series_ext.get_series_data(S)
        jayyy__igccl = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        iqrh__wry = 0
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(cdqk__krkx)
            ):
            ihk__jwmvj = 0
            pozl__ifw = bodo.libs.array_kernels.isna(cdqk__krkx, eam__gfspg)
            tlmye__aqeph = bodo.libs.array_kernels.isna(jayyy__igccl,
                eam__gfspg)
            if (pozl__ifw and not tlmye__aqeph or not pozl__ifw and
                tlmye__aqeph):
                ihk__jwmvj = 1
            elif not pozl__ifw:
                if cdqk__krkx[eam__gfspg] != jayyy__igccl[eam__gfspg]:
                    ihk__jwmvj = 1
            iqrh__wry += ihk__jwmvj
        return iqrh__wry == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    rmhax__vecjn = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    ersr__hjqd = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    rmhax__vecjn = dict(level=level)
    ersr__hjqd = dict(level=None)
    check_unsupported_args('Series.mad', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    hpi__zvdlj = types.float64
    zzxjk__hcyf = types.float64
    if S.dtype == types.float32:
        hpi__zvdlj = types.float32
        zzxjk__hcyf = types.float32
    lxs__dvc = hpi__zvdlj(0)
    pdt__xtut = zzxjk__hcyf(0)
    snq__zirgy = zzxjk__hcyf(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        jktkk__tepv = lxs__dvc
        iqrh__wry = pdt__xtut
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(A)):
            ihk__jwmvj = lxs__dvc
            fhpp__fsn = pdt__xtut
            if not bodo.libs.array_kernels.isna(A, eam__gfspg) or not skipna:
                ihk__jwmvj = A[eam__gfspg]
                fhpp__fsn = snq__zirgy
            jktkk__tepv += ihk__jwmvj
            iqrh__wry += fhpp__fsn
        yve__kndns = bodo.hiframes.series_kernels._mean_handle_nan(jktkk__tepv,
            iqrh__wry)
        hyalv__epynw = lxs__dvc
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(A)):
            ihk__jwmvj = lxs__dvc
            if not bodo.libs.array_kernels.isna(A, eam__gfspg) or not skipna:
                ihk__jwmvj = abs(A[eam__gfspg] - yve__kndns)
            hyalv__epynw += ihk__jwmvj
        lgee__ego = bodo.hiframes.series_kernels._mean_handle_nan(hyalv__epynw,
            iqrh__wry)
        return lgee__ego
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    rmhax__vecjn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', rmhax__vecjn, ersr__hjqd,
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
        dzos__csuha = 0
        ykdan__ipfew = 0
        iqrh__wry = 0
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(A)):
            ihk__jwmvj = 0
            fhpp__fsn = 0
            if not bodo.libs.array_kernels.isna(A, eam__gfspg) or not skipna:
                ihk__jwmvj = A[eam__gfspg]
                fhpp__fsn = 1
            dzos__csuha += ihk__jwmvj
            ykdan__ipfew += ihk__jwmvj * ihk__jwmvj
            iqrh__wry += fhpp__fsn
        ojih__tbu = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            dzos__csuha, ykdan__ipfew, iqrh__wry, ddof)
        avz__iekv = bodo.hiframes.series_kernels._sem_handle_nan(ojih__tbu,
            iqrh__wry)
        return avz__iekv
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', rmhax__vecjn, ersr__hjqd,
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
        dzos__csuha = 0.0
        ykdan__ipfew = 0.0
        aebg__siah = 0.0
        pxhf__qnifo = 0.0
        iqrh__wry = 0
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(A)):
            ihk__jwmvj = 0.0
            fhpp__fsn = 0
            if not bodo.libs.array_kernels.isna(A, eam__gfspg) or not skipna:
                ihk__jwmvj = np.float64(A[eam__gfspg])
                fhpp__fsn = 1
            dzos__csuha += ihk__jwmvj
            ykdan__ipfew += ihk__jwmvj ** 2
            aebg__siah += ihk__jwmvj ** 3
            pxhf__qnifo += ihk__jwmvj ** 4
            iqrh__wry += fhpp__fsn
        ojih__tbu = bodo.hiframes.series_kernels.compute_kurt(dzos__csuha,
            ykdan__ipfew, aebg__siah, pxhf__qnifo, iqrh__wry)
        return ojih__tbu
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', rmhax__vecjn, ersr__hjqd,
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
        dzos__csuha = 0.0
        ykdan__ipfew = 0.0
        aebg__siah = 0.0
        iqrh__wry = 0
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(A)):
            ihk__jwmvj = 0.0
            fhpp__fsn = 0
            if not bodo.libs.array_kernels.isna(A, eam__gfspg) or not skipna:
                ihk__jwmvj = np.float64(A[eam__gfspg])
                fhpp__fsn = 1
            dzos__csuha += ihk__jwmvj
            ykdan__ipfew += ihk__jwmvj ** 2
            aebg__siah += ihk__jwmvj ** 3
            iqrh__wry += fhpp__fsn
        ojih__tbu = bodo.hiframes.series_kernels.compute_skew(dzos__csuha,
            ykdan__ipfew, aebg__siah, iqrh__wry)
        return ojih__tbu
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', rmhax__vecjn, ersr__hjqd,
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
        cdqk__krkx = bodo.hiframes.pd_series_ext.get_series_data(S)
        jayyy__igccl = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        iqgol__bfz = 0
        for eam__gfspg in numba.parfors.parfor.internal_prange(len(cdqk__krkx)
            ):
            dxvvg__mnm = cdqk__krkx[eam__gfspg]
            tozl__zrbm = jayyy__igccl[eam__gfspg]
            iqgol__bfz += dxvvg__mnm * tozl__zrbm
        return iqgol__bfz
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    rmhax__vecjn = dict(skipna=skipna)
    ersr__hjqd = dict(skipna=True)
    check_unsupported_args('Series.cumsum', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(skipna=skipna)
    ersr__hjqd = dict(skipna=True)
    check_unsupported_args('Series.cumprod', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(skipna=skipna)
    ersr__hjqd = dict(skipna=True)
    check_unsupported_args('Series.cummin', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(skipna=skipna)
    ersr__hjqd = dict(skipna=True)
    check_unsupported_args('Series.cummax', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    ersr__hjqd = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        nym__svvtc = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, nym__svvtc, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    rmhax__vecjn = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    ersr__hjqd = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(level=level)
    ersr__hjqd = dict(level=None)
    check_unsupported_args('Series.count', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    rmhax__vecjn = dict(method=method, min_periods=min_periods)
    ersr__hjqd = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        kpinl__ujug = S.sum()
        mqo__tfwsw = other.sum()
        a = n * (S * other).sum() - kpinl__ujug * mqo__tfwsw
        evjem__qlr = n * (S ** 2).sum() - kpinl__ujug ** 2
        uohdc__ypnb = n * (other ** 2).sum() - mqo__tfwsw ** 2
        return a / np.sqrt(evjem__qlr * uohdc__ypnb)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    rmhax__vecjn = dict(min_periods=min_periods)
    ersr__hjqd = dict(min_periods=None)
    check_unsupported_args('Series.cov', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        kpinl__ujug = S.mean()
        mqo__tfwsw = other.mean()
        pgwyp__zehxq = ((S - kpinl__ujug) * (other - mqo__tfwsw)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(pgwyp__zehxq, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            fpf__hockt = np.sign(sum_val)
            return np.inf * fpf__hockt
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    rmhax__vecjn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(axis=axis, skipna=skipna)
    ersr__hjqd = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(axis=axis, skipna=skipna)
    ersr__hjqd = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', rmhax__vecjn, ersr__hjqd,
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
    rmhax__vecjn = dict(level=level, numeric_only=numeric_only)
    ersr__hjqd = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', rmhax__vecjn, ersr__hjqd,
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
        btj__mpicp = arr[:n]
        wwdr__dzip = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(btj__mpicp,
            wwdr__dzip, name)
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
        gne__ghww = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        btj__mpicp = arr[gne__ghww:]
        wwdr__dzip = index[gne__ghww:]
        return bodo.hiframes.pd_series_ext.init_series(btj__mpicp,
            wwdr__dzip, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    ivtu__hldw = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ivtu__hldw:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            nggcy__miw = index[0]
            sppup__aupgn = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                nggcy__miw, False))
        else:
            sppup__aupgn = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        btj__mpicp = arr[:sppup__aupgn]
        wwdr__dzip = index[:sppup__aupgn]
        return bodo.hiframes.pd_series_ext.init_series(btj__mpicp,
            wwdr__dzip, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    ivtu__hldw = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ivtu__hldw:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            xxdg__ijdi = index[-1]
            sppup__aupgn = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                xxdg__ijdi, True))
        else:
            sppup__aupgn = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        btj__mpicp = arr[len(arr) - sppup__aupgn:]
        wwdr__dzip = index[len(arr) - sppup__aupgn:]
        return bodo.hiframes.pd_series_ext.init_series(btj__mpicp,
            wwdr__dzip, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wzygs__fab = bodo.utils.conversion.index_to_array(index)
        bfg__bbs, wpmbq__fpk = bodo.libs.array_kernels.first_last_valid_index(
            arr, wzygs__fab)
        return wpmbq__fpk if bfg__bbs else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wzygs__fab = bodo.utils.conversion.index_to_array(index)
        bfg__bbs, wpmbq__fpk = bodo.libs.array_kernels.first_last_valid_index(
            arr, wzygs__fab, False)
        return wpmbq__fpk if bfg__bbs else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    rmhax__vecjn = dict(keep=keep)
    ersr__hjqd = dict(keep='first')
    check_unsupported_args('Series.nlargest', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wzygs__fab = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hvl__lhz, xnwu__kfqz = bodo.libs.array_kernels.nlargest(arr,
            wzygs__fab, n, True, bodo.hiframes.series_kernels.gt_f)
        egzrn__cpf = bodo.utils.conversion.convert_to_index(xnwu__kfqz)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, egzrn__cpf,
            name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    rmhax__vecjn = dict(keep=keep)
    ersr__hjqd = dict(keep='first')
    check_unsupported_args('Series.nsmallest', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wzygs__fab = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hvl__lhz, xnwu__kfqz = bodo.libs.array_kernels.nlargest(arr,
            wzygs__fab, n, False, bodo.hiframes.series_kernels.lt_f)
        egzrn__cpf = bodo.utils.conversion.convert_to_index(xnwu__kfqz)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, egzrn__cpf,
            name)
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
    rmhax__vecjn = dict(errors=errors)
    ersr__hjqd = dict(errors='raise')
    check_unsupported_args('Series.astype', rmhax__vecjn, ersr__hjqd,
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
        hvl__lhz = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    rmhax__vecjn = dict(axis=axis, is_copy=is_copy)
    ersr__hjqd = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        keop__bgof = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[keop__bgof],
            index[keop__bgof], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    rmhax__vecjn = dict(axis=axis, kind=kind, order=order)
    ersr__hjqd = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        lbiw__ekzhg = S.notna().values
        if not lbiw__ekzhg.all():
            hvl__lhz = np.full(n, -1, np.int64)
            hvl__lhz[lbiw__ekzhg] = argsort(arr[lbiw__ekzhg])
        else:
            hvl__lhz = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    rmhax__vecjn = dict(axis=axis, numeric_only=numeric_only)
    ersr__hjqd = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', rmhax__vecjn, ersr__hjqd,
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
        hvl__lhz = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    rmhax__vecjn = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    ersr__hjqd = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    rka__hsmvy = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ogo__nrvxv = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, rka__hsmvy)
        dpk__eirj = ogo__nrvxv.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        hvl__lhz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(dpk__eirj,
            0)
        egzrn__cpf = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            dpk__eirj)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, egzrn__cpf,
            name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    rmhax__vecjn = dict(axis=axis, inplace=inplace, kind=kind, ignore_index
        =ignore_index, key=key)
    ersr__hjqd = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    qnad__quazb = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ogo__nrvxv = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, qnad__quazb)
        dpk__eirj = ogo__nrvxv.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        hvl__lhz = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(dpk__eirj,
            0)
        egzrn__cpf = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            dpk__eirj)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, egzrn__cpf,
            name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    gjoa__tstyn = is_overload_true(is_nullable)
    opr__rdoo = 'def impl(bins, arr, is_nullable=True, include_lowest=True):\n'
    opr__rdoo += '  numba.parfors.parfor.init_prange()\n'
    opr__rdoo += '  n = len(arr)\n'
    if gjoa__tstyn:
        opr__rdoo += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        opr__rdoo += '  out_arr = np.empty(n, np.int64)\n'
    opr__rdoo += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    opr__rdoo += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if gjoa__tstyn:
        opr__rdoo += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        opr__rdoo += '      out_arr[i] = -1\n'
    opr__rdoo += '      continue\n'
    opr__rdoo += '    val = arr[i]\n'
    opr__rdoo += '    if include_lowest and val == bins[0]:\n'
    opr__rdoo += '      ind = 1\n'
    opr__rdoo += '    else:\n'
    opr__rdoo += '      ind = np.searchsorted(bins, val)\n'
    opr__rdoo += '    if ind == 0 or ind == len(bins):\n'
    if gjoa__tstyn:
        opr__rdoo += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        opr__rdoo += '      out_arr[i] = -1\n'
    opr__rdoo += '    else:\n'
    opr__rdoo += '      out_arr[i] = ind - 1\n'
    opr__rdoo += '  return out_arr\n'
    vzy__ylrbt = {}
    exec(opr__rdoo, {'bodo': bodo, 'np': np, 'numba': numba}, vzy__ylrbt)
    impl = vzy__ylrbt['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        pqg__wkn, vymm__klkdz = np.divmod(x, 1)
        if pqg__wkn == 0:
            ghotm__nnq = -int(np.floor(np.log10(abs(vymm__klkdz)))
                ) - 1 + precision
        else:
            ghotm__nnq = precision
        return np.around(x, ghotm__nnq)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        lbp__vllt = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(lbp__vllt)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        bsp__fycov = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            hnog__gvkj = bins.copy()
            if right and include_lowest:
                hnog__gvkj[0] = hnog__gvkj[0] - bsp__fycov
            ijd__cipg = bodo.libs.interval_arr_ext.init_interval_array(
                hnog__gvkj[:-1], hnog__gvkj[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(ijd__cipg,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        hnog__gvkj = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            hnog__gvkj[0] = hnog__gvkj[0] - 10.0 ** -precision
        ijd__cipg = bodo.libs.interval_arr_ext.init_interval_array(hnog__gvkj
            [:-1], hnog__gvkj[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(ijd__cipg, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        yxmz__gwln = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        ayt__ljpw = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        hvl__lhz = np.zeros(nbins, np.int64)
        for eam__gfspg in range(len(yxmz__gwln)):
            hvl__lhz[ayt__ljpw[eam__gfspg]] = yxmz__gwln[eam__gfspg]
        return hvl__lhz
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
            ctc__lzaa = (max_val - min_val) * 0.001
            if right:
                bins[0] -= ctc__lzaa
            else:
                bins[-1] += ctc__lzaa
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    rmhax__vecjn = dict(dropna=dropna)
    ersr__hjqd = dict(dropna=True)
    check_unsupported_args('Series.value_counts', rmhax__vecjn, ersr__hjqd,
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
    advk__lvdif = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    opr__rdoo = 'def impl(\n'
    opr__rdoo += '    S,\n'
    opr__rdoo += '    normalize=False,\n'
    opr__rdoo += '    sort=True,\n'
    opr__rdoo += '    ascending=False,\n'
    opr__rdoo += '    bins=None,\n'
    opr__rdoo += '    dropna=True,\n'
    opr__rdoo += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    opr__rdoo += '):\n'
    opr__rdoo += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    opr__rdoo += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    opr__rdoo += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if advk__lvdif:
        opr__rdoo += '    right = True\n'
        opr__rdoo += _gen_bins_handling(bins, S.dtype)
        opr__rdoo += '    arr = get_bin_inds(bins, arr)\n'
    opr__rdoo += '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n'
    opr__rdoo += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    opr__rdoo += '    )\n'
    opr__rdoo += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if advk__lvdif:
        opr__rdoo += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        opr__rdoo += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        opr__rdoo += '    index = get_bin_labels(bins)\n'
    else:
        opr__rdoo += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        opr__rdoo += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        opr__rdoo += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        opr__rdoo += '    )\n'
        opr__rdoo += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    opr__rdoo += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        opr__rdoo += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        bzgya__cqeob = 'len(S)' if advk__lvdif else 'count_arr.sum()'
        opr__rdoo += f'    res = res / float({bzgya__cqeob})\n'
    opr__rdoo += '    return res\n'
    vzy__ylrbt = {}
    exec(opr__rdoo, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, vzy__ylrbt)
    impl = vzy__ylrbt['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    opr__rdoo = ''
    if isinstance(bins, types.Integer):
        opr__rdoo += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        opr__rdoo += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            opr__rdoo += '    min_val = min_val.value\n'
            opr__rdoo += '    max_val = max_val.value\n'
        opr__rdoo += '    bins = compute_bins(bins, min_val, max_val, right)\n'
        if dtype == bodo.datetime64ns:
            opr__rdoo += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        opr__rdoo += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return opr__rdoo


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    rmhax__vecjn = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    ersr__hjqd = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    opr__rdoo = 'def impl(\n'
    opr__rdoo += '    x,\n'
    opr__rdoo += '    bins,\n'
    opr__rdoo += '    right=True,\n'
    opr__rdoo += '    labels=None,\n'
    opr__rdoo += '    retbins=False,\n'
    opr__rdoo += '    precision=3,\n'
    opr__rdoo += '    include_lowest=False,\n'
    opr__rdoo += "    duplicates='raise',\n"
    opr__rdoo += '    ordered=True\n'
    opr__rdoo += '):\n'
    if isinstance(x, SeriesType):
        opr__rdoo += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        opr__rdoo += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        opr__rdoo += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        opr__rdoo += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    opr__rdoo += _gen_bins_handling(bins, x.dtype)
    opr__rdoo += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    opr__rdoo += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    opr__rdoo += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    opr__rdoo += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        opr__rdoo += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        opr__rdoo += '    return res\n'
    else:
        opr__rdoo += '    return out_arr\n'
    vzy__ylrbt = {}
    exec(opr__rdoo, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, vzy__ylrbt)
    impl = vzy__ylrbt['impl']
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
    rmhax__vecjn = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    ersr__hjqd = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        qckez__sis = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, qckez__sis)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    rmhax__vecjn = dict(axis=axis, sort=sort, group_keys=group_keys,
        squeeze=squeeze, observed=observed, dropna=dropna)
    ersr__hjqd = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', rmhax__vecjn, ersr__hjqd,
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
        ajg__brfe = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            kfh__hgspc = bodo.utils.conversion.coerce_to_array(index)
            ogo__nrvxv = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                kfh__hgspc, arr), index, ajg__brfe)
            return ogo__nrvxv.groupby(' ')['']
        return impl_index
    stt__xgqu = by
    if isinstance(by, SeriesType):
        stt__xgqu = by.data
    if isinstance(stt__xgqu, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    ksos__gxml = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        kfh__hgspc = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ogo__nrvxv = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            kfh__hgspc, arr), index, ksos__gxml)
        return ogo__nrvxv.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    rmhax__vecjn = dict(verify_integrity=verify_integrity)
    ersr__hjqd = dict(verify_integrity=False)
    check_unsupported_args('Series.append', rmhax__vecjn, ersr__hjqd,
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
            nvklg__dad = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            hvl__lhz = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(hvl__lhz, A, nvklg__dad, False)
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
                name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hvl__lhz = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    rmhax__vecjn = dict(interpolation=interpolation)
    ersr__hjqd = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            hvl__lhz = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
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
        cqo__aqn = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(cqo__aqn, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    rmhax__vecjn = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    ersr__hjqd = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', rmhax__vecjn, ersr__hjqd,
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
        pdssc__dssii = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        pdssc__dssii = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    opr__rdoo = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {pdssc__dssii}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    inlye__nfmpa = dict()
    exec(opr__rdoo, {'bodo': bodo, 'numba': numba}, inlye__nfmpa)
    kto__mvqf = inlye__nfmpa['impl']
    return kto__mvqf


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        pdssc__dssii = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        pdssc__dssii = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    opr__rdoo = 'def impl(S,\n'
    opr__rdoo += '     value=None,\n'
    opr__rdoo += '    method=None,\n'
    opr__rdoo += '    axis=None,\n'
    opr__rdoo += '    inplace=False,\n'
    opr__rdoo += '    limit=None,\n'
    opr__rdoo += '   downcast=None,\n'
    opr__rdoo += '):\n'
    opr__rdoo += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    opr__rdoo += '    n = len(in_arr)\n'
    opr__rdoo += f'    out_arr = {pdssc__dssii}(n, -1)\n'
    opr__rdoo += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    opr__rdoo += '        s = in_arr[j]\n'
    opr__rdoo += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    opr__rdoo += '            s = value\n'
    opr__rdoo += '        out_arr[j] = s\n'
    opr__rdoo += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    inlye__nfmpa = dict()
    exec(opr__rdoo, {'bodo': bodo, 'numba': numba}, inlye__nfmpa)
    kto__mvqf = inlye__nfmpa['impl']
    return kto__mvqf


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
    uri__dls = bodo.hiframes.pd_series_ext.get_series_data(value)
    for eam__gfspg in numba.parfors.parfor.internal_prange(len(drql__aydbj)):
        s = drql__aydbj[eam__gfspg]
        if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg
            ) and not bodo.libs.array_kernels.isna(uri__dls, eam__gfspg):
            s = uri__dls[eam__gfspg]
        drql__aydbj[eam__gfspg] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
    for eam__gfspg in numba.parfors.parfor.internal_prange(len(drql__aydbj)):
        s = drql__aydbj[eam__gfspg]
        if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg):
            s = value
        drql__aydbj[eam__gfspg] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    uri__dls = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(drql__aydbj)
    hvl__lhz = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for fhfwb__eygs in numba.parfors.parfor.internal_prange(n):
        s = drql__aydbj[fhfwb__eygs]
        if bodo.libs.array_kernels.isna(drql__aydbj, fhfwb__eygs
            ) and not bodo.libs.array_kernels.isna(uri__dls, fhfwb__eygs):
            s = uri__dls[fhfwb__eygs]
        hvl__lhz[fhfwb__eygs] = s
        if bodo.libs.array_kernels.isna(drql__aydbj, fhfwb__eygs
            ) and bodo.libs.array_kernels.isna(uri__dls, fhfwb__eygs):
            bodo.libs.array_kernels.setna(hvl__lhz, fhfwb__eygs)
    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    uri__dls = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(drql__aydbj)
    hvl__lhz = bodo.utils.utils.alloc_type(n, drql__aydbj.dtype, (-1,))
    for eam__gfspg in numba.parfors.parfor.internal_prange(n):
        s = drql__aydbj[eam__gfspg]
        if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg
            ) and not bodo.libs.array_kernels.isna(uri__dls, eam__gfspg):
            s = uri__dls[eam__gfspg]
        hvl__lhz[eam__gfspg] = s
    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    rmhax__vecjn = dict(limit=limit, downcast=downcast)
    ersr__hjqd = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', rmhax__vecjn, ersr__hjqd,
        package_name='pandas', module_name='Series')
    qqacy__tew = not is_overload_none(value)
    hlspa__squen = not is_overload_none(method)
    if qqacy__tew and hlspa__squen:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not qqacy__tew and not hlspa__squen:
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
    if hlspa__squen:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        rxp__vsl = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(rxp__vsl)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(rxp__vsl)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    slkr__qgslx = element_type(S.data)
    mbke__dkys = None
    if qqacy__tew:
        mbke__dkys = element_type(types.unliteral(value))
    if mbke__dkys and not can_replace(slkr__qgslx, mbke__dkys):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {mbke__dkys} with series type {slkr__qgslx}'
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
        cmaph__kwz = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                uri__dls = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(drql__aydbj)
                hvl__lhz = bodo.utils.utils.alloc_type(n, cmaph__kwz, (-1,))
                for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg
                        ) and bodo.libs.array_kernels.isna(uri__dls, eam__gfspg
                        ):
                        bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                        continue
                    if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg):
                        hvl__lhz[eam__gfspg
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            uri__dls[eam__gfspg])
                        continue
                    hvl__lhz[eam__gfspg
                        ] = bodo.utils.conversion.unbox_if_timestamp(
                        drql__aydbj[eam__gfspg])
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return fillna_series_impl
        if hlspa__squen:
            vsjs__jsdue = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(slkr__qgslx, (types.Integer, types.Float)
                ) and slkr__qgslx not in vsjs__jsdue:
                raise BodoError(
                    f"Series.fillna(): series of type {slkr__qgslx} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                hvl__lhz = bodo.libs.array_kernels.ffill_bfill_arr(drql__aydbj,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(drql__aydbj)
            hvl__lhz = bodo.utils.utils.alloc_type(n, cmaph__kwz, (-1,))
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(drql__aydbj[
                    eam__gfspg])
                if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg):
                    s = value
                hvl__lhz[eam__gfspg] = s
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
                name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        oaei__cfekd = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        rmhax__vecjn = dict(limit=limit, downcast=downcast)
        ersr__hjqd = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', rmhax__vecjn,
            ersr__hjqd, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        slkr__qgslx = element_type(S.data)
        vsjs__jsdue = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(slkr__qgslx, (types.Integer, types.Float)
            ) and slkr__qgslx not in vsjs__jsdue:
            raise BodoError(
                f'Series.{overload_name}(): series of type {slkr__qgslx} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            hvl__lhz = bodo.libs.array_kernels.ffill_bfill_arr(drql__aydbj,
                oaei__cfekd)
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
                name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        okk__vdl = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(okk__vdl)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        ksnf__ympd = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(ksnf__ympd)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        ksnf__ympd = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(ksnf__ympd)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        ksnf__ympd = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(ksnf__ympd)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    rmhax__vecjn = dict(inplace=inplace, limit=limit, regex=regex, method=
        method)
    eapj__qdhi = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', rmhax__vecjn, eapj__qdhi,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    slkr__qgslx = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        jsmb__ebzld = element_type(to_replace.key_type)
        mbke__dkys = element_type(to_replace.value_type)
    else:
        jsmb__ebzld = element_type(to_replace)
        mbke__dkys = element_type(value)
    xinvm__meoz = None
    if slkr__qgslx != types.unliteral(jsmb__ebzld):
        if bodo.utils.typing.equality_always_false(slkr__qgslx, types.
            unliteral(jsmb__ebzld)
            ) or not bodo.utils.typing.types_equality_exists(slkr__qgslx,
            jsmb__ebzld):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(slkr__qgslx, (types.Float, types.Integer)
            ) or slkr__qgslx == np.bool_:
            xinvm__meoz = slkr__qgslx
    if not can_replace(slkr__qgslx, types.unliteral(mbke__dkys)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    zjky__vuzq = to_str_arr_if_dict_array(S.data)
    if isinstance(zjky__vuzq, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(drql__aydbj.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(drql__aydbj)
        hvl__lhz = bodo.utils.utils.alloc_type(n, zjky__vuzq, (-1,))
        oup__wrhiy = build_replace_dict(to_replace, value, xinvm__meoz)
        for eam__gfspg in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(drql__aydbj, eam__gfspg):
                bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                continue
            s = drql__aydbj[eam__gfspg]
            if s in oup__wrhiy:
                s = oup__wrhiy[s]
            hvl__lhz[eam__gfspg] = s
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    crpz__dfjcg = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    bfjpc__lgjwu = is_iterable_type(to_replace)
    hzmne__waa = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    zev__fqk = is_iterable_type(value)
    if crpz__dfjcg and hzmne__waa:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                oup__wrhiy = {}
                oup__wrhiy[key_dtype_conv(to_replace)] = value
                return oup__wrhiy
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            oup__wrhiy = {}
            oup__wrhiy[to_replace] = value
            return oup__wrhiy
        return impl
    if bfjpc__lgjwu and hzmne__waa:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                oup__wrhiy = {}
                for vzi__doxqu in to_replace:
                    oup__wrhiy[key_dtype_conv(vzi__doxqu)] = value
                return oup__wrhiy
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            oup__wrhiy = {}
            for vzi__doxqu in to_replace:
                oup__wrhiy[vzi__doxqu] = value
            return oup__wrhiy
        return impl
    if bfjpc__lgjwu and zev__fqk:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                oup__wrhiy = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for eam__gfspg in range(len(to_replace)):
                    oup__wrhiy[key_dtype_conv(to_replace[eam__gfspg])] = value[
                        eam__gfspg]
                return oup__wrhiy
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            oup__wrhiy = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for eam__gfspg in range(len(to_replace)):
                oup__wrhiy[to_replace[eam__gfspg]] = value[eam__gfspg]
            return oup__wrhiy
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
            hvl__lhz = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
                name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hvl__lhz = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    rmhax__vecjn = dict(ignore_index=ignore_index)
    bioxt__pnmr = dict(ignore_index=False)
    check_unsupported_args('Series.explode', rmhax__vecjn, bioxt__pnmr,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wzygs__fab = bodo.utils.conversion.index_to_array(index)
        hvl__lhz, oli__jdvgy = bodo.libs.array_kernels.explode(arr, wzygs__fab)
        egzrn__cpf = bodo.utils.conversion.index_from_array(oli__jdvgy)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, egzrn__cpf,
            name)
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
            tthm__ksqho = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                tthm__ksqho[eam__gfspg] = np.argmax(a[eam__gfspg])
            return tthm__ksqho
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ylnm__gkw = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                ylnm__gkw[eam__gfspg] = np.argmin(a[eam__gfspg])
            return ylnm__gkw
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
    rmhax__vecjn = dict(axis=axis, inplace=inplace, how=how)
    jnuf__pwd = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', rmhax__vecjn, jnuf__pwd,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            lbiw__ekzhg = S.notna().values
            wzygs__fab = bodo.utils.conversion.extract_index_array(S)
            egzrn__cpf = bodo.utils.conversion.convert_to_index(wzygs__fab[
                lbiw__ekzhg])
            hvl__lhz = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(drql__aydbj))
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                egzrn__cpf, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wzygs__fab = bodo.utils.conversion.extract_index_array(S)
            lbiw__ekzhg = S.notna().values
            egzrn__cpf = bodo.utils.conversion.convert_to_index(wzygs__fab[
                lbiw__ekzhg])
            hvl__lhz = drql__aydbj[lbiw__ekzhg]
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                egzrn__cpf, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    rmhax__vecjn = dict(freq=freq, axis=axis, fill_value=fill_value)
    ersr__hjqd = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', rmhax__vecjn, ersr__hjqd,
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
        hvl__lhz = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    rmhax__vecjn = dict(fill_method=fill_method, limit=limit, freq=freq)
    ersr__hjqd = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', rmhax__vecjn, ersr__hjqd,
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
        hvl__lhz = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
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
            tfdz__zmhe = 'None'
        else:
            tfdz__zmhe = 'other'
        opr__rdoo = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            opr__rdoo += '  cond = ~cond\n'
        opr__rdoo += '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
        opr__rdoo += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        opr__rdoo += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        opr__rdoo += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {tfdz__zmhe})\n'
            )
        opr__rdoo += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        vzy__ylrbt = {}
        exec(opr__rdoo, {'bodo': bodo, 'np': np}, vzy__ylrbt)
        impl = vzy__ylrbt['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        okk__vdl = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(okk__vdl)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    rmhax__vecjn = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    ersr__hjqd = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', rmhax__vecjn, ersr__hjqd,
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
    fnf__ibi = is_overload_constant_nan(other)
    if not (is_default or fnf__ibi or is_scalar_type(other) or isinstance(
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
            pcrsk__dtj = arr.dtype.elem_type
        else:
            pcrsk__dtj = arr.dtype
        if is_iterable_type(other):
            xrub__ucq = other.dtype
        elif fnf__ibi:
            xrub__ucq = types.float64
        else:
            xrub__ucq = types.unliteral(other)
        if not fnf__ibi and not is_common_scalar_dtype([pcrsk__dtj, xrub__ucq]
            ):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        rmhax__vecjn = dict(level=level, axis=axis)
        ersr__hjqd = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__),
            rmhax__vecjn, ersr__hjqd, package_name='pandas', module_name=
            'Series')
        otym__uwcvl = other == string_type or is_overload_constant_str(other)
        exs__aikm = is_iterable_type(other) and other.dtype == string_type
        oci__crm = S.dtype == string_type and (op == operator.add and (
            otym__uwcvl or exs__aikm) or op == operator.mul and isinstance(
            other, types.Integer))
        fbfyz__pzu = S.dtype == bodo.timedelta64ns
        dsxam__mbwru = S.dtype == bodo.datetime64ns
        jylwh__kdljo = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        ugan__yfg = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        lyirh__suc = fbfyz__pzu and (jylwh__kdljo or ugan__yfg
            ) or dsxam__mbwru and jylwh__kdljo
        lyirh__suc = lyirh__suc and op == operator.add
        if not (isinstance(S.dtype, types.Number) or oci__crm or lyirh__suc):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        vlnrp__szjv = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            zjky__vuzq = vlnrp__szjv.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and zjky__vuzq == types.Array(types.bool_, 1, 'C'):
                zjky__vuzq = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                hvl__lhz = bodo.utils.utils.alloc_type(n, zjky__vuzq, (-1,))
                for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                    qneep__kjaml = bodo.libs.array_kernels.isna(arr, eam__gfspg
                        )
                    if qneep__kjaml:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                        else:
                            hvl__lhz[eam__gfspg] = op(fill_value, other)
                    else:
                        hvl__lhz[eam__gfspg] = op(arr[eam__gfspg], other)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        zjky__vuzq = vlnrp__szjv.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and zjky__vuzq == types.Array(
            types.bool_, 1, 'C'):
            zjky__vuzq = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            axjp__jusl = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            hvl__lhz = bodo.utils.utils.alloc_type(n, zjky__vuzq, (-1,))
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                qneep__kjaml = bodo.libs.array_kernels.isna(arr, eam__gfspg)
                xiq__yvzzo = bodo.libs.array_kernels.isna(axjp__jusl,
                    eam__gfspg)
                if qneep__kjaml and xiq__yvzzo:
                    bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                elif qneep__kjaml:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                    else:
                        hvl__lhz[eam__gfspg] = op(fill_value, axjp__jusl[
                            eam__gfspg])
                elif xiq__yvzzo:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                    else:
                        hvl__lhz[eam__gfspg] = op(arr[eam__gfspg], fill_value)
                else:
                    hvl__lhz[eam__gfspg] = op(arr[eam__gfspg], axjp__jusl[
                        eam__gfspg])
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
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
        vlnrp__szjv = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            zjky__vuzq = vlnrp__szjv.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and zjky__vuzq == types.Array(types.bool_, 1, 'C'):
                zjky__vuzq = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                hvl__lhz = bodo.utils.utils.alloc_type(n, zjky__vuzq, None)
                for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                    qneep__kjaml = bodo.libs.array_kernels.isna(arr, eam__gfspg
                        )
                    if qneep__kjaml:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                        else:
                            hvl__lhz[eam__gfspg] = op(other, fill_value)
                    else:
                        hvl__lhz[eam__gfspg] = op(other, arr[eam__gfspg])
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        zjky__vuzq = vlnrp__szjv.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and zjky__vuzq == types.Array(
            types.bool_, 1, 'C'):
            zjky__vuzq = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            axjp__jusl = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            hvl__lhz = bodo.utils.utils.alloc_type(n, zjky__vuzq, None)
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                qneep__kjaml = bodo.libs.array_kernels.isna(arr, eam__gfspg)
                xiq__yvzzo = bodo.libs.array_kernels.isna(axjp__jusl,
                    eam__gfspg)
                hvl__lhz[eam__gfspg] = op(axjp__jusl[eam__gfspg], arr[
                    eam__gfspg])
                if qneep__kjaml and xiq__yvzzo:
                    bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                elif qneep__kjaml:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                    else:
                        hvl__lhz[eam__gfspg] = op(axjp__jusl[eam__gfspg],
                            fill_value)
                elif xiq__yvzzo:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                    else:
                        hvl__lhz[eam__gfspg] = op(fill_value, arr[eam__gfspg])
                else:
                    hvl__lhz[eam__gfspg] = op(axjp__jusl[eam__gfspg], arr[
                        eam__gfspg])
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
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
    for op, rqop__wjkp in explicit_binop_funcs_two_ways.items():
        for name in rqop__wjkp:
            okk__vdl = create_explicit_binary_op_overload(op)
            rltj__wyfk = create_explicit_binary_reverse_op_overload(op)
            foupq__spl = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(okk__vdl)
            overload_method(SeriesType, foupq__spl, no_unliteral=True)(
                rltj__wyfk)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        okk__vdl = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(okk__vdl)
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
                ctiie__xbho = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                hvl__lhz = dt64_arr_sub(arr, ctiie__xbho)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
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
                hvl__lhz = np.empty(n, np.dtype('datetime64[ns]'))
                for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, eam__gfspg):
                        bodo.libs.array_kernels.setna(hvl__lhz, eam__gfspg)
                        continue
                    bud__wyg = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[eam__gfspg]))
                    yhvd__wsgdo = op(bud__wyg, rhs)
                    hvl__lhz[eam__gfspg
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        yhvd__wsgdo.value)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
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
                    ctiie__xbho = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    hvl__lhz = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(ctiie__xbho))
                    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ctiie__xbho = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                hvl__lhz = op(arr, ctiie__xbho)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    czh__exifx = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    hvl__lhz = op(bodo.utils.conversion.unbox_if_timestamp(
                        czh__exifx), arr)
                    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                czh__exifx = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                hvl__lhz = op(czh__exifx, arr)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        okk__vdl = create_binary_op_overload(op)
        overload(op)(okk__vdl)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    wkf__lox = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, wkf__lox)
        for eam__gfspg in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, eam__gfspg
                ) or bodo.libs.array_kernels.isna(arg2, eam__gfspg):
                bodo.libs.array_kernels.setna(S, eam__gfspg)
                continue
            S[eam__gfspg
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                eam__gfspg]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[eam__gfspg]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                axjp__jusl = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, axjp__jusl)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        okk__vdl = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(okk__vdl)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                hvl__lhz = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        okk__vdl = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(okk__vdl)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    hvl__lhz = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
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
                    axjp__jusl = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    hvl__lhz = ufunc(arr, axjp__jusl)
                    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    axjp__jusl = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    hvl__lhz = ufunc(arr, axjp__jusl)
                    return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        okk__vdl = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(okk__vdl)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        wdo__iwj = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),))
        fpoqb__zsyx = np.arange(n),
        bodo.libs.timsort.sort(wdo__iwj, 0, n, fpoqb__zsyx)
        return fpoqb__zsyx[0]
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
        uajub__xfkbh = get_overload_const_str(downcast)
        if uajub__xfkbh in ('integer', 'signed'):
            out_dtype = types.int64
        elif uajub__xfkbh == 'unsigned':
            out_dtype = types.uint64
        else:
            assert uajub__xfkbh == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            drql__aydbj = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            hvl__lhz = pd.to_numeric(drql__aydbj, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index,
                name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            wxo__nsjjm = np.empty(n, np.float64)
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, eam__gfspg):
                    bodo.libs.array_kernels.setna(wxo__nsjjm, eam__gfspg)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(wxo__nsjjm,
                        eam__gfspg, arg_a, eam__gfspg)
            return wxo__nsjjm
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            wxo__nsjjm = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for eam__gfspg in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, eam__gfspg):
                    bodo.libs.array_kernels.setna(wxo__nsjjm, eam__gfspg)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(wxo__nsjjm,
                        eam__gfspg, arg_a, eam__gfspg)
            return wxo__nsjjm
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        lvy__jpkj = if_series_to_array_type(args[0])
        if isinstance(lvy__jpkj, types.Array) and isinstance(lvy__jpkj.
            dtype, types.Integer):
            lvy__jpkj = types.Array(types.float64, 1, 'C')
        return lvy__jpkj(*args)


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
    rsfl__oib = bodo.utils.utils.is_array_typ(x, True)
    bgvmk__gmk = bodo.utils.utils.is_array_typ(y, True)
    opr__rdoo = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        opr__rdoo += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if rsfl__oib and not bodo.utils.utils.is_array_typ(x, False):
        opr__rdoo += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if bgvmk__gmk and not bodo.utils.utils.is_array_typ(y, False):
        opr__rdoo += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    opr__rdoo += '  n = len(condition)\n'
    xzni__tdiy = x.dtype if rsfl__oib else types.unliteral(x)
    zjgxm__lnf = y.dtype if bgvmk__gmk else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        xzni__tdiy = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        zjgxm__lnf = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    una__vpygo = get_data(x)
    csrg__ldd = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(fpoqb__zsyx) for
        fpoqb__zsyx in [una__vpygo, csrg__ldd])
    if csrg__ldd == types.none:
        if isinstance(xzni__tdiy, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif una__vpygo == csrg__ldd and not is_nullable:
        out_dtype = dtype_to_array_type(xzni__tdiy)
    elif xzni__tdiy == string_type or zjgxm__lnf == string_type:
        out_dtype = bodo.string_array_type
    elif una__vpygo == bytes_type or (rsfl__oib and xzni__tdiy == bytes_type
        ) and (csrg__ldd == bytes_type or bgvmk__gmk and zjgxm__lnf ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(xzni__tdiy, bodo.PDCategoricalDtype):
        out_dtype = None
    elif xzni__tdiy in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(xzni__tdiy, 1, 'C')
    elif zjgxm__lnf in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(zjgxm__lnf, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(xzni__tdiy), numba.np.numpy_support.
            as_dtype(zjgxm__lnf)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(xzni__tdiy, bodo.PDCategoricalDtype):
        ahu__eem = 'x'
    else:
        ahu__eem = 'out_dtype'
    opr__rdoo += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {ahu__eem}, (-1,))\n')
    if isinstance(xzni__tdiy, bodo.PDCategoricalDtype):
        opr__rdoo += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        opr__rdoo += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    opr__rdoo += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    opr__rdoo += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if rsfl__oib:
        opr__rdoo += '      if bodo.libs.array_kernels.isna(x, j):\n'
        opr__rdoo += '        setna(out_arr, j)\n'
        opr__rdoo += '        continue\n'
    if isinstance(xzni__tdiy, bodo.PDCategoricalDtype):
        opr__rdoo += '      out_codes[j] = x_codes[j]\n'
    else:
        opr__rdoo += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if rsfl__oib else 'x'))
    opr__rdoo += '    else:\n'
    if bgvmk__gmk:
        opr__rdoo += '      if bodo.libs.array_kernels.isna(y, j):\n'
        opr__rdoo += '        setna(out_arr, j)\n'
        opr__rdoo += '        continue\n'
    if csrg__ldd == types.none:
        if isinstance(xzni__tdiy, bodo.PDCategoricalDtype):
            opr__rdoo += '      out_codes[j] = -1\n'
        else:
            opr__rdoo += '      setna(out_arr, j)\n'
    else:
        opr__rdoo += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if bgvmk__gmk else 'y'))
    opr__rdoo += '  return out_arr\n'
    vzy__ylrbt = {}
    exec(opr__rdoo, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, vzy__ylrbt)
    madks__scmaq = vzy__ylrbt['_impl']
    return madks__scmaq


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
        cipdq__mxhf = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(cipdq__mxhf, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(cipdq__mxhf):
            rgqno__hbz = cipdq__mxhf.data.dtype
        else:
            rgqno__hbz = cipdq__mxhf.dtype
        if isinstance(rgqno__hbz, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        tyw__amv = cipdq__mxhf
    else:
        ohr__hkn = []
        for cipdq__mxhf in choicelist:
            if not bodo.utils.utils.is_array_typ(cipdq__mxhf, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(cipdq__mxhf):
                rgqno__hbz = cipdq__mxhf.data.dtype
            else:
                rgqno__hbz = cipdq__mxhf.dtype
            if isinstance(rgqno__hbz, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            ohr__hkn.append(rgqno__hbz)
        if not is_common_scalar_dtype(ohr__hkn):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        tyw__amv = choicelist[0]
    if is_series_type(tyw__amv):
        tyw__amv = tyw__amv.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, tyw__amv.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(tyw__amv, types.Array) or isinstance(tyw__amv,
        BooleanArrayType) or isinstance(tyw__amv, IntegerArrayType) or bodo
        .utils.utils.is_array_typ(tyw__amv, False) and tyw__amv.dtype in [
        bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {tyw__amv} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    awmbe__qiwis = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        nppe__ldjj = choicelist.dtype
    else:
        aamy__wnx = False
        ohr__hkn = []
        for cipdq__mxhf in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                cipdq__mxhf, 'numpy.select()')
            if is_nullable_type(cipdq__mxhf):
                aamy__wnx = True
            if is_series_type(cipdq__mxhf):
                rgqno__hbz = cipdq__mxhf.data.dtype
            else:
                rgqno__hbz = cipdq__mxhf.dtype
            if isinstance(rgqno__hbz, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            ohr__hkn.append(rgqno__hbz)
        iqpvl__bnd, wvu__wls = get_common_scalar_dtype(ohr__hkn)
        if not wvu__wls:
            raise BodoError('Internal error in overload_np_select')
        ekm__uhk = dtype_to_array_type(iqpvl__bnd)
        if aamy__wnx:
            ekm__uhk = to_nullable_type(ekm__uhk)
        nppe__ldjj = ekm__uhk
    if isinstance(nppe__ldjj, SeriesType):
        nppe__ldjj = nppe__ldjj.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        fawck__mzqbv = True
    else:
        fawck__mzqbv = False
    hgwd__prj = False
    wqp__jlb = False
    if fawck__mzqbv:
        if isinstance(nppe__ldjj.dtype, types.Number):
            pass
        elif nppe__ldjj.dtype == types.bool_:
            wqp__jlb = True
        else:
            hgwd__prj = True
            nppe__ldjj = to_nullable_type(nppe__ldjj)
    elif default == types.none or is_overload_constant_nan(default):
        hgwd__prj = True
        nppe__ldjj = to_nullable_type(nppe__ldjj)
    opr__rdoo = 'def np_select_impl(condlist, choicelist, default=0):\n'
    opr__rdoo += '  if len(condlist) != len(choicelist):\n'
    opr__rdoo += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    opr__rdoo += '  output_len = len(choicelist[0])\n'
    opr__rdoo += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    opr__rdoo += '  for i in range(output_len):\n'
    if hgwd__prj:
        opr__rdoo += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif wqp__jlb:
        opr__rdoo += '    out[i] = False\n'
    else:
        opr__rdoo += '    out[i] = default\n'
    if awmbe__qiwis:
        opr__rdoo += '  for i in range(len(condlist) - 1, -1, -1):\n'
        opr__rdoo += '    cond = condlist[i]\n'
        opr__rdoo += '    choice = choicelist[i]\n'
        opr__rdoo += '    out = np.where(cond, choice, out)\n'
    else:
        for eam__gfspg in range(len(choicelist) - 1, -1, -1):
            opr__rdoo += f'  cond = condlist[{eam__gfspg}]\n'
            opr__rdoo += f'  choice = choicelist[{eam__gfspg}]\n'
            opr__rdoo += f'  out = np.where(cond, choice, out)\n'
    opr__rdoo += '  return out'
    vzy__ylrbt = dict()
    exec(opr__rdoo, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': nppe__ldjj}, vzy__ylrbt)
    impl = vzy__ylrbt['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hvl__lhz = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    rmhax__vecjn = dict(subset=subset, keep=keep, inplace=inplace)
    ersr__hjqd = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', rmhax__vecjn,
        ersr__hjqd, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        cnfp__lrepa = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (cnfp__lrepa,), wzygs__fab = bodo.libs.array_kernels.drop_duplicates((
            cnfp__lrepa,), index, 1)
        index = bodo.utils.conversion.index_from_array(wzygs__fab)
        return bodo.hiframes.pd_series_ext.init_series(cnfp__lrepa, index, name
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
    drcsa__bsybv = element_type(S.data)
    if not is_common_scalar_dtype([drcsa__bsybv, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([drcsa__bsybv, right]):
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
        hvl__lhz = np.empty(n, np.bool_)
        for eam__gfspg in numba.parfors.parfor.internal_prange(n):
            ihk__jwmvj = bodo.utils.conversion.box_if_dt64(arr[eam__gfspg])
            if inclusive == 'both':
                hvl__lhz[eam__gfspg
                    ] = ihk__jwmvj <= right and ihk__jwmvj >= left
            else:
                hvl__lhz[eam__gfspg] = ihk__jwmvj < right and ihk__jwmvj > left
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    rmhax__vecjn = dict(axis=axis)
    ersr__hjqd = dict(axis=None)
    check_unsupported_args('Series.repeat', rmhax__vecjn, ersr__hjqd,
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
            wzygs__fab = bodo.utils.conversion.index_to_array(index)
            hvl__lhz = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            oli__jdvgy = bodo.libs.array_kernels.repeat_kernel(wzygs__fab,
                repeats)
            egzrn__cpf = bodo.utils.conversion.index_from_array(oli__jdvgy)
            return bodo.hiframes.pd_series_ext.init_series(hvl__lhz,
                egzrn__cpf, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wzygs__fab = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        hvl__lhz = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        oli__jdvgy = bodo.libs.array_kernels.repeat_kernel(wzygs__fab, repeats)
        egzrn__cpf = bodo.utils.conversion.index_from_array(oli__jdvgy)
        return bodo.hiframes.pd_series_ext.init_series(hvl__lhz, egzrn__cpf,
            name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        fpoqb__zsyx = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(fpoqb__zsyx)
        wuot__oemn = {}
        for eam__gfspg in range(n):
            ihk__jwmvj = bodo.utils.conversion.box_if_dt64(fpoqb__zsyx[
                eam__gfspg])
            wuot__oemn[index[eam__gfspg]] = ihk__jwmvj
        return wuot__oemn
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    rxp__vsl = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            zdd__tya = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(rxp__vsl)
    elif is_literal_type(name):
        zdd__tya = get_literal_value(name)
    else:
        raise_bodo_error(rxp__vsl)
    zdd__tya = 0 if zdd__tya is None else zdd__tya
    wmfi__ztqfc = ColNamesMetaType((zdd__tya,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            wmfi__ztqfc)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
