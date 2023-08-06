"""
Implements array kernels such as median and quantile.
"""
import hashlib
import inspect
import math
import operator
import re
import warnings
from math import sqrt
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types, typing
from numba.core.imputils import lower_builtin
from numba.core.ir_utils import find_const, guard
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import overload, overload_attribute, register_jitable
from numba.np.arrayobj import make_array
from numba.np.numpy_support import as_dtype
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, init_categorical_array
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs import quantile_alg
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_info_decref_array, delete_table, delete_table_decref_arrays, drop_duplicates_table, info_from_table, info_to_array, sample_table
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, offset_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.dict_arr_ext import DictionaryArrayType
from bodo.libs.distributed_api import Reduce_Type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import str_arr_set_na, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, check_unsupported_args, decode_if_dict_array, element_type, find_common_np_dtype, get_overload_const_bool, get_overload_const_list, get_overload_const_str, is_overload_constant_bool, is_overload_constant_str, is_overload_none, is_overload_true, is_str_arr_type, raise_bodo_error, to_str_arr_if_dict_array
from bodo.utils.utils import build_set_seen_na, check_and_propagate_cpp_exception, numba_to_c_type, unliteral_all
ll.add_symbol('quantile_sequential', quantile_alg.quantile_sequential)
ll.add_symbol('quantile_parallel', quantile_alg.quantile_parallel)
MPI_ROOT = 0
sum_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value)
max_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Max.value)
min_op = np.int32(bodo.libs.distributed_api.Reduce_Type.Min.value)


def isna(arr, i):
    return False


@overload(isna)
def overload_isna(arr, i):
    i = types.unliteral(i)
    if arr == string_array_type:
        return lambda arr, i: bodo.libs.str_arr_ext.str_arr_is_na(arr, i)
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type,
        datetime_timedelta_array_type, string_array_split_view_type):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._null_bitmap, i)
    if isinstance(arr, ArrayItemArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, StructArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.struct_arr_ext.get_null_bitmap(arr), i)
    if isinstance(arr, TupleArrayType):
        return lambda arr, i: bodo.libs.array_kernels.isna(arr._data, i)
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        return lambda arr, i: arr.codes[i] == -1
    if arr == bodo.binary_array_type:
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bodo
            .libs.array_item_arr_ext.get_null_bitmap(arr._data), i)
    if isinstance(arr, types.List):
        if arr.dtype == types.none:
            return lambda arr, i: True
        elif isinstance(arr.dtype, types.optional):
            return lambda arr, i: arr[i] is None
        else:
            return lambda arr, i: False
    if isinstance(arr, bodo.NullableTupleType):
        return lambda arr, i: arr._null_values[i]
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, i: not bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr
            ._indices._null_bitmap, i) or bodo.libs.array_kernels.isna(arr.
            _data, arr._indices[i])
    if isinstance(arr, DatetimeArrayType):
        return lambda arr, i: np.isnat(arr._data[i])
    assert isinstance(arr, types.Array), f'Invalid array type in isna(): {arr}'
    dtype = arr.dtype
    if isinstance(dtype, types.Float):
        return lambda arr, i: np.isnan(arr[i])
    if isinstance(dtype, (types.NPDatetime, types.NPTimedelta)):
        return lambda arr, i: np.isnat(arr[i])
    return lambda arr, i: False


def setna(arr, ind, int_nan_const=0):
    arr[ind] = np.nan


@overload(setna, no_unliteral=True)
def setna_overload(arr, ind, int_nan_const=0):
    if isinstance(arr.dtype, types.Float):
        return setna
    if isinstance(arr.dtype, (types.NPDatetime, types.NPTimedelta)):
        asr__uqll = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = asr__uqll
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        asr__uqll = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = asr__uqll
        return _setnan_impl
    if arr == string_array_type:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = ''
            str_arr_set_na(arr, ind)
        return impl
    if isinstance(arr, DictionaryArrayType):
        return lambda arr, ind, int_nan_const=0: bodo.libs.array_kernels.setna(
            arr._indices, ind)
    if arr == boolean_array:

        def impl(arr, ind, int_nan_const=0):
            arr[ind] = False
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)):
        return (lambda arr, ind, int_nan_const=0: bodo.libs.int_arr_ext.
            set_bit_to_arr(arr._null_bitmap, ind, 0))
    if arr == bodo.binary_array_type:

        def impl_binary_arr(arr, ind, int_nan_const=0):
            xald__ummhe = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            xald__ummhe[ind + 1] = xald__ummhe[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            xald__ummhe = bodo.libs.array_item_arr_ext.get_offsets(arr)
            xald__ummhe[ind + 1] = xald__ummhe[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr), ind, 0)
        return impl_arr_item
    if isinstance(arr, bodo.libs.struct_arr_ext.StructArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.struct_arr_ext.
                get_null_bitmap(arr), ind, 0)
            data = bodo.libs.struct_arr_ext.get_data(arr)
            setna_tup(data, ind)
        return impl
    if isinstance(arr, TupleArrayType):

        def impl(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._data, ind)
        return impl
    if arr.dtype == types.bool_:

        def b_set(arr, ind, int_nan_const=0):
            arr[ind] = False
        return b_set
    if isinstance(arr, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):

        def setna_cat(arr, ind, int_nan_const=0):
            arr.codes[ind] = -1
        return setna_cat
    if isinstance(arr.dtype, types.Integer):

        def setna_int(arr, ind, int_nan_const=0):
            arr[ind] = int_nan_const
        return setna_int
    if arr == datetime_date_array_type:

        def setna_datetime_date(arr, ind, int_nan_const=0):
            arr._data[ind] = (1970 << 32) + (1 << 16) + 1
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_date
    if arr == datetime_timedelta_array_type:

        def setna_datetime_timedelta(arr, ind, int_nan_const=0):
            bodo.libs.array_kernels.setna(arr._days_data, ind)
            bodo.libs.array_kernels.setna(arr._seconds_data, ind)
            bodo.libs.array_kernels.setna(arr._microseconds_data, ind)
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, 0)
        return setna_datetime_timedelta
    return lambda arr, ind, int_nan_const=0: None


def setna_tup(arr_tup, ind, int_nan_const=0):
    for arr in arr_tup:
        arr[ind] = np.nan


