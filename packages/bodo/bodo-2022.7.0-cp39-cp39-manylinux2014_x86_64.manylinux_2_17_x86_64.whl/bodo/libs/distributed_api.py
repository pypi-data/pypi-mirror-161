import atexit
import datetime
import sys
import time
import warnings
from collections import defaultdict
from decimal import Decimal
from enum import Enum
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from mpi4py import MPI
from numba.core import cgutils, ir_utils, types
from numba.core.typing import signature
from numba.core.typing.builtins import IndexValueType
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, overload, register_jitable
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.libs import hdist
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType, set_bit_to_arr
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.pd_datetime_arr_ext import DatetimeArrayType
from bodo.libs.str_arr_ext import convert_len_arr_to_offset, get_bit_bitmap, get_data_ptr, get_null_bitmap_ptr, get_offset_ptr, num_total_chars, pre_alloc_string_array, set_bit_to, string_array_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, BodoWarning, ColNamesMetaType, decode_if_dict_array, is_overload_false, is_overload_none, is_str_arr_type
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, empty_like_type, is_array_typ, numba_to_c_type
ll.add_symbol('dist_get_time', hdist.dist_get_time)
ll.add_symbol('get_time', hdist.get_time)
ll.add_symbol('dist_reduce', hdist.dist_reduce)
ll.add_symbol('dist_arr_reduce', hdist.dist_arr_reduce)
ll.add_symbol('dist_exscan', hdist.dist_exscan)
ll.add_symbol('dist_irecv', hdist.dist_irecv)
ll.add_symbol('dist_isend', hdist.dist_isend)
ll.add_symbol('dist_wait', hdist.dist_wait)
ll.add_symbol('dist_get_item_pointer', hdist.dist_get_item_pointer)
ll.add_symbol('get_dummy_ptr', hdist.get_dummy_ptr)
ll.add_symbol('allgather', hdist.allgather)
ll.add_symbol('oneD_reshape_shuffle', hdist.oneD_reshape_shuffle)
ll.add_symbol('permutation_int', hdist.permutation_int)
ll.add_symbol('permutation_array_index', hdist.permutation_array_index)
ll.add_symbol('c_get_rank', hdist.dist_get_rank)
ll.add_symbol('c_get_size', hdist.dist_get_size)
ll.add_symbol('c_barrier', hdist.barrier)
ll.add_symbol('c_alltoall', hdist.c_alltoall)
ll.add_symbol('c_gather_scalar', hdist.c_gather_scalar)
ll.add_symbol('c_gatherv', hdist.c_gatherv)
ll.add_symbol('c_scatterv', hdist.c_scatterv)
ll.add_symbol('c_allgatherv', hdist.c_allgatherv)
ll.add_symbol('c_bcast', hdist.c_bcast)
ll.add_symbol('c_recv', hdist.dist_recv)
ll.add_symbol('c_send', hdist.dist_send)
mpi_req_numba_type = getattr(types, 'int' + str(8 * hdist.mpi_req_num_bytes))
MPI_ROOT = 0
ANY_SOURCE = np.int32(hdist.ANY_SOURCE)


class Reduce_Type(Enum):
    Sum = 0
    Prod = 1
    Min = 2
    Max = 3
    Argmin = 4
    Argmax = 5
    Or = 6
    Concat = 7
    No_Op = 8


_get_rank = types.ExternalFunction('c_get_rank', types.int32())
_get_size = types.ExternalFunction('c_get_size', types.int32())
_barrier = types.ExternalFunction('c_barrier', types.int32())


@numba.njit
def get_rank():
    return _get_rank()


@numba.njit
def get_size():
    return _get_size()


@numba.njit
def barrier():
    _barrier()


_get_time = types.ExternalFunction('get_time', types.float64())
dist_time = types.ExternalFunction('dist_get_time', types.float64())


@overload(time.time, no_unliteral=True)
def overload_time_time():
    return lambda : _get_time()


@numba.generated_jit(nopython=True)
def get_type_enum(arr):
    arr = arr.instance_type if isinstance(arr, types.TypeRef) else arr
    dtype = arr.dtype
    if isinstance(dtype, bodo.hiframes.pd_categorical_ext.PDCategoricalDtype):
        dtype = bodo.hiframes.pd_categorical_ext.get_categories_int_type(dtype)
    typ_val = numba_to_c_type(dtype)
    return lambda arr: np.int32(typ_val)


INT_MAX = np.iinfo(np.int32).max
_send = types.ExternalFunction('c_send', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def send(val, rank, tag):
    send_arr = np.full(1, val)
    wwvqe__sdc = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, wwvqe__sdc, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    wwvqe__sdc = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, wwvqe__sdc, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            wwvqe__sdc = get_type_enum(arr)
            return _isend(arr.ctypes, size, wwvqe__sdc, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        wwvqe__sdc = np.int32(numba_to_c_type(arr.dtype))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            ninj__hghwk = size + 7 >> 3
            jkwzf__kmec = _isend(arr._data.ctypes, size, wwvqe__sdc, pe,
                tag, cond)
            msnm__itcd = _isend(arr._null_bitmap.ctypes, ninj__hghwk,
                kmqxt__cyata, pe, tag, cond)
            return jkwzf__kmec, msnm__itcd
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        jeza__avt = np.int32(numba_to_c_type(offset_type))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            wtknh__zzpn = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(wtknh__zzpn, pe, tag - 1)
            ninj__hghwk = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                jeza__avt, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), wtknh__zzpn,
                kmqxt__cyata, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                ninj__hghwk, kmqxt__cyata, pe, tag)
            return None
        return impl_str_arr
    typ_enum = numba_to_c_type(types.uint8)

    def impl_voidptr(arr, size, pe, tag, cond=True):
        return _isend(arr, size, typ_enum, pe, tag, cond)
    return impl_voidptr


