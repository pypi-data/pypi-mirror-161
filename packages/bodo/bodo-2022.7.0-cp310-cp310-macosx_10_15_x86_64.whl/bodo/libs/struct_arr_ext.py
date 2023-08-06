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
            .utils.is_array_typ(wxo__nvdo, False) for wxo__nvdo in data)
        if names is not None:
            assert isinstance(names, tuple) and all(isinstance(wxo__nvdo,
                str) for wxo__nvdo in names) and len(names) == len(data)
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
        return StructType(tuple(jolsq__mvh.dtype for jolsq__mvh in self.
            data), self.names)

    @classmethod
    def from_dict(cls, d):
        assert isinstance(d, dict)
        names = tuple(str(wxo__nvdo) for wxo__nvdo in d.keys())
        data = tuple(dtype_to_array_type(jolsq__mvh) for jolsq__mvh in d.
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
            is_array_typ(wxo__nvdo, False) for wxo__nvdo in data)
        self.data = data
        super(StructArrayPayloadType, self).__init__(name=
            'StructArrayPayloadType({})'.format(data))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(StructArrayPayloadType)
class StructArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ezx__ddwl = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, ezx__ddwl)


@register_model(StructArrayType)
class StructArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructArrayPayloadType(fe_type.data)
        ezx__ddwl = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, ezx__ddwl)


def define_struct_arr_dtor(context, builder, struct_arr_type, payload_type):
    ijmdi__egwll = builder.module
    hvlq__vvw = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    qeau__obx = cgutils.get_or_insert_function(ijmdi__egwll, hvlq__vvw,
        name='.dtor.struct_arr.{}.{}.'.format(struct_arr_type.data,
        struct_arr_type.names))
    if not qeau__obx.is_declaration:
        return qeau__obx
    qeau__obx.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(qeau__obx.append_basic_block())
    pgltr__lzcrf = qeau__obx.args[0]
    vxbzw__jnq = context.get_value_type(payload_type).as_pointer()
    lvvnk__uaheq = builder.bitcast(pgltr__lzcrf, vxbzw__jnq)
    gkx__jhmof = context.make_helper(builder, payload_type, ref=lvvnk__uaheq)
    context.nrt.decref(builder, types.BaseTuple.from_types(struct_arr_type.
        data), gkx__jhmof.data)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        gkx__jhmof.null_bitmap)
    builder.ret_void()
    return qeau__obx


