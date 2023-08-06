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
    argim__gdh = get_type_enum(send_arr)
    _send(send_arr.ctypes, 1, argim__gdh, rank, tag)


_recv = types.ExternalFunction('c_recv', types.void(types.voidptr, types.
    int32, types.int32, types.int32, types.int32))


@numba.njit
def recv(dtype, rank, tag):
    recv_arr = np.empty(1, dtype)
    argim__gdh = get_type_enum(recv_arr)
    _recv(recv_arr.ctypes, 1, argim__gdh, rank, tag)
    return recv_arr[0]


_isend = types.ExternalFunction('dist_isend', mpi_req_numba_type(types.
    voidptr, types.int32, types.int32, types.int32, types.int32, types.bool_))


@numba.generated_jit(nopython=True)
def isend(arr, size, pe, tag, cond=True):
    if isinstance(arr, types.Array):

        def impl(arr, size, pe, tag, cond=True):
            argim__gdh = get_type_enum(arr)
            return _isend(arr.ctypes, size, argim__gdh, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        argim__gdh = np.int32(numba_to_c_type(arr.dtype))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            rxzg__cif = size + 7 >> 3
            vpcrh__kunbq = _isend(arr._data.ctypes, size, argim__gdh, pe,
                tag, cond)
            qfb__zdmo = _isend(arr._null_bitmap.ctypes, rxzg__cif,
                fmv__cbrnw, pe, tag, cond)
            return vpcrh__kunbq, qfb__zdmo
        return impl_nullable
    if is_str_arr_type(arr) or arr == binary_array_type:
        vuo__zsra = np.int32(numba_to_c_type(offset_type))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def impl_str_arr(arr, size, pe, tag, cond=True):
            arr = decode_if_dict_array(arr)
            urojk__qryhn = np.int64(bodo.libs.str_arr_ext.num_total_chars(arr))
            send(urojk__qryhn, pe, tag - 1)
            rxzg__cif = size + 7 >> 3
            _send(bodo.libs.str_arr_ext.get_offset_ptr(arr), size + 1,
                vuo__zsra, pe, tag)
            _send(bodo.libs.str_arr_ext.get_data_ptr(arr), urojk__qryhn,
                fmv__cbrnw, pe, tag)
            _send(bodo.libs.str_arr_ext.get_null_bitmap_ptr(arr), rxzg__cif,
                fmv__cbrnw, pe, tag)
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
            argim__gdh = get_type_enum(arr)
            return _irecv(arr.ctypes, size, argim__gdh, pe, tag, cond)
        return impl
    if isinstance(arr, (IntegerArrayType, DecimalArrayType)) or arr in (
        boolean_array, datetime_date_array_type):
        argim__gdh = np.int32(numba_to_c_type(arr.dtype))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def impl_nullable(arr, size, pe, tag, cond=True):
            rxzg__cif = size + 7 >> 3
            vpcrh__kunbq = _irecv(arr._data.ctypes, size, argim__gdh, pe,
                tag, cond)
            qfb__zdmo = _irecv(arr._null_bitmap.ctypes, rxzg__cif,
                fmv__cbrnw, pe, tag, cond)
            return vpcrh__kunbq, qfb__zdmo
        return impl_nullable
    if arr in [binary_array_type, string_array_type]:
        vuo__zsra = np.int32(numba_to_c_type(offset_type))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))
        if arr == binary_array_type:
            owsrj__fctc = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            owsrj__fctc = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        tnli__sosv = f"""def impl(arr, size, pe, tag, cond=True):
            # recv the number of string characters and resize buffer to proper size
            n_chars = bodo.libs.distributed_api.recv(np.int64, pe, tag - 1)
            new_arr = {owsrj__fctc}(size, n_chars)
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
        efp__zomnl = dict()
        exec(tnli__sosv, {'bodo': bodo, 'np': np, 'offset_typ_enum':
            vuo__zsra, 'char_typ_enum': fmv__cbrnw}, efp__zomnl)
        impl = efp__zomnl['impl']
        return impl
    raise BodoError(f'irecv(): array type {arr} not supported yet')


_alltoall = types.ExternalFunction('c_alltoall', types.void(types.voidptr,
    types.voidptr, types.int32, types.int32))


@numba.njit
def alltoall(send_arr, recv_arr, count):
    assert count < INT_MAX
    argim__gdh = get_type_enum(send_arr)
    _alltoall(send_arr.ctypes, recv_arr.ctypes, np.int32(count), argim__gdh)


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
        pys__pndp = n_pes if rank == root or allgather else 0
        ziv__vjn = np.empty(pys__pndp, dtype)
        c_gather_scalar(send.ctypes, ziv__vjn.ctypes, np.int32(typ_val),
            allgather, np.int32(root))
        return ziv__vjn
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
        biqc__pubt = cgutils.alloca_once(builder, args[0].type)
        builder.store(args[0], biqc__pubt)
        return builder.bitcast(biqc__pubt, lir.IntType(8).as_pointer())
    return types.voidptr(val_tp), codegen


@intrinsic
def load_val_ptr(typingctx, ptr_tp, val_tp=None):

    def codegen(context, builder, sig, args):
        biqc__pubt = builder.bitcast(args[0], args[1].type.as_pointer())
        return builder.load(biqc__pubt)
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
    kvdme__pgn = types.unliteral(value)
    if isinstance(kvdme__pgn, IndexValueType):
        kvdme__pgn = kvdme__pgn.val_typ
        cmqxn__bbz = [types.bool_, types.uint8, types.int8, types.uint16,
            types.int16, types.uint32, types.int32, types.float32, types.
            float64]
        if not sys.platform.startswith('win'):
            cmqxn__bbz.append(types.int64)
            cmqxn__bbz.append(bodo.datetime64ns)
            cmqxn__bbz.append(bodo.timedelta64ns)
            cmqxn__bbz.append(bodo.datetime_date_type)
        if kvdme__pgn not in cmqxn__bbz:
            raise BodoError('argmin/argmax not supported for type {}'.
                format(kvdme__pgn))
    typ_enum = np.int32(numba_to_c_type(kvdme__pgn))

    def impl(value, reduce_op):
        wvmc__hkl = value_to_ptr(value)
        qbvr__sqfri = value_to_ptr(value)
        _dist_reduce(wvmc__hkl, qbvr__sqfri, reduce_op, typ_enum)
        return load_val_ptr(qbvr__sqfri, value)
    return impl


_dist_exscan = types.ExternalFunction('dist_exscan', types.void(types.
    voidptr, types.voidptr, types.int32, types.int32))


@numba.generated_jit(nopython=True)
def dist_exscan(value, reduce_op):
    kvdme__pgn = types.unliteral(value)
    typ_enum = np.int32(numba_to_c_type(kvdme__pgn))
    qoi__ezq = kvdme__pgn(0)

    def impl(value, reduce_op):
        wvmc__hkl = value_to_ptr(value)
        qbvr__sqfri = value_to_ptr(qoi__ezq)
        _dist_exscan(wvmc__hkl, qbvr__sqfri, reduce_op, typ_enum)
        return load_val_ptr(qbvr__sqfri, value)
    return impl


@numba.njit
def get_bit(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@numba.njit
def copy_gathered_null_bytes(null_bitmap_ptr, tmp_null_bytes,
    recv_counts_nulls, recv_counts):
    dsh__hrx = 0
    bek__ejag = 0
    for i in range(len(recv_counts)):
        ekd__moyp = recv_counts[i]
        rxzg__cif = recv_counts_nulls[i]
        pbwj__yawe = tmp_null_bytes[dsh__hrx:dsh__hrx + rxzg__cif]
        for wjg__bcv in range(ekd__moyp):
            set_bit_to(null_bitmap_ptr, bek__ejag, get_bit(pbwj__yawe,
                wjg__bcv))
            bek__ejag += 1
        dsh__hrx += rxzg__cif


@numba.generated_jit(nopython=True)
def gatherv(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
    from bodo.libs.csr_matrix_ext import CSRMatrixType
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.gatherv()')
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            cxhqz__xpxnk = bodo.gatherv(data.codes, allgather, root=root)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                cxhqz__xpxnk, data.dtype)
        return impl_cat
    if isinstance(data, types.Array):
        typ_val = numba_to_c_type(data.dtype)

        def gatherv_impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            data = np.ascontiguousarray(data)
            rank = bodo.libs.distributed_api.get_rank()
            nxbns__iliwh = data.size
            recv_counts = gather_scalar(np.int32(nxbns__iliwh), allgather,
                root=root)
            iphe__xut = recv_counts.sum()
            xmc__kmvgz = empty_like_type(iphe__xut, data)
            ouh__kfjm = np.empty(1, np.int32)
            if rank == root or allgather:
                ouh__kfjm = bodo.ir.join.calc_disp(recv_counts)
            c_gatherv(data.ctypes, np.int32(nxbns__iliwh), xmc__kmvgz.
                ctypes, recv_counts.ctypes, ouh__kfjm.ctypes, np.int32(
                typ_val), allgather, np.int32(root))
            return xmc__kmvgz.reshape((-1,) + data.shape[1:])
        return gatherv_impl
    if is_str_arr_type(data):

        def gatherv_str_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            data = decode_if_dict_array(data)
            xmc__kmvgz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.str_arr_ext.init_str_arr(xmc__kmvgz)
        return gatherv_str_arr_impl
    if data == binary_array_type:

        def gatherv_binary_arr_impl(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            xmc__kmvgz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(xmc__kmvgz)
        return gatherv_binary_arr_impl
    if data == datetime_timedelta_array_type:
        typ_val = numba_to_c_type(types.int64)
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nxbns__iliwh = len(data)
            rxzg__cif = nxbns__iliwh + 7 >> 3
            recv_counts = gather_scalar(np.int32(nxbns__iliwh), allgather,
                root=root)
            iphe__xut = recv_counts.sum()
            xmc__kmvgz = empty_like_type(iphe__xut, data)
            ouh__kfjm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            awg__enm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                ouh__kfjm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                awg__enm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._days_data.ctypes, np.int32(nxbns__iliwh),
                xmc__kmvgz._days_data.ctypes, recv_counts.ctypes, ouh__kfjm
                .ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._seconds_data.ctypes, np.int32(nxbns__iliwh),
                xmc__kmvgz._seconds_data.ctypes, recv_counts.ctypes,
                ouh__kfjm.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._microseconds_data.ctypes, np.int32(nxbns__iliwh
                ), xmc__kmvgz._microseconds_data.ctypes, recv_counts.ctypes,
                ouh__kfjm.ctypes, np.int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(rxzg__cif),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, awg__enm.
                ctypes, fmv__cbrnw, allgather, np.int32(root))
            copy_gathered_null_bytes(xmc__kmvgz._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return xmc__kmvgz
        return gatherv_impl_int_arr
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        typ_val = numba_to_c_type(data.dtype)
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def gatherv_impl_int_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nxbns__iliwh = len(data)
            rxzg__cif = nxbns__iliwh + 7 >> 3
            recv_counts = gather_scalar(np.int32(nxbns__iliwh), allgather,
                root=root)
            iphe__xut = recv_counts.sum()
            xmc__kmvgz = empty_like_type(iphe__xut, data)
            ouh__kfjm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            awg__enm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                ouh__kfjm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                awg__enm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(data._data.ctypes, np.int32(nxbns__iliwh), xmc__kmvgz
                ._data.ctypes, recv_counts.ctypes, ouh__kfjm.ctypes, np.
                int32(typ_val), allgather, np.int32(root))
            c_gatherv(data._null_bitmap.ctypes, np.int32(rxzg__cif),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, awg__enm.
                ctypes, fmv__cbrnw, allgather, np.int32(root))
            copy_gathered_null_bytes(xmc__kmvgz._null_bitmap.ctypes,
                tmp_null_bytes, recv_counts_nulls, recv_counts)
            return xmc__kmvgz
        return gatherv_impl_int_arr
    if isinstance(data, DatetimeArrayType):
        nwpz__xpu = data.tz

        def impl_pd_datetime_arr(data, allgather=False, warn_if_rep=True,
            root=MPI_ROOT):
            bdl__rphu = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.pd_datetime_arr_ext.init_pandas_datetime_array(
                bdl__rphu, nwpz__xpu)
        return impl_pd_datetime_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, allgather=False, warn_if_rep=True, root
            =MPI_ROOT):
            yce__xcc = bodo.gatherv(data._left, allgather, warn_if_rep, root)
            lyr__bngk = bodo.gatherv(data._right, allgather, warn_if_rep, root)
            return bodo.libs.interval_arr_ext.init_interval_array(yce__xcc,
                lyr__bngk)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            zqe__vwd = bodo.hiframes.pd_series_ext.get_series_name(data)
            out_arr = bodo.libs.distributed_api.gatherv(arr, allgather,
                warn_if_rep, root)
            bex__uwxf = bodo.gatherv(index, allgather, warn_if_rep, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bex__uwxf, zqe__vwd)
        return impl
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):
        wlol__xhepj = np.iinfo(np.int64).max
        hulmi__pjwkp = np.iinfo(np.int64).min

        def impl_range_index(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            ogwwg__slzv = data._start
            bmu__eqhp = data._stop
            if len(data) == 0:
                ogwwg__slzv = wlol__xhepj
                bmu__eqhp = hulmi__pjwkp
            ogwwg__slzv = bodo.libs.distributed_api.dist_reduce(ogwwg__slzv,
                np.int32(Reduce_Type.Min.value))
            bmu__eqhp = bodo.libs.distributed_api.dist_reduce(bmu__eqhp, np
                .int32(Reduce_Type.Max.value))
            total_len = bodo.libs.distributed_api.dist_reduce(len(data), np
                .int32(Reduce_Type.Sum.value))
            if ogwwg__slzv == wlol__xhepj and bmu__eqhp == hulmi__pjwkp:
                ogwwg__slzv = 0
                bmu__eqhp = 0
            ocuj__tbh = max(0, -(-(bmu__eqhp - ogwwg__slzv) // data._step))
            if ocuj__tbh < total_len:
                bmu__eqhp = ogwwg__slzv + data._step * total_len
            if bodo.get_rank() != root and not allgather:
                ogwwg__slzv = 0
                bmu__eqhp = 0
            return bodo.hiframes.pd_index_ext.init_range_index(ogwwg__slzv,
                bmu__eqhp, data._step, data._name)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):
        from bodo.hiframes.pd_index_ext import PeriodIndexType
        if isinstance(data, PeriodIndexType):
            elsa__izc = data.freq

            def impl_pd_index(data, allgather=False, warn_if_rep=True, root
                =MPI_ROOT):
                arr = bodo.libs.distributed_api.gatherv(data._data,
                    allgather, root=root)
                return bodo.hiframes.pd_index_ext.init_period_index(arr,
                    data._name, elsa__izc)
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
            xmc__kmvgz = bodo.gatherv(data._data, allgather, root=root)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(xmc__kmvgz
                , data._names, data._name)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.table.TableType):
        harg__iihe = {'bodo': bodo, 'get_table_block': bodo.hiframes.table.
            get_table_block, 'ensure_column_unboxed': bodo.hiframes.table.
            ensure_column_unboxed, 'set_table_block': bodo.hiframes.table.
            set_table_block, 'set_table_len': bodo.hiframes.table.
            set_table_len, 'alloc_list_like': bodo.hiframes.table.
            alloc_list_like, 'init_table': bodo.hiframes.table.init_table}
        tnli__sosv = (
            f'def impl_table(data, allgather=False, warn_if_rep=True, root={MPI_ROOT}):\n'
            )
        tnli__sosv += '  T = data\n'
        tnli__sosv += '  T2 = init_table(T, True)\n'
        for polk__qlez in data.type_to_blk.values():
            harg__iihe[f'arr_inds_{polk__qlez}'] = np.array(data.
                block_to_arr_ind[polk__qlez], dtype=np.int64)
            tnli__sosv += (
                f'  arr_list_{polk__qlez} = get_table_block(T, {polk__qlez})\n'
                )
            tnli__sosv += f"""  out_arr_list_{polk__qlez} = alloc_list_like(arr_list_{polk__qlez}, len(arr_list_{polk__qlez}), True)
