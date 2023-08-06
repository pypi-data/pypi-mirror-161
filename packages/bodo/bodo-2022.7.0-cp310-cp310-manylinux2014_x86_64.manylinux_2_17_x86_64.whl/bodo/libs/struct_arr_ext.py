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
            .utils.is_array_typ(ylxwv__prxae, False) for ylxwv__prxae in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(ylxwv__prxae,
                str) for ylxwv__prxae in names) and len(names) == len(data)
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
        return StructType(tuple(oejjf__tmuhh.dtype for oejjf__tmuhh in self
            .data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(ylxwv__prxae) for ylxwv__prxae in d.keys())
        data = tuple(dtype_to_array_type(oejjf__tmuhh) for oejjf__tmuhh in
            d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(ylxwv__prxae, False) for ylxwv__prxae in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        omgn__iyq = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, omgn__iyq)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        omgn__iyq = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, omgn__iyq)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    ptr__heeuf = builder.module
    ciz__xia = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gxdhw__juix = cgutils.get_or_insert_function(ptr__heeuf, ciz__xia, name
        ='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not gxdhw__juix.is_declaration:
        return gxdhw__juix
    gxdhw__juix.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gxdhw__juix.append_basic_block())
    kao__pdfrr = gxdhw__juix.args[0]
    hklk__vewnj = context.get_value_type(payload_type).as_pointer()
    tpqc__tse = builder.bitcast(kao__pdfrr, hklk__vewnj)
    szt__ybead = context.make_helper(builder, payload_type, ref=tpqc__tse)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), szt__ybead.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        szt__ybead.null_bitmap)
    builder.ret_void()
    return gxdhw__juix


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    eev__alv = context.get_value_type(payload_type)
    gukus__copj = context.get_abi_sizeof(eev__alv)
    drcql__usmuh = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    rga__zut = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, gukus__copj), drcql__usmuh)
    zxvo__wwbwg = context.nrt.meminfo_data(builder, rga__zut)
    aamcf__vqpel = builder.bitcast(zxvo__wwbwg, eev__alv.as_pointer())
    szt__ybead = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    yjs__hvoxr = 0
    for arr_typ in struct_arr_type.data:
        mwk__zwkzr = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        lfz__dqfhu = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(yjs__hvoxr, yjs__hvoxr +
            mwk__zwkzr)])
        arr = gen_allocate_array(context, builder, arr_typ, lfz__dqfhu, c)
        arrs.append(arr)
        yjs__hvoxr += mwk__zwkzr
    szt__ybead.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    bafoy__odotk = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    gpb__fmiby = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [bafoy__odotk])
    null_bitmap_ptr = gpb__fmiby.data
    szt__ybead.null_bitmap = gpb__fmiby._getvalue()
    builder.store(szt__ybead._getvalue(), aamcf__vqpel)
    return rga__zut, szt__ybead.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    swg__mfeav = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        rmgsn__ckdv = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            rmgsn__ckdv)
        swg__mfeav.append(arr.data)
    dlm__mdra = cgutils.pack_array(c.builder, swg__mfeav
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, swg__mfeav)
    kzppj__eeqj = cgutils.alloca_once_value(c.builder, dlm__mdra)
    cwt__riaz = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(ylxwv__prxae.dtype)) for ylxwv__prxae in data_typ]
    zfi__bimil = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, cwt__riaz))
    ztjqw__bdpp = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, ylxwv__prxae) for
        ylxwv__prxae in names])
    hmo__dlu = cgutils.alloca_once_value(c.builder, ztjqw__bdpp)
    return kzppj__eeqj, zfi__bimil, hmo__dlu


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    ufdlw__oucqb = all(isinstance(oejjf__tmuhh, types.Array) and 
        oejjf__tmuhh.dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for oejjf__tmuhh in typ.data)
    if ufdlw__oucqb:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        lvf__blgw = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            lvf__blgw, i) for i in range(1, lvf__blgw.type.count)], lir.
            IntType(64))
    rga__zut, data_tup, null_bitmap_ptr = construct_struct_array(c.context,
        c.builder, typ, n_structs, n_elems, c)
    if ufdlw__oucqb:
        kzppj__eeqj, zfi__bimil, hmo__dlu = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        ciz__xia = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        gxdhw__juix = cgutils.get_or_insert_function(c.builder.module,
            ciz__xia, name='struct_array_from_sequence')
        c.builder.call(gxdhw__juix, [val, c.context.get_constant(types.
            int32, len(typ.data)), c.builder.bitcast(kzppj__eeqj, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            zfi__bimil, lir.IntType(8).as_pointer()), c.builder.bitcast(
            hmo__dlu, lir.IntType(8).as_pointer()), c.context.get_constant(
            types.bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    oqbp__wxajs = c.context.make_helper(c.builder, typ)
    oqbp__wxajs.meminfo = rga__zut
    uch__kkxp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(oqbp__wxajs._getvalue(), is_error=uch__kkxp)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    zgkl__qdt = context.insert_const_string(builder.module, 'pandas')
    hlo__dus = c.pyapi.import_module_noblock(zgkl__qdt)
    dsen__lveju = c.pyapi.object_getattr_string(hlo__dus, 'NA')
    with cgutils.for_range(builder, n_structs) as cwam__vystr:
        gkcjz__hml = cwam__vystr.index
        tnfz__vjid = seq_getitem(builder, context, val, gkcjz__hml)
        set_bitmap_bit(builder, null_bitmap_ptr, gkcjz__hml, 0)
        for mhu__cdnq in range(len(typ.data)):
            arr_typ = typ.data[mhu__cdnq]
            data_arr = builder.extract_value(data_tup, mhu__cdnq)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            towyg__oztzl, ahful__jwdfj = c.pyapi.call_jit_code(set_na, sig,
                [data_arr, gkcjz__hml])
        kqrt__gppl = is_na_value(builder, context, tnfz__vjid, dsen__lveju)
        tuvit__asm = builder.icmp_unsigned('!=', kqrt__gppl, lir.Constant(
            kqrt__gppl.type, 1))
        with builder.if_then(tuvit__asm):
            set_bitmap_bit(builder, null_bitmap_ptr, gkcjz__hml, 1)
            for mhu__cdnq in range(len(typ.data)):
                arr_typ = typ.data[mhu__cdnq]
                if is_tuple_array:
                    sqqaj__xkv = c.pyapi.tuple_getitem(tnfz__vjid, mhu__cdnq)
                else:
                    sqqaj__xkv = c.pyapi.dict_getitem_string(tnfz__vjid,
                        typ.names[mhu__cdnq])
                kqrt__gppl = is_na_value(builder, context, sqqaj__xkv,
                    dsen__lveju)
                tuvit__asm = builder.icmp_unsigned('!=', kqrt__gppl, lir.
                    Constant(kqrt__gppl.type, 1))
                with builder.if_then(tuvit__asm):
                    sqqaj__xkv = to_arr_obj_if_list_obj(c, context, builder,
                        sqqaj__xkv, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        sqqaj__xkv).value
                    data_arr = builder.extract_value(data_tup, mhu__cdnq)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    towyg__oztzl, ahful__jwdfj = c.pyapi.call_jit_code(set_data
                        , sig, [data_arr, gkcjz__hml, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(tnfz__vjid)
    c.pyapi.decref(hlo__dus)
    c.pyapi.decref(dsen__lveju)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    oqbp__wxajs = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    zxvo__wwbwg = context.nrt.meminfo_data(builder, oqbp__wxajs.meminfo)
    aamcf__vqpel = builder.bitcast(zxvo__wwbwg, context.get_value_type(
        payload_type).as_pointer())
    szt__ybead = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(aamcf__vqpel))
    return szt__ybead


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    szt__ybead = _get_struct_arr_payload(c.context, c.builder, typ, val)
    towyg__oztzl, length = c.pyapi.call_jit_code(lambda A: len(A), types.
        int64(typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), szt__ybead.null_bitmap).data
    ufdlw__oucqb = all(isinstance(oejjf__tmuhh, types.Array) and 
        oejjf__tmuhh.dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for oejjf__tmuhh in typ.data)
    if ufdlw__oucqb:
        kzppj__eeqj, zfi__bimil, hmo__dlu = _get_C_API_ptrs(c, szt__ybead.
            data, typ.data, typ.names)
        ciz__xia = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        plj__zmg = cgutils.get_or_insert_function(c.builder.module,
            ciz__xia, name='np_array_from_struct_array')
        arr = c.builder.call(plj__zmg, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(kzppj__eeqj, lir
            .IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            zfi__bimil, lir.IntType(8).as_pointer()), c.builder.bitcast(
            hmo__dlu, lir.IntType(8).as_pointer()), c.context.get_constant(
            types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, szt__ybead.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    zgkl__qdt = context.insert_const_string(builder.module, 'numpy')
    fdp__uojov = c.pyapi.import_module_noblock(zgkl__qdt)
    axm__evdc = c.pyapi.object_getattr_string(fdp__uojov, 'object_')
    zlyld__xeior = c.pyapi.long_from_longlong(length)
    oqz__mlo = c.pyapi.call_method(fdp__uojov, 'ndarray', (zlyld__xeior,
        axm__evdc))
    jvzgs__zho = c.pyapi.object_getattr_string(fdp__uojov, 'nan')
    with cgutils.for_range(builder, length) as cwam__vystr:
        gkcjz__hml = cwam__vystr.index
        pyarray_setitem(builder, context, oqz__mlo, gkcjz__hml, jvzgs__zho)
        pbk__yudnx = get_bitmap_bit(builder, null_bitmap_ptr, gkcjz__hml)
        qefqv__twkz = builder.icmp_unsigned('!=', pbk__yudnx, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(qefqv__twkz):
            if is_tuple_array:
                tnfz__vjid = c.pyapi.tuple_new(len(typ.data))
            else:
                tnfz__vjid = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(jvzgs__zho)
                    c.pyapi.tuple_setitem(tnfz__vjid, i, jvzgs__zho)
                else:
                    c.pyapi.dict_setitem_string(tnfz__vjid, typ.names[i],
                        jvzgs__zho)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                towyg__oztzl, einhi__gobdn = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, gkcjz__hml])
                with builder.if_then(einhi__gobdn):
                    towyg__oztzl, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, gkcjz__hml])
                    sah__bsoz = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(tnfz__vjid, i, sah__bsoz)
                    else:
                        c.pyapi.dict_setitem_string(tnfz__vjid, typ.names[i
                            ], sah__bsoz)
                        c.pyapi.decref(sah__bsoz)
            pyarray_setitem(builder, context, oqz__mlo, gkcjz__hml, tnfz__vjid)
            c.pyapi.decref(tnfz__vjid)
    c.pyapi.decref(fdp__uojov)
    c.pyapi.decref(axm__evdc)
    c.pyapi.decref(zlyld__xeior)
    c.pyapi.decref(jvzgs__zho)
    return oqz__mlo


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    psrr__gsbzc = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if psrr__gsbzc == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for acil__ddzzo in range(psrr__gsbzc)])
    elif nested_counts_type.count < psrr__gsbzc:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for acil__ddzzo in range(
            psrr__gsbzc - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(oejjf__tmuhh) for oejjf__tmuhh in
            names_typ.types)
    yojd__hthjq = tuple(oejjf__tmuhh.instance_type for oejjf__tmuhh in
        dtypes_typ.types)
    struct_arr_type = StructArrayType(yojd__hthjq, names)

    def codegen(context, builder, sig, args):
        iosd__sjcmu, nested_counts, acil__ddzzo, acil__ddzzo = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        rga__zut, acil__ddzzo, acil__ddzzo = construct_struct_array(context,
            builder, struct_arr_type, iosd__sjcmu, nested_counts)
        oqbp__wxajs = context.make_helper(builder, struct_arr_type)
        oqbp__wxajs.meminfo = rga__zut
        return oqbp__wxajs._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(ylxwv__prxae,
            str) for ylxwv__prxae in names) and len(names) == len(data)
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
        omgn__iyq = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, omgn__iyq)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        omgn__iyq = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, omgn__iyq)


