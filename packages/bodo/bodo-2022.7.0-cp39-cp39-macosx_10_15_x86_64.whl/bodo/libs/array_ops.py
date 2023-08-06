"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero, is_str_arr_type


def array_op_any(arr, skipna=True):
    pass


@overload(array_op_any)
def overload_array_op_any(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        kke__rhu = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        kke__rhu = False
    elif A == bodo.string_array_type:
        kke__rhu = ''
    elif A == bodo.binary_array_type:
        kke__rhu = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        xic__kdss = 0
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, zmc__iuh):
                if A[zmc__iuh] != kke__rhu:
                    xic__kdss += 1
        return xic__kdss != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        kke__rhu = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        kke__rhu = False
    elif A == bodo.string_array_type:
        kke__rhu = ''
    elif A == bodo.binary_array_type:
        kke__rhu = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        xic__kdss = 0
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, zmc__iuh):
                if A[zmc__iuh] == kke__rhu:
                    xic__kdss += 1
        return xic__kdss == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    ejlrt__yakh = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(ejlrt__yakh.ctypes,
        arr, parallel, skipna)
    return ejlrt__yakh[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        rim__reei = len(arr)
        npx__sqj = np.empty(rim__reei, np.bool_)
        for zmc__iuh in numba.parfors.parfor.internal_prange(rim__reei):
            npx__sqj[zmc__iuh] = bodo.libs.array_kernels.isna(arr, zmc__iuh)
        return npx__sqj
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xic__kdss = 0
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
            cfd__njufo = 0
            if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                cfd__njufo = 1
            xic__kdss += cfd__njufo
        ejlrt__yakh = xic__kdss
        return ejlrt__yakh
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    hxgsh__mqu = array_op_count(arr)
    pzll__ngsti = array_op_min(arr)
    cuuvh__uwp = array_op_max(arr)
    tou__cjqc = array_op_mean(arr)
    qodxm__pugk = array_op_std(arr)
    oiqhk__ycuom = array_op_quantile(arr, 0.25)
    knt__xdhk = array_op_quantile(arr, 0.5)
    tugdy__kwkba = array_op_quantile(arr, 0.75)
    return (hxgsh__mqu, tou__cjqc, qodxm__pugk, pzll__ngsti, oiqhk__ycuom,
        knt__xdhk, tugdy__kwkba, cuuvh__uwp)


def array_op_describe_dt_impl(arr):
    hxgsh__mqu = array_op_count(arr)
    pzll__ngsti = array_op_min(arr)
    cuuvh__uwp = array_op_max(arr)
    tou__cjqc = array_op_mean(arr)
    oiqhk__ycuom = array_op_quantile(arr, 0.25)
    knt__xdhk = array_op_quantile(arr, 0.5)
    tugdy__kwkba = array_op_quantile(arr, 0.75)
    return (hxgsh__mqu, tou__cjqc, pzll__ngsti, oiqhk__ycuom, knt__xdhk,
        tugdy__kwkba, cuuvh__uwp)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


@generated_jit(nopython=True)
def array_op_nbytes(arr):
    return array_op_nbytes_impl


def array_op_nbytes_impl(arr):
    return arr.nbytes


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = numba.cpython.builtins.get_type_max_value(np.int64)
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = xaa__bwwx
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[zmc__iuh]))
                    cfd__njufo = 1
                xaa__bwwx = min(xaa__bwwx, hsa__vlrwa)
                xic__kdss += cfd__njufo
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(xaa__bwwx,
                xic__kdss)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = numba.cpython.builtins.get_type_max_value(np.int64)
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = xaa__bwwx
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[zmc__iuh]))
                    cfd__njufo = 1
                xaa__bwwx = min(xaa__bwwx, hsa__vlrwa)
                xic__kdss += cfd__njufo
            return bodo.hiframes.pd_index_ext._dti_val_finalize(xaa__bwwx,
                xic__kdss)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            hts__rbarf = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            xaa__bwwx = numba.cpython.builtins.get_type_max_value(np.int64)
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(
                hts__rbarf)):
                ovvc__qcgaq = hts__rbarf[zmc__iuh]
                if ovvc__qcgaq == -1:
                    continue
                xaa__bwwx = min(xaa__bwwx, ovvc__qcgaq)
                xic__kdss += 1
            ejlrt__yakh = bodo.hiframes.series_kernels._box_cat_val(xaa__bwwx,
                arr.dtype, xic__kdss)
            return ejlrt__yakh
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = bodo.hiframes.series_kernels._get_date_max_value()
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = xaa__bwwx
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = arr[zmc__iuh]
                    cfd__njufo = 1
                xaa__bwwx = min(xaa__bwwx, hsa__vlrwa)
                xic__kdss += cfd__njufo
            ejlrt__yakh = bodo.hiframes.series_kernels._sum_handle_nan(
                xaa__bwwx, xic__kdss)
            return ejlrt__yakh
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xaa__bwwx = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        xic__kdss = 0
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
            hsa__vlrwa = xaa__bwwx
            cfd__njufo = 0
            if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                hsa__vlrwa = arr[zmc__iuh]
                cfd__njufo = 1
            xaa__bwwx = min(xaa__bwwx, hsa__vlrwa)
            xic__kdss += cfd__njufo
        ejlrt__yakh = bodo.hiframes.series_kernels._sum_handle_nan(xaa__bwwx,
            xic__kdss)
        return ejlrt__yakh
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = numba.cpython.builtins.get_type_min_value(np.int64)
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = xaa__bwwx
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[zmc__iuh]))
                    cfd__njufo = 1
                xaa__bwwx = max(xaa__bwwx, hsa__vlrwa)
                xic__kdss += cfd__njufo
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(xaa__bwwx,
                xic__kdss)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = numba.cpython.builtins.get_type_min_value(np.int64)
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = xaa__bwwx
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[zmc__iuh]))
                    cfd__njufo = 1
                xaa__bwwx = max(xaa__bwwx, hsa__vlrwa)
                xic__kdss += cfd__njufo
            return bodo.hiframes.pd_index_ext._dti_val_finalize(xaa__bwwx,
                xic__kdss)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            hts__rbarf = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            xaa__bwwx = -1
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(
                hts__rbarf)):
                xaa__bwwx = max(xaa__bwwx, hts__rbarf[zmc__iuh])
            ejlrt__yakh = bodo.hiframes.series_kernels._box_cat_val(xaa__bwwx,
                arr.dtype, 1)
            return ejlrt__yakh
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = bodo.hiframes.series_kernels._get_date_min_value()
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = xaa__bwwx
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = arr[zmc__iuh]
                    cfd__njufo = 1
                xaa__bwwx = max(xaa__bwwx, hsa__vlrwa)
                xic__kdss += cfd__njufo
            ejlrt__yakh = bodo.hiframes.series_kernels._sum_handle_nan(
                xaa__bwwx, xic__kdss)
            return ejlrt__yakh
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xaa__bwwx = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        xic__kdss = 0
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
            hsa__vlrwa = xaa__bwwx
            cfd__njufo = 0
            if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                hsa__vlrwa = arr[zmc__iuh]
                cfd__njufo = 1
            xaa__bwwx = max(xaa__bwwx, hsa__vlrwa)
            xic__kdss += cfd__njufo
        ejlrt__yakh = bodo.hiframes.series_kernels._sum_handle_nan(xaa__bwwx,
            xic__kdss)
        return ejlrt__yakh
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    sxfng__xhb = types.float64
    knq__ubrz = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        sxfng__xhb = types.float32
        knq__ubrz = types.float32
    ruav__dte = sxfng__xhb(0)
    yhzf__eeak = knq__ubrz(0)
    eiuc__tsqjw = knq__ubrz(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xaa__bwwx = ruav__dte
        xic__kdss = yhzf__eeak
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
            hsa__vlrwa = ruav__dte
            cfd__njufo = yhzf__eeak
            if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                hsa__vlrwa = arr[zmc__iuh]
                cfd__njufo = eiuc__tsqjw
            xaa__bwwx += hsa__vlrwa
            xic__kdss += cfd__njufo
        ejlrt__yakh = bodo.hiframes.series_kernels._mean_handle_nan(xaa__bwwx,
            xic__kdss)
        return ejlrt__yakh
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        gdq__kwa = 0.0
        rsxv__ktb = 0.0
        xic__kdss = 0
        for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
            hsa__vlrwa = 0.0
            cfd__njufo = 0
            if not bodo.libs.array_kernels.isna(arr, zmc__iuh) or not skipna:
                hsa__vlrwa = arr[zmc__iuh]
                cfd__njufo = 1
            gdq__kwa += hsa__vlrwa
            rsxv__ktb += hsa__vlrwa * hsa__vlrwa
            xic__kdss += cfd__njufo
        ejlrt__yakh = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            gdq__kwa, rsxv__ktb, xic__kdss, ddof)
        return ejlrt__yakh
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                npx__sqj = np.empty(len(q), np.int64)
                for zmc__iuh in range(len(q)):
                    pcvdi__gtyqz = np.float64(q[zmc__iuh])
                    npx__sqj[zmc__iuh] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), pcvdi__gtyqz)
                return npx__sqj.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            npx__sqj = np.empty(len(q), np.float64)
            for zmc__iuh in range(len(q)):
                pcvdi__gtyqz = np.float64(q[zmc__iuh])
                npx__sqj[zmc__iuh] = bodo.libs.array_kernels.quantile(arr,
                    pcvdi__gtyqz)
            return npx__sqj
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        bxqf__fial = types.intp
    elif arr.dtype == types.bool_:
        bxqf__fial = np.int64
    else:
        bxqf__fial = arr.dtype
    hwbxl__szty = bxqf__fial(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = hwbxl__szty
            rim__reei = len(arr)
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(rim__reei):
                hsa__vlrwa = hwbxl__szty
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh
                    ) or not skipna:
                    hsa__vlrwa = arr[zmc__iuh]
                    cfd__njufo = 1
                xaa__bwwx += hsa__vlrwa
                xic__kdss += cfd__njufo
            ejlrt__yakh = bodo.hiframes.series_kernels._var_handle_mincount(
                xaa__bwwx, xic__kdss, min_count)
            return ejlrt__yakh
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = hwbxl__szty
            rim__reei = len(arr)
            for zmc__iuh in numba.parfors.parfor.internal_prange(rim__reei):
                hsa__vlrwa = hwbxl__szty
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = arr[zmc__iuh]
                xaa__bwwx += hsa__vlrwa
            return xaa__bwwx
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    nfk__ldw = arr.dtype(1)
    if arr.dtype == types.bool_:
        nfk__ldw = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = nfk__ldw
            xic__kdss = 0
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = nfk__ldw
                cfd__njufo = 0
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh
                    ) or not skipna:
                    hsa__vlrwa = arr[zmc__iuh]
                    cfd__njufo = 1
                xic__kdss += cfd__njufo
                xaa__bwwx *= hsa__vlrwa
            ejlrt__yakh = bodo.hiframes.series_kernels._var_handle_mincount(
                xaa__bwwx, xic__kdss, min_count)
            return ejlrt__yakh
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xaa__bwwx = nfk__ldw
            for zmc__iuh in numba.parfors.parfor.internal_prange(len(arr)):
                hsa__vlrwa = nfk__ldw
                if not bodo.libs.array_kernels.isna(arr, zmc__iuh):
                    hsa__vlrwa = arr[zmc__iuh]
                xaa__bwwx *= hsa__vlrwa
            return xaa__bwwx
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        zmc__iuh = bodo.libs.array_kernels._nan_argmax(arr)
        return index[zmc__iuh]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        zmc__iuh = bodo.libs.array_kernels._nan_argmin(arr)
        return index[zmc__iuh]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            rnt__aej = {}
            for ybkws__wbtg in values:
                rnt__aej[bodo.utils.conversion.box_if_dt64(ybkws__wbtg)] = 0
            return rnt__aej
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        rim__reei = len(arr)
        npx__sqj = np.empty(rim__reei, np.bool_)
        for zmc__iuh in numba.parfors.parfor.internal_prange(rim__reei):
            npx__sqj[zmc__iuh] = bodo.utils.conversion.box_if_dt64(arr[
                zmc__iuh]) in values
        return npx__sqj
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    vow__vufu = len(in_arr_tup) != 1
    fyldk__ljqhi = list(in_arr_tup.types)
    qoh__gvfqv = 'def impl(in_arr_tup):\n'
    qoh__gvfqv += '  n = len(in_arr_tup[0])\n'
    if vow__vufu:
        mwqo__plwmg = ', '.join([f'in_arr_tup[{zmc__iuh}][unused]' for
            zmc__iuh in range(len(in_arr_tup))])
        tjtd__gjykz = ', '.join(['False' for nrsh__uggh in range(len(
            in_arr_tup))])
        qoh__gvfqv += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({mwqo__plwmg},), ({tjtd__gjykz},)): 0 for unused in range(0)}}
