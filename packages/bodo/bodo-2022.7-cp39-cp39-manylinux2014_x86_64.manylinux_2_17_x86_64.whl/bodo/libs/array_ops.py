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
        clx__bpq = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        clx__bpq = False
    elif A == bodo.string_array_type:
        clx__bpq = ''
    elif A == bodo.binary_array_type:
        clx__bpq = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        sbk__mwdh = 0
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, oeww__rcr):
                if A[oeww__rcr] != clx__bpq:
                    sbk__mwdh += 1
        return sbk__mwdh != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        clx__bpq = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        clx__bpq = False
    elif A == bodo.string_array_type:
        clx__bpq = ''
    elif A == bodo.binary_array_type:
        clx__bpq = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        sbk__mwdh = 0
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, oeww__rcr):
                if A[oeww__rcr] == clx__bpq:
                    sbk__mwdh += 1
        return sbk__mwdh == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    gwhb__vxmth = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(gwhb__vxmth.ctypes,
        arr, parallel, skipna)
    return gwhb__vxmth[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        wplsh__jdaha = len(arr)
        apsm__rmu = np.empty(wplsh__jdaha, np.bool_)
        for oeww__rcr in numba.parfors.parfor.internal_prange(wplsh__jdaha):
            apsm__rmu[oeww__rcr] = bodo.libs.array_kernels.isna(arr, oeww__rcr)
        return apsm__rmu
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        sbk__mwdh = 0
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
            vxox__ihi = 0
            if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                vxox__ihi = 1
            sbk__mwdh += vxox__ihi
        gwhb__vxmth = sbk__mwdh
        return gwhb__vxmth
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    bay__kuvdj = array_op_count(arr)
    sqpnk__lyqgm = array_op_min(arr)
    rul__yin = array_op_max(arr)
    obnvx__khip = array_op_mean(arr)
    cogvq__tmeb = array_op_std(arr)
    kufi__iyrg = array_op_quantile(arr, 0.25)
    pqhg__qwkkr = array_op_quantile(arr, 0.5)
    amud__icae = array_op_quantile(arr, 0.75)
    return (bay__kuvdj, obnvx__khip, cogvq__tmeb, sqpnk__lyqgm, kufi__iyrg,
        pqhg__qwkkr, amud__icae, rul__yin)


def array_op_describe_dt_impl(arr):
    bay__kuvdj = array_op_count(arr)
    sqpnk__lyqgm = array_op_min(arr)
    rul__yin = array_op_max(arr)
    obnvx__khip = array_op_mean(arr)
    kufi__iyrg = array_op_quantile(arr, 0.25)
    pqhg__qwkkr = array_op_quantile(arr, 0.5)
    amud__icae = array_op_quantile(arr, 0.75)
    return (bay__kuvdj, obnvx__khip, sqpnk__lyqgm, kufi__iyrg, pqhg__qwkkr,
        amud__icae, rul__yin)


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
            drf__rbwlf = numba.cpython.builtins.get_type_max_value(np.int64)
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = drf__rbwlf
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[oeww__rcr]))
                    vxox__ihi = 1
                drf__rbwlf = min(drf__rbwlf, trw__duta)
                sbk__mwdh += vxox__ihi
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(drf__rbwlf,
                sbk__mwdh)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = numba.cpython.builtins.get_type_max_value(np.int64)
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = drf__rbwlf
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[oeww__rcr])
                    vxox__ihi = 1
                drf__rbwlf = min(drf__rbwlf, trw__duta)
                sbk__mwdh += vxox__ihi
            return bodo.hiframes.pd_index_ext._dti_val_finalize(drf__rbwlf,
                sbk__mwdh)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            fbti__gtevt = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            drf__rbwlf = numba.cpython.builtins.get_type_max_value(np.int64)
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(
                fbti__gtevt)):
                xmyt__rdcsg = fbti__gtevt[oeww__rcr]
                if xmyt__rdcsg == -1:
                    continue
                drf__rbwlf = min(drf__rbwlf, xmyt__rdcsg)
                sbk__mwdh += 1
            gwhb__vxmth = bodo.hiframes.series_kernels._box_cat_val(drf__rbwlf,
                arr.dtype, sbk__mwdh)
            return gwhb__vxmth
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = bodo.hiframes.series_kernels._get_date_max_value()
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = drf__rbwlf
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = arr[oeww__rcr]
                    vxox__ihi = 1
                drf__rbwlf = min(drf__rbwlf, trw__duta)
                sbk__mwdh += vxox__ihi
            gwhb__vxmth = bodo.hiframes.series_kernels._sum_handle_nan(
                drf__rbwlf, sbk__mwdh)
            return gwhb__vxmth
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        drf__rbwlf = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype
            )
        sbk__mwdh = 0
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
            trw__duta = drf__rbwlf
            vxox__ihi = 0
            if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                trw__duta = arr[oeww__rcr]
                vxox__ihi = 1
            drf__rbwlf = min(drf__rbwlf, trw__duta)
            sbk__mwdh += vxox__ihi
        gwhb__vxmth = bodo.hiframes.series_kernels._sum_handle_nan(drf__rbwlf,
            sbk__mwdh)
        return gwhb__vxmth
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = numba.cpython.builtins.get_type_min_value(np.int64)
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = drf__rbwlf
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[oeww__rcr]))
                    vxox__ihi = 1
                drf__rbwlf = max(drf__rbwlf, trw__duta)
                sbk__mwdh += vxox__ihi
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(drf__rbwlf,
                sbk__mwdh)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = numba.cpython.builtins.get_type_min_value(np.int64)
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = drf__rbwlf
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[oeww__rcr])
                    vxox__ihi = 1
                drf__rbwlf = max(drf__rbwlf, trw__duta)
                sbk__mwdh += vxox__ihi
            return bodo.hiframes.pd_index_ext._dti_val_finalize(drf__rbwlf,
                sbk__mwdh)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            fbti__gtevt = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            drf__rbwlf = -1
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(
                fbti__gtevt)):
                drf__rbwlf = max(drf__rbwlf, fbti__gtevt[oeww__rcr])
            gwhb__vxmth = bodo.hiframes.series_kernels._box_cat_val(drf__rbwlf,
                arr.dtype, 1)
            return gwhb__vxmth
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = bodo.hiframes.series_kernels._get_date_min_value()
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = drf__rbwlf
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = arr[oeww__rcr]
                    vxox__ihi = 1
                drf__rbwlf = max(drf__rbwlf, trw__duta)
                sbk__mwdh += vxox__ihi
            gwhb__vxmth = bodo.hiframes.series_kernels._sum_handle_nan(
                drf__rbwlf, sbk__mwdh)
            return gwhb__vxmth
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        drf__rbwlf = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype
            )
        sbk__mwdh = 0
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
            trw__duta = drf__rbwlf
            vxox__ihi = 0
            if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                trw__duta = arr[oeww__rcr]
                vxox__ihi = 1
            drf__rbwlf = max(drf__rbwlf, trw__duta)
            sbk__mwdh += vxox__ihi
        gwhb__vxmth = bodo.hiframes.series_kernels._sum_handle_nan(drf__rbwlf,
            sbk__mwdh)
        return gwhb__vxmth
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
    wcwq__fqpo = types.float64
    rkza__fyln = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        wcwq__fqpo = types.float32
        rkza__fyln = types.float32
    xdynf__zxv = wcwq__fqpo(0)
    zwb__mzdng = rkza__fyln(0)
    pyap__mrqvk = rkza__fyln(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        drf__rbwlf = xdynf__zxv
        sbk__mwdh = zwb__mzdng
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
            trw__duta = xdynf__zxv
            vxox__ihi = zwb__mzdng
            if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                trw__duta = arr[oeww__rcr]
                vxox__ihi = pyap__mrqvk
            drf__rbwlf += trw__duta
            sbk__mwdh += vxox__ihi
        gwhb__vxmth = bodo.hiframes.series_kernels._mean_handle_nan(drf__rbwlf,
            sbk__mwdh)
        return gwhb__vxmth
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        rtbn__ubhs = 0.0
        nqij__iwhb = 0.0
        sbk__mwdh = 0
        for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
            trw__duta = 0.0
            vxox__ihi = 0
            if not bodo.libs.array_kernels.isna(arr, oeww__rcr) or not skipna:
                trw__duta = arr[oeww__rcr]
                vxox__ihi = 1
            rtbn__ubhs += trw__duta
            nqij__iwhb += trw__duta * trw__duta
            sbk__mwdh += vxox__ihi
        gwhb__vxmth = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            rtbn__ubhs, nqij__iwhb, sbk__mwdh, ddof)
        return gwhb__vxmth
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
                apsm__rmu = np.empty(len(q), np.int64)
                for oeww__rcr in range(len(q)):
                    pic__ris = np.float64(q[oeww__rcr])
                    apsm__rmu[oeww__rcr] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), pic__ris)
                return apsm__rmu.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            apsm__rmu = np.empty(len(q), np.float64)
            for oeww__rcr in range(len(q)):
                pic__ris = np.float64(q[oeww__rcr])
                apsm__rmu[oeww__rcr] = bodo.libs.array_kernels.quantile(arr,
                    pic__ris)
            return apsm__rmu
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
        dxpx__xxyxj = types.intp
    elif arr.dtype == types.bool_:
        dxpx__xxyxj = np.int64
    else:
        dxpx__xxyxj = arr.dtype
    aogdq__qzov = dxpx__xxyxj(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = aogdq__qzov
            wplsh__jdaha = len(arr)
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(wplsh__jdaha
                ):
                trw__duta = aogdq__qzov
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr
                    ) or not skipna:
                    trw__duta = arr[oeww__rcr]
                    vxox__ihi = 1
                drf__rbwlf += trw__duta
                sbk__mwdh += vxox__ihi
            gwhb__vxmth = bodo.hiframes.series_kernels._var_handle_mincount(
                drf__rbwlf, sbk__mwdh, min_count)
            return gwhb__vxmth
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = aogdq__qzov
            wplsh__jdaha = len(arr)
            for oeww__rcr in numba.parfors.parfor.internal_prange(wplsh__jdaha
                ):
                trw__duta = aogdq__qzov
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = arr[oeww__rcr]
                drf__rbwlf += trw__duta
            return drf__rbwlf
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    tzejf__odnvj = arr.dtype(1)
    if arr.dtype == types.bool_:
        tzejf__odnvj = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = tzejf__odnvj
            sbk__mwdh = 0
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = tzejf__odnvj
                vxox__ihi = 0
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr
                    ) or not skipna:
                    trw__duta = arr[oeww__rcr]
                    vxox__ihi = 1
                sbk__mwdh += vxox__ihi
                drf__rbwlf *= trw__duta
            gwhb__vxmth = bodo.hiframes.series_kernels._var_handle_mincount(
                drf__rbwlf, sbk__mwdh, min_count)
            return gwhb__vxmth
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            drf__rbwlf = tzejf__odnvj
            for oeww__rcr in numba.parfors.parfor.internal_prange(len(arr)):
                trw__duta = tzejf__odnvj
                if not bodo.libs.array_kernels.isna(arr, oeww__rcr):
                    trw__duta = arr[oeww__rcr]
                drf__rbwlf *= trw__duta
            return drf__rbwlf
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        oeww__rcr = bodo.libs.array_kernels._nan_argmax(arr)
        return index[oeww__rcr]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        oeww__rcr = bodo.libs.array_kernels._nan_argmin(arr)
        return index[oeww__rcr]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            ink__pjt = {}
            for zlpd__tnbc in values:
                ink__pjt[bodo.utils.conversion.box_if_dt64(zlpd__tnbc)] = 0
            return ink__pjt
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
        wplsh__jdaha = len(arr)
        apsm__rmu = np.empty(wplsh__jdaha, np.bool_)
        for oeww__rcr in numba.parfors.parfor.internal_prange(wplsh__jdaha):
            apsm__rmu[oeww__rcr] = bodo.utils.conversion.box_if_dt64(arr[
                oeww__rcr]) in values
        return apsm__rmu
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    fil__siwzh = len(in_arr_tup) != 1
    svyr__vpg = list(in_arr_tup.types)
    ratss__jqai = 'def impl(in_arr_tup):\n'
    ratss__jqai += '  n = len(in_arr_tup[0])\n'
    if fil__siwzh:
        qchbi__fnfv = ', '.join([f'in_arr_tup[{oeww__rcr}][unused]' for
            oeww__rcr in range(len(in_arr_tup))])
        tbook__rsuq = ', '.join(['False' for emp__qwmrp in range(len(
            in_arr_tup))])
        ratss__jqai += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({qchbi__fnfv},), ({tbook__rsuq},)): 0 for unused in range(0)}}