def construct_struct_array(context, builder, struct_arr_type, n_structs,
    n_elems, c=None):
    payload_type = StructArrayPayloadType(struct_arr_type.data)
    pzlae__bnksr = context.get_value_type(payload_type)
    keyzu__tlgmk = context.get_abi_sizeof(pzlae__bnksr)
    nwo__tpe = define_struct_arr_dtor(context, builder, struct_arr_type,
        payload_type)
    cref__qytmh = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, keyzu__tlgmk), nwo__tpe)
    izce__vpfdv = context.nrt.meminfo_data(builder, cref__qytmh)
    cgxz__fcr = builder.bitcast(izce__vpfdv, pzlae__bnksr.as_pointer())
    gkx__jhmof = cgutils.create_struct_proxy(payload_type)(context, builder)
    arrs = []
    gfpy__ndsjq = 0
    for arr_typ in struct_arr_type.data:
        xsf__ntu = bodo.utils.transform.get_type_alloc_counts(arr_typ.dtype)
        bog__roizq = cgutils.pack_array(builder, [n_structs] + [builder.
            extract_value(n_elems, i) for i in range(gfpy__ndsjq, 
            gfpy__ndsjq + xsf__ntu)])
        arr = gen_allocate_array(context, builder, arr_typ, bog__roizq, c)
        arrs.append(arr)
        gfpy__ndsjq += xsf__ntu
    gkx__jhmof.data = cgutils.pack_array(builder, arrs
        ) if types.is_homogeneous(*struct_arr_type.data
        ) else cgutils.pack_struct(builder, arrs)
    rrj__ycrzz = builder.udiv(builder.add(n_structs, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    gsepg__oiyxg = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [rrj__ycrzz])
    null_bitmap_ptr = gsepg__oiyxg.data
    gkx__jhmof.null_bitmap = gsepg__oiyxg._getvalue()
    builder.store(gkx__jhmof._getvalue(), cgxz__fcr)
    return cref__qytmh, gkx__jhmof.data, null_bitmap_ptr


def _get_C_API_ptrs(c, data_tup, data_typ, names):
    wda__jjh = []
    assert len(data_typ) > 0
    for i, arr_typ in enumerate(data_typ):
        zqsn__ixa = c.builder.extract_value(data_tup, i)
        arr = c.context.make_array(arr_typ)(c.context, c.builder, value=
            zqsn__ixa)
        wda__jjh.append(arr.data)
    eue__rrw = cgutils.pack_array(c.builder, wda__jjh) if types.is_homogeneous(
        *data_typ) else cgutils.pack_struct(c.builder, wda__jjh)
    vgsn__gveg = cgutils.alloca_once_value(c.builder, eue__rrw)
    gxof__rhm = [c.context.get_constant(types.int32, bodo.utils.utils.
        numba_to_c_type(wxo__nvdo.dtype)) for wxo__nvdo in data_typ]
    vdy__bcs = cgutils.alloca_once_value(c.builder, cgutils.pack_array(c.
        builder, gxof__rhm))
    goa__sic = cgutils.pack_array(c.builder, [c.context.insert_const_string
        (c.builder.module, wxo__nvdo) for wxo__nvdo in names])
    klpfq__pfh = cgutils.alloca_once_value(c.builder, goa__sic)
    return vgsn__gveg, vdy__bcs, klpfq__pfh


@unbox(StructArrayType)
def unbox_struct_array(typ, val, c, is_tuple_array=False):
    from bodo.libs.tuple_arr_ext import TupleArrayType
    n_structs = bodo.utils.utils.object_length(c, val)
    jfnp__eckdt = all(isinstance(jolsq__mvh, types.Array) and jolsq__mvh.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for jolsq__mvh in typ.data)
    if jfnp__eckdt:
        n_elems = cgutils.pack_array(c.builder, [], lir.IntType(64))
    else:
        tegm__cimnq = get_array_elem_counts(c, c.builder, c.context, val, 
            TupleArrayType(typ.data) if is_tuple_array else typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            tegm__cimnq, i) for i in range(1, tegm__cimnq.type.count)], lir
            .IntType(64))
    cref__qytmh, data_tup, null_bitmap_ptr = construct_struct_array(c.
        context, c.builder, typ, n_structs, n_elems, c)
    if jfnp__eckdt:
        vgsn__gveg, vdy__bcs, klpfq__pfh = _get_C_API_ptrs(c, data_tup, typ
            .data, typ.names)
        hvlq__vvw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1)])
        qeau__obx = cgutils.get_or_insert_function(c.builder.module,
            hvlq__vvw, name='struct_array_from_sequence')
        c.builder.call(qeau__obx, [val, c.context.get_constant(types.int32,
            len(typ.data)), c.builder.bitcast(vgsn__gveg, lir.IntType(8).
            as_pointer()), null_bitmap_ptr, c.builder.bitcast(vdy__bcs, lir
            .IntType(8).as_pointer()), c.builder.bitcast(klpfq__pfh, lir.
            IntType(8).as_pointer()), c.context.get_constant(types.bool_,
            is_tuple_array)])
    else:
        _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
            null_bitmap_ptr, is_tuple_array)
    weu__pfl = c.context.make_helper(c.builder, typ)
    weu__pfl.meminfo = cref__qytmh
    hyg__skyv = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(weu__pfl._getvalue(), is_error=hyg__skyv)


def _unbox_struct_array_generic(typ, val, c, n_structs, data_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    ngwpq__ajgv = context.insert_const_string(builder.module, 'pandas')
    cha__rmpl = c.pyapi.import_module_noblock(ngwpq__ajgv)
    tjqk__puxlp = c.pyapi.object_getattr_string(cha__rmpl, 'NA')
    with cgutils.for_range(builder, n_structs) as lwy__nhe:
        emo__gli = lwy__nhe.index
        xhs__oqglm = seq_getitem(builder, context, val, emo__gli)
        set_bitmap_bit(builder, null_bitmap_ptr, emo__gli, 0)
        for rgq__rwpf in range(len(typ.data)):
            arr_typ = typ.data[rgq__rwpf]
            data_arr = builder.extract_value(data_tup, rgq__rwpf)

            def set_na(data_arr, i):
                bodo.libs.array_kernels.setna(data_arr, i)
            sig = types.none(arr_typ, types.int64)
            hby__amxv, rxh__jtvbh = c.pyapi.call_jit_code(set_na, sig, [
                data_arr, emo__gli])
        zpib__orm = is_na_value(builder, context, xhs__oqglm, tjqk__puxlp)
        ymx__mxv = builder.icmp_unsigned('!=', zpib__orm, lir.Constant(
            zpib__orm.type, 1))
        with builder.if_then(ymx__mxv):
            set_bitmap_bit(builder, null_bitmap_ptr, emo__gli, 1)
            for rgq__rwpf in range(len(typ.data)):
                arr_typ = typ.data[rgq__rwpf]
                if is_tuple_array:
                    phcee__mgbhz = c.pyapi.tuple_getitem(xhs__oqglm, rgq__rwpf)
                else:
                    phcee__mgbhz = c.pyapi.dict_getitem_string(xhs__oqglm,
                        typ.names[rgq__rwpf])
                zpib__orm = is_na_value(builder, context, phcee__mgbhz,
                    tjqk__puxlp)
                ymx__mxv = builder.icmp_unsigned('!=', zpib__orm, lir.
                    Constant(zpib__orm.type, 1))
                with builder.if_then(ymx__mxv):
                    phcee__mgbhz = to_arr_obj_if_list_obj(c, context,
                        builder, phcee__mgbhz, arr_typ.dtype)
                    field_val = c.pyapi.to_native_value(arr_typ.dtype,
                        phcee__mgbhz).value
                    data_arr = builder.extract_value(data_tup, rgq__rwpf)

                    def set_data(data_arr, i, field_val):
                        data_arr[i] = field_val
                    sig = types.none(arr_typ, types.int64, arr_typ.dtype)
                    hby__amxv, rxh__jtvbh = c.pyapi.call_jit_code(set_data,
                        sig, [data_arr, emo__gli, field_val])
                    c.context.nrt.decref(builder, arr_typ.dtype, field_val)
        c.pyapi.decref(xhs__oqglm)
    c.pyapi.decref(cha__rmpl)
    c.pyapi.decref(tjqk__puxlp)


def _get_struct_arr_payload(context, builder, arr_typ, arr):
    weu__pfl = context.make_helper(builder, arr_typ, arr)
    payload_type = StructArrayPayloadType(arr_typ.data)
    izce__vpfdv = context.nrt.meminfo_data(builder, weu__pfl.meminfo)
    cgxz__fcr = builder.bitcast(izce__vpfdv, context.get_value_type(
        payload_type).as_pointer())
    gkx__jhmof = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(cgxz__fcr))
    return gkx__jhmof


