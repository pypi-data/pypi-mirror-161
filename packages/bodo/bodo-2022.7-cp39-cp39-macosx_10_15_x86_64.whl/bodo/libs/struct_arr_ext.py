"""Array implementation for structs of values.
Corresponds to Spark's StructType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Struct arrays: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in contiguous data arrays; one array per field. For example:
A:             ["AA", "B", "C"]
B:             [1, 2, 4]
"""
import operator
import llvmlite.binding as ll
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
from numba.typed.typedobjectutils import _cast
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.typing import BodoError, dtype_to_array_type, get_overload_const_int, get_overload_const_str, is_list_like_index_type, is_overload_constant_int, is_overload_constant_str, is_overload_none
ll.add_symbol('struct_array_from_sequence', array_ext.
    struct_array_from_sequence)
ll.add_symbol('np_array_from_struct_array', array_ext.
    np_array_from_struct_array)


class StructArrayType(types.ArrayCompatible):

    def __init__(self, data, names=None):
        assert isinstance(data, tuple) and len(data) > 0 and all(bodo.utils
            .utils.is_array_typ(hhv__lyuty, False) for hhv__lyuty in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(hhv__lyuty,
                str) for hhv__lyuty in names) and len(names) == len(data)
        else:
            names = tuple('f{}'.format(i) for i in range(len(data)))
        self.data = data
        self.names = names
        super(StructArrayType, self).__init__(name=
            'StructArrayType({}, {})'.format(data, names))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return StructType(tuple(snwj__qpms.dtype for snwj__qpms in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(hhv__lyuty) for hhv__lyuty in d.keys())
        data = tuple(dtype_to_array_type(snwj__qpms) for snwj__qpms in d.
            values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(hhv__lyuty, False) for hhv__lyuty in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        omjb__zbicm = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, omjb__zbicm)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        omjb__zbicm = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, omjb__zbicm)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    ymir__uyeo = builder.module
    xhnjk__trlih = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    som__haeb = cgutils.get_or_insert_function(ymir__uyeo, xhnjk__trlih,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not som__haeb.is_declaration:
        return som__haeb
    som__haeb.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(som__haeb.append_basic_block())
    ddbo__ixwbd = som__haeb.args[0]
    ovwh__vjclb = context.get_value_type(payload_type).as_pointer()
    xgq__ijgt = builder.bitcast(ddbo__ixwbd, ovwh__vjclb)
    crq__dowo = context.make_helper(builder, payload_type, ref=xgq__ijgt)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), crq__dowo.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), crq__dowo
        .null_bitmap)
    builder.ret_void()
    return som__haeb


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    ozcb__hkrf = context.get_value_type(payload_type)
    lyvxl__koac = context.get_abi_sizeof(ozcb__hkrf)
    cskxb__ixk = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    uhc__yiepb = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, lyvxl__koac), cskxb__ixk)
    uimhc__pjbvo = context.nrt.meminfo_data(builder, uhc__yiepb)
    rbpsj__mdzwp = builder.bitcast(uimhc__pjbvo, ozcb__hkrf.as_pointer())
    crq__dowo = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    tmld__lgftr = 0
    for arr_typ in struct_arr_type.data:
        uos__kjwas = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        hhawf__xat = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(tmld__lgftr, 
            tmld__lgftr + uos__kjwas)])
        arr = gen_allocate_array(context, builder, arr_typ, hhawf__xat, c)
        arrs.append(arr)
        tmld__lgftr += uos__kjwas
    crq__dowo.data = cgutils.pack_array(builder, arrs) if types.is_homogeneous(
        *struct_arr_type.data) else cgutils.pack_struct(builder, arrs)
    qyz__ywwax = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    vdrs__djb = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [qyz__ywwax])
    null_bitmap_ptr = vdrs__djb.data
    crq__dowo.null_bitmap = vdrs__djb._getvalue()
    builder.store(crq__dowo._getvalue(), rbpsj__mdzwp)
    return uhc__yiepb, crq__dowo.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    quuie__vlq = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        kdt__xnveu = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            kdt__xnveu)
        quuie__vlq.append(arr.data)
    pcp__hes = cgutils.pack_array(c.builder, quuie__vlq
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, quuie__vlq)
    yhag__nyb = cgutils.alloca_once_value(c.builder, pcp__hes)
    iyvt__dileb = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(hhv__lyuty.dtype)) for hhv__lyuty in data_typ]
    xmhr__xsup = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, iyvt__dileb))
    pgz__obtyf = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, hhv__lyuty) for hhv__lyuty in
        names])
    vimcv__sja = cgutils.alloca_once_value(c.builder, pgz__obtyf)
    return yhag__nyb, xmhr__xsup, vimcv__sja


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    ter__bgh = all(isinstance(snwj__qpms, types.Array) and snwj__qpms.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        snwj__qpms in typ.data)
    if ter__bgh:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        blby__toxs = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            blby__toxs, i) for i in range(1, blby__toxs.type.count)], lir.
            IntType(64))
    uhc__yiepb, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if ter__bgh:
        yhag__nyb, xmhr__xsup, vimcv__sja = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        xhnjk__trlih = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        som__haeb = cgutils.get_or_insert_function(c.builder.module,
            xhnjk__trlih, name='struct_array_from_sequence')
        c.builder.call(som__haeb, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(yhag__nyb, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(xmhr__xsup,
            lir.IntType(8).as_pointer()), c.builder.bitcast(vimcv__sja, lir
            .IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    xjkh__ofzy = c.context.make_helper(c.builder, typ)
    xjkh__ofzy.meminfo = uhc__yiepb
    yko__hft = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xjkh__ofzy._getvalue(), is_error=yko__hft)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    pfgo__rkra = context.insert_const_string(builder.module, 'pandas')
    dwg__zjm = c.pyapi.import_module_noblock(pfgo__rkra)
    dsc__nkt = c.pyapi.object_getattr_string(dwg__zjm, 'NA')
    with cgutils.for_range(builder, n_structs) as dvvcd__fulx:
        zyn__gvo = dvvcd__fulx.index
        kbgim__untp = seq_getitem(builder, context, val, zyn__gvo)
        set_bitmap_bit(builder, null_bitmap_ptr, zyn__gvo, 0)
        for tqinq__tbs in range(len(typ.data)):
            arr_typ = typ.data[tqinq__tbs]
            data_arr = builder.extract_value(data_tup, tqinq__tbs)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            llb__kkw, npw__fiyn = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, zyn__gvo])
        qww__ljt = is_na_value(builder, context, kbgim__untp, dsc__nkt)
        rwf__wng = builder.icmp_unsigned('!=', qww__ljt, lir.Constant(
            qww__ljt.type, 1))
        with builder.if_then(rwf__wng):
            set_bitmap_bit(builder, null_bitmap_ptr, zyn__gvo, 1)
            for tqinq__tbs in range(len(typ.data)):
                arr_typ = typ.data[tqinq__tbs]
                if is_tuple_array:
                    xjfph__nex = c.pyapi.tuple_getitem(kbgim__untp, tqinq__tbs)
                else:
                    xjfph__nex = c.pyapi.dict_getitem_string(kbgim__untp,
                        typ.names[tqinq__tbs])
                qww__ljt = is_na_value(builder, context, xjfph__nex, dsc__nkt)
                rwf__wng = builder.icmp_unsigned('!=', qww__ljt, lir.
                    Constant(qww__ljt.type, 1))
                with builder.if_then(rwf__wng):
                    xjfph__nex = to_arr_obj_if_list_obj(c, context, builder,
                        xjfph__nex, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        xjfph__nex).value
                    data_arr = builder.extract_value(data_tup, tqinq__tbs)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    llb__kkw, npw__fiyn = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, zyn__gvo, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(kbgim__untp)
    c.pyapi.decref(dwg__zjm)
    c.pyapi.decref(dsc__nkt)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    xjkh__ofzy = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    uimhc__pjbvo = context.nrt.meminfo_data(builder, xjkh__ofzy.meminfo)
    rbpsj__mdzwp = builder.bitcast(uimhc__pjbvo, context.get_value_type(
        payload_type).as_pointer())
    crq__dowo = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(rbpsj__mdzwp))
    return crq__dowo


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    crq__dowo = _get_struct_arr_payload(c.context, c.builder, typ, val)
    llb__kkw, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64(
        typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), crq__dowo.null_bitmap).data
    ter__bgh = all(isinstance(snwj__qpms, types.Array) and snwj__qpms.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        snwj__qpms in typ.data)
    if ter__bgh:
        yhag__nyb, xmhr__xsup, vimcv__sja = _get_C_API_ptrs(c, crq__dowo.
            data, typ.data, typ.names)
        xhnjk__trlih = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        brvkl__ycvh = cgutils.get_or_insert_function(c.builder.module,
            xhnjk__trlih, name='np_array_from_struct_array')
        arr = c.builder.call(brvkl__ycvh, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(yhag__nyb, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            xmhr__xsup, lir.IntType(8).as_pointer()), c.builder.bitcast(
            vimcv__sja, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, crq__dowo.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    pfgo__rkra = context.insert_const_string(builder.module, 'numpy')
    dhrb__chs = c.pyapi.import_module_noblock(pfgo__rkra)
    ubur__zhfdt = c.pyapi.object_getattr_string(dhrb__chs, 'object_')
    xszmt__tgcou = c.pyapi.long_from_longlong(length)
    slz__gyy = c.pyapi.call_method(dhrb__chs, 'ndarray', (xszmt__tgcou,
        ubur__zhfdt))
    vyo__hjz = c.pyapi.object_getattr_string(dhrb__chs, 'nan')
    with cgutils.for_range(builder, length) as dvvcd__fulx:
        zyn__gvo = dvvcd__fulx.index
        pyarray_setitem(builder, context, slz__gyy, zyn__gvo, vyo__hjz)
        nbxfb__bjvoa = get_bitmap_bit(builder, null_bitmap_ptr, zyn__gvo)
        hkm__xwgtd = builder.icmp_unsigned('!=', nbxfb__bjvoa, lir.Constant
            (lir.IntType(8), 0))
        with builder.if_then(hkm__xwgtd):
            if is_tuple_array:
                kbgim__untp = c.pyapi.tuple_new(len(typ.data))
            else:
                kbgim__untp = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(vyo__hjz)
                    c.pyapi.tuple_setitem(kbgim__untp, i, vyo__hjz)
                else:
                    c.pyapi.dict_setitem_string(kbgim__untp, typ.names[i],
                        vyo__hjz)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                llb__kkw, nooa__iph = c.pyapi.call_jit_code(lambda data_arr,
                    ind: not bodo.libs.array_kernels.isna(data_arr, ind),
                    types.bool_(arr_typ, types.int64), [data_arr, zyn__gvo])
                with builder.if_then(nooa__iph):
                    llb__kkw, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, zyn__gvo])
                    bis__bkbb = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(kbgim__untp, i, bis__bkbb)
                    else:
                        c.pyapi.dict_setitem_string(kbgim__untp, typ.names[
                            i], bis__bkbb)
                        c.pyapi.decref(bis__bkbb)
            pyarray_setitem(builder, context, slz__gyy, zyn__gvo, kbgim__untp)
            c.pyapi.decref(kbgim__untp)
    c.pyapi.decref(dhrb__chs)
    c.pyapi.decref(ubur__zhfdt)
    c.pyapi.decref(xszmt__tgcou)
    c.pyapi.decref(vyo__hjz)
    return slz__gyy


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    alkgr__lzixj = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if alkgr__lzixj == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for bkyc__tdh in range(alkgr__lzixj)])
    elif nested_counts_type.count < alkgr__lzixj:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for bkyc__tdh in range(
            alkgr__lzixj - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(snwj__qpms) for snwj__qpms in
            names_typ.types)
    jdpid__gyh = tuple(snwj__qpms.instance_type for snwj__qpms in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(jdpid__gyh, names)

    def codegen(context, builder, sig, args):
        nxats__tzg, nested_counts, bkyc__tdh, bkyc__tdh = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        uhc__yiepb, bkyc__tdh, bkyc__tdh = construct_struct_array(context,
            builder, struct_arr_type, nxats__tzg, nested_counts)
        xjkh__ofzy = context.make_helper(builder, struct_arr_type)
        xjkh__ofzy.meminfo = uhc__yiepb
        return xjkh__ofzy._getvalue()
    return struct_arr_type(num_structs_typ, nested_counts_typ, dtypes_typ,
        names_typ), codegen


def pre_alloc_struct_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 4 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_struct_arr_ext_pre_alloc_struct_array
    ) = pre_alloc_struct_array_equiv