@overload(setna_tup, no_unliteral=True)
def overload_setna_tup(arr_tup, ind, int_nan_const=0):
    udapn__vonv = arr_tup.count
    wal__jdl = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(udapn__vonv):
        wal__jdl += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    wal__jdl += '  return\n'
    klaeu__yjmr = {}
    exec(wal__jdl, {'setna': setna}, klaeu__yjmr)
    impl = klaeu__yjmr['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        wriwm__rumvz = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(wriwm__rumvz.start, wriwm__rumvz.stop, wriwm__rumvz.step
            ):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        mugqm__omfy = 'n'
        meum__pyhn = 'n_pes'
        trfmn__stfjf = 'min_op'
    else:
        mugqm__omfy = 'n-1, -1, -1'
        meum__pyhn = '-1'
        trfmn__stfjf = 'max_op'
    wal__jdl = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {meum__pyhn}
    for i in range({mugqm__omfy}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {trfmn__stfjf}))
        if possible_valid_rank != {meum__pyhn}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    klaeu__yjmr = {}
    exec(wal__jdl, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op': max_op,
        'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.box_if_dt64},
        klaeu__yjmr)
    impl = klaeu__yjmr['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    vfy__jijhh = array_to_info(arr)
    _median_series_computation(res, vfy__jijhh, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(vfy__jijhh)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    vfy__jijhh = array_to_info(arr)
    _autocorr_series_computation(res, vfy__jijhh, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(vfy__jijhh)


@numba.njit
def autocorr(arr, lag=1, parallel=False):
    res = np.empty(1, types.float64)
    autocorr_series_computation(res.ctypes, arr, lag, parallel)
    return res[0]


ll.add_symbol('compute_series_monotonicity', quantile_alg.
    compute_series_monotonicity)
_compute_series_monotonicity = types.ExternalFunction(
    'compute_series_monotonicity', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def series_monotonicity_call(res, arr, inc_dec, is_parallel):
    vfy__jijhh = array_to_info(arr)
    _compute_series_monotonicity(res, vfy__jijhh, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(vfy__jijhh)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    chxa__xaofh = res[0] > 0.5
    return chxa__xaofh


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        qnasn__nzwo = '-'
        nojsy__cdma = 'index_arr[0] > threshhold_date'
        mugqm__omfy = '1, n+1'
        itdzw__jgu = 'index_arr[-i] <= threshhold_date'
        pyy__hxk = 'i - 1'
    else:
        qnasn__nzwo = '+'
        nojsy__cdma = 'index_arr[-1] < threshhold_date'
        mugqm__omfy = 'n'
        itdzw__jgu = 'index_arr[i] >= threshhold_date'
        pyy__hxk = 'i'
    wal__jdl = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        wal__jdl += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        wal__jdl += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            wal__jdl += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            wal__jdl += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            wal__jdl += '    else:\n'
            wal__jdl += '      threshhold_date = initial_date + date_offset\n'
        else:
            wal__jdl += (
                f'    threshhold_date = initial_date {qnasn__nzwo} date_offset\n'
                )
    else:
        wal__jdl += f'  threshhold_date = initial_date {qnasn__nzwo} offset\n'
    wal__jdl += '  local_valid = 0\n'
    wal__jdl += f'  n = len(index_arr)\n'
    wal__jdl += f'  if n:\n'
    wal__jdl += f'    if {nojsy__cdma}:\n'
    wal__jdl += '      loc_valid = n\n'
    wal__jdl += '    else:\n'
    wal__jdl += f'      for i in range({mugqm__omfy}):\n'
    wal__jdl += f'        if {itdzw__jgu}:\n'
    wal__jdl += f'          loc_valid = {pyy__hxk}\n'
    wal__jdl += '          break\n'
    wal__jdl += '  if is_parallel:\n'
    wal__jdl += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    wal__jdl += '    return total_valid\n'
    wal__jdl += '  else:\n'
    wal__jdl += '    return loc_valid\n'
    klaeu__yjmr = {}
    exec(wal__jdl, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, klaeu__yjmr)
    return klaeu__yjmr['impl']


def quantile(A, q):
    return 0


def quantile_parallel(A, q):
    return 0


@infer_global(quantile)
@infer_global(quantile_parallel)
class QuantileType(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) in [2, 3]
        return signature(types.float64, *unliteral_all(args))


@lower_builtin(quantile, types.Array, types.float64)
@lower_builtin(quantile, IntegerArrayType, types.float64)
@lower_builtin(quantile, BooleanArrayType, types.float64)
def lower_dist_quantile_seq(context, builder, sig, args):
    zdelu__egmqj = numba_to_c_type(sig.args[0].dtype)
    ixj__xaqq = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), zdelu__egmqj))
    iyss__dqq = args[0]
    fpm__iqsow = sig.args[0]
    if isinstance(fpm__iqsow, (IntegerArrayType, BooleanArrayType)):
        iyss__dqq = cgutils.create_struct_proxy(fpm__iqsow)(context,
            builder, iyss__dqq).data
        fpm__iqsow = types.Array(fpm__iqsow.dtype, 1, 'C')
    assert fpm__iqsow.ndim == 1
    arr = make_array(fpm__iqsow)(context, builder, iyss__dqq)
    tnmra__rvj = builder.extract_value(arr.shape, 0)
    qlny__erhdj = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        tnmra__rvj, args[1], builder.load(ixj__xaqq)]
    vwed__ngn = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    tegni__dzhhs = lir.FunctionType(lir.DoubleType(), vwed__ngn)
    rcsk__xwi = cgutils.get_or_insert_function(builder.module, tegni__dzhhs,
        name='quantile_sequential')
    dmm__trd = builder.call(rcsk__xwi, qlny__erhdj)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return dmm__trd


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    zdelu__egmqj = numba_to_c_type(sig.args[0].dtype)
    ixj__xaqq = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), zdelu__egmqj))
    iyss__dqq = args[0]
    fpm__iqsow = sig.args[0]
    if isinstance(fpm__iqsow, (IntegerArrayType, BooleanArrayType)):
        iyss__dqq = cgutils.create_struct_proxy(fpm__iqsow)(context,
            builder, iyss__dqq).data
        fpm__iqsow = types.Array(fpm__iqsow.dtype, 1, 'C')
    assert fpm__iqsow.ndim == 1
    arr = make_array(fpm__iqsow)(context, builder, iyss__dqq)
    tnmra__rvj = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        lhnub__inw = args[2]
    else:
        lhnub__inw = tnmra__rvj
    qlny__erhdj = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        tnmra__rvj, lhnub__inw, args[1], builder.load(ixj__xaqq)]
    vwed__ngn = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType(
        64), lir.DoubleType(), lir.IntType(32)]
    tegni__dzhhs = lir.FunctionType(lir.DoubleType(), vwed__ngn)
    rcsk__xwi = cgutils.get_or_insert_function(builder.module, tegni__dzhhs,
        name='quantile_parallel')
    dmm__trd = builder.call(rcsk__xwi, qlny__erhdj)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return dmm__trd


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        zvj__rlbsl = np.nonzero(pd.isna(arr))[0]
        hff__yey = arr[1:] != arr[:-1]
        hff__yey[pd.isna(hff__yey)] = False
        ysdy__zvo = hff__yey.astype(np.bool_)
        upwys__rey = np.concatenate((np.array([True]), ysdy__zvo))
        if zvj__rlbsl.size:
            aijcy__yiv, ctax__mewjb = zvj__rlbsl[0], zvj__rlbsl[1:]
            upwys__rey[aijcy__yiv] = True
            if ctax__mewjb.size:
                upwys__rey[ctax__mewjb] = False
                if ctax__mewjb[-1] + 1 < upwys__rey.size:
                    upwys__rey[ctax__mewjb[-1] + 1] = True
            elif aijcy__yiv + 1 < upwys__rey.size:
                upwys__rey[aijcy__yiv + 1] = True
        return upwys__rey
    return impl


def rank(arr, method='average', na_option='keep', ascending=True, pct=False):
    return arr


