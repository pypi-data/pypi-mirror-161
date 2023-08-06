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
        gzxy__sxli = arr.dtype('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr[ind] = gzxy__sxli
        return _setnan_impl
    if isinstance(arr, DatetimeArrayType):
        gzxy__sxli = bodo.datetime64ns('NaT')

        def _setnan_impl(arr, ind, int_nan_const=0):
            arr._data[ind] = gzxy__sxli
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
            ofgy__khyz = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ofgy__khyz[ind + 1] = ofgy__khyz[ind]
            bodo.libs.int_arr_ext.set_bit_to_arr(bodo.libs.
                array_item_arr_ext.get_null_bitmap(arr._data), ind, 0)
        return impl_binary_arr
    if isinstance(arr, bodo.libs.array_item_arr_ext.ArrayItemArrayType):

        def impl_arr_item(arr, ind, int_nan_const=0):
            ofgy__khyz = bodo.libs.array_item_arr_ext.get_offsets(arr)
            ofgy__khyz[ind + 1] = ofgy__khyz[ind]
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
    otdu__dnz = arr_tup.count
    pts__ytqz = 'def f(arr_tup, ind, int_nan_const=0):\n'
    for i in range(otdu__dnz):
        pts__ytqz += '  setna(arr_tup[{}], ind, int_nan_const)\n'.format(i)
    pts__ytqz += '  return\n'
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'setna': setna}, wrfqb__qtlok)
    impl = wrfqb__qtlok['f']
    return impl


def setna_slice(arr, s):
    arr[s] = np.nan


@overload(setna_slice, no_unliteral=True)
def overload_setna_slice(arr, s):

    def impl(arr, s):
        kmfir__bmrph = numba.cpython.unicode._normalize_slice(s, len(arr))
        for i in range(kmfir__bmrph.start, kmfir__bmrph.stop, kmfir__bmrph.step
            ):
            setna(arr, i)
    return impl


@numba.generated_jit
def first_last_valid_index(arr, index_arr, is_first=True, parallel=False):
    is_first = get_overload_const_bool(is_first)
    if is_first:
        bfkj__pwoly = 'n'
        vbozd__xqyel = 'n_pes'
        nrvat__ecxvm = 'min_op'
    else:
        bfkj__pwoly = 'n-1, -1, -1'
        vbozd__xqyel = '-1'
        nrvat__ecxvm = 'max_op'
    pts__ytqz = f"""def impl(arr, index_arr, is_first=True, parallel=False):
    n = len(arr)
    index_value = index_arr[0]
    has_valid = False
    loc_valid_rank = -1
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        loc_valid_rank = {vbozd__xqyel}
    for i in range({bfkj__pwoly}):
        if not isna(arr, i):
            if parallel:
                loc_valid_rank = rank
            index_value = index_arr[i]
            has_valid = True
            break
    if parallel:
        possible_valid_rank = np.int32(bodo.libs.distributed_api.dist_reduce(loc_valid_rank, {nrvat__ecxvm}))
        if possible_valid_rank != {vbozd__xqyel}:
            has_valid = True
            index_value = bodo.libs.distributed_api.bcast_scalar(index_value, possible_valid_rank)
    return has_valid, box_if_dt64(index_value)

    """
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'np': np, 'bodo': bodo, 'isna': isna, 'max_op': max_op,
        'min_op': min_op, 'box_if_dt64': bodo.utils.conversion.box_if_dt64},
        wrfqb__qtlok)
    impl = wrfqb__qtlok['impl']
    return impl


ll.add_symbol('median_series_computation', quantile_alg.
    median_series_computation)
_median_series_computation = types.ExternalFunction('median_series_computation'
    , types.void(types.voidptr, bodo.libs.array.array_info_type, types.
    bool_, types.bool_))


@numba.njit
def median_series_computation(res, arr, is_parallel, skipna):
    zzqp__uivib = array_to_info(arr)
    _median_series_computation(res, zzqp__uivib, is_parallel, skipna)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(zzqp__uivib)


ll.add_symbol('autocorr_series_computation', quantile_alg.
    autocorr_series_computation)
_autocorr_series_computation = types.ExternalFunction(
    'autocorr_series_computation', types.void(types.voidptr, bodo.libs.
    array.array_info_type, types.int64, types.bool_))


@numba.njit
def autocorr_series_computation(res, arr, lag, is_parallel):
    zzqp__uivib = array_to_info(arr)
    _autocorr_series_computation(res, zzqp__uivib, lag, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(zzqp__uivib)


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
    zzqp__uivib = array_to_info(arr)
    _compute_series_monotonicity(res, zzqp__uivib, inc_dec, is_parallel)
    check_and_propagate_cpp_exception()
    delete_info_decref_array(zzqp__uivib)


@numba.njit
def series_monotonicity(arr, inc_dec, parallel=False):
    res = np.empty(1, types.float64)
    series_monotonicity_call(res.ctypes, arr, inc_dec, parallel)
    scdc__kpc = res[0] > 0.5
    return scdc__kpc


@numba.generated_jit(nopython=True)
def get_valid_entries_from_date_offset(index_arr, offset, initial_date,
    is_last, is_parallel=False):
    if get_overload_const_bool(is_last):
        tyyl__hmb = '-'
        ightv__cvc = 'index_arr[0] > threshhold_date'
        bfkj__pwoly = '1, n+1'
        apbv__smk = 'index_arr[-i] <= threshhold_date'
        kpai__ipce = 'i - 1'
    else:
        tyyl__hmb = '+'
        ightv__cvc = 'index_arr[-1] < threshhold_date'
        bfkj__pwoly = 'n'
        apbv__smk = 'index_arr[i] >= threshhold_date'
        kpai__ipce = 'i'
    pts__ytqz = (
        'def impl(index_arr, offset, initial_date, is_last, is_parallel=False):\n'
        )
    if types.unliteral(offset) == types.unicode_type:
        pts__ytqz += (
            '  with numba.objmode(threshhold_date=bodo.pd_timestamp_type):\n')
        pts__ytqz += (
            '    date_offset = pd.tseries.frequencies.to_offset(offset)\n')
        if not get_overload_const_bool(is_last):
            pts__ytqz += """    if not isinstance(date_offset, pd._libs.tslibs.Tick) and date_offset.is_on_offset(index_arr[0]):
"""
            pts__ytqz += (
                '      threshhold_date = initial_date - date_offset.base + date_offset\n'
                )
            pts__ytqz += '    else:\n'
            pts__ytqz += '      threshhold_date = initial_date + date_offset\n'
        else:
            pts__ytqz += (
                f'    threshhold_date = initial_date {tyyl__hmb} date_offset\n'
                )
    else:
        pts__ytqz += f'  threshhold_date = initial_date {tyyl__hmb} offset\n'
    pts__ytqz += '  local_valid = 0\n'
    pts__ytqz += f'  n = len(index_arr)\n'
    pts__ytqz += f'  if n:\n'
    pts__ytqz += f'    if {ightv__cvc}:\n'
    pts__ytqz += '      loc_valid = n\n'
    pts__ytqz += '    else:\n'
    pts__ytqz += f'      for i in range({bfkj__pwoly}):\n'
    pts__ytqz += f'        if {apbv__smk}:\n'
    pts__ytqz += f'          loc_valid = {kpai__ipce}\n'
    pts__ytqz += '          break\n'
    pts__ytqz += '  if is_parallel:\n'
    pts__ytqz += (
        '    total_valid = bodo.libs.distributed_api.dist_reduce(loc_valid, sum_op)\n'
        )
    pts__ytqz += '    return total_valid\n'
    pts__ytqz += '  else:\n'
    pts__ytqz += '    return loc_valid\n'
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'bodo': bodo, 'pd': pd, 'numba': numba, 'sum_op':
        sum_op}, wrfqb__qtlok)
    return wrfqb__qtlok['impl']


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
    ycgkp__lobla = numba_to_c_type(sig.args[0].dtype)
    hreg__qsydo = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), ycgkp__lobla))
    wucfm__azrtm = args[0]
    iukku__rrle = sig.args[0]
    if isinstance(iukku__rrle, (IntegerArrayType, BooleanArrayType)):
        wucfm__azrtm = cgutils.create_struct_proxy(iukku__rrle)(context,
            builder, wucfm__azrtm).data
        iukku__rrle = types.Array(iukku__rrle.dtype, 1, 'C')
    assert iukku__rrle.ndim == 1
    arr = make_array(iukku__rrle)(context, builder, wucfm__azrtm)
    cug__bsntq = builder.extract_value(arr.shape, 0)
    ktdg__vzsst = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        cug__bsntq, args[1], builder.load(hreg__qsydo)]
    bulek__wjpo = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        DoubleType(), lir.IntType(32)]
    kqg__arbg = lir.FunctionType(lir.DoubleType(), bulek__wjpo)
    yercp__aevfr = cgutils.get_or_insert_function(builder.module, kqg__arbg,
        name='quantile_sequential')
    cctd__zcg = builder.call(yercp__aevfr, ktdg__vzsst)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return cctd__zcg


@lower_builtin(quantile_parallel, types.Array, types.float64, types.intp)
@lower_builtin(quantile_parallel, IntegerArrayType, types.float64, types.intp)
@lower_builtin(quantile_parallel, BooleanArrayType, types.float64, types.intp)
def lower_dist_quantile_parallel(context, builder, sig, args):
    ycgkp__lobla = numba_to_c_type(sig.args[0].dtype)
    hreg__qsydo = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(32), ycgkp__lobla))
    wucfm__azrtm = args[0]
    iukku__rrle = sig.args[0]
    if isinstance(iukku__rrle, (IntegerArrayType, BooleanArrayType)):
        wucfm__azrtm = cgutils.create_struct_proxy(iukku__rrle)(context,
            builder, wucfm__azrtm).data
        iukku__rrle = types.Array(iukku__rrle.dtype, 1, 'C')
    assert iukku__rrle.ndim == 1
    arr = make_array(iukku__rrle)(context, builder, wucfm__azrtm)
    cug__bsntq = builder.extract_value(arr.shape, 0)
    if len(args) == 3:
        bny__fwvd = args[2]
    else:
        bny__fwvd = cug__bsntq
    ktdg__vzsst = [builder.bitcast(arr.data, lir.IntType(8).as_pointer()),
        cug__bsntq, bny__fwvd, args[1], builder.load(hreg__qsydo)]
    bulek__wjpo = [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
        IntType(64), lir.DoubleType(), lir.IntType(32)]
    kqg__arbg = lir.FunctionType(lir.DoubleType(), bulek__wjpo)
    yercp__aevfr = cgutils.get_or_insert_function(builder.module, kqg__arbg,
        name='quantile_parallel')
    cctd__zcg = builder.call(yercp__aevfr, ktdg__vzsst)
    bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context, builder
        )
    return cctd__zcg