"""
        ratss__jqai += '  map_vector = np.empty(n, np.int64)\n'
        for oeww__rcr, oeoh__xpgy in enumerate(svyr__vpg):
            ratss__jqai += f'  in_lst_{oeww__rcr} = []\n'
            if is_str_arr_type(oeoh__xpgy):
                ratss__jqai += f'  total_len_{oeww__rcr} = 0\n'
            ratss__jqai += f'  null_in_lst_{oeww__rcr} = []\n'
        ratss__jqai += '  for i in range(n):\n'
        hxayl__bxf = ', '.join([f'in_arr_tup[{oeww__rcr}][i]' for oeww__rcr in
            range(len(svyr__vpg))])
        gfpgj__wufl = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{oeww__rcr}], i)' for
            oeww__rcr in range(len(svyr__vpg))])
        ratss__jqai += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({hxayl__bxf},), ({gfpgj__wufl},))
"""
        ratss__jqai += '    if data_val not in arr_map:\n'
        ratss__jqai += '      set_val = len(arr_map)\n'
        ratss__jqai += '      values_tup = data_val._data\n'
        ratss__jqai += '      nulls_tup = data_val._null_values\n'
        for oeww__rcr, oeoh__xpgy in enumerate(svyr__vpg):
            ratss__jqai += (
                f'      in_lst_{oeww__rcr}.append(values_tup[{oeww__rcr}])\n')
            ratss__jqai += (
                f'      null_in_lst_{oeww__rcr}.append(nulls_tup[{oeww__rcr}])\n'
                )
            if is_str_arr_type(oeoh__xpgy):
                ratss__jqai += f"""      total_len_{oeww__rcr}  += nulls_tup[{oeww__rcr}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{oeww__rcr}], i)
"""
        ratss__jqai += '      arr_map[data_val] = len(arr_map)\n'
        ratss__jqai += '    else:\n'
        ratss__jqai += '      set_val = arr_map[data_val]\n'
        ratss__jqai += '    map_vector[i] = set_val\n'
        ratss__jqai += '  n_rows = len(arr_map)\n'
        for oeww__rcr, oeoh__xpgy in enumerate(svyr__vpg):
            if is_str_arr_type(oeoh__xpgy):
                ratss__jqai += f"""  out_arr_{oeww__rcr} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{oeww__rcr})
"""
            else:
                ratss__jqai += f"""  out_arr_{oeww__rcr} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{oeww__rcr}], (-1,))
"""
        ratss__jqai += '  for j in range(len(arr_map)):\n'
        for oeww__rcr in range(len(svyr__vpg)):
            ratss__jqai += f'    if null_in_lst_{oeww__rcr}[j]:\n'
            ratss__jqai += (
                f'      bodo.libs.array_kernels.setna(out_arr_{oeww__rcr}, j)\n'
                )
            ratss__jqai += '    else:\n'
            ratss__jqai += (
                f'      out_arr_{oeww__rcr}[j] = in_lst_{oeww__rcr}[j]\n')
        upuqw__per = ', '.join([f'out_arr_{oeww__rcr}' for oeww__rcr in
            range(len(svyr__vpg))])
        ratss__jqai += f'  return ({upuqw__per},), map_vector\n'
    else:
        ratss__jqai += '  in_arr = in_arr_tup[0]\n'
        ratss__jqai += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        ratss__jqai += '  map_vector = np.empty(n, np.int64)\n'
        ratss__jqai += '  is_na = 0\n'
        ratss__jqai += '  in_lst = []\n'
        ratss__jqai += '  na_idxs = []\n'
        if is_str_arr_type(svyr__vpg[0]):
            ratss__jqai += '  total_len = 0\n'
        ratss__jqai += '  for i in range(n):\n'
        ratss__jqai += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        ratss__jqai += '      is_na = 1\n'
        ratss__jqai += '      # Always put NA in the last location.\n'
        ratss__jqai += '      # We use -1 as a placeholder\n'
        ratss__jqai += '      set_val = -1\n'
        ratss__jqai += '      na_idxs.append(i)\n'
        ratss__jqai += '    else:\n'
        ratss__jqai += '      data_val = in_arr[i]\n'
        ratss__jqai += '      if data_val not in arr_map:\n'
        ratss__jqai += '        set_val = len(arr_map)\n'
        ratss__jqai += '        in_lst.append(data_val)\n'
        if is_str_arr_type(svyr__vpg[0]):
            ratss__jqai += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        ratss__jqai += '        arr_map[data_val] = len(arr_map)\n'
        ratss__jqai += '      else:\n'
        ratss__jqai += '        set_val = arr_map[data_val]\n'
        ratss__jqai += '    map_vector[i] = set_val\n'
        ratss__jqai += '  map_vector[na_idxs] = len(arr_map)\n'
        ratss__jqai += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(svyr__vpg[0]):
            ratss__jqai += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            ratss__jqai += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        ratss__jqai += '  for j in range(len(arr_map)):\n'
        ratss__jqai += '    out_arr[j] = in_lst[j]\n'
        ratss__jqai += '  if is_na:\n'
        ratss__jqai += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        ratss__jqai += f'  return (out_arr,), map_vector\n'
    nayd__fva = {}
    exec(ratss__jqai, {'bodo': bodo, 'np': np}, nayd__fva)
    impl = nayd__fva['impl']
    return impl
