import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        rnd__xbl = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, rnd__xbl)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    coi__xzcnk = context.get_value_type(str_arr_split_view_payload_type)
    lsngd__rmkvq = context.get_abi_sizeof(coi__xzcnk)
    wrsm__gqf = context.get_value_type(types.voidptr)
    iyud__ezj = context.get_value_type(types.uintp)
    sfcnc__ilqtl = lir.FunctionType(lir.VoidType(), [wrsm__gqf, iyud__ezj,
        wrsm__gqf])
    zbvnw__ght = cgutils.get_or_insert_function(builder.module,
        sfcnc__ilqtl, name='dtor_str_arr_split_view')
    uhm__dzdh = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, lsngd__rmkvq), zbvnw__ght)
    lip__wfzap = context.nrt.meminfo_data(builder, uhm__dzdh)
    wuc__vjc = builder.bitcast(lip__wfzap, coi__xzcnk.as_pointer())
    return uhm__dzdh, wuc__vjc


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        qhp__lcfy, nckhh__dtn = args
        uhm__dzdh, wuc__vjc = construct_str_arr_split_view(context, builder)
        yxc__iyoiw = _get_str_binary_arr_payload(context, builder,
            qhp__lcfy, string_array_type)
        xeba__vag = lir.FunctionType(lir.VoidType(), [wuc__vjc.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        gxr__kjho = cgutils.get_or_insert_function(builder.module,
            xeba__vag, name='str_arr_split_view_impl')
        xgj__nlqwh = context.make_helper(builder, offset_arr_type,
            yxc__iyoiw.offsets).data
        qoge__owpsv = context.make_helper(builder, char_arr_type,
            yxc__iyoiw.data).data
        foea__vhwng = context.make_helper(builder, null_bitmap_arr_type,
            yxc__iyoiw.null_bitmap).data
        euh__ljjpl = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(gxr__kjho, [wuc__vjc, yxc__iyoiw.n_arrays, xgj__nlqwh,
            qoge__owpsv, foea__vhwng, euh__ljjpl])
        xwtug__caquu = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(wuc__vjc))
        anyuz__pjfx = context.make_helper(builder, string_array_split_view_type
            )
        anyuz__pjfx.num_items = yxc__iyoiw.n_arrays
        anyuz__pjfx.index_offsets = xwtug__caquu.index_offsets
        anyuz__pjfx.data_offsets = xwtug__caquu.data_offsets
        anyuz__pjfx.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [qhp__lcfy])
        anyuz__pjfx.null_bitmap = xwtug__caquu.null_bitmap
        anyuz__pjfx.meminfo = uhm__dzdh
        ghsj__znws = anyuz__pjfx._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, ghsj__znws)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    aefj__tbqd = context.make_helper(builder, string_array_split_view_type, val
        )
    rztc__tcxml = context.insert_const_string(builder.module, 'numpy')
    frcbh__laqh = c.pyapi.import_module_noblock(rztc__tcxml)
    dtype = c.pyapi.object_getattr_string(frcbh__laqh, 'object_')
    lan__eiyz = builder.sext(aefj__tbqd.num_items, c.pyapi.longlong)
    icvr__dkxjh = c.pyapi.long_from_longlong(lan__eiyz)
    ejcdz__oppjg = c.pyapi.call_method(frcbh__laqh, 'ndarray', (icvr__dkxjh,
        dtype))
    uiy__ybth = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    qdnur__faeam = c.pyapi._get_function(uiy__ybth, name='array_getptr1')
    hlco__vizz = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    fit__icxsa = c.pyapi._get_function(hlco__vizz, name='array_setitem')
    bzmps__adlp = c.pyapi.object_getattr_string(frcbh__laqh, 'nan')
    with cgutils.for_range(builder, aefj__tbqd.num_items) as bphha__wtkym:
        str_ind = bphha__wtkym.index
        riqi__lurte = builder.sext(builder.load(builder.gep(aefj__tbqd.
            index_offsets, [str_ind])), lir.IntType(64))
        nyyte__trwbc = builder.sext(builder.load(builder.gep(aefj__tbqd.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        ozmz__vxq = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        izqv__tllz = builder.gep(aefj__tbqd.null_bitmap, [ozmz__vxq])
        wnaf__ujz = builder.load(izqv__tllz)
        qqc__ouuy = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(wnaf__ujz, qqc__ouuy), lir.Constant
            (lir.IntType(8), 1))
        kcn__fwe = builder.sub(nyyte__trwbc, riqi__lurte)
        kcn__fwe = builder.sub(kcn__fwe, kcn__fwe.type(1))
        fyuhx__oxjr = builder.call(qdnur__faeam, [ejcdz__oppjg, str_ind])
        tacis__pwpcc = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(tacis__pwpcc) as (unxi__lreqe, fvgu__cpv):
            with unxi__lreqe:
                wxuoh__utx = c.pyapi.list_new(kcn__fwe)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    wxuoh__utx), likely=True):
                    with cgutils.for_range(c.builder, kcn__fwe
                        ) as bphha__wtkym:
                        ommcf__glf = builder.add(riqi__lurte, bphha__wtkym.
                            index)
                        data_start = builder.load(builder.gep(aefj__tbqd.
                            data_offsets, [ommcf__glf]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        dtlz__iui = builder.load(builder.gep(aefj__tbqd.
                            data_offsets, [builder.add(ommcf__glf,
                            ommcf__glf.type(1))]))
                        zkud__zju = builder.gep(builder.extract_value(
                            aefj__tbqd.data, 0), [data_start])
                        snmg__jjvmc = builder.sext(builder.sub(dtlz__iui,
                            data_start), lir.IntType(64))
                        dnx__ovo = c.pyapi.string_from_string_and_size(
                            zkud__zju, snmg__jjvmc)
                        c.pyapi.list_setitem(wxuoh__utx, bphha__wtkym.index,
                            dnx__ovo)
                builder.call(fit__icxsa, [ejcdz__oppjg, fyuhx__oxjr,
                    wxuoh__utx])
            with fvgu__cpv:
                builder.call(fit__icxsa, [ejcdz__oppjg, fyuhx__oxjr,
                    bzmps__adlp])
    c.pyapi.decref(frcbh__laqh)
    c.pyapi.decref(dtype)
    c.pyapi.decref(bzmps__adlp)
    return ejcdz__oppjg


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        mfjgf__uadc, rdcnc__kjlq, zkud__zju = args
        uhm__dzdh, wuc__vjc = construct_str_arr_split_view(context, builder)
        xeba__vag = lir.FunctionType(lir.VoidType(), [wuc__vjc.type, lir.
            IntType(64), lir.IntType(64)])
        gxr__kjho = cgutils.get_or_insert_function(builder.module,
            xeba__vag, name='str_arr_split_view_alloc')
        builder.call(gxr__kjho, [wuc__vjc, mfjgf__uadc, rdcnc__kjlq])
        xwtug__caquu = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(wuc__vjc))
        anyuz__pjfx = context.make_helper(builder, string_array_split_view_type
            )
        anyuz__pjfx.num_items = mfjgf__uadc
        anyuz__pjfx.index_offsets = xwtug__caquu.index_offsets
        anyuz__pjfx.data_offsets = xwtug__caquu.data_offsets
        anyuz__pjfx.data = zkud__zju
        anyuz__pjfx.null_bitmap = xwtug__caquu.null_bitmap
        context.nrt.incref(builder, data_t, zkud__zju)
        anyuz__pjfx.meminfo = uhm__dzdh
        ghsj__znws = anyuz__pjfx._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, ghsj__znws)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        xyyk__inoyk, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            xyyk__inoyk = builder.extract_value(xyyk__inoyk, 0)
        return builder.bitcast(builder.gep(xyyk__inoyk, [ind]), lir.IntType
            (8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        xyyk__inoyk, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            xyyk__inoyk = builder.extract_value(xyyk__inoyk, 0)
        return builder.load(builder.gep(xyyk__inoyk, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        xyyk__inoyk, ind, xsfp__almhc = args
        kbs__yjcbi = builder.gep(xyyk__inoyk, [ind])
        builder.store(xsfp__almhc, kbs__yjcbi)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        hrtzh__byafb, ind = args
        ljkeu__giv = context.make_helper(builder, arr_ctypes_t, hrtzh__byafb)
        koz__ney = context.make_helper(builder, arr_ctypes_t)
        koz__ney.data = builder.gep(ljkeu__giv.data, [ind])
        koz__ney.meminfo = ljkeu__giv.meminfo
        ylgo__ijq = koz__ney._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, ylgo__ijq)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    rrfm__hkey = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not rrfm__hkey:
        return 0, 0, 0
    ommcf__glf = getitem_c_arr(arr._index_offsets, item_ind)
    exkxw__kgpid = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    hkok__oxe = exkxw__kgpid - ommcf__glf
    if str_ind >= hkok__oxe:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, ommcf__glf + str_ind)
    data_start += 1
    if ommcf__glf + str_ind == 0:
        data_start = 0
    dtlz__iui = getitem_c_arr(arr._data_offsets, ommcf__glf + str_ind + 1)
    xgfty__lhnl = dtlz__iui - data_start
    return 1, data_start, xgfty__lhnl


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        xdy__lwif = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            ommcf__glf = getitem_c_arr(A._index_offsets, ind)
            exkxw__kgpid = getitem_c_arr(A._index_offsets, ind + 1)
            zbz__tpvr = exkxw__kgpid - ommcf__glf - 1
            qhp__lcfy = bodo.libs.str_arr_ext.pre_alloc_string_array(zbz__tpvr,
                -1)
            for yjsv__lkhx in range(zbz__tpvr):
                data_start = getitem_c_arr(A._data_offsets, ommcf__glf +
                    yjsv__lkhx)
                data_start += 1
                if ommcf__glf + yjsv__lkhx == 0:
                    data_start = 0
                dtlz__iui = getitem_c_arr(A._data_offsets, ommcf__glf +
                    yjsv__lkhx + 1)
                xgfty__lhnl = dtlz__iui - data_start
                kbs__yjcbi = get_array_ctypes_ptr(A._data, data_start)
                fmybz__ngbl = bodo.libs.str_arr_ext.decode_utf8(kbs__yjcbi,
                    xgfty__lhnl)
                qhp__lcfy[yjsv__lkhx] = fmybz__ngbl
            return qhp__lcfy
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        kjcvv__cevgu = offset_type.bitwidth // 8

        def _impl(A, ind):
            zbz__tpvr = len(A)
            if zbz__tpvr != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            mfjgf__uadc = 0
            rdcnc__kjlq = 0
            for yjsv__lkhx in range(zbz__tpvr):
                if ind[yjsv__lkhx]:
                    mfjgf__uadc += 1
                    ommcf__glf = getitem_c_arr(A._index_offsets, yjsv__lkhx)
                    exkxw__kgpid = getitem_c_arr(A._index_offsets, 
                        yjsv__lkhx + 1)
                    rdcnc__kjlq += exkxw__kgpid - ommcf__glf
            ejcdz__oppjg = pre_alloc_str_arr_view(mfjgf__uadc, rdcnc__kjlq,
                A._data)
            item_ind = 0
            uusti__rhfi = 0
            for yjsv__lkhx in range(zbz__tpvr):
                if ind[yjsv__lkhx]:
                    ommcf__glf = getitem_c_arr(A._index_offsets, yjsv__lkhx)
                    exkxw__kgpid = getitem_c_arr(A._index_offsets, 
                        yjsv__lkhx + 1)
                    ggn__kpjmi = exkxw__kgpid - ommcf__glf
                    setitem_c_arr(ejcdz__oppjg._index_offsets, item_ind,
                        uusti__rhfi)
                    kbs__yjcbi = get_c_arr_ptr(A._data_offsets, ommcf__glf)
                    xyk__nvuq = get_c_arr_ptr(ejcdz__oppjg._data_offsets,
                        uusti__rhfi)
                    _memcpy(xyk__nvuq, kbs__yjcbi, ggn__kpjmi, kjcvv__cevgu)
                    rrfm__hkey = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, yjsv__lkhx)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ejcdz__oppjg.
                        _null_bitmap, item_ind, rrfm__hkey)
                    item_ind += 1
                    uusti__rhfi += ggn__kpjmi
            setitem_c_arr(ejcdz__oppjg._index_offsets, item_ind, uusti__rhfi)
            return ejcdz__oppjg
        return _impl
