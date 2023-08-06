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
        ngf__ryrv = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        ngf__ryrv = False
    elif A == bodo.string_array_type:
        ngf__ryrv = ''
    elif A == bodo.binary_array_type:
        ngf__ryrv = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        faj__afcq = 0
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, wfmw__iftlp):
                if A[wfmw__iftlp] != ngf__ryrv:
                    faj__afcq += 1
        return faj__afcq != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        ngf__ryrv = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        ngf__ryrv = False
    elif A == bodo.string_array_type:
        ngf__ryrv = ''
    elif A == bodo.binary_array_type:
        ngf__ryrv = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        faj__afcq = 0
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, wfmw__iftlp):
                if A[wfmw__iftlp] == ngf__ryrv:
                    faj__afcq += 1
        return faj__afcq == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    wbodg__hexs = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(wbodg__hexs.ctypes,
        arr, parallel, skipna)
    return wbodg__hexs[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ouyyg__zbvb = len(arr)
        dgcl__afjjb = np.empty(ouyyg__zbvb, np.bool_)
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(ouyyg__zbvb):
            dgcl__afjjb[wfmw__iftlp] = bodo.libs.array_kernels.isna(arr,
                wfmw__iftlp)
        return dgcl__afjjb
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        faj__afcq = 0
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
            qsuzo__ttgt = 0
            if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                qsuzo__ttgt = 1
            faj__afcq += qsuzo__ttgt
        wbodg__hexs = faj__afcq
        return wbodg__hexs
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    bcz__gqu = array_op_count(arr)
    hhur__xsr = array_op_min(arr)
    bntwu__ddcx = array_op_max(arr)
    tyc__hywfe = array_op_mean(arr)
    qhu__npub = array_op_std(arr)
    uczh__degir = array_op_quantile(arr, 0.25)
    ois__mzb = array_op_quantile(arr, 0.5)
    odnu__ikn = array_op_quantile(arr, 0.75)
    return (bcz__gqu, tyc__hywfe, qhu__npub, hhur__xsr, uczh__degir,
        ois__mzb, odnu__ikn, bntwu__ddcx)


def array_op_describe_dt_impl(arr):
    bcz__gqu = array_op_count(arr)
    hhur__xsr = array_op_min(arr)
    bntwu__ddcx = array_op_max(arr)
    tyc__hywfe = array_op_mean(arr)
    uczh__degir = array_op_quantile(arr, 0.25)
    ois__mzb = array_op_quantile(arr, 0.5)
    odnu__ikn = array_op_quantile(arr, 0.75)
    return (bcz__gqu, tyc__hywfe, hhur__xsr, uczh__degir, ois__mzb,
        odnu__ikn, bntwu__ddcx)


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
            jqfh__rijxy = numba.cpython.builtins.get_type_max_value(np.int64)
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = jqfh__rijxy
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[wfmw__iftlp]))
                    qsuzo__ttgt = 1
                jqfh__rijxy = min(jqfh__rijxy, nsckc__kmj)
                faj__afcq += qsuzo__ttgt
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(jqfh__rijxy,
                faj__afcq)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = numba.cpython.builtins.get_type_max_value(np.int64)
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = jqfh__rijxy
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[wfmw__iftlp]))
                    qsuzo__ttgt = 1
                jqfh__rijxy = min(jqfh__rijxy, nsckc__kmj)
                faj__afcq += qsuzo__ttgt
            return bodo.hiframes.pd_index_ext._dti_val_finalize(jqfh__rijxy,
                faj__afcq)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            rnkci__uyvmg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = numba.cpython.builtins.get_type_max_value(np.int64)
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(
                rnkci__uyvmg)):
                bkpn__vmf = rnkci__uyvmg[wfmw__iftlp]
                if bkpn__vmf == -1:
                    continue
                jqfh__rijxy = min(jqfh__rijxy, bkpn__vmf)
                faj__afcq += 1
            wbodg__hexs = bodo.hiframes.series_kernels._box_cat_val(jqfh__rijxy
                , arr.dtype, faj__afcq)
            return wbodg__hexs
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = bodo.hiframes.series_kernels._get_date_max_value()
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = jqfh__rijxy
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = arr[wfmw__iftlp]
                    qsuzo__ttgt = 1
                jqfh__rijxy = min(jqfh__rijxy, nsckc__kmj)
                faj__afcq += qsuzo__ttgt
            wbodg__hexs = bodo.hiframes.series_kernels._sum_handle_nan(
                jqfh__rijxy, faj__afcq)
            return wbodg__hexs
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jqfh__rijxy = bodo.hiframes.series_kernels._get_type_max_value(arr.
            dtype)
        faj__afcq = 0
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
            nsckc__kmj = jqfh__rijxy
            qsuzo__ttgt = 0
            if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                nsckc__kmj = arr[wfmw__iftlp]
                qsuzo__ttgt = 1
            jqfh__rijxy = min(jqfh__rijxy, nsckc__kmj)
            faj__afcq += qsuzo__ttgt
        wbodg__hexs = bodo.hiframes.series_kernels._sum_handle_nan(jqfh__rijxy,
            faj__afcq)
        return wbodg__hexs
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = numba.cpython.builtins.get_type_min_value(np.int64)
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = jqfh__rijxy
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[wfmw__iftlp]))
                    qsuzo__ttgt = 1
                jqfh__rijxy = max(jqfh__rijxy, nsckc__kmj)
                faj__afcq += qsuzo__ttgt
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(jqfh__rijxy,
                faj__afcq)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = numba.cpython.builtins.get_type_min_value(np.int64)
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = jqfh__rijxy
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[wfmw__iftlp]))
                    qsuzo__ttgt = 1
                jqfh__rijxy = max(jqfh__rijxy, nsckc__kmj)
                faj__afcq += qsuzo__ttgt
            return bodo.hiframes.pd_index_ext._dti_val_finalize(jqfh__rijxy,
                faj__afcq)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            rnkci__uyvmg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = -1
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(
                rnkci__uyvmg)):
                jqfh__rijxy = max(jqfh__rijxy, rnkci__uyvmg[wfmw__iftlp])
            wbodg__hexs = bodo.hiframes.series_kernels._box_cat_val(jqfh__rijxy
                , arr.dtype, 1)
            return wbodg__hexs
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = bodo.hiframes.series_kernels._get_date_min_value()
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = jqfh__rijxy
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = arr[wfmw__iftlp]
                    qsuzo__ttgt = 1
                jqfh__rijxy = max(jqfh__rijxy, nsckc__kmj)
                faj__afcq += qsuzo__ttgt
            wbodg__hexs = bodo.hiframes.series_kernels._sum_handle_nan(
                jqfh__rijxy, faj__afcq)
            return wbodg__hexs
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jqfh__rijxy = bodo.hiframes.series_kernels._get_type_min_value(arr.
            dtype)
        faj__afcq = 0
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
            nsckc__kmj = jqfh__rijxy
            qsuzo__ttgt = 0
            if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                nsckc__kmj = arr[wfmw__iftlp]
                qsuzo__ttgt = 1
            jqfh__rijxy = max(jqfh__rijxy, nsckc__kmj)
            faj__afcq += qsuzo__ttgt
        wbodg__hexs = bodo.hiframes.series_kernels._sum_handle_nan(jqfh__rijxy,
            faj__afcq)
        return wbodg__hexs
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
    nzpa__eejr = types.float64
    lgao__qnvh = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        nzpa__eejr = types.float32
        lgao__qnvh = types.float32
    gtp__wet = nzpa__eejr(0)
    vck__afwlk = lgao__qnvh(0)
    pbuov__nyfmr = lgao__qnvh(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        jqfh__rijxy = gtp__wet
        faj__afcq = vck__afwlk
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
            nsckc__kmj = gtp__wet
            qsuzo__ttgt = vck__afwlk
            if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                nsckc__kmj = arr[wfmw__iftlp]
                qsuzo__ttgt = pbuov__nyfmr
            jqfh__rijxy += nsckc__kmj
            faj__afcq += qsuzo__ttgt
        wbodg__hexs = bodo.hiframes.series_kernels._mean_handle_nan(jqfh__rijxy
            , faj__afcq)
        return wbodg__hexs
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        ofak__azfgg = 0.0
        jhkk__lrc = 0.0
        faj__afcq = 0
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
            nsckc__kmj = 0.0
            qsuzo__ttgt = 0
            if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp
                ) or not skipna:
                nsckc__kmj = arr[wfmw__iftlp]
                qsuzo__ttgt = 1
            ofak__azfgg += nsckc__kmj
            jhkk__lrc += nsckc__kmj * nsckc__kmj
            faj__afcq += qsuzo__ttgt
        wbodg__hexs = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            ofak__azfgg, jhkk__lrc, faj__afcq, ddof)
        return wbodg__hexs
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
                dgcl__afjjb = np.empty(len(q), np.int64)
                for wfmw__iftlp in range(len(q)):
                    ssfn__abw = np.float64(q[wfmw__iftlp])
                    dgcl__afjjb[wfmw__iftlp
                        ] = bodo.libs.array_kernels.quantile(arr.view(np.
                        int64), ssfn__abw)
                return dgcl__afjjb.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            dgcl__afjjb = np.empty(len(q), np.float64)
            for wfmw__iftlp in range(len(q)):
                ssfn__abw = np.float64(q[wfmw__iftlp])
                dgcl__afjjb[wfmw__iftlp] = bodo.libs.array_kernels.quantile(arr
                    , ssfn__abw)
            return dgcl__afjjb
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
        xauyj__pgfp = types.intp
    elif arr.dtype == types.bool_:
        xauyj__pgfp = np.int64
    else:
        xauyj__pgfp = arr.dtype
    xorzr__vqb = xauyj__pgfp(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = xorzr__vqb
            ouyyg__zbvb = len(arr)
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(ouyyg__zbvb
                ):
                nsckc__kmj = xorzr__vqb
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp
                    ) or not skipna:
                    nsckc__kmj = arr[wfmw__iftlp]
                    qsuzo__ttgt = 1
                jqfh__rijxy += nsckc__kmj
                faj__afcq += qsuzo__ttgt
            wbodg__hexs = bodo.hiframes.series_kernels._var_handle_mincount(
                jqfh__rijxy, faj__afcq, min_count)
            return wbodg__hexs
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = xorzr__vqb
            ouyyg__zbvb = len(arr)
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(ouyyg__zbvb
                ):
                nsckc__kmj = xorzr__vqb
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = arr[wfmw__iftlp]
                jqfh__rijxy += nsckc__kmj
            return jqfh__rijxy
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    mavrm__ydo = arr.dtype(1)
    if arr.dtype == types.bool_:
        mavrm__ydo = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = mavrm__ydo
            faj__afcq = 0
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = mavrm__ydo
                qsuzo__ttgt = 0
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp
                    ) or not skipna:
                    nsckc__kmj = arr[wfmw__iftlp]
                    qsuzo__ttgt = 1
                faj__afcq += qsuzo__ttgt
                jqfh__rijxy *= nsckc__kmj
            wbodg__hexs = bodo.hiframes.series_kernels._var_handle_mincount(
                jqfh__rijxy, faj__afcq, min_count)
            return wbodg__hexs
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            jqfh__rijxy = mavrm__ydo
            for wfmw__iftlp in numba.parfors.parfor.internal_prange(len(arr)):
                nsckc__kmj = mavrm__ydo
                if not bodo.libs.array_kernels.isna(arr, wfmw__iftlp):
                    nsckc__kmj = arr[wfmw__iftlp]
                jqfh__rijxy *= nsckc__kmj
            return jqfh__rijxy
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        wfmw__iftlp = bodo.libs.array_kernels._nan_argmax(arr)
        return index[wfmw__iftlp]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        wfmw__iftlp = bodo.libs.array_kernels._nan_argmin(arr)
        return index[wfmw__iftlp]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            uwega__rpcj = {}
            for ygns__rqw in values:
                uwega__rpcj[bodo.utils.conversion.box_if_dt64(ygns__rqw)] = 0
            return uwega__rpcj
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
        ouyyg__zbvb = len(arr)
        dgcl__afjjb = np.empty(ouyyg__zbvb, np.bool_)
        for wfmw__iftlp in numba.parfors.parfor.internal_prange(ouyyg__zbvb):
            dgcl__afjjb[wfmw__iftlp] = bodo.utils.conversion.box_if_dt64(arr
                [wfmw__iftlp]) in values
        return dgcl__afjjb
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    djuw__dwk = len(in_arr_tup) != 1
    ofu__repi = list(in_arr_tup.types)
    yey__eoh = 'def impl(in_arr_tup):\n'
    yey__eoh += '  n = len(in_arr_tup[0])\n'
    if djuw__dwk:
        hegm__jnanz = ', '.join([f'in_arr_tup[{wfmw__iftlp}][unused]' for
            wfmw__iftlp in range(len(in_arr_tup))])
        nbbf__uhke = ', '.join(['False' for etufs__xbas in range(len(
            in_arr_tup))])
        yey__eoh += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({hegm__jnanz},), ({nbbf__uhke},)): 0 for unused in range(0)}}