_irecv = types.ExternalFunction('dist_irecv', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def irecv(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            wwvqe__sdc = get_type_enum(arr)
            return _irecv(arr.ctypes, size, wwvqe__sdc, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        wwvqe__sdc = np.int32(numba_to_c_type(arr.dtype))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            ninj__hghwk = size + 7 >> 3
            jkwzf__kmec = _irecv(arr._data.ctypes, size, wwvqe__sdc, pe,
                tag, cond)
            msnm__itcd = _irecv(arr._null_bitmap.ctypes, ninj__hghwk,
                kmqxt__cyata, pe, tag, cond)
            return jkwzf__kmec, msnm__itcd
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        jeza__avt = np.int32(numba_to_c_type(offset_type))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            batw__oamu = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            batw__oamu = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        affmm__bhjlk = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {batw__oamu}(size, n_chars)
            bodo.libs.str_arr_ext.move_str_binary_arr_payload(arr, new_arr)

            n_bytes = (size + 7) >> 3
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_offset_ptr(arr),
                size + 1,
                offset_typ_enum,
                pe,
                tag,
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_data_ptr(arr), n_chars, char_typ_enum, pe, tag
            )
            bodo.libs.distributed_api._recv(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                n_bytes,
                char_typ_enum,
                pe,
                tag,
            )
            return None"""
        eth__ewwt = dict()
        exec(affmm__bhjlk, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            jeza__avt, 'char_typ_enum': kmqxt__cyata}, eth__ewwt)
        impl = eth__ewwt['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    wwvqe__sdc = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), wwvqe__sdc)


@numba.generated_jit(nopython=True)
def gather_scalar(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    data = types.unliteral(data)
    typ_val = numba_to_c_type(data)
    dtype = data

    def gather_scalar_impl(data, allgather=False, warn_if_rep=True, root=
        MPI_ROOT):
        n_pes = bodo.libs.distributed_api.get_size()
        rank = bodo.libs.distributed_api.get_rank()
        send = np.full(1, data, dtype)
        cnigt__wct = n_pes if rank == root or allgather else 0
        viiu__ato = np.empty(cnigt__wct, dtype)
        c_gather_scalar(send.ctypes, viiu__ato.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return viiu__ato
    return gather_scalar_impl


c_gather_scalar = types.ExternalFunction('c_gather_scalar', types.void(
    types.voidptr, types.voidptr, types.int32, types.bool_, types.int32))
c_gatherv = types.ExternalFunction('c_gatherv', types.void(types.voidptr,
    types.int32, types.voidptr, types.voidptr, types.voidptr, types.int32,
    types.bool_, types.int32))
c_scatterv = types.ExternalFunction('c_scatterv', types.void(types.voidptr,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.int32))


@intrinsic
def value_to_ptr(typingctx, val_tp=None):

    def codegen(context, builder, sig, args):
        fpny__xrlb = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], fpny__xrlb)
        return builder.bitcast(fpny__xrlb, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        fpny__xrlb = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(fpny__xrlb)
    return val_tp(ptr_tp, val_tp), codegen


_dist_reduce = types.ExternalFunction('dist_reduce', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))
_dist_arr_reduce = types.ExternalFunction('dist_arr_reduce', types.void(
    types.voidptr, types.int64, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_reduce(value, reduce_op):
    if isinstance(value, types.Array):
        typ_enum = np.int32(numba_to_c_type(value.dtype))

        def impl_arr(value, reduce_op):
            A = np.ascontiguousarray(value)
            _dist_arr_reduce(A.ctypes, A.size, reduce_op, typ_enum)
            return A
        return impl_arr
    xxne__fug = types.unliteral(value)
    if isinstance(xxne__fug, IndexValueType):
        xxne__fug = xxne__fug.val_typ
        lngq__nkw = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            lngq__nkw.append(types.int64)
            lngq__nkw.append(bodo.datetime64ns)
            lngq__nkw.append(bodo.timedelta64ns)
            lngq__nkw.append(bodo.datetime_date_type)
        if xxne__fug not in lngq__nkw:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(xxne__fug))
    typ_enum = np.int32(numba_to_c_type(xxne__fug))

    def impl(value, reduce_op):
        hlerw__cbdlu = value_to_ptr(value)
        nsgn__ouudu = value_to_ptr(value)
        _dist_reduce(hlerw__cbdlu, nsgn__ouudu, reduce_op, typ_enum)
        return load_val_ptr(nsgn__ouudu, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    xxne__fug = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(xxne__fug))
    aswta__dfikq = xxne__fug(0)

    def impl(value, reduce_op):
        hlerw__cbdlu = value_to_ptr(value)
        nsgn__ouudu = value_to_ptr(aswta__dfikq)
        _dist_exscan(hlerw__cbdlu, nsgn__ouudu, reduce_op, typ_enum)
        return load_val_ptr(nsgn__ouudu, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    yijhl__qbrs = 0
    dkdnc__rim = 0
    for i in range(len(recv_counts)):
        fncl__ppofu = recv_counts[i]
        ninj__hghwk = recv_counts_nulls[i]
        mft__lou = tmp_null_bytes[yijhl__qbrs:yijhl__qbrs + ninj__hghwk]
        for tojl__bau in range(fncl__ppofu):
            set_bit_to(null_bitmap_ptr, dkdnc__rim, get_bit(mft__lou,
                tojl__bau))
            dkdnc__rim += 1
        yijhl__qbrs += ninj__hghwk


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            ecaz__fqnpl = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                ecaz__fqnpl, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            udn__keg = data.size
            recv_counts = gather_scalar(np.int32(udn__keg), allgather, root
                =root)
            qlqw__fbbwk = recv_counts.sum()
            mua__etjpt = empty_like_type(qlqw__fbbwk, data)
            biqtq__uzf = np.empty(1, np.int32)
            if rank == root or allgather:
                biqtq__uzf = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(udn__keg), mua__etjpt.ctypes,
                recv_counts.ctypes, biqtq__uzf.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return mua__etjpt.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            mua__etjpt = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(mua__etjpt)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            mua__etjpt = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(mua__etjpt)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            udn__keg = len(data)
            ninj__hghwk = udn__keg + 7 >> 3
            recv_counts = gather_scalar(np.int32(udn__keg), allgather, root
                =root)
            qlqw__fbbwk = recv_counts.sum()
            mua__etjpt = empty_like_type(qlqw__fbbwk, data)
            biqtq__uzf = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sdxiu__sbiit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                biqtq__uzf = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sdxiu__sbiit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(udn__keg),
                mua__etjpt._days_data.ctypes, recv_counts.ctypes,
                biqtq__uzf.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(udn__keg),
                mua__etjpt._seconds_data.ctypes, recv_counts.ctypes,
                biqtq__uzf.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(udn__keg),
                mua__etjpt._microseconds_data.ctypes, recv_counts.ctypes,
                biqtq__uzf.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(ninj__hghwk),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sdxiu__sbiit.ctypes, kmqxt__cyata, allgather, np.int32(root))
            copy_gathered_null_bytes(mua__etjpt._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return mua__etjpt
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            udn__keg = len(data)
            ninj__hghwk = udn__keg + 7 >> 3
            recv_counts = gather_scalar(np.int32(udn__keg), allgather, root
                =root)
            qlqw__fbbwk = recv_counts.sum()
            mua__etjpt = empty_like_type(qlqw__fbbwk, data)
            biqtq__uzf = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sdxiu__sbiit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                biqtq__uzf = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sdxiu__sbiit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(udn__keg), mua__etjpt.
                _data.ctypes, recv_counts.ctypes, biqtq__uzf.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(ninj__hghwk),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sdxiu__sbiit.ctypes, kmqxt__cyata, allgather, np.int32(root))
            copy_gathered_null_bytes(mua__etjpt._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return mua__etjpt
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        otdjm__icv = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            banv__biu = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                banv__biu, otdjm__icv)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            iupr__ifdat = bodo.gatherv(data._left, allgather, warn_if_rep, root
                )
            hgn__ecj = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(iupr__ifdat,
                hgn__ecj)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qhlqf__xmajp = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            lspgq__rpba = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lspgq__rpba, qhlqf__xmajp)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        tstnv__wzpj = np.iinfo(np.int64).max
        gag__gtuf = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            pde__bti = data._start
            ftn__fez = data._stop
            if len(data) == 0:
                pde__bti = tstnv__wzpj
                ftn__fez = gag__gtuf
            pde__bti = bodo.libs.distributed_api.dist_reduce(pde__bti, np.
                int32(Reduce_Type.Min.value))
            ftn__fez = bodo.libs.distributed_api.dist_reduce(ftn__fez, np.
                int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if pde__bti == tstnv__wzpj and ftn__fez == gag__gtuf:
                pde__bti = 0
                ftn__fez = 0
            vtxlq__cwf = max(0, -(-(ftn__fez - pde__bti) // data._step))
            if vtxlq__cwf < total_len:
                ftn__fez = pde__bti + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                pde__bti = 0
                ftn__fez = 0
            return bodo.hiframes.pd_index_ext.init_range_index(pde__bti,
                ftn__fez, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            tfe__kiryi = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, tfe__kiryi)
        else:

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.utils.conversion.index_from_array(arr, data._name)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            mua__etjpt = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(mua__etjpt
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        aeu__dcyi = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        affmm__bhjlk = f"""def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):
"""
        affmm__bhjlk += '  T = data\n'
        affmm__bhjlk += '  T2 = init_table(T, True)\n'
        for ropq__whf in data.type_to_blk.values():
            aeu__dcyi[f'arr_inds_{ropq__whf}'] = np.array(data.
                block_to_arr_ind[ropq__whf], dtype=np.int64)
            affmm__bhjlk += (
                f'  arr_list_{ropq__whf} = get_table_block(T, {ropq__whf})\n')
            affmm__bhjlk += f"""  out_arr_list_{ropq__whf} = alloc_list_like(arr_list_{ropq__whf}, len(arr_list_{ropq__whf}), True)
"""
            affmm__bhjlk += f'  for i in range(len(arr_list_{ropq__whf})):\n'
            affmm__bhjlk += (
                f'    arr_ind_{ropq__whf} = arr_inds_{ropq__whf}[i]\n')
            affmm__bhjlk += f"""    ensure_column_unboxed(T, arr_list_{ropq__whf}, i, arr_ind_{ropq__whf})
"""
            affmm__bhjlk += f"""    out_arr_{ropq__whf} = bodo.gatherv(arr_list_{ropq__whf}[i], allgather, warn_if_rep, root)
"""
            affmm__bhjlk += (
                f'    out_arr_list_{ropq__whf}[i] = out_arr_{ropq__whf}\n')
            affmm__bhjlk += (
                f'  T2 = set_table_block(T2, out_arr_list_{ropq__whf}, {ropq__whf})\n'
                )
        affmm__bhjlk += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        affmm__bhjlk += f'  T2 = set_table_len(T2, length)\n'
        affmm__bhjlk += f'  return T2\n'
        eth__ewwt = {}
        exec(affmm__bhjlk, aeu__dcyi, eth__ewwt)
        tkles__eyizp = eth__ewwt['impl_table']
        return tkles__eyizp
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mqu__ygw = len(data.columns)
        if mqu__ygw == 0:
            letgs__tge = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                fxexg__shloc = bodo.gatherv(index, allgather, warn_if_rep, root
                    )
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    fxexg__shloc, letgs__tge)
            return impl
        uyna__qisa = ', '.join(f'g_data_{i}' for i in range(mqu__ygw))
        affmm__bhjlk = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            tlux__ako = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            uyna__qisa = 'T2'
            affmm__bhjlk += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            affmm__bhjlk += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(mqu__ygw):
                affmm__bhjlk += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                affmm__bhjlk += (
                    """  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)