"""
            tnli__sosv += f'  for i in range(len(arr_list_{polk__qlez})):\n'
            tnli__sosv += (
                f'    arr_ind_{polk__qlez} = arr_inds_{polk__qlez}[i]\n')
            tnli__sosv += f"""    ensure_column_unboxed(T, arr_list_{polk__qlez}, i, arr_ind_{polk__qlez})
"""
            tnli__sosv += f"""    out_arr_{polk__qlez} = bodo.gatherv(arr_list_{polk__qlez}[i], allgather, warn_if_rep, root)
"""
            tnli__sosv += (
                f'    out_arr_list_{polk__qlez}[i] = out_arr_{polk__qlez}\n')
            tnli__sosv += (
                f'  T2 = set_table_block(T2, out_arr_list_{polk__qlez}, {polk__qlez})\n'
                )
        tnli__sosv += (
            f'  length = T._len if bodo.get_rank() == root or allgather else 0\n'
            )
        tnli__sosv += f'  T2 = set_table_len(T2, length)\n'
        tnli__sosv += f'  return T2\n'
        efp__zomnl = {}
        exec(tnli__sosv, harg__iihe, efp__zomnl)
        ufd__awig = efp__zomnl['impl_table']
        return ufd__awig
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        yzswv__bxvqu = len(data.columns)
        if yzswv__bxvqu == 0:
            ygnne__vzsqe = ColNamesMetaType(())

            def impl(data, allgather=False, warn_if_rep=True, root=MPI_ROOT):
                index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data
                    )
                hnc__oxz = bodo.gatherv(index, allgather, warn_if_rep, root)
                return bodo.hiframes.pd_dataframe_ext.init_dataframe((),
                    hnc__oxz, ygnne__vzsqe)
            return impl
        yys__pdr = ', '.join(f'g_data_{i}' for i in range(yzswv__bxvqu))
        tnli__sosv = (
            'def impl_df(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        if data.is_table_format:
            from bodo.transforms.distributed_analysis import Distribution
            fgv__uivg = bodo.hiframes.pd_dataframe_ext.DataFrameType(data.
                data, data.index, data.columns, Distribution.REP, True)
            yys__pdr = 'T2'
            tnli__sosv += (
                '  T = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(data)\n'
                )
            tnli__sosv += (
                '  T2 = bodo.gatherv(T, allgather, warn_if_rep, root)\n')
        else:
            for i in range(yzswv__bxvqu):
                tnli__sosv += (
                    """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                    .format(i, i))
                tnli__sosv += (
                    '  g_data_{} = bodo.gatherv(data_{}, allgather, warn_if_rep, root)\n'
                    .format(i, i))
        tnli__sosv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        tnli__sosv += (
            '  g_index = bodo.gatherv(index, allgather, warn_if_rep, root)\n')
        tnli__sosv += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_gatherv_with_cols)