@numba.generated_jit(nopython=True)
def _rank_detect_ties(arr):

    def impl(arr):
        rvldr__rbecc = np.nonzero(pd.isna(arr))[0]
        hjyc__rmumu = arr[1:] != arr[:-1]
        hjyc__rmumu[pd.isna(hjyc__rmumu)] = False
        ieflk__sagz = hjyc__rmumu.astype(np.bool_)
        hcmjr__pmqqq = np.concatenate((np.array([True]), ieflk__sagz))
        if rvldr__rbecc.size:
            ifq__vupk, dcb__ziulz = rvldr__rbecc[0], rvldr__rbecc[1:]
            hcmjr__pmqqq[ifq__vupk] = True
            if dcb__ziulz.size:
                hcmjr__pmqqq[dcb__ziulz] = False
                if dcb__ziulz[-1] + 1 < hcmjr__pmqqq.size:
                    hcmjr__pmqqq[dcb__ziulz[-1] + 1] = True
            elif ifq__vupk + 1 < hcmjr__pmqqq.size:
                hcmjr__pmqqq[ifq__vupk + 1] = True
        return hcmjr__pmqqq
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
    pts__ytqz = (
        "def impl(arr, method='average', na_option='keep', ascending=True, pct=False):\n"
        )
    pts__ytqz += '  na_idxs = pd.isna(arr)\n'
    pts__ytqz += '  sorter = bodo.hiframes.series_impl.argsort(arr)\n'
    pts__ytqz += '  nas = sum(na_idxs)\n'
    if not ascending:
        pts__ytqz += '  if nas and nas < (sorter.size - 1):\n'
        pts__ytqz += '    sorter[:-nas] = sorter[-(nas + 1)::-1]\n'
        pts__ytqz += '  else:\n'
        pts__ytqz += '    sorter = sorter[::-1]\n'
    if na_option == 'top':
        pts__ytqz += (
            '  sorter = np.concatenate((sorter[-nas:], sorter[:-nas]))\n')
    pts__ytqz += '  inv = np.empty(sorter.size, dtype=np.intp)\n'
    pts__ytqz += '  inv[sorter] = np.arange(sorter.size)\n'
    if method == 'first':
        pts__ytqz += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
        pts__ytqz += '    inv,\n'
        pts__ytqz += '    new_dtype=np.float64,\n'
        pts__ytqz += '    copy=True,\n'
        pts__ytqz += '    nan_to_str=False,\n'
        pts__ytqz += '    from_series=True,\n'
        pts__ytqz += '    ) + 1\n'
    else:
        pts__ytqz += '  arr = arr[sorter]\n'
        pts__ytqz += '  obs = bodo.libs.array_kernels._rank_detect_ties(arr)\n'
        pts__ytqz += '  dense = obs.cumsum()[inv]\n'
        if method == 'dense':
            pts__ytqz += '  ret = bodo.utils.conversion.fix_arr_dtype(\n'
            pts__ytqz += '    dense,\n'
            pts__ytqz += '    new_dtype=np.float64,\n'
            pts__ytqz += '    copy=True,\n'
            pts__ytqz += '    nan_to_str=False,\n'
            pts__ytqz += '    from_series=True,\n'
            pts__ytqz += '  )\n'
        else:
            pts__ytqz += (
                '  count = np.concatenate((np.nonzero(obs)[0], np.array([len(obs)])))\n'
                )
            pts__ytqz += """  count_float = bodo.utils.conversion.fix_arr_dtype(count, new_dtype=np.float64, copy=True, nan_to_str=False, from_series=True)
"""
            if method == 'max':
                pts__ytqz += '  ret = count_float[dense]\n'
            elif method == 'min':
                pts__ytqz += '  ret = count_float[dense - 1] + 1\n'
            else:
                pts__ytqz += (
                    '  ret = 0.5 * (count_float[dense] + count_float[dense - 1] + 1)\n'
                    )
    if pct:
        if method == 'dense':
            if na_option == 'keep':
                pts__ytqz += '  ret[na_idxs] = -1\n'
            pts__ytqz += '  div_val = np.max(ret)\n'
        elif na_option == 'keep':
            pts__ytqz += '  div_val = arr.size - nas\n'
        else:
            pts__ytqz += '  div_val = arr.size\n'
        pts__ytqz += '  for i in range(len(ret)):\n'
        pts__ytqz += '    ret[i] = ret[i] / div_val\n'
    if na_option == 'keep':
        pts__ytqz += '  ret[na_idxs] = np.nan\n'
    pts__ytqz += '  return ret\n'
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'np': np, 'pd': pd, 'bodo': bodo}, wrfqb__qtlok)
    return wrfqb__qtlok['impl']


@numba.njit
def min_heapify(arr, ind_arr, n, start, cmp_f):
    danyf__bnp = start
    uxyj__vxxvn = 2 * start + 1
    wrd__gbz = 2 * start + 2
    if uxyj__vxxvn < n and not cmp_f(arr[uxyj__vxxvn], arr[danyf__bnp]):
        danyf__bnp = uxyj__vxxvn
    if wrd__gbz < n and not cmp_f(arr[wrd__gbz], arr[danyf__bnp]):
        danyf__bnp = wrd__gbz
    if danyf__bnp != start:
        arr[start], arr[danyf__bnp] = arr[danyf__bnp], arr[start]
        ind_arr[start], ind_arr[danyf__bnp] = ind_arr[danyf__bnp], ind_arr[
            start]
        min_heapify(arr, ind_arr, n, danyf__bnp, cmp_f)


def select_k_nonan(A, index_arr, m, k):
    return A[:k]


@overload(select_k_nonan, no_unliteral=True)
def select_k_nonan_overload(A, index_arr, m, k):
    dtype = A.dtype
    if isinstance(dtype, types.Integer):
        return lambda A, index_arr, m, k: (A[:k].copy(), index_arr[:k].copy
            (), k)

    def select_k_nonan_float(A, index_arr, m, k):
        hisw__ucye = np.empty(k, A.dtype)
        svffp__rigwr = np.empty(k, index_arr.dtype)
        i = 0
        ind = 0
        while i < m and ind < k:
            if not bodo.libs.array_kernels.isna(A, i):
                hisw__ucye[ind] = A[i]
                svffp__rigwr[ind] = index_arr[i]
                ind += 1
            i += 1
        if ind < k:
            hisw__ucye = hisw__ucye[:ind]
            svffp__rigwr = svffp__rigwr[:ind]
        return hisw__ucye, svffp__rigwr, i
    return select_k_nonan_float


@numba.njit
def nlargest(A, index_arr, k, is_largest, cmp_f):
    m = len(A)
    if k == 0:
        return A[:0], index_arr[:0]
    if k >= m:
        wdps__yow = np.sort(A)
        lsdf__seqq = index_arr[np.argsort(A)]
        cojpp__oheky = pd.Series(wdps__yow).notna().values
        wdps__yow = wdps__yow[cojpp__oheky]
        lsdf__seqq = lsdf__seqq[cojpp__oheky]
        if is_largest:
            wdps__yow = wdps__yow[::-1]
            lsdf__seqq = lsdf__seqq[::-1]
        return np.ascontiguousarray(wdps__yow), np.ascontiguousarray(lsdf__seqq
            )
    hisw__ucye, svffp__rigwr, start = select_k_nonan(A, index_arr, m, k)
    svffp__rigwr = svffp__rigwr[hisw__ucye.argsort()]
    hisw__ucye.sort()
    if not is_largest:
        hisw__ucye = np.ascontiguousarray(hisw__ucye[::-1])
        svffp__rigwr = np.ascontiguousarray(svffp__rigwr[::-1])
    for i in range(start, m):
        if cmp_f(A[i], hisw__ucye[0]):
            hisw__ucye[0] = A[i]
            svffp__rigwr[0] = index_arr[i]
            min_heapify(hisw__ucye, svffp__rigwr, k, 0, cmp_f)
    svffp__rigwr = svffp__rigwr[hisw__ucye.argsort()]
    hisw__ucye.sort()
    if is_largest:
        hisw__ucye = hisw__ucye[::-1]
        svffp__rigwr = svffp__rigwr[::-1]
    return np.ascontiguousarray(hisw__ucye), np.ascontiguousarray(svffp__rigwr)


@numba.njit
def nlargest_parallel(A, I, k, is_largest, cmp_f):
    yuhq__uhwb = bodo.libs.distributed_api.get_rank()
    cab__mvso, lcxo__vsx = nlargest(A, I, k, is_largest, cmp_f)
    ofe__unkg = bodo.libs.distributed_api.gatherv(cab__mvso)
    hkr__rsfy = bodo.libs.distributed_api.gatherv(lcxo__vsx)
    if yuhq__uhwb == MPI_ROOT:
        res, xdy__ljnz = nlargest(ofe__unkg, hkr__rsfy, k, is_largest, cmp_f)
    else:
        res = np.empty(k, A.dtype)
        xdy__ljnz = np.empty(k, I.dtype)
    bodo.libs.distributed_api.bcast(res)
    bodo.libs.distributed_api.bcast(xdy__ljnz)
    return res, xdy__ljnz


@numba.njit(no_cpython_wrapper=True, cache=True)
def nancorr(mat, cov=0, minpv=1, parallel=False):
    qfpem__ujazx, pfyup__qcetx = mat.shape
    kosmt__lrsz = np.empty((pfyup__qcetx, pfyup__qcetx), dtype=np.float64)
    for fkbx__pnkid in range(pfyup__qcetx):
        for oqfy__zeim in range(fkbx__pnkid + 1):
            yfvt__ywb = 0
            zalh__jhp = ooud__wuwg = pnhhu__upjg = omlj__zojlk = 0.0
            for i in range(qfpem__ujazx):
                if np.isfinite(mat[i, fkbx__pnkid]) and np.isfinite(mat[i,
                    oqfy__zeim]):
                    lep__yzfm = mat[i, fkbx__pnkid]
                    zhg__obijw = mat[i, oqfy__zeim]
                    yfvt__ywb += 1
                    pnhhu__upjg += lep__yzfm
                    omlj__zojlk += zhg__obijw
            if parallel:
                yfvt__ywb = bodo.libs.distributed_api.dist_reduce(yfvt__ywb,
                    sum_op)
                pnhhu__upjg = bodo.libs.distributed_api.dist_reduce(pnhhu__upjg
                    , sum_op)
                omlj__zojlk = bodo.libs.distributed_api.dist_reduce(omlj__zojlk
                    , sum_op)
            if yfvt__ywb < minpv:
                kosmt__lrsz[fkbx__pnkid, oqfy__zeim] = kosmt__lrsz[
                    oqfy__zeim, fkbx__pnkid] = np.nan
            else:
                mtcop__pjkt = pnhhu__upjg / yfvt__ywb
                iuqy__bmp = omlj__zojlk / yfvt__ywb
                pnhhu__upjg = 0.0
                for i in range(qfpem__ujazx):
                    if np.isfinite(mat[i, fkbx__pnkid]) and np.isfinite(mat
                        [i, oqfy__zeim]):
                        lep__yzfm = mat[i, fkbx__pnkid] - mtcop__pjkt
                        zhg__obijw = mat[i, oqfy__zeim] - iuqy__bmp
                        pnhhu__upjg += lep__yzfm * zhg__obijw
                        zalh__jhp += lep__yzfm * lep__yzfm
                        ooud__wuwg += zhg__obijw * zhg__obijw
                if parallel:
                    pnhhu__upjg = bodo.libs.distributed_api.dist_reduce(
                        pnhhu__upjg, sum_op)
                    zalh__jhp = bodo.libs.distributed_api.dist_reduce(zalh__jhp
                        , sum_op)
                    ooud__wuwg = bodo.libs.distributed_api.dist_reduce(
                        ooud__wuwg, sum_op)
                teund__wvel = yfvt__ywb - 1.0 if cov else sqrt(zalh__jhp *
                    ooud__wuwg)
                if teund__wvel != 0.0:
                    kosmt__lrsz[fkbx__pnkid, oqfy__zeim] = kosmt__lrsz[
                        oqfy__zeim, fkbx__pnkid] = pnhhu__upjg / teund__wvel
                else:
                    kosmt__lrsz[fkbx__pnkid, oqfy__zeim] = kosmt__lrsz[
                        oqfy__zeim, fkbx__pnkid] = np.nan
    return kosmt__lrsz