"""
                    .format(i, i))
        affmm__bhjlk += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        affmm__bhjlk += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        affmm__bhjlk += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(uyna__qisa))
        eth__ewwt = {}
        aeu__dcyi = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(affmm__bhjlk, aeu__dcyi, eth__ewwt)
        grckz__qmofx = eth__ewwt['impl_df']
        return grckz__qmofx
    if isinstance(data, ArrayItemArrayType):
        toi__sldjv = np.int32(numba_to_c_type(types.int32))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            xkeq__fnisu = bodo.libs.array_item_arr_ext.get_offsets(data)
            afbt__xmhsl = bodo.libs.array_item_arr_ext.get_data(data)
            afbt__xmhsl = afbt__xmhsl[:xkeq__fnisu[-1]]
            lcqg__yzspb = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            udn__keg = len(data)
            eflm__ahx = np.empty(udn__keg, np.uint32)
            ninj__hghwk = udn__keg + 7 >> 3
            for i in range(udn__keg):
                eflm__ahx[i] = xkeq__fnisu[i + 1] - xkeq__fnisu[i]
            recv_counts = gather_scalar(np.int32(udn__keg), allgather, root
                =root)
            qlqw__fbbwk = recv_counts.sum()
            biqtq__uzf = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            sdxiu__sbiit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                biqtq__uzf = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for nnlya__tohn in range(len(recv_counts)):
                    recv_counts_nulls[nnlya__tohn] = recv_counts[nnlya__tohn
                        ] + 7 >> 3
                sdxiu__sbiit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            ujyoy__pfldz = np.empty(qlqw__fbbwk + 1, np.uint32)
            bdjg__qhcvx = bodo.gatherv(afbt__xmhsl, allgather, warn_if_rep,
                root)
            nrskw__iten = np.empty(qlqw__fbbwk + 7 >> 3, np.uint8)
            c_gatherv(eflm__ahx.ctypes, np.int32(udn__keg), ujyoy__pfldz.
                ctypes, recv_counts.ctypes, biqtq__uzf.ctypes, toi__sldjv,
                allgather, np.int32(root))
            c_gatherv(lcqg__yzspb.ctypes, np.int32(ninj__hghwk),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sdxiu__sbiit.ctypes, kmqxt__cyata, allgather, np.int32(root))
            dummy_use(data)
            luf__ydtn = np.empty(qlqw__fbbwk + 1, np.uint64)
            convert_len_arr_to_offset(ujyoy__pfldz.ctypes, luf__ydtn.ctypes,
                qlqw__fbbwk)
            copy_gathered_null_bytes(nrskw__iten.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                qlqw__fbbwk, bdjg__qhcvx, luf__ydtn, nrskw__iten)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        nojc__okoqt = data.names
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            blrxa__pfh = bodo.libs.struct_arr_ext.get_data(data)
            brx__fjx = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            wjox__xkz = bodo.gatherv(blrxa__pfh, allgather=allgather, root=root
                )
            rank = bodo.libs.distributed_api.get_rank()
            udn__keg = len(data)
            ninj__hghwk = udn__keg + 7 >> 3
            recv_counts = gather_scalar(np.int32(udn__keg), allgather, root
                =root)
            qlqw__fbbwk = recv_counts.sum()
            qhwn__kpepz = np.empty(qlqw__fbbwk + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            sdxiu__sbiit = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                sdxiu__sbiit = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(brx__fjx.ctypes, np.int32(ninj__hghwk),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes,
                sdxiu__sbiit.ctypes, kmqxt__cyata, allgather, np.int32(root))
            copy_gathered_null_bytes(qhwn__kpepz.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(wjox__xkz,
                qhwn__kpepz, nojc__okoqt)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            mua__etjpt = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(mua__etjpt)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            mua__etjpt = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(mua__etjpt)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            mua__etjpt = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(mua__etjpt)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            mua__etjpt = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            fsgtd__wmm = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            luih__ufdl = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            wcwb__fek = gather_scalar(data.shape[0], allgather, root=root)
            ifhhr__grfpd = wcwb__fek.sum()
            mqu__ygw = bodo.libs.distributed_api.dist_reduce(data.shape[1],
                np.int32(Reduce_Type.Max.value))
            mee__ivy = np.empty(ifhhr__grfpd + 1, np.int64)
            fsgtd__wmm = fsgtd__wmm.astype(np.int64)
            mee__ivy[0] = 0
            win__kcjf = 1
            kgtmv__tqj = 0
            for szk__rlwz in wcwb__fek:
                for hcb__anzsq in range(szk__rlwz):
                    wvrb__htcdl = luih__ufdl[kgtmv__tqj + 1] - luih__ufdl[
                        kgtmv__tqj]
                    mee__ivy[win__kcjf] = mee__ivy[win__kcjf - 1] + wvrb__htcdl
                    win__kcjf += 1
                    kgtmv__tqj += 1
                kgtmv__tqj += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(mua__etjpt,
                fsgtd__wmm, mee__ivy, (ifhhr__grfpd, mqu__ygw))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        affmm__bhjlk = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        affmm__bhjlk += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        eth__ewwt = {}
        exec(affmm__bhjlk, {'bodo': bodo}, eth__ewwt)
        mrvy__emt = eth__ewwt['impl_tuple']
        return mrvy__emt
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    affmm__bhjlk = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    affmm__bhjlk += '    if random:\n'
    affmm__bhjlk += '        if random_seed is None:\n'
    affmm__bhjlk += '            random = 1\n'
    affmm__bhjlk += '        else:\n'
    affmm__bhjlk += '            random = 2\n'
    affmm__bhjlk += '    if random_seed is None:\n'
    affmm__bhjlk += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        lfdp__ivtv = data
        mqu__ygw = len(lfdp__ivtv.columns)
        for i in range(mqu__ygw):
            affmm__bhjlk += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        affmm__bhjlk += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        uyna__qisa = ', '.join(f'data_{i}' for i in range(mqu__ygw))
        affmm__bhjlk += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(rsx__uxlfo) for
            rsx__uxlfo in range(mqu__ygw))))
        affmm__bhjlk += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        affmm__bhjlk += '    if dests is None:\n'
        affmm__bhjlk += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        affmm__bhjlk += '    else:\n'
        affmm__bhjlk += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for wfrt__neji in range(mqu__ygw):
            affmm__bhjlk += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(wfrt__neji))
        affmm__bhjlk += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(mqu__ygw))
        affmm__bhjlk += '    delete_table(out_table)\n'
        affmm__bhjlk += '    if parallel:\n'
        affmm__bhjlk += '        delete_table(table_total)\n'
        uyna__qisa = ', '.join('out_arr_{}'.format(i) for i in range(mqu__ygw))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        affmm__bhjlk += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(uyna__qisa, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        affmm__bhjlk += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        affmm__bhjlk += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        affmm__bhjlk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        affmm__bhjlk += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        affmm__bhjlk += '    if dests is None:\n'
        affmm__bhjlk += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        affmm__bhjlk += '    else:\n'
        affmm__bhjlk += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        affmm__bhjlk += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        affmm__bhjlk += """    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)
