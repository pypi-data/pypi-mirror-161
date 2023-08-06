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
        adst__wnx = ArrayItemArrayType(char_arr_type)
        xurg__yugj = [('data', adst__wnx)]
        models.StructModel.__init__(self, dmm, fe_type, xurg__yugj)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')
lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        toe__bsmy, = args
        kjbuq__mynb = context.make_helper(builder, string_array_type)
        kjbuq__mynb.data = toe__bsmy
        context.nrt.incref(builder, data_typ, toe__bsmy)
        return kjbuq__mynb._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    pzmre__uni = c.context.insert_const_string(c.builder.module, 'pandas')
    gefm__yok = c.pyapi.import_module_noblock(pzmre__uni)
    mnzhg__jjqw = c.pyapi.call_method(gefm__yok, 'StringDtype', ())
    c.pyapi.decref(gefm__yok)
    return mnzhg__jjqw


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        qaf__blbvs = bodo.libs.dict_arr_ext.get_binary_op_overload(op, lhs, rhs
            )
        if qaf__blbvs is not None:
            return qaf__blbvs
        if is_str_arr_type(lhs) and is_str_arr_type(rhs):

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                hnxu__egbtq = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(hnxu__egbtq)
                for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
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
                hnxu__egbtq = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(hnxu__egbtq)
                for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
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
                hnxu__egbtq = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(hnxu__egbtq)
                for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
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
    cxsd__wpy = is_str_arr_type(lhs) or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    paak__fwvm = is_str_arr_type(rhs) or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if is_str_arr_type(lhs) and paak__fwvm or cxsd__wpy and is_str_arr_type(rhs
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
    yng__yrou = context.make_helper(builder, arr_typ, arr_value)
    adst__wnx = ArrayItemArrayType(char_arr_type)
    beda__qviuh = _get_array_item_arr_payload(context, builder, adst__wnx,
        yng__yrou.data)
    return beda__qviuh


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return beda__qviuh.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        orhh__cll = context.make_helper(builder, offset_arr_type,
            beda__qviuh.offsets).data
        return _get_num_total_chars(builder, orhh__cll, beda__qviuh.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kssbv__qguab = context.make_helper(builder, offset_arr_type,
            beda__qviuh.offsets)
        hisbg__bgeo = context.make_helper(builder, offset_ctypes_type)
        hisbg__bgeo.data = builder.bitcast(kssbv__qguab.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        hisbg__bgeo.meminfo = kssbv__qguab.meminfo
        mnzhg__jjqw = hisbg__bgeo._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            mnzhg__jjqw)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        toe__bsmy = context.make_helper(builder, char_arr_type, beda__qviuh
            .data)
        hisbg__bgeo = context.make_helper(builder, data_ctypes_type)
        hisbg__bgeo.data = toe__bsmy.data
        hisbg__bgeo.meminfo = toe__bsmy.meminfo
        mnzhg__jjqw = hisbg__bgeo._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            mnzhg__jjqw)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        zaiu__wva, ind = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            zaiu__wva, sig.args[0])
        toe__bsmy = context.make_helper(builder, char_arr_type, beda__qviuh
            .data)
        hisbg__bgeo = context.make_helper(builder, data_ctypes_type)
        hisbg__bgeo.data = builder.gep(toe__bsmy.data, [ind])
        hisbg__bgeo.meminfo = toe__bsmy.meminfo
        mnzhg__jjqw = hisbg__bgeo._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            mnzhg__jjqw)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        wwomp__eje, ohsec__heztz, vsbbj__pec, rlgqy__vht = args
        nwatx__ooo = builder.bitcast(builder.gep(wwomp__eje, [ohsec__heztz]
            ), lir.IntType(8).as_pointer())
        mil__xxkd = builder.bitcast(builder.gep(vsbbj__pec, [rlgqy__vht]),
            lir.IntType(8).as_pointer())
        hzeh__tab = builder.load(mil__xxkd)
        builder.store(hzeh__tab, nwatx__ooo)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qyaxk__dof = context.make_helper(builder, null_bitmap_arr_type,
            beda__qviuh.null_bitmap)
        hisbg__bgeo = context.make_helper(builder, data_ctypes_type)
        hisbg__bgeo.data = qyaxk__dof.data
        hisbg__bgeo.meminfo = qyaxk__dof.meminfo
        mnzhg__jjqw = hisbg__bgeo._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            mnzhg__jjqw)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        orhh__cll = context.make_helper(builder, offset_arr_type,
            beda__qviuh.offsets).data
        return builder.load(builder.gep(orhh__cll, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, beda__qviuh
            .offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        vmff__ugj, ind = args
        if in_bitmap_typ == data_ctypes_type:
            hisbg__bgeo = context.make_helper(builder, data_ctypes_type,
                vmff__ugj)
            vmff__ugj = hisbg__bgeo.data
        return builder.load(builder.gep(vmff__ugj, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        vmff__ugj, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            hisbg__bgeo = context.make_helper(builder, data_ctypes_type,
                vmff__ugj)
            vmff__ugj = hisbg__bgeo.data
        builder.store(val, builder.gep(vmff__ugj, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        mwh__eixpm = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ztrc__bnm = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wkhs__wtu = context.make_helper(builder, offset_arr_type,
            mwh__eixpm.offsets).data
        vtueq__lymxi = context.make_helper(builder, offset_arr_type,
            ztrc__bnm.offsets).data
        rja__dlic = context.make_helper(builder, char_arr_type, mwh__eixpm.data
            ).data
        cbif__xtto = context.make_helper(builder, char_arr_type, ztrc__bnm.data
            ).data
        lzdwq__zmose = context.make_helper(builder, null_bitmap_arr_type,
            mwh__eixpm.null_bitmap).data
        rbc__bldul = context.make_helper(builder, null_bitmap_arr_type,
            ztrc__bnm.null_bitmap).data
        xlev__ffzb = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, vtueq__lymxi, wkhs__wtu, xlev__ffzb)
        cgutils.memcpy(builder, cbif__xtto, rja__dlic, builder.load(builder
            .gep(wkhs__wtu, [ind])))
        icv__kqfh = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        rtkqm__usrvh = builder.lshr(icv__kqfh, lir.Constant(lir.IntType(64), 3)
            )
        cgutils.memcpy(builder, rbc__bldul, lzdwq__zmose, rtkqm__usrvh)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        mwh__eixpm = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ztrc__bnm = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wkhs__wtu = context.make_helper(builder, offset_arr_type,
            mwh__eixpm.offsets).data
        rja__dlic = context.make_helper(builder, char_arr_type, mwh__eixpm.data
            ).data
        cbif__xtto = context.make_helper(builder, char_arr_type, ztrc__bnm.data
            ).data
        num_total_chars = _get_num_total_chars(builder, wkhs__wtu,
            mwh__eixpm.n_arrays)
        cgutils.memcpy(builder, cbif__xtto, rja__dlic, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        mwh__eixpm = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ztrc__bnm = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wkhs__wtu = context.make_helper(builder, offset_arr_type,
            mwh__eixpm.offsets).data
        vtueq__lymxi = context.make_helper(builder, offset_arr_type,
            ztrc__bnm.offsets).data
        lzdwq__zmose = context.make_helper(builder, null_bitmap_arr_type,
            mwh__eixpm.null_bitmap).data
        hnxu__egbtq = mwh__eixpm.n_arrays
        dbl__qyr = context.get_constant(offset_type, 0)
        ohp__qikxm = cgutils.alloca_once_value(builder, dbl__qyr)
        with cgutils.for_range(builder, hnxu__egbtq) as jjne__qkg:
            oyo__jaxli = lower_is_na(context, builder, lzdwq__zmose,
                jjne__qkg.index)
            with cgutils.if_likely(builder, builder.not_(oyo__jaxli)):
                biwvx__pzut = builder.load(builder.gep(wkhs__wtu, [
                    jjne__qkg.index]))
                dscu__phta = builder.load(ohp__qikxm)
                builder.store(biwvx__pzut, builder.gep(vtueq__lymxi, [
                    dscu__phta]))
                builder.store(builder.add(dscu__phta, lir.Constant(context.
                    get_value_type(offset_type), 1)), ohp__qikxm)
        dscu__phta = builder.load(ohp__qikxm)
        biwvx__pzut = builder.load(builder.gep(wkhs__wtu, [hnxu__egbtq]))
        builder.store(biwvx__pzut, builder.gep(vtueq__lymxi, [dscu__phta]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        qugej__lwere, ind, str, ejja__sip = args
        qugej__lwere = context.make_array(sig.args[0])(context, builder,
            qugej__lwere)
        xavg__aji = builder.gep(qugej__lwere.data, [ind])
        cgutils.raw_memcpy(builder, xavg__aji, str, ejja__sip, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        xavg__aji, ind, prhc__beg, ejja__sip = args
        xavg__aji = builder.gep(xavg__aji, [ind])
        cgutils.raw_memcpy(builder, xavg__aji, prhc__beg, ejja__sip, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.generated_jit(nopython=True)
def get_str_arr_item_length(A, i):
    if A == bodo.dict_str_arr_type:

        def impl(A, i):
            idx = A._indices[i]
            dlv__xwyr = A._data
            return np.int64(getitem_str_offset(dlv__xwyr, idx + 1) -
                getitem_str_offset(dlv__xwyr, idx))
        return impl
    else:
        return lambda A, i: np.int64(getitem_str_offset(A, i + 1) -
            getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    cyp__jxvj = np.int64(getitem_str_offset(A, i))
    dhrr__cou = np.int64(getitem_str_offset(A, i + 1))
    l = dhrr__cou - cyp__jxvj
    otinl__mzunm = get_data_ptr_ind(A, cyp__jxvj)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(otinl__mzunm, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    wrw__jdrb = getitem_str_offset(A, i)
    nfkg__xcdcv = getitem_str_offset(A, i + 1)
    bfkdq__mdnku = nfkg__xcdcv - wrw__jdrb
    fjul__eae = getitem_str_offset(B, j)
    piz__lprwu = fjul__eae + bfkdq__mdnku
    setitem_str_offset(B, j + 1, piz__lprwu)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if bfkdq__mdnku != 0:
        toe__bsmy = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(toe__bsmy, np.
            int64(fjul__eae), np.int64(piz__lprwu))
        zto__cafx = get_data_ptr(B).data
        jlcs__ufich = get_data_ptr(A).data
        memcpy_region(zto__cafx, fjul__eae, jlcs__ufich, wrw__jdrb,
            bfkdq__mdnku, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    hnxu__egbtq = len(str_arr)
    cioup__qqnqe = np.empty(hnxu__egbtq, np.bool_)
    for i in range(hnxu__egbtq):
        cioup__qqnqe[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return cioup__qqnqe


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if is_str_arr_type(data) or data == binary_array_type:

        def to_list_impl(data, str_null_bools=None):
            hnxu__egbtq = len(data)
            l = []
            for i in range(hnxu__egbtq):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        grd__zffiv = data.count
        xezqk__iktt = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(grd__zffiv)]
        if is_overload_true(str_null_bools):
            xezqk__iktt += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(grd__zffiv) if is_str_arr_type(data.types[i]) or data
                .types[i] == binary_array_type]
        fnb__wzlpv = 'def f(data, str_null_bools=None):\n'
        fnb__wzlpv += '  return ({}{})\n'.format(', '.join(xezqk__iktt), 
            ',' if grd__zffiv == 1 else '')
        aiem__saaa = {}
        exec(fnb__wzlpv, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, aiem__saaa)
        nbby__ncuan = aiem__saaa['f']
        return nbby__ncuan
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                hnxu__egbtq = len(list_data)
                for i in range(hnxu__egbtq):
                    prhc__beg = list_data[i]
                    str_arr[i] = prhc__beg
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                hnxu__egbtq = len(list_data)
                for i in range(hnxu__egbtq):
                    prhc__beg = list_data[i]
                    str_arr[i] = prhc__beg
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        grd__zffiv = str_arr.count
        xii__xtw = 0
        fnb__wzlpv = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(grd__zffiv):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                fnb__wzlpv += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, grd__zffiv + xii__xtw))
                xii__xtw += 1
            else:
                fnb__wzlpv += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        fnb__wzlpv += '  return\n'
        aiem__saaa = {}
        exec(fnb__wzlpv, {'cp_str_list_to_array': cp_str_list_to_array},
            aiem__saaa)
        alps__lgpe = aiem__saaa['f']
        return alps__lgpe
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            hnxu__egbtq = len(str_list)
            str_arr = pre_alloc_string_array(hnxu__egbtq, -1)
            for i in range(hnxu__egbtq):
                prhc__beg = str_list[i]
                str_arr[i] = prhc__beg
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            hnxu__egbtq = len(A)
            shqco__tougu = 0
            for i in range(hnxu__egbtq):
                prhc__beg = A[i]
                shqco__tougu += get_utf8_size(prhc__beg)
            return shqco__tougu
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        hnxu__egbtq = len(arr)
        n_chars = num_total_chars(arr)
        zoc__ehcdt = pre_alloc_string_array(hnxu__egbtq, np.int64(n_chars))
        copy_str_arr_slice(zoc__ehcdt, arr, hnxu__egbtq)
        return zoc__ehcdt
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
    fnb__wzlpv = 'def f(in_seq):\n'
    fnb__wzlpv += '    n_strs = len(in_seq)\n'
    fnb__wzlpv += '    A = pre_alloc_string_array(n_strs, -1)\n'
    fnb__wzlpv += '    return A\n'
    aiem__saaa = {}
    exec(fnb__wzlpv, {'pre_alloc_string_array': pre_alloc_string_array},
        aiem__saaa)
    phugf__qbi = aiem__saaa['f']
    return phugf__qbi


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    in_seq = types.unliteral(in_seq)
    if in_seq.dtype == bodo.bytes_type:
        gaul__gvnh = 'pre_alloc_binary_array'
    else:
        gaul__gvnh = 'pre_alloc_string_array'
    fnb__wzlpv = 'def f(in_seq):\n'
    fnb__wzlpv += '    n_strs = len(in_seq)\n'
    fnb__wzlpv += f'    A = {gaul__gvnh}(n_strs, -1)\n'
    fnb__wzlpv += '    for i in range(n_strs):\n'
    fnb__wzlpv += '        A[i] = in_seq[i]\n'
    fnb__wzlpv += '    return A\n'
    aiem__saaa = {}
    exec(fnb__wzlpv, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, aiem__saaa)
    phugf__qbi = aiem__saaa['f']
    return phugf__qbi


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        vxts__gckc = builder.add(beda__qviuh.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        uzak__hdm = builder.lshr(lir.Constant(lir.IntType(64), offset_type.
            bitwidth), lir.Constant(lir.IntType(64), 3))
        rtkqm__usrvh = builder.mul(vxts__gckc, uzak__hdm)
        iqwf__nhaop = context.make_array(offset_arr_type)(context, builder,
            beda__qviuh.offsets).data
        cgutils.memset(builder, iqwf__nhaop, rtkqm__usrvh, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        zpns__lyiu = beda__qviuh.n_arrays
        rtkqm__usrvh = builder.lshr(builder.add(zpns__lyiu, lir.Constant(
            lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        sbsrg__hmjj = context.make_array(null_bitmap_arr_type)(context,
            builder, beda__qviuh.null_bitmap).data
        cgutils.memset(builder, sbsrg__hmjj, rtkqm__usrvh, 0)
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
    puxx__zdgtm = 0
    if total_len == 0:
        for i in range(len(offsets)):
            offsets[i] = 0
    else:
        udx__nfbp = len(len_arr)
        for i in range(udx__nfbp):
            offsets[i] = puxx__zdgtm
            puxx__zdgtm += len_arr[i]
        offsets[udx__nfbp] = puxx__zdgtm
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    vqu__vgpu = i // 8
    uibgd__lbir = getitem_str_bitmap(bits, vqu__vgpu)
    uibgd__lbir ^= np.uint8(-np.uint8(bit_is_set) ^ uibgd__lbir) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, vqu__vgpu, uibgd__lbir)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    aps__qkqnb = get_null_bitmap_ptr(out_str_arr)
    uugos__zlk = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        tfemo__iabf = get_bit_bitmap(uugos__zlk, j)
        set_bit_to(aps__qkqnb, out_start + j, tfemo__iabf)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, zaiu__wva, ryuma__eqc, meou__kqsa = args
        mwh__eixpm = _get_str_binary_arr_payload(context, builder,
            zaiu__wva, string_array_type)
        ztrc__bnm = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        wkhs__wtu = context.make_helper(builder, offset_arr_type,
            mwh__eixpm.offsets).data
        vtueq__lymxi = context.make_helper(builder, offset_arr_type,
            ztrc__bnm.offsets).data
        rja__dlic = context.make_helper(builder, char_arr_type, mwh__eixpm.data
            ).data
        cbif__xtto = context.make_helper(builder, char_arr_type, ztrc__bnm.data
            ).data
        num_total_chars = _get_num_total_chars(builder, wkhs__wtu,
            mwh__eixpm.n_arrays)
        mxo__jgsxr = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        cluh__ohkhm = cgutils.get_or_insert_function(builder.module,
            mxo__jgsxr, name='set_string_array_range')
        builder.call(cluh__ohkhm, [vtueq__lymxi, cbif__xtto, wkhs__wtu,
            rja__dlic, ryuma__eqc, meou__kqsa, mwh__eixpm.n_arrays,
            num_total_chars])
        mmnc__xbd = context.typing_context.resolve_value_type(copy_nulls_range)
        vroyf__dyg = mmnc__xbd.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        cgx__pzj = context.get_function(mmnc__xbd, vroyf__dyg)
        cgx__pzj(builder, (out_arr, zaiu__wva, ryuma__eqc))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    nxs__mjp = c.context.make_helper(c.builder, typ, val)
    adst__wnx = ArrayItemArrayType(char_arr_type)
    beda__qviuh = _get_array_item_arr_payload(c.context, c.builder,
        adst__wnx, nxs__mjp.data)
    zmpc__hujql = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    vqcv__lrcn = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        vqcv__lrcn = 'pd_array_from_string_array'
    mxo__jgsxr = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    arc__rin = cgutils.get_or_insert_function(c.builder.module, mxo__jgsxr,
        name=vqcv__lrcn)
    orhh__cll = c.context.make_array(offset_arr_type)(c.context, c.builder,
        beda__qviuh.offsets).data
    otinl__mzunm = c.context.make_array(char_arr_type)(c.context, c.builder,
        beda__qviuh.data).data
    sbsrg__hmjj = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, beda__qviuh.null_bitmap).data
    arr = c.builder.call(arc__rin, [beda__qviuh.n_arrays, orhh__cll,
        otinl__mzunm, sbsrg__hmjj, zmpc__hujql])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        sbsrg__hmjj = context.make_array(null_bitmap_arr_type)(context,
            builder, beda__qviuh.null_bitmap).data
        gpfuc__zgro = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        vny__oun = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        uibgd__lbir = builder.load(builder.gep(sbsrg__hmjj, [gpfuc__zgro],
            inbounds=True))
        xqj__tmo = lir.ArrayType(lir.IntType(8), 8)
        nqyro__aims = cgutils.alloca_once_value(builder, lir.Constant(
            xqj__tmo, (1, 2, 4, 8, 16, 32, 64, 128)))
        wzkic__bdmbg = builder.load(builder.gep(nqyro__aims, [lir.Constant(
            lir.IntType(64), 0), vny__oun], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(uibgd__lbir,
            wzkic__bdmbg), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gpfuc__zgro = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        vny__oun = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        sbsrg__hmjj = context.make_array(null_bitmap_arr_type)(context,
            builder, beda__qviuh.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, beda__qviuh
            .offsets).data
        zivw__pufmi = builder.gep(sbsrg__hmjj, [gpfuc__zgro], inbounds=True)
        uibgd__lbir = builder.load(zivw__pufmi)
        xqj__tmo = lir.ArrayType(lir.IntType(8), 8)
        nqyro__aims = cgutils.alloca_once_value(builder, lir.Constant(
            xqj__tmo, (1, 2, 4, 8, 16, 32, 64, 128)))
        wzkic__bdmbg = builder.load(builder.gep(nqyro__aims, [lir.Constant(
            lir.IntType(64), 0), vny__oun], inbounds=True))
        wzkic__bdmbg = builder.xor(wzkic__bdmbg, lir.Constant(lir.IntType(8
            ), -1))
        builder.store(builder.and_(uibgd__lbir, wzkic__bdmbg), zivw__pufmi)
        if str_arr_typ == string_array_type:
            lpcp__vgl = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            drny__vpe = builder.icmp_unsigned('!=', lpcp__vgl, beda__qviuh.
                n_arrays)
            with builder.if_then(drny__vpe):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [lpcp__vgl]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        gpfuc__zgro = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        vny__oun = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        sbsrg__hmjj = context.make_array(null_bitmap_arr_type)(context,
            builder, beda__qviuh.null_bitmap).data
        zivw__pufmi = builder.gep(sbsrg__hmjj, [gpfuc__zgro], inbounds=True)
        uibgd__lbir = builder.load(zivw__pufmi)
        xqj__tmo = lir.ArrayType(lir.IntType(8), 8)
        nqyro__aims = cgutils.alloca_once_value(builder, lir.Constant(
            xqj__tmo, (1, 2, 4, 8, 16, 32, 64, 128)))
        wzkic__bdmbg = builder.load(builder.gep(nqyro__aims, [lir.Constant(
            lir.IntType(64), 0), vny__oun], inbounds=True))
        builder.store(builder.or_(uibgd__lbir, wzkic__bdmbg), zivw__pufmi)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        rtkqm__usrvh = builder.udiv(builder.add(beda__qviuh.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        sbsrg__hmjj = context.make_array(null_bitmap_arr_type)(context,
            builder, beda__qviuh.null_bitmap).data
        cgutils.memset(builder, sbsrg__hmjj, rtkqm__usrvh, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    ttqoz__gwlj = context.make_helper(builder, string_array_type, str_arr)
    adst__wnx = ArrayItemArrayType(char_arr_type)
    qwexf__hod = context.make_helper(builder, adst__wnx, ttqoz__gwlj.data)
    ste__qnst = ArrayItemArrayPayloadType(adst__wnx)
    fatm__zpe = context.nrt.meminfo_data(builder, qwexf__hod.meminfo)
    arfhq__oujjq = builder.bitcast(fatm__zpe, context.get_value_type(
        ste__qnst).as_pointer())
    return arfhq__oujjq


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        xoy__bjnz, dqry__gub = args
        xqpj__aylbr = _get_str_binary_arr_data_payload_ptr(context, builder,
            dqry__gub)
        klk__aguet = _get_str_binary_arr_data_payload_ptr(context, builder,
            xoy__bjnz)
        xfif__cbpv = _get_str_binary_arr_payload(context, builder,
            dqry__gub, sig.args[1])
        knq__kyn = _get_str_binary_arr_payload(context, builder, xoy__bjnz,
            sig.args[0])
        context.nrt.incref(builder, char_arr_type, xfif__cbpv.data)
        context.nrt.incref(builder, offset_arr_type, xfif__cbpv.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, xfif__cbpv.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, knq__kyn.data)
        context.nrt.decref(builder, offset_arr_type, knq__kyn.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, knq__kyn.null_bitmap)
        builder.store(builder.load(xqpj__aylbr), klk__aguet)
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
        hnxu__egbtq = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return hnxu__egbtq
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, xavg__aji, xcq__owprn = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder, arr,
            sig.args[0])
        offsets = context.make_helper(builder, offset_arr_type, beda__qviuh
            .offsets).data
        data = context.make_helper(builder, char_arr_type, beda__qviuh.data
            ).data
        mxo__jgsxr = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        fctnj__yhnh = cgutils.get_or_insert_function(builder.module,
            mxo__jgsxr, name='setitem_string_array')
        fsbx__mjdm = context.get_constant(types.int32, -1)
        csts__llqa = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets,
            beda__qviuh.n_arrays)
        builder.call(fctnj__yhnh, [offsets, data, num_total_chars, builder.
            extract_value(xavg__aji, 0), xcq__owprn, fsbx__mjdm, csts__llqa,
            ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    mxo__jgsxr = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    ovprc__jro = cgutils.get_or_insert_function(builder.module, mxo__jgsxr,
        name='is_na')
    return builder.call(ovprc__jro, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        nwatx__ooo, mil__xxkd, grd__zffiv, rzi__zodn = args
        cgutils.raw_memcpy(builder, nwatx__ooo, mil__xxkd, grd__zffiv,
            rzi__zodn)
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
        sgu__cvf, grzz__gwf = unicode_to_utf8_and_len(val)
        xcywj__cclwz = getitem_str_offset(A, ind)
        rmfp__njsc = getitem_str_offset(A, ind + 1)
        jyc__nwtll = rmfp__njsc - xcywj__cclwz
        if jyc__nwtll != grzz__gwf:
            return False
        xavg__aji = get_data_ptr_ind(A, xcywj__cclwz)
        return memcmp(xavg__aji, sgu__cvf, grzz__gwf) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        xcywj__cclwz = getitem_str_offset(A, ind)
        jyc__nwtll = bodo.libs.str_ext.int_to_str_len(val)
        huy__xfv = xcywj__cclwz + jyc__nwtll
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            xcywj__cclwz, huy__xfv)
        xavg__aji = get_data_ptr_ind(A, xcywj__cclwz)
        inplace_int64_to_str(xavg__aji, jyc__nwtll, val)
        setitem_str_offset(A, ind + 1, xcywj__cclwz + jyc__nwtll)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        xavg__aji, = args
        nreso__bzjzo = context.insert_const_string(builder.module, '<NA>')
        pmq__jwl = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, xavg__aji, nreso__bzjzo, pmq__jwl, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    rgl__lpcmh = len('<NA>')

    def impl(A, ind):
        xcywj__cclwz = getitem_str_offset(A, ind)
        huy__xfv = xcywj__cclwz + rgl__lpcmh
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            xcywj__cclwz, huy__xfv)
        xavg__aji = get_data_ptr_ind(A, xcywj__cclwz)
        inplace_set_NA_str(xavg__aji)
        setitem_str_offset(A, ind + 1, xcywj__cclwz + rgl__lpcmh)
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
            xcywj__cclwz = getitem_str_offset(A, ind)
            rmfp__njsc = getitem_str_offset(A, ind + 1)
            xcq__owprn = rmfp__njsc - xcywj__cclwz
            xavg__aji = get_data_ptr_ind(A, xcywj__cclwz)
            xlmtd__viv = decode_utf8(xavg__aji, xcq__owprn)
            return xlmtd__viv
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            hnxu__egbtq = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(hnxu__egbtq):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            zto__cafx = get_data_ptr(out_arr).data
            jlcs__ufich = get_data_ptr(A).data
            xii__xtw = 0
            dscu__phta = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(hnxu__egbtq):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    itngy__mem = get_str_arr_item_length(A, i)
                    if itngy__mem == 1:
                        copy_single_char(zto__cafx, dscu__phta, jlcs__ufich,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(zto__cafx, dscu__phta, jlcs__ufich,
                            getitem_str_offset(A, i), itngy__mem, 1)
                    dscu__phta += itngy__mem
                    setitem_str_offset(out_arr, xii__xtw + 1, dscu__phta)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, xii__xtw)
                    else:
                        str_arr_set_not_na(out_arr, xii__xtw)
                    xii__xtw += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            hnxu__egbtq = len(ind)
            out_arr = pre_alloc_string_array(hnxu__egbtq, -1)
            xii__xtw = 0
            for i in range(hnxu__egbtq):
                prhc__beg = A[ind[i]]
                out_arr[xii__xtw] = prhc__beg
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, xii__xtw)
                xii__xtw += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            hnxu__egbtq = len(A)
            xno__cepa = numba.cpython.unicode._normalize_slice(ind, hnxu__egbtq
                )
            gew__lxkws = numba.cpython.unicode._slice_span(xno__cepa)
            if xno__cepa.step == 1:
                xcywj__cclwz = getitem_str_offset(A, xno__cepa.start)
                rmfp__njsc = getitem_str_offset(A, xno__cepa.stop)
                n_chars = rmfp__njsc - xcywj__cclwz
                zoc__ehcdt = pre_alloc_string_array(gew__lxkws, np.int64(
                    n_chars))
                for i in range(gew__lxkws):
                    zoc__ehcdt[i] = A[xno__cepa.start + i]
                    if str_arr_is_na(A, xno__cepa.start + i):
                        str_arr_set_na(zoc__ehcdt, i)
                return zoc__ehcdt
            else:
                zoc__ehcdt = pre_alloc_string_array(gew__lxkws, -1)
                for i in range(gew__lxkws):
                    zoc__ehcdt[i] = A[xno__cepa.start + i * xno__cepa.step]
                    if str_arr_is_na(A, xno__cepa.start + i * xno__cepa.step):
                        str_arr_set_na(zoc__ehcdt, i)
                return zoc__ehcdt
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
    wrzee__ubhke = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(wrzee__ubhke)
        tfu__iym = 4

        def impl_scalar(A, idx, val):
            guq__xdrj = (val._length if val._is_ascii else tfu__iym * val.
                _length)
            toe__bsmy = A._data
            xcywj__cclwz = np.int64(getitem_str_offset(A, idx))
            huy__xfv = xcywj__cclwz + guq__xdrj
            bodo.libs.array_item_arr_ext.ensure_data_capacity(toe__bsmy,
                xcywj__cclwz, huy__xfv)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                huy__xfv, val._data, val._length, val._kind, val._is_ascii, idx
                )
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                xno__cepa = numba.cpython.unicode._normalize_slice(idx, len(A))
                cyp__jxvj = xno__cepa.start
                toe__bsmy = A._data
                xcywj__cclwz = np.int64(getitem_str_offset(A, cyp__jxvj))
                huy__xfv = xcywj__cclwz + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(toe__bsmy,
                    xcywj__cclwz, huy__xfv)
                set_string_array_range(A, val, cyp__jxvj, xcywj__cclwz)
                tivcc__ovxs = 0
                for i in range(xno__cepa.start, xno__cepa.stop, xno__cepa.step
                    ):
                    if str_arr_is_na(val, tivcc__ovxs):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    tivcc__ovxs += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                btujw__fpgl = str_list_to_array(val)
                A[idx] = btujw__fpgl
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                xno__cepa = numba.cpython.unicode._normalize_slice(idx, len(A))
                for i in range(xno__cepa.start, xno__cepa.stop, xno__cepa.step
                    ):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(wrzee__ubhke)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                hnxu__egbtq = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(hnxu__egbtq, -1)
                for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
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
                hnxu__egbtq = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(hnxu__egbtq, -1)
                wpks__eqh = 0
                for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, wpks__eqh):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, wpks__eqh)
                        else:
                            out_arr[i] = str(val[wpks__eqh])
                        wpks__eqh += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(wrzee__ubhke)
    raise BodoError(wrzee__ubhke)


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
    nvg__jroa = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(nvg__jroa, (types.Float, types.Integer)
        ) and nvg__jroa not in (types.bool_, bodo.libs.bool_arr_ext.
        boolean_dtype):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(nvg__jroa, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            hnxu__egbtq = len(A)
            B = np.empty(hnxu__egbtq, nvg__jroa)
            for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    elif nvg__jroa == types.bool_:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            hnxu__egbtq = len(A)
            B = np.empty(hnxu__egbtq, nvg__jroa)
            for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = False
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    elif nvg__jroa == bodo.libs.bool_arr_ext.boolean_dtype:

        def impl_bool(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            hnxu__egbtq = len(A)
            B = np.empty(hnxu__egbtq, nvg__jroa)
            for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
                if bodo.libs.array_kernels.isna(A, i):
                    bodo.libs.array_kernels.setna(B, i)
                else:
                    B[i] = bool(A[i])
            return B
        return impl_bool
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            hnxu__egbtq = len(A)
            B = np.empty(hnxu__egbtq, nvg__jroa)
            for i in numba.parfors.parfor.internal_prange(hnxu__egbtq):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        xavg__aji, xcq__owprn = args
        nzy__mjll = context.get_python_api(builder)
        vteei__zlv = nzy__mjll.string_from_string_and_size(xavg__aji,
            xcq__owprn)
        sjpx__yalrf = nzy__mjll.to_native_value(string_type, vteei__zlv).value
        rhlj__wrkmi = cgutils.create_struct_proxy(string_type)(context,
            builder, sjpx__yalrf)
        rhlj__wrkmi.hash = rhlj__wrkmi.hash.type(-1)
        nzy__mjll.decref(vteei__zlv)
        return rhlj__wrkmi._getvalue()
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
        fjj__axlpg, arr, ind, idpv__tidu = args
        beda__qviuh = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, beda__qviuh
            .offsets).data
        data = context.make_helper(builder, char_arr_type, beda__qviuh.data
            ).data
        mxo__jgsxr = lir.FunctionType(lir.IntType(32), [fjj__axlpg.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        odow__silc = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            odow__silc = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        fcgkj__glan = cgutils.get_or_insert_function(builder.module,
            mxo__jgsxr, odow__silc)
        return builder.call(fcgkj__glan, [fjj__axlpg, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    zmpc__hujql = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    mxo__jgsxr = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    lxccz__inu = cgutils.get_or_insert_function(c.builder.module,
        mxo__jgsxr, name='string_array_from_sequence')
    obylx__emei = c.builder.call(lxccz__inu, [val, zmpc__hujql])
    adst__wnx = ArrayItemArrayType(char_arr_type)
    qwexf__hod = c.context.make_helper(c.builder, adst__wnx)
    qwexf__hod.meminfo = obylx__emei
    ttqoz__gwlj = c.context.make_helper(c.builder, typ)
    toe__bsmy = qwexf__hod._getvalue()
    ttqoz__gwlj.data = toe__bsmy
    rhque__uph = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ttqoz__gwlj._getvalue(), is_error=rhque__uph)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    hnxu__egbtq = len(pyval)
    dscu__phta = 0
    hlu__eny = np.empty(hnxu__egbtq + 1, np_offset_type)
    jzu__hibo = []
    ikzm__lvq = np.empty(hnxu__egbtq + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        hlu__eny[i] = dscu__phta
        kmw__lhuax = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ikzm__lvq, i, int(not kmw__lhuax))
        if kmw__lhuax:
            continue
        xhmrn__uvbxn = list(s.encode()) if isinstance(s, str) else list(s)
        jzu__hibo.extend(xhmrn__uvbxn)
        dscu__phta += len(xhmrn__uvbxn)
    hlu__eny[hnxu__egbtq] = dscu__phta
    vnty__vqpm = np.array(jzu__hibo, np.uint8)
    ahgqz__efpg = context.get_constant(types.int64, hnxu__egbtq)
    dihzt__nuya = context.get_constant_generic(builder, char_arr_type,
        vnty__vqpm)
    gnn__lws = context.get_constant_generic(builder, offset_arr_type, hlu__eny)
    zru__wpmcd = context.get_constant_generic(builder, null_bitmap_arr_type,
        ikzm__lvq)
    beda__qviuh = lir.Constant.literal_struct([ahgqz__efpg, dihzt__nuya,
        gnn__lws, zru__wpmcd])
    beda__qviuh = cgutils.global_constant(builder, '.const.payload',
        beda__qviuh).bitcast(cgutils.voidptr_t)
    rqahw__ujbls = context.get_constant(types.int64, -1)
    ebb__mzq = context.get_constant_null(types.voidptr)
    pdxzz__jyq = lir.Constant.literal_struct([rqahw__ujbls, ebb__mzq,
        ebb__mzq, beda__qviuh, rqahw__ujbls])
    pdxzz__jyq = cgutils.global_constant(builder, '.const.meminfo', pdxzz__jyq
        ).bitcast(cgutils.voidptr_t)
    toe__bsmy = lir.Constant.literal_struct([pdxzz__jyq])
    ttqoz__gwlj = lir.Constant.literal_struct([toe__bsmy])
    return ttqoz__gwlj


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