@numba.generated_jit(nopython=True)
def duplicated(data, parallel=False):
    n = len(data)
    if n == 0:
        return lambda data, parallel=False: np.empty(0, dtype=np.bool_)
    lkcfx__dbt = n != 1
    pts__ytqz = 'def impl(data, parallel=False):\n'
    pts__ytqz += '  if parallel:\n'
    nguzi__rkov = ', '.join(f'array_to_info(data[{i}])' for i in range(n))
    pts__ytqz += f'    cpp_table = arr_info_list_to_table([{nguzi__rkov}])\n'
    pts__ytqz += (
        f'    out_cpp_table = bodo.libs.array.shuffle_table(cpp_table, {n}, parallel, 1)\n'
        )
    pym__hykbh = ', '.join(
        f'info_to_array(info_from_table(out_cpp_table, {i}), data[{i}])' for
        i in range(n))
    pts__ytqz += f'    data = ({pym__hykbh},)\n'
    pts__ytqz += (
        '    shuffle_info = bodo.libs.array.get_shuffle_info(out_cpp_table)\n')
    pts__ytqz += '    bodo.libs.array.delete_table(out_cpp_table)\n'
    pts__ytqz += '    bodo.libs.array.delete_table(cpp_table)\n'
    pts__ytqz += '  n = len(data[0])\n'
    pts__ytqz += '  out = np.empty(n, np.bool_)\n'
    pts__ytqz += '  uniqs = dict()\n'
    if lkcfx__dbt:
        pts__ytqz += '  for i in range(n):\n'
        nxbc__hrru = ', '.join(f'data[{i}][i]' for i in range(n))
        pzg__pxfhs = ',  '.join(
            f'bodo.libs.array_kernels.isna(data[{i}], i)' for i in range(n))
        pts__ytqz += f"""    val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({nxbc__hrru},), ({pzg__pxfhs},))
"""
        pts__ytqz += '    if val in uniqs:\n'
        pts__ytqz += '      out[i] = True\n'
        pts__ytqz += '    else:\n'
        pts__ytqz += '      out[i] = False\n'
        pts__ytqz += '      uniqs[val] = 0\n'
    else:
        pts__ytqz += '  data = data[0]\n'
        pts__ytqz += '  hasna = False\n'
        pts__ytqz += '  for i in range(n):\n'
        pts__ytqz += '    if bodo.libs.array_kernels.isna(data, i):\n'
        pts__ytqz += '      out[i] = hasna\n'
        pts__ytqz += '      hasna = True\n'
        pts__ytqz += '    else:\n'
        pts__ytqz += '      val = data[i]\n'
        pts__ytqz += '      if val in uniqs:\n'
        pts__ytqz += '        out[i] = True\n'
        pts__ytqz += '      else:\n'
        pts__ytqz += '        out[i] = False\n'
        pts__ytqz += '        uniqs[val] = 0\n'
    pts__ytqz += '  if parallel:\n'
    pts__ytqz += (
        '    out = bodo.hiframes.pd_groupby_ext.reverse_shuffle(out, shuffle_info)\n'
        )
    pts__ytqz += '  return out\n'
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'bodo': bodo, 'np': np, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table}, wrfqb__qtlok)
    impl = wrfqb__qtlok['impl']
    return impl


def sample_table_operation(data, ind_arr, n, frac, replace, parallel=False):
    return data, ind_arr


@overload(sample_table_operation, no_unliteral=True)
def overload_sample_table_operation(data, ind_arr, n, frac, replace,
    parallel=False):
    otdu__dnz = len(data)
    pts__ytqz = 'def impl(data, ind_arr, n, frac, replace, parallel=False):\n'
    pts__ytqz += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        otdu__dnz)))
    pts__ytqz += '  table_total = arr_info_list_to_table(info_list_total)\n'
    pts__ytqz += (
        '  out_table = sample_table(table_total, n, frac, replace, parallel)\n'
        .format(otdu__dnz))
    for xdst__kvu in range(otdu__dnz):
        pts__ytqz += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(xdst__kvu, xdst__kvu, xdst__kvu))
    pts__ytqz += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(otdu__dnz))
    pts__ytqz += '  delete_table(out_table)\n'
    pts__ytqz += '  delete_table(table_total)\n'
    pts__ytqz += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(otdu__dnz)))
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'sample_table': sample_table, 'arr_info_list_to_table':
        arr_info_list_to_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays}, wrfqb__qtlok
        )
    impl = wrfqb__qtlok['impl']
    return impl


def drop_duplicates(data, ind_arr, ncols, parallel=False):
    return data, ind_arr


@overload(drop_duplicates, no_unliteral=True)
def overload_drop_duplicates(data, ind_arr, ncols, parallel=False):
    otdu__dnz = len(data)
    pts__ytqz = 'def impl(data, ind_arr, ncols, parallel=False):\n'
    pts__ytqz += '  info_list_total = [{}, array_to_info(ind_arr)]\n'.format(
        ', '.join('array_to_info(data[{}])'.format(x) for x in range(
        otdu__dnz)))
    pts__ytqz += '  table_total = arr_info_list_to_table(info_list_total)\n'
    pts__ytqz += '  keep_i = 0\n'
    pts__ytqz += """  out_table = drop_duplicates_table(table_total, parallel, ncols, keep_i, False, True)
"""
    for xdst__kvu in range(otdu__dnz):
        pts__ytqz += (
            '  out_arr_{} = info_to_array(info_from_table(out_table, {}), data[{}])\n'
            .format(xdst__kvu, xdst__kvu, xdst__kvu))
    pts__ytqz += (
        '  out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)\n'
        .format(otdu__dnz))
    pts__ytqz += '  delete_table(out_table)\n'
    pts__ytqz += '  delete_table(table_total)\n'
    pts__ytqz += '  return ({},), out_arr_index\n'.format(', '.join(
        'out_arr_{}'.format(i) for i in range(otdu__dnz)))
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'np': np, 'bodo': bodo, 'array_to_info': array_to_info,
        'drop_duplicates_table': drop_duplicates_table,
        'arr_info_list_to_table': arr_info_list_to_table, 'info_from_table':
        info_from_table, 'info_to_array': info_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays}, wrfqb__qtlok)
    impl = wrfqb__qtlok['impl']
    return impl


def drop_duplicates_array(data_arr, parallel=False):
    return data_arr


@overload(drop_duplicates_array, no_unliteral=True)
def overload_drop_duplicates_array(data_arr, parallel=False):

    def impl(data_arr, parallel=False):
        hqmg__lzbq = [array_to_info(data_arr)]
        snt__cjgum = arr_info_list_to_table(hqmg__lzbq)
        munw__yprp = 0
        juocg__dykya = drop_duplicates_table(snt__cjgum, parallel, 1,
            munw__yprp, False, True)
        rpqf__whqbv = info_to_array(info_from_table(juocg__dykya, 0), data_arr)
        delete_table(juocg__dykya)
        delete_table(snt__cjgum)
        return rpqf__whqbv
    return impl


def dropna(data, how, thresh, subset, parallel=False):
    return data


@overload(dropna, no_unliteral=True)
def overload_dropna(data, how, thresh, subset):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.dropna()')
    map__ssmm = len(data.types)
    cadas__cdtn = [('out' + str(i)) for i in range(map__ssmm)]
    eiqz__mdtmd = get_overload_const_list(subset)
    how = get_overload_const_str(how)
    ahdyd__cgmkl = ['isna(data[{}], i)'.format(i) for i in eiqz__mdtmd]
    xsqfl__rss = 'not ({})'.format(' or '.join(ahdyd__cgmkl))
    if not is_overload_none(thresh):
        xsqfl__rss = '(({}) <= ({}) - thresh)'.format(' + '.join(
            ahdyd__cgmkl), map__ssmm - 1)
    elif how == 'all':
        xsqfl__rss = 'not ({})'.format(' and '.join(ahdyd__cgmkl))
    pts__ytqz = 'def _dropna_imp(data, how, thresh, subset):\n'
    pts__ytqz += '  old_len = len(data[0])\n'
    pts__ytqz += '  new_len = 0\n'
    pts__ytqz += '  for i in range(old_len):\n'
    pts__ytqz += '    if {}:\n'.format(xsqfl__rss)
    pts__ytqz += '      new_len += 1\n'
    for i, out in enumerate(cadas__cdtn):
        if isinstance(data[i], bodo.CategoricalArrayType):
            pts__ytqz += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, data[{1}], (-1,))\n'
                .format(out, i))
        else:
            pts__ytqz += (
                '  {0} = bodo.utils.utils.alloc_type(new_len, t{1}, (-1,))\n'
                .format(out, i))
    pts__ytqz += '  curr_ind = 0\n'
    pts__ytqz += '  for i in range(old_len):\n'
    pts__ytqz += '    if {}:\n'.format(xsqfl__rss)
    for i in range(map__ssmm):
        pts__ytqz += '      if isna(data[{}], i):\n'.format(i)
        pts__ytqz += '        setna({}, curr_ind)\n'.format(cadas__cdtn[i])
        pts__ytqz += '      else:\n'
        pts__ytqz += '        {}[curr_ind] = data[{}][i]\n'.format(cadas__cdtn
            [i], i)
    pts__ytqz += '      curr_ind += 1\n'
    pts__ytqz += '  return {}\n'.format(', '.join(cadas__cdtn))
    wrfqb__qtlok = {}
    ysvyv__qgu = {'t{}'.format(i): huxc__vzad for i, huxc__vzad in
        enumerate(data.types)}
    ysvyv__qgu.update({'isna': isna, 'setna': setna, 'init_nested_counts':
        bodo.utils.indexing.init_nested_counts, 'add_nested_counts': bodo.
        utils.indexing.add_nested_counts, 'bodo': bodo})
    exec(pts__ytqz, ysvyv__qgu, wrfqb__qtlok)
    fjq__xsw = wrfqb__qtlok['_dropna_imp']
    return fjq__xsw