"""
        affmm__bhjlk += '    delete_table(out_table)\n'
        affmm__bhjlk += '    if parallel:\n'
        affmm__bhjlk += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        affmm__bhjlk += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        affmm__bhjlk += '    if not parallel:\n'
        affmm__bhjlk += '        return data\n'
        affmm__bhjlk += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        affmm__bhjlk += '    if dests is None:\n'
        affmm__bhjlk += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        affmm__bhjlk += '    elif bodo.get_rank() not in dests:\n'
        affmm__bhjlk += '        dim0_local_size = 0\n'
        affmm__bhjlk += '    else:\n'
        affmm__bhjlk += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        affmm__bhjlk += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        affmm__bhjlk += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        affmm__bhjlk += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        affmm__bhjlk += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        affmm__bhjlk += '    if dests is None:\n'
        affmm__bhjlk += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        affmm__bhjlk += '    else:\n'
        affmm__bhjlk += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        affmm__bhjlk += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        affmm__bhjlk += '    delete_table(out_table)\n'
        affmm__bhjlk += '    if parallel:\n'
        affmm__bhjlk += '        delete_table(table_total)\n'
        affmm__bhjlk += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    eth__ewwt = {}
    aeu__dcyi = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        aeu__dcyi.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(lfdp__ivtv.columns)})
    exec(affmm__bhjlk, aeu__dcyi, eth__ewwt)
    impl = eth__ewwt['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    affmm__bhjlk = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        affmm__bhjlk += '    if seed is None:\n'
        affmm__bhjlk += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        affmm__bhjlk += '    np.random.seed(seed)\n'
        affmm__bhjlk += '    if not parallel:\n'
        affmm__bhjlk += '        data = data.copy()\n'
        affmm__bhjlk += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            affmm__bhjlk += '        data = data[:n_samples]\n'
        affmm__bhjlk += '        return data\n'
        affmm__bhjlk += '    else:\n'
        affmm__bhjlk += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        affmm__bhjlk += '        permutation = np.arange(dim0_global_size)\n'
        affmm__bhjlk += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            affmm__bhjlk += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            affmm__bhjlk += '        n_samples = dim0_global_size\n'
        affmm__bhjlk += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        affmm__bhjlk += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        affmm__bhjlk += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        affmm__bhjlk += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        affmm__bhjlk += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        affmm__bhjlk += '        return output\n'
    else:
        affmm__bhjlk += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            affmm__bhjlk += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            affmm__bhjlk += '    output = output[:local_n_samples]\n'
        affmm__bhjlk += '    return output\n'
    eth__ewwt = {}
    exec(affmm__bhjlk, {'np': np, 'bodo': bodo}, eth__ewwt)
    impl = eth__ewwt['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    unrc__mksut = np.empty(sendcounts_nulls.sum(), np.uint8)
    yijhl__qbrs = 0
    dkdnc__rim = 0
    for ytf__jkaef in range(len(sendcounts)):
        fncl__ppofu = sendcounts[ytf__jkaef]
        ninj__hghwk = sendcounts_nulls[ytf__jkaef]
        mft__lou = unrc__mksut[yijhl__qbrs:yijhl__qbrs + ninj__hghwk]
        for tojl__bau in range(fncl__ppofu):
            set_bit_to_arr(mft__lou, tojl__bau, get_bit_bitmap(
                null_bitmap_ptr, dkdnc__rim))
            dkdnc__rim += 1
        yijhl__qbrs += ninj__hghwk
    return unrc__mksut


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    faxh__oyq = MPI.COMM_WORLD
    data = faxh__oyq.bcast(data, root)
    return data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_scatterv_send_counts(send_counts, n_pes, n):
    if not is_overload_none(send_counts):
        return lambda send_counts, n_pes, n: send_counts

    def impl(send_counts, n_pes, n):
        send_counts = np.empty(n_pes, np.int32)
        for i in range(n_pes):
            send_counts[i] = get_node_portion(n, n_pes, i)
        return send_counts
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _scatterv_np(data, send_counts=None, warn_if_dist=True):
    typ_val = numba_to_c_type(data.dtype)
    xiotj__abgef = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    khoba__ushis = (0,) * xiotj__abgef

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        knwwb__paiy = np.ascontiguousarray(data)
        zrfea__qnao = data.ctypes
        uorwx__eqa = khoba__ushis
        if rank == MPI_ROOT:
            uorwx__eqa = knwwb__paiy.shape
        uorwx__eqa = bcast_tuple(uorwx__eqa)
        dkdq__pwni = get_tuple_prod(uorwx__eqa[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            uorwx__eqa[0])
        send_counts *= dkdq__pwni
        udn__keg = send_counts[rank]
        btsmy__qwnxj = np.empty(udn__keg, dtype)
        biqtq__uzf = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(zrfea__qnao, send_counts.ctypes, biqtq__uzf.ctypes,
            btsmy__qwnxj.ctypes, np.int32(udn__keg), np.int32(typ_val))
        return btsmy__qwnxj.reshape((-1,) + uorwx__eqa[1:])
    return scatterv_arr_impl


def _get_name_value_for_type(name_typ):
    assert isinstance(name_typ, (types.UnicodeType, types.StringLiteral)
        ) or name_typ == types.none
    return None if name_typ == types.none else '_' + str(ir_utils.next_label())


def get_value_for_type(dtype):
    if isinstance(dtype, types.Array):
        return np.zeros((1,) * dtype.ndim, numba.np.numpy_support.as_dtype(
            dtype.dtype))
    if dtype == string_array_type:
        return pd.array(['A'], 'string')
    if dtype == bodo.dict_str_arr_type:
        import pyarrow as pa
        return pa.array(['a'], type=pa.dictionary(pa.int32(), pa.string()))
    if dtype == binary_array_type:
        return np.array([b'A'], dtype=object)
    if isinstance(dtype, IntegerArrayType):
        kvzmu__zvetd = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], kvzmu__zvetd)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        qhlqf__xmajp = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=qhlqf__xmajp)
        kxch__xuu = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(kxch__xuu)
        return pd.Index(arr, name=qhlqf__xmajp)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        qhlqf__xmajp = _get_name_value_for_type(dtype.name_typ)
        nojc__okoqt = tuple(_get_name_value_for_type(t) for t in dtype.
            names_typ)
        dyln__ibj = tuple(get_value_for_type(t) for t in dtype.array_types)
        dyln__ibj = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in dyln__ibj)
        val = pd.MultiIndex.from_arrays(dyln__ibj, names=nojc__okoqt)
        val.name = qhlqf__xmajp
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        qhlqf__xmajp = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=qhlqf__xmajp)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dyln__ibj = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({qhlqf__xmajp: arr for qhlqf__xmajp, arr in zip
            (dtype.columns, dyln__ibj)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        kxch__xuu = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(kxch__xuu[0], kxch__xuu
            [0])])
    raise BodoError(f'get_value_for_type(dtype): Missing data type {dtype}')


def scatterv(data, send_counts=None, warn_if_dist=True):
    rank = bodo.libs.distributed_api.get_rank()
    if rank != MPI_ROOT and data is not None:
        warnings.warn(BodoWarning(
            "bodo.scatterv(): A non-None value for 'data' was found on a rank other than the root. This data won't be sent to any other ranks and will be overwritten with data from rank 0."
            ))
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return scatterv_impl(data, send_counts)


@overload(scatterv)
def scatterv_overload(data, send_counts=None, warn_if_dist=True):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.scatterv()')
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.scatterv()')
    return lambda data, send_counts=None, warn_if_dist=True: scatterv_impl(data
        , send_counts)


@numba.generated_jit(nopython=True)
def scatterv_impl(data, send_counts=None, warn_if_dist=True):
    if isinstance(data, types.Array):
        return lambda data, send_counts=None, warn_if_dist=True: _scatterv_np(
            data, send_counts)
    if is_str_arr_type(data) or data == binary_array_type:
        toi__sldjv = np.int32(numba_to_c_type(types.int32))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            batw__oamu = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            batw__oamu = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        affmm__bhjlk = f"""def impl(
            data, send_counts=None, warn_if_dist=True
        ):  # pragma: no cover
            data = decode_if_dict_array(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            n_all = bodo.libs.distributed_api.bcast_scalar(len(data))

            # convert offsets to lengths of strings
            send_arr_lens = np.empty(
                len(data), np.uint32
            )  # XXX offset type is offset_type, lengths for comm are uint32
            for i in range(len(data)):
                send_arr_lens[i] = bodo.libs.str_arr_ext.get_str_arr_item_length(
                    data, i
                )

            # ------- calculate buffer counts -------

            send_counts = bodo.libs.distributed_api._get_scatterv_send_counts(send_counts, n_pes, n_all)

            # displacements
            displs = bodo.ir.join.calc_disp(send_counts)

            # compute send counts for characters
            send_counts_char = np.empty(n_pes, np.int32)
            if rank == 0:
                curr_str = 0
                for i in range(n_pes):
                    c = 0
                    for _ in range(send_counts[i]):
                        c += send_arr_lens[curr_str]
                        curr_str += 1
                    send_counts_char[i] = c

            bodo.libs.distributed_api.bcast(send_counts_char)

            # displacements for characters
            displs_char = bodo.ir.join.calc_disp(send_counts_char)

            # compute send counts for nulls
            send_counts_nulls = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                send_counts_nulls[i] = (send_counts[i] + 7) >> 3

            # displacements for nulls
            displs_nulls = bodo.ir.join.calc_disp(send_counts_nulls)

            # alloc output array
            n_loc = send_counts[rank]  # total number of elements on this PE
            n_loc_char = send_counts_char[rank]
            recv_arr = {batw__oamu}(n_loc, n_loc_char)

            # ----- string lengths -----------

            recv_lens = np.empty(n_loc, np.uint32)
            bodo.libs.distributed_api.c_scatterv(
                send_arr_lens.ctypes,
                send_counts.ctypes,
                displs.ctypes,
                recv_lens.ctypes,
                np.int32(n_loc),
                int32_typ_enum,
            )

            # TODO: don't hardcode offset type. Also, if offset is 32 bit we can
            # use the same buffer
            bodo.libs.str_arr_ext.convert_len_arr_to_offset(recv_lens.ctypes, bodo.libs.str_arr_ext.get_offset_ptr(recv_arr), n_loc)

            # ----- string characters -----------

            bodo.libs.distributed_api.c_scatterv(
                bodo.libs.str_arr_ext.get_data_ptr(data),
                send_counts_char.ctypes,
                displs_char.ctypes,
                bodo.libs.str_arr_ext.get_data_ptr(recv_arr),
                np.int32(n_loc_char),
                char_typ_enum,
            )

            # ----------- null bitmap -------------

            n_recv_bytes = (n_loc + 7) >> 3

            send_null_bitmap = bodo.libs.distributed_api.get_scatter_null_bytes_buff(
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(data), send_counts, send_counts_nulls
            )

            bodo.libs.distributed_api.c_scatterv(
                send_null_bitmap.ctypes,
                send_counts_nulls.ctypes,
                displs_nulls.ctypes,
                bodo.libs.str_arr_ext.get_null_bitmap_ptr(recv_arr),
                np.int32(n_recv_bytes),
                char_typ_enum,
            )

            return recv_arr"""
        eth__ewwt = dict()
        exec(affmm__bhjlk, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            toi__sldjv, 'char_typ_enum': kmqxt__cyata,
            'decode_if_dict_array': decode_if_dict_array}, eth__ewwt)
        impl = eth__ewwt['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        toi__sldjv = np.int32(numba_to_c_type(types.int32))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            rbusd__vbeu = bodo.libs.array_item_arr_ext.get_offsets(data)
            rbekf__bllh = bodo.libs.array_item_arr_ext.get_data(data)
            rbekf__bllh = rbekf__bllh[:rbusd__vbeu[-1]]
            gotsm__xpg = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            cvtzr__prhha = bcast_scalar(len(data))
            gsn__dhct = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                gsn__dhct[i] = rbusd__vbeu[i + 1] - rbusd__vbeu[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                cvtzr__prhha)
            biqtq__uzf = bodo.ir.join.calc_disp(send_counts)
            cvef__xelx = np.empty(n_pes, np.int32)
            if rank == 0:
                kadhs__itpsy = 0
                for i in range(n_pes):
                    pmi__mhvf = 0
                    for hcb__anzsq in range(send_counts[i]):
                        pmi__mhvf += gsn__dhct[kadhs__itpsy]
                        kadhs__itpsy += 1
                    cvef__xelx[i] = pmi__mhvf
            bcast(cvef__xelx)
            mob__mqt = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                mob__mqt[i] = send_counts[i] + 7 >> 3
            sdxiu__sbiit = bodo.ir.join.calc_disp(mob__mqt)
            udn__keg = send_counts[rank]
            uyifh__amnd = np.empty(udn__keg + 1, np_offset_type)
            jfe__qrkh = bodo.libs.distributed_api.scatterv_impl(rbekf__bllh,
                cvef__xelx)
            qfgwb__iqu = udn__keg + 7 >> 3
            jrod__yhqre = np.empty(qfgwb__iqu, np.uint8)
            sjj__vrt = np.empty(udn__keg, np.uint32)
            c_scatterv(gsn__dhct.ctypes, send_counts.ctypes, biqtq__uzf.
                ctypes, sjj__vrt.ctypes, np.int32(udn__keg), toi__sldjv)
            convert_len_arr_to_offset(sjj__vrt.ctypes, uyifh__amnd.ctypes,
                udn__keg)
            yqg__kevuj = get_scatter_null_bytes_buff(gotsm__xpg.ctypes,
                send_counts, mob__mqt)
            c_scatterv(yqg__kevuj.ctypes, mob__mqt.ctypes, sdxiu__sbiit.
                ctypes, jrod__yhqre.ctypes, np.int32(qfgwb__iqu), kmqxt__cyata)
            return bodo.libs.array_item_arr_ext.init_array_item_array(udn__keg,
                jfe__qrkh, uyifh__amnd, jrod__yhqre)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            khz__gihd = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            khz__gihd = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            khz__gihd = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            khz__gihd = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            knwwb__paiy = data._data
            brx__fjx = data._null_bitmap
            xxx__izh = len(knwwb__paiy)
            ndp__snvsh = _scatterv_np(knwwb__paiy, send_counts)
            cvtzr__prhha = bcast_scalar(xxx__izh)
            wpm__qvalp = len(ndp__snvsh) + 7 >> 3
            hcu__mskj = np.empty(wpm__qvalp, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                cvtzr__prhha)
            mob__mqt = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                mob__mqt[i] = send_counts[i] + 7 >> 3
            sdxiu__sbiit = bodo.ir.join.calc_disp(mob__mqt)
            yqg__kevuj = get_scatter_null_bytes_buff(brx__fjx.ctypes,
                send_counts, mob__mqt)
            c_scatterv(yqg__kevuj.ctypes, mob__mqt.ctypes, sdxiu__sbiit.
                ctypes, hcu__mskj.ctypes, np.int32(wpm__qvalp), kmqxt__cyata)
            return khz__gihd(ndp__snvsh, hcu__mskj)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            mzq__okcp = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            fylm__lez = bodo.libs.distributed_api.scatterv_impl(data._right,
                send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(mzq__okcp,
                fylm__lez)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            pde__bti = data._start
            ftn__fez = data._stop
            yxh__ikaiu = data._step
            qhlqf__xmajp = data._name
            qhlqf__xmajp = bcast_scalar(qhlqf__xmajp)
            pde__bti = bcast_scalar(pde__bti)
            ftn__fez = bcast_scalar(ftn__fez)
            yxh__ikaiu = bcast_scalar(yxh__ikaiu)
            exmy__bbfm = bodo.libs.array_kernels.calc_nitems(pde__bti,
                ftn__fez, yxh__ikaiu)
            chunk_start = bodo.libs.distributed_api.get_start(exmy__bbfm,
                n_pes, rank)
            ocytb__ljusx = bodo.libs.distributed_api.get_node_portion(
                exmy__bbfm, n_pes, rank)
            znmtq__soai = pde__bti + yxh__ikaiu * chunk_start
            cahav__yyigz = pde__bti + yxh__ikaiu * (chunk_start + ocytb__ljusx)
            cahav__yyigz = min(cahav__yyigz, ftn__fez)
            return bodo.hiframes.pd_index_ext.init_range_index(znmtq__soai,
                cahav__yyigz, yxh__ikaiu, qhlqf__xmajp)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        tfe__kiryi = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            knwwb__paiy = data._data
            qhlqf__xmajp = data._name
            qhlqf__xmajp = bcast_scalar(qhlqf__xmajp)
            arr = bodo.libs.distributed_api.scatterv_impl(knwwb__paiy,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                qhlqf__xmajp, tfe__kiryi)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            knwwb__paiy = data._data
            qhlqf__xmajp = data._name
            qhlqf__xmajp = bcast_scalar(qhlqf__xmajp)
            arr = bodo.libs.distributed_api.scatterv_impl(knwwb__paiy,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, qhlqf__xmajp)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            mua__etjpt = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            qhlqf__xmajp = bcast_scalar(data._name)
            nojc__okoqt = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(mua__etjpt
                , nojc__okoqt, qhlqf__xmajp)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qhlqf__xmajp = bodo.hiframes.pd_series_ext.get_series_name(data)
            fiuo__dzwpt = bcast_scalar(qhlqf__xmajp)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            lspgq__rpba = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lspgq__rpba, fiuo__dzwpt)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mqu__ygw = len(data.columns)
        uyna__qisa = ', '.join('g_data_{}'.format(i) for i in range(mqu__ygw))
        cwnwp__mdtq = ColNamesMetaType(data.columns)
        affmm__bhjlk = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(mqu__ygw):
            affmm__bhjlk += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            affmm__bhjlk += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        affmm__bhjlk += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        affmm__bhjlk += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        affmm__bhjlk += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({uyna__qisa},), g_index, __col_name_meta_scaterv_impl)
"""
        eth__ewwt = {}
        exec(affmm__bhjlk, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            cwnwp__mdtq}, eth__ewwt)
        grckz__qmofx = eth__ewwt['impl_df']
        return grckz__qmofx
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            ecaz__fqnpl = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                ecaz__fqnpl, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        affmm__bhjlk = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        affmm__bhjlk += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        eth__ewwt = {}
        exec(affmm__bhjlk, {'bodo': bodo}, eth__ewwt)
        mrvy__emt = eth__ewwt['impl_tuple']
        return mrvy__emt
    if data is types.none:
        return lambda data, send_counts=None, warn_if_dist=True: None
    raise BodoError('scatterv() not available for {}'.format(data))


