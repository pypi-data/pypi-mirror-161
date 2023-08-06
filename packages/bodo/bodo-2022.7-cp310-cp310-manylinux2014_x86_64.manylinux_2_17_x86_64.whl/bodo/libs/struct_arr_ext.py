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
            .utils.is_array_typ(yftt__omf, False) for yftt__omf in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(yftt__omf,
                str) for yftt__omf in names) and len(names) == len(data)
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
        return StructType(tuple(hln__yhq.dtype for hln__yhq in self.data),
            self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(yftt__omf) for yftt__omf in d.keys())
        data = tuple(dtype_to_array_type(hln__yhq) for hln__yhq in d.values())
        return StructArrayType(data, names)

    def copy(self):
        return StructArrayType(self.data, self.names)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class StructArrayPayloadType(types.Type):

    def __init__(self, data):
        assert isinstance(data, tuple) and all(bodo.utils.utils.
            is_array_typ(yftt__omf, False) for yftt__omf in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        cjay__ajuef = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, cjay__ajuef)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        cjay__ajuef = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, cjay__ajuef)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    fwaqy__sfiqp = builder.module
    evaf__ftw = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    pdzw__hjr = cgutils.get_or_insert_function(fwaqy__sfiqp, evaf__ftw,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not pdzw__hjr.is_declaration:
        return pdzw__hjr
    pdzw__hjr.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(pdzw__hjr.append_basic_block())
    tmnsu__xav = pdzw__hjr.args[0]
    aqac__apilo = context.get_value_type(payload_type).as_pointer()
    ixsbx__gskew = builder.bitcast(tmnsu__xav, aqac__apilo)
    rhdsv__yksvy = context.make_helper(builder, payload_type, ref=ixsbx__gskew)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), rhdsv__yksvy.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        rhdsv__yksvy.null_bitmap)
    builder.ret_void()
    return pdzw__hjr


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    ena__rzoot = context.get_value_type(payload_type)
    qohib__aap = context.get_abi_sizeof(ena__rzoot)
    ieyb__jsjss = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    taof__rhcts = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qohib__aap), ieyb__jsjss)
    qdvzx__ivbnv = context.nrt.meminfo_data(builder, taof__rhcts)
    ehysk__ngcmj = builder.bitcast(qdvzx__ivbnv, ena__rzoot.as_pointer())
    rhdsv__yksvy = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    thu__opvgx = 0
    for arr_typ in struct_arr_type.data:
        tmu__yeu = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        ymepb__ligw = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(thu__opvgx, thu__opvgx +
            tmu__yeu)])
        arr = gen_allocate_array(context, builder, arr_typ, ymepb__ligw, c)
        arrs.append(arr)
        thu__opvgx += tmu__yeu
    rhdsv__yksvy.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    eyh__xfnjo = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    sfh__mdk = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [eyh__xfnjo])
    null_bitmap_ptr = sfh__mdk.data
    rhdsv__yksvy.null_bitmap = sfh__mdk._getvalue()
    builder.store(rhdsv__yksvy._getvalue(), ehysk__ngcmj)
    return taof__rhcts, rhdsv__yksvy.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    hdsy__vgncy = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        uojrz__vui = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            uojrz__vui)
        hdsy__vgncy.append(arr.data)
    iyvlj__aougx = cgutils.pack_array(c.builder, hdsy__vgncy
        ) if types.is_homogeneous(*data_typ) else cgutils.pack_struct(c.
        builder, hdsy__vgncy)
    ivsej__jcju = cgutils.alloca_once_value(c.builder, iyvlj__aougx)
    ysfv__pifui = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(yftt__omf.dtype)) for yftt__omf in data_typ]
    zdfbv__iwlb = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c
        .builder, ysfv__pifui))
    dyv__ffpm = cgutils.pack_array(c.builder, [c.context.
        insert_const_string(c.builder.module, yftt__omf) for yftt__omf in
        names])
    ofsp__mggyb = cgutils.alloca_once_value(c.builder, dyv__ffpm)
    return ivsej__jcju, zdfbv__iwlb, ofsp__mggyb


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    tvtsh__xnsh = all(isinstance(hln__yhq, types.Array) and hln__yhq.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        hln__yhq in typ.data)
    if tvtsh__xnsh:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        kjmq__dpwm = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            kjmq__dpwm, i) for i in range(1, kjmq__dpwm.type.count)], lir.
            IntType(64))
    taof__rhcts, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if tvtsh__xnsh:
        ivsej__jcju, zdfbv__iwlb, ofsp__mggyb = _get_C_API_ptrs(c, data_tup,
            typ.data, typ.names)
        evaf__ftw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        pdzw__hjr = cgutils.get_or_insert_function(c.builder.module,
            evaf__ftw, name='struct_array_from_sequence')
        c.builder.call(pdzw__hjr, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(ivsej__jcju, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(zdfbv__iwlb,
            lir.IntType(8).as_pointer()), c.builder.bitcast(ofsp__mggyb,
            lir.IntType(8).as_pointer()), c.context.get_constant(types.
            bool_, is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    zvpjx__qtg = c.context.make_helper(c.builder, typ)
    zvpjx__qtg.meminfo = taof__rhcts
    jqk__gsa = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zvpjx__qtg._getvalue(), is_error=jqk__gsa)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    bebmx__hlfmq = context.insert_const_string(builder.module, 'pandas')
    hwg__tty = c.pyapi.import_module_noblock(bebmx__hlfmq)
    inbp__okt = c.pyapi.object_getattr_string(hwg__tty, 'NA')
    with cgutils.for_range(builder, n_structs) as prjf__dyalm:
        zrsz__gbvrp = prjf__dyalm.index
        lznmo__ylbtt = seq_getitem(builder, context, val, zrsz__gbvrp)
        set_bitmap_bit(builder, null_bitmap_ptr, zrsz__gbvrp, 0)
        for bja__ssmjd in range(len(typ.data)):
            arr_typ = typ.data[bja__ssmjd]
            data_arr = builder.extract_value(data_tup, bja__ssmjd)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            dcm__pef, oew__lvp = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, zrsz__gbvrp])
        fxv__ppi = is_na_value(builder, context, lznmo__ylbtt, inbp__okt)
        coa__dbe = builder.icmp_unsigned('!=', fxv__ppi, lir.Constant(
            fxv__ppi.type, 1))
        with builder.if_then(coa__dbe):
            set_bitmap_bit(builder, null_bitmap_ptr, zrsz__gbvrp, 1)
            for bja__ssmjd in range(len(typ.data)):
                arr_typ = typ.data[bja__ssmjd]
                if is_tuple_array:
                    sen__kwlpn = c.pyapi.tuple_getitem(lznmo__ylbtt, bja__ssmjd
                        )
                else:
                    sen__kwlpn = c.pyapi.dict_getitem_string(lznmo__ylbtt,
                        typ.names[bja__ssmjd])
                fxv__ppi = is_na_value(builder, context, sen__kwlpn, inbp__okt)
                coa__dbe = builder.icmp_unsigned('!=', fxv__ppi, lir.
                    Constant(fxv__ppi.type, 1))
                with builder.if_then(coa__dbe):
                    sen__kwlpn = to_arr_obj_if_list_obj(c, context, builder,
                        sen__kwlpn, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        sen__kwlpn).value
                    data_arr = builder.extract_value(data_tup, bja__ssmjd)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    dcm__pef, oew__lvp = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, zrsz__gbvrp, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(lznmo__ylbtt)
    c.pyapi.decref(hwg__tty)
    c.pyapi.decref(inbp__okt)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    zvpjx__qtg = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    qdvzx__ivbnv = context.nrt.meminfo_data(builder, zvpjx__qtg.meminfo)
    ehysk__ngcmj = builder.bitcast(qdvzx__ivbnv, context.get_value_type(
        payload_type).as_pointer())
    rhdsv__yksvy = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(ehysk__ngcmj))
    return rhdsv__yksvy


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    rhdsv__yksvy = _get_struct_arr_payload(c.context, c.builder, typ, val)
    dcm__pef, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64(
        typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), rhdsv__yksvy.null_bitmap).data
    tvtsh__xnsh = all(isinstance(hln__yhq, types.Array) and hln__yhq.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        hln__yhq in typ.data)
    if tvtsh__xnsh:
        ivsej__jcju, zdfbv__iwlb, ofsp__mggyb = _get_C_API_ptrs(c,
            rhdsv__yksvy.data, typ.data, typ.names)
        evaf__ftw = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        sndrd__vnmzr = cgutils.get_or_insert_function(c.builder.module,
            evaf__ftw, name='np_array_from_struct_array')
        arr = c.builder.call(sndrd__vnmzr, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(ivsej__jcju, lir
            .IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            zdfbv__iwlb, lir.IntType(8).as_pointer()), c.builder.bitcast(
            ofsp__mggyb, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, rhdsv__yksvy.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    bebmx__hlfmq = context.insert_const_string(builder.module, 'numpy')
    jhcc__kxfb = c.pyapi.import_module_noblock(bebmx__hlfmq)
    hano__wuhpe = c.pyapi.object_getattr_string(jhcc__kxfb, 'object_')
    sjiq__erg = c.pyapi.long_from_longlong(length)
    wejmp__mpeoo = c.pyapi.call_method(jhcc__kxfb, 'ndarray', (sjiq__erg,
        hano__wuhpe))
    xllqw__rcca = c.pyapi.object_getattr_string(jhcc__kxfb, 'nan')
    with cgutils.for_range(builder, length) as prjf__dyalm:
        zrsz__gbvrp = prjf__dyalm.index
        pyarray_setitem(builder, context, wejmp__mpeoo, zrsz__gbvrp,
            xllqw__rcca)
        eoqil__gzylr = get_bitmap_bit(builder, null_bitmap_ptr, zrsz__gbvrp)
        tfa__jcmp = builder.icmp_unsigned('!=', eoqil__gzylr, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(tfa__jcmp):
            if is_tuple_array:
                lznmo__ylbtt = c.pyapi.tuple_new(len(typ.data))
            else:
                lznmo__ylbtt = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(xllqw__rcca)
                    c.pyapi.tuple_setitem(lznmo__ylbtt, i, xllqw__rcca)
                else:
                    c.pyapi.dict_setitem_string(lznmo__ylbtt, typ.names[i],
                        xllqw__rcca)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                dcm__pef, nfdk__robk = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, zrsz__gbvrp])
                with builder.if_then(nfdk__robk):
                    dcm__pef, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, zrsz__gbvrp])
                    isbe__ckan = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(lznmo__ylbtt, i, isbe__ckan)
                    else:
                        c.pyapi.dict_setitem_string(lznmo__ylbtt, typ.names
                            [i], isbe__ckan)
                        c.pyapi.decref(isbe__ckan)
            pyarray_setitem(builder, context, wejmp__mpeoo, zrsz__gbvrp,
                lznmo__ylbtt)
            c.pyapi.decref(lznmo__ylbtt)
    c.pyapi.decref(jhcc__kxfb)
    c.pyapi.decref(hano__wuhpe)
    c.pyapi.decref(sjiq__erg)
    c.pyapi.decref(xllqw__rcca)
    return wejmp__mpeoo


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    apdkv__bbhat = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if apdkv__bbhat == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for dnoeh__lzj in range(apdkv__bbhat)])
    elif nested_counts_type.count < apdkv__bbhat:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for dnoeh__lzj in range(
            apdkv__bbhat - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(hln__yhq) for hln__yhq in
            names_typ.types)
    basz__vjop = tuple(hln__yhq.instance_type for hln__yhq in dtypes_typ.types)
    struct_arr_type = StructArrayType(basz__vjop, names)

    def codegen(context, builder, sig, args):
        ehpq__jlni, nested_counts, dnoeh__lzj, dnoeh__lzj = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        taof__rhcts, dnoeh__lzj, dnoeh__lzj = construct_struct_array(context,
            builder, struct_arr_type, ehpq__jlni, nested_counts)
        zvpjx__qtg = context.make_helper(builder, struct_arr_type)
        zvpjx__qtg.meminfo = taof__rhcts
        return zvpjx__qtg._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(yftt__omf, str) for
            yftt__omf in names) and len(names) == len(data)
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
        cjay__ajuef = [('data', types.BaseTuple.from_types(fe_type.data)),
            ('null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, cjay__ajuef)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        cjay__ajuef = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, cjay__ajuef)


def define_struct_dtor(context, builder, struct_type, payload_type):
    fwaqy__sfiqp = builder.module
    evaf__ftw = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    pdzw__hjr = cgutils.get_or_insert_function(fwaqy__sfiqp, evaf__ftw,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not pdzw__hjr.is_declaration:
        return pdzw__hjr
    pdzw__hjr.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(pdzw__hjr.append_basic_block())
    tmnsu__xav = pdzw__hjr.args[0]
    aqac__apilo = context.get_value_type(payload_type).as_pointer()
    ixsbx__gskew = builder.bitcast(tmnsu__xav, aqac__apilo)
    rhdsv__yksvy = context.make_helper(builder, payload_type, ref=ixsbx__gskew)
    for i in range(len(struct_type.data)):
        ecttf__zjxd = builder.extract_value(rhdsv__yksvy.null_bitmap, i)
        tfa__jcmp = builder.icmp_unsigned('==', ecttf__zjxd, lir.Constant(
            ecttf__zjxd.type, 1))
        with builder.if_then(tfa__jcmp):
            val = builder.extract_value(rhdsv__yksvy.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return pdzw__hjr


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    qdvzx__ivbnv = context.nrt.meminfo_data(builder, struct.meminfo)
    ehysk__ngcmj = builder.bitcast(qdvzx__ivbnv, context.get_value_type(
        payload_type).as_pointer())
    rhdsv__yksvy = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(ehysk__ngcmj))
    return rhdsv__yksvy, ehysk__ngcmj


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    bebmx__hlfmq = context.insert_const_string(builder.module, 'pandas')
    hwg__tty = c.pyapi.import_module_noblock(bebmx__hlfmq)
    inbp__okt = c.pyapi.object_getattr_string(hwg__tty, 'NA')
    klet__rvv = []
    nulls = []
    for i, hln__yhq in enumerate(typ.data):
        isbe__ckan = c.pyapi.dict_getitem_string(val, typ.names[i])
        mehp__rve = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        ujlt__mcy = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(hln__yhq)))
        fxv__ppi = is_na_value(builder, context, isbe__ckan, inbp__okt)
        tfa__jcmp = builder.icmp_unsigned('!=', fxv__ppi, lir.Constant(
            fxv__ppi.type, 1))
        with builder.if_then(tfa__jcmp):
            builder.store(context.get_constant(types.uint8, 1), mehp__rve)
            field_val = c.pyapi.to_native_value(hln__yhq, isbe__ckan).value
            builder.store(field_val, ujlt__mcy)
        klet__rvv.append(builder.load(ujlt__mcy))
        nulls.append(builder.load(mehp__rve))
    c.pyapi.decref(hwg__tty)
    c.pyapi.decref(inbp__okt)
    taof__rhcts = construct_struct(context, builder, typ, klet__rvv, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = taof__rhcts
    jqk__gsa = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=jqk__gsa)


@box(StructType)
def box_struct(typ, val, c):
    eyoy__wjy = c.pyapi.dict_new(len(typ.data))
    rhdsv__yksvy, dnoeh__lzj = _get_struct_payload(c.context, c.builder,
        typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(eyoy__wjy, typ.names[i], c.pyapi.
            borrow_none())
        ecttf__zjxd = c.builder.extract_value(rhdsv__yksvy.null_bitmap, i)
        tfa__jcmp = c.builder.icmp_unsigned('==', ecttf__zjxd, lir.Constant
            (ecttf__zjxd.type, 1))
        with c.builder.if_then(tfa__jcmp):
            dcdkd__hnpzc = c.builder.extract_value(rhdsv__yksvy.data, i)
            c.context.nrt.incref(c.builder, val_typ, dcdkd__hnpzc)
            sen__kwlpn = c.pyapi.from_native_value(val_typ, dcdkd__hnpzc, c
                .env_manager)
            c.pyapi.dict_setitem_string(eyoy__wjy, typ.names[i], sen__kwlpn)
            c.pyapi.decref(sen__kwlpn)
    c.context.nrt.decref(c.builder, typ, val)
    return eyoy__wjy


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(hln__yhq) for hln__yhq in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, sdnz__tfwha = args
        payload_type = StructPayloadType(struct_type.data)
        ena__rzoot = context.get_value_type(payload_type)
        qohib__aap = context.get_abi_sizeof(ena__rzoot)
        ieyb__jsjss = define_struct_dtor(context, builder, struct_type,
            payload_type)
        taof__rhcts = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, qohib__aap), ieyb__jsjss)
        qdvzx__ivbnv = context.nrt.meminfo_data(builder, taof__rhcts)
        ehysk__ngcmj = builder.bitcast(qdvzx__ivbnv, ena__rzoot.as_pointer())
        rhdsv__yksvy = cgutils.create_struct_proxy(payload_type)(context,
            builder)
        rhdsv__yksvy.data = data
        rhdsv__yksvy.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for dnoeh__lzj in range(len(
            data_typ.types))])
        builder.store(rhdsv__yksvy._getvalue(), ehysk__ngcmj)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = taof__rhcts
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        rhdsv__yksvy, dnoeh__lzj = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rhdsv__yksvy.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        rhdsv__yksvy, dnoeh__lzj = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rhdsv__yksvy.null_bitmap)
    cyror__ypqx = types.UniTuple(types.int8, len(struct_typ.data))
    return cyror__ypqx(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, dnoeh__lzj, val = args
        rhdsv__yksvy, ehysk__ngcmj = _get_struct_payload(context, builder,
            struct_typ, struct)
        ttjx__apbt = rhdsv__yksvy.data
        zsllo__ucnvo = builder.insert_value(ttjx__apbt, val, field_ind)
        wcn__mxwyo = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, wcn__mxwyo, ttjx__apbt)
        context.nrt.incref(builder, wcn__mxwyo, zsllo__ucnvo)
        rhdsv__yksvy.data = zsllo__ucnvo
        builder.store(rhdsv__yksvy._getvalue(), ehysk__ngcmj)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    ujvkx__bibyt = get_overload_const_str(ind)
    if ujvkx__bibyt not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            ujvkx__bibyt, struct))
    return struct.names.index(ujvkx__bibyt)


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
    ena__rzoot = context.get_value_type(payload_type)
    qohib__aap = context.get_abi_sizeof(ena__rzoot)
    ieyb__jsjss = define_struct_dtor(context, builder, struct_type,
        payload_type)
    taof__rhcts = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qohib__aap), ieyb__jsjss)
    qdvzx__ivbnv = context.nrt.meminfo_data(builder, taof__rhcts)
    ehysk__ngcmj = builder.bitcast(qdvzx__ivbnv, ena__rzoot.as_pointer())
    rhdsv__yksvy = cgutils.create_struct_proxy(payload_type)(context, builder)
    rhdsv__yksvy.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    rhdsv__yksvy.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(rhdsv__yksvy._getvalue(), ehysk__ngcmj)
    return taof__rhcts


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    mvy__owbdz = tuple(d.dtype for d in struct_arr_typ.data)
    buta__ypho = StructType(mvy__owbdz, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        xsgc__xdqma, ind = args
        rhdsv__yksvy = _get_struct_arr_payload(context, builder,
            struct_arr_typ, xsgc__xdqma)
        klet__rvv = []
        xrmk__ksmq = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            uojrz__vui = builder.extract_value(rhdsv__yksvy.data, i)
            edc__myg = context.compile_internal(builder, lambda arr, ind: 
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [uojrz__vui,
                ind])
            xrmk__ksmq.append(edc__myg)
            bhree__zoqyf = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            tfa__jcmp = builder.icmp_unsigned('==', edc__myg, lir.Constant(
                edc__myg.type, 1))
            with builder.if_then(tfa__jcmp):
                pbmx__oily = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    uojrz__vui, ind])
                builder.store(pbmx__oily, bhree__zoqyf)
            klet__rvv.append(builder.load(bhree__zoqyf))
        if isinstance(buta__ypho, types.DictType):
            ymp__xbmo = [context.insert_const_string(builder.module,
                vpooo__tvx) for vpooo__tvx in struct_arr_typ.names]
            htorz__ziuek = cgutils.pack_array(builder, klet__rvv)
            huej__mhlnp = cgutils.pack_array(builder, ymp__xbmo)

            def impl(names, vals):
                d = {}
                for i, vpooo__tvx in enumerate(names):
                    d[vpooo__tvx] = vals[i]
                return d
            hsbn__sifbh = context.compile_internal(builder, impl,
                buta__ypho(types.Tuple(tuple(types.StringLiteral(vpooo__tvx
                ) for vpooo__tvx in struct_arr_typ.names)), types.Tuple(
                mvy__owbdz)), [huej__mhlnp, htorz__ziuek])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                mvy__owbdz), htorz__ziuek)
            return hsbn__sifbh
        taof__rhcts = construct_struct(context, builder, buta__ypho,
            klet__rvv, xrmk__ksmq)
        struct = context.make_helper(builder, buta__ypho)
        struct.meminfo = taof__rhcts
        return struct._getvalue()
    return buta__ypho(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        rhdsv__yksvy = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rhdsv__yksvy.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        rhdsv__yksvy = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            rhdsv__yksvy.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(hln__yhq) for hln__yhq in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, sfh__mdk, sdnz__tfwha = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        ena__rzoot = context.get_value_type(payload_type)
        qohib__aap = context.get_abi_sizeof(ena__rzoot)
        ieyb__jsjss = define_struct_arr_dtor(context, builder,
            struct_arr_type, payload_type)
        taof__rhcts = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, qohib__aap), ieyb__jsjss)
        qdvzx__ivbnv = context.nrt.meminfo_data(builder, taof__rhcts)
        ehysk__ngcmj = builder.bitcast(qdvzx__ivbnv, ena__rzoot.as_pointer())
        rhdsv__yksvy = cgutils.create_struct_proxy(payload_type)(context,
            builder)
        rhdsv__yksvy.data = data
        rhdsv__yksvy.null_bitmap = sfh__mdk
        builder.store(rhdsv__yksvy._getvalue(), ehysk__ngcmj)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, sfh__mdk)
        zvpjx__qtg = context.make_helper(builder, struct_arr_type)
        zvpjx__qtg.meminfo = taof__rhcts
        return zvpjx__qtg._getvalue()
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
    gobkw__phc = len(arr.data)
    ggu__ool = 'def impl(arr, ind):\n'
    ggu__ool += '  data = get_data(arr)\n'
    ggu__ool += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        ggu__ool += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        ggu__ool += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        ggu__ool += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    ggu__ool += ('  return init_struct_arr(({},), out_null_bitmap, ({},))\n'
        .format(', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for
        i in range(gobkw__phc)), ', '.join("'{}'".format(vpooo__tvx) for
        vpooo__tvx in arr.names)))
    dctlh__gnkwg = {}
    exec(ggu__ool, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, dctlh__gnkwg)
    impl = dctlh__gnkwg['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        gobkw__phc = len(arr.data)
        ggu__ool = 'def impl(arr, ind, val):\n'
        ggu__ool += '  data = get_data(arr)\n'
        ggu__ool += '  null_bitmap = get_null_bitmap(arr)\n'
        ggu__ool += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(gobkw__phc):
            if isinstance(val, StructType):
                ggu__ool += "  if is_field_value_null(val, '{}'):\n".format(arr
                    .names[i])
                ggu__ool += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                ggu__ool += '  else:\n'
                ggu__ool += "    data[{}][ind] = val['{}']\n".format(i, arr
                    .names[i])
            else:
                ggu__ool += "  data[{}][ind] = val['{}']\n".format(i, arr.
                    names[i])
        dctlh__gnkwg = {}
        exec(ggu__ool, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, dctlh__gnkwg)
        impl = dctlh__gnkwg['impl']
        return impl
    if isinstance(ind, types.SliceType):
        gobkw__phc = len(arr.data)
        ggu__ool = 'def impl(arr, ind, val):\n'
        ggu__ool += '  data = get_data(arr)\n'
        ggu__ool += '  null_bitmap = get_null_bitmap(arr)\n'
        ggu__ool += '  val_data = get_data(val)\n'
        ggu__ool += '  val_null_bitmap = get_null_bitmap(val)\n'
        ggu__ool += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(gobkw__phc):
            ggu__ool += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        dctlh__gnkwg = {}
        exec(ggu__ool, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, dctlh__gnkwg)
        impl = dctlh__gnkwg['impl']
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
    ggu__ool = 'def impl(A):\n'
    ggu__ool += '  total_nbytes = 0\n'
    ggu__ool += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        ggu__ool += f'  total_nbytes += data[{i}].nbytes\n'
    ggu__ool += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    ggu__ool += '  return total_nbytes\n'
    dctlh__gnkwg = {}
    exec(ggu__ool, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, dctlh__gnkwg)
    impl = dctlh__gnkwg['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        sfh__mdk = get_null_bitmap(A)
        hoho__akn = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        gctc__qhpqk = sfh__mdk.copy()
        return init_struct_arr(hoho__akn, gctc__qhpqk, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(yftt__omf.copy() for yftt__omf in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    tixhi__xxac = arrs.count
    ggu__ool = 'def f(arrs):\n'
    ggu__ool += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.format
        (i) for i in range(tixhi__xxac)))
    dctlh__gnkwg = {}
    exec(ggu__ool, {}, dctlh__gnkwg)
    impl = dctlh__gnkwg['f']
    return impl
