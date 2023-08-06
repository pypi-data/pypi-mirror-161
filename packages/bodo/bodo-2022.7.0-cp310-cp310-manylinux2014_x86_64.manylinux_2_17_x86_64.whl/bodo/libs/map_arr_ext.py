"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    nily__obpq = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(nily__obpq)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        recx__yqdal = _get_map_arr_data_type(fe_type)
        bfpz__quyxf = [('data', recx__yqdal)]
        models.StructModel.__init__(self, dmm, fe_type, bfpz__quyxf)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    lxk__ckaoq = all(isinstance(zdl__xkbok, types.Array) and zdl__xkbok.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for zdl__xkbok in (typ.key_arr_type, typ.
        value_arr_type))
    if lxk__ckaoq:
        bnsyy__tqfu = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        fqer__ays = cgutils.get_or_insert_function(c.builder.module,
            bnsyy__tqfu, name='count_total_elems_list_array')
        hsa__pkgb = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            fqer__ays, [val])])
    else:
        hsa__pkgb = get_array_elem_counts(c, c.builder, c.context, val, typ)
    recx__yqdal = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, recx__yqdal,
        hsa__pkgb, c)
    swha__craa = _get_array_item_arr_payload(c.context, c.builder,
        recx__yqdal, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, swha__craa.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, swha__craa.offsets).data
    ihv__twlks = _get_struct_arr_payload(c.context, c.builder, recx__yqdal.
        dtype, swha__craa.data)
    key_arr = c.builder.extract_value(ihv__twlks.data, 0)
    value_arr = c.builder.extract_value(ihv__twlks.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    cgr__gqaa, idup__qsq = c.pyapi.call_jit_code(lambda A: A.fill(255), sig,
        [ihv__twlks.null_bitmap])
    if lxk__ckaoq:
        ooof__mza = c.context.make_array(recx__yqdal.dtype.data[0])(c.
            context, c.builder, key_arr).data
        cujom__blsg = c.context.make_array(recx__yqdal.dtype.data[1])(c.
            context, c.builder, value_arr).data
        bnsyy__tqfu = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        uxhs__jlvbb = cgutils.get_or_insert_function(c.builder.module,
            bnsyy__tqfu, name='map_array_from_sequence')
        cjl__iup = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        jold__yfy = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(uxhs__jlvbb, [val, c.builder.bitcast(ooof__mza, lir.
            IntType(8).as_pointer()), c.builder.bitcast(cujom__blsg, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), cjl__iup), lir.Constant(lir.IntType(
            32), jold__yfy)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    ktyne__hxr = c.context.make_helper(c.builder, typ)
    ktyne__hxr.data = data_arr
    fimxn__vdmek = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ktyne__hxr._getvalue(), is_error=fimxn__vdmek)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    mwtjc__pysy = context.insert_const_string(builder.module, 'pandas')
    hotbb__crc = c.pyapi.import_module_noblock(mwtjc__pysy)
    qgabd__ukjq = c.pyapi.object_getattr_string(hotbb__crc, 'NA')
    xyuix__upol = c.context.get_constant(offset_type, 0)
    builder.store(xyuix__upol, offsets_ptr)
    lpy__ghc = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as iqemd__pdqdl:
        hdure__wla = iqemd__pdqdl.index
        item_ind = builder.load(lpy__ghc)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [hdure__wla]))
        tjo__mrdlr = seq_getitem(builder, context, val, hdure__wla)
        set_bitmap_bit(builder, null_bitmap_ptr, hdure__wla, 0)
        wiqk__guge = is_na_value(builder, context, tjo__mrdlr, qgabd__ukjq)
        bowhg__vcu = builder.icmp_unsigned('!=', wiqk__guge, lir.Constant(
            wiqk__guge.type, 1))
        with builder.if_then(bowhg__vcu):
            set_bitmap_bit(builder, null_bitmap_ptr, hdure__wla, 1)
            tgsbf__qpkt = dict_keys(builder, context, tjo__mrdlr)
            xvq__uuhfq = dict_values(builder, context, tjo__mrdlr)
            n_items = bodo.utils.utils.object_length(c, tgsbf__qpkt)
            _unbox_array_item_array_copy_data(typ.key_arr_type, tgsbf__qpkt,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                xvq__uuhfq, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), lpy__ghc)
            c.pyapi.decref(tgsbf__qpkt)
            c.pyapi.decref(xvq__uuhfq)
        c.pyapi.decref(tjo__mrdlr)
    builder.store(builder.trunc(builder.load(lpy__ghc), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(hotbb__crc)
    c.pyapi.decref(qgabd__ukjq)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    ktyne__hxr = c.context.make_helper(c.builder, typ, val)
    data_arr = ktyne__hxr.data
    recx__yqdal = _get_map_arr_data_type(typ)
    swha__craa = _get_array_item_arr_payload(c.context, c.builder,
        recx__yqdal, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, swha__craa.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, swha__craa.offsets).data
    ihv__twlks = _get_struct_arr_payload(c.context, c.builder, recx__yqdal.
        dtype, swha__craa.data)
    key_arr = c.builder.extract_value(ihv__twlks.data, 0)
    value_arr = c.builder.extract_value(ihv__twlks.data, 1)
    if all(isinstance(zdl__xkbok, types.Array) and zdl__xkbok.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        zdl__xkbok in (typ.key_arr_type, typ.value_arr_type)):
        ooof__mza = c.context.make_array(recx__yqdal.dtype.data[0])(c.
            context, c.builder, key_arr).data
        cujom__blsg = c.context.make_array(recx__yqdal.dtype.data[1])(c.
            context, c.builder, value_arr).data
        bnsyy__tqfu = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        osu__nof = cgutils.get_or_insert_function(c.builder.module,
            bnsyy__tqfu, name='np_array_from_map_array')
        cjl__iup = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        jold__yfy = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(osu__nof, [swha__craa.n_arrays, c.builder.
            bitcast(ooof__mza, lir.IntType(8).as_pointer()), c.builder.
            bitcast(cujom__blsg, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), cjl__iup), lir.
            Constant(lir.IntType(32), jold__yfy)])
    else:
        arr = _box_map_array_generic(typ, c, swha__craa.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    mwtjc__pysy = context.insert_const_string(builder.module, 'numpy')
    ypeam__hlkl = c.pyapi.import_module_noblock(mwtjc__pysy)
    ubzqj__rtlkz = c.pyapi.object_getattr_string(ypeam__hlkl, 'object_')
    ehjk__hsok = c.pyapi.long_from_longlong(n_maps)
    aozc__mnzl = c.pyapi.call_method(ypeam__hlkl, 'ndarray', (ehjk__hsok,
        ubzqj__rtlkz))
    tsd__fvsvr = c.pyapi.object_getattr_string(ypeam__hlkl, 'nan')
    yrhur__djwsg = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    lpy__ghc = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_maps) as iqemd__pdqdl:
        ucbfi__gpxb = iqemd__pdqdl.index
        pyarray_setitem(builder, context, aozc__mnzl, ucbfi__gpxb, tsd__fvsvr)
        qwut__ioy = get_bitmap_bit(builder, null_bitmap_ptr, ucbfi__gpxb)
        sfj__zgww = builder.icmp_unsigned('!=', qwut__ioy, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(sfj__zgww):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(ucbfi__gpxb, lir.Constant(
                ucbfi__gpxb.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [ucbfi__gpxb]))), lir.IntType(64))
            item_ind = builder.load(lpy__ghc)
            tjo__mrdlr = c.pyapi.dict_new()
            ehv__jhun = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            cgr__gqaa, qnxf__eeu = c.pyapi.call_jit_code(ehv__jhun, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            cgr__gqaa, nik__wnus = c.pyapi.call_jit_code(ehv__jhun, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            afzi__djij = c.pyapi.from_native_value(typ.key_arr_type,
                qnxf__eeu, c.env_manager)
            liycq__komwq = c.pyapi.from_native_value(typ.value_arr_type,
                nik__wnus, c.env_manager)
            vwqh__ycl = c.pyapi.call_function_objargs(yrhur__djwsg, (
                afzi__djij, liycq__komwq))
            dict_merge_from_seq2(builder, context, tjo__mrdlr, vwqh__ycl)
            builder.store(builder.add(item_ind, n_items), lpy__ghc)
            pyarray_setitem(builder, context, aozc__mnzl, ucbfi__gpxb,
                tjo__mrdlr)
            c.pyapi.decref(vwqh__ycl)
            c.pyapi.decref(afzi__djij)
            c.pyapi.decref(liycq__komwq)
            c.pyapi.decref(tjo__mrdlr)
    c.pyapi.decref(yrhur__djwsg)
    c.pyapi.decref(ypeam__hlkl)
    c.pyapi.decref(ubzqj__rtlkz)
    c.pyapi.decref(ehjk__hsok)
    c.pyapi.decref(tsd__fvsvr)
    return aozc__mnzl


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    ktyne__hxr = context.make_helper(builder, sig.return_type)
    ktyne__hxr.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return ktyne__hxr._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    ciic__lfgo = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return ciic__lfgo(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    rjhi__nqm = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(rjhi__nqm)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    ecpz__mjuog = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            xhn__orbpo = val.keys()
            sqgkm__vsd = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), ecpz__mjuog, ('key', 'value'))
            for aqfcj__lpnh, pfgzm__sxt in enumerate(xhn__orbpo):
                sqgkm__vsd[aqfcj__lpnh] = bodo.libs.struct_arr_ext.init_struct(
                    (pfgzm__sxt, val[pfgzm__sxt]), ('key', 'value'))
            arr._data[ind] = sqgkm__vsd
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            vav__wonnk = dict()
            vwvl__lczd = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            sqgkm__vsd = bodo.libs.array_item_arr_ext.get_data(arr._data)
            jmxgg__ucftt, jdmft__iile = bodo.libs.struct_arr_ext.get_data(
                sqgkm__vsd)
            mcvol__wiqtt = vwvl__lczd[ind]
            aknt__npcz = vwvl__lczd[ind + 1]
            for aqfcj__lpnh in range(mcvol__wiqtt, aknt__npcz):
                vav__wonnk[jmxgg__ucftt[aqfcj__lpnh]] = jdmft__iile[aqfcj__lpnh
                    ]
            return vav__wonnk
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