class StructType(types.Type):

    def __init__(self, data, names):
        assert isinstance(data, tuple) and len(data) > 0
        assert isinstance(names, tuple) and all(isinstance(hhv__lyuty, str) for
            hhv__lyuty in names) and len(names) == len(data)
        self.data = data
        self.names = names
        super(StructType, self).__init__(name='StructType({}, {})'.format(
            data, names))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple)
        self.data = data
        super(StructPayloadType, self).__init__(name=
            'StructPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructPayloadType)
class StructPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        omjb__zbicm = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, omjb__zbicm)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        omjb__zbicm = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, omjb__zbicm)


def define_struct_dtor(context, builder, struct_type, payload_type):
    ymir__uyeo = builder.module
    xhnjk__trlih = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    som__haeb = cgutils.get_or_insert_function(ymir__uyeo, xhnjk__trlih,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not som__haeb.is_declaration:
        return som__haeb
    som__haeb.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(som__haeb.append_basic_block())
    ddbo__ixwbd = som__haeb.args[0]
    ovwh__vjclb = context.get_value_type(payload_type).as_pointer()
    xgq__ijgt = builder.bitcast(ddbo__ixwbd, ovwh__vjclb)
    crq__dowo = context.make_helper(builder, payload_type, ref=xgq__ijgt)
    for i in range(len(struct_type.data)):
        ygvy__muutp = builder.extract_value(crq__dowo.null_bitmap, i)
        hkm__xwgtd = builder.icmp_unsigned('==', ygvy__muutp, lir.Constant(
            ygvy__muutp.type, 1))
        with builder.if_then(hkm__xwgtd):
            val = builder.extract_value(crq__dowo.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return som__haeb


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    uimhc__pjbvo = context.nrt.meminfo_data(builder, struct.meminfo)
    rbpsj__mdzwp = builder.bitcast(uimhc__pjbvo, context.get_value_type(
        payload_type).as_pointer())
    crq__dowo = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(rbpsj__mdzwp))
    return crq__dowo, rbpsj__mdzwp


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    pfgo__rkra = context.insert_const_string(builder.module, 'pandas')
    dwg__zjm = c.pyapi.import_module_noblock(pfgo__rkra)
    dsc__nkt = c.pyapi.object_getattr_string(dwg__zjm, 'NA')
    gqrrn__uknwm = []
    nulls = []
    for i, snwj__qpms in enumerate(typ.data):
        bis__bkbb = c.pyapi.dict_getitem_string(val, typ.names[i])
        ugrjx__yjjk = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        sion__mak = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(snwj__qpms)))
        qww__ljt = is_na_value(builder, context, bis__bkbb, dsc__nkt)
        hkm__xwgtd = builder.icmp_unsigned('!=', qww__ljt, lir.Constant(
            qww__ljt.type, 1))
        with builder.if_then(hkm__xwgtd):
            builder.store(context.get_constant(types.uint8, 1), ugrjx__yjjk)
            field_val = c.pyapi.to_native_value(snwj__qpms, bis__bkbb).value
            builder.store(field_val, sion__mak)
        gqrrn__uknwm.append(builder.load(sion__mak))
        nulls.append(builder.load(ugrjx__yjjk))
    c.pyapi.decref(dwg__zjm)
    c.pyapi.decref(dsc__nkt)
    uhc__yiepb = construct_struct(context, builder, typ, gqrrn__uknwm, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = uhc__yiepb
    yko__hft = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=yko__hft)


