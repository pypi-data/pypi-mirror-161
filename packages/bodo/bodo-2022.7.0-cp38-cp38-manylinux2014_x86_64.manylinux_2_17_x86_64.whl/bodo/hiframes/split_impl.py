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
        iew__thtyh = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, iew__thtyh)


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
    kfuez__dhfg = context.get_value_type(str_arr_split_view_payload_type)
    ifaw__mlsi = context.get_abi_sizeof(kfuez__dhfg)
    hqt__fdhj = context.get_value_type(types.voidptr)
    ljmtk__pvhy = context.get_value_type(types.uintp)
    ayzgw__bnfa = lir.FunctionType(lir.VoidType(), [hqt__fdhj, ljmtk__pvhy,
        hqt__fdhj])
    tdox__sknyr = cgutils.get_or_insert_function(builder.module,
        ayzgw__bnfa, name='dtor_str_arr_split_view')
    hvtoh__cdrag = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, ifaw__mlsi), tdox__sknyr)
    ujw__sai = context.nrt.meminfo_data(builder, hvtoh__cdrag)
    sxzq__xkbc = builder.bitcast(ujw__sai, kfuez__dhfg.as_pointer())
    return hvtoh__cdrag, sxzq__xkbc


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        tfxr__sdz, eobc__gyzmf = args
        hvtoh__cdrag, sxzq__xkbc = construct_str_arr_split_view(context,
            builder)
        zwo__mopjh = _get_str_binary_arr_payload(context, builder,
            tfxr__sdz, string_array_type)
        jqw__rgx = lir.FunctionType(lir.VoidType(), [sxzq__xkbc.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        kzmyq__mutq = cgutils.get_or_insert_function(builder.module,
            jqw__rgx, name='str_arr_split_view_impl')
        dqk__xxlcj = context.make_helper(builder, offset_arr_type,
            zwo__mopjh.offsets).data
        mdqvd__fnfz = context.make_helper(builder, char_arr_type,
            zwo__mopjh.data).data
        nnt__wxddu = context.make_helper(builder, null_bitmap_arr_type,
            zwo__mopjh.null_bitmap).data
        jau__grth = context.get_constant(types.int8, ord(sep_typ.literal_value)
            )
        builder.call(kzmyq__mutq, [sxzq__xkbc, zwo__mopjh.n_arrays,
            dqk__xxlcj, mdqvd__fnfz, nnt__wxddu, jau__grth])
        hijup__bkmdl = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(sxzq__xkbc))
        ehh__erouh = context.make_helper(builder, string_array_split_view_type)
        ehh__erouh.num_items = zwo__mopjh.n_arrays
        ehh__erouh.index_offsets = hijup__bkmdl.index_offsets
        ehh__erouh.data_offsets = hijup__bkmdl.data_offsets
        ehh__erouh.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [tfxr__sdz])
        ehh__erouh.null_bitmap = hijup__bkmdl.null_bitmap
        ehh__erouh.meminfo = hvtoh__cdrag
        qfs__cog = ehh__erouh._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, qfs__cog)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    atm__jvfy = context.make_helper(builder, string_array_split_view_type, val)
    opt__ump = context.insert_const_string(builder.module, 'numpy')
    tetij__yjkit = c.pyapi.import_module_noblock(opt__ump)
    dtype = c.pyapi.object_getattr_string(tetij__yjkit, 'object_')
    pep__vcgw = builder.sext(atm__jvfy.num_items, c.pyapi.longlong)
    xkvtm__tnk = c.pyapi.long_from_longlong(pep__vcgw)
    egx__rty = c.pyapi.call_method(tetij__yjkit, 'ndarray', (xkvtm__tnk, dtype)
        )
    gpri__iwq = lir.FunctionType(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    bunt__vqt = c.pyapi._get_function(gpri__iwq, name='array_getptr1')
    tfr__rlrac = lir.FunctionType(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    yaqc__huuz = c.pyapi._get_function(tfr__rlrac, name='array_setitem')
    yhbh__dsbwe = c.pyapi.object_getattr_string(tetij__yjkit, 'nan')
    with cgutils.for_range(builder, atm__jvfy.num_items) as gwvw__fkhf:
        str_ind = gwvw__fkhf.index
        zry__wtiw = builder.sext(builder.load(builder.gep(atm__jvfy.
            index_offsets, [str_ind])), lir.IntType(64))
        ilau__akdwx = builder.sext(builder.load(builder.gep(atm__jvfy.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        fqorm__picy = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        fsi__qzewy = builder.gep(atm__jvfy.null_bitmap, [fqorm__picy])
        yveh__vpbdp = builder.load(fsi__qzewy)
        xfm__yvn = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(yveh__vpbdp, xfm__yvn), lir.
            Constant(lir.IntType(8), 1))
        zsf__nnpe = builder.sub(ilau__akdwx, zry__wtiw)
        zsf__nnpe = builder.sub(zsf__nnpe, zsf__nnpe.type(1))
        mpqih__brl = builder.call(bunt__vqt, [egx__rty, str_ind])
        sxzi__glgl = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(sxzi__glgl) as (heb__tjt, oiz__atufm):
            with heb__tjt:
                wkr__dhv = c.pyapi.list_new(zsf__nnpe)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    wkr__dhv), likely=True):
                    with cgutils.for_range(c.builder, zsf__nnpe) as gwvw__fkhf:
                        mtmcm__rdsv = builder.add(zry__wtiw, gwvw__fkhf.index)
                        data_start = builder.load(builder.gep(atm__jvfy.
                            data_offsets, [mtmcm__rdsv]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        ulk__djh = builder.load(builder.gep(atm__jvfy.
                            data_offsets, [builder.add(mtmcm__rdsv,
                            mtmcm__rdsv.type(1))]))
                        epb__npa = builder.gep(builder.extract_value(
                            atm__jvfy.data, 0), [data_start])
                        qfrsf__ujagi = builder.sext(builder.sub(ulk__djh,
                            data_start), lir.IntType(64))
                        tjtit__scpas = c.pyapi.string_from_string_and_size(
                            epb__npa, qfrsf__ujagi)
                        c.pyapi.list_setitem(wkr__dhv, gwvw__fkhf.index,
                            tjtit__scpas)
                builder.call(yaqc__huuz, [egx__rty, mpqih__brl, wkr__dhv])
            with oiz__atufm:
                builder.call(yaqc__huuz, [egx__rty, mpqih__brl, yhbh__dsbwe])
    c.pyapi.decref(tetij__yjkit)
    c.pyapi.decref(dtype)
    c.pyapi.decref(yhbh__dsbwe)
    return egx__rty


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        gxpr__qtie, oqyp__yhw, epb__npa = args
        hvtoh__cdrag, sxzq__xkbc = construct_str_arr_split_view(context,
            builder)
        jqw__rgx = lir.FunctionType(lir.VoidType(), [sxzq__xkbc.type, lir.
            IntType(64), lir.IntType(64)])
        kzmyq__mutq = cgutils.get_or_insert_function(builder.module,
            jqw__rgx, name='str_arr_split_view_alloc')
        builder.call(kzmyq__mutq, [sxzq__xkbc, gxpr__qtie, oqyp__yhw])
        hijup__bkmdl = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(sxzq__xkbc))
        ehh__erouh = context.make_helper(builder, string_array_split_view_type)
        ehh__erouh.num_items = gxpr__qtie
        ehh__erouh.index_offsets = hijup__bkmdl.index_offsets
        ehh__erouh.data_offsets = hijup__bkmdl.data_offsets
        ehh__erouh.data = epb__npa
        ehh__erouh.null_bitmap = hijup__bkmdl.null_bitmap
        context.nrt.incref(builder, data_t, epb__npa)
        ehh__erouh.meminfo = hvtoh__cdrag
        qfs__cog = ehh__erouh._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, qfs__cog)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        uryf__xcjdm, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            uryf__xcjdm = builder.extract_value(uryf__xcjdm, 0)
        return builder.bitcast(builder.gep(uryf__xcjdm, [ind]), lir.IntType
            (8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        uryf__xcjdm, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            uryf__xcjdm = builder.extract_value(uryf__xcjdm, 0)
        return builder.load(builder.gep(uryf__xcjdm, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        uryf__xcjdm, ind, ptve__lfox = args
        zmq__iwqc = builder.gep(uryf__xcjdm, [ind])
        builder.store(ptve__lfox, zmq__iwqc)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        zgpvo__otjy, ind = args
        dfa__uhkml = context.make_helper(builder, arr_ctypes_t, zgpvo__otjy)
        vzn__gciz = context.make_helper(builder, arr_ctypes_t)
        vzn__gciz.data = builder.gep(dfa__uhkml.data, [ind])
        vzn__gciz.meminfo = dfa__uhkml.meminfo
        faux__tnsb = vzn__gciz._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, faux__tnsb)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    gzk__fsywi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not gzk__fsywi:
        return 0, 0, 0
    mtmcm__rdsv = getitem_c_arr(arr._index_offsets, item_ind)
    soa__ombu = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    cvbl__vvy = soa__ombu - mtmcm__rdsv
    if str_ind >= cvbl__vvy:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, mtmcm__rdsv + str_ind)
    data_start += 1
    if mtmcm__rdsv + str_ind == 0:
        data_start = 0
    ulk__djh = getitem_c_arr(arr._data_offsets, mtmcm__rdsv + str_ind + 1)
    dovg__khsyv = ulk__djh - data_start
    return 1, data_start, dovg__khsyv


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
        opw__sedbj = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            mtmcm__rdsv = getitem_c_arr(A._index_offsets, ind)
            soa__ombu = getitem_c_arr(A._index_offsets, ind + 1)
            jpz__mdh = soa__ombu - mtmcm__rdsv - 1
            tfxr__sdz = bodo.libs.str_arr_ext.pre_alloc_string_array(jpz__mdh,
                -1)
            for bfs__ybnj in range(jpz__mdh):
                data_start = getitem_c_arr(A._data_offsets, mtmcm__rdsv +
                    bfs__ybnj)
                data_start += 1
                if mtmcm__rdsv + bfs__ybnj == 0:
                    data_start = 0
                ulk__djh = getitem_c_arr(A._data_offsets, mtmcm__rdsv +
                    bfs__ybnj + 1)
                dovg__khsyv = ulk__djh - data_start
                zmq__iwqc = get_array_ctypes_ptr(A._data, data_start)
                zanj__vkjdr = bodo.libs.str_arr_ext.decode_utf8(zmq__iwqc,
                    dovg__khsyv)
                tfxr__sdz[bfs__ybnj] = zanj__vkjdr
            return tfxr__sdz
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        ninam__cyp = offset_type.bitwidth // 8

        def _impl(A, ind):
            jpz__mdh = len(A)
            if jpz__mdh != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            gxpr__qtie = 0
            oqyp__yhw = 0
            for bfs__ybnj in range(jpz__mdh):
                if ind[bfs__ybnj]:
                    gxpr__qtie += 1
                    mtmcm__rdsv = getitem_c_arr(A._index_offsets, bfs__ybnj)
                    soa__ombu = getitem_c_arr(A._index_offsets, bfs__ybnj + 1)
                    oqyp__yhw += soa__ombu - mtmcm__rdsv
            egx__rty = pre_alloc_str_arr_view(gxpr__qtie, oqyp__yhw, A._data)
            item_ind = 0
            wavy__eeqhe = 0
            for bfs__ybnj in range(jpz__mdh):
                if ind[bfs__ybnj]:
                    mtmcm__rdsv = getitem_c_arr(A._index_offsets, bfs__ybnj)
                    soa__ombu = getitem_c_arr(A._index_offsets, bfs__ybnj + 1)
                    tnfpz__kiyvr = soa__ombu - mtmcm__rdsv
                    setitem_c_arr(egx__rty._index_offsets, item_ind,
                        wavy__eeqhe)
                    zmq__iwqc = get_c_arr_ptr(A._data_offsets, mtmcm__rdsv)
                    iugr__lzql = get_c_arr_ptr(egx__rty._data_offsets,
                        wavy__eeqhe)
                    _memcpy(iugr__lzql, zmq__iwqc, tnfpz__kiyvr, ninam__cyp)
                    gzk__fsywi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, bfs__ybnj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(egx__rty.
                        _null_bitmap, item_ind, gzk__fsywi)
                    item_ind += 1
                    wavy__eeqhe += tnfpz__kiyvr
            setitem_c_arr(egx__rty._index_offsets, item_ind, wavy__eeqhe)
            return egx__rty
        return _impl
