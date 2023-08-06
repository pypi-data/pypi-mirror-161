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
            gzx__dietw = bodo.hiframes.pd_series_ext.get_series_data(s)
            spw__ciete = bodo.libs.pd_datetime_arr_ext.unwrap_tz_array(
                gzx__dietw)
            return spw__ciete
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
            yor__cfv = list()
            for vfqk__wgs in range(len(S)):
                yor__cfv.append(S.iat[vfqk__wgs])
            return yor__cfv
        return impl_float

    def impl(S):
        yor__cfv = list()
        for vfqk__wgs in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, vfqk__wgs):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            yor__cfv.append(S.iat[vfqk__wgs])
        return yor__cfv
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    hpae__wdbqg = dict(dtype=dtype, copy=copy, na_value=na_value)
    coxjz__zdc = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    hpae__wdbqg = dict(name=name, inplace=inplace)
    coxjz__zdc = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', hpae__wdbqg, coxjz__zdc,
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
        sveiy__ppe = ', '.join(['index_arrs[{}]'.format(vfqk__wgs) for
            vfqk__wgs in range(S.index.nlevels)])
    else:
        sveiy__ppe = '    bodo.utils.conversion.index_to_array(index)\n'
    idp__bra = 'index' if 'index' != series_name else 'level_0'
    gfprp__tsn = get_index_names(S.index, 'Series.reset_index()', idp__bra)
    columns = [name for name in gfprp__tsn]
    columns.append(series_name)
    zfeak__vrmq = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    zfeak__vrmq += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    zfeak__vrmq += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    if isinstance(S.index, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        zfeak__vrmq += (
            '    index_arrs = bodo.hiframes.pd_index_ext.get_index_data(index)\n'
            )
    zfeak__vrmq += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    zfeak__vrmq += f"""    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({sveiy__ppe}, arr), df_index, __col_name_meta_value_series_reset_index)
"""
    vqs__gskw = {}
    exec(zfeak__vrmq, {'bodo': bodo,
        '__col_name_meta_value_series_reset_index': ColNamesMetaType(tuple(
        columns))}, vqs__gskw)
    vrv__vlp = vqs__gskw['_impl']
    return vrv__vlp


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bmgx__ppfv = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
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
        bmgx__ppfv = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[vfqk__wgs]):
                bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
            else:
                bmgx__ppfv[vfqk__wgs] = np.round(arr[vfqk__wgs], decimals)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    coxjz__zdc = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', hpae__wdbqg, coxjz__zdc,
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
        zty__muz = bodo.hiframes.pd_series_ext.get_series_data(S)
        qmr__szp = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        giprz__jrtmw = 0
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(zty__muz)):
            lwb__ojix = 0
            tceeu__kwp = bodo.libs.array_kernels.isna(zty__muz, vfqk__wgs)
            tkn__zub = bodo.libs.array_kernels.isna(qmr__szp, vfqk__wgs)
            if tceeu__kwp and not tkn__zub or not tceeu__kwp and tkn__zub:
                lwb__ojix = 1
            elif not tceeu__kwp:
                if zty__muz[vfqk__wgs] != qmr__szp[vfqk__wgs]:
                    lwb__ojix = 1
            giprz__jrtmw += lwb__ojix
        return giprz__jrtmw == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    hpae__wdbqg = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    coxjz__zdc = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.all()'
        )

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_all(A)
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    hpae__wdbqg = dict(level=level)
    coxjz__zdc = dict(level=None)
    check_unsupported_args('Series.mad', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    ihgs__qjo = types.float64
    qpa__ztop = types.float64
    if S.dtype == types.float32:
        ihgs__qjo = types.float32
        qpa__ztop = types.float32
    xxu__owpf = ihgs__qjo(0)
    plwr__mnwe = qpa__ztop(0)
    xvhcr__cavtc = qpa__ztop(1)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.mad()'
        )

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        rrg__cshpz = xxu__owpf
        giprz__jrtmw = plwr__mnwe
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(A)):
            lwb__ojix = xxu__owpf
            jftpt__psg = plwr__mnwe
            if not bodo.libs.array_kernels.isna(A, vfqk__wgs) or not skipna:
                lwb__ojix = A[vfqk__wgs]
                jftpt__psg = xvhcr__cavtc
            rrg__cshpz += lwb__ojix
            giprz__jrtmw += jftpt__psg
        pnsk__dyd = bodo.hiframes.series_kernels._mean_handle_nan(rrg__cshpz,
            giprz__jrtmw)
        ftty__rrdpj = xxu__owpf
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(A)):
            lwb__ojix = xxu__owpf
            if not bodo.libs.array_kernels.isna(A, vfqk__wgs) or not skipna:
                lwb__ojix = abs(A[vfqk__wgs] - pnsk__dyd)
            ftty__rrdpj += lwb__ojix
        mof__ixoeh = bodo.hiframes.series_kernels._mean_handle_nan(ftty__rrdpj,
            giprz__jrtmw)
        return mof__ixoeh
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    hpae__wdbqg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', hpae__wdbqg, coxjz__zdc,
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
        dhy__igae = 0
        hdn__ool = 0
        giprz__jrtmw = 0
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(A)):
            lwb__ojix = 0
            jftpt__psg = 0
            if not bodo.libs.array_kernels.isna(A, vfqk__wgs) or not skipna:
                lwb__ojix = A[vfqk__wgs]
                jftpt__psg = 1
            dhy__igae += lwb__ojix
            hdn__ool += lwb__ojix * lwb__ojix
            giprz__jrtmw += jftpt__psg
        icyri__ipy = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            dhy__igae, hdn__ool, giprz__jrtmw, ddof)
        hrzoi__xffbj = bodo.hiframes.series_kernels._sem_handle_nan(icyri__ipy,
            giprz__jrtmw)
        return hrzoi__xffbj
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', hpae__wdbqg, coxjz__zdc,
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
        dhy__igae = 0.0
        hdn__ool = 0.0
        rfpzu__fqs = 0.0
        kxorc__traaj = 0.0
        giprz__jrtmw = 0
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(A)):
            lwb__ojix = 0.0
            jftpt__psg = 0
            if not bodo.libs.array_kernels.isna(A, vfqk__wgs) or not skipna:
                lwb__ojix = np.float64(A[vfqk__wgs])
                jftpt__psg = 1
            dhy__igae += lwb__ojix
            hdn__ool += lwb__ojix ** 2
            rfpzu__fqs += lwb__ojix ** 3
            kxorc__traaj += lwb__ojix ** 4
            giprz__jrtmw += jftpt__psg
        icyri__ipy = bodo.hiframes.series_kernels.compute_kurt(dhy__igae,
            hdn__ool, rfpzu__fqs, kxorc__traaj, giprz__jrtmw)
        return icyri__ipy
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', hpae__wdbqg, coxjz__zdc,
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
        dhy__igae = 0.0
        hdn__ool = 0.0
        rfpzu__fqs = 0.0
        giprz__jrtmw = 0
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(A)):
            lwb__ojix = 0.0
            jftpt__psg = 0
            if not bodo.libs.array_kernels.isna(A, vfqk__wgs) or not skipna:
                lwb__ojix = np.float64(A[vfqk__wgs])
                jftpt__psg = 1
            dhy__igae += lwb__ojix
            hdn__ool += lwb__ojix ** 2
            rfpzu__fqs += lwb__ojix ** 3
            giprz__jrtmw += jftpt__psg
        icyri__ipy = bodo.hiframes.series_kernels.compute_skew(dhy__igae,
            hdn__ool, rfpzu__fqs, giprz__jrtmw)
        return icyri__ipy
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', hpae__wdbqg, coxjz__zdc,
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
        zty__muz = bodo.hiframes.pd_series_ext.get_series_data(S)
        qmr__szp = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        onfhc__logtu = 0
        for vfqk__wgs in numba.parfors.parfor.internal_prange(len(zty__muz)):
            eqz__cayn = zty__muz[vfqk__wgs]
            jwv__ddu = qmr__szp[vfqk__wgs]
            onfhc__logtu += eqz__cayn * jwv__ddu
        return onfhc__logtu
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    hpae__wdbqg = dict(skipna=skipna)
    coxjz__zdc = dict(skipna=True)
    check_unsupported_args('Series.cumsum', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(skipna=skipna)
    coxjz__zdc = dict(skipna=True)
    check_unsupported_args('Series.cumprod', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(skipna=skipna)
    coxjz__zdc = dict(skipna=True)
    check_unsupported_args('Series.cummin', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(skipna=skipna)
    coxjz__zdc = dict(skipna=True)
    check_unsupported_args('Series.cummax', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    coxjz__zdc = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        smcp__yfcwe = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, smcp__yfcwe, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    hpae__wdbqg = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    coxjz__zdc = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(level=level)
    coxjz__zdc = dict(level=None)
    check_unsupported_args('Series.count', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    hpae__wdbqg = dict(method=method, min_periods=min_periods)
    coxjz__zdc = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.corr()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.corr()')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        cqali__uhje = S.sum()
        unicn__iuoa = other.sum()
        a = n * (S * other).sum() - cqali__uhje * unicn__iuoa
        crkq__wrek = n * (S ** 2).sum() - cqali__uhje ** 2
        aro__ruwl = n * (other ** 2).sum() - unicn__iuoa ** 2
        return a / np.sqrt(crkq__wrek * aro__ruwl)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    hpae__wdbqg = dict(min_periods=min_periods)
    coxjz__zdc = dict(min_periods=None)
    check_unsupported_args('Series.cov', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S, 'Series.cov()'
        )
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(other,
        'Series.cov()')

    def impl(S, other, min_periods=None, ddof=1):
        cqali__uhje = S.mean()
        unicn__iuoa = other.mean()
        hbu__nfh = ((S - cqali__uhje) * (other - unicn__iuoa)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(hbu__nfh, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            npht__wwzfz = np.sign(sum_val)
            return np.inf * npht__wwzfz
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    hpae__wdbqg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(axis=axis, skipna=skipna)
    coxjz__zdc = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(axis=axis, skipna=skipna)
    coxjz__zdc = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', hpae__wdbqg, coxjz__zdc,
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
    hpae__wdbqg = dict(level=level, numeric_only=numeric_only)
    coxjz__zdc = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', hpae__wdbqg, coxjz__zdc,
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
        yxe__zso = arr[:n]
        eitxb__rahwy = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(yxe__zso,
            eitxb__rahwy, name)
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
        ienui__ckvix = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yxe__zso = arr[ienui__ckvix:]
        eitxb__rahwy = index[ienui__ckvix:]
        return bodo.hiframes.pd_series_ext.init_series(yxe__zso,
            eitxb__rahwy, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    ivq__qmhqh = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ivq__qmhqh:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.first()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            xfyn__aqk = index[0]
            oshi__uzn = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, xfyn__aqk,
                False))
        else:
            oshi__uzn = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yxe__zso = arr[:oshi__uzn]
        eitxb__rahwy = index[:oshi__uzn]
        return bodo.hiframes.pd_series_ext.init_series(yxe__zso,
            eitxb__rahwy, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    ivq__qmhqh = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in ivq__qmhqh:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.last()')

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            ecmzj__qfwi = index[-1]
            oshi__uzn = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                ecmzj__qfwi, True))
        else:
            oshi__uzn = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yxe__zso = arr[len(arr) - oshi__uzn:]
        eitxb__rahwy = index[len(arr) - oshi__uzn:]
        return bodo.hiframes.pd_series_ext.init_series(yxe__zso,
            eitxb__rahwy, name)
    return impl


@overload_method(SeriesType, 'first_valid_index', inline='always',
    no_unliteral=True)
def overload_series_first_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wtva__ozt = bodo.utils.conversion.index_to_array(index)
        jgph__unyxy, bee__eii = bodo.libs.array_kernels.first_last_valid_index(
            arr, wtva__ozt)
        return bee__eii if jgph__unyxy else None
    return impl


@overload_method(SeriesType, 'last_valid_index', inline='always',
    no_unliteral=True)
def overload_series_last_valid_index(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wtva__ozt = bodo.utils.conversion.index_to_array(index)
        jgph__unyxy, bee__eii = bodo.libs.array_kernels.first_last_valid_index(
            arr, wtva__ozt, False)
        return bee__eii if jgph__unyxy else None
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    hpae__wdbqg = dict(keep=keep)
    coxjz__zdc = dict(keep='first')
    check_unsupported_args('Series.nlargest', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nlargest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wtva__ozt = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bmgx__ppfv, cbpv__hqsfh = bodo.libs.array_kernels.nlargest(arr,
            wtva__ozt, n, True, bodo.hiframes.series_kernels.gt_f)
        cas__bqf = bodo.utils.conversion.convert_to_index(cbpv__hqsfh)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, cas__bqf,
            name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    hpae__wdbqg = dict(keep=keep)
    coxjz__zdc = dict(keep='first')
    check_unsupported_args('Series.nsmallest', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.nsmallest()')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        wtva__ozt = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bmgx__ppfv, cbpv__hqsfh = bodo.libs.array_kernels.nlargest(arr,
            wtva__ozt, n, False, bodo.hiframes.series_kernels.lt_f)
        cas__bqf = bodo.utils.conversion.convert_to_index(cbpv__hqsfh)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, cas__bqf,
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
    hpae__wdbqg = dict(errors=errors)
    coxjz__zdc = dict(errors='raise')
    check_unsupported_args('Series.astype', hpae__wdbqg, coxjz__zdc,
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
        bmgx__ppfv = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    hpae__wdbqg = dict(axis=axis, is_copy=is_copy)
    coxjz__zdc = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        twyvd__qrf = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[twyvd__qrf],
            index[twyvd__qrf], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    hpae__wdbqg = dict(axis=axis, kind=kind, order=order)
    coxjz__zdc = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hhoj__bydk = S.notna().values
        if not hhoj__bydk.all():
            bmgx__ppfv = np.full(n, -1, np.int64)
            bmgx__ppfv[hhoj__bydk] = argsort(arr[hhoj__bydk])
        else:
            bmgx__ppfv = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'rank', inline='always', no_unliteral=True)
def overload_series_rank(S, axis=0, method='average', numeric_only=None,
    na_option='keep', ascending=True, pct=False):
    hpae__wdbqg = dict(axis=axis, numeric_only=numeric_only)
    coxjz__zdc = dict(axis=0, numeric_only=None)
    check_unsupported_args('Series.rank', hpae__wdbqg, coxjz__zdc,
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
        bmgx__ppfv = bodo.libs.array_kernels.rank(arr, method=method,
            na_option=na_option, ascending=ascending, pct=pct)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    hpae__wdbqg = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    coxjz__zdc = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )
    sqbt__wxqs = ColNamesMetaType(('$_bodo_col3_',))

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rbe__kgxm = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, sqbt__wxqs)
        clya__lldq = rbe__kgxm.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        bmgx__ppfv = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            clya__lldq, 0)
        cas__bqf = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            clya__lldq)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, cas__bqf,
            name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    hpae__wdbqg = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    coxjz__zdc = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )
    nvx__enw = ColNamesMetaType(('$_bodo_col_',))

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        rbe__kgxm = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, nvx__enw)
        clya__lldq = rbe__kgxm.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        bmgx__ppfv = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            clya__lldq, 0)
        cas__bqf = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            clya__lldq)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, cas__bqf,
            name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    epa__mvmn = is_overload_true(is_nullable)
    zfeak__vrmq = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    zfeak__vrmq += '  numba.parfors.parfor.init_prange()\n'
    zfeak__vrmq += '  n = len(arr)\n'
    if epa__mvmn:
        zfeak__vrmq += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        zfeak__vrmq += '  out_arr = np.empty(n, np.int64)\n'
    zfeak__vrmq += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    zfeak__vrmq += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if epa__mvmn:
        zfeak__vrmq += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        zfeak__vrmq += '      out_arr[i] = -1\n'
    zfeak__vrmq += '      continue\n'
    zfeak__vrmq += '    val = arr[i]\n'
    zfeak__vrmq += '    if include_lowest and val == bins[0]:\n'
    zfeak__vrmq += '      ind = 1\n'
    zfeak__vrmq += '    else:\n'
    zfeak__vrmq += '      ind = np.searchsorted(bins, val)\n'
    zfeak__vrmq += '    if ind == 0 or ind == len(bins):\n'
    if epa__mvmn:
        zfeak__vrmq += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        zfeak__vrmq += '      out_arr[i] = -1\n'
    zfeak__vrmq += '    else:\n'
    zfeak__vrmq += '      out_arr[i] = ind - 1\n'
    zfeak__vrmq += '  return out_arr\n'
    vqs__gskw = {}
    exec(zfeak__vrmq, {'bodo': bodo, 'np': np, 'numba': numba}, vqs__gskw)
    impl = vqs__gskw['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        apvvd__borz, kfcz__eyg = np.divmod(x, 1)
        if apvvd__borz == 0:
            bcp__icnf = -int(np.floor(np.log10(abs(kfcz__eyg)))
                ) - 1 + precision
        else:
            bcp__icnf = precision
        return np.around(x, bcp__icnf)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        xaaq__haqim = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(xaaq__haqim)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        boy__bbib = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            fpdew__fav = bins.copy()
            if right and include_lowest:
                fpdew__fav[0] = fpdew__fav[0] - boy__bbib
            hqjtb__zdu = bodo.libs.interval_arr_ext.init_interval_array(
                fpdew__fav[:-1], fpdew__fav[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(hqjtb__zdu,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        fpdew__fav = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            fpdew__fav[0] = fpdew__fav[0] - 10.0 ** -precision
        hqjtb__zdu = bodo.libs.interval_arr_ext.init_interval_array(fpdew__fav
            [:-1], fpdew__fav[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(hqjtb__zdu, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        gup__lnqco = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        mbd__luq = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        bmgx__ppfv = np.zeros(nbins, np.int64)
        for vfqk__wgs in range(len(gup__lnqco)):
            bmgx__ppfv[mbd__luq[vfqk__wgs]] = gup__lnqco[vfqk__wgs]
        return bmgx__ppfv
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
            lofcx__lujy = (max_val - min_val) * 0.001
            if right:
                bins[0] -= lofcx__lujy
            else:
                bins[-1] += lofcx__lujy
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    hpae__wdbqg = dict(dropna=dropna)
    coxjz__zdc = dict(dropna=True)
    check_unsupported_args('Series.value_counts', hpae__wdbqg, coxjz__zdc,
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
    gpevx__woxh = not is_overload_none(bins)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.value_counts()')
    zfeak__vrmq = 'def impl(\n'
    zfeak__vrmq += '    S,\n'
    zfeak__vrmq += '    normalize=False,\n'
    zfeak__vrmq += '    sort=True,\n'
    zfeak__vrmq += '    ascending=False,\n'
    zfeak__vrmq += '    bins=None,\n'
    zfeak__vrmq += '    dropna=True,\n'
    zfeak__vrmq += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    zfeak__vrmq += '):\n'
    zfeak__vrmq += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    zfeak__vrmq += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    zfeak__vrmq += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if gpevx__woxh:
        zfeak__vrmq += '    right = True\n'
        zfeak__vrmq += _gen_bins_handling(bins, S.dtype)
        zfeak__vrmq += '    arr = get_bin_inds(bins, arr)\n'
    zfeak__vrmq += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    zfeak__vrmq += (
        '        (arr,), index, __col_name_meta_value_series_value_counts\n')
    zfeak__vrmq += '    )\n'
    zfeak__vrmq += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if gpevx__woxh:
        zfeak__vrmq += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        zfeak__vrmq += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        zfeak__vrmq += '    index = get_bin_labels(bins)\n'
    else:
        zfeak__vrmq += """    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
"""
        zfeak__vrmq += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        zfeak__vrmq += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        zfeak__vrmq += '    )\n'
        zfeak__vrmq += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    zfeak__vrmq += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        zfeak__vrmq += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        klbqg__tcwy = 'len(S)' if gpevx__woxh else 'count_arr.sum()'
        zfeak__vrmq += f'    res = res / float({klbqg__tcwy})\n'
    zfeak__vrmq += '    return res\n'
    vqs__gskw = {}
    exec(zfeak__vrmq, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins, '__col_name_meta_value_series_value_counts':
        ColNamesMetaType(('$_bodo_col2_',))}, vqs__gskw)
    impl = vqs__gskw['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    zfeak__vrmq = ''
    if isinstance(bins, types.Integer):
        zfeak__vrmq += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        zfeak__vrmq += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            zfeak__vrmq += '    min_val = min_val.value\n'
            zfeak__vrmq += '    max_val = max_val.value\n'
        zfeak__vrmq += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            zfeak__vrmq += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        zfeak__vrmq += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return zfeak__vrmq


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    hpae__wdbqg = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    coxjz__zdc = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='General')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x, 'pandas.cut()'
        )
    zfeak__vrmq = 'def impl(\n'
    zfeak__vrmq += '    x,\n'
    zfeak__vrmq += '    bins,\n'
    zfeak__vrmq += '    right=True,\n'
    zfeak__vrmq += '    labels=None,\n'
    zfeak__vrmq += '    retbins=False,\n'
    zfeak__vrmq += '    precision=3,\n'
    zfeak__vrmq += '    include_lowest=False,\n'
    zfeak__vrmq += "    duplicates='raise',\n"
    zfeak__vrmq += '    ordered=True\n'
    zfeak__vrmq += '):\n'
    if isinstance(x, SeriesType):
        zfeak__vrmq += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        zfeak__vrmq += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        zfeak__vrmq += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        zfeak__vrmq += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    zfeak__vrmq += _gen_bins_handling(bins, x.dtype)
    zfeak__vrmq += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    zfeak__vrmq += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    zfeak__vrmq += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    zfeak__vrmq += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        zfeak__vrmq += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        zfeak__vrmq += '    return res\n'
    else:
        zfeak__vrmq += '    return out_arr\n'
    vqs__gskw = {}
    exec(zfeak__vrmq, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, vqs__gskw)
    impl = vqs__gskw['impl']
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
    hpae__wdbqg = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    coxjz__zdc = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(x,
        'pandas.qcut()')

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        fsunu__ucvhk = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, fsunu__ucvhk)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    hpae__wdbqg = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze
        =squeeze, observed=observed, dropna=dropna)
    coxjz__zdc = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', hpae__wdbqg, coxjz__zdc,
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
        dyn__fln = ColNamesMetaType((' ', ''))

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            wdld__uohkp = bodo.utils.conversion.coerce_to_array(index)
            rbe__kgxm = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                wdld__uohkp, arr), index, dyn__fln)
            return rbe__kgxm.groupby(' ')['']
        return impl_index
    qjtgb__ytbp = by
    if isinstance(by, SeriesType):
        qjtgb__ytbp = by.data
    if isinstance(qjtgb__ytbp, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )
    ngaw__nva = ColNamesMetaType((' ', ''))

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        wdld__uohkp = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        rbe__kgxm = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            wdld__uohkp, arr), index, ngaw__nva)
        return rbe__kgxm.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    hpae__wdbqg = dict(verify_integrity=verify_integrity)
    coxjz__zdc = dict(verify_integrity=False)
    check_unsupported_args('Series.append', hpae__wdbqg, coxjz__zdc,
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
            vijd__blkg = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            bmgx__ppfv = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(bmgx__ppfv, A, vijd__blkg, False)
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bmgx__ppfv = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    hpae__wdbqg = dict(interpolation=interpolation)
    coxjz__zdc = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.quantile()')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            bmgx__ppfv = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
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
        lnwcm__deqi = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(lnwcm__deqi, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    hpae__wdbqg = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    coxjz__zdc = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', hpae__wdbqg, coxjz__zdc,
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
        rel__lwu = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        rel__lwu = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    zfeak__vrmq = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {rel__lwu}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    rhv__iagk = dict()
    exec(zfeak__vrmq, {'bodo': bodo, 'numba': numba}, rhv__iagk)
    glc__vkph = rhv__iagk['impl']
    return glc__vkph


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        rel__lwu = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        rel__lwu = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    zfeak__vrmq = 'def impl(S,\n'
    zfeak__vrmq += '     value=None,\n'
    zfeak__vrmq += '    method=None,\n'
    zfeak__vrmq += '    axis=None,\n'
    zfeak__vrmq += '    inplace=False,\n'
    zfeak__vrmq += '    limit=None,\n'
    zfeak__vrmq += '   downcast=None,\n'
    zfeak__vrmq += '):\n'
    zfeak__vrmq += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    zfeak__vrmq += '    n = len(in_arr)\n'
    zfeak__vrmq += f'    out_arr = {rel__lwu}(n, -1)\n'
    zfeak__vrmq += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    zfeak__vrmq += '        s = in_arr[j]\n'
    zfeak__vrmq += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    zfeak__vrmq += '            s = value\n'
    zfeak__vrmq += '        out_arr[j] = s\n'
    zfeak__vrmq += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    rhv__iagk = dict()
    exec(zfeak__vrmq, {'bodo': bodo, 'numba': numba}, rhv__iagk)
    glc__vkph = rhv__iagk['impl']
    return glc__vkph


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
    vlrmf__wctq = bodo.hiframes.pd_series_ext.get_series_data(value)
    for vfqk__wgs in numba.parfors.parfor.internal_prange(len(fbdei__tncog)):
        s = fbdei__tncog[vfqk__wgs]
        if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs
            ) and not bodo.libs.array_kernels.isna(vlrmf__wctq, vfqk__wgs):
            s = vlrmf__wctq[vfqk__wgs]
        fbdei__tncog[vfqk__wgs] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
    for vfqk__wgs in numba.parfors.parfor.internal_prange(len(fbdei__tncog)):
        s = fbdei__tncog[vfqk__wgs]
        if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs):
            s = value
        fbdei__tncog[vfqk__wgs] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    vlrmf__wctq = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(fbdei__tncog)
    bmgx__ppfv = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for rvfvy__xpdqq in numba.parfors.parfor.internal_prange(n):
        s = fbdei__tncog[rvfvy__xpdqq]
        if bodo.libs.array_kernels.isna(fbdei__tncog, rvfvy__xpdqq
            ) and not bodo.libs.array_kernels.isna(vlrmf__wctq, rvfvy__xpdqq):
            s = vlrmf__wctq[rvfvy__xpdqq]
        bmgx__ppfv[rvfvy__xpdqq] = s
        if bodo.libs.array_kernels.isna(fbdei__tncog, rvfvy__xpdqq
            ) and bodo.libs.array_kernels.isna(vlrmf__wctq, rvfvy__xpdqq):
            bodo.libs.array_kernels.setna(bmgx__ppfv, rvfvy__xpdqq)
    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    vlrmf__wctq = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(fbdei__tncog)
    bmgx__ppfv = bodo.utils.utils.alloc_type(n, fbdei__tncog.dtype, (-1,))
    for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
        s = fbdei__tncog[vfqk__wgs]
        if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs
            ) and not bodo.libs.array_kernels.isna(vlrmf__wctq, vfqk__wgs):
            s = vlrmf__wctq[vfqk__wgs]
        bmgx__ppfv[vfqk__wgs] = s
    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    hpae__wdbqg = dict(limit=limit, downcast=downcast)
    coxjz__zdc = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', hpae__wdbqg, coxjz__zdc,
        package_name='pandas', module_name='Series')
    grah__hpu = not is_overload_none(value)
    atko__tas = not is_overload_none(method)
    if grah__hpu and atko__tas:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not grah__hpu and not atko__tas:
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
    if atko__tas:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        jvovp__zfuey = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(jvovp__zfuey)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(jvovp__zfuey)
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.fillna()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(value,
        'Series.fillna()')
    ekvs__kygj = element_type(S.data)
    unm__qqh = None
    if grah__hpu:
        unm__qqh = element_type(types.unliteral(value))
    if unm__qqh and not can_replace(ekvs__kygj, unm__qqh):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {unm__qqh} with series type {ekvs__kygj}'
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
        gke__ifqw = to_str_arr_if_dict_array(S.data)
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                vlrmf__wctq = bodo.hiframes.pd_series_ext.get_series_data(value
                    )
                n = len(fbdei__tncog)
                bmgx__ppfv = bodo.utils.utils.alloc_type(n, gke__ifqw, (-1,))
                for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs
                        ) and bodo.libs.array_kernels.isna(vlrmf__wctq,
                        vfqk__wgs):
                        bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                        continue
                    if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs):
                        bmgx__ppfv[vfqk__wgs
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            vlrmf__wctq[vfqk__wgs])
                        continue
                    bmgx__ppfv[vfqk__wgs
                        ] = bodo.utils.conversion.unbox_if_timestamp(
                        fbdei__tncog[vfqk__wgs])
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return fillna_series_impl
        if atko__tas:
            vnvl__zyxmj = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(ekvs__kygj, (types.Integer, types.Float)
                ) and ekvs__kygj not in vnvl__zyxmj:
                raise BodoError(
                    f"Series.fillna(): series of type {ekvs__kygj} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                bmgx__ppfv = bodo.libs.array_kernels.ffill_bfill_arr(
                    fbdei__tncog, method)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(fbdei__tncog)
            bmgx__ppfv = bodo.utils.utils.alloc_type(n, gke__ifqw, (-1,))
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(fbdei__tncog[
                    vfqk__wgs])
                if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs):
                    s = value
                bmgx__ppfv[vfqk__wgs] = s
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        oun__psq = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        hpae__wdbqg = dict(limit=limit, downcast=downcast)
        coxjz__zdc = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', hpae__wdbqg,
            coxjz__zdc, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        ekvs__kygj = element_type(S.data)
        vnvl__zyxmj = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(ekvs__kygj, (types.Integer, types.Float)
            ) and ekvs__kygj not in vnvl__zyxmj:
            raise BodoError(
                f'Series.{overload_name}(): series of type {ekvs__kygj} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            bmgx__ppfv = bodo.libs.array_kernels.ffill_bfill_arr(fbdei__tncog,
                oun__psq)
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        avqy__tbtt = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            avqy__tbtt)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        vseoe__lek = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(vseoe__lek)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        vseoe__lek = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(vseoe__lek)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        vseoe__lek = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(vseoe__lek)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    hpae__wdbqg = dict(inplace=inplace, limit=limit, regex=regex, method=method
        )
    aavj__pmszw = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', hpae__wdbqg, aavj__pmszw,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.replace()')
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    ekvs__kygj = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        lqba__cnq = element_type(to_replace.key_type)
        unm__qqh = element_type(to_replace.value_type)
    else:
        lqba__cnq = element_type(to_replace)
        unm__qqh = element_type(value)
    zgihb__zjgxp = None
    if ekvs__kygj != types.unliteral(lqba__cnq):
        if bodo.utils.typing.equality_always_false(ekvs__kygj, types.
            unliteral(lqba__cnq)
            ) or not bodo.utils.typing.types_equality_exists(ekvs__kygj,
            lqba__cnq):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(ekvs__kygj, (types.Float, types.Integer)
            ) or ekvs__kygj == np.bool_:
            zgihb__zjgxp = ekvs__kygj
    if not can_replace(ekvs__kygj, types.unliteral(unm__qqh)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    yev__uajwh = to_str_arr_if_dict_array(S.data)
    if isinstance(yev__uajwh, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(fbdei__tncog.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(fbdei__tncog)
        bmgx__ppfv = bodo.utils.utils.alloc_type(n, yev__uajwh, (-1,))
        goeuu__havt = build_replace_dict(to_replace, value, zgihb__zjgxp)
        for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(fbdei__tncog, vfqk__wgs):
                bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                continue
            s = fbdei__tncog[vfqk__wgs]
            if s in goeuu__havt:
                s = goeuu__havt[s]
            bmgx__ppfv[vfqk__wgs] = s
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    nsp__rjzd = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    iwhk__aspox = is_iterable_type(to_replace)
    alhd__jzbl = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    xqpt__avu = is_iterable_type(value)
    if nsp__rjzd and alhd__jzbl:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                goeuu__havt = {}
                goeuu__havt[key_dtype_conv(to_replace)] = value
                return goeuu__havt
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            goeuu__havt = {}
            goeuu__havt[to_replace] = value
            return goeuu__havt
        return impl
    if iwhk__aspox and alhd__jzbl:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                goeuu__havt = {}
                for uysr__jglt in to_replace:
                    goeuu__havt[key_dtype_conv(uysr__jglt)] = value
                return goeuu__havt
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            goeuu__havt = {}
            for uysr__jglt in to_replace:
                goeuu__havt[uysr__jglt] = value
            return goeuu__havt
        return impl
    if iwhk__aspox and xqpt__avu:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                goeuu__havt = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for vfqk__wgs in range(len(to_replace)):
                    goeuu__havt[key_dtype_conv(to_replace[vfqk__wgs])] = value[
                        vfqk__wgs]
                return goeuu__havt
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            goeuu__havt = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for vfqk__wgs in range(len(to_replace)):
                goeuu__havt[to_replace[vfqk__wgs]] = value[vfqk__wgs]
            return goeuu__havt
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
            bmgx__ppfv = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bmgx__ppfv = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    hpae__wdbqg = dict(ignore_index=ignore_index)
    xxal__zom = dict(ignore_index=False)
    check_unsupported_args('Series.explode', hpae__wdbqg, xxal__zom,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtva__ozt = bodo.utils.conversion.index_to_array(index)
        bmgx__ppfv, ekxfz__pyp = bodo.libs.array_kernels.explode(arr, wtva__ozt
            )
        cas__bqf = bodo.utils.conversion.index_from_array(ekxfz__pyp)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, cas__bqf,
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
            wwz__jfs = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                wwz__jfs[vfqk__wgs] = np.argmax(a[vfqk__wgs])
            return wwz__jfs
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            qmvz__uvbmk = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                qmvz__uvbmk[vfqk__wgs] = np.argmin(a[vfqk__wgs])
            return qmvz__uvbmk
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
    hpae__wdbqg = dict(axis=axis, inplace=inplace, how=how)
    aez__stxx = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', hpae__wdbqg, aez__stxx,
        package_name='pandas', module_name='Series')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(S,
        'Series.dropna()')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            hhoj__bydk = S.notna().values
            wtva__ozt = bodo.utils.conversion.extract_index_array(S)
            cas__bqf = bodo.utils.conversion.convert_to_index(wtva__ozt[
                hhoj__bydk])
            bmgx__ppfv = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(fbdei__tncog))
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                cas__bqf, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            wtva__ozt = bodo.utils.conversion.extract_index_array(S)
            hhoj__bydk = S.notna().values
            cas__bqf = bodo.utils.conversion.convert_to_index(wtva__ozt[
                hhoj__bydk])
            bmgx__ppfv = fbdei__tncog[hhoj__bydk]
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                cas__bqf, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    hpae__wdbqg = dict(freq=freq, axis=axis, fill_value=fill_value)
    coxjz__zdc = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', hpae__wdbqg, coxjz__zdc,
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
        bmgx__ppfv = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    hpae__wdbqg = dict(fill_method=fill_method, limit=limit, freq=freq)
    coxjz__zdc = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', hpae__wdbqg, coxjz__zdc,
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
        bmgx__ppfv = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
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
            aeb__zeika = 'None'
        else:
            aeb__zeika = 'other'
        zfeak__vrmq = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            zfeak__vrmq += '  cond = ~cond\n'
        zfeak__vrmq += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        zfeak__vrmq += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zfeak__vrmq += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zfeak__vrmq += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {aeb__zeika})
"""
        zfeak__vrmq += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        vqs__gskw = {}
        exec(zfeak__vrmq, {'bodo': bodo, 'np': np}, vqs__gskw)
        impl = vqs__gskw['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        avqy__tbtt = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(avqy__tbtt)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, module_name, S, cond, other,
    inplace, axis, level, errors, try_cast):
    hpae__wdbqg = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    coxjz__zdc = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', hpae__wdbqg, coxjz__zdc,
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
    rupsi__iwwo = is_overload_constant_nan(other)
    if not (is_default or rupsi__iwwo or is_scalar_type(other) or 
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
            iifx__ifj = arr.dtype.elem_type
        else:
            iifx__ifj = arr.dtype
        if is_iterable_type(other):
            mrbhz__uqw = other.dtype
        elif rupsi__iwwo:
            mrbhz__uqw = types.float64
        else:
            mrbhz__uqw = types.unliteral(other)
        if not rupsi__iwwo and not is_common_scalar_dtype([iifx__ifj,
            mrbhz__uqw]):
            raise BodoError(
                f"{func_name}() {module_name.lower()} and 'other' must share a common type."
                )


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        hpae__wdbqg = dict(level=level, axis=axis)
        coxjz__zdc = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), hpae__wdbqg,
            coxjz__zdc, package_name='pandas', module_name='Series')
        iiaui__qqx = other == string_type or is_overload_constant_str(other)
        pkjbi__gwbpz = is_iterable_type(other) and other.dtype == string_type
        dbkaq__glsg = S.dtype == string_type and (op == operator.add and (
            iiaui__qqx or pkjbi__gwbpz) or op == operator.mul and
            isinstance(other, types.Integer))
        xhb__ptuy = S.dtype == bodo.timedelta64ns
        nbi__zjyb = S.dtype == bodo.datetime64ns
        xbwmy__tabhc = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        odgk__yblux = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        res__pdn = xhb__ptuy and (xbwmy__tabhc or odgk__yblux
            ) or nbi__zjyb and xbwmy__tabhc
        res__pdn = res__pdn and op == operator.add
        if not (isinstance(S.dtype, types.Number) or dbkaq__glsg or res__pdn):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        prrij__nwa = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            yev__uajwh = prrij__nwa.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and yev__uajwh == types.Array(types.bool_, 1, 'C'):
                yev__uajwh = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                bmgx__ppfv = bodo.utils.utils.alloc_type(n, yev__uajwh, (-1,))
                for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                    qnm__aklh = bodo.libs.array_kernels.isna(arr, vfqk__wgs)
                    if qnm__aklh:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs
                                )
                        else:
                            bmgx__ppfv[vfqk__wgs] = op(fill_value, other)
                    else:
                        bmgx__ppfv[vfqk__wgs] = op(arr[vfqk__wgs], other)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        yev__uajwh = prrij__nwa.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and yev__uajwh == types.Array(
            types.bool_, 1, 'C'):
            yev__uajwh = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zaah__cfue = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            bmgx__ppfv = bodo.utils.utils.alloc_type(n, yev__uajwh, (-1,))
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                qnm__aklh = bodo.libs.array_kernels.isna(arr, vfqk__wgs)
                icc__zmey = bodo.libs.array_kernels.isna(zaah__cfue, vfqk__wgs)
                if qnm__aklh and icc__zmey:
                    bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                elif qnm__aklh:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                    else:
                        bmgx__ppfv[vfqk__wgs] = op(fill_value, zaah__cfue[
                            vfqk__wgs])
                elif icc__zmey:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                    else:
                        bmgx__ppfv[vfqk__wgs] = op(arr[vfqk__wgs], fill_value)
                else:
                    bmgx__ppfv[vfqk__wgs] = op(arr[vfqk__wgs], zaah__cfue[
                        vfqk__wgs])
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
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
        prrij__nwa = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            yev__uajwh = prrij__nwa.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and yev__uajwh == types.Array(types.bool_, 1, 'C'):
                yev__uajwh = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                bmgx__ppfv = bodo.utils.utils.alloc_type(n, yev__uajwh, None)
                for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                    qnm__aklh = bodo.libs.array_kernels.isna(arr, vfqk__wgs)
                    if qnm__aklh:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs
                                )
                        else:
                            bmgx__ppfv[vfqk__wgs] = op(other, fill_value)
                    else:
                        bmgx__ppfv[vfqk__wgs] = op(other, arr[vfqk__wgs])
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        yev__uajwh = prrij__nwa.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and yev__uajwh == types.Array(
            types.bool_, 1, 'C'):
            yev__uajwh = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            zaah__cfue = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            bmgx__ppfv = bodo.utils.utils.alloc_type(n, yev__uajwh, None)
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                qnm__aklh = bodo.libs.array_kernels.isna(arr, vfqk__wgs)
                icc__zmey = bodo.libs.array_kernels.isna(zaah__cfue, vfqk__wgs)
                bmgx__ppfv[vfqk__wgs] = op(zaah__cfue[vfqk__wgs], arr[
                    vfqk__wgs])
                if qnm__aklh and icc__zmey:
                    bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                elif qnm__aklh:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                    else:
                        bmgx__ppfv[vfqk__wgs] = op(zaah__cfue[vfqk__wgs],
                            fill_value)
                elif icc__zmey:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                    else:
                        bmgx__ppfv[vfqk__wgs] = op(fill_value, arr[vfqk__wgs])
                else:
                    bmgx__ppfv[vfqk__wgs] = op(zaah__cfue[vfqk__wgs], arr[
                        vfqk__wgs])
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
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
    for op, edofm__rsjr in explicit_binop_funcs_two_ways.items():
        for name in edofm__rsjr:
            avqy__tbtt = create_explicit_binary_op_overload(op)
            yws__ntui = create_explicit_binary_reverse_op_overload(op)
            xbs__rezpa = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(avqy__tbtt)
            overload_method(SeriesType, xbs__rezpa, no_unliteral=True)(
                yws__ntui)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        avqy__tbtt = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(avqy__tbtt)
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
                vos__jujjt = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                bmgx__ppfv = dt64_arr_sub(arr, vos__jujjt)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
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
                bmgx__ppfv = np.empty(n, np.dtype('datetime64[ns]'))
                for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, vfqk__wgs):
                        bodo.libs.array_kernels.setna(bmgx__ppfv, vfqk__wgs)
                        continue
                    hxyd__zgcm = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[vfqk__wgs]))
                    fjdc__myc = op(hxyd__zgcm, rhs)
                    bmgx__ppfv[vfqk__wgs
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        fjdc__myc.value)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
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
                    vos__jujjt = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    bmgx__ppfv = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(vos__jujjt))
                    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                vos__jujjt = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                bmgx__ppfv = op(arr, vos__jujjt)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    ehzjl__cjrr = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    bmgx__ppfv = op(bodo.utils.conversion.
                        unbox_if_timestamp(ehzjl__cjrr), arr)
                    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ehzjl__cjrr = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                bmgx__ppfv = op(ehzjl__cjrr, arr)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        avqy__tbtt = create_binary_op_overload(op)
        overload(op)(avqy__tbtt)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    rxk__ojnh = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, rxk__ojnh)
        for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, vfqk__wgs
                ) or bodo.libs.array_kernels.isna(arg2, vfqk__wgs):
                bodo.libs.array_kernels.setna(S, vfqk__wgs)
                continue
            S[vfqk__wgs
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                vfqk__wgs]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[vfqk__wgs]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                zaah__cfue = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, zaah__cfue)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        avqy__tbtt = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(avqy__tbtt)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                bmgx__ppfv = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        avqy__tbtt = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(avqy__tbtt)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    bmgx__ppfv = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
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
                    zaah__cfue = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    bmgx__ppfv = ufunc(arr, zaah__cfue)
                    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    zaah__cfue = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    bmgx__ppfv = ufunc(arr, zaah__cfue)
                    return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        avqy__tbtt = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(avqy__tbtt)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        qvei__toz = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),))
        gzx__dietw = np.arange(n),
        bodo.libs.timsort.sort(qvei__toz, 0, n, gzx__dietw)
        return gzx__dietw[0]
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
        dnlma__ysd = get_overload_const_str(downcast)
        if dnlma__ysd in ('integer', 'signed'):
            out_dtype = types.int64
        elif dnlma__ysd == 'unsigned':
            out_dtype = types.uint64
        else:
            assert dnlma__ysd == 'float'
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arg_a,
        'pandas.to_numeric()')
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            fbdei__tncog = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            bmgx__ppfv = pd.to_numeric(fbdei__tncog, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                index, name)
        return impl_series
    if not is_str_arr_type(arg_a):
        raise BodoError(f'pd.to_numeric(): invalid argument type {arg_a}')
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            irjag__ehxe = np.empty(n, np.float64)
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, vfqk__wgs):
                    bodo.libs.array_kernels.setna(irjag__ehxe, vfqk__wgs)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(irjag__ehxe,
                        vfqk__wgs, arg_a, vfqk__wgs)
            return irjag__ehxe
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            irjag__ehxe = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, vfqk__wgs):
                    bodo.libs.array_kernels.setna(irjag__ehxe, vfqk__wgs)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(irjag__ehxe,
                        vfqk__wgs, arg_a, vfqk__wgs)
            return irjag__ehxe
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        yvn__ejh = if_series_to_array_type(args[0])
        if isinstance(yvn__ejh, types.Array) and isinstance(yvn__ejh.dtype,
            types.Integer):
            yvn__ejh = types.Array(types.float64, 1, 'C')
        return yvn__ejh(*args)


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
    gtv__dnx = bodo.utils.utils.is_array_typ(x, True)
    sfjt__ytafv = bodo.utils.utils.is_array_typ(y, True)
    zfeak__vrmq = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        zfeak__vrmq += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if gtv__dnx and not bodo.utils.utils.is_array_typ(x, False):
        zfeak__vrmq += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if sfjt__ytafv and not bodo.utils.utils.is_array_typ(y, False):
        zfeak__vrmq += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    zfeak__vrmq += '  n = len(condition)\n'
    wff__roc = x.dtype if gtv__dnx else types.unliteral(x)
    mququ__jkuo = y.dtype if sfjt__ytafv else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        wff__roc = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        mququ__jkuo = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    cvn__rtmg = get_data(x)
    vruwf__armf = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(gzx__dietw) for
        gzx__dietw in [cvn__rtmg, vruwf__armf])
    if vruwf__armf == types.none:
        if isinstance(wff__roc, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif cvn__rtmg == vruwf__armf and not is_nullable:
        out_dtype = dtype_to_array_type(wff__roc)
    elif wff__roc == string_type or mququ__jkuo == string_type:
        out_dtype = bodo.string_array_type
    elif cvn__rtmg == bytes_type or (gtv__dnx and wff__roc == bytes_type) and (
        vruwf__armf == bytes_type or sfjt__ytafv and mququ__jkuo == bytes_type
        ):
        out_dtype = binary_array_type
    elif isinstance(wff__roc, bodo.PDCategoricalDtype):
        out_dtype = None
    elif wff__roc in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(wff__roc, 1, 'C')
    elif mququ__jkuo in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(mququ__jkuo, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(wff__roc), numba.np.numpy_support.
            as_dtype(mququ__jkuo)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(wff__roc, bodo.PDCategoricalDtype):
        arjv__vgmc = 'x'
    else:
        arjv__vgmc = 'out_dtype'
    zfeak__vrmq += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {arjv__vgmc}, (-1,))\n')
    if isinstance(wff__roc, bodo.PDCategoricalDtype):
        zfeak__vrmq += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        zfeak__vrmq += """  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)
