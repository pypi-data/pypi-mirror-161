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
        srsa__kkhim = ArrayItemArrayType(char_arr_type)
        lfrcd__pnpe = [('data', srsa__kkhim)]
        models.StructModel.__init__(self, dmm, fe_type, lfrcd__pnpe)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        ntsrv__sxji, = args
        oei__ppumx = context.make_helper(builder, string_array_type)
        oei__ppumx.data = ntsrv__sxji
        context.nrt.incref(builder, data_typ, ntsrv__sxji)
        return oei__ppumx._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    bpod__nkj = c.context.insert_const_string(c.builder.module, 'pandas')
    atsqg__zxl = c.pyapi.import_module_noblock(bpod__nkj)
    smhy__zdm = c.pyapi.call_method(atsqg__zxl, 'StringDtype', ())
    c.pyapi.decref(atsqg__zxl)
    return smhy__zdm


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        zek__dif = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs)
        if zek__dif is not None:
            return zek__dif
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                dnmfe__yldc = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(dnmfe__yldc)
                for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
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
                dnmfe__yldc = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(dnmfe__yldc)
                for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
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
                dnmfe__yldc = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(dnmfe__yldc)
                for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
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
    qmrkj__qdw = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    bcr__jmz = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and bcr__jmz or qmrkj__qdw and is_str_arr_type(rhs
        ):

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
    sfnr__terpe = context.make_helper(builder, arr_typ, arr_value)
    srsa__kkhim = ArrayItemArrayType(char_arr_type)
    pzps__ahoe = _get_array_item_arr_payload(context, builder, srsa__kkhim,
        sfnr__terpe.data)
    return pzps__ahoe


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return pzps__ahoe.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        vxb__uslg = context.make_helper(builder, offset_arr_type,
            pzps__ahoe.offsets).data
        return _get_num_total_chars(builder, vxb__uslg, pzps__ahoe.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xpmze__xvpq = context.make_helper(builder, offset_arr_type,
            pzps__ahoe.offsets)
        fst__ftr = context.make_helper(builder, offset_ctypes_type)
        fst__ftr.data = builder.bitcast(xpmze__xvpq.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        fst__ftr.meminfo = xpmze__xvpq.meminfo
        smhy__zdm = fst__ftr._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            smhy__zdm)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ntsrv__sxji = context.make_helper(builder, char_arr_type,
            pzps__ahoe.data)
        fst__ftr = context.make_helper(builder, data_ctypes_type)
        fst__ftr.data = ntsrv__sxji.data
        fst__ftr.meminfo = ntsrv__sxji.meminfo
        smhy__zdm = fst__ftr._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, smhy__zdm)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        weoqu__sqi, ind = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            weoqu__sqi, sig.args[0])
        ntsrv__sxji = context.make_helper(builder, char_arr_type,
            pzps__ahoe.data)
        fst__ftr = context.make_helper(builder, data_ctypes_type)
        fst__ftr.data = builder.gep(ntsrv__sxji.data, [ind])
        fst__ftr.meminfo = ntsrv__sxji.meminfo
        smhy__zdm = fst__ftr._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, smhy__zdm)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        gsxgp__mscyw, wkppw__lll, dveq__rbgz, lymg__gnol = args
        qzpn__triz = builder.bitcast(builder.gep(gsxgp__mscyw, [wkppw__lll]
            ), lir.IntType(8).as_pointer())
        xqbb__tjjsz = builder.bitcast(builder.gep(dveq__rbgz, [lymg__gnol]),
            lir.IntType(8).as_pointer())
        wtha__tyktm = builder.load(xqbb__tjjsz)
        builder.store(wtha__tyktm, qzpn__triz)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        jmdmp__oisch = context.make_helper(builder, null_bitmap_arr_type,
            pzps__ahoe.null_bitmap)
        fst__ftr = context.make_helper(builder, data_ctypes_type)
        fst__ftr.data = jmdmp__oisch.data
        fst__ftr.meminfo = jmdmp__oisch.meminfo
        smhy__zdm = fst__ftr._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, smhy__zdm)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        vxb__uslg = context.make_helper(builder, offset_arr_type,
            pzps__ahoe.offsets).data
        return builder.load(builder.gep(vxb__uslg, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, pzps__ahoe.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        xklsk__cji, ind = args
        if in_bitmap_typ == data_ctypes_type:
            fst__ftr = context.make_helper(builder, data_ctypes_type,
                xklsk__cji)
            xklsk__cji = fst__ftr.data
        return builder.load(builder.gep(xklsk__cji, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        xklsk__cji, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            fst__ftr = context.make_helper(builder, data_ctypes_type,
                xklsk__cji)
            xklsk__cji = fst__ftr.data
        builder.store(val, builder.gep(xklsk__cji, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        rqezy__uaksp = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        obz__islc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        qdel__ritd = context.make_helper(builder, offset_arr_type,
            rqezy__uaksp.offsets).data
        hqd__say = context.make_helper(builder, offset_arr_type, obz__islc.
            offsets).data
        bxwr__fiyhl = context.make_helper(builder, char_arr_type,
            rqezy__uaksp.data).data
        wgq__ezbrr = context.make_helper(builder, char_arr_type, obz__islc.data
            ).data
        azblx__aovrd = context.make_helper(builder, null_bitmap_arr_type,
            rqezy__uaksp.null_bitmap).data
        gcpa__paii = context.make_helper(builder, null_bitmap_arr_type,
            obz__islc.null_bitmap).data
        geyp__rhgk = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, hqd__say, qdel__ritd, geyp__rhgk)
        cgutils.memcpy(builder, wgq__ezbrr, bxwr__fiyhl, builder.load(
            builder.gep(qdel__ritd, [ind])))
        rlysp__sbho = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        upgt__kkkjf = builder.lshr(rlysp__sbho, lir.Constant(lir.IntType(64
            ), 3))
        cgutils.memcpy(builder, gcpa__paii, azblx__aovrd, upgt__kkkjf)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        rqezy__uaksp = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        obz__islc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        qdel__ritd = context.make_helper(builder, offset_arr_type,
            rqezy__uaksp.offsets).data
        bxwr__fiyhl = context.make_helper(builder, char_arr_type,
            rqezy__uaksp.data).data
        wgq__ezbrr = context.make_helper(builder, char_arr_type, obz__islc.data
            ).data
        num_total_chars = _get_num_total_chars(builder, qdel__ritd,
            rqezy__uaksp.n_arrays)
        cgutils.memcpy(builder, wgq__ezbrr, bxwr__fiyhl, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        rqezy__uaksp = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        obz__islc = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        qdel__ritd = context.make_helper(builder, offset_arr_type,
            rqezy__uaksp.offsets).data
        hqd__say = context.make_helper(builder, offset_arr_type, obz__islc.
            offsets).data
        azblx__aovrd = context.make_helper(builder, null_bitmap_arr_type,
            rqezy__uaksp.null_bitmap).data
        dnmfe__yldc = rqezy__uaksp.n_arrays
        pey__dbbmd = context.get_constant(offset_type, 0)
        awx__cilrj = cgutils.alloca_once_value(builder, pey__dbbmd)
        with cgutils.for_range(builder, dnmfe__yldc) as tzkb__hwnt:
            uty__cfi = lower_is_na(context, builder, azblx__aovrd,
                tzkb__hwnt.index)
            with cgutils.if_likely(builder, builder.not_(uty__cfi)):
                oeoq__iptz = builder.load(builder.gep(qdel__ritd, [
                    tzkb__hwnt.index]))
                ulj__zpzb = builder.load(awx__cilrj)
                builder.store(oeoq__iptz, builder.gep(hqd__say, [ulj__zpzb]))
                builder.store(builder.add(ulj__zpzb, lir.Constant(context.
                    get_value_type(offset_type), 1)), awx__cilrj)
        ulj__zpzb = builder.load(awx__cilrj)
        oeoq__iptz = builder.load(builder.gep(qdel__ritd, [dnmfe__yldc]))
        builder.store(oeoq__iptz, builder.gep(hqd__say, [ulj__zpzb]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        lkzy__bfd, ind, str, ezy__kast = args
        lkzy__bfd = context.make_array(sig.args[0])(context, builder, lkzy__bfd
            )
        ulydz__pphf = builder.gep(lkzy__bfd.data, [ind])
        cgutils.raw_memcpy(builder, ulydz__pphf, str, ezy__kast, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        ulydz__pphf, ind, jgsxc__uunq, ezy__kast = args
        ulydz__pphf = builder.gep(ulydz__pphf, [ind])
        cgutils.raw_memcpy(builder, ulydz__pphf, jgsxc__uunq, ezy__kast, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            avfs__wya = A._data
            return np.int64(getitem_str_offset(avfs__wya, idx + 1) -
                getitem_str_offset(avfs__wya, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    areqi__isoh = np.int64(getitem_str_offset(A, i))
    iwe__fli = np.int64(getitem_str_offset(A, i + 1))
    l = iwe__fli - areqi__isoh
    bvi__huzq = get_data_ptr_ind(A, areqi__isoh)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(bvi__huzq, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    jbi__ryink = getitem_str_offset(A, i)
    gvhg__pcsry = getitem_str_offset(A, i + 1)
    cdozn__behbt = gvhg__pcsry - jbi__ryink
    cerl__rqit = getitem_str_offset(B, j)
    xdpa__rgg = cerl__rqit + cdozn__behbt
    setitem_str_offset(B, j + 1, xdpa__rgg)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if cdozn__behbt != 0:
        ntsrv__sxji = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(ntsrv__sxji, np.
            int64(cerl__rqit), np.int64(xdpa__rgg))
        mlkb__vkrvw = get_data_ptr(B).data
        nwxrb__bfqvu = get_data_ptr(A).data
        memcpy_region(mlkb__vkrvw, cerl__rqit, nwxrb__bfqvu, jbi__ryink,
            cdozn__behbt, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    dnmfe__yldc = len(str_arr)
    cmr__rbzpd = np.empty(dnmfe__yldc, np.bool_)
    for i in range(dnmfe__yldc):
        cmr__rbzpd[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return cmr__rbzpd


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            dnmfe__yldc = len(data)
            l = []
            for i in range(dnmfe__yldc):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        mhvdh__ijq = data.count
        jaa__ztsgp = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(mhvdh__ijq)]
        if is_overload_true(str_null_bools):
            jaa__ztsgp += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(mhvdh__ijq) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        iqae__gpr = 'def f(data, str_null_bools=None):\n'
        iqae__gpr += '  return ({}{})\n'.format(', '.join(jaa__ztsgp), ',' if
            mhvdh__ijq == 1 else '')
        lcvch__dfazj = {}
        exec(iqae__gpr, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, lcvch__dfazj)
        sgvgb__kzxme = lcvch__dfazj['f']
        return sgvgb__kzxme
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                dnmfe__yldc = len(list_data)
                for i in range(dnmfe__yldc):
                    jgsxc__uunq = list_data[i]
                    str_arr[i] = jgsxc__uunq
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                dnmfe__yldc = len(list_data)
                for i in range(dnmfe__yldc):
                    jgsxc__uunq = list_data[i]
                    str_arr[i] = jgsxc__uunq
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        mhvdh__ijq = str_arr.count
        cdbxk__smzup = 0
        iqae__gpr = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(mhvdh__ijq):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                iqae__gpr += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, mhvdh__ijq + cdbxk__smzup))
                cdbxk__smzup += 1
            else:
                iqae__gpr += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        iqae__gpr += '  return\n'
        lcvch__dfazj = {}
        exec(iqae__gpr, {'cp_str_list_to_array': cp_str_list_to_array},
            lcvch__dfazj)
        pospb__gua = lcvch__dfazj['f']
        return pospb__gua
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            dnmfe__yldc = len(str_list)
            str_arr = pre_alloc_string_array(dnmfe__yldc, -1)
            for i in range(dnmfe__yldc):
                jgsxc__uunq = str_list[i]
                str_arr[i] = jgsxc__uunq
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            dnmfe__yldc = len(A)
            zou__ejx = 0
            for i in range(dnmfe__yldc):
                jgsxc__uunq = A[i]
                zou__ejx += get_utf8_size(jgsxc__uunq)
            return zou__ejx
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        dnmfe__yldc = len(arr)
        n_chars = num_total_chars(arr)
        qky__ihuig = pre_alloc_string_array(dnmfe__yldc, np.int64(n_chars))
        copy_str_arr_slice(qky__ihuig, arr, dnmfe__yldc)
        return qky__ihuig
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
    iqae__gpr = 'def f(in_seq):\n'
    iqae__gpr += '    n_strs = len(in_seq)\n'
    iqae__gpr += '    A = pre_alloc_string_array(n_strs, -1)\n'
    iqae__gpr += '    return A\n'
    lcvch__dfazj = {}
    exec(iqae__gpr, {'pre_alloc_string_array': pre_alloc_string_array},
        lcvch__dfazj)
    jszfz__tsvqg = lcvch__dfazj['f']
    return jszfz__tsvqg


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        hwdj__wcrl = 'pre_alloc_binary_array'
    else:
        hwdj__wcrl = 'pre_alloc_string_array'
    iqae__gpr = 'def f(in_seq):\n'
    iqae__gpr += '    n_strs = len(in_seq)\n'
    iqae__gpr += f'    A = {hwdj__wcrl}(n_strs, -1)\n'
    iqae__gpr += '    for i in range(n_strs):\n'
    iqae__gpr += '        A[i] = in_seq[i]\n'
    iqae__gpr += '    return A\n'
    lcvch__dfazj = {}
    exec(iqae__gpr, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, lcvch__dfazj)
    jszfz__tsvqg = lcvch__dfazj['f']
    return jszfz__tsvqg


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        sti__hbiy = builder.add(pzps__ahoe.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        gkvs__tuf = builder.lshr(lir.Constant(lir.IntType(64), offset_type.
            bitwidth), lir.Constant(lir.IntType(64), 3))
        upgt__kkkjf = builder.mul(sti__hbiy, gkvs__tuf)
        eqzrm__hmvv = context.make_array(offset_arr_type)(context, builder,
            pzps__ahoe.offsets).data
        cgutils.memset(builder, eqzrm__hmvv, upgt__kkkjf, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        utebj__qqu = pzps__ahoe.n_arrays
        upgt__kkkjf = builder.lshr(builder.add(utebj__qqu, lir.Constant(lir
            .IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        btpk__rwpq = context.make_array(null_bitmap_arr_type)(context,
            builder, pzps__ahoe.null_bitmap).data
        cgutils.memset(builder, btpk__rwpq, upgt__kkkjf, 0)
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
    fwt__wbw = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        wbp__eoob = len(len_arr)
        for i in range(wbp__eoob):
            offsets[i] = fwt__wbw
            fwt__wbw += len_arr[i]
        offsets[wbp__eoob] = fwt__wbw
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    nsjk__ibd = i // 8
    jlt__zdu = getitem_str_bitmap(bits, nsjk__ibd)
    jlt__zdu ^= np.uint8(-np.uint8(bit_is_set) ^ jlt__zdu) & kBitmask[i % 8]
    setitem_str_bitmap(bits, nsjk__ibd, jlt__zdu)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    xrx__spay = get_null_bitmap_ptr(out_str_arr)
    fkbs__nqfe = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        lvs__lns = get_bit_bitmap(fkbs__nqfe, j)
        set_bit_to(xrx__spay, out_start + j, lvs__lns)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, weoqu__sqi, nkez__jrmqb, zoy__tbjc = args
        rqezy__uaksp = _get_str_binary_arr_payload(context, builder,
            weoqu__sqi, string_array_type)
        obz__islc = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        qdel__ritd = context.make_helper(builder, offset_arr_type,
            rqezy__uaksp.offsets).data
        hqd__say = context.make_helper(builder, offset_arr_type, obz__islc.
            offsets).data
        bxwr__fiyhl = context.make_helper(builder, char_arr_type,
            rqezy__uaksp.data).data
        wgq__ezbrr = context.make_helper(builder, char_arr_type, obz__islc.data
            ).data
        num_total_chars = _get_num_total_chars(builder, qdel__ritd,
            rqezy__uaksp.n_arrays)
        fuyy__egudl = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        xva__urw = cgutils.get_or_insert_function(builder.module,
            fuyy__egudl, name='set_string_array_range')
        builder.call(xva__urw, [hqd__say, wgq__ezbrr, qdel__ritd,
            bxwr__fiyhl, nkez__jrmqb, zoy__tbjc, rqezy__uaksp.n_arrays,
            num_total_chars])
        kiquv__pvzn = context.typing_context.resolve_value_type(
            copy_nulls_range)
        nmys__asxty = kiquv__pvzn.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        qoy__pdf = context.get_function(kiquv__pvzn, nmys__asxty)
        qoy__pdf(builder, (out_arr, weoqu__sqi, nkez__jrmqb))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    ceyvc__dkbv = c.context.make_helper(c.builder, typ, val)
    srsa__kkhim = ArrayItemArrayType(char_arr_type)
    pzps__ahoe = _get_array_item_arr_payload(c.context, c.builder,
        srsa__kkhim, ceyvc__dkbv.data)
    luoej__mxc = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    ntrj__szxl = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        ntrj__szxl = 'pd_array_from_string_array'
    fuyy__egudl = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    jiq__lisfl = cgutils.get_or_insert_function(c.builder.module,
        fuyy__egudl, name=ntrj__szxl)
    vxb__uslg = c.context.make_array(offset_arr_type)(c.context, c.builder,
        pzps__ahoe.offsets).data
    bvi__huzq = c.context.make_array(char_arr_type)(c.context, c.builder,
        pzps__ahoe.data).data
    btpk__rwpq = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, pzps__ahoe.null_bitmap).data
    arr = c.builder.call(jiq__lisfl, [pzps__ahoe.n_arrays, vxb__uslg,
        bvi__huzq, btpk__rwpq, luoej__mxc])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        btpk__rwpq = context.make_array(null_bitmap_arr_type)(context,
            builder, pzps__ahoe.null_bitmap).data
        ugmz__wwowo = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        xww__rqka = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        jlt__zdu = builder.load(builder.gep(btpk__rwpq, [ugmz__wwowo],
            inbounds=True))
        qwo__qjfqo = lir.ArrayType(lir.IntType(8), 8)
        nfb__hddt = cgutils.alloca_once_value(builder, lir.Constant(
            qwo__qjfqo, (1, 2, 4, 8, 16, 32, 64, 128)))
        bzi__turkr = builder.load(builder.gep(nfb__hddt, [lir.Constant(lir.
            IntType(64), 0), xww__rqka], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(jlt__zdu,
            bzi__turkr), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ugmz__wwowo = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        xww__rqka = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        btpk__rwpq = context.make_array(null_bitmap_arr_type)(context,
            builder, pzps__ahoe.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, pzps__ahoe.
            offsets).data
        uwvgh__enbc = builder.gep(btpk__rwpq, [ugmz__wwowo], inbounds=True)
        jlt__zdu = builder.load(uwvgh__enbc)
        qwo__qjfqo = lir.ArrayType(lir.IntType(8), 8)
        nfb__hddt = cgutils.alloca_once_value(builder, lir.Constant(
            qwo__qjfqo, (1, 2, 4, 8, 16, 32, 64, 128)))
        bzi__turkr = builder.load(builder.gep(nfb__hddt, [lir.Constant(lir.
            IntType(64), 0), xww__rqka], inbounds=True))
        bzi__turkr = builder.xor(bzi__turkr, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(jlt__zdu, bzi__turkr), uwvgh__enbc)
        if str_arr_typ == string_array_type:
            arg__yig = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            agc__jhbog = builder.icmp_unsigned('!=', arg__yig, pzps__ahoe.
                n_arrays)
            with builder.if_then(agc__jhbog):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [arg__yig]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ugmz__wwowo = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        xww__rqka = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        btpk__rwpq = context.make_array(null_bitmap_arr_type)(context,
            builder, pzps__ahoe.null_bitmap).data
        uwvgh__enbc = builder.gep(btpk__rwpq, [ugmz__wwowo], inbounds=True)
        jlt__zdu = builder.load(uwvgh__enbc)
        qwo__qjfqo = lir.ArrayType(lir.IntType(8), 8)
        nfb__hddt = cgutils.alloca_once_value(builder, lir.Constant(
            qwo__qjfqo, (1, 2, 4, 8, 16, 32, 64, 128)))
        bzi__turkr = builder.load(builder.gep(nfb__hddt, [lir.Constant(lir.
            IntType(64), 0), xww__rqka], inbounds=True))
        builder.store(builder.or_(jlt__zdu, bzi__turkr), uwvgh__enbc)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        upgt__kkkjf = builder.udiv(builder.add(pzps__ahoe.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        btpk__rwpq = context.make_array(null_bitmap_arr_type)(context,
            builder, pzps__ahoe.null_bitmap).data
        cgutils.memset(builder, btpk__rwpq, upgt__kkkjf, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    loxth__qzyvt = context.make_helper(builder, string_array_type, str_arr)
    srsa__kkhim = ArrayItemArrayType(char_arr_type)
    qnr__qrh = context.make_helper(builder, srsa__kkhim, loxth__qzyvt.data)
    kog__lial = ArrayItemArrayPayloadType(srsa__kkhim)
    qdw__lhi = context.nrt.meminfo_data(builder, qnr__qrh.meminfo)
    obbf__rxq = builder.bitcast(qdw__lhi, context.get_value_type(kog__lial)
        .as_pointer())
    return obbf__rxq


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        teuy__yxsi, skj__nen = args
        sxjcp__izzcl = _get_str_binary_arr_data_payload_ptr(context,
            builder, skj__nen)
        ahgf__jfcz = _get_str_binary_arr_data_payload_ptr(context, builder,
            teuy__yxsi)
        pvzk__mlu = _get_str_binary_arr_payload(context, builder, skj__nen,
            sig.args[1])
        wlcbk__uqfpl = _get_str_binary_arr_payload(context, builder,
            teuy__yxsi, sig.args[0])
        context.nrt.incref(builder, char_arr_type, pvzk__mlu.data)
        context.nrt.incref(builder, offset_arr_type, pvzk__mlu.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, pvzk__mlu.null_bitmap
            )
        context.nrt.decref(builder, char_arr_type, wlcbk__uqfpl.data)
        context.nrt.decref(builder, offset_arr_type, wlcbk__uqfpl.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, wlcbk__uqfpl.
            null_bitmap)
        builder.store(builder.load(sxjcp__izzcl), ahgf__jfcz)
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
        dnmfe__yldc = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return dnmfe__yldc
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, ulydz__pphf, oirr__poi = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder, arr, sig
            .args[0])
        offsets = context.make_helper(builder, offset_arr_type, pzps__ahoe.
            offsets).data
        data = context.make_helper(builder, char_arr_type, pzps__ahoe.data
            ).data
        fuyy__egudl = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        mylvk__dtxex = cgutils.get_or_insert_function(builder.module,
            fuyy__egudl, name='setitem_string_array')
        ncw__umxjy = context.get_constant(types.int32, -1)
        chws__rik = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, pzps__ahoe
            .n_arrays)
        builder.call(mylvk__dtxex, [offsets, data, num_total_chars, builder
            .extract_value(ulydz__pphf, 0), oirr__poi, ncw__umxjy,
            chws__rik, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    fuyy__egudl = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    umrt__rqmhq = cgutils.get_or_insert_function(builder.module,
        fuyy__egudl, name='is_na')
    return builder.call(umrt__rqmhq, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        qzpn__triz, xqbb__tjjsz, mhvdh__ijq, jzcv__yjde = args
        cgutils.raw_memcpy(builder, qzpn__triz, xqbb__tjjsz, mhvdh__ijq,
            jzcv__yjde)
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
        hdw__ivqm, kxqda__egdm = unicode_to_utf8_and_len(val)
        vyy__ahg = getitem_str_offset(A, ind)
        mrba__emiu = getitem_str_offset(A, ind + 1)
        naj__vbzwu = mrba__emiu - vyy__ahg
        if naj__vbzwu != kxqda__egdm:
            return False
        ulydz__pphf = get_data_ptr_ind(A, vyy__ahg)
        return memcmp(ulydz__pphf, hdw__ivqm, kxqda__egdm) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        vyy__ahg = getitem_str_offset(A, ind)
        naj__vbzwu = bodo.libs.str_ext.int_to_str_len(val)
        wvt__hbpi = vyy__ahg + naj__vbzwu
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, vyy__ahg,
            wvt__hbpi)
        ulydz__pphf = get_data_ptr_ind(A, vyy__ahg)
        inplace_int64_to_str(ulydz__pphf, naj__vbzwu, val)
        setitem_str_offset(A, ind + 1, vyy__ahg + naj__vbzwu)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        ulydz__pphf, = args
        ckfz__hkzck = context.insert_const_string(builder.module, '<NA>')
        dizot__vey = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, ulydz__pphf, ckfz__hkzck, dizot__vey, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    porc__nynp = len('<NA>')

    def impl(A, ind):
        vyy__ahg = getitem_str_offset(A, ind)
        wvt__hbpi = vyy__ahg + porc__nynp
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data, vyy__ahg,
            wvt__hbpi)
        ulydz__pphf = get_data_ptr_ind(A, vyy__ahg)
        inplace_set_NA_str(ulydz__pphf)
        setitem_str_offset(A, ind + 1, vyy__ahg + porc__nynp)
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
            vyy__ahg = getitem_str_offset(A, ind)
            mrba__emiu = getitem_str_offset(A, ind + 1)
            oirr__poi = mrba__emiu - vyy__ahg
            ulydz__pphf = get_data_ptr_ind(A, vyy__ahg)
            yrz__ngt = decode_utf8(ulydz__pphf, oirr__poi)
            return yrz__ngt
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            dnmfe__yldc = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(dnmfe__yldc):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            mlkb__vkrvw = get_data_ptr(out_arr).data
            nwxrb__bfqvu = get_data_ptr(A).data
            cdbxk__smzup = 0
            ulj__zpzb = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(dnmfe__yldc):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    vto__lpuj = get_str_arr_item_length(A, i)
                    if vto__lpuj == 1:
                        copy_single_char(mlkb__vkrvw, ulj__zpzb,
                            nwxrb__bfqvu, getitem_str_offset(A, i))
                    else:
                        memcpy_region(mlkb__vkrvw, ulj__zpzb, nwxrb__bfqvu,
                            getitem_str_offset(A, i), vto__lpuj, 1)
                    ulj__zpzb += vto__lpuj
                    setitem_str_offset(out_arr, cdbxk__smzup + 1, ulj__zpzb)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, cdbxk__smzup)
                    else:
                        str_arr_set_not_na(out_arr, cdbxk__smzup)
                    cdbxk__smzup += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            dnmfe__yldc = len(ind)
            out_arr = pre_alloc_string_array(dnmfe__yldc, -1)
            cdbxk__smzup = 0
            for i in range(dnmfe__yldc):
                jgsxc__uunq = A[ind[i]]
                out_arr[cdbxk__smzup] = jgsxc__uunq
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, cdbxk__smzup)
                cdbxk__smzup += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            dnmfe__yldc = len(A)
            mma__opc = numba.cpython.unicode._normalize_slice(ind, dnmfe__yldc)
            gvai__fam = numba.cpython.unicode._slice_span(mma__opc)
            if mma__opc.step == 1:
                vyy__ahg = getitem_str_offset(A, mma__opc.start)
                mrba__emiu = getitem_str_offset(A, mma__opc.stop)
                n_chars = mrba__emiu - vyy__ahg
                qky__ihuig = pre_alloc_string_array(gvai__fam, np.int64(
                    n_chars))
                for i in range(gvai__fam):
                    qky__ihuig[i] = A[mma__opc.start + i]
                    if str_arr_is_na(A, mma__opc.start + i):
                        str_arr_set_na(qky__ihuig, i)
                return qky__ihuig
            else:
                qky__ihuig = pre_alloc_string_array(gvai__fam, -1)
                for i in range(gvai__fam):
                    qky__ihuig[i] = A[mma__opc.start + i * mma__opc.step]
                    if str_arr_is_na(A, mma__opc.start + i * mma__opc.step):
                        str_arr_set_na(qky__ihuig, i)
                return qky__ihuig
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
    ryiot__jpg = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(ryiot__jpg)
        joj__hcaum = 4

        def impl_scalar(A, idx, val):
            uknr__vrw = (val._length if val._is_ascii else joj__hcaum * val
                ._length)
            ntsrv__sxji = A._data
            vyy__ahg = np.int64(getitem_str_offset(A, idx))
            wvt__hbpi = vyy__ahg + uknr__vrw
            bodo.libs.array_item_arr_ext.ensure_data_capacity(ntsrv__sxji,
                vyy__ahg, wvt__hbpi)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                wvt__hbpi, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                mma__opc = numba.cpython.unicode._normalize_slice(idx, len(A))
                areqi__isoh = mma__opc.start
                ntsrv__sxji = A._data
                vyy__ahg = np.int64(getitem_str_offset(A, areqi__isoh))
                wvt__hbpi = vyy__ahg + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(ntsrv__sxji,
                    vyy__ahg, wvt__hbpi)
                set_string_array_range(A, val, areqi__isoh, vyy__ahg)
                hjsc__mcuav = 0
                for i in range(mma__opc.start, mma__opc.stop, mma__opc.step):
                    if str_arr_is_na(val, hjsc__mcuav):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    hjsc__mcuav += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                nsftc__arrpc = str_list_to_array(val)
                A[idx] = nsftc__arrpc
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                mma__opc = numba.cpython.unicode._normalize_slice(idx, len(A))
                for i in range(mma__opc.start, mma__opc.stop, mma__opc.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(ryiot__jpg)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                dnmfe__yldc = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(dnmfe__yldc, -1)
                for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
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
                dnmfe__yldc = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(dnmfe__yldc, -1)
                fgav__zxu = 0
                for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, fgav__zxu):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, fgav__zxu)
                        else:
                            out_arr[i] = str(val[fgav__zxu])
                        fgav__zxu += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(ryiot__jpg)
    raise BodoError(ryiot__jpg)


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
    rct__pisg = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(rct__pisg, (types.Float, types.Integer)
        ) and rct__pisg not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(rct__pisg, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            dnmfe__yldc = len(A)
            B = np.empty(dnmfe__yldc, rct__pisg)
            for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif rct__pisg == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            dnmfe__yldc = len(A)
            B = np.empty(dnmfe__yldc, rct__pisg)
            for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif rct__pisg == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            dnmfe__yldc = len(A)
            B = np.empty(dnmfe__yldc, rct__pisg)
            for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            dnmfe__yldc = len(A)
            B = np.empty(dnmfe__yldc, rct__pisg)
            for i in numba.parfors.parfor.internal_prange(dnmfe__yldc):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        ulydz__pphf, oirr__poi = args
        mrkyi__ltcay = context.get_python_api(builder)
        mbqc__qgnd = mrkyi__ltcay.string_from_string_and_size(ulydz__pphf,
            oirr__poi)
        sdpuu__uaea = mrkyi__ltcay.to_native_value(string_type, mbqc__qgnd
            ).value
        lbepf__jbll = cgutils.create_struct_proxy(string_type)(context,
            builder, sdpuu__uaea)
        lbepf__jbll.hash = lbepf__jbll.hash.type(-1)
        mrkyi__ltcay.decref(mbqc__qgnd)
        return lbepf__jbll._getvalue()
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
        boqnw__ruxo, arr, ind, det__rtyfa = args
        pzps__ahoe = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, pzps__ahoe.
            offsets).data
        data = context.make_helper(builder, char_arr_type, pzps__ahoe.data
            ).data
        fuyy__egudl = lir.FunctionType(lir.IntType(32), [boqnw__ruxo.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        ddwc__qmh = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            ddwc__qmh = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        oat__zau = cgutils.get_or_insert_function(builder.module,
            fuyy__egudl, ddwc__qmh)
        return builder.call(oat__zau, [boqnw__ruxo, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    luoej__mxc = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    fuyy__egudl = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(32)])
    ahh__fhubl = cgutils.get_or_insert_function(c.builder.module,
        fuyy__egudl, name='string_array_from_sequence')
    cnqa__pnfx = c.builder.call(ahh__fhubl, [val, luoej__mxc])
    srsa__kkhim = ArrayItemArrayType(char_arr_type)
    qnr__qrh = c.context.make_helper(c.builder, srsa__kkhim)
    qnr__qrh.meminfo = cnqa__pnfx
    loxth__qzyvt = c.context.make_helper(c.builder, typ)
    ntsrv__sxji = qnr__qrh._getvalue()
    loxth__qzyvt.data = ntsrv__sxji
    iyrah__rtq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(loxth__qzyvt._getvalue(), is_error=iyrah__rtq)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    dnmfe__yldc = len(pyval)
    ulj__zpzb = 0
    zle__oko = np.empty(dnmfe__yldc + 1, np_offset_type)
    wma__zlds = []
    epgoz__aaxb = np.empty(dnmfe__yldc + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        zle__oko[i] = ulj__zpzb
        aid__pdyx = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(epgoz__aaxb, i, int(not aid__pdyx)
            )
        if aid__pdyx:
            continue
        ewodx__ezhsy = list(s.encode()) if isinstance(s, str) else list(s)
        wma__zlds.extend(ewodx__ezhsy)
        ulj__zpzb += len(ewodx__ezhsy)
    zle__oko[dnmfe__yldc] = ulj__zpzb
    zgpw__eztb = np.array(wma__zlds, np.uint8)
    ybb__xvr = context.get_constant(types.int64, dnmfe__yldc)
    bpm__hpqdb = context.get_constant_generic(builder, char_arr_type,
        zgpw__eztb)
    qin__qfqi = context.get_constant_generic(builder, offset_arr_type, zle__oko
        )
    ovk__gtzhd = context.get_constant_generic(builder, null_bitmap_arr_type,
        epgoz__aaxb)
    pzps__ahoe = lir.Constant.literal_struct([ybb__xvr, bpm__hpqdb,
        qin__qfqi, ovk__gtzhd])
    pzps__ahoe = cgutils.global_constant(builder, '.const.payload', pzps__ahoe
        ).bitcast(cgutils.voidptr_t)
    wlm__roa = context.get_constant(types.int64, -1)
    gso__rpm = context.get_constant_null(types.voidptr)
    vch__qgurl = lir.Constant.literal_struct([wlm__roa, gso__rpm, gso__rpm,
        pzps__ahoe, wlm__roa])
    vch__qgurl = cgutils.global_constant(builder, '.const.meminfo', vch__qgurl
        ).bitcast(cgutils.voidptr_t)
    ntsrv__sxji = lir.Constant.literal_struct([vch__qgurl])
    loxth__qzyvt = lir.Constant.literal_struct([ntsrv__sxji])
    return loxth__qzyvt


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