@intrinsic
def cptr_to_voidptr(typingctx, cptr_tp=None):

    def codegen(context, builder, sig, args):
        return builder.bitcast(args[0], lir.IntType(8).as_pointer())
    return types.voidptr(cptr_tp), codegen


def bcast(data, root=MPI_ROOT):
    return


@overload(bcast, no_unliteral=True)
def bcast_overload(data, root=MPI_ROOT):
    bodo.hiframes.pd_timestamp_ext.check_tz_aware_unsupported(data,
        'bodo.bcast()')
    if isinstance(data, types.Array):

        def bcast_impl(data, root=MPI_ROOT):
            typ_enum = get_type_enum(data)
            count = data.size
            assert count < INT_MAX
            c_bcast(data.ctypes, np.int32(count), typ_enum, np.array([-1]).
                ctypes, 0, np.int32(root))
            return
        return bcast_impl
    if isinstance(data, DecimalArrayType):

        def bcast_decimal_arr(data, root=MPI_ROOT):
            count = data._data.size
            assert count < INT_MAX
            c_bcast(data._data.ctypes, np.int32(count), CTypeEnum.Int128.
                value, np.array([-1]).ctypes, 0, np.int32(root))
            bcast(data._null_bitmap, root)
            return
        return bcast_decimal_arr
    if isinstance(data, IntegerArrayType) or data in (boolean_array,
        datetime_date_array_type):

        def bcast_impl_int_arr(data, root=MPI_ROOT):
            bcast(data._data, root)
            bcast(data._null_bitmap, root)
            return
        return bcast_impl_int_arr
    if is_str_arr_type(data) or data == binary_array_type:
        jeza__avt = np.int32(numba_to_c_type(offset_type))
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            udn__keg = len(data)
            xub__telea = num_total_chars(data)
            assert udn__keg < INT_MAX
            assert xub__telea < INT_MAX
            kmsp__uym = get_offset_ptr(data)
            zrfea__qnao = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            ninj__hghwk = udn__keg + 7 >> 3
            c_bcast(kmsp__uym, np.int32(udn__keg + 1), jeza__avt, np.array(
                [-1]).ctypes, 0, np.int32(root))
            c_bcast(zrfea__qnao, np.int32(xub__telea), kmqxt__cyata, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(ninj__hghwk), kmqxt__cyata,
                np.array([-1]).ctypes, 0, np.int32(root))
        return bcast_str_impl


