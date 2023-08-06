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
        ixk__kxt = [('n_arrays', types.int64), ('data', fe_type.array_type.
            dtype), ('offsets', types.Array(offset_type, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, ixk__kxt)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        ixk__kxt = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, ixk__kxt)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    wysr__nwu = builder.module
    tog__oqhaq = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    yep__sqo = cgutils.get_or_insert_function(wysr__nwu, tog__oqhaq, name=
        '.dtor.array_item.{}'.format(array_item_type.dtype))
    if not yep__sqo.is_declaration:
        return yep__sqo
    yep__sqo.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(yep__sqo.append_basic_block())
    kqxgk__uhdw = yep__sqo.args[0]
    jnfzz__kmgs = context.get_value_type(payload_type).as_pointer()
    upl__urrpt = builder.bitcast(kqxgk__uhdw, jnfzz__kmgs)
    giesm__vjqjh = context.make_helper(builder, payload_type, ref=upl__urrpt)
    context.nrt.decref(builder, array_item_type.dtype, giesm__vjqjh.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        giesm__vjqjh.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        giesm__vjqjh.null_bitmap)
    builder.ret_void()
    return yep__sqo


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    pqsd__vptnl = context.get_value_type(payload_type)
    niqw__hlo = context.get_abi_sizeof(pqsd__vptnl)
    gyr__qrx = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    nquvj__xoqo = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, niqw__hlo), gyr__qrx)
    uucbe__ncm = context.nrt.meminfo_data(builder, nquvj__xoqo)
    rtmi__qit = builder.bitcast(uucbe__ncm, pqsd__vptnl.as_pointer())
    giesm__vjqjh = cgutils.create_struct_proxy(payload_type)(context, builder)
    giesm__vjqjh.n_arrays = n_arrays
    urw__qqqk = n_elems.type.count
    wgh__cvwma = builder.extract_value(n_elems, 0)
    qtwlg__pdktj = cgutils.alloca_once_value(builder, wgh__cvwma)
    jskyd__bjr = builder.icmp_signed('==', wgh__cvwma, lir.Constant(
        wgh__cvwma.type, -1))
    with builder.if_then(jskyd__bjr):
        builder.store(n_arrays, qtwlg__pdktj)
    n_elems = cgutils.pack_array(builder, [builder.load(qtwlg__pdktj)] + [
        builder.extract_value(n_elems, wlr__nttoz) for wlr__nttoz in range(
        1, urw__qqqk)])
    giesm__vjqjh.data = gen_allocate_array(context, builder,
        array_item_type.dtype, n_elems, c)
    ozu__bbtq = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    utpp__zmy = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [ozu__bbtq])
    offsets_ptr = utpp__zmy.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    giesm__vjqjh.offsets = utpp__zmy._getvalue()
    fkkzy__dizwf = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    jqw__pxu = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [fkkzy__dizwf])
    null_bitmap_ptr = jqw__pxu.data
    giesm__vjqjh.null_bitmap = jqw__pxu._getvalue()
    builder.store(giesm__vjqjh._getvalue(), rtmi__qit)
    return nquvj__xoqo, giesm__vjqjh.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    htdea__zgl, wqp__kbskx = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    hgiuh__nmmau = context.insert_const_string(builder.module, 'pandas')
    fir__nweo = c.pyapi.import_module_noblock(hgiuh__nmmau)
    hxxw__xvc = c.pyapi.object_getattr_string(fir__nweo, 'NA')
    wmzn__zgjy = c.context.get_constant(offset_type, 0)
    builder.store(wmzn__zgjy, offsets_ptr)
    gar__pjj = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as ljgc__fsmm:
        hhqu__nlywe = ljgc__fsmm.index
        item_ind = builder.load(gar__pjj)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [hhqu__nlywe]))
        arr_obj = seq_getitem(builder, context, val, hhqu__nlywe)
        set_bitmap_bit(builder, null_bitmap_ptr, hhqu__nlywe, 0)
        psf__gbgw = is_na_value(builder, context, arr_obj, hxxw__xvc)
        bcqxi__jfld = builder.icmp_unsigned('!=', psf__gbgw, lir.Constant(
            psf__gbgw.type, 1))
        with builder.if_then(bcqxi__jfld):
            set_bitmap_bit(builder, null_bitmap_ptr, hhqu__nlywe, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), gar__pjj)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(gar__pjj), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(fir__nweo)
    c.pyapi.decref(hxxw__xvc)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    mbo__vmuoy = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if mbo__vmuoy:
        tog__oqhaq = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        vgvk__zvc = cgutils.get_or_insert_function(c.builder.module,
            tog__oqhaq, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(vgvk__zvc,
            [val])])
    else:
        zhcwo__hdef = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            zhcwo__hdef, wlr__nttoz) for wlr__nttoz in range(1, zhcwo__hdef
            .type.count)])
    nquvj__xoqo, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if mbo__vmuoy:
        vxi__vrv = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        vfv__orsnl = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        tog__oqhaq = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        yep__sqo = cgutils.get_or_insert_function(c.builder.module,
            tog__oqhaq, name='array_item_array_from_sequence')
        c.builder.call(yep__sqo, [val, c.builder.bitcast(vfv__orsnl, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), vxi__vrv)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    mrwra__wpnb = c.context.make_helper(c.builder, typ)
    mrwra__wpnb.meminfo = nquvj__xoqo
    pqm__nylp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mrwra__wpnb._getvalue(), is_error=pqm__nylp)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    mrwra__wpnb = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    uucbe__ncm = context.nrt.meminfo_data(builder, mrwra__wpnb.meminfo)
    rtmi__qit = builder.bitcast(uucbe__ncm, context.get_value_type(
        payload_type).as_pointer())
    giesm__vjqjh = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(rtmi__qit))
    return giesm__vjqjh


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    hgiuh__nmmau = context.insert_const_string(builder.module, 'numpy')
    enmw__thl = c.pyapi.import_module_noblock(hgiuh__nmmau)
    jscjv__wkztc = c.pyapi.object_getattr_string(enmw__thl, 'object_')
    eeq__bjg = c.pyapi.long_from_longlong(n_arrays)
    mmi__lth = c.pyapi.call_method(enmw__thl, 'ndarray', (eeq__bjg,
        jscjv__wkztc))
    laa__usfl = c.pyapi.object_getattr_string(enmw__thl, 'nan')
    gar__pjj = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_arrays) as ljgc__fsmm:
        hhqu__nlywe = ljgc__fsmm.index
        pyarray_setitem(builder, context, mmi__lth, hhqu__nlywe, laa__usfl)
        srt__lfw = get_bitmap_bit(builder, null_bitmap_ptr, hhqu__nlywe)
        lvv__mav = builder.icmp_unsigned('!=', srt__lfw, lir.Constant(lir.
            IntType(8), 0))
        with builder.if_then(lvv__mav):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(hhqu__nlywe, lir.Constant(
                hhqu__nlywe.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [hhqu__nlywe]))), lir.IntType(64))
            item_ind = builder.load(gar__pjj)
            htdea__zgl, tkxg__yvrz = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), gar__pjj)
            arr_obj = c.pyapi.from_native_value(typ.dtype, tkxg__yvrz, c.
                env_manager)
            pyarray_setitem(builder, context, mmi__lth, hhqu__nlywe, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(enmw__thl)
    c.pyapi.decref(jscjv__wkztc)
    c.pyapi.decref(eeq__bjg)
    c.pyapi.decref(laa__usfl)
    return mmi__lth


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    giesm__vjqjh = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = giesm__vjqjh.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), giesm__vjqjh.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), giesm__vjqjh.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        vxi__vrv = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        vfv__orsnl = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        tog__oqhaq = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        xem__ztoj = cgutils.get_or_insert_function(c.builder.module,
            tog__oqhaq, name='np_array_from_array_item_array')
        arr = c.builder.call(xem__ztoj, [giesm__vjqjh.n_arrays, c.builder.
            bitcast(vfv__orsnl, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), vxi__vrv)])
    else:
        arr = _box_array_item_array_generic(typ, c, giesm__vjqjh.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    nqmdv__kqmdy, flwg__dbasf, ddc__extb = args
    zwa__edlyk = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    kkma__waptu = sig.args[1]
    if not isinstance(kkma__waptu, types.UniTuple):
        flwg__dbasf = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), -1) for ddc__extb in range(zwa__edlyk)])
    elif kkma__waptu.count < zwa__edlyk:
        flwg__dbasf = cgutils.pack_array(builder, [builder.extract_value(
            flwg__dbasf, wlr__nttoz) for wlr__nttoz in range(kkma__waptu.
            count)] + [lir.Constant(lir.IntType(64), -1) for ddc__extb in
            range(zwa__edlyk - kkma__waptu.count)])
    nquvj__xoqo, ddc__extb, ddc__extb, ddc__extb = construct_array_item_array(
        context, builder, array_item_type, nqmdv__kqmdy, flwg__dbasf)
    mrwra__wpnb = context.make_helper(builder, array_item_type)
    mrwra__wpnb.meminfo = nquvj__xoqo
    return mrwra__wpnb._getvalue()


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
    n_arrays, dzbv__upr, utpp__zmy, jqw__pxu = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    pqsd__vptnl = context.get_value_type(payload_type)
    niqw__hlo = context.get_abi_sizeof(pqsd__vptnl)
    gyr__qrx = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    nquvj__xoqo = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, niqw__hlo), gyr__qrx)
    uucbe__ncm = context.nrt.meminfo_data(builder, nquvj__xoqo)
    rtmi__qit = builder.bitcast(uucbe__ncm, pqsd__vptnl.as_pointer())
    giesm__vjqjh = cgutils.create_struct_proxy(payload_type)(context, builder)
    giesm__vjqjh.n_arrays = n_arrays
    giesm__vjqjh.data = dzbv__upr
    giesm__vjqjh.offsets = utpp__zmy
    giesm__vjqjh.null_bitmap = jqw__pxu
    builder.store(giesm__vjqjh._getvalue(), rtmi__qit)
    context.nrt.incref(builder, signature.args[1], dzbv__upr)
    context.nrt.incref(builder, signature.args[2], utpp__zmy)
    context.nrt.incref(builder, signature.args[3], jqw__pxu)
    mrwra__wpnb = context.make_helper(builder, array_item_type)
    mrwra__wpnb.meminfo = nquvj__xoqo
    return mrwra__wpnb._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    drce__reld = ArrayItemArrayType(data_type)
    sig = drce__reld(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        giesm__vjqjh = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            giesm__vjqjh.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        giesm__vjqjh = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        vfv__orsnl = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, giesm__vjqjh.offsets).data
        utpp__zmy = builder.bitcast(vfv__orsnl, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(utpp__zmy, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        giesm__vjqjh = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            giesm__vjqjh.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        giesm__vjqjh = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            giesm__vjqjh.null_bitmap)
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
        giesm__vjqjh = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return giesm__vjqjh.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, sycp__fxwaf = args
        mrwra__wpnb = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        uucbe__ncm = context.nrt.meminfo_data(builder, mrwra__wpnb.meminfo)
        rtmi__qit = builder.bitcast(uucbe__ncm, context.get_value_type(
            payload_type).as_pointer())
        giesm__vjqjh = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(rtmi__qit))
        context.nrt.decref(builder, data_typ, giesm__vjqjh.data)
        giesm__vjqjh.data = sycp__fxwaf
        context.nrt.incref(builder, data_typ, sycp__fxwaf)
        builder.store(giesm__vjqjh._getvalue(), rtmi__qit)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    dzbv__upr = get_data(arr)
    mapy__thxml = len(dzbv__upr)
    if mapy__thxml < new_size:
        pydo__kdaa = max(2 * mapy__thxml, new_size)
        sycp__fxwaf = bodo.libs.array_kernels.resize_and_copy(dzbv__upr,
            old_size, pydo__kdaa)
        replace_data_arr(arr, sycp__fxwaf)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    dzbv__upr = get_data(arr)
    utpp__zmy = get_offsets(arr)
    vcm__bcua = len(dzbv__upr)
    hpy__wjrzr = utpp__zmy[-1]
    if vcm__bcua != hpy__wjrzr:
        sycp__fxwaf = bodo.libs.array_kernels.resize_and_copy(dzbv__upr,
            hpy__wjrzr, hpy__wjrzr)
        replace_data_arr(arr, sycp__fxwaf)


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
            utpp__zmy = get_offsets(arr)
            dzbv__upr = get_data(arr)
            tojs__frn = utpp__zmy[ind]
            npk__kzr = utpp__zmy[ind + 1]
            return dzbv__upr[tojs__frn:npk__kzr]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        zctkm__zefg = arr.dtype

        def impl_bool(arr, ind):
            lor__eheyn = len(arr)
            if lor__eheyn != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            jqw__pxu = get_null_bitmap(arr)
            n_arrays = 0
            qocs__tdrq = init_nested_counts(zctkm__zefg)
            for wlr__nttoz in range(lor__eheyn):
                if ind[wlr__nttoz]:
                    n_arrays += 1
                    twre__hgt = arr[wlr__nttoz]
                    qocs__tdrq = add_nested_counts(qocs__tdrq, twre__hgt)
            mmi__lth = pre_alloc_array_item_array(n_arrays, qocs__tdrq,
                zctkm__zefg)
            kdq__qikfo = get_null_bitmap(mmi__lth)
            dhz__afgg = 0
            for rzrrj__riyz in range(lor__eheyn):
                if ind[rzrrj__riyz]:
                    mmi__lth[dhz__afgg] = arr[rzrrj__riyz]
                    lkzvx__ybale = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        jqw__pxu, rzrrj__riyz)
                    bodo.libs.int_arr_ext.set_bit_to_arr(kdq__qikfo,
                        dhz__afgg, lkzvx__ybale)
                    dhz__afgg += 1
            return mmi__lth
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        zctkm__zefg = arr.dtype

        def impl_int(arr, ind):
            jqw__pxu = get_null_bitmap(arr)
            lor__eheyn = len(ind)
            n_arrays = lor__eheyn
            qocs__tdrq = init_nested_counts(zctkm__zefg)
            for elhj__kqexb in range(lor__eheyn):
                wlr__nttoz = ind[elhj__kqexb]
                twre__hgt = arr[wlr__nttoz]
                qocs__tdrq = add_nested_counts(qocs__tdrq, twre__hgt)
            mmi__lth = pre_alloc_array_item_array(n_arrays, qocs__tdrq,
                zctkm__zefg)
            kdq__qikfo = get_null_bitmap(mmi__lth)
            for ruqw__pgi in range(lor__eheyn):
                rzrrj__riyz = ind[ruqw__pgi]
                mmi__lth[ruqw__pgi] = arr[rzrrj__riyz]
                lkzvx__ybale = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    jqw__pxu, rzrrj__riyz)
                bodo.libs.int_arr_ext.set_bit_to_arr(kdq__qikfo, ruqw__pgi,
                    lkzvx__ybale)
            return mmi__lth
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            lor__eheyn = len(arr)
            quziu__ehyal = numba.cpython.unicode._normalize_slice(ind,
                lor__eheyn)
            yihys__okxcd = np.arange(quziu__ehyal.start, quziu__ehyal.stop,
                quziu__ehyal.step)
            return arr[yihys__okxcd]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            utpp__zmy = get_offsets(A)
            jqw__pxu = get_null_bitmap(A)
            if idx == 0:
                utpp__zmy[0] = 0
            n_items = len(val)
            lzvnz__imqbn = utpp__zmy[idx] + n_items
            ensure_data_capacity(A, utpp__zmy[idx], lzvnz__imqbn)
            dzbv__upr = get_data(A)
            utpp__zmy[idx + 1] = utpp__zmy[idx] + n_items
            dzbv__upr[utpp__zmy[idx]:utpp__zmy[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(jqw__pxu, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            quziu__ehyal = numba.cpython.unicode._normalize_slice(idx, len(A))
            for wlr__nttoz in range(quziu__ehyal.start, quziu__ehyal.stop,
                quziu__ehyal.step):
                A[wlr__nttoz] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            utpp__zmy = get_offsets(A)
            jqw__pxu = get_null_bitmap(A)
            wgele__weyu = get_offsets(val)
            dfdmt__guw = get_data(val)
            gnh__iwlka = get_null_bitmap(val)
            lor__eheyn = len(A)
            quziu__ehyal = numba.cpython.unicode._normalize_slice(idx,
                lor__eheyn)
            srl__rrx, fkmo__wdxn = quziu__ehyal.start, quziu__ehyal.stop
            assert quziu__ehyal.step == 1
            if srl__rrx == 0:
                utpp__zmy[srl__rrx] = 0
            hou__suiis = utpp__zmy[srl__rrx]
            lzvnz__imqbn = hou__suiis + len(dfdmt__guw)
            ensure_data_capacity(A, hou__suiis, lzvnz__imqbn)
            dzbv__upr = get_data(A)
            dzbv__upr[hou__suiis:hou__suiis + len(dfdmt__guw)] = dfdmt__guw
            utpp__zmy[srl__rrx:fkmo__wdxn + 1] = wgele__weyu + hou__suiis
            zioly__mri = 0
            for wlr__nttoz in range(srl__rrx, fkmo__wdxn):
                lkzvx__ybale = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    gnh__iwlka, zioly__mri)
                bodo.libs.int_arr_ext.set_bit_to_arr(jqw__pxu, wlr__nttoz,
                    lkzvx__ybale)
                zioly__mri += 1
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