@overload(rank, no_unliteral=True, inline='always')
def overload_rank(arr, method='average', na_option='keep', ascending=True,
    pct=False):
    if not is_overload_constant_str(method):
        raise_bodo_error(
            "Series.rank(): 'method' argument must be a constant string")
    method = get_overload_const_str(method)
    if not is_overload_constant_str(na_option):
        raise_bodo_error(
            "Series.rank(): 'na_option' argument must be a constant string")
    na_option = get_overload_const_str(na_option)
    if not is_overload_constant_bool(ascending):
        raise_bodo_error(
            "Series.rank(): 'ascending' argument must be a constant boolean")
    ascending = get_overload_const_bool(ascending)
    if not is_overload_constant_bool(pct):
        raise_bodo_error(
            "Series.rank(): 'pct' argument must be a constant boolean")
    pct = get_overload_const_bool(pct)
    if method == 'first' and not ascending:
        raise BodoError(
            "Series.rank(): method='first' with ascending=False is currently unsupported."
            )
    wal__jdl = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    wal__jdl += '  na_idxs = pd.isna(arr)\n'
    wal__jdl += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    wal__jdl += '  nas = sum(na_idxs)\n'
    if not ascending:
        wal__jdl += '  if nas and nas < (sorter.size - 1):\n'
        wal__jdl += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        wal__jdl += '  else:\n'
        wal__jdl += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        wal__jdl += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    wal__jdl += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    wal__jdl += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        wal__jdl += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        wal__jdl += '    inv,\n'
        wal__jdl += '    new_dtype=np.float64,\n'
        wal__jdl += '    copy=True,\n'
        wal__jdl += '    nan_to_str=False,\n'
        wal__jdl += '    from_series=True,\n'
        wal__jdl += '    ) + 1\n'
    else:
        wal__jdl += '  arr = arr[sorter]\n'
        wal__jdl += '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n'
        wal__jdl += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            wal__jdl += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            wal__jdl += '    dense,\n'
            wal__jdl += '    new_dtype=np.float64,\n'
            wal__jdl += '    copy=True,\n'
            wal__jdl += '    nan_to_str=False,\n'
            wal__jdl += '    from_series=True,\n'
            wal__jdl += '  )\n'
        else:
            wal__jdl += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            wal__jdl += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                wal__jdl += '  ret = count_float[dense]\n'
            elif method == 'min':
                wal__jdl += '  ret = count_float[dense - 1] + 1\n'
            else:
                wal__jdl += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                wal__jdl += '  ret[na_idxs] = -1\n'
            wal__jdl += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            wal__jdl += '  div_val = arr.size - nas\n'
        else:
            wal__jdl += '  div_val = arr.size\n'
        wal__jdl += '  for i in range(len(ret)):\n'
        wal__jdl += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        wal__jdl += '  ret[na_idxs] = np.nan\n'
    wal__jdl += '  return ret\n'
    klaeu__yjmr = {}
    exec(wal__jdl, {'np': np, 'pd': pd, 'bodo': bodo}, klaeu__yjmr)
    return klaeu__yjmr['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    chn__ywp = start
    upanv__vny = 2 * start + 1
    tejyw__byroz = 2 * start + 2
    if upanv__vny < n and not cmp_f(arr[upanv__vny], arr[chn__ywp]):
        chn__ywp = upanv__vny
    if tejyw__byroz < n and not cmp_f(arr[tejyw__byroz], arr[chn__ywp]):
        chn__ywp = tejyw__byroz
    if chn__ywp != start:
        arr[start], arr[chn__ywp] = arr[chn__ywp], arr[start]
        ind_arr[start], ind_arr[chn__ywp] = ind_arr[chn__ywp], ind_arr[start]
        min_heapify(arr, ind_arr, n, chn__ywp, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        ontk__jjz = np.empty(k, A.dtype)
        njgda__vgc = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                ontk__jjz[ind] = A[i]
                njgda__vgc[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            ontk__jjz = ontk__jjz[:ind]
            njgda__vgc = njgda__vgc[:ind]
        return ontk__jjz, njgda__vgc, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        vhrv__fpw = np.sort(A)
        hqxd__redu = index_arr[np.argsort(A)]
        ktt__upg = pd.Series(vhrv__fpw).notna().values
        vhrv__fpw = vhrv__fpw[ktt__upg]
        hqxd__redu = hqxd__redu[ktt__upg]
        if is_largest:
            vhrv__fpw = vhrv__fpw[::-1]
            hqxd__redu = hqxd__redu[::-1]
        return np.ascontiguousarray(vhrv__fpw), np.ascontiguousarray(hqxd__redu
            )
    ontk__jjz, njgda__vgc, start = select_k_nonan(A, index_arr, m, k)
    njgda__vgc = njgda__vgc[ontk__jjz.argsort()]
    ontk__jjz.sort()
    if not is_largest:
        ontk__jjz = np.ascontiguousarray(ontk__jjz[::-1])
        njgda__vgc = np.ascontiguousarray(njgda__vgc[::-1])
    for i in range(start, m):
        if cmp_f(A[i], ontk__jjz[0]):
            ontk__jjz[0] = A[i]
            njgda__vgc[0] = index_arr[i]
            min_heapify(ontk__jjz, njgda__vgc, k, 0, cmp_f)
    njgda__vgc = njgda__vgc[ontk__jjz.argsort()]
    ontk__jjz.sort()
    if is_largest:
        ontk__jjz = ontk__jjz[::-1]
        njgda__vgc = njgda__vgc[::-1]
    return np.ascontiguousarray(ontk__jjz), np.ascontiguousarray(njgda__vgc)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    jxto__xwyuz = bodo.libs.distributed_api.get_rank()
    bjkqw__rudei, udmj__gcmsu = nlargest(A, I, k, is_largest, cmp_f)
    xgh__tbv = bodo.libs.distributed_api.gatherv(bjkqw__rudei)
    fum__mpxm = bodo.libs.distributed_api.gatherv(udmj__gcmsu)
    if jxto__xwyuz == MPI_ROOT:
        res, rcypa__wms = nlargest(xgh__tbv, fum__mpxm, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        rcypa__wms = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(rcypa__wms)
    return res, rcypa__wms


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    kix__tyr, lml__gghy = mat.shape
    uvzoq__hxghc = np.empty((lml__gghy, lml__gghy), dtype=np.float64)
    for hzy__jgz in range(lml__gghy):
        for vxdw__hwd in range(hzy__jgz + 1):
            yqax__sqwb = 0
            kohez__ewg = zuzsd__qmxpv = scaq__vzomt = owoqz__muzz = 0.0
            for i in range(kix__tyr):
                if np.isfinite(mat[i, hzy__jgz]) and np.isfinite(mat[i,
                    vxdw__hwd]):
                    iqnhz__ocqtg = mat[i, hzy__jgz]
                    xtk__pwk = mat[i, vxdw__hwd]
                    yqax__sqwb += 1
                    scaq__vzomt += iqnhz__ocqtg
                    owoqz__muzz += xtk__pwk
            if parallel:
                yqax__sqwb = bodo.libs.distributed_api.dist_reduce(yqax__sqwb,
                    sum_op)
                scaq__vzomt = bodo.libs.distributed_api.dist_reduce(scaq__vzomt
                    , sum_op)
                owoqz__muzz = bodo.libs.distributed_api.dist_reduce(owoqz__muzz
                    , sum_op)
            if yqax__sqwb < minpv:
                uvzoq__hxghc[hzy__jgz, vxdw__hwd] = uvzoq__hxghc[vxdw__hwd,
                    hzy__jgz] = np.nan
            else:
                ibevh__zzm = scaq__vzomt / yqax__sqwb
                jdju__grz = owoqz__muzz / yqax__sqwb
                scaq__vzomt = 0.0
                for i in range(kix__tyr):
                    if np.isfinite(mat[i, hzy__jgz]) and np.isfinite(mat[i,
                        vxdw__hwd]):
                        iqnhz__ocqtg = mat[i, hzy__jgz] - ibevh__zzm
                        xtk__pwk = mat[i, vxdw__hwd] - jdju__grz
                        scaq__vzomt += iqnhz__ocqtg * xtk__pwk
                        kohez__ewg += iqnhz__ocqtg * iqnhz__ocqtg
                        zuzsd__qmxpv += xtk__pwk * xtk__pwk
                if parallel:
                    scaq__vzomt = bodo.libs.distributed_api.dist_reduce(
                        scaq__vzomt, sum_op)
                    kohez__ewg = bodo.libs.distributed_api.dist_reduce(
                        kohez__ewg, sum_op)
                    zuzsd__qmxpv = bodo.libs.distributed_api.dist_reduce(
                        zuzsd__qmxpv, sum_op)
                ycdf__hipmc = yqax__sqwb - 1.0 if cov else sqrt(kohez__ewg *
                    zuzsd__qmxpv)
                if ycdf__hipmc != 0.0:
                    uvzoq__hxghc[hzy__jgz, vxdw__hwd] = uvzoq__hxghc[
                        vxdw__hwd, hzy__jgz] = scaq__vzomt / ycdf__hipmc
                else:
                    uvzoq__hxghc[hzy__jgz, vxdw__hwd] = uvzoq__hxghc[
                        vxdw__hwd, hzy__jgz] = np.nan
    return uvzoq__hxghc


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    aveaf__upjb = n != 1
    wal__jdl = 'def impl(data, parallel=False):\n'
    wal__jdl += '  if parallel:\n'
    djw__zdn = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    wal__jdl += f'    cpp_table = arr_info_list_to_table([{djw__zdn}])\n'
    wal__jdl += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    vobjt__dvptf = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    wal__jdl += f'    data = ({vobjt__dvptf},)\n'
    wal__jdl += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    wal__jdl += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    wal__jdl += '    bodo.libs.array.delete_table(cpp_table)\n'
    wal__jdl += '  n = len(data[0])\n'
    wal__jdl += '  out = np.empty(n, np.bool_)\n'
    wal__jdl += '  uniqs = dict()\n'
    if aveaf__upjb:
        wal__jdl += '  for i in range(n):\n'
        afvt__cjr = ', '.join(f'data[{i}][i]' for i in range(n))
        nfooh__rve = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        wal__jdl += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({afvt__cjr},), ({nfooh__rve},))
"""
        wal__jdl += '    if val in uniqs:\n'
        wal__jdl += '      out[i] = True\n'
        wal__jdl += '    else:\n'
        wal__jdl += '      out[i] = False\n'
        wal__jdl += '      uniqs[val] = 0\n'
    else:
        wal__jdl += '  data = data[0]\n'
        wal__jdl += '  hasna = False\n'
        wal__jdl += '  for i in range(n):\n'
        wal__jdl += '    if bodo.libs.array_kernels.isna(data, i):\n'
        wal__jdl += '      out[i] = hasna\n'
        wal__jdl += '      hasna = True\n'
        wal__jdl += '    else:\n'
        wal__jdl += '      val = data[i]\n'
        wal__jdl += '      if val in uniqs:\n'
        wal__jdl += '        out[i] = True\n'
        wal__jdl += '      else:\n'
        wal__jdl += '        out[i] = False\n'
        wal__jdl += '        uniqs[val] = 0\n'
    wal__jdl += '  if parallel:\n'
    wal__jdl += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    wal__jdl += '  return out\n'
    klaeu__yjmr = {}
    exec(wal__jdl, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, klaeu__yjmr)
    impl = klaeu__yjmr['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    udapn__vonv = len(data)
    wal__jdl = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    wal__jdl += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        udapn__vonv)))
    wal__jdl += '  table_total = arr_info_list_to_table(info_list_total)\n'
    wal__jdl += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(udapn__vonv))
    for xpgxa__iuram in range(udapn__vonv):
        wal__jdl += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(xpgxa__iuram, xpgxa__iuram, xpgxa__iuram))
    wal__jdl += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(udapn__vonv))
    wal__jdl += '  delete_table(out_table)\n'
    wal__jdl += '  delete_table(table_total)\n'
    wal__jdl += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(udapn__vonv)))
    klaeu__yjmr = {}
    exec(wal__jdl, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, klaeu__yjmr)
    impl = klaeu__yjmr['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    udapn__vonv = len(data)
    wal__jdl = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    wal__jdl += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        udapn__vonv)))
    wal__jdl += '  table_total = arr_info_list_to_table(info_list_total)\n'
    wal__jdl += '  keep_i = 0\n'
    wal__jdl += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for xpgxa__iuram in range(udapn__vonv):
        wal__jdl += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(xpgxa__iuram, xpgxa__iuram, xpgxa__iuram))
    wal__jdl += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(udapn__vonv))
    wal__jdl += '  delete_table(out_table)\n'
    wal__jdl += '  delete_table(table_total)\n'
    wal__jdl += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(udapn__vonv)))
    klaeu__yjmr = {}
    exec(wal__jdl, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, klaeu__yjmr)
    impl = klaeu__yjmr['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        xjp__tyi = [array_to_info(data_arr)]
        xyesa__giiiv = arr_info_list_to_table(xjp__tyi)
        ysbz__rwrr = 0
        oxxtd__kngj = drop_duplicates_table(xyesa__giiiv, parallel, 1,
            ysbz__rwrr, False, True)
        axdgk__rmaja = info_to_array(info_from_table(oxxtd__kngj, 0), data_arr)
        delete_table(oxxtd__kngj)
        delete_table(xyesa__giiiv)
        return axdgk__rmaja
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    hymlv__lwtf = len(data.types)
    map__wmqsh = [('out' + str(i)) for i in range(hymlv__lwtf)]
    ifi__nlwoc = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    bla__vcebz = ['isna(data[{}], i)'.format(i) for i in ifi__nlwoc]
    dccrs__aqyp = 'not ({})'.format(' or '.join(bla__vcebz))
    if not is_overload_none(thresh):
        dccrs__aqyp = '(({}) <= ({}) - thresh)'.format(' + '.join(
            bla__vcebz), hymlv__lwtf - 1)
    elif how == 'all':
        dccrs__aqyp = 'not ({})'.format(' and '.join(bla__vcebz))
    wal__jdl = 'def _dropna_imp(data, how, thresh, subset):\n'
    wal__jdl += '  old_len = len(data[0])\n'
    wal__jdl += '  new_len = 0\n'
    wal__jdl += '  for i in range(old_len):\n'
    wal__jdl += '    if {}:\n'.format(dccrs__aqyp)
    wal__jdl += '      new_len += 1\n'
    for i, out in enumerate(map__wmqsh):
        if isinstance(data[i], bodo.CategoricalArrayType):
            wal__jdl += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            wal__jdl += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    wal__jdl += '  curr_ind = 0\n'
    wal__jdl += '  for i in range(old_len):\n'
    wal__jdl += '    if {}:\n'.format(dccrs__aqyp)
    for i in range(hymlv__lwtf):
        wal__jdl += '      if isna(data[{}], i):\n'.format(i)
        wal__jdl += '        setna({}, curr_ind)\n'.format(map__wmqsh[i])
        wal__jdl += '      else:\n'
        wal__jdl += '        {}[curr_ind] = data[{}][i]\n'.format(map__wmqsh
            [i], i)
    wal__jdl += '      curr_ind += 1\n'
    wal__jdl += '  return {}\n'.format(', '.join(map__wmqsh))
    klaeu__yjmr = {}
    vfxv__vowcq = {'t{}'.format(i): bdn__obko for i, bdn__obko in enumerate
        (data.types)}
    vfxv__vowcq.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(wal__jdl, vfxv__vowcq, klaeu__yjmr)
    ulr__vdbey = klaeu__yjmr['_dropna_imp']
    return ulr__vdbey


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        fpm__iqsow = arr.dtype
        skho__hgkvs = fpm__iqsow.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            vlwu__yqho = init_nested_counts(skho__hgkvs)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                vlwu__yqho = add_nested_counts(vlwu__yqho, val[ind])
            axdgk__rmaja = bodo.utils.utils.alloc_type(n, fpm__iqsow,
                vlwu__yqho)
            for jap__tvxyc in range(n):
                if bodo.libs.array_kernels.isna(arr, jap__tvxyc):
                    setna(axdgk__rmaja, jap__tvxyc)
                    continue
                val = arr[jap__tvxyc]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(axdgk__rmaja, jap__tvxyc)
                    continue
                axdgk__rmaja[jap__tvxyc] = val[ind]
            return axdgk__rmaja
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    xboxz__znf = _to_readonly(arr_types.types[0])
    return all(isinstance(bdn__obko, CategoricalArrayType) and _to_readonly
        (bdn__obko) == xboxz__znf for bdn__obko in arr_types.types)


def concat(arr_list):
    return pd.concat(arr_list)


@overload(concat, no_unliteral=True)
def concat_overload(arr_list):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(arr_list.
        dtype, 'bodo.concat()')
    if isinstance(arr_list, bodo.NullableTupleType):
        return lambda arr_list: bodo.libs.array_kernels.concat(arr_list._data)
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, ArrayItemArrayType):
        ggv__ytyhr = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            sfubx__udfg = 0
            vmspa__bqcbs = []
            for A in arr_list:
                nan__kylts = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                vmspa__bqcbs.append(bodo.libs.array_item_arr_ext.get_data(A))
                sfubx__udfg += nan__kylts
            iue__yfslz = np.empty(sfubx__udfg + 1, offset_type)
            jrbf__abjkr = bodo.libs.array_kernels.concat(vmspa__bqcbs)
            ovzgu__uvb = np.empty(sfubx__udfg + 7 >> 3, np.uint8)
            mvwrc__sazrr = 0
            gqoks__djnrh = 0
            for A in arr_list:
                rch__akkhb = bodo.libs.array_item_arr_ext.get_offsets(A)
                hjpj__cnj = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                nan__kylts = len(A)
                fkxrd__jghy = rch__akkhb[nan__kylts]
                for i in range(nan__kylts):
                    iue__yfslz[i + mvwrc__sazrr] = rch__akkhb[i] + gqoks__djnrh
                    yqqch__opr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        hjpj__cnj, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ovzgu__uvb, i +
                        mvwrc__sazrr, yqqch__opr)
                mvwrc__sazrr += nan__kylts
                gqoks__djnrh += fkxrd__jghy
            iue__yfslz[mvwrc__sazrr] = gqoks__djnrh
            axdgk__rmaja = bodo.libs.array_item_arr_ext.init_array_item_array(
                sfubx__udfg, jrbf__abjkr, iue__yfslz, ovzgu__uvb)
            return axdgk__rmaja
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        vxf__eopwg = arr_list.dtype.names
        wal__jdl = 'def struct_array_concat_impl(arr_list):\n'
        wal__jdl += f'    n_all = 0\n'
        for i in range(len(vxf__eopwg)):
            wal__jdl += f'    concat_list{i} = []\n'
        wal__jdl += '    for A in arr_list:\n'
        wal__jdl += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(vxf__eopwg)):
            wal__jdl += f'        concat_list{i}.append(data_tuple[{i}])\n'
        wal__jdl += '        n_all += len(A)\n'
        wal__jdl += '    n_bytes = (n_all + 7) >> 3\n'
        wal__jdl += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        wal__jdl += '    curr_bit = 0\n'
        wal__jdl += '    for A in arr_list:\n'
        wal__jdl += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        wal__jdl += '        for j in range(len(A)):\n'
        wal__jdl += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        wal__jdl += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        wal__jdl += '            curr_bit += 1\n'
        wal__jdl += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        ljdjy__qhez = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(vxf__eopwg))])
        wal__jdl += f'        ({ljdjy__qhez},),\n'
        wal__jdl += '        new_mask,\n'
        wal__jdl += f'        {vxf__eopwg},\n'
        wal__jdl += '    )\n'
        klaeu__yjmr = {}
        exec(wal__jdl, {'bodo': bodo, 'np': np}, klaeu__yjmr)
        return klaeu__yjmr['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            aqf__uzc = 0
            for A in arr_list:
                aqf__uzc += len(A)
            cflwe__goukl = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(aqf__uzc))
            ynrk__shrj = 0
            for A in arr_list:
                for i in range(len(A)):
                    cflwe__goukl._data[i + ynrk__shrj] = A._data[i]
                    yqqch__opr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cflwe__goukl.
                        _null_bitmap, i + ynrk__shrj, yqqch__opr)
                ynrk__shrj += len(A)
            return cflwe__goukl
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            aqf__uzc = 0
            for A in arr_list:
                aqf__uzc += len(A)
            cflwe__goukl = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(aqf__uzc))
            ynrk__shrj = 0
            for A in arr_list:
                for i in range(len(A)):
                    cflwe__goukl._days_data[i + ynrk__shrj] = A._days_data[i]
                    cflwe__goukl._seconds_data[i + ynrk__shrj
                        ] = A._seconds_data[i]
                    cflwe__goukl._microseconds_data[i + ynrk__shrj
                        ] = A._microseconds_data[i]
                    yqqch__opr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cflwe__goukl.
                        _null_bitmap, i + ynrk__shrj, yqqch__opr)
                ynrk__shrj += len(A)
            return cflwe__goukl
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        qacq__jeen = arr_list.dtype.precision
        zxbv__kjnn = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            aqf__uzc = 0
            for A in arr_list:
                aqf__uzc += len(A)
            cflwe__goukl = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                aqf__uzc, qacq__jeen, zxbv__kjnn)
            ynrk__shrj = 0
            for A in arr_list:
                for i in range(len(A)):
                    cflwe__goukl._data[i + ynrk__shrj] = A._data[i]
                    yqqch__opr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(cflwe__goukl.
                        _null_bitmap, i + ynrk__shrj, yqqch__opr)
                ynrk__shrj += len(A)
            return cflwe__goukl
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        bdn__obko) for bdn__obko in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            fcvzs__ctqz = arr_list.types[0]
        else:
            fcvzs__ctqz = arr_list.dtype
        fcvzs__ctqz = to_str_arr_if_dict_array(fcvzs__ctqz)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            hwko__iocc = 0
            tnpo__eih = 0
            for A in arr_list:
                arr = A
                hwko__iocc += len(arr)
                tnpo__eih += bodo.libs.str_arr_ext.num_total_chars(arr)
            axdgk__rmaja = bodo.utils.utils.alloc_type(hwko__iocc,
                fcvzs__ctqz, (tnpo__eih,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(axdgk__rmaja, -1)
            vdnmb__qxbny = 0
            vjest__ovt = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(axdgk__rmaja,
                    arr, vdnmb__qxbny, vjest__ovt)
                vdnmb__qxbny += len(arr)
                vjest__ovt += bodo.libs.str_arr_ext.num_total_chars(arr)
            return axdgk__rmaja
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(bdn__obko.dtype, types.Integer) for
        bdn__obko in arr_list.types) and any(isinstance(bdn__obko,
        IntegerArrayType) for bdn__obko in arr_list.types):

        def impl_int_arr_list(arr_list):
            mst__ioxh = convert_to_nullable_tup(arr_list)
            rylz__luxn = []
            pvc__lzsd = 0
            for A in mst__ioxh:
                rylz__luxn.append(A._data)
                pvc__lzsd += len(A)
            jrbf__abjkr = bodo.libs.array_kernels.concat(rylz__luxn)
            uak__lkx = pvc__lzsd + 7 >> 3
            esnd__xjzor = np.empty(uak__lkx, np.uint8)
            mud__ael = 0
            for A in mst__ioxh:
                vqqbr__plzcy = A._null_bitmap
                for jap__tvxyc in range(len(A)):
                    yqqch__opr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        vqqbr__plzcy, jap__tvxyc)
                    bodo.libs.int_arr_ext.set_bit_to_arr(esnd__xjzor,
                        mud__ael, yqqch__opr)
                    mud__ael += 1
            return bodo.libs.int_arr_ext.init_integer_array(jrbf__abjkr,
                esnd__xjzor)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(bdn__obko.dtype == types.bool_ for bdn__obko in
        arr_list.types) and any(bdn__obko == boolean_array for bdn__obko in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            mst__ioxh = convert_to_nullable_tup(arr_list)
            rylz__luxn = []
            pvc__lzsd = 0
            for A in mst__ioxh:
                rylz__luxn.append(A._data)
                pvc__lzsd += len(A)
            jrbf__abjkr = bodo.libs.array_kernels.concat(rylz__luxn)
            uak__lkx = pvc__lzsd + 7 >> 3
            esnd__xjzor = np.empty(uak__lkx, np.uint8)
            mud__ael = 0
            for A in mst__ioxh:
                vqqbr__plzcy = A._null_bitmap
                for jap__tvxyc in range(len(A)):
                    yqqch__opr = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        vqqbr__plzcy, jap__tvxyc)
                    bodo.libs.int_arr_ext.set_bit_to_arr(esnd__xjzor,
                        mud__ael, yqqch__opr)
                    mud__ael += 1
            return bodo.libs.bool_arr_ext.init_bool_array(jrbf__abjkr,
                esnd__xjzor)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            bkrj__ihsh = []
            for A in arr_list:
                bkrj__ihsh.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                bkrj__ihsh), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        lszuk__jrbmn = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        wal__jdl = 'def impl(arr_list):\n'
        wal__jdl += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({lszuk__jrbmn},)), arr_list[0].dtype)
"""
        uzv__pokku = {}
        exec(wal__jdl, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, uzv__pokku)
        return uzv__pokku['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            pvc__lzsd = 0
            for A in arr_list:
                pvc__lzsd += len(A)
            axdgk__rmaja = np.empty(pvc__lzsd, dtype)
            osn__znbx = 0
            for A in arr_list:
                n = len(A)
                axdgk__rmaja[osn__znbx:osn__znbx + n] = A
                osn__znbx += n
            return axdgk__rmaja
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(bdn__obko,
        (types.Array, IntegerArrayType)) and isinstance(bdn__obko.dtype,
        types.Integer) for bdn__obko in arr_list.types) and any(isinstance(
        bdn__obko, types.Array) and isinstance(bdn__obko.dtype, types.Float
        ) for bdn__obko in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            czy__iyyip = []
            for A in arr_list:
                czy__iyyip.append(A._data)
            fxw__cygyj = bodo.libs.array_kernels.concat(czy__iyyip)
            uvzoq__hxghc = bodo.libs.map_arr_ext.init_map_arr(fxw__cygyj)
            return uvzoq__hxghc
        return impl_map_arr_list
    for jlthu__hwoiz in arr_list:
        if not isinstance(jlthu__hwoiz, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(bdn__obko.astype(np.float64) for bdn__obko in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    udapn__vonv = len(arr_tup.types)
    wal__jdl = 'def f(arr_tup):\n'
    wal__jdl += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        udapn__vonv)), ',' if udapn__vonv == 1 else '')
    klaeu__yjmr = {}
    exec(wal__jdl, {'np': np}, klaeu__yjmr)
    snuw__tva = klaeu__yjmr['f']
    return snuw__tva


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    udapn__vonv = len(arr_tup.types)
    iinjo__txqxo = find_common_np_dtype(arr_tup.types)
    skho__hgkvs = None
    psokt__umrv = ''
    if isinstance(iinjo__txqxo, types.Integer):
        skho__hgkvs = bodo.libs.int_arr_ext.IntDtype(iinjo__txqxo)
        psokt__umrv = '.astype(out_dtype, False)'
    wal__jdl = 'def f(arr_tup):\n'
    wal__jdl += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, psokt__umrv) for i in range(udapn__vonv)), ',' if 
        udapn__vonv == 1 else '')
    klaeu__yjmr = {}
    exec(wal__jdl, {'bodo': bodo, 'out_dtype': skho__hgkvs}, klaeu__yjmr)
    gcvfo__rtr = klaeu__yjmr['f']
    return gcvfo__rtr


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, ejri__gabi = build_set_seen_na(A)
        return len(s) + int(not dropna and ejri__gabi)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        dcmpl__dbc = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        qqj__himm = len(dcmpl__dbc)
        return bodo.libs.distributed_api.dist_reduce(qqj__himm, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([plrd__fbuep for plrd__fbuep in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        fbur__ecoyd = np.finfo(A.dtype(1).dtype).max
    else:
        fbur__ecoyd = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        axdgk__rmaja = np.empty(n, A.dtype)
        lzu__ckste = fbur__ecoyd
        for i in range(n):
            lzu__ckste = min(lzu__ckste, A[i])
            axdgk__rmaja[i] = lzu__ckste
        return axdgk__rmaja
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        fbur__ecoyd = np.finfo(A.dtype(1).dtype).min
    else:
        fbur__ecoyd = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        axdgk__rmaja = np.empty(n, A.dtype)
        lzu__ckste = fbur__ecoyd
        for i in range(n):
            lzu__ckste = max(lzu__ckste, A[i])
            axdgk__rmaja[i] = lzu__ckste
        return axdgk__rmaja
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        fokvx__zbt = arr_info_list_to_table([array_to_info(A)])
        hubvr__trs = 1
        ysbz__rwrr = 0
        oxxtd__kngj = drop_duplicates_table(fokvx__zbt, parallel,
            hubvr__trs, ysbz__rwrr, dropna, True)
        axdgk__rmaja = info_to_array(info_from_table(oxxtd__kngj, 0), A)
        delete_table(fokvx__zbt)
        delete_table(oxxtd__kngj)
        return axdgk__rmaja
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    ggv__ytyhr = bodo.utils.typing.to_nullable_type(arr.dtype)
    mxj__qque = index_arr
    emrq__kzott = mxj__qque.dtype

    def impl(arr, index_arr):
        n = len(arr)
        vlwu__yqho = init_nested_counts(ggv__ytyhr)
        fgv__yauh = init_nested_counts(emrq__kzott)
        for i in range(n):
            utz__rofme = index_arr[i]
            if isna(arr, i):
                vlwu__yqho = (vlwu__yqho[0] + 1,) + vlwu__yqho[1:]
                fgv__yauh = add_nested_counts(fgv__yauh, utz__rofme)
                continue
            bfg__vlpfa = arr[i]
            if len(bfg__vlpfa) == 0:
                vlwu__yqho = (vlwu__yqho[0] + 1,) + vlwu__yqho[1:]
                fgv__yauh = add_nested_counts(fgv__yauh, utz__rofme)
                continue
            vlwu__yqho = add_nested_counts(vlwu__yqho, bfg__vlpfa)
            for mfpeu__stf in range(len(bfg__vlpfa)):
                fgv__yauh = add_nested_counts(fgv__yauh, utz__rofme)
        axdgk__rmaja = bodo.utils.utils.alloc_type(vlwu__yqho[0],
            ggv__ytyhr, vlwu__yqho[1:])
        fkojg__rsauk = bodo.utils.utils.alloc_type(vlwu__yqho[0], mxj__qque,
            fgv__yauh)
        gqoks__djnrh = 0
        for i in range(n):
            if isna(arr, i):
                setna(axdgk__rmaja, gqoks__djnrh)
                fkojg__rsauk[gqoks__djnrh] = index_arr[i]
                gqoks__djnrh += 1
                continue
            bfg__vlpfa = arr[i]
            fkxrd__jghy = len(bfg__vlpfa)
            if fkxrd__jghy == 0:
                setna(axdgk__rmaja, gqoks__djnrh)
                fkojg__rsauk[gqoks__djnrh] = index_arr[i]
                gqoks__djnrh += 1
                continue
            axdgk__rmaja[gqoks__djnrh:gqoks__djnrh + fkxrd__jghy] = bfg__vlpfa
            fkojg__rsauk[gqoks__djnrh:gqoks__djnrh + fkxrd__jghy] = index_arr[i
                ]
            gqoks__djnrh += fkxrd__jghy
        return axdgk__rmaja, fkojg__rsauk
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    ggv__ytyhr = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        vlwu__yqho = init_nested_counts(ggv__ytyhr)
        for i in range(n):
            if isna(arr, i):
                vlwu__yqho = (vlwu__yqho[0] + 1,) + vlwu__yqho[1:]
                taipl__qqrdn = 1
            else:
                bfg__vlpfa = arr[i]
                upjop__mgvpw = len(bfg__vlpfa)
                if upjop__mgvpw == 0:
                    vlwu__yqho = (vlwu__yqho[0] + 1,) + vlwu__yqho[1:]
                    taipl__qqrdn = 1
                    continue
                else:
                    vlwu__yqho = add_nested_counts(vlwu__yqho, bfg__vlpfa)
                    taipl__qqrdn = upjop__mgvpw
            if counts[i] != taipl__qqrdn:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        axdgk__rmaja = bodo.utils.utils.alloc_type(vlwu__yqho[0],
            ggv__ytyhr, vlwu__yqho[1:])
        gqoks__djnrh = 0
        for i in range(n):
            if isna(arr, i):
                setna(axdgk__rmaja, gqoks__djnrh)
                gqoks__djnrh += 1
                continue
            bfg__vlpfa = arr[i]
            fkxrd__jghy = len(bfg__vlpfa)
            if fkxrd__jghy == 0:
                setna(axdgk__rmaja, gqoks__djnrh)
                gqoks__djnrh += 1
                continue
            axdgk__rmaja[gqoks__djnrh:gqoks__djnrh + fkxrd__jghy] = bfg__vlpfa
            gqoks__djnrh += fkxrd__jghy
        return axdgk__rmaja
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(fzkz__lrydy) for fzkz__lrydy in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        ewfv__glhlq = 'np.empty(n, np.int64)'
        qsc__hies = 'out_arr[i] = 1'
        wthw__nwo = 'max(len(arr[i]), 1)'
    else:
        ewfv__glhlq = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        qsc__hies = 'bodo.libs.array_kernels.setna(out_arr, i)'
        wthw__nwo = 'len(arr[i])'
    wal__jdl = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {ewfv__glhlq}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {qsc__hies}
        else:
            out_arr[i] = {wthw__nwo}
    return out_arr
    """
    klaeu__yjmr = {}
    exec(wal__jdl, {'bodo': bodo, 'numba': numba, 'np': np}, klaeu__yjmr)
    impl = klaeu__yjmr['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    mxj__qque = index_arr
    emrq__kzott = mxj__qque.dtype

    def impl(arr, pat, n, index_arr):
        mvxmw__hfg = pat is not None and len(pat) > 1
        if mvxmw__hfg:
            injkd__ioshm = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        jvlr__vjp = len(arr)
        hwko__iocc = 0
        tnpo__eih = 0
        fgv__yauh = init_nested_counts(emrq__kzott)
        for i in range(jvlr__vjp):
            utz__rofme = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                hwko__iocc += 1
                fgv__yauh = add_nested_counts(fgv__yauh, utz__rofme)
                continue
            if mvxmw__hfg:
                qhtwa__yxhj = injkd__ioshm.split(arr[i], maxsplit=n)
            else:
                qhtwa__yxhj = arr[i].split(pat, n)
            hwko__iocc += len(qhtwa__yxhj)
            for s in qhtwa__yxhj:
                fgv__yauh = add_nested_counts(fgv__yauh, utz__rofme)
                tnpo__eih += bodo.libs.str_arr_ext.get_utf8_size(s)
        axdgk__rmaja = bodo.libs.str_arr_ext.pre_alloc_string_array(hwko__iocc,
            tnpo__eih)
        fkojg__rsauk = bodo.utils.utils.alloc_type(hwko__iocc, mxj__qque,
            fgv__yauh)
        tcofm__ifnt = 0
        for jap__tvxyc in range(jvlr__vjp):
            if isna(arr, jap__tvxyc):
                axdgk__rmaja[tcofm__ifnt] = ''
                bodo.libs.array_kernels.setna(axdgk__rmaja, tcofm__ifnt)
                fkojg__rsauk[tcofm__ifnt] = index_arr[jap__tvxyc]
                tcofm__ifnt += 1
                continue
            if mvxmw__hfg:
                qhtwa__yxhj = injkd__ioshm.split(arr[jap__tvxyc], maxsplit=n)
            else:
                qhtwa__yxhj = arr[jap__tvxyc].split(pat, n)
            hakp__moaz = len(qhtwa__yxhj)
            axdgk__rmaja[tcofm__ifnt:tcofm__ifnt + hakp__moaz] = qhtwa__yxhj
            fkojg__rsauk[tcofm__ifnt:tcofm__ifnt + hakp__moaz] = index_arr[
                jap__tvxyc]
            tcofm__ifnt += hakp__moaz
        return axdgk__rmaja, fkojg__rsauk
    return impl


def gen_na_array(n, arr):
    return np.full(n, np.nan)


@overload(gen_na_array, no_unliteral=True)
def overload_gen_na_array(n, arr, use_dict_arr=False):
    if isinstance(arr, types.TypeRef):
        arr = arr.instance_type
    dtype = arr.dtype
    if not isinstance(arr, IntegerArrayType) and isinstance(dtype, (types.
        Integer, types.Float)):
        dtype = dtype if isinstance(dtype, types.Float) else types.float64

        def impl_float(n, arr, use_dict_arr=False):
            numba.parfors.parfor.init_prange()
            axdgk__rmaja = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                axdgk__rmaja[i] = np.nan
            return axdgk__rmaja
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            nxinx__yps = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            xyem__qdv = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(xyem__qdv, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(nxinx__yps,
                xyem__qdv, True)
        return impl_dict
    xonw__slgfs = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        axdgk__rmaja = bodo.utils.utils.alloc_type(n, xonw__slgfs, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(axdgk__rmaja, i)
        return axdgk__rmaja
    return impl


def gen_na_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_gen_na_array = (
    gen_na_array_equiv)


def resize_and_copy(A, new_len):
    return A


@overload(resize_and_copy, no_unliteral=True)
def overload_resize_and_copy(A, old_size, new_len):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.resize_and_copy()')
    pogs__gpxwa = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            axdgk__rmaja = bodo.utils.utils.alloc_type(new_len, pogs__gpxwa)
            bodo.libs.str_arr_ext.str_copy_ptr(axdgk__rmaja.ctypes, 0, A.
                ctypes, old_size)
            return axdgk__rmaja
        return impl_char

    def impl(A, old_size, new_len):
        axdgk__rmaja = bodo.utils.utils.alloc_type(new_len, pogs__gpxwa, (-1,))
        axdgk__rmaja[:old_size] = A[:old_size]
        return axdgk__rmaja
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    hbpl__xmgg = math.ceil((stop - start) / step)
    return int(max(hbpl__xmgg, 0))


def calc_nitems_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    if guard(find_const, self.func_ir, args[0]) == 0 and guard(find_const,
        self.func_ir, args[2]) == 1:
        return ArrayAnalysis.AnalyzeResult(shape=args[1], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_array_kernels_calc_nitems = (
    calc_nitems_equiv)


def arange_parallel_impl(return_type, *args):
    dtype = as_dtype(return_type.dtype)

    def arange_1(stop):
        return np.arange(0, stop, 1, dtype)

    def arange_2(start, stop):
        return np.arange(start, stop, 1, dtype)

    def arange_3(start, stop, step):
        return np.arange(start, stop, step, dtype)
    if any(isinstance(plrd__fbuep, types.Complex) for plrd__fbuep in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            easju__cxq = (stop - start) / step
            hbpl__xmgg = math.ceil(easju__cxq.real)
            otbta__gku = math.ceil(easju__cxq.imag)
            lrt__bvxz = int(max(min(otbta__gku, hbpl__xmgg), 0))
            arr = np.empty(lrt__bvxz, dtype)
            for i in numba.parfors.parfor.internal_prange(lrt__bvxz):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            lrt__bvxz = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(lrt__bvxz, dtype)
            for i in numba.parfors.parfor.internal_prange(lrt__bvxz):
                arr[i] = start + i * step
            return arr
    if len(args) == 1:
        return arange_1
    elif len(args) == 2:
        return arange_2
    elif len(args) == 3:
        return arange_3
    elif len(args) == 4:
        return arange_4
    else:
        raise BodoError('parallel arange with types {}'.format(args))


if bodo.numba_compat._check_numba_change:
    lines = inspect.getsource(numba.parfors.parfor.arange_parallel_impl)
    if hashlib.sha256(lines.encode()).hexdigest(
        ) != 'c72b0390b4f3e52dcc5426bd42c6b55ff96bae5a425381900985d36e7527a4bd':
        warnings.warn('numba.parfors.parfor.arange_parallel_impl has changed')
numba.parfors.parfor.swap_functions_map['arange', 'numpy'
    ] = arange_parallel_impl


def sort(arr, ascending, inplace):
    return np.sort(arr)


@overload(sort, no_unliteral=True)
def overload_sort(arr, ascending, inplace):

    def impl(arr, ascending, inplace):
        n = len(arr)
        data = np.arange(n),
        ziaz__qirog = arr,
        if not inplace:
            ziaz__qirog = arr.copy(),
        vddv__aezma = bodo.libs.str_arr_ext.to_list_if_immutable_arr(
            ziaz__qirog)
        xlr__saown = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(vddv__aezma, 0, n, xlr__saown)
        if not ascending:
            bodo.libs.timsort.reverseRange(vddv__aezma, 0, n, xlr__saown)
        bodo.libs.str_arr_ext.cp_str_list_to_array(ziaz__qirog, vddv__aezma)
        return ziaz__qirog[0]
    return impl


def overload_array_max(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).max()
        return impl


overload(np.max, inline='always', no_unliteral=True)(overload_array_max)
overload(max, inline='always', no_unliteral=True)(overload_array_max)


def overload_array_min(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).min()
        return impl


overload(np.min, inline='always', no_unliteral=True)(overload_array_min)
overload(min, inline='always', no_unliteral=True)(overload_array_min)


def overload_array_sum(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).sum()
    return impl


overload(np.sum, inline='always', no_unliteral=True)(overload_array_sum)
overload(sum, inline='always', no_unliteral=True)(overload_array_sum)


@overload(np.prod, inline='always', no_unliteral=True)
def overload_array_prod(A):
    if isinstance(A, IntegerArrayType) or A == boolean_array:

        def impl(A):
            return pd.Series(A).prod()
    return impl


def nonzero(arr):
    return arr,


@overload(nonzero, no_unliteral=True)
def nonzero_overload(A, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.nonzero()')
    if not bodo.utils.utils.is_array_typ(A, False):
        return

    def impl(A, parallel=False):
        n = len(A)
        if parallel:
            offset = bodo.libs.distributed_api.dist_exscan(n, Reduce_Type.
                Sum.value)
        else:
            offset = 0
        uvzoq__hxghc = []
        for i in range(n):
            if A[i]:
                uvzoq__hxghc.append(i + offset)
        return np.array(uvzoq__hxghc, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    pogs__gpxwa = element_type(A)
    if pogs__gpxwa == types.unicode_type:
        null_value = '""'
    elif pogs__gpxwa == types.bool_:
        null_value = 'False'
    elif pogs__gpxwa == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif pogs__gpxwa == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    tcofm__ifnt = 'i'
    shel__ehth = False
    cvw__ron = get_overload_const_str(method)
    if cvw__ron in ('ffill', 'pad'):
        mui__uyehu = 'n'
        send_right = True
    elif cvw__ron in ('backfill', 'bfill'):
        mui__uyehu = 'n-1, -1, -1'
        send_right = False
        if pogs__gpxwa == types.unicode_type:
            tcofm__ifnt = '(n - 1) - i'
            shel__ehth = True
    wal__jdl = 'def impl(A, method, parallel=False):\n'
    wal__jdl += '  A = decode_if_dict_array(A)\n'
    wal__jdl += '  has_last_value = False\n'
    wal__jdl += f'  last_value = {null_value}\n'
    wal__jdl += '  if parallel:\n'
    wal__jdl += '    rank = bodo.libs.distributed_api.get_rank()\n'
    wal__jdl += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    wal__jdl += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    wal__jdl += '  n = len(A)\n'
    wal__jdl += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    wal__jdl += f'  for i in range({mui__uyehu}):\n'
    wal__jdl += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    wal__jdl += (
        f'      bodo.libs.array_kernels.setna(out_arr, {tcofm__ifnt})\n')
    wal__jdl += '      continue\n'
    wal__jdl += '    s = A[i]\n'
    wal__jdl += '    if bodo.libs.array_kernels.isna(A, i):\n'
    wal__jdl += '      s = last_value\n'
    wal__jdl += f'    out_arr[{tcofm__ifnt}] = s\n'
    wal__jdl += '    last_value = s\n'
    wal__jdl += '    has_last_value = True\n'
    if shel__ehth:
        wal__jdl += '  return out_arr[::-1]\n'
    else:
        wal__jdl += '  return out_arr\n'
    lvau__nzhwb = {}
    exec(wal__jdl, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, lvau__nzhwb)
    impl = lvau__nzhwb['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        udkw__cpex = 0
        qnsq__xvf = n_pes - 1
        iqpnj__gccu = np.int32(rank + 1)
        vigs__asy = np.int32(rank - 1)
        zwqfc__yssur = len(in_arr) - 1
        acttk__alzkk = -1
        gaw__ygeaw = -1
    else:
        udkw__cpex = n_pes - 1
        qnsq__xvf = 0
        iqpnj__gccu = np.int32(rank - 1)
        vigs__asy = np.int32(rank + 1)
        zwqfc__yssur = 0
        acttk__alzkk = len(in_arr)
        gaw__ygeaw = 1
    scf__ghdk = np.int32(bodo.hiframes.rolling.comm_border_tag)
    fdf__kzrc = np.empty(1, dtype=np.bool_)
    hguea__xwzjt = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    ong__rkl = np.empty(1, dtype=np.bool_)
    wicz__xtrz = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    wcmbp__xilf = False
    dio__adph = null_value
    for i in range(zwqfc__yssur, acttk__alzkk, gaw__ygeaw):
        if not isna(in_arr, i):
            wcmbp__xilf = True
            dio__adph = in_arr[i]
            break
    if rank != udkw__cpex:
        itf__uqhf = bodo.libs.distributed_api.irecv(fdf__kzrc, 1, vigs__asy,
            scf__ghdk, True)
        bodo.libs.distributed_api.wait(itf__uqhf, True)
        pzb__bsaa = bodo.libs.distributed_api.irecv(hguea__xwzjt, 1,
            vigs__asy, scf__ghdk, True)
        bodo.libs.distributed_api.wait(pzb__bsaa, True)
        iakn__ypcbw = fdf__kzrc[0]
        tkxpk__joat = hguea__xwzjt[0]
    else:
        iakn__ypcbw = False
        tkxpk__joat = null_value
    if wcmbp__xilf:
        ong__rkl[0] = wcmbp__xilf
        wicz__xtrz[0] = dio__adph
    else:
        ong__rkl[0] = iakn__ypcbw
        wicz__xtrz[0] = tkxpk__joat
    if rank != qnsq__xvf:
        kjts__mbkm = bodo.libs.distributed_api.isend(ong__rkl, 1,
            iqpnj__gccu, scf__ghdk, True)
        nftc__vmf = bodo.libs.distributed_api.isend(wicz__xtrz, 1,
            iqpnj__gccu, scf__ghdk, True)
    return iakn__ypcbw, tkxpk__joat


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    lmb__swjqz = {'axis': axis, 'kind': kind, 'order': order}
    gpkd__mdv = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', lmb__swjqz, gpkd__mdv, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    pogs__gpxwa = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            jvlr__vjp = len(A)
            axdgk__rmaja = bodo.utils.utils.alloc_type(jvlr__vjp * repeats,
                pogs__gpxwa, (-1,))
            for i in range(jvlr__vjp):
                tcofm__ifnt = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for jap__tvxyc in range(repeats):
                        bodo.libs.array_kernels.setna(axdgk__rmaja, 
                            tcofm__ifnt + jap__tvxyc)
                else:
                    axdgk__rmaja[tcofm__ifnt:tcofm__ifnt + repeats] = A[i]
            return axdgk__rmaja
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        jvlr__vjp = len(A)
        axdgk__rmaja = bodo.utils.utils.alloc_type(repeats.sum(),
            pogs__gpxwa, (-1,))
        tcofm__ifnt = 0
        for i in range(jvlr__vjp):
            pyy__htyg = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for jap__tvxyc in range(pyy__htyg):
                    bodo.libs.array_kernels.setna(axdgk__rmaja, tcofm__ifnt +
                        jap__tvxyc)
            else:
                axdgk__rmaja[tcofm__ifnt:tcofm__ifnt + pyy__htyg] = A[i]
            tcofm__ifnt += pyy__htyg
        return axdgk__rmaja
    return impl_arr


@overload(np.repeat, inline='always', no_unliteral=True)
def np_repeat(A, repeats):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    if not isinstance(repeats, types.Integer):
        raise BodoError(
            'Only integer type supported for repeats in np.repeat()')

    def impl(A, repeats):
        return bodo.libs.array_kernels.repeat_kernel(A, repeats)
    return impl


@numba.generated_jit
def repeat_like(A, dist_like_arr):
    if not bodo.utils.utils.is_array_typ(A, False
        ) or not bodo.utils.utils.is_array_typ(dist_like_arr, False):
        raise BodoError('Both A and dist_like_arr must be array-like.')

    def impl(A, dist_like_arr):
        return bodo.libs.array_kernels.repeat_kernel(A, len(dist_like_arr))
    return impl


@overload(np.unique, inline='always', no_unliteral=True)
def np_unique(A):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return

    def impl(A):
        jhk__higs = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(jhk__higs, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        rmxuw__xnv = bodo.libs.array_kernels.concat([A1, A2])
        gnb__aknnh = bodo.libs.array_kernels.unique(rmxuw__xnv)
        return pd.Series(gnb__aknnh).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    lmb__swjqz = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    gpkd__mdv = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', lmb__swjqz, gpkd__mdv, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        tcx__nbreh = bodo.libs.array_kernels.unique(A1)
        klug__gou = bodo.libs.array_kernels.unique(A2)
        rmxuw__xnv = bodo.libs.array_kernels.concat([tcx__nbreh, klug__gou])
        qoac__htc = pd.Series(rmxuw__xnv).sort_values().values
        return slice_array_intersect1d(qoac__htc)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    ktt__upg = arr[1:] == arr[:-1]
    return arr[:-1][ktt__upg]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    scf__ghdk = np.int32(bodo.hiframes.rolling.comm_border_tag)
    ddn__uifvb = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        bpdd__yvk = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), scf__ghdk, True)
        bodo.libs.distributed_api.wait(bpdd__yvk, True)
    if rank == n_pes - 1:
        return None
    else:
        rrx__thfd = bodo.libs.distributed_api.irecv(ddn__uifvb, 1, np.int32
            (rank + 1), scf__ghdk, True)
        bodo.libs.distributed_api.wait(rrx__thfd, True)
        return ddn__uifvb[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    ktt__upg = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            ktt__upg[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        oul__atd = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == oul__atd:
            ktt__upg[n - 1] = True
    return ktt__upg


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    lmb__swjqz = {'assume_unique': assume_unique}
    gpkd__mdv = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', lmb__swjqz, gpkd__mdv, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        tcx__nbreh = bodo.libs.array_kernels.unique(A1)
        klug__gou = bodo.libs.array_kernels.unique(A2)
        ktt__upg = calculate_mask_setdiff1d(tcx__nbreh, klug__gou)
        return pd.Series(tcx__nbreh[ktt__upg]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    ktt__upg = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        ktt__upg &= A1 != A2[i]
    return ktt__upg


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    lmb__swjqz = {'retstep': retstep, 'axis': axis}
    gpkd__mdv = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', lmb__swjqz, gpkd__mdv, 'numpy')
    xll__qwpf = False
    if is_overload_none(dtype):
        pogs__gpxwa = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            xll__qwpf = True
        pogs__gpxwa = numba.np.numpy_support.as_dtype(dtype).type
    if xll__qwpf:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            qphvs__bpxrp = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            axdgk__rmaja = np.empty(num, pogs__gpxwa)
            for i in numba.parfors.parfor.internal_prange(num):
                axdgk__rmaja[i] = pogs__gpxwa(np.floor(start + i *
                    qphvs__bpxrp))
            return axdgk__rmaja
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            qphvs__bpxrp = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            axdgk__rmaja = np.empty(num, pogs__gpxwa)
            for i in numba.parfors.parfor.internal_prange(num):
                axdgk__rmaja[i] = pogs__gpxwa(start + i * qphvs__bpxrp)
            return axdgk__rmaja
        return impl


def np_linspace_get_stepsize(start, stop, num, endpoint):
    return 0


@overload(np_linspace_get_stepsize, no_unliteral=True)
def overload_np_linspace_get_stepsize(start, stop, num, endpoint):

    def impl(start, stop, num, endpoint):
        if num < 0:
            raise ValueError('np.linspace() Num must be >= 0')
        if endpoint:
            num -= 1
        if num > 1:
            return (stop - start) / num
        return 0
    return impl


@overload(operator.contains, no_unliteral=True)
def arr_contains(A, val):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'np.contains()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.dtype == types.
        unliteral(val)):
        return

    def impl(A, val):
        numba.parfors.parfor.init_prange()
        udapn__vonv = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                udapn__vonv += A[i] == val
        return udapn__vonv > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    lmb__swjqz = {'axis': axis, 'out': out, 'keepdims': keepdims}
    gpkd__mdv = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', lmb__swjqz, gpkd__mdv, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        udapn__vonv = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                udapn__vonv += int(bool(A[i]))
        return udapn__vonv > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    lmb__swjqz = {'axis': axis, 'out': out, 'keepdims': keepdims}
    gpkd__mdv = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', lmb__swjqz, gpkd__mdv, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        udapn__vonv = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                udapn__vonv += int(bool(A[i]))
        return udapn__vonv == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    lmb__swjqz = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    gpkd__mdv = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', lmb__swjqz, gpkd__mdv, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        koho__eeu = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            axdgk__rmaja = np.empty(n, koho__eeu)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(axdgk__rmaja, i)
                    continue
                axdgk__rmaja[i] = np_cbrt_scalar(A[i], koho__eeu)
            return axdgk__rmaja
        return impl_arr
    koho__eeu = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, koho__eeu)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    eukyd__uhwuq = x < 0
    if eukyd__uhwuq:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if eukyd__uhwuq:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    ixb__ojev = isinstance(tup, (types.BaseTuple, types.List))
    kpurg__ywu = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for jlthu__hwoiz in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                jlthu__hwoiz, 'numpy.hstack()')
            ixb__ojev = ixb__ojev and bodo.utils.utils.is_array_typ(
                jlthu__hwoiz, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        ixb__ojev = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif kpurg__ywu:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        fxct__uri = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for jlthu__hwoiz in fxct__uri.types:
            kpurg__ywu = kpurg__ywu and bodo.utils.utils.is_array_typ(
                jlthu__hwoiz, False)
    if not (ixb__ojev or kpurg__ywu):
        return
    if kpurg__ywu:

        def impl_series(tup):
            arr_tup = bodo.hiframes.pd_series_ext.get_series_data(tup)
            return bodo.libs.array_kernels.concat(arr_tup)
        return impl_series

    def impl(tup):
        return bodo.libs.array_kernels.concat(tup)
    return impl


@overload(np.random.multivariate_normal, inline='always', no_unliteral=True)
def np_random_multivariate_normal(mean, cov, size=None, check_valid='warn',
    tol=1e-08):
    lmb__swjqz = {'check_valid': check_valid, 'tol': tol}
    gpkd__mdv = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', lmb__swjqz,
        gpkd__mdv, 'numpy')
    if not isinstance(size, types.Integer):
        raise BodoError(
            'np.random.multivariate_normal() size argument is required and must be an integer'
            )
    if not (bodo.utils.utils.is_array_typ(mean, False) and mean.ndim == 1):
        raise BodoError(
            'np.random.multivariate_normal() mean must be a 1 dimensional numpy array'
            )
    if not (bodo.utils.utils.is_array_typ(cov, False) and cov.ndim == 2):
        raise BodoError(
            'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
            )

    def impl(mean, cov, size=None, check_valid='warn', tol=1e-08):
        _validate_multivar_norm(cov)
        kix__tyr = mean.shape[0]
        hyr__hheo = size, kix__tyr
        drfzi__jmbyg = np.random.standard_normal(hyr__hheo)
        cov = cov.astype(np.float64)
        btrpd__esd, s, pbjr__kkarb = np.linalg.svd(cov)
        res = np.dot(drfzi__jmbyg, np.sqrt(s).reshape(kix__tyr, 1) *
            pbjr__kkarb)
        xie__xtcgr = res + mean
        return xie__xtcgr
    return impl


def _validate_multivar_norm(cov):
    return


@overload(_validate_multivar_norm, no_unliteral=True)
def _overload_validate_multivar_norm(cov):

    def impl(cov):
        if cov.shape[0] != cov.shape[1]:
            raise ValueError(
                'np.random.multivariate_normal() cov must be a 2 dimensional square, numpy array'
                )
    return impl


def _nan_argmin(arr):
    return


@overload(_nan_argmin, no_unliteral=True)
def _overload_nan_argmin(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            numba.parfors.parfor.init_prange()
            meum__pyhn = bodo.hiframes.series_kernels._get_type_max_value(arr)
            cdbv__ioo = typing.builtins.IndexValue(-1, meum__pyhn)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                oxc__pdttz = typing.builtins.IndexValue(i, arr[i])
                cdbv__ioo = min(cdbv__ioo, oxc__pdttz)
            return cdbv__ioo.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        gchtc__onluw = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            jmz__zwyfg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            meum__pyhn = gchtc__onluw(len(arr.dtype.categories) + 1)
            cdbv__ioo = typing.builtins.IndexValue(-1, meum__pyhn)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                oxc__pdttz = typing.builtins.IndexValue(i, jmz__zwyfg[i])
                cdbv__ioo = min(cdbv__ioo, oxc__pdttz)
            return cdbv__ioo.index
        return impl_cat_arr
    return lambda arr: arr.argmin()


def _nan_argmax(arr):
    return


@overload(_nan_argmax, no_unliteral=True)
def _overload_nan_argmax(arr):
    if isinstance(arr, IntegerArrayType) or arr in [boolean_array,
        datetime_date_array_type] or arr.dtype == bodo.timedelta64ns:

        def impl_bodo_arr(arr):
            n = len(arr)
            numba.parfors.parfor.init_prange()
            meum__pyhn = bodo.hiframes.series_kernels._get_type_min_value(arr)
            cdbv__ioo = typing.builtins.IndexValue(-1, meum__pyhn)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                oxc__pdttz = typing.builtins.IndexValue(i, arr[i])
                cdbv__ioo = max(cdbv__ioo, oxc__pdttz)
            return cdbv__ioo.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        gchtc__onluw = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            n = len(arr)
            jmz__zwyfg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            meum__pyhn = gchtc__onluw(-1)
            cdbv__ioo = typing.builtins.IndexValue(-1, meum__pyhn)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                oxc__pdttz = typing.builtins.IndexValue(i, jmz__zwyfg[i])
                cdbv__ioo = max(cdbv__ioo, oxc__pdttz)
            return cdbv__ioo.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