def get(arr, ind):
    return pd.Series(arr).str.get(ind)


@overload(get, no_unliteral=True)
def overload_get(arr, ind):
    if isinstance(arr, ArrayItemArrayType):
        iukku__rrle = arr.dtype
        xdev__bkkq = iukku__rrle.dtype

        def get_arr_item(arr, ind):
            n = len(arr)
            ndx__pnap = init_nested_counts(xdev__bkkq)
            for k in range(n):
                if bodo.libs.array_kernels.isna(arr, k):
                    continue
                val = arr[k]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    continue
                ndx__pnap = add_nested_counts(ndx__pnap, val[ind])
            rpqf__whqbv = bodo.utils.utils.alloc_type(n, iukku__rrle, ndx__pnap
                )
            for wcm__uex in range(n):
                if bodo.libs.array_kernels.isna(arr, wcm__uex):
                    setna(rpqf__whqbv, wcm__uex)
                    continue
                val = arr[wcm__uex]
                if not len(val) > ind >= -len(val
                    ) or bodo.libs.array_kernels.isna(val, ind):
                    setna(rpqf__whqbv, wcm__uex)
                    continue
                rpqf__whqbv[wcm__uex] = val[ind]
            return rpqf__whqbv
        return get_arr_item


def _is_same_categorical_array_type(arr_types):
    from bodo.hiframes.pd_categorical_ext import _to_readonly
    if not isinstance(arr_types, types.BaseTuple) or len(arr_types) == 0:
        return False
    nnhmv__pvv = _to_readonly(arr_types.types[0])
    return all(isinstance(huxc__vzad, CategoricalArrayType) and 
        _to_readonly(huxc__vzad) == nnhmv__pvv for huxc__vzad in arr_types.
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
        bwxf__yiev = arr_list.dtype.dtype

        def array_item_concat_impl(arr_list):
            nwhr__ywgcf = 0
            nafsr__axa = []
            for A in arr_list:
                hhmj__lmyqk = len(A)
                bodo.libs.array_item_arr_ext.trim_excess_data(A)
                nafsr__axa.append(bodo.libs.array_item_arr_ext.get_data(A))
                nwhr__ywgcf += hhmj__lmyqk
            lrkqv__hcxff = np.empty(nwhr__ywgcf + 1, offset_type)
            xruvk__gweoe = bodo.libs.array_kernels.concat(nafsr__axa)
            mstuw__gtvr = np.empty(nwhr__ywgcf + 7 >> 3, np.uint8)
            dzrds__wmkm = 0
            jhmst__ezf = 0
            for A in arr_list:
                lfmxg__ztbw = bodo.libs.array_item_arr_ext.get_offsets(A)
                zzoh__hjf = bodo.libs.array_item_arr_ext.get_null_bitmap(A)
                hhmj__lmyqk = len(A)
                unp__czp = lfmxg__ztbw[hhmj__lmyqk]
                for i in range(hhmj__lmyqk):
                    lrkqv__hcxff[i + dzrds__wmkm] = lfmxg__ztbw[i] + jhmst__ezf
                    dahfx__ohttc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        zzoh__hjf, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(mstuw__gtvr, i +
                        dzrds__wmkm, dahfx__ohttc)
                dzrds__wmkm += hhmj__lmyqk
                jhmst__ezf += unp__czp
            lrkqv__hcxff[dzrds__wmkm] = jhmst__ezf
            rpqf__whqbv = bodo.libs.array_item_arr_ext.init_array_item_array(
                nwhr__ywgcf, xruvk__gweoe, lrkqv__hcxff, mstuw__gtvr)
            return rpqf__whqbv
        return array_item_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.StructArrayType):
        fjzwy__tvf = arr_list.dtype.names
        pts__ytqz = 'def struct_array_concat_impl(arr_list):\n'
        pts__ytqz += f'    n_all = 0\n'
        for i in range(len(fjzwy__tvf)):
            pts__ytqz += f'    concat_list{i} = []\n'
        pts__ytqz += '    for A in arr_list:\n'
        pts__ytqz += (
            '        data_tuple = bodo.libs.struct_arr_ext.get_data(A)\n')
        for i in range(len(fjzwy__tvf)):
            pts__ytqz += f'        concat_list{i}.append(data_tuple[{i}])\n'
        pts__ytqz += '        n_all += len(A)\n'
        pts__ytqz += '    n_bytes = (n_all + 7) >> 3\n'
        pts__ytqz += '    new_mask = np.empty(n_bytes, np.uint8)\n'
        pts__ytqz += '    curr_bit = 0\n'
        pts__ytqz += '    for A in arr_list:\n'
        pts__ytqz += (
            '        old_mask = bodo.libs.struct_arr_ext.get_null_bitmap(A)\n')
        pts__ytqz += '        for j in range(len(A)):\n'
        pts__ytqz += (
            '            bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        pts__ytqz += (
            '            bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        pts__ytqz += '            curr_bit += 1\n'
        pts__ytqz += '    return bodo.libs.struct_arr_ext.init_struct_arr(\n'
        ufdio__jfb = ', '.join([
            f'bodo.libs.array_kernels.concat(concat_list{i})' for i in
            range(len(fjzwy__tvf))])
        pts__ytqz += f'        ({ufdio__jfb},),\n'
        pts__ytqz += '        new_mask,\n'
        pts__ytqz += f'        {fjzwy__tvf},\n'
        pts__ytqz += '    )\n'
        wrfqb__qtlok = {}
        exec(pts__ytqz, {'bodo': bodo, 'np': np}, wrfqb__qtlok)
        return wrfqb__qtlok['struct_array_concat_impl']
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_date_array_type:

        def datetime_date_array_concat_impl(arr_list):
            kclnw__xnv = 0
            for A in arr_list:
                kclnw__xnv += len(A)
            lqox__lrvf = (bodo.hiframes.datetime_date_ext.
                alloc_datetime_date_array(kclnw__xnv))
            oygm__gaku = 0
            for A in arr_list:
                for i in range(len(A)):
                    lqox__lrvf._data[i + oygm__gaku] = A._data[i]
                    dahfx__ohttc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lqox__lrvf.
                        _null_bitmap, i + oygm__gaku, dahfx__ohttc)
                oygm__gaku += len(A)
            return lqox__lrvf
        return datetime_date_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == datetime_timedelta_array_type:

        def datetime_timedelta_array_concat_impl(arr_list):
            kclnw__xnv = 0
            for A in arr_list:
                kclnw__xnv += len(A)
            lqox__lrvf = (bodo.hiframes.datetime_timedelta_ext.
                alloc_datetime_timedelta_array(kclnw__xnv))
            oygm__gaku = 0
            for A in arr_list:
                for i in range(len(A)):
                    lqox__lrvf._days_data[i + oygm__gaku] = A._days_data[i]
                    lqox__lrvf._seconds_data[i + oygm__gaku] = A._seconds_data[
                        i]
                    lqox__lrvf._microseconds_data[i + oygm__gaku
                        ] = A._microseconds_data[i]
                    dahfx__ohttc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lqox__lrvf.
                        _null_bitmap, i + oygm__gaku, dahfx__ohttc)
                oygm__gaku += len(A)
            return lqox__lrvf
        return datetime_timedelta_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, DecimalArrayType):
        nten__wwxe = arr_list.dtype.precision
        nvr__yagy = arr_list.dtype.scale

        def decimal_array_concat_impl(arr_list):
            kclnw__xnv = 0
            for A in arr_list:
                kclnw__xnv += len(A)
            lqox__lrvf = bodo.libs.decimal_arr_ext.alloc_decimal_array(
                kclnw__xnv, nten__wwxe, nvr__yagy)
            oygm__gaku = 0
            for A in arr_list:
                for i in range(len(A)):
                    lqox__lrvf._data[i + oygm__gaku] = A._data[i]
                    dahfx__ohttc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, i)
                    bodo.libs.int_arr_ext.set_bit_to_arr(lqox__lrvf.
                        _null_bitmap, i + oygm__gaku, dahfx__ohttc)
                oygm__gaku += len(A)
            return lqox__lrvf
        return decimal_array_concat_impl
    if isinstance(arr_list, (types.UniTuple, types.List)) and (is_str_arr_type
        (arr_list.dtype) or arr_list.dtype == bodo.binary_array_type
        ) or isinstance(arr_list, types.BaseTuple) and all(is_str_arr_type(
        huxc__vzad) for huxc__vzad in arr_list.types):
        if isinstance(arr_list, types.BaseTuple):
            dcaee__hij = arr_list.types[0]
        else:
            dcaee__hij = arr_list.dtype
        dcaee__hij = to_str_arr_if_dict_array(dcaee__hij)

        def impl_str(arr_list):
            arr_list = decode_if_dict_array(arr_list)
            wvb__mvvp = 0
            uxv__bqyzc = 0
            for A in arr_list:
                arr = A
                wvb__mvvp += len(arr)
                uxv__bqyzc += bodo.libs.str_arr_ext.num_total_chars(arr)
            rpqf__whqbv = bodo.utils.utils.alloc_type(wvb__mvvp, dcaee__hij,
                (uxv__bqyzc,))
            bodo.libs.str_arr_ext.set_null_bits_to_value(rpqf__whqbv, -1)
            cdxok__amgqw = 0
            woe__kmsu = 0
            for A in arr_list:
                arr = A
                bodo.libs.str_arr_ext.set_string_array_range(rpqf__whqbv,
                    arr, cdxok__amgqw, woe__kmsu)
                cdxok__amgqw += len(arr)
                woe__kmsu += bodo.libs.str_arr_ext.num_total_chars(arr)
            return rpqf__whqbv
        return impl_str
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, IntegerArrayType) or isinstance(arr_list, types.
        BaseTuple) and all(isinstance(huxc__vzad.dtype, types.Integer) for
        huxc__vzad in arr_list.types) and any(isinstance(huxc__vzad,
        IntegerArrayType) for huxc__vzad in arr_list.types):

        def impl_int_arr_list(arr_list):
            zfn__baas = convert_to_nullable_tup(arr_list)
            sxz__anhod = []
            rnlj__ontf = 0
            for A in zfn__baas:
                sxz__anhod.append(A._data)
                rnlj__ontf += len(A)
            xruvk__gweoe = bodo.libs.array_kernels.concat(sxz__anhod)
            kev__qii = rnlj__ontf + 7 >> 3
            vbx__mopta = np.empty(kev__qii, np.uint8)
            fvwu__jvlc = 0
            for A in zfn__baas:
                fam__spnl = A._null_bitmap
                for wcm__uex in range(len(A)):
                    dahfx__ohttc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        fam__spnl, wcm__uex)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vbx__mopta,
                        fvwu__jvlc, dahfx__ohttc)
                    fvwu__jvlc += 1
            return bodo.libs.int_arr_ext.init_integer_array(xruvk__gweoe,
                vbx__mopta)
        return impl_int_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)
        ) and arr_list.dtype == boolean_array or isinstance(arr_list, types
        .BaseTuple) and all(huxc__vzad.dtype == types.bool_ for huxc__vzad in
        arr_list.types) and any(huxc__vzad == boolean_array for huxc__vzad in
        arr_list.types):

        def impl_bool_arr_list(arr_list):
            zfn__baas = convert_to_nullable_tup(arr_list)
            sxz__anhod = []
            rnlj__ontf = 0
            for A in zfn__baas:
                sxz__anhod.append(A._data)
                rnlj__ontf += len(A)
            xruvk__gweoe = bodo.libs.array_kernels.concat(sxz__anhod)
            kev__qii = rnlj__ontf + 7 >> 3
            vbx__mopta = np.empty(kev__qii, np.uint8)
            fvwu__jvlc = 0
            for A in zfn__baas:
                fam__spnl = A._null_bitmap
                for wcm__uex in range(len(A)):
                    dahfx__ohttc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        fam__spnl, wcm__uex)
                    bodo.libs.int_arr_ext.set_bit_to_arr(vbx__mopta,
                        fvwu__jvlc, dahfx__ohttc)
                    fvwu__jvlc += 1
            return bodo.libs.bool_arr_ext.init_bool_array(xruvk__gweoe,
                vbx__mopta)
        return impl_bool_arr_list
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, CategoricalArrayType):

        def cat_array_concat_impl(arr_list):
            wnx__diij = []
            for A in arr_list:
                wnx__diij.append(A.codes)
            return init_categorical_array(bodo.libs.array_kernels.concat(
                wnx__diij), arr_list[0].dtype)
        return cat_array_concat_impl
    if _is_same_categorical_array_type(arr_list):
        qfs__fnu = ', '.join(f'arr_list[{i}].codes' for i in range(len(
            arr_list)))
        pts__ytqz = 'def impl(arr_list):\n'
        pts__ytqz += f"""    return init_categorical_array(bodo.libs.array_kernels.concat(({qfs__fnu},)), arr_list[0].dtype)
"""
        amapp__ivt = {}
        exec(pts__ytqz, {'bodo': bodo, 'init_categorical_array':
            init_categorical_array}, amapp__ivt)
        return amapp__ivt['impl']
    if isinstance(arr_list, types.List) and isinstance(arr_list.dtype,
        types.Array) and arr_list.dtype.ndim == 1:
        dtype = arr_list.dtype.dtype

        def impl_np_arr_list(arr_list):
            rnlj__ontf = 0
            for A in arr_list:
                rnlj__ontf += len(A)
            rpqf__whqbv = np.empty(rnlj__ontf, dtype)
            uuj__koa = 0
            for A in arr_list:
                n = len(A)
                rpqf__whqbv[uuj__koa:uuj__koa + n] = A
                uuj__koa += n
            return rpqf__whqbv
        return impl_np_arr_list
    if isinstance(arr_list, types.BaseTuple) and any(isinstance(huxc__vzad,
        (types.Array, IntegerArrayType)) and isinstance(huxc__vzad.dtype,
        types.Integer) for huxc__vzad in arr_list.types) and any(isinstance
        (huxc__vzad, types.Array) and isinstance(huxc__vzad.dtype, types.
        Float) for huxc__vzad in arr_list.types):
        return lambda arr_list: np.concatenate(astype_float_tup(arr_list))
    if isinstance(arr_list, (types.UniTuple, types.List)) and isinstance(
        arr_list.dtype, bodo.MapArrayType):

        def impl_map_arr_list(arr_list):
            yxozv__birz = []
            for A in arr_list:
                yxozv__birz.append(A._data)
            qtf__uay = bodo.libs.array_kernels.concat(yxozv__birz)
            kosmt__lrsz = bodo.libs.map_arr_ext.init_map_arr(qtf__uay)
            return kosmt__lrsz
        return impl_map_arr_list
    for yfad__cyp in arr_list:
        if not isinstance(yfad__cyp, types.Array):
            raise_bodo_error(f'concat of array types {arr_list} not supported')
    return lambda arr_list: np.concatenate(arr_list)