@box(StructArrayType)
def box_struct_arr(typ, val, c, is_tuple_array=False):
    gkx__jhmof = _get_struct_arr_payload(c.context, c.builder, typ, val)
    hby__amxv, length = c.pyapi.call_jit_code(lambda A: len(A), types.int64
        (typ), [val])
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), gkx__jhmof.null_bitmap).data
    jfnp__eckdt = all(isinstance(jolsq__mvh, types.Array) and jolsq__mvh.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for jolsq__mvh in typ.data)
    if jfnp__eckdt:
        vgsn__gveg, vdy__bcs, klpfq__pfh = _get_C_API_ptrs(c, gkx__jhmof.
            data, typ.data, typ.names)
        hvlq__vvw = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(32), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        wsf__whlgo = cgutils.get_or_insert_function(c.builder.module,
            hvlq__vvw, name='np_array_from_struct_array')
        arr = c.builder.call(wsf__whlgo, [length, c.context.get_constant(
            types.int32, len(typ.data)), c.builder.bitcast(vgsn__gveg, lir.
            IntType(8).as_pointer()), null_bitmap_ptr, c.builder.bitcast(
            vdy__bcs, lir.IntType(8).as_pointer()), c.builder.bitcast(
            klpfq__pfh, lir.IntType(8).as_pointer()), c.context.
            get_constant(types.bool_, is_tuple_array)])
    else:
        arr = _box_struct_array_generic(typ, c, length, gkx__jhmof.data,
            null_bitmap_ptr, is_tuple_array)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_struct_array_generic(typ, c, length, data_arrs_tup,
    null_bitmap_ptr, is_tuple_array=False):
    context = c.context
    builder = c.builder
    ngwpq__ajgv = context.insert_const_string(builder.module, 'numpy')
    bvy__gocvu = c.pyapi.import_module_noblock(ngwpq__ajgv)
    dgvfe__fjwtg = c.pyapi.object_getattr_string(bvy__gocvu, 'object_')
    scoj__rqyal = c.pyapi.long_from_longlong(length)
    axx__yyee = c.pyapi.call_method(bvy__gocvu, 'ndarray', (scoj__rqyal,
        dgvfe__fjwtg))
    ebc__hdq = c.pyapi.object_getattr_string(bvy__gocvu, 'nan')
    with cgutils.for_range(builder, length) as lwy__nhe:
        emo__gli = lwy__nhe.index
        pyarray_setitem(builder, context, axx__yyee, emo__gli, ebc__hdq)
        ewc__jnn = get_bitmap_bit(builder, null_bitmap_ptr, emo__gli)
        uek__yfzp = builder.icmp_unsigned('!=', ewc__jnn, lir.Constant(lir.
            IntType(8), 0))
        with builder.if_then(uek__yfzp):
            if is_tuple_array:
                xhs__oqglm = c.pyapi.tuple_new(len(typ.data))
            else:
                xhs__oqglm = c.pyapi.dict_new(len(typ.data))
            for i, arr_typ in enumerate(typ.data):
                if is_tuple_array:
                    c.pyapi.incref(ebc__hdq)
                    c.pyapi.tuple_setitem(xhs__oqglm, i, ebc__hdq)
                else:
                    c.pyapi.dict_setitem_string(xhs__oqglm, typ.names[i],
                        ebc__hdq)
                data_arr = c.builder.extract_value(data_arrs_tup, i)
                hby__amxv, ezbkg__ckrtn = c.pyapi.call_jit_code(lambda
                    data_arr, ind: not bodo.libs.array_kernels.isna(
                    data_arr, ind), types.bool_(arr_typ, types.int64), [
                    data_arr, emo__gli])
                with builder.if_then(ezbkg__ckrtn):
                    hby__amxv, field_val = c.pyapi.call_jit_code(lambda
                        data_arr, ind: data_arr[ind], arr_typ.dtype(arr_typ,
                        types.int64), [data_arr, emo__gli])
                    ktv__xuels = c.pyapi.from_native_value(arr_typ.dtype,
                        field_val, c.env_manager)
                    if is_tuple_array:
                        c.pyapi.tuple_setitem(xhs__oqglm, i, ktv__xuels)
                    else:
                        c.pyapi.dict_setitem_string(xhs__oqglm, typ.names[i
                            ], ktv__xuels)
                        c.pyapi.decref(ktv__xuels)
            pyarray_setitem(builder, context, axx__yyee, emo__gli, xhs__oqglm)
            c.pyapi.decref(xhs__oqglm)
    c.pyapi.decref(bvy__gocvu)
    c.pyapi.decref(dgvfe__fjwtg)
    c.pyapi.decref(scoj__rqyal)
    c.pyapi.decref(ebc__hdq)
    return axx__yyee