def define_struct_dtor(context, builder, struct_type, payload_type):
    ptr__heeuf = builder.module
    ciz__xia = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    gxdhw__juix = cgutils.get_or_insert_function(ptr__heeuf, ciz__xia, name
        ='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not gxdhw__juix.is_declaration:
        return gxdhw__juix
    gxdhw__juix.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(gxdhw__juix.append_basic_block())
    kao__pdfrr = gxdhw__juix.args[0]
    hklk__vewnj = context.get_value_type(payload_type).as_pointer()
    tpqc__tse = builder.bitcast(kao__pdfrr, hklk__vewnj)
    szt__ybead = context.make_helper(builder, payload_type, ref=tpqc__tse)
    for i in range(len(struct_type.data)):
        lgrt__nhc = builder.extract_value(szt__ybead.null_bitmap, i)
        qefqv__twkz = builder.icmp_unsigned('==', lgrt__nhc, lir.Constant(
            lgrt__nhc.type, 1))
        with builder.if_then(qefqv__twkz):
            val = builder.extract_value(szt__ybead.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return gxdhw__juix


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    zxvo__wwbwg = context.nrt.meminfo_data(builder, struct.meminfo)
    aamcf__vqpel = builder.bitcast(zxvo__wwbwg, context.get_value_type(
        payload_type).as_pointer())
    szt__ybead = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(aamcf__vqpel))
    return szt__ybead, aamcf__vqpel


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    zgkl__qdt = context.insert_const_string(builder.module, 'pandas')
    hlo__dus = c.pyapi.import_module_noblock(zgkl__qdt)
    dsen__lveju = c.pyapi.object_getattr_string(hlo__dus, 'NA')
    jexqw__bet = []
    nulls = []
    for i, oejjf__tmuhh in enumerate(typ.data):
        sah__bsoz = c.pyapi.dict_getitem_string(val, typ.names[i])
        yncrf__oen = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        bmdsc__jczim = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(oejjf__tmuhh)))
        kqrt__gppl = is_na_value(builder, context, sah__bsoz, dsen__lveju)
        qefqv__twkz = builder.icmp_unsigned('!=', kqrt__gppl, lir.Constant(
            kqrt__gppl.type, 1))
        with builder.if_then(qefqv__twkz):
            builder.store(context.get_constant(types.uint8, 1), yncrf__oen)
            field_val = c.pyapi.to_native_value(oejjf__tmuhh, sah__bsoz).value
            builder.store(field_val, bmdsc__jczim)
        jexqw__bet.append(builder.load(bmdsc__jczim))
        nulls.append(builder.load(yncrf__oen))
    c.pyapi.decref(hlo__dus)
    c.pyapi.decref(dsen__lveju)
    rga__zut = construct_struct(context, builder, typ, jexqw__bet, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = rga__zut
    uch__kkxp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=uch__kkxp)