c_bcast = types.ExternalFunction('c_bcast', types.void(types.voidptr, types
    .int32, types.int32, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def bcast_scalar(val, root=MPI_ROOT):
    val = types.unliteral(val)
    if not (isinstance(val, (types.Integer, types.Float)) or val in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.string_type, types.none,
        types.bool_]):
        raise BodoError(
            f'bcast_scalar requires an argument of type Integer, Float, datetime64ns, timedelta64ns, string, None, or Bool. Found type {val}'
            )
    if val == types.none:
        return lambda val, root=MPI_ROOT: None
    if val == bodo.string_type:
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                eyjcw__sucv = 0
                rjpzv__pzmg = np.empty(0, np.uint8).ctypes
            else:
                rjpzv__pzmg, eyjcw__sucv = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            eyjcw__sucv = bodo.libs.distributed_api.bcast_scalar(eyjcw__sucv,
                root)
            if rank != root:
                nzbze__rdwn = np.empty(eyjcw__sucv + 1, np.uint8)
                nzbze__rdwn[eyjcw__sucv] = 0
                rjpzv__pzmg = nzbze__rdwn.ctypes
            c_bcast(rjpzv__pzmg, np.int32(eyjcw__sucv), kmqxt__cyata, np.
                array([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(rjpzv__pzmg, eyjcw__sucv)
        return impl_str
    typ_val = numba_to_c_type(val)
    affmm__bhjlk = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    eth__ewwt = {}
    exec(affmm__bhjlk, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, eth__ewwt)
    hro__impxj = eth__ewwt['bcast_scalar_impl']
    return hro__impxj


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    auwlb__bkprq = len(val)
    affmm__bhjlk = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    affmm__bhjlk += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(auwlb__bkprq
        )), ',' if auwlb__bkprq else '')
    eth__ewwt = {}
    exec(affmm__bhjlk, {'bcast_scalar': bcast_scalar}, eth__ewwt)
    ltq__muem = eth__ewwt['bcast_tuple_impl']
    return ltq__muem


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            udn__keg = bcast_scalar(len(arr), root)
            dzzql__jwy = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(udn__keg, dzzql__jwy)
            return arr
        return prealloc_impl
    return lambda arr, root=MPI_ROOT: arr


def get_local_slice(idx, arr_start, total_len):
    return idx


@overload(get_local_slice, no_unliteral=True, jit_options={'cache': True,
    'no_cpython_wrapper': True})
def get_local_slice_overload(idx, arr_start, total_len):
    if not idx.has_step:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            znmtq__soai = max(arr_start, slice_index.start) - arr_start
            cahav__yyigz = max(slice_index.stop - arr_start, 0)
            return slice(znmtq__soai, cahav__yyigz)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            pde__bti = slice_index.start
            yxh__ikaiu = slice_index.step
            zral__yuryw = (0 if yxh__ikaiu == 1 or pde__bti > arr_start else
                abs(yxh__ikaiu - arr_start % yxh__ikaiu) % yxh__ikaiu)
            znmtq__soai = max(arr_start, slice_index.start
                ) - arr_start + zral__yuryw
            cahav__yyigz = max(slice_index.stop - arr_start, 0)
            return slice(znmtq__soai, cahav__yyigz, yxh__ikaiu)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        ywv__yfh = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[ywv__yfh])
    return getitem_impl


dummy_use = numba.njit(lambda a: None)


def int_getitem(arr, ind, arr_start, total_len, is_1D):
    return arr[ind]


def transform_str_getitem_output(data, length):
    pass


@overload(transform_str_getitem_output)
def overload_transform_str_getitem_output(data, length):
    if data == bodo.string_type:
        return lambda data, length: bodo.libs.str_arr_ext.decode_utf8(data.
            _data, length)
    if data == types.Array(types.uint8, 1, 'C'):
        return lambda data, length: bodo.libs.binary_arr_ext.init_bytes_type(
            data, length)
    raise BodoError(
        f'Internal Error: Expected String or Uint8 Array, found {data}')


@overload(int_getitem, no_unliteral=True)
def int_getitem_overload(arr, ind, arr_start, total_len, is_1D):
    if is_str_arr_type(arr) or arr == bodo.binary_array_type:
        dghr__fwmk = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        kmqxt__cyata = np.int32(numba_to_c_type(types.uint8))
        nkbx__roz = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            ewx__hil = np.int32(10)
            tag = np.int32(11)
            khz__ouf = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                afbt__xmhsl = arr._data
                huk__dibi = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    afbt__xmhsl, ind)
                ctud__oixy = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    afbt__xmhsl, ind + 1)
                length = ctud__oixy - huk__dibi
                fpny__xrlb = afbt__xmhsl[ind]
                khz__ouf[0] = length
                isend(khz__ouf, np.int32(1), root, ewx__hil, True)
                isend(fpny__xrlb, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(nkbx__roz,
                dghr__fwmk, 0, 1)
            vtxlq__cwf = 0
            if rank == root:
                vtxlq__cwf = recv(np.int64, ANY_SOURCE, ewx__hil)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    nkbx__roz, dghr__fwmk, vtxlq__cwf, 1)
                zrfea__qnao = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(zrfea__qnao, np.int32(vtxlq__cwf), kmqxt__cyata,
                    ANY_SOURCE, tag)
            dummy_use(khz__ouf)
            vtxlq__cwf = bcast_scalar(vtxlq__cwf)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    nkbx__roz, dghr__fwmk, vtxlq__cwf, 1)
            zrfea__qnao = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(zrfea__qnao, np.int32(vtxlq__cwf), kmqxt__cyata, np.
                array([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, vtxlq__cwf)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        gwbhl__vjgcb = (bodo.hiframes.pd_categorical_ext.
            get_categories_int_type(arr.dtype))

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, gwbhl__vjgcb)
            if arr_start <= ind < arr_start + len(arr):
                ecaz__fqnpl = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = ecaz__fqnpl[ind - arr_start]
                send_arr = np.full(1, data, gwbhl__vjgcb)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = gwbhl__vjgcb(-1)
            if rank == root:
                val = recv(gwbhl__vjgcb, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            hvggr__ozy = arr.dtype.categories[max(val, 0)]
            return hvggr__ozy
        return cat_getitem_impl
    jaq__uciab = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, jaq__uciab)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, jaq__uciab)[0]
        if rank == root:
            val = recv(jaq__uciab, ANY_SOURCE, tag)
        dummy_use(send_arr)
        val = bcast_scalar(val)
        return val
    return getitem_impl


