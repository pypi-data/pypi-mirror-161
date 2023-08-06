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
        ixso__gwq = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        ixso__gwq = False
    elif A == bodo.string_array_type:
        ixso__gwq = ''
    elif A == bodo.binary_array_type:
        ixso__gwq = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform any with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        psr__zvoj = 0
        for asjm__yml in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, asjm__yml):
                if A[asjm__yml] != ixso__gwq:
                    psr__zvoj += 1
        return psr__zvoj != 0
    return impl


def array_op_all(arr, skipna=True):
    pass


@overload(array_op_all)
def overload_array_op_all(A, skipna=True):
    if isinstance(A, types.Array) and isinstance(A.dtype, types.Integer
        ) or isinstance(A, bodo.libs.int_arr_ext.IntegerArrayType):
        ixso__gwq = 0
    elif isinstance(A, bodo.libs.bool_arr_ext.BooleanArrayType) or isinstance(A
        , types.Array) and A.dtype == types.bool_:
        ixso__gwq = False
    elif A == bodo.string_array_type:
        ixso__gwq = ''
    elif A == bodo.binary_array_type:
        ixso__gwq = b''
    else:
        raise bodo.utils.typing.BodoError(
            f'Cannot perform all with this array type: {A}')

    def impl(A, skipna=True):
        numba.parfors.parfor.init_prange()
        psr__zvoj = 0
        for asjm__yml in numba.parfors.parfor.internal_prange(len(A)):
            if not bodo.libs.array_kernels.isna(A, asjm__yml):
                if A[asjm__yml] == ixso__gwq:
                    psr__zvoj += 1
        return psr__zvoj == 0
    return impl


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    kni__gekn = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(kni__gekn.ctypes, arr,
        parallel, skipna)
    return kni__gekn[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        aklw__ckm = len(arr)
        vohvr__kim = np.empty(aklw__ckm, np.bool_)
        for asjm__yml in numba.parfors.parfor.internal_prange(aklw__ckm):
            vohvr__kim[asjm__yml] = bodo.libs.array_kernels.isna(arr, asjm__yml
                )
        return vohvr__kim
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        psr__zvoj = 0
        for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
            icm__ooxth = 0
            if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                icm__ooxth = 1
            psr__zvoj += icm__ooxth
        kni__gekn = psr__zvoj
        return kni__gekn
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    juep__cfcef = array_op_count(arr)
    fia__nvo = array_op_min(arr)
    eqdpa__dee = array_op_max(arr)
    wjwo__ylkb = array_op_mean(arr)
    yxoba__ectv = array_op_std(arr)
    vro__lqi = array_op_quantile(arr, 0.25)
    ahj__ojj = array_op_quantile(arr, 0.5)
    kmapt__utjis = array_op_quantile(arr, 0.75)
    return (juep__cfcef, wjwo__ylkb, yxoba__ectv, fia__nvo, vro__lqi,
        ahj__ojj, kmapt__utjis, eqdpa__dee)


def array_op_describe_dt_impl(arr):
    juep__cfcef = array_op_count(arr)
    fia__nvo = array_op_min(arr)
    eqdpa__dee = array_op_max(arr)
    wjwo__ylkb = array_op_mean(arr)
    vro__lqi = array_op_quantile(arr, 0.25)
    ahj__ojj = array_op_quantile(arr, 0.5)
    kmapt__utjis = array_op_quantile(arr, 0.75)
    return (juep__cfcef, wjwo__ylkb, fia__nvo, vro__lqi, ahj__ojj,
        kmapt__utjis, eqdpa__dee)


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
            yah__hzoq = numba.cpython.builtins.get_type_max_value(np.int64)
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = yah__hzoq
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[asjm__yml]))
                    icm__ooxth = 1
                yah__hzoq = min(yah__hzoq, ylpw__anxip)
                psr__zvoj += icm__ooxth
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(yah__hzoq,
                psr__zvoj)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            yah__hzoq = numba.cpython.builtins.get_type_max_value(np.int64)
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = yah__hzoq
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[asjm__yml]))
                    icm__ooxth = 1
                yah__hzoq = min(yah__hzoq, ylpw__anxip)
                psr__zvoj += icm__ooxth
            return bodo.hiframes.pd_index_ext._dti_val_finalize(yah__hzoq,
                psr__zvoj)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            jeu__liqc = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yah__hzoq = numba.cpython.builtins.get_type_max_value(np.int64)
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(
                jeu__liqc)):
                lgo__cqekm = jeu__liqc[asjm__yml]
                if lgo__cqekm == -1:
                    continue
                yah__hzoq = min(yah__hzoq, lgo__cqekm)
                psr__zvoj += 1
            kni__gekn = bodo.hiframes.series_kernels._box_cat_val(yah__hzoq,
                arr.dtype, psr__zvoj)
            return kni__gekn
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            yah__hzoq = bodo.hiframes.series_kernels._get_date_max_value()
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = yah__hzoq
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = arr[asjm__yml]
                    icm__ooxth = 1
                yah__hzoq = min(yah__hzoq, ylpw__anxip)
                psr__zvoj += icm__ooxth
            kni__gekn = bodo.hiframes.series_kernels._sum_handle_nan(yah__hzoq,
                psr__zvoj)
            return kni__gekn
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yah__hzoq = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        psr__zvoj = 0
        for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
            ylpw__anxip = yah__hzoq
            icm__ooxth = 0
            if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                ylpw__anxip = arr[asjm__yml]
                icm__ooxth = 1
            yah__hzoq = min(yah__hzoq, ylpw__anxip)
            psr__zvoj += icm__ooxth
        kni__gekn = bodo.hiframes.series_kernels._sum_handle_nan(yah__hzoq,
            psr__zvoj)
        return kni__gekn
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            yah__hzoq = numba.cpython.builtins.get_type_min_value(np.int64)
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = yah__hzoq
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[asjm__yml]))
                    icm__ooxth = 1
                yah__hzoq = max(yah__hzoq, ylpw__anxip)
                psr__zvoj += icm__ooxth
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(yah__hzoq,
                psr__zvoj)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            yah__hzoq = numba.cpython.builtins.get_type_min_value(np.int64)
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = yah__hzoq
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[asjm__yml]))
                    icm__ooxth = 1
                yah__hzoq = max(yah__hzoq, ylpw__anxip)
                psr__zvoj += icm__ooxth
            return bodo.hiframes.pd_index_ext._dti_val_finalize(yah__hzoq,
                psr__zvoj)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            jeu__liqc = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            yah__hzoq = -1
            for asjm__yml in numba.parfors.parfor.internal_prange(len(
                jeu__liqc)):
                yah__hzoq = max(yah__hzoq, jeu__liqc[asjm__yml])
            kni__gekn = bodo.hiframes.series_kernels._box_cat_val(yah__hzoq,
                arr.dtype, 1)
            return kni__gekn
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            yah__hzoq = bodo.hiframes.series_kernels._get_date_min_value()
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = yah__hzoq
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = arr[asjm__yml]
                    icm__ooxth = 1
                yah__hzoq = max(yah__hzoq, ylpw__anxip)
                psr__zvoj += icm__ooxth
            kni__gekn = bodo.hiframes.series_kernels._sum_handle_nan(yah__hzoq,
                psr__zvoj)
            return kni__gekn
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yah__hzoq = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        psr__zvoj = 0
        for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
            ylpw__anxip = yah__hzoq
            icm__ooxth = 0
            if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                ylpw__anxip = arr[asjm__yml]
                icm__ooxth = 1
            yah__hzoq = max(yah__hzoq, ylpw__anxip)
            psr__zvoj += icm__ooxth
        kni__gekn = bodo.hiframes.series_kernels._sum_handle_nan(yah__hzoq,
            psr__zvoj)
        return kni__gekn
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
    pqk__kewe = types.float64
    gioe__fewla = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        pqk__kewe = types.float32
        gioe__fewla = types.float32
    ofja__igmvv = pqk__kewe(0)
    zendo__vzyje = gioe__fewla(0)
    pveu__irb = gioe__fewla(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        yah__hzoq = ofja__igmvv
        psr__zvoj = zendo__vzyje
        for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
            ylpw__anxip = ofja__igmvv
            icm__ooxth = zendo__vzyje
            if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                ylpw__anxip = arr[asjm__yml]
                icm__ooxth = pveu__irb
            yah__hzoq += ylpw__anxip
            psr__zvoj += icm__ooxth
        kni__gekn = bodo.hiframes.series_kernels._mean_handle_nan(yah__hzoq,
            psr__zvoj)
        return kni__gekn
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        oqrpt__foh = 0.0
        mty__bjz = 0.0
        psr__zvoj = 0
        for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
            ylpw__anxip = 0.0
            icm__ooxth = 0
            if not bodo.libs.array_kernels.isna(arr, asjm__yml) or not skipna:
                ylpw__anxip = arr[asjm__yml]
                icm__ooxth = 1
            oqrpt__foh += ylpw__anxip
            mty__bjz += ylpw__anxip * ylpw__anxip
            psr__zvoj += icm__ooxth
        kni__gekn = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            oqrpt__foh, mty__bjz, psr__zvoj, ddof)
        return kni__gekn
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
                vohvr__kim = np.empty(len(q), np.int64)
                for asjm__yml in range(len(q)):
                    ngod__ywx = np.float64(q[asjm__yml])
                    vohvr__kim[asjm__yml] = bodo.libs.array_kernels.quantile(
                        arr.view(np.int64), ngod__ywx)
                return vohvr__kim.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            vohvr__kim = np.empty(len(q), np.float64)
            for asjm__yml in range(len(q)):
                ngod__ywx = np.float64(q[asjm__yml])
                vohvr__kim[asjm__yml] = bodo.libs.array_kernels.quantile(arr,
                    ngod__ywx)
            return vohvr__kim
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
        jjk__nzfsv = types.intp
    elif arr.dtype == types.bool_:
        jjk__nzfsv = np.int64
    else:
        jjk__nzfsv = arr.dtype
    zkd__xat = jjk__nzfsv(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yah__hzoq = zkd__xat
            aklw__ckm = len(arr)
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(aklw__ckm):
                ylpw__anxip = zkd__xat
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml
                    ) or not skipna:
                    ylpw__anxip = arr[asjm__yml]
                    icm__ooxth = 1
                yah__hzoq += ylpw__anxip
                psr__zvoj += icm__ooxth
            kni__gekn = bodo.hiframes.series_kernels._var_handle_mincount(
                yah__hzoq, psr__zvoj, min_count)
            return kni__gekn
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yah__hzoq = zkd__xat
            aklw__ckm = len(arr)
            for asjm__yml in numba.parfors.parfor.internal_prange(aklw__ckm):
                ylpw__anxip = zkd__xat
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = arr[asjm__yml]
                yah__hzoq += ylpw__anxip
            return yah__hzoq
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    daob__ajs = arr.dtype(1)
    if arr.dtype == types.bool_:
        daob__ajs = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yah__hzoq = daob__ajs
            psr__zvoj = 0
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = daob__ajs
                icm__ooxth = 0
                if not bodo.libs.array_kernels.isna(arr, asjm__yml
                    ) or not skipna:
                    ylpw__anxip = arr[asjm__yml]
                    icm__ooxth = 1
                psr__zvoj += icm__ooxth
                yah__hzoq *= ylpw__anxip
            kni__gekn = bodo.hiframes.series_kernels._var_handle_mincount(
                yah__hzoq, psr__zvoj, min_count)
            return kni__gekn
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            yah__hzoq = daob__ajs
            for asjm__yml in numba.parfors.parfor.internal_prange(len(arr)):
                ylpw__anxip = daob__ajs
                if not bodo.libs.array_kernels.isna(arr, asjm__yml):
                    ylpw__anxip = arr[asjm__yml]
                yah__hzoq *= ylpw__anxip
            return yah__hzoq
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        asjm__yml = bodo.libs.array_kernels._nan_argmax(arr)
        return index[asjm__yml]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        asjm__yml = bodo.libs.array_kernels._nan_argmin(arr)
        return index[asjm__yml]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            lqqtl__dhf = {}
            for ooci__oawea in values:
                lqqtl__dhf[bodo.utils.conversion.box_if_dt64(ooci__oawea)] = 0
            return lqqtl__dhf
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
        aklw__ckm = len(arr)
        vohvr__kim = np.empty(aklw__ckm, np.bool_)
        for asjm__yml in numba.parfors.parfor.internal_prange(aklw__ckm):
            vohvr__kim[asjm__yml] = bodo.utils.conversion.box_if_dt64(arr[
                asjm__yml]) in values
        return vohvr__kim
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    cfsm__mlp = len(in_arr_tup) != 1
    iyio__cow = list(in_arr_tup.types)
    ghwjl__hbo = 'def impl(in_arr_tup):\n'
    ghwjl__hbo += '  n = len(in_arr_tup[0])\n'
    if cfsm__mlp:
        nfxn__vgg = ', '.join([f'in_arr_tup[{asjm__yml}][unused]' for
            asjm__yml in range(len(in_arr_tup))])
        fthu__dnkq = ', '.join(['False' for obw__mksx in range(len(
            in_arr_tup))])
        ghwjl__hbo += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({nfxn__vgg},), ({fthu__dnkq},)): 0 for unused in range(0)}}
