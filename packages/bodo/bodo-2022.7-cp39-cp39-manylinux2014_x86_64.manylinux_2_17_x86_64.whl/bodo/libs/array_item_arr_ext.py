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
        whyrv__ngn = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, whyrv__ngn)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        whyrv__ngn = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, whyrv__ngn)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    uae__jpxl = builder.module
    hzps__dxd = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    wkd__lwue = cgutils.get_or_insert_function(uae__jpxl, hzps__dxd, name=
        '.dtor.array_item.{}'.format(array_item_type.dtype))
    if not wkd__lwue.is_declaration:
        return wkd__lwue
    wkd__lwue.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(wkd__lwue.append_basic_block())
    kpmw__yrji = wkd__lwue.args[0]
    izto__cvia = context.get_value_type(payload_type).as_pointer()
    ghhs__vpvul = builder.bitcast(kpmw__yrji, izto__cvia)
    jcqnd__hesbd = context.make_helper(builder, payload_type, ref=ghhs__vpvul)
    context.nrt.decref(builder, array_item_type.dtype, jcqnd__hesbd.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        jcqnd__hesbd.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        jcqnd__hesbd.null_bitmap)
    builder.ret_void()
    return wkd__lwue


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    ikfot__mbxhw = context.get_value_type(payload_type)
    irdmo__nnjo = context.get_abi_sizeof(ikfot__mbxhw)
    kmdic__lhd = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    ofvqa__xmoj = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, irdmo__nnjo), kmdic__lhd)
    yscwc__zvkjt = context.nrt.meminfo_data(builder, ofvqa__xmoj)
    knowb__ksf = builder.bitcast(yscwc__zvkjt, ikfot__mbxhw.as_pointer())
    jcqnd__hesbd = cgutils.create_struct_proxy(payload_type)(context, builder)
    jcqnd__hesbd.n_arrays = n_arrays
    bswj__plr = n_elems.type.count
    clbu__ouj = builder.extract_value(n_elems, 0)
    ztgla__uhgl = cgutils.alloca_once_value(builder, clbu__ouj)
    tvd__klw = builder.icmp_signed('==', clbu__ouj, lir.Constant(clbu__ouj.
        type, -1))
    with builder.if_then(tvd__klw):
        builder.store(n_arrays, ztgla__uhgl)
    n_elems = cgutils.pack_array(builder, [builder.load(ztgla__uhgl)] + [
        builder.extract_value(n_elems, vcai__dmtis) for vcai__dmtis in
        range(1, bswj__plr)])
    jcqnd__hesbd.data = gen_allocate_array(context, builder,
        array_item_type.dtype, n_elems, c)
    swkn__xtj = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    gew__lezk = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [swkn__xtj])
    offsets_ptr = gew__lezk.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    jcqnd__hesbd.offsets = gew__lezk._getvalue()
    vden__dssj = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    cdjf__xcuj = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [vden__dssj])
    null_bitmap_ptr = cdjf__xcuj.data
    jcqnd__hesbd.null_bitmap = cdjf__xcuj._getvalue()
    builder.store(jcqnd__hesbd._getvalue(), knowb__ksf)
    return ofvqa__xmoj, jcqnd__hesbd.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    vaxk__fbee, uvvsd__ihqm = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    ljb__ttadd = context.insert_const_string(builder.module, 'pandas')
    rgdos__ozwc = c.pyapi.import_module_noblock(ljb__ttadd)
    prb__stn = c.pyapi.object_getattr_string(rgdos__ozwc, 'NA')
    yrz__byi = c.context.get_constant(offset_type, 0)
    builder.store(yrz__byi, offsets_ptr)
    hhpo__uptx = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as wtgd__ink:
        hmtm__wtc = wtgd__ink.index
        item_ind = builder.load(hhpo__uptx)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [hmtm__wtc]))
        arr_obj = seq_getitem(builder, context, val, hmtm__wtc)
        set_bitmap_bit(builder, null_bitmap_ptr, hmtm__wtc, 0)
        zdh__puywd = is_na_value(builder, context, arr_obj, prb__stn)
        cfv__kyisw = builder.icmp_unsigned('!=', zdh__puywd, lir.Constant(
            zdh__puywd.type, 1))
        with builder.if_then(cfv__kyisw):
            set_bitmap_bit(builder, null_bitmap_ptr, hmtm__wtc, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), hhpo__uptx)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(hhpo__uptx), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(rgdos__ozwc)
    c.pyapi.decref(prb__stn)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    wwom__kuefm = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if wwom__kuefm:
        hzps__dxd = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        tvxs__snxo = cgutils.get_or_insert_function(c.builder.module,
            hzps__dxd, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(tvxs__snxo,
            [val])])
    else:
        wvbqy__dwcg = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            wvbqy__dwcg, vcai__dmtis) for vcai__dmtis in range(1,
            wvbqy__dwcg.type.count)])
    ofvqa__xmoj, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if wwom__kuefm:
        kzlzp__snvek = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        kaogk__xks = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        hzps__dxd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        wkd__lwue = cgutils.get_or_insert_function(c.builder.module,
            hzps__dxd, name='array_item_array_from_sequence')
        c.builder.call(wkd__lwue, [val, c.builder.bitcast(kaogk__xks, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), kzlzp__snvek)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    ywg__glai = c.context.make_helper(c.builder, typ)
    ywg__glai.meminfo = ofvqa__xmoj
    ybdy__etwns = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ywg__glai._getvalue(), is_error=ybdy__etwns)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    ywg__glai = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    yscwc__zvkjt = context.nrt.meminfo_data(builder, ywg__glai.meminfo)
    knowb__ksf = builder.bitcast(yscwc__zvkjt, context.get_value_type(
        payload_type).as_pointer())
    jcqnd__hesbd = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(knowb__ksf))
    return jcqnd__hesbd


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    ljb__ttadd = context.insert_const_string(builder.module, 'numpy')
    nxent__dvpv = c.pyapi.import_module_noblock(ljb__ttadd)
    nfurr__gld = c.pyapi.object_getattr_string(nxent__dvpv, 'object_')
    xomt__pif = c.pyapi.long_from_longlong(n_arrays)
    jlwm__mvhmh = c.pyapi.call_method(nxent__dvpv, 'ndarray', (xomt__pif,
        nfurr__gld))
    fgb__ymaj = c.pyapi.object_getattr_string(nxent__dvpv, 'nan')
    hhpo__uptx = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as wtgd__ink:
        hmtm__wtc = wtgd__ink.index
        pyarray_setitem(builder, context, jlwm__mvhmh, hmtm__wtc, fgb__ymaj)
        mrj__xzs = get_bitmap_bit(builder, null_bitmap_ptr, hmtm__wtc)
        ahvdq__bzyuh = builder.icmp_unsigned('!=', mrj__xzs, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(ahvdq__bzyuh):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(hmtm__wtc, lir.Constant(hmtm__wtc
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                hmtm__wtc]))), lir.IntType(64))
            item_ind = builder.load(hhpo__uptx)
            vaxk__fbee, uldr__hkfte = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), hhpo__uptx)
            arr_obj = c.pyapi.from_native_value(typ.dtype, uldr__hkfte, c.
                env_manager)
            pyarray_setitem(builder, context, jlwm__mvhmh, hmtm__wtc, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(nxent__dvpv)
    c.pyapi.decref(nfurr__gld)
    c.pyapi.decref(xomt__pif)
    c.pyapi.decref(fgb__ymaj)
    return jlwm__mvhmh


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    jcqnd__hesbd = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = jcqnd__hesbd.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), jcqnd__hesbd.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), jcqnd__hesbd.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        kzlzp__snvek = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        kaogk__xks = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        hzps__dxd = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        vrty__rza = cgutils.get_or_insert_function(c.builder.module,
            hzps__dxd, name='np_array_from_array_item_array')
        arr = c.builder.call(vrty__rza, [jcqnd__hesbd.n_arrays, c.builder.
            bitcast(kaogk__xks, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), kzlzp__snvek)])
    else:
        arr = _box_array_item_array_generic(typ, c, jcqnd__hesbd.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    foeec__rns, zfy__vfrt, xum__fju = args
    qtsq__skrf = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    aqo__mohfi = sig.args[1]
    if not isinstance(aqo__mohfi, types.UniTuple):
        zfy__vfrt = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for xum__fju in range(qtsq__skrf)])
    elif aqo__mohfi.count < qtsq__skrf:
        zfy__vfrt = cgutils.pack_array(builder, [builder.extract_value(
            zfy__vfrt, vcai__dmtis) for vcai__dmtis in range(aqo__mohfi.
            count)] + [lir.Constant(lir.IntType(64), -1) for xum__fju in
            range(qtsq__skrf - aqo__mohfi.count)])
    ofvqa__xmoj, xum__fju, xum__fju, xum__fju = construct_array_item_array(
        context, builder, array_item_type, foeec__rns, zfy__vfrt)
    ywg__glai = context.make_helper(builder, array_item_type)
    ywg__glai.meminfo = ofvqa__xmoj
    return ywg__glai._getvalue()


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
    n_arrays, ujzi__qmgi, gew__lezk, cdjf__xcuj = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    ikfot__mbxhw = context.get_value_type(payload_type)
    irdmo__nnjo = context.get_abi_sizeof(ikfot__mbxhw)
    kmdic__lhd = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    ofvqa__xmoj = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, irdmo__nnjo), kmdic__lhd)
    yscwc__zvkjt = context.nrt.meminfo_data(builder, ofvqa__xmoj)
    knowb__ksf = builder.bitcast(yscwc__zvkjt, ikfot__mbxhw.as_pointer())
    jcqnd__hesbd = cgutils.create_struct_proxy(payload_type)(context, builder)
    jcqnd__hesbd.n_arrays = n_arrays
    jcqnd__hesbd.data = ujzi__qmgi
    jcqnd__hesbd.offsets = gew__lezk
    jcqnd__hesbd.null_bitmap = cdjf__xcuj
    builder.store(jcqnd__hesbd._getvalue(), knowb__ksf)
    context.nrt.incref(builder, signature.args[1], ujzi__qmgi)
    context.nrt.incref(builder, signature.args[2], gew__lezk)
    context.nrt.incref(builder, signature.args[3], cdjf__xcuj)
    ywg__glai = context.make_helper(builder, array_item_type)
    ywg__glai.meminfo = ofvqa__xmoj
    return ywg__glai._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    xqyk__sidr = ArrayItemArrayType(data_type)
    sig = xqyk__sidr(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        jcqnd__hesbd = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            jcqnd__hesbd.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        jcqnd__hesbd = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        kaogk__xks = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, jcqnd__hesbd.offsets).data
        gew__lezk = builder.bitcast(kaogk__xks, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(gew__lezk, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        jcqnd__hesbd = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            jcqnd__hesbd.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        jcqnd__hesbd = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            jcqnd__hesbd.null_bitmap)
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
        jcqnd__hesbd = _get_array_item_arr_payload(context, builder,
            arr_typ, arr)
        return jcqnd__hesbd.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, oagb__jay = args
        ywg__glai = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        yscwc__zvkjt = context.nrt.meminfo_data(builder, ywg__glai.meminfo)
        knowb__ksf = builder.bitcast(yscwc__zvkjt, context.get_value_type(
            payload_type).as_pointer())
        jcqnd__hesbd = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(knowb__ksf))
        context.nrt.decref(builder, data_typ, jcqnd__hesbd.data)
        jcqnd__hesbd.data = oagb__jay
        context.nrt.incref(builder, data_typ, oagb__jay)
        builder.store(jcqnd__hesbd._getvalue(), knowb__ksf)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    ujzi__qmgi = get_data(arr)
    xfpwq__jgw = len(ujzi__qmgi)
    if xfpwq__jgw < new_size:
        egc__fnd = max(2 * xfpwq__jgw, new_size)
        oagb__jay = bodo.libs.array_kernels.resize_and_copy(ujzi__qmgi,
            old_size, egc__fnd)
        replace_data_arr(arr, oagb__jay)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    ujzi__qmgi = get_data(arr)
    gew__lezk = get_offsets(arr)
    bymq__erait = len(ujzi__qmgi)
    nfy__eqxni = gew__lezk[-1]
    if bymq__erait != nfy__eqxni:
        oagb__jay = bodo.libs.array_kernels.resize_and_copy(ujzi__qmgi,
            nfy__eqxni, nfy__eqxni)
        replace_data_arr(arr, oagb__jay)


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
            gew__lezk = get_offsets(arr)
            ujzi__qmgi = get_data(arr)
            bgznk__wgqru = gew__lezk[ind]
            fwpuh__vqr = gew__lezk[ind + 1]
            return ujzi__qmgi[bgznk__wgqru:fwpuh__vqr]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        jnr__nxehd = arr.dtype

        def impl_bool(arr, ind):
            vryhz__rfur = len(arr)
            if vryhz__rfur != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            cdjf__xcuj = get_null_bitmap(arr)
            n_arrays = 0
            aapfn__ozxuo = init_nested_counts(jnr__nxehd)
            for vcai__dmtis in range(vryhz__rfur):
                if ind[vcai__dmtis]:
                    n_arrays += 1
                    skr__qnpt = arr[vcai__dmtis]
                    aapfn__ozxuo = add_nested_counts(aapfn__ozxuo, skr__qnpt)
            jlwm__mvhmh = pre_alloc_array_item_array(n_arrays, aapfn__ozxuo,
                jnr__nxehd)
            jbgvo__tmwb = get_null_bitmap(jlwm__mvhmh)
            kdyqw__ajpc = 0
            for jbd__vspp in range(vryhz__rfur):
                if ind[jbd__vspp]:
                    jlwm__mvhmh[kdyqw__ajpc] = arr[jbd__vspp]
                    thq__kxs = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        cdjf__xcuj, jbd__vspp)
                    bodo.libs.int_arr_ext.set_bit_to_arr(jbgvo__tmwb,
                        kdyqw__ajpc, thq__kxs)
                    kdyqw__ajpc += 1
            return jlwm__mvhmh
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        jnr__nxehd = arr.dtype

        def impl_int(arr, ind):
            cdjf__xcuj = get_null_bitmap(arr)
            vryhz__rfur = len(ind)
            n_arrays = vryhz__rfur
            aapfn__ozxuo = init_nested_counts(jnr__nxehd)
            for hso__lljcy in range(vryhz__rfur):
                vcai__dmtis = ind[hso__lljcy]
                skr__qnpt = arr[vcai__dmtis]
                aapfn__ozxuo = add_nested_counts(aapfn__ozxuo, skr__qnpt)
            jlwm__mvhmh = pre_alloc_array_item_array(n_arrays, aapfn__ozxuo,
                jnr__nxehd)
            jbgvo__tmwb = get_null_bitmap(jlwm__mvhmh)
            for tqawx__pkfrn in range(vryhz__rfur):
                jbd__vspp = ind[tqawx__pkfrn]
                jlwm__mvhmh[tqawx__pkfrn] = arr[jbd__vspp]
                thq__kxs = bodo.libs.int_arr_ext.get_bit_bitmap_arr(cdjf__xcuj,
                    jbd__vspp)
                bodo.libs.int_arr_ext.set_bit_to_arr(jbgvo__tmwb,
                    tqawx__pkfrn, thq__kxs)
            return jlwm__mvhmh
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            vryhz__rfur = len(arr)
            qnudk__rkbi = numba.cpython.unicode._normalize_slice(ind,
                vryhz__rfur)
            cxkx__ciqi = np.arange(qnudk__rkbi.start, qnudk__rkbi.stop,
                qnudk__rkbi.step)
            return arr[cxkx__ciqi]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            gew__lezk = get_offsets(A)
            cdjf__xcuj = get_null_bitmap(A)
            if idx == 0:
                gew__lezk[0] = 0
            n_items = len(val)
            mrg__qodku = gew__lezk[idx] + n_items
            ensure_data_capacity(A, gew__lezk[idx], mrg__qodku)
            ujzi__qmgi = get_data(A)
            gew__lezk[idx + 1] = gew__lezk[idx] + n_items
            ujzi__qmgi[gew__lezk[idx]:gew__lezk[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(cdjf__xcuj, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            qnudk__rkbi = numba.cpython.unicode._normalize_slice(idx, len(A))
            for vcai__dmtis in range(qnudk__rkbi.start, qnudk__rkbi.stop,
                qnudk__rkbi.step):
                A[vcai__dmtis] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            gew__lezk = get_offsets(A)
            cdjf__xcuj = get_null_bitmap(A)
            enion__qpo = get_offsets(val)
            txxv__fps = get_data(val)
            fpyp__pvzm = get_null_bitmap(val)
            vryhz__rfur = len(A)
            qnudk__rkbi = numba.cpython.unicode._normalize_slice(idx,
                vryhz__rfur)
            imim__udk, vjgl__dhk = qnudk__rkbi.start, qnudk__rkbi.stop
            assert qnudk__rkbi.step == 1
            if imim__udk == 0:
                gew__lezk[imim__udk] = 0
            mhf__wjz = gew__lezk[imim__udk]
            mrg__qodku = mhf__wjz + len(txxv__fps)
            ensure_data_capacity(A, mhf__wjz, mrg__qodku)
            ujzi__qmgi = get_data(A)
            ujzi__qmgi[mhf__wjz:mhf__wjz + len(txxv__fps)] = txxv__fps
            gew__lezk[imim__udk:vjgl__dhk + 1] = enion__qpo + mhf__wjz
            zxzkk__hehk = 0
            for vcai__dmtis in range(imim__udk, vjgl__dhk):
                thq__kxs = bodo.libs.int_arr_ext.get_bit_bitmap_arr(fpyp__pvzm,
                    zxzkk__hehk)
                bodo.libs.int_arr_ext.set_bit_to_arr(cdjf__xcuj,
                    vcai__dmtis, thq__kxs)
                zxzkk__hehk += 1
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