"""
        yey__eoh += '  map_vector = np.empty(n, np.int64)\n'
        for wfmw__iftlp, uof__alc in enumerate(ofu__repi):
            yey__eoh += f'  in_lst_{wfmw__iftlp} = []\n'
            if is_str_arr_type(uof__alc):
                yey__eoh += f'  total_len_{wfmw__iftlp} = 0\n'
            yey__eoh += f'  null_in_lst_{wfmw__iftlp} = []\n'
        yey__eoh += '  for i in range(n):\n'
        acz__nswr = ', '.join([f'in_arr_tup[{wfmw__iftlp}][i]' for
            wfmw__iftlp in range(len(ofu__repi))])
        txj__vtxim = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{wfmw__iftlp}], i)' for
            wfmw__iftlp in range(len(ofu__repi))])
        yey__eoh += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({acz__nswr},), ({txj__vtxim},))
"""
        yey__eoh += '    if data_val not in arr_map:\n'
        yey__eoh += '      set_val = len(arr_map)\n'
        yey__eoh += '      values_tup = data_val._data\n'
        yey__eoh += '      nulls_tup = data_val._null_values\n'
        for wfmw__iftlp, uof__alc in enumerate(ofu__repi):
            yey__eoh += (
                f'      in_lst_{wfmw__iftlp}.append(values_tup[{wfmw__iftlp}])\n'
                )
            yey__eoh += (
                f'      null_in_lst_{wfmw__iftlp}.append(nulls_tup[{wfmw__iftlp}])\n'
                )
            if is_str_arr_type(uof__alc):
                yey__eoh += f"""      total_len_{wfmw__iftlp}  += nulls_tup[{wfmw__iftlp}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{wfmw__iftlp}], i)
"""
        yey__eoh += '      arr_map[data_val] = len(arr_map)\n'
        yey__eoh += '    else:\n'
        yey__eoh += '      set_val = arr_map[data_val]\n'
        yey__eoh += '    map_vector[i] = set_val\n'
        yey__eoh += '  n_rows = len(arr_map)\n'
        for wfmw__iftlp, uof__alc in enumerate(ofu__repi):
            if is_str_arr_type(uof__alc):
                yey__eoh += f"""  out_arr_{wfmw__iftlp} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{wfmw__iftlp})
"""
            else:
                yey__eoh += f"""  out_arr_{wfmw__iftlp} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{wfmw__iftlp}], (-1,))
"""
        yey__eoh += '  for j in range(len(arr_map)):\n'
        for wfmw__iftlp in range(len(ofu__repi)):
            yey__eoh += f'    if null_in_lst_{wfmw__iftlp}[j]:\n'
            yey__eoh += (
                f'      bodo.libs.array_kernels.setna(out_arr_{wfmw__iftlp}, j)\n'
                )
            yey__eoh += '    else:\n'
            yey__eoh += (
                f'      out_arr_{wfmw__iftlp}[j] = in_lst_{wfmw__iftlp}[j]\n')
        kopfv__haj = ', '.join([f'out_arr_{wfmw__iftlp}' for wfmw__iftlp in
            range(len(ofu__repi))])
        yey__eoh += f'  return ({kopfv__haj},), map_vector\n'
    else:
        yey__eoh += '  in_arr = in_arr_tup[0]\n'
        yey__eoh += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        yey__eoh += '  map_vector = np.empty(n, np.int64)\n'
        yey__eoh += '  is_na = 0\n'
        yey__eoh += '  in_lst = []\n'
        yey__eoh += '  na_idxs = []\n'
        if is_str_arr_type(ofu__repi[0]):
            yey__eoh += '  total_len = 0\n'
        yey__eoh += '  for i in range(n):\n'
        yey__eoh += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        yey__eoh += '      is_na = 1\n'
        yey__eoh += '      # Always put NA in the last location.\n'
        yey__eoh += '      # We use -1 as a placeholder\n'
        yey__eoh += '      set_val = -1\n'
        yey__eoh += '      na_idxs.append(i)\n'
        yey__eoh += '    else:\n'
        yey__eoh += '      data_val = in_arr[i]\n'
        yey__eoh += '      if data_val not in arr_map:\n'
        yey__eoh += '        set_val = len(arr_map)\n'
        yey__eoh += '        in_lst.append(data_val)\n'
        if is_str_arr_type(ofu__repi[0]):
            yey__eoh += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        yey__eoh += '        arr_map[data_val] = len(arr_map)\n'
        yey__eoh += '      else:\n'
        yey__eoh += '        set_val = arr_map[data_val]\n'
        yey__eoh += '    map_vector[i] = set_val\n'
        yey__eoh += '  map_vector[na_idxs] = len(arr_map)\n'
        yey__eoh += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(ofu__repi[0]):
            yey__eoh += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            yey__eoh += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        yey__eoh += '  for j in range(len(arr_map)):\n'
        yey__eoh += '    out_arr[j] = in_lst[j]\n'
        yey__eoh += '  if is_na:\n'
        yey__eoh += '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n'
        yey__eoh += f'  return (out_arr,), map_vector\n'
    doeby__sctx = {}
    exec(yey__eoh, {'bodo': bodo, 'np': np}, doeby__sctx)
    impl = doeby__sctx['impl']
    return impl
