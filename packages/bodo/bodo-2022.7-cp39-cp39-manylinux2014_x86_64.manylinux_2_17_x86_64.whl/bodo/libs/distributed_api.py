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
    jpb__oxui = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, jpb__oxui, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    jpb__oxui = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, jpb__oxui, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            jpb__oxui = get_type_enum(arr)
            return _isend(arr.ctypes, size, jpb__oxui, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        jpb__oxui = np.int32(numba_to_c_type(arr.dtype))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            cmv__iplox = size + 7 >> 3
            flrfb__kwsh = _isend(arr._data.ctypes, size, jpb__oxui, pe, tag,
                cond)
            gvhlw__tzh = _isend(arr._null_bitmap.ctypes, cmv__iplox,
                qwd__ildz, pe, tag, cond)
            return flrfb__kwsh, gvhlw__tzh
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        ccu__hot = np.int32(numba_to_c_type(offset_type))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            pdsaq__ypw = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(pdsaq__ypw, pe, tag - 1)
            cmv__iplox = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                ccu__hot, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), pdsaq__ypw,
                qwd__ildz, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                cmv__iplox, qwd__ildz, pe, tag)
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
            jpb__oxui = get_type_enum(arr)
            return _irecv(arr.ctypes, size, jpb__oxui, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        jpb__oxui = np.int32(numba_to_c_type(arr.dtype))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            cmv__iplox = size + 7 >> 3
            flrfb__kwsh = _irecv(arr._data.ctypes, size, jpb__oxui, pe, tag,
                cond)
            gvhlw__tzh = _irecv(arr._null_bitmap.ctypes, cmv__iplox,
                qwd__ildz, pe, tag, cond)
            return flrfb__kwsh, gvhlw__tzh
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        ccu__hot = np.int32(numba_to_c_type(offset_type))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            rojqr__etnmj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rojqr__etnmj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        kxiq__ogtnv = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {rojqr__etnmj}(size, n_chars)
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
        fvf__tsxf = dict()
        exec(kxiq__ogtnv, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            ccu__hot, 'char_typ_enum': qwd__ildz}, fvf__tsxf)
        impl = fvf__tsxf['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    jpb__oxui = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), jpb__oxui)


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
        ovtb__ova = n_pes if rank == root or allgather else 0
        qvhem__tdsgs = np.empty(ovtb__ova, dtype)
        c_gather_scalar(send.ctypes, qvhem__tdsgs.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return qvhem__tdsgs
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
        ruu__vnpad = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], ruu__vnpad)
        return builder.bitcast(ruu__vnpad, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        ruu__vnpad = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(ruu__vnpad)
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
    wyr__ard = types.unliteral(value)
    if isinstance(wyr__ard, IndexValueType):
        wyr__ard = wyr__ard.val_typ
        fdiri__yxpt = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            fdiri__yxpt.append(types.int64)
            fdiri__yxpt.append(bodo.datetime64ns)
            fdiri__yxpt.append(bodo.timedelta64ns)
            fdiri__yxpt.append(bodo.datetime_date_type)
        if wyr__ard not in fdiri__yxpt:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(wyr__ard))
    typ_enum = np.int32(numba_to_c_type(wyr__ard))

    def impl(value, reduce_op):
        axcjw__bby = value_to_ptr(value)
        tdfes__hhqh = value_to_ptr(value)
        _dist_reduce(axcjw__bby, tdfes__hhqh, reduce_op, typ_enum)
        return load_val_ptr(tdfes__hhqh, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    wyr__ard = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(wyr__ard))
    pgk__iexy = wyr__ard(0)

    def impl(value, reduce_op):
        axcjw__bby = value_to_ptr(value)
        tdfes__hhqh = value_to_ptr(pgk__iexy)
        _dist_exscan(axcjw__bby, tdfes__hhqh, reduce_op, typ_enum)
        return load_val_ptr(tdfes__hhqh, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    csneb__tei = 0
    vdz__zyh = 0
    for i in range(len(recv_counts)):
        jkx__xfuw = recv_counts[i]
        cmv__iplox = recv_counts_nulls[i]
        qhlw__fuydm = tmp_null_bytes[csneb__tei:csneb__tei + cmv__iplox]
        for moqkn__dlccy in range(jkx__xfuw):
            set_bit_to(null_bitmap_ptr, vdz__zyh, get_bit(qhlw__fuydm,
                moqkn__dlccy))
            vdz__zyh += 1
        csneb__tei += cmv__iplox


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            cidof__rmb = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                cidof__rmb, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            nmsef__aia = data.size
            recv_counts = gather_scalar(np.int32(nmsef__aia), allgather,
                root=root)
            lnel__akuoa = recv_counts.sum()
            nqiv__mgpz = empty_like_type(lnel__akuoa, data)
            lsex__bbzc = np.empty(1, np.int32)
            if rank == root or allgather:
                lsex__bbzc = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(nmsef__aia), nqiv__mgpz.ctypes,
                recv_counts.ctypes, lsex__bbzc.ctypes, np.int32(typ_val),
                allgather, np.int32(root))
            return nqiv__mgpz.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            nqiv__mgpz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(nqiv__mgpz)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            nqiv__mgpz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(nqiv__mgpz)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nmsef__aia = len(data)
            cmv__iplox = nmsef__aia + 7 >> 3
            recv_counts = gather_scalar(np.int32(nmsef__aia), allgather,
                root=root)
            lnel__akuoa = recv_counts.sum()
            nqiv__mgpz = empty_like_type(lnel__akuoa, data)
            lsex__bbzc = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            vagkp__ici = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                lsex__bbzc = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                vagkp__ici = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(nmsef__aia),
                nqiv__mgpz._days_data.ctypes, recv_counts.ctypes,
                lsex__bbzc.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(nmsef__aia),
                nqiv__mgpz._seconds_data.ctypes, recv_counts.ctypes,
                lsex__bbzc.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(nmsef__aia),
                nqiv__mgpz._microseconds_data.ctypes, recv_counts.ctypes,
                lsex__bbzc.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(cmv__iplox),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, vagkp__ici
                .ctypes, qwd__ildz, allgather, np.int32(root))
            copy_gathered_null_bytes(nqiv__mgpz._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return nqiv__mgpz
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nmsef__aia = len(data)
            cmv__iplox = nmsef__aia + 7 >> 3
            recv_counts = gather_scalar(np.int32(nmsef__aia), allgather,
                root=root)
            lnel__akuoa = recv_counts.sum()
            nqiv__mgpz = empty_like_type(lnel__akuoa, data)
            lsex__bbzc = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            vagkp__ici = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                lsex__bbzc = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                vagkp__ici = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(nmsef__aia), nqiv__mgpz.
                _data.ctypes, recv_counts.ctypes, lsex__bbzc.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(cmv__iplox),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, vagkp__ici
                .ctypes, qwd__ildz, allgather, np.int32(root))
            copy_gathered_null_bytes(nqiv__mgpz._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return nqiv__mgpz
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        srube__kkief = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            tfhef__uen = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                tfhef__uen, srube__kkief)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            uurs__gxez = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            get__zmkcd = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(uurs__gxez,
                get__zmkcd)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            vgsz__sxri = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            hmfi__jnpg = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hmfi__jnpg, vgsz__sxri)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        hxzd__wjpzz = np.iinfo(np.int64).max
        tbn__humo = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            tbdjb__vjam = data._start
            ywj__uos = data._stop
            if len(data) == 0:
                tbdjb__vjam = hxzd__wjpzz
                ywj__uos = tbn__humo
            tbdjb__vjam = bodo.libs.distributed_api.dist_reduce(tbdjb__vjam,
                np.int32(Reduce_Type.Min.value))
            ywj__uos = bodo.libs.distributed_api.dist_reduce(ywj__uos, np.
                int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if tbdjb__vjam == hxzd__wjpzz and ywj__uos == tbn__humo:
                tbdjb__vjam = 0
                ywj__uos = 0
            vnse__itrsu = max(0, -(-(ywj__uos - tbdjb__vjam) // data._step))
            if vnse__itrsu < total_len:
                ywj__uos = tbdjb__vjam + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                tbdjb__vjam = 0
                ywj__uos = 0
            return bodo.hiframes.pd_index_ext.init_range_index(tbdjb__vjam,
                ywj__uos, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            xuivf__dtviq = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, xuivf__dtviq)
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
            nqiv__mgpz = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(nqiv__mgpz
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        zkg__ptrb = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        kxiq__ogtnv = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        kxiq__ogtnv += '  T = data\n'
        kxiq__ogtnv += '  T2 = init_table(T, True)\n'
        for hud__yqdcy in data.type_to_blk.values():
            zkg__ptrb[f'arr_inds_{hud__yqdcy}'] = np.array(data.
                block_to_arr_ind[hud__yqdcy], dtype=np.int64)
            kxiq__ogtnv += (
                f'  arr_list_{hud__yqdcy} = get_table_block(T, {hud__yqdcy})\n'
                )
            kxiq__ogtnv += f"""  out_arr_list_{hud__yqdcy} = alloc_list_like(arr_list_{hud__yqdcy}, len(arr_list_{hud__yqdcy}), True)
"""
            kxiq__ogtnv += f'  for i in range(len(arr_list_{hud__yqdcy})):\n'
            kxiq__ogtnv += (
                f'    arr_ind_{hud__yqdcy} = arr_inds_{hud__yqdcy}[i]\n')
            kxiq__ogtnv += f"""    ensure_column_unboxed(T, arr_list_{hud__yqdcy}, i, arr_ind_{hud__yqdcy})
"""
            kxiq__ogtnv += f"""    out_arr_{hud__yqdcy} = bodo.gatherv(arr_list_{hud__yqdcy}[i], allgather, warn_if_rep, root)
"""
            kxiq__ogtnv += (
                f'    out_arr_list_{hud__yqdcy}[i] = out_arr_{hud__yqdcy}\n')
            kxiq__ogtnv += (
                f'  T2 = set_table_block(T2, out_arr_list_{hud__yqdcy}, {hud__yqdcy})\n'
                )
        kxiq__ogtnv += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        kxiq__ogtnv += f'  T2 = set_table_len(T2, length)\n'
        kxiq__ogtnv += f'  return T2\n'
        fvf__tsxf = {}
        exec(kxiq__ogtnv, zkg__ptrb, fvf__tsxf)
        wkgbs__ovmxh = fvf__tsxf['impl_table']
        return wkgbs__ovmxh
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dcej__fofp = len(data.columns)
        if dcej__fofp == 0:
            gsl__aur = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                nkxga__aedn = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    nkxga__aedn, gsl__aur)
            return impl
        rnp__ddl = ', '.join(f'g_data_{i}' for i in range(dcej__fofp))
        kxiq__ogtnv = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            aat__opked = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            rnp__ddl = 'T2'
            kxiq__ogtnv += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            kxiq__ogtnv += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(dcej__fofp):
                kxiq__ogtnv += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                kxiq__ogtnv += (
                    """  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)
"""
                    .format(i, i))
        kxiq__ogtnv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        kxiq__ogtnv += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        kxiq__ogtnv += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(rnp__ddl))
        fvf__tsxf = {}
        zkg__ptrb = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(kxiq__ogtnv, zkg__ptrb, fvf__tsxf)
        sdnd__ftsf = fvf__tsxf['impl_df']
        return sdnd__ftsf
    if isinstance(data, ArrayItemArrayType):
        nuw__wzqdn = np.int32(numba_to_c_type(types.int32))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            qbzln__nym = bodo.libs.array_item_arr_ext.get_offsets(data)
            lma__oxdw = bodo.libs.array_item_arr_ext.get_data(data)
            lma__oxdw = lma__oxdw[:qbzln__nym[-1]]
            unt__pdvj = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            nmsef__aia = len(data)
            tcvs__flish = np.empty(nmsef__aia, np.uint32)
            cmv__iplox = nmsef__aia + 7 >> 3
            for i in range(nmsef__aia):
                tcvs__flish[i] = qbzln__nym[i + 1] - qbzln__nym[i]
            recv_counts = gather_scalar(np.int32(nmsef__aia), allgather,
                root=root)
            lnel__akuoa = recv_counts.sum()
            lsex__bbzc = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            vagkp__ici = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                lsex__bbzc = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for xjafq__taild in range(len(recv_counts)):
                    recv_counts_nulls[xjafq__taild] = recv_counts[xjafq__taild
                        ] + 7 >> 3
                vagkp__ici = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            qrqie__lyoo = np.empty(lnel__akuoa + 1, np.uint32)
            aoxbr__lvjhe = bodo.gatherv(lma__oxdw, allgather, warn_if_rep, root
                )
            mpbhc__bgf = np.empty(lnel__akuoa + 7 >> 3, np.uint8)
            c_gatherv(tcvs__flish.ctypes, np.int32(nmsef__aia), qrqie__lyoo
                .ctypes, recv_counts.ctypes, lsex__bbzc.ctypes, nuw__wzqdn,
                allgather, np.int32(root))
            c_gatherv(unt__pdvj.ctypes, np.int32(cmv__iplox),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, vagkp__ici
                .ctypes, qwd__ildz, allgather, np.int32(root))
            dummy_use(data)
            tva__mvi = np.empty(lnel__akuoa + 1, np.uint64)
            convert_len_arr_to_offset(qrqie__lyoo.ctypes, tva__mvi.ctypes,
                lnel__akuoa)
            copy_gathered_null_bytes(mpbhc__bgf.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                lnel__akuoa, aoxbr__lvjhe, tva__mvi, mpbhc__bgf)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        vnxbh__hwnsc = data.names
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            bcgt__ckeyk = bodo.libs.struct_arr_ext.get_data(data)
            rgj__mdsis = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            dzv__telem = bodo.gatherv(bcgt__ckeyk, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            nmsef__aia = len(data)
            cmv__iplox = nmsef__aia + 7 >> 3
            recv_counts = gather_scalar(np.int32(nmsef__aia), allgather,
                root=root)
            lnel__akuoa = recv_counts.sum()
            qqle__vpvtp = np.empty(lnel__akuoa + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            vagkp__ici = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                vagkp__ici = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(rgj__mdsis.ctypes, np.int32(cmv__iplox),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, vagkp__ici
                .ctypes, qwd__ildz, allgather, np.int32(root))
            copy_gathered_null_bytes(qqle__vpvtp.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(dzv__telem,
                qqle__vpvtp, vnxbh__hwnsc)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            nqiv__mgpz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(nqiv__mgpz)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            nqiv__mgpz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(nqiv__mgpz)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            nqiv__mgpz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(nqiv__mgpz)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            nqiv__mgpz = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            jpwc__zzonu = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            ybmju__ovc = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            ketxf__ytli = gather_scalar(data.shape[0], allgather, root=root)
            usei__tkgn = ketxf__ytli.sum()
            dcej__fofp = bodo.libs.distributed_api.dist_reduce(data.shape[1
                ], np.int32(Reduce_Type.Max.value))
            tgk__intk = np.empty(usei__tkgn + 1, np.int64)
            jpwc__zzonu = jpwc__zzonu.astype(np.int64)
            tgk__intk[0] = 0
            detg__vcuws = 1
            uodtw__bya = 0
            for uqpkb__mko in ketxf__ytli:
                for wigc__lunkk in range(uqpkb__mko):
                    xbv__nkei = ybmju__ovc[uodtw__bya + 1] - ybmju__ovc[
                        uodtw__bya]
                    tgk__intk[detg__vcuws] = tgk__intk[detg__vcuws - 1
                        ] + xbv__nkei
                    detg__vcuws += 1
                    uodtw__bya += 1
                uodtw__bya += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(nqiv__mgpz,
                jpwc__zzonu, tgk__intk, (usei__tkgn, dcej__fofp))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        kxiq__ogtnv = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        kxiq__ogtnv += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'bodo': bodo}, fvf__tsxf)
        ugzy__hxu = fvf__tsxf['impl_tuple']
        return ugzy__hxu
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    kxiq__ogtnv = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    kxiq__ogtnv += '    if random:\n'
    kxiq__ogtnv += '        if random_seed is None:\n'
    kxiq__ogtnv += '            random = 1\n'
    kxiq__ogtnv += '        else:\n'
    kxiq__ogtnv += '            random = 2\n'
    kxiq__ogtnv += '    if random_seed is None:\n'
    kxiq__ogtnv += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        eywm__irg = data
        dcej__fofp = len(eywm__irg.columns)
        for i in range(dcej__fofp):
            kxiq__ogtnv += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        kxiq__ogtnv += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        rnp__ddl = ', '.join(f'data_{i}' for i in range(dcej__fofp))
        kxiq__ogtnv += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(vinn__yqpcv) for
            vinn__yqpcv in range(dcej__fofp))))
        kxiq__ogtnv += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        kxiq__ogtnv += '    if dests is None:\n'
        kxiq__ogtnv += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        kxiq__ogtnv += '    else:\n'
        kxiq__ogtnv += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for ycmv__xnsd in range(dcej__fofp):
            kxiq__ogtnv += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(ycmv__xnsd))
        kxiq__ogtnv += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(dcej__fofp))
        kxiq__ogtnv += '    delete_table(out_table)\n'
        kxiq__ogtnv += '    if parallel:\n'
        kxiq__ogtnv += '        delete_table(table_total)\n'
        rnp__ddl = ', '.join('out_arr_{}'.format(i) for i in range(dcej__fofp))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        kxiq__ogtnv += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(rnp__ddl, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        kxiq__ogtnv += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        kxiq__ogtnv += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        kxiq__ogtnv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        kxiq__ogtnv += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        kxiq__ogtnv += '    if dests is None:\n'
        kxiq__ogtnv += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        kxiq__ogtnv += '    else:\n'
        kxiq__ogtnv += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        kxiq__ogtnv += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        kxiq__ogtnv += """    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)
"""
        kxiq__ogtnv += '    delete_table(out_table)\n'
        kxiq__ogtnv += '    if parallel:\n'
        kxiq__ogtnv += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        kxiq__ogtnv += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        kxiq__ogtnv += '    if not parallel:\n'
        kxiq__ogtnv += '        return data\n'
        kxiq__ogtnv += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        kxiq__ogtnv += '    if dests is None:\n'
        kxiq__ogtnv += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        kxiq__ogtnv += '    elif bodo.get_rank() not in dests:\n'
        kxiq__ogtnv += '        dim0_local_size = 0\n'
        kxiq__ogtnv += '    else:\n'
        kxiq__ogtnv += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        kxiq__ogtnv += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        kxiq__ogtnv += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        kxiq__ogtnv += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        kxiq__ogtnv += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        kxiq__ogtnv += '    if dests is None:\n'
        kxiq__ogtnv += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        kxiq__ogtnv += '    else:\n'
        kxiq__ogtnv += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        kxiq__ogtnv += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        kxiq__ogtnv += '    delete_table(out_table)\n'
        kxiq__ogtnv += '    if parallel:\n'
        kxiq__ogtnv += '        delete_table(table_total)\n'
        kxiq__ogtnv += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    fvf__tsxf = {}
    zkg__ptrb = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        zkg__ptrb.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(eywm__irg.columns)})
    exec(kxiq__ogtnv, zkg__ptrb, fvf__tsxf)
    impl = fvf__tsxf['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    kxiq__ogtnv = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        kxiq__ogtnv += '    if seed is None:\n'
        kxiq__ogtnv += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        kxiq__ogtnv += '    np.random.seed(seed)\n'
        kxiq__ogtnv += '    if not parallel:\n'
        kxiq__ogtnv += '        data = data.copy()\n'
        kxiq__ogtnv += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            kxiq__ogtnv += '        data = data[:n_samples]\n'
        kxiq__ogtnv += '        return data\n'
        kxiq__ogtnv += '    else:\n'
        kxiq__ogtnv += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        kxiq__ogtnv += '        permutation = np.arange(dim0_global_size)\n'
        kxiq__ogtnv += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            kxiq__ogtnv += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            kxiq__ogtnv += '        n_samples = dim0_global_size\n'
        kxiq__ogtnv += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        kxiq__ogtnv += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        kxiq__ogtnv += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        kxiq__ogtnv += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        kxiq__ogtnv += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        kxiq__ogtnv += '        return output\n'
    else:
        kxiq__ogtnv += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            kxiq__ogtnv += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            kxiq__ogtnv += '    output = output[:local_n_samples]\n'
        kxiq__ogtnv += '    return output\n'
    fvf__tsxf = {}
    exec(kxiq__ogtnv, {'np': np, 'bodo': bodo}, fvf__tsxf)
    impl = fvf__tsxf['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    tgnk__dxk = np.empty(sendcounts_nulls.sum(), np.uint8)
    csneb__tei = 0
    vdz__zyh = 0
    for uyd__jzgyx in range(len(sendcounts)):
        jkx__xfuw = sendcounts[uyd__jzgyx]
        cmv__iplox = sendcounts_nulls[uyd__jzgyx]
        qhlw__fuydm = tgnk__dxk[csneb__tei:csneb__tei + cmv__iplox]
        for moqkn__dlccy in range(jkx__xfuw):
            set_bit_to_arr(qhlw__fuydm, moqkn__dlccy, get_bit_bitmap(
                null_bitmap_ptr, vdz__zyh))
            vdz__zyh += 1
        csneb__tei += cmv__iplox
    return tgnk__dxk


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    sno__brbt = MPI.COMM_WORLD
    data = sno__brbt.bcast(data, root)
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
    qfla__pxfq = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    pvymd__ochkf = (0,) * qfla__pxfq

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        kfjkm__ytv = np.ascontiguousarray(data)
        vbc__qqjyf = data.ctypes
        ixy__jeja = pvymd__ochkf
        if rank == MPI_ROOT:
            ixy__jeja = kfjkm__ytv.shape
        ixy__jeja = bcast_tuple(ixy__jeja)
        izxlr__pjj = get_tuple_prod(ixy__jeja[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            ixy__jeja[0])
        send_counts *= izxlr__pjj
        nmsef__aia = send_counts[rank]
        pwqpn__btq = np.empty(nmsef__aia, dtype)
        lsex__bbzc = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(vbc__qqjyf, send_counts.ctypes, lsex__bbzc.ctypes,
            pwqpn__btq.ctypes, np.int32(nmsef__aia), np.int32(typ_val))
        return pwqpn__btq.reshape((-1,) + ixy__jeja[1:])
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
        xumq__cbpn = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], xumq__cbpn)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        vgsz__sxri = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=vgsz__sxri)
        edqs__blam = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(edqs__blam)
        return pd.Index(arr, name=vgsz__sxri)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        vgsz__sxri = _get_name_value_for_type(dtype.name_typ)
        vnxbh__hwnsc = tuple(_get_name_value_for_type(t) for t in dtype.
            names_typ)
        qabd__aduw = tuple(get_value_for_type(t) for t in dtype.array_types)
        qabd__aduw = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in qabd__aduw)
        val = pd.MultiIndex.from_arrays(qabd__aduw, names=vnxbh__hwnsc)
        val.name = vgsz__sxri
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        vgsz__sxri = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=vgsz__sxri)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qabd__aduw = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({vgsz__sxri: arr for vgsz__sxri, arr in zip(
            dtype.columns, qabd__aduw)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        edqs__blam = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(edqs__blam[0],
            edqs__blam[0])])
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
        nuw__wzqdn = np.int32(numba_to_c_type(types.int32))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            rojqr__etnmj = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            rojqr__etnmj = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        kxiq__ogtnv = f"""def impl(
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
            recv_arr = {rojqr__etnmj}(n_loc, n_loc_char)

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
        fvf__tsxf = dict()
        exec(kxiq__ogtnv, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            nuw__wzqdn, 'char_typ_enum': qwd__ildz, 'decode_if_dict_array':
            decode_if_dict_array}, fvf__tsxf)
        impl = fvf__tsxf['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        nuw__wzqdn = np.int32(numba_to_c_type(types.int32))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            dhhj__tjtlb = bodo.libs.array_item_arr_ext.get_offsets(data)
            olnv__mgit = bodo.libs.array_item_arr_ext.get_data(data)
            olnv__mgit = olnv__mgit[:dhhj__tjtlb[-1]]
            rvk__ttwh = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            lcva__vfs = bcast_scalar(len(data))
            izf__pemr = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                izf__pemr[i] = dhhj__tjtlb[i + 1] - dhhj__tjtlb[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                lcva__vfs)
            lsex__bbzc = bodo.ir.join.calc_disp(send_counts)
            coc__mkga = np.empty(n_pes, np.int32)
            if rank == 0:
                wof__zyj = 0
                for i in range(n_pes):
                    iia__fqtg = 0
                    for wigc__lunkk in range(send_counts[i]):
                        iia__fqtg += izf__pemr[wof__zyj]
                        wof__zyj += 1
                    coc__mkga[i] = iia__fqtg
            bcast(coc__mkga)
            feby__herf = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                feby__herf[i] = send_counts[i] + 7 >> 3
            vagkp__ici = bodo.ir.join.calc_disp(feby__herf)
            nmsef__aia = send_counts[rank]
            dywv__lah = np.empty(nmsef__aia + 1, np_offset_type)
            kznyh__ezwv = bodo.libs.distributed_api.scatterv_impl(olnv__mgit,
                coc__mkga)
            yxxj__uodq = nmsef__aia + 7 >> 3
            raen__xjfa = np.empty(yxxj__uodq, np.uint8)
            jmizc__kha = np.empty(nmsef__aia, np.uint32)
            c_scatterv(izf__pemr.ctypes, send_counts.ctypes, lsex__bbzc.
                ctypes, jmizc__kha.ctypes, np.int32(nmsef__aia), nuw__wzqdn)
            convert_len_arr_to_offset(jmizc__kha.ctypes, dywv__lah.ctypes,
                nmsef__aia)
            hvq__fgc = get_scatter_null_bytes_buff(rvk__ttwh.ctypes,
                send_counts, feby__herf)
            c_scatterv(hvq__fgc.ctypes, feby__herf.ctypes, vagkp__ici.
                ctypes, raen__xjfa.ctypes, np.int32(yxxj__uodq), qwd__ildz)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                nmsef__aia, kznyh__ezwv, dywv__lah, raen__xjfa)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            fgtvg__fnu = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            fgtvg__fnu = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            fgtvg__fnu = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            fgtvg__fnu = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            kfjkm__ytv = data._data
            rgj__mdsis = data._null_bitmap
            zbrdn__qiiw = len(kfjkm__ytv)
            mwm__ggiye = _scatterv_np(kfjkm__ytv, send_counts)
            lcva__vfs = bcast_scalar(zbrdn__qiiw)
            vuj__wxdgp = len(mwm__ggiye) + 7 >> 3
            mznrb__biqux = np.empty(vuj__wxdgp, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                lcva__vfs)
            feby__herf = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                feby__herf[i] = send_counts[i] + 7 >> 3
            vagkp__ici = bodo.ir.join.calc_disp(feby__herf)
            hvq__fgc = get_scatter_null_bytes_buff(rgj__mdsis.ctypes,
                send_counts, feby__herf)
            c_scatterv(hvq__fgc.ctypes, feby__herf.ctypes, vagkp__ici.
                ctypes, mznrb__biqux.ctypes, np.int32(vuj__wxdgp), qwd__ildz)
            return fgtvg__fnu(mwm__ggiye, mznrb__biqux)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            bry__amxrt = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            hclus__dbq = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(bry__amxrt,
                hclus__dbq)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            tbdjb__vjam = data._start
            ywj__uos = data._stop
            jfv__rxx = data._step
            vgsz__sxri = data._name
            vgsz__sxri = bcast_scalar(vgsz__sxri)
            tbdjb__vjam = bcast_scalar(tbdjb__vjam)
            ywj__uos = bcast_scalar(ywj__uos)
            jfv__rxx = bcast_scalar(jfv__rxx)
            eemdb__dzjh = bodo.libs.array_kernels.calc_nitems(tbdjb__vjam,
                ywj__uos, jfv__rxx)
            chunk_start = bodo.libs.distributed_api.get_start(eemdb__dzjh,
                n_pes, rank)
            kaq__xum = bodo.libs.distributed_api.get_node_portion(eemdb__dzjh,
                n_pes, rank)
            yfjih__qhmr = tbdjb__vjam + jfv__rxx * chunk_start
            khfhl__njmcb = tbdjb__vjam + jfv__rxx * (chunk_start + kaq__xum)
            khfhl__njmcb = min(khfhl__njmcb, ywj__uos)
            return bodo.hiframes.pd_index_ext.init_range_index(yfjih__qhmr,
                khfhl__njmcb, jfv__rxx, vgsz__sxri)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        xuivf__dtviq = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            kfjkm__ytv = data._data
            vgsz__sxri = data._name
            vgsz__sxri = bcast_scalar(vgsz__sxri)
            arr = bodo.libs.distributed_api.scatterv_impl(kfjkm__ytv,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                vgsz__sxri, xuivf__dtviq)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            kfjkm__ytv = data._data
            vgsz__sxri = data._name
            vgsz__sxri = bcast_scalar(vgsz__sxri)
            arr = bodo.libs.distributed_api.scatterv_impl(kfjkm__ytv,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, vgsz__sxri)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            nqiv__mgpz = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            vgsz__sxri = bcast_scalar(data._name)
            vnxbh__hwnsc = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(nqiv__mgpz
                , vnxbh__hwnsc, vgsz__sxri)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            vgsz__sxri = bodo.hiframes.pd_series_ext.get_series_name(data)
            itvxd__nquj = bcast_scalar(vgsz__sxri)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            hmfi__jnpg = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hmfi__jnpg, itvxd__nquj)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dcej__fofp = len(data.columns)
        rnp__ddl = ', '.join('g_data_{}'.format(i) for i in range(dcej__fofp))
        atu__zcij = ColNamesMetaType(data.columns)
        kxiq__ogtnv = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(dcej__fofp):
            kxiq__ogtnv += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            kxiq__ogtnv += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        kxiq__ogtnv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        kxiq__ogtnv += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        kxiq__ogtnv += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({rnp__ddl},), g_index, __col_name_meta_scaterv_impl)
"""
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            atu__zcij}, fvf__tsxf)
        sdnd__ftsf = fvf__tsxf['impl_df']
        return sdnd__ftsf
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            cidof__rmb = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                cidof__rmb, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        kxiq__ogtnv = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        kxiq__ogtnv += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'bodo': bodo}, fvf__tsxf)
        ugzy__hxu = fvf__tsxf['impl_tuple']
        return ugzy__hxu
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
        ccu__hot = np.int32(numba_to_c_type(offset_type))
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            nmsef__aia = len(data)
            gpe__aadr = num_total_chars(data)
            assert nmsef__aia < INT_MAX
            assert gpe__aadr < INT_MAX
            cbkta__qge = get_offset_ptr(data)
            vbc__qqjyf = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            cmv__iplox = nmsef__aia + 7 >> 3
            c_bcast(cbkta__qge, np.int32(nmsef__aia + 1), ccu__hot, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(vbc__qqjyf, np.int32(gpe__aadr), qwd__ildz, np.array([-
                1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(cmv__iplox), qwd__ildz, np.
                array([-1]).ctypes, 0, np.int32(root))
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
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                ogis__wwvm = 0
                xxr__lxsc = np.empty(0, np.uint8).ctypes
            else:
                xxr__lxsc, ogis__wwvm = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            ogis__wwvm = bodo.libs.distributed_api.bcast_scalar(ogis__wwvm,
                root)
            if rank != root:
                byx__rgmcp = np.empty(ogis__wwvm + 1, np.uint8)
                byx__rgmcp[ogis__wwvm] = 0
                xxr__lxsc = byx__rgmcp.ctypes
            c_bcast(xxr__lxsc, np.int32(ogis__wwvm), qwd__ildz, np.array([-
                1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(xxr__lxsc, ogis__wwvm)
        return impl_str
    typ_val = numba_to_c_type(val)
    kxiq__ogtnv = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    fvf__tsxf = {}
    exec(kxiq__ogtnv, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, fvf__tsxf)
    lbf__ifs = fvf__tsxf['bcast_scalar_impl']
    return lbf__ifs


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    cslhz__rqyv = len(val)
    kxiq__ogtnv = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    kxiq__ogtnv += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(cslhz__rqyv)
        ), ',' if cslhz__rqyv else '')
    fvf__tsxf = {}
    exec(kxiq__ogtnv, {'bcast_scalar': bcast_scalar}, fvf__tsxf)
    xsb__ssbq = fvf__tsxf['bcast_tuple_impl']
    return xsb__ssbq


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nmsef__aia = bcast_scalar(len(arr), root)
            vidn__ogxgg = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(nmsef__aia, vidn__ogxgg)
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
            yfjih__qhmr = max(arr_start, slice_index.start) - arr_start
            khfhl__njmcb = max(slice_index.stop - arr_start, 0)
            return slice(yfjih__qhmr, khfhl__njmcb)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            tbdjb__vjam = slice_index.start
            jfv__rxx = slice_index.step
            wvj__oeiig = (0 if jfv__rxx == 1 or tbdjb__vjam > arr_start else
                abs(jfv__rxx - arr_start % jfv__rxx) % jfv__rxx)
            yfjih__qhmr = max(arr_start, slice_index.start
                ) - arr_start + wvj__oeiig
            khfhl__njmcb = max(slice_index.stop - arr_start, 0)
            return slice(yfjih__qhmr, khfhl__njmcb, jfv__rxx)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        bxz__qvq = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[bxz__qvq])
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
        vgc__ojwes = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        qwd__ildz = np.int32(numba_to_c_type(types.uint8))
        mxbbl__favow = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            apgp__gxut = np.int32(10)
            tag = np.int32(11)
            bfpz__ognh = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                lma__oxdw = arr._data
                uxh__qhywd = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    lma__oxdw, ind)
                pgon__nbij = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    lma__oxdw, ind + 1)
                length = pgon__nbij - uxh__qhywd
                ruu__vnpad = lma__oxdw[ind]
                bfpz__ognh[0] = length
                isend(bfpz__ognh, np.int32(1), root, apgp__gxut, True)
                isend(ruu__vnpad, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                mxbbl__favow, vgc__ojwes, 0, 1)
            vnse__itrsu = 0
            if rank == root:
                vnse__itrsu = recv(np.int64, ANY_SOURCE, apgp__gxut)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    mxbbl__favow, vgc__ojwes, vnse__itrsu, 1)
                vbc__qqjyf = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(vbc__qqjyf, np.int32(vnse__itrsu), qwd__ildz,
                    ANY_SOURCE, tag)
            dummy_use(bfpz__ognh)
            vnse__itrsu = bcast_scalar(vnse__itrsu)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    mxbbl__favow, vgc__ojwes, vnse__itrsu, 1)
            vbc__qqjyf = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(vbc__qqjyf, np.int32(vnse__itrsu), qwd__ildz, np.array(
                [-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, vnse__itrsu)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        wlcb__qmx = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, wlcb__qmx)
            if arr_start <= ind < arr_start + len(arr):
                cidof__rmb = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = cidof__rmb[ind - arr_start]
                send_arr = np.full(1, data, wlcb__qmx)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = wlcb__qmx(-1)
            if rank == root:
                val = recv(wlcb__qmx, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            vupd__gfads = arr.dtype.categories[max(val, 0)]
            return vupd__gfads
        return cat_getitem_impl
    ntk__dzokx = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, ntk__dzokx)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, ntk__dzokx)[0]
        if rank == root:
            val = recv(ntk__dzokx, ANY_SOURCE, tag)
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
    obj__ntfmb = get_type_enum(out_data)
    assert typ_enum == obj__ntfmb
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
    kxiq__ogtnv = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        kxiq__ogtnv += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    kxiq__ogtnv += '  return\n'
    fvf__tsxf = {}
    exec(kxiq__ogtnv, {'alltoallv': alltoallv}, fvf__tsxf)
    ygid__fbl = fvf__tsxf['f']
    return ygid__fbl


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    tbdjb__vjam = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return tbdjb__vjam, count


