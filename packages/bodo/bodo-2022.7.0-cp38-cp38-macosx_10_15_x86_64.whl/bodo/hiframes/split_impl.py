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
        ycvfd__nub = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, ycvfd__nub)


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
    muw__kjd = context.get_value_type(str_arr_split_view_payload_type)
    cckk__pyhc = context.get_abi_sizeof(muw__kjd)
    rhefc__kzbz = context.get_value_type(types.voidptr)
    enz__eza = context.get_value_type(types.uintp)
    ppas__cvxa = lir.FunctionType(lir.VoidType(), [rhefc__kzbz, enz__eza,
        rhefc__kzbz])
    bbh__lwq = cgutils.get_or_insert_function(builder.module, ppas__cvxa,
        name='dtor_str_arr_split_view')
    pzdkr__xpm = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, cckk__pyhc), bbh__lwq)
    fqgp__pcww = context.nrt.meminfo_data(builder, pzdkr__xpm)
    kucz__tgmu = builder.bitcast(fqgp__pcww, muw__kjd.as_pointer())
    return pzdkr__xpm, kucz__tgmu


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        qbl__ztfuo, tahoq__srihv = args
        pzdkr__xpm, kucz__tgmu = construct_str_arr_split_view(context, builder)
        mofcp__okkn = _get_str_binary_arr_payload(context, builder,
            qbl__ztfuo, string_array_type)
        oes__ibslk = lir.FunctionType(lir.VoidType(), [kucz__tgmu.type, lir
            .IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        lbcs__kjgvx = cgutils.get_or_insert_function(builder.module,
            oes__ibslk, name='str_arr_split_view_impl')
        ldi__ngry = context.make_helper(builder, offset_arr_type,
            mofcp__okkn.offsets).data
        dja__jkxr = context.make_helper(builder, char_arr_type, mofcp__okkn
            .data).data
        ymw__tgnav = context.make_helper(builder, null_bitmap_arr_type,
            mofcp__okkn.null_bitmap).data
        eht__ihkl = context.get_constant(types.int8, ord(sep_typ.literal_value)
            )
        builder.call(lbcs__kjgvx, [kucz__tgmu, mofcp__okkn.n_arrays,
            ldi__ngry, dja__jkxr, ymw__tgnav, eht__ihkl])
        oires__mcsz = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(kucz__tgmu))
        aqox__vvsl = context.make_helper(builder, string_array_split_view_type)
        aqox__vvsl.num_items = mofcp__okkn.n_arrays
        aqox__vvsl.index_offsets = oires__mcsz.index_offsets
        aqox__vvsl.data_offsets = oires__mcsz.data_offsets
        aqox__vvsl.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [qbl__ztfuo])
        aqox__vvsl.null_bitmap = oires__mcsz.null_bitmap
        aqox__vvsl.meminfo = pzdkr__xpm
        trj__kux = aqox__vvsl._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, trj__kux)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    aofb__pgzo = context.make_helper(builder, string_array_split_view_type, val
        )
    juyzg__whugv = context.insert_const_string(builder.module, 'numpy')
    caygt__aqnnr = c.pyapi.import_module_noblock(juyzg__whugv)
    dtype = c.pyapi.object_getattr_string(caygt__aqnnr, 'object_')
    rnffr__ywyc = builder.sext(aofb__pgzo.num_items, c.pyapi.longlong)
    fxb__ysqc = c.pyapi.long_from_longlong(rnffr__ywyc)
    brf__nnukm = c.pyapi.call_method(caygt__aqnnr, 'ndarray', (fxb__ysqc,
        dtype))
    ard__tlt = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.pyobj,
        c.pyapi.py_ssize_t])
    tgbd__uuhc = c.pyapi._get_function(ard__tlt, name='array_getptr1')
    iez__avvu = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    zmyc__gyxst = c.pyapi._get_function(iez__avvu, name='array_setitem')
    pkhp__lblnn = c.pyapi.object_getattr_string(caygt__aqnnr, 'nan')
    with cgutils.for_range(builder, aofb__pgzo.num_items) as kcmg__rufre:
        str_ind = kcmg__rufre.index
        gpwz__oump = builder.sext(builder.load(builder.gep(aofb__pgzo.
            index_offsets, [str_ind])), lir.IntType(64))
        aqtw__ljh = builder.sext(builder.load(builder.gep(aofb__pgzo.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        mqn__ctsds = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        lpscv__toc = builder.gep(aofb__pgzo.null_bitmap, [mqn__ctsds])
        kpt__fnm = builder.load(lpscv__toc)
        dlo__kkic = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(kpt__fnm, dlo__kkic), lir.Constant(
            lir.IntType(8), 1))
        xjkkc__ushnu = builder.sub(aqtw__ljh, gpwz__oump)
        xjkkc__ushnu = builder.sub(xjkkc__ushnu, xjkkc__ushnu.type(1))
        zbnsh__cticc = builder.call(tgbd__uuhc, [brf__nnukm, str_ind])
        rrnes__yani = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(rrnes__yani) as (piyju__sudxm, selt__jrzs):
            with piyju__sudxm:
                vyvh__ctrtt = c.pyapi.list_new(xjkkc__ushnu)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    vyvh__ctrtt), likely=True):
                    with cgutils.for_range(c.builder, xjkkc__ushnu
                        ) as kcmg__rufre:
                        tem__mzzzv = builder.add(gpwz__oump, kcmg__rufre.index)
                        data_start = builder.load(builder.gep(aofb__pgzo.
                            data_offsets, [tem__mzzzv]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        ngfyp__nwxm = builder.load(builder.gep(aofb__pgzo.
                            data_offsets, [builder.add(tem__mzzzv,
                            tem__mzzzv.type(1))]))
                        aqpkj__eee = builder.gep(builder.extract_value(
                            aofb__pgzo.data, 0), [data_start])
                        ebvob__zpn = builder.sext(builder.sub(ngfyp__nwxm,
                            data_start), lir.IntType(64))
                        mzaeo__uxkbs = c.pyapi.string_from_string_and_size(
                            aqpkj__eee, ebvob__zpn)
                        c.pyapi.list_setitem(vyvh__ctrtt, kcmg__rufre.index,
                            mzaeo__uxkbs)
                builder.call(zmyc__gyxst, [brf__nnukm, zbnsh__cticc,
                    vyvh__ctrtt])
            with selt__jrzs:
                builder.call(zmyc__gyxst, [brf__nnukm, zbnsh__cticc,
                    pkhp__lblnn])
    c.pyapi.decref(caygt__aqnnr)
    c.pyapi.decref(dtype)
    c.pyapi.decref(pkhp__lblnn)
    return brf__nnukm


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        uabjk__pnql, lccq__fsacz, aqpkj__eee = args
        pzdkr__xpm, kucz__tgmu = construct_str_arr_split_view(context, builder)
        oes__ibslk = lir.FunctionType(lir.VoidType(), [kucz__tgmu.type, lir
            .IntType(64), lir.IntType(64)])
        lbcs__kjgvx = cgutils.get_or_insert_function(builder.module,
            oes__ibslk, name='str_arr_split_view_alloc')
        builder.call(lbcs__kjgvx, [kucz__tgmu, uabjk__pnql, lccq__fsacz])
        oires__mcsz = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(kucz__tgmu))
        aqox__vvsl = context.make_helper(builder, string_array_split_view_type)
        aqox__vvsl.num_items = uabjk__pnql
        aqox__vvsl.index_offsets = oires__mcsz.index_offsets
        aqox__vvsl.data_offsets = oires__mcsz.data_offsets
        aqox__vvsl.data = aqpkj__eee
        aqox__vvsl.null_bitmap = oires__mcsz.null_bitmap
        context.nrt.incref(builder, data_t, aqpkj__eee)
        aqox__vvsl.meminfo = pzdkr__xpm
        trj__kux = aqox__vvsl._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, trj__kux)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        mhr__ycaze, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            mhr__ycaze = builder.extract_value(mhr__ycaze, 0)
        return builder.bitcast(builder.gep(mhr__ycaze, [ind]), lir.IntType(
            8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        mhr__ycaze, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            mhr__ycaze = builder.extract_value(mhr__ycaze, 0)
        return builder.load(builder.gep(mhr__ycaze, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        mhr__ycaze, ind, htb__rtiwu = args
        rqy__rmpgx = builder.gep(mhr__ycaze, [ind])
        builder.store(htb__rtiwu, rqy__rmpgx)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        trm__welvn, ind = args
        gkakv__nox = context.make_helper(builder, arr_ctypes_t, trm__welvn)
        nshgi__rip = context.make_helper(builder, arr_ctypes_t)
        nshgi__rip.data = builder.gep(gkakv__nox.data, [ind])
        nshgi__rip.meminfo = gkakv__nox.meminfo
        qufxp__kiewm = nshgi__rip._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, qufxp__kiewm)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    ejf__kbw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not ejf__kbw:
        return 0, 0, 0
    tem__mzzzv = getitem_c_arr(arr._index_offsets, item_ind)
    das__bbgm = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    gwx__gfmkb = das__bbgm - tem__mzzzv
    if str_ind >= gwx__gfmkb:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, tem__mzzzv + str_ind)
    data_start += 1
    if tem__mzzzv + str_ind == 0:
        data_start = 0
    ngfyp__nwxm = getitem_c_arr(arr._data_offsets, tem__mzzzv + str_ind + 1)
    jqa__coioa = ngfyp__nwxm - data_start
    return 1, data_start, jqa__coioa


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
        nwkw__nuax = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            tem__mzzzv = getitem_c_arr(A._index_offsets, ind)
            das__bbgm = getitem_c_arr(A._index_offsets, ind + 1)
            dgh__dpm = das__bbgm - tem__mzzzv - 1
            qbl__ztfuo = bodo.libs.str_arr_ext.pre_alloc_string_array(dgh__dpm,
                -1)
            for xowvg__bsur in range(dgh__dpm):
                data_start = getitem_c_arr(A._data_offsets, tem__mzzzv +
                    xowvg__bsur)
                data_start += 1
                if tem__mzzzv + xowvg__bsur == 0:
                    data_start = 0
                ngfyp__nwxm = getitem_c_arr(A._data_offsets, tem__mzzzv +
                    xowvg__bsur + 1)
                jqa__coioa = ngfyp__nwxm - data_start
                rqy__rmpgx = get_array_ctypes_ptr(A._data, data_start)
                jqvil__jdi = bodo.libs.str_arr_ext.decode_utf8(rqy__rmpgx,
                    jqa__coioa)
                qbl__ztfuo[xowvg__bsur] = jqvil__jdi
            return qbl__ztfuo
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        jjh__ueeul = offset_type.bitwidth // 8

        def _impl(A, ind):
            dgh__dpm = len(A)
            if dgh__dpm != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            uabjk__pnql = 0
            lccq__fsacz = 0
            for xowvg__bsur in range(dgh__dpm):
                if ind[xowvg__bsur]:
                    uabjk__pnql += 1
                    tem__mzzzv = getitem_c_arr(A._index_offsets, xowvg__bsur)
                    das__bbgm = getitem_c_arr(A._index_offsets, xowvg__bsur + 1
                        )
                    lccq__fsacz += das__bbgm - tem__mzzzv
            brf__nnukm = pre_alloc_str_arr_view(uabjk__pnql, lccq__fsacz, A
                ._data)
            item_ind = 0
            btr__lgo = 0
            for xowvg__bsur in range(dgh__dpm):
                if ind[xowvg__bsur]:
                    tem__mzzzv = getitem_c_arr(A._index_offsets, xowvg__bsur)
                    das__bbgm = getitem_c_arr(A._index_offsets, xowvg__bsur + 1
                        )
                    cbva__sdch = das__bbgm - tem__mzzzv
                    setitem_c_arr(brf__nnukm._index_offsets, item_ind, btr__lgo
                        )
                    rqy__rmpgx = get_c_arr_ptr(A._data_offsets, tem__mzzzv)
                    dvq__nrt = get_c_arr_ptr(brf__nnukm._data_offsets, btr__lgo
                        )
                    _memcpy(dvq__nrt, rqy__rmpgx, cbva__sdch, jjh__ueeul)
                    ejf__kbw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, xowvg__bsur)
                    bodo.libs.int_arr_ext.set_bit_to_arr(brf__nnukm.
                        _null_bitmap, item_ind, ejf__kbw)
                    item_ind += 1
                    btr__lgo += cbva__sdch
            setitem_c_arr(brf__nnukm._index_offsets, item_ind, btr__lgo)
            return brf__nnukm
        return _impl