def _fix_nested_counts(nested_counts, struct_arr_type, nested_counts_type,
    builder):
    gsugs__yht = bodo.utils.transform.get_type_alloc_counts(struct_arr_type
        ) - 1
    if gsugs__yht == 0:
        return nested_counts
    if not isinstance(nested_counts_type, types.UniTuple):
        nested_counts = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for xtuyt__gcqml in range(gsugs__yht)])
    elif nested_counts_type.count < gsugs__yht:
        nested_counts = cgutils.pack_array(builder, [builder.extract_value(
            nested_counts, i) for i in range(nested_counts_type.count)] + [
            lir.Constant(lir.IntType(64), -1) for xtuyt__gcqml in range(
            gsugs__yht - nested_counts_type.count)])
    return nested_counts


@intrinsic
def pre_alloc_struct_array(typingctx, num_structs_typ, nested_counts_typ,
    dtypes_typ, names_typ=None):
    assert isinstance(num_structs_typ, types.Integer) and isinstance(dtypes_typ
        , types.BaseTuple)
    if is_overload_none(names_typ):
        names = tuple(f'f{i}' for i in range(len(dtypes_typ)))
    else:
        names = tuple(get_overload_const_str(jolsq__mvh) for jolsq__mvh in
            names_typ.types)
    gdim__qjv = tuple(jolsq__mvh.instance_type for jolsq__mvh in dtypes_typ
        .types)
    struct_arr_type = StructArrayType(gdim__qjv, names)

    def codegen(context, builder, sig, args):
        ebrjn__ugzen, nested_counts, xtuyt__gcqml, xtuyt__gcqml = args
        nested_counts_type = sig.args[1]
        nested_counts = _fix_nested_counts(nested_counts, struct_arr_type,
            nested_counts_type, builder)
        cref__qytmh, xtuyt__gcqml, xtuyt__gcqml = construct_struct_array(
            context, builder, struct_arr_type, ebrjn__ugzen, nested_counts)
        weu__pfl = context.make_helper(builder, struct_arr_type)
        weu__pfl.meminfo = cref__qytmh
        return weu__pfl._getvalue()
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
        assert isinstance(names, tuple) and all(isinstance(wxo__nvdo, str) for
            wxo__nvdo in names) and len(names) == len(data)
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
        ezx__ddwl = [('data', types.BaseTuple.from_types(fe_type.data)), (
            'null_bitmap', types.UniTuple(types.int8, len(fe_type.data)))]
        models.StructModel.__init__(self, dmm, fe_type, ezx__ddwl)


@register_model(StructType)
class StructModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = StructPayloadType(fe_type.data)
        ezx__ddwl = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, ezx__ddwl)


def define_struct_dtor(context, builder, struct_type, payload_type):
    ijmdi__egwll = builder.module
    hvlq__vvw = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    qeau__obx = cgutils.get_or_insert_function(ijmdi__egwll, hvlq__vvw,
        name='.dtor.struct.{}.{}.'.format(struct_type.data, struct_type.names))
    if not qeau__obx.is_declaration:
        return qeau__obx
    qeau__obx.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(qeau__obx.append_basic_block())
    pgltr__lzcrf = qeau__obx.args[0]
    vxbzw__jnq = context.get_value_type(payload_type).as_pointer()
    lvvnk__uaheq = builder.bitcast(pgltr__lzcrf, vxbzw__jnq)
    gkx__jhmof = context.make_helper(builder, payload_type, ref=lvvnk__uaheq)
    for i in range(len(struct_type.data)):
        kxypy__djes = builder.extract_value(gkx__jhmof.null_bitmap, i)
        uek__yfzp = builder.icmp_unsigned('==', kxypy__djes, lir.Constant(
            kxypy__djes.type, 1))
        with builder.if_then(uek__yfzp):
            val = builder.extract_value(gkx__jhmof.data, i)
            context.nrt.decref(builder, struct_type.data[i], val)
    builder.ret_void()
    return qeau__obx


