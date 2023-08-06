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
    ycke__jkraz = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(ycke__jkraz)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bdug__iypc = _get_map_arr_data_type(fe_type)
        qpbn__sna = [('data', bdug__iypc)]
        models.StructModel.__init__(self, dmm, fe_type, qpbn__sna)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    ngysc__hpg = all(isinstance(hlri__xnni, types.Array) and hlri__xnni.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for hlri__xnni in (typ.key_arr_type, typ.
        value_arr_type))
    if ngysc__hpg:
        laylv__scf = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        hkds__zjizm = cgutils.get_or_insert_function(c.builder.module,
            laylv__scf, name='count_total_elems_list_array')
        zyrx__yru = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            hkds__zjizm, [val])])
    else:
        zyrx__yru = get_array_elem_counts(c, c.builder, c.context, val, typ)
    bdug__iypc = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, bdug__iypc,
        zyrx__yru, c)
    pmtbh__qadk = _get_array_item_arr_payload(c.context, c.builder,
        bdug__iypc, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, pmtbh__qadk.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, pmtbh__qadk.offsets).data
    vghh__uteq = _get_struct_arr_payload(c.context, c.builder, bdug__iypc.
        dtype, pmtbh__qadk.data)
    key_arr = c.builder.extract_value(vghh__uteq.data, 0)
    value_arr = c.builder.extract_value(vghh__uteq.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    juxpn__rzxg, tpht__puarq = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [vghh__uteq.null_bitmap])
    if ngysc__hpg:
        poz__ojnx = c.context.make_array(bdug__iypc.dtype.data[0])(c.
            context, c.builder, key_arr).data
        fnl__wxa = c.context.make_array(bdug__iypc.dtype.data[1])(c.context,
            c.builder, value_arr).data
        laylv__scf = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        rqsxp__heszs = cgutils.get_or_insert_function(c.builder.module,
            laylv__scf, name='map_array_from_sequence')
        budi__haxio = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        ooe__whr = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(rqsxp__heszs, [val, c.builder.bitcast(poz__ojnx, lir
            .IntType(8).as_pointer()), c.builder.bitcast(fnl__wxa, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), budi__haxio), lir.Constant(lir.
            IntType(32), ooe__whr)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    ywhnt__jdoje = c.context.make_helper(c.builder, typ)
    ywhnt__jdoje.data = data_arr
    kgu__jqexi = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ywhnt__jdoje._getvalue(), is_error=kgu__jqexi)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    utu__ypgi = context.insert_const_string(builder.module, 'pandas')
    yqvdf__vqbj = c.pyapi.import_module_noblock(utu__ypgi)
    rfyw__wmb = c.pyapi.object_getattr_string(yqvdf__vqbj, 'NA')
    qopar__wdkaq = c.context.get_constant(offset_type, 0)
    builder.store(qopar__wdkaq, offsets_ptr)
    suvb__qacz = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as sjrl__yjk:
        ibqu__boamf = sjrl__yjk.index
        item_ind = builder.load(suvb__qacz)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [ibqu__boamf]))
        fqx__sslf = seq_getitem(builder, context, val, ibqu__boamf)
        set_bitmap_bit(builder, null_bitmap_ptr, ibqu__boamf, 0)
        tfns__ryh = is_na_value(builder, context, fqx__sslf, rfyw__wmb)
        iqn__pifjw = builder.icmp_unsigned('!=', tfns__ryh, lir.Constant(
            tfns__ryh.type, 1))
        with builder.if_then(iqn__pifjw):
            set_bitmap_bit(builder, null_bitmap_ptr, ibqu__boamf, 1)
            yfkp__yzh = dict_keys(builder, context, fqx__sslf)
            qpi__qgype = dict_values(builder, context, fqx__sslf)
            n_items = bodo.utils.utils.object_length(c, yfkp__yzh)
            _unbox_array_item_array_copy_data(typ.key_arr_type, yfkp__yzh,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                qpi__qgype, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), suvb__qacz)
            c.pyapi.decref(yfkp__yzh)
            c.pyapi.decref(qpi__qgype)
        c.pyapi.decref(fqx__sslf)
    builder.store(builder.trunc(builder.load(suvb__qacz), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(yqvdf__vqbj)
    c.pyapi.decref(rfyw__wmb)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    ywhnt__jdoje = c.context.make_helper(c.builder, typ, val)
    data_arr = ywhnt__jdoje.data
    bdug__iypc = _get_map_arr_data_type(typ)
    pmtbh__qadk = _get_array_item_arr_payload(c.context, c.builder,
        bdug__iypc, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, pmtbh__qadk.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, pmtbh__qadk.offsets).data
    vghh__uteq = _get_struct_arr_payload(c.context, c.builder, bdug__iypc.
        dtype, pmtbh__qadk.data)
    key_arr = c.builder.extract_value(vghh__uteq.data, 0)
    value_arr = c.builder.extract_value(vghh__uteq.data, 1)
    if all(isinstance(hlri__xnni, types.Array) and hlri__xnni.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type) for
        hlri__xnni in (typ.key_arr_type, typ.value_arr_type)):
        poz__ojnx = c.context.make_array(bdug__iypc.dtype.data[0])(c.
            context, c.builder, key_arr).data
        fnl__wxa = c.context.make_array(bdug__iypc.dtype.data[1])(c.context,
            c.builder, value_arr).data
        laylv__scf = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        lmvf__ywfun = cgutils.get_or_insert_function(c.builder.module,
            laylv__scf, name='np_array_from_map_array')
        budi__haxio = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        ooe__whr = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(lmvf__ywfun, [pmtbh__qadk.n_arrays, c.builder.
            bitcast(poz__ojnx, lir.IntType(8).as_pointer()), c.builder.
            bitcast(fnl__wxa, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), budi__haxio),
            lir.Constant(lir.IntType(32), ooe__whr)])
    else:
        arr = _box_map_array_generic(typ, c, pmtbh__qadk.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    utu__ypgi = context.insert_const_string(builder.module, 'numpy')
    akmb__svmde = c.pyapi.import_module_noblock(utu__ypgi)
    lwa__aodlx = c.pyapi.object_getattr_string(akmb__svmde, 'object_')
    gbce__qylnx = c.pyapi.long_from_longlong(n_maps)
    sbng__gpl = c.pyapi.call_method(akmb__svmde, 'ndarray', (gbce__qylnx,
        lwa__aodlx))
    hmep__aisj = c.pyapi.object_getattr_string(akmb__svmde, 'nan')
    dshbp__gbaa = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    suvb__qacz = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as sjrl__yjk:
        hves__rsxp = sjrl__yjk.index
        pyarray_setitem(builder, context, sbng__gpl, hves__rsxp, hmep__aisj)
        dekm__uzdk = get_bitmap_bit(builder, null_bitmap_ptr, hves__rsxp)
        vvaxs__inzck = builder.icmp_unsigned('!=', dekm__uzdk, lir.Constant
            (lir.IntType(8), 0))
        with builder.if_then(vvaxs__inzck):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(hves__rsxp, lir.Constant(
                hves__rsxp.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [hves__rsxp]))), lir.IntType(64))
            item_ind = builder.load(suvb__qacz)
            fqx__sslf = c.pyapi.dict_new()
            okluy__xbe = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            juxpn__rzxg, dpx__fvi = c.pyapi.call_jit_code(okluy__xbe, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            juxpn__rzxg, rpey__pxw = c.pyapi.call_jit_code(okluy__xbe, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            alvaj__gagfj = c.pyapi.from_native_value(typ.key_arr_type,
                dpx__fvi, c.env_manager)
            kuej__mcpjj = c.pyapi.from_native_value(typ.value_arr_type,
                rpey__pxw, c.env_manager)
            oyfyv__qnii = c.pyapi.call_function_objargs(dshbp__gbaa, (
                alvaj__gagfj, kuej__mcpjj))
            dict_merge_from_seq2(builder, context, fqx__sslf, oyfyv__qnii)
            builder.store(builder.add(item_ind, n_items), suvb__qacz)
            pyarray_setitem(builder, context, sbng__gpl, hves__rsxp, fqx__sslf)
            c.pyapi.decref(oyfyv__qnii)
            c.pyapi.decref(alvaj__gagfj)
            c.pyapi.decref(kuej__mcpjj)
            c.pyapi.decref(fqx__sslf)
    c.pyapi.decref(dshbp__gbaa)
    c.pyapi.decref(akmb__svmde)
    c.pyapi.decref(lwa__aodlx)
    c.pyapi.decref(gbce__qylnx)
    c.pyapi.decref(hmep__aisj)
    return sbng__gpl


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    ywhnt__jdoje = context.make_helper(builder, sig.return_type)
    ywhnt__jdoje.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return ywhnt__jdoje._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    qec__kzdwy = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return qec__kzdwy(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    qsbtw__rbtu = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(qsbtw__rbtu)


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
    hdrgt__hrs = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            bybob__eayq = val.keys()
            zrn__lgi = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len(
                val), (-1,), hdrgt__hrs, ('key', 'value'))
            for ckfa__rkzcw, gxftd__ivgmi in enumerate(bybob__eayq):
                zrn__lgi[ckfa__rkzcw] = bodo.libs.struct_arr_ext.init_struct((
                    gxftd__ivgmi, val[gxftd__ivgmi]), ('key', 'value'))
            arr._data[ind] = zrn__lgi
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
            ixfd__soeey = dict()
            hggbv__rnbhm = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            zrn__lgi = bodo.libs.array_item_arr_ext.get_data(arr._data)
            aamg__znti, yxr__ejofe = bodo.libs.struct_arr_ext.get_data(zrn__lgi
                )
            btsrb__tjyfc = hggbv__rnbhm[ind]
            ziigh__awtze = hggbv__rnbhm[ind + 1]
            for ckfa__rkzcw in range(btsrb__tjyfc, ziigh__awtze):
                ixfd__soeey[aamg__znti[ckfa__rkzcw]] = yxr__ejofe[ckfa__rkzcw]
            return ixfd__soeey
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