"""
            .format(yys__pdr))
        efp__zomnl = {}
        harg__iihe = {'bodo': bodo,
            '__col_name_meta_value_gatherv_with_cols': ColNamesMetaType(
            data.columns)}
        exec(tnli__sosv, harg__iihe, efp__zomnl)
        dzgs__obmv = efp__zomnl['impl_df']
        return dzgs__obmv
    if isinstance(data, ArrayItemArrayType):
        hcov__hcggd = np.int32(numba_to_c_type(types.int32))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def gatherv_array_item_arr_impl(data, allgather=False, warn_if_rep=
            True, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            rmhqt__ecjl = bodo.libs.array_item_arr_ext.get_offsets(data)
            dbtvh__lll = bodo.libs.array_item_arr_ext.get_data(data)
            dbtvh__lll = dbtvh__lll[:rmhqt__ecjl[-1]]
            nakpr__gggk = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            nxbns__iliwh = len(data)
            fus__pszyo = np.empty(nxbns__iliwh, np.uint32)
            rxzg__cif = nxbns__iliwh + 7 >> 3
            for i in range(nxbns__iliwh):
                fus__pszyo[i] = rmhqt__ecjl[i + 1] - rmhqt__ecjl[i]
            recv_counts = gather_scalar(np.int32(nxbns__iliwh), allgather,
                root=root)
            iphe__xut = recv_counts.sum()
            ouh__kfjm = np.empty(1, np.int32)
            recv_counts_nulls = np.empty(1, np.int32)
            awg__enm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                ouh__kfjm = bodo.ir.join.calc_disp(recv_counts)
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for qmeq__yob in range(len(recv_counts)):
                    recv_counts_nulls[qmeq__yob] = recv_counts[qmeq__yob
                        ] + 7 >> 3
                awg__enm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            fuwdo__ifrob = np.empty(iphe__xut + 1, np.uint32)
            zcoh__qumk = bodo.gatherv(dbtvh__lll, allgather, warn_if_rep, root)
            rewem__ivxam = np.empty(iphe__xut + 7 >> 3, np.uint8)
            c_gatherv(fus__pszyo.ctypes, np.int32(nxbns__iliwh),
                fuwdo__ifrob.ctypes, recv_counts.ctypes, ouh__kfjm.ctypes,
                hcov__hcggd, allgather, np.int32(root))
            c_gatherv(nakpr__gggk.ctypes, np.int32(rxzg__cif),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, awg__enm.
                ctypes, fmv__cbrnw, allgather, np.int32(root))
            dummy_use(data)
            ulg__cgvy = np.empty(iphe__xut + 1, np.uint64)
            convert_len_arr_to_offset(fuwdo__ifrob.ctypes, ulg__cgvy.ctypes,
                iphe__xut)
            copy_gathered_null_bytes(rewem__ivxam.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            out_arr = bodo.libs.array_item_arr_ext.init_array_item_array(
                iphe__xut, zcoh__qumk, ulg__cgvy, rewem__ivxam)
            return out_arr
        return gatherv_array_item_arr_impl
    if isinstance(data, StructArrayType):
        ixyg__aycga = data.names
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def impl_struct_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            snm__guyw = bodo.libs.struct_arr_ext.get_data(data)
            ydxk__wmum = bodo.libs.struct_arr_ext.get_null_bitmap(data)
            tpzrk__jhtn = bodo.gatherv(snm__guyw, allgather=allgather, root
                =root)
            rank = bodo.libs.distributed_api.get_rank()
            nxbns__iliwh = len(data)
            rxzg__cif = nxbns__iliwh + 7 >> 3
            recv_counts = gather_scalar(np.int32(nxbns__iliwh), allgather,
                root=root)
            iphe__xut = recv_counts.sum()
            vxwjf__ozdak = np.empty(iphe__xut + 7 >> 3, np.uint8)
            recv_counts_nulls = np.empty(1, np.int32)
            awg__enm = np.empty(1, np.int32)
            tmp_null_bytes = np.empty(1, np.uint8)
            if rank == root or allgather:
                recv_counts_nulls = np.empty(len(recv_counts), np.int32)
                for i in range(len(recv_counts)):
                    recv_counts_nulls[i] = recv_counts[i] + 7 >> 3
                awg__enm = bodo.ir.join.calc_disp(recv_counts_nulls)
                tmp_null_bytes = np.empty(recv_counts_nulls.sum(), np.uint8)
            c_gatherv(ydxk__wmum.ctypes, np.int32(rxzg__cif),
                tmp_null_bytes.ctypes, recv_counts_nulls.ctypes, awg__enm.
                ctypes, fmv__cbrnw, allgather, np.int32(root))
            copy_gathered_null_bytes(vxwjf__ozdak.ctypes, tmp_null_bytes,
                recv_counts_nulls, recv_counts)
            return bodo.libs.struct_arr_ext.init_struct_arr(tpzrk__jhtn,
                vxwjf__ozdak, ixyg__aycga)
        return impl_struct_arr
    if data == binary_array_type:

        def impl_bin_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            xmc__kmvgz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.binary_arr_ext.init_binary_arr(xmc__kmvgz)
        return impl_bin_arr
    if isinstance(data, TupleArrayType):

        def impl_tuple_arr(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            xmc__kmvgz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.tuple_arr_ext.init_tuple_arr(xmc__kmvgz)
        return impl_tuple_arr
    if isinstance(data, MapArrayType):

        def impl_map_arr(data, allgather=False, warn_if_rep=True, root=MPI_ROOT
            ):
            xmc__kmvgz = bodo.gatherv(data._data, allgather, warn_if_rep, root)
            return bodo.libs.map_arr_ext.init_map_arr(xmc__kmvgz)
        return impl_map_arr
    if isinstance(data, CSRMatrixType):

        def impl_csr_matrix(data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT):
            xmc__kmvgz = bodo.gatherv(data.data, allgather, warn_if_rep, root)
            lmma__vqu = bodo.gatherv(data.indices, allgather, warn_if_rep, root
                )
            bxea__jykt = bodo.gatherv(data.indptr, allgather, warn_if_rep, root
                )
            unoi__isa = gather_scalar(data.shape[0], allgather, root=root)
            ljzt__gwvi = unoi__isa.sum()
            yzswv__bxvqu = bodo.libs.distributed_api.dist_reduce(data.shape
                [1], np.int32(Reduce_Type.Max.value))
            hnm__kleii = np.empty(ljzt__gwvi + 1, np.int64)
            lmma__vqu = lmma__vqu.astype(np.int64)
            hnm__kleii[0] = 0
            kdvb__ylist = 1
            kaxs__zkg = 0
            for odok__zavp in unoi__isa:
                for rejmy__vgem in range(odok__zavp):
                    zjm__rexv = bxea__jykt[kaxs__zkg + 1] - bxea__jykt[
                        kaxs__zkg]
                    hnm__kleii[kdvb__ylist] = hnm__kleii[kdvb__ylist - 1
                        ] + zjm__rexv
                    kdvb__ylist += 1
                    kaxs__zkg += 1
                kaxs__zkg += 1
            return bodo.libs.csr_matrix_ext.init_csr_matrix(xmc__kmvgz,
                lmma__vqu, hnm__kleii, (ljzt__gwvi, yzswv__bxvqu))
        return impl_csr_matrix
    if isinstance(data, types.BaseTuple):
        tnli__sosv = (
            'def impl_tuple(data, allgather=False, warn_if_rep=True, root={}):\n'
            .format(MPI_ROOT))
        tnli__sosv += '  return ({}{})\n'.format(', '.join(
            'bodo.gatherv(data[{}], allgather, warn_if_rep, root)'.format(i
            ) for i in range(len(data))), ',' if len(data) > 0 else '')
        efp__zomnl = {}
        exec(tnli__sosv, {'bodo': bodo}, efp__zomnl)
        crlac__hzahh = efp__zomnl['impl_tuple']
        return crlac__hzahh
    if data is types.none:
        return (lambda data, allgather=False, warn_if_rep=True, root=
            MPI_ROOT: None)
    raise BodoError('gatherv() not available for {}'.format(data))


@numba.generated_jit(nopython=True)
def rebalance(data, dests=None, random=False, random_seed=None, parallel=False
    ):
    bodo.hiframes.pd_dataframe_ext.check_runtime_cols_unsupported(data,
        'bodo.rebalance()')
    tnli__sosv = (
        'def impl(data, dests=None, random=False, random_seed=None, parallel=False):\n'
        )
    tnli__sosv += '    if random:\n'
    tnli__sosv += '        if random_seed is None:\n'
    tnli__sosv += '            random = 1\n'
    tnli__sosv += '        else:\n'
    tnli__sosv += '            random = 2\n'
    tnli__sosv += '    if random_seed is None:\n'
    tnli__sosv += '        random_seed = -1\n'
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        xcl__igf = data
        yzswv__bxvqu = len(xcl__igf.columns)
        for i in range(yzswv__bxvqu):
            tnli__sosv += f"""    data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i})
"""
        tnli__sosv += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data))
"""
        yys__pdr = ', '.join(f'data_{i}' for i in range(yzswv__bxvqu))
        tnli__sosv += ('    info_list_total = [{}, array_to_info(ind_arr)]\n'
            .format(', '.join('array_to_info(data_{})'.format(bobm__knh) for
            bobm__knh in range(yzswv__bxvqu))))
        tnli__sosv += (
            '    table_total = arr_info_list_to_table(info_list_total)\n')
        tnli__sosv += '    if dests is None:\n'
        tnli__sosv += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        tnli__sosv += '    else:\n'
        tnli__sosv += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        for zol__pji in range(yzswv__bxvqu):
            tnli__sosv += (
                """    out_arr_{0} = info_to_array(info_from_table(out_table, {0}), data_{0})
"""
                .format(zol__pji))
        tnli__sosv += (
            """    out_arr_index = info_to_array(info_from_table(out_table, {}), ind_arr)
"""
            .format(yzswv__bxvqu))
        tnli__sosv += '    delete_table(out_table)\n'
        tnli__sosv += '    if parallel:\n'
        tnli__sosv += '        delete_table(table_total)\n'
        yys__pdr = ', '.join('out_arr_{}'.format(i) for i in range(
            yzswv__bxvqu))
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        tnli__sosv += (
            """    return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), {}, __col_name_meta_value_rebalance)
"""
            .format(yys__pdr, index))
    elif isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):
        tnli__sosv += (
            '    data_0 = bodo.hiframes.pd_series_ext.get_series_data(data)\n')
        tnli__sosv += """    ind_arr = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(data))
"""
        tnli__sosv += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(data)\n')
        tnli__sosv += """    table_total = arr_info_list_to_table([array_to_info(data_0), array_to_info(ind_arr)])
"""
        tnli__sosv += '    if dests is None:\n'
        tnli__sosv += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        tnli__sosv += '    else:\n'
        tnli__sosv += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        tnli__sosv += (
            '    out_arr_0 = info_to_array(info_from_table(out_table, 0), data_0)\n'
            )
        tnli__sosv += (
            '    out_arr_index = info_to_array(info_from_table(out_table, 1), ind_arr)\n'
            )
        tnli__sosv += '    delete_table(out_table)\n'
        tnli__sosv += '    if parallel:\n'
        tnli__sosv += '        delete_table(table_total)\n'
        index = 'bodo.utils.conversion.index_from_array(out_arr_index)'
        tnli__sosv += f"""    return bodo.hiframes.pd_series_ext.init_series(out_arr_0, {index}, name)
"""
    elif isinstance(data, types.Array):
        assert is_overload_false(random
            ), 'Call random_shuffle instead of rebalance'
        tnli__sosv += '    if not parallel:\n'
        tnli__sosv += '        return data\n'
        tnli__sosv += """    dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        tnli__sosv += '    if dests is None:\n'
        tnli__sosv += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        tnli__sosv += '    elif bodo.get_rank() not in dests:\n'
        tnli__sosv += '        dim0_local_size = 0\n'
        tnli__sosv += '    else:\n'
        tnli__sosv += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, len(dests), dests.index(bodo.get_rank()))
"""
        tnli__sosv += """    out = np.empty((dim0_local_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        tnli__sosv += """    bodo.libs.distributed_api.dist_oneD_reshape_shuffle(out, data, dim0_global_size, dests)