def _get_struct_payload(context, builder, typ, struct):
    struct = context.make_helper(builder, typ, struct)
    payload_type = StructPayloadType(typ.data)
    izce__vpfdv = context.nrt.meminfo_data(builder, struct.meminfo)
    cgxz__fcr = builder.bitcast(izce__vpfdv, context.get_value_type(
        payload_type).as_pointer())
    gkx__jhmof = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(cgxz__fcr))
    return gkx__jhmof, cgxz__fcr


@unbox(StructType)
def unbox_struct(typ, val, c):
    context = c.context
    builder = c.builder
    ngwpq__ajgv = context.insert_const_string(builder.module, 'pandas')
    cha__rmpl = c.pyapi.import_module_noblock(ngwpq__ajgv)
    tjqk__puxlp = c.pyapi.object_getattr_string(cha__rmpl, 'NA')
    nya__eldhm = []
    nulls = []
    for i, jolsq__mvh in enumerate(typ.data):
        ktv__xuels = c.pyapi.dict_getitem_string(val, typ.names[i])
        dipif__rvcdv = cgutils.alloca_once_value(c.builder, context.
            get_constant(types.uint8, 0))
        rjon__nzxrj = cgutils.alloca_once_value(c.builder, cgutils.
            get_null_value(context.get_value_type(jolsq__mvh)))
        zpib__orm = is_na_value(builder, context, ktv__xuels, tjqk__puxlp)
        uek__yfzp = builder.icmp_unsigned('!=', zpib__orm, lir.Constant(
            zpib__orm.type, 1))
        with builder.if_then(uek__yfzp):
            builder.store(context.get_constant(types.uint8, 1), dipif__rvcdv)
            field_val = c.pyapi.to_native_value(jolsq__mvh, ktv__xuels).value
            builder.store(field_val, rjon__nzxrj)
        nya__eldhm.append(builder.load(rjon__nzxrj))
        nulls.append(builder.load(dipif__rvcdv))
    c.pyapi.decref(cha__rmpl)
    c.pyapi.decref(tjqk__puxlp)
    cref__qytmh = construct_struct(context, builder, typ, nya__eldhm, nulls)
    struct = context.make_helper(builder, typ)
    struct.meminfo = cref__qytmh
    hyg__skyv = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(struct._getvalue(), is_error=hyg__skyv)


@box(StructType)
def box_struct(typ, val, c):
    gazw__zmdvr = c.pyapi.dict_new(len(typ.data))
    gkx__jhmof, xtuyt__gcqml = _get_struct_payload(c.context, c.builder,
        typ, val)
    assert len(typ.data) > 0
    for i, val_typ in enumerate(typ.data):
        c.pyapi.dict_setitem_string(gazw__zmdvr, typ.names[i], c.pyapi.
            borrow_none())
        kxypy__djes = c.builder.extract_value(gkx__jhmof.null_bitmap, i)
        uek__yfzp = c.builder.icmp_unsigned('==', kxypy__djes, lir.Constant
            (kxypy__djes.type, 1))
        with c.builder.if_then(uek__yfzp):
            cnwv__ksey = c.builder.extract_value(gkx__jhmof.data, i)
            c.context.nrt.incref(c.builder, val_typ, cnwv__ksey)
            phcee__mgbhz = c.pyapi.from_native_value(val_typ, cnwv__ksey, c
                .env_manager)
            c.pyapi.dict_setitem_string(gazw__zmdvr, typ.names[i], phcee__mgbhz
                )
            c.pyapi.decref(phcee__mgbhz)
    c.context.nrt.decref(c.builder, typ, val)
    return gazw__zmdvr


@intrinsic
def init_struct(typingctx, data_typ, names_typ=None):
    names = tuple(get_overload_const_str(jolsq__mvh) for jolsq__mvh in
        names_typ.types)
    struct_type = StructType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, uyptt__ush = args
        payload_type = StructPayloadType(struct_type.data)
        pzlae__bnksr = context.get_value_type(payload_type)
        keyzu__tlgmk = context.get_abi_sizeof(pzlae__bnksr)
        nwo__tpe = define_struct_dtor(context, builder, struct_type,
            payload_type)
        cref__qytmh = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, keyzu__tlgmk), nwo__tpe)
        izce__vpfdv = context.nrt.meminfo_data(builder, cref__qytmh)
        cgxz__fcr = builder.bitcast(izce__vpfdv, pzlae__bnksr.as_pointer())
        gkx__jhmof = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        gkx__jhmof.data = data
        gkx__jhmof.null_bitmap = cgutils.pack_array(builder, [context.
            get_constant(types.uint8, 1) for xtuyt__gcqml in range(len(
            data_typ.types))])
        builder.store(gkx__jhmof._getvalue(), cgxz__fcr)
        context.nrt.incref(builder, data_typ, data)
        struct = context.make_helper(builder, struct_type)
        struct.meminfo = cref__qytmh
        return struct._getvalue()
    return struct_type(data_typ, names_typ), codegen


