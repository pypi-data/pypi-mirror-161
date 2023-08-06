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
    aipps__egjzc = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(aipps__egjzc)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        uarrd__ycuo = _get_map_arr_data_type(fe_type)
        fcrs__fohw = [('data', uarrd__ycuo)]
        models.StructModel.__init__(self, dmm, fe_type, fcrs__fohw)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    stgxt__mlbem = all(isinstance(hbgq__vhx, types.Array) and hbgq__vhx.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for hbgq__vhx in (typ.key_arr_type, typ.
        value_arr_type))
    if stgxt__mlbem:
        ddi__srum = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        xnzzn__nsnd = cgutils.get_or_insert_function(c.builder.module,
            ddi__srum, name='count_total_elems_list_array')
        vsn__zmkm = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            xnzzn__nsnd, [val])])
    else:
        vsn__zmkm = get_array_elem_counts(c, c.builder, c.context, val, typ)
    uarrd__ycuo = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, uarrd__ycuo,
        vsn__zmkm, c)
    lane__jegin = _get_array_item_arr_payload(c.context, c.builder,
        uarrd__ycuo, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, lane__jegin.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, lane__jegin.offsets).data
    phdzx__uoa = _get_struct_arr_payload(c.context, c.builder, uarrd__ycuo.
        dtype, lane__jegin.data)
    key_arr = c.builder.extract_value(phdzx__uoa.data, 0)
    value_arr = c.builder.extract_value(phdzx__uoa.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    ykprm__iyi, rdwnd__qnm = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [phdzx__uoa.null_bitmap])
    if stgxt__mlbem:
        fjdk__qnpjv = c.context.make_array(uarrd__ycuo.dtype.data[0])(c.
            context, c.builder, key_arr).data
        frt__apt = c.context.make_array(uarrd__ycuo.dtype.data[1])(c.
            context, c.builder, value_arr).data
        ddi__srum = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        qpkse__bail = cgutils.get_or_insert_function(c.builder.module,
            ddi__srum, name='map_array_from_sequence')
        jod__oegrj = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zetvf__fixrm = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.
            dtype)
        c.builder.call(qpkse__bail, [val, c.builder.bitcast(fjdk__qnpjv,
            lir.IntType(8).as_pointer()), c.builder.bitcast(frt__apt, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), jod__oegrj), lir.Constant(lir.IntType
            (32), zetvf__fixrm)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    jjjk__koww = c.context.make_helper(c.builder, typ)
    jjjk__koww.data = data_arr
    tflqp__isj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jjjk__koww._getvalue(), is_error=tflqp__isj)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    kzby__jttf = context.insert_const_string(builder.module, 'pandas')
    tohq__qicsa = c.pyapi.import_module_noblock(kzby__jttf)
    hvw__fsc = c.pyapi.object_getattr_string(tohq__qicsa, 'NA')
    ptf__dyja = c.context.get_constant(offset_type, 0)
    builder.store(ptf__dyja, offsets_ptr)
    osjuc__hmizv = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as kgkb__estiz:
        qbh__kzpkz = kgkb__estiz.index
        item_ind = builder.load(osjuc__hmizv)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [qbh__kzpkz]))
        vhl__ozmtz = seq_getitem(builder, context, val, qbh__kzpkz)
        set_bitmap_bit(builder, null_bitmap_ptr, qbh__kzpkz, 0)
        vuwap__oghw = is_na_value(builder, context, vhl__ozmtz, hvw__fsc)
        kuckw__kzr = builder.icmp_unsigned('!=', vuwap__oghw, lir.Constant(
            vuwap__oghw.type, 1))
        with builder.if_then(kuckw__kzr):
            set_bitmap_bit(builder, null_bitmap_ptr, qbh__kzpkz, 1)
            wnfzq__deku = dict_keys(builder, context, vhl__ozmtz)
            ryoo__kkbcg = dict_values(builder, context, vhl__ozmtz)
            n_items = bodo.utils.utils.object_length(c, wnfzq__deku)
            _unbox_array_item_array_copy_data(typ.key_arr_type, wnfzq__deku,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                ryoo__kkbcg, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), osjuc__hmizv)
            c.pyapi.decref(wnfzq__deku)
            c.pyapi.decref(ryoo__kkbcg)
        c.pyapi.decref(vhl__ozmtz)
    builder.store(builder.trunc(builder.load(osjuc__hmizv), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(tohq__qicsa)
    c.pyapi.decref(hvw__fsc)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    jjjk__koww = c.context.make_helper(c.builder, typ, val)
    data_arr = jjjk__koww.data
    uarrd__ycuo = _get_map_arr_data_type(typ)
    lane__jegin = _get_array_item_arr_payload(c.context, c.builder,
        uarrd__ycuo, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, lane__jegin.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, lane__jegin.offsets).data
    phdzx__uoa = _get_struct_arr_payload(c.context, c.builder, uarrd__ycuo.
        dtype, lane__jegin.data)
    key_arr = c.builder.extract_value(phdzx__uoa.data, 0)
    value_arr = c.builder.extract_value(phdzx__uoa.data, 1)
    if all(isinstance(hbgq__vhx, types.Array) and hbgq__vhx.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type) for
        hbgq__vhx in (typ.key_arr_type, typ.value_arr_type)):
        fjdk__qnpjv = c.context.make_array(uarrd__ycuo.dtype.data[0])(c.
            context, c.builder, key_arr).data
        frt__apt = c.context.make_array(uarrd__ycuo.dtype.data[1])(c.
            context, c.builder, value_arr).data
        ddi__srum = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        plgoc__obgt = cgutils.get_or_insert_function(c.builder.module,
            ddi__srum, name='np_array_from_map_array')
        jod__oegrj = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zetvf__fixrm = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.
            dtype)
        arr = c.builder.call(plgoc__obgt, [lane__jegin.n_arrays, c.builder.
            bitcast(fjdk__qnpjv, lir.IntType(8).as_pointer()), c.builder.
            bitcast(frt__apt, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), jod__oegrj), lir
            .Constant(lir.IntType(32), zetvf__fixrm)])
    else:
        arr = _box_map_array_generic(typ, c, lane__jegin.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    kzby__jttf = context.insert_const_string(builder.module, 'numpy')
    oszri__jsxr = c.pyapi.import_module_noblock(kzby__jttf)
    uyu__iol = c.pyapi.object_getattr_string(oszri__jsxr, 'object_')
    rodjk__rfgq = c.pyapi.long_from_longlong(n_maps)
    hrv__czb = c.pyapi.call_method(oszri__jsxr, 'ndarray', (rodjk__rfgq,
        uyu__iol))
    ljt__yscv = c.pyapi.object_getattr_string(oszri__jsxr, 'nan')
    zavl__xonb = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    osjuc__hmizv = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as kgkb__estiz:
        mfa__nkji = kgkb__estiz.index
        pyarray_setitem(builder, context, hrv__czb, mfa__nkji, ljt__yscv)
        cnkz__ici = get_bitmap_bit(builder, null_bitmap_ptr, mfa__nkji)
        ihloe__sbfr = builder.icmp_unsigned('!=', cnkz__ici, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(ihloe__sbfr):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(mfa__nkji, lir.Constant(mfa__nkji
                .type, 1))])), builder.load(builder.gep(offsets_ptr, [
                mfa__nkji]))), lir.IntType(64))
            item_ind = builder.load(osjuc__hmizv)
            vhl__ozmtz = c.pyapi.dict_new()
            pes__qzj = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            ykprm__iyi, ufeqi__hpk = c.pyapi.call_jit_code(pes__qzj, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            ykprm__iyi, bnjno__bxpwn = c.pyapi.call_jit_code(pes__qzj, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            xfc__smcc = c.pyapi.from_native_value(typ.key_arr_type,
                ufeqi__hpk, c.env_manager)
            pvai__wysu = c.pyapi.from_native_value(typ.value_arr_type,
                bnjno__bxpwn, c.env_manager)
            zyjl__svesv = c.pyapi.call_function_objargs(zavl__xonb, (
                xfc__smcc, pvai__wysu))
            dict_merge_from_seq2(builder, context, vhl__ozmtz, zyjl__svesv)
            builder.store(builder.add(item_ind, n_items), osjuc__hmizv)
            pyarray_setitem(builder, context, hrv__czb, mfa__nkji, vhl__ozmtz)
            c.pyapi.decref(zyjl__svesv)
            c.pyapi.decref(xfc__smcc)
            c.pyapi.decref(pvai__wysu)
            c.pyapi.decref(vhl__ozmtz)
    c.pyapi.decref(zavl__xonb)
    c.pyapi.decref(oszri__jsxr)
    c.pyapi.decref(uyu__iol)
    c.pyapi.decref(rodjk__rfgq)
    c.pyapi.decref(ljt__yscv)
    return hrv__czb


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    jjjk__koww = context.make_helper(builder, sig.return_type)
    jjjk__koww.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return jjjk__koww._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    ihmru__jhew = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return ihmru__jhew(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    huatl__nmeux = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(huatl__nmeux)


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
    lxyxv__affbg = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            hgsjy__mcc = val.keys()
            ymyi__hmqc = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), lxyxv__affbg, ('key', 'value'))
            for gtog__mxs, momu__aguav in enumerate(hgsjy__mcc):
                ymyi__hmqc[gtog__mxs] = bodo.libs.struct_arr_ext.init_struct((
                    momu__aguav, val[momu__aguav]), ('key', 'value'))
            arr._data[ind] = ymyi__hmqc
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
            jdl__xhtd = dict()
            mfexf__ebcz = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            ymyi__hmqc = bodo.libs.array_item_arr_ext.get_data(arr._data)
            eifp__wtgbm, ojwt__mfir = bodo.libs.struct_arr_ext.get_data(
                ymyi__hmqc)
            mcie__rrelp = mfexf__ebcz[ind]
            xrxvg__ebc = mfexf__ebcz[ind + 1]
            for gtog__mxs in range(mcie__rrelp, xrxvg__ebc):
                jdl__xhtd[eifp__wtgbm[gtog__mxs]] = ojwt__mfir[gtog__mxs]
            return jdl__xhtd
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