"""
        tnli__sosv += '    return out\n'
    elif bodo.utils.utils.is_array_typ(data, False):
        tnli__sosv += (
            '    table_total = arr_info_list_to_table([array_to_info(data)])\n'
            )
        tnli__sosv += '    if dests is None:\n'
        tnli__sosv += """        out_table = shuffle_renormalization(table_total, random, random_seed, parallel)
"""
        tnli__sosv += '    else:\n'
        tnli__sosv += """        out_table = shuffle_renormalization_group(table_total, random, random_seed, parallel, len(dests), np.array(dests, dtype=np.int32).ctypes)
"""
        tnli__sosv += (
            '    out_arr = info_to_array(info_from_table(out_table, 0), data)\n'
            )
        tnli__sosv += '    delete_table(out_table)\n'
        tnli__sosv += '    if parallel:\n'
        tnli__sosv += '        delete_table(table_total)\n'
        tnli__sosv += '    return out_arr\n'
    else:
        raise BodoError(f'Type {data} not supported for bodo.rebalance')
    efp__zomnl = {}
    harg__iihe = {'np': np, 'bodo': bodo, 'array_to_info': bodo.libs.array.
        array_to_info, 'shuffle_renormalization': bodo.libs.array.
        shuffle_renormalization, 'shuffle_renormalization_group': bodo.libs
        .array.shuffle_renormalization_group, 'arr_info_list_to_table':
        bodo.libs.array.arr_info_list_to_table, 'info_from_table': bodo.
        libs.array.info_from_table, 'info_to_array': bodo.libs.array.
        info_to_array, 'delete_table': bodo.libs.array.delete_table}
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        harg__iihe.update({'__col_name_meta_value_rebalance':
            ColNamesMetaType(xcl__igf.columns)})
    exec(tnli__sosv, harg__iihe, efp__zomnl)
    impl = efp__zomnl['impl']
    return impl


@numba.generated_jit(nopython=True)
def random_shuffle(data, seed=None, dests=None, n_samples=None, parallel=False
    ):
    tnli__sosv = (
        'def impl(data, seed=None, dests=None, n_samples=None, parallel=False):\n'
        )
    if isinstance(data, types.Array):
        if not is_overload_none(dests):
            raise BodoError('not supported')
        tnli__sosv += '    if seed is None:\n'
        tnli__sosv += """        seed = bodo.libs.distributed_api.bcast_scalar(np.random.randint(0, 2**31))
"""
        tnli__sosv += '    np.random.seed(seed)\n'
        tnli__sosv += '    if not parallel:\n'
        tnli__sosv += '        data = data.copy()\n'
        tnli__sosv += '        np.random.shuffle(data)\n'
        if not is_overload_none(n_samples):
            tnli__sosv += '        data = data[:n_samples]\n'
        tnli__sosv += '        return data\n'
        tnli__sosv += '    else:\n'
        tnli__sosv += """        dim0_global_size = bodo.libs.distributed_api.dist_reduce(data.shape[0], np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value))
"""
        tnli__sosv += '        permutation = np.arange(dim0_global_size)\n'
        tnli__sosv += '        np.random.shuffle(permutation)\n'
        if not is_overload_none(n_samples):
            tnli__sosv += (
                '        n_samples = max(0, min(dim0_global_size, n_samples))\n'
                )
        else:
            tnli__sosv += '        n_samples = dim0_global_size\n'
        tnli__sosv += """        dim0_local_size = bodo.libs.distributed_api.get_node_portion(dim0_global_size, bodo.get_size(), bodo.get_rank())
"""
        tnli__sosv += """        dim0_output_size = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
        tnli__sosv += """        output = np.empty((dim0_output_size,) + tuple(data.shape[1:]), dtype=data.dtype)
"""
        tnli__sosv += (
            '        dtype_size = bodo.io.np_io.get_dtype_size(data.dtype)\n')
        tnli__sosv += """        bodo.libs.distributed_api.dist_permutation_array_index(output, dim0_global_size, dtype_size, data, permutation, len(permutation), n_samples)
"""
        tnli__sosv += '        return output\n'
    else:
        tnli__sosv += """    output = bodo.libs.distributed_api.rebalance(data, dests=dests, random=True, random_seed=seed, parallel=parallel)
"""
        if not is_overload_none(n_samples):
            tnli__sosv += """    local_n_samples = bodo.libs.distributed_api.get_node_portion(n_samples, bodo.get_size(), bodo.get_rank())
"""
            tnli__sosv += '    output = output[:local_n_samples]\n'
        tnli__sosv += '    return output\n'
    efp__zomnl = {}
    exec(tnli__sosv, {'np': np, 'bodo': bodo}, efp__zomnl)
    impl = efp__zomnl['impl']
    return impl


@numba.generated_jit(nopython=True)
def allgatherv(data, warn_if_rep=True, root=MPI_ROOT):
    return lambda data, warn_if_rep=True, root=MPI_ROOT: gatherv(data, True,
        warn_if_rep, root)


@numba.njit
def get_scatter_null_bytes_buff(null_bitmap_ptr, sendcounts, sendcounts_nulls):
    if bodo.get_rank() != MPI_ROOT:
        return np.empty(1, np.uint8)
    zgc__uqk = np.empty(sendcounts_nulls.sum(), np.uint8)
    dsh__hrx = 0
    bek__ejag = 0
    for aiuy__sadwq in range(len(sendcounts)):
        ekd__moyp = sendcounts[aiuy__sadwq]
        rxzg__cif = sendcounts_nulls[aiuy__sadwq]
        pbwj__yawe = zgc__uqk[dsh__hrx:dsh__hrx + rxzg__cif]
        for wjg__bcv in range(ekd__moyp):
            set_bit_to_arr(pbwj__yawe, wjg__bcv, get_bit_bitmap(
                null_bitmap_ptr, bek__ejag))
            bek__ejag += 1
        dsh__hrx += rxzg__cif
    return zgc__uqk