@box(StructType)
def box_struct(typ, val, c):
    hot__mizbt = c.pyapi.dict_new(len(typ.data))
    crq__dowo, bkyc__tdh = _get_struct_payload(c.context, c.builder, typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(hot__mizbt, typ.names[i], c.pyapi.
            borrow_none())
        ygvy__muutp = c.builder.extract_value(crq__dowo.null_bitmap, i)
        hkm__xwgtd = c.builder.icmp_unsigned('==', ygvy__muutp, lir.
            Constant(ygvy__muutp.type, 1))
        with c.builder.if_then(hkm__xwgtd):
            pafv__uehj = c.builder.extract_value(crq__dowo.data, i)
            c.context.nrt.incref(c.builder, val_typ, pafv__uehj)
            xjfph__nex = c.pyapi.from_native_value(val_typ, pafv__uehj, c.
                env_manager)
            c.pyapi.dict_setitem_string(hot__mizbt, typ.names[i], xjfph__nex)
            c.pyapi.decref(xjfph__nex)
    c.context.nrt.decref(c.builder, typ, val)
    return hot__mizbt


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(snwj__qpms) for snwj__qpms in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, wwb__ipwor = args
        payload_type = StructPayloadType(struct_type.data)
        ozcb__hkrf = context.get_value_type(payload_type)
        lyvxl__koac = context.get_abi_sizeof(ozcb__hkrf)
        cskxb__ixk = define_struct_dtor(context, builder, struct_type,
            payload_type)
        uhc__yiepb = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, lyvxl__koac), cskxb__ixk)
        uimhc__pjbvo = context.nrt.meminfo_data(builder, uhc__yiepb)
        rbpsj__mdzwp = builder.bitcast(uimhc__pjbvo, ozcb__hkrf.as_pointer())
        crq__dowo = cgutils.create_struct_proxy(payload_type)(context, builder)
        crq__dowo.data = data
        crq__dowo.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for bkyc__tdh in range(len(
            data_typ.types))])
        builder.store(crq__dowo._getvalue(), rbpsj__mdzwp)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = uhc__yiepb
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        crq__dowo, bkyc__tdh = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            crq__dowo.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        crq__dowo, bkyc__tdh = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            crq__dowo.null_bitmap)
    oeojh__ilf = types.UniTuple(types.int8, len(struct_typ.data))
    return oeojh__ilf(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, bkyc__tdh, val = args
        crq__dowo, rbpsj__mdzwp = _get_struct_payload(context, builder,
            struct_typ, struct)
        ntf__wbazg = crq__dowo.data
        wvd__gtns = builder.insert_value(ntf__wbazg, val, field_ind)
        pek__jyg = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, pek__jyg, ntf__wbazg)
        context.nrt.incref(builder, pek__jyg, wvd__gtns)
        crq__dowo.data = wvd__gtns
        builder.store(crq__dowo._getvalue(), rbpsj__mdzwp)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    wgvi__ahhho = get_overload_const_str(ind)
    if wgvi__ahhho not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            wgvi__ahhho, struct))
    return struct.names.index(wgvi__ahhho)