@box(StructType)
def box_struct(typ, val, c):
    tsfa__pbl = c.pyapi.dict_new(len(typ.data))
    szt__ybead, acil__ddzzo = _get_struct_payload(c.context, c.builder, typ,
        val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(tsfa__pbl, typ.names[i], c.pyapi.
            borrow_none())
        lgrt__nhc = c.builder.extract_value(szt__ybead.null_bitmap, i)
        qefqv__twkz = c.builder.icmp_unsigned('==', lgrt__nhc, lir.Constant
            (lgrt__nhc.type, 1))
        with c.builder.if_then(qefqv__twkz):
            phfcp__mhg = c.builder.extract_value(szt__ybead.data, i)
            c.context.nrt.incref(c.builder, val_typ, phfcp__mhg)
            sqqaj__xkv = c.pyapi.from_native_value(val_typ, phfcp__mhg, c.
                env_manager)
            c.pyapi.dict_setitem_string(tsfa__pbl, typ.names[i], sqqaj__xkv)
            c.pyapi.decref(sqqaj__xkv)
    c.context.nrt.decref(c.builder, typ, val)
    return tsfa__pbl


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(oejjf__tmuhh) for oejjf__tmuhh in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, hqjn__xtly = args
        payload_type = StructPayloadType(struct_type.data)
        eev__alv = context.get_value_type(payload_type)
        gukus__copj = context.get_abi_sizeof(eev__alv)
        drcql__usmuh = define_struct_dtor(context, builder, struct_type,
            payload_type)
        rga__zut = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, gukus__copj), drcql__usmuh)
        zxvo__wwbwg = context.nrt.meminfo_data(builder, rga__zut)
        aamcf__vqpel = builder.bitcast(zxvo__wwbwg, eev__alv.as_pointer())
        szt__ybead = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        szt__ybead.data = data
        szt__ybead.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for acil__ddzzo in range(len(
            data_typ.types))])
        builder.store(szt__ybead._getvalue(), aamcf__vqpel)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = rga__zut
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        szt__ybead, acil__ddzzo = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            szt__ybead.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        szt__ybead, acil__ddzzo = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            szt__ybead.null_bitmap)
    vfia__mbp = types.UniTuple(types.int8, len(struct_typ.data))
    return vfia__mbp(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, acil__ddzzo, val = args
        szt__ybead, aamcf__vqpel = _get_struct_payload(context, builder,
            struct_typ, struct)
        fnyel__vrtw = szt__ybead.data
        qcjmo__rnpjn = builder.insert_value(fnyel__vrtw, val, field_ind)
        vrl__ybk = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, vrl__ybk, fnyel__vrtw)
        context.nrt.incref(builder, vrl__ybk, qcjmo__rnpjn)
        szt__ybead.data = qcjmo__rnpjn
        builder.store(szt__ybead._getvalue(), aamcf__vqpel)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    zjxjo__yyl = get_overload_const_str(ind)
    if zjxjo__yyl not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            zjxjo__yyl, struct))
    return struct.names.index(zjxjo__yyl)


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
    eev__alv = context.get_value_type(payload_type)
    gukus__copj = context.get_abi_sizeof(eev__alv)
    drcql__usmuh = define_struct_dtor(context, builder, struct_type,
        payload_type)
    rga__zut = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, gukus__copj), drcql__usmuh)
    zxvo__wwbwg = context.nrt.meminfo_data(builder, rga__zut)
    aamcf__vqpel = builder.bitcast(zxvo__wwbwg, eev__alv.as_pointer())
    szt__ybead = cgutils.create_struct_proxy(payload_type)(context, builder)
    szt__ybead.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    szt__ybead.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(szt__ybead._getvalue(), aamcf__vqpel)
    return rga__zut


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    uicg__fbmzl = tuple(d.dtype for d in struct_arr_typ.data)
    ajwb__tlg = StructType(uicg__fbmzl, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        zmoz__nyqe, ind = args
        szt__ybead = _get_struct_arr_payload(context, builder,
            struct_arr_typ, zmoz__nyqe)
        jexqw__bet = []
        ixd__rof = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            rmgsn__ckdv = builder.extract_value(szt__ybead.data, i)
            ijh__mpl = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [
                rmgsn__ckdv, ind])
            ixd__rof.append(ijh__mpl)
            vmu__krq = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            qefqv__twkz = builder.icmp_unsigned('==', ijh__mpl, lir.
                Constant(ijh__mpl.type, 1))
            with builder.if_then(qefqv__twkz):
                vrtn__fgfiw = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    rmgsn__ckdv, ind])
                builder.store(vrtn__fgfiw, vmu__krq)
            jexqw__bet.append(builder.load(vmu__krq))
        if isinstance(ajwb__tlg, types.DictType):
            qay__rqse = [context.insert_const_string(builder.module,
                nvush__ggwr) for nvush__ggwr in struct_arr_typ.names]
            cwhtu__dxpwk = cgutils.pack_array(builder, jexqw__bet)
            xcpp__nnm = cgutils.pack_array(builder, qay__rqse)

            def impl(names, vals):
                d = {}
                for i, nvush__ggwr in enumerate(names):
                    d[nvush__ggwr] = vals[i]
                return d
            yllow__kijn = context.compile_internal(builder, impl, ajwb__tlg
                (types.Tuple(tuple(types.StringLiteral(nvush__ggwr) for
                nvush__ggwr in struct_arr_typ.names)), types.Tuple(
                uicg__fbmzl)), [xcpp__nnm, cwhtu__dxpwk])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                uicg__fbmzl), cwhtu__dxpwk)
            return yllow__kijn
        rga__zut = construct_struct(context, builder, ajwb__tlg, jexqw__bet,
            ixd__rof)
        struct = context.make_helper(builder, ajwb__tlg)
        struct.meminfo = rga__zut
        return struct._getvalue()
    return ajwb__tlg(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        szt__ybead = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            szt__ybead.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        szt__ybead = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            szt__ybead.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(oejjf__tmuhh) for oejjf__tmuhh in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, gpb__fmiby, hqjn__xtly = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        eev__alv = context.get_value_type(payload_type)
        gukus__copj = context.get_abi_sizeof(eev__alv)
        drcql__usmuh = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        rga__zut = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, gukus__copj), drcql__usmuh)
        zxvo__wwbwg = context.nrt.meminfo_data(builder, rga__zut)
        aamcf__vqpel = builder.bitcast(zxvo__wwbwg, eev__alv.as_pointer())
        szt__ybead = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        szt__ybead.data = data
        szt__ybead.null_bitmap = gpb__fmiby
        builder.store(szt__ybead._getvalue(), aamcf__vqpel)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, gpb__fmiby)
        oqbp__wxajs = context.make_helper(builder, struct_arr_type)
        oqbp__wxajs.meminfo = rga__zut
        return oqbp__wxajs._getvalue()
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
    vqle__ktvov = len(arr.data)
    fbdsm__aqntg = 'def impl(arr, ind):\n'
    fbdsm__aqntg += '  data = get_data(arr)\n'
    fbdsm__aqntg += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        fbdsm__aqntg += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        fbdsm__aqntg += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        fbdsm__aqntg += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    fbdsm__aqntg += (
        '  return init_struct_arr(({},), out_null_bitmap, ({},))\n'.format(
        ', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for i in
        range(vqle__ktvov)), ', '.join("'{}'".format(nvush__ggwr) for
        nvush__ggwr in arr.names)))
    dgma__eyxar = {}
    exec(fbdsm__aqntg, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, dgma__eyxar)
    impl = dgma__eyxar['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        vqle__ktvov = len(arr.data)
        fbdsm__aqntg = 'def impl(arr, ind, val):\n'
        fbdsm__aqntg += '  data = get_data(arr)\n'
        fbdsm__aqntg += '  null_bitmap = get_null_bitmap(arr)\n'
        fbdsm__aqntg += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(vqle__ktvov):
            if isinstance(val, StructType):
                fbdsm__aqntg += ("  if is_field_value_null(val, '{}'):\n".
                    format(arr.names[i]))
                fbdsm__aqntg += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                fbdsm__aqntg += '  else:\n'
                fbdsm__aqntg += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                fbdsm__aqntg += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        dgma__eyxar = {}
        exec(fbdsm__aqntg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, dgma__eyxar)
        impl = dgma__eyxar['impl']
        return impl
    if isinstance(ind, types.SliceType):
        vqle__ktvov = len(arr.data)
        fbdsm__aqntg = 'def impl(arr, ind, val):\n'
        fbdsm__aqntg += '  data = get_data(arr)\n'
        fbdsm__aqntg += '  null_bitmap = get_null_bitmap(arr)\n'
        fbdsm__aqntg += '  val_data = get_data(val)\n'
        fbdsm__aqntg += '  val_null_bitmap = get_null_bitmap(val)\n'
        fbdsm__aqntg += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(vqle__ktvov):
            fbdsm__aqntg += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        dgma__eyxar = {}
        exec(fbdsm__aqntg, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, dgma__eyxar)
        impl = dgma__eyxar['impl']
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
    fbdsm__aqntg = 'def impl(A):\n'
    fbdsm__aqntg += '  total_nbytes = 0\n'
    fbdsm__aqntg += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        fbdsm__aqntg += f'  total_nbytes += data[{i}].nbytes\n'
    fbdsm__aqntg += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    fbdsm__aqntg += '  return total_nbytes\n'
    dgma__eyxar = {}
    exec(fbdsm__aqntg, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, dgma__eyxar)
    impl = dgma__eyxar['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        gpb__fmiby = get_null_bitmap(A)
        zzr__eyhbr = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        lxid__wdqv = gpb__fmiby.copy()
        return init_struct_arr(zzr__eyhbr, lxid__wdqv, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(ylxwv__prxae.copy() for ylxwv__prxae in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    wgbib__yvcpo = arrs.count
    fbdsm__aqntg = 'def f(arrs):\n'
    fbdsm__aqntg += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(wgbib__yvcpo)))
    dgma__eyxar = {}
    exec(fbdsm__aqntg, {}, dgma__eyxar)
    impl = dgma__eyxar['f']
    return impl