@intrinsic
def get_struct_data(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        gkx__jhmof, xtuyt__gcqml = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gkx__jhmof.data)
    return types.BaseTuple.from_types(struct_typ.data)(struct_typ), codegen


@intrinsic
def get_struct_null_bitmap(typingctx, struct_typ=None):
    assert isinstance(struct_typ, StructType)

    def codegen(context, builder, sig, args):
        struct, = args
        gkx__jhmof, xtuyt__gcqml = _get_struct_payload(context, builder,
            struct_typ, struct)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gkx__jhmof.null_bitmap)
    pwiim__krj = types.UniTuple(types.int8, len(struct_typ.data))
    return pwiim__krj(struct_typ), codegen


@intrinsic
def set_struct_data(typingctx, struct_typ, field_ind_typ, val_typ=None):
    assert isinstance(struct_typ, StructType) and is_overload_constant_int(
        field_ind_typ)
    field_ind = get_overload_const_int(field_ind_typ)

    def codegen(context, builder, sig, args):
        struct, xtuyt__gcqml, val = args
        gkx__jhmof, cgxz__fcr = _get_struct_payload(context, builder,
            struct_typ, struct)
        cmxjd__lzg = gkx__jhmof.data
        yfq__txlgz = builder.insert_value(cmxjd__lzg, val, field_ind)
        erhv__vna = types.BaseTuple.from_types(struct_typ.data)
        context.nrt.decref(builder, erhv__vna, cmxjd__lzg)
        context.nrt.incref(builder, erhv__vna, yfq__txlgz)
        gkx__jhmof.data = yfq__txlgz
        builder.store(gkx__jhmof._getvalue(), cgxz__fcr)
        return context.get_dummy_value()
    return types.none(struct_typ, field_ind_typ, val_typ), codegen


def _get_struct_field_ind(struct, ind, op):
    if not is_overload_constant_str(ind):
        raise BodoError(
            'structs (from struct array) only support constant strings for {}, not {}'
            .format(op, ind))
    ewr__som = get_overload_const_str(ind)
    if ewr__som not in struct.names:
        raise BodoError('Field {} does not exist in struct {}'.format(
            ewr__som, struct))
    return struct.names.index(ewr__som)


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
    pzlae__bnksr = context.get_value_type(payload_type)
    keyzu__tlgmk = context.get_abi_sizeof(pzlae__bnksr)
    nwo__tpe = define_struct_dtor(context, builder, struct_type, payload_type)
    cref__qytmh = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, keyzu__tlgmk), nwo__tpe)
    izce__vpfdv = context.nrt.meminfo_data(builder, cref__qytmh)
    cgxz__fcr = builder.bitcast(izce__vpfdv, pzlae__bnksr.as_pointer())
    gkx__jhmof = cgutils.create_struct_proxy(payload_type)(context, builder)
    gkx__jhmof.data = cgutils.pack_array(builder, values
        ) if types.is_homogeneous(*struct_type.data) else cgutils.pack_struct(
        builder, values)
    gkx__jhmof.null_bitmap = cgutils.pack_array(builder, nulls)
    builder.store(gkx__jhmof._getvalue(), cgxz__fcr)
    return cref__qytmh