def astype_float_tup(arr_tup):
    return tuple(huxc__vzad.astype(np.float64) for huxc__vzad in arr_tup)


@overload(astype_float_tup, no_unliteral=True)
def overload_astype_float_tup(arr_tup):
    assert isinstance(arr_tup, types.BaseTuple)
    otdu__dnz = len(arr_tup.types)
    pts__ytqz = 'def f(arr_tup):\n'
    pts__ytqz += '  return ({}{})\n'.format(','.join(
        'arr_tup[{}].astype(np.float64)'.format(i) for i in range(otdu__dnz
        )), ',' if otdu__dnz == 1 else '')
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'np': np}, wrfqb__qtlok)
    wuel__vyew = wrfqb__qtlok['f']
    return wuel__vyew


def convert_to_nullable_tup(arr_tup):
    return arr_tup


@overload(convert_to_nullable_tup, no_unliteral=True)
def overload_convert_to_nullable_tup(arr_tup):
    if isinstance(arr_tup, (types.UniTuple, types.List)) and isinstance(arr_tup
        .dtype, (IntegerArrayType, BooleanArrayType)):
        return lambda arr_tup: arr_tup
    assert isinstance(arr_tup, types.BaseTuple)
    otdu__dnz = len(arr_tup.types)
    drvs__xrjq = find_common_np_dtype(arr_tup.types)
    xdev__bkkq = None
    kyjro__rvls = ''
    if isinstance(drvs__xrjq, types.Integer):
        xdev__bkkq = bodo.libs.int_arr_ext.IntDtype(drvs__xrjq)
        kyjro__rvls = '.astype(out_dtype, False)'
    pts__ytqz = 'def f(arr_tup):\n'
    pts__ytqz += '  return ({}{})\n'.format(','.join(
        'bodo.utils.conversion.coerce_to_array(arr_tup[{}], use_nullable_array=True){}'
        .format(i, kyjro__rvls) for i in range(otdu__dnz)), ',' if 
        otdu__dnz == 1 else '')
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'bodo': bodo, 'out_dtype': xdev__bkkq}, wrfqb__qtlok)
    nomp__opusv = wrfqb__qtlok['f']
    return nomp__opusv


def nunique(A, dropna):
    return len(set(A))


def nunique_parallel(A, dropna):
    return len(set(A))


@overload(nunique, no_unliteral=True)
def nunique_overload(A, dropna):

    def nunique_seq(A, dropna):
        s, zca__eeu = build_set_seen_na(A)
        return len(s) + int(not dropna and zca__eeu)
    return nunique_seq


@overload(nunique_parallel, no_unliteral=True)
def nunique_overload_parallel(A, dropna):
    sum_op = bodo.libs.distributed_api.Reduce_Type.Sum.value

    def nunique_par(A, dropna):
        gcc__hmixt = bodo.libs.array_kernels.unique(A, dropna, parallel=True)
        flu__xdvu = len(gcc__hmixt)
        return bodo.libs.distributed_api.dist_reduce(flu__xdvu, np.int32(
            sum_op))
    return nunique_par


def unique(A, dropna=False, parallel=False):
    return np.array([ituaa__wwn for ituaa__wwn in set(A)]).astype(A.dtype)


def cummin(A):
    return A


@overload(cummin, no_unliteral=True)
def cummin_overload(A):
    if isinstance(A.dtype, types.Float):
        bjba__erz = np.finfo(A.dtype(1).dtype).max
    else:
        bjba__erz = np.iinfo(A.dtype(1).dtype).max

    def impl(A):
        n = len(A)
        rpqf__whqbv = np.empty(n, A.dtype)
        nqng__nhvlz = bjba__erz
        for i in range(n):
            nqng__nhvlz = min(nqng__nhvlz, A[i])
            rpqf__whqbv[i] = nqng__nhvlz
        return rpqf__whqbv
    return impl


def cummax(A):
    return A


@overload(cummax, no_unliteral=True)
def cummax_overload(A):
    if isinstance(A.dtype, types.Float):
        bjba__erz = np.finfo(A.dtype(1).dtype).min
    else:
        bjba__erz = np.iinfo(A.dtype(1).dtype).min

    def impl(A):
        n = len(A)
        rpqf__whqbv = np.empty(n, A.dtype)
        nqng__nhvlz = bjba__erz
        for i in range(n):
            nqng__nhvlz = max(nqng__nhvlz, A[i])
            rpqf__whqbv[i] = nqng__nhvlz
        return rpqf__whqbv
    return impl


@overload(unique, no_unliteral=True)
def unique_overload(A, dropna=False, parallel=False):

    def unique_impl(A, dropna=False, parallel=False):
        zmyg__xgcn = arr_info_list_to_table([array_to_info(A)])
        nxtd__gqy = 1
        munw__yprp = 0
        juocg__dykya = drop_duplicates_table(zmyg__xgcn, parallel,
            nxtd__gqy, munw__yprp, dropna, True)
        rpqf__whqbv = info_to_array(info_from_table(juocg__dykya, 0), A)
        delete_table(zmyg__xgcn)
        delete_table(juocg__dykya)
        return rpqf__whqbv
    return unique_impl


def explode(arr, index_arr):
    return pd.Series(arr, index_arr).explode()


@overload(explode, no_unliteral=True)
def overload_explode(arr, index_arr):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    bwxf__yiev = bodo.utils.typing.to_nullable_type(arr.dtype)
    jozgj__mtt = index_arr
    cvl__jxy = jozgj__mtt.dtype

    def impl(arr, index_arr):
        n = len(arr)
        ndx__pnap = init_nested_counts(bwxf__yiev)
        vhgv__dcjk = init_nested_counts(cvl__jxy)
        for i in range(n):
            fha__lrm = index_arr[i]
            if isna(arr, i):
                ndx__pnap = (ndx__pnap[0] + 1,) + ndx__pnap[1:]
                vhgv__dcjk = add_nested_counts(vhgv__dcjk, fha__lrm)
                continue
            hzu__hcfyl = arr[i]
            if len(hzu__hcfyl) == 0:
                ndx__pnap = (ndx__pnap[0] + 1,) + ndx__pnap[1:]
                vhgv__dcjk = add_nested_counts(vhgv__dcjk, fha__lrm)
                continue
            ndx__pnap = add_nested_counts(ndx__pnap, hzu__hcfyl)
            for qzfdk__yuur in range(len(hzu__hcfyl)):
                vhgv__dcjk = add_nested_counts(vhgv__dcjk, fha__lrm)
        rpqf__whqbv = bodo.utils.utils.alloc_type(ndx__pnap[0], bwxf__yiev,
            ndx__pnap[1:])
        lskum__kwjmp = bodo.utils.utils.alloc_type(ndx__pnap[0], jozgj__mtt,
            vhgv__dcjk)
        jhmst__ezf = 0
        for i in range(n):
            if isna(arr, i):
                setna(rpqf__whqbv, jhmst__ezf)
                lskum__kwjmp[jhmst__ezf] = index_arr[i]
                jhmst__ezf += 1
                continue
            hzu__hcfyl = arr[i]
            unp__czp = len(hzu__hcfyl)
            if unp__czp == 0:
                setna(rpqf__whqbv, jhmst__ezf)
                lskum__kwjmp[jhmst__ezf] = index_arr[i]
                jhmst__ezf += 1
                continue
            rpqf__whqbv[jhmst__ezf:jhmst__ezf + unp__czp] = hzu__hcfyl
            lskum__kwjmp[jhmst__ezf:jhmst__ezf + unp__czp] = index_arr[i]
            jhmst__ezf += unp__czp
        return rpqf__whqbv, lskum__kwjmp
    return impl


