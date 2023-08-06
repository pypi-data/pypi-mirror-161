"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        xcs__jcid = [('n_arrays', types.int64), ('data', fe_type.array_type
            .dtype), ('offsets', types.Array(offset_type, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, xcs__jcid)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        xcs__jcid = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, xcs__jcid)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    xnod__ier = builder.module
    gvbub__uzcg = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    zuzj__ihqt = cgutils.get_or_insert_function(xnod__ier, gvbub__uzcg,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not zuzj__ihqt.is_declaration:
        return zuzj__ihqt
    zuzj__ihqt.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(zuzj__ihqt.append_basic_block())
    owue__fzxd = zuzj__ihqt.args[0]
    xhpl__qqrie = context.get_value_type(payload_type).as_pointer()
    lpkbx__oan = builder.bitcast(owue__fzxd, xhpl__qqrie)
    nxhxn__iuq = context.make_helper(builder, payload_type, ref=lpkbx__oan)
    context.nrt.decref(builder, array_item_type.dtype, nxhxn__iuq.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        nxhxn__iuq.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        nxhxn__iuq.null_bitmap)
    builder.ret_void()
    return zuzj__ihqt


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    reqpv__ubfc = context.get_value_type(payload_type)
    qgflx__ynm = context.get_abi_sizeof(reqpv__ubfc)
    cuqnt__cda = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    atcfc__qyz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qgflx__ynm), cuqnt__cda)
    dguhg__xizpb = context.nrt.meminfo_data(builder, atcfc__qyz)
    msfaa__zvfs = builder.bitcast(dguhg__xizpb, reqpv__ubfc.as_pointer())
    nxhxn__iuq = cgutils.create_struct_proxy(payload_type)(context, builder)
    nxhxn__iuq.n_arrays = n_arrays
    rqlw__moje = n_elems.type.count
    cbvy__ota = builder.extract_value(n_elems, 0)
    jldwe__xgnsy = cgutils.alloca_once_value(builder, cbvy__ota)
    hkte__por = builder.icmp_signed('==', cbvy__ota, lir.Constant(cbvy__ota
        .type, -1))
    with builder.if_then(hkte__por):
        builder.store(n_arrays, jldwe__xgnsy)
    n_elems = cgutils.pack_array(builder, [builder.load(jldwe__xgnsy)] + [
        builder.extract_value(n_elems, kwh__pgqrg) for kwh__pgqrg in range(
        1, rqlw__moje)])
    nxhxn__iuq.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    udet__dnk = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    pgys__qgcsg = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [udet__dnk])
    offsets_ptr = pgys__qgcsg.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    nxhxn__iuq.offsets = pgys__qgcsg._getvalue()
    hilx__zhn = builder.udiv(builder.add(n_arrays, lir.Constant(lir.IntType
        (64), 7)), lir.Constant(lir.IntType(64), 8))
    ncodu__xowtl = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [hilx__zhn])
    null_bitmap_ptr = ncodu__xowtl.data
    nxhxn__iuq.null_bitmap = ncodu__xowtl._getvalue()
    builder.store(nxhxn__iuq._getvalue(), msfaa__zvfs)
    return atcfc__qyz, nxhxn__iuq.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    hgzt__dhw, gwj__jgq = c.pyapi.call_jit_code(copy_data, sig, [data_arr,
        item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    ejjch__xqwpu = context.insert_const_string(builder.module, 'pandas')
    hkupb__yqih = c.pyapi.import_module_noblock(ejjch__xqwpu)
    pls__wadz = c.pyapi.object_getattr_string(hkupb__yqih, 'NA')
    quzk__mepa = c.context.get_constant(offset_type, 0)
    builder.store(quzk__mepa, offsets_ptr)
    rvyvt__ohagw = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as wyux__mdk:
        ptic__ijer = wyux__mdk.index
        item_ind = builder.load(rvyvt__ohagw)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [ptic__ijer]))
        arr_obj = seq_getitem(builder, context, val, ptic__ijer)
        set_bitmap_bit(builder, null_bitmap_ptr, ptic__ijer, 0)
        sraj__idqd = is_na_value(builder, context, arr_obj, pls__wadz)
        bvn__lbifj = builder.icmp_unsigned('!=', sraj__idqd, lir.Constant(
            sraj__idqd.type, 1))
        with builder.if_then(bvn__lbifj):
            set_bitmap_bit(builder, null_bitmap_ptr, ptic__ijer, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), rvyvt__ohagw)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(rvyvt__ohagw), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(hkupb__yqih)
    c.pyapi.decref(pls__wadz)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    egdg__nijgf = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if egdg__nijgf:
        gvbub__uzcg = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        zshag__yisaw = cgutils.get_or_insert_function(c.builder.module,
            gvbub__uzcg, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(
            zshag__yisaw, [val])])
    else:
        oax__hzn = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            oax__hzn, kwh__pgqrg) for kwh__pgqrg in range(1, oax__hzn.type.
            count)])
    atcfc__qyz, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if egdg__nijgf:
        jxlpl__meh = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        quv__vjsrm = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        gvbub__uzcg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        zuzj__ihqt = cgutils.get_or_insert_function(c.builder.module,
            gvbub__uzcg, name='array_item_array_from_sequence')
        c.builder.call(zuzj__ihqt, [val, c.builder.bitcast(quv__vjsrm, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), jxlpl__meh)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    rwbgb__uvq = c.context.make_helper(c.builder, typ)
    rwbgb__uvq.meminfo = atcfc__qyz
    oqb__fwn = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rwbgb__uvq._getvalue(), is_error=oqb__fwn)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    rwbgb__uvq = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    dguhg__xizpb = context.nrt.meminfo_data(builder, rwbgb__uvq.meminfo)
    msfaa__zvfs = builder.bitcast(dguhg__xizpb, context.get_value_type(
        payload_type).as_pointer())
    nxhxn__iuq = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(msfaa__zvfs))
    return nxhxn__iuq


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    ejjch__xqwpu = context.insert_const_string(builder.module, 'numpy')
    qxdvv__ugliw = c.pyapi.import_module_noblock(ejjch__xqwpu)
    xmff__zsp = c.pyapi.object_getattr_string(qxdvv__ugliw, 'object_')
    ilho__vcpp = c.pyapi.long_from_longlong(n_arrays)
    ijnxm__aij = c.pyapi.call_method(qxdvv__ugliw, 'ndarray', (ilho__vcpp,
        xmff__zsp))
    aln__sunr = c.pyapi.object_getattr_string(qxdvv__ugliw, 'nan')
    rvyvt__ohagw = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as wyux__mdk:
        ptic__ijer = wyux__mdk.index
        pyarray_setitem(builder, context, ijnxm__aij, ptic__ijer, aln__sunr)
        wcaye__skgh = get_bitmap_bit(builder, null_bitmap_ptr, ptic__ijer)
        bzxy__wsl = builder.icmp_unsigned('!=', wcaye__skgh, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(bzxy__wsl):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(ptic__ijer, lir.Constant(
                ptic__ijer.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [ptic__ijer]))), lir.IntType(64))
            item_ind = builder.load(rvyvt__ohagw)
            hgzt__dhw, xtf__ppf = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), rvyvt__ohagw)
            arr_obj = c.pyapi.from_native_value(typ.dtype, xtf__ppf, c.
                env_manager)
            pyarray_setitem(builder, context, ijnxm__aij, ptic__ijer, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(qxdvv__ugliw)
    c.pyapi.decref(xmff__zsp)
    c.pyapi.decref(ilho__vcpp)
    c.pyapi.decref(aln__sunr)
    return ijnxm__aij


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    nxhxn__iuq = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = nxhxn__iuq.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), nxhxn__iuq.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), nxhxn__iuq.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        jxlpl__meh = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        quv__vjsrm = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        gvbub__uzcg = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        ota__mwjf = cgutils.get_or_insert_function(c.builder.module,
            gvbub__uzcg, name='np_array_from_array_item_array')
        arr = c.builder.call(ota__mwjf, [nxhxn__iuq.n_arrays, c.builder.
            bitcast(quv__vjsrm, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), jxlpl__meh)])
    else:
        arr = _box_array_item_array_generic(typ, c, nxhxn__iuq.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    ikna__qmc, vsxf__yvn, zij__xzmgt = args
    ybba__tao = bodo.utils.transform.get_type_alloc_counts(array_item_type.
        dtype)
    xxxes__ebemr = sig.args[1]
    if not isinstance(xxxes__ebemr, types.UniTuple):
        vsxf__yvn = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for zij__xzmgt in range(ybba__tao)])
    elif xxxes__ebemr.count < ybba__tao:
        vsxf__yvn = cgutils.pack_array(builder, [builder.extract_value(
            vsxf__yvn, kwh__pgqrg) for kwh__pgqrg in range(xxxes__ebemr.
            count)] + [lir.Constant(lir.IntType(64), -1) for zij__xzmgt in
            range(ybba__tao - xxxes__ebemr.count)])
    atcfc__qyz, zij__xzmgt, zij__xzmgt, zij__xzmgt = (
        construct_array_item_array(context, builder, array_item_type,
        ikna__qmc, vsxf__yvn))
    rwbgb__uvq = context.make_helper(builder, array_item_type)
    rwbgb__uvq.meminfo = atcfc__qyz
    return rwbgb__uvq._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, vddpq__rnna, pgys__qgcsg, ncodu__xowtl = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    reqpv__ubfc = context.get_value_type(payload_type)
    qgflx__ynm = context.get_abi_sizeof(reqpv__ubfc)
    cuqnt__cda = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    atcfc__qyz = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, qgflx__ynm), cuqnt__cda)
    dguhg__xizpb = context.nrt.meminfo_data(builder, atcfc__qyz)
    msfaa__zvfs = builder.bitcast(dguhg__xizpb, reqpv__ubfc.as_pointer())
    nxhxn__iuq = cgutils.create_struct_proxy(payload_type)(context, builder)
    nxhxn__iuq.n_arrays = n_arrays
    nxhxn__iuq.data = vddpq__rnna
    nxhxn__iuq.offsets = pgys__qgcsg
    nxhxn__iuq.null_bitmap = ncodu__xowtl
    builder.store(nxhxn__iuq._getvalue(), msfaa__zvfs)
    context.nrt.incref(builder, signature.args[1], vddpq__rnna)
    context.nrt.incref(builder, signature.args[2], pgys__qgcsg)
    context.nrt.incref(builder, signature.args[3], ncodu__xowtl)
    rwbgb__uvq = context.make_helper(builder, array_item_type)
    rwbgb__uvq.meminfo = atcfc__qyz
    return rwbgb__uvq._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    esb__oberz = ArrayItemArrayType(data_type)
    sig = esb__oberz(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        nxhxn__iuq = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return impl_ret_borrowed(context, builder, sig.return_type,
            nxhxn__iuq.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        nxhxn__iuq = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        quv__vjsrm = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, nxhxn__iuq.offsets).data
        pgys__qgcsg = builder.bitcast(quv__vjsrm, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(pgys__qgcsg, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        nxhxn__iuq = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return impl_ret_borrowed(context, builder, sig.return_type,
            nxhxn__iuq.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        nxhxn__iuq = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return impl_ret_borrowed(context, builder, sig.return_type,
            nxhxn__iuq.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        nxhxn__iuq = _get_array_item_arr_payload(context, builder, arr_typ, arr
            )
        return nxhxn__iuq.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, bmkg__sqweb = args
        rwbgb__uvq = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        dguhg__xizpb = context.nrt.meminfo_data(builder, rwbgb__uvq.meminfo)
        msfaa__zvfs = builder.bitcast(dguhg__xizpb, context.get_value_type(
            payload_type).as_pointer())
        nxhxn__iuq = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(msfaa__zvfs))
        context.nrt.decref(builder, data_typ, nxhxn__iuq.data)
        nxhxn__iuq.data = bmkg__sqweb
        context.nrt.incref(builder, data_typ, bmkg__sqweb)
        builder.store(nxhxn__iuq._getvalue(), msfaa__zvfs)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    vddpq__rnna = get_data(arr)
    zofxh__mtym = len(vddpq__rnna)
    if zofxh__mtym < new_size:
        yyrfm__hbwx = max(2 * zofxh__mtym, new_size)
        bmkg__sqweb = bodo.libs.array_kernels.resize_and_copy(vddpq__rnna,
            old_size, yyrfm__hbwx)
        replace_data_arr(arr, bmkg__sqweb)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    vddpq__rnna = get_data(arr)
    pgys__qgcsg = get_offsets(arr)
    wmbv__bllp = len(vddpq__rnna)
    ksna__wjgk = pgys__qgcsg[-1]
    if wmbv__bllp != ksna__wjgk:
        bmkg__sqweb = bodo.libs.array_kernels.resize_and_copy(vddpq__rnna,
            ksna__wjgk, ksna__wjgk)
        replace_data_arr(arr, bmkg__sqweb)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            pgys__qgcsg = get_offsets(arr)
            vddpq__rnna = get_data(arr)
            bql__esn = pgys__qgcsg[ind]
            ypi__nuqt = pgys__qgcsg[ind + 1]
            return vddpq__rnna[bql__esn:ypi__nuqt]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        vsgo__dlp = arr.dtype

        def impl_bool(arr, ind):
            zyv__bvni = len(arr)
            if zyv__bvni != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ncodu__xowtl = get_null_bitmap(arr)
            n_arrays = 0
            odkr__sadwr = init_nested_counts(vsgo__dlp)
            for kwh__pgqrg in range(zyv__bvni):
                if ind[kwh__pgqrg]:
                    n_arrays += 1
                    usci__yii = arr[kwh__pgqrg]
                    odkr__sadwr = add_nested_counts(odkr__sadwr, usci__yii)
            ijnxm__aij = pre_alloc_array_item_array(n_arrays, odkr__sadwr,
                vsgo__dlp)
            pnmyt__fmi = get_null_bitmap(ijnxm__aij)
            tng__glw = 0
            for rezij__rhfr in range(zyv__bvni):
                if ind[rezij__rhfr]:
                    ijnxm__aij[tng__glw] = arr[rezij__rhfr]
                    hefq__srxo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ncodu__xowtl, rezij__rhfr)
                    bodo.libs.int_arr_ext.set_bit_to_arr(pnmyt__fmi,
                        tng__glw, hefq__srxo)
                    tng__glw += 1
            return ijnxm__aij
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        vsgo__dlp = arr.dtype

        def impl_int(arr, ind):
            ncodu__xowtl = get_null_bitmap(arr)
            zyv__bvni = len(ind)
            n_arrays = zyv__bvni
            odkr__sadwr = init_nested_counts(vsgo__dlp)
            for jetci__fmfjj in range(zyv__bvni):
                kwh__pgqrg = ind[jetci__fmfjj]
                usci__yii = arr[kwh__pgqrg]
                odkr__sadwr = add_nested_counts(odkr__sadwr, usci__yii)
            ijnxm__aij = pre_alloc_array_item_array(n_arrays, odkr__sadwr,
                vsgo__dlp)
            pnmyt__fmi = get_null_bitmap(ijnxm__aij)
            for sni__bwe in range(zyv__bvni):
                rezij__rhfr = ind[sni__bwe]
                ijnxm__aij[sni__bwe] = arr[rezij__rhfr]
                hefq__srxo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    ncodu__xowtl, rezij__rhfr)
                bodo.libs.int_arr_ext.set_bit_to_arr(pnmyt__fmi, sni__bwe,
                    hefq__srxo)
            return ijnxm__aij
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            zyv__bvni = len(arr)
            ljwui__irjus = numba.cpython.unicode._normalize_slice(ind,
                zyv__bvni)
            ekcv__dgj = np.arange(ljwui__irjus.start, ljwui__irjus.stop,
                ljwui__irjus.step)
            return arr[ekcv__dgj]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            pgys__qgcsg = get_offsets(A)
            ncodu__xowtl = get_null_bitmap(A)
            if idx == 0:
                pgys__qgcsg[0] = 0
            n_items = len(val)
            vdtzr__nxq = pgys__qgcsg[idx] + n_items
            ensure_data_capacity(A, pgys__qgcsg[idx], vdtzr__nxq)
            vddpq__rnna = get_data(A)
            pgys__qgcsg[idx + 1] = pgys__qgcsg[idx] + n_items
            vddpq__rnna[pgys__qgcsg[idx]:pgys__qgcsg[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(ncodu__xowtl, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            ljwui__irjus = numba.cpython.unicode._normalize_slice(idx, len(A))
            for kwh__pgqrg in range(ljwui__irjus.start, ljwui__irjus.stop,
                ljwui__irjus.step):
                A[kwh__pgqrg] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            pgys__qgcsg = get_offsets(A)
            ncodu__xowtl = get_null_bitmap(A)
            bokcb__iqjo = get_offsets(val)
            ofywm__fnhrt = get_data(val)
            feq__wasy = get_null_bitmap(val)
            zyv__bvni = len(A)
            ljwui__irjus = numba.cpython.unicode._normalize_slice(idx,
                zyv__bvni)
            obl__awmpz, efdyk__yuusa = ljwui__irjus.start, ljwui__irjus.stop
            assert ljwui__irjus.step == 1
            if obl__awmpz == 0:
                pgys__qgcsg[obl__awmpz] = 0
            pehjd__nivp = pgys__qgcsg[obl__awmpz]
            vdtzr__nxq = pehjd__nivp + len(ofywm__fnhrt)
            ensure_data_capacity(A, pehjd__nivp, vdtzr__nxq)
            vddpq__rnna = get_data(A)
            vddpq__rnna[pehjd__nivp:pehjd__nivp + len(ofywm__fnhrt)
                ] = ofywm__fnhrt
            pgys__qgcsg[obl__awmpz:efdyk__yuusa + 1
                ] = bokcb__iqjo + pehjd__nivp
            zgvp__kuvt = 0
            for kwh__pgqrg in range(obl__awmpz, efdyk__yuusa):
                hefq__srxo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(feq__wasy
                    , zgvp__kuvt)
                bodo.libs.int_arr_ext.set_bit_to_arr(ncodu__xowtl,
                    kwh__pgqrg, hefq__srxo)
                zgvp__kuvt += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