"""
    zfeak__vrmq += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    zfeak__vrmq += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if gtv__dnx:
        zfeak__vrmq += '      if bodo.libs.array_kernels.isna(x, j):\n'
        zfeak__vrmq += '        setna(out_arr, j)\n'
        zfeak__vrmq += '        continue\n'
    if isinstance(wff__roc, bodo.PDCategoricalDtype):
        zfeak__vrmq += '      out_codes[j] = x_codes[j]\n'
    else:
        zfeak__vrmq += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if gtv__dnx else 'x'))
    zfeak__vrmq += '    else:\n'
    if sfjt__ytafv:
        zfeak__vrmq += '      if bodo.libs.array_kernels.isna(y, j):\n'
        zfeak__vrmq += '        setna(out_arr, j)\n'
        zfeak__vrmq += '        continue\n'
    if vruwf__armf == types.none:
        if isinstance(wff__roc, bodo.PDCategoricalDtype):
            zfeak__vrmq += '      out_codes[j] = -1\n'
        else:
            zfeak__vrmq += '      setna(out_arr, j)\n'
    else:
        zfeak__vrmq += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if sfjt__ytafv else 'y'))
    zfeak__vrmq += '  return out_arr\n'
    vqs__gskw = {}
    exec(zfeak__vrmq, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, vqs__gskw)
    vrv__vlp = vqs__gskw['_impl']
    return vrv__vlp


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
        ylws__fjesb = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(ylws__fjesb, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(ylws__fjesb):
            zsqrv__grb = ylws__fjesb.data.dtype
        else:
            zsqrv__grb = ylws__fjesb.dtype
        if isinstance(zsqrv__grb, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        sngfc__jxxjs = ylws__fjesb
    else:
        kgokz__dxsq = []
        for ylws__fjesb in choicelist:
            if not bodo.utils.utils.is_array_typ(ylws__fjesb, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(ylws__fjesb):
                zsqrv__grb = ylws__fjesb.data.dtype
            else:
                zsqrv__grb = ylws__fjesb.dtype
            if isinstance(zsqrv__grb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            kgokz__dxsq.append(zsqrv__grb)
        if not is_common_scalar_dtype(kgokz__dxsq):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        sngfc__jxxjs = choicelist[0]
    if is_series_type(sngfc__jxxjs):
        sngfc__jxxjs = sngfc__jxxjs.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, sngfc__jxxjs.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(sngfc__jxxjs, types.Array) or isinstance(
        sngfc__jxxjs, BooleanArrayType) or isinstance(sngfc__jxxjs,
        IntegerArrayType) or bodo.utils.utils.is_array_typ(sngfc__jxxjs, 
        False) and sngfc__jxxjs.dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {sngfc__jxxjs} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    tpws__tdx = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        znui__efxt = choicelist.dtype
    else:
        bpbmh__lfy = False
        kgokz__dxsq = []
        for ylws__fjesb in choicelist:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                ylws__fjesb, 'numpy.select()')
            if is_nullable_type(ylws__fjesb):
                bpbmh__lfy = True
            if is_series_type(ylws__fjesb):
                zsqrv__grb = ylws__fjesb.data.dtype
            else:
                zsqrv__grb = ylws__fjesb.dtype
            if isinstance(zsqrv__grb, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            kgokz__dxsq.append(zsqrv__grb)
        cyl__xsyjd, umm__hsq = get_common_scalar_dtype(kgokz__dxsq)
        if not umm__hsq:
            raise BodoError('Internal error in overload_np_select')
        tmn__rli = dtype_to_array_type(cyl__xsyjd)
        if bpbmh__lfy:
            tmn__rli = to_nullable_type(tmn__rli)
        znui__efxt = tmn__rli
    if isinstance(znui__efxt, SeriesType):
        znui__efxt = znui__efxt.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        zwun__dqulm = True
    else:
        zwun__dqulm = False
    giry__urntj = False
    aeor__bdpnn = False
    if zwun__dqulm:
        if isinstance(znui__efxt.dtype, types.Number):
            pass
        elif znui__efxt.dtype == types.bool_:
            aeor__bdpnn = True
        else:
            giry__urntj = True
            znui__efxt = to_nullable_type(znui__efxt)
    elif default == types.none or is_overload_constant_nan(default):
        giry__urntj = True
        znui__efxt = to_nullable_type(znui__efxt)
    zfeak__vrmq = 'def np_select_impl(condlist, choicelist, default=0):\n'
    zfeak__vrmq += '  if len(condlist) != len(choicelist):\n'
    zfeak__vrmq += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    zfeak__vrmq += '  output_len = len(choicelist[0])\n'
    zfeak__vrmq += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    zfeak__vrmq += '  for i in range(output_len):\n'
    if giry__urntj:
        zfeak__vrmq += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif aeor__bdpnn:
        zfeak__vrmq += '    out[i] = False\n'
    else:
        zfeak__vrmq += '    out[i] = default\n'
    if tpws__tdx:
        zfeak__vrmq += '  for i in range(len(condlist) - 1, -1, -1):\n'
        zfeak__vrmq += '    cond = condlist[i]\n'
        zfeak__vrmq += '    choice = choicelist[i]\n'
        zfeak__vrmq += '    out = np.where(cond, choice, out)\n'
    else:
        for vfqk__wgs in range(len(choicelist) - 1, -1, -1):
            zfeak__vrmq += f'  cond = condlist[{vfqk__wgs}]\n'
            zfeak__vrmq += f'  choice = choicelist[{vfqk__wgs}]\n'
            zfeak__vrmq += f'  out = np.where(cond, choice, out)\n'
    zfeak__vrmq += '  return out'
    vqs__gskw = dict()
    exec(zfeak__vrmq, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': znui__efxt}, vqs__gskw)
    impl = vqs__gskw['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        bmgx__ppfv = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    hpae__wdbqg = dict(subset=subset, keep=keep, inplace=inplace)
    coxjz__zdc = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', hpae__wdbqg,
        coxjz__zdc, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        fqkv__isacw = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (fqkv__isacw,), wtva__ozt = bodo.libs.array_kernels.drop_duplicates((
            fqkv__isacw,), index, 1)
        index = bodo.utils.conversion.index_from_array(wtva__ozt)
        return bodo.hiframes.pd_series_ext.init_series(fqkv__isacw, index, name
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
    zotql__irxw = element_type(S.data)
    if not is_common_scalar_dtype([zotql__irxw, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([zotql__irxw, right]):
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
        bmgx__ppfv = np.empty(n, np.bool_)
        for vfqk__wgs in numba.parfors.parfor.internal_prange(n):
            lwb__ojix = bodo.utils.conversion.box_if_dt64(arr[vfqk__wgs])
            if inclusive == 'both':
                bmgx__ppfv[vfqk__wgs
                    ] = lwb__ojix <= right and lwb__ojix >= left
            else:
                bmgx__ppfv[vfqk__wgs] = lwb__ojix < right and lwb__ojix > left
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    hpae__wdbqg = dict(axis=axis)
    coxjz__zdc = dict(axis=None)
    check_unsupported_args('Series.repeat', hpae__wdbqg, coxjz__zdc,
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
            wtva__ozt = bodo.utils.conversion.index_to_array(index)
            bmgx__ppfv = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            ekxfz__pyp = bodo.libs.array_kernels.repeat_kernel(wtva__ozt,
                repeats)
            cas__bqf = bodo.utils.conversion.index_from_array(ekxfz__pyp)
            return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv,
                cas__bqf, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        wtva__ozt = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        bmgx__ppfv = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        ekxfz__pyp = bodo.libs.array_kernels.repeat_kernel(wtva__ozt, repeats)
        cas__bqf = bodo.utils.conversion.index_from_array(ekxfz__pyp)
        return bodo.hiframes.pd_series_ext.init_series(bmgx__ppfv, cas__bqf,
            name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        gzx__dietw = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(gzx__dietw)
        pta__hzeee = {}
        for vfqk__wgs in range(n):
            lwb__ojix = bodo.utils.conversion.box_if_dt64(gzx__dietw[vfqk__wgs]
                )
            pta__hzeee[index[vfqk__wgs]] = lwb__ojix
        return pta__hzeee
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    jvovp__zfuey = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            lcung__zsfjo = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(jvovp__zfuey)
    elif is_literal_type(name):
        lcung__zsfjo = get_literal_value(name)
    else:
        raise_bodo_error(jvovp__zfuey)
    lcung__zsfjo = 0 if lcung__zsfjo is None else lcung__zsfjo
    otm__zxv = ColNamesMetaType((lcung__zsfjo,))

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            otm__zxv)
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