def explode_no_index(arr):
    return pd.Series(arr).explode()


@overload(explode_no_index, no_unliteral=True)
def overload_explode_no_index(arr, counts):
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type
    bwxf__yiev = bodo.utils.typing.to_nullable_type(arr.dtype)

    def impl(arr, counts):
        n = len(arr)
        ndx__pnap = init_nested_counts(bwxf__yiev)
        for i in range(n):
            if isna(arr, i):
                ndx__pnap = (ndx__pnap[0] + 1,) + ndx__pnap[1:]
                eyi__owqyl = 1
            else:
                hzu__hcfyl = arr[i]
                rjeh__bwm = len(hzu__hcfyl)
                if rjeh__bwm == 0:
                    ndx__pnap = (ndx__pnap[0] + 1,) + ndx__pnap[1:]
                    eyi__owqyl = 1
                    continue
                else:
                    ndx__pnap = add_nested_counts(ndx__pnap, hzu__hcfyl)
                    eyi__owqyl = rjeh__bwm
            if counts[i] != eyi__owqyl:
                raise ValueError(
                    'DataFrame.explode(): columns must have matching element counts'
                    )
        rpqf__whqbv = bodo.utils.utils.alloc_type(ndx__pnap[0], bwxf__yiev,
            ndx__pnap[1:])
        jhmst__ezf = 0
        for i in range(n):
            if isna(arr, i):
                setna(rpqf__whqbv, jhmst__ezf)
                jhmst__ezf += 1
                continue
            hzu__hcfyl = arr[i]
            unp__czp = len(hzu__hcfyl)
            if unp__czp == 0:
                setna(rpqf__whqbv, jhmst__ezf)
                jhmst__ezf += 1
                continue
            rpqf__whqbv[jhmst__ezf:jhmst__ezf + unp__czp] = hzu__hcfyl
            jhmst__ezf += unp__czp
        return rpqf__whqbv
    return impl


def get_arr_lens(arr, na_empty_as_one=True):
    return [len(ufd__zucot) for ufd__zucot in arr]


@overload(get_arr_lens, inline='always', no_unliteral=True)
def overload_get_arr_lens(arr, na_empty_as_one=True):
    na_empty_as_one = get_overload_const_bool(na_empty_as_one)
    assert isinstance(arr, ArrayItemArrayType
        ) or arr == string_array_split_view_type or is_str_arr_type(arr
        ) and not na_empty_as_one, f'get_arr_lens: invalid input array type {arr}'
    if na_empty_as_one:
        dmbnz__kjmim = 'np.empty(n, np.int64)'
        vvb__ngxtd = 'out_arr[i] = 1'
        rjx__zbnv = 'max(len(arr[i]), 1)'
    else:
        dmbnz__kjmim = 'bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)'
        vvb__ngxtd = 'bodo.libs.array_kernels.setna(out_arr, i)'
        rjx__zbnv = 'len(arr[i])'
    pts__ytqz = f"""def impl(arr, na_empty_as_one=True):
    numba.parfors.parfor.init_prange()
    n = len(arr)
    out_arr = {dmbnz__kjmim}
    for i in numba.parfors.parfor.internal_prange(n):
        if bodo.libs.array_kernels.isna(arr, i):
            {vvb__ngxtd}
        else:
            out_arr[i] = {rjx__zbnv}
    return out_arr
    """
    wrfqb__qtlok = {}
    exec(pts__ytqz, {'bodo': bodo, 'numba': numba, 'np': np}, wrfqb__qtlok)
    impl = wrfqb__qtlok['impl']
    return impl


def explode_str_split(arr, pat, n, index_arr):
    return pd.Series(arr, index_arr).str.split(pat, n).explode()


@overload(explode_str_split, no_unliteral=True)
def overload_explode_str_split(arr, pat, n, index_arr):
    assert is_str_arr_type(arr
        ), f'explode_str_split: string array expected, not {arr}'
    jozgj__mtt = index_arr
    cvl__jxy = jozgj__mtt.dtype

    def impl(arr, pat, n, index_arr):
        mfinc__sbb = pat is not None and len(pat) > 1
        if mfinc__sbb:
            kfekr__wqrfd = re.compile(pat)
            if n == -1:
                n = 0
        elif n == 0:
            n = -1
        ddf__tvyag = len(arr)
        wvb__mvvp = 0
        uxv__bqyzc = 0
        vhgv__dcjk = init_nested_counts(cvl__jxy)
        for i in range(ddf__tvyag):
            fha__lrm = index_arr[i]
            if bodo.libs.array_kernels.isna(arr, i):
                wvb__mvvp += 1
                vhgv__dcjk = add_nested_counts(vhgv__dcjk, fha__lrm)
                continue
            if mfinc__sbb:
                jqf__fph = kfekr__wqrfd.split(arr[i], maxsplit=n)
            else:
                jqf__fph = arr[i].split(pat, n)
            wvb__mvvp += len(jqf__fph)
            for s in jqf__fph:
                vhgv__dcjk = add_nested_counts(vhgv__dcjk, fha__lrm)
                uxv__bqyzc += bodo.libs.str_arr_ext.get_utf8_size(s)
        rpqf__whqbv = bodo.libs.str_arr_ext.pre_alloc_string_array(wvb__mvvp,
            uxv__bqyzc)
        lskum__kwjmp = bodo.utils.utils.alloc_type(wvb__mvvp, jozgj__mtt,
            vhgv__dcjk)
        lgm__tlhpo = 0
        for wcm__uex in range(ddf__tvyag):
            if isna(arr, wcm__uex):
                rpqf__whqbv[lgm__tlhpo] = ''
                bodo.libs.array_kernels.setna(rpqf__whqbv, lgm__tlhpo)
                lskum__kwjmp[lgm__tlhpo] = index_arr[wcm__uex]
                lgm__tlhpo += 1
                continue
            if mfinc__sbb:
                jqf__fph = kfekr__wqrfd.split(arr[wcm__uex], maxsplit=n)
            else:
                jqf__fph = arr[wcm__uex].split(pat, n)
            rexu__kdpim = len(jqf__fph)
            rpqf__whqbv[lgm__tlhpo:lgm__tlhpo + rexu__kdpim] = jqf__fph
            lskum__kwjmp[lgm__tlhpo:lgm__tlhpo + rexu__kdpim] = index_arr[
                wcm__uex]
            lgm__tlhpo += rexu__kdpim
        return rpqf__whqbv, lskum__kwjmp
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
            rpqf__whqbv = np.empty(n, dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                rpqf__whqbv[i] = np.nan
            return rpqf__whqbv
        return impl_float
    if arr == bodo.dict_str_arr_type and is_overload_true(use_dict_arr):

        def impl_dict(n, arr, use_dict_arr=False):
            xbzy__kbq = bodo.libs.str_arr_ext.pre_alloc_string_array(0, 0)
            oyio__nml = bodo.libs.int_arr_ext.alloc_int_array(n, np.int32)
            numba.parfors.parfor.init_prange()
            for i in numba.parfors.parfor.internal_prange(n):
                setna(oyio__nml, i)
            return bodo.libs.dict_arr_ext.init_dict_arr(xbzy__kbq,
                oyio__nml, True)
        return impl_dict
    sci__ojsmj = to_str_arr_if_dict_array(arr)

    def impl(n, arr, use_dict_arr=False):
        numba.parfors.parfor.init_prange()
        rpqf__whqbv = bodo.utils.utils.alloc_type(n, sci__ojsmj, (0,))
        for i in numba.parfors.parfor.internal_prange(n):
            setna(rpqf__whqbv, i)
        return rpqf__whqbv
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
    qwd__geags = A
    if A == types.Array(types.uint8, 1, 'C'):

        def impl_char(A, old_size, new_len):
            rpqf__whqbv = bodo.utils.utils.alloc_type(new_len, qwd__geags)
            bodo.libs.str_arr_ext.str_copy_ptr(rpqf__whqbv.ctypes, 0, A.
                ctypes, old_size)
            return rpqf__whqbv
        return impl_char

    def impl(A, old_size, new_len):
        rpqf__whqbv = bodo.utils.utils.alloc_type(new_len, qwd__geags, (-1,))
        rpqf__whqbv[:old_size] = A[:old_size]
        return rpqf__whqbv
    return impl


@register_jitable
def calc_nitems(start, stop, step):
    fzarh__bsl = math.ceil((stop - start) / step)
    return int(max(fzarh__bsl, 0))


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
    if any(isinstance(ituaa__wwn, types.Complex) for ituaa__wwn in args):

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            uqkra__xkzk = (stop - start) / step
            fzarh__bsl = math.ceil(uqkra__xkzk.real)
            aiw__ddsl = math.ceil(uqkra__xkzk.imag)
            zenai__pnz = int(max(min(aiw__ddsl, fzarh__bsl), 0))
            arr = np.empty(zenai__pnz, dtype)
            for i in numba.parfors.parfor.internal_prange(zenai__pnz):
                arr[i] = start + i * step
            return arr
    else:

        def arange_4(start, stop, step, dtype):
            numba.parfors.parfor.init_prange()
            zenai__pnz = bodo.libs.array_kernels.calc_nitems(start, stop, step)
            arr = np.empty(zenai__pnz, dtype)
            for i in numba.parfors.parfor.internal_prange(zenai__pnz):
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
        egftd__mnxe = arr,
        if not inplace:
            egftd__mnxe = arr.copy(),
        nep__vupkg = bodo.libs.str_arr_ext.to_list_if_immutable_arr(egftd__mnxe
            )
        hqkij__biirf = bodo.libs.str_arr_ext.to_list_if_immutable_arr(data,
            True)
        bodo.libs.timsort.sort(nep__vupkg, 0, n, hqkij__biirf)
        if not ascending:
            bodo.libs.timsort.reverseRange(nep__vupkg, 0, n, hqkij__biirf)
        bodo.libs.str_arr_ext.cp_str_list_to_array(egftd__mnxe, nep__vupkg)
        return egftd__mnxe[0]
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
        kosmt__lrsz = []
        for i in range(n):
            if A[i]:
                kosmt__lrsz.append(i + offset)
        return np.array(kosmt__lrsz, np.int64),
    return impl


def ffill_bfill_arr(arr):
    return arr


@overload(ffill_bfill_arr, no_unliteral=True)
def ffill_bfill_overload(A, method, parallel=False):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'bodo.ffill_bfill_arr()')
    qwd__geags = element_type(A)
    if qwd__geags == types.unicode_type:
        null_value = '""'
    elif qwd__geags == types.bool_:
        null_value = 'False'
    elif qwd__geags == bodo.datetime64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_datetime(0))')
    elif qwd__geags == bodo.timedelta64ns:
        null_value = (
            'bodo.utils.conversion.unbox_if_timestamp(pd.to_timedelta(0))')
    else:
        null_value = '0'
    lgm__tlhpo = 'i'
    yqghe__cfmd = False
    vmq__ndwp = get_overload_const_str(method)
    if vmq__ndwp in ('ffill', 'pad'):
        mipht__gexb = 'n'
        send_right = True
    elif vmq__ndwp in ('backfill', 'bfill'):
        mipht__gexb = 'n-1, -1, -1'
        send_right = False
        if qwd__geags == types.unicode_type:
            lgm__tlhpo = '(n - 1) - i'
            yqghe__cfmd = True
    pts__ytqz = 'def impl(A, method, parallel=False):\n'
    pts__ytqz += '  A = decode_if_dict_array(A)\n'
    pts__ytqz += '  has_last_value = False\n'
    pts__ytqz += f'  last_value = {null_value}\n'
    pts__ytqz += '  if parallel:\n'
    pts__ytqz += '    rank = bodo.libs.distributed_api.get_rank()\n'
    pts__ytqz += '    n_pes = bodo.libs.distributed_api.get_size()\n'
    pts__ytqz += f"""    has_last_value, last_value = null_border_icomm(A, rank, n_pes, {null_value}, {send_right})
"""
    pts__ytqz += '  n = len(A)\n'
    pts__ytqz += '  out_arr = bodo.utils.utils.alloc_type(n, A, (-1,))\n'
    pts__ytqz += f'  for i in range({mipht__gexb}):\n'
    pts__ytqz += (
        '    if (bodo.libs.array_kernels.isna(A, i) and not has_last_value):\n'
        )
    pts__ytqz += (
        f'      bodo.libs.array_kernels.setna(out_arr, {lgm__tlhpo})\n')
    pts__ytqz += '      continue\n'
    pts__ytqz += '    s = A[i]\n'
    pts__ytqz += '    if bodo.libs.array_kernels.isna(A, i):\n'
    pts__ytqz += '      s = last_value\n'
    pts__ytqz += f'    out_arr[{lgm__tlhpo}] = s\n'
    pts__ytqz += '    last_value = s\n'
    pts__ytqz += '    has_last_value = True\n'
    if yqghe__cfmd:
        pts__ytqz += '  return out_arr[::-1]\n'
    else:
        pts__ytqz += '  return out_arr\n'
    htpk__vblg = {}
    exec(pts__ytqz, {'bodo': bodo, 'numba': numba, 'pd': pd,
        'null_border_icomm': null_border_icomm, 'decode_if_dict_array':
        decode_if_dict_array}, htpk__vblg)
    impl = htpk__vblg['impl']
    return impl