"""
        ghwjl__hbo += '  map_vector = np.empty(n, np.int64)\n'
        for asjm__yml, unvvs__dgmu in enumerate(iyio__cow):
            ghwjl__hbo += f'  in_lst_{asjm__yml} = []\n'
            if is_str_arr_type(unvvs__dgmu):
                ghwjl__hbo += f'  total_len_{asjm__yml} = 0\n'
            ghwjl__hbo += f'  null_in_lst_{asjm__yml} = []\n'
        ghwjl__hbo += '  for i in range(n):\n'
        teqg__fajn = ', '.join([f'in_arr_tup[{asjm__yml}][i]' for asjm__yml in
            range(len(iyio__cow))])
        xusnr__pmr = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{asjm__yml}], i)' for
            asjm__yml in range(len(iyio__cow))])
        ghwjl__hbo += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({teqg__fajn},), ({xusnr__pmr},))
"""
        ghwjl__hbo += '    if data_val not in arr_map:\n'
        ghwjl__hbo += '      set_val = len(arr_map)\n'
        ghwjl__hbo += '      values_tup = data_val._data\n'
        ghwjl__hbo += '      nulls_tup = data_val._null_values\n'
        for asjm__yml, unvvs__dgmu in enumerate(iyio__cow):
            ghwjl__hbo += (
                f'      in_lst_{asjm__yml}.append(values_tup[{asjm__yml}])\n')
            ghwjl__hbo += (
                f'      null_in_lst_{asjm__yml}.append(nulls_tup[{asjm__yml}])\n'
                )
            if is_str_arr_type(unvvs__dgmu):
                ghwjl__hbo += f"""      total_len_{asjm__yml}  += nulls_tup[{asjm__yml}] * bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr_tup[{asjm__yml}], i)
"""
        ghwjl__hbo += '      arr_map[data_val] = len(arr_map)\n'
        ghwjl__hbo += '    else:\n'
        ghwjl__hbo += '      set_val = arr_map[data_val]\n'
        ghwjl__hbo += '    map_vector[i] = set_val\n'
        ghwjl__hbo += '  n_rows = len(arr_map)\n'
        for asjm__yml, unvvs__dgmu in enumerate(iyio__cow):
            if is_str_arr_type(unvvs__dgmu):
                ghwjl__hbo += f"""  out_arr_{asjm__yml} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{asjm__yml})
"""
            else:
                ghwjl__hbo += f"""  out_arr_{asjm__yml} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{asjm__yml}], (-1,))
"""
        ghwjl__hbo += '  for j in range(len(arr_map)):\n'
        for asjm__yml in range(len(iyio__cow)):
            ghwjl__hbo += f'    if null_in_lst_{asjm__yml}[j]:\n'
            ghwjl__hbo += (
                f'      bodo.libs.array_kernels.setna(out_arr_{asjm__yml}, j)\n'
                )
            ghwjl__hbo += '    else:\n'
            ghwjl__hbo += (
                f'      out_arr_{asjm__yml}[j] = in_lst_{asjm__yml}[j]\n')
        ovyjq__nif = ', '.join([f'out_arr_{asjm__yml}' for asjm__yml in
            range(len(iyio__cow))])
        ghwjl__hbo += f'  return ({ovyjq__nif},), map_vector\n'
    else:
        ghwjl__hbo += '  in_arr = in_arr_tup[0]\n'
        ghwjl__hbo += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        ghwjl__hbo += '  map_vector = np.empty(n, np.int64)\n'
        ghwjl__hbo += '  is_na = 0\n'
        ghwjl__hbo += '  in_lst = []\n'
        ghwjl__hbo += '  na_idxs = []\n'
        if is_str_arr_type(iyio__cow[0]):
            ghwjl__hbo += '  total_len = 0\n'
        ghwjl__hbo += '  for i in range(n):\n'
        ghwjl__hbo += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        ghwjl__hbo += '      is_na = 1\n'
        ghwjl__hbo += '      # Always put NA in the last location.\n'
        ghwjl__hbo += '      # We use -1 as a placeholder\n'
        ghwjl__hbo += '      set_val = -1\n'
        ghwjl__hbo += '      na_idxs.append(i)\n'
        ghwjl__hbo += '    else:\n'
        ghwjl__hbo += '      data_val = in_arr[i]\n'
        ghwjl__hbo += '      if data_val not in arr_map:\n'
        ghwjl__hbo += '        set_val = len(arr_map)\n'
        ghwjl__hbo += '        in_lst.append(data_val)\n'
        if is_str_arr_type(iyio__cow[0]):
            ghwjl__hbo += """        total_len += bodo.libs.str_arr_ext.get_str_arr_item_length(in_arr, i)
"""
        ghwjl__hbo += '        arr_map[data_val] = len(arr_map)\n'
        ghwjl__hbo += '      else:\n'
        ghwjl__hbo += '        set_val = arr_map[data_val]\n'
        ghwjl__hbo += '    map_vector[i] = set_val\n'
        ghwjl__hbo += '  map_vector[na_idxs] = len(arr_map)\n'
        ghwjl__hbo += '  n_rows = len(arr_map) + is_na\n'
        if is_str_arr_type(iyio__cow[0]):
            ghwjl__hbo += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            ghwjl__hbo += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        ghwjl__hbo += '  for j in range(len(arr_map)):\n'
        ghwjl__hbo += '    out_arr[j] = in_lst[j]\n'
        ghwjl__hbo += '  if is_na:\n'
        ghwjl__hbo += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        ghwjl__hbo += f'  return (out_arr,), map_vector\n'
    eizp__tpwsj = {}
    exec(ghwjl__hbo, {'bodo': bodo, 'np': np}, eizp__tpwsj)
    impl = eizp__tpwsj['impl']
    return impl
