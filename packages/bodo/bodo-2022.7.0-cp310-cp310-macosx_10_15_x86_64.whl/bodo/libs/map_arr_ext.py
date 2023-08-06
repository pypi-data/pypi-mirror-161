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
    zsp__gbvts = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(zsp__gbvts)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        tgnqf__pffx = _get_map_arr_data_type(fe_type)
        fnbwg__sqbu = [('data', tgnqf__pffx)]
        models.StructModel.__init__(self, dmm, fe_type, fnbwg__sqbu)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    uohgx__ygweg = all(isinstance(urf__znyu, types.Array) and urf__znyu.
        dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for urf__znyu in (typ.key_arr_type, typ.
        value_arr_type))
    if uohgx__ygweg:
        zeq__caw = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        lah__nkpd = cgutils.get_or_insert_function(c.builder.module,
            zeq__caw, name='count_total_elems_list_array')
        uuh__bvrce = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            lah__nkpd, [val])])
    else:
        uuh__bvrce = get_array_elem_counts(c, c.builder, c.context, val, typ)
    tgnqf__pffx = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, tgnqf__pffx,
        uuh__bvrce, c)
    zygka__tib = _get_array_item_arr_payload(c.context, c.builder,
        tgnqf__pffx, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, zygka__tib.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, zygka__tib.offsets).data
    iylgo__gkuj = _get_struct_arr_payload(c.context, c.builder, tgnqf__pffx
        .dtype, zygka__tib.data)
    key_arr = c.builder.extract_value(iylgo__gkuj.data, 0)
    value_arr = c.builder.extract_value(iylgo__gkuj.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    kydbx__fekhh, yuzv__nmpx = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [iylgo__gkuj.null_bitmap])
    if uohgx__ygweg:
        pzos__qud = c.context.make_array(tgnqf__pffx.dtype.data[0])(c.
            context, c.builder, key_arr).data
        cpax__zhj = c.context.make_array(tgnqf__pffx.dtype.data[1])(c.
            context, c.builder, value_arr).data
        zeq__caw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        uat__nwsr = cgutils.get_or_insert_function(c.builder.module,
            zeq__caw, name='map_array_from_sequence')
        pgqa__gupq = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zqbe__fxj = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(uat__nwsr, [val, c.builder.bitcast(pzos__qud, lir.
            IntType(8).as_pointer()), c.builder.bitcast(cpax__zhj, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), pgqa__gupq), lir.Constant(lir.IntType
            (32), zqbe__fxj)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    hvam__fpwx = c.context.make_helper(c.builder, typ)
    hvam__fpwx.data = data_arr
    qxl__ubp = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(hvam__fpwx._getvalue(), is_error=qxl__ubp)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    hqq__neqj = context.insert_const_string(builder.module, 'pandas')
    lvco__ltf = c.pyapi.import_module_noblock(hqq__neqj)
    rdd__tko = c.pyapi.object_getattr_string(lvco__ltf, 'NA')
    cpe__hzwbt = c.context.get_constant(offset_type, 0)
    builder.store(cpe__hzwbt, offsets_ptr)
    jrv__svt = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as ylxhw__axbj:
        zdp__ydv = ylxhw__axbj.index
        item_ind = builder.load(jrv__svt)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [zdp__ydv]))
        hwjrr__aieii = seq_getitem(builder, context, val, zdp__ydv)
        set_bitmap_bit(builder, null_bitmap_ptr, zdp__ydv, 0)
        iuup__myx = is_na_value(builder, context, hwjrr__aieii, rdd__tko)
        veq__upwem = builder.icmp_unsigned('!=', iuup__myx, lir.Constant(
            iuup__myx.type, 1))
        with builder.if_then(veq__upwem):
            set_bitmap_bit(builder, null_bitmap_ptr, zdp__ydv, 1)
            tbvph__mxkoz = dict_keys(builder, context, hwjrr__aieii)
            ideh__bemg = dict_values(builder, context, hwjrr__aieii)
            n_items = bodo.utils.utils.object_length(c, tbvph__mxkoz)
            _unbox_array_item_array_copy_data(typ.key_arr_type,
                tbvph__mxkoz, c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                ideh__bemg, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), jrv__svt)
            c.pyapi.decref(tbvph__mxkoz)
            c.pyapi.decref(ideh__bemg)
        c.pyapi.decref(hwjrr__aieii)
    builder.store(builder.trunc(builder.load(jrv__svt), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(lvco__ltf)
    c.pyapi.decref(rdd__tko)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    hvam__fpwx = c.context.make_helper(c.builder, typ, val)
    data_arr = hvam__fpwx.data
    tgnqf__pffx = _get_map_arr_data_type(typ)
    zygka__tib = _get_array_item_arr_payload(c.context, c.builder,
        tgnqf__pffx, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, zygka__tib.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, zygka__tib.offsets).data
    iylgo__gkuj = _get_struct_arr_payload(c.context, c.builder, tgnqf__pffx
        .dtype, zygka__tib.data)
    key_arr = c.builder.extract_value(iylgo__gkuj.data, 0)
    value_arr = c.builder.extract_value(iylgo__gkuj.data, 1)
    if all(isinstance(urf__znyu, types.Array) and urf__znyu.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type) for
        urf__znyu in (typ.key_arr_type, typ.value_arr_type)):
        pzos__qud = c.context.make_array(tgnqf__pffx.dtype.data[0])(c.
            context, c.builder, key_arr).data
        cpax__zhj = c.context.make_array(tgnqf__pffx.dtype.data[1])(c.
            context, c.builder, value_arr).data
        zeq__caw = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        lrcg__doi = cgutils.get_or_insert_function(c.builder.module,
            zeq__caw, name='np_array_from_map_array')
        pgqa__gupq = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zqbe__fxj = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(lrcg__doi, [zygka__tib.n_arrays, c.builder.
            bitcast(pzos__qud, lir.IntType(8).as_pointer()), c.builder.
            bitcast(cpax__zhj, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), pgqa__gupq), lir
            .Constant(lir.IntType(32), zqbe__fxj)])
    else:
        arr = _box_map_array_generic(typ, c, zygka__tib.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    hqq__neqj = context.insert_const_string(builder.module, 'numpy')
    bsn__nvgdt = c.pyapi.import_module_noblock(hqq__neqj)
    dhvvg__wbut = c.pyapi.object_getattr_string(bsn__nvgdt, 'object_')
    ycbvh__mjs = c.pyapi.long_from_longlong(n_maps)
    jhe__pqmwc = c.pyapi.call_method(bsn__nvgdt, 'ndarray', (ycbvh__mjs,
        dhvvg__wbut))
    wexk__xjmnb = c.pyapi.object_getattr_string(bsn__nvgdt, 'nan')
    msuu__tfcu = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    jrv__svt = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_maps) as ylxhw__axbj:
        pyavg__qoua = ylxhw__axbj.index
        pyarray_setitem(builder, context, jhe__pqmwc, pyavg__qoua, wexk__xjmnb)
        owaat__bkvtg = get_bitmap_bit(builder, null_bitmap_ptr, pyavg__qoua)
        icj__nuda = builder.icmp_unsigned('!=', owaat__bkvtg, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(icj__nuda):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(pyavg__qoua, lir.Constant(
                pyavg__qoua.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [pyavg__qoua]))), lir.IntType(64))
            item_ind = builder.load(jrv__svt)
            hwjrr__aieii = c.pyapi.dict_new()
            jdzbx__nup = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            kydbx__fekhh, dnpr__clao = c.pyapi.call_jit_code(jdzbx__nup,
                typ.key_arr_type(typ.key_arr_type, types.int64, types.int64
                ), [key_arr, item_ind, n_items])
            kydbx__fekhh, ghd__dff = c.pyapi.call_jit_code(jdzbx__nup, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            mvogj__faag = c.pyapi.from_native_value(typ.key_arr_type,
                dnpr__clao, c.env_manager)
            isa__entxb = c.pyapi.from_native_value(typ.value_arr_type,
                ghd__dff, c.env_manager)
            okyev__bopjs = c.pyapi.call_function_objargs(msuu__tfcu, (
                mvogj__faag, isa__entxb))
            dict_merge_from_seq2(builder, context, hwjrr__aieii, okyev__bopjs)
            builder.store(builder.add(item_ind, n_items), jrv__svt)
            pyarray_setitem(builder, context, jhe__pqmwc, pyavg__qoua,
                hwjrr__aieii)
            c.pyapi.decref(okyev__bopjs)
            c.pyapi.decref(mvogj__faag)
            c.pyapi.decref(isa__entxb)
            c.pyapi.decref(hwjrr__aieii)
    c.pyapi.decref(msuu__tfcu)
    c.pyapi.decref(bsn__nvgdt)
    c.pyapi.decref(dhvvg__wbut)
    c.pyapi.decref(ycbvh__mjs)
    c.pyapi.decref(wexk__xjmnb)
    return jhe__pqmwc


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    hvam__fpwx = context.make_helper(builder, sig.return_type)
    hvam__fpwx.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return hvam__fpwx._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    xfp__erzo = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return xfp__erzo(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    gjvd__zcor = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(gjvd__zcor)


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
    tclj__knyia = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            nky__ncj = val.keys()
            amlv__kgtnw = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), tclj__knyia, ('key', 'value'))
            for obfn__aiq, wwfrf__helk in enumerate(nky__ncj):
                amlv__kgtnw[obfn__aiq] = bodo.libs.struct_arr_ext.init_struct((
                    wwfrf__helk, val[wwfrf__helk]), ('key', 'value'))
            arr._data[ind] = amlv__kgtnw
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
            eya__ctd = dict()
            wxui__iglp = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            amlv__kgtnw = bodo.libs.array_item_arr_ext.get_data(arr._data)
            rwzt__elpw, fze__ljho = bodo.libs.struct_arr_ext.get_data(
                amlv__kgtnw)
            vtz__ghw = wxui__iglp[ind]
            eejk__dfq = wxui__iglp[ind + 1]
            for obfn__aiq in range(vtz__ghw, eejk__dfq):
                eya__ctd[rwzt__elpw[obfn__aiq]] = fze__ljho[obfn__aiq]
            return eya__ctd
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