@register_jitable(cache=True)
def null_border_icomm(in_arr, rank, n_pes, null_value, send_right=True):
    if send_right:
        bhdih__arwg = 0
        hqgot__dnt = n_pes - 1
        cvco__has = np.int32(rank + 1)
        vzq__pemsx = np.int32(rank - 1)
        cxcn__fif = len(in_arr) - 1
        jjf__ccxi = -1
        ggd__vtz = -1
    else:
        bhdih__arwg = n_pes - 1
        hqgot__dnt = 0
        cvco__has = np.int32(rank - 1)
        vzq__pemsx = np.int32(rank + 1)
        cxcn__fif = 0
        jjf__ccxi = len(in_arr)
        ggd__vtz = 1
    zwbfq__gesp = np.int32(bodo.hiframes.rolling.comm_border_tag)
    twadh__ldw = np.empty(1, dtype=np.bool_)
    cpog__zbc = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    myvqg__hbt = np.empty(1, dtype=np.bool_)
    mekne__rwwft = bodo.utils.utils.alloc_type(1, in_arr, (-1,))
    ayxei__woq = False
    hujq__lbkd = null_value
    for i in range(cxcn__fif, jjf__ccxi, ggd__vtz):
        if not isna(in_arr, i):
            ayxei__woq = True
            hujq__lbkd = in_arr[i]
            break
    if rank != bhdih__arwg:
        aaydj__jgwql = bodo.libs.distributed_api.irecv(twadh__ldw, 1,
            vzq__pemsx, zwbfq__gesp, True)
        bodo.libs.distributed_api.wait(aaydj__jgwql, True)
        fcxi__mqun = bodo.libs.distributed_api.irecv(cpog__zbc, 1,
            vzq__pemsx, zwbfq__gesp, True)
        bodo.libs.distributed_api.wait(fcxi__mqun, True)
        rbqt__rkcio = twadh__ldw[0]
        fozh__spc = cpog__zbc[0]
    else:
        rbqt__rkcio = False
        fozh__spc = null_value
    if ayxei__woq:
        myvqg__hbt[0] = ayxei__woq
        mekne__rwwft[0] = hujq__lbkd
    else:
        myvqg__hbt[0] = rbqt__rkcio
        mekne__rwwft[0] = fozh__spc
    if rank != hqgot__dnt:
        nupce__svntm = bodo.libs.distributed_api.isend(myvqg__hbt, 1,
            cvco__has, zwbfq__gesp, True)
        kiale__fukc = bodo.libs.distributed_api.isend(mekne__rwwft, 1,
            cvco__has, zwbfq__gesp, True)
    return rbqt__rkcio, fozh__spc


@overload(np.sort, inline='always', no_unliteral=True)
def np_sort(A, axis=-1, kind=None, order=None):
    if not bodo.utils.utils.is_array_typ(A, False) or isinstance(A, types.Array
        ):
        return
    ptsz__rnw = {'axis': axis, 'kind': kind, 'order': order}
    gskj__yqfbe = {'axis': -1, 'kind': None, 'order': None}
    check_unsupported_args('np.sort', ptsz__rnw, gskj__yqfbe, 'numpy')

    def impl(A, axis=-1, kind=None, order=None):
        return pd.Series(A).sort_values().values
    return impl


def repeat_kernel(A, repeats):
    return A


@overload(repeat_kernel, no_unliteral=True)
def repeat_kernel_overload(A, repeats):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A,
        'Series.repeat()')
    qwd__geags = to_str_arr_if_dict_array(A)
    if isinstance(repeats, types.Integer):

        def impl_int(A, repeats):
            A = decode_if_dict_array(A)
            ddf__tvyag = len(A)
            rpqf__whqbv = bodo.utils.utils.alloc_type(ddf__tvyag * repeats,
                qwd__geags, (-1,))
            for i in range(ddf__tvyag):
                lgm__tlhpo = i * repeats
                if bodo.libs.array_kernels.isna(A, i):
                    for wcm__uex in range(repeats):
                        bodo.libs.array_kernels.setna(rpqf__whqbv, 
                            lgm__tlhpo + wcm__uex)
                else:
                    rpqf__whqbv[lgm__tlhpo:lgm__tlhpo + repeats] = A[i]
            return rpqf__whqbv
        return impl_int

    def impl_arr(A, repeats):
        A = decode_if_dict_array(A)
        ddf__tvyag = len(A)
        rpqf__whqbv = bodo.utils.utils.alloc_type(repeats.sum(), qwd__geags,
            (-1,))
        lgm__tlhpo = 0
        for i in range(ddf__tvyag):
            rdyi__rgdfr = repeats[i]
            if bodo.libs.array_kernels.isna(A, i):
                for wcm__uex in range(rdyi__rgdfr):
                    bodo.libs.array_kernels.setna(rpqf__whqbv, lgm__tlhpo +
                        wcm__uex)
            else:
                rpqf__whqbv[lgm__tlhpo:lgm__tlhpo + rdyi__rgdfr] = A[i]
            lgm__tlhpo += rdyi__rgdfr
        return rpqf__whqbv
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
        equ__ukdc = bodo.libs.array_kernels.unique(A)
        return bodo.allgatherv(equ__ukdc, False)
    return impl


@overload(np.union1d, inline='always', no_unliteral=True)
def overload_union1d(A1, A2):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.union1d()')

    def impl(A1, A2):
        qoapo__pyqgp = bodo.libs.array_kernels.concat([A1, A2])
        mynfz__thsog = bodo.libs.array_kernels.unique(qoapo__pyqgp)
        return pd.Series(mynfz__thsog).sort_values().values
    return impl