@intrinsic
def struct_array_get_struct(typingctx, struct_arr_typ, ind_typ=None):
    assert isinstance(struct_arr_typ, StructArrayType) and isinstance(ind_typ,
        types.Integer)
    ykrsn__jrlbr = tuple(d.dtype for d in struct_arr_typ.data)
    esuwh__dqckx = StructType(ykrsn__jrlbr, struct_arr_typ.names)

    def codegen(context, builder, sig, args):
        lain__yuj, ind = args
        gkx__jhmof = _get_struct_arr_payload(context, builder,
            struct_arr_typ, lain__yuj)
        nya__eldhm = []
        kgru__urgb = []
        for i, arr_typ in enumerate(struct_arr_typ.data):
            zqsn__ixa = builder.extract_value(gkx__jhmof.data, i)
            gbsr__utlvo = context.compile_internal(builder, lambda arr, ind:
                np.uint8(0) if bodo.libs.array_kernels.isna(arr, ind) else
                np.uint8(1), types.uint8(arr_typ, types.int64), [zqsn__ixa,
                ind])
            kgru__urgb.append(gbsr__utlvo)
            pcis__pdrig = cgutils.alloca_once_value(builder, context.
                get_constant_null(arr_typ.dtype))
            uek__yfzp = builder.icmp_unsigned('==', gbsr__utlvo, lir.
                Constant(gbsr__utlvo.type, 1))
            with builder.if_then(uek__yfzp):
                zkh__eiuc = context.compile_internal(builder, lambda arr,
                    ind: arr[ind], arr_typ.dtype(arr_typ, types.int64), [
                    zqsn__ixa, ind])
                builder.store(zkh__eiuc, pcis__pdrig)
            nya__eldhm.append(builder.load(pcis__pdrig))
        if isinstance(esuwh__dqckx, types.DictType):
            xfyq__zkafd = [context.insert_const_string(builder.module,
                psqd__vzsko) for psqd__vzsko in struct_arr_typ.names]
            pgp__dvwn = cgutils.pack_array(builder, nya__eldhm)
            patcb__zje = cgutils.pack_array(builder, xfyq__zkafd)

            def impl(names, vals):
                d = {}
                for i, psqd__vzsko in enumerate(names):
                    d[psqd__vzsko] = vals[i]
                return d
            ckobq__oils = context.compile_internal(builder, impl,
                esuwh__dqckx(types.Tuple(tuple(types.StringLiteral(
                psqd__vzsko) for psqd__vzsko in struct_arr_typ.names)),
                types.Tuple(ykrsn__jrlbr)), [patcb__zje, pgp__dvwn])
            context.nrt.decref(builder, types.BaseTuple.from_types(
                ykrsn__jrlbr), pgp__dvwn)
            return ckobq__oils
        cref__qytmh = construct_struct(context, builder, esuwh__dqckx,
            nya__eldhm, kgru__urgb)
        struct = context.make_helper(builder, esuwh__dqckx)
        struct.meminfo = cref__qytmh
        return struct._getvalue()
    return esuwh__dqckx(struct_arr_typ, ind_typ), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        gkx__jhmof = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gkx__jhmof.data)
    return types.BaseTuple.from_types(arr_typ.data)(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, StructArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        gkx__jhmof = _get_struct_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            gkx__jhmof.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


@intrinsic
def init_struct_arr(typingctx, data_typ, null_bitmap_typ, names_typ=None):
    names = tuple(get_overload_const_str(jolsq__mvh) for jolsq__mvh in
        names_typ.types)
    struct_arr_type = StructArrayType(data_typ.types, names)

    def codegen(context, builder, sig, args):
        data, gsepg__oiyxg, uyptt__ush = args
        payload_type = StructArrayPayloadType(struct_arr_type.data)
        pzlae__bnksr = context.get_value_type(payload_type)
        keyzu__tlgmk = context.get_abi_sizeof(pzlae__bnksr)
        nwo__tpe = define_struct_arr_dtor(context, builder, struct_arr_type,
            payload_type)
        cref__qytmh = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, keyzu__tlgmk), nwo__tpe)
        izce__vpfdv = context.nrt.meminfo_data(builder, cref__qytmh)
        cgxz__fcr = builder.bitcast(izce__vpfdv, pzlae__bnksr.as_pointer())
        gkx__jhmof = cgutils.create_struct_proxy(payload_type)(context, builder
            )
        gkx__jhmof.data = data
        gkx__jhmof.null_bitmap = gsepg__oiyxg
        builder.store(gkx__jhmof._getvalue(), cgxz__fcr)
        context.nrt.incref(builder, data_typ, data)
        context.nrt.incref(builder, null_bitmap_typ, gsepg__oiyxg)
        weu__pfl = context.make_helper(builder, struct_arr_type)
        weu__pfl.meminfo = cref__qytmh
        return weu__pfl._getvalue()
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
    jvxhx__nlnq = len(arr.data)
    veohn__qvviq = 'def impl(arr, ind):\n'
    veohn__qvviq += '  data = get_data(arr)\n'
    veohn__qvviq += '  null_bitmap = get_null_bitmap(arr)\n'
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        veohn__qvviq += """  out_null_bitmap = get_new_null_mask_bool_index(null_bitmap, ind, len(data[0]))
"""
    elif is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        veohn__qvviq += """  out_null_bitmap = get_new_null_mask_int_index(null_bitmap, ind, len(data[0]))
"""
    elif isinstance(ind, types.SliceType):
        veohn__qvviq += """  out_null_bitmap = get_new_null_mask_slice_index(null_bitmap, ind, len(data[0]))
"""
    else:
        raise BodoError('invalid index {} in struct array indexing'.format(ind)
            )
    veohn__qvviq += (
        '  return init_struct_arr(({},), out_null_bitmap, ({},))\n'.format(
        ', '.join('ensure_contig_if_np(data[{}][ind])'.format(i) for i in
        range(jvxhx__nlnq)), ', '.join("'{}'".format(psqd__vzsko) for
        psqd__vzsko in arr.names)))
    fscii__jqtdx = {}
    exec(veohn__qvviq, {'init_struct_arr': init_struct_arr, 'get_data':
        get_data, 'get_null_bitmap': get_null_bitmap, 'ensure_contig_if_np':
        bodo.utils.conversion.ensure_contig_if_np,
        'get_new_null_mask_bool_index': bodo.utils.indexing.
        get_new_null_mask_bool_index, 'get_new_null_mask_int_index': bodo.
        utils.indexing.get_new_null_mask_int_index,
        'get_new_null_mask_slice_index': bodo.utils.indexing.
        get_new_null_mask_slice_index}, fscii__jqtdx)
    impl = fscii__jqtdx['impl']
    return impl