"""
        qoh__gvfqv += '  map_vector = np.empty(n, np.int64)\n'
        for zmc__iuh, kshkh__tdxu in enumerate(fyldk__ljqhi):
            qoh__gvfqv += f'  in_lst_{zmc__iuh} = []\n'
            if is_str_arr_type(kshkh__tdxu):
                qoh__gvfqv += f'  total_len_{zmc__iuh} = 0\n'
            qoh__gvfqv += f'  null_in_lst_{zmc__iuh} = []\n'
        qoh__gvfqv += '  for i in range(n):\n'
        jugx__vvogf = ', '.join([f'in_arr_tup[{zmc__iuh}][i]' for zmc__iuh in
            range(len(fyldk__ljqhi))])
        ybv__pox = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{zmc__iuh}], i)' for
            zmc__iuh in range(len(fyldk__ljqhi))])
        qoh__gvfqv += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({jugx__vvogf},), ({ybv__pox},))
"""
        qoh__gvfqv += '    if data_val not in arr_map:\n'
        qoh__gvfqv += '      set_val = len(arr_map)\n'
        qoh__gvfqv += '      values_tup = data_val._data\n'
        qoh__gvfqv += '      nulls_tup = data_val._null_values\n'
        for zmc__iuh, kshkh__tdxu in enumerate(fyldk__ljqhi):
            qoh__gvfqv += (
                f'      in_lst_{zmc__iuh}.append(values_tup[{zmc__iuh}])\n')
            qoh__gvfqv += (
                f'      null_in_lst_{zmc__iuh}.append(nulls_tup[{zmc__iuh}])\n'
                )
            if is_str_arr_type(kshkh__tdxu):
                qoh__gvfqv += f"""      total_len_{zmc__iuh}  += nulls_tup[{zmc__iuh}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{zmc__iuh}], i)
"""
        qoh__gvfqv += '      arr_map[data_val] = len(arr_map)\n'
        qoh__gvfqv += '    else:\n'
        qoh__gvfqv += '      set_val = arr_map[data_val]\n'
        qoh__gvfqv += '    map_vector[i] = set_val\n'
        qoh__gvfqv += '  n_rows = len(arr_map)\n'
        for zmc__iuh, kshkh__tdxu in enumerate(fyldk__ljqhi):
            if is_str_arr_type(kshkh__tdxu):
                qoh__gvfqv += f"""  out_arr_{zmc__iuh} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{zmc__iuh})
"""
            else:
                qoh__gvfqv += f"""  out_arr_{zmc__iuh} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{zmc__iuh}], (-1,))
"""
        qoh__gvfqv += '  for j in range(len(arr_map)):\n'
        for zmc__iuh in range(len(fyldk__ljqhi)):
            qoh__gvfqv += f'    if null_in_lst_{zmc__iuh}[j]:\n'
            qoh__gvfqv += (
                f'      bodo.libs.array_kernels.setna(out_arr_{zmc__iuh}, j)\n'
                )
            qoh__gvfqv += '    else:\n'
            qoh__gvfqv += (
                f'      out_arr_{zmc__iuh}[j] = in_lst_{zmc__iuh}[j]\n')
        rza__ypdct = ', '.join([f'out_arr_{zmc__iuh}' for zmc__iuh in range
            (len(fyldk__ljqhi))])
        qoh__gvfqv += f'  return ({rza__ypdct},), map_vector\n'
    else:
        qoh__gvfqv += '  in_arr = in_arr_tup[0]\n'
        qoh__gvfqv += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        qoh__gvfqv += '  map_vector = np.empty(n, np.int64)\n'
        qoh__gvfqv += '  is_na = 0\n'
        qoh__gvfqv += '  in_lst = []\n'
        qoh__gvfqv += '  na_idxs = []\n'
        if is_str_arr_type(fyldk__ljqhi[0]):
            qoh__gvfqv += '  total_len = 0\n'
        qoh__gvfqv += '  for i in range(n):\n'
        qoh__gvfqv += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        qoh__gvfqv += '      is_na = 1\n'
        qoh__gvfqv += '      # Always put NA in the last location.\n'
        qoh__gvfqv += '      # We use -1 as a placeholder\n'
        qoh__gvfqv += '      set_val = -1\n'
        qoh__gvfqv += '      na_idxs.append(i)\n'
        qoh__gvfqv += '    else:\n'
        qoh__gvfqv += '      data_val = in_arr[i]\n'
        qoh__gvfqv += '      if data_val not in arr_map:\n'
        qoh__gvfqv += '        set_val = len(arr_map)\n'
        qoh__gvfqv += '        in_lst.append(data_val)\n'
        if is_str_arr_type(fyldk__ljqhi[0]):
            qoh__gvfqv += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        qoh__gvfqv += '        arr_map[data_val] = len(arr_map)\n'
        qoh__gvfqv += '      else:\n'
        qoh__gvfqv += '        set_val = arr_map[data_val]\n'
        qoh__gvfqv += '    map_vector[i] = set_val\n'
        qoh__gvfqv += '  map_vector[na_idxs] = len(arr_map)\n'
        qoh__gvfqv += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(fyldk__ljqhi[0]):
            qoh__gvfqv += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            qoh__gvfqv += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        qoh__gvfqv += '  for j in range(len(arr_map)):\n'
        qoh__gvfqv += '    out_arr[j] = in_lst[j]\n'
        qoh__gvfqv += '  if is_na:\n'
        qoh__gvfqv += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        qoh__gvfqv += f'  return (out_arr,), map_vector\n'
    dbc__esm = {}
    exec(qoh__gvfqv, {'bodo': bodo, 'np': np}, dbc__esm)
    impl = dbc__esm['impl']
    return impl