def _bcast_dtype(data, root=MPI_ROOT):
    try:
        from mpi4py import MPI
    except:
        raise BodoError('mpi4py is required for scatterv')
    cvgy__lwc = MPI.COMM_WORLD
    data = cvgy__lwc.bcast(data, root)
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
    ecqq__ylrk = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    plhe__tadxc = (0,) * ecqq__ylrk

    def scatterv_arr_impl(data, send_counts=None, warn_if_dist=True):
        rank = bodo.libs.distributed_api.get_rank()
        n_pes = bodo.libs.distributed_api.get_size()
        tofs__rdmmd = np.ascontiguousarray(data)
        eequs__ppvjn = data.ctypes
        tixuy__ikczt = plhe__tadxc
        if rank == MPI_ROOT:
            tixuy__ikczt = tofs__rdmmd.shape
        tixuy__ikczt = bcast_tuple(tixuy__ikczt)
        lbodg__njdtc = get_tuple_prod(tixuy__ikczt[1:])
        send_counts = _get_scatterv_send_counts(send_counts, n_pes,
            tixuy__ikczt[0])
        send_counts *= lbodg__njdtc
        nxbns__iliwh = send_counts[rank]
        vbu__wyjl = np.empty(nxbns__iliwh, dtype)
        ouh__kfjm = bodo.ir.join.calc_disp(send_counts)
        c_scatterv(eequs__ppvjn, send_counts.ctypes, ouh__kfjm.ctypes,
            vbu__wyjl.ctypes, np.int32(nxbns__iliwh), np.int32(typ_val))
        return vbu__wyjl.reshape((-1,) + tixuy__ikczt[1:])
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
        mqtnn__eia = '{}Int{}'.format('' if dtype.dtype.signed else 'U',
            dtype.dtype.bitwidth)
        return pd.array([3], mqtnn__eia)
    if dtype == boolean_array:
        return pd.array([True], 'boolean')
    if isinstance(dtype, DecimalArrayType):
        return np.array([Decimal('32.1')])
    if dtype == datetime_date_array_type:
        return np.array([datetime.date(2011, 8, 9)])
    if dtype == datetime_timedelta_array_type:
        return np.array([datetime.timedelta(33)])
    if bodo.hiframes.pd_index_ext.is_pd_index_type(dtype):
        zqe__vwd = _get_name_value_for_type(dtype.name_typ)
        if isinstance(dtype, bodo.hiframes.pd_index_ext.RangeIndexType):
            return pd.RangeIndex(1, name=zqe__vwd)
        wse__zbww = bodo.utils.typing.get_index_data_arr_types(dtype)[0]
        arr = get_value_for_type(wse__zbww)
        return pd.Index(arr, name=zqe__vwd)
    if isinstance(dtype, bodo.hiframes.pd_multi_index_ext.MultiIndexType):
        import pyarrow as pa
        zqe__vwd = _get_name_value_for_type(dtype.name_typ)
        ixyg__aycga = tuple(_get_name_value_for_type(t) for t in dtype.
            names_typ)
        mhusv__rlcjz = tuple(get_value_for_type(t) for t in dtype.array_types)
        mhusv__rlcjz = tuple(a.to_numpy(False) if isinstance(a, pa.Array) else
            a for a in mhusv__rlcjz)
        val = pd.MultiIndex.from_arrays(mhusv__rlcjz, names=ixyg__aycga)
        val.name = zqe__vwd
        return val
    if isinstance(dtype, bodo.hiframes.pd_series_ext.SeriesType):
        zqe__vwd = _get_name_value_for_type(dtype.name_typ)
        arr = get_value_for_type(dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.Series(arr, index, name=zqe__vwd)
    if isinstance(dtype, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        mhusv__rlcjz = tuple(get_value_for_type(t) for t in dtype.data)
        index = get_value_for_type(dtype.index)
        return pd.DataFrame({zqe__vwd: arr for zqe__vwd, arr in zip(dtype.
            columns, mhusv__rlcjz)}, index)
    if isinstance(dtype, CategoricalArrayType):
        return pd.Categorical.from_codes([0], dtype.dtype.categories)
    if isinstance(dtype, types.BaseTuple):
        return tuple(get_value_for_type(t) for t in dtype.types)
    if isinstance(dtype, ArrayItemArrayType):
        return pd.Series([get_value_for_type(dtype.dtype),
            get_value_for_type(dtype.dtype)]).values
    if isinstance(dtype, IntervalArrayType):
        wse__zbww = get_value_for_type(dtype.arr_type)
        return pd.arrays.IntervalArray([pd.Interval(wse__zbww[0], wse__zbww
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
        hcov__hcggd = np.int32(numba_to_c_type(types.int32))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))
        if data == binary_array_type:
            owsrj__fctc = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
        else:
            owsrj__fctc = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
        tnli__sosv = f"""def impl(
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
            recv_arr = {owsrj__fctc}(n_loc, n_loc_char)

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
        efp__zomnl = dict()
        exec(tnli__sosv, {'bodo': bodo, 'np': np, 'int32_typ_enum':
            hcov__hcggd, 'char_typ_enum': fmv__cbrnw,
            'decode_if_dict_array': decode_if_dict_array}, efp__zomnl)
        impl = efp__zomnl['impl']
        return impl
    if isinstance(data, ArrayItemArrayType):
        hcov__hcggd = np.int32(numba_to_c_type(types.int32))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def scatterv_array_item_impl(data, send_counts=None, warn_if_dist=True
            ):
            lduxq__eyxlt = bodo.libs.array_item_arr_ext.get_offsets(data)
            okdvh__and = bodo.libs.array_item_arr_ext.get_data(data)
            okdvh__and = okdvh__and[:lduxq__eyxlt[-1]]
            fyle__zirzh = bodo.libs.array_item_arr_ext.get_null_bitmap(data)
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            bliex__vnnoo = bcast_scalar(len(data))
            klf__bpzt = np.empty(len(data), np.uint32)
            for i in range(len(data)):
                klf__bpzt[i] = lduxq__eyxlt[i + 1] - lduxq__eyxlt[i]
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                bliex__vnnoo)
            ouh__kfjm = bodo.ir.join.calc_disp(send_counts)
            oophz__guqpp = np.empty(n_pes, np.int32)
            if rank == 0:
                itzc__cdq = 0
                for i in range(n_pes):
                    btoko__zmsnc = 0
                    for rejmy__vgem in range(send_counts[i]):
                        btoko__zmsnc += klf__bpzt[itzc__cdq]
                        itzc__cdq += 1
                    oophz__guqpp[i] = btoko__zmsnc
            bcast(oophz__guqpp)
            pzx__tfbm = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                pzx__tfbm[i] = send_counts[i] + 7 >> 3
            awg__enm = bodo.ir.join.calc_disp(pzx__tfbm)
            nxbns__iliwh = send_counts[rank]
            oolcn__tdgg = np.empty(nxbns__iliwh + 1, np_offset_type)
            vjiw__rhs = bodo.libs.distributed_api.scatterv_impl(okdvh__and,
                oophz__guqpp)
            mjpnn__dkfcg = nxbns__iliwh + 7 >> 3
            ahm__zajz = np.empty(mjpnn__dkfcg, np.uint8)
            esctt__bxpvb = np.empty(nxbns__iliwh, np.uint32)
            c_scatterv(klf__bpzt.ctypes, send_counts.ctypes, ouh__kfjm.
                ctypes, esctt__bxpvb.ctypes, np.int32(nxbns__iliwh),
                hcov__hcggd)
            convert_len_arr_to_offset(esctt__bxpvb.ctypes, oolcn__tdgg.
                ctypes, nxbns__iliwh)
            rbry__xhuzi = get_scatter_null_bytes_buff(fyle__zirzh.ctypes,
                send_counts, pzx__tfbm)
            c_scatterv(rbry__xhuzi.ctypes, pzx__tfbm.ctypes, awg__enm.
                ctypes, ahm__zajz.ctypes, np.int32(mjpnn__dkfcg), fmv__cbrnw)
            return bodo.libs.array_item_arr_ext.init_array_item_array(
                nxbns__iliwh, vjiw__rhs, oolcn__tdgg, ahm__zajz)
        return scatterv_array_item_impl
    if isinstance(data, (IntegerArrayType, DecimalArrayType)) or data in (
        boolean_array, datetime_date_array_type):
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))
        if isinstance(data, IntegerArrayType):
            mnr__hczjq = bodo.libs.int_arr_ext.init_integer_array
        if isinstance(data, DecimalArrayType):
            precision = data.precision
            scale = data.scale
            mnr__hczjq = numba.njit(no_cpython_wrapper=True)(lambda d, b:
                bodo.libs.decimal_arr_ext.init_decimal_array(d, b,
                precision, scale))
        if data == boolean_array:
            mnr__hczjq = bodo.libs.bool_arr_ext.init_bool_array
        if data == datetime_date_array_type:
            mnr__hczjq = (bodo.hiframes.datetime_date_ext.
                init_datetime_date_array)

        def scatterv_impl_int_arr(data, send_counts=None, warn_if_dist=True):
            n_pes = bodo.libs.distributed_api.get_size()
            tofs__rdmmd = data._data
            ydxk__wmum = data._null_bitmap
            oigr__eay = len(tofs__rdmmd)
            zbep__jjh = _scatterv_np(tofs__rdmmd, send_counts)
            bliex__vnnoo = bcast_scalar(oigr__eay)
            cef__pgnn = len(zbep__jjh) + 7 >> 3
            zdcxy__fsldq = np.empty(cef__pgnn, np.uint8)
            send_counts = _get_scatterv_send_counts(send_counts, n_pes,
                bliex__vnnoo)
            pzx__tfbm = np.empty(n_pes, np.int32)
            for i in range(n_pes):
                pzx__tfbm[i] = send_counts[i] + 7 >> 3
            awg__enm = bodo.ir.join.calc_disp(pzx__tfbm)
            rbry__xhuzi = get_scatter_null_bytes_buff(ydxk__wmum.ctypes,
                send_counts, pzx__tfbm)
            c_scatterv(rbry__xhuzi.ctypes, pzx__tfbm.ctypes, awg__enm.
                ctypes, zdcxy__fsldq.ctypes, np.int32(cef__pgnn), fmv__cbrnw)
            return mnr__hczjq(zbep__jjh, zdcxy__fsldq)
        return scatterv_impl_int_arr
    if isinstance(data, IntervalArrayType):

        def impl_interval_arr(data, send_counts=None, warn_if_dist=True):
            ygj__yadx = bodo.libs.distributed_api.scatterv_impl(data._left,
                send_counts)
            onh__nzabh = bodo.libs.distributed_api.scatterv_impl(data.
                _right, send_counts)
            return bodo.libs.interval_arr_ext.init_interval_array(ygj__yadx,
                onh__nzabh)
        return impl_interval_arr
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, send_counts=None, warn_if_dist=True):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ogwwg__slzv = data._start
            bmu__eqhp = data._stop
            cfvch__xnwr = data._step
            zqe__vwd = data._name
            zqe__vwd = bcast_scalar(zqe__vwd)
            ogwwg__slzv = bcast_scalar(ogwwg__slzv)
            bmu__eqhp = bcast_scalar(bmu__eqhp)
            cfvch__xnwr = bcast_scalar(cfvch__xnwr)
            mlxyv__pguxi = bodo.libs.array_kernels.calc_nitems(ogwwg__slzv,
                bmu__eqhp, cfvch__xnwr)
            chunk_start = bodo.libs.distributed_api.get_start(mlxyv__pguxi,
                n_pes, rank)
            hsyvr__ovu = bodo.libs.distributed_api.get_node_portion(
                mlxyv__pguxi, n_pes, rank)
            vzhru__lwcdm = ogwwg__slzv + cfvch__xnwr * chunk_start
            hvor__uxwas = ogwwg__slzv + cfvch__xnwr * (chunk_start + hsyvr__ovu
                )
            hvor__uxwas = min(hvor__uxwas, bmu__eqhp)
            return bodo.hiframes.pd_index_ext.init_range_index(vzhru__lwcdm,
                hvor__uxwas, cfvch__xnwr, zqe__vwd)
        return impl_range_index
    if isinstance(data, bodo.hiframes.pd_index_ext.PeriodIndexType):
        elsa__izc = data.freq

        def impl_period_index(data, send_counts=None, warn_if_dist=True):
            tofs__rdmmd = data._data
            zqe__vwd = data._name
            zqe__vwd = bcast_scalar(zqe__vwd)
            arr = bodo.libs.distributed_api.scatterv_impl(tofs__rdmmd,
                send_counts)
            return bodo.hiframes.pd_index_ext.init_period_index(arr,
                zqe__vwd, elsa__izc)
        return impl_period_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, send_counts=None, warn_if_dist=True):
            tofs__rdmmd = data._data
            zqe__vwd = data._name
            zqe__vwd = bcast_scalar(zqe__vwd)
            arr = bodo.libs.distributed_api.scatterv_impl(tofs__rdmmd,
                send_counts)
            return bodo.utils.conversion.index_from_array(arr, zqe__vwd)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_multi_index_ext.MultiIndexType):

        def impl_multi_index(data, send_counts=None, warn_if_dist=True):
            xmc__kmvgz = bodo.libs.distributed_api.scatterv_impl(data._data,
                send_counts)
            zqe__vwd = bcast_scalar(data._name)
            ixyg__aycga = bcast_tuple(data._names)
            return bodo.hiframes.pd_multi_index_ext.init_multi_index(xmc__kmvgz
                , ixyg__aycga, zqe__vwd)
        return impl_multi_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, send_counts=None, warn_if_dist=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            zqe__vwd = bodo.hiframes.pd_series_ext.get_series_name(data)
            pjw__ypq = bcast_scalar(zqe__vwd)
            out_arr = bodo.libs.distributed_api.scatterv_impl(arr, send_counts)
            bex__uwxf = bodo.libs.distributed_api.scatterv_impl(index,
                send_counts)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bex__uwxf, pjw__ypq)
        return impl_series
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        yzswv__bxvqu = len(data.columns)
        yys__pdr = ', '.join('g_data_{}'.format(i) for i in range(yzswv__bxvqu)
            )
        woxmv__ppmi = ColNamesMetaType(data.columns)
        tnli__sosv = (
            'def impl_df(data, send_counts=None, warn_if_dist=True):\n')
        for i in range(yzswv__bxvqu):
            tnli__sosv += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            tnli__sosv += (
                """  g_data_{} = bodo.libs.distributed_api.scatterv_impl(data_{}, send_counts)
"""
                .format(i, i))
        tnli__sosv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        tnli__sosv += (
            '  g_index = bodo.libs.distributed_api.scatterv_impl(index, send_counts)\n'
            )
        tnli__sosv += f"""  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({yys__pdr},), g_index, __col_name_meta_scaterv_impl)
"""
        efp__zomnl = {}
        exec(tnli__sosv, {'bodo': bodo, '__col_name_meta_scaterv_impl':
            woxmv__ppmi}, efp__zomnl)
        dzgs__obmv = efp__zomnl['impl_df']
        return dzgs__obmv
    if isinstance(data, CategoricalArrayType):

        def impl_cat(data, send_counts=None, warn_if_dist=True):
            cxhqz__xpxnk = bodo.libs.distributed_api.scatterv_impl(data.
                codes, send_counts)
            return bodo.hiframes.pd_categorical_ext.init_categorical_array(
                cxhqz__xpxnk, data.dtype)
        return impl_cat
    if isinstance(data, types.BaseTuple):
        tnli__sosv = (
            'def impl_tuple(data, send_counts=None, warn_if_dist=True):\n')
        tnli__sosv += '  return ({}{})\n'.format(', '.join(
            'bodo.libs.distributed_api.scatterv_impl(data[{}], send_counts)'
            .format(i) for i in range(len(data))), ',' if len(data) > 0 else ''
            )
        efp__zomnl = {}
        exec(tnli__sosv, {'bodo': bodo}, efp__zomnl)
        crlac__hzahh = efp__zomnl['impl_tuple']
        return crlac__hzahh
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
        vuo__zsra = np.int32(numba_to_c_type(offset_type))
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def bcast_str_impl(data, root=MPI_ROOT):
            data = decode_if_dict_array(data)
            nxbns__iliwh = len(data)
            zjqcl__rbaj = num_total_chars(data)
            assert nxbns__iliwh < INT_MAX
            assert zjqcl__rbaj < INT_MAX
            oos__huhoo = get_offset_ptr(data)
            eequs__ppvjn = get_data_ptr(data)
            null_bitmap_ptr = get_null_bitmap_ptr(data)
            rxzg__cif = nxbns__iliwh + 7 >> 3
            c_bcast(oos__huhoo, np.int32(nxbns__iliwh + 1), vuo__zsra, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(eequs__ppvjn, np.int32(zjqcl__rbaj), fmv__cbrnw, np.
                array([-1]).ctypes, 0, np.int32(root))
            c_bcast(null_bitmap_ptr, np.int32(rxzg__cif), fmv__cbrnw, np.
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
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))

        def impl_str(val, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            if rank != root:
                fzyo__fpi = 0
                poiqm__emgxa = np.empty(0, np.uint8).ctypes
            else:
                poiqm__emgxa, fzyo__fpi = (bodo.libs.str_ext.
                    unicode_to_utf8_and_len(val))
            fzyo__fpi = bodo.libs.distributed_api.bcast_scalar(fzyo__fpi, root)
            if rank != root:
                smz__vqew = np.empty(fzyo__fpi + 1, np.uint8)
                smz__vqew[fzyo__fpi] = 0
                poiqm__emgxa = smz__vqew.ctypes
            c_bcast(poiqm__emgxa, np.int32(fzyo__fpi), fmv__cbrnw, np.array
                ([-1]).ctypes, 0, np.int32(root))
            return bodo.libs.str_arr_ext.decode_utf8(poiqm__emgxa, fzyo__fpi)
        return impl_str
    typ_val = numba_to_c_type(val)
    tnli__sosv = f"""def bcast_scalar_impl(val, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = val
  c_bcast(send.ctypes, np.int32(1), np.int32({typ_val}), np.array([-1]).ctypes, 0, np.int32(root))
  return send[0]
"""
    dtype = numba.np.numpy_support.as_dtype(val)
    efp__zomnl = {}
    exec(tnli__sosv, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast, 'dtype':
        dtype}, efp__zomnl)
    qmp__ocxgv = efp__zomnl['bcast_scalar_impl']
    return qmp__ocxgv


@numba.generated_jit(nopython=True)
def bcast_tuple(val, root=MPI_ROOT):
    assert isinstance(val, types.BaseTuple)
    aokom__qkixd = len(val)
    tnli__sosv = f'def bcast_tuple_impl(val, root={MPI_ROOT}):\n'
    tnli__sosv += '  return ({}{})'.format(','.join(
        'bcast_scalar(val[{}], root)'.format(i) for i in range(aokom__qkixd
        )), ',' if aokom__qkixd else '')
    efp__zomnl = {}
    exec(tnli__sosv, {'bcast_scalar': bcast_scalar}, efp__zomnl)
    fpz__ainsw = efp__zomnl['bcast_tuple_impl']
    return fpz__ainsw


def prealloc_str_for_bcast(arr, root=MPI_ROOT):
    return arr


@overload(prealloc_str_for_bcast, no_unliteral=True)
def prealloc_str_for_bcast_overload(arr, root=MPI_ROOT):
    if arr == string_array_type:

        def prealloc_impl(arr, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            nxbns__iliwh = bcast_scalar(len(arr), root)
            lzl__yptbn = bcast_scalar(np.int64(num_total_chars(arr)), root)
            if rank != root:
                arr = pre_alloc_string_array(nxbns__iliwh, lzl__yptbn)
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
            vzhru__lwcdm = max(arr_start, slice_index.start) - arr_start
            hvor__uxwas = max(slice_index.stop - arr_start, 0)
            return slice(vzhru__lwcdm, hvor__uxwas)
    else:

        def impl(idx, arr_start, total_len):
            slice_index = numba.cpython.unicode._normalize_slice(idx, total_len
                )
            ogwwg__slzv = slice_index.start
            cfvch__xnwr = slice_index.step
            nbv__ikt = (0 if cfvch__xnwr == 1 or ogwwg__slzv > arr_start else
                abs(cfvch__xnwr - arr_start % cfvch__xnwr) % cfvch__xnwr)
            vzhru__lwcdm = max(arr_start, slice_index.start
                ) - arr_start + nbv__ikt
            hvor__uxwas = max(slice_index.stop - arr_start, 0)
            return slice(vzhru__lwcdm, hvor__uxwas, cfvch__xnwr)
    return impl


def slice_getitem(arr, slice_index, arr_start, total_len):
    return arr[slice_index]


@overload(slice_getitem, no_unliteral=True, jit_options={'cache': True})
def slice_getitem_overload(arr, slice_index, arr_start, total_len):

    def getitem_impl(arr, slice_index, arr_start, total_len):
        eixp__biofv = get_local_slice(slice_index, arr_start, total_len)
        return bodo.utils.conversion.ensure_contig_if_np(arr[eixp__biofv])
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
        tmdpl__dzsd = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND
        fmv__cbrnw = np.int32(numba_to_c_type(types.uint8))
        vwl__cet = arr.dtype

        def str_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            arr = decode_if_dict_array(arr)
            ind = ind % total_len
            root = np.int32(0)
            btunf__kxt = np.int32(10)
            tag = np.int32(11)
            idfs__emcga = np.zeros(1, np.int64)
            if arr_start <= ind < arr_start + len(arr):
                ind = ind - arr_start
                dbtvh__lll = arr._data
                vvsp__xzeh = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    dbtvh__lll, ind)
                srrx__wsrk = bodo.libs.array_item_arr_ext.get_offsets_ind(
                    dbtvh__lll, ind + 1)
                length = srrx__wsrk - vvsp__xzeh
                biqc__pubt = dbtvh__lll[ind]
                idfs__emcga[0] = length
                isend(idfs__emcga, np.int32(1), root, btunf__kxt, True)
                isend(biqc__pubt, np.int32(length), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(vwl__cet,
                tmdpl__dzsd, 0, 1)
            ocuj__tbh = 0
            if rank == root:
                ocuj__tbh = recv(np.int64, ANY_SOURCE, btunf__kxt)
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    vwl__cet, tmdpl__dzsd, ocuj__tbh, 1)
                eequs__ppvjn = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
                _recv(eequs__ppvjn, np.int32(ocuj__tbh), fmv__cbrnw,
                    ANY_SOURCE, tag)
            dummy_use(idfs__emcga)
            ocuj__tbh = bcast_scalar(ocuj__tbh)
            dummy_use(arr)
            if rank != root:
                val = bodo.libs.str_ext.alloc_empty_bytes_or_string_data(
                    vwl__cet, tmdpl__dzsd, ocuj__tbh, 1)
            eequs__ppvjn = bodo.libs.str_ext.get_unicode_or_numpy_data(val)
            c_bcast(eequs__ppvjn, np.int32(ocuj__tbh), fmv__cbrnw, np.array
                ([-1]).ctypes, 0, np.int32(root))
            val = transform_str_getitem_output(val, ocuj__tbh)
            return val
        return str_getitem_impl
    if isinstance(arr, bodo.CategoricalArrayType):
        dlk__kgfk = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            arr.dtype)

        def cat_getitem_impl(arr, ind, arr_start, total_len, is_1D):
            if ind >= total_len:
                raise IndexError('index out of bounds')
            ind = ind % total_len
            root = np.int32(0)
            tag = np.int32(11)
            send_arr = np.zeros(1, dlk__kgfk)
            if arr_start <= ind < arr_start + len(arr):
                cxhqz__xpxnk = (bodo.hiframes.pd_categorical_ext.
                    get_categorical_arr_codes(arr))
                data = cxhqz__xpxnk[ind - arr_start]
                send_arr = np.full(1, data, dlk__kgfk)
                isend(send_arr, np.int32(1), root, tag, True)
            rank = bodo.libs.distributed_api.get_rank()
            val = dlk__kgfk(-1)
            if rank == root:
                val = recv(dlk__kgfk, ANY_SOURCE, tag)
            dummy_use(send_arr)
            val = bcast_scalar(val)
            imd__gyvl = arr.dtype.categories[max(val, 0)]
            return imd__gyvl
        return cat_getitem_impl
    bqzs__cjydp = arr.dtype

    def getitem_impl(arr, ind, arr_start, total_len, is_1D):
        if ind >= total_len:
            raise IndexError('index out of bounds')
        ind = ind % total_len
        root = np.int32(0)
        tag = np.int32(11)
        send_arr = np.zeros(1, bqzs__cjydp)
        if arr_start <= ind < arr_start + len(arr):
            data = arr[ind - arr_start]
            send_arr = np.full(1, data)
            isend(send_arr, np.int32(1), root, tag, True)
        rank = bodo.libs.distributed_api.get_rank()
        val = np.zeros(1, bqzs__cjydp)[0]
        if rank == root:
            val = recv(bqzs__cjydp, ANY_SOURCE, tag)
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
    gro__ydv = get_type_enum(out_data)
    assert typ_enum == gro__ydv
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
    tnli__sosv = (
        'def f(send_data, out_data, send_counts, recv_counts, send_disp, recv_disp):\n'
        )
    for i in range(count):
        tnli__sosv += (
            """  alltoallv(send_data[{}], out_data[{}], send_counts, recv_counts, send_disp, recv_disp)
"""
            .format(i, i))
    tnli__sosv += '  return\n'
    efp__zomnl = {}
    exec(tnli__sosv, {'alltoallv': alltoallv}, efp__zomnl)
    lvmm__blg = efp__zomnl['f']
    return lvmm__blg


@numba.njit
def get_start_count(n):
    rank = bodo.libs.distributed_api.get_rank()
    n_pes = bodo.libs.distributed_api.get_size()
    ogwwg__slzv = bodo.libs.distributed_api.get_start(n, n_pes, rank)
    count = bodo.libs.distributed_api.get_node_portion(n, n_pes, rank)
    return ogwwg__slzv, count


@numba.njit
def get_start(total_size, pes, rank):
    ziv__vjn = total_size % pes
    cqv__jpiz = (total_size - ziv__vjn) // pes
    return rank * cqv__jpiz + min(rank, ziv__vjn)


@numba.njit
def get_end(total_size, pes, rank):
    ziv__vjn = total_size % pes
    cqv__jpiz = (total_size - ziv__vjn) // pes
    return (rank + 1) * cqv__jpiz + min(rank + 1, ziv__vjn)


@numba.njit
def get_node_portion(total_size, pes, rank):
    ziv__vjn = total_size % pes
    cqv__jpiz = (total_size - ziv__vjn) // pes
    if rank < ziv__vjn:
        return cqv__jpiz + 1
    else:
        return cqv__jpiz


@numba.generated_jit(nopython=True)
def dist_cumsum(in_arr, out_arr):
    qoi__ezq = in_arr.dtype(0)
    zrpe__rug = np.int32(Reduce_Type.Sum.value)

    def cumsum_impl(in_arr, out_arr):
        btoko__zmsnc = qoi__ezq
        for zyo__ybwo in np.nditer(in_arr):
            btoko__zmsnc += zyo__ybwo.item()
        ung__vyn = dist_exscan(btoko__zmsnc, zrpe__rug)
        for i in range(in_arr.size):
            ung__vyn += in_arr[i]
            out_arr[i] = ung__vyn
        return 0
    return cumsum_impl


@numba.generated_jit(nopython=True)
def dist_cumprod(in_arr, out_arr):
    juciw__sfx = in_arr.dtype(1)
    zrpe__rug = np.int32(Reduce_Type.Prod.value)

    def cumprod_impl(in_arr, out_arr):
        btoko__zmsnc = juciw__sfx
        for zyo__ybwo in np.nditer(in_arr):
            btoko__zmsnc *= zyo__ybwo.item()
        ung__vyn = dist_exscan(btoko__zmsnc, zrpe__rug)
        if get_rank() == 0:
            ung__vyn = juciw__sfx
        for i in range(in_arr.size):
            ung__vyn *= in_arr[i]
            out_arr[i] = ung__vyn
        return 0
    return cumprod_impl


@numba.generated_jit(nopython=True)
def dist_cummin(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        juciw__sfx = np.finfo(in_arr.dtype(1).dtype).max
    else:
        juciw__sfx = np.iinfo(in_arr.dtype(1).dtype).max
    zrpe__rug = np.int32(Reduce_Type.Min.value)

    def cummin_impl(in_arr, out_arr):
        btoko__zmsnc = juciw__sfx
        for zyo__ybwo in np.nditer(in_arr):
            btoko__zmsnc = min(btoko__zmsnc, zyo__ybwo.item())
        ung__vyn = dist_exscan(btoko__zmsnc, zrpe__rug)
        if get_rank() == 0:
            ung__vyn = juciw__sfx
        for i in range(in_arr.size):
            ung__vyn = min(ung__vyn, in_arr[i])
            out_arr[i] = ung__vyn
        return 0
    return cummin_impl


@numba.generated_jit(nopython=True)
def dist_cummax(in_arr, out_arr):
    if isinstance(in_arr.dtype, types.Float):
        juciw__sfx = np.finfo(in_arr.dtype(1).dtype).min
    else:
        juciw__sfx = np.iinfo(in_arr.dtype(1).dtype).min
    juciw__sfx = in_arr.dtype(1)
    zrpe__rug = np.int32(Reduce_Type.Max.value)

    def cummax_impl(in_arr, out_arr):
        btoko__zmsnc = juciw__sfx
        for zyo__ybwo in np.nditer(in_arr):
            btoko__zmsnc = max(btoko__zmsnc, zyo__ybwo.item())
        ung__vyn = dist_exscan(btoko__zmsnc, zrpe__rug)
        if get_rank() == 0:
            ung__vyn = juciw__sfx
        for i in range(in_arr.size):
            ung__vyn = max(ung__vyn, in_arr[i])
            out_arr[i] = ung__vyn
        return 0
    return cummax_impl


_allgather = types.ExternalFunction('allgather', types.void(types.voidptr,
    types.int32, types.voidptr, types.int32))


@numba.njit
def allgather(arr, val):
    argim__gdh = get_type_enum(arr)
    _allgather(arr.ctypes, 1, value_to_ptr(val), argim__gdh)


def dist_return(A):
    return A


def rep_return(A):
    return A


def dist_return_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    tev__kaqk = args[0]
    if equiv_set.has_shape(tev__kaqk):
        return ArrayAnalysis.AnalyzeResult(shape=tev__kaqk, pre=[])
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
    ldx__whblr = '(' + ' or '.join(['False'] + [f'len(args[{i}]) != 0' for 
        i, qqam__skj in enumerate(args) if is_array_typ(qqam__skj) or
        isinstance(qqam__skj, bodo.hiframes.pd_dataframe_ext.DataFrameType)]
        ) + ')'
    tnli__sosv = f"""def impl(*args):
    if {ldx__whblr} or bodo.get_rank() == 0:
        print(*args)"""
    efp__zomnl = {}
    exec(tnli__sosv, globals(), efp__zomnl)
    impl = efp__zomnl['impl']
    return impl


_wait = types.ExternalFunction('dist_wait', types.void(mpi_req_numba_type,
    types.bool_))


@numba.generated_jit(nopython=True)
def wait(req, cond=True):
    if isinstance(req, types.BaseTuple):
        count = len(req.types)
        ssc__fdktm = ','.join(f'_wait(req[{i}], cond)' for i in range(count))
        tnli__sosv = 'def f(req, cond=True):\n'
        tnli__sosv += f'  return {ssc__fdktm}\n'
        efp__zomnl = {}
        exec(tnli__sosv, {'_wait': _wait}, efp__zomnl)
        impl = efp__zomnl['f']
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
        ziv__vjn = 1
        for a in t:
            ziv__vjn *= a
        return ziv__vjn
    return get_tuple_prod_impl


sig = types.void(types.voidptr, types.voidptr, types.intp, types.intp,
    types.intp, types.intp, types.int32, types.voidptr)
oneD_reshape_shuffle = types.ExternalFunction('oneD_reshape_shuffle', sig)


@numba.njit(no_cpython_wrapper=True, cache=True)
def dist_oneD_reshape_shuffle(lhs, in_arr, new_dim0_global_len, dest_ranks=None
    ):
    txemj__gwys = np.ascontiguousarray(in_arr)
    tjm__bzvvd = get_tuple_prod(txemj__gwys.shape[1:])
    rupv__dkbl = get_tuple_prod(lhs.shape[1:])
    if dest_ranks is not None:
        kojai__gbzv = np.array(dest_ranks, dtype=np.int32)
    else:
        kojai__gbzv = np.empty(0, dtype=np.int32)
    dtype_size = bodo.io.np_io.get_dtype_size(in_arr.dtype)
    oneD_reshape_shuffle(lhs.ctypes, txemj__gwys.ctypes,
        new_dim0_global_len, len(in_arr), dtype_size * rupv__dkbl, 
        dtype_size * tjm__bzvvd, len(kojai__gbzv), kojai__gbzv.ctypes)
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
    zczf__rsz = np.ascontiguousarray(rhs)
    aff__mgjsf = get_tuple_prod(zczf__rsz.shape[1:])
    bdfte__pjqtj = dtype_size * aff__mgjsf
    permutation_array_index(lhs.ctypes, lhs_len, bdfte__pjqtj, zczf__rsz.
        ctypes, zczf__rsz.shape[0], p.ctypes, p_len, n_samples)
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
        tnli__sosv = (
            f"""def bcast_scalar_impl(data, comm_ranks, nranks, root={MPI_ROOT}):
  send = np.empty(1, dtype)
  send[0] = data
  c_bcast(send.ctypes, np.int32(1), np.int32({{}}), comm_ranks,ctypes, np.int32({{}}), np.int32(root))
  return send[0]
"""
            .format(typ_val, nranks))
        dtype = numba.np.numpy_support.as_dtype(data)
        efp__zomnl = {}
        exec(tnli__sosv, {'bodo': bodo, 'np': np, 'c_bcast': c_bcast,
            'dtype': dtype}, efp__zomnl)
        qmp__ocxgv = efp__zomnl['bcast_scalar_impl']
        return qmp__ocxgv
    if isinstance(data, types.Array):
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: _bcast_np(data,
            comm_ranks, nranks, root)
    if isinstance(data, bodo.hiframes.pd_dataframe_ext.DataFrameType):
        yzswv__bxvqu = len(data.columns)
        yys__pdr = ', '.join('g_data_{}'.format(i) for i in range(yzswv__bxvqu)
            )
        eym__xnei = ColNamesMetaType(data.columns)
        tnli__sosv = (
            f'def impl_df(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        for i in range(yzswv__bxvqu):
            tnli__sosv += (
                """  data_{} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {})
"""
                .format(i, i))
            tnli__sosv += (
                """  g_data_{} = bodo.libs.distributed_api.bcast_comm_impl(data_{}, comm_ranks, nranks, root)
"""
                .format(i, i))
        tnli__sosv += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)\n'
            )
        tnli__sosv += """  g_index = bodo.libs.distributed_api.bcast_comm_impl(index, comm_ranks, nranks, root)
"""
        tnli__sosv += (
            """  return bodo.hiframes.pd_dataframe_ext.init_dataframe(({},), g_index, __col_name_meta_value_bcast_comm)
"""
            .format(yys__pdr))
        efp__zomnl = {}
        exec(tnli__sosv, {'bodo': bodo, '__col_name_meta_value_bcast_comm':
            eym__xnei}, efp__zomnl)
        dzgs__obmv = efp__zomnl['impl_df']
        return dzgs__obmv
    if isinstance(data, bodo.hiframes.pd_index_ext.RangeIndexType):

        def impl_range_index(data, comm_ranks, nranks, root=MPI_ROOT):
            rank = bodo.libs.distributed_api.get_rank()
            n_pes = bodo.libs.distributed_api.get_size()
            ogwwg__slzv = data._start
            bmu__eqhp = data._stop
            cfvch__xnwr = data._step
            zqe__vwd = data._name
            zqe__vwd = bcast_scalar(zqe__vwd, root)
            ogwwg__slzv = bcast_scalar(ogwwg__slzv, root)
            bmu__eqhp = bcast_scalar(bmu__eqhp, root)
            cfvch__xnwr = bcast_scalar(cfvch__xnwr, root)
            mlxyv__pguxi = bodo.libs.array_kernels.calc_nitems(ogwwg__slzv,
                bmu__eqhp, cfvch__xnwr)
            chunk_start = bodo.libs.distributed_api.get_start(mlxyv__pguxi,
                n_pes, rank)
            hsyvr__ovu = bodo.libs.distributed_api.get_node_portion(
                mlxyv__pguxi, n_pes, rank)
            vzhru__lwcdm = ogwwg__slzv + cfvch__xnwr * chunk_start
            hvor__uxwas = ogwwg__slzv + cfvch__xnwr * (chunk_start + hsyvr__ovu
                )
            hvor__uxwas = min(hvor__uxwas, bmu__eqhp)
            return bodo.hiframes.pd_index_ext.init_range_index(vzhru__lwcdm,
                hvor__uxwas, cfvch__xnwr, zqe__vwd)
        return impl_range_index
    if bodo.hiframes.pd_index_ext.is_pd_index_type(data):

        def impl_pd_index(data, comm_ranks, nranks, root=MPI_ROOT):
            tofs__rdmmd = data._data
            zqe__vwd = data._name
            arr = bodo.libs.distributed_api.bcast_comm_impl(tofs__rdmmd,
                comm_ranks, nranks, root)
            return bodo.utils.conversion.index_from_array(arr, zqe__vwd)
        return impl_pd_index
    if isinstance(data, bodo.hiframes.pd_series_ext.SeriesType):

        def impl_series(data, comm_ranks, nranks, root=MPI_ROOT):
            arr = bodo.hiframes.pd_series_ext.get_series_data(data)
            index = bodo.hiframes.pd_series_ext.get_series_index(data)
            zqe__vwd = bodo.hiframes.pd_series_ext.get_series_name(data)
            pjw__ypq = bodo.libs.distributed_api.bcast_comm_impl(zqe__vwd,
                comm_ranks, nranks, root)
            out_arr = bodo.libs.distributed_api.bcast_comm_impl(arr,
                comm_ranks, nranks, root)
            bex__uwxf = bodo.libs.distributed_api.bcast_comm_impl(index,
                comm_ranks, nranks, root)
            return bodo.hiframes.pd_series_ext.init_series(out_arr,
                bex__uwxf, pjw__ypq)
        return impl_series
    if isinstance(data, types.BaseTuple):
        tnli__sosv = (
            f'def impl_tuple(data, comm_ranks, nranks, root={MPI_ROOT}):\n')
        tnli__sosv += '  return ({}{})\n'.format(', '.join(
            'bcast_comm_impl(data[{}], comm_ranks, nranks, root)'.format(i) for
            i in range(len(data))), ',' if len(data) > 0 else '')
        efp__zomnl = {}
        exec(tnli__sosv, {'bcast_comm_impl': bcast_comm_impl}, efp__zomnl)
        crlac__hzahh = efp__zomnl['impl_tuple']
        return crlac__hzahh
    if data is types.none:
        return lambda data, comm_ranks, nranks, root=MPI_ROOT: None


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _bcast_np(data, comm_ranks, nranks, root=MPI_ROOT):
    typ_val = numba_to_c_type(data.dtype)
    ecqq__ylrk = data.ndim
    dtype = data.dtype
    if dtype == types.NPDatetime('ns'):
        dtype = np.dtype('datetime64[ns]')
    elif dtype == types.NPTimedelta('ns'):
        dtype = np.dtype('timedelta64[ns]')
    plhe__tadxc = (0,) * ecqq__ylrk

    def bcast_arr_impl(data, comm_ranks, nranks, root=MPI_ROOT):
        rank = bodo.libs.distributed_api.get_rank()
        tofs__rdmmd = np.ascontiguousarray(data)
        eequs__ppvjn = data.ctypes
        tixuy__ikczt = plhe__tadxc
        if rank == root:
            tixuy__ikczt = tofs__rdmmd.shape
        tixuy__ikczt = bcast_tuple(tixuy__ikczt, root)
        lbodg__njdtc = get_tuple_prod(tixuy__ikczt[1:])
        send_counts = tixuy__ikczt[0] * lbodg__njdtc
        vbu__wyjl = np.empty(send_counts, dtype)
        if rank == MPI_ROOT:
            c_bcast(eequs__ppvjn, np.int32(send_counts), np.int32(typ_val),
                comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return data
        else:
            c_bcast(vbu__wyjl.ctypes, np.int32(send_counts), np.int32(
                typ_val), comm_ranks.ctypes, np.int32(nranks), np.int32(root))
            return vbu__wyjl.reshape((-1,) + tixuy__ikczt[1:])
    return bcast_arr_impl


node_ranks = None


def get_host_ranks():
    global node_ranks
    if node_ranks is None:
        cvgy__lwc = MPI.COMM_WORLD
        qbj__ohipw = MPI.Get_processor_name()
        kbyl__owcp = cvgy__lwc.allgather(qbj__ohipw)
        node_ranks = defaultdict(list)
        for i, afcex__jwvcm in enumerate(kbyl__owcp):
            node_ranks[afcex__jwvcm].append(i)
    return node_ranks


def create_subcomm_mpi4py(comm_ranks):
    cvgy__lwc = MPI.COMM_WORLD
    ddmbm__jjpzo = cvgy__lwc.Get_group()
    xatf__bqzaq = ddmbm__jjpzo.Incl(comm_ranks)
    kwypo__auunq = cvgy__lwc.Create_group(xatf__bqzaq)
    return kwypo__auunq


def get_nodes_first_ranks():
    cfn__zfbgs = get_host_ranks()
    return np.array([nnpx__liov[0] for nnpx__liov in cfn__zfbgs.values()],
        dtype='int32')


def get_num_nodes():
    return len(get_host_ranks())
