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
        jojv__irli = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, jojv__irli)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        jojv__irli = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, jojv__irli)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    excjj__qvk = builder.module
    mnu__duw = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    kidgu__uybd = cgutils.get_or_insert_function(excjj__qvk, mnu__duw, name
        ='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not kidgu__uybd.is_declaration:
        return kidgu__uybd
    kidgu__uybd.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(kidgu__uybd.append_basic_block())
    evqnl__zgcq = kidgu__uybd.args[0]
    bim__bkj = context.get_value_type(payload_type).as_pointer()
    psqx__vao = builder.bitcast(evqnl__zgcq, bim__bkj)
    ijyt__vpg = context.make_helper(builder, payload_type, ref=psqx__vao)
    context.nrt.decref(builder, array_item_type.dtype, ijyt__vpg.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), ijyt__vpg
        .offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), ijyt__vpg
        .null_bitmap)
    builder.ret_void()
    return kidgu__uybd


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    wfy__mykl = context.get_value_type(payload_type)
    dtzjr__qydoz = context.get_abi_sizeof(wfy__mykl)
    ttk__ghkmj = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    srodl__wai = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, dtzjr__qydoz), ttk__ghkmj)
    pfk__ucii = context.nrt.meminfo_data(builder, srodl__wai)
    gkvho__ijleu = builder.bitcast(pfk__ucii, wfy__mykl.as_pointer())
    ijyt__vpg = cgutils.create_struct_proxy(payload_type)(context, builder)
    ijyt__vpg.n_arrays = n_arrays
    xcayw__linpk = n_elems.type.count
    labb__xtrj = builder.extract_value(n_elems, 0)
    zyrn__rchv = cgutils.alloca_once_value(builder, labb__xtrj)
    qvd__wnx = builder.icmp_signed('==', labb__xtrj, lir.Constant(
        labb__xtrj.type, -1))
    with builder.if_then(qvd__wnx):
        builder.store(n_arrays, zyrn__rchv)
    n_elems = cgutils.pack_array(builder, [builder.load(zyrn__rchv)] + [
        builder.extract_value(n_elems, ipwc__tlz) for ipwc__tlz in range(1,
        xcayw__linpk)])
    ijyt__vpg.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    fwjj__yvfq = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    bobwm__keoj = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [fwjj__yvfq])
    offsets_ptr = bobwm__keoj.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    ijyt__vpg.offsets = bobwm__keoj._getvalue()
    lwhi__gmpb = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    poala__lhlwp = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [lwhi__gmpb])
    null_bitmap_ptr = poala__lhlwp.data
    ijyt__vpg.null_bitmap = poala__lhlwp._getvalue()
    builder.store(ijyt__vpg._getvalue(), gkvho__ijleu)
    return srodl__wai, ijyt__vpg.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    ovt__eopl, dppy__vyr = c.pyapi.call_jit_code(copy_data, sig, [data_arr,
        item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    sxtl__tptf = context.insert_const_string(builder.module, 'pandas')
    nsymt__hbo = c.pyapi.import_module_noblock(sxtl__tptf)
    kwv__ocst = c.pyapi.object_getattr_string(nsymt__hbo, 'NA')
    fmia__gjkd = c.context.get_constant(offset_type, 0)
    builder.store(fmia__gjkd, offsets_ptr)
    nwypw__mef = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as plze__pfuh:
        aaes__qtlm = plze__pfuh.index
        item_ind = builder.load(nwypw__mef)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [aaes__qtlm]))
        arr_obj = seq_getitem(builder, context, val, aaes__qtlm)
        set_bitmap_bit(builder, null_bitmap_ptr, aaes__qtlm, 0)
        tdjh__yvk = is_na_value(builder, context, arr_obj, kwv__ocst)
        sdgn__hvas = builder.icmp_unsigned('!=', tdjh__yvk, lir.Constant(
            tdjh__yvk.type, 1))
        with builder.if_then(sdgn__hvas):
            set_bitmap_bit(builder, null_bitmap_ptr, aaes__qtlm, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), nwypw__mef)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(nwypw__mef), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(nsymt__hbo)
    c.pyapi.decref(kwv__ocst)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    rjscm__oqis = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if rjscm__oqis:
        mnu__duw = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        gfj__evww = cgutils.get_or_insert_function(c.builder.module,
            mnu__duw, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(gfj__evww,
            [val])])
    else:
        lqvzy__elhzl = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            lqvzy__elhzl, ipwc__tlz) for ipwc__tlz in range(1, lqvzy__elhzl
            .type.count)])
    srodl__wai, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if rjscm__oqis:
        qfr__shdxk = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        rebx__urw = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        mnu__duw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        kidgu__uybd = cgutils.get_or_insert_function(c.builder.module,
            mnu__duw, name='array_item_array_from_sequence')
        c.builder.call(kidgu__uybd, [val, c.builder.bitcast(rebx__urw, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), qfr__shdxk)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    fja__esvfe = c.context.make_helper(c.builder, typ)
    fja__esvfe.meminfo = srodl__wai
    uwo__qtdo = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(fja__esvfe._getvalue(), is_error=uwo__qtdo)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    fja__esvfe = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    pfk__ucii = context.nrt.meminfo_data(builder, fja__esvfe.meminfo)
    gkvho__ijleu = builder.bitcast(pfk__ucii, context.get_value_type(
        payload_type).as_pointer())
    ijyt__vpg = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(gkvho__ijleu))
    return ijyt__vpg


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    sxtl__tptf = context.insert_const_string(builder.module, 'numpy')
    hlwpy__yefa = c.pyapi.import_module_noblock(sxtl__tptf)
    reb__muyq = c.pyapi.object_getattr_string(hlwpy__yefa, 'object_')
    okas__jdsq = c.pyapi.long_from_longlong(n_arrays)
    mqg__kpzp = c.pyapi.call_method(hlwpy__yefa, 'ndarray', (okas__jdsq,
        reb__muyq))
    tbwo__nyn = c.pyapi.object_getattr_string(hlwpy__yefa, 'nan')
    nwypw__mef = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as plze__pfuh:
        aaes__qtlm = plze__pfuh.index
        pyarray_setitem(builder, context, mqg__kpzp, aaes__qtlm, tbwo__nyn)
        wbe__jstw = get_bitmap_bit(builder, null_bitmap_ptr, aaes__qtlm)
        yda__kibm = builder.icmp_unsigned('!=', wbe__jstw, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(yda__kibm):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(aaes__qtlm, lir.Constant(
                aaes__qtlm.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [aaes__qtlm]))), lir.IntType(64))
            item_ind = builder.load(nwypw__mef)
            ovt__eopl, adf__tzn = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), nwypw__mef)
            arr_obj = c.pyapi.from_native_value(typ.dtype, adf__tzn, c.
                env_manager)
            pyarray_setitem(builder, context, mqg__kpzp, aaes__qtlm, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(hlwpy__yefa)
    c.pyapi.decref(reb__muyq)
    c.pyapi.decref(okas__jdsq)
    c.pyapi.decref(tbwo__nyn)
    return mqg__kpzp


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    ijyt__vpg = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = ijyt__vpg.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), ijyt__vpg.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), ijyt__vpg.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        qfr__shdxk = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        rebx__urw = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        mnu__duw = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        iiphe__yyh = cgutils.get_or_insert_function(c.builder.module,
            mnu__duw, name='np_array_from_array_item_array')
        arr = c.builder.call(iiphe__yyh, [ijyt__vpg.n_arrays, c.builder.
            bitcast(rebx__urw, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), qfr__shdxk)])
    else:
        arr = _box_array_item_array_generic(typ, c, ijyt__vpg.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    pimos__yax, wldfe__fdpxg, zll__rnkw = args
    ncm__keb = bodo.utils.transform.get_type_alloc_counts(array_item_type.dtype
        )
    qvn__uicz = sig.args[1]
    if not isinstance(qvn__uicz, types.UniTuple):
        wldfe__fdpxg = cgutils.pack_array(builder, [lir.Constant(lir.
            IntType(64), -1) for zll__rnkw in range(ncm__keb)])
    elif qvn__uicz.count < ncm__keb:
        wldfe__fdpxg = cgutils.pack_array(builder, [builder.extract_value(
            wldfe__fdpxg, ipwc__tlz) for ipwc__tlz in range(qvn__uicz.count
            )] + [lir.Constant(lir.IntType(64), -1) for zll__rnkw in range(
            ncm__keb - qvn__uicz.count)])
    srodl__wai, zll__rnkw, zll__rnkw, zll__rnkw = construct_array_item_array(
        context, builder, array_item_type, pimos__yax, wldfe__fdpxg)
    fja__esvfe = context.make_helper(builder, array_item_type)
    fja__esvfe.meminfo = srodl__wai
    return fja__esvfe._getvalue()


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
    n_arrays, uotqr__kbsf, bobwm__keoj, poala__lhlwp = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    wfy__mykl = context.get_value_type(payload_type)
    dtzjr__qydoz = context.get_abi_sizeof(wfy__mykl)
    ttk__ghkmj = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    srodl__wai = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, dtzjr__qydoz), ttk__ghkmj)
    pfk__ucii = context.nrt.meminfo_data(builder, srodl__wai)
    gkvho__ijleu = builder.bitcast(pfk__ucii, wfy__mykl.as_pointer())
    ijyt__vpg = cgutils.create_struct_proxy(payload_type)(context, builder)
    ijyt__vpg.n_arrays = n_arrays
    ijyt__vpg.data = uotqr__kbsf
    ijyt__vpg.offsets = bobwm__keoj
    ijyt__vpg.null_bitmap = poala__lhlwp
    builder.store(ijyt__vpg._getvalue(), gkvho__ijleu)
    context.nrt.incref(builder, signature.args[1], uotqr__kbsf)
    context.nrt.incref(builder, signature.args[2], bobwm__keoj)
    context.nrt.incref(builder, signature.args[3], poala__lhlwp)
    fja__esvfe = context.make_helper(builder, array_item_type)
    fja__esvfe.meminfo = srodl__wai
    return fja__esvfe._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    jon__zsth = ArrayItemArrayType(data_type)
    sig = jon__zsth(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ijyt__vpg = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ijyt__vpg.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        ijyt__vpg = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        rebx__urw = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, ijyt__vpg.offsets).data
        bobwm__keoj = builder.bitcast(rebx__urw, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(bobwm__keoj, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ijyt__vpg = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ijyt__vpg.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        ijyt__vpg = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            ijyt__vpg.null_bitmap)
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
        ijyt__vpg = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return ijyt__vpg.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, ttfbq__rpd = args
        fja__esvfe = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        pfk__ucii = context.nrt.meminfo_data(builder, fja__esvfe.meminfo)
        gkvho__ijleu = builder.bitcast(pfk__ucii, context.get_value_type(
            payload_type).as_pointer())
        ijyt__vpg = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(gkvho__ijleu))
        context.nrt.decref(builder, data_typ, ijyt__vpg.data)
        ijyt__vpg.data = ttfbq__rpd
        context.nrt.incref(builder, data_typ, ttfbq__rpd)
        builder.store(ijyt__vpg._getvalue(), gkvho__ijleu)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    uotqr__kbsf = get_data(arr)
    jrss__wwg = len(uotqr__kbsf)
    if jrss__wwg < new_size:
        tgju__bglzz = max(2 * jrss__wwg, new_size)
        ttfbq__rpd = bodo.libs.array_kernels.resize_and_copy(uotqr__kbsf,
            old_size, tgju__bglzz)
        replace_data_arr(arr, ttfbq__rpd)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    uotqr__kbsf = get_data(arr)
    bobwm__keoj = get_offsets(arr)
    hmi__kbyu = len(uotqr__kbsf)
    ynhv__ghu = bobwm__keoj[-1]
    if hmi__kbyu != ynhv__ghu:
        ttfbq__rpd = bodo.libs.array_kernels.resize_and_copy(uotqr__kbsf,
            ynhv__ghu, ynhv__ghu)
        replace_data_arr(arr, ttfbq__rpd)


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
            bobwm__keoj = get_offsets(arr)
            uotqr__kbsf = get_data(arr)
            tppy__llh = bobwm__keoj[ind]
            riawx__qidn = bobwm__keoj[ind + 1]
            return uotqr__kbsf[tppy__llh:riawx__qidn]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        bdfwu__jdt = arr.dtype

        def impl_bool(arr, ind):
            loofh__slyw = len(arr)
            if loofh__slyw != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            poala__lhlwp = get_null_bitmap(arr)
            n_arrays = 0
            nelb__ggat = init_nested_counts(bdfwu__jdt)
            for ipwc__tlz in range(loofh__slyw):
                if ind[ipwc__tlz]:
                    n_arrays += 1
                    gcs__msqfo = arr[ipwc__tlz]
                    nelb__ggat = add_nested_counts(nelb__ggat, gcs__msqfo)
            mqg__kpzp = pre_alloc_array_item_array(n_arrays, nelb__ggat,
                bdfwu__jdt)
            qxew__rfphk = get_null_bitmap(mqg__kpzp)
            oed__pcd = 0
            for dtxe__kph in range(loofh__slyw):
                if ind[dtxe__kph]:
                    mqg__kpzp[oed__pcd] = arr[dtxe__kph]
                    scrc__mjsig = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        poala__lhlwp, dtxe__kph)
                    bodo.libs.int_arr_ext.set_bit_to_arr(qxew__rfphk,
                        oed__pcd, scrc__mjsig)
                    oed__pcd += 1
            return mqg__kpzp
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        bdfwu__jdt = arr.dtype

        def impl_int(arr, ind):
            poala__lhlwp = get_null_bitmap(arr)
            loofh__slyw = len(ind)
            n_arrays = loofh__slyw
            nelb__ggat = init_nested_counts(bdfwu__jdt)
            for vgd__qqcm in range(loofh__slyw):
                ipwc__tlz = ind[vgd__qqcm]
                gcs__msqfo = arr[ipwc__tlz]
                nelb__ggat = add_nested_counts(nelb__ggat, gcs__msqfo)
            mqg__kpzp = pre_alloc_array_item_array(n_arrays, nelb__ggat,
                bdfwu__jdt)
            qxew__rfphk = get_null_bitmap(mqg__kpzp)
            for mzcsh__vsde in range(loofh__slyw):
                dtxe__kph = ind[mzcsh__vsde]
                mqg__kpzp[mzcsh__vsde] = arr[dtxe__kph]
                scrc__mjsig = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    poala__lhlwp, dtxe__kph)
                bodo.libs.int_arr_ext.set_bit_to_arr(qxew__rfphk,
                    mzcsh__vsde, scrc__mjsig)
            return mqg__kpzp
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            loofh__slyw = len(arr)
            cvia__uus = numba.cpython.unicode._normalize_slice(ind, loofh__slyw
                )
            oku__dcwkw = np.arange(cvia__uus.start, cvia__uus.stop,
                cvia__uus.step)
            return arr[oku__dcwkw]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            bobwm__keoj = get_offsets(A)
            poala__lhlwp = get_null_bitmap(A)
            if idx == 0:
                bobwm__keoj[0] = 0
            n_items = len(val)
            yrtyn__agxb = bobwm__keoj[idx] + n_items
            ensure_data_capacity(A, bobwm__keoj[idx], yrtyn__agxb)
            uotqr__kbsf = get_data(A)
            bobwm__keoj[idx + 1] = bobwm__keoj[idx] + n_items
            uotqr__kbsf[bobwm__keoj[idx]:bobwm__keoj[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(poala__lhlwp, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            cvia__uus = numba.cpython.unicode._normalize_slice(idx, len(A))
            for ipwc__tlz in range(cvia__uus.start, cvia__uus.stop,
                cvia__uus.step):
                A[ipwc__tlz] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            bobwm__keoj = get_offsets(A)
            poala__lhlwp = get_null_bitmap(A)
            drzdx__qycnd = get_offsets(val)
            pdnfv__azw = get_data(val)
            tej__wtr = get_null_bitmap(val)
            loofh__slyw = len(A)
            cvia__uus = numba.cpython.unicode._normalize_slice(idx, loofh__slyw
                )
            pofcg__jqum, romh__yvf = cvia__uus.start, cvia__uus.stop
            assert cvia__uus.step == 1
            if pofcg__jqum == 0:
                bobwm__keoj[pofcg__jqum] = 0
            uiraq__etvzz = bobwm__keoj[pofcg__jqum]
            yrtyn__agxb = uiraq__etvzz + len(pdnfv__azw)
            ensure_data_capacity(A, uiraq__etvzz, yrtyn__agxb)
            uotqr__kbsf = get_data(A)
            uotqr__kbsf[uiraq__etvzz:uiraq__etvzz + len(pdnfv__azw)
                ] = pdnfv__azw
            bobwm__keoj[pofcg__jqum:romh__yvf + 1
                ] = drzdx__qycnd + uiraq__etvzz
            qnpiy__agyml = 0
            for ipwc__tlz in range(pofcg__jqum, romh__yvf):
                scrc__mjsig = bodo.libs.int_arr_ext.get_bit_bitmap_arr(tej__wtr
                    , qnpiy__agyml)
                bodo.libs.int_arr_ext.set_bit_to_arr(poala__lhlwp,
                    ipwc__tlz, scrc__mjsig)
                qnpiy__agyml += 1
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