c_alltoallv = types.ExternalFunction('c_alltoallv', types.void(types.
    voidptr, types.voidptr, types.voidptr, types.voidptr, types.voidptr,
    types.voidptr, types.int32))


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def alltoallv(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    typ_enum = get_type_enum(send_data)
    igci__mbpic = get_type_enum(out_data)
    assert typ_enum == igci__mbpic
    if isinstance(send_data, (IntegerArrayType, DecimalArrayType)
        ) or send_data in (boolean_array, datetime_date_array_type):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data._data.ctypes,
            out_data._data.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    if isinstance(send_data, bodo.CategoricalArrayType):
        return (lambda send_data, out_data, send_counts, recv_counts,
            send_disp, recv_disp: c_alltoallv(send_data.codes.ctypes,
            out_data.codes.ctypes, send_counts.ctypes, recv_counts.ctypes,
            send_disp.ctypes, recv_disp.ctypes, typ_enum))
    return (lambda send_data, out_data, send_counts, recv_counts, send_disp,
        recv_disp: c_alltoallv(send_data.ctypes, out_data.ctypes,
        send_counts.ctypes, recv_counts.ctypes, send_disp.ctypes, recv_disp
        .ctypes, typ_enum))


def alltoallv_tup(send_data, out_data, send_counts, recv_counts, send_disp,
    recv_disp):
    return


@overload(alltoallv_tup, no_unliteral=True)
def alltoallv_tup_overload(send_data, out_data, send_counts, recv_counts,
    send_disp, recv_disp):
    count = send_data.count
    assert out_data.count == count
    affmm__bhjlk = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        affmm__bhjlk += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    affmm__bhjlk += '  return\n'
    eth__ewwt = {}
    exec(affmm__bhjlk, {'alltoallv': alltoallv}, eth__ewwt)
    wrw__csqip = eth__ewwt['f']
    return wrw__csqip


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    pde__bti = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return pde__bti, count


@numba.njit
def get_start(total_size, pes, rank):
    viiu__ato = total_size % pes
    rmne__hhnib = (total_size - viiu__ato) // pes
    return rank * rmne__hhnib + min(rank, viiu__ato)


@numba.njit
def get_end(total_size, pes, rank):
    viiu__ato = total_size % pes
    rmne__hhnib = (total_size - viiu__ato) // pes
    return (rank + 1) * rmne__hhnib + min(rank + 1, viiu__ato)


@numba.njit
def get_node_portion(total_size, pes, rank):
    viiu__ato = total_size % pes
    rmne__hhnib = (total_size - viiu__ato) // pes
    if rank < viiu__ato:
        return rmne__hhnib + 1
    else:
        return rmne__hhnib


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    aswta__dfikq = in_arr.dtype(0)
    dkb__ckk = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        pmi__mhvf = aswta__dfikq
        for jxty__wxdhm in np.nditer(in_arr):
            pmi__mhvf += jxty__wxdhm.item()
        prvvs__yjujr = dist_exscan(pmi__mhvf, dkb__ckk)
        for i in range(in_arr.size):
            prvvs__yjujr += in_arr[i]
            out_arr[i] = prvvs__yjujr
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    fbnh__laxyf = in_arr.dtype(1)
    dkb__ckk = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        pmi__mhvf = fbnh__laxyf
        for jxty__wxdhm in np.nditer(in_arr):
            pmi__mhvf *= jxty__wxdhm.item()
        prvvs__yjujr = dist_exscan(pmi__mhvf, dkb__ckk)
        if get_rank() == 0:
            prvvs__yjujr = fbnh__laxyf
        for i in range(in_arr.size):
            prvvs__yjujr *= in_arr[i]
            out_arr[i] = prvvs__yjujr
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        fbnh__laxyf = np.finfo(in_arr.dtype(1).dtype).max
    else:
        fbnh__laxyf = np.iinfo(in_arr.dtype(1).dtype).max
    dkb__ckk = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        pmi__mhvf = fbnh__laxyf
        for jxty__wxdhm in np.nditer(in_arr):
            pmi__mhvf = min(pmi__mhvf, jxty__wxdhm.item())
        prvvs__yjujr = dist_exscan(pmi__mhvf, dkb__ckk)
        if get_rank() == 0:
            prvvs__yjujr = fbnh__laxyf
        for i in range(in_arr.size):
            prvvs__yjujr = min(prvvs__yjujr, in_arr[i])
            out_arr[i] = prvvs__yjujr
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        fbnh__laxyf = np.finfo(in_arr.dtype(1).dtype).min
    else:
        fbnh__laxyf = np.iinfo(in_arr.dtype(1).dtype).min
    fbnh__laxyf = in_arr.dtype(1)
    dkb__ckk = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        pmi__mhvf = fbnh__laxyf
        for jxty__wxdhm in np.nditer(in_arr):
            pmi__mhvf = max(pmi__mhvf, jxty__wxdhm.item())
        prvvs__yjujr = dist_exscan(pmi__mhvf, dkb__ckk)
        if get_rank() == 0:
            prvvs__yjujr = fbnh__laxyf
        for i in range(in_arr.size):
            prvvs__yjujr = max(prvvs__yjujr, in_arr[i])
            out_arr[i] = prvvs__yjujr
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    wwvqe__sdc = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), wwvqe__sdc)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    gja__ieu = args[0]
    if equiv_set.has_shape(gja__ieu):
        return ArrayAnalysis.AnalyzeResult(shape=gja__ieu, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_dist_return = (
    dist_return_equiv)
ArrayAnalysis._analyze_op_call_bodo_libs_distributed_api_rep_return = (
    dist_return_equiv)


def threaded_return(A):
    return A


@numba.njit
def set_arr_local(arr, ind, val):
    arr[ind] = val


@numba.njit
def local_alloc_size(n, in_arr):
    return n


@infer_global(threaded_return)
@infer_global(dist_return)
@infer_global(rep_return)
class ThreadedRetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        return signature(args[0], *args)


@numba.njit
def parallel_print(*args):
    print(*args)


@numba.njit
def single_print(*args):
    if bodo.libs.distributed_api.get_rank() == 0:
        print(*args)


def print_if_not_empty(args):
    pass


@overload(print_if_not_empty)
def overload_print_if_not_empty(*args):
    xrbyw__fqmx = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for
        i, jnlu__xoic in enumerate(args) if is_array_typ(jnlu__xoic) or
        isinstance(jnlu__xoic, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    affmm__bhjlk = f"""def impl(*args):
    if {xrbyw__fqmx} or bodo.get_rank() == 0:
        print(*args)"""
    eth__ewwt = {}
    exec(affmm__bhjlk, globals(), eth__ewwt)
    impl = eth__ewwt['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        zeduw__outxb = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        affmm__bhjlk = 'def f(req, cond=True):\n'
        affmm__bhjlk += f'  return {zeduw__outxb}\n'
        eth__ewwt = {}
        exec(affmm__bhjlk, {'_wait': _wait}, eth__ewwt)
        impl = eth__ewwt['f']
        return impl
    if is_overload_none(req):
        return lambda req, cond=True: None
    return lambda req, cond=True: _wait(req, cond)


@register_jitable
def _set_if_in_range(A, val, index, chunk_start):
    if index >= chunk_start and index < chunk_start + len(A):
        A[index - chunk_start] = val


@register_jitable
def _root_rank_select(old_val, new_val):
    if get_rank() == 0:
        return old_val
    return new_val


def get_tuple_prod(t):
    return np.prod(t)


@overload(get_tuple_prod, no_unliteral=True)
def get_tuple_prod_overload(t):
    if t == numba.core.types.containers.Tuple(()):
        return lambda t: 1

    def get_tuple_prod_impl(t):
        viiu__ato = 1
        for a in t:
            viiu__ato *= a
        return viiu__ato
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    xxlmm__nlgo = np.ascontiguousarray(in_arr)
    mtw__nxv = get_tuple_prod(xxlmm__nlgo.shape[1:])
    ykv__rdyo = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        ogcj__rzuxv = np.array(dest_ranks, dtype=np.int32)
    else:
        ogcj__rzuxv = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, xxlmm__nlgo.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * ykv__rdyo, 
        dtype_size * mtw__nxv, len(ogcj__rzuxv), ogcj__rzuxv.ctypes)
    check_and_propagate_cpp_exception()


permutation_int = types.ExternalFunction('permutation_int', types.void(
    types.voidptr, types.intp))


@numba.njit
def dist_permutation_int(lhs, n):
    permutation_int(lhs.ctypes, n)


permutation_array_index = types.ExternalFunction('permutation_array_index',
    types.void(types.voidptr, types.intp, types.intp, types.voidptr, types.
    int64, types.voidptr, types.intp, types.int64))


@numba.njit
def dist_permutation_array_index(lhs, lhs_len, dtype_size, rhs, p, p_len,
    n_samples):
    jlgph__kiid = np.ascontiguousarray(rhs)
    jrd__zhfen = get_tuple_prod(jlgph__kiid.shape[1:])
    qjl__wnr = dtype_size * jrd__zhfen
    permutation_array_index(lhs.ctypes, lhs_len, qjl__wnr, jlgph__kiid.
        ctypes, jlgph__kiid.shape[0], p.ctypes, p_len, n_samples)
    check_and_propagate_cpp_exception()


from bodo.io import fsspec_reader, hdfs_reader, s3_reader
ll.add_symbol('finalize', hdist.finalize)
finalize = types.ExternalFunction('finalize', types.int32())
ll.add_symbol('finalize_s3', s3_reader.finalize_s3)
finalize_s3 = types.ExternalFunction('finalize_s3', types.int32())
ll.add_symbol('finalize_fsspec', fsspec_reader.finalize_fsspec)
finalize_fsspec = types.ExternalFunction('finalize_fsspec', types.int32())
ll.add_symbol('disconnect_hdfs', hdfs_reader.disconnect_hdfs)
disconnect_hdfs = types.ExternalFunction('disconnect_hdfs', types.int32())


def _check_for_cpp_errors():
    pass


@overload(_check_for_cpp_errors)
def overload_check_for_cpp_errors():
    return lambda : check_and_propagate_cpp_exception()


@numba.njit
def call_finalize():
    finalize()
    finalize_s3()
    finalize_fsspec()
    _check_for_cpp_errors()
    disconnect_hdfs()


def flush_stdout():
    if not sys.stdout.closed:
        sys.stdout.flush()


atexit.register(call_finalize)
atexit.register(flush_stdout)


def bcast_comm(data, comm_ranks, nranks, root=MPI_ROOT):
    rank = bodo.libs.distributed_api.get_rank()
    dtype = bodo.typeof(data)
    dtype = _bcast_dtype(dtype, root)
    if rank != MPI_ROOT:
        data = get_value_for_type(dtype)
    return bcast_comm_impl(data, comm_ranks, nranks, root)


@overload(bcast_comm)
def bcast_comm_overload(data, comm_ranks, nranks, root=MPI_ROOT):
    return lambda data, comm_ranks, nranks, root=MPI_ROOT: bcast_comm_impl(data
        , comm_ranks, nranks, root)


@numba.generated_jit(nopython=True)
def bcast_comm_impl(data, comm_ranks, nranks, root=MPI_ROOT):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.bcast_comm()')
    if isinstance(data, (types.Integer, types.Float)):
        typ_val = numba_to_c_type(data)
        affmm__bhjlk = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        eth__ewwt = {}
        exec(affmm__bhjlk, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, eth__ewwt)
        hro__impxj = eth__ewwt['bcast_scalar_impl']
        return hro__impxj
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mqu__ygw = len(data.columns)
        uyna__qisa = ', '.join('g_data_{}'.format(i) for i in range(mqu__ygw))
        tcfe__soisj = ColNamesMetaType(data.columns)
        affmm__bhjlk = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(mqu__ygw):
            affmm__bhjlk += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            affmm__bhjlk += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        affmm__bhjlk += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        affmm__bhjlk += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        affmm__bhjlk += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(uyna__qisa))
        eth__ewwt = {}
        exec(affmm__bhjlk, {'bodo': bodo,
            '__col_name_meta_value_bcast_comm': tcfe__soisj}, eth__ewwt)
        grckz__qmofx = eth__ewwt['impl_df']
        return grckz__qmofx
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            pde__bti = data._start
            ftn__fez = data._stop
            yxh__ikaiu = data._step
            qhlqf__xmajp = data._name
            qhlqf__xmajp = bcast_scalar(qhlqf__xmajp, root)
            pde__bti = bcast_scalar(pde__bti, root)
            ftn__fez = bcast_scalar(ftn__fez, root)
            yxh__ikaiu = bcast_scalar(yxh__ikaiu, root)
            exmy__bbfm = bodo.libs.array_kernels.calc_nitems(pde__bti,
                ftn__fez, yxh__ikaiu)
            chunk_start = bodo.libs.distributed_api.get_start(exmy__bbfm,
                n_pes, rank)
            ocytb__ljusx = bodo.libs.distributed_api.get_node_portion(
                exmy__bbfm, n_pes, rank)
            znmtq__soai = pde__bti + yxh__ikaiu * chunk_start
            cahav__yyigz = pde__bti + yxh__ikaiu * (chunk_start + ocytb__ljusx)
            cahav__yyigz = min(cahav__yyigz, ftn__fez)
            return bodo.hiframes.pd_index_ext.init_range_index(znmtq__soai,
                cahav__yyigz, yxh__ikaiu, qhlqf__xmajp)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            knwwb__paiy = data._data
            qhlqf__xmajp = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(knwwb__paiy,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, qhlqf__xmajp)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            qhlqf__xmajp = bodo.hiframes.pd_series_ext.get_series_name(data)
            fiuo__dzwpt = bodo.libs.distributed_api.bcast_comm_impl(
                qhlqf__xmajp, comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            lspgq__rpba = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lspgq__rpba, fiuo__dzwpt)
        return impl_series
    if isinstance(data, types.BaseTuple):
        affmm__bhjlk = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        affmm__bhjlk += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        eth__ewwt = {}
        exec(affmm__bhjlk, {'bcast_comm_impl': bcast_comm_impl}, eth__ewwt)
        mrvy__emt = eth__ewwt['impl_tuple']
        return mrvy__emt
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    xiotj__abgef = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    khoba__ushis = (0,) * xiotj__abgef

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        knwwb__paiy = np.ascontiguousarray(data)
        zrfea__qnao = data.ctypes
        uorwx__eqa = khoba__ushis
        if rank == root:
            uorwx__eqa = knwwb__paiy.shape
        uorwx__eqa = bcast_tuple(uorwx__eqa, root)
        dkdq__pwni = get_tuple_prod(uorwx__eqa[1:])
        send_counts = uorwx__eqa[0] * dkdq__pwni
        btsmy__qwnxj = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(zrfea__qnao, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(btsmy__qwnxj.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return btsmy__qwnxj.reshape((-1,) + uorwx__eqa[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        faxh__oyq = MPI.COMM_WORLD
        nfr__wzmo = MPI.Get_processor_name()
        agl__xjetw = faxh__oyq.allgather(nfr__wzmo)
        node_ranks = defaultdict(list)
        for i, lbp__hzf in enumerate(agl__xjetw):
            node_ranks[lbp__hzf].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    faxh__oyq = MPI.COMM_WORLD
    mpa__zsuf = faxh__oyq.Get_group()
    pddwt__qjn = mpa__zsuf.Incl(comm_ranks)
    ypjc__cpm = faxh__oyq.Create_group(pddwt__qjn)
    return ypjc__cpm


def get_nodes_first_ranks():
    dgdu__xgldh = get_host_ranks()
    return np.array([btvhj__dmg[0] for btvhj__dmg in dgdu__xgldh.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
