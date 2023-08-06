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
        vkqei__wunsu = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = vkqei__wunsu
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        vkqei__wunsu = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = vkqei__wunsu
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
            ivtx__eja = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ivtx__eja[ind + 1] = ivtx__eja[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            ivtx__eja = bodo.libs.array_item_arr_ext.get_offsets(arr)
            ivtx__eja[ind + 1] = ivtx__eja[ind]
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
    bypxo__abpw = arr_tup.count
    lsjqn__tcbir = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(bypxo__abpw):
        lsjqn__tcbir += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    lsjqn__tcbir += '  return\n'
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'setna': setna}, lzlu__wbb)
    impl = lzlu__wbb['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        eeje__nqika = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(eeje__nqika.start, eeje__nqika.stop, eeje__nqika.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        ofzpq__wveyy = 'n'
        ifkn__mjfpf = 'n_pes'
        qayyk__eug = 'min_op'
    else:
        ofzpq__wveyy = 'n-1, -1, -1'
        ifkn__mjfpf = '-1'
        qayyk__eug = 'max_op'
    lsjqn__tcbir = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {ifkn__mjfpf}
    for i in range({ofzpq__wveyy}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {qayyk__eug}))
        if possible_valid_rank != {ifkn__mjfpf}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, lzlu__wbb)
    impl = lzlu__wbb['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    weink__zigw = array_to_info(arr)
    _median_series_computation(res, weink__zigw, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(weink__zigw)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    weink__zigw = array_to_info(arr)
    _autocorr_series_computation(res, weink__zigw, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(weink__zigw)


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
    weink__zigw = array_to_info(arr)
    _compute_series_monotonicity(res, weink__zigw, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(weink__zigw)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    imk__qhhq = res[0] > 0.5
    return imk__qhhq


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        zjhs__ntul = '-'
        wfzai__vkmi = 'index_arr[0] > threshhold_date'
        ofzpq__wveyy = '1, n+1'
        itaz__kvpi = 'index_arr[-i] <= threshhold_date'
        mxj__guo = 'i - 1'
    else:
        zjhs__ntul = '+'
        wfzai__vkmi = 'index_arr[-1] < threshhold_date'
        ofzpq__wveyy = 'n'
        itaz__kvpi = 'index_arr[i] >= threshhold_date'
        mxj__guo = 'i'
    lsjqn__tcbir = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        lsjqn__tcbir += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        lsjqn__tcbir += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            lsjqn__tcbir += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            lsjqn__tcbir += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            lsjqn__tcbir += '    else:\n'
            lsjqn__tcbir += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            lsjqn__tcbir += (
                f'    threshhold_date = initial_date {zjhs__ntul} date_offset\n'
                )
    else:
        lsjqn__tcbir += (
            f'  threshhold_date = initial_date {zjhs__ntul} offset\n')
    lsjqn__tcbir += '  local_valid = 0\n'
    lsjqn__tcbir += f'  n = len(index_arr)\n'
    lsjqn__tcbir += f'  if n:\n'
    lsjqn__tcbir += f'    if {wfzai__vkmi}:\n'
    lsjqn__tcbir += '      loc_valid = n\n'
    lsjqn__tcbir += '    else:\n'
    lsjqn__tcbir += f'      for i in range({ofzpq__wveyy}):\n'
    lsjqn__tcbir += f'        if {itaz__kvpi}:\n'
    lsjqn__tcbir += f'          loc_valid = {mxj__guo}\n'
    lsjqn__tcbir += '          break\n'
    lsjqn__tcbir += '  if is_parallel:\n'
    lsjqn__tcbir += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    lsjqn__tcbir += '    return total_valid\n'
    lsjqn__tcbir += '  else:\n'
    lsjqn__tcbir += '    return loc_valid\n'
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, lzlu__wbb)
    return lzlu__wbb['impl']


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
    bog__gdxa = numba_to_c_type(sig.args[0].dtype)
    cljf__wjd = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), bog__gdxa))
    aleuh__bbit = args[0]
    cqsvc__ryal = sig.args[0]
    if isinstance(cqsvc__ryal, (IntegerArrayType, BooleanArrayType)):
        aleuh__bbit = cgutils.create_struct_proxy(cqsvc__ryal)(context,
            builder, aleuh__bbit).data
        cqsvc__ryal = types.Array(cqsvc__ryal.dtype, 1, 'C')
    assert cqsvc__ryal.ndim == 1
    arr = make_array(cqsvc__ryal)(context, builder, aleuh__bbit)
    ino__ppd = builder.extract_value(arr.shape, 0)
    vewf__dbma = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        ino__ppd, args[1], builder.load(cljf__wjd)]
    ayjt__uzotn = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    lwko__sbtdu = lir.FunctionType(lir.DoubleType(), ayjt__uzotn)
    towkn__rffq = cgutils.get_or_insert_function(builder.module,
        lwko__sbtdu, name='quantile_sequential')
    zgcmr__kqa = builder.call(towkn__rffq, vewf__dbma)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return zgcmr__kqa


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    bog__gdxa = numba_to_c_type(sig.args[0].dtype)
    cljf__wjd = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (32), bog__gdxa))
    aleuh__bbit = args[0]
    cqsvc__ryal = sig.args[0]
    if isinstance(cqsvc__ryal, (IntegerArrayType, BooleanArrayType)):
        aleuh__bbit = cgutils.create_struct_proxy(cqsvc__ryal)(context,
            builder, aleuh__bbit).data
        cqsvc__ryal = types.Array(cqsvc__ryal.dtype, 1, 'C')
    assert cqsvc__ryal.ndim == 1
    arr = make_array(cqsvc__ryal)(context, builder, aleuh__bbit)
    ino__ppd = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        zmduj__kuznw = args[2]
    else:
        zmduj__kuznw = ino__ppd
    vewf__dbma = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        ino__ppd, zmduj__kuznw, args[1], builder.load(cljf__wjd)]
    ayjt__uzotn = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        IntType(64), lir.DoubleType(), lir.IntType(32)]
    lwko__sbtdu = lir.FunctionType(lir.DoubleType(), ayjt__uzotn)
    towkn__rffq = cgutils.get_or_insert_function(builder.module,
        lwko__sbtdu, name='quantile_parallel')
    zgcmr__kqa = builder.call(towkn__rffq, vewf__dbma)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return zgcmr__kqa


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        lrw__zoayk = np.nonzero(pd.isna(arr))[0]
        rlkw__bnwuq = arr[1:] != arr[:-1]
        rlkw__bnwuq[pd.isna(rlkw__bnwuq)] = False
        glasq__btnfq = rlkw__bnwuq.astype(np.bool_)
        wmfi__lha = np.concatenate((np.array([True]), glasq__btnfq))
        if lrw__zoayk.size:
            wrlm__eqgyj, kgppq__zhv = lrw__zoayk[0], lrw__zoayk[1:]
            wmfi__lha[wrlm__eqgyj] = True
            if kgppq__zhv.size:
                wmfi__lha[kgppq__zhv] = False
                if kgppq__zhv[-1] + 1 < wmfi__lha.size:
                    wmfi__lha[kgppq__zhv[-1] + 1] = True
            elif wrlm__eqgyj + 1 < wmfi__lha.size:
                wmfi__lha[wrlm__eqgyj + 1] = True
        return wmfi__lha
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
    lsjqn__tcbir = """def impl(arr, method='average', na_option='keep', ascending=True, pct=False):
"""
    lsjqn__tcbir += '  na_idxs = pd.isna(arr)\n'
    lsjqn__tcbir += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    lsjqn__tcbir += '  nas = sum(na_idxs)\n'
    if not ascending:
        lsjqn__tcbir += '  if nas and nas < (sorter.size - 1):\n'
        lsjqn__tcbir += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        lsjqn__tcbir += '  else:\n'
        lsjqn__tcbir += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        lsjqn__tcbir += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    lsjqn__tcbir += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    lsjqn__tcbir += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        lsjqn__tcbir += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        lsjqn__tcbir += '    inv,\n'
        lsjqn__tcbir += '    new_dtype=np.float64,\n'
        lsjqn__tcbir += '    copy=True,\n'
        lsjqn__tcbir += '    nan_to_str=False,\n'
        lsjqn__tcbir += '    from_series=True,\n'
        lsjqn__tcbir += '    ) + 1\n'
    else:
        lsjqn__tcbir += '  arr = arr[sorter]\n'
        lsjqn__tcbir += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        lsjqn__tcbir += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            lsjqn__tcbir += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            lsjqn__tcbir += '    dense,\n'
            lsjqn__tcbir += '    new_dtype=np.float64,\n'
            lsjqn__tcbir += '    copy=True,\n'
            lsjqn__tcbir += '    nan_to_str=False,\n'
            lsjqn__tcbir += '    from_series=True,\n'
            lsjqn__tcbir += '  )\n'
        else:
            lsjqn__tcbir += """  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))
"""
            lsjqn__tcbir += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                lsjqn__tcbir += '  ret = count_float[dense]\n'
            elif method == 'min':
                lsjqn__tcbir += '  ret = count_float[dense - 1] + 1\n'
            else:
                lsjqn__tcbir += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                lsjqn__tcbir += '  ret[na_idxs] = -1\n'
            lsjqn__tcbir += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            lsjqn__tcbir += '  div_val = arr.size - nas\n'
        else:
            lsjqn__tcbir += '  div_val = arr.size\n'
        lsjqn__tcbir += '  for i in range(len(ret)):\n'
        lsjqn__tcbir += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        lsjqn__tcbir += '  ret[na_idxs] = np.nan\n'
    lsjqn__tcbir += '  return ret\n'
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'np': np, 'pd': pd, 'bodo': bodo}, lzlu__wbb)
    return lzlu__wbb['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    zddx__wtiwd = start
    oyy__ifj = 2 * start + 1
    wztsq__wbu = 2 * start + 2
    if oyy__ifj < n and not cmp_f(arr[oyy__ifj], arr[zddx__wtiwd]):
        zddx__wtiwd = oyy__ifj
    if wztsq__wbu < n and not cmp_f(arr[wztsq__wbu], arr[zddx__wtiwd]):
        zddx__wtiwd = wztsq__wbu
    if zddx__wtiwd != start:
        arr[start], arr[zddx__wtiwd] = arr[zddx__wtiwd], arr[start]
        ind_arr[start], ind_arr[zddx__wtiwd] = ind_arr[zddx__wtiwd], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, zddx__wtiwd, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        yumg__drka = np.empty(k, A.dtype)
        zvas__fjonq = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                yumg__drka[ind] = A[i]
                zvas__fjonq[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            yumg__drka = yumg__drka[:ind]
            zvas__fjonq = zvas__fjonq[:ind]
        return yumg__drka, zvas__fjonq, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        fbt__nbh = np.sort(A)
        pzm__mecsk = index_arr[np.argsort(A)]
        feh__ibzn = pd.Series(fbt__nbh).notna().values
        fbt__nbh = fbt__nbh[feh__ibzn]
        pzm__mecsk = pzm__mecsk[feh__ibzn]
        if is_largest:
            fbt__nbh = fbt__nbh[::-1]
            pzm__mecsk = pzm__mecsk[::-1]
        return np.ascontiguousarray(fbt__nbh), np.ascontiguousarray(pzm__mecsk)
    yumg__drka, zvas__fjonq, start = select_k_nonan(A, index_arr, m, k)
    zvas__fjonq = zvas__fjonq[yumg__drka.argsort()]
    yumg__drka.sort()
    if not is_largest:
        yumg__drka = np.ascontiguousarray(yumg__drka[::-1])
        zvas__fjonq = np.ascontiguousarray(zvas__fjonq[::-1])
    for i in range(start, m):
        if cmp_f(A[i], yumg__drka[0]):
            yumg__drka[0] = A[i]
            zvas__fjonq[0] = index_arr[i]
            min_heapify(yumg__drka, zvas__fjonq, k, 0, cmp_f)
    zvas__fjonq = zvas__fjonq[yumg__drka.argsort()]
    yumg__drka.sort()
    if is_largest:
        yumg__drka = yumg__drka[::-1]
        zvas__fjonq = zvas__fjonq[::-1]
    return np.ascontiguousarray(yumg__drka), np.ascontiguousarray(zvas__fjonq)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    qrx__glcrh = bodo.libs.distributed_api.get_rank()
    dvv__prhya, ptlli__yiams = nlargest(A, I, k, is_largest, cmp_f)
    tuez__euqdq = bodo.libs.distributed_api.gatherv(dvv__prhya)
    lds__vma = bodo.libs.distributed_api.gatherv(ptlli__yiams)
    if qrx__glcrh == MPI_ROOT:
        res, rjghz__yvxj = nlargest(tuez__euqdq, lds__vma, k, is_largest, cmp_f
            )
    else:
        res = np.empty(k, A.dtype)
        rjghz__yvxj = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(rjghz__yvxj)
    return res, rjghz__yvxj


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    rknr__egojl, ted__edzh = mat.shape
    aafl__fxqc = np.empty((ted__edzh, ted__edzh), dtype=np.float64)
    for vtrve__eklw in range(ted__edzh):
        for boj__wpkp in range(vtrve__eklw + 1):
            degjf__qacwn = 0
            emf__mkq = oytua__ndy = tjyqt__ipr = dfxln__xjsln = 0.0
            for i in range(rknr__egojl):
                if np.isfinite(mat[i, vtrve__eklw]) and np.isfinite(mat[i,
                    boj__wpkp]):
                    eoh__qbbl = mat[i, vtrve__eklw]
                    vxyb__nokf = mat[i, boj__wpkp]
                    degjf__qacwn += 1
                    tjyqt__ipr += eoh__qbbl
                    dfxln__xjsln += vxyb__nokf
            if parallel:
                degjf__qacwn = bodo.libs.distributed_api.dist_reduce(
                    degjf__qacwn, sum_op)
                tjyqt__ipr = bodo.libs.distributed_api.dist_reduce(tjyqt__ipr,
                    sum_op)
                dfxln__xjsln = bodo.libs.distributed_api.dist_reduce(
                    dfxln__xjsln, sum_op)
            if degjf__qacwn < minpv:
                aafl__fxqc[vtrve__eklw, boj__wpkp] = aafl__fxqc[boj__wpkp,
                    vtrve__eklw] = np.nan
            else:
                wuycc__hej = tjyqt__ipr / degjf__qacwn
                tglr__ozfw = dfxln__xjsln / degjf__qacwn
                tjyqt__ipr = 0.0
                for i in range(rknr__egojl):
                    if np.isfinite(mat[i, vtrve__eklw]) and np.isfinite(mat
                        [i, boj__wpkp]):
                        eoh__qbbl = mat[i, vtrve__eklw] - wuycc__hej
                        vxyb__nokf = mat[i, boj__wpkp] - tglr__ozfw
                        tjyqt__ipr += eoh__qbbl * vxyb__nokf
                        emf__mkq += eoh__qbbl * eoh__qbbl
                        oytua__ndy += vxyb__nokf * vxyb__nokf
                if parallel:
                    tjyqt__ipr = bodo.libs.distributed_api.dist_reduce(
                        tjyqt__ipr, sum_op)
                    emf__mkq = bodo.libs.distributed_api.dist_reduce(emf__mkq,
                        sum_op)
                    oytua__ndy = bodo.libs.distributed_api.dist_reduce(
                        oytua__ndy, sum_op)
                hppcd__wroc = degjf__qacwn - 1.0 if cov else sqrt(emf__mkq *
                    oytua__ndy)
                if hppcd__wroc != 0.0:
                    aafl__fxqc[vtrve__eklw, boj__wpkp] = aafl__fxqc[
                        boj__wpkp, vtrve__eklw] = tjyqt__ipr / hppcd__wroc
                else:
                    aafl__fxqc[vtrve__eklw, boj__wpkp] = aafl__fxqc[
                        boj__wpkp, vtrve__eklw] = np.nan
    return aafl__fxqc


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    tsmy__dkn = n != 1
    lsjqn__tcbir = 'def impl(data, parallel=False):\n'
    lsjqn__tcbir += '  if parallel:\n'
    bpmg__dyj = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    lsjqn__tcbir += f'    cpp_table = arr_info_list_to_table([{bpmg__dyj}])\n'
    lsjqn__tcbir += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    qdaz__psu = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    lsjqn__tcbir += f'    data = ({qdaz__psu},)\n'
    lsjqn__tcbir += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    lsjqn__tcbir += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    lsjqn__tcbir += '    bodo.libs.array.delete_table(cpp_table)\n'
    lsjqn__tcbir += '  n = len(data[0])\n'
    lsjqn__tcbir += '  out = np.empty(n, np.bool_)\n'
    lsjqn__tcbir += '  uniqs = dict()\n'
    if tsmy__dkn:
        lsjqn__tcbir += '  for i in range(n):\n'
        arfgh__cxo = ', '.join(f'data[{i}][i]' for i in range(n))
        fanb__jkpit = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        lsjqn__tcbir += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({arfgh__cxo},), ({fanb__jkpit},))
"""
        lsjqn__tcbir += '    if val in uniqs:\n'
        lsjqn__tcbir += '      out[i] = True\n'
        lsjqn__tcbir += '    else:\n'
        lsjqn__tcbir += '      out[i] = False\n'
        lsjqn__tcbir += '      uniqs[val] = 0\n'
    else:
        lsjqn__tcbir += '  data = data[0]\n'
        lsjqn__tcbir += '  hasna = False\n'
        lsjqn__tcbir += '  for i in range(n):\n'
        lsjqn__tcbir += '    if bodo.libs.array_kernels.isna(data, i):\n'
        lsjqn__tcbir += '      out[i] = hasna\n'
        lsjqn__tcbir += '      hasna = True\n'
        lsjqn__tcbir += '    else:\n'
        lsjqn__tcbir += '      val = data[i]\n'
        lsjqn__tcbir += '      if val in uniqs:\n'
        lsjqn__tcbir += '        out[i] = True\n'
        lsjqn__tcbir += '      else:\n'
        lsjqn__tcbir += '        out[i] = False\n'
        lsjqn__tcbir += '        uniqs[val] = 0\n'
    lsjqn__tcbir += '  if parallel:\n'
    lsjqn__tcbir += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    lsjqn__tcbir += '  return out\n'
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        lzlu__wbb)
    impl = lzlu__wbb['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    bypxo__abpw = len(data)
    lsjqn__tcbir = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    lsjqn__tcbir += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (bypxo__abpw))))
    lsjqn__tcbir += '  table_total = arr_info_list_to_table(info_list_total)\n'
    lsjqn__tcbir += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(bypxo__abpw))
    for uel__iqv in range(bypxo__abpw):
        lsjqn__tcbir += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(uel__iqv, uel__iqv, uel__iqv))
    lsjqn__tcbir += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(bypxo__abpw))
    lsjqn__tcbir += '  delete_table(out_table)\n'
    lsjqn__tcbir += '  delete_table(table_total)\n'
    lsjqn__tcbir += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(bypxo__abpw)))
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, lzlu__wbb)
    impl = lzlu__wbb['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    bypxo__abpw = len(data)
    lsjqn__tcbir = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    lsjqn__tcbir += ('  info_list_total = [{}, array_to_info(ind_arr)]\n'.
        format(', '.join('array_to_info(data[{}])'.format(x) for x in range
        (bypxo__abpw))))
    lsjqn__tcbir += '  table_total = arr_info_list_to_table(info_list_total)\n'
    lsjqn__tcbir += '  keep_i = 0\n'
    lsjqn__tcbir += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for uel__iqv in range(bypxo__abpw):
        lsjqn__tcbir += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(uel__iqv, uel__iqv, uel__iqv))
    lsjqn__tcbir += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(bypxo__abpw))
    lsjqn__tcbir += '  delete_table(out_table)\n'
    lsjqn__tcbir += '  delete_table(table_total)\n'
    lsjqn__tcbir += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(bypxo__abpw)))
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, lzlu__wbb)
    impl = lzlu__wbb['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        nhmzi__mvd = [array_to_info(data_arr)]
        tpeaw__ufjjz = arr_info_list_to_table(nhmzi__mvd)
        eyp__lnc = 0
        qll__xgb = drop_duplicates_table(tpeaw__ufjjz, parallel, 1,
            eyp__lnc, False, True)
        riz__hkvlv = info_to_array(info_from_table(qll__xgb, 0), data_arr)
        delete_table(qll__xgb)
        delete_table(tpeaw__ufjjz)
        return riz__hkvlv
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    bbly__mqogm = len(data.types)
    abv__pipb = [('out' + str(i)) for i in range(bbly__mqogm)]
    ouxa__jlmj = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    pui__svdjc = ['isna(data[{}], i)'.format(i) for i in ouxa__jlmj]
    gyuu__fww = 'not ({})'.format(' or '.join(pui__svdjc))
    if not is_overload_none(thresh):
        gyuu__fww = '(({}) <= ({}) - thresh)'.format(' + '.join(pui__svdjc),
            bbly__mqogm - 1)
    elif how == 'all':
        gyuu__fww = 'not ({})'.format(' and '.join(pui__svdjc))
    lsjqn__tcbir = 'def _dropna_imp(data, how, thresh, subset):\n'
    lsjqn__tcbir += '  old_len = len(data[0])\n'
    lsjqn__tcbir += '  new_len = 0\n'
    lsjqn__tcbir += '  for i in range(old_len):\n'
    lsjqn__tcbir += '    if {}:\n'.format(gyuu__fww)
    lsjqn__tcbir += '      new_len += 1\n'
    for i, out in enumerate(abv__pipb):
        if isinstance(data[i], bodo.CategoricalArrayType):
            lsjqn__tcbir += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            lsjqn__tcbir += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    lsjqn__tcbir += '  curr_ind = 0\n'
    lsjqn__tcbir += '  for i in range(old_len):\n'
    lsjqn__tcbir += '    if {}:\n'.format(gyuu__fww)
    for i in range(bbly__mqogm):
        lsjqn__tcbir += '      if isna(data[{}], i):\n'.format(i)
        lsjqn__tcbir += '        setna({}, curr_ind)\n'.format(abv__pipb[i])
        lsjqn__tcbir += '      else:\n'
        lsjqn__tcbir += '        {}[curr_ind] = data[{}][i]\n'.format(abv__pipb
            [i], i)
    lsjqn__tcbir += '      curr_ind += 1\n'
    lsjqn__tcbir += '  return {}\n'.format(', '.join(abv__pipb))
    lzlu__wbb = {}
    pws__fyst = {'t{}'.format(i): vqfw__koa for i, vqfw__koa in enumerate(
        data.types)}
    pws__fyst.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(lsjqn__tcbir, pws__fyst, lzlu__wbb)
    iezb__ain = lzlu__wbb['_dropna_imp']
    return iezb__ain


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        cqsvc__ryal = arr.dtype
        rapw__jega = cqsvc__ryal.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            phvn__kezpf = init_nested_counts(rapw__jega)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                phvn__kezpf = add_nested_counts(phvn__kezpf, val[ind])
            riz__hkvlv = bodo.utils.utils.alloc_type(n, cqsvc__ryal,
                phvn__kezpf)
            for llo__xjgx in range(n):
                if bodo.libs.array_kernels.isna(arr, llo__xjgx):
                    setna(riz__hkvlv, llo__xjgx)
                    continue
                val = arr[llo__xjgx]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(riz__hkvlv, llo__xjgx)
                    continue
                riz__hkvlv[llo__xjgx] = val[ind]
            return riz__hkvlv
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    ann__iux = _to_readonly(arr_types.types[0])
    return all(isinstance(vqfw__koa, CategoricalArrayType) and _to_readonly
        (vqfw__koa) == ann__iux for vqfw__koa in arr_types.types)


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
        rkh__igh = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            iuisd__jqx = 0
            hve__kzjgn = []
            for A in arr_list:
                wam__pmla = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                hve__kzjgn.append(bodo.libs.array_item_arr_ext.get_data(A))
                iuisd__jqx += wam__pmla
            ixyn__xajfu = np.empty(iuisd__jqx + 1, offset_type)
            vlpux__gnm = bodo.libs.array_kernels.concat(hve__kzjgn)
            uzash__bldxx = np.empty(iuisd__jqx + 7 >> 3, np.uint8)
            divlz__fonnm = 0
            xkfq__akm = 0
            for A in arr_list:
                acnp__otpmo = bodo.libs.array_item_arr_ext.get_offsets(A)
                oyhtd__zoao = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                wam__pmla = len(A)
                naps__gaau = acnp__otpmo[wam__pmla]
                for i in range(wam__pmla):
                    ixyn__xajfu[i + divlz__fonnm] = acnp__otpmo[i] + xkfq__akm
                    rma__wkcv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        oyhtd__zoao, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(uzash__bldxx, i +
                        divlz__fonnm, rma__wkcv)
                divlz__fonnm += wam__pmla
                xkfq__akm += naps__gaau
            ixyn__xajfu[divlz__fonnm] = xkfq__akm
            riz__hkvlv = bodo.libs.array_item_arr_ext.init_array_item_array(
                iuisd__jqx, vlpux__gnm, ixyn__xajfu, uzash__bldxx)
            return riz__hkvlv
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        jaoz__xufl = arr_list.dtype.names
        lsjqn__tcbir = 'def struct_array_concat_impl(arr_list):\n'
        lsjqn__tcbir += f'    n_all = 0\n'
        for i in range(len(jaoz__xufl)):
            lsjqn__tcbir += f'    concat_list{i} = []\n'
        lsjqn__tcbir += '    for A in arr_list:\n'
        lsjqn__tcbir += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(jaoz__xufl)):
            lsjqn__tcbir += f'        concat_list{i}.append(data_tuple[{i}])\n'
        lsjqn__tcbir += '        n_all += len(A)\n'
        lsjqn__tcbir += '    n_bytes = (n_all + 7) >> 3\n'
        lsjqn__tcbir += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        lsjqn__tcbir += '    curr_bit = 0\n'
        lsjqn__tcbir += '    for A in arr_list:\n'
        lsjqn__tcbir += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        lsjqn__tcbir += '        for j in range(len(A)):\n'
        lsjqn__tcbir += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        lsjqn__tcbir += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        lsjqn__tcbir += '            curr_bit += 1\n'
        lsjqn__tcbir += (
            '    return bodo.libs.struct_arr_ext.init_struct_arr(\n')
        qpigm__wkiii = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(jaoz__xufl))])
        lsjqn__tcbir += f'        ({qpigm__wkiii},),\n'
        lsjqn__tcbir += '        new_mask,\n'
        lsjqn__tcbir += f'        {jaoz__xufl},\n'
        lsjqn__tcbir += '    )\n'
        lzlu__wbb = {}
        exec(lsjqn__tcbir, {'bodo': bodo, 'np': np}, lzlu__wbb)
        return lzlu__wbb['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            iajk__usctr = 0
            for A in arr_list:
                iajk__usctr += len(A)
            fqu__yoh = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(iajk__usctr))
            iawig__aql = 0
            for A in arr_list:
                for i in range(len(A)):
                    fqu__yoh._data[i + iawig__aql] = A._data[i]
                    rma__wkcv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(fqu__yoh.
                        _null_bitmap, i + iawig__aql, rma__wkcv)
                iawig__aql += len(A)
            return fqu__yoh
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            iajk__usctr = 0
            for A in arr_list:
                iajk__usctr += len(A)
            fqu__yoh = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(iajk__usctr))
            iawig__aql = 0
            for A in arr_list:
                for i in range(len(A)):
                    fqu__yoh._days_data[i + iawig__aql] = A._days_data[i]
                    fqu__yoh._seconds_data[i + iawig__aql] = A._seconds_data[i]
                    fqu__yoh._microseconds_data[i + iawig__aql
                        ] = A._microseconds_data[i]
                    rma__wkcv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(fqu__yoh.
                        _null_bitmap, i + iawig__aql, rma__wkcv)
                iawig__aql += len(A)
            return fqu__yoh
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        nurzc__whuj = arr_list.dtype.precision
        wzl__zfmxz = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            iajk__usctr = 0
            for A in arr_list:
                iajk__usctr += len(A)
            fqu__yoh = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                iajk__usctr, nurzc__whuj, wzl__zfmxz)
            iawig__aql = 0
            for A in arr_list:
                for i in range(len(A)):
                    fqu__yoh._data[i + iawig__aql] = A._data[i]
                    rma__wkcv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(fqu__yoh.
                        _null_bitmap, i + iawig__aql, rma__wkcv)
                iawig__aql += len(A)
            return fqu__yoh
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        vqfw__koa) for vqfw__koa in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            zjmv__jaovt = arr_list.types[0]
        else:
            zjmv__jaovt = arr_list.dtype
        zjmv__jaovt = to_str_arr_if_dict_array(zjmv__jaovt)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            pxoja__asu = 0
            jqihm__smpq = 0
            for A in arr_list:
                arr = A
                pxoja__asu += len(arr)
                jqihm__smpq += bodo.libs.str_arr_ext.num_total_chars(arr)
            riz__hkvlv = bodo.utils.utils.alloc_type(pxoja__asu,
                zjmv__jaovt, (jqihm__smpq,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(riz__hkvlv, -1)
            hxbtt__aepxt = 0
            slvf__czj = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(riz__hkvlv,
                    arr, hxbtt__aepxt, slvf__czj)
                hxbtt__aepxt += len(arr)
                slvf__czj += bodo.libs.str_arr_ext.num_total_chars(arr)
            return riz__hkvlv
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(vqfw__koa.dtype, types.Integer) for
        vqfw__koa in arr_list.types) and any(isinstance(vqfw__koa,
        IntegerArrayType) for vqfw__koa in arr_list.types):

        def impl_int_arr_list(arr_list):
            ddidz__dgk = convert_to_nullable_tup(arr_list)
            ith__bhntv = []
            zyhe__yjqlo = 0
            for A in ddidz__dgk:
                ith__bhntv.append(A._data)
                zyhe__yjqlo += len(A)
            vlpux__gnm = bodo.libs.array_kernels.concat(ith__bhntv)
            wchv__ozir = zyhe__yjqlo + 7 >> 3
            tqrbs__egekd = np.empty(wchv__ozir, np.uint8)
            pnr__aylaz = 0
            for A in ddidz__dgk:
                zhrqe__cvoy = A._null_bitmap
                for llo__xjgx in range(len(A)):
                    rma__wkcv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        zhrqe__cvoy, llo__xjgx)
                    bodo.libs.int_arr_ext.set_bit_to_arr(tqrbs__egekd,
                        pnr__aylaz, rma__wkcv)
                    pnr__aylaz += 1
            return bodo.libs.int_arr_ext.init_integer_array(vlpux__gnm,
                tqrbs__egekd)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(vqfw__koa.dtype == types.bool_ for vqfw__koa in
        arr_list.types) and any(vqfw__koa == boolean_array for vqfw__koa in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            ddidz__dgk = convert_to_nullable_tup(arr_list)
            ith__bhntv = []
            zyhe__yjqlo = 0
            for A in ddidz__dgk:
                ith__bhntv.append(A._data)
                zyhe__yjqlo += len(A)
            vlpux__gnm = bodo.libs.array_kernels.concat(ith__bhntv)
            wchv__ozir = zyhe__yjqlo + 7 >> 3
            tqrbs__egekd = np.empty(wchv__ozir, np.uint8)
            pnr__aylaz = 0
            for A in ddidz__dgk:
                zhrqe__cvoy = A._null_bitmap
                for llo__xjgx in range(len(A)):
                    rma__wkcv = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        zhrqe__cvoy, llo__xjgx)
                    bodo.libs.int_arr_ext.set_bit_to_arr(tqrbs__egekd,
                        pnr__aylaz, rma__wkcv)
                    pnr__aylaz += 1
            return bodo.libs.bool_arr_ext.init_bool_array(vlpux__gnm,
                tqrbs__egekd)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            xzuib__cqpz = []
            for A in arr_list:
                xzuib__cqpz.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                xzuib__cqpz), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        uuct__jquxj = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        lsjqn__tcbir = 'def impl(arr_list):\n'
        lsjqn__tcbir += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({uuct__jquxj},)), arr_list[0].dtype)
"""
        ybr__oubo = {}
        exec(lsjqn__tcbir, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, ybr__oubo)
        return ybr__oubo['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            zyhe__yjqlo = 0
            for A in arr_list:
                zyhe__yjqlo += len(A)
            riz__hkvlv = np.empty(zyhe__yjqlo, dtype)
            ywdb__jrroc = 0
            for A in arr_list:
                n = len(A)
                riz__hkvlv[ywdb__jrroc:ywdb__jrroc + n] = A
                ywdb__jrroc += n
            return riz__hkvlv
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(vqfw__koa,
        (types.Array, IntegerArrayType)) and isinstance(vqfw__koa.dtype,
        types.Integer) for vqfw__koa in arr_list.types) and any(isinstance(
        vqfw__koa, types.Array) and isinstance(vqfw__koa.dtype, types.Float
        ) for vqfw__koa in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            wyr__hum = []
            for A in arr_list:
                wyr__hum.append(A._data)
            ddiwb__lpw = bodo.libs.array_kernels.concat(wyr__hum)
            aafl__fxqc = bodo.libs.map_arr_ext.init_map_arr(ddiwb__lpw)
            return aafl__fxqc
        return impl_map_arr_list
    for dkdl__vjr in arr_list:
        if not isinstance(dkdl__vjr, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(vqfw__koa.astype(np.float64) for vqfw__koa in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    bypxo__abpw = len(arr_tup.types)
    lsjqn__tcbir = 'def f(arr_tup):\n'
    lsjqn__tcbir += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        bypxo__abpw)), ',' if bypxo__abpw == 1 else '')
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'np': np}, lzlu__wbb)
    xpbho__vdcpk = lzlu__wbb['f']
    return xpbho__vdcpk


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    bypxo__abpw = len(arr_tup.types)
    sdt__azzg = find_common_np_dtype(arr_tup.types)
    rapw__jega = None
    ujtm__harq = ''
    if isinstance(sdt__azzg, types.Integer):
        rapw__jega = bodo.libs.int_arr_ext.IntDtype(sdt__azzg)
        ujtm__harq = '.astype(out_dtype, False)'
    lsjqn__tcbir = 'def f(arr_tup):\n'
    lsjqn__tcbir += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, ujtm__harq) for i in range(bypxo__abpw)), ',' if 
        bypxo__abpw == 1 else '')
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'bodo': bodo, 'out_dtype': rapw__jega}, lzlu__wbb)
    dqsb__rxmp = lzlu__wbb['f']
    return dqsb__rxmp


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, mthl__dmz = build_set_seen_na(A)
        return len(s) + int(not dropna and mthl__dmz)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        xnlo__jcam = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        psjt__lim = len(xnlo__jcam)
        return bodo.libs.distributed_api.dist_reduce(psjt__lim, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([hvjjm__vovgy for hvjjm__vovgy in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        kdv__oauf = np.finfo(A.dtype(1).dtype).max
    else:
        kdv__oauf = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        riz__hkvlv = np.empty(n, A.dtype)
        hoyo__tbvo = kdv__oauf
        for i in range(n):
            hoyo__tbvo = min(hoyo__tbvo, A[i])
            riz__hkvlv[i] = hoyo__tbvo
        return riz__hkvlv
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        kdv__oauf = np.finfo(A.dtype(1).dtype).min
    else:
        kdv__oauf = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        riz__hkvlv = np.empty(n, A.dtype)
        hoyo__tbvo = kdv__oauf
        for i in range(n):
            hoyo__tbvo = max(hoyo__tbvo, A[i])
            riz__hkvlv[i] = hoyo__tbvo
        return riz__hkvlv
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        kwfh__dagb = arr_info_list_to_table([array_to_info(A)])
        knurq__bpli = 1
        eyp__lnc = 0
        qll__xgb = drop_duplicates_table(kwfh__dagb, parallel, knurq__bpli,
            eyp__lnc, dropna, True)
        riz__hkvlv = info_to_array(info_from_table(qll__xgb, 0), A)
        delete_table(kwfh__dagb)
        delete_table(qll__xgb)
        return riz__hkvlv
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    rkh__igh = bodo.utils.typing.to_nullable_type(arr.dtype)
    oiw__nli = index_arr
    hkfyu__aje = oiw__nli.dtype

    def impl(arr, index_arr):
        n = len(arr)
        phvn__kezpf = init_nested_counts(rkh__igh)
        pvmx__bgj = init_nested_counts(hkfyu__aje)
        for i in range(n):
            ewi__vup = index_arr[i]
            if isna(arr, i):
                phvn__kezpf = (phvn__kezpf[0] + 1,) + phvn__kezpf[1:]
                pvmx__bgj = add_nested_counts(pvmx__bgj, ewi__vup)
                continue
            nkxqq__jyank = arr[i]
            if len(nkxqq__jyank) == 0:
                phvn__kezpf = (phvn__kezpf[0] + 1,) + phvn__kezpf[1:]
                pvmx__bgj = add_nested_counts(pvmx__bgj, ewi__vup)
                continue
            phvn__kezpf = add_nested_counts(phvn__kezpf, nkxqq__jyank)
            for zos__csr in range(len(nkxqq__jyank)):
                pvmx__bgj = add_nested_counts(pvmx__bgj, ewi__vup)
        riz__hkvlv = bodo.utils.utils.alloc_type(phvn__kezpf[0], rkh__igh,
            phvn__kezpf[1:])
        ruyic__ucuay = bodo.utils.utils.alloc_type(phvn__kezpf[0], oiw__nli,
            pvmx__bgj)
        xkfq__akm = 0
        for i in range(n):
            if isna(arr, i):
                setna(riz__hkvlv, xkfq__akm)
                ruyic__ucuay[xkfq__akm] = index_arr[i]
                xkfq__akm += 1
                continue
            nkxqq__jyank = arr[i]
            naps__gaau = len(nkxqq__jyank)
            if naps__gaau == 0:
                setna(riz__hkvlv, xkfq__akm)
                ruyic__ucuay[xkfq__akm] = index_arr[i]
                xkfq__akm += 1
                continue
            riz__hkvlv[xkfq__akm:xkfq__akm + naps__gaau] = nkxqq__jyank
            ruyic__ucuay[xkfq__akm:xkfq__akm + naps__gaau] = index_arr[i]
            xkfq__akm += naps__gaau
        return riz__hkvlv, ruyic__ucuay
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    rkh__igh = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        phvn__kezpf = init_nested_counts(rkh__igh)
        for i in range(n):
            if isna(arr, i):
                phvn__kezpf = (phvn__kezpf[0] + 1,) + phvn__kezpf[1:]
                tppj__auvyo = 1
            else:
                nkxqq__jyank = arr[i]
                fduub__roeh = len(nkxqq__jyank)
                if fduub__roeh == 0:
                    phvn__kezpf = (phvn__kezpf[0] + 1,) + phvn__kezpf[1:]
                    tppj__auvyo = 1
                    continue
                else:
                    phvn__kezpf = add_nested_counts(phvn__kezpf, nkxqq__jyank)
                    tppj__auvyo = fduub__roeh
            if counts[i] != tppj__auvyo:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        riz__hkvlv = bodo.utils.utils.alloc_type(phvn__kezpf[0], rkh__igh,
            phvn__kezpf[1:])
        xkfq__akm = 0
        for i in range(n):
            if isna(arr, i):
                setna(riz__hkvlv, xkfq__akm)
                xkfq__akm += 1
                continue
            nkxqq__jyank = arr[i]
            naps__gaau = len(nkxqq__jyank)
            if naps__gaau == 0:
                setna(riz__hkvlv, xkfq__akm)
                xkfq__akm += 1
                continue
            riz__hkvlv[xkfq__akm:xkfq__akm + naps__gaau] = nkxqq__jyank
            xkfq__akm += naps__gaau
        return riz__hkvlv
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(yivnj__eka) for yivnj__eka in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        wjmqg__est = 'np.empty(n, np.int64)'
        tcq__esgo = 'out_arr[i] = 1'
        hkmt__qpvtl = 'max(len(arr[i]), 1)'
    else:
        wjmqg__est = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        tcq__esgo = 'bodo.libs.array_kernels.setna(out_arr, i)'
        hkmt__qpvtl = 'len(arr[i])'
    lsjqn__tcbir = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {wjmqg__est}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {tcq__esgo}
        else:
            out_arr[i] = {hkmt__qpvtl}
    return out_arr
    """
    lzlu__wbb = {}
    exec(lsjqn__tcbir, {'bodo': bodo, 'numba': numba, 'np': np}, lzlu__wbb)
    impl = lzlu__wbb['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    oiw__nli = index_arr
    hkfyu__aje = oiw__nli.dtype

    def impl(arr, pat, n, index_arr):
        nvux__axonn = pat is not None and len(pat) > 1
        if nvux__axonn:
            nrp__jue = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        ndjfj__feqhx = len(arr)
        pxoja__asu = 0
        jqihm__smpq = 0
        pvmx__bgj = init_nested_counts(hkfyu__aje)
        for i in range(ndjfj__feqhx):
            ewi__vup = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                pxoja__asu += 1
                pvmx__bgj = add_nested_counts(pvmx__bgj, ewi__vup)
                continue
            if nvux__axonn:
                gseas__xqee = nrp__jue.split(arr[i], maxsplit=n)
            else:
                gseas__xqee = arr[i].split(pat, n)
            pxoja__asu += len(gseas__xqee)
            for s in gseas__xqee:
                pvmx__bgj = add_nested_counts(pvmx__bgj, ewi__vup)
                jqihm__smpq += bodo.libs.str_arr_ext.get_utf8_size(s)
        riz__hkvlv = bodo.libs.str_arr_ext.pre_alloc_string_array(pxoja__asu,
            jqihm__smpq)
        ruyic__ucuay = bodo.utils.utils.alloc_type(pxoja__asu, oiw__nli,
            pvmx__bgj)
        aatu__okc = 0
        for llo__xjgx in range(ndjfj__feqhx):
            if isna(arr, llo__xjgx):
                riz__hkvlv[aatu__okc] = ''
                bodo.libs.array_kernels.setna(riz__hkvlv, aatu__okc)
                ruyic__ucuay[aatu__okc] = index_arr[llo__xjgx]
                aatu__okc += 1
                continue
            if nvux__axonn:
                gseas__xqee = nrp__jue.split(arr[llo__xjgx], maxsplit=n)
            else:
                gseas__xqee = arr[llo__xjgx].split(pat, n)
            smmce__eaz = len(gseas__xqee)
            riz__hkvlv[aatu__okc:aatu__okc + smmce__eaz] = gseas__xqee
            ruyic__ucuay[aatu__okc:aatu__okc + smmce__eaz] = index_arr[
                llo__xjgx]
            aatu__okc += smmce__eaz
        return riz__hkvlv, ruyic__ucuay
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
            riz__hkvlv = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                riz__hkvlv[i] = np.nan
            return riz__hkvlv
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            dek__okdru = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            tel__ergio = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(tel__ergio, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(dek__okdru,
                tel__ergio, True)
        return impl_dict
    odi__ohnw = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        riz__hkvlv = bodo.utils.utils.alloc_type(n, odi__ohnw, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(riz__hkvlv, i)
        return riz__hkvlv
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
    bmdxp__knzkt = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            riz__hkvlv = bodo.utils.utils.alloc_type(new_len, bmdxp__knzkt)
            bodo.libs.str_arr_ext.str_copy_ptr(riz__hkvlv.ctypes, 0, A.
                ctypes, old_size)
            return riz__hkvlv
        return impl_char

    def impl(A, old_size, new_len):
        riz__hkvlv = bodo.utils.utils.alloc_type(new_len, bmdxp__knzkt, (-1,))
        riz__hkvlv[:old_size] = A[:old_size]
        return riz__hkvlv
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    afb__vsrpr = math.ceil((stop - start) / step)
    return int(max(afb__vsrpr, 0))


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
    if any(isinstance(hvjjm__vovgy, types.Complex) for hvjjm__vovgy in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            ehdj__divww = (stop - start) / step
            afb__vsrpr = math.ceil(ehdj__divww.real)
            utxa__foch = math.ceil(ehdj__divww.imag)
            xhqa__fwc = int(max(min(utxa__foch, afb__vsrpr), 0))
            arr = np.empty(xhqa__fwc, dtype)
            for i in numba.parfors.parfor.internal_prange(xhqa__fwc):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            xhqa__fwc = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(xhqa__fwc, dtype)
            for i in numba.parfors.parfor.internal_prange(xhqa__fwc):
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
        tmco__rlabv = arr,
        if not inplace:
            tmco__rlabv = arr.copy(),
        gwil__pptq = bodo.libs.str_arr_ext.to_list_if_immutable_arr(tmco__rlabv
            )
        jhlnu__yevz = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True
            )
        bodo.libs.timsort.sort(gwil__pptq, 0, n, jhlnu__yevz)
        if not ascending:
            bodo.libs.timsort.reverseRange(gwil__pptq, 0, n, jhlnu__yevz)
        bodo.libs.str_arr_ext.cp_str_list_to_array(tmco__rlabv, gwil__pptq)
        return tmco__rlabv[0]
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
        aafl__fxqc = []
        for i in range(n):
            if A[i]:
                aafl__fxqc.append(i + offset)
        return np.array(aafl__fxqc, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    bmdxp__knzkt = element_type(A)
    if bmdxp__knzkt == types.unicode_type:
        null_value = '""'
    elif bmdxp__knzkt == types.bool_:
        null_value = 'False'
    elif bmdxp__knzkt == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif bmdxp__knzkt == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    aatu__okc = 'i'
    oiht__pehm = False
    ikjgl__furor = get_overload_const_str(method)
    if ikjgl__furor in ('ffill', 'pad'):
        auwe__fznfv = 'n'
        send_right = True
    elif ikjgl__furor in ('backfill', 'bfill'):
        auwe__fznfv = 'n-1, -1, -1'
        send_right = False
        if bmdxp__knzkt == types.unicode_type:
            aatu__okc = '(n - 1) - i'
            oiht__pehm = True
    lsjqn__tcbir = 'def impl(A, method, parallel=False):\n'
    lsjqn__tcbir += '  A = decode_if_dict_array(A)\n'
    lsjqn__tcbir += '  has_last_value = False\n'
    lsjqn__tcbir += f'  last_value = {null_value}\n'
    lsjqn__tcbir += '  if parallel:\n'
    lsjqn__tcbir += '    rank = bodo.libs.distributed_api.get_rank()\n'
    lsjqn__tcbir += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    lsjqn__tcbir += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    lsjqn__tcbir += '  n = len(A)\n'
    lsjqn__tcbir += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    lsjqn__tcbir += f'  for i in range({auwe__fznfv}):\n'
    lsjqn__tcbir += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    lsjqn__tcbir += (
        f'      bodo.libs.array_kernels.setna(out_arr, {aatu__okc})\n')
    lsjqn__tcbir += '      continue\n'
    lsjqn__tcbir += '    s = A[i]\n'
    lsjqn__tcbir += '    if bodo.libs.array_kernels.isna(A, i):\n'
    lsjqn__tcbir += '      s = last_value\n'
    lsjqn__tcbir += f'    out_arr[{aatu__okc}] = s\n'
    lsjqn__tcbir += '    last_value = s\n'
    lsjqn__tcbir += '    has_last_value = True\n'
    if oiht__pehm:
        lsjqn__tcbir += '  return out_arr[::-1]\n'
    else:
        lsjqn__tcbir += '  return out_arr\n'
    ibau__oeo = {}
    exec(lsjqn__tcbir, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, ibau__oeo)
    impl = ibau__oeo['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        mzznm__msgo = 0
        tcgoj__ugk = n_pes - 1
        tdxfw__yyg = np.int32(rank + 1)
        mosm__jqn = np.int32(rank - 1)
        dwbdc__xrfd = len(in_arr) - 1
        uybyd__rar = -1
        mpm__xoslc = -1
    else:
        mzznm__msgo = n_pes - 1
        tcgoj__ugk = 0
        tdxfw__yyg = np.int32(rank - 1)
        mosm__jqn = np.int32(rank + 1)
        dwbdc__xrfd = 0
        uybyd__rar = len(in_arr)
        mpm__xoslc = 1
    qand__quhb = np.int32(bodo.hiframes.rolling.comm_border_tag)
    buwv__iwd = np.empty(1, dtype=np.bool_)
    qtq__mvir = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    oihuk__txvf = np.empty(1, dtype=np.bool_)
    wekl__hqu = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    ltmlj__nsc = False
    zhyh__cdefh = null_value
    for i in range(dwbdc__xrfd, uybyd__rar, mpm__xoslc):
        if not isna(in_arr, i):
            ltmlj__nsc = True
            zhyh__cdefh = in_arr[i]
            break
    if rank != mzznm__msgo:
        zrpf__anqu = bodo.libs.distributed_api.irecv(buwv__iwd, 1,
            mosm__jqn, qand__quhb, True)
        bodo.libs.distributed_api.wait(zrpf__anqu, True)
        dwq__cxafb = bodo.libs.distributed_api.irecv(qtq__mvir, 1,
            mosm__jqn, qand__quhb, True)
        bodo.libs.distributed_api.wait(dwq__cxafb, True)
        shelm__tere = buwv__iwd[0]
        nzxnu__wry = qtq__mvir[0]
    else:
        shelm__tere = False
        nzxnu__wry = null_value
    if ltmlj__nsc:
        oihuk__txvf[0] = ltmlj__nsc
        wekl__hqu[0] = zhyh__cdefh
    else:
        oihuk__txvf[0] = shelm__tere
        wekl__hqu[0] = nzxnu__wry
    if rank != tcgoj__ugk:
        usyuj__yzgvh = bodo.libs.distributed_api.isend(oihuk__txvf, 1,
            tdxfw__yyg, qand__quhb, True)
        vpank__jtaqb = bodo.libs.distributed_api.isend(wekl__hqu, 1,
            tdxfw__yyg, qand__quhb, True)
    return shelm__tere, nzxnu__wry


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    vxewn__rjldk = {'axis': axis, 'kind': kind, 'order': order}
    bsilt__vepbs = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', vxewn__rjldk, bsilt__vepbs, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    bmdxp__knzkt = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            ndjfj__feqhx = len(A)
            riz__hkvlv = bodo.utils.utils.alloc_type(ndjfj__feqhx * repeats,
                bmdxp__knzkt, (-1,))
            for i in range(ndjfj__feqhx):
                aatu__okc = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for llo__xjgx in range(repeats):
                        bodo.libs.array_kernels.setna(riz__hkvlv, aatu__okc +
                            llo__xjgx)
                else:
                    riz__hkvlv[aatu__okc:aatu__okc + repeats] = A[i]
            return riz__hkvlv
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        ndjfj__feqhx = len(A)
        riz__hkvlv = bodo.utils.utils.alloc_type(repeats.sum(),
            bmdxp__knzkt, (-1,))
        aatu__okc = 0
        for i in range(ndjfj__feqhx):
            qbjpq__gbj = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for llo__xjgx in range(qbjpq__gbj):
                    bodo.libs.array_kernels.setna(riz__hkvlv, aatu__okc +
                        llo__xjgx)
            else:
                riz__hkvlv[aatu__okc:aatu__okc + qbjpq__gbj] = A[i]
            aatu__okc += qbjpq__gbj
        return riz__hkvlv
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
        vbun__hez = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(vbun__hez, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        ixh__nkbq = bodo.libs.array_kernels.concat([A1, A2])
        cmo__qoj = bodo.libs.array_kernels.unique(ixh__nkbq)
        return pd.Series(cmo__qoj).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    vxewn__rjldk = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    bsilt__vepbs = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', vxewn__rjldk, bsilt__vepbs,
        'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        eyz__jxnu = bodo.libs.array_kernels.unique(A1)
        pmh__mbz = bodo.libs.array_kernels.unique(A2)
        ixh__nkbq = bodo.libs.array_kernels.concat([eyz__jxnu, pmh__mbz])
        ygog__usynl = pd.Series(ixh__nkbq).sort_values().values
        return slice_array_intersect1d(ygog__usynl)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    feh__ibzn = arr[1:] == arr[:-1]
    return arr[:-1][feh__ibzn]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    qand__quhb = np.int32(bodo.hiframes.rolling.comm_border_tag)
    wajgw__bve = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        hdwe__mrp = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), qand__quhb, True)
        bodo.libs.distributed_api.wait(hdwe__mrp, True)
    if rank == n_pes - 1:
        return None
    else:
        mig__ioi = bodo.libs.distributed_api.irecv(wajgw__bve, 1, np.int32(
            rank + 1), qand__quhb, True)
        bodo.libs.distributed_api.wait(mig__ioi, True)
        return wajgw__bve[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    feh__ibzn = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            feh__ibzn[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        utzi__imxkg = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == utzi__imxkg:
            feh__ibzn[n - 1] = True
    return feh__ibzn


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    vxewn__rjldk = {'assume_unique': assume_unique}
    bsilt__vepbs = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', vxewn__rjldk, bsilt__vepbs, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        eyz__jxnu = bodo.libs.array_kernels.unique(A1)
        pmh__mbz = bodo.libs.array_kernels.unique(A2)
        feh__ibzn = calculate_mask_setdiff1d(eyz__jxnu, pmh__mbz)
        return pd.Series(eyz__jxnu[feh__ibzn]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    feh__ibzn = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        feh__ibzn &= A1 != A2[i]
    return feh__ibzn


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    vxewn__rjldk = {'retstep': retstep, 'axis': axis}
    bsilt__vepbs = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', vxewn__rjldk, bsilt__vepbs, 'numpy')
    cbd__caoiy = False
    if is_overload_none(dtype):
        bmdxp__knzkt = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            cbd__caoiy = True
        bmdxp__knzkt = numba.np.numpy_support.as_dtype(dtype).type
    if cbd__caoiy:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            nbgb__sixmy = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            riz__hkvlv = np.empty(num, bmdxp__knzkt)
            for i in numba.parfors.parfor.internal_prange(num):
                riz__hkvlv[i] = bmdxp__knzkt(np.floor(start + i * nbgb__sixmy))
            return riz__hkvlv
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            nbgb__sixmy = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            riz__hkvlv = np.empty(num, bmdxp__knzkt)
            for i in numba.parfors.parfor.internal_prange(num):
                riz__hkvlv[i] = bmdxp__knzkt(start + i * nbgb__sixmy)
            return riz__hkvlv
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
        bypxo__abpw = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                bypxo__abpw += A[i] == val
        return bypxo__abpw > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    vxewn__rjldk = {'axis': axis, 'out': out, 'keepdims': keepdims}
    bsilt__vepbs = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', vxewn__rjldk, bsilt__vepbs, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        bypxo__abpw = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                bypxo__abpw += int(bool(A[i]))
        return bypxo__abpw > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    vxewn__rjldk = {'axis': axis, 'out': out, 'keepdims': keepdims}
    bsilt__vepbs = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', vxewn__rjldk, bsilt__vepbs, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        bypxo__abpw = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                bypxo__abpw += int(bool(A[i]))
        return bypxo__abpw == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    vxewn__rjldk = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    bsilt__vepbs = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', vxewn__rjldk, bsilt__vepbs, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        okhh__eqro = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            riz__hkvlv = np.empty(n, okhh__eqro)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(riz__hkvlv, i)
                    continue
                riz__hkvlv[i] = np_cbrt_scalar(A[i], okhh__eqro)
            return riz__hkvlv
        return impl_arr
    okhh__eqro = np.promote_types(numba.np.numpy_support.as_dtype(A), numba
        .np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, okhh__eqro)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    gpebo__pvst = x < 0
    if gpebo__pvst:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if gpebo__pvst:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    gib__wyrzo = isinstance(tup, (types.BaseTuple, types.List))
    huuxi__wuvt = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for dkdl__vjr in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(dkdl__vjr
                , 'numpy.hstack()')
            gib__wyrzo = gib__wyrzo and bodo.utils.utils.is_array_typ(dkdl__vjr
                , False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        gib__wyrzo = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif huuxi__wuvt:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        jetu__recqk = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for dkdl__vjr in jetu__recqk.types:
            huuxi__wuvt = huuxi__wuvt and bodo.utils.utils.is_array_typ(
                dkdl__vjr, False)
    if not (gib__wyrzo or huuxi__wuvt):
        return
    if huuxi__wuvt:

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
    vxewn__rjldk = {'check_valid': check_valid, 'tol': tol}
    bsilt__vepbs = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', vxewn__rjldk,
        bsilt__vepbs, 'numpy')
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
        rknr__egojl = mean.shape[0]
        lng__pjvmj = size, rknr__egojl
        kxngn__xho = np.random.standard_normal(lng__pjvmj)
        cov = cov.astype(np.float64)
        qjtkv__ojoif, s, dhh__twen = np.linalg.svd(cov)
        res = np.dot(kxngn__xho, np.sqrt(s).reshape(rknr__egojl, 1) * dhh__twen
            )
        kjanc__enf = res + mean
        return kjanc__enf
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
            ifkn__mjfpf = bodo.hiframes.series_kernels._get_type_max_value(arr)
            gog__pko = typing.builtins.IndexValue(-1, ifkn__mjfpf)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                tey__mybgd = typing.builtins.IndexValue(i, arr[i])
                gog__pko = min(gog__pko, tey__mybgd)
            return gog__pko.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        vxhso__lqknx = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            uxh__zdu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            ifkn__mjfpf = vxhso__lqknx(len(arr.dtype.categories) + 1)
            gog__pko = typing.builtins.IndexValue(-1, ifkn__mjfpf)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                tey__mybgd = typing.builtins.IndexValue(i, uxh__zdu[i])
                gog__pko = min(gog__pko, tey__mybgd)
            return gog__pko.index
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
            ifkn__mjfpf = bodo.hiframes.series_kernels._get_type_min_value(arr)
            gog__pko = typing.builtins.IndexValue(-1, ifkn__mjfpf)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                tey__mybgd = typing.builtins.IndexValue(i, arr[i])
                gog__pko = max(gog__pko, tey__mybgd)
            return gog__pko.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        vxhso__lqknx = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def impl_cat_arr(arr):
            n = len(arr)
            uxh__zdu = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            ifkn__mjfpf = vxhso__lqknx(-1)
            gog__pko = typing.builtins.IndexValue(-1, ifkn__mjfpf)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                tey__mybgd = typing.builtins.IndexValue(i, uxh__zdu[i])
                gog__pko = max(gog__pko, tey__mybgd)
            return gog__pko.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
