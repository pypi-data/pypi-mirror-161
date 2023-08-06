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
        hmolv__kqjiy = ArrayItemArrayType(char_arr_type)
        gbs__hipxp = [('data', hmolv__kqjiy)]
        models.StructModel.__init__(self, dmm, fe_type, gbs__hipxp)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        ogw__qwwfi, = args
        jdoup__jorg = context.make_helper(builder, string_array_type)
        jdoup__jorg.data = ogw__qwwfi
        context.nrt.incref(builder, data_typ, ogw__qwwfi)
        return jdoup__jorg._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    owza__euu = c.context.insert_const_string(c.builder.module, 'pandas')
    vvp__kmzua = c.pyapi.import_module_noblock(owza__euu)
    frnkg__ddlnl = c.pyapi.call_method(vvp__kmzua, 'StringDtype', ())
    c.pyapi.decref(vvp__kmzua)
    return frnkg__ddlnl


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        sfxxs__qwlub = bodo.libs.dict_arr_ext.get_binary_op_overload(op,
            lhs, rhs)
        if sfxxs__qwlub is not None:
            return sfxxs__qwlub
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                fty__zmtt = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(fty__zmtt)
                for i in numba.parfors.parfor.internal_prange(fty__zmtt):
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
                fty__zmtt = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(fty__zmtt)
                for i in numba.parfors.parfor.internal_prange(fty__zmtt):
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
                fty__zmtt = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(fty__zmtt)
                for i in numba.parfors.parfor.internal_prange(fty__zmtt):
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
    lwu__ztq = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    jer__lab = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and jer__lab or lwu__ztq and is_str_arr_type(rhs):

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
    lpbse__pznm = context.make_helper(builder, arr_typ, arr_value)
    hmolv__kqjiy = ArrayItemArrayType(char_arr_type)
    uyu__ujqts = _get_array_item_arr_payload(context, builder, hmolv__kqjiy,
        lpbse__pznm.data)
    return uyu__ujqts


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return uyu__ujqts.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        lpekr__hxti = context.make_helper(builder, offset_arr_type,
            uyu__ujqts.offsets).data
        return _get_num_total_chars(builder, lpekr__hxti, uyu__ujqts.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        nscfe__zdhd = context.make_helper(builder, offset_arr_type,
            uyu__ujqts.offsets)
        ndha__jsty = context.make_helper(builder, offset_ctypes_type)
        ndha__jsty.data = builder.bitcast(nscfe__zdhd.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        ndha__jsty.meminfo = nscfe__zdhd.meminfo
        frnkg__ddlnl = ndha__jsty._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            frnkg__ddlnl)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ogw__qwwfi = context.make_helper(builder, char_arr_type, uyu__ujqts
            .data)
        ndha__jsty = context.make_helper(builder, data_ctypes_type)
        ndha__jsty.data = ogw__qwwfi.data
        ndha__jsty.meminfo = ogw__qwwfi.meminfo
        frnkg__ddlnl = ndha__jsty._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            frnkg__ddlnl)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        nkv__hjcmi, ind = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            nkv__hjcmi, sig.args[0])
        ogw__qwwfi = context.make_helper(builder, char_arr_type, uyu__ujqts
            .data)
        ndha__jsty = context.make_helper(builder, data_ctypes_type)
        ndha__jsty.data = builder.gep(ogw__qwwfi.data, [ind])
        ndha__jsty.meminfo = ogw__qwwfi.meminfo
        frnkg__ddlnl = ndha__jsty._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            frnkg__ddlnl)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        uaaq__uxyl, clpy__fon, qsgw__wiqj, awjsf__fdzb = args
        nvwbp__capu = builder.bitcast(builder.gep(uaaq__uxyl, [clpy__fon]),
            lir.IntType(8).as_pointer())
        prql__xlgok = builder.bitcast(builder.gep(qsgw__wiqj, [awjsf__fdzb]
            ), lir.IntType(8).as_pointer())
        mdaa__zav = builder.load(prql__xlgok)
        builder.store(mdaa__zav, nvwbp__capu)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        gzd__dsif = context.make_helper(builder, null_bitmap_arr_type,
            uyu__ujqts.null_bitmap)
        ndha__jsty = context.make_helper(builder, data_ctypes_type)
        ndha__jsty.data = gzd__dsif.data
        ndha__jsty.meminfo = gzd__dsif.meminfo
        frnkg__ddlnl = ndha__jsty._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            frnkg__ddlnl)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        lpekr__hxti = context.make_helper(builder, offset_arr_type,
            uyu__ujqts.offsets).data
        return builder.load(builder.gep(lpekr__hxti, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, uyu__ujqts.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        rii__bxn, ind = args
        if in_bitmap_typ == data_ctypes_type:
            ndha__jsty = context.make_helper(builder, data_ctypes_type,
                rii__bxn)
            rii__bxn = ndha__jsty.data
        return builder.load(builder.gep(rii__bxn, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        rii__bxn, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            ndha__jsty = context.make_helper(builder, data_ctypes_type,
                rii__bxn)
            rii__bxn = ndha__jsty.data
        builder.store(val, builder.gep(rii__bxn, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        edgu__saf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        mcjrg__zicgs = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        dynre__qxmi = context.make_helper(builder, offset_arr_type,
            edgu__saf.offsets).data
        tyhnv__ahpp = context.make_helper(builder, offset_arr_type,
            mcjrg__zicgs.offsets).data
        apr__tymgn = context.make_helper(builder, char_arr_type, edgu__saf.data
            ).data
        nexwk__glau = context.make_helper(builder, char_arr_type,
            mcjrg__zicgs.data).data
        qqie__qonke = context.make_helper(builder, null_bitmap_arr_type,
            edgu__saf.null_bitmap).data
        rbgkc__mjncn = context.make_helper(builder, null_bitmap_arr_type,
            mcjrg__zicgs.null_bitmap).data
        mjwpp__gbc = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, tyhnv__ahpp, dynre__qxmi, mjwpp__gbc)
        cgutils.memcpy(builder, nexwk__glau, apr__tymgn, builder.load(
            builder.gep(dynre__qxmi, [ind])))
        busp__ufnz = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        klsog__fktkh = builder.lshr(busp__ufnz, lir.Constant(lir.IntType(64
            ), 3))
        cgutils.memcpy(builder, rbgkc__mjncn, qqie__qonke, klsog__fktkh)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        edgu__saf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        mcjrg__zicgs = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        dynre__qxmi = context.make_helper(builder, offset_arr_type,
            edgu__saf.offsets).data
        apr__tymgn = context.make_helper(builder, char_arr_type, edgu__saf.data
            ).data
        nexwk__glau = context.make_helper(builder, char_arr_type,
            mcjrg__zicgs.data).data
        num_total_chars = _get_num_total_chars(builder, dynre__qxmi,
            edgu__saf.n_arrays)
        cgutils.memcpy(builder, nexwk__glau, apr__tymgn, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        edgu__saf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        mcjrg__zicgs = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        dynre__qxmi = context.make_helper(builder, offset_arr_type,
            edgu__saf.offsets).data
        tyhnv__ahpp = context.make_helper(builder, offset_arr_type,
            mcjrg__zicgs.offsets).data
        qqie__qonke = context.make_helper(builder, null_bitmap_arr_type,
            edgu__saf.null_bitmap).data
        fty__zmtt = edgu__saf.n_arrays
        kvijg__dgq = context.get_constant(offset_type, 0)
        funcp__txq = cgutils.alloca_once_value(builder, kvijg__dgq)
        with cgutils.for_range(builder, fty__zmtt) as nfhx__sjrpl:
            ivy__gav = lower_is_na(context, builder, qqie__qonke,
                nfhx__sjrpl.index)
            with cgutils.if_likely(builder, builder.not_(ivy__gav)):
                optn__tuvmr = builder.load(builder.gep(dynre__qxmi, [
                    nfhx__sjrpl.index]))
                yjxs__woplt = builder.load(funcp__txq)
                builder.store(optn__tuvmr, builder.gep(tyhnv__ahpp, [
                    yjxs__woplt]))
                builder.store(builder.add(yjxs__woplt, lir.Constant(context
                    .get_value_type(offset_type), 1)), funcp__txq)
        yjxs__woplt = builder.load(funcp__txq)
        optn__tuvmr = builder.load(builder.gep(dynre__qxmi, [fty__zmtt]))
        builder.store(optn__tuvmr, builder.gep(tyhnv__ahpp, [yjxs__woplt]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        tgqw__rdw, ind, str, xmh__sau = args
        tgqw__rdw = context.make_array(sig.args[0])(context, builder, tgqw__rdw
            )
        tknj__xgv = builder.gep(tgqw__rdw.data, [ind])
        cgutils.raw_memcpy(builder, tknj__xgv, str, xmh__sau, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        tknj__xgv, ind, ohikn__nxntv, xmh__sau = args
        tknj__xgv = builder.gep(tknj__xgv, [ind])
        cgutils.raw_memcpy(builder, tknj__xgv, ohikn__nxntv, xmh__sau, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            xqpns__slp = A._data
            return np.int64(getitem_str_offset(xqpns__slp, idx + 1) -
                getitem_str_offset(xqpns__slp, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    ycfte__nqmon = np.int64(getitem_str_offset(A, i))
    mnl__skdj = np.int64(getitem_str_offset(A, i + 1))
    l = mnl__skdj - ycfte__nqmon
    nkki__ubkkn = get_data_ptr_ind(A, ycfte__nqmon)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(nkki__ubkkn, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    qmbyu__bosnf = getitem_str_offset(A, i)
    evp__gvus = getitem_str_offset(A, i + 1)
    muug__txf = evp__gvus - qmbyu__bosnf
    copn__qas = getitem_str_offset(B, j)
    wxdlo__ilva = copn__qas + muug__txf
    setitem_str_offset(B, j + 1, wxdlo__ilva)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if muug__txf != 0:
        ogw__qwwfi = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(ogw__qwwfi, np.
            int64(copn__qas), np.int64(wxdlo__ilva))
        oet__ashtu = get_data_ptr(B).data
        dzmrp__tfog = get_data_ptr(A).data
        memcpy_region(oet__ashtu, copn__qas, dzmrp__tfog, qmbyu__bosnf,
            muug__txf, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    fty__zmtt = len(str_arr)
    esyi__rhtwd = np.empty(fty__zmtt, np.bool_)
    for i in range(fty__zmtt):
        esyi__rhtwd[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return esyi__rhtwd


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            fty__zmtt = len(data)
            l = []
            for i in range(fty__zmtt):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        tpvnz__gcy = data.count
        hthn__jbr = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(tpvnz__gcy)]
        if is_overload_true(str_null_bools):
            hthn__jbr += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(tpvnz__gcy) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        cwax__sou = 'def f(data, str_null_bools=None):\n'
        cwax__sou += '  return ({}{})\n'.format(', '.join(hthn__jbr), ',' if
            tpvnz__gcy == 1 else '')
        rmyyu__mcuvo = {}
        exec(cwax__sou, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, rmyyu__mcuvo)
        wkv__cvot = rmyyu__mcuvo['f']
        return wkv__cvot
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                fty__zmtt = len(list_data)
                for i in range(fty__zmtt):
                    ohikn__nxntv = list_data[i]
                    str_arr[i] = ohikn__nxntv
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                fty__zmtt = len(list_data)
                for i in range(fty__zmtt):
                    ohikn__nxntv = list_data[i]
                    str_arr[i] = ohikn__nxntv
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        tpvnz__gcy = str_arr.count
        cxze__hao = 0
        cwax__sou = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(tpvnz__gcy):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                cwax__sou += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, tpvnz__gcy + cxze__hao))
                cxze__hao += 1
            else:
                cwax__sou += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        cwax__sou += '  return\n'
        rmyyu__mcuvo = {}
        exec(cwax__sou, {'cp_str_list_to_array': cp_str_list_to_array},
            rmyyu__mcuvo)
        dsdb__rckmt = rmyyu__mcuvo['f']
        return dsdb__rckmt
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            fty__zmtt = len(str_list)
            str_arr = pre_alloc_string_array(fty__zmtt, -1)
            for i in range(fty__zmtt):
                ohikn__nxntv = str_list[i]
                str_arr[i] = ohikn__nxntv
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            fty__zmtt = len(A)
            gcm__zqhb = 0
            for i in range(fty__zmtt):
                ohikn__nxntv = A[i]
                gcm__zqhb += get_utf8_size(ohikn__nxntv)
            return gcm__zqhb
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        fty__zmtt = len(arr)
        n_chars = num_total_chars(arr)
        ryzcj__zqtx = pre_alloc_string_array(fty__zmtt, np.int64(n_chars))
        copy_str_arr_slice(ryzcj__zqtx, arr, fty__zmtt)
        return ryzcj__zqtx
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
    cwax__sou = 'def f(in_seq):\n'
    cwax__sou += '    n_strs = len(in_seq)\n'
    cwax__sou += '    A = pre_alloc_string_array(n_strs, -1)\n'
    cwax__sou += '    return A\n'
    rmyyu__mcuvo = {}
    exec(cwax__sou, {'pre_alloc_string_array': pre_alloc_string_array},
        rmyyu__mcuvo)
    aph__epbho = rmyyu__mcuvo['f']
    return aph__epbho


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        svzga__kbll = 'pre_alloc_binary_array'
    else:
        svzga__kbll = 'pre_alloc_string_array'
    cwax__sou = 'def f(in_seq):\n'
    cwax__sou += '    n_strs = len(in_seq)\n'
    cwax__sou += f'    A = {svzga__kbll}(n_strs, -1)\n'
    cwax__sou += '    for i in range(n_strs):\n'
    cwax__sou += '        A[i] = in_seq[i]\n'
    cwax__sou += '    return A\n'
    rmyyu__mcuvo = {}
    exec(cwax__sou, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, rmyyu__mcuvo)
    aph__epbho = rmyyu__mcuvo['f']
    return aph__epbho


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        gnv__cvai = builder.add(uyu__ujqts.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        hiha__jdp = builder.lshr(lir.Constant(lir.IntType(64), offset_type.
            bitwidth), lir.Constant(lir.IntType(64), 3))
        klsog__fktkh = builder.mul(gnv__cvai, hiha__jdp)
        xen__lvsq = context.make_array(offset_arr_type)(context, builder,
            uyu__ujqts.offsets).data
        cgutils.memset(builder, xen__lvsq, klsog__fktkh, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        hmoma__iyrr = uyu__ujqts.n_arrays
        klsog__fktkh = builder.lshr(builder.add(hmoma__iyrr, lir.Constant(
            lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        yzel__kcgq = context.make_array(null_bitmap_arr_type)(context,
            builder, uyu__ujqts.null_bitmap).data
        cgutils.memset(builder, yzel__kcgq, klsog__fktkh, 0)
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
    nhhaw__tth = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        mnuc__wtwu = len(len_arr)
        for i in range(mnuc__wtwu):
            offsets[i] = nhhaw__tth
            nhhaw__tth += len_arr[i]
        offsets[mnuc__wtwu] = nhhaw__tth
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    azb__opo = i // 8
    qiply__dtqf = getitem_str_bitmap(bits, azb__opo)
    qiply__dtqf ^= np.uint8(-np.uint8(bit_is_set) ^ qiply__dtqf) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, azb__opo, qiply__dtqf)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    hus__hsju = get_null_bitmap_ptr(out_str_arr)
    wpi__rpnz = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        nzlo__iax = get_bit_bitmap(wpi__rpnz, j)
        set_bit_to(hus__hsju, out_start + j, nzlo__iax)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, nkv__hjcmi, gny__pjpyn, jigzu__fca = args
        edgu__saf = _get_str_binary_arr_payload(context, builder,
            nkv__hjcmi, string_array_type)
        mcjrg__zicgs = _get_str_binary_arr_payload(context, builder,
            out_arr, string_array_type)
        dynre__qxmi = context.make_helper(builder, offset_arr_type,
            edgu__saf.offsets).data
        tyhnv__ahpp = context.make_helper(builder, offset_arr_type,
            mcjrg__zicgs.offsets).data
        apr__tymgn = context.make_helper(builder, char_arr_type, edgu__saf.data
            ).data
        nexwk__glau = context.make_helper(builder, char_arr_type,
            mcjrg__zicgs.data).data
        num_total_chars = _get_num_total_chars(builder, dynre__qxmi,
            edgu__saf.n_arrays)
        jqykj__rzmat = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        rxgbn__qkaf = cgutils.get_or_insert_function(builder.module,
            jqykj__rzmat, name='set_string_array_range')
        builder.call(rxgbn__qkaf, [tyhnv__ahpp, nexwk__glau, dynre__qxmi,
            apr__tymgn, gny__pjpyn, jigzu__fca, edgu__saf.n_arrays,
            num_total_chars])
        dzqu__nbdqr = context.typing_context.resolve_value_type(
            copy_nulls_range)
        ali__wdx = dzqu__nbdqr.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        botbs__uayf = context.get_function(dzqu__nbdqr, ali__wdx)
        botbs__uayf(builder, (out_arr, nkv__hjcmi, gny__pjpyn))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    zod__jghz = c.context.make_helper(c.builder, typ, val)
    hmolv__kqjiy = ArrayItemArrayType(char_arr_type)
    uyu__ujqts = _get_array_item_arr_payload(c.context, c.builder,
        hmolv__kqjiy, zod__jghz.data)
    jlk__azg = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    zxdw__zgsv = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        zxdw__zgsv = 'pd_array_from_string_array'
    jqykj__rzmat = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    kms__oejj = cgutils.get_or_insert_function(c.builder.module,
        jqykj__rzmat, name=zxdw__zgsv)
    lpekr__hxti = c.context.make_array(offset_arr_type)(c.context, c.
        builder, uyu__ujqts.offsets).data
    nkki__ubkkn = c.context.make_array(char_arr_type)(c.context, c.builder,
        uyu__ujqts.data).data
    yzel__kcgq = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, uyu__ujqts.null_bitmap).data
    arr = c.builder.call(kms__oejj, [uyu__ujqts.n_arrays, lpekr__hxti,
        nkki__ubkkn, yzel__kcgq, jlk__azg])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        yzel__kcgq = context.make_array(null_bitmap_arr_type)(context,
            builder, uyu__ujqts.null_bitmap).data
        gwhww__detpj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        daivg__xdnge = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        qiply__dtqf = builder.load(builder.gep(yzel__kcgq, [gwhww__detpj],
            inbounds=True))
        wyozy__nvbv = lir.ArrayType(lir.IntType(8), 8)
        rwcvi__iseb = cgutils.alloca_once_value(builder, lir.Constant(
            wyozy__nvbv, (1, 2, 4, 8, 16, 32, 64, 128)))
        ukson__nhftd = builder.load(builder.gep(rwcvi__iseb, [lir.Constant(
            lir.IntType(64), 0), daivg__xdnge], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(qiply__dtqf,
            ukson__nhftd), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gwhww__detpj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        daivg__xdnge = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        yzel__kcgq = context.make_array(null_bitmap_arr_type)(context,
            builder, uyu__ujqts.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, uyu__ujqts.
            offsets).data
        hdrv__xbu = builder.gep(yzel__kcgq, [gwhww__detpj], inbounds=True)
        qiply__dtqf = builder.load(hdrv__xbu)
        wyozy__nvbv = lir.ArrayType(lir.IntType(8), 8)
        rwcvi__iseb = cgutils.alloca_once_value(builder, lir.Constant(
            wyozy__nvbv, (1, 2, 4, 8, 16, 32, 64, 128)))
        ukson__nhftd = builder.load(builder.gep(rwcvi__iseb, [lir.Constant(
            lir.IntType(64), 0), daivg__xdnge], inbounds=True))
        ukson__nhftd = builder.xor(ukson__nhftd, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(qiply__dtqf, ukson__nhftd), hdrv__xbu)
        if str_arr_typ == string_array_type:
            mwom__wzjv = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            pzf__edn = builder.icmp_unsigned('!=', mwom__wzjv, uyu__ujqts.
                n_arrays)
            with builder.if_then(pzf__edn):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [mwom__wzjv]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gwhww__detpj = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        daivg__xdnge = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        yzel__kcgq = context.make_array(null_bitmap_arr_type)(context,
            builder, uyu__ujqts.null_bitmap).data
        hdrv__xbu = builder.gep(yzel__kcgq, [gwhww__detpj], inbounds=True)
        qiply__dtqf = builder.load(hdrv__xbu)
        wyozy__nvbv = lir.ArrayType(lir.IntType(8), 8)
        rwcvi__iseb = cgutils.alloca_once_value(builder, lir.Constant(
            wyozy__nvbv, (1, 2, 4, 8, 16, 32, 64, 128)))
        ukson__nhftd = builder.load(builder.gep(rwcvi__iseb, [lir.Constant(
            lir.IntType(64), 0), daivg__xdnge], inbounds=True))
        builder.store(builder.or_(qiply__dtqf, ukson__nhftd), hdrv__xbu)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        klsog__fktkh = builder.udiv(builder.add(uyu__ujqts.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        yzel__kcgq = context.make_array(null_bitmap_arr_type)(context,
            builder, uyu__ujqts.null_bitmap).data
        cgutils.memset(builder, yzel__kcgq, klsog__fktkh, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    trep__nad = context.make_helper(builder, string_array_type, str_arr)
    hmolv__kqjiy = ArrayItemArrayType(char_arr_type)
    lpx__etqf = context.make_helper(builder, hmolv__kqjiy, trep__nad.data)
    czx__vxqni = ArrayItemArrayPayloadType(hmolv__kqjiy)
    hrzh__ewo = context.nrt.meminfo_data(builder, lpx__etqf.meminfo)
    ecx__wifi = builder.bitcast(hrzh__ewo, context.get_value_type(
        czx__vxqni).as_pointer())
    return ecx__wifi


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        otyix__jjz, wwjg__venj = args
        vahan__rcl = _get_str_binary_arr_data_payload_ptr(context, builder,
            wwjg__venj)
        auch__rnndc = _get_str_binary_arr_data_payload_ptr(context, builder,
            otyix__jjz)
        wman__guhhx = _get_str_binary_arr_payload(context, builder,
            wwjg__venj, sig.args[1])
        dib__emdo = _get_str_binary_arr_payload(context, builder,
            otyix__jjz, sig.args[0])
        context.nrt.incref(builder, char_arr_type, wman__guhhx.data)
        context.nrt.incref(builder, offset_arr_type, wman__guhhx.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, wman__guhhx.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, dib__emdo.data)
        context.nrt.decref(builder, offset_arr_type, dib__emdo.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, dib__emdo.null_bitmap
            )
        builder.store(builder.load(vahan__rcl), auch__rnndc)
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
        fty__zmtt = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return fty__zmtt
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, tknj__xgv, inqjo__yokyn = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder, arr, sig
            .args[0])
        offsets = context.make_helper(builder, offset_arr_type, uyu__ujqts.
            offsets).data
        data = context.make_helper(builder, char_arr_type, uyu__ujqts.data
            ).data
        jqykj__rzmat = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        nbiwu__rnles = cgutils.get_or_insert_function(builder.module,
            jqykj__rzmat, name='setitem_string_array')
        flhd__shqo = context.get_constant(types.int32, -1)
        mxuvv__rnvi = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, uyu__ujqts
            .n_arrays)
        builder.call(nbiwu__rnles, [offsets, data, num_total_chars, builder
            .extract_value(tknj__xgv, 0), inqjo__yokyn, flhd__shqo,
            mxuvv__rnvi, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    jqykj__rzmat = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    weyl__pvvj = cgutils.get_or_insert_function(builder.module,
        jqykj__rzmat, name='is_na')
    return builder.call(weyl__pvvj, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        nvwbp__capu, prql__xlgok, tpvnz__gcy, jqoe__sdq = args
        cgutils.raw_memcpy(builder, nvwbp__capu, prql__xlgok, tpvnz__gcy,
            jqoe__sdq)
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
        lhqcl__avrqy, vqhjz__guqgt = unicode_to_utf8_and_len(val)
        alf__vuvlb = getitem_str_offset(A, ind)
        nvsoj__tlxd = getitem_str_offset(A, ind + 1)
        djrjj__rsk = nvsoj__tlxd - alf__vuvlb
        if djrjj__rsk != vqhjz__guqgt:
            return False
        tknj__xgv = get_data_ptr_ind(A, alf__vuvlb)
        return memcmp(tknj__xgv, lhqcl__avrqy, vqhjz__guqgt) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        alf__vuvlb = getitem_str_offset(A, ind)
        djrjj__rsk = bodo.libs.str_ext.int_to_str_len(val)
        wakyw__bobnt = alf__vuvlb + djrjj__rsk
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            alf__vuvlb, wakyw__bobnt)
        tknj__xgv = get_data_ptr_ind(A, alf__vuvlb)
        inplace_int64_to_str(tknj__xgv, djrjj__rsk, val)
        setitem_str_offset(A, ind + 1, alf__vuvlb + djrjj__rsk)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        tknj__xgv, = args
        fkqth__ukle = context.insert_const_string(builder.module, '<NA>')
        mayf__ofqa = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, tknj__xgv, fkqth__ukle, mayf__ofqa, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    tksis__jmsgk = len('<NA>')

    def impl(A, ind):
        alf__vuvlb = getitem_str_offset(A, ind)
        wakyw__bobnt = alf__vuvlb + tksis__jmsgk
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            alf__vuvlb, wakyw__bobnt)
        tknj__xgv = get_data_ptr_ind(A, alf__vuvlb)
        inplace_set_NA_str(tknj__xgv)
        setitem_str_offset(A, ind + 1, alf__vuvlb + tksis__jmsgk)
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
            alf__vuvlb = getitem_str_offset(A, ind)
            nvsoj__tlxd = getitem_str_offset(A, ind + 1)
            inqjo__yokyn = nvsoj__tlxd - alf__vuvlb
            tknj__xgv = get_data_ptr_ind(A, alf__vuvlb)
            yed__yygfu = decode_utf8(tknj__xgv, inqjo__yokyn)
            return yed__yygfu
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            fty__zmtt = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(fty__zmtt):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            oet__ashtu = get_data_ptr(out_arr).data
            dzmrp__tfog = get_data_ptr(A).data
            cxze__hao = 0
            yjxs__woplt = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(fty__zmtt):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    sicx__qgmw = get_str_arr_item_length(A, i)
                    if sicx__qgmw == 1:
                        copy_single_char(oet__ashtu, yjxs__woplt,
                            dzmrp__tfog, getitem_str_offset(A, i))
                    else:
                        memcpy_region(oet__ashtu, yjxs__woplt, dzmrp__tfog,
                            getitem_str_offset(A, i), sicx__qgmw, 1)
                    yjxs__woplt += sicx__qgmw
                    setitem_str_offset(out_arr, cxze__hao + 1, yjxs__woplt)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, cxze__hao)
                    else:
                        str_arr_set_not_na(out_arr, cxze__hao)
                    cxze__hao += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            fty__zmtt = len(ind)
            out_arr = pre_alloc_string_array(fty__zmtt, -1)
            cxze__hao = 0
            for i in range(fty__zmtt):
                ohikn__nxntv = A[ind[i]]
                out_arr[cxze__hao] = ohikn__nxntv
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, cxze__hao)
                cxze__hao += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            fty__zmtt = len(A)
            lceb__fyues = numba.cpython.unicode._normalize_slice(ind, fty__zmtt
                )
            qap__xyeb = numba.cpython.unicode._slice_span(lceb__fyues)
            if lceb__fyues.step == 1:
                alf__vuvlb = getitem_str_offset(A, lceb__fyues.start)
                nvsoj__tlxd = getitem_str_offset(A, lceb__fyues.stop)
                n_chars = nvsoj__tlxd - alf__vuvlb
                ryzcj__zqtx = pre_alloc_string_array(qap__xyeb, np.int64(
                    n_chars))
                for i in range(qap__xyeb):
                    ryzcj__zqtx[i] = A[lceb__fyues.start + i]
                    if str_arr_is_na(A, lceb__fyues.start + i):
                        str_arr_set_na(ryzcj__zqtx, i)
                return ryzcj__zqtx
            else:
                ryzcj__zqtx = pre_alloc_string_array(qap__xyeb, -1)
                for i in range(qap__xyeb):
                    ryzcj__zqtx[i] = A[lceb__fyues.start + i * lceb__fyues.step
                        ]
                    if str_arr_is_na(A, lceb__fyues.start + i * lceb__fyues
                        .step):
                        str_arr_set_na(ryzcj__zqtx, i)
                return ryzcj__zqtx
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
    ajptt__zxaw = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(ajptt__zxaw)
        iarsk__zcso = 4

        def impl_scalar(A, idx, val):
            gbc__zkkrk = (val._length if val._is_ascii else iarsk__zcso *
                val._length)
            ogw__qwwfi = A._data
            alf__vuvlb = np.int64(getitem_str_offset(A, idx))
            wakyw__bobnt = alf__vuvlb + gbc__zkkrk
            bodo.libs.array_item_arr_ext.ensure_data_capacity(ogw__qwwfi,
                alf__vuvlb, wakyw__bobnt)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                wakyw__bobnt, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                lceb__fyues = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                ycfte__nqmon = lceb__fyues.start
                ogw__qwwfi = A._data
                alf__vuvlb = np.int64(getitem_str_offset(A, ycfte__nqmon))
                wakyw__bobnt = alf__vuvlb + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(ogw__qwwfi,
                    alf__vuvlb, wakyw__bobnt)
                set_string_array_range(A, val, ycfte__nqmon, alf__vuvlb)
                kcqb__bntx = 0
                for i in range(lceb__fyues.start, lceb__fyues.stop,
                    lceb__fyues.step):
                    if str_arr_is_na(val, kcqb__bntx):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    kcqb__bntx += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                dnt__ivkuo = str_list_to_array(val)
                A[idx] = dnt__ivkuo
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                lceb__fyues = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(lceb__fyues.start, lceb__fyues.stop,
                    lceb__fyues.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(ajptt__zxaw)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                fty__zmtt = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(fty__zmtt, -1)
                for i in numba.parfors.parfor.internal_prange(fty__zmtt):
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
                fty__zmtt = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(fty__zmtt, -1)
                brva__idpln = 0
                for i in numba.parfors.parfor.internal_prange(fty__zmtt):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, brva__idpln):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, brva__idpln)
                        else:
                            out_arr[i] = str(val[brva__idpln])
                        brva__idpln += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(ajptt__zxaw)
    raise BodoError(ajptt__zxaw)


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
    xtof__jzq = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(xtof__jzq, (types.Float, types.Integer)
        ) and xtof__jzq not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(xtof__jzq, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            fty__zmtt = len(A)
            B = np.empty(fty__zmtt, xtof__jzq)
            for i in numba.parfors.parfor.internal_prange(fty__zmtt):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif xtof__jzq == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            fty__zmtt = len(A)
            B = np.empty(fty__zmtt, xtof__jzq)
            for i in numba.parfors.parfor.internal_prange(fty__zmtt):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif xtof__jzq == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            fty__zmtt = len(A)
            B = np.empty(fty__zmtt, xtof__jzq)
            for i in numba.parfors.parfor.internal_prange(fty__zmtt):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            fty__zmtt = len(A)
            B = np.empty(fty__zmtt, xtof__jzq)
            for i in numba.parfors.parfor.internal_prange(fty__zmtt):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        tknj__xgv, inqjo__yokyn = args
        dssz__nnv = context.get_python_api(builder)
        bvvix__tlw = dssz__nnv.string_from_string_and_size(tknj__xgv,
            inqjo__yokyn)
        jjv__yfmdz = dssz__nnv.to_native_value(string_type, bvvix__tlw).value
        sgoa__wvqqs = cgutils.create_struct_proxy(string_type)(context,
            builder, jjv__yfmdz)
        sgoa__wvqqs.hash = sgoa__wvqqs.hash.type(-1)
        dssz__nnv.decref(bvvix__tlw)
        return sgoa__wvqqs._getvalue()
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
        ewoff__uvw, arr, ind, xmyie__bnw = args
        uyu__ujqts = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, uyu__ujqts.
            offsets).data
        data = context.make_helper(builder, char_arr_type, uyu__ujqts.data
            ).data
        jqykj__rzmat = lir.FunctionType(lir.IntType(32), [ewoff__uvw.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        hpvdo__jmyz = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            hpvdo__jmyz = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        dkv__pesio = cgutils.get_or_insert_function(builder.module,
            jqykj__rzmat, hpvdo__jmyz)
        return builder.call(dkv__pesio, [ewoff__uvw, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    jlk__azg = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    jqykj__rzmat = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(32)])
    psghk__yqrgd = cgutils.get_or_insert_function(c.builder.module,
        jqykj__rzmat, name='string_array_from_sequence')
    xerut__emy = c.builder.call(psghk__yqrgd, [val, jlk__azg])
    hmolv__kqjiy = ArrayItemArrayType(char_arr_type)
    lpx__etqf = c.context.make_helper(c.builder, hmolv__kqjiy)
    lpx__etqf.meminfo = xerut__emy
    trep__nad = c.context.make_helper(c.builder, typ)
    ogw__qwwfi = lpx__etqf._getvalue()
    trep__nad.data = ogw__qwwfi
    uqsi__wgzj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(trep__nad._getvalue(), is_error=uqsi__wgzj)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    fty__zmtt = len(pyval)
    yjxs__woplt = 0
    jpxsb__namk = np.empty(fty__zmtt + 1, np_offset_type)
    obru__kqv = []
    vcaeu__mzbvz = np.empty(fty__zmtt + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        jpxsb__namk[i] = yjxs__woplt
        vzvsc__ykhp = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(vcaeu__mzbvz, i, int(not
            vzvsc__ykhp))
        if vzvsc__ykhp:
            continue
        zsv__hlrgq = list(s.encode()) if isinstance(s, str) else list(s)
        obru__kqv.extend(zsv__hlrgq)
        yjxs__woplt += len(zsv__hlrgq)
    jpxsb__namk[fty__zmtt] = yjxs__woplt
    iim__iuhh = np.array(obru__kqv, np.uint8)
    dsnk__qyiu = context.get_constant(types.int64, fty__zmtt)
    jkdw__qcg = context.get_constant_generic(builder, char_arr_type, iim__iuhh)
    kxvhe__hken = context.get_constant_generic(builder, offset_arr_type,
        jpxsb__namk)
    nfgtl__atr = context.get_constant_generic(builder, null_bitmap_arr_type,
        vcaeu__mzbvz)
    uyu__ujqts = lir.Constant.literal_struct([dsnk__qyiu, jkdw__qcg,
        kxvhe__hken, nfgtl__atr])
    uyu__ujqts = cgutils.global_constant(builder, '.const.payload', uyu__ujqts
        ).bitcast(cgutils.voidptr_t)
    jhfko__zpjy = context.get_constant(types.int64, -1)
    wfpzn__jyv = context.get_constant_null(types.voidptr)
    hghfp__hmzhr = lir.Constant.literal_struct([jhfko__zpjy, wfpzn__jyv,
        wfpzn__jyv, uyu__ujqts, jhfko__zpjy])
    hghfp__hmzhr = cgutils.global_constant(builder, '.const.meminfo',
        hghfp__hmzhr).bitcast(cgutils.voidptr_t)
    ogw__qwwfi = lir.Constant.literal_struct([hghfp__hmzhr])
    trep__nad = lir.Constant.literal_struct([ogw__qwwfi])
    return trep__nad


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