def is_field_value_null(s, field_name):
    pass


@overload(is_field_value_null, no_unliteral=True)
def overload_is_field_value_null(s, field_name):
    field_ind = _get_struct_field_ind(s, field_name, 'element access (getitem)'
        )
    return lambda s, field_name: get_struct_null_bitmap(s)[field_ind] == 0


@overload(operator.getitem, no_unliteral=True)
def struct_getitem(struct, ind):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'element access (getitem)')
    return lambda struct, ind: get_struct_data(struct)[field_ind]


@overload(operator.setitem, no_unliteral=True)
def struct_setitem(struct, ind, val):
    if not isinstance(struct, StructType):
        return
    field_ind = _get_struct_field_ind(struct, ind, 'item assignment (setitem)')
    field_typ = struct.data[field_ind]
    return lambda struct, ind, val: set_struct_data(struct, field_ind,
        _cast(val, field_typ))


@overload(len, no_unliteral=True)
def overload_struct_arr_len(struct):
    if isinstance(struct, StructType):
        num_fields = len(struct.data)
        return lambda struct: num_fields


def construct_struct(context, builder, struct_type, values, nulls):
    payload_type = StructPayloadType(struct_type.data)
    ozcb__hkrf = context.get_value_type(payload_type)
    lyvxl__koac = context.get_abi_sizeof(ozcb__hkrf)
    cskxb__ixk = define_struct_dtor(context, builder, struct_type, payload_type
        )
    uhc__yiepb = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, lyvxl__koac), cskxb__ixk)
    uimhc__pjbvo = context.nrt.meminfo_data(builder, uhc__yiepb)
    rbpsj__mdzwp = builder.bitcast(uimhc__pjbvo, ozcb__hkrf.as_pointer())
    crq__dowo = cgutils.create_struct_proxy(payload_type)(context, builder)
    crq__dowo.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    crq__dowo.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(crq__dowo._getvalue(), rbpsj__mdzwp)
    return uhc__yiepb


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    tbigm__pxx = tuple(d.dtype for d in struct_arr_typ.data)
    ckrql__enm = StructType(tbigm__pxx, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        iwlqe__fxs, ind = args
        crq__dowo = _get_struct_arr_payload(context, builder,
            struct_arr_typ, iwlqe__fxs)
        gqrrn__uknwm = []
        ocri__oehw = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            kdt__xnveu = builder.extract_value(crq__dowo.data, i)
            jfzk__nguob = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [kdt__xnveu,
                ind])
            ocri__oehw.append(jfzk__nguob)
            huaq__gea = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            hkm__xwgtd = builder.icmp_unsigned('==', jfzk__nguob, lir.
                Constant(jfzk__nguob.type, 1))
            with builder.if_then(hkm__xwgtd):
                edi__qbjbc = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    kdt__xnveu, ind])
                builder.store(edi__qbjbc, huaq__gea)
            gqrrn__uknwm.append(builder.load(huaq__gea))
        if isinstance(ckrql__enm, types.DictType):
            rlqyo__hgp = [context.insert_const_string(builder.module,
                aanof__yky) for aanof__yky in struct_arr_typ.names]
            mphr__avv = cgutils.pack_array(builder, gqrrn__uknwm)
            rxsfm__etlqu = cgutils.pack_array(builder, rlqyo__hgp)

            def impl(names, vals):
                d = {}
                for i, aanof__yky in enumerate(names):
                    d[aanof__yky] = vals[i]
                return d
            hqzk__vfd = context.compile_internal(builder, impl, ckrql__enm(
                types.Tuple(tuple(types.StringLiteral(aanof__yky) for
                aanof__yky in struct_arr_typ.names)), types.Tuple(
                tbigm__pxx)), [rxsfm__etlqu, mphr__avv])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                tbigm__pxx), mphr__avv)
            return hqzk__vfd
        uhc__yiepb = construct_struct(context, builder, ckrql__enm,
            gqrrn__uknwm, ocri__oehw)
        struct = context.make_helper(builder, ckrql__enm)
        struct.meminfo = uhc__yiepb
        return struct._getvalue()
    return ckrql__enm(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        crq__dowo = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            crq__dowo.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        crq__dowo = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            crq__dowo.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(snwj__qpms) for snwj__qpms in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, vdrs__djb, wwb__ipwor = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        ozcb__hkrf = context.get_value_type(payload_type)
        lyvxl__koac = context.get_abi_sizeof(ozcb__hkrf)
        cskxb__ixk = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        uhc__yiepb = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, lyvxl__koac), cskxb__ixk)
        uimhc__pjbvo = context.nrt.meminfo_data(builder, uhc__yiepb)
        rbpsj__mdzwp = builder.bitcast(uimhc__pjbvo, ozcb__hkrf.as_pointer())
        crq__dowo = cgutils.create_struct_proxy(payload_type)(context, builder)
        crq__dowo.data = data
        crq__dowo.null_bitmap = vdrs__djb
        builder.store(crq__dowo._getvalue(), rbpsj__mdzwp)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, vdrs__djb)
        xjkh__ofzy = context.make_helper(builder, struct_arr_type)
        xjkh__ofzy.meminfo = uhc__yiepb
        return xjkh__ofzy._getvalue()
    return struct_arr_type(data_typ, null_bitmap_typ, names_typ), codegen


