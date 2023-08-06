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
        hin__xcocy = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, hin__xcocy)


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
    jhk__slgs = context.get_value_type(str_arr_split_view_payload_type)
    rgcp__iuc = context.get_abi_sizeof(jhk__slgs)
    rou__qimt = context.get_value_type(types.voidptr)
    uhknj__dcjf = context.get_value_type(types.uintp)
    wpwn__njwl = lir.FunctionType(lir.VoidType(), [rou__qimt, uhknj__dcjf,
        rou__qimt])
    vmzad__qkb = cgutils.get_or_insert_function(builder.module, wpwn__njwl,
        name='dtor_str_arr_split_view')
    atmrj__yyzho = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, rgcp__iuc), vmzad__qkb)
    sqvli__mvz = context.nrt.meminfo_data(builder, atmrj__yyzho)
    qsas__xwc = builder.bitcast(sqvli__mvz, jhk__slgs.as_pointer())
    return atmrj__yyzho, qsas__xwc


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        gbvkv__gurnq, omank__ktpt = args
        atmrj__yyzho, qsas__xwc = construct_str_arr_split_view(context, builder
            )
        jju__pfuw = _get_str_binary_arr_payload(context, builder,
            gbvkv__gurnq, string_array_type)
        dgvt__mnl = lir.FunctionType(lir.VoidType(), [qsas__xwc.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        lbdk__wkg = cgutils.get_or_insert_function(builder.module,
            dgvt__mnl, name='str_arr_split_view_impl')
        ybxul__prn = context.make_helper(builder, offset_arr_type,
            jju__pfuw.offsets).data
        yzng__ufza = context.make_helper(builder, char_arr_type, jju__pfuw.data
            ).data
        sdje__tcpdi = context.make_helper(builder, null_bitmap_arr_type,
            jju__pfuw.null_bitmap).data
        gzza__gmmgr = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(lbdk__wkg, [qsas__xwc, jju__pfuw.n_arrays, ybxul__prn,
            yzng__ufza, sdje__tcpdi, gzza__gmmgr])
        amri__dly = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(qsas__xwc))
        brps__vlgg = context.make_helper(builder, string_array_split_view_type)
        brps__vlgg.num_items = jju__pfuw.n_arrays
        brps__vlgg.index_offsets = amri__dly.index_offsets
        brps__vlgg.data_offsets = amri__dly.data_offsets
        brps__vlgg.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [
            gbvkv__gurnq])
        brps__vlgg.null_bitmap = amri__dly.null_bitmap
        brps__vlgg.meminfo = atmrj__yyzho
        vcx__cbl = brps__vlgg._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, vcx__cbl)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    onvdb__omk = context.make_helper(builder, string_array_split_view_type, val
        )
    fxynr__psrb = context.insert_const_string(builder.module, 'numpy')
    hrg__mgzrs = c.pyapi.import_module_noblock(fxynr__psrb)
    dtype = c.pyapi.object_getattr_string(hrg__mgzrs, 'object_')
    tihs__ikm = builder.sext(onvdb__omk.num_items, c.pyapi.longlong)
    xyd__horf = c.pyapi.long_from_longlong(tihs__ikm)
    geckw__vkq = c.pyapi.call_method(hrg__mgzrs, 'ndarray', (xyd__horf, dtype))
    sdrs__lhcyn = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    eacm__upks = c.pyapi._get_function(sdrs__lhcyn, name='array_getptr1')
    sks__ply = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.IntType
        (8).as_pointer(), c.pyapi.pyobj])
    msy__fzl = c.pyapi._get_function(sks__ply, name='array_setitem')
    dag__gwt = c.pyapi.object_getattr_string(hrg__mgzrs, 'nan')
    with cgutils.for_range(builder, onvdb__omk.num_items) as rjymy__ztek:
        str_ind = rjymy__ztek.index
        ujb__toh = builder.sext(builder.load(builder.gep(onvdb__omk.
            index_offsets, [str_ind])), lir.IntType(64))
        ruglz__ozmb = builder.sext(builder.load(builder.gep(onvdb__omk.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        ojoz__hjsr = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        qktw__zfa = builder.gep(onvdb__omk.null_bitmap, [ojoz__hjsr])
        siqei__atygd = builder.load(qktw__zfa)
        xcv__veld = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(siqei__atygd, xcv__veld), lir.
            Constant(lir.IntType(8), 1))
        bcqf__szayr = builder.sub(ruglz__ozmb, ujb__toh)
        bcqf__szayr = builder.sub(bcqf__szayr, bcqf__szayr.type(1))
        gcmn__akn = builder.call(eacm__upks, [geckw__vkq, str_ind])
        bmd__taenf = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(bmd__taenf) as (ujw__jhf, zejiy__rinnc):
            with ujw__jhf:
                etmsp__hwchw = c.pyapi.list_new(bcqf__szayr)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    etmsp__hwchw), likely=True):
                    with cgutils.for_range(c.builder, bcqf__szayr
                        ) as rjymy__ztek:
                        tztw__ossk = builder.add(ujb__toh, rjymy__ztek.index)
                        data_start = builder.load(builder.gep(onvdb__omk.
                            data_offsets, [tztw__ossk]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        ajudu__aeal = builder.load(builder.gep(onvdb__omk.
                            data_offsets, [builder.add(tztw__ossk,
                            tztw__ossk.type(1))]))
                        dtdfs__oaif = builder.gep(builder.extract_value(
                            onvdb__omk.data, 0), [data_start])
                        aars__udvg = builder.sext(builder.sub(ajudu__aeal,
                            data_start), lir.IntType(64))
                        kurt__yyl = c.pyapi.string_from_string_and_size(
                            dtdfs__oaif, aars__udvg)
                        c.pyapi.list_setitem(etmsp__hwchw, rjymy__ztek.
                            index, kurt__yyl)
                builder.call(msy__fzl, [geckw__vkq, gcmn__akn, etmsp__hwchw])
            with zejiy__rinnc:
                builder.call(msy__fzl, [geckw__vkq, gcmn__akn, dag__gwt])
    c.pyapi.decref(hrg__mgzrs)
    c.pyapi.decref(dtype)
    c.pyapi.decref(dag__gwt)
    return geckw__vkq


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        twev__eipni, jkvnm__zjpff, dtdfs__oaif = args
        atmrj__yyzho, qsas__xwc = construct_str_arr_split_view(context, builder
            )
        dgvt__mnl = lir.FunctionType(lir.VoidType(), [qsas__xwc.type, lir.
            IntType(64), lir.IntType(64)])
        lbdk__wkg = cgutils.get_or_insert_function(builder.module,
            dgvt__mnl, name='str_arr_split_view_alloc')
        builder.call(lbdk__wkg, [qsas__xwc, twev__eipni, jkvnm__zjpff])
        amri__dly = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(qsas__xwc))
        brps__vlgg = context.make_helper(builder, string_array_split_view_type)
        brps__vlgg.num_items = twev__eipni
        brps__vlgg.index_offsets = amri__dly.index_offsets
        brps__vlgg.data_offsets = amri__dly.data_offsets
        brps__vlgg.data = dtdfs__oaif
        brps__vlgg.null_bitmap = amri__dly.null_bitmap
        context.nrt.incref(builder, data_t, dtdfs__oaif)
        brps__vlgg.meminfo = atmrj__yyzho
        vcx__cbl = brps__vlgg._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, vcx__cbl)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        pycg__eqj, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            pycg__eqj = builder.extract_value(pycg__eqj, 0)
        return builder.bitcast(builder.gep(pycg__eqj, [ind]), lir.IntType(8
            ).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        pycg__eqj, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            pycg__eqj = builder.extract_value(pycg__eqj, 0)
        return builder.load(builder.gep(pycg__eqj, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        pycg__eqj, ind, uiqtx__wdb = args
        lqb__navpk = builder.gep(pycg__eqj, [ind])
        builder.store(uiqtx__wdb, lqb__navpk)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        ayoyn__quxeh, ind = args
        vtyeh__blw = context.make_helper(builder, arr_ctypes_t, ayoyn__quxeh)
        mlltw__hwbsk = context.make_helper(builder, arr_ctypes_t)
        mlltw__hwbsk.data = builder.gep(vtyeh__blw.data, [ind])
        mlltw__hwbsk.meminfo = vtyeh__blw.meminfo
        socm__rru = mlltw__hwbsk._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, socm__rru)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    nnob__bbd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not nnob__bbd:
        return 0, 0, 0
    tztw__ossk = getitem_c_arr(arr._index_offsets, item_ind)
    ymo__hkdpi = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    nxon__ofrv = ymo__hkdpi - tztw__ossk
    if str_ind >= nxon__ofrv:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, tztw__ossk + str_ind)
    data_start += 1
    if tztw__ossk + str_ind == 0:
        data_start = 0
    ajudu__aeal = getitem_c_arr(arr._data_offsets, tztw__ossk + str_ind + 1)
    tblw__mqpa = ajudu__aeal - data_start
    return 1, data_start, tblw__mqpa


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
        ybvi__memj = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            tztw__ossk = getitem_c_arr(A._index_offsets, ind)
            ymo__hkdpi = getitem_c_arr(A._index_offsets, ind + 1)
            gcfp__bgx = ymo__hkdpi - tztw__ossk - 1
            gbvkv__gurnq = bodo.libs.str_arr_ext.pre_alloc_string_array(
                gcfp__bgx, -1)
            for mfs__zge in range(gcfp__bgx):
                data_start = getitem_c_arr(A._data_offsets, tztw__ossk +
                    mfs__zge)
                data_start += 1
                if tztw__ossk + mfs__zge == 0:
                    data_start = 0
                ajudu__aeal = getitem_c_arr(A._data_offsets, tztw__ossk +
                    mfs__zge + 1)
                tblw__mqpa = ajudu__aeal - data_start
                lqb__navpk = get_array_ctypes_ptr(A._data, data_start)
                sjb__xecnz = bodo.libs.str_arr_ext.decode_utf8(lqb__navpk,
                    tblw__mqpa)
                gbvkv__gurnq[mfs__zge] = sjb__xecnz
            return gbvkv__gurnq
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        kiqdd__pmfv = offset_type.bitwidth // 8

        def _impl(A, ind):
            gcfp__bgx = len(A)
            if gcfp__bgx != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            twev__eipni = 0
            jkvnm__zjpff = 0
            for mfs__zge in range(gcfp__bgx):
                if ind[mfs__zge]:
                    twev__eipni += 1
                    tztw__ossk = getitem_c_arr(A._index_offsets, mfs__zge)
                    ymo__hkdpi = getitem_c_arr(A._index_offsets, mfs__zge + 1)
                    jkvnm__zjpff += ymo__hkdpi - tztw__ossk
            geckw__vkq = pre_alloc_str_arr_view(twev__eipni, jkvnm__zjpff,
                A._data)
            item_ind = 0
            obnvu__cyn = 0
            for mfs__zge in range(gcfp__bgx):
                if ind[mfs__zge]:
                    tztw__ossk = getitem_c_arr(A._index_offsets, mfs__zge)
                    ymo__hkdpi = getitem_c_arr(A._index_offsets, mfs__zge + 1)
                    xssba__ltxjl = ymo__hkdpi - tztw__ossk
                    setitem_c_arr(geckw__vkq._index_offsets, item_ind,
                        obnvu__cyn)
                    lqb__navpk = get_c_arr_ptr(A._data_offsets, tztw__ossk)
                    bje__koh = get_c_arr_ptr(geckw__vkq._data_offsets,
                        obnvu__cyn)
                    _memcpy(bje__koh, lqb__navpk, xssba__ltxjl, kiqdd__pmfv)
                    nnob__bbd = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, mfs__zge)
                    bodo.libs.int_arr_ext.set_bit_to_arr(geckw__vkq.
                        _null_bitmap, item_ind, nnob__bbd)
                    item_ind += 1
                    obnvu__cyn += xssba__ltxjl
            setitem_c_arr(geckw__vkq._index_offsets, item_ind, obnvu__cyn)
            return geckw__vkq
        return _impl
