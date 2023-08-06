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
        ixe__marhr = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = ixe__marhr
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        ixe__marhr = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = ixe__marhr
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
            jcr__kckre = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            jcr__kckre[ind + 1] = jcr__kckre[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            jcr__kckre = bodo.libs.array_item_arr_ext.get_offsets(arr)
            jcr__kckre[ind + 1] = jcr__kckre[ind]
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
    fumqv__tdt = arr_tup.count
    vsvji__ymjh = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(fumqv__tdt):
        vsvji__ymjh += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    vsvji__ymjh += '  return\n'
    duwf__saj = {}
    exec(vsvji__ymjh, {'setna': setna}, duwf__saj)
    impl = duwf__saj['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        srwno__naio = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(srwno__naio.start, srwno__naio.stop, srwno__naio.step):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        zinwg__yxvco = 'n'
        nrim__glnpj = 'n_pes'
        aenql__nnelk = 'min_op'
    else:
        zinwg__yxvco = 'n-1, -1, -1'
        nrim__glnpj = '-1'
        aenql__nnelk = 'max_op'
    vsvji__ymjh = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {nrim__glnpj}
    for i in range({zinwg__yxvco}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {aenql__nnelk}))
        if possible_valid_rank != {nrim__glnpj}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    duwf__saj = {}
    exec(vsvji__ymjh, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op':
        max_op, 'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.
        box_if_dt64}, duwf__saj)
    impl = duwf__saj['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    jhr__lnaq = array_to_info(arr)
    _median_series_computation(res, jhr__lnaq, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(jhr__lnaq)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    jhr__lnaq = array_to_info(arr)
    _autocorr_series_computation(res, jhr__lnaq, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(jhr__lnaq)


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
    jhr__lnaq = array_to_info(arr)
    _compute_series_monotonicity(res, jhr__lnaq, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(jhr__lnaq)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    oyki__qok = res[0] > 0.5
    return oyki__qok


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        xkxmn__oqgq = '-'
        kqj__teuuz = 'index_arr[0] > threshhold_date'
        zinwg__yxvco = '1, n+1'
        glgo__steuz = 'index_arr[-i] <= threshhold_date'
        iomsy__ypbo = 'i - 1'
    else:
        xkxmn__oqgq = '+'
        kqj__teuuz = 'index_arr[-1] < threshhold_date'
        zinwg__yxvco = 'n'
        glgo__steuz = 'index_arr[i] >= threshhold_date'
        iomsy__ypbo = 'i'
    vsvji__ymjh = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        vsvji__ymjh += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        vsvji__ymjh += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            vsvji__ymjh += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            vsvji__ymjh += """      threshhold_date = initial_date - date_offset.base + date_offset
"""
            vsvji__ymjh += '    else:\n'
            vsvji__ymjh += (
                '      threshhold_date = initial_date + date_offset\n')
        else:
            vsvji__ymjh += (
                f'    threshhold_date = initial_date {xkxmn__oqgq} date_offset\n'
                )
    else:
        vsvji__ymjh += (
            f'  threshhold_date = initial_date {xkxmn__oqgq} offset\n')
    vsvji__ymjh += '  local_valid = 0\n'
    vsvji__ymjh += f'  n = len(index_arr)\n'
    vsvji__ymjh += f'  if n:\n'
    vsvji__ymjh += f'    if {kqj__teuuz}:\n'
    vsvji__ymjh += '      loc_valid = n\n'
    vsvji__ymjh += '    else:\n'
    vsvji__ymjh += f'      for i in range({zinwg__yxvco}):\n'
    vsvji__ymjh += f'        if {glgo__steuz}:\n'
    vsvji__ymjh += f'          loc_valid = {iomsy__ypbo}\n'
    vsvji__ymjh += '          break\n'
    vsvji__ymjh += '  if is_parallel:\n'
    vsvji__ymjh += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    vsvji__ymjh += '    return total_valid\n'
    vsvji__ymjh += '  else:\n'
    vsvji__ymjh += '    return loc_valid\n'
    duwf__saj = {}
    exec(vsvji__ymjh, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, duwf__saj)
    return duwf__saj['impl']


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
    shdso__ndzln = numba_to_c_type(sig.args[0].dtype)
    rxmxs__sxp = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), shdso__ndzln))
    qwe__zfye = args[0]
    zehq__aai = sig.args[0]
    if isinstance(zehq__aai, (IntegerArrayType, BooleanArrayType)):
        qwe__zfye = cgutils.create_struct_proxy(zehq__aai)(context, builder,
            qwe__zfye).data
        zehq__aai = types.Array(zehq__aai.dtype, 1, 'C')
    assert zehq__aai.ndim == 1
    arr = make_array(zehq__aai)(context, builder, qwe__zfye)
    nvf__ezxs = builder.extract_value(arr.shape, 0)
    ohl__wbxtu = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        nvf__ezxs, args[1], builder.load(rxmxs__sxp)]
    lex__uzxqo = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    spbbr__mgsgm = lir.FunctionType(lir.DoubleType(), lex__uzxqo)
    esvle__odfd = cgutils.get_or_insert_function(builder.module,
        spbbr__mgsgm, name='quantile_sequential')
    rnymo__ovm = builder.call(esvle__odfd, ohl__wbxtu)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return rnymo__ovm


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    shdso__ndzln = numba_to_c_type(sig.args[0].dtype)
    rxmxs__sxp = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), shdso__ndzln))
    qwe__zfye = args[0]
    zehq__aai = sig.args[0]
    if isinstance(zehq__aai, (IntegerArrayType, BooleanArrayType)):
        qwe__zfye = cgutils.create_struct_proxy(zehq__aai)(context, builder,
            qwe__zfye).data
        zehq__aai = types.Array(zehq__aai.dtype, 1, 'C')
    assert zehq__aai.ndim == 1
    arr = make_array(zehq__aai)(context, builder, qwe__zfye)
    nvf__ezxs = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        yer__htn = args[2]
    else:
        yer__htn = nvf__ezxs
    ohl__wbxtu = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        nvf__ezxs, yer__htn, args[1], builder.load(rxmxs__sxp)]
    lex__uzxqo = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.IntType
        (64), lir.DoubleType(), lir.IntType(32)]
    spbbr__mgsgm = lir.FunctionType(lir.DoubleType(), lex__uzxqo)
    esvle__odfd = cgutils.get_or_insert_function(builder.module,
        spbbr__mgsgm, name='quantile_parallel')
    rnymo__ovm = builder.call(esvle__odfd, ohl__wbxtu)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return rnymo__ovm


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        cabjy__etove = np.nonzero(pd.isna(arr))[0]
        cekb__kow = arr[1:] != arr[:-1]
        cekb__kow[pd.isna(cekb__kow)] = False
        odx__xmiol = cekb__kow.astype(np.bool_)
        dlbq__qzij = np.concatenate((np.array([True]), odx__xmiol))
        if cabjy__etove.size:
            wyrjg__xxkxf, xsp__ayu = cabjy__etove[0], cabjy__etove[1:]
            dlbq__qzij[wyrjg__xxkxf] = True
            if xsp__ayu.size:
                dlbq__qzij[xsp__ayu] = False
                if xsp__ayu[-1] + 1 < dlbq__qzij.size:
                    dlbq__qzij[xsp__ayu[-1] + 1] = True
            elif wyrjg__xxkxf + 1 < dlbq__qzij.size:
                dlbq__qzij[wyrjg__xxkxf + 1] = True
        return dlbq__qzij
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
    vsvji__ymjh = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    vsvji__ymjh += '  na_idxs = pd.isna(arr)\n'
    vsvji__ymjh += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    vsvji__ymjh += '  nas = sum(na_idxs)\n'
    if not ascending:
        vsvji__ymjh += '  if nas and nas < (sorter.size - 1):\n'
        vsvji__ymjh += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        vsvji__ymjh += '  else:\n'
        vsvji__ymjh += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        vsvji__ymjh += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    vsvji__ymjh += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    vsvji__ymjh += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        vsvji__ymjh += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        vsvji__ymjh += '    inv,\n'
        vsvji__ymjh += '    new_dtype=np.float64,\n'
        vsvji__ymjh += '    copy=True,\n'
        vsvji__ymjh += '    nan_to_str=False,\n'
        vsvji__ymjh += '    from_series=True,\n'
        vsvji__ymjh += '    ) + 1\n'
    else:
        vsvji__ymjh += '  arr = arr[sorter]\n'
        vsvji__ymjh += (
            '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n')
        vsvji__ymjh += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            vsvji__ymjh += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            vsvji__ymjh += '    dense,\n'
            vsvji__ymjh += '    new_dtype=np.float64,\n'
            vsvji__ymjh += '    copy=True,\n'
            vsvji__ymjh += '    nan_to_str=False,\n'
            vsvji__ymjh += '    from_series=True,\n'
            vsvji__ymjh += '  )\n'
        else:
            vsvji__ymjh += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            vsvji__ymjh += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                vsvji__ymjh += '  ret = count_float[dense]\n'
            elif method == 'min':
                vsvji__ymjh += '  ret = count_float[dense - 1] + 1\n'
            else:
                vsvji__ymjh += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                vsvji__ymjh += '  ret[na_idxs] = -1\n'
            vsvji__ymjh += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            vsvji__ymjh += '  div_val = arr.size - nas\n'
        else:
            vsvji__ymjh += '  div_val = arr.size\n'
        vsvji__ymjh += '  for i in range(len(ret)):\n'
        vsvji__ymjh += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        vsvji__ymjh += '  ret[na_idxs] = np.nan\n'
    vsvji__ymjh += '  return ret\n'
    duwf__saj = {}
    exec(vsvji__ymjh, {'np': np, 'pd': pd, 'bodo': bodo}, duwf__saj)
    return duwf__saj['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    yro__dfe = start
    oumb__kqrj = 2 * start + 1
    thutt__bsh = 2 * start + 2
    if oumb__kqrj < n and not cmp_f(arr[oumb__kqrj], arr[yro__dfe]):
        yro__dfe = oumb__kqrj
    if thutt__bsh < n and not cmp_f(arr[thutt__bsh], arr[yro__dfe]):
        yro__dfe = thutt__bsh
    if yro__dfe != start:
        arr[start], arr[yro__dfe] = arr[yro__dfe], arr[start]
        ind_arr[start], ind_arr[yro__dfe] = ind_arr[yro__dfe], ind_arr[start]
        min_heapify(arr, ind_arr, n, yro__dfe, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        tde__hfsab = np.empty(k, A.dtype)
        cacr__lvw = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                tde__hfsab[ind] = A[i]
                cacr__lvw[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            tde__hfsab = tde__hfsab[:ind]
            cacr__lvw = cacr__lvw[:ind]
        return tde__hfsab, cacr__lvw, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        vobrq__vaa = np.sort(A)
        rjwl__gkxtr = index_arr[np.argsort(A)]
        gvmao__jpb = pd.Series(vobrq__vaa).notna().values
        vobrq__vaa = vobrq__vaa[gvmao__jpb]
        rjwl__gkxtr = rjwl__gkxtr[gvmao__jpb]
        if is_largest:
            vobrq__vaa = vobrq__vaa[::-1]
            rjwl__gkxtr = rjwl__gkxtr[::-1]
        return np.ascontiguousarray(vobrq__vaa), np.ascontiguousarray(
            rjwl__gkxtr)
    tde__hfsab, cacr__lvw, start = select_k_nonan(A, index_arr, m, k)
    cacr__lvw = cacr__lvw[tde__hfsab.argsort()]
    tde__hfsab.sort()
    if not is_largest:
        tde__hfsab = np.ascontiguousarray(tde__hfsab[::-1])
        cacr__lvw = np.ascontiguousarray(cacr__lvw[::-1])
    for i in range(start, m):
        if cmp_f(A[i], tde__hfsab[0]):
            tde__hfsab[0] = A[i]
            cacr__lvw[0] = index_arr[i]
            min_heapify(tde__hfsab, cacr__lvw, k, 0, cmp_f)
    cacr__lvw = cacr__lvw[tde__hfsab.argsort()]
    tde__hfsab.sort()
    if is_largest:
        tde__hfsab = tde__hfsab[::-1]
        cacr__lvw = cacr__lvw[::-1]
    return np.ascontiguousarray(tde__hfsab), np.ascontiguousarray(cacr__lvw)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    lbgop__ybad = bodo.libs.distributed_api.get_rank()
    bnxs__xjxb, mimaa__iood = nlargest(A, I, k, is_largest, cmp_f)
    pvylg__kvai = bodo.libs.distributed_api.gatherv(bnxs__xjxb)
    nqxlu__zbwp = bodo.libs.distributed_api.gatherv(mimaa__iood)
    if lbgop__ybad == MPI_ROOT:
        res, tjvu__arl = nlargest(pvylg__kvai, nqxlu__zbwp, k, is_largest,
            cmp_f)
    else:
        res = np.empty(k, A.dtype)
        tjvu__arl = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(tjvu__arl)
    return res, tjvu__arl


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    pyf__lad, udud__dliwv = mat.shape
    pzdtv__qnjq = np.empty((udud__dliwv, udud__dliwv), dtype=np.float64)
    for mgf__tjhks in range(udud__dliwv):
        for ikc__ftso in range(mgf__tjhks + 1):
            sfa__rcm = 0
            ncikc__etsxs = rqlfn__ssbk = zhd__fxbpk = alq__empmc = 0.0
            for i in range(pyf__lad):
                if np.isfinite(mat[i, mgf__tjhks]) and np.isfinite(mat[i,
                    ikc__ftso]):
                    ivc__znk = mat[i, mgf__tjhks]
                    lnwl__bkob = mat[i, ikc__ftso]
                    sfa__rcm += 1
                    zhd__fxbpk += ivc__znk
                    alq__empmc += lnwl__bkob
            if parallel:
                sfa__rcm = bodo.libs.distributed_api.dist_reduce(sfa__rcm,
                    sum_op)
                zhd__fxbpk = bodo.libs.distributed_api.dist_reduce(zhd__fxbpk,
                    sum_op)
                alq__empmc = bodo.libs.distributed_api.dist_reduce(alq__empmc,
                    sum_op)
            if sfa__rcm < minpv:
                pzdtv__qnjq[mgf__tjhks, ikc__ftso] = pzdtv__qnjq[ikc__ftso,
                    mgf__tjhks] = np.nan
            else:
                nabkx__vpt = zhd__fxbpk / sfa__rcm
                wnu__sxnoe = alq__empmc / sfa__rcm
                zhd__fxbpk = 0.0
                for i in range(pyf__lad):
                    if np.isfinite(mat[i, mgf__tjhks]) and np.isfinite(mat[
                        i, ikc__ftso]):
                        ivc__znk = mat[i, mgf__tjhks] - nabkx__vpt
                        lnwl__bkob = mat[i, ikc__ftso] - wnu__sxnoe
                        zhd__fxbpk += ivc__znk * lnwl__bkob
                        ncikc__etsxs += ivc__znk * ivc__znk
                        rqlfn__ssbk += lnwl__bkob * lnwl__bkob
                if parallel:
                    zhd__fxbpk = bodo.libs.distributed_api.dist_reduce(
                        zhd__fxbpk, sum_op)
                    ncikc__etsxs = bodo.libs.distributed_api.dist_reduce(
                        ncikc__etsxs, sum_op)
                    rqlfn__ssbk = bodo.libs.distributed_api.dist_reduce(
                        rqlfn__ssbk, sum_op)
                ellr__igzc = sfa__rcm - 1.0 if cov else sqrt(ncikc__etsxs *
                    rqlfn__ssbk)
                if ellr__igzc != 0.0:
                    pzdtv__qnjq[mgf__tjhks, ikc__ftso] = pzdtv__qnjq[
                        ikc__ftso, mgf__tjhks] = zhd__fxbpk / ellr__igzc
                else:
                    pzdtv__qnjq[mgf__tjhks, ikc__ftso] = pzdtv__qnjq[
                        ikc__ftso, mgf__tjhks] = np.nan
    return pzdtv__qnjq


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    xvx__ayiv = n != 1
    vsvji__ymjh = 'def impl(data, parallel=False):\n'
    vsvji__ymjh += '  if parallel:\n'
    all__lez = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    vsvji__ymjh += f'    cpp_table = arr_info_list_to_table([{all__lez}])\n'
    vsvji__ymjh += f"""    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)
"""
    hru__qsu = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    vsvji__ymjh += f'    data = ({hru__qsu},)\n'
    vsvji__ymjh += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    vsvji__ymjh += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    vsvji__ymjh += '    bodo.libs.array.delete_table(cpp_table)\n'
    vsvji__ymjh += '  n = len(data[0])\n'
    vsvji__ymjh += '  out = np.empty(n, np.bool_)\n'
    vsvji__ymjh += '  uniqs = dict()\n'
    if xvx__ayiv:
        vsvji__ymjh += '  for i in range(n):\n'
        pvn__glc = ', '.join(f'data[{i}][i]' for i in range(n))
        caoo__eikb = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        vsvji__ymjh += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({pvn__glc},), ({caoo__eikb},))
"""
        vsvji__ymjh += '    if val in uniqs:\n'
        vsvji__ymjh += '      out[i] = True\n'
        vsvji__ymjh += '    else:\n'
        vsvji__ymjh += '      out[i] = False\n'
        vsvji__ymjh += '      uniqs[val] = 0\n'
    else:
        vsvji__ymjh += '  data = data[0]\n'
        vsvji__ymjh += '  hasna = False\n'
        vsvji__ymjh += '  for i in range(n):\n'
        vsvji__ymjh += '    if bodo.libs.array_kernels.isna(data, i):\n'
        vsvji__ymjh += '      out[i] = hasna\n'
        vsvji__ymjh += '      hasna = True\n'
        vsvji__ymjh += '    else:\n'
        vsvji__ymjh += '      val = data[i]\n'
        vsvji__ymjh += '      if val in uniqs:\n'
        vsvji__ymjh += '        out[i] = True\n'
        vsvji__ymjh += '      else:\n'
        vsvji__ymjh += '        out[i] = False\n'
        vsvji__ymjh += '        uniqs[val] = 0\n'
    vsvji__ymjh += '  if parallel:\n'
    vsvji__ymjh += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    vsvji__ymjh += '  return out\n'
    duwf__saj = {}
    exec(vsvji__ymjh, {'bodo': bodo, 'np': np, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'info_to_array': info_to_array, 'info_from_table': info_from_table},
        duwf__saj)
    impl = duwf__saj['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    fumqv__tdt = len(data)
    vsvji__ymjh = (
        'def impl(data, ind_arr, n, frac, replace, parallel=False):\n')
    vsvji__ymjh += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        fumqv__tdt)))
    vsvji__ymjh += '  table_total = arr_info_list_to_table(info_list_total)\n'
    vsvji__ymjh += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(fumqv__tdt))
    for euup__qjrs in range(fumqv__tdt):
        vsvji__ymjh += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(euup__qjrs, euup__qjrs, euup__qjrs))
    vsvji__ymjh += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(fumqv__tdt))
    vsvji__ymjh += '  delete_table(out_table)\n'
    vsvji__ymjh += '  delete_table(table_total)\n'
    vsvji__ymjh += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(fumqv__tdt)))
    duwf__saj = {}
    exec(vsvji__ymjh, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'sample_table': sample_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, duwf__saj)
    impl = duwf__saj['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    fumqv__tdt = len(data)
    vsvji__ymjh = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    vsvji__ymjh += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        fumqv__tdt)))
    vsvji__ymjh += '  table_total = arr_info_list_to_table(info_list_total)\n'
    vsvji__ymjh += '  keep_i = 0\n'
    vsvji__ymjh += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for euup__qjrs in range(fumqv__tdt):
        vsvji__ymjh += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(euup__qjrs, euup__qjrs, euup__qjrs))
    vsvji__ymjh += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(fumqv__tdt))
    vsvji__ymjh += '  delete_table(out_table)\n'
    vsvji__ymjh += '  delete_table(table_total)\n'
    vsvji__ymjh += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(fumqv__tdt)))
    duwf__saj = {}
    exec(vsvji__ymjh, {'np': np, 'bodo': bodo, 'array_to_info':
        array_to_info, 'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, duwf__saj)
    impl = duwf__saj['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        riwdi__andlr = [array_to_info(data_arr)]
        jey__ylrrs = arr_info_list_to_table(riwdi__andlr)
        vrxf__oybs = 0
        nkeiw__yzhe = drop_duplicates_table(jey__ylrrs, parallel, 1,
            vrxf__oybs, False, True)
        hssm__vpo = info_to_array(info_from_table(nkeiw__yzhe, 0), data_arr)
        delete_table(nkeiw__yzhe)
        delete_table(jey__ylrrs)
        return hssm__vpo
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    fes__jrpi = len(data.types)
    dxnj__ajj = [('out' + str(i)) for i in range(fes__jrpi)]
    ptxh__rpyvj = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    awbp__udvx = ['isna(data[{}], i)'.format(i) for i in ptxh__rpyvj]
    iae__snnc = 'not ({})'.format(' or '.join(awbp__udvx))
    if not is_overload_none(thresh):
        iae__snnc = '(({}) <= ({}) - thresh)'.format(' + '.join(awbp__udvx),
            fes__jrpi - 1)
    elif how == 'all':
        iae__snnc = 'not ({})'.format(' and '.join(awbp__udvx))
    vsvji__ymjh = 'def _dropna_imp(data, how, thresh, subset):\n'
    vsvji__ymjh += '  old_len = len(data[0])\n'
    vsvji__ymjh += '  new_len = 0\n'
    vsvji__ymjh += '  for i in range(old_len):\n'
    vsvji__ymjh += '    if {}:\n'.format(iae__snnc)
    vsvji__ymjh += '      new_len += 1\n'
    for i, out in enumerate(dxnj__ajj):
        if isinstance(data[i], bodo.CategoricalArrayType):
            vsvji__ymjh += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            vsvji__ymjh += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    vsvji__ymjh += '  curr_ind = 0\n'
    vsvji__ymjh += '  for i in range(old_len):\n'
    vsvji__ymjh += '    if {}:\n'.format(iae__snnc)
    for i in range(fes__jrpi):
        vsvji__ymjh += '      if isna(data[{}], i):\n'.format(i)
        vsvji__ymjh += '        setna({}, curr_ind)\n'.format(dxnj__ajj[i])
        vsvji__ymjh += '      else:\n'
        vsvji__ymjh += '        {}[curr_ind] = data[{}][i]\n'.format(dxnj__ajj
            [i], i)
    vsvji__ymjh += '      curr_ind += 1\n'
    vsvji__ymjh += '  return {}\n'.format(', '.join(dxnj__ajj))
    duwf__saj = {}
    qfw__xhgs = {'t{}'.format(i): vvk__delae for i, vvk__delae in enumerate
        (data.types)}
    qfw__xhgs.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(vsvji__ymjh, qfw__xhgs, duwf__saj)
    bqy__uzm = duwf__saj['_dropna_imp']
    return bqy__uzm


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        zehq__aai = arr.dtype
        zmeyt__xpx = zehq__aai.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            wctlh__wqx = init_nested_counts(zmeyt__xpx)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                wctlh__wqx = add_nested_counts(wctlh__wqx, val[ind])
            hssm__vpo = bodo.utils.utils.alloc_type(n, zehq__aai, wctlh__wqx)
            for zced__ijakg in range(n):
                if bodo.libs.array_kernels.isna(arr, zced__ijakg):
                    setna(hssm__vpo, zced__ijakg)
                    continue
                val = arr[zced__ijakg]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(hssm__vpo, zced__ijakg)
                    continue
                hssm__vpo[zced__ijakg] = val[ind]
            return hssm__vpo
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    bfo__osmlr = _to_readonly(arr_types.types[0])
    return all(isinstance(vvk__delae, CategoricalArrayType) and 
        _to_readonly(vvk__delae) == bfo__osmlr for vvk__delae in arr_types.
        types)


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
        opd__wopr = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            qnt__ynjj = 0
            eeej__gkq = []
            for A in arr_list:
                bxpv__pcn = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                eeej__gkq.append(bodo.libs.array_item_arr_ext.get_data(A))
                qnt__ynjj += bxpv__pcn
            natv__pwrfc = np.empty(qnt__ynjj + 1, offset_type)
            denub__chc = bodo.libs.array_kernels.concat(eeej__gkq)
            fpr__kvl = np.empty(qnt__ynjj + 7 >> 3, np.uint8)
            gxd__jtxir = 0
            wzoni__rvn = 0
            for A in arr_list:
                fir__ztm = bodo.libs.array_item_arr_ext.get_offsets(A)
                ojb__ezhcf = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                bxpv__pcn = len(A)
                buuxr__vqbl = fir__ztm[bxpv__pcn]
                for i in range(bxpv__pcn):
                    natv__pwrfc[i + gxd__jtxir] = fir__ztm[i] + wzoni__rvn
                    pxd__mcrms = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ojb__ezhcf, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(fpr__kvl, i +
                        gxd__jtxir, pxd__mcrms)
                gxd__jtxir += bxpv__pcn
                wzoni__rvn += buuxr__vqbl
            natv__pwrfc[gxd__jtxir] = wzoni__rvn
            hssm__vpo = bodo.libs.array_item_arr_ext.init_array_item_array(
                qnt__ynjj, denub__chc, natv__pwrfc, fpr__kvl)
            return hssm__vpo
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        wcnz__itqyp = arr_list.dtype.names
        vsvji__ymjh = 'def struct_array_concat_impl(arr_list):\n'
        vsvji__ymjh += f'    n_all = 0\n'
        for i in range(len(wcnz__itqyp)):
            vsvji__ymjh += f'    concat_list{i} = []\n'
        vsvji__ymjh += '    for A in arr_list:\n'
        vsvji__ymjh += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(wcnz__itqyp)):
            vsvji__ymjh += f'        concat_list{i}.append(data_tuple[{i}])\n'
        vsvji__ymjh += '        n_all += len(A)\n'
        vsvji__ymjh += '    n_bytes = (n_all + 7) >> 3\n'
        vsvji__ymjh += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        vsvji__ymjh += '    curr_bit = 0\n'
        vsvji__ymjh += '    for A in arr_list:\n'
        vsvji__ymjh += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        vsvji__ymjh += '        for j in range(len(A)):\n'
        vsvji__ymjh += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        vsvji__ymjh += """            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)
"""
        vsvji__ymjh += '            curr_bit += 1\n'
        vsvji__ymjh += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        rrptr__eig = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(wcnz__itqyp))])
        vsvji__ymjh += f'        ({rrptr__eig},),\n'
        vsvji__ymjh += '        new_mask,\n'
        vsvji__ymjh += f'        {wcnz__itqyp},\n'
        vsvji__ymjh += '    )\n'
        duwf__saj = {}
        exec(vsvji__ymjh, {'bodo': bodo, 'np': np}, duwf__saj)
        return duwf__saj['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            udyf__zgmq = 0
            for A in arr_list:
                udyf__zgmq += len(A)
            sdgp__anbe = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(udyf__zgmq))
            mcmx__hhv = 0
            for A in arr_list:
                for i in range(len(A)):
                    sdgp__anbe._data[i + mcmx__hhv] = A._data[i]
                    pxd__mcrms = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(sdgp__anbe.
                        _null_bitmap, i + mcmx__hhv, pxd__mcrms)
                mcmx__hhv += len(A)
            return sdgp__anbe
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            udyf__zgmq = 0
            for A in arr_list:
                udyf__zgmq += len(A)
            sdgp__anbe = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(udyf__zgmq))
            mcmx__hhv = 0
            for A in arr_list:
                for i in range(len(A)):
                    sdgp__anbe._days_data[i + mcmx__hhv] = A._days_data[i]
                    sdgp__anbe._seconds_data[i + mcmx__hhv] = A._seconds_data[i
                        ]
                    sdgp__anbe._microseconds_data[i + mcmx__hhv
                        ] = A._microseconds_data[i]
                    pxd__mcrms = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(sdgp__anbe.
                        _null_bitmap, i + mcmx__hhv, pxd__mcrms)
                mcmx__hhv += len(A)
            return sdgp__anbe
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        yaly__bjea = arr_list.dtype.precision
        siqtv__xafeh = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            udyf__zgmq = 0
            for A in arr_list:
                udyf__zgmq += len(A)
            sdgp__anbe = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                udyf__zgmq, yaly__bjea, siqtv__xafeh)
            mcmx__hhv = 0
            for A in arr_list:
                for i in range(len(A)):
                    sdgp__anbe._data[i + mcmx__hhv] = A._data[i]
                    pxd__mcrms = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(sdgp__anbe.
                        _null_bitmap, i + mcmx__hhv, pxd__mcrms)
                mcmx__hhv += len(A)
            return sdgp__anbe
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        vvk__delae) for vvk__delae in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            xwbn__fmke = arr_list.types[0]
        else:
            xwbn__fmke = arr_list.dtype
        xwbn__fmke = to_str_arr_if_dict_array(xwbn__fmke)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            tvcyy__xffbc = 0
            qstlm__odxgp = 0
            for A in arr_list:
                arr = A
                tvcyy__xffbc += len(arr)
                qstlm__odxgp += bodo.libs.str_arr_ext.num_total_chars(arr)
            hssm__vpo = bodo.utils.utils.alloc_type(tvcyy__xffbc,
                xwbn__fmke, (qstlm__odxgp,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(hssm__vpo, -1)
            tkjwq__qaokx = 0
            hoznd__ojm = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(hssm__vpo, arr,
                    tkjwq__qaokx, hoznd__ojm)
                tkjwq__qaokx += len(arr)
                hoznd__ojm += bodo.libs.str_arr_ext.num_total_chars(arr)
            return hssm__vpo
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(vvk__delae.dtype, types.Integer) for
        vvk__delae in arr_list.types) and any(isinstance(vvk__delae,
        IntegerArrayType) for vvk__delae in arr_list.types):

        def impl_int_arr_list(arr_list):
            vccgw__ppcc = convert_to_nullable_tup(arr_list)
            alc__swvva = []
            flsk__yeb = 0
            for A in vccgw__ppcc:
                alc__swvva.append(A._data)
                flsk__yeb += len(A)
            denub__chc = bodo.libs.array_kernels.concat(alc__swvva)
            mtt__jyfgq = flsk__yeb + 7 >> 3
            jfs__lwo = np.empty(mtt__jyfgq, np.uint8)
            njff__nktx = 0
            for A in vccgw__ppcc:
                iopu__uhvv = A._null_bitmap
                for zced__ijakg in range(len(A)):
                    pxd__mcrms = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        iopu__uhvv, zced__ijakg)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jfs__lwo,
                        njff__nktx, pxd__mcrms)
                    njff__nktx += 1
            return bodo.libs.int_arr_ext.init_integer_array(denub__chc,
                jfs__lwo)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(vvk__delae.dtype == types.bool_ for vvk__delae in
        arr_list.types) and any(vvk__delae == boolean_array for vvk__delae in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            vccgw__ppcc = convert_to_nullable_tup(arr_list)
            alc__swvva = []
            flsk__yeb = 0
            for A in vccgw__ppcc:
                alc__swvva.append(A._data)
                flsk__yeb += len(A)
            denub__chc = bodo.libs.array_kernels.concat(alc__swvva)
            mtt__jyfgq = flsk__yeb + 7 >> 3
            jfs__lwo = np.empty(mtt__jyfgq, np.uint8)
            njff__nktx = 0
            for A in vccgw__ppcc:
                iopu__uhvv = A._null_bitmap
                for zced__ijakg in range(len(A)):
                    pxd__mcrms = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        iopu__uhvv, zced__ijakg)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jfs__lwo,
                        njff__nktx, pxd__mcrms)
                    njff__nktx += 1
            return bodo.libs.bool_arr_ext.init_bool_array(denub__chc, jfs__lwo)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            odozh__ujen = []
            for A in arr_list:
                odozh__ujen.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                odozh__ujen), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        xcm__aakc = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        vsvji__ymjh = 'def impl(arr_list):\n'
        vsvji__ymjh += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({xcm__aakc},)), arr_list[0].dtype)
"""
        cbooc__hoy = {}
        exec(vsvji__ymjh, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, cbooc__hoy)
        return cbooc__hoy['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            flsk__yeb = 0
            for A in arr_list:
                flsk__yeb += len(A)
            hssm__vpo = np.empty(flsk__yeb, dtype)
            hvhi__kxd = 0
            for A in arr_list:
                n = len(A)
                hssm__vpo[hvhi__kxd:hvhi__kxd + n] = A
                hvhi__kxd += n
            return hssm__vpo
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(vvk__delae,
        (types.Array, IntegerArrayType)) and isinstance(vvk__delae.dtype,
        types.Integer) for vvk__delae in arr_list.types) and any(isinstance
        (vvk__delae, types.Array) and isinstance(vvk__delae.dtype, types.
        Float) for vvk__delae in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            ocb__sfjgs = []
            for A in arr_list:
                ocb__sfjgs.append(A._data)
            rmumn__fbhzk = bodo.libs.array_kernels.concat(ocb__sfjgs)
            pzdtv__qnjq = bodo.libs.map_arr_ext.init_map_arr(rmumn__fbhzk)
            return pzdtv__qnjq
        return impl_map_arr_list
    for lcouv__dufuv in arr_list:
        if not isinstance(lcouv__dufuv, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(vvk__delae.astype(np.float64) for vvk__delae in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    fumqv__tdt = len(arr_tup.types)
    vsvji__ymjh = 'def f(arr_tup):\n'
    vsvji__ymjh += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(
        fumqv__tdt)), ',' if fumqv__tdt == 1 else '')
    duwf__saj = {}
    exec(vsvji__ymjh, {'np': np}, duwf__saj)
    ukv__yenaq = duwf__saj['f']
    return ukv__yenaq


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    fumqv__tdt = len(arr_tup.types)
    sqrsh__unkt = find_common_np_dtype(arr_tup.types)
    zmeyt__xpx = None
    kwaz__pax = ''
    if isinstance(sqrsh__unkt, types.Integer):
        zmeyt__xpx = bodo.libs.int_arr_ext.IntDtype(sqrsh__unkt)
        kwaz__pax = '.astype(out_dtype, False)'
    vsvji__ymjh = 'def f(arr_tup):\n'
    vsvji__ymjh += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, kwaz__pax) for i in range(fumqv__tdt)), ',' if 
        fumqv__tdt == 1 else '')
    duwf__saj = {}
    exec(vsvji__ymjh, {'bodo': bodo, 'out_dtype': zmeyt__xpx}, duwf__saj)
    dgx__ekwpz = duwf__saj['f']
    return dgx__ekwpz


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, zdaa__bgp = build_set_seen_na(A)
        return len(s) + int(not dropna and zdaa__bgp)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        todcu__obij = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        uiya__crp = len(todcu__obij)
        return bodo.libs.distributed_api.dist_reduce(uiya__crp, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([hdze__tvcw for hdze__tvcw in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        zvknq__tlmw = np.finfo(A.dtype(1).dtype).max
    else:
        zvknq__tlmw = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        hssm__vpo = np.empty(n, A.dtype)
        dqyji__iyr = zvknq__tlmw
        for i in range(n):
            dqyji__iyr = min(dqyji__iyr, A[i])
            hssm__vpo[i] = dqyji__iyr
        return hssm__vpo
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        zvknq__tlmw = np.finfo(A.dtype(1).dtype).min
    else:
        zvknq__tlmw = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        hssm__vpo = np.empty(n, A.dtype)
        dqyji__iyr = zvknq__tlmw
        for i in range(n):
            dqyji__iyr = max(dqyji__iyr, A[i])
            hssm__vpo[i] = dqyji__iyr
        return hssm__vpo
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        txqpb__pqbtn = arr_info_list_to_table([array_to_info(A)])
        eqd__pyoln = 1
        vrxf__oybs = 0
        nkeiw__yzhe = drop_duplicates_table(txqpb__pqbtn, parallel,
            eqd__pyoln, vrxf__oybs, dropna, True)
        hssm__vpo = info_to_array(info_from_table(nkeiw__yzhe, 0), A)
        delete_table(txqpb__pqbtn)
        delete_table(nkeiw__yzhe)
        return hssm__vpo
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    opd__wopr = bodo.utils.typing.to_nullable_type(arr.dtype)
    sio__mrx = index_arr
    qjv__qwrbd = sio__mrx.dtype

    def impl(arr, index_arr):
        n = len(arr)
        wctlh__wqx = init_nested_counts(opd__wopr)
        eyrf__xin = init_nested_counts(qjv__qwrbd)
        for i in range(n):
            dxs__pcaml = index_arr[i]
            if isna(arr, i):
                wctlh__wqx = (wctlh__wqx[0] + 1,) + wctlh__wqx[1:]
                eyrf__xin = add_nested_counts(eyrf__xin, dxs__pcaml)
                continue
            ongp__rtag = arr[i]
            if len(ongp__rtag) == 0:
                wctlh__wqx = (wctlh__wqx[0] + 1,) + wctlh__wqx[1:]
                eyrf__xin = add_nested_counts(eyrf__xin, dxs__pcaml)
                continue
            wctlh__wqx = add_nested_counts(wctlh__wqx, ongp__rtag)
            for pxb__iyif in range(len(ongp__rtag)):
                eyrf__xin = add_nested_counts(eyrf__xin, dxs__pcaml)
        hssm__vpo = bodo.utils.utils.alloc_type(wctlh__wqx[0], opd__wopr,
            wctlh__wqx[1:])
        yjvwl__ghuo = bodo.utils.utils.alloc_type(wctlh__wqx[0], sio__mrx,
            eyrf__xin)
        wzoni__rvn = 0
        for i in range(n):
            if isna(arr, i):
                setna(hssm__vpo, wzoni__rvn)
                yjvwl__ghuo[wzoni__rvn] = index_arr[i]
                wzoni__rvn += 1
                continue
            ongp__rtag = arr[i]
            buuxr__vqbl = len(ongp__rtag)
            if buuxr__vqbl == 0:
                setna(hssm__vpo, wzoni__rvn)
                yjvwl__ghuo[wzoni__rvn] = index_arr[i]
                wzoni__rvn += 1
                continue
            hssm__vpo[wzoni__rvn:wzoni__rvn + buuxr__vqbl] = ongp__rtag
            yjvwl__ghuo[wzoni__rvn:wzoni__rvn + buuxr__vqbl] = index_arr[i]
            wzoni__rvn += buuxr__vqbl
        return hssm__vpo, yjvwl__ghuo
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    opd__wopr = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        wctlh__wqx = init_nested_counts(opd__wopr)
        for i in range(n):
            if isna(arr, i):
                wctlh__wqx = (wctlh__wqx[0] + 1,) + wctlh__wqx[1:]
                exj__rhgqo = 1
            else:
                ongp__rtag = arr[i]
                lbc__auiu = len(ongp__rtag)
                if lbc__auiu == 0:
                    wctlh__wqx = (wctlh__wqx[0] + 1,) + wctlh__wqx[1:]
                    exj__rhgqo = 1
                    continue
                else:
                    wctlh__wqx = add_nested_counts(wctlh__wqx, ongp__rtag)
                    exj__rhgqo = lbc__auiu
            if counts[i] != exj__rhgqo:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        hssm__vpo = bodo.utils.utils.alloc_type(wctlh__wqx[0], opd__wopr,
            wctlh__wqx[1:])
        wzoni__rvn = 0
        for i in range(n):
            if isna(arr, i):
                setna(hssm__vpo, wzoni__rvn)
                wzoni__rvn += 1
                continue
            ongp__rtag = arr[i]
            buuxr__vqbl = len(ongp__rtag)
            if buuxr__vqbl == 0:
                setna(hssm__vpo, wzoni__rvn)
                wzoni__rvn += 1
                continue
            hssm__vpo[wzoni__rvn:wzoni__rvn + buuxr__vqbl] = ongp__rtag
            wzoni__rvn += buuxr__vqbl
        return hssm__vpo
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(rdiw__urwgo) for rdiw__urwgo in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        yhu__cwiaa = 'np.empty(n, np.int64)'
        agsfa__wmp = 'out_arr[i] = 1'
        pvep__gbtw = 'max(len(arr[i]), 1)'
    else:
        yhu__cwiaa = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        agsfa__wmp = 'bodo.libs.array_kernels.setna(out_arr, i)'
        pvep__gbtw = 'len(arr[i])'
    vsvji__ymjh = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {yhu__cwiaa}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {agsfa__wmp}
        else:
            out_arr[i] = {pvep__gbtw}
    return out_arr
    """
    duwf__saj = {}
    exec(vsvji__ymjh, {'bodo': bodo, 'numba': numba, 'np': np}, duwf__saj)
    impl = duwf__saj['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    sio__mrx = index_arr
    qjv__qwrbd = sio__mrx.dtype

    def impl(arr, pat, n, index_arr):
        wpp__zitt = pat is not None and len(pat) > 1
        if wpp__zitt:
            pebm__drl = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        kapbd__jow = len(arr)
        tvcyy__xffbc = 0
        qstlm__odxgp = 0
        eyrf__xin = init_nested_counts(qjv__qwrbd)
        for i in range(kapbd__jow):
            dxs__pcaml = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                tvcyy__xffbc += 1
                eyrf__xin = add_nested_counts(eyrf__xin, dxs__pcaml)
                continue
            if wpp__zitt:
                kotio__btl = pebm__drl.split(arr[i], maxsplit=n)
            else:
                kotio__btl = arr[i].split(pat, n)
            tvcyy__xffbc += len(kotio__btl)
            for s in kotio__btl:
                eyrf__xin = add_nested_counts(eyrf__xin, dxs__pcaml)
                qstlm__odxgp += bodo.libs.str_arr_ext.get_utf8_size(s)
        hssm__vpo = bodo.libs.str_arr_ext.pre_alloc_string_array(tvcyy__xffbc,
            qstlm__odxgp)
        yjvwl__ghuo = bodo.utils.utils.alloc_type(tvcyy__xffbc, sio__mrx,
            eyrf__xin)
        rnrv__eixd = 0
        for zced__ijakg in range(kapbd__jow):
            if isna(arr, zced__ijakg):
                hssm__vpo[rnrv__eixd] = ''
                bodo.libs.array_kernels.setna(hssm__vpo, rnrv__eixd)
                yjvwl__ghuo[rnrv__eixd] = index_arr[zced__ijakg]
                rnrv__eixd += 1
                continue
            if wpp__zitt:
                kotio__btl = pebm__drl.split(arr[zced__ijakg], maxsplit=n)
            else:
                kotio__btl = arr[zced__ijakg].split(pat, n)
            hrk__dpcx = len(kotio__btl)
            hssm__vpo[rnrv__eixd:rnrv__eixd + hrk__dpcx] = kotio__btl
            yjvwl__ghuo[rnrv__eixd:rnrv__eixd + hrk__dpcx] = index_arr[
                zced__ijakg]
            rnrv__eixd += hrk__dpcx
        return hssm__vpo, yjvwl__ghuo
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
            hssm__vpo = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                hssm__vpo[i] = np.nan
            return hssm__vpo
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            uit__bfjbw = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            ozdkk__mmmcy = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(ozdkk__mmmcy, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(uit__bfjbw,
                ozdkk__mmmcy, True)
        return impl_dict
    euvod__jpbbs = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        hssm__vpo = bodo.utils.utils.alloc_type(n, euvod__jpbbs, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(hssm__vpo, i)
        return hssm__vpo
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
    iyrw__guv = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            hssm__vpo = bodo.utils.utils.alloc_type(new_len, iyrw__guv)
            bodo.libs.str_arr_ext.str_copy_ptr(hssm__vpo.ctypes, 0, A.
                ctypes, old_size)
            return hssm__vpo
        return impl_char

    def impl(A, old_size, new_len):
        hssm__vpo = bodo.utils.utils.alloc_type(new_len, iyrw__guv, (-1,))
        hssm__vpo[:old_size] = A[:old_size]
        return hssm__vpo
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    daecr__jeeqf = math.ceil((stop - start) / step)
    return int(max(daecr__jeeqf, 0))


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
    if any(isinstance(hdze__tvcw, types.Complex) for hdze__tvcw in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            ptgl__vsnm = (stop - start) / step
            daecr__jeeqf = math.ceil(ptgl__vsnm.real)
            kysy__tye = math.ceil(ptgl__vsnm.imag)
            isx__psf = int(max(min(kysy__tye, daecr__jeeqf), 0))
            arr = np.empty(isx__psf, dtype)
            for i in numba.parfors.parfor.internal_prange(isx__psf):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            isx__psf = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(isx__psf, dtype)
            for i in numba.parfors.parfor.internal_prange(isx__psf):
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
        sigjx__fyl = arr,
        if not inplace:
            sigjx__fyl = arr.copy(),
        jcnf__ume = bodo.libs.str_arr_ext.to_list_if_immutable_arr(sigjx__fyl)
        zyk__cso = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data, True)
        bodo.libs.timsort.sort(jcnf__ume, 0, n, zyk__cso)
        if not ascending:
            bodo.libs.timsort.reverseRange(jcnf__ume, 0, n, zyk__cso)
        bodo.libs.str_arr_ext.cp_str_list_to_array(sigjx__fyl, jcnf__ume)
        return sigjx__fyl[0]
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
        pzdtv__qnjq = []
        for i in range(n):
            if A[i]:
                pzdtv__qnjq.append(i + offset)
        return np.array(pzdtv__qnjq, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    iyrw__guv = element_type(A)
    if iyrw__guv == types.unicode_type:
        null_value = '""'
    elif iyrw__guv == types.bool_:
        null_value = 'False'
    elif iyrw__guv == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif iyrw__guv == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    rnrv__eixd = 'i'
    iwa__hgh = False
    lzjjb__epej = get_overload_const_str(method)
    if lzjjb__epej in ('ffill', 'pad'):
        eua__gwg = 'n'
        send_right = True
    elif lzjjb__epej in ('backfill', 'bfill'):
        eua__gwg = 'n-1, -1, -1'
        send_right = False
        if iyrw__guv == types.unicode_type:
            rnrv__eixd = '(n - 1) - i'
            iwa__hgh = True
    vsvji__ymjh = 'def impl(A, method, parallel=False):\n'
    vsvji__ymjh += '  A = decode_if_dict_array(A)\n'
    vsvji__ymjh += '  has_last_value = False\n'
    vsvji__ymjh += f'  last_value = {null_value}\n'
    vsvji__ymjh += '  if parallel:\n'
    vsvji__ymjh += '    rank = bodo.libs.distributed_api.get_rank()\n'
    vsvji__ymjh += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    vsvji__ymjh += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    vsvji__ymjh += '  n = len(A)\n'
    vsvji__ymjh += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    vsvji__ymjh += f'  for i in range({eua__gwg}):\n'
    vsvji__ymjh += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    vsvji__ymjh += (
        f'      bodo.libs.array_kernels.setna(out_arr, {rnrv__eixd})\n')
    vsvji__ymjh += '      continue\n'
    vsvji__ymjh += '    s = A[i]\n'
    vsvji__ymjh += '    if bodo.libs.array_kernels.isna(A, i):\n'
    vsvji__ymjh += '      s = last_value\n'
    vsvji__ymjh += f'    out_arr[{rnrv__eixd}] = s\n'
    vsvji__ymjh += '    last_value = s\n'
    vsvji__ymjh += '    has_last_value = True\n'
    if iwa__hgh:
        vsvji__ymjh += '  return out_arr[::-1]\n'
    else:
        vsvji__ymjh += '  return out_arr\n'
    rmcad__ddx = {}
    exec(vsvji__ymjh, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, rmcad__ddx)
    impl = rmcad__ddx['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        odm__czzl = 0
        dzr__eroa = n_pes - 1
        ivfq__qwmhq = np.int32(rank + 1)
        qkjn__hxol = np.int32(rank - 1)
        fizw__qbe = len(in_arr) - 1
        hnt__uedz = -1
        hfb__tvp = -1
    else:
        odm__czzl = n_pes - 1
        dzr__eroa = 0
        ivfq__qwmhq = np.int32(rank - 1)
        qkjn__hxol = np.int32(rank + 1)
        fizw__qbe = 0
        hnt__uedz = len(in_arr)
        hfb__tvp = 1
    snkdj__ffhy = np.int32(bodo.hiframes.rolling.comm_border_tag)
    pzvp__xywdj = np.empty(1, dtype=np.bool_)
    ucnq__usnki = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    qyikq__eqglv = np.empty(1, dtype=np.bool_)
    vkxau__ftc = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    drl__pjcy = False
    cbxi__dfye = null_value
    for i in range(fizw__qbe, hnt__uedz, hfb__tvp):
        if not isna(in_arr, i):
            drl__pjcy = True
            cbxi__dfye = in_arr[i]
            break
    if rank != odm__czzl:
        byp__ssgz = bodo.libs.distributed_api.irecv(pzvp__xywdj, 1,
            qkjn__hxol, snkdj__ffhy, True)
        bodo.libs.distributed_api.wait(byp__ssgz, True)
        zbebb__daea = bodo.libs.distributed_api.irecv(ucnq__usnki, 1,
            qkjn__hxol, snkdj__ffhy, True)
        bodo.libs.distributed_api.wait(zbebb__daea, True)
        ezfvt__agdm = pzvp__xywdj[0]
        ykmp__dgpd = ucnq__usnki[0]
    else:
        ezfvt__agdm = False
        ykmp__dgpd = null_value
    if drl__pjcy:
        qyikq__eqglv[0] = drl__pjcy
        vkxau__ftc[0] = cbxi__dfye
    else:
        qyikq__eqglv[0] = ezfvt__agdm
        vkxau__ftc[0] = ykmp__dgpd
    if rank != dzr__eroa:
        rwsl__qxzft = bodo.libs.distributed_api.isend(qyikq__eqglv, 1,
            ivfq__qwmhq, snkdj__ffhy, True)
        ivepr__fowoh = bodo.libs.distributed_api.isend(vkxau__ftc, 1,
            ivfq__qwmhq, snkdj__ffhy, True)
    return ezfvt__agdm, ykmp__dgpd


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    uwb__ahw = {'axis': axis, 'kind': kind, 'order': order}
    oxo__uye = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', uwb__ahw, oxo__uye, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    iyrw__guv = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            kapbd__jow = len(A)
            hssm__vpo = bodo.utils.utils.alloc_type(kapbd__jow * repeats,
                iyrw__guv, (-1,))
            for i in range(kapbd__jow):
                rnrv__eixd = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for zced__ijakg in range(repeats):
                        bodo.libs.array_kernels.setna(hssm__vpo, rnrv__eixd +
                            zced__ijakg)
                else:
                    hssm__vpo[rnrv__eixd:rnrv__eixd + repeats] = A[i]
            return hssm__vpo
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        kapbd__jow = len(A)
        hssm__vpo = bodo.utils.utils.alloc_type(repeats.sum(), iyrw__guv, (-1,)
            )
        rnrv__eixd = 0
        for i in range(kapbd__jow):
            wah__qsh = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for zced__ijakg in range(wah__qsh):
                    bodo.libs.array_kernels.setna(hssm__vpo, rnrv__eixd +
                        zced__ijakg)
            else:
                hssm__vpo[rnrv__eixd:rnrv__eixd + wah__qsh] = A[i]
            rnrv__eixd += wah__qsh
        return hssm__vpo
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
        xwwf__pgs = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(xwwf__pgs, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        ivu__vza = bodo.libs.array_kernels.concat([A1, A2])
        cuw__cawrn = bodo.libs.array_kernels.unique(ivu__vza)
        return pd.Series(cuw__cawrn).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    uwb__ahw = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    oxo__uye = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', uwb__ahw, oxo__uye, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        tgk__gut = bodo.libs.array_kernels.unique(A1)
        swm__zwrj = bodo.libs.array_kernels.unique(A2)
        ivu__vza = bodo.libs.array_kernels.concat([tgk__gut, swm__zwrj])
        xlrv__lgdv = pd.Series(ivu__vza).sort_values().values
        return slice_array_intersect1d(xlrv__lgdv)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    gvmao__jpb = arr[1:] == arr[:-1]
    return arr[:-1][gvmao__jpb]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    snkdj__ffhy = np.int32(bodo.hiframes.rolling.comm_border_tag)
    iivex__ekbxm = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        arhwg__ygwpr = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32
            (rank - 1), snkdj__ffhy, True)
        bodo.libs.distributed_api.wait(arhwg__ygwpr, True)
    if rank == n_pes - 1:
        return None
    else:
        qhry__tvcna = bodo.libs.distributed_api.irecv(iivex__ekbxm, 1, np.
            int32(rank + 1), snkdj__ffhy, True)
        bodo.libs.distributed_api.wait(qhry__tvcna, True)
        return iivex__ekbxm[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    gvmao__jpb = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            gvmao__jpb[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        cmde__mxube = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == cmde__mxube:
            gvmao__jpb[n - 1] = True
    return gvmao__jpb


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    uwb__ahw = {'assume_unique': assume_unique}
    oxo__uye = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', uwb__ahw, oxo__uye, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        tgk__gut = bodo.libs.array_kernels.unique(A1)
        swm__zwrj = bodo.libs.array_kernels.unique(A2)
        gvmao__jpb = calculate_mask_setdiff1d(tgk__gut, swm__zwrj)
        return pd.Series(tgk__gut[gvmao__jpb]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    gvmao__jpb = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        gvmao__jpb &= A1 != A2[i]
    return gvmao__jpb


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    uwb__ahw = {'retstep': retstep, 'axis': axis}
    oxo__uye = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', uwb__ahw, oxo__uye, 'numpy')
    tmzj__dyui = False
    if is_overload_none(dtype):
        iyrw__guv = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            tmzj__dyui = True
        iyrw__guv = numba.np.numpy_support.as_dtype(dtype).type
    if tmzj__dyui:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            anb__ezwhi = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hssm__vpo = np.empty(num, iyrw__guv)
            for i in numba.parfors.parfor.internal_prange(num):
                hssm__vpo[i] = iyrw__guv(np.floor(start + i * anb__ezwhi))
            return hssm__vpo
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            anb__ezwhi = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            hssm__vpo = np.empty(num, iyrw__guv)
            for i in numba.parfors.parfor.internal_prange(num):
                hssm__vpo[i] = iyrw__guv(start + i * anb__ezwhi)
            return hssm__vpo
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
        fumqv__tdt = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                fumqv__tdt += A[i] == val
        return fumqv__tdt > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    uwb__ahw = {'axis': axis, 'out': out, 'keepdims': keepdims}
    oxo__uye = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', uwb__ahw, oxo__uye, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        fumqv__tdt = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                fumqv__tdt += int(bool(A[i]))
        return fumqv__tdt > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    uwb__ahw = {'axis': axis, 'out': out, 'keepdims': keepdims}
    oxo__uye = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', uwb__ahw, oxo__uye, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        fumqv__tdt = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                fumqv__tdt += int(bool(A[i]))
        return fumqv__tdt == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    uwb__ahw = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    oxo__uye = {'out': None, 'where': True, 'casting': 'same_kind', 'order':
        'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', uwb__ahw, oxo__uye, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        pmd__mtxt = np.promote_types(numba.np.numpy_support.as_dtype(A.
            dtype), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            hssm__vpo = np.empty(n, pmd__mtxt)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(hssm__vpo, i)
                    continue
                hssm__vpo[i] = np_cbrt_scalar(A[i], pmd__mtxt)
            return hssm__vpo
        return impl_arr
    pmd__mtxt = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, pmd__mtxt)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    uih__oibe = x < 0
    if uih__oibe:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if uih__oibe:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    hlvx__gmivj = isinstance(tup, (types.BaseTuple, types.List))
    dwcvg__ogee = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for lcouv__dufuv in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(
                lcouv__dufuv, 'numpy.hstack()')
            hlvx__gmivj = hlvx__gmivj and bodo.utils.utils.is_array_typ(
                lcouv__dufuv, False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        hlvx__gmivj = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif dwcvg__ogee:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        ljvze__ncg = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for lcouv__dufuv in ljvze__ncg.types:
            dwcvg__ogee = dwcvg__ogee and bodo.utils.utils.is_array_typ(
                lcouv__dufuv, False)
    if not (hlvx__gmivj or dwcvg__ogee):
        return
    if dwcvg__ogee:

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
    uwb__ahw = {'check_valid': check_valid, 'tol': tol}
    oxo__uye = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', uwb__ahw,
        oxo__uye, 'numpy')
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
        pyf__lad = mean.shape[0]
        gtust__nck = size, pyf__lad
        qquai__jdt = np.random.standard_normal(gtust__nck)
        cov = cov.astype(np.float64)
        khdj__ial, s, oym__ybk = np.linalg.svd(cov)
        res = np.dot(qquai__jdt, np.sqrt(s).reshape(pyf__lad, 1) * oym__ybk)
        dha__cbo = res + mean
        return dha__cbo
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
            nrim__glnpj = bodo.hiframes.series_kernels._get_type_max_value(arr)
            mstvi__ptc = typing.builtins.IndexValue(-1, nrim__glnpj)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xog__wapg = typing.builtins.IndexValue(i, arr[i])
                mstvi__ptc = min(mstvi__ptc, xog__wapg)
            return mstvi__ptc.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        dae__ilxa = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            xbnkh__bvg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nrim__glnpj = dae__ilxa(len(arr.dtype.categories) + 1)
            mstvi__ptc = typing.builtins.IndexValue(-1, nrim__glnpj)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xog__wapg = typing.builtins.IndexValue(i, xbnkh__bvg[i])
                mstvi__ptc = min(mstvi__ptc, xog__wapg)
            return mstvi__ptc.index
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
            nrim__glnpj = bodo.hiframes.series_kernels._get_type_min_value(arr)
            mstvi__ptc = typing.builtins.IndexValue(-1, nrim__glnpj)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xog__wapg = typing.builtins.IndexValue(i, arr[i])
                mstvi__ptc = max(mstvi__ptc, xog__wapg)
            return mstvi__ptc.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        dae__ilxa = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            xbnkh__bvg = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            nrim__glnpj = dae__ilxa(-1)
            mstvi__ptc = typing.builtins.IndexValue(-1, nrim__glnpj)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                xog__wapg = typing.builtins.IndexValue(i, xbnkh__bvg[i])
                mstvi__ptc = max(mstvi__ptc, xog__wapg)
            return mstvi__ptc.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