@overload(operator.setitem, no_unliteral=True)
def struct_arr_setitem(arr, ind, val):
    if not isinstance(arr, StructArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    if isinstance(ind, types.Integer):
        jvxhx__nlnq = len(arr.data)
        veohn__qvviq = 'def impl(arr, ind, val):\n'
        veohn__qvviq += '  data = get_data(arr)\n'
        veohn__qvviq += '  null_bitmap = get_null_bitmap(arr)\n'
        veohn__qvviq += '  set_bit_to_arr(null_bitmap, ind, 1)\n'
        for i in range(jvxhx__nlnq):
            if isinstance(val, StructType):
                veohn__qvviq += ("  if is_field_value_null(val, '{}'):\n".
                    format(arr.names[i]))
                veohn__qvviq += (
                    '    bodo.libs.array_kernels.setna(data[{}], ind)\n'.
                    format(i))
                veohn__qvviq += '  else:\n'
                veohn__qvviq += "    data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
            else:
                veohn__qvviq += "  data[{}][ind] = val['{}']\n".format(i,
                    arr.names[i])
        fscii__jqtdx = {}
        exec(veohn__qvviq, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'is_field_value_null':
            is_field_value_null}, fscii__jqtdx)
        impl = fscii__jqtdx['impl']
        return impl
    if isinstance(ind, types.SliceType):
        jvxhx__nlnq = len(arr.data)
        veohn__qvviq = 'def impl(arr, ind, val):\n'
        veohn__qvviq += '  data = get_data(arr)\n'
        veohn__qvviq += '  null_bitmap = get_null_bitmap(arr)\n'
        veohn__qvviq += '  val_data = get_data(val)\n'
        veohn__qvviq += '  val_null_bitmap = get_null_bitmap(val)\n'
        veohn__qvviq += """  setitem_slice_index_null_bits(null_bitmap, val_null_bitmap, ind, len(arr))
"""
        for i in range(jvxhx__nlnq):
            veohn__qvviq += '  data[{0}][ind] = val_data[{0}]\n'.format(i)
        fscii__jqtdx = {}
        exec(veohn__qvviq, {'bodo': bodo, 'get_data': get_data,
            'get_null_bitmap': get_null_bitmap, 'set_bit_to_arr': bodo.libs
            .int_arr_ext.set_bit_to_arr, 'setitem_slice_index_null_bits':
            bodo.utils.indexing.setitem_slice_index_null_bits}, fscii__jqtdx)
        impl = fscii__jqtdx['impl']
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
    veohn__qvviq = 'def impl(A):\n'
    veohn__qvviq += '  total_nbytes = 0\n'
    veohn__qvviq += '  data = get_data(A)\n'
    for i in range(len(A.data)):
        veohn__qvviq += f'  total_nbytes += data[{i}].nbytes\n'
    veohn__qvviq += '  total_nbytes += get_null_bitmap(A).nbytes\n'
    veohn__qvviq += '  return total_nbytes\n'
    fscii__jqtdx = {}
    exec(veohn__qvviq, {'get_data': get_data, 'get_null_bitmap':
        get_null_bitmap}, fscii__jqtdx)
    impl = fscii__jqtdx['impl']
    return impl


@overload_method(StructArrayType, 'copy', no_unliteral=True)
def overload_struct_arr_copy(A):
    names = A.names

    def copy_impl(A):
        data = get_data(A)
        gsepg__oiyxg = get_null_bitmap(A)
        minin__dylbf = bodo.libs.struct_arr_ext.copy_arr_tup(data)
        xemx__dac = gsepg__oiyxg.copy()
        return init_struct_arr(minin__dylbf, xemx__dac, names)
    return copy_impl


def copy_arr_tup(arrs):
    return tuple(wxo__nvdo.copy() for wxo__nvdo in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    zoaow__psj = arrs.count
    veohn__qvviq = 'def f(arrs):\n'
    veohn__qvviq += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(zoaow__psj)))
    fscii__jqtdx = {}
    exec(veohn__qvviq, {}, fscii__jqtdx)
    impl = fscii__jqtdx['f']
    return impl