@numba.njit
def get_start(total_size, pes, rank):
    qvhem__tdsgs = total_size % pes
    ykt__aouda = (total_size - qvhem__tdsgs) // pes
    return rank * ykt__aouda + min(rank, qvhem__tdsgs)


@numba.njit
def get_end(total_size, pes, rank):
    qvhem__tdsgs = total_size % pes
    ykt__aouda = (total_size - qvhem__tdsgs) // pes
    return (rank + 1) * ykt__aouda + min(rank + 1, qvhem__tdsgs)


@numba.njit
def get_node_portion(total_size, pes, rank):
    qvhem__tdsgs = total_size % pes
    ykt__aouda = (total_size - qvhem__tdsgs) // pes
    if rank < qvhem__tdsgs:
        return ykt__aouda + 1
    else:
        return ykt__aouda


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    pgk__iexy = in_arr.dtype(0)
    tbhf__mokub = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        iia__fqtg = pgk__iexy
        for rdw__lgnl in np.nditer(in_arr):
            iia__fqtg += rdw__lgnl.item()
        ahkj__slqg = dist_exscan(iia__fqtg, tbhf__mokub)
        for i in range(in_arr.size):
            ahkj__slqg += in_arr[i]
            out_arr[i] = ahkj__slqg
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    wqdw__xpso = in_arr.dtype(1)
    tbhf__mokub = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        iia__fqtg = wqdw__xpso
        for rdw__lgnl in np.nditer(in_arr):
            iia__fqtg *= rdw__lgnl.item()
        ahkj__slqg = dist_exscan(iia__fqtg, tbhf__mokub)
        if get_rank() == 0:
            ahkj__slqg = wqdw__xpso
        for i in range(in_arr.size):
            ahkj__slqg *= in_arr[i]
            out_arr[i] = ahkj__slqg
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        wqdw__xpso = np.finfo(in_arr.dtype(1).dtype).max
    else:
        wqdw__xpso = np.iinfo(in_arr.dtype(1).dtype).max
    tbhf__mokub = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        iia__fqtg = wqdw__xpso
        for rdw__lgnl in np.nditer(in_arr):
            iia__fqtg = min(iia__fqtg, rdw__lgnl.item())
        ahkj__slqg = dist_exscan(iia__fqtg, tbhf__mokub)
        if get_rank() == 0:
            ahkj__slqg = wqdw__xpso
        for i in range(in_arr.size):
            ahkj__slqg = min(ahkj__slqg, in_arr[i])
            out_arr[i] = ahkj__slqg
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        wqdw__xpso = np.finfo(in_arr.dtype(1).dtype).min
    else:
        wqdw__xpso = np.iinfo(in_arr.dtype(1).dtype).min
    wqdw__xpso = in_arr.dtype(1)
    tbhf__mokub = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        iia__fqtg = wqdw__xpso
        for rdw__lgnl in np.nditer(in_arr):
            iia__fqtg = max(iia__fqtg, rdw__lgnl.item())
        ahkj__slqg = dist_exscan(iia__fqtg, tbhf__mokub)
        if get_rank() == 0:
            ahkj__slqg = wqdw__xpso
        for i in range(in_arr.size):
            ahkj__slqg = max(ahkj__slqg, in_arr[i])
            out_arr[i] = ahkj__slqg
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    jpb__oxui = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), jpb__oxui)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ikbln__kysfj = args[0]
    if equiv_set.has_shape(ikbln__kysfj):
        return ArrayAnalysis.AnalyzeResult(shape=ikbln__kysfj, pre=[])
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
    gof__cfs = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for i,
        uurel__qej in enumerate(args) if is_array_typ(uurel__qej) or
        isinstance(uurel__qej, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    kxiq__ogtnv = f"""def impl(*args):
    if {gof__cfs} or bodo.get_rank() == 0:
        print(*args)"""
    fvf__tsxf = {}
    exec(kxiq__ogtnv, globals(), fvf__tsxf)
    impl = fvf__tsxf['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        gnxf__ysar = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        kxiq__ogtnv = 'def f(req, cond=True):\n'
        kxiq__ogtnv += f'  return {gnxf__ysar}\n'
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'_wait': _wait}, fvf__tsxf)
        impl = fvf__tsxf['f']
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
        qvhem__tdsgs = 1
        for a in t:
            qvhem__tdsgs *= a
        return qvhem__tdsgs
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    jyaal__bptrq = np.ascontiguousarray(in_arr)
    lid__mwpkf = get_tuple_prod(jyaal__bptrq.shape[1:])
    ccl__bzli = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        wygsz__nssi = np.array(dest_ranks, dtype=np.int32)
    else:
        wygsz__nssi = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, jyaal__bptrq.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * ccl__bzli, 
        dtype_size * lid__mwpkf, len(wygsz__nssi), wygsz__nssi.ctypes)
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
    gmzls__tydi = np.ascontiguousarray(rhs)
    fgbpl__gwi = get_tuple_prod(gmzls__tydi.shape[1:])
    azeox__grssn = dtype_size * fgbpl__gwi
    permutation_array_index(lhs.ctypes, lhs_len, azeox__grssn, gmzls__tydi.
        ctypes, gmzls__tydi.shape[0], p.ctypes, p_len, n_samples)
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
        kxiq__ogtnv = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, fvf__tsxf)
        lbf__ifs = fvf__tsxf['bcast_scalar_impl']
        return lbf__ifs
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        dcej__fofp = len(data.columns)
        rnp__ddl = ', '.join('g_data_{}'.format(i) for i in range(dcej__fofp))
        fgrmf__saf = ColNamesMetaType(data.columns)
        kxiq__ogtnv = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(dcej__fofp):
            kxiq__ogtnv += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            kxiq__ogtnv += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        kxiq__ogtnv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        kxiq__ogtnv += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        kxiq__ogtnv += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(rnp__ddl))
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            fgrmf__saf}, fvf__tsxf)
        sdnd__ftsf = fvf__tsxf['impl_df']
        return sdnd__ftsf
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            tbdjb__vjam = data._start
            ywj__uos = data._stop
            jfv__rxx = data._step
            vgsz__sxri = data._name
            vgsz__sxri = bcast_scalar(vgsz__sxri, root)
            tbdjb__vjam = bcast_scalar(tbdjb__vjam, root)
            ywj__uos = bcast_scalar(ywj__uos, root)
            jfv__rxx = bcast_scalar(jfv__rxx, root)
            eemdb__dzjh = bodo.libs.array_kernels.calc_nitems(tbdjb__vjam,
                ywj__uos, jfv__rxx)
            chunk_start = bodo.libs.distributed_api.get_start(eemdb__dzjh,
                n_pes, rank)
            kaq__xum = bodo.libs.distributed_api.get_node_portion(eemdb__dzjh,
                n_pes, rank)
            yfjih__qhmr = tbdjb__vjam + jfv__rxx * chunk_start
            khfhl__njmcb = tbdjb__vjam + jfv__rxx * (chunk_start + kaq__xum)
            khfhl__njmcb = min(khfhl__njmcb, ywj__uos)
            return bodo.hiframes.pd_index_ext.init_range_index(yfjih__qhmr,
                khfhl__njmcb, jfv__rxx, vgsz__sxri)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            kfjkm__ytv = data._data
            vgsz__sxri = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(kfjkm__ytv,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, vgsz__sxri)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            vgsz__sxri = bodo.hiframes.pd_series_ext.get_series_name(data)
            itvxd__nquj = bodo.libs.distributed_api.bcast_comm_impl(vgsz__sxri,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            hmfi__jnpg = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                hmfi__jnpg, itvxd__nquj)
        return impl_series
    if isinstance(data, types.BaseTuple):
        kxiq__ogtnv = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        kxiq__ogtnv += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        fvf__tsxf = {}
        exec(kxiq__ogtnv, {'bcast_comm_impl': bcast_comm_impl}, fvf__tsxf)
        ugzy__hxu = fvf__tsxf['impl_tuple']
        return ugzy__hxu
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    qfla__pxfq = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    pvymd__ochkf = (0,) * qfla__pxfq

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        kfjkm__ytv = np.ascontiguousarray(data)
        vbc__qqjyf = data.ctypes
        ixy__jeja = pvymd__ochkf
        if rank == root:
            ixy__jeja = kfjkm__ytv.shape
        ixy__jeja = bcast_tuple(ixy__jeja, root)
        izxlr__pjj = get_tuple_prod(ixy__jeja[1:])
        send_counts = ixy__jeja[0] * izxlr__pjj
        pwqpn__btq = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(vbc__qqjyf, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(pwqpn__btq.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return pwqpn__btq.reshape((-1,) + ixy__jeja[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        sno__brbt = MPI.COMM_WORLD
        qfub__xoodt = MPI.Get_processor_name()
        jvha__tsget = sno__brbt.allgather(qfub__xoodt)
        node_ranks = defaultdict(list)
        for i, tseh__nughp in enumerate(jvha__tsget):
            node_ranks[tseh__nughp].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    sno__brbt = MPI.COMM_WORLD
    tjcry__gcag = sno__brbt.Get_group()
    ccjr__uwmpq = tjcry__gcag.Incl(comm_ranks)
    uiobr__sod = sno__brbt.Create_group(ccjr__uwmpq)
    return uiobr__sod


def get_nodes_first_ranks():
    bvcw__noh = get_host_ranks()
    return np.array([okw__bvkgp[0] for okw__bvkgp in bvcw__noh.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
