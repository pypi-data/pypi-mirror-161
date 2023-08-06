"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoArrayIterator, BodoError, decode_if_dict_array, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, is_str_arr_type, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return BodoArrayIterator(self)

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        wbi__exrqr = ArrayItemArrayType(char_arr_type)
        krdn__rsr = [('data', wbi__exrqr)]
        models.StructModel.__init__(self, dmm, fe_type, krdn__rsr)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        yopw__jghd, = args
        huo__avlb = context.make_helper(builder, string_array_type)
        huo__avlb.data = yopw__jghd
        context.nrt.incref(builder, data_typ, yopw__jghd)
        return huo__avlb._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    pbb__afhe = c.context.insert_const_string(c.builder.module, 'pandas')
    evzk__wyc = c.pyapi.import_module_noblock(pbb__afhe)
    vuf__zfryn = c.pyapi.call_method(evzk__wyc, 'StringDtype', ())
    c.pyapi.decref(evzk__wyc)
    return vuf__zfryn


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        aiiat__nqw = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs
            )
        if aiiat__nqw is not None:
            return aiiat__nqw
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qqfm__yhh = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(qqfm__yhh)
                for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qqfm__yhh = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(qqfm__yhh)
                for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                qqfm__yhh = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(qqfm__yhh)
                for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise_bodo_error(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    tjzrl__nmwvz = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    xgw__fga = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and xgw__fga or tjzrl__nmwvz and is_str_arr_type(
        rhs):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j
                    ) or bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs[j]
            return out_arr
        return impl_both
    if is_str_arr_type(lhs) and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and is_str_arr_type(rhs):

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs + rhs[j]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if is_str_arr_type(lhs) and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and is_str_arr_type(rhs):

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    agqx__yktlt = context.make_helper(builder, arr_typ, arr_value)
    wbi__exrqr = ArrayItemArrayType(char_arr_type)
    uucx__bho = _get_array_item_arr_payload(context, builder, wbi__exrqr,
        agqx__yktlt.data)
    return uucx__bho


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return uucx__bho.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kgf__iog = context.make_helper(builder, offset_arr_type, uucx__bho.
            offsets).data
        return _get_num_total_chars(builder, kgf__iog, uucx__bho.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        daxun__ajmnq = context.make_helper(builder, offset_arr_type,
            uucx__bho.offsets)
        icbm__hfpe = context.make_helper(builder, offset_ctypes_type)
        icbm__hfpe.data = builder.bitcast(daxun__ajmnq.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        icbm__hfpe.meminfo = daxun__ajmnq.meminfo
        vuf__zfryn = icbm__hfpe._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            vuf__zfryn)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        yopw__jghd = context.make_helper(builder, char_arr_type, uucx__bho.data
            )
        icbm__hfpe = context.make_helper(builder, data_ctypes_type)
        icbm__hfpe.data = yopw__jghd.data
        icbm__hfpe.meminfo = yopw__jghd.meminfo
        vuf__zfryn = icbm__hfpe._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, vuf__zfryn
            )
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        vkbkb__wmt, ind = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            vkbkb__wmt, sig.args[0])
        yopw__jghd = context.make_helper(builder, char_arr_type, uucx__bho.data
            )
        icbm__hfpe = context.make_helper(builder, data_ctypes_type)
        icbm__hfpe.data = builder.gep(yopw__jghd.data, [ind])
        icbm__hfpe.meminfo = yopw__jghd.meminfo
        vuf__zfryn = icbm__hfpe._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, vuf__zfryn
            )
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        jjwpw__scjr, vlylw__sgi, aihb__wlme, qna__osj = args
        urze__uwv = builder.bitcast(builder.gep(jjwpw__scjr, [vlylw__sgi]),
            lir.IntType(8).as_pointer())
        hee__qei = builder.bitcast(builder.gep(aihb__wlme, [qna__osj]), lir
            .IntType(8).as_pointer())
        csrad__drjzz = builder.load(hee__qei)
        builder.store(csrad__drjzz, urze__uwv)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qxlsj__uevpr = context.make_helper(builder, null_bitmap_arr_type,
            uucx__bho.null_bitmap)
        icbm__hfpe = context.make_helper(builder, data_ctypes_type)
        icbm__hfpe.data = qxlsj__uevpr.data
        icbm__hfpe.meminfo = qxlsj__uevpr.meminfo
        vuf__zfryn = icbm__hfpe._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, vuf__zfryn
            )
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kgf__iog = context.make_helper(builder, offset_arr_type, uucx__bho.
            offsets).data
        return builder.load(builder.gep(kgf__iog, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, uucx__bho.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        nxzn__ccd, ind = args
        if in_bitmap_typ == data_ctypes_type:
            icbm__hfpe = context.make_helper(builder, data_ctypes_type,
                nxzn__ccd)
            nxzn__ccd = icbm__hfpe.data
        return builder.load(builder.gep(nxzn__ccd, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        nxzn__ccd, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            icbm__hfpe = context.make_helper(builder, data_ctypes_type,
                nxzn__ccd)
            nxzn__ccd = icbm__hfpe.data
        builder.store(val, builder.gep(nxzn__ccd, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        qhu__jchue = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        wok__mvnvu = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        ibek__cchov = context.make_helper(builder, offset_arr_type,
            qhu__jchue.offsets).data
        jwa__wvfj = context.make_helper(builder, offset_arr_type,
            wok__mvnvu.offsets).data
        nfm__ixol = context.make_helper(builder, char_arr_type, qhu__jchue.data
            ).data
        iut__nigx = context.make_helper(builder, char_arr_type, wok__mvnvu.data
            ).data
        pyfwr__yswmy = context.make_helper(builder, null_bitmap_arr_type,
            qhu__jchue.null_bitmap).data
        isz__boyzc = context.make_helper(builder, null_bitmap_arr_type,
            wok__mvnvu.null_bitmap).data
        ikkcp__qca = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, jwa__wvfj, ibek__cchov, ikkcp__qca)
        cgutils.memcpy(builder, iut__nigx, nfm__ixol, builder.load(builder.
            gep(ibek__cchov, [ind])))
        nlcp__vtn = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        pknt__ycavn = builder.lshr(nlcp__vtn, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, isz__boyzc, pyfwr__yswmy, pknt__ycavn)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        qhu__jchue = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        wok__mvnvu = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        ibek__cchov = context.make_helper(builder, offset_arr_type,
            qhu__jchue.offsets).data
        nfm__ixol = context.make_helper(builder, char_arr_type, qhu__jchue.data
            ).data
        iut__nigx = context.make_helper(builder, char_arr_type, wok__mvnvu.data
            ).data
        num_total_chars = _get_num_total_chars(builder, ibek__cchov,
            qhu__jchue.n_arrays)
        cgutils.memcpy(builder, iut__nigx, nfm__ixol, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        qhu__jchue = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        wok__mvnvu = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        ibek__cchov = context.make_helper(builder, offset_arr_type,
            qhu__jchue.offsets).data
        jwa__wvfj = context.make_helper(builder, offset_arr_type,
            wok__mvnvu.offsets).data
        pyfwr__yswmy = context.make_helper(builder, null_bitmap_arr_type,
            qhu__jchue.null_bitmap).data
        qqfm__yhh = qhu__jchue.n_arrays
        vwxo__xsdi = context.get_constant(offset_type, 0)
        lmu__zgyi = cgutils.alloca_once_value(builder, vwxo__xsdi)
        with cgutils.for_range(builder, qqfm__yhh) as najf__kgn:
            rekc__qff = lower_is_na(context, builder, pyfwr__yswmy,
                najf__kgn.index)
            with cgutils.if_likely(builder, builder.not_(rekc__qff)):
                pakxz__kgcmb = builder.load(builder.gep(ibek__cchov, [
                    najf__kgn.index]))
                nonz__ccdi = builder.load(lmu__zgyi)
                builder.store(pakxz__kgcmb, builder.gep(jwa__wvfj, [
                    nonz__ccdi]))
                builder.store(builder.add(nonz__ccdi, lir.Constant(context.
                    get_value_type(offset_type), 1)), lmu__zgyi)
        nonz__ccdi = builder.load(lmu__zgyi)
        pakxz__kgcmb = builder.load(builder.gep(ibek__cchov, [qqfm__yhh]))
        builder.store(pakxz__kgcmb, builder.gep(jwa__wvfj, [nonz__ccdi]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        yghp__xxeee, ind, str, ddpjt__yvvtu = args
        yghp__xxeee = context.make_array(sig.args[0])(context, builder,
            yghp__xxeee)
        nzyt__fvv = builder.gep(yghp__xxeee.data, [ind])
        cgutils.raw_memcpy(builder, nzyt__fvv, str, ddpjt__yvvtu, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        nzyt__fvv, ind, onhf__iolw, ddpjt__yvvtu = args
        nzyt__fvv = builder.gep(nzyt__fvv, [ind])
        cgutils.raw_memcpy(builder, nzyt__fvv, onhf__iolw, ddpjt__yvvtu, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            tkabi__jyxqo = A._data
            return np.int64(getitem_str_offset(tkabi__jyxqo, idx + 1) -
                getitem_str_offset(tkabi__jyxqo, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    yfdwq__ckk = np.int64(getitem_str_offset(A, i))
    vby__hun = np.int64(getitem_str_offset(A, i + 1))
    l = vby__hun - yfdwq__ckk
    esgx__twip = get_data_ptr_ind(A, yfdwq__ckk)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(esgx__twip, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    gmdsh__gypg = getitem_str_offset(A, i)
    bvz__zhkmz = getitem_str_offset(A, i + 1)
    dhzu__ehp = bvz__zhkmz - gmdsh__gypg
    lct__suh = getitem_str_offset(B, j)
    ktmot__rtod = lct__suh + dhzu__ehp
    setitem_str_offset(B, j + 1, ktmot__rtod)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if dhzu__ehp != 0:
        yopw__jghd = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(yopw__jghd, np.
            int64(lct__suh), np.int64(ktmot__rtod))
        nay__udkhy = get_data_ptr(B).data
        ywv__zytm = get_data_ptr(A).data
        memcpy_region(nay__udkhy, lct__suh, ywv__zytm, gmdsh__gypg,
            dhzu__ehp, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    qqfm__yhh = len(str_arr)
    jzdog__efqrs = np.empty(qqfm__yhh, np.bool_)
    for i in range(qqfm__yhh):
        jzdog__efqrs[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return jzdog__efqrs


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            qqfm__yhh = len(data)
            l = []
            for i in range(qqfm__yhh):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        ium__xxofc = data.count
        oskkk__rjc = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(ium__xxofc)]
        if is_overload_true(str_null_bools):
            oskkk__rjc += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(ium__xxofc) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        hka__hchm = 'def f(data, str_null_bools=None):\n'
        hka__hchm += '  return ({}{})\n'.format(', '.join(oskkk__rjc), ',' if
            ium__xxofc == 1 else '')
        jxaz__kdgpa = {}
        exec(hka__hchm, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, jxaz__kdgpa)
        uqt__xiqky = jxaz__kdgpa['f']
        return uqt__xiqky
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                qqfm__yhh = len(list_data)
                for i in range(qqfm__yhh):
                    onhf__iolw = list_data[i]
                    str_arr[i] = onhf__iolw
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                qqfm__yhh = len(list_data)
                for i in range(qqfm__yhh):
                    onhf__iolw = list_data[i]
                    str_arr[i] = onhf__iolw
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        ium__xxofc = str_arr.count
        pmha__ybrmq = 0
        hka__hchm = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(ium__xxofc):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                hka__hchm += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, ium__xxofc + pmha__ybrmq))
                pmha__ybrmq += 1
            else:
                hka__hchm += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        hka__hchm += '  return\n'
        jxaz__kdgpa = {}
        exec(hka__hchm, {'cp_str_list_to_array': cp_str_list_to_array},
            jxaz__kdgpa)
        bqh__ozda = jxaz__kdgpa['f']
        return bqh__ozda
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            qqfm__yhh = len(str_list)
            str_arr = pre_alloc_string_array(qqfm__yhh, -1)
            for i in range(qqfm__yhh):
                onhf__iolw = str_list[i]
                str_arr[i] = onhf__iolw
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            qqfm__yhh = len(A)
            tlbu__tqv = 0
            for i in range(qqfm__yhh):
                onhf__iolw = A[i]
                tlbu__tqv += get_utf8_size(onhf__iolw)
            return tlbu__tqv
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        qqfm__yhh = len(arr)
        n_chars = num_total_chars(arr)
        eld__pan = pre_alloc_string_array(qqfm__yhh, np.int64(n_chars))
        copy_str_arr_slice(eld__pan, arr, qqfm__yhh)
        return eld__pan
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    hka__hchm = 'def f(in_seq):\n'
    hka__hchm += '    n_strs = len(in_seq)\n'
    hka__hchm += '    A = pre_alloc_string_array(n_strs, -1)\n'
    hka__hchm += '    return A\n'
    jxaz__kdgpa = {}
    exec(hka__hchm, {'pre_alloc_string_array': pre_alloc_string_array},
        jxaz__kdgpa)
    kmbv__anech = jxaz__kdgpa['f']
    return kmbv__anech


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        oxtsg__jzgh = 'pre_alloc_binary_array'
    else:
        oxtsg__jzgh = 'pre_alloc_string_array'
    hka__hchm = 'def f(in_seq):\n'
    hka__hchm += '    n_strs = len(in_seq)\n'
    hka__hchm += f'    A = {oxtsg__jzgh}(n_strs, -1)\n'
    hka__hchm += '    for i in range(n_strs):\n'
    hka__hchm += '        A[i] = in_seq[i]\n'
    hka__hchm += '    return A\n'
    jxaz__kdgpa = {}
    exec(hka__hchm, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, jxaz__kdgpa)
    kmbv__anech = jxaz__kdgpa['f']
    return kmbv__anech


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xza__rvoa = builder.add(uucx__bho.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        unn__cnmjj = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        pknt__ycavn = builder.mul(xza__rvoa, unn__cnmjj)
        vfn__stmi = context.make_array(offset_arr_type)(context, builder,
            uucx__bho.offsets).data
        cgutils.memset(builder, vfn__stmi, pknt__ycavn, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kvr__hpyd = uucx__bho.n_arrays
        pknt__ycavn = builder.lshr(builder.add(kvr__hpyd, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        eqo__dbzu = context.make_array(null_bitmap_arr_type)(context,
            builder, uucx__bho.null_bitmap).data
        cgutils.memset(builder, eqo__dbzu, pknt__ycavn, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    uttek__dbka = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        agy__yqc = len(len_arr)
        for i in range(agy__yqc):
            offsets[i] = uttek__dbka
            uttek__dbka += len_arr[i]
        offsets[agy__yqc] = uttek__dbka
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    quokz__qyq = i // 8
    ktesf__cowk = getitem_str_bitmap(bits, quokz__qyq)
    ktesf__cowk ^= np.uint8(-np.uint8(bit_is_set) ^ ktesf__cowk) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, quokz__qyq, ktesf__cowk)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    wgjh__uwol = get_null_bitmap_ptr(out_str_arr)
    ksx__ltor = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        lho__fkss = get_bit_bitmap(ksx__ltor, j)
        set_bit_to(wgjh__uwol, out_start + j, lho__fkss)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, vkbkb__wmt, agt__gjve, kjor__dnem = args
        qhu__jchue = _get_str_binary_arr_payload(context, builder,
            vkbkb__wmt, string_array_type)
        wok__mvnvu = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        ibek__cchov = context.make_helper(builder, offset_arr_type,
            qhu__jchue.offsets).data
        jwa__wvfj = context.make_helper(builder, offset_arr_type,
            wok__mvnvu.offsets).data
        nfm__ixol = context.make_helper(builder, char_arr_type, qhu__jchue.data
            ).data
        iut__nigx = context.make_helper(builder, char_arr_type, wok__mvnvu.data
            ).data
        num_total_chars = _get_num_total_chars(builder, ibek__cchov,
            qhu__jchue.n_arrays)
        idkqw__zvl = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        opns__nbef = cgutils.get_or_insert_function(builder.module,
            idkqw__zvl, name='set_string_array_range')
        builder.call(opns__nbef, [jwa__wvfj, iut__nigx, ibek__cchov,
            nfm__ixol, agt__gjve, kjor__dnem, qhu__jchue.n_arrays,
            num_total_chars])
        rwdlx__tfqfh = context.typing_context.resolve_value_type(
            copy_nulls_range)
        jkcfg__lcer = rwdlx__tfqfh.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        csv__pcit = context.get_function(rwdlx__tfqfh, jkcfg__lcer)
        csv__pcit(builder, (out_arr, vkbkb__wmt, agt__gjve))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    dvrp__crwg = c.context.make_helper(c.builder, typ, val)
    wbi__exrqr = ArrayItemArrayType(char_arr_type)
    uucx__bho = _get_array_item_arr_payload(c.context, c.builder,
        wbi__exrqr, dvrp__crwg.data)
    gtx__bxrqo = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    bnge__mgfna = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        bnge__mgfna = 'pd_array_from_string_array'
    idkqw__zvl = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    tuoex__wjw = cgutils.get_or_insert_function(c.builder.module,
        idkqw__zvl, name=bnge__mgfna)
    kgf__iog = c.context.make_array(offset_arr_type)(c.context, c.builder,
        uucx__bho.offsets).data
    esgx__twip = c.context.make_array(char_arr_type)(c.context, c.builder,
        uucx__bho.data).data
    eqo__dbzu = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, uucx__bho.null_bitmap).data
    arr = c.builder.call(tuoex__wjw, [uucx__bho.n_arrays, kgf__iog,
        esgx__twip, eqo__dbzu, gtx__bxrqo])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        eqo__dbzu = context.make_array(null_bitmap_arr_type)(context,
            builder, uucx__bho.null_bitmap).data
        ihysc__thglm = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        evd__pqlnt = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        ktesf__cowk = builder.load(builder.gep(eqo__dbzu, [ihysc__thglm],
            inbounds=True))
        ftpw__yhfx = lir.ArrayType(lir.IntType(8), 8)
        jiejo__fdie = cgutils.alloca_once_value(builder, lir.Constant(
            ftpw__yhfx, (1, 2, 4, 8, 16, 32, 64, 128)))
        emyz__cxz = builder.load(builder.gep(jiejo__fdie, [lir.Constant(lir
            .IntType(64), 0), evd__pqlnt], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(ktesf__cowk,
            emyz__cxz), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ihysc__thglm = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        evd__pqlnt = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        eqo__dbzu = context.make_array(null_bitmap_arr_type)(context,
            builder, uucx__bho.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, uucx__bho.
            offsets).data
        fgffo__fttt = builder.gep(eqo__dbzu, [ihysc__thglm], inbounds=True)
        ktesf__cowk = builder.load(fgffo__fttt)
        ftpw__yhfx = lir.ArrayType(lir.IntType(8), 8)
        jiejo__fdie = cgutils.alloca_once_value(builder, lir.Constant(
            ftpw__yhfx, (1, 2, 4, 8, 16, 32, 64, 128)))
        emyz__cxz = builder.load(builder.gep(jiejo__fdie, [lir.Constant(lir
            .IntType(64), 0), evd__pqlnt], inbounds=True))
        emyz__cxz = builder.xor(emyz__cxz, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(ktesf__cowk, emyz__cxz), fgffo__fttt)
        if str_arr_typ == string_array_type:
            fess__sbnp = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            mrog__efarx = builder.icmp_unsigned('!=', fess__sbnp, uucx__bho
                .n_arrays)
            with builder.if_then(mrog__efarx):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [fess__sbnp]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ihysc__thglm = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        evd__pqlnt = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        eqo__dbzu = context.make_array(null_bitmap_arr_type)(context,
            builder, uucx__bho.null_bitmap).data
        fgffo__fttt = builder.gep(eqo__dbzu, [ihysc__thglm], inbounds=True)
        ktesf__cowk = builder.load(fgffo__fttt)
        ftpw__yhfx = lir.ArrayType(lir.IntType(8), 8)
        jiejo__fdie = cgutils.alloca_once_value(builder, lir.Constant(
            ftpw__yhfx, (1, 2, 4, 8, 16, 32, 64, 128)))
        emyz__cxz = builder.load(builder.gep(jiejo__fdie, [lir.Constant(lir
            .IntType(64), 0), evd__pqlnt], inbounds=True))
        builder.store(builder.or_(ktesf__cowk, emyz__cxz), fgffo__fttt)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        uucx__bho = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pknt__ycavn = builder.udiv(builder.add(uucx__bho.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        eqo__dbzu = context.make_array(null_bitmap_arr_type)(context,
            builder, uucx__bho.null_bitmap).data
        cgutils.memset(builder, eqo__dbzu, pknt__ycavn, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    xxzk__psra = context.make_helper(builder, string_array_type, str_arr)
    wbi__exrqr = ArrayItemArrayType(char_arr_type)
    vqvrb__cpama = context.make_helper(builder, wbi__exrqr, xxzk__psra.data)
    peo__blszx = ArrayItemArrayPayloadType(wbi__exrqr)
    agke__ivsef = context.nrt.meminfo_data(builder, vqvrb__cpama.meminfo)
    tvmm__wlcnz = builder.bitcast(agke__ivsef, context.get_value_type(
        peo__blszx).as_pointer())
    return tvmm__wlcnz


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        euc__zsl, yzgjy__mlta = args
        fvk__cbgvt = _get_str_binary_arr_data_payload_ptr(context, builder,
            yzgjy__mlta)
        lqwoq__llw = _get_str_binary_arr_data_payload_ptr(context, builder,
            euc__zsl)
        lqks__mdw = _get_str_binary_arr_payload(context, builder,
            yzgjy__mlta, sig.args[1])
        mnu__nbqn = _get_str_binary_arr_payload(context, builder, euc__zsl,
            sig.args[0])
        context.nrt.incref(builder, char_arr_type, lqks__mdw.data)
        context.nrt.incref(builder, offset_arr_type, lqks__mdw.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, lqks__mdw.null_bitmap
            )
        context.nrt.decref(builder, char_arr_type, mnu__nbqn.data)
        context.nrt.decref(builder, offset_arr_type, mnu__nbqn.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, mnu__nbqn.null_bitmap
            )
        builder.store(builder.load(fvk__cbgvt), lqwoq__llw)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        qqfm__yhh = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return qqfm__yhh
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, nzyt__fvv, ffrw__txeg = args
        uucx__bho = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, uucx__bho.
            offsets).data
        data = context.make_helper(builder, char_arr_type, uucx__bho.data).data
        idkqw__zvl = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        ixs__vngow = cgutils.get_or_insert_function(builder.module,
            idkqw__zvl, name='setitem_string_array')
        nnr__kpbz = context.get_constant(types.int32, -1)
        bcx__iwc = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, uucx__bho.
            n_arrays)
        builder.call(ixs__vngow, [offsets, data, num_total_chars, builder.
            extract_value(nzyt__fvv, 0), ffrw__txeg, nnr__kpbz, bcx__iwc, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    idkqw__zvl = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    fba__pdyzo = cgutils.get_or_insert_function(builder.module, idkqw__zvl,
        name='is_na')
    return builder.call(fba__pdyzo, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        urze__uwv, hee__qei, ium__xxofc, wth__ahkcx = args
        cgutils.raw_memcpy(builder, urze__uwv, hee__qei, ium__xxofc, wth__ahkcx
            )
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        ydlwz__zpfih, fncx__buxkt = unicode_to_utf8_and_len(val)
        gnscq__srza = getitem_str_offset(A, ind)
        eukf__fdbyd = getitem_str_offset(A, ind + 1)
        jrr__xfw = eukf__fdbyd - gnscq__srza
        if jrr__xfw != fncx__buxkt:
            return False
        nzyt__fvv = get_data_ptr_ind(A, gnscq__srza)
        return memcmp(nzyt__fvv, ydlwz__zpfih, fncx__buxkt) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        gnscq__srza = getitem_str_offset(A, ind)
        jrr__xfw = bodo.libs.str_ext.int_to_str_len(val)
        osvsb__vgm = gnscq__srza + jrr__xfw
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            gnscq__srza, osvsb__vgm)
        nzyt__fvv = get_data_ptr_ind(A, gnscq__srza)
        inplace_int64_to_str(nzyt__fvv, jrr__xfw, val)
        setitem_str_offset(A, ind + 1, gnscq__srza + jrr__xfw)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        nzyt__fvv, = args
        sss__ewsro = context.insert_const_string(builder.module, '<NA>')
        bdn__oih = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, nzyt__fvv, sss__ewsro, bdn__oih, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    esfn__uefni = len('<NA>')

    def impl(A, ind):
        gnscq__srza = getitem_str_offset(A, ind)
        osvsb__vgm = gnscq__srza + esfn__uefni
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            gnscq__srza, osvsb__vgm)
        nzyt__fvv = get_data_ptr_ind(A, gnscq__srza)
        inplace_set_NA_str(nzyt__fvv)
        setitem_str_offset(A, ind + 1, gnscq__srza + esfn__uefni)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            gnscq__srza = getitem_str_offset(A, ind)
            eukf__fdbyd = getitem_str_offset(A, ind + 1)
            ffrw__txeg = eukf__fdbyd - gnscq__srza
            nzyt__fvv = get_data_ptr_ind(A, gnscq__srza)
            lxg__nvi = decode_utf8(nzyt__fvv, ffrw__txeg)
            return lxg__nvi
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            qqfm__yhh = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(qqfm__yhh):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            nay__udkhy = get_data_ptr(out_arr).data
            ywv__zytm = get_data_ptr(A).data
            pmha__ybrmq = 0
            nonz__ccdi = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(qqfm__yhh):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    luyp__jcrrf = get_str_arr_item_length(A, i)
                    if luyp__jcrrf == 1:
                        copy_single_char(nay__udkhy, nonz__ccdi, ywv__zytm,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(nay__udkhy, nonz__ccdi, ywv__zytm,
                            getitem_str_offset(A, i), luyp__jcrrf, 1)
                    nonz__ccdi += luyp__jcrrf
                    setitem_str_offset(out_arr, pmha__ybrmq + 1, nonz__ccdi)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, pmha__ybrmq)
                    else:
                        str_arr_set_not_na(out_arr, pmha__ybrmq)
                    pmha__ybrmq += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            qqfm__yhh = len(ind)
            out_arr = pre_alloc_string_array(qqfm__yhh, -1)
            pmha__ybrmq = 0
            for i in range(qqfm__yhh):
                onhf__iolw = A[ind[i]]
                out_arr[pmha__ybrmq] = onhf__iolw
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, pmha__ybrmq)
                pmha__ybrmq += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            qqfm__yhh = len(A)
            bia__zsbq = numba.cpython.unicode._normalize_slice(ind, qqfm__yhh)
            qgshf__lehq = numba.cpython.unicode._slice_span(bia__zsbq)
            if bia__zsbq.step == 1:
                gnscq__srza = getitem_str_offset(A, bia__zsbq.start)
                eukf__fdbyd = getitem_str_offset(A, bia__zsbq.stop)
                n_chars = eukf__fdbyd - gnscq__srza
                eld__pan = pre_alloc_string_array(qgshf__lehq, np.int64(
                    n_chars))
                for i in range(qgshf__lehq):
                    eld__pan[i] = A[bia__zsbq.start + i]
                    if str_arr_is_na(A, bia__zsbq.start + i):
                        str_arr_set_na(eld__pan, i)
                return eld__pan
            else:
                eld__pan = pre_alloc_string_array(qgshf__lehq, -1)
                for i in range(qgshf__lehq):
                    eld__pan[i] = A[bia__zsbq.start + i * bia__zsbq.step]
                    if str_arr_is_na(A, bia__zsbq.start + i * bia__zsbq.step):
                        str_arr_set_na(eld__pan, i)
                return eld__pan
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    uua__oyabw = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(uua__oyabw)
        wkk__herth = 4

        def impl_scalar(A, idx, val):
            iool__sdpkq = (val._length if val._is_ascii else wkk__herth *
                val._length)
            yopw__jghd = A._data
            gnscq__srza = np.int64(getitem_str_offset(A, idx))
            osvsb__vgm = gnscq__srza + iool__sdpkq
            bodo.libs.array_item_arr_ext.ensure_data_capacity(yopw__jghd,
                gnscq__srza, osvsb__vgm)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                osvsb__vgm, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                bia__zsbq = numba.cpython.unicode._normalize_slice(idx, len(A))
                yfdwq__ckk = bia__zsbq.start
                yopw__jghd = A._data
                gnscq__srza = np.int64(getitem_str_offset(A, yfdwq__ckk))
                osvsb__vgm = gnscq__srza + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(yopw__jghd,
                    gnscq__srza, osvsb__vgm)
                set_string_array_range(A, val, yfdwq__ckk, gnscq__srza)
                btnci__vxnr = 0
                for i in range(bia__zsbq.start, bia__zsbq.stop, bia__zsbq.step
                    ):
                    if str_arr_is_na(val, btnci__vxnr):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    btnci__vxnr += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                enm__rgnao = str_list_to_array(val)
                A[idx] = enm__rgnao
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                bia__zsbq = numba.cpython.unicode._normalize_slice(idx, len(A))
                for i in range(bia__zsbq.start, bia__zsbq.stop, bia__zsbq.step
                    ):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(uua__oyabw)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                qqfm__yhh = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(qqfm__yhh, -1)
                for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                qqfm__yhh = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(qqfm__yhh, -1)
                uicl__upx = 0
                for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, uicl__upx):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, uicl__upx)
                        else:
                            out_arr[i] = str(val[uicl__upx])
                        uicl__upx += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(uua__oyabw)
    raise BodoError(uua__oyabw)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    obf__njor = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(obf__njor, (types.Float, types.Integer)
        ) and obf__njor not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(obf__njor, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            qqfm__yhh = len(A)
            B = np.empty(qqfm__yhh, obf__njor)
            for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif obf__njor == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            qqfm__yhh = len(A)
            B = np.empty(qqfm__yhh, obf__njor)
            for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif obf__njor == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            qqfm__yhh = len(A)
            B = np.empty(qqfm__yhh, obf__njor)
            for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            qqfm__yhh = len(A)
            B = np.empty(qqfm__yhh, obf__njor)
            for i in numba.parfors.parfor.internal_prange(qqfm__yhh):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        nzyt__fvv, ffrw__txeg = args
        evjd__jwjz = context.get_python_api(builder)
        ouw__ovqy = evjd__jwjz.string_from_string_and_size(nzyt__fvv,
            ffrw__txeg)
        idp__cnroe = evjd__jwjz.to_native_value(string_type, ouw__ovqy).value
        wkcn__mthfg = cgutils.create_struct_proxy(string_type)(context,
            builder, idp__cnroe)
        wkcn__mthfg.hash = wkcn__mthfg.hash.type(-1)
        evjd__jwjz.decref(ouw__ovqy)
        return wkcn__mthfg._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    str_arr = decode_if_dict_array(str_arr)
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type, '_str_arr_item_to_numeric: str arr expected'
    assert ind_t == types.int64, '_str_arr_item_to_numeric: integer index expected'

    def codegen(context, builder, sig, args):
        vpdu__jfj, arr, ind, xkgr__oqdr = args
        uucx__bho = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, uucx__bho.
            offsets).data
        data = context.make_helper(builder, char_arr_type, uucx__bho.data).data
        idkqw__zvl = lir.FunctionType(lir.IntType(32), [vpdu__jfj.type, lir
            .IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        tddxc__htu = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            tddxc__htu = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        yddw__nzl = cgutils.get_or_insert_function(builder.module,
            idkqw__zvl, tddxc__htu)
        return builder.call(yddw__nzl, [vpdu__jfj, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    gtx__bxrqo = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    idkqw__zvl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    ubn__oryg = cgutils.get_or_insert_function(c.builder.module, idkqw__zvl,
        name='string_array_from_sequence')
    vypdw__ijh = c.builder.call(ubn__oryg, [val, gtx__bxrqo])
    wbi__exrqr = ArrayItemArrayType(char_arr_type)
    vqvrb__cpama = c.context.make_helper(c.builder, wbi__exrqr)
    vqvrb__cpama.meminfo = vypdw__ijh
    xxzk__psra = c.context.make_helper(c.builder, typ)
    yopw__jghd = vqvrb__cpama._getvalue()
    xxzk__psra.data = yopw__jghd
    atw__cveu = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xxzk__psra._getvalue(), is_error=atw__cveu)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    qqfm__yhh = len(pyval)
    nonz__ccdi = 0
    jqg__iyk = np.empty(qqfm__yhh + 1, np_offset_type)
    csw__bjpz = []
    egka__gmi = np.empty(qqfm__yhh + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        jqg__iyk[i] = nonz__ccdi
        mksd__khiu = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(egka__gmi, i, int(not mksd__khiu))
        if mksd__khiu:
            continue
        ujb__scfcb = list(s.encode()) if isinstance(s, str) else list(s)
        csw__bjpz.extend(ujb__scfcb)
        nonz__ccdi += len(ujb__scfcb)
    jqg__iyk[qqfm__yhh] = nonz__ccdi
    rdq__glbhn = np.array(csw__bjpz, np.uint8)
    hmw__dsm = context.get_constant(types.int64, qqfm__yhh)
    dgnjg__rtub = context.get_constant_generic(builder, char_arr_type,
        rdq__glbhn)
    iqd__aaf = context.get_constant_generic(builder, offset_arr_type, jqg__iyk)
    jifxe__crs = context.get_constant_generic(builder, null_bitmap_arr_type,
        egka__gmi)
    uucx__bho = lir.Constant.literal_struct([hmw__dsm, dgnjg__rtub,
        iqd__aaf, jifxe__crs])
    uucx__bho = cgutils.global_constant(builder, '.const.payload', uucx__bho
        ).bitcast(cgutils.voidptr_t)
    prtxu__afzmd = context.get_constant(types.int64, -1)
    knwy__wfd = context.get_constant_null(types.voidptr)
    ljh__ypy = lir.Constant.literal_struct([prtxu__afzmd, knwy__wfd,
        knwy__wfd, uucx__bho, prtxu__afzmd])
    ljh__ypy = cgutils.global_constant(builder, '.const.meminfo', ljh__ypy
        ).bitcast(cgutils.voidptr_t)
    yopw__jghd = lir.Constant.literal_struct([ljh__ypy])
    xxzk__psra = lir.Constant.literal_struct([yopw__jghd])
    return xxzk__psra


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