@overload(np.intersect1d, inline='always', no_unliteral=True)
def overload_intersect1d(A1, A2, assume_unique=False, return_indices=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    ptsz__rnw = {'assume_unique': assume_unique, 'return_indices':
        return_indices}
    gskj__yqfbe = {'assume_unique': False, 'return_indices': False}
    check_unsupported_args('np.intersect1d', ptsz__rnw, gskj__yqfbe, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.intersect1d()'
            )
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.intersect1d()')

    def impl(A1, A2, assume_unique=False, return_indices=False):
        crf__mevn = bodo.libs.array_kernels.unique(A1)
        frwct__gpx = bodo.libs.array_kernels.unique(A2)
        qoapo__pyqgp = bodo.libs.array_kernels.concat([crf__mevn, frwct__gpx])
        pfo__ceday = pd.Series(qoapo__pyqgp).sort_values().values
        return slice_array_intersect1d(pfo__ceday)
    return impl


@register_jitable
def slice_array_intersect1d(arr):
    cojpp__oheky = arr[1:] == arr[:-1]
    return arr[:-1][cojpp__oheky]


@register_jitable(cache=True)
def intersection_mask_comm(arr, rank, n_pes):
    zwbfq__gesp = np.int32(bodo.hiframes.rolling.comm_border_tag)
    ajpzk__gjt = bodo.utils.utils.alloc_type(1, arr, (-1,))
    if rank != 0:
        radn__wuavf = bodo.libs.distributed_api.isend(arr[:1], 1, np.int32(
            rank - 1), zwbfq__gesp, True)
        bodo.libs.distributed_api.wait(radn__wuavf, True)
    if rank == n_pes - 1:
        return None
    else:
        hxp__ekjgo = bodo.libs.distributed_api.irecv(ajpzk__gjt, 1, np.
            int32(rank + 1), zwbfq__gesp, True)
        bodo.libs.distributed_api.wait(hxp__ekjgo, True)
        return ajpzk__gjt[0]


@register_jitable(cache=True)
def intersection_mask(arr, parallel=False):
    n = len(arr)
    cojpp__oheky = np.full(n, False)
    for i in range(n - 1):
        if arr[i] == arr[i + 1]:
            cojpp__oheky[i] = True
    if parallel:
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        zgor__bobw = intersection_mask_comm(arr, rank, n_pes)
        if rank != n_pes - 1 and arr[n - 1] == zgor__bobw:
            cojpp__oheky[n - 1] = True
    return cojpp__oheky


@overload(np.setdiff1d, inline='always', no_unliteral=True)
def overload_setdiff1d(A1, A2, assume_unique=False):
    if not bodo.utils.utils.is_array_typ(A1, False
        ) or not bodo.utils.utils.is_array_typ(A2, False):
        return
    ptsz__rnw = {'assume_unique': assume_unique}
    gskj__yqfbe = {'assume_unique': False}
    check_unsupported_args('np.setdiff1d', ptsz__rnw, gskj__yqfbe, 'numpy')
    if A1 != A2:
        raise BodoError('Both arrays must be the same type in np.setdiff1d()')
    if A1.ndim != 1 or A2.ndim != 1:
        raise BodoError('Only 1D arrays supported in np.setdiff1d()')

    def impl(A1, A2, assume_unique=False):
        crf__mevn = bodo.libs.array_kernels.unique(A1)
        frwct__gpx = bodo.libs.array_kernels.unique(A2)
        cojpp__oheky = calculate_mask_setdiff1d(crf__mevn, frwct__gpx)
        return pd.Series(crf__mevn[cojpp__oheky]).sort_values().values
    return impl


@register_jitable
def calculate_mask_setdiff1d(A1, A2):
    cojpp__oheky = np.ones(len(A1), np.bool_)
    for i in range(len(A2)):
        cojpp__oheky &= A1 != A2[i]
    return cojpp__oheky


@overload(np.linspace, inline='always', no_unliteral=True)
def np_linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=
    None, axis=0):
    ptsz__rnw = {'retstep': retstep, 'axis': axis}
    gskj__yqfbe = {'retstep': False, 'axis': 0}
    check_unsupported_args('np.linspace', ptsz__rnw, gskj__yqfbe, 'numpy')
    vsyif__vvul = False
    if is_overload_none(dtype):
        qwd__geags = np.promote_types(np.promote_types(numba.np.
            numpy_support.as_dtype(start), numba.np.numpy_support.as_dtype(
            stop)), numba.np.numpy_support.as_dtype(types.float64)).type
    else:
        if isinstance(dtype.dtype, types.Integer):
            vsyif__vvul = True
        qwd__geags = numba.np.numpy_support.as_dtype(dtype).type
    if vsyif__vvul:

        def impl_int(start, stop, num=50, endpoint=True, retstep=False,
            dtype=None, axis=0):
            ychrj__gic = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            rpqf__whqbv = np.empty(num, qwd__geags)
            for i in numba.parfors.parfor.internal_prange(num):
                rpqf__whqbv[i] = qwd__geags(np.floor(start + i * ychrj__gic))
            return rpqf__whqbv
        return impl_int
    else:

        def impl(start, stop, num=50, endpoint=True, retstep=False, dtype=
            None, axis=0):
            ychrj__gic = np_linspace_get_stepsize(start, stop, num, endpoint)
            numba.parfors.parfor.init_prange()
            rpqf__whqbv = np.empty(num, qwd__geags)
            for i in numba.parfors.parfor.internal_prange(num):
                rpqf__whqbv[i] = qwd__geags(start + i * ychrj__gic)
            return rpqf__whqbv
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
        otdu__dnz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                otdu__dnz += A[i] == val
        return otdu__dnz > 0
    return impl


@overload(np.any, inline='always', no_unliteral=True)
def np_any(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.any()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    ptsz__rnw = {'axis': axis, 'out': out, 'keepdims': keepdims}
    gskj__yqfbe = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', ptsz__rnw, gskj__yqfbe, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        otdu__dnz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                otdu__dnz += int(bool(A[i]))
        return otdu__dnz > 0
    return impl


@overload(np.all, inline='always', no_unliteral=True)
def np_all(A, axis=None, out=None, keepdims=None):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(A, 'np.all()')
    if not (bodo.utils.utils.is_array_typ(A, False) and A.ndim == 1):
        return
    ptsz__rnw = {'axis': axis, 'out': out, 'keepdims': keepdims}
    gskj__yqfbe = {'axis': None, 'out': None, 'keepdims': None}
    check_unsupported_args('np.any', ptsz__rnw, gskj__yqfbe, 'numpy')

    def impl(A, axis=None, out=None, keepdims=None):
        numba.parfors.parfor.init_prange()
        otdu__dnz = 0
        n = len(A)
        for i in numba.parfors.parfor.internal_prange(n):
            if not bodo.libs.array_kernels.isna(A, i):
                otdu__dnz += int(bool(A[i]))
        return otdu__dnz == n
    return impl


@overload(np.cbrt, inline='always', no_unliteral=True)
def np_cbrt(A, out=None, where=True, casting='same_kind', order='K', dtype=
    None, subok=True):
    if not (isinstance(A, types.Number) or bodo.utils.utils.is_array_typ(A,
        False) and A.ndim == 1 and isinstance(A.dtype, types.Number)):
        return
    ptsz__rnw = {'out': out, 'where': where, 'casting': casting, 'order':
        order, 'dtype': dtype, 'subok': subok}
    gskj__yqfbe = {'out': None, 'where': True, 'casting': 'same_kind',
        'order': 'K', 'dtype': None, 'subok': True}
    check_unsupported_args('np.cbrt', ptsz__rnw, gskj__yqfbe, 'numpy')
    if bodo.utils.utils.is_array_typ(A, False):
        hnh__isq = np.promote_types(numba.np.numpy_support.as_dtype(A.dtype
            ), numba.np.numpy_support.as_dtype(types.float32)).type

        def impl_arr(A, out=None, where=True, casting='same_kind', order=
            'K', dtype=None, subok=True):
            numba.parfors.parfor.init_prange()
            n = len(A)
            rpqf__whqbv = np.empty(n, hnh__isq)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(rpqf__whqbv, i)
                    continue
                rpqf__whqbv[i] = np_cbrt_scalar(A[i], hnh__isq)
            return rpqf__whqbv
        return impl_arr
    hnh__isq = np.promote_types(numba.np.numpy_support.as_dtype(A), numba.
        np.numpy_support.as_dtype(types.float32)).type

    def impl_scalar(A, out=None, where=True, casting='same_kind', order='K',
        dtype=None, subok=True):
        return np_cbrt_scalar(A, hnh__isq)
    return impl_scalar


@register_jitable
def np_cbrt_scalar(x, float_dtype):
    if np.isnan(x):
        return np.nan
    zhmcm__ndx = x < 0
    if zhmcm__ndx:
        x = -x
    res = np.power(float_dtype(x), 1.0 / 3.0)
    if zhmcm__ndx:
        return -res
    return res


@overload(np.hstack, no_unliteral=True)
def np_hstack(tup):
    lol__jitt = isinstance(tup, (types.BaseTuple, types.List))
    szv__abhvm = isinstance(tup, (bodo.SeriesType, bodo.hiframes.
        pd_series_ext.HeterogeneousSeriesType)) and isinstance(tup.data, (
        types.BaseTuple, types.List, bodo.NullableTupleType))
    if isinstance(tup, types.BaseTuple):
        for yfad__cyp in tup.types:
            bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(yfad__cyp
                , 'numpy.hstack()')
            lol__jitt = lol__jitt and bodo.utils.utils.is_array_typ(yfad__cyp,
                False)
    elif isinstance(tup, types.List):
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup.dtype,
            'numpy.hstack()')
        lol__jitt = bodo.utils.utils.is_array_typ(tup.dtype, False)
    elif szv__abhvm:
        bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(tup,
            'numpy.hstack()')
        grrot__khynu = tup.data.tuple_typ if isinstance(tup.data, bodo.
            NullableTupleType) else tup.data
        for yfad__cyp in grrot__khynu.types:
            szv__abhvm = szv__abhvm and bodo.utils.utils.is_array_typ(yfad__cyp
                , False)
    if not (lol__jitt or szv__abhvm):
        return
    if szv__abhvm:

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
    ptsz__rnw = {'check_valid': check_valid, 'tol': tol}
    gskj__yqfbe = {'check_valid': 'warn', 'tol': 1e-08}
    check_unsupported_args('np.random.multivariate_normal', ptsz__rnw,
        gskj__yqfbe, 'numpy')
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
        qfpem__ujazx = mean.shape[0]
        oscdp__ywft = size, qfpem__ujazx
        cdfx__dth = np.random.standard_normal(oscdp__ywft)
        cov = cov.astype(np.float64)
        ugm__thc, s, mgnlt__jvmcs = np.linalg.svd(cov)
        res = np.dot(cdfx__dth, np.sqrt(s).reshape(qfpem__ujazx, 1) *
            mgnlt__jvmcs)
        nxo__olrw = res + mean
        return nxo__olrw
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
            vbozd__xqyel = bodo.hiframes.series_kernels._get_type_max_value(arr
                )
            lxm__ngou = typing.builtins.IndexValue(-1, vbozd__xqyel)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                lmkq__wvop = typing.builtins.IndexValue(i, arr[i])
                lxm__ngou = min(lxm__ngou, lmkq__wvop)
            return lxm__ngou.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        bltxn__ylf = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            rnc__ssrk = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            vbozd__xqyel = bltxn__ylf(len(arr.dtype.categories) + 1)
            lxm__ngou = typing.builtins.IndexValue(-1, vbozd__xqyel)
            for i in numba.parfors.parfor.internal_prange(len(arr)):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                lmkq__wvop = typing.builtins.IndexValue(i, rnc__ssrk[i])
                lxm__ngou = min(lxm__ngou, lmkq__wvop)
            return lxm__ngou.index
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
            vbozd__xqyel = bodo.hiframes.series_kernels._get_type_min_value(arr
                )
            lxm__ngou = typing.builtins.IndexValue(-1, vbozd__xqyel)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                lmkq__wvop = typing.builtins.IndexValue(i, arr[i])
                lxm__ngou = max(lxm__ngou, lmkq__wvop)
            return lxm__ngou.index
        return impl_bodo_arr
    if isinstance(arr, CategoricalArrayType):
        assert arr.dtype.ordered, 'Categorical Array must be ordered to select an argmin'
        bltxn__ylf = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def impl_cat_arr(arr):
            n = len(arr)
            rnc__ssrk = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            vbozd__xqyel = bltxn__ylf(-1)
            lxm__ngou = typing.builtins.IndexValue(-1, vbozd__xqyel)
            for i in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arr, i):
                    continue
                lmkq__wvop = typing.builtins.IndexValue(i, rnc__ssrk[i])
                lxm__ngou = max(lxm__ngou, lmkq__wvop)
            return lxm__ngou.index
        return impl_cat_arr
    return lambda arr: arr.argmax()


@overload_attribute(types.Array, 'nbytes', inline='always')
def overload_dataframe_index(A):
    return lambda A: A.size * bodo.io.np_io.get_dtype_size(A.dtype)
