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
    amtp__cwah = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, amtp__cwah, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    amtp__cwah = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, amtp__cwah, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            amtp__cwah = get_type_enum(arr)
            return _isend(arr.ctypes, size, amtp__cwah, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        amtp__cwah = np.int32(numba_to_c_type(arr.dtype))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            fwj__zkfei = size + 7 >> 3
            phrrx__qwuoi = _isend(arr._data.ctypes, size, amtp__cwah, pe,
                tag, cond)
            etbsz__wru = _isend(arr._null_bitmap.ctypes, fwj__zkfei,
                bnk__gbkad, pe, tag, cond)
            return phrrx__qwuoi, etbsz__wru
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        mmfr__iga = np.int32(numba_to_c_type(offset_type))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            vpd__yslvi = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(vpd__yslvi, pe, tag - 1)
            fwj__zkfei = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                mmfr__iga, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), vpd__yslvi,
                bnk__gbkad, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr),
                fwj__zkfei, bnk__gbkad, pe, tag)
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
            amtp__cwah = get_type_enum(arr)
            return _irecv(arr.ctypes, size, amtp__cwah, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        amtp__cwah = np.int32(numba_to_c_type(arr.dtype))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            fwj__zkfei = size + 7 >> 3
            phrrx__qwuoi = _irecv(arr._data.ctypes, size, amtp__cwah, pe,
                tag, cond)
            etbsz__wru = _irecv(arr._null_bitmap.ctypes, fwj__zkfei,
                bnk__gbkad, pe, tag, cond)
            return phrrx__qwuoi, etbsz__wru
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        mmfr__iga = np.int32(numba_to_c_type(offset_type))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            biwtp__bxzoz = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            biwtp__bxzoz = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        xeqwc__unz = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {biwtp__bxzoz}(size, n_chars)
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
        wla__xuiw = dict()
        exec(xeqwc__unz, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            mmfr__iga, 'char_typ_enum': bnk__gbkad}, wla__xuiw)
        impl = wla__xuiw['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    amtp__cwah = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), amtp__cwah)


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
        ekgdl__rzqkj = n_pes if rank == root or allgather else 0
        qyc__plyuk = np.empty(ekgdl__rzqkj, dtype)
        c_gather_scalar(send.ctypes, qyc__plyuk.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return qyc__plyuk
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
        ligi__auf = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], ligi__auf)
        return builder.bitcast(ligi__auf, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        ligi__auf = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(ligi__auf)
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
    xlzg__gevsm = types.unliteral(value)
    if isinstance(xlzg__gevsm, IndexValueType):
        xlzg__gevsm = xlzg__gevsm.val_typ
        rntml__cgj = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            rntml__cgj.append(types.int64)
            rntml__cgj.append(bodo.datetime64ns)
            rntml__cgj.append(bodo.timedelta64ns)
            rntml__cgj.append(bodo.datetime_date_type)
        if xlzg__gevsm not in rntml__cgj:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(xlzg__gevsm))
    typ_enum = np.int32(numba_to_c_type(xlzg__gevsm))

    def impl(value, reduce_op):
        lga__nypl = value_to_ptr(value)
        rify__ydst = value_to_ptr(value)
        _dist_reduce(lga__nypl, rify__ydst, reduce_op, typ_enum)
        return load_val_ptr(rify__ydst, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    xlzg__gevsm = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(xlzg__gevsm))
    taa__ond = xlzg__gevsm(0)

    def impl(value, reduce_op):
        lga__nypl = value_to_ptr(value)
        rify__ydst = value_to_ptr(taa__ond)
        _dist_exscan(lga__nypl, rify__ydst, reduce_op, typ_enum)
        return load_val_ptr(rify__ydst, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    pwf__mqgf = 0
    ycj__ztwq = 0
    for i in range(len(recv_counts)):
        zsqu__wrrw = recv_counts[i]
        fwj__zkfei = recv_counts_nulls[i]
        ulgdj__tqpt = tmp_null_bytes[pwf__mqgf:pwf__mqgf + fwj__zkfei]
        for ctmd__cnsh in range(zsqu__wrrw):
            set_bit_to(null_bitmap_ptr, ycj__ztwq, get_bit(ulgdj__tqpt,
                ctmd__cnsh))
            ycj__ztwq += 1
        pwf__mqgf += fwj__zkfei


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            gvz__espf = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                gvz__espf, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            zkgy__ihfuu = data.size
            recv_counts = gather_scalar(np.int32(zkgy__ihfuu), allgather,
                root=root)
            svltd__wvx = recv_counts.sum()
            gxlp__zpvuu = empty_like_type(svltd__wvx, data)
            uei__kigrk = np.empty(1, np.int32)
            if rank == root or allgather:
                uei__kigrk = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(zkgy__ihfuu), gxlp__zpvuu.
                ctypes, recv_counts.ctypes, uei__kigrk.ctypes, np.int32(
                typ_val), allgather, np.int32(root))
            return gxlp__zpvuu.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            gxlp__zpvuu = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.str_arr_ext.init_str_arr(gxlp__zpvuu)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            gxlp__zpvuu = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(gxlp__zpvuu)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            zkgy__ihfuu = len(data)
            fwj__zkfei = zkgy__ihfuu + 7 >> 3
            recv_counts = gather_scalar(np.int32(zkgy__ihfuu), allgather,
                root=root)
            svltd__wvx = recv_counts.sum()
            gxlp__zpvuu = empty_like_type(svltd__wvx, data)
            uei__kigrk = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            fkxu__cqw = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                uei__kigrk = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                fkxu__cqw = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(zkgy__ihfuu),
                gxlp__zpvuu._days_data.ctypes, recv_counts.ctypes,
                uei__kigrk.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._seconds_data.ctypes, np.int32(zkgy__ihfuu),
                gxlp__zpvuu._seconds_data.ctypes, recv_counts.ctypes,
                uei__kigrk.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._microseconds_data.ctypes, np.int32(zkgy__ihfuu),
                gxlp__zpvuu._microseconds_data.ctypes, recv_counts.ctypes,
                uei__kigrk.ctypes, np.int32(typ_val), allgather, np.int32(root)
                )
            c_gatherv(data._null_bitmap.ctypes, np.int32(fwj__zkfei),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, fkxu__cqw.
                ctypes, bnk__gbkad, allgather, np.int32(root))
            copy_gathered_null_bytes(gxlp__zpvuu._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return gxlp__zpvuu
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            zkgy__ihfuu = len(data)
            fwj__zkfei = zkgy__ihfuu + 7 >> 3
            recv_counts = gather_scalar(np.int32(zkgy__ihfuu), allgather,
                root=root)
            svltd__wvx = recv_counts.sum()
            gxlp__zpvuu = empty_like_type(svltd__wvx, data)
            uei__kigrk = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            fkxu__cqw = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                uei__kigrk = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                fkxu__cqw = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(zkgy__ihfuu), gxlp__zpvuu
                ._data.ctypes, recv_counts.ctypes, uei__kigrk.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(fwj__zkfei),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, fkxu__cqw.
                ctypes, bnk__gbkad, allgather, np.int32(root))
            copy_gathered_null_bytes(gxlp__zpvuu._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return gxlp__zpvuu
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        yax__rgprq = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            zpg__yspn = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                zpg__yspn, yax__rgprq)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            ngyd__nlto = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            dlu__mnaox = bodo.gatherv(data._right, allgather, warn_if_rep, root
                )
            return bodo.libs.interval_arr_ext.init_interval_array(ngyd__nlto,
                dlu__mnaox)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ehtv__pgiip = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            lghd__xek = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lghd__xek, ehtv__pgiip)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        evia__veff = np.iinfo(np.int64).max
        sol__pmihx = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            fdtp__hkixi = data._start
            kxlpz__htk = data._stop
            if len(data) == 0:
                fdtp__hkixi = evia__veff
                kxlpz__htk = sol__pmihx
            fdtp__hkixi = bodo.libs.distributed_api.dist_reduce(fdtp__hkixi,
                np.int32(Reduce_Type.Min.value))
            kxlpz__htk = bodo.libs.distributed_api.dist_reduce(kxlpz__htk,
                np.int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if fdtp__hkixi == evia__veff and kxlpz__htk == sol__pmihx:
                fdtp__hkixi = 0
                kxlpz__htk = 0
            bycsv__bfl = max(0, -(-(kxlpz__htk - fdtp__hkixi) // data._step))
            if bycsv__bfl < total_len:
                kxlpz__htk = fdtp__hkixi + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                fdtp__hkixi = 0
                kxlpz__htk = 0
            return bodo.hiframes.pd_index_ext.init_range_index(fdtp__hkixi,
                kxlpz__htk, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            eyugl__amnda = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, eyugl__amnda)
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
            gxlp__zpvuu = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                gxlp__zpvuu, data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        qgq__lju = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        xeqwc__unz = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        xeqwc__unz += '  T = data\n'
        xeqwc__unz += '  T2 = init_table(T, True)\n'
        for fekw__pdki in data.type_to_blk.values():
            qgq__lju[f'arr_inds_{fekw__pdki}'] = np.array(data.
                block_to_arr_ind[fekw__pdki], dtype=np.int64)
            xeqwc__unz += (
                f'  arr_list_{fekw__pdki} = get_table_block(T, {fekw__pdki})\n'
                )
            xeqwc__unz += f"""  out_arr_list_{fekw__pdki} = alloc_list_like(arr_list_{fekw__pdki}, len(arr_list_{fekw__pdki}), True)
"""
            xeqwc__unz += f'  for i in range(len(arr_list_{fekw__pdki})):\n'
            xeqwc__unz += (
                f'    arr_ind_{fekw__pdki} = arr_inds_{fekw__pdki}[i]\n')
            xeqwc__unz += f"""    ensure_column_unboxed(T, arr_list_{fekw__pdki}, i, arr_ind_{fekw__pdki})
"""
            xeqwc__unz += f"""    out_arr_{fekw__pdki} = bodo.gatherv(arr_list_{fekw__pdki}[i], allgather, warn_if_rep, root)
"""
            xeqwc__unz += (
                f'    out_arr_list_{fekw__pdki}[i] = out_arr_{fekw__pdki}\n')
            xeqwc__unz += (
                f'  T2 = set_table_block(T2, out_arr_list_{fekw__pdki}, {fekw__pdki})\n'
                )
        xeqwc__unz += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        xeqwc__unz += f'  T2 = set_table_len(T2, length)\n'
        xeqwc__unz += f'  return T2\n'
        wla__xuiw = {}
        exec(xeqwc__unz, qgq__lju, wla__xuiw)
        ivhvu__cpoxx = wla__xuiw['impl_table']
        return ivhvu__cpoxx
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ihgse__hhcn = len(data.columns)
        if ihgse__hhcn == 0:
            moifk__fdv = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                zlk__hiarq = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    zlk__hiarq, moifk__fdv)
            return impl
        pqf__dckql = ', '.join(f'g_data_{i}' for i in range(ihgse__hhcn))
        xeqwc__unz = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            ihqq__ywefv = bodo.hiframes.pd_dataframe_ext.DataFrameType(data
                .data, data.index, data.columns, Distribution.REP, True)
            pqf__dckql = 'T2'
            xeqwc__unz += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            xeqwc__unz += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(ihgse__hhcn):
                xeqwc__unz += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                xeqwc__unz += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        xeqwc__unz += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        xeqwc__unz += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        xeqwc__unz += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(pqf__dckql))
        wla__xuiw = {}
        qgq__lju = {'bodo': bodo, '__col_name_meta_value_gatherv_with_cols':
            ColNamesMetaType(data.columns)}
        exec(xeqwc__unz, qgq__lju, wla__xuiw)
        xjqyv__rrxlo = wla__xuiw['impl_df']
        return xjqyv__rrxlo
    if isinstance(data, ArrayItemArrayType):
        rdl__krywp = np.int32(numba_to_c_type(types.int32))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            qxmz__ywws = bodo.libs.array_item_arr_ext.get_offsets(data)
            rtkjy__qtm = bodo.libs.array_item_arr_ext.get_data(data)
            rtkjy__qtm = rtkjy__qtm[:qxmz__ywws[-1]]
            skmr__miz = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            zkgy__ihfuu = len(data)
            lvkb__gfi = np.empty(zkgy__ihfuu, np.uint32)
            fwj__zkfei = zkgy__ihfuu + 7 >> 3
            for i in range(zkgy__ihfuu):
                lvkb__gfi[i] = qxmz__ywws[i + 1] - qxmz__ywws[i]
            recv_counts = gather_scalar(np.int32(zkgy__ihfuu), allgather,
                root=root)
            svltd__wvx = recv_counts.sum()
            uei__kigrk = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            fkxu__cqw = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                uei__kigrk = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for gcr__vnbi in range(len(recv_counts)):
                    recv_counts_nulls[gcr__vnbi] = recv_counts[gcr__vnbi
                        ] + 7 >> 3
                fkxu__cqw = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            cikvv__brbzz = np.empty(svltd__wvx + 1, np.uint32)
            vzhim__efh = bodo.gatherv(rtkjy__qtm, allgather, warn_if_rep, root)
            itdy__dlkos = np.empty(svltd__wvx + 7 >> 3, np.uint8)
            c_gatherv(lvkb__gfi.ctypes, np.int32(zkgy__ihfuu), cikvv__brbzz
                .ctypes, recv_counts.ctypes, uei__kigrk.ctypes, rdl__krywp,
                allgather, np.int32(root))
            c_gatherv(skmr__miz.ctypes, np.int32(fwj__zkfei),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, fkxu__cqw.
                ctypes, bnk__gbkad, allgather, np.int32(root))
            dummy_use(data)
            bum__kdoxa = np.empty(svltd__wvx + 1, np.uint64)
            convert_len_arr_to_offset(cikvv__brbzz.ctypes, bum__kdoxa.
                ctypes, svltd__wvx)
            copy_gathered_null_bytes(itdy__dlkos.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                svltd__wvx, vzhim__efh, bum__kdoxa, itdy__dlkos)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        bub__netiw = data.names
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            vdpp__bsvpq = bodo.libs.struct_arr_ext.get_data(data)
            amau__stno = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            rnqto__gon = bodo.gatherv(vdpp__bsvpq, allgather=allgather,
                root=root)
            rank = bodo.libs.distributed_api.get_rank()
            zkgy__ihfuu = len(data)
            fwj__zkfei = zkgy__ihfuu + 7 >> 3
            recv_counts = gather_scalar(np.int32(zkgy__ihfuu), allgather,
                root=root)
            svltd__wvx = recv_counts.sum()
            hcvbd__iuqqe = np.empty(svltd__wvx + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            fkxu__cqw = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                fkxu__cqw = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(amau__stno.ctypes, np.int32(fwj__zkfei),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, fkxu__cqw.
                ctypes, bnk__gbkad, allgather, np.int32(root))
            copy_gathered_null_bytes(hcvbd__iuqqe.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(rnqto__gon,
                hcvbd__iuqqe, bub__netiw)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            gxlp__zpvuu = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.binary_arr_ext.init_binary_arr(gxlp__zpvuu)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            gxlp__zpvuu = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.tuple_arr_ext.init_tuple_arr(gxlp__zpvuu)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            gxlp__zpvuu = bodo.gatherv(data._data, allgather, warn_if_rep, root
                )
            return bodo.libs.map_arr_ext.init_map_arr(gxlp__zpvuu)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            gxlp__zpvuu = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            ups__vyyla = bodo.gatherv(data.indices, allgather, warn_if_rep,
                root)
            bnbf__grz = bodo.gatherv(data.indptr, allgather, warn_if_rep, root)
            dlxdb__ijq = gather_scalar(data.shape[0], allgather, root=root)
            tba__edoqj = dlxdb__ijq.sum()
            ihgse__hhcn = bodo.libs.distributed_api.dist_reduce(data.shape[
                1], np.int32(Reduce_Type.Max.value))
            lwl__cxda = np.empty(tba__edoqj + 1, np.int64)
            ups__vyyla = ups__vyyla.astype(np.int64)
            lwl__cxda[0] = 0
            jvp__fgqnw = 1
            gjf__merp = 0
            for cckzo__lxgi in dlxdb__ijq:
                for hbp__pbv in range(cckzo__lxgi):
                    qjnm__itbss = bnbf__grz[gjf__merp + 1] - bnbf__grz[
                        gjf__merp]
                    lwl__cxda[jvp__fgqnw] = lwl__cxda[jvp__fgqnw - 1
                        ] + qjnm__itbss
                    jvp__fgqnw += 1
                    gjf__merp += 1
                gjf__merp += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(gxlp__zpvuu,
                ups__vyyla, lwl__cxda, (tba__edoqj, ihgse__hhcn))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        xeqwc__unz = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        xeqwc__unz += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        wla__xuiw = {}
        exec(xeqwc__unz, {'bodo': bodo}, wla__xuiw)
        bcpby__dnrhj = wla__xuiw['impl_tuple']
        return bcpby__dnrhj
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    xeqwc__unz = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    xeqwc__unz += '    if random:\n'
    xeqwc__unz += '        if random_seed is None:\n'
    xeqwc__unz += '            random = 1\n'
    xeqwc__unz += '        else:\n'
    xeqwc__unz += '            random = 2\n'
    xeqwc__unz += '    if random_seed is None:\n'
    xeqwc__unz += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        vdfx__tqyhg = data
        ihgse__hhcn = len(vdfx__tqyhg.columns)
        for i in range(ihgse__hhcn):
            xeqwc__unz += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        xeqwc__unz += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        pqf__dckql = ', '.join(f'data_{i}' for i in range(ihgse__hhcn))
        xeqwc__unz += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(zhs__gbnx) for
            zhs__gbnx in range(ihgse__hhcn))))
        xeqwc__unz += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        xeqwc__unz += '    if dests is None:\n'
        xeqwc__unz += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        xeqwc__unz += '    else:\n'
        xeqwc__unz += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for itzqc__ynkla in range(ihgse__hhcn):
            xeqwc__unz += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(itzqc__ynkla))
        xeqwc__unz += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(ihgse__hhcn))
        xeqwc__unz += '    delete_table(out_table)\n'
        xeqwc__unz += '    if parallel:\n'
        xeqwc__unz += '        delete_table(table_total)\n'
        pqf__dckql = ', '.join('out_arr_{}'.format(i) for i in range(
            ihgse__hhcn))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        xeqwc__unz += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(pqf__dckql, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        xeqwc__unz += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        xeqwc__unz += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        xeqwc__unz += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        xeqwc__unz += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        xeqwc__unz += '    if dests is None:\n'
        xeqwc__unz += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        xeqwc__unz += '    else:\n'
        xeqwc__unz += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        xeqwc__unz += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        xeqwc__unz += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        xeqwc__unz += '    delete_table(out_table)\n'
        xeqwc__unz += '    if parallel:\n'
        xeqwc__unz += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        xeqwc__unz += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        xeqwc__unz += '    if not parallel:\n'
        xeqwc__unz += '        return data\n'
        xeqwc__unz += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        xeqwc__unz += '    if dests is None:\n'
        xeqwc__unz += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        xeqwc__unz += '    elif bodo.get_rank() not in dests:\n'
        xeqwc__unz += '        dim0_local_size = 0\n'
        xeqwc__unz += '    else:\n'
        xeqwc__unz += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        xeqwc__unz += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        xeqwc__unz += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        xeqwc__unz += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        xeqwc__unz += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        xeqwc__unz += '    if dests is None:\n'
        xeqwc__unz += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        xeqwc__unz += '    else:\n'
        xeqwc__unz += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        xeqwc__unz += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        xeqwc__unz += '    delete_table(out_table)\n'
        xeqwc__unz += '    if parallel:\n'
        xeqwc__unz += '        delete_table(table_total)\n'
        xeqwc__unz += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    wla__xuiw = {}
    qgq__lju = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qgq__lju.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(vdfx__tqyhg.columns)})
    exec(xeqwc__unz, qgq__lju, wla__xuiw)
    impl = wla__xuiw['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    xeqwc__unz = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        xeqwc__unz += '    if seed is None:\n'
        xeqwc__unz += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        xeqwc__unz += '    np.random.seed(seed)\n'
        xeqwc__unz += '    if not parallel:\n'
        xeqwc__unz += '        data = data.copy()\n'
        xeqwc__unz += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            xeqwc__unz += '        data = data[:n_samples]\n'
        xeqwc__unz += '        return data\n'
        xeqwc__unz += '    else:\n'
        xeqwc__unz += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        xeqwc__unz += '        permutation = np.arange(dim0_global_size)\n'
        xeqwc__unz += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            xeqwc__unz += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            xeqwc__unz += '        n_samples = dim0_global_size\n'
        xeqwc__unz += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        xeqwc__unz += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        xeqwc__unz += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        xeqwc__unz += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        xeqwc__unz += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        xeqwc__unz += '        return output\n'
    else:
        xeqwc__unz += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            xeqwc__unz += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            xeqwc__unz += '    output = output[:local_n_samples]\n'
        xeqwc__unz += '    return output\n'
    wla__xuiw = {}
    exec(xeqwc__unz, {'np': np, 'bodo': bodo}, wla__xuiw)
    impl = wla__xuiw['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    wsfk__sgsx = np.empty(sendcounts_nulls.sum(), np.uint8)
    pwf__mqgf = 0
    ycj__ztwq = 0
    for lan__egunk in range(len(sendcounts)):
        zsqu__wrrw = sendcounts[lan__egunk]
        fwj__zkfei = sendcounts_nulls[lan__egunk]
        ulgdj__tqpt = wsfk__sgsx[pwf__mqgf:pwf__mqgf + fwj__zkfei]
        for ctmd__cnsh in range(zsqu__wrrw):
            set_bit_to_arr(ulgdj__tqpt, ctmd__cnsh, get_bit_bitmap(
                null_bitmap_ptr, ycj__ztwq))
            ycj__ztwq += 1
        pwf__mqgf += fwj__zkfei
    return wsfk__sgsx


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    kls__ftyb = MPI.COMM_WORLD
    data = kls__ftyb.bcast(data, root)
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
    kppzi__wmm = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    owede__hou = (0,) * kppzi__wmm

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        sjh__wflvt = np.ascontiguousarray(data)
        hma__zpvi = data.ctypes
        llptr__cmb = owede__hou
        if rank == MPI_ROOT:
            llptr__cmb = sjh__wflvt.shape
        llptr__cmb = bcast_tuple(llptr__cmb)
        ijyng__lrax = get_tuple_prod(llptr__cmb[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            llptr__cmb[0])
        send_counts *= ijyng__lrax
        zkgy__ihfuu = send_counts[rank]
        brr__bwo = np.empty(zkgy__ihfuu, dtype)
        uei__kigrk = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(hma__zpvi, send_counts.ctypes, uei__kigrk.ctypes,
            brr__bwo.ctypes, np.int32(zkgy__ihfuu), np.int32(typ_val))
        return brr__bwo.reshape((-1,) + llptr__cmb[1:])
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
        sfnb__jjg = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], sfnb__jjg)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        ehtv__pgiip = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=ehtv__pgiip)
        xtq__dfqg = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(xtq__dfqg)
        return pd.Index(arr, name=ehtv__pgiip)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        ehtv__pgiip = _get_name_value_for_type(dtype.name_typ)
        bub__netiw = tuple(_get_name_value_for_type(t) for t in dtype.names_typ
            )
        qvkhe__mvpzp = tuple(get_value_for_type(t) for t in dtype.array_types)
        qvkhe__mvpzp = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in qvkhe__mvpzp)
        val = pd.MultiIndex.from_arrays(qvkhe__mvpzp, names=bub__netiw)
        val.name = ehtv__pgiip
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        ehtv__pgiip = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=ehtv__pgiip)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        qvkhe__mvpzp = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({ehtv__pgiip: arr for ehtv__pgiip, arr in zip(
            dtype.columns, qvkhe__mvpzp)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        xtq__dfqg = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(xtq__dfqg[0], xtq__dfqg
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
        rdl__krywp = np.int32(numba_to_c_type(types.int32))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            biwtp__bxzoz = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            biwtp__bxzoz = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        xeqwc__unz = f"""def impl(
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
            recv_arr = {biwtp__bxzoz}(n_loc, n_loc_char)

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
        wla__xuiw = dict()
        exec(xeqwc__unz, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            rdl__krywp, 'char_typ_enum': bnk__gbkad, 'decode_if_dict_array':
            decode_if_dict_array}, wla__xuiw)
        impl = wla__xuiw['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        rdl__krywp = np.int32(numba_to_c_type(types.int32))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            cvnhz__pqcfk = bodo.libs.array_item_arr_ext.get_offsets(data)
            puavo__lipno = bodo.libs.array_item_arr_ext.get_data(data)
            puavo__lipno = puavo__lipno[:cvnhz__pqcfk[-1]]
            rwezs__btukk = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            fgzfp__uurj = bcast_scalar(len(data))
            wvv__mojwt = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                wvv__mojwt[i] = cvnhz__pqcfk[i + 1] - cvnhz__pqcfk[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                fgzfp__uurj)
            uei__kigrk = bodo.ir.join.calc_disp(send_counts)
            mce__wnw = np.empty(n_pes, np.int32)
            if rank == 0:
                cpsui__qma = 0
                for i in range(n_pes):
                    gqf__yed = 0
                    for hbp__pbv in range(send_counts[i]):
                        gqf__yed += wvv__mojwt[cpsui__qma]
                        cpsui__qma += 1
                    mce__wnw[i] = gqf__yed
            bcast(mce__wnw)
            gvc__cell = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                gvc__cell[i] = send_counts[i] + 7 >> 3
            fkxu__cqw = bodo.ir.join.calc_disp(gvc__cell)
            zkgy__ihfuu = send_counts[rank]
            ewhj__yverj = np.empty(zkgy__ihfuu + 1, np_offset_type)
            pmfh__iwupu = bodo.libs.distributed_api.scatterv_impl(puavo__lipno,
                mce__wnw)
            ooalq__kux = zkgy__ihfuu + 7 >> 3
            nisv__ntpha = np.empty(ooalq__kux, np.uint8)
            csjjb__pxp = np.empty(zkgy__ihfuu, np.uint32)
            c_scatterv(wvv__mojwt.ctypes, send_counts.ctypes, uei__kigrk.
                ctypes, csjjb__pxp.ctypes, np.int32(zkgy__ihfuu), rdl__krywp)
            convert_len_arr_to_offset(csjjb__pxp.ctypes, ewhj__yverj.ctypes,
                zkgy__ihfuu)
            esp__mgqpi = get_scatter_null_bytes_buff(rwezs__btukk.ctypes,
                send_counts, gvc__cell)
            c_scatterv(esp__mgqpi.ctypes, gvc__cell.ctypes, fkxu__cqw.
                ctypes, nisv__ntpha.ctypes, np.int32(ooalq__kux), bnk__gbkad)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                zkgy__ihfuu, pmfh__iwupu, ewhj__yverj, nisv__ntpha)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            cmnv__ekjc = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            cmnv__ekjc = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            cmnv__ekjc = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            cmnv__ekjc = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            sjh__wflvt = data._data
            amau__stno = data._null_bitmap
            okd__hnt = len(sjh__wflvt)
            xmyf__iwd = _scatterv_np(sjh__wflvt, send_counts)
            fgzfp__uurj = bcast_scalar(okd__hnt)
            ktwkt__zhe = len(xmyf__iwd) + 7 >> 3
            sln__vgq = np.empty(ktwkt__zhe, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                fgzfp__uurj)
            gvc__cell = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                gvc__cell[i] = send_counts[i] + 7 >> 3
            fkxu__cqw = bodo.ir.join.calc_disp(gvc__cell)
            esp__mgqpi = get_scatter_null_bytes_buff(amau__stno.ctypes,
                send_counts, gvc__cell)
            c_scatterv(esp__mgqpi.ctypes, gvc__cell.ctypes, fkxu__cqw.
                ctypes, sln__vgq.ctypes, np.int32(ktwkt__zhe), bnk__gbkad)
            return cmnv__ekjc(xmyf__iwd, sln__vgq)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            bzepy__tfdwv = bodo.libs.distributed_api.scatterv_impl(data.
                _left, send_counts)
            qdd__mohec = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(bzepy__tfdwv,
                qdd__mohec)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            fdtp__hkixi = data._start
            kxlpz__htk = data._stop
            ugcr__iwna = data._step
            ehtv__pgiip = data._name
            ehtv__pgiip = bcast_scalar(ehtv__pgiip)
            fdtp__hkixi = bcast_scalar(fdtp__hkixi)
            kxlpz__htk = bcast_scalar(kxlpz__htk)
            ugcr__iwna = bcast_scalar(ugcr__iwna)
            wjxgx__rggmi = bodo.libs.array_kernels.calc_nitems(fdtp__hkixi,
                kxlpz__htk, ugcr__iwna)
            chunk_start = bodo.libs.distributed_api.get_start(wjxgx__rggmi,
                n_pes, rank)
            gqzj__vzs = bodo.libs.distributed_api.get_node_portion(wjxgx__rggmi
                , n_pes, rank)
            zgkp__kcm = fdtp__hkixi + ugcr__iwna * chunk_start
            rckh__mcavv = fdtp__hkixi + ugcr__iwna * (chunk_start + gqzj__vzs)
            rckh__mcavv = min(rckh__mcavv, kxlpz__htk)
            return bodo.hiframes.pd_index_ext.init_range_index(zgkp__kcm,
                rckh__mcavv, ugcr__iwna, ehtv__pgiip)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        eyugl__amnda = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            sjh__wflvt = data._data
            ehtv__pgiip = data._name
            ehtv__pgiip = bcast_scalar(ehtv__pgiip)
            arr = bodo.libs.distributed_api.scatterv_impl(sjh__wflvt,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                ehtv__pgiip, eyugl__amnda)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            sjh__wflvt = data._data
            ehtv__pgiip = data._name
            ehtv__pgiip = bcast_scalar(ehtv__pgiip)
            arr = bodo.libs.distributed_api.scatterv_impl(sjh__wflvt,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, ehtv__pgiip)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            gxlp__zpvuu = bodo.libs.distributed_api.scatterv_impl(data.
                _data, send_counts)
            ehtv__pgiip = bcast_scalar(data._name)
            bub__netiw = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(
                gxlp__zpvuu, bub__netiw, ehtv__pgiip)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ehtv__pgiip = bodo.hiframes.pd_series_ext.get_series_name(data)
            miwqe__spzyh = bcast_scalar(ehtv__pgiip)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            lghd__xek = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lghd__xek, miwqe__spzyh)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ihgse__hhcn = len(data.columns)
        pqf__dckql = ', '.join('g_data_{}'.format(i) for i in range(
            ihgse__hhcn))
        fwo__fgo = ColNamesMetaType(data.columns)
        xeqwc__unz = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(ihgse__hhcn):
            xeqwc__unz += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            xeqwc__unz += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        xeqwc__unz += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        xeqwc__unz += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        xeqwc__unz += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({pqf__dckql},), g_index, __col_name_meta_scaterv_impl)
"""
        wla__xuiw = {}
        exec(xeqwc__unz, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            fwo__fgo}, wla__xuiw)
        xjqyv__rrxlo = wla__xuiw['impl_df']
        return xjqyv__rrxlo
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            gvz__espf = bodo.libs.distributed_api.scatterv_impl(data.codes,
                send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                gvz__espf, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        xeqwc__unz = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        xeqwc__unz += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        wla__xuiw = {}
        exec(xeqwc__unz, {'bodo': bodo}, wla__xuiw)
        bcpby__dnrhj = wla__xuiw['impl_tuple']
        return bcpby__dnrhj
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
        mmfr__iga = np.int32(numba_to_c_type(offset_type))
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            zkgy__ihfuu = len(data)
            pznvy__sulrm = num_total_chars(data)
            assert zkgy__ihfuu < INT_MAX
            assert pznvy__sulrm < INT_MAX
            fhhpl__eey = get_offset_ptr(data)
            hma__zpvi = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            fwj__zkfei = zkgy__ihfuu + 7 >> 3
            c_bcast(fhhpl__eey, np.int32(zkgy__ihfuu + 1), mmfr__iga, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(hma__zpvi, np.int32(pznvy__sulrm), bnk__gbkad, np.array
                ([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(fwj__zkfei), bnk__gbkad, np.
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
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                xzaw__ofgbk = 0
                ybzb__zucd = np.empty(0, np.uint8).ctypes
            else:
                ybzb__zucd, xzaw__ofgbk = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            xzaw__ofgbk = bodo.libs.distributed_api.bcast_scalar(xzaw__ofgbk,
                root)
            if rank != root:
                aiqzl__qytwx = np.empty(xzaw__ofgbk + 1, np.uint8)
                aiqzl__qytwx[xzaw__ofgbk] = 0
                ybzb__zucd = aiqzl__qytwx.ctypes
            c_bcast(ybzb__zucd, np.int32(xzaw__ofgbk), bnk__gbkad, np.array
                ([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(ybzb__zucd, xzaw__ofgbk)
        return impl_str
    typ_val = numba_to_c_type(val)
    xeqwc__unz = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    wla__xuiw = {}
    exec(xeqwc__unz, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, wla__xuiw)
    pkm__hnqfo = wla__xuiw['bcast_scalar_impl']
    return pkm__hnqfo


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    bhjvx__dhq = len(val)
    xeqwc__unz = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    xeqwc__unz += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(bhjvx__dhq)),
        ',' if bhjvx__dhq else '')
    wla__xuiw = {}
    exec(xeqwc__unz, {'bcast_scalar': bcast_scalar}, wla__xuiw)
    krw__egvey = wla__xuiw['bcast_tuple_impl']
    return krw__egvey


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            zkgy__ihfuu = bcast_scalar(len(arr), root)
            cttoh__hamfe = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(zkgy__ihfuu, cttoh__hamfe)
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
            zgkp__kcm = max(arr_start, slice_index.start) - arr_start
            rckh__mcavv = max(slice_index.stop - arr_start, 0)
            return slice(zgkp__kcm, rckh__mcavv)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            fdtp__hkixi = slice_index.start
            ugcr__iwna = slice_index.step
            miy__qgs = (0 if ugcr__iwna == 1 or fdtp__hkixi > arr_start else
                abs(ugcr__iwna - arr_start % ugcr__iwna) % ugcr__iwna)
            zgkp__kcm = max(arr_start, slice_index.start
                ) - arr_start + miy__qgs
            rckh__mcavv = max(slice_index.stop - arr_start, 0)
            return slice(zgkp__kcm, rckh__mcavv, ugcr__iwna)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        zgdms__mgzq = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[zgdms__mgzq])
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
        vdjd__rehx = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        bnk__gbkad = np.int32(numba_to_c_type(types.uint8))
        nzkx__azbn = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            ixe__vdhb = np.int32(10)
            tag = np.int32(11)
            jatek__mxxtf = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                rtkjy__qtm = arr._data
                jncvj__yky = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    rtkjy__qtm, ind)
                moxf__wpuv = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    rtkjy__qtm, ind + 1)
                length = moxf__wpuv - jncvj__yky
                ligi__auf = rtkjy__qtm[ind]
                jatek__mxxtf[0] = length
                isend(jatek__mxxtf, np.int32(1), root, ixe__vdhb, True)
                isend(ligi__auf, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(nzkx__azbn
                , vdjd__rehx, 0, 1)
            bycsv__bfl = 0
            if rank == root:
                bycsv__bfl = recv(np.int64, ANY_SOURCE, ixe__vdhb)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    nzkx__azbn, vdjd__rehx, bycsv__bfl, 1)
                hma__zpvi = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(hma__zpvi, np.int32(bycsv__bfl), bnk__gbkad,
                    ANY_SOURCE, tag)
            dummy_use(jatek__mxxtf)
            bycsv__bfl = bcast_scalar(bycsv__bfl)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    nzkx__azbn, vdjd__rehx, bycsv__bfl, 1)
            hma__zpvi = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(hma__zpvi, np.int32(bycsv__bfl), bnk__gbkad, np.array([
                -1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, bycsv__bfl)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        terpn__ohbk = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, terpn__ohbk)
            if arr_start <= ind < arr_start + len(arr):
                gvz__espf = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = gvz__espf[ind - arr_start]
                send_arr = np.full(1, data, terpn__ohbk)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = terpn__ohbk(-1)
            if rank == root:
                val = recv(terpn__ohbk, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            rgl__pagh = arr.dtype.categories[max(val, 0)]
            return rgl__pagh
        return cat_getitem_impl
    fkbt__axcg = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, fkbt__axcg)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, fkbt__axcg)[0]
        if rank == root:
            val = recv(fkbt__axcg, ANY_SOURCE, tag)
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
    uozoy__cwapi = get_type_enum(out_data)
    assert typ_enum == uozoy__cwapi
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
    xeqwc__unz = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        xeqwc__unz += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    xeqwc__unz += '  return\n'
    wla__xuiw = {}
    exec(xeqwc__unz, {'alltoallv': alltoallv}, wla__xuiw)
    cbcm__igvhc = wla__xuiw['f']
    return cbcm__igvhc


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    fdtp__hkixi = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return fdtp__hkixi, count


@numba.njit
def get_start(total_size, pes, rank):
    qyc__plyuk = total_size % pes
    atmi__wtav = (total_size - qyc__plyuk) // pes
    return rank * atmi__wtav + min(rank, qyc__plyuk)


@numba.njit
def get_end(total_size, pes, rank):
    qyc__plyuk = total_size % pes
    atmi__wtav = (total_size - qyc__plyuk) // pes
    return (rank + 1) * atmi__wtav + min(rank + 1, qyc__plyuk)


@numba.njit
def get_node_portion(total_size, pes, rank):
    qyc__plyuk = total_size % pes
    atmi__wtav = (total_size - qyc__plyuk) // pes
    if rank < qyc__plyuk:
        return atmi__wtav + 1
    else:
        return atmi__wtav


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    taa__ond = in_arr.dtype(0)
    ugv__izn = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        gqf__yed = taa__ond
        for gjs__iiou in np.nditer(in_arr):
            gqf__yed += gjs__iiou.item()
        xvpqn__jyycg = dist_exscan(gqf__yed, ugv__izn)
        for i in range(in_arr.size):
            xvpqn__jyycg += in_arr[i]
            out_arr[i] = xvpqn__jyycg
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    ilp__gknyn = in_arr.dtype(1)
    ugv__izn = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        gqf__yed = ilp__gknyn
        for gjs__iiou in np.nditer(in_arr):
            gqf__yed *= gjs__iiou.item()
        xvpqn__jyycg = dist_exscan(gqf__yed, ugv__izn)
        if get_rank() == 0:
            xvpqn__jyycg = ilp__gknyn
        for i in range(in_arr.size):
            xvpqn__jyycg *= in_arr[i]
            out_arr[i] = xvpqn__jyycg
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        ilp__gknyn = np.finfo(in_arr.dtype(1).dtype).max
    else:
        ilp__gknyn = np.iinfo(in_arr.dtype(1).dtype).max
    ugv__izn = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        gqf__yed = ilp__gknyn
        for gjs__iiou in np.nditer(in_arr):
            gqf__yed = min(gqf__yed, gjs__iiou.item())
        xvpqn__jyycg = dist_exscan(gqf__yed, ugv__izn)
        if get_rank() == 0:
            xvpqn__jyycg = ilp__gknyn
        for i in range(in_arr.size):
            xvpqn__jyycg = min(xvpqn__jyycg, in_arr[i])
            out_arr[i] = xvpqn__jyycg
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        ilp__gknyn = np.finfo(in_arr.dtype(1).dtype).min
    else:
        ilp__gknyn = np.iinfo(in_arr.dtype(1).dtype).min
    ilp__gknyn = in_arr.dtype(1)
    ugv__izn = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        gqf__yed = ilp__gknyn
        for gjs__iiou in np.nditer(in_arr):
            gqf__yed = max(gqf__yed, gjs__iiou.item())
        xvpqn__jyycg = dist_exscan(gqf__yed, ugv__izn)
        if get_rank() == 0:
            xvpqn__jyycg = ilp__gknyn
        for i in range(in_arr.size):
            xvpqn__jyycg = max(xvpqn__jyycg, in_arr[i])
            out_arr[i] = xvpqn__jyycg
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    amtp__cwah = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), amtp__cwah)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    cchm__xra = args[0]
    if equiv_set.has_shape(cchm__xra):
        return ArrayAnalysis.AnalyzeResult(shape=cchm__xra, pre=[])
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
    jthe__huol = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for 
        i, hgv__gmmy in enumerate(args) if is_array_typ(hgv__gmmy) or
        isinstance(hgv__gmmy, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    xeqwc__unz = f"""def impl(*args):
    if {jthe__huol} or bodo.get_rank() == 0:
        print(*args)"""
    wla__xuiw = {}
    exec(xeqwc__unz, globals(), wla__xuiw)
    impl = wla__xuiw['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        wbfz__rur = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        xeqwc__unz = 'def f(req, cond=True):\n'
        xeqwc__unz += f'  return {wbfz__rur}\n'
        wla__xuiw = {}
        exec(xeqwc__unz, {'_wait': _wait}, wla__xuiw)
        impl = wla__xuiw['f']
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
        qyc__plyuk = 1
        for a in t:
            qyc__plyuk *= a
        return qyc__plyuk
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    dzxqv__ifrb = np.ascontiguousarray(in_arr)
    nrq__zawz = get_tuple_prod(dzxqv__ifrb.shape[1:])
    oukqv__ebap = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        jxw__yjcbz = np.array(dest_ranks, dtype=np.int32)
    else:
        jxw__yjcbz = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, dzxqv__ifrb.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * oukqv__ebap, 
        dtype_size * nrq__zawz, len(jxw__yjcbz), jxw__yjcbz.ctypes)
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
    ofol__mudj = np.ascontiguousarray(rhs)
    hhbwo__simf = get_tuple_prod(ofol__mudj.shape[1:])
    kbu__epzt = dtype_size * hhbwo__simf
    permutation_array_index(lhs.ctypes, lhs_len, kbu__epzt, ofol__mudj.
        ctypes, ofol__mudj.shape[0], p.ctypes, p_len, n_samples)
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
        xeqwc__unz = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        wla__xuiw = {}
        exec(xeqwc__unz, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, wla__xuiw)
        pkm__hnqfo = wla__xuiw['bcast_scalar_impl']
        return pkm__hnqfo
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        ihgse__hhcn = len(data.columns)
        pqf__dckql = ', '.join('g_data_{}'.format(i) for i in range(
            ihgse__hhcn))
        xfya__oldtz = ColNamesMetaType(data.columns)
        xeqwc__unz = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(ihgse__hhcn):
            xeqwc__unz += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            xeqwc__unz += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        xeqwc__unz += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        xeqwc__unz += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        xeqwc__unz += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(pqf__dckql))
        wla__xuiw = {}
        exec(xeqwc__unz, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            xfya__oldtz}, wla__xuiw)
        xjqyv__rrxlo = wla__xuiw['impl_df']
        return xjqyv__rrxlo
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            fdtp__hkixi = data._start
            kxlpz__htk = data._stop
            ugcr__iwna = data._step
            ehtv__pgiip = data._name
            ehtv__pgiip = bcast_scalar(ehtv__pgiip, root)
            fdtp__hkixi = bcast_scalar(fdtp__hkixi, root)
            kxlpz__htk = bcast_scalar(kxlpz__htk, root)
            ugcr__iwna = bcast_scalar(ugcr__iwna, root)
            wjxgx__rggmi = bodo.libs.array_kernels.calc_nitems(fdtp__hkixi,
                kxlpz__htk, ugcr__iwna)
            chunk_start = bodo.libs.distributed_api.get_start(wjxgx__rggmi,
                n_pes, rank)
            gqzj__vzs = bodo.libs.distributed_api.get_node_portion(wjxgx__rggmi
                , n_pes, rank)
            zgkp__kcm = fdtp__hkixi + ugcr__iwna * chunk_start
            rckh__mcavv = fdtp__hkixi + ugcr__iwna * (chunk_start + gqzj__vzs)
            rckh__mcavv = min(rckh__mcavv, kxlpz__htk)
            return bodo.hiframes.pd_index_ext.init_range_index(zgkp__kcm,
                rckh__mcavv, ugcr__iwna, ehtv__pgiip)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            sjh__wflvt = data._data
            ehtv__pgiip = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(sjh__wflvt,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, ehtv__pgiip)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            ehtv__pgiip = bodo.hiframes.pd_series_ext.get_series_name(data)
            miwqe__spzyh = bodo.libs.distributed_api.bcast_comm_impl(
                ehtv__pgiip, comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            lghd__xek = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                lghd__xek, miwqe__spzyh)
        return impl_series
    if isinstance(data, types.BaseTuple):
        xeqwc__unz = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        xeqwc__unz += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        wla__xuiw = {}
        exec(xeqwc__unz, {'bcast_comm_impl': bcast_comm_impl}, wla__xuiw)
        bcpby__dnrhj = wla__xuiw['impl_tuple']
        return bcpby__dnrhj
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    kppzi__wmm = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    owede__hou = (0,) * kppzi__wmm

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        sjh__wflvt = np.ascontiguousarray(data)
        hma__zpvi = data.ctypes
        llptr__cmb = owede__hou
        if rank == root:
            llptr__cmb = sjh__wflvt.shape
        llptr__cmb = bcast_tuple(llptr__cmb, root)
        ijyng__lrax = get_tuple_prod(llptr__cmb[1:])
        send_counts = llptr__cmb[0] * ijyng__lrax
        brr__bwo = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(hma__zpvi, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(brr__bwo.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return brr__bwo.reshape((-1,) + llptr__cmb[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        kls__ftyb = MPI.COMM_WORLD
        plrr__jajn = MPI.Get_processor_name()
        ive__qtig = kls__ftyb.allgather(plrr__jajn)
        node_ranks = defaultdict(list)
        for i, umot__zegu in enumerate(ive__qtig):
            node_ranks[umot__zegu].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    kls__ftyb = MPI.COMM_WORLD
    bat__lkdsg = kls__ftyb.Get_group()
    nnzcc__bbod = bat__lkdsg.Incl(comm_ranks)
    euow__bqht = kls__ftyb.Create_group(nnzcc__bbod)
    return euow__bqht


def get_nodes_first_ranks():
    ooek__qztmw = get_host_ranks()
    return np.array([ltgvd__amorc[0] for ltgvd__amorc in ooek__qztmw.values
        ()], dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
