"""Array implementation for binary (bytes) objects, which are usually immutable.
It is equivalent to string array, except that it stores a 'bytes' object for each
element instead of 'str'.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, overload, overload_attribute, overload_method
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.utils.typing import BodoError, is_list_like_index_type
_bytes_fromhex = types.ExternalFunction('bytes_fromhex', types.int64(types.
    voidptr, types.voidptr, types.uint64))
ll.add_symbol('bytes_to_hex', hstr_ext.bytes_to_hex)
ll.add_symbol('bytes_fromhex', hstr_ext.bytes_fromhex)
bytes_type = types.Bytes(types.uint8, 1, 'C', readonly=True)


class BinaryArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(BinaryArrayType, self).__init__(name='BinaryArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return bytes_type

    def copy(self):
        return BinaryArrayType()

    @property
    def iterator_type(self):
        return bodo.utils.typing.BodoArrayIterator(self)


binary_array_type = BinaryArrayType()


@overload(len, no_unliteral=True)
def bin_arr_len_overload(bin_arr):
    if bin_arr == binary_array_type:
        return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'size')
def bin_arr_size_overload(bin_arr):
    return lambda bin_arr: len(bin_arr._data)


@overload_attribute(BinaryArrayType, 'shape')
def bin_arr_shape_overload(bin_arr):
    return lambda bin_arr: (len(bin_arr._data),)


@overload_attribute(BinaryArrayType, 'nbytes')
def bin_arr_nbytes_overload(bin_arr):
    return lambda bin_arr: bin_arr._data.nbytes


@overload_attribute(BinaryArrayType, 'ndim')
def overload_bin_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BinaryArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: np.dtype('O')


@numba.njit
def pre_alloc_binary_array(n_bytestrs, n_chars):
    if n_chars is None:
        n_chars = -1
    bin_arr = init_binary_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_bytestrs), (np.int64(n_chars)
        ,), bodo.libs.str_arr_ext.char_arr_type))
    if n_chars == 0:
        bodo.libs.str_arr_ext.set_all_offsets_to_0(bin_arr)
    return bin_arr


@intrinsic
def init_binary_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, sig, args):
        ztwjl__hylrs, = args
        qwl__omhpu = context.make_helper(builder, binary_array_type)
        qwl__omhpu.data = ztwjl__hylrs
        context.nrt.incref(builder, data_typ, ztwjl__hylrs)
        return qwl__omhpu._getvalue()
    return binary_array_type(data_typ), codegen


@intrinsic
def init_bytes_type(typingctx, data_typ, length_type):
    assert data_typ == types.Array(types.uint8, 1, 'C')
    assert length_type == types.int64

    def codegen(context, builder, sig, args):
        rhpxr__houw = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        ali__eicr = args[1]
        nuftb__pvp = cgutils.create_struct_proxy(bytes_type)(context, builder)
        nuftb__pvp.meminfo = context.nrt.meminfo_alloc(builder, ali__eicr)
        nuftb__pvp.nitems = ali__eicr
        nuftb__pvp.itemsize = lir.Constant(nuftb__pvp.itemsize.type, 1)
        nuftb__pvp.data = context.nrt.meminfo_data(builder, nuftb__pvp.meminfo)
        nuftb__pvp.parent = cgutils.get_null_value(nuftb__pvp.parent.type)
        nuftb__pvp.shape = cgutils.pack_array(builder, [ali__eicr], context
            .get_value_type(types.intp))
        nuftb__pvp.strides = rhpxr__houw.strides
        cgutils.memcpy(builder, nuftb__pvp.data, rhpxr__houw.data, ali__eicr)
        return nuftb__pvp._getvalue()
    return bytes_type(data_typ, length_type), codegen


@intrinsic
def cast_bytes_uint8array(typingctx, data_typ):
    assert data_typ == bytes_type

    def codegen(context, builder, sig, args):
        return impl_ret_borrowed(context, builder, sig.return_type, args[0])
    return types.Array(types.uint8, 1, 'C')(data_typ), codegen


@overload_method(BinaryArrayType, 'copy', no_unliteral=True)
def binary_arr_copy_overload(arr):

    def copy_impl(arr):
        return init_binary_arr(arr._data.copy())
    return copy_impl


@overload_method(types.Bytes, 'hex')
def binary_arr_hex(arr):
    pld__aquoz = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

    def impl(arr):
        ali__eicr = len(arr) * 2
        output = numba.cpython.unicode._empty_string(pld__aquoz, ali__eicr, 1)
        bytes_to_hex(output, arr)
        return output
    return impl


@lower_cast(types.CPointer(types.uint8), types.voidptr)
def cast_uint8_array_to_voidptr(context, builder, fromty, toty, val):
    return val


make_attribute_wrapper(types.Bytes, 'data', '_data')


@overload_method(types.Bytes, '__hash__')
def bytes_hash(arr):

    def impl(arr):
        return numba.cpython.hashing._Py_HashBytes(arr._data, len(arr))
    return impl


@intrinsic
def bytes_to_hex(typingctx, output, arr):

    def codegen(context, builder, sig, args):
        hfzp__ntgkh = cgutils.create_struct_proxy(sig.args[0])(context,
            builder, value=args[0])
        escjt__yrzt = cgutils.create_struct_proxy(sig.args[1])(context,
            builder, value=args[1])
        wdnh__mywwn = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(64)])
        ieiti__udi = cgutils.get_or_insert_function(builder.module,
            wdnh__mywwn, name='bytes_to_hex')
        builder.call(ieiti__udi, (hfzp__ntgkh.data, escjt__yrzt.data,
            escjt__yrzt.nitems))
    return types.void(output, arr), codegen


@overload(operator.getitem, no_unliteral=True)
def binary_arr_getitem(arr, ind):
    if arr != binary_array_type:
        return
    if isinstance(ind, types.Integer):

        def impl(arr, ind):
            rmyu__pqeuz = arr._data[ind]
            return init_bytes_type(rmyu__pqeuz, len(rmyu__pqeuz))
        return impl
    if is_list_like_index_type(ind) and (ind.dtype == types.bool_ or
        isinstance(ind.dtype, types.Integer)) or isinstance(ind, types.
        SliceType):
        return lambda arr, ind: init_binary_arr(arr._data[ind])
    raise BodoError(
        f'getitem for Binary Array with indexing type {ind} not supported.')


def bytes_fromhex(hex_str):
    pass


@overload(bytes_fromhex)
def overload_bytes_fromhex(hex_str):
    hex_str = types.unliteral(hex_str)
    if hex_str == bodo.string_type:
        pld__aquoz = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def impl(hex_str):
            if not hex_str._is_ascii or hex_str._kind != pld__aquoz:
                raise TypeError(
                    'bytes.fromhex is only supported on ascii strings')
            ztwjl__hylrs = np.empty(len(hex_str) // 2, np.uint8)
            ali__eicr = _bytes_fromhex(ztwjl__hylrs.ctypes, hex_str._data,
                len(hex_str))
            razhg__vlts = init_bytes_type(ztwjl__hylrs, ali__eicr)
            return razhg__vlts
        return impl
    raise BodoError(f'bytes.fromhex not supported with argument type {hex_str}'
        )


@overload(operator.setitem)
def binary_arr_setitem(arr, ind, val):
    if arr != binary_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if val != bytes_type:
        raise BodoError(
            f'setitem for Binary Array only supported with bytes value and integer indexing'
            )
    if isinstance(ind, types.Integer):

        def impl(arr, ind, val):
            arr._data[ind] = bodo.libs.binary_arr_ext.cast_bytes_uint8array(val
                )
        return impl
    raise BodoError(
        f'setitem for Binary Array with indexing type {ind} not supported.')


def create_binary_cmp_op_overload(op):

    def overload_binary_cmp(lhs, rhs):
        ulagk__smdj = lhs == binary_array_type
        hoy__tyb = rhs == binary_array_type
        ovqys__vptx = 'lhs' if ulagk__smdj else 'rhs'
        qlt__xzcn = 'def impl(lhs, rhs):\n'
        qlt__xzcn += '  numba.parfors.parfor.init_prange()\n'
        qlt__xzcn += f'  n = len({ovqys__vptx})\n'
        qlt__xzcn += '  out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(n)\n'
        qlt__xzcn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        eapj__comg = []
        if ulagk__smdj:
            eapj__comg.append('bodo.libs.array_kernels.isna(lhs, i)')
        if hoy__tyb:
            eapj__comg.append('bodo.libs.array_kernels.isna(rhs, i)')
        qlt__xzcn += f"    if {' or '.join(eapj__comg)}:\n"
        qlt__xzcn += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        qlt__xzcn += '      continue\n'
        bpwx__akq = 'lhs[i]' if ulagk__smdj else 'lhs'
        iosa__zdxqo = 'rhs[i]' if hoy__tyb else 'rhs'
        qlt__xzcn += f'    out_arr[i] = op({bpwx__akq}, {iosa__zdxqo})\n'
        qlt__xzcn += '  return out_arr\n'
        sbm__dxynw = {}
        exec(qlt__xzcn, {'bodo': bodo, 'numba': numba, 'op': op}, sbm__dxynw)
        return sbm__dxynw['impl']
    return overload_binary_cmp


lower_builtin('getiter', binary_array_type)(numba.np.arrayobj.getiter_array)


def pre_alloc_binary_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_binary_arr_ext_pre_alloc_binary_array
    ) = pre_alloc_binary_arr_equiv