@overload(operator.getitem, no_unliteral=True)
def struct_arr_getitem(arr, ind):
    if not isinstance(arr, StructArrayType):
        return
    if isinstance(ind, types.Integer):

        def struct_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            return struct_array_get_struct(arr, ind)
        return struct_arr_getitem_impl
    zmd__nlpfq = len(arr.data)
    osugy__hthms = 'def impl(arr, ind):\n'
    osugy__hthms += '  data = get_data(arr)\n'
    osugy__hthms += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        osugy__hthms += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        osugy__hthms += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        osugy__hthms += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    osugy__hthms += (
        '  return init_struct_arr(({},), out_null_bitmap, ({},))\n'.format(
        ', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for i in
        range(zmd__nlpfq)), ', '.join("'{}'".format(aanof__yky) for
        aanof__yky in arr.names)))
    wrwjo__smqp = {}
    exec(osugy__hthms, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, wrwjo__smqp)
    impl = wrwjo__smqp['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        zmd__nlpfq = len(arr.data)
        osugy__hthms = 'def impl(arr, ind, val):\n'
        osugy__hthms += '  data = get_data(arr)\n'
        osugy__hthms += '  null_bitmap = get_null_bitmap(arr)\n'
        osugy__hthms += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(zmd__nlpfq):
            if isinstance(val, StructType):
                osugy__hthms += ("  if is_field_value_null(val, '{}'):\n".
                    format(arr.names[i]))
                osugy__hthms += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                osugy__hthms += '  else:\n'
                osugy__hthms += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                osugy__hthms += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        wrwjo__smqp = {}
        exec(osugy__hthms, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, wrwjo__smqp)
        impl = wrwjo__smqp['impl']
        return impl
    if isinstance(ind, types.SliceType):
        zmd__nlpfq = len(arr.data)
        osugy__hthms = 'def impl(arr, ind, val):\n'
        osugy__hthms += '  data = get_data(arr)\n'
        osugy__hthms += '  null_bitmap = get_null_bitmap(arr)\n'
        osugy__hthms += '  val_data = get_data(val)\n'
        osugy__hthms += '  val_null_bitmap = get_null_bitmap(val)\n'
        osugy__hthms += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(zmd__nlpfq):
            osugy__hthms += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        wrwjo__smqp = {}
        exec(osugy__hthms, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, wrwjo__smqp)
        impl = wrwjo__smqp['impl']
        return impl
    raise BodoError(
        'only setitem with scalar/slice index is currently supported for struct arrays'
        )


@overload(len, no_unliteral=True)
def overload_struct_arr_len(A):
    if isinstance(A, StructArrayType):
        return lambda A: len(get_data(A)[0])


@overload_attribute(StructArrayType, 'shape')
def overload_struct_arr_shape(A):
    return lambda A: (len(get_data(A)[0]),)


@overload_attribute(StructArrayType, 'dtype')
def overload_struct_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(StructArrayType, 'ndim')
def overload_struct_arr_ndim(A):
    return lambda A: 1


@overload_attribute(StructArrayType, 'nbytes')
def overload_struct_arr_nbytes(A):
    osugy__hthms = 'def impl(A):\n'
    osugy__hthms += '  total_nbytes = 0\n'
    osugy__hthms += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        osugy__hthms += f'  total_nbytes += data[{i}].nbytes\n'
    osugy__hthms += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    osugy__hthms += '  return total_nbytes\n'
    wrwjo__smqp = {}
    exec(osugy__hthms, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, wrwjo__smqp)
    impl = wrwjo__smqp['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        vdrs__djb = get_null_bitmap(A)
        rfzk__eeuk = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        knm__jboy = vdrs__djb.copy()
        return init_struct_arr(rfzk__eeuk, knm__jboy, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(hhv__lyuty.copy() for hhv__lyuty in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    uhp__ipivd = arrs.count
    osugy__hthms = 'def f(arrs):\n'
    osugy__hthms += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(uhp__ipivd)))
    wrwjo__smqp = {}
    exec(osugy__hthms, {}, wrwjo__smqp)
    impl = wrwjo__smqp['f']
    return impl
